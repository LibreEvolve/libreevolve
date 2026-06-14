from libreevolve.problems.benchmarks.runtime_rng_replay_boundary import (
    RUNTIME_RNG_REPLAY_BOUNDARY_SCHEMA,
    runtime_rng_replay_boundary_record,
    render_runtime_rng_replay_boundary_summary,
    validate_runtime_rng_replay_boundary,
)


def test_runtime_rng_replay_boundary_accepts_framework_rng_record():
    boundary = runtime_rng_replay_boundary_record()

    validation = validate_runtime_rng_replay_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "framework_rng_snapshot_restore_without_full_resumed_trace_replay"
    )
    assert validation.required_evidence_field_count == 15
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == RUNTIME_RNG_REPLAY_BOUNDARY_SCHEMA
    assert boundary["owned_surfaces"] == [
        "loop_parent_explore_exploit_choice",
        "prompt_template_sampling",
        "program_database_sampling",
        "island_sampling",
        "map_elites_sampling",
    ]
    assert "process-global RNG" in boundary["claim_boundary"]


def test_runtime_rng_replay_boundary_rejects_full_replay_overclaim():
    boundary = runtime_rng_replay_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_sampling_replay_ready"
    boundary["missing_evidence"]["end_to_end_sampling_continuity_trace"] = "recorded"
    boundary["owned_surfaces"] = ["prompt_template_sampling"]

    validation = validate_runtime_rng_replay_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_owned_surfaces" in codes
    assert (
        "invalid_missing_evidence_end_to_end_sampling_continuity_trace"
        in codes
    )


def test_render_runtime_rng_replay_boundary_summary_reports_shape():
    summary = render_runtime_rng_replay_boundary_summary(
        runtime_rng_replay_boundary_record()
    )

    assert "Runtime RNG replay boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | framework_rng_snapshot_restore_without_full_resumed_trace_replay |"
        in summary
    )
    assert "| required_evidence_field_count | 15 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
