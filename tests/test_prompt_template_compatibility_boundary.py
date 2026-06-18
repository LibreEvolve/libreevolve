from libreevolve.problems.benchmarks.prompt_template_compatibility_boundary import (
    PROMPT_TEMPLATE_COMPATIBILITY_BOUNDARY_SCHEMA,
    prompt_template_compatibility_boundary_record,
    render_prompt_template_compatibility_boundary_summary,
    validate_prompt_template_compatibility_boundary,
)


def test_prompt_template_compatibility_boundary_accepts_generic_validation_boundary():
    boundary = prompt_template_compatibility_boundary_record()

    validation = validate_prompt_template_compatibility_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "generic_template_validation_without_role_specific_compatibility_policy"
    )
    assert validation.required_evidence_field_count == 19
    assert validation.missing_evidence_count == 9
    assert boundary["schema"] == PROMPT_TEMPLATE_COMPATIBILITY_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.2", "2.3"]
    assert boundary["claim_ready"] is False
    assert (
        boundary["duplicate_arm_policy"]["status"]
        == "independent_prompt_arms_preserved"
    )
    assert (
        "does not claim a role-specific template compatibility matrix"
        in boundary["claim_boundary"]
    )


def test_prompt_template_compatibility_boundary_rejects_role_overclaim():
    boundary = prompt_template_compatibility_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "role_specific_prompt_template_compatibility_ready"
    boundary["missing_evidence"]["role_specific_template_compatibility_matrix"] = (
        "recorded"
    )
    boundary["duplicate_arm_policy"]["semantic_deduplication"] = "performed"
    boundary["required_evidence_fields"] = ["known_placeholder_schema"]

    validation = validate_prompt_template_compatibility_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert (
        "invalid_missing_evidence_role_specific_template_compatibility_matrix"
        in codes
    )
    assert "invalid_duplicate_arm_semantic_deduplication" in codes
    assert "missing_required_evidence_field" in codes


def test_render_prompt_template_compatibility_boundary_summary_reports_shape():
    summary = render_prompt_template_compatibility_boundary_summary(
        prompt_template_compatibility_boundary_record()
    )

    assert "Prompt-template compatibility boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | generic_template_validation_without_role_specific_compatibility_policy |"
        in summary
    )
    assert "| required_evidence_field_count | 19 |" in summary
    assert "| missing_evidence_count | 9 |" in summary
