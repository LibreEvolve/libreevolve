from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FIGURE3_SUPERVISED_EXHIBIT_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_figure3_supervised_exhibit_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_FIGURE_ID = "Figure 3"
EXPECTED_SUBFIGURE_IDS = ("Figure 3a", "Figure 3b", "Figure 3c")
EXPECTED_BOUNDARY_STATUS = "figure3_supervised_exhibit_not_reproduced"
EXPECTED_SUPPORTING_SURFACES = (
    "embedded_evaluator_entrypoint_report",
    "prompt_history",
    "candidate_history",
    "mutation_search_replace_parser",
    "natural_language_preamble_boundary",
    "prompt_section_packing_boundary",
    "prompt_example_copy_boundary",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "figure_id",
    "subfigure_ids",
    "source_pdf_locator",
    "supervised_learning_pipeline_identity",
    "source_file_excerpt_artifact",
    "evaluate_function_excerpt_artifact",
    "assembled_prompt_excerpt_artifact",
    "llm_output_excerpt_artifact",
    "displayed_score_values",
    "current_program_score_link",
    "proposed_program_score_link",
    "prompt_history_links",
    "candidate_history_links",
    "evaluator_result_links",
    "omitted_line_policy",
    "abbreviation_policy",
    "rendered_artifact_hashes",
    "source_excerpt_hashes",
    "paper_source_evidence",
)
EXPECTED_MISSING_EVIDENCE = {
    "source_file_excerpt_artifact": "not_recorded_locally",
    "evaluate_function_excerpt_artifact": "not_recorded_locally",
    "assembled_prompt_excerpt_artifact": "not_recorded_locally",
    "llm_output_excerpt_artifact": "not_recorded_locally",
    "displayed_score_values": "not_recorded_locally",
    "prompt_history_links": "not_recorded_locally",
    "candidate_history_links": "not_recorded_locally",
    "evaluator_result_links": "not_recorded_locally",
    "rendered_artifact_hashes": "not_recorded_locally",
}


@dataclass(frozen=True)
class Figure3SupervisedExhibitBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class Figure3SupervisedExhibitBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[Figure3SupervisedExhibitBoundaryIssue]


def figure3_supervised_exhibit_boundary_record() -> dict[str, Any]:
    """Return the current Figure 3 supervised-learning exhibit boundary."""

    return {
        "schema": FIGURE3_SUPERVISED_EXHIBIT_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_figure_id": EXPECTED_SOURCE_FIGURE_ID,
        "source_subfigure_ids": list(EXPECTED_SUBFIGURE_IDS),
        "source_claim": (
            "AlphaEvolve Figure 3 is a supervised-learning pipeline exhibit "
            "with linked source-code/evaluate, assembled-prompt, and LLM-output "
            "subfigures"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "supporting_surfaces": list(EXPECTED_SUPPORTING_SURFACES),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has generic embedded "
            "evaluate, prompt-history, candidate-history, SEARCH/REPLACE, "
            "preamble, prompt-packing, and prompt-example-copy surfaces. It "
            "does not claim reproduced Figure 3 supervised-learning subfigure "
            "exhibits, exact source/prompt/output excerpts, displayed score "
            "values, rendered artifact hashes, or links from the displayed "
            "paper example to concrete local run artifacts."
        ),
    }


def validate_figure3_supervised_exhibit_boundary(
    boundary: object | str | Path | None = None,
) -> Figure3SupervisedExhibitBoundaryValidation:
    data, read_issues = _load_boundary(
        figure3_supervised_exhibit_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return Figure3SupervisedExhibitBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[Figure3SupervisedExhibitBoundaryIssue] = []
    if data.get("schema") != FIGURE3_SUPERVISED_EXHIBIT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Figure 3 supervised-exhibit boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_figure_id") != EXPECTED_SOURCE_FIGURE_ID:
        issues.append(_issue("invalid_source_figure_id", "source_figure_id must be Figure 3"))
    if data.get("source_subfigure_ids") != list(EXPECTED_SUBFIGURE_IDS):
        issues.append(_issue("invalid_source_subfigure_ids", "source_subfigure_ids must identify Figure 3a/3b/3c"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "supervised-learning pipeline exhibit" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify the Figure 3 supervised-learning exhibit"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "Figure 3 supervised-exhibit boundary must not claim reproduced exhibit evidence"))
    _validate_supporting_surfaces(data.get("supporting_surfaces"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim reproduced Figure 3" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that reproduced Figure 3 exhibit evidence is not claimed"))
    return Figure3SupervisedExhibitBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_figure3_supervised_exhibit_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_figure3_supervised_exhibit_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve Figure 3 supervised-learning exhibit boundary",
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
) -> tuple[dict[str, Any] | None, list[Figure3SupervisedExhibitBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Figure 3 supervised-exhibit boundary must be a JSON object")]


def _validate_supporting_surfaces(
    value: object,
    issues: list[Figure3SupervisedExhibitBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_supporting_surfaces", "supporting_surfaces must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_SUPPORTING_SURFACES)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_supporting_surface", f"supporting_surfaces lacks entries: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_supporting_surface", f"supporting_surfaces has unknown entries: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_supporting_surface", "supporting surfaces must be strings"))
    return len(seen)


def _validate_required_fields(
    value: object,
    issues: list[Figure3SupervisedExhibitBoundaryIssue],
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
    issues: list[Figure3SupervisedExhibitBoundaryIssue],
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


def _issue(code: str, message: str) -> Figure3SupervisedExhibitBoundaryIssue:
    return Figure3SupervisedExhibitBoundaryIssue(code, message)
