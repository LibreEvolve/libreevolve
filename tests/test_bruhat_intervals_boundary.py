from libreevolve.problems.benchmarks.bruhat_intervals_boundary import (
    BRUHAT_INTERVALS_BOUNDARY_SCHEMA,
    bruhat_intervals_boundary_record,
    render_bruhat_intervals_boundary_summary,
    validate_bruhat_intervals_boundary,
)


def test_bruhat_intervals_boundary_accepts_absence_record():
    boundary = bruhat_intervals_boundary_record()

    validation = validate_bruhat_intervals_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "constructive_math_context_without_local_bruhat_hypercube_benchmark"
    )
    assert validation.component_count == 14
    assert validation.required_evidence_field_count == 24
    assert validation.missing_evidence_count == 20
    assert boundary["schema"] == BRUHAT_INTERVALS_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v1"
    assert boundary["source_pdf_date"] == "2026-01-06"
    assert boundary["local_evidence"]["bruhat_order_verifier_ready"] is False
    assert boundary["reported_result"]["hypercube_dimension"] == "m * 2^(m-1)"
    assert "does not claim permutation-pair candidate schemas" in (
        boundary["claim_boundary"]
    )


def test_bruhat_intervals_boundary_rejects_premature_runtime_claims():
    boundary = bruhat_intervals_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][2]["status"] = "verified_local_snapshot"
    boundary["framework_components"][0]["local_status"] = "implemented"
    boundary["local_evidence"]["bruhat_order_verifier_ready"] = True
    boundary["local_evidence"]["repository_runtime_verified"] = True
    boundary["reported_result"]["hypercube_dimension"] = "m * 2^m"
    boundary["missing_evidence"]["bruhat_order_verifier"] = "implemented"

    validation = validate_bruhat_intervals_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_bruhat_order_verifier_ready_overclaim" in codes
    assert "local_evidence_repository_runtime_verified_overclaim" in codes
    assert "reported_result_hypercube_dimension_mismatch" in codes
    assert "missing_evidence_mismatch" in codes


def test_render_bruhat_intervals_boundary_summary_reports_shape():
    summary = render_bruhat_intervals_boundary_summary(
        bruhat_intervals_boundary_record()
    )

    assert "Bruhat Intervals boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | constructive_math_context_without_local_bruhat_hypercube_benchmark |"
        in summary
    )
    assert "| component_count | 14 |" in summary
