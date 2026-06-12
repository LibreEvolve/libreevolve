from libreevolve.problems.benchmarks.deepevolve_boundary import (
    DEEPEVOLVE_BOUNDARY_SCHEMA,
    deepevolve_boundary_record,
    render_deepevolve_boundary_summary,
    validate_deepevolve_boundary,
)


def test_deepevolve_boundary_accepts_absence_record():
    boundary = deepevolve_boundary_record()

    validation = validate_deepevolve_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "retrieval_context_inspiration_without_deepevolve_loop_parity"
    )
    assert validation.component_count == 15
    assert validation.required_evidence_field_count == 28
    assert validation.missing_evidence_count == 20
    assert boundary["schema"] == DEEPEVOLVE_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v1"
    assert boundary["local_evidence"]["retrieval_context_ready"] is True
    assert boundary["local_evidence"]["cross_file_coding_ready"] is False
    assert "does not claim DeepEvolve's six-module" in boundary["claim_boundary"]


def test_deepevolve_boundary_rejects_premature_runtime_claims():
    boundary = deepevolve_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][1]["status"] = "verified_local_runtime"
    boundary["framework_components"][5]["local_status"] = "implemented"
    boundary["local_evidence"]["cross_file_coding_ready"] = True
    boundary["local_evidence"]["repository_runtime_verified"] = True
    boundary["missing_evidence"]["cross_file_code_editing"] = "implemented"

    validation = validate_deepevolve_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_cross_file_coding_ready_overclaim" in codes
    assert "local_evidence_repository_runtime_verified_overclaim" in codes
    assert "invalid_missing_evidence_cross_file_code_editing" in codes


def test_render_deepevolve_boundary_summary_reports_shape():
    summary = render_deepevolve_boundary_summary(deepevolve_boundary_record())

    assert "DeepEvolve boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | retrieval_context_inspiration_without_deepevolve_loop_parity |"
        in summary
    )
    assert "| component_count | 15 |" in summary
