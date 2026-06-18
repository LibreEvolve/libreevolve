from libreevolve.problems.benchmarks.roadmap_benchmark_portfolio_readiness_boundary import (
    ROADMAP_BENCHMARK_PORTFOLIO_READINESS_BOUNDARY_SCHEMA,
    render_roadmap_benchmark_portfolio_readiness_boundary_summary,
    roadmap_benchmark_portfolio_readiness_boundary_record,
    validate_roadmap_benchmark_portfolio_readiness_boundary,
)


def test_roadmap_benchmark_portfolio_readiness_accepts_bounded_matrix():
    boundary = roadmap_benchmark_portfolio_readiness_boundary_record()

    validation = validate_roadmap_benchmark_portfolio_readiness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_benchmark_portfolio_readiness_matrix_without_representative_gate"
    )
    assert boundary["schema"] == ROADMAP_BENCHMARK_PORTFOLIO_READINESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_portfolio_boundary_input"]
        == "papers/roadmap_representative_benchmark_portfolio_boundary.json"
    )
    assert boundary["source_family_count"] == 5
    assert boundary["source_active_todo_ref_count"] == 10
    assert boundary["source_sidecar_ref_count"] == 12
    assert boundary["readiness_criterion_count"] == 6
    assert boundary["sidecar_ref_count"] == 12
    assert boundary["active_todo_ref_count"] == 12
    assert [record["criterion_id"] for record in boundary["readiness_criteria"]] == [
        "domain_coverage_matrix",
        "benchmark_admission_checklist",
        "repeated_seed_run_matrix",
        "anti_gaming_certification",
        "sota_baseline_citation_sufficiency",
        "portfolio_balance_ci_freshness",
    ]
    assert boundary["benchmark_portfolio_claim_guard_count"] == 6
    assert [
        record["criterion_id"] for record in boundary["benchmark_portfolio_claim_guard"]
    ] == [
        "domain_coverage_matrix",
        "benchmark_admission_checklist",
        "repeated_seed_run_matrix",
        "anti_gaming_certification",
        "sota_baseline_citation_sufficiency",
        "portfolio_balance_ci_freshness",
    ]
    assert all(
        "missing_before_representative_claim" in record
        for record in boundary["benchmark_portfolio_claim_guard"]
    )
    assert all(
        sidecar["exists"]
        for record in boundary["readiness_criteria"]
        for sidecar in record["sidecar_refs"]
    )
    assert all(
        todo_ref["exists"] and todo_ref["required_phrase_present"]
        for record in boundary["readiness_criteria"]
        for todo_ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "domain_coverage_matrix": "not_recorded_locally",
        "benchmark_admission_checklist": "not_recorded_locally",
        "repeated_seed_run_matrix": "not_recorded_locally",
        "anti_gaming_certification": "not_recorded_locally",
        "sota_baseline_citation_sufficiency": "not_recorded_locally",
        "portfolio_balance_ci_freshness": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim a domain-coverage matrix" in boundary["claim_boundary"]
    assert "claim guard for each portfolio surface" in boundary["claim_boundary"]


def test_roadmap_benchmark_portfolio_readiness_rejects_overclaim_and_drift():
    boundary = roadmap_benchmark_portfolio_readiness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "representative_benchmark_portfolio_gate_ready"
    boundary["readiness_criterion_count"] = 0
    boundary["readiness_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["benchmark_portfolio_claim_guard_count"] = 0
    boundary["missing_evidence"]["domain_coverage_matrix"] = "recorded"
    boundary["required_evidence_fields"] = ["domain_coverage_matrix"]

    validation = validate_roadmap_benchmark_portfolio_readiness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_readiness_criterion_count" in codes
    assert "invalid_readiness_criteria" in codes
    assert "invalid_benchmark_portfolio_claim_guard_count" in codes
    assert "invalid_missing_evidence_domain_coverage_matrix" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_benchmark_portfolio_readiness_summary_reports_shape():
    summary = render_roadmap_benchmark_portfolio_readiness_boundary_summary(
        roadmap_benchmark_portfolio_readiness_boundary_record()
    )

    assert "ROADMAP benchmark portfolio readiness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_benchmark_portfolio_readiness_matrix_without_representative_gate |"
        in summary
    )
    assert "| readiness_criterion_count | 6 |" in summary
    assert "| sidecar_ref_count | 12 |" in summary
    assert "| active_todo_ref_count | 12 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
