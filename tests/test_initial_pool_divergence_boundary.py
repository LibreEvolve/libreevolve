from libreevolve.problems.benchmarks.initial_pool_divergence_boundary import (
    INITIAL_POOL_DIVERGENCE_BOUNDARY_SCHEMA,
    initial_pool_divergence_boundary_record,
    render_initial_pool_divergence_boundary_summary,
    validate_initial_pool_divergence_boundary,
)


def test_initial_pool_divergence_boundary_accepts_telemetry_boundary():
    boundary = initial_pool_divergence_boundary_record()

    validation = validate_initial_pool_divergence_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "syntactic_metric_and_evaluator_output_telemetry_only"
    )
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == INITIAL_POOL_DIVERGENCE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        "does not claim task-specific functional-distance artifacts"
        in boundary["claim_boundary"]
    )
    assert "generic_evaluator_output_signature_distance" in (
        boundary["required_evidence_fields"]
    )


def test_initial_pool_divergence_boundary_rejects_discovery_distance_overclaim():
    boundary = initial_pool_divergence_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "functional_discovery_distance_ready"
    boundary["missing_evidence"]["syntax_and_function_joint_claim_gate"] = "recorded"
    boundary["required_evidence_fields"] = ["seed_pool_baseline_records"]

    validation = validate_initial_pool_divergence_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert (
        "invalid_missing_evidence_syntax_and_function_joint_claim_gate"
        in codes
    )
    assert "missing_required_evidence_field" in codes


def test_render_initial_pool_divergence_boundary_summary_reports_shape():
    summary = render_initial_pool_divergence_boundary_summary(
        initial_pool_divergence_boundary_record()
    )

    assert "Initial-pool divergence boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | syntactic_metric_and_evaluator_output_telemetry_only |"
        in summary
    )
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
