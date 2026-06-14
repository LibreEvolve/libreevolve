from libreevolve.problems.benchmarks.lineage_replay_boundary import (
    LINEAGE_REPLAY_BOUNDARY_SCHEMA,
    lineage_replay_boundary_record,
    render_lineage_replay_boundary_summary,
    validate_lineage_replay_boundary,
)


def test_lineage_replay_boundary_accepts_deterministic_id_policy_record():
    boundary = lineage_replay_boundary_record()

    validation = validate_lineage_replay_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "deterministic_loop_id_policy_without_end_to_end_lineage_replay"
    )
    assert validation.required_evidence_field_count == 20
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == LINEAGE_REPLAY_BOUNDARY_SCHEMA
    assert "ordered_llm_call_ids" in boundary["required_evidence_fields"]
    assert "provider-output replay in resumed traces" in boundary["claim_boundary"]


def test_lineage_replay_boundary_rejects_full_replay_overclaim():
    boundary = lineage_replay_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "end_to_end_lineage_replay_ready"
    boundary["missing_evidence"]["end_to_end_resumed_lineage_trace"] = "recorded"
    boundary["required_evidence_fields"] = ["runtime_lineage_replay_policy_schema"]

    validation = validate_lineage_replay_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_end_to_end_resumed_lineage_trace" in codes
    assert "missing_required_evidence_field" in codes


def test_render_lineage_replay_boundary_summary_reports_shape():
    summary = render_lineage_replay_boundary_summary(
        lineage_replay_boundary_record()
    )

    assert "Lineage replay boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | deterministic_loop_id_policy_without_end_to_end_lineage_replay |"
        in summary
    )
    assert "| required_evidence_field_count | 20 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
