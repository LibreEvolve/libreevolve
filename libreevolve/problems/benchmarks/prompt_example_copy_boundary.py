from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROMPT_EXAMPLE_COPY_BOUNDARY_SCHEMA = "libreevolve.prompt_example_copy_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_RUNTIME_REPORT_SCHEMA = "libreevolve.prompt_example_copy_report.v1"
EXPECTED_BOUNDARY_STATUS = "built_in_example_copy_diagnostics_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "built_in_example_inventory",
    "exact_copy_signal",
    "normalized_region_copy_signal",
    "example_format_skeleton_signal",
    "candidate_status_counts",
    "mutation_mode_counts",
    "sample_copy_records",
    "hard_or_configurable_rejection_policy",
    "semantic_or_renamed_copy_detection",
    "custom_prompt_template_example_inventory",
    "per_template_example_source_mapping",
    "cross_run_copy_rate_table",
    "copy_signal_to_acceptance_outcome_policy",
    "prompt_example_revision_guidance",
)
EXPECTED_MISSING_EVIDENCE = {
    "hard_or_configurable_rejection_policy": "not_recorded_locally",
    "semantic_or_renamed_copy_detection": "not_recorded_locally",
    "custom_prompt_template_example_inventory": "not_recorded_locally",
    "per_template_example_source_mapping": "not_recorded_locally",
    "cross_run_copy_rate_table": "not_recorded_locally",
    "copy_signal_to_acceptance_outcome_policy": "not_recorded_locally",
    "prompt_example_revision_guidance": "not_recorded_locally",
}


@dataclass(frozen=True)
class PromptExampleCopyBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class PromptExampleCopyBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[PromptExampleCopyBoundaryIssue]


def prompt_example_copy_boundary_record() -> dict[str, Any]:
    """Return the prompt-example copy diagnostics versus enforcement boundary."""

    return {
        "schema": PROMPT_EXAMPLE_COPY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve prompts can include concrete SEARCH/REPLACE examples, "
            "but generated proposals should edit the current program rather "
            "than copying illustrative prompt examples as candidate patches"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_schema": EXPECTED_RUNTIME_REPORT_SCHEMA,
        "runtime_report_status": "prompt_example_copy_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve manifests include "
            "runtime.history.prompt_example_copy_report for built-in mutation "
            "example inventories plus exact, normalized-region, and "
            "example-format skeleton copy diagnostics with candidate status, "
            "mutation mode, and sample record evidence. It does not claim hard "
            "or configurable rejection policy, semantic or renamed copy "
            "detection, custom prompt-template example inventories, "
            "per-template source mapping, cross-run copy-rate tables, "
            "copy-signal-to-acceptance outcome policy, or prompt-example "
            "revision guidance."
        ),
    }


def validate_prompt_example_copy_boundary(
    boundary: object | str | Path | None = None,
) -> PromptExampleCopyBoundaryValidation:
    data, read_issues = _load_boundary(
        prompt_example_copy_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return PromptExampleCopyBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[PromptExampleCopyBoundaryIssue] = []
    if data.get("schema") != PROMPT_EXAMPLE_COPY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported prompt-example copy boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "SEARCH/REPLACE examples" not in source_claim
        or "current program" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify examples versus current-program edits"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_schema") != EXPECTED_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", f"runtime_report_schema must be {EXPECTED_RUNTIME_REPORT_SCHEMA}"))
    if data.get("runtime_report_status") != "prompt_example_copy_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to prompt-example copy diagnostics"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "prompt-example copy boundary must not claim complete guard readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim hard or configurable rejection policy" not in boundary_text
        or "semantic or renamed copy detection" not in boundary_text
        or "custom prompt-template example inventories" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate built-in diagnostics from full example-copy guard readiness"))
    return PromptExampleCopyBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_prompt_example_copy_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_prompt_example_copy_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Prompt example-copy boundary",
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
) -> tuple[dict[str, Any] | None, list[PromptExampleCopyBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "prompt-example copy boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[PromptExampleCopyBoundaryIssue],
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
    issues: list[PromptExampleCopyBoundaryIssue],
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


def _issue(code: str, message: str) -> PromptExampleCopyBoundaryIssue:
    return PromptExampleCopyBoundaryIssue(code, message)
