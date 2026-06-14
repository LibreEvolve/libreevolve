from libreevolve.problems.benchmarks.llm_stochastic_reproducibility_boundary import (
    LLM_STOCHASTIC_REPRODUCIBILITY_BOUNDARY_SCHEMA,
    llm_stochastic_reproducibility_boundary_record,
    render_llm_stochastic_reproducibility_boundary_summary,
    validate_llm_stochastic_reproducibility_boundary,
)


def test_llm_stochastic_reproducibility_boundary_accepts_request_telemetry_boundary():
    boundary = llm_stochastic_reproducibility_boundary_record()

    validation = validate_llm_stochastic_reproducibility_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "request_parameter_telemetry_without_deterministic_provider_replay"
    )
    assert validation.required_evidence_field_count == 15
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == LLM_STOCHASTIC_REPRODUCIBILITY_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.2", "2.3", "2.4", "4"]
    assert boundary["claim_ready"] is False
    assert "does not claim a backend/API-mode seed-support matrix" in boundary["claim_boundary"]


def test_llm_stochastic_reproducibility_boundary_rejects_determinism_overclaim():
    boundary = llm_stochastic_reproducibility_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "deterministic_provider_replay_ready"
    boundary["missing_evidence"]["repeated_identical_call_fixtures"] = "recorded"
    boundary["required_evidence_fields"] = [
        "normalized_request_parameters",
    ]

    validation = validate_llm_stochastic_reproducibility_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_repeated_identical_call_fixtures" in codes
    assert "missing_required_evidence_field" in codes


def test_render_llm_stochastic_reproducibility_boundary_summary_reports_shape():
    summary = render_llm_stochastic_reproducibility_boundary_summary(
        llm_stochastic_reproducibility_boundary_record()
    )

    assert "LLM stochastic reproducibility boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | request_parameter_telemetry_without_deterministic_provider_replay |"
        in summary
    )
    assert "| required_evidence_field_count | 15 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
