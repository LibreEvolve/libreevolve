from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BENCHMARK_HARDENING_SCHEMA = "libreevolve.benchmark_hardening.v1"
BENCHMARK_HARDENING_ARTIFACT_INVENTORY_SCHEMA = "libreevolve.benchmark_hardening_artifact_inventory.v1"
BENCHMARK_LEVELS = frozenset({"smoke", "benchmark", "paper_claim"})
SHORTCUT_CATEGORIES = frozenset(
    {
        "hardcoded_cases",
        "library_delegation",
        "dead_code_counter",
        "external_io",
        "stateful_cache",
        "prompt_or_metadata_leakage",
        "invalid_artifact",
        "reference_oracle_access",
    }
)
DETECTOR_KINDS = frozenset({"static_ast", "runtime_probe", "randomized_cases", "exhaustive_cases", "artifact_validator"})
FIXTURE_STATUSES = frozenset({"passed", "failed", "not_run"})
PROTECTED_SIGNAL_KINDS = frozenset({"operation_count", "rank", "correctness", "construction_artifact", "score"})
ARTIFACT_KINDS = frozenset({"hardening_report", "negative_fixture", "detector_log", "artifact_schema"})
_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class BenchmarkHardeningIssue:
    code: str
    message: str


@dataclass(frozen=True)
class BenchmarkHardeningValidation:
    ok: bool
    benchmark_ready: bool
    benchmark_id: str | None
    level: str | None
    issues: list[BenchmarkHardeningIssue]


def validate_benchmark_hardening_report(report: object | str | Path) -> BenchmarkHardeningValidation:
    """Validate anti-gaming coverage metadata for advertised benchmarks."""
    data, read_issues = _load_report(report)
    if read_issues:
        return BenchmarkHardeningValidation(False, False, None, None, read_issues)
    assert isinstance(data, dict)
    issues: list[BenchmarkHardeningIssue] = []
    if data.get("schema") != BENCHMARK_HARDENING_SCHEMA:
        issues.append(BenchmarkHardeningIssue("invalid_schema", "unsupported benchmark hardening schema"))
    benchmark_id = _id_field(data, "benchmark_id", issues)
    level = data.get("level")
    if level not in BENCHMARK_LEVELS:
        issues.append(BenchmarkHardeningIssue("invalid_level", "unsupported benchmark level"))
        level = None
    protected_signal_ids = _validate_protected_signals(data.get("protected_signals"), issues)
    categories = _validate_shortcuts(
        data.get("shortcut_threats"),
        protected_signal_ids,
        issues,
    )
    fixture_categories = _validate_negative_fixtures(data.get("negative_fixtures"), issues)
    _validate_artifacts(data.get("artifacts"), issues)
    if level in {"benchmark", "paper_claim"}:
        missing_fixtures = categories - fixture_categories
        if missing_fixtures:
            issues.append(
                BenchmarkHardeningIssue(
                    "missing_negative_fixture",
                    "benchmark-level hardening requires a passed negative fixture for every shortcut threat",
                )
            )
    benchmark_ready = not issues and level in {"benchmark", "paper_claim"}
    return BenchmarkHardeningValidation(
        ok=not issues,
        benchmark_ready=benchmark_ready,
        benchmark_id=benchmark_id,
        level=level,
        issues=issues,
    )


def render_benchmark_hardening_summary(report: dict[str, Any]) -> str:
    validation = validate_benchmark_hardening_report(report)
    status = "ok" if validation.ok else "invalid"
    ready = "yes" if validation.benchmark_ready else "no"
    lines = [
        f"Benchmark hardening report: {report.get('benchmark_id', '<unknown>')}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| benchmark_ready | {ready} |",
        f"| level | {report.get('level', '<unknown>')} |",
        f"| protected_signal_count | {len(report.get('protected_signals', [])) if isinstance(report.get('protected_signals'), list) else 0} |",
        f"| shortcut_threat_count | {len(report.get('shortcut_threats', [])) if isinstance(report.get('shortcut_threats'), list) else 0} |",
        f"| negative_fixture_count | {len(report.get('negative_fixtures', [])) if isinstance(report.get('negative_fixtures'), list) else 0} |",
        f"| artifact_count | {len(report.get('artifacts', [])) if isinstance(report.get('artifacts'), list) else 0} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def benchmark_hardening_artifact_inventory(
    report: object | str | Path,
    artifact_root: str | Path,
) -> dict[str, Any]:
    """Verify negative-fixture and hardening artifact references under a root."""
    data, read_issues = _load_report(report)
    root = Path(artifact_root)
    records: list[dict[str, Any]] = []
    issues = [
        {"code": issue.code, "message": issue.message}
        for issue in read_issues
    ]
    if data is not None:
        for field in ("negative_fixtures", "artifacts"):
            values = data.get(field)
            if isinstance(values, list):
                for index, record in enumerate(values):
                    records.append(_hardening_inventory_record(record, root, field, index))
            else:
                issues.append(
                    {
                        "code": f"invalid_{field}",
                        "message": f"{field} must be a non-empty list",
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
        if record["status"] in {"invalid_record", "unsafe_path", "read_error"}
    )
    if not records and data is not None:
        issues.append(
            {
                "code": "empty_artifact_inventory",
                "message": "no negative fixture or artifact records were available to verify",
            }
        )
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return {
        "schema": BENCHMARK_HARDENING_ARTIFACT_INVENTORY_SCHEMA,
        "report_schema": data.get("schema") if isinstance(data, dict) else None,
        "benchmark_id": data.get("benchmark_id") if isinstance(data, dict) else None,
        "level": data.get("level") if isinstance(data, dict) else None,
        "artifact_root_policy": "safe_relative_report_paths_under_artifact_root",
        "artifact_root_name": root.name,
        "record_count": len(records),
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
        "records": records,
    }


def _load_report(report: object | str | Path) -> tuple[dict[str, Any] | None, list[BenchmarkHardeningIssue]]:
    if isinstance(report, dict):
        return dict(report), []
    if isinstance(report, (str, Path)):
        path = Path(report)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [BenchmarkHardeningIssue("read_error", f"failed to read hardening report: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [BenchmarkHardeningIssue("invalid_json", f"invalid hardening JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [BenchmarkHardeningIssue("invalid_shape", "benchmark hardening report must be a JSON object")]


def _hardening_inventory_record(
    record: object,
    root: Path,
    section: str,
    index: int,
) -> dict[str, Any]:
    if not isinstance(record, dict):
        return {
            "section": section,
            "index": index,
            "kind": "unknown",
            "path": "",
            "status": "invalid_record",
            "issues": ["invalid_record"],
        }
    kind = record.get("kind")
    if section == "negative_fixtures":
        kind = record.get("category")
    path = record.get("path")
    expected_sha = record.get("sha256")
    expected_bytes = record.get("bytes")
    inventory: dict[str, Any] = {
        "section": section,
        "index": index,
        "kind": kind if isinstance(kind, str) else "unknown",
        "path": path if isinstance(path, str) else "",
        "expected_sha256": expected_sha if isinstance(expected_sha, str) else "",
        "expected_bytes": expected_bytes if isinstance(expected_bytes, int) and not isinstance(expected_bytes, bool) else None,
        "status": "verified",
        "issues": [],
    }
    path_obj = Path(path) if isinstance(path, str) else None
    if (
        path_obj is None
        or not path
        or path_obj.is_absolute()
        or path.startswith(("/", "\\"))
        or ".." in path_obj.parts
    ):
        inventory["status"] = "unsafe_path"
        inventory["issues"].append("invalid_record_path")
        return inventory
    try:
        resolved_root = root.resolve()
        resolved_path = (resolved_root / path_obj).resolve(strict=False)
    except OSError:
        inventory["status"] = "unsafe_path"
        inventory["issues"].append("invalid_record_path")
        return inventory
    if not resolved_path.is_relative_to(resolved_root):
        inventory["status"] = "unsafe_path"
        inventory["issues"].append("record_path_outside_root")
        return inventory
    if not resolved_path.exists():
        inventory["status"] = "missing_file"
        inventory["issues"].append("missing_record_file")
        return inventory
    if not resolved_path.is_file():
        inventory["status"] = "unsafe_path"
        inventory["issues"].append("record_path_not_file")
        return inventory
    try:
        raw = resolved_path.read_bytes()
    except OSError:
        inventory["status"] = "read_error"
        inventory["issues"].append("record_read_error")
        return inventory
    actual_sha = hashlib.sha256(raw).hexdigest()
    actual_bytes = len(raw)
    inventory["actual_sha256"] = actual_sha
    inventory["actual_bytes"] = actual_bytes
    if not isinstance(expected_sha, str) or _SHA256_RE.fullmatch(expected_sha) is None:
        inventory["status"] = "hash_mismatch"
        inventory["issues"].append("invalid_expected_record_hash")
    elif actual_sha != expected_sha:
        inventory["status"] = "hash_mismatch"
        inventory["issues"].append("record_hash_mismatch")
    if isinstance(expected_bytes, bool) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
        if inventory["status"] == "verified":
            inventory["status"] = "bytes_mismatch"
        inventory["issues"].append("invalid_expected_record_bytes")
    elif actual_bytes != expected_bytes:
        if inventory["status"] == "verified":
            inventory["status"] = "bytes_mismatch"
        inventory["issues"].append("record_bytes_mismatch")
    return inventory


def _id_field(data: dict[str, Any], field: str, issues: list[BenchmarkHardeningIssue]) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or _ID_RE.fullmatch(value) is None:
        issues.append(BenchmarkHardeningIssue(f"invalid_{field}", f"{field} must be a stable identifier"))
        return None
    return value


def _validate_protected_signals(value: object, issues: list[BenchmarkHardeningIssue]) -> set[str]:
    signal_ids: set[str] = set()
    if not isinstance(value, list) or not value:
        issues.append(BenchmarkHardeningIssue("invalid_protected_signals", "protected_signals must be a non-empty list"))
        return signal_ids
    seen: set[str] = set()
    for signal in value:
        if not isinstance(signal, dict):
            issues.append(BenchmarkHardeningIssue("invalid_protected_signal", "protected signal must be an object"))
            continue
        signal_id = signal.get("id")
        if not isinstance(signal_id, str) or _ID_RE.fullmatch(signal_id) is None:
            issues.append(BenchmarkHardeningIssue("invalid_protected_signal_id", "protected signal id must be stable"))
        elif signal_id in seen:
            issues.append(BenchmarkHardeningIssue("duplicate_protected_signal", "protected signal ids must be unique"))
        else:
            seen.add(signal_id)
            signal_ids.add(signal_id)
        if signal.get("kind") not in PROTECTED_SIGNAL_KINDS:
            issues.append(BenchmarkHardeningIssue("invalid_protected_signal_kind", "unsupported protected signal kind"))
        if not isinstance(signal.get("description"), str) or not signal["description"].strip():
            issues.append(BenchmarkHardeningIssue("missing_protected_signal_description", "protected signal description is required"))
    return signal_ids


def _validate_shortcuts(
    value: object,
    protected_signal_ids: set[str],
    issues: list[BenchmarkHardeningIssue],
) -> set[str]:
    if not isinstance(value, list) or not value:
        issues.append(BenchmarkHardeningIssue("invalid_shortcut_threats", "shortcut_threats must be a non-empty list"))
        return set()
    categories: set[str] = set()
    for threat in value:
        if not isinstance(threat, dict):
            issues.append(BenchmarkHardeningIssue("invalid_shortcut_threat", "shortcut threat must be an object"))
            continue
        category = threat.get("category")
        if category not in SHORTCUT_CATEGORIES:
            issues.append(BenchmarkHardeningIssue("invalid_shortcut_category", "unsupported shortcut category"))
            continue
        categories.add(category)
        detector = threat.get("detector")
        if not isinstance(detector, dict):
            issues.append(BenchmarkHardeningIssue("invalid_shortcut_detector", "shortcut detector must be an object"))
            continue
        if detector.get("kind") not in DETECTOR_KINDS:
            issues.append(BenchmarkHardeningIssue("invalid_detector_kind", "unsupported shortcut detector kind"))
        if not isinstance(detector.get("description"), str) or not detector["description"].strip():
            issues.append(BenchmarkHardeningIssue("missing_detector_description", "shortcut detector description is required"))
        linked_signals = threat.get("protected_signal_ids")
        if not isinstance(linked_signals, list) or not linked_signals:
            issues.append(BenchmarkHardeningIssue("invalid_shortcut_protected_signals", "shortcut threat must list protected_signal_ids"))
        else:
            seen_signals: set[str] = set()
            for signal_id in linked_signals:
                if not isinstance(signal_id, str) or _ID_RE.fullmatch(signal_id) is None:
                    issues.append(BenchmarkHardeningIssue("invalid_shortcut_protected_signal_id", "shortcut protected signal id must be stable"))
                elif signal_id in seen_signals:
                    issues.append(BenchmarkHardeningIssue("duplicate_shortcut_protected_signal_id", "shortcut protected_signal_ids must be unique"))
                elif signal_id not in protected_signal_ids:
                    issues.append(BenchmarkHardeningIssue("unknown_shortcut_protected_signal", "shortcut protected_signal_ids must reference protected_signals"))
                else:
                    seen_signals.add(signal_id)
    return categories


def _validate_negative_fixtures(value: object, issues: list[BenchmarkHardeningIssue]) -> set[str]:
    if not isinstance(value, list) or not value:
        issues.append(BenchmarkHardeningIssue("invalid_negative_fixtures", "negative_fixtures must be a non-empty list"))
        return set()
    covered: set[str] = set()
    seen: set[str] = set()
    for fixture in value:
        if not isinstance(fixture, dict):
            issues.append(BenchmarkHardeningIssue("invalid_negative_fixture", "negative fixture must be an object"))
            continue
        fixture_id = fixture.get("id")
        if not isinstance(fixture_id, str) or _ID_RE.fullmatch(fixture_id) is None:
            issues.append(BenchmarkHardeningIssue("invalid_negative_fixture_id", "negative fixture id must be stable"))
        elif fixture_id in seen:
            issues.append(BenchmarkHardeningIssue("duplicate_negative_fixture", "negative fixture ids must be unique"))
        else:
            seen.add(fixture_id)
        category = fixture.get("category")
        if category not in SHORTCUT_CATEGORIES:
            issues.append(BenchmarkHardeningIssue("invalid_negative_fixture_category", "unsupported negative fixture category"))
        status = fixture.get("status")
        if status not in FIXTURE_STATUSES:
            issues.append(BenchmarkHardeningIssue("invalid_negative_fixture_status", "unsupported negative fixture status"))
        elif status == "passed" and category in SHORTCUT_CATEGORIES:
            covered.add(category)
        _validate_file_record(fixture, "negative_fixture", issues)
    return covered


def _validate_artifacts(value: object, issues: list[BenchmarkHardeningIssue]) -> None:
    if not isinstance(value, list) or not value:
        issues.append(BenchmarkHardeningIssue("invalid_artifacts", "artifacts must be a non-empty list"))
        return
    for artifact in value:
        if not isinstance(artifact, dict):
            issues.append(BenchmarkHardeningIssue("invalid_artifact", "artifact must be an object"))
            continue
        if artifact.get("kind") not in ARTIFACT_KINDS:
            issues.append(BenchmarkHardeningIssue("invalid_artifact_kind", "unsupported artifact kind"))
        _validate_file_record(artifact, "artifact", issues)


def _validate_file_record(record: dict[str, Any], prefix: str, issues: list[BenchmarkHardeningIssue]) -> None:
    path = record.get("path")
    path_obj = Path(path) if isinstance(path, str) else None
    if (
        path_obj is None
        or not path
        or path_obj.is_absolute()
        or path.startswith(("/", "\\"))
        or ".." in path_obj.parts
    ):
        issues.append(BenchmarkHardeningIssue(f"invalid_{prefix}_path", f"{prefix} path must be safe and relative"))
    sha = record.get("sha256")
    if not isinstance(sha, str) or _SHA256_RE.fullmatch(sha) is None:
        issues.append(BenchmarkHardeningIssue(f"invalid_{prefix}_hash", f"{prefix} sha256 must be a lowercase SHA-256 hex digest"))
    byte_count = record.get("bytes")
    if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count <= 0:
        issues.append(BenchmarkHardeningIssue(f"invalid_{prefix}_bytes", f"{prefix} bytes must be a positive integer"))
