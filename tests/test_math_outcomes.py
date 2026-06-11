from libreevolve.problems.benchmarks.math_outcomes import (
    EXPECTED_REQUIRED_AGGREGATE_FIELDS,
    EXPECTED_REQUIRED_INSTANCE_FIELDS,
    EXPECTED_SOURCE_SUMMARY,
    MATH_OUTCOME_BOUNDARY_SCHEMA,
    alphaevolve_math_outcome_boundary,
    validate_math_outcome_boundary,
)


def test_math_outcome_boundary_is_exported_from_benchmark_package():
    from libreevolve.problems import benchmarks

    boundary = benchmarks.alphaevolve_math_outcome_boundary()

    assert boundary["schema"] == benchmarks.MATH_OUTCOME_BOUNDARY_SCHEMA
    assert benchmarks.validate_math_outcome_boundary(boundary).ok is True


def test_alphaevolve_math_outcome_boundary_preserves_section_3_2_claim():
    boundary = alphaevolve_math_outcome_boundary()
    validation = validate_math_outcome_boundary(boundary)

    assert validation.ok is True
    assert validation.status == "not_recorded_locally"
    assert validation.minimum_problem_instances == 51
    assert validation.minimum_branch_count == 6
    assert boundary["schema"] == MATH_OUTCOME_BOUNDARY_SCHEMA
    for field, expected_value in EXPECTED_SOURCE_SUMMARY.items():
        assert boundary[field] == expected_value
    assert boundary["required_instance_fields"] == list(EXPECTED_REQUIRED_INSTANCE_FIELDS)
    assert boundary["required_aggregate_fields"] == list(EXPECTED_REQUIRED_AGGREGATE_FIELDS)
    assert set(boundary["missing_evidence"].values()) == {"not_recorded_locally"}
    assert "does not claim local per-problem outcome rows" in boundary["scope_boundary"]


def test_math_outcome_boundary_rejects_premature_aggregate_claims():
    boundary = alphaevolve_math_outcome_boundary()
    boundary["status"] = "recorded"
    boundary["minimum_problem_instances"] = 50
    boundary["minimum_branch_count"] = 5
    boundary["rediscovered_best_known_percent_approx"] = 90.0
    boundary["improved_sota_percent_approx"] = 20.0
    boundary["required_instance_fields"] = ["instance_id"]
    boundary["required_aggregate_fields"] = ["total_problem_instances"]
    boundary["missing_evidence"]["aggregate_counts"] = "recorded"
    boundary["scope_boundary"] = "Local aggregate evidence is ready."

    validation = validate_math_outcome_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_status" in codes
    assert "invalid_minimum_problem_instances" in codes
    assert "invalid_minimum_branch_count" in codes
    assert "invalid_rediscovered_best_known_percent_approx" in codes
    assert "invalid_required_instance_fields" in codes
    assert "invalid_required_aggregate_fields" in codes
    assert "invalid_missing_aggregate_counts" in codes
    assert "invalid_aggregate_percent_sum" in codes
    assert "missing_scope_boundary" in codes


def test_math_outcome_boundary_rejects_missing_evidence_shape():
    boundary = alphaevolve_math_outcome_boundary()
    boundary["missing_evidence"] = []

    validation = validate_math_outcome_boundary(boundary)

    assert validation.ok is False
    assert [issue.code for issue in validation.issues] == ["invalid_missing_evidence"]
