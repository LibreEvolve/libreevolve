from libreevolve.problems.benchmarks.math_outcomes import (
    EXPECTED_HEURISTIC_HANDOFF_SUMMARY,
    EXPECTED_HEURISTIC_STAGE_SEQUENCE_SUMMARY,
    EXPECTED_REQUIRED_AGGREGATE_FIELDS,
    EXPECTED_REQUIRED_HEURISTIC_HANDOFF_FIELDS,
    EXPECTED_REQUIRED_HEURISTIC_STAGE_FIELDS,
    EXPECTED_REQUIRED_INSTANCE_FIELDS,
    EXPECTED_REQUIRED_STARTING_CONSTRUCTION_FIELDS,
    EXPECTED_SOURCE_SUMMARY,
    EXPECTED_STARTING_CONSTRUCTION_SUMMARY,
    MATH_HEURISTIC_HANDOFF_BOUNDARY_SCHEMA,
    MATH_HEURISTIC_STAGE_SEQUENCE_BOUNDARY_SCHEMA,
    MATH_OUTCOME_BOUNDARY_SCHEMA,
    MATH_STARTING_CONSTRUCTION_BOUNDARY_SCHEMA,
    alphaevolve_math_heuristic_handoff_boundary,
    alphaevolve_math_heuristic_stage_sequence_boundary,
    alphaevolve_math_outcome_boundary,
    alphaevolve_math_starting_construction_boundary,
    validate_math_heuristic_handoff_boundary,
    validate_math_heuristic_stage_sequence_boundary,
    validate_math_outcome_boundary,
    validate_math_starting_construction_boundary,
)


def test_math_outcome_boundary_is_exported_from_benchmark_package():
    from libreevolve.problems import benchmarks

    boundary = benchmarks.alphaevolve_math_outcome_boundary()

    assert boundary["schema"] == benchmarks.MATH_OUTCOME_BOUNDARY_SCHEMA
    assert benchmarks.validate_math_outcome_boundary(boundary).ok is True
    starting = benchmarks.alphaevolve_math_starting_construction_boundary()
    assert starting["schema"] == benchmarks.MATH_STARTING_CONSTRUCTION_BOUNDARY_SCHEMA
    assert benchmarks.validate_math_starting_construction_boundary(starting).ok is True
    handoff = benchmarks.alphaevolve_math_heuristic_handoff_boundary()
    assert handoff["schema"] == benchmarks.MATH_HEURISTIC_HANDOFF_BOUNDARY_SCHEMA
    assert benchmarks.validate_math_heuristic_handoff_boundary(handoff).ok is True
    stages = benchmarks.alphaevolve_math_heuristic_stage_sequence_boundary()
    assert stages["schema"] == benchmarks.MATH_HEURISTIC_STAGE_SEQUENCE_BOUNDARY_SCHEMA
    assert benchmarks.validate_math_heuristic_stage_sequence_boundary(stages).ok is True


def test_alphaevolve_math_outcome_boundary_preserves_section_3_2_claim():
    boundary = alphaevolve_math_outcome_boundary()
    validation = validate_math_outcome_boundary(boundary)

    assert validation.ok is True
    assert validation.status == "not_recorded_locally"
    assert validation.minimum_problem_instances == 51
    assert validation.minimum_branch_count == 6
    assert boundary["schema"] == MATH_OUTCOME_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["3.2"]
    for field, expected_value in EXPECTED_SOURCE_SUMMARY.items():
        assert boundary[field] == expected_value
    assert boundary["required_instance_fields"] == list(EXPECTED_REQUIRED_INSTANCE_FIELDS)
    assert boundary["required_aggregate_fields"] == list(EXPECTED_REQUIRED_AGGREGATE_FIELDS)
    assert set(boundary["missing_evidence"].values()) == {"not_recorded_locally"}
    assert boundary["section_3_2_blanket_verification_claim_status"] == (
        "not_present_in_pinned_source"
    )
    assert "verification_claim" not in boundary
    assert "simple or random construction" in boundary["source_fidelity_note"]
    assert "misattributed blanket verification sentence" in boundary["scope_boundary"]
    assert "does not claim local per-problem outcome rows" in boundary["scope_boundary"]


def test_alphaevolve_math_starting_construction_boundary_preserves_section_3_2_claim():
    boundary = alphaevolve_math_starting_construction_boundary()
    validation = validate_math_starting_construction_boundary(boundary)

    assert validation.ok is True
    assert validation.status == "not_recorded_locally"
    assert boundary["schema"] == MATH_STARTING_CONSTRUCTION_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["3.2"]
    for field, expected_value in EXPECTED_STARTING_CONSTRUCTION_SUMMARY.items():
        assert boundary[field] == expected_value
    assert boundary["allowed_claimed_starting_classes"] == ["simple", "random"]
    assert boundary["required_starting_construction_fields"] == list(EXPECTED_REQUIRED_STARTING_CONSTRUCTION_FIELDS)
    assert set(boundary["missing_evidence"].values()) == {"not_recorded_locally"}
    assert "does not claim local per-instance starting construction artifacts" in boundary["scope_boundary"]


def test_alphaevolve_math_heuristic_handoff_boundary_preserves_section_3_2_claim():
    boundary = alphaevolve_math_heuristic_handoff_boundary()
    validation = validate_math_heuristic_handoff_boundary(boundary)

    assert validation.ok is True
    assert validation.status == "not_recorded_locally"
    assert boundary["schema"] == MATH_HEURISTIC_HANDOFF_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["3.2"]
    for field, expected_value in EXPECTED_HEURISTIC_HANDOFF_SUMMARY.items():
        assert boundary[field] == expected_value
    assert boundary["required_handoff_fields"] == list(EXPECTED_REQUIRED_HEURISTIC_HANDOFF_FIELDS)
    assert set(boundary["missing_evidence"].values()) == {"not_recorded_locally"}
    assert "does not claim local heuristic program artifacts" in boundary["scope_boundary"]


def test_alphaevolve_math_heuristic_stage_sequence_boundary_preserves_section_3_2_claim():
    boundary = alphaevolve_math_heuristic_stage_sequence_boundary()
    validation = validate_math_heuristic_stage_sequence_boundary(boundary)

    assert validation.ok is True
    assert validation.status == "not_recorded_locally"
    assert boundary["schema"] == MATH_HEURISTIC_STAGE_SEQUENCE_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["3.2"]
    for field, expected_value in EXPECTED_HEURISTIC_STAGE_SEQUENCE_SUMMARY.items():
        assert boundary[field] == expected_value
    assert boundary["minimum_stage_roles"] == [
        "early_large_gains_from_random_or_simple_initial_states",
        "later_fine_tuning_near_optimal_configurations",
    ]
    assert boundary["required_stage_fields"] == list(EXPECTED_REQUIRED_HEURISTIC_STAGE_FIELDS)
    assert set(boundary["missing_evidence"].values()) == {"not_recorded_locally"}
    assert "does not claim local per-stage heuristic artifacts" in boundary["scope_boundary"]


def test_math_outcome_boundary_rejects_premature_aggregate_claims():
    boundary = alphaevolve_math_outcome_boundary()
    boundary["status"] = "recorded"
    boundary["source_section_ids"] = ["3.1"]
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
    assert "invalid_source_section_ids" in codes
    assert "invalid_minimum_problem_instances" in codes
    assert "invalid_minimum_branch_count" in codes
    assert "invalid_rediscovered_best_known_percent_approx" in codes
    assert "invalid_required_instance_fields" in codes
    assert "invalid_required_aggregate_fields" in codes
    assert "invalid_missing_aggregate_counts" in codes
    assert "invalid_aggregate_percent_sum" in codes
    assert "missing_scope_boundary" in codes


def test_math_starting_construction_boundary_rejects_premature_seed_claims():
    boundary = alphaevolve_math_starting_construction_boundary()
    boundary["status"] = "recorded"
    boundary["source_section_ids"] = ["3.1"]
    boundary["allowed_claimed_starting_classes"] = ["simple", "random", "human_seeded"]
    boundary["unsupported_without_explicit_label"] = ["human_seeded"]
    boundary["required_starting_construction_fields"] = ["instance_id"]
    boundary["missing_evidence"]["baseline_metric_values"] = "recorded"
    boundary["scope_boundary"] = "Local starting constructions are verified."

    validation = validate_math_starting_construction_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_starting_status" in codes
    assert "invalid_starting_source_section_ids" in codes
    assert "invalid_starting_allowed_claimed_starting_classes" in codes
    assert "invalid_allowed_starting_classes" in codes
    assert "invalid_unsupported_starting_classes" in codes
    assert "invalid_required_starting_construction_fields" in codes
    assert "invalid_starting_missing_baseline_metric_values" in codes
    assert "missing_starting_scope_boundary" in codes


def test_math_heuristic_handoff_boundary_rejects_premature_handoff_claims():
    boundary = alphaevolve_math_heuristic_handoff_boundary()
    boundary["status"] = "recorded"
    boundary["source_section_ids"] = ["3.1"]
    boundary["example_budget_seconds"] = 0
    boundary["required_handoff_fields"] = ["instance_id"]
    boundary["missing_evidence"]["produced_construction_artifacts"] = "recorded"
    boundary["scope_boundary"] = "Local heuristic handoff evidence is verified."

    validation = validate_math_heuristic_handoff_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_handoff_status" in codes
    assert "invalid_handoff_source_section_ids" in codes
    assert "invalid_handoff_example_budget_seconds" in codes
    assert "invalid_required_handoff_fields" in codes
    assert "invalid_handoff_missing_produced_construction_artifacts" in codes
    assert "missing_handoff_scope_boundary" in codes


def test_math_heuristic_stage_sequence_boundary_rejects_premature_stage_claims():
    boundary = alphaevolve_math_heuristic_stage_sequence_boundary()
    boundary["status"] = "recorded"
    boundary["source_section_ids"] = ["3.1"]
    boundary["minimum_stage_roles"] = ["early_large_gains_from_random_or_simple_initial_states"]
    boundary["required_stage_fields"] = ["stage_index"]
    boundary["missing_evidence"]["improvement_delta_records"] = "recorded"
    boundary["scope_boundary"] = "Local stage sequence evidence is verified."

    validation = validate_math_heuristic_stage_sequence_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_stage_sequence_status" in codes
    assert "invalid_stage_sequence_source_section_ids" in codes
    assert "invalid_stage_sequence_minimum_stage_roles" in codes
    assert "invalid_stage_sequence_roles" in codes
    assert "invalid_required_stage_fields" in codes
    assert "invalid_stage_sequence_missing_improvement_delta_records" in codes
    assert "missing_stage_sequence_scope_boundary" in codes


def test_math_outcome_boundary_rejects_missing_evidence_shape():
    boundary = alphaevolve_math_outcome_boundary()
    boundary["missing_evidence"] = []

    validation = validate_math_outcome_boundary(boundary)

    assert validation.ok is False
    assert [issue.code for issue in validation.issues] == ["invalid_missing_evidence"]


def test_math_starting_construction_boundary_rejects_missing_evidence_shape():
    boundary = alphaevolve_math_starting_construction_boundary()
    boundary["missing_evidence"] = []

    validation = validate_math_starting_construction_boundary(boundary)

    assert validation.ok is False
    assert [issue.code for issue in validation.issues] == ["invalid_starting_missing_evidence"]


def test_math_heuristic_handoff_boundary_rejects_missing_evidence_shape():
    boundary = alphaevolve_math_heuristic_handoff_boundary()
    boundary["missing_evidence"] = []

    validation = validate_math_heuristic_handoff_boundary(boundary)

    assert validation.ok is False
    assert [issue.code for issue in validation.issues] == ["invalid_handoff_missing_evidence"]


def test_math_heuristic_stage_sequence_boundary_rejects_missing_evidence_shape():
    boundary = alphaevolve_math_heuristic_stage_sequence_boundary()
    boundary["missing_evidence"] = []

    validation = validate_math_heuristic_stage_sequence_boundary(boundary)

    assert validation.ok is False
    assert [issue.code for issue in validation.issues] == ["invalid_stage_sequence_missing_evidence"]
