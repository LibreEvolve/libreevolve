from libreevolve.problems.benchmarks.meta_prompt_scoring_boundary import (
    META_PROMPT_SCORING_BOUNDARY_SCHEMA,
    meta_prompt_scoring_boundary_record,
    render_meta_prompt_scoring_boundary_summary,
    validate_meta_prompt_scoring_boundary,
)


def test_meta_prompt_scoring_boundary_accepts_child_score_reward_boundary():
    boundary = meta_prompt_scoring_boundary_record()

    validation = validate_meta_prompt_scoring_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "child_score_prompt_rewards_without_calibrated_lineage_attribution"
    )
    assert validation.required_evidence_field_count == 16
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == META_PROMPT_SCORING_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.2"]
    assert boundary["claim_ready"] is False
    assert boundary["runtime_surfaces"]["reward_metadata_key"] == "last_prompt_reward"
    assert (
        "does not claim calibrated prompt reward signals"
        in boundary["claim_boundary"]
    )


def test_meta_prompt_scoring_boundary_rejects_calibrated_overclaim():
    boundary = meta_prompt_scoring_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "calibrated_prompt_reward_attribution_ready"
    boundary["missing_evidence"]["calibrated_prompt_reward_signal"] = "recorded"
    boundary["runtime_surfaces"]["reward_metadata_key"] = "calibrated_reward"
    boundary["required_evidence_fields"] = ["prompt_reward_mode_absolute"]

    validation = validate_meta_prompt_scoring_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_runtime_surfaces" in codes
    assert "invalid_missing_evidence_calibrated_prompt_reward_signal" in codes
    assert "missing_required_evidence_field" in codes


def test_render_meta_prompt_scoring_boundary_summary_reports_shape():
    summary = render_meta_prompt_scoring_boundary_summary(
        meta_prompt_scoring_boundary_record()
    )

    assert "Meta-prompt scoring boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | child_score_prompt_rewards_without_calibrated_lineage_attribution |"
        in summary
    )
    assert "| required_evidence_field_count | 16 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
