from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RELATED_WORK_TAXONOMY_BOUNDARY_SCHEMA = (
    "libreevolve.related_work_taxonomy_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("5",)
EXPECTED_BOUNDARY_STATUS = "paper_index_rows_without_related_work_taxonomy"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_paper_inventory",
    "paper_index_status_rows",
    "individual_source_gap_todos",
    "related_work_source_id_map",
    "method_family_taxonomy",
    "candidate_representation_taxonomy",
    "feedback_signal_taxonomy",
    "task_stage_taxonomy",
    "comparison_axis_taxonomy",
    "source_category_citations",
    "alphaevolve_positioning_claim_table",
    "readme_related_work_summary_gate",
    "roadmap_related_work_summary_gate",
    "paper_index_related_work_summary_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "related_work_source_id_map": "not_recorded_locally",
    "method_family_taxonomy": "not_recorded_locally",
    "candidate_representation_taxonomy": "not_recorded_locally",
    "feedback_signal_taxonomy": "not_recorded_locally",
    "task_stage_taxonomy": "not_recorded_locally",
    "comparison_axis_taxonomy": "not_recorded_locally",
    "source_category_citations": "not_recorded_locally",
    "alphaevolve_positioning_claim_table": "not_recorded_locally",
    "readme_related_work_summary_gate": "not_recorded_locally",
    "roadmap_related_work_summary_gate": "not_recorded_locally",
    "paper_index_related_work_summary_gate": "not_recorded_locally",
}


@dataclass(frozen=True)
class RelatedWorkTaxonomyBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RelatedWorkTaxonomyBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[RelatedWorkTaxonomyBoundaryIssue]


def related_work_taxonomy_boundary_record() -> dict[str, Any]:
    """Return the flat paper-index versus Related Work taxonomy boundary."""

    return {
        "schema": RELATED_WORK_TAXONOMY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 5 Related Work positions the system as "
            "execution-feedback code superoptimization and algorithm discovery "
            "against pre-LLM search, AlphaTensor, GPU-kernel and LLM-agent "
            "optimizers, AI-for-science systems, and proof discovery"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "paper_index_status": "flat_source_inventory_and_individual_gap_rows",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has a source-paper "
            "inventory, paper-index status rows, and individual source-gap "
            "TODOs. It does not claim a Related Work taxonomy with source-id "
            "category mapping, method-family labels, candidate-representation "
            "labels, feedback-signal labels, task-stage labels, comparison "
            "axes, category citations, an AlphaEvolve positioning-claim table, "
            "or README/ROADMAP/paper-index gates for Related Work summary "
            "claims."
        ),
    }


def validate_related_work_taxonomy_boundary(
    boundary: object | str | Path | None = None,
) -> RelatedWorkTaxonomyBoundaryValidation:
    data, read_issues = _load_boundary(
        related_work_taxonomy_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return RelatedWorkTaxonomyBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[RelatedWorkTaxonomyBoundaryIssue] = []
    if data.get("schema") != RELATED_WORK_TAXONOMY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported related-work taxonomy boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['5']"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "Related Work" not in source_claim
        or "execution-feedback code superoptimization" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve Related Work positioning"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("paper_index_status") != "flat_source_inventory_and_individual_gap_rows":
        issues.append(_issue("invalid_paper_index_status", "paper_index_status must stay scoped to flat source inventory and individual gap rows"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "related-work taxonomy boundary must not claim positioning readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a Related Work taxonomy" not in boundary_text
        or "AlphaEvolve positioning-claim table" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate flat paper inventory from Related Work taxonomy claims"))
    return RelatedWorkTaxonomyBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_related_work_taxonomy_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_related_work_taxonomy_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Related Work taxonomy boundary",
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
) -> tuple[dict[str, Any] | None, list[RelatedWorkTaxonomyBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "related-work taxonomy boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RelatedWorkTaxonomyBoundaryIssue],
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
    issues: list[RelatedWorkTaxonomyBoundaryIssue],
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


def _issue(code: str, message: str) -> RelatedWorkTaxonomyBoundaryIssue:
    return RelatedWorkTaxonomyBoundaryIssue(code, message)
