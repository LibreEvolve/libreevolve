from libreevolve.problems.benchmarks.sorting_network_rediscovery_boundary import (
    SORTING_NETWORK_REDISCOVERY_BOUNDARY_SCHEMA,
    render_sorting_network_rediscovery_boundary_summary,
    sorting_network_rediscovery_boundary_record,
    validate_sorting_network_rediscovery_boundary,
)


def test_sorting_network_rediscovery_boundary_accepts_absence_record():
    boundary = sorting_network_rediscovery_boundary_record()

    validation = validate_sorting_network_rediscovery_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "executable_candidate_only"
    assert validation.problem_count == 2
    assert validation.required_evidence_field_count == 18
    assert validation.missing_evidence_count == 9
    assert boundary["schema"] == SORTING_NETWORK_REDISCOVERY_BOUNDARY_SCHEMA
    assert boundary["problem_ids"] == ["sorting_network_8", "sorting_network_9"]
    assert boundary["implemented_candidate_evidence"]["sorting_network_8"][
        "known_target_comparators"
    ] == 19
    assert boundary["implemented_candidate_evidence"]["sorting_network_9"][
        "binary_inputs_checked"
    ] == 512
    assert boundary["implemented_candidate_evidence"]["sorting_network_9"][
        "clean_checkout_run_contract"
    ].endswith("sorting_network_9/run_contract.json")
    assert boundary["implemented_candidate_evidence"]["sorting_network_9"][
        "benchmark_goal_prompt_artifact"
    ].endswith("sorting_network_9/benchmark_goal_prompt.json")
    assert boundary["implemented_candidate_evidence"]["sorting_network_9"][
        "benchmark_goal_prompt_validator"
    ] == "libreevolve/problems/benchmarks/benchmark_goal_prompt.py"
    assert "does not claim source-cited benchmark calibration" in boundary["claim_boundary"]


def test_sorting_network_rediscovery_boundary_rejects_premature_claim():
    boundary = sorting_network_rediscovery_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "certified_rediscovery"
    boundary["problem_ids"] = ["sorting_network_9"]
    boundary["missing_evidence"]["repeated_seed_run_tables"] = "recorded"
    boundary["implemented_candidate_evidence"]["sorting_network_8"]["known_target_comparators"] = 20
    boundary["implemented_candidate_evidence"]["sorting_network_9"][
        "clean_checkout_run_contract"
    ] = "missing.json"
    boundary["implemented_candidate_evidence"]["sorting_network_9"][
        "benchmark_goal_prompt_artifact"
    ] = "missing.json"
    boundary["implemented_candidate_evidence"]["sorting_network_9"][
        "benchmark_goal_prompt_validator"
    ] = "missing.py"
    boundary["required_evidence_fields"] = ["exhaustive_zero_one_validation"]

    validation = validate_sorting_network_rediscovery_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_problem_ids" in codes
    assert "invalid_missing_evidence_repeated_seed_run_tables" in codes
    assert "invalid_candidate_sorting_network_8_known_target_comparators" in codes
    assert "invalid_candidate_sorting_network_9_clean_checkout_run_contract" in codes
    assert "invalid_candidate_sorting_network_9_benchmark_goal_prompt_artifact" in codes
    assert "invalid_candidate_sorting_network_9_benchmark_goal_prompt_validator" in codes
    assert "missing_required_evidence_field" in codes


def test_render_sorting_network_rediscovery_boundary_summary_reports_shape():
    summary = render_sorting_network_rediscovery_boundary_summary(
        sorting_network_rediscovery_boundary_record()
    )

    assert "AlphaEvolve sorting-network rediscovery boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | executable_candidate_only |" in summary
    assert "| problem_count | 2 |" in summary
    assert "| required_evidence_field_count | 18 |" in summary
    assert "| missing_evidence_count | 9 |" in summary
