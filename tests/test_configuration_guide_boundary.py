from libreevolve.problems.benchmarks.configuration_guide_boundary import (
    CONFIGURATION_GUIDE_BOUNDARY_SCHEMA,
    configuration_guide_boundary_record,
    render_configuration_guide_boundary_summary,
    validate_configuration_guide_boundary,
)


def test_configuration_guide_boundary_accepts_current_static_inventory():
    boundary = configuration_guide_boundary_record()

    validation = validate_configuration_guide_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "configuration_guide_static_inventory_with_known_cli_and_llm_accounting_gaps"
    )
    assert boundary["schema"] == CONFIGURATION_GUIDE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert validation.configuration_marker_count == 20
    assert validation.cli_option_marker_count == 14
    assert validation.config_source_anchor_count == 10
    assert validation.cli_source_anchor_count == 8
    assert validation.test_and_doc_anchor_count == 6
    assert validation.missing_cli_option_count == 4
    assert validation.missing_marker_count == 0
    assert validation.missing_evidence_count == 8
    assert boundary["missing_marker_records"] == []
    assert [record["required_marker"] for record in boundary["missing_cli_option_records"]] == [
        "--max-llm-provider-attempts",
        "--max-llm-tokens",
        "--max-llm-cost-microusd",
        "--max-llm-seconds",
    ]
    assert boundary["missing_evidence"] == {
        "complete_config_field_default_map": "not_recorded_locally",
        "complete_cli_option_to_config_map": "not_recorded_locally",
        "yaml_key_validation_semantic_map": "not_recorded_locally",
        "manifest_provenance_field_map": "not_recorded_locally",
        "restore_capability_semantic_map": "not_recorded_locally",
        "runtime_llm_accounting_wording_reconciliation": "not_recorded_locally",
        "configuration_docs_ci_drift_gate": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "runtime.llm_accounting wording gap" in boundary["claim_boundary"]


def test_configuration_guide_boundary_rejects_overclaim_and_drift():
    boundary = configuration_guide_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "configuration_guide_semantic_drift_gate_ready"
    boundary["configuration_marker_count"] = 0
    boundary["configuration_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["cli_option_marker_count"] = 0
    boundary["missing_cli_option_count"] = 0
    boundary["missing_cli_option_records"] = []
    boundary["config_source_anchor_count"] = 0
    boundary["cli_source_anchor_count"] = 0
    boundary["test_and_doc_anchor_count"] = 0
    boundary["missing_marker_count"] = 1
    boundary["missing_marker_records"] = [boundary["configuration_marker_records"][0]]
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["configuration_doc_precedence_markers"]

    validation = validate_configuration_guide_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_configuration_marker_count" in codes
    assert "invalid_configuration_marker_records" in codes
    assert "invalid_cli_option_marker_count" in codes
    assert "invalid_missing_cli_option_count" in codes
    assert "invalid_missing_cli_option_records" in codes
    assert "invalid_config_source_anchor_count" in codes
    assert "invalid_cli_source_anchor_count" in codes
    assert "invalid_test_and_doc_anchor_count" in codes
    assert "invalid_missing_marker_count" in codes
    assert "invalid_missing_marker_records" in codes
    assert "missing_configuration_guide_marker" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_configuration_guide_boundary_summary_reports_shape():
    summary = render_configuration_guide_boundary_summary(
        configuration_guide_boundary_record()
    )

    assert "Configuration guide boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | configuration_guide_static_inventory_with_known_cli_and_llm_accounting_gaps |"
        in summary
    )
    assert "| configuration_marker_count | 20 |" in summary
    assert "| cli_option_marker_count | 14 |" in summary
    assert "| config_source_anchor_count | 10 |" in summary
    assert "| cli_source_anchor_count | 8 |" in summary
    assert "| test_and_doc_anchor_count | 6 |" in summary
    assert "| missing_cli_option_count | 4 |" in summary
    assert "| missing_marker_count | 0 |" in summary
    assert "| missing_evidence_count | 8 |" in summary
