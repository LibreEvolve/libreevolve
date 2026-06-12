from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


NATURAL_LANGUAGE_PREAMBLE_BOUNDARY_SCHEMA = (
    "libreevolve.natural_language_preamble_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_RUNTIME_REPORT_SCHEMA = "libreevolve.natural_language_preamble_report.v1"
EXPECTED_BOUNDARY_STATUS = "bounded_leading_preamble_capture_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "bounded_leading_explanatory_preamble_capture",
    "redacted_preamble_preview_and_hash",
    "structured_proposal_metadata_interop",
    "structured_mutation_marker_boundary",
    "interleaved_or_trailing_prose_rejection",
    "diff_file_block_leading_preamble_support",
    "candidate_status_counts",
    "mutation_mode_counts",
    "configurable_preamble_policy_controls",
    "raw_full_replacement_preamble_disambiguation",
    "semantic_rationale_quality_scoring",
    "cross_run_preamble_table",
    "preamble_to_proposal_memory_joins",
    "arbitrary_unparsed_rationale_acceptance_policy",
)
EXPECTED_MISSING_EVIDENCE = {
    "configurable_preamble_policy_controls": "not_recorded_locally",
    "raw_full_replacement_preamble_disambiguation": "not_recorded_locally",
    "semantic_rationale_quality_scoring": "not_recorded_locally",
    "cross_run_preamble_table": "not_recorded_locally",
    "preamble_to_proposal_memory_joins": "not_recorded_locally",
    "arbitrary_unparsed_rationale_acceptance_policy": "not_recorded_locally",
}


@dataclass(frozen=True)
class NaturalLanguagePreambleBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class NaturalLanguagePreambleBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[NaturalLanguagePreambleBoundaryIssue]


def natural_language_preamble_boundary_record() -> dict[str, Any]:
    """Return the bounded-preamble versus complete rationale-handling boundary."""

    return {
        "schema": NATURAL_LANGUAGE_PREAMBLE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve mutation responses may include natural-language "
            "explanation before SEARCH/REPLACE edit payloads while the edits "
            "remain structured diff blocks"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_schema": EXPECTED_RUNTIME_REPORT_SCHEMA,
        "runtime_report_status": "natural_language_preamble_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve manifests include "
            "runtime.history.natural_language_preamble_report for bounded, "
            "redacted leading explanatory text before the first structured "
            "mutation marker, with structured proposal metadata interop, "
            "diff/file/block leading-preamble support, status/mode counts, and "
            "rejection of prose between or after mutation sections. It does "
            "not claim configurable preamble policy controls, raw full-"
            "replacement preamble disambiguation, semantic rationale-quality "
            "scoring, cross-run preamble tables, preamble-to-proposal-memory "
            "joins, or arbitrary unparsed rationale acceptance."
        ),
    }


def validate_natural_language_preamble_boundary(
    boundary: object | str | Path | None = None,
) -> NaturalLanguagePreambleBoundaryValidation:
    data, read_issues = _load_boundary(
        natural_language_preamble_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return NaturalLanguagePreambleBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[NaturalLanguagePreambleBoundaryIssue] = []
    if data.get("schema") != NATURAL_LANGUAGE_PREAMBLE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported natural-language preamble boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "natural-language explanation" not in source_claim
        or "SEARCH/REPLACE" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify explanatory prose before SEARCH/REPLACE payloads"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_schema") != EXPECTED_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", f"runtime_report_schema must be {EXPECTED_RUNTIME_REPORT_SCHEMA}"))
    if data.get("runtime_report_status") != "natural_language_preamble_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to bounded preamble telemetry"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "natural-language preamble boundary must not claim complete rationale handling"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim configurable preamble policy controls" not in boundary_text
        or "semantic rationale-quality scoring" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded preamble capture from complete rationale handling"))
    return NaturalLanguagePreambleBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_natural_language_preamble_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_natural_language_preamble_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Natural-language preamble boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[NaturalLanguagePreambleBoundaryIssue]]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")]
    else:
        try:
            data = json.loads(Path(boundary).read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")]
    if isinstance(data, dict):
        return data, []
    return None, [_issue("invalid_shape", "natural-language preamble boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[NaturalLanguagePreambleBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_required_evidence_field", f"missing required evidence fields: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_required_evidence_field", f"unknown required evidence fields: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[NaturalLanguagePreambleBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_missing_evidence_key", f"missing_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_missing_evidence_key", f"missing_evidence has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _issue(code: str, message: str) -> NaturalLanguagePreambleBoundaryIssue:
    return NaturalLanguagePreambleBoundaryIssue(code, message)
