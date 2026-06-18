from libreevolve.problems.benchmarks.prompt_database_parity_boundary import (
    PROMPT_DATABASE_PARITY_BOUNDARY_SCHEMA,
    prompt_database_parity_boundary_record,
    render_prompt_database_parity_boundary_summary,
    validate_prompt_database_parity_boundary,
)


def test_prompt_database_parity_boundary_accepts_local_prompt_arm_boundary():
    boundary = prompt_database_parity_boundary_record()

    validation = validate_prompt_database_parity_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "local_prompt_arm_history_without_solution_database_equivalent_archive"
    )
    assert validation.required_evidence_field_count == 19
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == PROMPT_DATABASE_PARITY_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.2"]
    assert boundary["claim_ready"] is False
    assert boundary["runtime_surfaces"]["history_stream"] == "prompt_history.jsonl"
    assert (
        "does not claim prompt-side archive retention policy"
        in boundary["claim_boundary"]
    )


def test_prompt_database_parity_boundary_rejects_archive_overclaim():
    boundary = prompt_database_parity_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "solution_database_equivalent_prompt_archive_ready"
    boundary["missing_evidence"]["prompt_side_archive_retention_policy"] = "recorded"
    boundary["runtime_surfaces"]["selection_policy"] = "map_elites_prompt_archive"
    boundary["required_evidence_fields"] = ["prompt_history_jsonl"]

    validation = validate_prompt_database_parity_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_runtime_surfaces" in codes
    assert (
        "invalid_missing_evidence_prompt_side_archive_retention_policy"
        in codes
    )
    assert "missing_required_evidence_field" in codes


def test_render_prompt_database_parity_boundary_summary_reports_shape():
    summary = render_prompt_database_parity_boundary_summary(
        prompt_database_parity_boundary_record()
    )

    assert "PromptDatabase parity boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | local_prompt_arm_history_without_solution_database_equivalent_archive |"
        in summary
    )
    assert "| required_evidence_field_count | 19 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
