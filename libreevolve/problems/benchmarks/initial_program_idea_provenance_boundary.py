from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


INITIAL_PROGRAM_IDEA_PROVENANCE_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_initial_program_idea_provenance_boundary.v1"
)
INITIAL_PROGRAM_IDEA_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.initial_program_idea_provenance_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.1", "3.1")
EXPECTED_BOUNDARY_STATUS = "metadata_contract_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "seed_source_identity_recorded",
    "generation_zero_history_linked",
    "idea_origin_metadata_present",
    "human_or_background_contribution_labels",
    "seed_variant_ids_recorded",
    "evaluator_metric_linkage",
    "exact_rendered_prompt_context_digest",
    "prompt_history_seed_context_span",
    "seed_workspace_hash_to_prompt_linkage",
    "per_variant_run_artifact_manifest",
    "equal_budget_replicate_protocol",
    "matrix_parameter_seed_idea_attribution",
    "equal_budget_seed_variant_results",
    "alphaevolve_human_seeded_benchmark_parity",
    "prompt_context_to_seed_idea_linkage",
    "simple_random_researcher_seed_comparison",
    "matrix_seed_variant_result_tables",
    "constructive_math_seed_variant_result_tables",
    "human_contribution_review_or_signoff",
    "paper_facing_certification_rows",
)
EXPECTED_MISSING_EVIDENCE = {
    "equal_budget_seed_variant_results": "not_recorded_locally",
    "exact_rendered_prompt_context_digest": "not_recorded_locally",
    "prompt_history_seed_context_span": "not_recorded_locally",
    "seed_workspace_hash_to_prompt_linkage": "not_recorded_locally",
    "per_variant_run_artifact_manifest": "not_recorded_locally",
    "equal_budget_replicate_protocol": "not_recorded_locally",
    "matrix_parameter_seed_idea_attribution": "not_recorded_locally",
    "simple_random_researcher_seed_comparison": "not_recorded_locally",
    "matrix_seed_variant_result_tables": "not_recorded_locally",
    "constructive_math_seed_variant_result_tables": "not_recorded_locally",
    "human_contribution_review_or_signoff": "not_recorded_locally",
    "prompt_context_to_seed_idea_linkage": "not_recorded_locally",
    "paper_facing_certification_rows": "not_recorded_locally",
    "alphaevolve_human_seeded_benchmark_parity": "not_recorded_locally",
}


@dataclass(frozen=True)
class InitialProgramIdeaProvenanceBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class InitialProgramIdeaProvenanceBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[InitialProgramIdeaProvenanceBoundaryIssue]


def initial_program_idea_provenance_boundary_record() -> dict[str, Any]:
    """Return the paper-facing initial-program idea provenance boundary."""

    return {
        "schema": INITIAL_PROGRAM_IDEA_PROVENANCE_BOUNDARY_SCHEMA,
        "runtime_report_schema": INITIAL_PROGRAM_IDEA_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 2.1 identifies the initial program and "
            "optional background knowledge as user inputs, while Section 3.1 "
            "reports matrix runs that improved when researchers seeded initial "
            "programs with ideas such as stochastic evaluation or evolutionary "
            "approaches"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "initial_program_idea_provenance_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has optional seed idea "
            "metadata fields under problem.seed_sources and a runtime report "
            "linking seed sources to generation-zero history, seed variant ids, "
            "idea-origin classes, contribution roles, prior-technique labels, "
            "background references, and evaluator metrics, but does not claim "
            "equal-budget seed-variant result tables, exact rendered prompt "
            "digests, prompt-history seed-context spans, seed-workspace-hash-"
            "to-prompt linkage, per-variant run-artifact manifests, "
            "equal-budget replicate protocols, simple/random/researcher seed "
            "comparisons, matrix or constructive-math seed-variant reports, "
            "matrix-parameter seed-idea attribution, human contribution "
            "review/signoff, prompt-context-to-seed linkage, paper-facing "
            "certification rows, or AlphaEvolve human-seeded benchmark parity."
        ),
    }


def validate_initial_program_idea_provenance_boundary(
    boundary: object | str | Path | None = None,
) -> InitialProgramIdeaProvenanceBoundaryValidation:
    data, read_issues = _load_boundary(
        initial_program_idea_provenance_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return InitialProgramIdeaProvenanceBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[InitialProgramIdeaProvenanceBoundaryIssue] = []
    if data.get("schema") != INITIAL_PROGRAM_IDEA_PROVENANCE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported initial-program idea provenance boundary schema"))
    if data.get("runtime_report_schema") != INITIAL_PROGRAM_IDEA_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify initial-program idea provenance reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.1', '3.1']"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "Section 3.1" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve initial-program idea evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "initial_program_idea_provenance_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to initial-program idea provenance reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "initial-program idea boundary must not claim paper readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim equal-budget seed-variant result tables" not in boundary_text
        or "AlphaEvolve human-seeded benchmark parity" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim human-seeded benchmark parity"))
    return InitialProgramIdeaProvenanceBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_initial_program_idea_provenance_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_initial_program_idea_provenance_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve initial-program idea provenance boundary",
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
) -> tuple[dict[str, Any] | None, list[InitialProgramIdeaProvenanceBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "initial-program idea provenance boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[InitialProgramIdeaProvenanceBoundaryIssue],
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
    issues: list[InitialProgramIdeaProvenanceBoundaryIssue],
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


def _issue(code: str, message: str) -> InitialProgramIdeaProvenanceBoundaryIssue:
    return InitialProgramIdeaProvenanceBoundaryIssue(code, message)
