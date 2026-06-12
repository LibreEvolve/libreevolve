from libreevolve.problems.benchmarks.bilateral_trade_boundary import (
    BILATERAL_TRADE_BOUNDARY_SCHEMA,
    bilateral_trade_boundary_record,
    render_bilateral_trade_boundary_summary,
    validate_bilateral_trade_boundary,
)


def test_bilateral_trade_boundary_accepts_absence_record():
    boundary = bilateral_trade_boundary_record()

    validation = validate_bilateral_trade_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "mechanism_design_result_without_local_distribution_benchmark"
    )
    assert validation.component_count == 14
    assert validation.required_evidence_field_count == 24
    assert validation.missing_evidence_count == 20
    assert boundary["schema"] == BILATERAL_TRADE_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v1"
    assert boundary["source_last_revised_date"] == "2026-03-09"
    assert boundary["local_evidence"]["gft_evaluator_ready"] is False
    assert boundary["reported_result"]["approximation_ratio"] == 2.0749
    assert "does not claim bilateral-trade distribution candidate schemas" in (
        boundary["claim_boundary"]
    )


def test_bilateral_trade_boundary_rejects_premature_runtime_claims():
    boundary = bilateral_trade_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][0]["status"] = "verified_local_snapshot"
    boundary["framework_components"][0]["local_status"] = "implemented"
    boundary["local_evidence"]["distribution_candidate_schema_ready"] = True
    boundary["local_evidence"]["gft_evaluator_ready"] = True
    boundary["local_evidence"]["repository_runtime_verified"] = True
    boundary["reported_result"]["approximation_ratio"] = 2.08
    boundary["missing_evidence"]["first_best_gft_evaluator"] = "implemented"

    validation = validate_bilateral_trade_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_distribution_candidate_schema_ready_overclaim" in codes
    assert "local_evidence_gft_evaluator_ready_overclaim" in codes
    assert "local_evidence_repository_runtime_verified_overclaim" in codes
    assert "reported_result_approximation_ratio_mismatch" in codes
    assert "missing_evidence_mismatch" in codes


def test_render_bilateral_trade_boundary_summary_reports_shape():
    summary = render_bilateral_trade_boundary_summary(bilateral_trade_boundary_record())

    assert "Bilateral Trade boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | mechanism_design_result_without_local_distribution_benchmark |"
        in summary
    )
    assert "| component_count | 14 |" in summary
