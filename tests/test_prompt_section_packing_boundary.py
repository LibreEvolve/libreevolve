from libreevolve.problems.benchmarks.prompt_section_packing_boundary import (
    PROMPT_SECTION_PACKING_BOUNDARY_SCHEMA,
    prompt_section_packing_boundary_record,
    render_prompt_section_packing_boundary_summary,
    validate_prompt_section_packing_boundary,
)


def test_prompt_section_packing_boundary_accepts_mutation_only_boundary():
    boundary = prompt_section_packing_boundary_record()

    validation = validate_prompt_section_packing_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "mutation_section_packing_without_all_role_provider_token_policy"
    )
    assert validation.required_evidence_field_count == 22
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == PROMPT_SECTION_PACKING_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.2", "2.3", "2.4"]
    assert boundary["claim_ready"] is False
    assert (
        "does not claim all-role provider-token section packing"
        in boundary["claim_boundary"]
    )


def test_prompt_section_packing_boundary_rejects_all_role_overclaim():
    boundary = prompt_section_packing_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "all_role_provider_token_section_packing_ready"
    boundary["missing_evidence"]["all_role_provider_token_section_packing"] = "recorded"
    boundary["required_evidence_fields"] = ["prompt_max_chars"]

    validation = validate_prompt_section_packing_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_all_role_provider_token_section_packing" in codes
    assert "missing_required_evidence_field" in codes


def test_render_prompt_section_packing_boundary_summary_reports_shape():
    summary = render_prompt_section_packing_boundary_summary(
        prompt_section_packing_boundary_record()
    )

    assert "Prompt section-packing boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | mutation_section_packing_without_all_role_provider_token_policy |"
        in summary
    )
    assert "| required_evidence_field_count | 22 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
