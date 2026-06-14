from libreevolve.problems.benchmarks.compiler_adoption_path_boundary import (
    COMPILER_ADOPTION_PATH_BOUNDARY_SCHEMA,
    compiler_adoption_path_boundary_record,
    render_compiler_adoption_path_boundary_summary,
    validate_compiler_adoption_path_boundary,
)


def test_compiler_adoption_path_boundary_accepts_metadata_boundary():
    boundary = compiler_adoption_path_boundary_record()

    validation = validate_compiler_adoption_path_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "metadata_contract_without_real_compiler_adoption_artifacts"
    )
    assert validation.required_evidence_field_count == 18
    assert validation.missing_evidence_count == 13
    assert boundary["schema"] == COMPILER_ADOPTION_PATH_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["3.3.4"]
    assert boundary["claim_ready"] is False
    assert "does not claim real compiler patch or pass artifacts" in boundary["claim_boundary"]


def test_compiler_adoption_path_boundary_rejects_overclaim():
    boundary = compiler_adoption_path_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "compiler_adoption_artifacts_ready"
    boundary["missing_evidence"]["reviewer_signoff_file"] = "recorded"
    boundary["required_evidence_fields"] = [
        "systems_result_compiler_domain_gate",
    ]

    validation = validate_compiler_adoption_path_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_reviewer_signoff_file" in codes
    assert "missing_required_evidence_field" in codes


def test_render_compiler_adoption_path_boundary_summary_reports_shape():
    summary = render_compiler_adoption_path_boundary_summary(
        compiler_adoption_path_boundary_record()
    )

    assert "Compiler adoption path boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | metadata_contract_without_real_compiler_adoption_artifacts |"
        in summary
    )
    assert "| required_evidence_field_count | 18 |" in summary
    assert "| missing_evidence_count | 13 |" in summary
