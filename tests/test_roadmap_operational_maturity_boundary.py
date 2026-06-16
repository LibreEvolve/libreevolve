from libreevolve.problems.benchmarks.roadmap_operational_maturity_boundary import (
    ROADMAP_OPERATIONAL_MATURITY_BOUNDARY_SCHEMA,
    render_roadmap_operational_maturity_boundary_summary,
    roadmap_operational_maturity_boundary_record,
    validate_roadmap_operational_maturity_boundary,
)


def test_roadmap_operational_maturity_accepts_bounded_criteria_map():
    boundary = roadmap_operational_maturity_boundary_record()

    validation = validate_roadmap_operational_maturity_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_operational_maturity_criteria_without_acceptance_threshold"
    )
    assert boundary["schema"] == ROADMAP_OPERATIONAL_MATURITY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["roadmap_heading_present"] is True
    assert boundary["criterion_count"] == 6
    assert boundary["active_todo_ref_count"] == 10
    assert [record["criterion_id"] for record in boundary["criteria_records"]] == [
        "config_validation",
        "strict_jsonl_diagnostics",
        "run_inspection",
        "release_provenance",
        "ci_workflow_coverage",
        "run_artifact_lifecycle",
    ]
    assert all(record["roadmap_phrase_present"] for record in boundary["criteria_records"])
    assert all(
        sidecar["exists"]
        for record in boundary["criteria_records"]
        for sidecar in record["current_sidecar_refs"]
    )
    assert all(
        todo_ref["required_phrase_present"]
        for record in boundary["criteria_records"]
        for todo_ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "acceptance_threshold": "not_recorded_locally",
        "unified_run_artifact_lifecycle_inventory": "not_recorded_locally",
        "semantic_docs_verification": "not_recorded_locally",
        "signed_release_provenance": "not_recorded_locally",
        "ci_cross_platform_policy": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim a global acceptance threshold" in boundary["claim_boundary"]


def test_roadmap_operational_maturity_rejects_overclaim_and_drift():
    boundary = roadmap_operational_maturity_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "operational_maturity_ready"
    boundary["criterion_count"] = 5
    boundary["criteria_records"][0]["roadmap_phrase_present"] = False
    boundary["missing_evidence"]["acceptance_threshold"] = "recorded"
    boundary["required_evidence_fields"] = ["criteria_records"]

    validation = validate_roadmap_operational_maturity_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_criterion_count" in codes
    assert "invalid_criteria_records" in codes
    assert "invalid_missing_evidence_acceptance_threshold" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_operational_maturity_summary_reports_shape():
    summary = render_roadmap_operational_maturity_boundary_summary(
        roadmap_operational_maturity_boundary_record()
    )

    assert "ROADMAP operational maturity boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_operational_maturity_criteria_without_acceptance_threshold |"
        in summary
    )
    assert "| criterion_count | 6 |" in summary
    assert "| active_todo_ref_count | 10 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
