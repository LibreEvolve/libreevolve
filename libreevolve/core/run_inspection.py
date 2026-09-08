"""Pure inspection helpers for persisted LibreEvolve runs.

This module intentionally has no Click dependency.  The CLI owns option parsing,
terminal formatting, and translation of RunInspectionError into Click errors.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re

from libreevolve.core.artifact_schema import validate_non_jsonl_artifact_policy_manifest, validate_quarantine_artifact_policy_manifest, validate_run_artifact_bundle_report
from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.core.validator_policy import (
    validate_run_artifact_validator_boundary_consistency,
)
from libreevolve.population.program import validate_program_identity, validate_program_metrics


_ARCHIVE_DESCRIPTOR_PREVIEW_LIMIT = 8
_ARCHIVE_DESCRIPTOR_LABEL_DISPLAY_LIMIT = 48
_ARCHIVE_DESCRIPTOR_JSON_DISPLAY_LIMIT = 512
_SHOW_DIAGNOSTIC_LABEL_DISPLAY_LIMIT = 64
_SHOW_DIAGNOSTIC_BUCKET_LIMIT = 5
_SHOW_SOURCE_DISPLAY_LIMIT = 4096


class RunInspectionError(ValueError):
    """Raised for invalid or unreadable persisted inspection data."""


@dataclass(frozen=True)
class InspectionResult:
    total: int
    runtime_status: str
    selection: str
    best_line_number: int
    best: dict
    archive_summary: str | None
    lineage_summary: str | None
    prompt_summary: str | None
    evaluation_summary: str | None
    feedback_summary: str | None
    failure_summary: str | None
    validator_boundary_summary: str | None
    run_artifact_bundle_summary: str | None
    quarantine_summary: str | None
    non_jsonl_artifact_summary: str | None
    metrics: dict | None
    workspace: tuple[str, dict[str, str]] | None


def inspect_run(run_dir: str | Path) -> InspectionResult:
    """Validate and select the best record from a persisted run."""
    run_path = Path(run_dir)
    history_path = run_path / "history.jsonl"
    if not history_path.exists():
        raise RunInspectionError(f"No history.jsonl found in {run_dir}")

    total = 0
    has_archive_metadata = False
    first_modern_line = None
    first_legacy_line = None
    best_modern = None
    best_legacy = None
    archive_cell_upper_bound = _show_archive_cell_upper_bound(run_path)
    for line_number, record in _iter_history_records(
        history_path,
        archive_cell_upper_bound=archive_cell_upper_bound,
    ):
        total += 1
        is_modern = _has_archive_metadata(record)
        if is_modern:
            if first_modern_line is None:
                first_modern_line = line_number
            if first_legacy_line is not None:
                _raise_mixed_history_schema(
                    line_number, first_legacy_line, first_modern_line
                )
            has_archive_metadata = True
            if _is_archive_admitted_valid(record):
                best_modern = _select_better_record(
                    best_modern,
                    (line_number, record),
                    lambda item: _record_selection_key(item[1]),
                )
        else:
            if first_legacy_line is None:
                first_legacy_line = line_number
            if first_modern_line is not None:
                _raise_mixed_history_schema(
                    line_number, first_legacy_line, first_modern_line
                )
        best_legacy = _select_better_record(
            best_legacy,
            (line_number, record),
            lambda item: float(item[1].get("fitness", float("-inf"))),
        )

    if total == 0:
        raise RunInspectionError("history.jsonl is empty")
    if has_archive_metadata:
        if best_modern is None:
            raise RunInspectionError("No archive-retained valid programs found")
        best_line_number, best = best_modern
        selection = "archive-retained valid"
    else:
        best_line_number, best = best_legacy
        selection = "legacy highest-fitness"

    runtime_status = _show_runtime_status(run_path, total)
    _validate_display_record(best, best_line_number)
    archive_summary = _archive_summary(
        best,
        best_line_number,
        archive_cell_upper_bound=archive_cell_upper_bound,
    )
    workspace = _history_record_workspace(best, best_line_number)
    return InspectionResult(
        total=total,
        runtime_status=runtime_status,
        selection=selection,
        best_line_number=best_line_number,
        best=best,
        archive_summary=archive_summary,
        lineage_summary=_lineage_summary(best),
        prompt_summary=_prompt_summary(best, best_line_number),
        evaluation_summary=_evaluation_diagnostics_summary(best, best_line_number),
        feedback_summary=_feedback_summary(best, best_line_number),
        failure_summary=_failure_statistics_summary(run_path),
        validator_boundary_summary=_validator_boundary_artifact_summary(run_path),
        run_artifact_bundle_summary=_run_artifact_bundle_summary(run_path),
        quarantine_summary=_quarantine_stream_summary(run_path),
        non_jsonl_artifact_summary=_non_jsonl_artifact_policy_summary(run_path),
        metrics=best.get("metrics"),
        workspace=workspace,
    )


def read_manifest(path: Path) -> dict:
    return _read_show_manifest(path)


def validate_manifest_run_artifact_bundle_report(
    manifest: dict,
    *,
    error_prefix: str,
) -> None:
    _validate_manifest_run_artifact_bundle_report(
        manifest,
        error_prefix=error_prefix,
    )


def render_source(
    source: str,
    *,
    path: str | None = None,
    display_limit: int | None = _SHOW_SOURCE_DISPLAY_LIMIT,
    redact: bool = False,
) -> str:
    return _show_source_text(
        source,
        path=path,
        display_limit=display_limit,
        redact=redact,
    )


def bounded_redacted_text(text: str, limit: int = 1000) -> str:
    rendered = redact_sensitive_text(text)
    if len(rendered) <= limit:
        return rendered
    return rendered[:limit] + "...<truncated>"


def _show_runtime_status(run_dir: Path, history_rows: int) -> str:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return "legacy history-only (manifest.json missing)"
    manifest = _read_show_manifest(manifest_path)
    runtime = manifest.get("runtime")
    if runtime is None:
        return "partial best-so-far (manifest runtime missing)"
    if not isinstance(runtime, dict):
        raise RunInspectionError("Malformed manifest.json: runtime must be an object")
    status = runtime.get("status")
    if status not in {"completed", "aborted"}:
        raise RunInspectionError(
            "Malformed manifest.json: runtime.status must be 'completed' or 'aborted'"
        )
    stop_reason = runtime.get("stop_reason")
    if not _is_manifest_runtime_label(stop_reason):
        raise RunInspectionError(
            "Malformed manifest.json: runtime.stop_reason must be a manifest-safe label"
        )
    _validate_show_manifest_history(runtime.get("history"), history_rows)
    if status == "completed":
        return f"completed (stop_reason: {stop_reason})"
    return f"aborted best-so-far (stop_reason: {stop_reason})"


def _validator_boundary_artifact_summary(run_dir: Path) -> str | None:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    validation = validate_run_artifact_validator_boundary_consistency(run_dir)
    if not validation.manifest_policy_present and not validation.issues:
        return None
    if not validation.ok:
        issue = validation.issues[0]
        location = issue.stream or "run artifacts"
        if issue.line_number is not None:
            location = f"{location} line {issue.line_number}"
        raise RunInspectionError(
            "Validator boundary artifact validation failed: "
            f"{location}: {issue.code}: {issue.message}"
        )
    streams = ",".join(validation.checked_streams) or "none"
    return (
        "Validator boundary: "
        f"checked_attempts={validation.checked_attempts}; streams={streams}"
    )


def _run_artifact_bundle_summary(run_dir: Path) -> str | None:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    manifest = _read_show_manifest(manifest_path)
    _validate_manifest_run_artifact_bundle_report(
        manifest,
        error_prefix="Run artifact bundle validation failed",
    )
    artifact_schema = manifest.get("artifact_schema")
    if not isinstance(artifact_schema, dict):
        return None
    accepted_streams = _present_schema_jsonl_streams(run_dir, artifact_schema)
    quarantine = _validate_quarantine_streams(run_dir, artifact_schema)
    non_jsonl_checked = 0
    if "non_jsonl_artifacts" in artifact_schema:
        validation = validate_non_jsonl_artifact_policy_manifest(manifest)
        if not validation["ok"]:
            issue = validation["issues"][0]
            raise RunInspectionError(
                "Run artifact bundle validation failed: "
                "Non-JSONL artifact policy validation failed: "
                f"{issue['code']}: {issue['message']}"
            )
        non_jsonl_checked = validation["checked_artifact_count"]
    if (
        not accepted_streams
        and quarantine["stream_count"] == 0
        and non_jsonl_checked == 0
    ):
        return None
    return (
        "Run artifact bundle: "
        f"accepted_streams={len(accepted_streams)}; "
        f"quarantine_streams={quarantine['stream_count']}; "
        f"quarantine_records={quarantine['record_count']}; "
        f"non_jsonl_checked={non_jsonl_checked}; "
    )


def _present_schema_jsonl_streams(run_dir: Path, artifact_schema: dict) -> list[str]:
    jsonl_schema = artifact_schema.get("jsonl_records")
    if not isinstance(jsonl_schema, dict):
        return []
    streams = []
    for stream_name in sorted(jsonl_schema):
        if not isinstance(stream_name, str) or not stream_name:
            raise RunInspectionError(
                "Malformed manifest.json: JSONL stream names must be "
                "non-empty strings"
            )
        if (run_dir / stream_name).exists():
            streams.append(stream_name)
    return streams


def _quarantine_stream_summary(run_dir: Path) -> str | None:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    manifest = _read_show_manifest(manifest_path)
    artifact_schema = manifest.get("artifact_schema")
    if (
        not isinstance(artifact_schema, dict)
        or "quarantine_jsonl_records" not in artifact_schema
    ):
        return None
    quarantine = _validate_quarantine_streams(run_dir, artifact_schema)
    if quarantine["stream_count"] == 0:
        return None
    streams = ",".join(quarantine["streams"])
    return (
        "Quarantine streams: "
        f"checked={quarantine['stream_count']}; "
        f"records={quarantine['record_count']}; "
        f"streams={streams}"
    )


def _validate_quarantine_streams(run_dir: Path, artifact_schema: dict) -> dict:
    validation = validate_quarantine_artifact_policy_manifest(
        {"artifact_schema": artifact_schema},
        run_dir=run_dir,
    )
    if not validation["ok"]:
        issue = validation["issues"][0]
        raise RunInspectionError(
            "Quarantine stream validation failed: "
            f"{issue['code']}: {bounded_redacted_text(issue['message'])}"
        )
    return {
        "stream_count": validation["checked_stream_count"],
        "record_count": validation["record_count"],
        "streams": validation["present_streams"],
    }


def _non_jsonl_artifact_policy_summary(run_dir: Path) -> str | None:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    manifest = _read_show_manifest(manifest_path)
    artifact_schema = manifest.get("artifact_schema")
    if (
        not isinstance(artifact_schema, dict)
        or "non_jsonl_artifacts" not in artifact_schema
    ):
        return None
    validation = validate_non_jsonl_artifact_policy_manifest(manifest)
    if not validation["ok"]:
        issue = validation["issues"][0]
        raise RunInspectionError(
            "Non-JSONL artifact policy validation failed: "
            f"{issue['code']}: {issue['message']}"
        )
    return (
        "Non-JSONL artifacts: "
        f"checked={validation['checked_artifact_count']}"
    )


def run_artifacts_doc_text() -> str | None:
    """Read the checkout guide when present; installed packages may omit it."""
    doc_path = Path(__file__).resolve().parents[2] / "docs" / "run-artifacts.md"
    try:
        return doc_path.read_text(encoding="utf-8")
    except OSError:
        return None


def _show_archive_cell_upper_bound(run_dir: Path) -> int | None:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    manifest = _read_show_manifest(manifest_path)
    config = manifest.get("config")
    if config is None:
        return None
    if not isinstance(config, dict):
        raise RunInspectionError("Malformed manifest.json: config must be an object")
    bins = config.get("map_elites_bins")
    if bins is None:
        return None
    if isinstance(bins, bool) or not isinstance(bins, int) or bins < 1:
        raise RunInspectionError(
            "Malformed manifest.json: config.map_elites_bins must be a positive integer"
        )
    return bins


def _read_show_manifest(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise RunInspectionError(
            f"Malformed manifest.json: invalid UTF-8 ({exc.reason})"
        ) from exc
    except OSError as exc:
        raise RunInspectionError(f"Failed to read manifest.json: {exc}") from exc
    try:
        manifest = json.loads(text, object_pairs_hook=_reject_duplicate_history_json_names)
    except _DuplicateHistoryJsonNameError as exc:
        raise RunInspectionError(f"Malformed manifest.json: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RunInspectionError(f"Malformed manifest.json: {exc.msg}") from exc
    if not isinstance(manifest, dict):
        raise RunInspectionError("Malformed manifest.json: expected JSON object")
    return manifest


def _validate_show_manifest_history(history: object, history_rows: int) -> None:
    if history is None:
        return
    if not isinstance(history, dict):
        raise RunInspectionError("Malformed manifest.json: runtime.history must be an object")
    programs_logged = history.get("programs_logged")
    if programs_logged is None:
        return
    if (
        isinstance(programs_logged, bool)
        or not isinstance(programs_logged, int)
        or programs_logged < 0
    ):
        raise RunInspectionError(
            "Malformed manifest.json: runtime.history.programs_logged "
            "must be a non-negative integer"
        )
    if programs_logged != history_rows:
        raise RunInspectionError(
            "Inconsistent manifest.json/runtime history: "
            f"programs_logged={programs_logged} but history.jsonl has {history_rows} row(s)"
        )


def _is_manifest_runtime_label(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if redact_sensitive_text(value) != value:
        return False
    return re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value) is not None

def _validate_manifest_run_artifact_bundle_report(
    manifest: dict,
    *,
    error_prefix: str,
) -> None:
    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        return
    report = runtime.get("run_artifact_bundle_report")
    if report is None:
        return
    validation = validate_run_artifact_bundle_report(report)
    if validation["ok"]:
        return
    issue = validation["issues"][0]
    raise RunInspectionError(
        f"{error_prefix}: run artifact bundle report validation failed: "
        f"{issue['code']}: {issue['message']}"
    )


def _has_archive_metadata(record: dict) -> bool:
    return isinstance(record.get("metadata"), dict) and "archive_admission" in record["metadata"]


def _raise_mixed_history_schema(
    line_number: int, first_legacy_line: int, first_modern_line: int
) -> None:
    raise RunInspectionError(
        "Malformed history.jsonl at line "
        f"{line_number}: mixed legacy/current history schemas "
        f"(first legacy row line {first_legacy_line}, "
        f"first archive_admission row line {first_modern_line})"
    )


def _iter_history_records(path: Path, *, archive_cell_upper_bound: int | None = None):
    try:
        handle = path.open("rb")
    except OSError as exc:
        raise RunInspectionError(f"Failed to read history.jsonl: {exc}") from exc
    seen_ids: dict[str, int] = {}
    with handle:
        for line_number, raw_line in enumerate(handle, start=1):
            try:
                line = raw_line.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise RunInspectionError(
                    "Malformed history.jsonl at line "
                    f"{line_number}: invalid UTF-8 ({exc.reason})"
                ) from exc
            if not line.strip():
                continue
            try:
                record = json.loads(
                    line,
                    object_pairs_hook=_reject_duplicate_history_json_names,
                )
            except _DuplicateHistoryJsonNameError as exc:
                raise RunInspectionError(
                    f"Malformed history.jsonl at line {line_number}: {exc}"
                ) from exc
            except json.JSONDecodeError as exc:
                raise RunInspectionError(
                    f"Malformed history.jsonl at line {line_number}: {exc.msg}"
                ) from exc
            if not isinstance(record, dict):
                raise RunInspectionError(
                    f"Malformed history.jsonl at line {line_number}: expected JSON object"
                )
            _validate_history_fitness(record, line_number)
            _validate_history_generation(record, line_number)
            _validate_history_identity(record, line_number, seen_ids)
            _validate_history_metrics(record, line_number)
            _validate_history_display_payload(record, line_number)
            if _has_archive_metadata(record):
                _validate_current_history_record(
                    record,
                    line_number,
                    archive_cell_upper_bound=archive_cell_upper_bound,
                )
            yield line_number, record


class _DuplicateHistoryJsonNameError(ValueError):
    pass


def _reject_duplicate_history_json_names(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateHistoryJsonNameError(
                f"duplicate JSON object name {key!r}"
            )
        result[key] = value
    return result


def _validate_history_fitness(record: dict, line_number: int) -> None:
    fitness = record.get("fitness")
    if (
        isinstance(fitness, bool)
        or not isinstance(fitness, (int, float))
        or not math.isfinite(float(fitness))
    ):
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: fitness must be a finite number"
        )


def _validate_history_generation(record: dict, line_number: int) -> None:
    generation = record.get("generation")
    if isinstance(generation, bool) or not isinstance(generation, int) or generation < 0:
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: generation must be a non-negative integer"
        )


def _validate_history_identity(
    record: dict, line_number: int, seen_ids: dict[str, int]
) -> None:
    try:
        validate_program_identity(record.get("id"), record.get("parent_id"), record.get("lineage"))
    except ValueError as exc:
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: {exc}"
        ) from exc
    program_id = record["id"]
    if program_id in seen_ids:
        raise RunInspectionError(
            "Malformed history.jsonl at line "
            f"{line_number}: duplicate program id {program_id!r} "
            f"(first seen at line {seen_ids[program_id]})"
        )
    seen_ids[program_id] = line_number


def _validate_history_metrics(record: dict, line_number: int) -> None:
    metrics = record.get("metrics")
    if metrics is None:
        return
    if not isinstance(metrics, dict):
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: metrics must be an object"
        )
    try:
        record["metrics"] = validate_program_metrics(metrics)
    except ValueError as exc:
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: {exc}"
        ) from exc


def _validate_history_display_payload(record: dict, line_number: int) -> None:
    _history_record_workspace(record, line_number)


def _validate_current_history_record(
    record: dict,
    line_number: int,
    *,
    archive_cell_upper_bound: int | None = None,
) -> None:
    metadata = record.get("metadata")
    assert isinstance(metadata, dict)
    admission = metadata.get("archive_admission")
    if not isinstance(admission, dict):
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: archive_admission must be an object"
        )
    _validate_archive_admission_program_id(record, admission, line_number)
    evaluation = record.get("evaluation")
    if evaluation is not None and not isinstance(evaluation, dict):
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: evaluation must be an object"
        )
    if isinstance(evaluation, dict) and "is_valid" in evaluation and not isinstance(
        evaluation["is_valid"], bool
    ):
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: evaluation.is_valid must be a boolean"
        )
    admitted = _archive_bool(admission, "admitted", line_number)
    cell_admitted = _archive_bool(
        admission,
        "cell_admitted",
        line_number,
        fallback=admission.get("entered_cell"),
    )
    elite_retained = _archive_bool(
        admission,
        "elite_retained",
        line_number,
        fallback=admission.get("entered_elite"),
    )
    search_state_changed = _archive_bool(
        admission,
        "search_state_changed",
        line_number,
    )
    sampling_eligible = _archive_bool(
        admission,
        "sampling_eligible",
        line_number,
    )
    flags = [
        cell_admitted,
        elite_retained,
        search_state_changed,
        sampling_eligible,
    ]
    if admitted is True and any(flag is not None for flag in flags) and not any(
        flag is True for flag in flags
    ):
        raise RunInspectionError(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.admitted is true but no "
            "retention/search-state flag is true"
        )
    _archive_summary(
        record,
        line_number,
        archive_cell_upper_bound=archive_cell_upper_bound,
    )


def _validate_archive_admission_program_id(
    record: dict, admission: dict, line_number: int
) -> None:
    admission_program_id = admission.get("program_id")
    if admission_program_id is None:
        return
    try:
        validate_program_identity(admission_program_id)
    except ValueError as exc:
        raise RunInspectionError(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.program_id must be a "
            "manifest-safe identifier"
        ) from exc
    if admission_program_id != record["id"]:
        raise RunInspectionError(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.program_id must match history row id"
        )


def _validate_display_record(record: dict, line_number: int) -> None:
    program_id = record.get("id")
    if not isinstance(program_id, str) or not program_id:
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: id must be a non-empty string"
        )
    generation = record.get("generation")
    if isinstance(generation, bool) or not isinstance(generation, int) or generation < 0:
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: generation must be a non-negative integer"
        )
    metrics = record.get("metrics")
    if metrics is not None and not isinstance(metrics, dict):
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: metrics must be an object"
        )


def _history_record_workspace(record: dict, line_number: int) -> tuple[str, dict[str, str]] | None:
    files = record.get("files")
    if files is None:
        code = record.get("code")
        if not isinstance(code, str):
            raise RunInspectionError(
                f"Malformed history.jsonl at line {line_number}: code must be a string"
            )
        return None
    if not isinstance(files, dict):
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: files must be an object"
        )
    primary_file = record.get("primary_file", "main.py")
    if not isinstance(primary_file, str):
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: primary_file must be a string"
        )
    if primary_file not in files:
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: primary_file missing from files"
        )
    normalized: dict[str, str] = {}
    for path, content in files.items():
        if not isinstance(path, str) or not isinstance(content, str):
            raise RunInspectionError(
                f"Malformed history.jsonl at line {line_number}: files must map strings to strings"
            )
        normalized[path] = content
    path_policy = record.get("workspace_path_policy")
    allowed_reserved_paths = []
    if isinstance(path_policy, dict):
        raw_allowed = path_policy.get("allowed_reserved_paths", [])
        if isinstance(raw_allowed, list) and all(isinstance(item, str) for item in raw_allowed):
            allowed_reserved_paths = raw_allowed
    try:
        workspace = CandidateWorkspace(
            normalized,
            primary_file,
            allowed_reserved_paths=frozenset(allowed_reserved_paths),
        )
    except ValueError as exc:
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: {exc}"
        ) from exc
    return workspace.primary_file, dict(workspace.files)


def _select_better_record(current, candidate, key):
    if current is None or key(candidate) > key(current):
        return candidate
    return current


def _is_archive_admitted_valid(record: dict) -> bool:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    admission = metadata.get("archive_admission") if isinstance(metadata, dict) else None
    evaluation = record.get("evaluation") if isinstance(record.get("evaluation"), dict) else {}
    return (
        isinstance(admission, dict)
        and admission.get("admitted") is True
        and evaluation.get("is_valid") is True
    )


def _record_selection_key(record: dict) -> tuple[float, float]:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    admission = metadata.get("archive_admission") if isinstance(metadata, dict) else {}
    raw = None
    if isinstance(admission, dict):
        raw = admission.get("selection_score")
    if not isinstance(raw, (int, float)) or isinstance(raw, bool):
        raw = metadata.get("selection_score") if isinstance(metadata, dict) else None
    selection_score = (
        float(raw)
        if isinstance(raw, (int, float)) and not isinstance(raw, bool) and math.isfinite(float(raw))
        else None
    )
    if selection_score is None:
        selection_score = float(record.get("fitness", float("-inf")))
    return (selection_score, float(record.get("fitness", float("-inf"))))


def _archive_summary(
    record: dict,
    line_number: int,
    *,
    archive_cell_upper_bound: int | None = None,
) -> str | None:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    admission = metadata.get("archive_admission") if isinstance(metadata, dict) else None
    if not isinstance(admission, dict):
        return None
    parts = []
    raw_selection_score = admission.get("selection_score")
    if raw_selection_score is not None and (
        isinstance(raw_selection_score, bool)
        or not isinstance(raw_selection_score, (int, float))
        or not math.isfinite(float(raw_selection_score))
    ):
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: archive_admission.selection_score must be a finite number"
        )
    if (
        isinstance(raw_selection_score, (int, float))
        and not isinstance(raw_selection_score, bool)
        and math.isfinite(float(raw_selection_score))
    ):
        parts.append(f"selection_score={float(raw_selection_score):.6f}")
    cell_admitted = _archive_bool(
        admission,
        "cell_admitted",
        line_number,
        fallback=admission.get("entered_cell"),
    )
    if cell_admitted is not None:
        parts.append(f"cell_admitted={cell_admitted}")
    elite_retained = _archive_bool(
        admission,
        "elite_retained",
        line_number,
        fallback=admission.get("entered_elite"),
    )
    if elite_retained is not None:
        parts.append(f"elite_retained={elite_retained}")
    search_state_changed = _archive_bool(
        admission,
        "search_state_changed",
        line_number,
        fallback=admission.get("admitted"),
    )
    if search_state_changed is not None:
        parts.append(f"search_state_changed={search_state_changed}")
    sampling_eligible = _archive_bool(
        admission,
        "sampling_eligible",
        line_number,
        fallback=admission.get("entered_cell"),
    )
    if sampling_eligible is not None:
        parts.append(f"sampling_eligible={sampling_eligible}")
    island_id = admission.get("island_id")
    if island_id is not None:
        if isinstance(island_id, bool) or not isinstance(island_id, int) or island_id < 0:
            raise RunInspectionError(
                f"Malformed history.jsonl at line {line_number}: archive_admission.island_id must be a non-negative integer"
            )
        parts.append(f"island={island_id}")
    cell = admission.get("cell")
    if cell is not None:
        if (
            not isinstance(cell, list)
            or len(cell) != 3
            or any(
                isinstance(value, bool) or not isinstance(value, int) or value < 0
                for value in cell
            )
        ):
            raise RunInspectionError(
                f"Malformed history.jsonl at line {line_number}: archive_admission.cell must be a list of three non-negative integers"
            )
        if archive_cell_upper_bound is not None and any(
            value >= archive_cell_upper_bound for value in cell
        ):
            raise RunInspectionError(
                "Malformed history.jsonl at line "
                f"{line_number}: archive_admission.cell values must be less "
                "than manifest config.map_elites_bins "
                f"({archive_cell_upper_bound})"
            )
        parts.append(f"cell={cell}")
    descriptors = _validate_archive_descriptors(
        admission.get("descriptors"), line_number
    )
    if descriptors:
        parts.extend(_archive_descriptor_parts(descriptors))
    parts.extend(
        _archive_objective_vector_parts(
            admission.get("objective_vector"),
            line_number,
        )
    )
    return f"Archive:        {'; '.join(parts)}" if parts else None


def _archive_objective_vector_parts(value: object, line_number: int) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, dict):
        raise RunInspectionError(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.objective_vector must be an object or null"
        )
    allowed = {"policy", "normalized_metrics", "selection_policy"}
    unsupported = sorted(set(value) - allowed)
    if unsupported:
        raise RunInspectionError(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.objective_vector has unsupported fields: {unsupported}"
        )
    if value.get("policy") != "normalized_declared_metric_vector_v1":
        raise RunInspectionError(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.objective_vector.policy is unsupported"
        )
    raw_metrics = value.get("normalized_metrics")
    if not isinstance(raw_metrics, dict):
        raise RunInspectionError(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.objective_vector.normalized_metrics must be an object"
        )
    metrics: dict[str, float] = {}
    for name, score in raw_metrics.items():
        try:
            validate_program_metrics({name: 0.0})
        except ValueError as exc:
            raise RunInspectionError(
                "Malformed history.jsonl at line "
                f"{line_number}: archive_admission.objective_vector metric names must be manifest-safe metric names"
            ) from exc
        if (
            isinstance(score, bool)
            or not isinstance(score, (int, float))
            or not math.isfinite(float(score))
            or not 0.0 <= float(score) <= 1.0
        ):
            raise RunInspectionError(
                "Malformed history.jsonl at line "
                f"{line_number}: archive_admission.objective_vector metric values must be finite normalized scores"
            )
        metrics[name] = float(score)
    selection_policy = value.get("selection_policy")
    if selection_policy is not None and not isinstance(selection_policy, dict):
        raise RunInspectionError(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.objective_vector.selection_policy must be an object"
        )
    parts = _objective_metric_vector_parts(metrics)
    if isinstance(selection_policy, dict):
        policy_type = selection_policy.get("type")
        if policy_type is not None:
            if not _is_manifest_runtime_label(policy_type):
                raise RunInspectionError(
                    "Malformed history.jsonl at line "
                    f"{line_number}: archive_admission.objective_vector.selection_policy.type must be a manifest-safe label"
                )
            parts.append(f"objective_policy={policy_type}")
    return parts


def _objective_metric_vector_parts(metrics: dict[str, float]) -> list[str]:
    rendered = json.dumps(metrics, sort_keys=True, allow_nan=False)
    if (
        len(metrics) <= _ARCHIVE_DESCRIPTOR_PREVIEW_LIMIT
        and len(rendered) <= _ARCHIVE_DESCRIPTOR_JSON_DISPLAY_LIMIT
        and all(
            len(name) <= _ARCHIVE_DESCRIPTOR_LABEL_DISPLAY_LIMIT
            for name in metrics
        )
    ):
        return [f"objective_metrics={rendered}"]
    canonical = json.dumps(
        metrics,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    preview = {
        _descriptor_preview_label(name): value
        for name, value in sorted(metrics.items())[:_ARCHIVE_DESCRIPTOR_PREVIEW_LIMIT]
    }
    omitted = max(0, len(metrics) - len(preview))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return [
        f"objective_metrics_count={len(metrics)}",
        f"objective_metrics_preview={json.dumps(preview, sort_keys=True, allow_nan=False)}",
        f"objective_metrics_omitted={omitted}",
        f"objective_metrics_sha256={digest}",
    ]


def _validate_archive_descriptors(
    descriptors: object, line_number: int
) -> dict[str, int | float] | None:
    if descriptors is None:
        return None
    if not isinstance(descriptors, dict):
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: archive_admission.descriptors must map strings to finite numbers"
        )
    normalized: dict[str, int | float] = {}
    for name, value in descriptors.items():
        try:
            validate_program_metrics({name: 0.0})
        except ValueError as exc:
            raise RunInspectionError(
                "Malformed history.jsonl at line "
                f"{line_number}: archive_admission.descriptor names must be "
                "manifest-safe metric names"
            ) from exc
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
        ):
            raise RunInspectionError(
                f"Malformed history.jsonl at line {line_number}: archive_admission.descriptors must map strings to finite numbers"
            )
        normalized[name] = value
    return normalized


def _archive_descriptor_parts(descriptors: dict[str, int | float]) -> list[str]:
    rendered = json.dumps(descriptors, sort_keys=True, allow_nan=False)
    if (
        len(descriptors) <= _ARCHIVE_DESCRIPTOR_PREVIEW_LIMIT
        and len(rendered) <= _ARCHIVE_DESCRIPTOR_JSON_DISPLAY_LIMIT
        and all(
            len(name) <= _ARCHIVE_DESCRIPTOR_LABEL_DISPLAY_LIMIT
            for name in descriptors
        )
    ):
        return [f"descriptors={rendered}"]
    canonical = json.dumps(
        descriptors,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    preview = {
        _descriptor_preview_label(name): value
        for name, value in sorted(descriptors.items())[
            :_ARCHIVE_DESCRIPTOR_PREVIEW_LIMIT
        ]
    }
    omitted = max(0, len(descriptors) - len(preview))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return [
        f"descriptors_count={len(descriptors)}",
        f"descriptors_preview={json.dumps(preview, sort_keys=True, allow_nan=False)}",
        f"descriptors_omitted={omitted}",
        f"descriptors_sha256={digest}",
    ]


def _descriptor_preview_label(name: str) -> str:
    if len(name) <= _ARCHIVE_DESCRIPTOR_LABEL_DISPLAY_LIMIT:
        return name
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]
    prefix_len = _ARCHIVE_DESCRIPTOR_LABEL_DISPLAY_LIMIT - len(digest) - 4
    return f"{name[:prefix_len]}...{digest}"


def _archive_bool(
    admission: dict, field: str, line_number: int, *, fallback: object = None
) -> bool | None:
    raw = admission.get(field, fallback)
    if raw is None:
        return None
    if not isinstance(raw, bool):
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: archive_admission.{field} must be a boolean"
        )
    return raw


def _lineage_summary(record: dict) -> str | None:
    parent_id = record.get("parent_id")
    lineage = record.get("lineage")
    if parent_id is None and lineage is None:
        return None
    parts = [f"parent={parent_id if parent_id is not None else '<root>'}"]
    if isinstance(lineage, list):
        parts.append(f"lineage_depth={len(lineage)}")
        if lineage:
            tail = lineage[-3:]
            prefix = "..." if len(lineage) > len(tail) else ""
            parts.append(f"lineage_tail={prefix}{'->'.join(tail)}")
    return f"Lineage:       {'; '.join(parts)}"


def _prompt_summary(record: dict, line_number: int) -> str | None:
    metadata = record.get("metadata")
    if not isinstance(metadata, dict):
        return None
    parts: list[str] = []
    prompt_program_id = metadata.get("prompt_program_id")
    if prompt_program_id is not None:
        try:
            validate_program_identity(prompt_program_id)
        except ValueError as exc:
            raise RunInspectionError(
                f"Malformed history.jsonl at line {line_number}: prompt_program_id must be a manifest-safe identifier"
            ) from exc
        parts.append(f"prompt_program_id={prompt_program_id}")
    parent_selection = metadata.get("parent_selection")
    if parent_selection is not None:
        if not isinstance(parent_selection, dict):
            raise RunInspectionError(
                f"Malformed history.jsonl at line {line_number}: parent_selection must be an object"
            )
        strategy = parent_selection.get("strategy")
        if strategy is not None:
            if not _is_manifest_runtime_label(strategy):
                raise RunInspectionError(
                    f"Malformed history.jsonl at line {line_number}: parent_selection.strategy must be a manifest-safe label"
                )
            parts.append(f"parent_strategy={strategy}")
        selected = parent_selection.get("selected_program_id")
        if selected is not None:
            try:
                validate_program_identity(selected)
            except ValueError as exc:
                raise RunInspectionError(
                    f"Malformed history.jsonl at line {line_number}: parent_selection.selected_program_id must be a manifest-safe identifier"
                ) from exc
            parts.append(f"selected_parent={selected}")
        target_metric = parent_selection.get("target_metric")
        if target_metric is not None:
            try:
                validate_program_metrics({target_metric: 0.0})
            except ValueError as exc:
                raise RunInspectionError(
                    f"Malformed history.jsonl at line {line_number}: parent_selection.target_metric must be a manifest-safe metric name"
                ) from exc
            parts.append(f"target_metric={target_metric}")
    return f"Prompt:        {'; '.join(parts)}" if parts else None


def _evaluation_diagnostics_summary(record: dict, line_number: int) -> str | None:
    evaluation = record.get("evaluation")
    if not isinstance(evaluation, dict):
        return None
    parts: list[str] = []
    if "is_valid" in evaluation:
        parts.append(f"is_valid={evaluation['is_valid']}")
    stages = evaluation.get("stages")
    if stages is not None:
        if not isinstance(stages, list):
            raise RunInspectionError(
                f"Malformed history.jsonl at line {line_number}: evaluation.stages must be a list"
            )
        failed = []
        for index, stage in enumerate(stages):
            if not isinstance(stage, dict):
                raise RunInspectionError(
                    f"Malformed history.jsonl at line {line_number}: evaluation.stages[{index}] must be an object"
                )
            passed = stage.get("passed")
            if passed is not None and not isinstance(passed, bool):
                raise RunInspectionError(
                    f"Malformed history.jsonl at line {line_number}: evaluation.stages[{index}].passed must be a boolean"
                )
            if passed is False:
                failed.append(_stage_failure_label(stage, index))
        parts.append(f"stages={len(stages)}")
        parts.append(f"failed={len(failed)}")
        if failed:
            parts.append(
                "failed_stages="
                + ",".join(failed[:_SHOW_DIAGNOSTIC_BUCKET_LIMIT])
            )
    accounting = evaluation.get("accounting")
    if accounting is not None:
        if not isinstance(accounting, dict):
            raise RunInspectionError(
                f"Malformed history.jsonl at line {line_number}: evaluation.accounting must be an object"
            )
        for key in (
            "configured_stage_samples",
            "subprocess_attempts",
            "retry_attempts",
            "timeout_count",
            "sample_budget_exhaustions",
            "stage_budget_exhaustions",
        ):
            value = accounting.get(key)
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise RunInspectionError(
                    f"Malformed history.jsonl at line {line_number}: evaluation.accounting.{key} must be a non-negative integer"
                )
            parts.append(f"{key}={value}")
    return f"Evaluation:    {'; '.join(parts)}" if parts else None


def _stage_failure_label(stage: dict, index: int) -> str:
    name = stage.get("name")
    if not isinstance(name, str) or not name:
        name = f"stage_{index}"
    error = stage.get("error")
    if isinstance(error, str) and error:
        return (
            f"{_diagnostic_label(name)}:{_diagnostic_label(error)}"
        )
    return _diagnostic_label(name)


def _feedback_summary(record: dict, line_number: int) -> str | None:
    evaluation = record.get("evaluation")
    if not isinstance(evaluation, dict):
        return None
    metadata = evaluation.get("metadata")
    if not isinstance(metadata, dict):
        return None
    feedback = metadata.get("llm_feedback")
    if feedback is None:
        return None
    if not isinstance(feedback, list):
        raise RunInspectionError(
            f"Malformed history.jsonl at line {line_number}: evaluation.metadata.llm_feedback must be a list"
        )
    applied: list[str] = []
    failed: list[str] = []
    weighted_delta = 0.0
    for index, item in enumerate(feedback):
        if not isinstance(item, dict):
            raise RunInspectionError(
                f"Malformed history.jsonl at line {line_number}: evaluation.metadata.llm_feedback[{index}] must be an object"
            )
        name = _diagnostic_label(str(item.get("name", f"feedback_{index}")))
        error = item.get("error")
        if isinstance(error, str) and error:
            failed.append(f"{name}:{_diagnostic_label(error)}")
        else:
            applied.append(name)
        delta = item.get("weighted_delta")
        if isinstance(delta, (int, float)) and not isinstance(delta, bool) and math.isfinite(float(delta)):
            weighted_delta += float(delta)
    parts = [f"llm_feedback={len(feedback)}"]
    if applied:
        parts.append(
            "applied=" + ",".join(applied[:_SHOW_DIAGNOSTIC_BUCKET_LIMIT])
        )
    if failed:
        parts.append(
            "failed=" + ",".join(failed[:_SHOW_DIAGNOSTIC_BUCKET_LIMIT])
        )
    if weighted_delta:
        parts.append(f"weighted_delta={weighted_delta:.6f}")
    return f"Feedback:      {'; '.join(parts)}"


def _failure_statistics_summary(run_dir: Path) -> str | None:
    failure_path = run_dir / "failure_history.jsonl"
    if not failure_path.exists():
        return None
    try:
        from libreevolve.core.database import (
            HistoryRestoreError,
            load_failure_history_records,
        )

        records = load_failure_history_records(failure_path)
    except HistoryRestoreError as exc:
        raise RunInspectionError(str(exc)) from exc
    admission_reasons: dict[str, int] = {}
    errors: dict[str, int] = {}
    repeated_records = 0
    for record in records:
        _increment_bucket(admission_reasons, record.get("admission_reason"))
        _increment_bucket(errors, record.get("error"))
        repetition_count = record.get("repetition_count")
        if (
            isinstance(repetition_count, int)
            and not isinstance(repetition_count, bool)
            and repetition_count > 1
        ):
            repeated_records += 1
    parts = [f"total={len(records)}"]
    rendered_admission = _render_count_buckets(admission_reasons)
    if rendered_admission:
        parts.append(f"admission_reasons={rendered_admission}")
    rendered_errors = _render_count_buckets(errors)
    if rendered_errors:
        parts.append(f"errors={rendered_errors}")
    if repeated_records:
        parts.append(f"repeated_records={repeated_records}")
    return f"Failures:      {'; '.join(parts)}"


def _increment_bucket(buckets: dict[str, int], value: object) -> None:
    if not isinstance(value, str) or not value:
        value = "<none>"
    buckets[_diagnostic_label(value)] = buckets.get(_diagnostic_label(value), 0) + 1


def _render_count_buckets(buckets: dict[str, int]) -> str:
    if not buckets:
        return ""
    items = sorted(buckets.items(), key=lambda item: (-item[1], item[0]))
    rendered = ",".join(
        f"{label}:{count}" for label, count in items[:_SHOW_DIAGNOSTIC_BUCKET_LIMIT]
    )
    omitted = len(items) - _SHOW_DIAGNOSTIC_BUCKET_LIMIT
    if omitted > 0:
        rendered += f",+{omitted}_more"
    return rendered


def _diagnostic_label(value: str) -> str:
    safe = redact_sensitive_text(value).strip()
    safe = re.sub(r"\s+", "_", safe)
    if not safe:
        safe = "<empty>"
    if len(safe) <= _SHOW_DIAGNOSTIC_LABEL_DISPLAY_LIMIT:
        return safe
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]
    keep = _SHOW_DIAGNOSTIC_LABEL_DISPLAY_LIMIT - len(digest) - 4
    return f"{safe[:keep]}...{digest}"


def _show_source_text(
    source: str,
    *,
    path: str | None = None,
    display_limit: int | None = _SHOW_SOURCE_DISPLAY_LIMIT,
    redact: bool = False,
) -> str:
    rendered = redact_sensitive_text(source) if redact else source
    if display_limit is None or len(rendered) <= display_limit:
        return rendered
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
    omitted = len(rendered) - display_limit
    label = f" for {path}" if path is not None else ""
    redacted_line = "\nsource_redacted=True" if redact and rendered != source else ""
    notice = (
        "\n\n--- libreevolve show source truncated ---\n"
        f"source_truncated=True{label}{redacted_line}\n"
        f"source_chars={len(source)}\n"
        f"rendered_chars={len(rendered)}\n"
        f"displayed_chars={display_limit}\n"
        f"omitted_chars={omitted}\n"
        f"source_sha256={digest}\n"
        "full_source=history.jsonl"
    )
    return rendered[:display_limit] + notice
