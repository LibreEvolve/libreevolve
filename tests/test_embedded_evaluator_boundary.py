from libreevolve.problems.benchmarks.embedded_evaluator_boundary import (
    EMBEDDED_EVALUATOR_BOUNDARY_SCHEMA,
    embedded_evaluator_boundary_record,
    render_embedded_evaluator_boundary_summary,
    validate_embedded_evaluator_boundary,
)


def test_embedded_evaluator_boundary_accepts_absence_record():
    boundary = embedded_evaluator_boundary_record()

    validation = validate_embedded_evaluator_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "embedded_entrypoint_without_full_figure3_parity"
    assert validation.required_evidence_field_count == 22
    assert validation.missing_evidence_count == 12
    assert boundary["schema"] == EMBEDDED_EVALUATOR_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.1", "2.3"]
    assert boundary["source_figure_ids"] == ["Figure 3"]
    assert "does not claim full AlphaEvolve Figure 3 evaluator parity" in (
        boundary["claim_boundary"]
    )
    assert "embedded_only_problem_definition" in boundary["required_evidence_fields"]
    assert "default_candidate_owned_evaluator_policy" in (
        boundary["required_evidence_fields"]
    )
    assert (
        boundary["missing_evidence"]["default_candidate_owned_evaluator_loading"]
        == "not_recorded_locally"
    )
    assert "Figure 3 codebase fixture identity" in boundary["claim_boundary"]
    assert "generated_task_input_stream" in boundary["required_evidence_fields"]
    assert (
        boundary["missing_evidence"]["replayable_generated_input_artifact"]
        == "not_recorded_locally"
    )
    assert boundary["task_input_replay_boundary"]["claim_ready"] is False
    assert "generated task-input stream" in (
        boundary["task_input_replay_boundary"]["missing_before_task_input_parity"]
    )


def test_embedded_evaluator_boundary_rejects_premature_figure3_claim():
    boundary = embedded_evaluator_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_figure3_parity_recorded"
    boundary["source_section_ids"] = ["2.1"]
    boundary["source_figure_ids"] = ["Figure 2"]
    boundary["missing_evidence"]["build_isolation_policy"] = "recorded"
    boundary["required_evidence_fields"] = ["candidate_primary_file"]
    boundary["task_input_replay_boundary"]["claim_ready"] = True

    validation = validate_embedded_evaluator_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_source_figure_ids" in codes
    assert "invalid_missing_evidence_build_isolation_policy" in codes
    assert "missing_required_evidence_field" in codes
    assert "task_input_replay_overclaim" in codes


def test_render_embedded_evaluator_boundary_summary_reports_shape():
    summary = render_embedded_evaluator_boundary_summary(
        embedded_evaluator_boundary_record()
    )

    assert "AlphaEvolve embedded evaluator boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | embedded_entrypoint_without_full_figure3_parity |" in summary
    assert "| required_evidence_field_count | 22 |" in summary
    assert "| missing_evidence_count | 12 |" in summary
