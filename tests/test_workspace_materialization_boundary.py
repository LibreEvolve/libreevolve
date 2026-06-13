from libreevolve.problems.benchmarks.workspace_materialization_boundary import (
    WORKSPACE_MATERIALIZATION_BOUNDARY_SCHEMA,
    render_workspace_materialization_boundary_summary,
    validate_workspace_materialization_boundary,
    workspace_materialization_boundary_record,
)


def test_workspace_materialization_boundary_accepts_current_boundary():
    boundary = workspace_materialization_boundary_record()

    validation = validate_workspace_materialization_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "local_file_workspace_diagnostics_only"
    assert validation.required_evidence_field_count == 12
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == WORKSPACE_MATERIALIZATION_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.1", "Table 1"]
    assert "static_source_copy_portable_identity" in boundary["required_evidence_fields"]
    assert boundary["missing_evidence"]["bulk_directory_operation_diagnostics"] == (
        "not_supported"
    )
    assert "does not claim portable static source-copy identity" in (
        boundary["claim_boundary"]
    )


def test_workspace_materialization_boundary_rejects_future_surface_overclaim():
    boundary = workspace_materialization_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "future_topology_surfaces_ready"
    boundary["source_section_ids"] = ["2.6"]
    boundary["missing_evidence"]["bulk_directory_operation_diagnostics"] = "recorded"
    boundary["required_evidence_fields"] = [
        "candidate_materialization_error_reason_contract"
    ]

    validation = validate_workspace_materialization_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_bulk_directory_operation_diagnostics" in codes
    assert "missing_required_evidence_field" in codes


def test_render_workspace_materialization_boundary_summary_reports_shape():
    summary = render_workspace_materialization_boundary_summary(
        workspace_materialization_boundary_record()
    )

    assert "AlphaEvolve workspace materialization boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | local_file_workspace_diagnostics_only |" in summary
    assert "| required_evidence_field_count | 12 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
