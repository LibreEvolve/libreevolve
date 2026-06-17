from libreevolve.problems.benchmarks.restore_certification_boundary import (
    RESTORE_CERTIFICATION_BOUNDARY_SCHEMA,
    render_restore_certification_boundary_summary,
    restore_certification_boundary_record,
    validate_restore_certification_boundary,
)


def test_restore_certification_boundary_accepts_compatible_manifest_scope():
    boundary = restore_certification_boundary_record()

    validation = validate_restore_certification_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "compatible_manifest_restore_certification_without_full_replay_proof"
    )
    assert validation.required_evidence_field_count == 22
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == RESTORE_CERTIFICATION_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert len(boundary["implemented_runtime_evidence"]) == 17
    assert (
        "explicit separation of quarantine diagnostics from accepted state"
        in boundary["claim_boundary"]
    )


def test_restore_certification_boundary_rejects_full_replay_overclaim():
    boundary = restore_certification_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "end_to_end_restore_replay_certified"
    boundary["missing_evidence"]["independent_restore_replay_audit"] = "recorded"
    boundary["required_evidence_fields"] = ["runtime_restore_certification_schema"]
    del boundary["implemented_runtime_evidence"]["provider_output_replay_exclusion"]

    validation = validate_restore_certification_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_independent_restore_replay_audit" in codes
    assert "missing_required_evidence_field" in codes
    assert "missing_implemented_runtime_evidence" in codes


def test_render_restore_certification_boundary_summary_reports_shape():
    summary = render_restore_certification_boundary_summary(
        restore_certification_boundary_record()
    )

    assert "Restore certification boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | compatible_manifest_restore_certification_without_full_replay_proof |"
        in summary
    )
    assert "| required_evidence_field_count | 22 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
