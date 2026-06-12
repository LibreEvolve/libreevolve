from libreevolve.problems.benchmarks.prompt_example_copy_boundary import (
    PROMPT_EXAMPLE_COPY_BOUNDARY_SCHEMA,
    prompt_example_copy_boundary_record,
    render_prompt_example_copy_boundary_summary,
    validate_prompt_example_copy_boundary,
)


def test_prompt_example_copy_boundary_accepts_builtin_diagnostics_boundary():
    boundary = prompt_example_copy_boundary_record()

    validation = validate_prompt_example_copy_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "built_in_example_copy_diagnostics_only"
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == PROMPT_EXAMPLE_COPY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        "does not claim hard or configurable rejection policy"
        in boundary["claim_boundary"]
    )


def test_prompt_example_copy_boundary_rejects_full_guard_overclaim():
    boundary = prompt_example_copy_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_prompt_example_copy_guard_ready"
    boundary["missing_evidence"]["semantic_or_renamed_copy_detection"] = "recorded"
    boundary["required_evidence_fields"] = ["built_in_example_inventory"]

    validation = validate_prompt_example_copy_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert (
        "invalid_missing_evidence_semantic_or_renamed_copy_detection"
        in codes
    )
    assert "missing_required_evidence_field" in codes


def test_render_prompt_example_copy_boundary_summary_reports_shape():
    summary = render_prompt_example_copy_boundary_summary(
        prompt_example_copy_boundary_record()
    )

    assert "Prompt example-copy boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | built_in_example_copy_diagnostics_only |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
