from libreevolve.problems.benchmarks.duplicate_work_policy_boundary import (
    DUPLICATE_WORK_POLICY_BOUNDARY_SCHEMA,
    duplicate_work_policy_boundary_record,
    render_duplicate_work_policy_boundary_summary,
    validate_duplicate_work_policy_boundary,
)


def test_duplicate_work_policy_boundary_accepts_run_local_cache_boundary():
    boundary = duplicate_work_policy_boundary_record()

    validation = validate_duplicate_work_policy_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "run_local_cache_with_durable_exact_workspace_index"
    )
    assert validation.required_evidence_field_count == 17
    assert validation.missing_evidence_count == 8
    assert boundary["schema"] == DUPLICATE_WORK_POLICY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        "does not claim cross-run workspace hash lookup"
        in boundary["claim_boundary"]
    )
    assert "duplicate_work_cache_index.jsonl" in boundary["claim_boundary"]


def test_duplicate_work_policy_boundary_rejects_durable_memory_overclaim():
    boundary = duplicate_work_policy_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "alphaevolve_grade_duplicate_work_memory_ready"
    boundary["missing_evidence"]["durable_evaluation_cache_storage"] = "recorded"
    boundary["required_evidence_fields"] = ["deterministic_workspace_hash_grouping"]

    validation = validate_duplicate_work_policy_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert (
        "invalid_missing_evidence_durable_evaluation_cache_storage"
        in codes
    )
    assert "missing_required_evidence_field" in codes


def test_render_duplicate_work_policy_boundary_summary_reports_shape():
    summary = render_duplicate_work_policy_boundary_summary(
        duplicate_work_policy_boundary_record()
    )

    assert "Duplicate-work policy boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | run_local_cache_with_durable_exact_workspace_index |"
        in summary
    )
    assert "| required_evidence_field_count | 17 |" in summary
    assert "| missing_evidence_count | 8 |" in summary
