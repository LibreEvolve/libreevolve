from libreevolve.problems.benchmarks.failure_memory_boundary import (
    FAILURE_MEMORY_BOUNDARY_SCHEMA,
    failure_memory_boundary_record,
    render_failure_memory_boundary_summary,
    validate_failure_memory_boundary,
)


def test_failure_memory_boundary_accepts_run_local_diagnostics_boundary():
    boundary = failure_memory_boundary_record()

    validation = validate_failure_memory_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "run_local_failure_diagnostics_not_semantic_memory"
    assert validation.required_evidence_field_count == 18
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == FAILURE_MEMORY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "does not claim durable cross-run failure tables" in boundary["claim_boundary"]


def test_failure_memory_boundary_rejects_semantic_memory_overclaim():
    boundary = failure_memory_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "semantic_failed_proposal_memory_ready"
    boundary["missing_evidence"]["semantic_failed_proposal_retrieval"] = "recorded"
    boundary["required_evidence_fields"] = ["failure_history_jsonl_rows"]

    validation = validate_failure_memory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_semantic_failed_proposal_retrieval" in codes
    assert "missing_required_evidence_field" in codes


def test_render_failure_memory_boundary_summary_reports_shape():
    summary = render_failure_memory_boundary_summary(
        failure_memory_boundary_record()
    )

    assert "Failure memory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | run_local_failure_diagnostics_not_semantic_memory |" in summary
    assert "| required_evidence_field_count | 18 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
