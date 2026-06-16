from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DOCUMENTATION_TRUTHFULNESS_BOUNDARY_SCHEMA = (
    "libreevolve.documentation_truthfulness_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "cross_document_guards_without_semantic_claim_proof"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_status_scope",
    "roadmap_status_scope",
    "papers_index_status_scope",
    "active_todo_ledgers",
    "completed_todo_ledgers",
    "docs_readme_routing",
    "docs_index_reader_path_inventory",
    "docs_status_ledger_inventory",
    "docs_architecture_runtime_flow_inventory",
    "github_actions_docs_path_filters",
    "paper_manifest_readme_consistency",
    "paper_manifest_papers_index_consistency",
    "paper_manifest_todo_coverage_rows",
    "paper_manifest_stale_absence_wording_checks",
    "boundary_sidecar_registry",
    "tracked_legacy_surface_inventory",
    "readme_agent_routing_inventory",
    "readme_documentation_map_inventory",
    "readme_repository_layout_inventory",
    "readme_quick_start_smoke_inventory",
    "readme_install_smoke_inventory",
    "readme_provider_auth_inventory",
    "readme_provider_example_matrix_inventory",
    "readme_cli_provider_guardrail_inventory",
    "readme_paper_cache_topic_inventory",
    "readme_paper_cache_rehydrate_inventory",
    "documentation_claim_inventory",
    "focused_boundary_tests",
    "semantic_claim_verifier",
    "implementation_evidence_mapping",
    "stale_completed_entry_detection",
    "generated_alignment_report",
    "full_alphaevolve_claim_truth_proof",
)
EXPECTED_MISSING_EVIDENCE = {
    "semantic_claim_verifier": "not_recorded_locally",
    "implementation_evidence_mapping": "not_recorded_locally",
    "stale_completed_entry_detection": "not_recorded_locally",
    "generated_alignment_report": "not_recorded_locally",
    "full_alphaevolve_claim_truth_proof": "not_recorded_locally",
}


@dataclass(frozen=True)
class DocumentationTruthfulnessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class DocumentationTruthfulnessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[DocumentationTruthfulnessBoundaryIssue]


def documentation_truthfulness_boundary_record() -> dict[str, Any]:
    """Return the docs-alignment guard versus semantic proof boundary."""

    return {
        "schema": DOCUMENTATION_TRUTHFULNESS_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve-alignment documentation should keep project claims "
            "synchronized with implemented behavior and cited evidence"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has README status scoping, "
            "ROADMAP status scoping, papers-index status scoping, active and "
            "completed TODO ledgers, docs/README routing, docs-index reader-path "
            "inventory, docs/status.md ledger inventory, docs/architecture.md runtime-flow inventory, GitHub Actions docs path filters, paper-manifest README and papers-index consistency "
            "checks, paper-manifest TODO coverage rows, stale source-specific "
            "absence wording checks, a boundary sidecar registry, a top-level "
            "tracked legacy-surface inventory, README AGENTS.md routing "
            "inventory, README Documentation Map inventory, README Repository Layout inventory, README quick-start smoke inventory, README install-smoke "
            "inventory, README provider-auth setup inventory, README provider-example "
            "matrix inventory, README CLI-provider guardrail inventory, README paper-cache "
            "topic inventory, README paper-cache rehydrate inventory, "
            "README/ROADMAP claim inventory, and "
            "focused boundary tests. It does not claim semantic "
            "documentation-claim verification, complete implementation-evidence "
            "mapping, stale completed entry detection, generated alignment "
            "reports, or full proof that every "
            "AlphaEvolve-facing claim is current."
        ),
    }


def validate_documentation_truthfulness_boundary(
    boundary: object | str | Path | None = None,
) -> DocumentationTruthfulnessBoundaryValidation:
    data, read_issues = _load_boundary(
        documentation_truthfulness_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return DocumentationTruthfulnessBoundaryValidation(
            False, None, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[DocumentationTruthfulnessBoundaryIssue] = []
    if data.get("schema") != DOCUMENTATION_TRUTHFULNESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported documentation truthfulness boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "synchronized with implemented behavior" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify synchronized documentation and implemented behavior"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "documentation truthfulness boundary must not claim semantic proof"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim semantic documentation-claim verification" not in boundary_text
        or "complete implementation-evidence mapping" not in boundary_text
        or "full proof that every AlphaEvolve-facing claim is current" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate cross-document guards from semantic claim proof"))
    return DocumentationTruthfulnessBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_documentation_truthfulness_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_documentation_truthfulness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Documentation truthfulness boundary",
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
) -> tuple[dict[str, Any] | None, list[DocumentationTruthfulnessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "documentation truthfulness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[DocumentationTruthfulnessBoundaryIssue],
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
    issues: list[DocumentationTruthfulnessBoundaryIssue],
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


def _issue(code: str, message: str) -> DocumentationTruthfulnessBoundaryIssue:
    return DocumentationTruthfulnessBoundaryIssue(code, message)
