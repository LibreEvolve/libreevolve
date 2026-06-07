from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LLM_FEEDBACK_CALIBRATION_SCHEMA = "libreevolve.llm_feedback_calibration.v1"
LLM_FEEDBACK_CALIBRATION_ARTIFACT_INVENTORY_SCHEMA = (
    "libreevolve.llm_feedback_calibration_artifact_inventory.v1"
)
_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_ARTIFACT_KINDS = frozenset(
    {"calibration_report", "raw_records", "grader_config", "plot"}
)


@dataclass(frozen=True)
class FeedbackCalibrationIssue:
    code: str
    message: str


@dataclass(frozen=True)
class FeedbackCalibrationValidation:
    ok: bool
    calibration_ready: bool
    grader_count: int
    task_count: int
    record_count: int
    issues: list[FeedbackCalibrationIssue]


def validate_feedback_calibration_report(
    report: object | str | Path,
) -> FeedbackCalibrationValidation:
    """Validate LLM feedback-grader calibration evidence without running it."""
    data, read_issues = _load_report(report)
    if read_issues:
        return FeedbackCalibrationValidation(False, False, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[FeedbackCalibrationIssue] = []
    if data.get("schema") != LLM_FEEDBACK_CALIBRATION_SCHEMA:
        issues.append(
            FeedbackCalibrationIssue(
                "invalid_schema",
                "unsupported LLM feedback calibration schema",
            )
        )
    _id_field(data, "report_id", issues)
    declared_ready = data.get("calibration_ready")
    if not isinstance(declared_ready, bool):
        issues.append(
            FeedbackCalibrationIssue(
                "invalid_calibration_ready",
                "calibration_ready must be boolean",
            )
        )
        declared_ready = False
    graders = _validate_graders(data.get("graders"), issues)
    tasks = _validate_tasks(data.get("tasks"), issues)
    records = _validate_records(data.get("records"), graders, tasks, issues)
    _validate_artifacts(data.get("artifacts"), issues)
    if declared_ready is True:
        if len(graders) == 0:
            issues.append(
                FeedbackCalibrationIssue(
                    "missing_ready_graders",
                    "calibration-ready reports require at least one grader",
                )
            )
        if len(tasks) < 2:
            issues.append(
                FeedbackCalibrationIssue(
                    "insufficient_ready_tasks",
                    "calibration-ready reports require at least two tasks",
                )
            )
        if not records:
            issues.append(
                FeedbackCalibrationIssue(
                    "missing_ready_records",
                    "calibration-ready reports require scored records",
                )
            )
        if not data.get("artifacts"):
            issues.append(
                FeedbackCalibrationIssue(
                    "missing_ready_artifacts",
                    "calibration-ready reports require artifact references",
                )
            )
    calibration_ready = not issues and declared_ready is True
    return FeedbackCalibrationValidation(
        ok=not issues,
        calibration_ready=calibration_ready,
        grader_count=len(graders),
        task_count=len(tasks),
        record_count=len(records),
        issues=issues,
    )


def render_feedback_calibration_summary(report: dict[str, Any]) -> str:
    validation = validate_feedback_calibration_report(report)
    status = "ok" if validation.ok else "invalid"
    ready = "yes" if validation.calibration_ready else "no"
    lines = [
        f"LLM feedback calibration: {report.get('report_id', '<unknown>')}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| calibration_ready | {ready} |",
        f"| grader_count | {validation.grader_count} |",
        f"| task_count | {validation.task_count} |",
        f"| record_count | {validation.record_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def feedback_calibration_artifact_inventory(
    report: object | str | Path,
    artifact_root: str | Path,
) -> dict[str, Any]:
    """Verify feedback-calibration artifact references against concrete files."""
    data, read_issues = _load_report(report)
    root = Path(artifact_root)
    records: list[dict[str, Any]] = []
    issues = [
        {"code": issue.code, "message": issue.message}
        for issue in read_issues
    ]
    if data is not None:
        artifacts = data.get("artifacts")
        if isinstance(artifacts, list):
            records = [
                _artifact_inventory_record(artifact, root) for artifact in artifacts
            ]
        else:
            issues.append(
                {
                    "code": "invalid_artifacts",
                    "message": "artifacts must be a non-empty list",
                }
            )
    verified_count = sum(1 for record in records if record["status"] == "verified")
    missing_count = sum(1 for record in records if record["status"] == "missing_file")
    mismatch_count = sum(
        1
        for record in records
        if record["status"] in {"hash_mismatch", "bytes_mismatch"}
    )
    invalid_count = sum(
        1
        for record in records
        if record["status"] in {"invalid_artifact", "unsafe_path", "read_error"}
    )
    if not records and data is not None:
        issues.append(
            {
                "code": "empty_artifact_inventory",
                "message": "no calibration artifact records were available to verify",
            }
        )
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return {
        "schema": LLM_FEEDBACK_CALIBRATION_ARTIFACT_INVENTORY_SCHEMA,
        "report_schema": data.get("schema") if isinstance(data, dict) else None,
        "report_id": data.get("report_id") if isinstance(data, dict) else None,
        "artifact_root_policy": "safe_relative_calibration_paths_under_artifact_root",
        "artifact_root_name": root.name,
        "artifact_count": len(records),
        "verified_count": verified_count,
        "missing_count": missing_count,
        "mismatch_count": mismatch_count,
        "invalid_count": invalid_count,
        "records_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "ok": (
            not issues
            and bool(records)
            and verified_count == len(records)
            and missing_count == 0
            and mismatch_count == 0
            and invalid_count == 0
        ),
        "issues": issues,
        "artifacts": records,
    }


def _load_report(
    report: object | str | Path,
) -> tuple[dict[str, Any] | None, list[FeedbackCalibrationIssue]]:
    if isinstance(report, dict):
        return dict(report), []
    if isinstance(report, (str, Path)):
        path = Path(report)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [
                FeedbackCalibrationIssue(
                    "read_error",
                    f"failed to read feedback calibration report: {exc}",
                )
            ]
        except json.JSONDecodeError as exc:
            return None, [
                FeedbackCalibrationIssue(
                    "invalid_json",
                    f"invalid feedback calibration JSON: {exc.msg}",
                )
            ]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [
        FeedbackCalibrationIssue(
            "invalid_shape",
            "feedback calibration report must be a JSON object",
        )
    ]


def _validate_graders(
    value: object,
    issues: list[FeedbackCalibrationIssue],
) -> set[str]:
    if not isinstance(value, list) or not value:
        issues.append(
            FeedbackCalibrationIssue(
                "invalid_graders",
                "graders must be a non-empty list",
            )
        )
        return set()
    graders: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            issues.append(
                FeedbackCalibrationIssue(
                    "invalid_grader",
                    "grader records must be objects",
                )
            )
            continue
        name = _id_field(item, "name", issues)
        metric = _id_field(item, "metric", issues)
        if name in graders:
            issues.append(
                FeedbackCalibrationIssue(
                    "duplicate_grader",
                    "grader names must be unique",
                )
            )
        if name is not None:
            graders.add(name)
        if metric is None:
            continue
        if item.get("normalization") != "configured_bounds_to_unit_interval":
            issues.append(
                FeedbackCalibrationIssue(
                    "invalid_grader_normalization",
                    "grader normalization must be configured_bounds_to_unit_interval",
                )
            )
        if item.get("direction") not in {"maximize", "minimize"}:
            issues.append(
                FeedbackCalibrationIssue(
                    "invalid_grader_direction",
                    "grader direction must be maximize or minimize",
                )
            )
    return graders


def _validate_tasks(
    value: object,
    issues: list[FeedbackCalibrationIssue],
) -> set[str]:
    if not isinstance(value, list) or not value:
        issues.append(
            FeedbackCalibrationIssue(
                "invalid_tasks",
                "tasks must be a non-empty list",
            )
        )
        return set()
    tasks: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            issues.append(
                FeedbackCalibrationIssue(
                    "invalid_task",
                    "task records must be objects",
                )
            )
            continue
        task_id = _id_field(item, "task_id", issues)
        if task_id in tasks:
            issues.append(
                FeedbackCalibrationIssue(
                    "duplicate_task",
                    "task ids must be unique",
                )
            )
        if task_id is not None:
            tasks.add(task_id)
    return tasks


def _validate_records(
    value: object,
    graders: set[str],
    tasks: set[str],
    issues: list[FeedbackCalibrationIssue],
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        issues.append(
            FeedbackCalibrationIssue(
                "invalid_records",
                "records must be a non-empty list",
            )
        )
        return []
    records: list[dict[str, Any]] = []
    coverage: set[tuple[str, str]] = set()
    for item in value:
        if not isinstance(item, dict):
            issues.append(
                FeedbackCalibrationIssue(
                    "invalid_record",
                    "calibration records must be objects",
                )
            )
            continue
        grader = _id_field(item, "grader", issues)
        task_id = _id_field(item, "task_id", issues)
        if grader is not None and grader not in graders:
            issues.append(
                FeedbackCalibrationIssue(
                    "unknown_record_grader",
                    "calibration record references an undeclared grader",
                )
            )
        if task_id is not None and task_id not in tasks:
            issues.append(
                FeedbackCalibrationIssue(
                    "unknown_record_task",
                    "calibration record references an undeclared task",
                )
            )
        seed = item.get("seed")
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            issues.append(
                FeedbackCalibrationIssue(
                    "invalid_record_seed",
                    "calibration record seed must be a non-negative integer",
                )
            )
        expected = _unit_interval_number(
            item.get("expected_normalized_score"),
            "invalid_expected_normalized_score",
            issues,
        )
        observed = _unit_interval_number(
            item.get("observed_normalized_score"),
            "invalid_observed_normalized_score",
            issues,
        )
        absolute_error = _unit_interval_number(
            item.get("absolute_error"),
            "invalid_absolute_error",
            issues,
        )
        if expected is not None and observed is not None and absolute_error is not None:
            if abs(abs(expected - observed) - absolute_error) > 1e-9:
                issues.append(
                    FeedbackCalibrationIssue(
                        "absolute_error_mismatch",
                        "absolute_error must equal the normalized score difference",
                    )
                )
        if grader is not None and task_id is not None:
            coverage.add((grader, task_id))
        records.append(item)
    missing = {(grader, task) for grader in graders for task in tasks} - coverage
    if missing:
        issues.append(
            FeedbackCalibrationIssue(
                "missing_grader_task_coverage",
                "each grader must have at least one record for each task",
            )
        )
    return records


def _validate_artifacts(
    value: object,
    issues: list[FeedbackCalibrationIssue],
) -> None:
    if not isinstance(value, list) or not value:
        issues.append(
            FeedbackCalibrationIssue(
                "invalid_artifacts",
                "artifacts must be a non-empty list",
            )
        )
        return
    for item in value:
        if not isinstance(item, dict):
            issues.append(
                FeedbackCalibrationIssue(
                    "invalid_artifact",
                    "artifact records must be objects",
                )
            )
            continue
        if item.get("kind") not in _ARTIFACT_KINDS:
            issues.append(
                FeedbackCalibrationIssue(
                    "invalid_artifact_kind",
                    "artifact kind is unsupported",
                )
            )
        _path_field(item.get("path"), issues)
        sha = item.get("sha256")
        if not isinstance(sha, str) or _SHA256_RE.fullmatch(sha) is None:
            issues.append(
                FeedbackCalibrationIssue(
                    "invalid_artifact_sha256",
                    "artifact sha256 must be a lowercase SHA-256 hex digest",
                )
            )
        size = item.get("bytes")
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            issues.append(
                FeedbackCalibrationIssue(
                    "invalid_artifact_bytes",
                    "artifact bytes must be a positive integer",
                )
            )


def _artifact_inventory_record(artifact: object, root: Path) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        return {
            "kind": "unknown",
            "path": "",
            "status": "invalid_artifact",
            "issues": ["invalid_artifact"],
        }
    kind = artifact.get("kind")
    path = artifact.get("path")
    expected_sha = artifact.get("sha256")
    expected_bytes = artifact.get("bytes")
    record: dict[str, Any] = {
        "kind": kind if isinstance(kind, str) else "unknown",
        "path": path if isinstance(path, str) else "",
        "expected_sha256": expected_sha if isinstance(expected_sha, str) else "",
        "expected_bytes": (
            expected_bytes
            if isinstance(expected_bytes, int) and not isinstance(expected_bytes, bool)
            else None
        ),
        "status": "verified",
        "issues": [],
    }
    path_obj = Path(path) if isinstance(path, str) else None
    if path_obj is None or _unsafe_path(path, path_obj):
        record["status"] = "unsafe_path"
        record["issues"].append("invalid_artifact_path")
        return record
    try:
        resolved_root = root.resolve()
        resolved_path = (resolved_root / path_obj).resolve(strict=False)
    except OSError:
        record["status"] = "unsafe_path"
        record["issues"].append("invalid_artifact_path")
        return record
    if not resolved_path.is_relative_to(resolved_root):
        record["status"] = "unsafe_path"
        record["issues"].append("artifact_path_outside_root")
        return record
    if not resolved_path.exists():
        record["status"] = "missing_file"
        record["issues"].append("missing_artifact_file")
        return record
    if not resolved_path.is_file() or resolved_path.is_symlink():
        record["status"] = "unsafe_path"
        record["issues"].append("artifact_path_not_regular_file")
        return record
    try:
        raw = resolved_path.read_bytes()
    except OSError:
        record["status"] = "read_error"
        record["issues"].append("artifact_read_error")
        return record
    actual_sha = hashlib.sha256(raw).hexdigest()
    record["actual_sha256"] = actual_sha
    record["actual_bytes"] = len(raw)
    if not isinstance(expected_sha, str) or _SHA256_RE.fullmatch(expected_sha) is None:
        record["status"] = "hash_mismatch"
        record["issues"].append("invalid_expected_artifact_hash")
    elif actual_sha != expected_sha:
        record["status"] = "hash_mismatch"
        record["issues"].append("artifact_hash_mismatch")
    if isinstance(expected_bytes, bool) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
        if record["status"] == "verified":
            record["status"] = "bytes_mismatch"
        record["issues"].append("invalid_expected_artifact_bytes")
    elif len(raw) != expected_bytes:
        if record["status"] == "verified":
            record["status"] = "bytes_mismatch"
        record["issues"].append("artifact_bytes_mismatch")
    return record


def _id_field(
    data: dict[str, Any],
    field: str,
    issues: list[FeedbackCalibrationIssue],
) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or _ID_RE.fullmatch(value) is None:
        issues.append(
            FeedbackCalibrationIssue(
                f"invalid_{field}",
                f"{field} must be a stable identifier",
            )
        )
        return None
    return value


def _unit_interval_number(
    value: object,
    code: str,
    issues: list[FeedbackCalibrationIssue],
) -> float | None:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or float(value) < 0.0
        or float(value) > 1.0
    ):
        issues.append(
            FeedbackCalibrationIssue(
                code,
                "calibration scores must be finite numbers in [0, 1]",
            )
        )
        return None
    return float(value)


def _path_field(value: object, issues: list[FeedbackCalibrationIssue]) -> None:
    path = Path(value) if isinstance(value, str) else None
    if path is None or _unsafe_path(value, path):
        issues.append(
            FeedbackCalibrationIssue(
                "invalid_artifact_path",
                "artifact paths must be safe relative paths",
            )
        )


def _unsafe_path(value: object, path: Path) -> bool:
    return (
        not isinstance(value, str)
        or not value
        or path.is_absolute()
        or value.startswith(("/", "\\"))
        or ".." in path.parts
    )
