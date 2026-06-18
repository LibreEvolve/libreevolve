from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROPOSAL_SCORE_BOUNDARY_SCHEMA = "libreevolve.proposal_score_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_PROPOSAL_SCORE_REPORT_SCHEMA = "libreevolve.proposal_score_report.v1"
EXPECTED_HYPOTHESIS_INDEX_SCHEMA = "libreevolve.hypothesis_index.v1"
EXPECTED_SCORING_POLICY_SCHEMA = "libreevolve.proposal_scoring_policy.v1"
EXPECTED_BOUNDARY_STATUS = "bounded_current_run_scores_and_lexical_families_not_semantic_idea_memory"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "versioned_proposal_score_records",
    "captured_idea_rationale_hypothesis_metadata",
    "bounded_hypothesis_index",
    "redacted_text_previews_and_hashes",
    "outcome_linked_quality_signal",
    "exact_signature_novelty_signal",
    "duplicate_signature_counts",
    "top_record_score_ordering",
    "current_run_lexical_family_diagnostics",
    "current_run_resurfacing_hypothesis_source",
    "recent_deepresearch_query_terms",
    "semantic_embedding_proposal_index",
    "calibrated_proposal_quality_model",
    "cross_run_persisted_proposal_table",
    "prompt_archive_policy_using_proposal_scores",
    "benchmark_linked_proposal_quality_validation",
    "hypothesis_refinement_loop",
)
EXPECTED_MISSING_EVIDENCE = {
    "semantic_embedding_proposal_index": "not_recorded_locally",
    "calibrated_proposal_quality_model": "not_recorded_locally",
    "cross_run_persisted_proposal_table": "not_recorded_locally",
    "prompt_archive_policy_using_proposal_scores": "not_recorded_locally",
    "benchmark_linked_proposal_quality_validation": "not_recorded_locally",
    "hypothesis_refinement_loop": "not_recorded_locally",
}


@dataclass(frozen=True)
class ProposalScoreBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ProposalScoreBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ProposalScoreBoundaryIssue]


def proposal_score_boundary_record() -> dict[str, Any]:
    """Return the proposal-score versus semantic idea-memory boundary."""

    return {
        "schema": PROPOSAL_SCORE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve-style evolutionary memory should make prior ideas, "
            "rationales, and hypotheses reusable through quality-aware and "
            "novelty-aware search, not only attach proposal text to candidates"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "proposal_score_report_schema": EXPECTED_PROPOSAL_SCORE_REPORT_SCHEMA,
        "hypothesis_index_schema": EXPECTED_HYPOTHESIS_INDEX_SCHEMA,
        "scoring_policy_schema": EXPECTED_SCORING_POLICY_SCHEMA,
        "runtime_report_status": "bounded_current_run_proposal_scores_and_lexical_families_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve manifests can show bounded "
            "current-run proposal scoring and hypothesis evidence: versioned "
            "proposal score records, captured idea/rationale/hypothesis "
            "metadata, bounded hypothesis-index summaries, redacted text "
            "previews and hashes, outcome-linked quality signals, exact "
            "signature novelty signals, duplicate signature counts, top-record "
            "score ordering, deterministic current-run lexical proposal-family "
            "diagnostics, current-run resurfacing hypothesis sources, and "
            "recent DeepResearch query terms. It does not claim semantic or "
            "embedding-backed proposal retrieval, calibrated proposal-quality "
            "models, cross-run persisted proposal tables, prompt/archive "
            "selection policy using proposal scores, benchmark-linked proposal "
            "quality validation, or hypothesis refinement loops."
        ),
    }


def validate_proposal_score_boundary(
    boundary: object | str | Path | None = None,
) -> ProposalScoreBoundaryValidation:
    data, read_issues = _load_boundary(
        proposal_score_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ProposalScoreBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ProposalScoreBoundaryIssue] = []
    if data.get("schema") != PROPOSAL_SCORE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported proposal score boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "prior ideas" not in source_claim
        or "quality-aware and novelty-aware search" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify quality/novelty-aware proposal memory"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("proposal_score_report_schema") != EXPECTED_PROPOSAL_SCORE_REPORT_SCHEMA:
        issues.append(_issue("invalid_proposal_score_report_schema", f"proposal_score_report_schema must be {EXPECTED_PROPOSAL_SCORE_REPORT_SCHEMA}"))
    if data.get("hypothesis_index_schema") != EXPECTED_HYPOTHESIS_INDEX_SCHEMA:
        issues.append(_issue("invalid_hypothesis_index_schema", f"hypothesis_index_schema must be {EXPECTED_HYPOTHESIS_INDEX_SCHEMA}"))
    if data.get("scoring_policy_schema") != EXPECTED_SCORING_POLICY_SCHEMA:
        issues.append(_issue("invalid_scoring_policy_schema", f"scoring_policy_schema must be {EXPECTED_SCORING_POLICY_SCHEMA}"))
    if data.get("runtime_report_status") != "bounded_current_run_proposal_scores_and_lexical_families_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to bounded current-run proposal scores and lexical families"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "proposal score boundary must not claim semantic idea-memory readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim semantic or embedding-backed proposal retrieval" not in boundary_text
        or "current-run lexical proposal-family diagnostics" not in boundary_text
        or "cross-run persisted proposal tables" not in boundary_text
        or "prompt/archive selection policy using proposal scores" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded proposal scores from semantic idea memory"))
    return ProposalScoreBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_proposal_score_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_proposal_score_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Proposal score boundary",
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
) -> tuple[dict[str, Any] | None, list[ProposalScoreBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "proposal score boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ProposalScoreBoundaryIssue],
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
    issues: list[ProposalScoreBoundaryIssue],
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


def _issue(code: str, message: str) -> ProposalScoreBoundaryIssue:
    return ProposalScoreBoundaryIssue(code, message)
