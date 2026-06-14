from libreevolve.problems.benchmarks.gemini_self_training_loop_boundary import (
    GEMINI_SELF_TRAINING_LOOP_BOUNDARY_SCHEMA,
    gemini_self_training_loop_boundary_record,
    render_gemini_self_training_loop_boundary_summary,
    validate_gemini_self_training_loop_boundary,
)


def test_gemini_self_training_loop_boundary_accepts_deployment_only_boundary():
    boundary = gemini_self_training_loop_boundary_record()

    validation = validate_gemini_self_training_loop_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "pallas_deployment_without_gemini_self_training_loop"
    )
    assert validation.required_evidence_field_count == 19
    assert validation.missing_evidence_count == 17
    assert boundary["schema"] == GEMINI_SELF_TRAINING_LOOP_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["3.3.2", "Discussion"]
    assert boundary["claim_ready"] is False
    assert "does not claim Gemini model-family identity" in boundary["claim_boundary"]


def test_gemini_self_training_loop_boundary_rejects_self_training_overclaim():
    boundary = gemini_self_training_loop_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "gemini_self_training_loop_ready"
    boundary["missing_evidence"]["gemini_training_workload_identity"] = "recorded"
    boundary["required_evidence_fields"] = ["pallas_kernel_deployment_record"]

    validation = validate_gemini_self_training_loop_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_gemini_training_workload_identity" in codes
    assert "missing_required_evidence_field" in codes


def test_render_gemini_self_training_loop_boundary_summary_reports_shape():
    summary = render_gemini_self_training_loop_boundary_summary(
        gemini_self_training_loop_boundary_record()
    )

    assert "Gemini self-training loop boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | pallas_deployment_without_gemini_self_training_loop |"
        in summary
    )
    assert "| required_evidence_field_count | 19 |" in summary
    assert "| missing_evidence_count | 17 |" in summary
