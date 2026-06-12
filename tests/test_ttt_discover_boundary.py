from libreevolve.problems.benchmarks.ttt_discover_boundary import (
    TTT_DISCOVER_BOUNDARY_SCHEMA,
    render_ttt_discover_boundary_summary,
    ttt_discover_boundary_record,
    validate_ttt_discover_boundary,
)


def test_ttt_discover_boundary_accepts_absence_record():
    boundary = ttt_discover_boundary_record()

    validation = validate_ttt_discover_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "test_time_training_context_without_local_policy_update_runtime"
    )
    assert validation.component_count == 14
    assert validation.required_evidence_field_count == 24
    assert validation.missing_evidence_count == 20
    assert boundary["schema"] == TTT_DISCOVER_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v2"
    assert boundary["source_last_revised_date"] == "2026-02-05"
    assert boundary["local_evidence"]["policy_update_loop_ready"] is False
    assert boundary["reported_method"]["training_steps"] == 50
    assert boundary["reported_method"]["rollouts_per_step"] == 512
    assert "does not claim test-time policy weight updates" in (
        boundary["claim_boundary"]
    )


def test_ttt_discover_boundary_rejects_premature_runtime_claims():
    boundary = ttt_discover_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][1]["status"] = "verified_local_snapshot"
    boundary["framework_components"][0]["local_status"] = "implemented"
    boundary["local_evidence"]["policy_update_loop_ready"] = True
    boundary["local_evidence"]["repository_runtime_verified"] = True
    boundary["reported_method"]["training_steps"] = 49
    boundary["reported_results"][0] = "Erdos minimum overlap improved to 0.3809"
    boundary["missing_evidence"]["test_time_training_policy_update_loop"] = (
        "implemented"
    )

    validation = validate_ttt_discover_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_policy_update_loop_ready_overclaim" in codes
    assert "local_evidence_repository_runtime_verified_overclaim" in codes
    assert "reported_method_training_steps_mismatch" in codes
    assert "reported_results_mismatch" in codes
    assert "missing_evidence_mismatch" in codes


def test_render_ttt_discover_boundary_summary_reports_shape():
    summary = render_ttt_discover_boundary_summary(ttt_discover_boundary_record())

    assert "TTT-Discover boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | test_time_training_context_without_local_policy_update_runtime |"
        in summary
    )
    assert "| component_count | 14 |" in summary
