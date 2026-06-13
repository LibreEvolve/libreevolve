from libreevolve.problems.benchmarks.implementation_evidence_map_boundary import (
    IMPLEMENTATION_EVIDENCE_MAP_BOUNDARY_SCHEMA,
    implementation_evidence_map_boundary_record,
    render_implementation_evidence_map_boundary_summary,
    validate_implementation_evidence_map_boundary,
)


def test_implementation_evidence_map_boundary_accepts_core_requirement_anchors():
    boundary = implementation_evidence_map_boundary_record()

    validation = validate_implementation_evidence_map_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "core_requirement_anchors_without_exhaustive_coverage"
    )
    assert validation.requirement_count == 6
    assert validation.missing_evidence_count == 11
    assert boundary["schema"] == IMPLEMENTATION_EVIDENCE_MAP_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    requirement_ids = {
        requirement["requirement_id"] for requirement in boundary["requirements"]
    }
    assert "alphaevolve_program_markers" in requirement_ids
    assert "alphaevolve_published_benchmarks" in requirement_ids
    assert (
        boundary["missing_evidence"]["paper_index_status_claim_inventory"]
        == "not_recorded_locally"
    )
    assert (
        boundary["missing_evidence"]["implemented_benchmark_bullet_coverage_map"]
        == "not_recorded_locally"
    )
    assert "does not claim an exhaustive requirement inventory" in boundary["claim_boundary"]
    assert "absence-sentence freshness matrix" in boundary["claim_boundary"]


def test_implementation_evidence_map_boundary_rejects_exhaustive_overclaim():
    boundary = implementation_evidence_map_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "exhaustive_alphaevolve_implementation_audit_ready"
    boundary["missing_evidence"]["exhaustive_requirement_inventory"] = "recorded"
    boundary["requirements"] = boundary["requirements"][1:]

    validation = validate_implementation_evidence_map_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_exhaustive_requirement_inventory" in codes
    assert "missing_requirement_id" in codes


def test_implementation_evidence_map_boundary_rejects_anchor_drift():
    boundary = implementation_evidence_map_boundary_record()
    boundary["requirements"][0]["module_refs"] = ["libreevolve/core/loop.py"]

    validation = validate_implementation_evidence_map_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_alphaevolve_program_markers_module_refs" in codes


def test_render_implementation_evidence_map_boundary_summary_reports_shape():
    summary = render_implementation_evidence_map_boundary_summary(
        implementation_evidence_map_boundary_record()
    )

    assert "Implementation evidence map boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | core_requirement_anchors_without_exhaustive_coverage |"
        in summary
    )
    assert "| requirement_count | 6 |" in summary
    assert "| missing_evidence_count | 11 |" in summary
