from libreevolve.problems.benchmarks.primary_prompt_role_telemetry_boundary import (
    PRIMARY_PROMPT_ROLE_TELEMETRY_BOUNDARY_SCHEMA,
    primary_prompt_role_telemetry_boundary_record,
    render_primary_prompt_role_telemetry_boundary_summary,
    validate_primary_prompt_role_telemetry_boundary,
)


def test_primary_prompt_role_telemetry_boundary_accepts_hash_only_join_boundary():
    boundary = primary_prompt_role_telemetry_boundary_record()

    validation = validate_primary_prompt_role_telemetry_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "hash_only_prompt_role_policy_join_without_provider_payload_parity"
    )
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == PRIMARY_PROMPT_ROLE_TELEMETRY_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.2"]
    assert boundary["claim_ready"] is False
    assert (
        boundary["joined_policy_shapes"]["configured_structured_messages"][
            "instruction_metadata_retention"
        ]
        == "hash_only"
    )
    assert (
        "does not claim provider-family payload shape audit"
        in boundary["claim_boundary"]
    )


def test_primary_prompt_role_telemetry_boundary_rejects_payload_overclaim():
    boundary = primary_prompt_role_telemetry_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "provider_payload_parity_ready"
    boundary["missing_evidence"]["provider_family_payload_shape_audit"] = "recorded"
    boundary["joined_policy_shapes"]["configured_structured_messages"][
        "instruction_metadata_retention"
    ] = "raw_text"
    boundary["required_evidence_fields"] = ["mutation_call_id_join"]

    validation = validate_primary_prompt_role_telemetry_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert (
        "invalid_missing_evidence_provider_family_payload_shape_audit"
        in codes
    )
    assert "invalid_instruction_metadata_retention" in codes
    assert "missing_required_evidence_field" in codes


def test_render_primary_prompt_role_telemetry_boundary_summary_reports_shape():
    summary = render_primary_prompt_role_telemetry_boundary_summary(
        primary_prompt_role_telemetry_boundary_record()
    )

    assert "Primary-prompt role telemetry boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | hash_only_prompt_role_policy_join_without_provider_payload_parity |"
        in summary
    )
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
