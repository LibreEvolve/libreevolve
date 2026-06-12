from libreevolve.problems.benchmarks.provider_diagnostics_replay_boundary import (
    PROVIDER_DIAGNOSTICS_REPLAY_BOUNDARY_SCHEMA,
    provider_diagnostics_replay_boundary_record,
    render_provider_diagnostics_replay_boundary_summary,
    validate_provider_diagnostics_replay_boundary,
)


def test_provider_diagnostics_replay_boundary_accepts_bounded_diagnostics():
    boundary = provider_diagnostics_replay_boundary_record()

    validation = validate_provider_diagnostics_replay_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_scalar_diagnostics_without_raw_provider_replay"
    )
    assert validation.required_evidence_field_count == 18
    assert validation.missing_evidence_count == 4
    assert boundary["schema"] == PROVIDER_DIAGNOSTICS_REPLAY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "does not claim raw provider-payload sidecars" in boundary["claim_boundary"]


def test_provider_diagnostics_replay_boundary_rejects_raw_replay_overclaim():
    boundary = provider_diagnostics_replay_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "raw_provider_replay_ready"
    boundary["missing_evidence"]["raw_provider_payload_sidecars"] = "recorded"
    boundary["required_evidence_fields"] = ["provider_usage_metadata"]

    validation = validate_provider_diagnostics_replay_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_raw_provider_payload_sidecars" in codes
    assert "missing_required_evidence_field" in codes


def test_render_provider_diagnostics_replay_boundary_summary_reports_shape():
    summary = render_provider_diagnostics_replay_boundary_summary(
        provider_diagnostics_replay_boundary_record()
    )

    assert "Provider diagnostics replay boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_scalar_diagnostics_without_raw_provider_replay |"
        in summary
    )
    assert "| required_evidence_field_count | 18 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
