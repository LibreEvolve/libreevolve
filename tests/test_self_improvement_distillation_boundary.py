from libreevolve.problems.benchmarks.self_improvement_distillation_boundary import (
    SELF_IMPROVEMENT_DISTILLATION_BOUNDARY_SCHEMA,
    render_self_improvement_distillation_boundary_summary,
    self_improvement_distillation_boundary_record,
    validate_self_improvement_distillation_boundary,
)


def test_self_improvement_distillation_boundary_accepts_absence_record():
    boundary = self_improvement_distillation_boundary_record()

    validation = validate_self_improvement_distillation_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "discussion_context_only"
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 14
    assert boundary["schema"] == SELF_IMPROVEMENT_DISTILLATION_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["Discussion"]
    assert boundary["local_pdf_page"] == 21
    assert "Discussion context only" in boundary["claim_boundary"]
    assert "does not claim evolved optimization" in boundary["claim_boundary"]
    assert "distillation training runs" in boundary["claim_boundary"]
    assert "not online RL" in boundary["non_evidence_boundaries"]["ttt_rl_grpo_data_jsonl"]


def test_self_improvement_distillation_boundary_rejects_premature_claim():
    boundary = self_improvement_distillation_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "self_improvement_ready"
    boundary["source_section_ids"] = ["Section 3"]
    boundary["missing_evidence"]["distillation_training_run"] = "recorded"
    boundary["non_evidence_boundaries"]["ttt_rl_grpo_data_jsonl"] = "distillation data"
    boundary["required_evidence_fields"] = ["optimized_component_identity"]

    validation = validate_self_improvement_distillation_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_distillation_training_run" in codes
    assert "invalid_non_evidence_boundary_ttt_rl_grpo_data_jsonl" in codes
    assert "missing_required_evidence_field" in codes


def test_render_self_improvement_distillation_boundary_summary_reports_shape():
    summary = render_self_improvement_distillation_boundary_summary(
        self_improvement_distillation_boundary_record()
    )

    assert "AlphaEvolve self-improvement/distillation boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | discussion_context_only |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 14 |" in summary
