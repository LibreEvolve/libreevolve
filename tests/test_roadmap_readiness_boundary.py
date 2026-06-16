from libreevolve.problems.benchmarks.roadmap_readiness_boundary import (
    ROADMAP_READINESS_BOUNDARY_SCHEMA,
    render_roadmap_readiness_boundary_summary,
    roadmap_readiness_boundary_record,
    validate_roadmap_readiness_boundary,
)


def test_roadmap_readiness_boundary_accepts_weighted_todo_ledger():
    boundary = roadmap_readiness_boundary_record()

    validation = validate_roadmap_readiness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "weighted_todo_ledger_without_semantic_alphaevolve_readiness"
    )
    assert boundary["schema"] == ROADMAP_READINESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["category_count"] == 4
    assert boundary["category_weight_total"] == 100
    assert boundary["readiness_percent_status"] == (
        "todo_ledger_only_not_semantic_alphaevolve_readiness"
    )
    assert boundary["raw_todo_ledger_active_count"] > 0
    assert boundary["raw_todo_ledger_completed_count"] > 0
    assert boundary["weighted_todo_ledger_completion_percent"] > 0
    assert boundary["weighted_todo_ledger_completion_percent"] < 100
    category_ids = {category["category_id"] for category in boundary["categories"]}
    assert "technical_implementation_parity" in category_ids
    assert "paper_source_and_benchmark_evidence" in category_ids
    assert "roadmap_priority_and_phase_evidence" in category_ids
    assert boundary["missing_evidence"] == {
        "semantic_requirement_mapping": "not_recorded_locally",
        "canonical_gap_deduplication": "not_recorded_locally",
        "source_span_disposition_matrix": "not_recorded_locally",
        "category_test_gate_mapping": "not_recorded_locally",
        "benchmark_reproduction_certification": "not_recorded_locally",
        "operational_release_readiness_gate": "not_recorded_locally",
    }
    assert (
        "does not claim semantic AlphaEvolve implementation readiness"
        in boundary["claim_boundary"]
    )


def test_roadmap_readiness_boundary_rejects_readiness_overclaim_and_drift():
    boundary = roadmap_readiness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "semantic_alphaevolve_readiness_ready"
    boundary["category_weight_total"] = 99
    boundary["categories"][0]["active_count"] = 0
    boundary["readiness_percent_status"] = "semantic_alphaevolve_readiness"
    boundary["missing_evidence"]["semantic_requirement_mapping"] = "recorded"
    boundary["required_evidence_fields"] = ["stable_readiness_categories"]

    validation = validate_roadmap_readiness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_category_weight_total" in codes
    assert "invalid_categories" in codes
    assert "invalid_readiness_percent_status" in codes
    assert "invalid_missing_evidence_semantic_requirement_mapping" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_readiness_boundary_summary_reports_shape():
    summary = render_roadmap_readiness_boundary_summary(
        roadmap_readiness_boundary_record()
    )

    assert "ROADMAP readiness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | weighted_todo_ledger_without_semantic_alphaevolve_readiness |"
        in summary
    )
    assert "| category_count | 4 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
    assert "| weighted_todo_ledger_completion_percent |" in summary
