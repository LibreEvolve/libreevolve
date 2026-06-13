from libreevolve.problems.benchmarks.stochastic_prompt_format_boundary import (
    STOCHASTIC_PROMPT_FORMAT_BOUNDARY_SCHEMA,
    render_stochastic_prompt_format_boundary_summary,
    stochastic_prompt_format_boundary_record,
    validate_stochastic_prompt_format_boundary,
)


def test_stochastic_prompt_format_boundary_accepts_effective_config_boundary():
    boundary = stochastic_prompt_format_boundary_record()

    validation = validate_stochastic_prompt_format_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "effective_config_distribution_without_separate_source_identity"
    )
    assert validation.required_evidence_field_count == 16
    assert validation.missing_evidence_count == 8
    assert boundary["schema"] == STOCHASTIC_PROMPT_FORMAT_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.2"]
    assert boundary["claim_ready"] is False
    assert (
        "does not claim separate distribution config source path"
        in boundary["claim_boundary"]
    )


def test_stochastic_prompt_format_boundary_rejects_separate_source_overclaim():
    boundary = stochastic_prompt_format_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "separate_source_distribution_claim_ready"
    boundary["missing_evidence"]["separate_distribution_config_source_path"] = "recorded"
    boundary["required_evidence_fields"] = ["prompt_format_markers"]

    validation = validate_stochastic_prompt_format_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert (
        "invalid_missing_evidence_separate_distribution_config_source_path"
        in codes
    )
    assert "missing_required_evidence_field" in codes


def test_render_stochastic_prompt_format_boundary_summary_reports_shape():
    summary = render_stochastic_prompt_format_boundary_summary(
        stochastic_prompt_format_boundary_record()
    )

    assert "Stochastic prompt-format boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | effective_config_distribution_without_separate_source_identity |"
        in summary
    )
    assert "| required_evidence_field_count | 16 |" in summary
    assert "| missing_evidence_count | 8 |" in summary
