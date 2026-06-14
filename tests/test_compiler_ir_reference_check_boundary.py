from libreevolve.problems.benchmarks.compiler_ir_reference_check_boundary import (
    COMPILER_IR_REFERENCE_CHECK_BOUNDARY_SCHEMA,
    compiler_ir_reference_check_boundary_record,
    render_compiler_ir_reference_check_boundary_summary,
    validate_compiler_ir_reference_check_boundary,
)


def test_compiler_ir_reference_check_boundary_accepts_metadata_boundary():
    boundary = compiler_ir_reference_check_boundary_record()

    validation = validate_compiler_ir_reference_check_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "metadata_contract_without_real_ir_reference_check_artifacts"
    )
    assert validation.required_evidence_field_count == 16
    assert validation.missing_evidence_count == 11
    assert boundary["schema"] == COMPILER_IR_REFERENCE_CHECK_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["3.3.4"]
    assert boundary["claim_ready"] is False
    assert "does not claim real reference implementation artifacts" in boundary["claim_boundary"]


def test_compiler_ir_reference_check_boundary_rejects_overclaim():
    boundary = compiler_ir_reference_check_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "compiler_ir_reference_check_artifacts_ready"
    boundary["missing_evidence"]["per_edit_reference_check_outputs"] = "recorded"
    boundary["required_evidence_fields"] = [
        "systems_result_compiler_domain_gate",
    ]

    validation = validate_compiler_ir_reference_check_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_per_edit_reference_check_outputs" in codes
    assert "missing_required_evidence_field" in codes


def test_render_compiler_ir_reference_check_boundary_summary_reports_shape():
    summary = render_compiler_ir_reference_check_boundary_summary(
        compiler_ir_reference_check_boundary_record()
    )

    assert "Compiler IR reference-check boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | metadata_contract_without_real_ir_reference_check_artifacts |"
        in summary
    )
    assert "| required_evidence_field_count | 16 |" in summary
    assert "| missing_evidence_count | 11 |" in summary
