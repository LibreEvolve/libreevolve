from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROMPT_SECTION_PACKING_BOUNDARY_SCHEMA = (
    "libreevolve.prompt_section_packing_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.2", "2.3", "2.4")
EXPECTED_BOUNDARY_STATUS = "mutation_section_packing_without_all_role_provider_token_policy"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "prompt_max_chars",
    "prompt_max_estimated_tokens",
    "heuristic_estimated_token_cap",
    "provider_token_counter_hook",
    "mutation_common_counter_discovery",
    "final_prompt_role_counter_discovery",
    "prompt_section_budget_schema",
    "section_priority_packing_decisions",
    "required_section_fit_status",
    "provider_counter_boundary_fields",
    "runtime_prompt_section_packing_coverage",
    "mutation_section_packing_role",
    "critique_final_prompt_boundary_only",
    "feedback_final_prompt_boundary_only",
    "meta_prompt_final_prompt_boundary_only",
    "bounded_validator_metadata_summaries",
    "bounded_evaluator_artifact_excerpts",
    "all_role_provider_token_section_packing",
    "exact_non_openai_provider_counters",
    "registry_custom_role_section_packing",
    "retrieval_context_plugin_failure_memory_packing",
    "full_validator_metadata_prompt_policy",
)
EXPECTED_MISSING_EVIDENCE = {
    "all_role_provider_token_section_packing": "not_recorded_locally",
    "exact_non_openai_provider_counters": "not_recorded_locally",
    "registry_custom_role_section_packing": "not_recorded_locally",
    "retrieval_context_plugin_failure_memory_packing": "not_recorded_locally",
    "full_validator_metadata_prompt_policy": "not_recorded_locally",
}


@dataclass(frozen=True)
class PromptSectionPackingBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class PromptSectionPackingBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[PromptSectionPackingBoundaryIssue]


def prompt_section_packing_boundary_record() -> dict[str, Any]:
    """Return the mutation section-packing versus all-role prompt policy boundary."""

    return {
        "schema": PROMPT_SECTION_PACKING_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve prompt context can include previous program execution "
            "results, outputs, scores, and other feedback; prompt/output "
            "formatting and multi-score prompt diversity must remain bounded "
            "to the selected model context"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "section_budget_schema": "libreevolve.prompt_section_budget.v1",
        "coverage_schema": "libreevolve.prompt_section_packing_coverage.v1",
        "coverage_validation_schema": (
            "libreevolve.prompt_section_packing_coverage_validation.v1"
        ),
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has prompt_max_chars, "
            "prompt_max_estimated_tokens, heuristic estimated-token caps, a "
            "provider token-counter hook, mutation common-counter discovery, "
            "final prompt role-counter discovery, prompt section-budget records, "
            "section-priority packing decisions, required-section fit status, "
            "provider-counter boundary fields, runtime prompt-section-packing "
            "coverage, mutation as the section-packed prompt role, critique, "
            "feedback, and meta-prompt as final-prompt-boundary-only roles, "
            "bounded validator metadata summaries, and bounded evaluator "
            "artifact excerpts. It does not claim all-role provider-token "
            "section packing, exact non-OpenAI provider counters, registry/"
            "custom role section packing, retrieval/context/plugin/failure-"
            "memory section packing, or full validator-metadata prompt policy."
        ),
    }


def validate_prompt_section_packing_boundary(
    boundary: object | str | Path | None = None,
) -> PromptSectionPackingBoundaryValidation:
    data, read_issues = _load_boundary(
        prompt_section_packing_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return PromptSectionPackingBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[PromptSectionPackingBoundaryIssue] = []
    if data.get("schema") != PROMPT_SECTION_PACKING_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported prompt section-packing boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.2, 2.3, and 2.4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "execution results" not in source_claim
        or "selected model context" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify execution-feedback context and selected-model fitting"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    _validate_schema_field(data, "section_budget_schema", "libreevolve.prompt_section_budget.v1", issues)
    _validate_schema_field(data, "coverage_schema", "libreevolve.prompt_section_packing_coverage.v1", issues)
    _validate_schema_field(data, "coverage_validation_schema", "libreevolve.prompt_section_packing_coverage_validation.v1", issues)
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "prompt section-packing boundary must not claim all-role provider-token readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim all-role provider-token section packing" not in boundary_text
        or "exact non-OpenAI provider counters" not in boundary_text
        or "full validator-metadata prompt policy" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate mutation packing from all-role provider-token prompt policy"))
    return PromptSectionPackingBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_prompt_section_packing_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_prompt_section_packing_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Prompt section-packing boundary",
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
) -> tuple[dict[str, Any] | None, list[PromptSectionPackingBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "prompt section-packing boundary must be a JSON object")]


def _validate_schema_field(
    data: dict[str, Any],
    field: str,
    expected: str,
    issues: list[PromptSectionPackingBoundaryIssue],
) -> None:
    if data.get(field) != expected:
        issues.append(_issue(f"invalid_{field}", f"{field} must be {expected}"))


def _validate_required_fields(
    value: object,
    issues: list[PromptSectionPackingBoundaryIssue],
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
    issues: list[PromptSectionPackingBoundaryIssue],
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


def _issue(code: str, message: str) -> PromptSectionPackingBoundaryIssue:
    return PromptSectionPackingBoundaryIssue(code, message)
