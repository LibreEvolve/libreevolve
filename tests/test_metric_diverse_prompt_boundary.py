from libreevolve.problems.benchmarks.metric_diverse_prompt_boundary import (
    METRIC_DIVERSE_PROMPT_BOUNDARY_SCHEMA,
    metric_diverse_prompt_boundary_record,
    render_metric_diverse_prompt_boundary_summary,
    validate_metric_diverse_prompt_boundary,
)


def test_metric_diverse_prompt_boundary_accepts_prompt_visible_boundary():
    boundary = metric_diverse_prompt_boundary_record()

    validation = validate_metric_diverse_prompt_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "prompt_visible_evidence_not_benchmark_policy"
    assert validation.required_evidence_field_count == 16
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == METRIC_DIVERSE_PROMPT_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.4"]
    assert boundary["claim_ready"] is False
    assert (
        "does not claim benchmark-required metric-diverse prompt policy"
        in boundary["claim_boundary"]
    )


def test_metric_diverse_prompt_boundary_rejects_benchmark_policy_overclaim():
    boundary = metric_diverse_prompt_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "alphaevolve_section_2_4_benchmark_ready"
    boundary["source_section_ids"] = ["2.3"]
    boundary["missing_evidence"]["equal_budget_comparison_report"] = "recorded"
    boundary["required_evidence_fields"] = ["prompt_visible_inspiration_ids"]

    validation = validate_metric_diverse_prompt_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_equal_budget_comparison_report" in codes
    assert "missing_required_evidence_field" in codes


def test_render_metric_diverse_prompt_boundary_summary_reports_shape():
    summary = render_metric_diverse_prompt_boundary_summary(
        metric_diverse_prompt_boundary_record()
    )

    assert "Metric-diverse prompt boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | prompt_visible_evidence_not_benchmark_policy |" in summary
    assert "| required_evidence_field_count | 16 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
