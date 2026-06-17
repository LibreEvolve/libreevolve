from libreevolve.problems.benchmarks.evolutionary_database_boundary import (
    EVOLUTIONARY_DATABASE_BOUNDARY_SCHEMA,
    evolutionary_database_boundary_record,
    render_evolutionary_database_boundary_summary,
    validate_evolutionary_database_boundary,
)


def test_evolutionary_database_boundary_accepts_current_run_resurfacing_scope():
    boundary = evolutionary_database_boundary_record()

    validation = validate_evolutionary_database_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "current_run_resurfacing_without_durable_database"
    assert validation.required_evidence_field_count == 20
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == EVOLUTIONARY_DATABASE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert len(boundary["implemented_runtime_evidence"]) == 14
    assert (
        "does not claim a durable cross-run query store"
        in boundary["claim_boundary"]
    )


def test_evolutionary_database_boundary_rejects_durable_database_overclaim():
    boundary = evolutionary_database_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "durable_alphaevolve_database_ready"
    boundary["missing_evidence"]["durable_cross_run_query_store"] = "recorded"
    boundary["required_evidence_fields"] = ["accepted_history_jsonl"]
    del boundary["implemented_runtime_evidence"]["artifact_index_summary"]

    validation = validate_evolutionary_database_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_durable_cross_run_query_store" in codes
    assert "missing_required_evidence_field" in codes
    assert "missing_implemented_runtime_evidence" in codes


def test_render_evolutionary_database_boundary_summary_reports_shape():
    summary = render_evolutionary_database_boundary_summary(
        evolutionary_database_boundary_record()
    )

    assert "Evolutionary database boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | current_run_resurfacing_without_durable_database |" in summary
    assert "| required_evidence_field_count | 20 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
