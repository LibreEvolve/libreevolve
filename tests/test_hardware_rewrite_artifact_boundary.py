from libreevolve.problems.benchmarks.hardware_rewrite_artifact_boundary import (
    HARDWARE_REWRITE_ARTIFACT_BOUNDARY_SCHEMA,
    hardware_rewrite_artifact_boundary_record,
    render_hardware_rewrite_artifact_boundary_summary,
    validate_hardware_rewrite_artifact_boundary,
)


def test_hardware_rewrite_artifact_boundary_accepts_metadata_only_boundary():
    boundary = hardware_rewrite_artifact_boundary_record()

    validation = validate_hardware_rewrite_artifact_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "metadata_contract_without_concrete_rewrite_artifacts"
    )
    assert validation.required_evidence_field_count == 19
    assert validation.missing_evidence_count == 16
    assert boundary["schema"] == HARDWARE_REWRITE_ARTIFACT_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["3.3.3"]
    assert boundary["claim_ready"] is False
    assert "does not claim an exact TPU arithmetic-circuit identity" in boundary["claim_boundary"]


def test_hardware_rewrite_artifact_boundary_rejects_artifact_overclaim():
    boundary = hardware_rewrite_artifact_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "hardware_rewrite_artifacts_ready"
    boundary["missing_evidence"]["source_verilog_artifact"] = "recorded"
    boundary["required_evidence_fields"] = [
        "systems_result_hardware_domain_gate",
    ]

    validation = validate_hardware_rewrite_artifact_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_source_verilog_artifact" in codes
    assert "missing_required_evidence_field" in codes


def test_render_hardware_rewrite_artifact_boundary_summary_reports_shape():
    summary = render_hardware_rewrite_artifact_boundary_summary(
        hardware_rewrite_artifact_boundary_record()
    )

    assert "Hardware rewrite artifact boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | metadata_contract_without_concrete_rewrite_artifacts |"
        in summary
    )
    assert "| required_evidence_field_count | 19 |" in summary
    assert "| missing_evidence_count | 16 |" in summary
