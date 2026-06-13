from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STOCHASTIC_PROMPT_FORMAT_BOUNDARY_SCHEMA = (
    "libreevolve.stochastic_prompt_format_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.2",)
EXPECTED_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.stochastic_prompt_format_distribution_report.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "effective_config_distribution_without_separate_source_identity"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "prompt_format_markers",
    "prompt_format_options",
    "normalized_probabilities",
    "selected_alternative_hashes",
    "prompt_call_linkage",
    "weight_source_boundary",
    "prompt_context_override_source",
    "run_local_rng_replay_boundary",
    "separate_distribution_config_source_path",
    "separate_distribution_config_source_hash",
    "separate_distribution_config_byte_count",
    "config_precedence_record",
    "human_authored_alternative_provenance",
    "author_reviewer_metadata",
    "revision_or_change_history",
    "paper_facing_separate_file_validator",
)
EXPECTED_MISSING_EVIDENCE = {
    "separate_distribution_config_source_path": "not_recorded_locally",
    "separate_distribution_config_source_hash": "not_recorded_locally",
    "separate_distribution_config_byte_count": "not_recorded_locally",
    "config_precedence_record": "not_recorded_locally",
    "human_authored_alternative_provenance": "not_recorded_locally",
    "author_reviewer_metadata": "not_recorded_locally",
    "revision_or_change_history": "not_recorded_locally",
    "paper_facing_separate_file_validator": "not_recorded_locally",
}


@dataclass(frozen=True)
class StochasticPromptFormatBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class StochasticPromptFormatBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[StochasticPromptFormatBoundaryIssue]


def stochastic_prompt_format_boundary_record() -> dict[str, Any]:
    """Return the stochastic prompt-format evidence versus source-parity boundary."""

    return {
        "schema": STOCHASTIC_PROMPT_FORMAT_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve uses stochastic prompt formatting with template "
            "placeholders, human-provided alternatives, and probability "
            "distributions supplied in a separate config file"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_schema": EXPECTED_RUNTIME_REPORT_SCHEMA,
        "runtime_report_status": "effective_config_distribution_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve runtime histories include "
            "stochastic prompt-format markers, configured prompt_format_options, "
            "normalized probabilities, selected alternative hashes, prompt/call "
            "linkage, weight-source boundaries, prompt-context override source, "
            "and the run-local RNG replay boundary. It does not claim separate "
            "distribution config source path, separate distribution config "
            "source hash, byte-count provenance, config precedence records, "
            "human-authored alternative provenance, author/reviewer metadata, "
            "revision history, or a paper-facing separate-file validator."
        ),
    }


def validate_stochastic_prompt_format_boundary(
    boundary: object | str | Path | None = None,
) -> StochasticPromptFormatBoundaryValidation:
    data, read_issues = _load_boundary(
        stochastic_prompt_format_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return StochasticPromptFormatBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[StochasticPromptFormatBoundaryIssue] = []
    if data.get("schema") != STOCHASTIC_PROMPT_FORMAT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported stochastic prompt-format boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.2"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "human-provided alternatives" not in source_claim
        or "separate config file" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify human alternatives and separate config-file distributions"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_schema") != EXPECTED_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", f"runtime_report_schema must be {EXPECTED_RUNTIME_REPORT_SCHEMA}"))
    if data.get("runtime_report_status") != "effective_config_distribution_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to effective config distribution evidence"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "stochastic prompt-format boundary must not claim separate-source parity"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim separate distribution config source path" not in boundary_text
        or "human-authored alternative provenance" not in boundary_text
        or "paper-facing separate-file validator" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate effective config distribution evidence from separate-source parity"))
    return StochasticPromptFormatBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_stochastic_prompt_format_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_stochastic_prompt_format_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Stochastic prompt-format boundary",
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
) -> tuple[dict[str, Any] | None, list[StochasticPromptFormatBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "stochastic prompt-format boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[StochasticPromptFormatBoundaryIssue],
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
    issues: list[StochasticPromptFormatBoundaryIssue],
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


def _issue(code: str, message: str) -> StochasticPromptFormatBoundaryIssue:
    return StochasticPromptFormatBoundaryIssue(code, message)
