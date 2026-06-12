from libreevolve.problems.benchmarks.combinatorics_berczy_boundary import (
    COMBINATORICS_BERCZY_BOUNDARY_SCHEMA,
    combinatorics_berczy_boundary_record,
    render_combinatorics_berczy_boundary_summary,
    validate_combinatorics_berczy_boundary,
)


def test_combinatorics_berczy_boundary_accepts_absence_record():
    boundary = combinatorics_berczy_boundary_record()

    validation = validate_combinatorics_berczy_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "reported_combinatorics_experiments_without_local_harness_parity"
    )
    assert validation.component_count == 14
    assert validation.required_evidence_field_count == 24
    assert validation.missing_evidence_count == 20
    assert boundary["schema"] == COMBINATORICS_BERCZY_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v1"
    assert boundary["source_last_revised_date"] == "2026-03-04"
    assert boundary["local_evidence"]["bipartite_harness_ready"] is False
    assert (
        "does not claim bipartite or planar graph-reconstruction harnesses"
        in boundary["claim_boundary"]
    )


def test_combinatorics_berczy_boundary_rejects_premature_harness_claims():
    boundary = combinatorics_berczy_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][0]["status"] = "verified_local_snapshot"
    boundary["framework_components"][0]["local_status"] = "implemented"
    boundary["local_evidence"]["bipartite_harness_ready"] = True
    boundary["local_evidence"]["independent_verifier_ready"] = True
    boundary["local_evidence"]["repository_runtime_verified"] = True
    boundary["missing_evidence"]["bipartite_graph_reconstruction_harness"] = "implemented"

    validation = validate_combinatorics_berczy_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_bipartite_harness_ready_overclaim" in codes
    assert "local_evidence_independent_verifier_ready_overclaim" in codes
    assert "local_evidence_repository_runtime_verified_overclaim" in codes
    assert "missing_evidence_mismatch" in codes


def test_render_combinatorics_berczy_boundary_summary_reports_shape():
    summary = render_combinatorics_berczy_boundary_summary(
        combinatorics_berczy_boundary_record()
    )

    assert "Combinatorics Berczy boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | reported_combinatorics_experiments_without_local_harness_parity |"
        in summary
    )
    assert "| component_count | 14 |" in summary
