from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROCESS_EXHIBIT_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_process_exhibit_boundary.v1"
PROCESS_EXHIBIT_RUNTIME_REPORT_SCHEMA = "libreevolve.alphaevolve_process_exhibit_report.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_FIGURE_IDS = ("Figure 1", "Figure 2")
EXPECTED_BOUNDARY_STATUS = "process_mapping_with_step_row_summaries_without_full_parity"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "figure_id",
    "source_page",
    "source_caption",
    "diagram_node_id",
    "diagram_edge_id",
    "local_component_ref",
    "figure2_pseudocode_step",
    "rendered_diagram_artifact_path",
    "rendered_diagram_artifact_hash",
    "exact_diagram_text_export",
    "accessibility_export",
    "async_topology_record",
    "evaluator_pool_parallelism_record",
    "artifact_step_validation_record",
)
EXPECTED_MISSING_EVIDENCE = {
    "exact_source_diagram_text_reproduction": "not_recorded_locally",
    "async_controller_sampler_evaluator_topology": "not_recorded_locally",
    "independent_evaluator_pool_parallelism": "not_recorded_locally",
    "semantic_candidate_level_step_stream_join": "not_recorded_locally",
}


@dataclass(frozen=True)
class ProcessExhibitBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ProcessExhibitBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ProcessExhibitBoundaryIssue]


def process_exhibit_boundary_record() -> dict[str, Any]:
    """Return the current Figure 1/Figure 2 process-diagram absence boundary."""

    return {
        "schema": PROCESS_EXHIBIT_BOUNDARY_SCHEMA,
        "runtime_report_schema": PROCESS_EXHIBIT_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_figure_ids": list(EXPECTED_SOURCE_FIGURE_IDS),
        "source_claim": (
            "AlphaEvolve Figure 1 presents the high-level discovery loop and "
            "Figure 2 expands it into database sampling, prompt construction, "
            "LLM generation, diff application, evaluator execution, and "
            "database admission"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "alphaevolve_process_exhibit_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has a validated runtime "
            "mapping from AlphaEvolve Figure 1/Figure 2 process nodes, edges, "
            "and pseudocode steps to local components and artifacts, plus "
            "generated Mermaid/text accessibility artifacts, step-stream "
            "artifact-link validation, strict JSONL row summaries, and "
            "component-to-TODO links. It does not claim exact source-diagram "
            "reproduction, async controller/sampler/evaluator topology, "
            "independent evaluator-pool parallelism, or semantic "
            "candidate-level joins across every process step stream."
        ),
    }


def validate_process_exhibit_boundary(
    boundary: object | str | Path | None = None,
) -> ProcessExhibitBoundaryValidation:
    data, read_issues = _load_boundary(
        process_exhibit_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ProcessExhibitBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ProcessExhibitBoundaryIssue] = []
    if data.get("schema") != PROCESS_EXHIBIT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported process exhibit boundary schema"))
    if data.get("runtime_report_schema") != PROCESS_EXHIBIT_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify process exhibit reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_figure_ids") != list(EXPECTED_SOURCE_FIGURE_IDS):
        issues.append(_issue("invalid_source_figure_ids", "source_figure_ids must be ['Figure 1', 'Figure 2']"))
    if not isinstance(data.get("source_claim"), str) or "Figure 1" not in data["source_claim"] or "Figure 2" not in data["source_claim"]:
        issues.append(_issue("invalid_source_claim", "source_claim must identify Figure 1 and Figure 2"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "alphaevolve_process_exhibit_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to process exhibit reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "process exhibit boundary must not claim paper readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim rendered process-diagram parity"))
    return ProcessExhibitBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_process_exhibit_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_process_exhibit_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve process exhibit boundary",
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
) -> tuple[dict[str, Any] | None, list[ProcessExhibitBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "process exhibit boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ProcessExhibitBoundaryIssue],
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
    issues: list[ProcessExhibitBoundaryIssue],
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


def _issue(code: str, message: str) -> ProcessExhibitBoundaryIssue:
    return ProcessExhibitBoundaryIssue(code, message)
