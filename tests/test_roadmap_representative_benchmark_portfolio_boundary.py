from libreevolve.problems.benchmarks.roadmap_representative_benchmark_portfolio_boundary import (
    ROADMAP_REPRESENTATIVE_BENCHMARK_PORTFOLIO_BOUNDARY_SCHEMA,
    render_roadmap_representative_benchmark_portfolio_boundary_summary,
    roadmap_representative_benchmark_portfolio_boundary_record,
    validate_roadmap_representative_benchmark_portfolio_boundary,
)


def test_roadmap_representative_benchmark_portfolio_accepts_bounded_map():
    boundary = roadmap_representative_benchmark_portfolio_boundary_record()

    validation = validate_roadmap_representative_benchmark_portfolio_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_benchmark_portfolio_map_without_representative_readiness_gate"
    )
    assert boundary["schema"] == ROADMAP_REPRESENTATIVE_BENCHMARK_PORTFOLIO_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["roadmap_heading_present"] is True
    assert boundary["family_count"] == 5
    assert boundary["active_todo_ref_count"] == 10
    assert boundary["sidecar_ref_count"] == 12
    assert [record["family_id"] for record in boundary["portfolio_family_records"]] == [
        "sorting_network_rediscovery",
        "matrix_tensor_suite",
        "constructive_math_geometry",
        "systems_kernel_scheduling",
        "smoke_fixture_guardrail",
    ]
    assert all(record["roadmap_phrase_present"] for record in boundary["portfolio_family_records"])
    assert all(
        sidecar["exists"]
        for record in boundary["portfolio_family_records"]
        for sidecar in record["current_sidecar_refs"]
    )
    assert all(
        todo_ref["required_phrase_present"]
        for record in boundary["portfolio_family_records"]
        for todo_ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "domain_coverage_matrix": "not_recorded_locally",
        "benchmark_admission_checklist": "not_recorded_locally",
        "repeated_seed_run_matrix": "not_recorded_locally",
        "anti_gaming_certification": "not_recorded_locally",
        "sota_baseline_citations": "not_recorded_locally",
        "portfolio_balance_score": "not_recorded_locally",
        "ci_portfolio_freshness_gate": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim a domain-coverage matrix" in boundary["claim_boundary"]


def test_roadmap_representative_benchmark_portfolio_rejects_overclaim_and_drift():
    boundary = roadmap_representative_benchmark_portfolio_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "representative_benchmark_portfolio_ready"
    boundary["family_count"] = 4
    boundary["portfolio_family_records"][0]["roadmap_phrase_present"] = False
    boundary["missing_evidence"]["domain_coverage_matrix"] = "recorded"
    boundary["required_evidence_fields"] = ["portfolio_family_records"]

    validation = validate_roadmap_representative_benchmark_portfolio_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_family_count" in codes
    assert "invalid_portfolio_family_records" in codes
    assert "invalid_missing_evidence_domain_coverage_matrix" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_representative_benchmark_portfolio_summary_reports_shape():
    summary = render_roadmap_representative_benchmark_portfolio_boundary_summary(
        roadmap_representative_benchmark_portfolio_boundary_record()
    )

    assert "ROADMAP representative benchmark portfolio boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_benchmark_portfolio_map_without_representative_readiness_gate |"
        in summary
    )
    assert "| family_count | 5 |" in summary
    assert "| active_todo_ref_count | 10 |" in summary
    assert "| missing_evidence_count | 8 |" in summary
