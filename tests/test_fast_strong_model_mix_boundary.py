from libreevolve.problems.benchmarks.fast_strong_model_mix_boundary import (
    FAST_STRONG_MODEL_MIX_BOUNDARY_SCHEMA,
    fast_strong_model_mix_boundary_record,
    render_fast_strong_model_mix_boundary_summary,
    validate_fast_strong_model_mix_boundary,
)


def test_fast_strong_model_mix_boundary_accepts_metadata_only_boundary():
    boundary = fast_strong_model_mix_boundary_record()

    validation = validate_fast_strong_model_mix_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "throughput_depth_metadata_without_experiment_report"
    )
    assert validation.required_evidence_field_count == 29
    assert validation.missing_evidence_count == 15
    assert boundary["schema"] == FAST_STRONG_MODEL_MIX_BOUNDARY_SCHEMA
    assert boundary["source_section_id"] == "2.3"
    assert boundary["source_section_ids"] == ["2.3"]
    assert boundary["claim_ready"] is False
    assert "does not claim experiment-level selection traces" in boundary["claim_boundary"]
    assert "fixed compute budget definition" in boundary["claim_boundary"]
    assert "fast/strong provider-model identity" in boundary["claim_boundary"]
    assert "per-lane token/cost/latency accounting" in boundary["claim_boundary"]


def test_fast_strong_model_mix_boundary_rejects_experiment_overclaim():
    boundary = fast_strong_model_mix_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "alphaevolve_fast_strong_model_mix_ready"
    boundary["source_section_ids"] = ["2.4"]
    boundary["missing_evidence"]["experiment_level_selection_traces"] = "recorded"
    boundary["missing_evidence"]["fixed_compute_budget_definition"] = "recorded"
    boundary["required_evidence_fields"] = ["throughput_depth_strategy"]

    validation = validate_fast_strong_model_mix_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_experiment_level_selection_traces" in codes
    assert "invalid_missing_evidence_fixed_compute_budget_definition" in codes
    assert "missing_required_evidence_field" in codes


def test_render_fast_strong_model_mix_boundary_summary_reports_shape():
    summary = render_fast_strong_model_mix_boundary_summary(
        fast_strong_model_mix_boundary_record()
    )

    assert "Fast/strong model-mix boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | throughput_depth_metadata_without_experiment_report |"
        in summary
    )
    assert "| required_evidence_field_count | 29 |" in summary
    assert "| missing_evidence_count | 15 |" in summary
