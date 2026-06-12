from libreevolve.problems.benchmarks.ramsey_numbers_boundary import (
    RAMSEY_NUMBERS_BOUNDARY_SCHEMA,
    ramsey_numbers_boundary_record,
    render_ramsey_numbers_boundary_summary,
    validate_ramsey_numbers_boundary,
)


def test_ramsey_numbers_boundary_accepts_absence_record():
    boundary = ramsey_numbers_boundary_record()

    validation = validate_ramsey_numbers_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "constructive_ramsey_context_without_graph_witness_parity"
    )
    assert validation.component_count == 14
    assert validation.required_evidence_field_count == 24
    assert validation.missing_evidence_count == 20
    assert boundary["schema"] == RAMSEY_NUMBERS_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v5"
    assert boundary["source_last_revised_date"] == "2026-04-21"
    assert boundary["local_evidence"]["graph_verifier_ready"] is False
    assert "does not claim Ramsey graph candidate schemas" in boundary["claim_boundary"]


def test_ramsey_numbers_boundary_rejects_premature_graph_runtime_claims():
    boundary = ramsey_numbers_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][1]["status"] = "verified_local_snapshot"
    boundary["framework_components"][0]["local_status"] = "implemented"
    boundary["local_evidence"]["graph_verifier_ready"] = True
    boundary["local_evidence"]["repository_runtime_verified"] = True
    boundary["missing_evidence"]["clique_independent_set_verifier"] = "implemented"

    validation = validate_ramsey_numbers_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_graph_verifier_ready_overclaim" in codes
    assert "local_evidence_repository_runtime_verified_overclaim" in codes
    assert "invalid_missing_evidence_clique_independent_set_verifier" in codes


def test_render_ramsey_numbers_boundary_summary_reports_shape():
    summary = render_ramsey_numbers_boundary_summary(ramsey_numbers_boundary_record())

    assert "Ramsey Numbers boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | constructive_ramsey_context_without_graph_witness_parity |"
        in summary
    )
    assert "| component_count | 14 |" in summary
