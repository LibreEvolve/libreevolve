import json

from libreevolve.problems.benchmarks.appendix_b_registry import (
    EXPECTED_APPENDIX_B_RESULT_ROW_BOUNDARY,
    EXPECTED_APPENDIX_B_RESULT_ROW_MISSING_EVIDENCE_KEYS,
    EXPECTED_APPENDIX_B_RESULT_ROW_REQUIRED_FIELDS,
    EXPECTED_B5_SOURCE_FORMULATION,
    EXPECTED_B5_STEP_FUNCTION_BOUNDARY,
    EXPECTED_B5_STEP_FUNCTION_REQUIRED_FIELDS,
    EXPECTED_B6_THEOREM_CONDITION,
    EXPECTED_B6_WITNESS_IDS,
    EXPECTED_B6_WITNESS_REQUIRED_FIELDS,
    EXPECTED_B6_WITNESS_ROWS,
    EXPECTED_B7_PACKING_IDS,
    EXPECTED_B7_PACKING_REQUIRED_FIELDS,
    EXPECTED_B7_PACKING_ROWS,
    EXPECTED_B7_PACKING_SUMMARY,
    EXPECTED_B8_METRIC_CONVENTIONS,
    EXPECTED_B8_WITNESS_IDS,
    EXPECTED_B8_WITNESS_REQUIRED_FIELDS,
    EXPECTED_B8_WITNESS_ROWS,
    EXPECTED_AUTOCORRELATION_LABELS,
    EXPECTED_AUTOCORRELATION_STEP_EVIDENCE,
    EXPECTED_B4_HERMITE_REQUIRED_FIELDS,
    EXPECTED_B4_HERMITE_RESULT,
    EXPECTED_B4_PRIOR_BOUND_ROUNDING,
    EXPECTED_B4_REVISION_REQUIRED_FIELDS,
    EXPECTED_B4_REVISION_RESULT,
    EXPECTED_B4_SIMILARITY_EVIDENCE,
    EXPECTED_B4_SOURCE_FORMULATION,
    EXPECTED_FIGURE5_B12_PRECISION_BOUNDARY,
    EXPECTED_B11_KISSING_IDS,
    EXPECTED_B11_KISSING_REQUIRED_FIELDS,
    EXPECTED_B11_KISSING_ROWS,
    EXPECTED_B11_KISSING_SUMMARY,
    EXPECTED_FAMILY_IDS,
    EXPECTED_HEILBRONN_IDS,
    EXPECTED_HEILBRONN_ROWS,
    EXPECTED_HEILBRONN_SUMMARIES,
    EXPECTED_SUM_OF_RADII_IDS,
    EXPECTED_SUM_OF_RADII_ROWS,
    EXPECTED_SUM_OF_RADII_SUMMARIES,
    EXPECTED_AUTOCORRELATION_STEP_BOUNDARIES,
    EXPECTED_AUTOCORRELATION_STEP_REQUIRED_FIELDS,
    REGISTRY_PATH,
    validate_appendix_b_registry,
)


def test_appendix_b_registry_enumerates_all_alphaevolve_families():
    report = validate_appendix_b_registry()
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    family_ids = [family["id"] for family in data["families"]]
    result_boundary = data["result_row_boundary"]

    assert report.ok is True
    assert report.family_count == 13
    assert tuple(family_ids) == EXPECTED_FAMILY_IDS
    assert report.implemented_count == 1
    assert report.planned_count == 12
    assert report.unsupported_count == 0
    assert family_ids.count("circle_packing_unit_square") == 1
    for field, expected in EXPECTED_APPENDIX_B_RESULT_ROW_BOUNDARY.items():
        assert result_boundary[field] == expected
    assert result_boundary["required_result_row_fields"] == list(EXPECTED_APPENDIX_B_RESULT_ROW_REQUIRED_FIELDS)
    assert set(result_boundary["missing_evidence"]) == set(EXPECTED_APPENDIX_B_RESULT_ROW_MISSING_EVIDENCE_KEYS)
    assert set(result_boundary["source_section_ids"]) == {f"B.{index}" for index in range(1, 14)}
    assert all(
        value == "not_recorded_locally"
        for value in result_boundary["missing_evidence"].values()
    )
    autocorrelation = {
        family["id"]: family
        for family in data["families"][:3]
    }
    for family_id, expected in EXPECTED_AUTOCORRELATION_LABELS.items():
        assert autocorrelation[family_id]["paper_label"]["source_section_id"] == expected["source_section_id"]
        assert autocorrelation[family_id]["paper_label"]["paper_heading"] == expected["paper_heading"]
        assert autocorrelation[family_id]["paper_label"]["constant_id"] == expected["constant_id"]
        assert autocorrelation[family_id]["name"] == expected["display_label"]
        assert autocorrelation[family_id]["paper_label"]["internal_family_id"] == family_id
        assert autocorrelation[family_id]["paper_label"]["internal_label_policy"] == (
            "internal_id_only_not_paper_label"
        )
        evidence = autocorrelation[family_id]["step_function_evidence"]
        for field, expected_value in EXPECTED_AUTOCORRELATION_STEP_EVIDENCE[family_id].items():
            assert evidence[field] == expected_value
        boundary = autocorrelation[family_id]["step_function_payload_boundary"]
        for field, expected_value in EXPECTED_AUTOCORRELATION_STEP_BOUNDARIES[family_id].items():
            assert boundary[field] == expected_value
        assert boundary["required_payload_fields"] == list(EXPECTED_AUTOCORRELATION_STEP_REQUIRED_FIELDS)
        assert boundary["status"] == "not_recorded_locally"
    b4 = next(family for family in data["families"] if family["id"] == "uncertainty_inequality")
    assert b4["source_formulation_evidence"] == EXPECTED_B4_SOURCE_FORMULATION
    assert b4["prior_bound_rounding_evidence"] == EXPECTED_B4_PRIOR_BOUND_ROUNDING
    assert b4["hermite_result_boundary"] == EXPECTED_B4_HERMITE_RESULT
    assert b4["hermite_result_boundary"]["required_payload_fields"] == list(EXPECTED_B4_HERMITE_REQUIRED_FIELDS)
    assert b4["prior_construction_similarity_evidence"] == EXPECTED_B4_SIMILARITY_EVIDENCE
    assert b4["revision_result_boundary"] == EXPECTED_B4_REVISION_RESULT
    assert b4["revision_result_boundary"]["required_revision_fields"] == list(EXPECTED_B4_REVISION_REQUIRED_FIELDS)
    b8 = next(family for family in data["families"] if family["id"] == "max_min_distance_point_sets")
    assert b8["metric_convention_evidence"] == list(EXPECTED_B8_METRIC_CONVENTIONS)
    boundary = b8["witness_certificate_boundary"]
    assert boundary["status"] == "not_recorded_locally"
    assert boundary["required_witness_fields"] == list(EXPECTED_B8_WITNESS_REQUIRED_FIELDS)
    assert [row["result_id"] for row in boundary["missing_witnesses"]] == list(EXPECTED_B8_WITNESS_IDS)
    for witness, expected in zip(boundary["missing_witnesses"], EXPECTED_B8_WITNESS_ROWS, strict=True):
        for field, expected_value in expected.items():
            assert witness[field] == expected_value
    b5 = next(family for family in data["families"] if family["id"] == "erdos_minimum_overlap")
    assert b5["source_formulation_evidence"] == EXPECTED_B5_SOURCE_FORMULATION
    assert b5["step_function_result_boundary"] == EXPECTED_B5_STEP_FUNCTION_BOUNDARY
    assert b5["step_function_result_boundary"]["required_payload_fields"] == list(EXPECTED_B5_STEP_FUNCTION_REQUIRED_FIELDS)
    assert b5["artifact_schema"] == {
        "construction": "normalized_step_function",
        "certificate": "integral_and_shift_overlap_certificate",
    }
    b6 = next(family for family in data["families"] if family["id"] == "sums_differences_finite_sets")
    assert b6["theorem_condition_evidence"] == EXPECTED_B6_THEOREM_CONDITION
    b6_boundary = b6["finite_set_witness_boundary"]
    assert b6_boundary["status"] == "not_recorded_locally"
    assert b6_boundary["required_witness_fields"] == list(EXPECTED_B6_WITNESS_REQUIRED_FIELDS)
    assert [row["result_id"] for row in b6_boundary["missing_witnesses"]] == list(EXPECTED_B6_WITNESS_IDS)
    for witness, expected in zip(b6_boundary["missing_witnesses"], EXPECTED_B6_WITNESS_ROWS, strict=True):
        for field, expected_value in expected.items():
            assert witness[field] == expected_value
    b7 = next(family for family in data["families"] if family["id"] == "regular_hexagon_packing")
    b7_boundary = b7["packing_result_boundary"]
    for field, expected_value in EXPECTED_B7_PACKING_SUMMARY.items():
        assert b7_boundary[field] == expected_value
    assert b7_boundary["required_witness_fields"] == list(EXPECTED_B7_PACKING_REQUIRED_FIELDS)
    assert [row["result_id"] for row in b7_boundary["missing_witnesses"]] == list(EXPECTED_B7_PACKING_IDS)
    for witness, expected in zip(b7_boundary["missing_witnesses"], EXPECTED_B7_PACKING_ROWS, strict=True):
        for field, expected_value in expected.items():
            assert witness[field] == expected_value
    for family_id, expected_summary in EXPECTED_HEILBRONN_SUMMARIES.items():
        family = next(family for family in data["families"] if family["id"] == family_id)
        boundary = family["heilbronn_result_boundary"]
        for field, expected_value in expected_summary.items():
            assert boundary[field] == expected_value
        assert [row["result_id"] for row in boundary["missing_witnesses"]] == list(EXPECTED_HEILBRONN_IDS[family_id])
        for witness, expected in zip(boundary["missing_witnesses"], EXPECTED_HEILBRONN_ROWS[family_id], strict=True):
            for field, expected_value in expected.items():
                assert witness[field] == expected_value
    b11 = next(family for family in data["families"] if family["id"] == "kissing_number_d11")
    b11_boundary = b11["kissing_result_boundary"]
    assert b11_boundary["required_witness_fields"] == list(EXPECTED_B11_KISSING_REQUIRED_FIELDS)
    for field, expected_value in EXPECTED_B11_KISSING_SUMMARY.items():
        assert b11_boundary[field] == expected_value
    assert [row["result_id"] for row in b11_boundary["missing_witnesses"]] == list(EXPECTED_B11_KISSING_IDS)
    for witness, expected in zip(b11_boundary["missing_witnesses"], EXPECTED_B11_KISSING_ROWS, strict=True):
        for field, expected_value in expected.items():
            assert witness[field] == expected_value
    for family_id, expected_summary in EXPECTED_SUM_OF_RADII_SUMMARIES.items():
        family = next(family for family in data["families"] if family["id"] == family_id)
        boundary = family["sum_of_radii_result_boundary"]
        for field, expected_value in expected_summary.items():
            assert boundary[field] == expected_value
        assert [row["result_id"] for row in boundary["missing_witnesses"]] == list(EXPECTED_SUM_OF_RADII_IDS[family_id])
        for witness, expected in zip(boundary["missing_witnesses"], EXPECTED_SUM_OF_RADII_ROWS[family_id], strict=True):
            for field, expected_value in expected.items():
                assert witness[field] == expected_value
    b12_precision = next(family for family in data["families"] if family["id"] == "circle_packing_unit_square")
    assert b12_precision["figure5_b12_precision_boundary"] == EXPECTED_FIGURE5_B12_PRECISION_BOUNDARY


def test_appendix_b_registry_requires_result_row_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    del data["result_row_boundary"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_appendix_b_result_row_boundary"]


def test_appendix_b_registry_rejects_result_row_boundary_overclaim(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    boundary = data["result_row_boundary"]
    boundary["status"] = "recorded"
    boundary["source_section_ids"] = ["B.1"]
    boundary["required_result_row_fields"] = ["result_id"]
    boundary["missing_evidence"]["previous_best_attribution"] = "recorded"
    boundary["scope_boundary"] = "Normalized Appendix B result rows are verified."
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_result_row_boundary_status" in codes
    assert "invalid_result_row_boundary_source_section_ids" in codes
    assert "invalid_result_row_required_fields" in codes
    assert "invalid_result_row_missing_previous_best_attribution" in codes
    assert "missing_result_row_scope_boundary" in codes


def test_appendix_b_registry_requires_result_row_missing_evidence_object(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    data["result_row_boundary"]["missing_evidence"] = ["normalized_result_rows"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["invalid_result_row_missing_evidence"]


def test_appendix_b_registry_requires_advertised_fixtures_to_exist(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    for family in data["families"]:
        if family["id"] == "circle_packing_unit_square":
            family["fixture"] = "libreevolve/problems/examples/missing"
            break
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_fixture_path"]
    assert report.issues[0].family_id == "circle_packing_unit_square"


def test_appendix_b_registry_requires_non_implemented_families_to_avoid_fixtures(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    data["families"][0]["fixture"] = "libreevolve/problems/examples/circle_packing"
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["unexpected_fixture"]
    assert report.issues[0].family_id == "autocorrelation_bounds_k3"


def test_appendix_b_registry_requires_autocorrelation_paper_labels(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    first = data["families"][0]
    first["name"] = "Autocorrelation inequality, k=3"
    first["paper_label"]["constant_id"] = "C0"
    first["paper_label"]["internal_family_id"] = "wrong"
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_paper_label_constant_id" in codes
    assert "invalid_paper_label_internal_id" in codes
    assert "paper_label_name_mismatch" in codes
    assert "paper_label_uses_internal_k_label" in codes


def test_appendix_b_registry_requires_autocorrelation_label_object(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    del data["families"][1]["paper_label"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_paper_label"]
    assert report.issues[0].family_id == "autocorrelation_bounds_k4"


def test_appendix_b_registry_requires_autocorrelation_step_evidence(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    first = data["families"][0]
    first["step_function_evidence"]["interval_count"] = 50
    first["step_function_evidence"]["domain"] = "[0, 1]"
    first["step_function_evidence"]["function_sign_policy"] = "signed_real"
    first["step_function_evidence"]["reported_bound"] = 1.6
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_step_function_interval_count" in codes
    assert "invalid_step_function_domain" in codes
    assert "invalid_step_function_function_sign_policy" in codes
    assert "invalid_step_function_reported_bound" in codes


def test_appendix_b_registry_requires_autocorrelation_step_evidence_object(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    del data["families"][2]["step_function_evidence"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_step_function_evidence"]
    assert report.issues[0].family_id == "autocorrelation_bounds_k5"


def test_appendix_b_registry_requires_autocorrelation_step_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    del data["families"][0]["step_function_payload_boundary"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_autocorrelation_step_boundary"]
    assert report.issues[0].family_id == "autocorrelation_bounds_k3"


def test_appendix_b_registry_rejects_autocorrelation_step_boundary_overclaim(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    first = data["families"][0]
    boundary = first["step_function_payload_boundary"]
    boundary["status"] = "recorded"
    boundary["interval_count"] = 50
    boundary["required_payload_fields"] = ["result_id"]
    boundary["step_function_payload_status"] = "recorded"
    boundary["verifier_artifact_status"] = "recorded"
    boundary["claim_boundary"] = "Local step-function payload is verified."
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_autocorrelation_step_boundary_status" in codes
    assert "invalid_autocorrelation_step_boundary_interval_count" in codes
    assert "invalid_autocorrelation_step_required_payload_fields" in codes
    assert "invalid_autocorrelation_step_step_function_payload_status" in codes
    assert "invalid_autocorrelation_step_verifier_artifact_status" in codes
    assert "autocorrelation_step_boundary_interval_count_mismatch" in codes
    assert "missing_autocorrelation_step_claim_boundary" in codes


def test_appendix_b_registry_requires_b4_uncertainty_boundaries(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b4 = next(family for family in data["families"] if family["id"] == "uncertainty_inequality")
    b4["source_formulation_evidence"]["known_upper_bound_after_four_digit_rounding"] = 0.354
    b4["source_formulation_evidence"]["construction_payload_status"] = "recorded"
    b4["prior_bound_rounding_evidence"]["prior_upper_bound_rounded_solution"] = 0.353
    b4["prior_bound_rounding_evidence"]["prior_source_locator_status"] = "recorded"
    b4["prior_bound_rounding_evidence"]["prior_solution_rounding_artifact_status"] = "recorded"
    b4["prior_bound_rounding_evidence"]["rounding_audit_certificate_status"] = "recorded"
    b4["hermite_result_boundary"]["reported_upper_bound"] = 0.36
    b4["hermite_result_boundary"]["coefficient_payload_status"] = "recorded"
    b4["hermite_result_boundary"]["hermite_basis_certificate_status"] = "recorded"
    b4["hermite_result_boundary"]["fourier_transform_certificate_status"] = "recorded"
    b4["hermite_result_boundary"]["origin_condition_certificate_status"] = "recorded"
    b4["hermite_result_boundary"]["eventual_nonnegative_certificate_status"] = "recorded"
    b4["hermite_result_boundary"]["root_certificate_status"] = "recorded"
    b4["hermite_result_boundary"]["recomputed_upper_bound_status"] = "recorded"
    b4["hermite_result_boundary"]["claim_boundary"] = "Local coefficients are verified."
    b4["prior_construction_similarity_evidence"]["comparison_status"] = "recorded"
    b4["prior_construction_similarity_evidence"]["prior_coefficient_payload_status"] = "recorded"
    b4["prior_construction_similarity_evidence"]["alphaevolve_coefficient_payload_status"] = "recorded"
    b4["prior_construction_similarity_evidence"]["basis_alignment_certificate_status"] = "recorded"
    b4["prior_construction_similarity_evidence"]["coefficient_similarity_metric_status"] = "recorded"
    b4["prior_construction_similarity_evidence"]["near_optimality_hypothesis_source_status"] = "recorded"
    b4["prior_construction_similarity_evidence"]["claim_boundary"] = "Local comparison is verified."
    b4["revision_result_boundary"]["revised_reported_constant"] = 0.4
    b4["revision_result_boundary"]["revision_artifact_status"] = "recorded"
    b4["revision_result_boundary"]["comparison_to_0_3284_certificate_status"] = "recorded"
    b4["revision_result_boundary"]["claim_boundary"] = "Local revision is verified."
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_b4_source_known_upper_bound_after_four_digit_rounding" in codes
    assert "invalid_b4_source_construction_payload_status" in codes
    assert "invalid_b4_source_bound_order" in codes
    assert "invalid_b4_prior_prior_upper_bound_rounded_solution" in codes
    assert "invalid_b4_prior_prior_source_locator_status" in codes
    assert "invalid_b4_prior_prior_solution_rounding_artifact_status" in codes
    assert "invalid_b4_prior_rounding_audit_certificate_status" in codes
    assert "invalid_b4_prior_rounding_order" in codes
    assert "invalid_b4_hermite_reported_upper_bound" in codes
    assert "invalid_b4_hermite_coefficient_payload_status" in codes
    assert "invalid_b4_hermite_hermite_basis_certificate_status" in codes
    assert "invalid_b4_hermite_fourier_transform_certificate_status" in codes
    assert "invalid_b4_hermite_origin_condition_certificate_status" in codes
    assert "invalid_b4_hermite_eventual_nonnegative_certificate_status" in codes
    assert "invalid_b4_hermite_root_certificate_status" in codes
    assert "invalid_b4_hermite_recomputed_upper_bound_status" in codes
    assert "missing_b4_hermite_claim_boundary" in codes
    assert "invalid_b4_hermite_improvement_direction" in codes
    assert "invalid_b4_similarity_comparison_status" in codes
    assert "invalid_b4_similarity_prior_coefficient_payload_status" in codes
    assert "invalid_b4_similarity_alphaevolve_coefficient_payload_status" in codes
    assert "invalid_b4_similarity_basis_alignment_certificate_status" in codes
    assert "invalid_b4_similarity_coefficient_similarity_metric_status" in codes
    assert "invalid_b4_similarity_near_optimality_hypothesis_source_status" in codes
    assert "missing_b4_similarity_claim_boundary" in codes
    assert "invalid_b4_revision_revised_reported_constant" in codes
    assert "invalid_b4_revision_revision_artifact_status" in codes
    assert "invalid_b4_revision_comparison_to_0_3284_certificate_status" in codes
    assert "missing_b4_revision_claim_boundary" in codes
    assert "invalid_b4_revision_improvement_direction" in codes


def test_appendix_b_registry_requires_b4_uncertainty_boundary_objects(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b4 = next(family for family in data["families"] if family["id"] == "uncertainty_inequality")
    del b4["source_formulation_evidence"]
    del b4["prior_bound_rounding_evidence"]
    del b4["hermite_result_boundary"]
    del b4["prior_construction_similarity_evidence"]
    del b4["revision_result_boundary"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == [
        "missing_b4_source_formulation",
        "missing_b4_prior_bound_rounding",
        "missing_b4_hermite_result_boundary",
        "missing_b4_similarity_evidence",
        "missing_b4_revision_result_boundary",
    ]
    assert {issue.family_id for issue in report.issues} == {"uncertainty_inequality"}


def test_appendix_b_registry_requires_b8_metric_convention_rows(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b8 = next(family for family in data["families"] if family["id"] == "max_min_distance_point_sets")
    first = b8["metric_convention_evidence"][0]
    first["reported_value_convention"] = "direct_ratio"
    first["derived_ratio"] = 12.889266112
    first["prior_best_value"] = 12.0
    b8["metric_convention_evidence"][1]["dimension"] = 4
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_b8_reported_value_convention" in codes
    assert "invalid_b8_derived_ratio" in codes
    assert "invalid_b8_derived_ratio_math" in codes
    assert "invalid_b8_improvement_direction" in codes
    assert "invalid_b8_dimension" in codes


def test_appendix_b_registry_requires_b8_metric_convention_list(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b8 = next(family for family in data["families"] if family["id"] == "max_min_distance_point_sets")
    del b8["metric_convention_evidence"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_b8_metric_convention_evidence"]
    assert report.issues[0].family_id == "max_min_distance_point_sets"


def test_appendix_b_registry_requires_b8_witness_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b8 = next(family for family in data["families"] if family["id"] == "max_min_distance_point_sets")
    del b8["witness_certificate_boundary"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_b8_witness_boundary"]
    assert report.issues[0].family_id == "max_min_distance_point_sets"


def test_appendix_b_registry_rejects_b8_witness_boundary_overclaim(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b8 = next(family for family in data["families"] if family["id"] == "max_min_distance_point_sets")
    boundary = b8["witness_certificate_boundary"]
    boundary["status"] = "recorded"
    boundary["required_witness_fields"] = ["result_id"]
    first = boundary["missing_witnesses"][0]
    first["point_count"] = 15
    first["raw_reported_squared_ratio"] = 13.0
    first["coordinate_artifact_status"] = "recorded"
    first["point_count_certificate_status"] = "recorded"
    first["coordinate_dimension_certificate_status"] = "recorded"
    first["pairwise_distance_matrix_artifact_status"] = "recorded"
    first["minimum_pair_witness_certificate_status"] = "recorded"
    first["maximum_pair_witness_certificate_status"] = "recorded"
    first["squared_ratio_recomputation_certificate_status"] = "recorded"
    first["figure_panel_artifact_status"] = "recorded"
    first["claim_boundary"] = "Coordinates exist."
    boundary["missing_witnesses"] = boundary["missing_witnesses"][:1]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_b8_witness_boundary_status" in codes
    assert "invalid_b8_witness_required_fields" in codes
    assert "invalid_b8_missing_witness_count" in codes
    assert "invalid_b8_witness_point_count" in codes
    assert "invalid_b8_witness_raw_reported_squared_ratio" in codes
    assert "invalid_b8_witness_improvement_direction" in codes
    assert "invalid_b8_coordinate_artifact_status" in codes
    assert "invalid_b8_point_count_certificate_status" in codes
    assert "invalid_b8_coordinate_dimension_certificate_status" in codes
    assert "invalid_b8_pairwise_distance_matrix_artifact_status" in codes
    assert "invalid_b8_minimum_pair_witness_certificate_status" in codes
    assert "invalid_b8_maximum_pair_witness_certificate_status" in codes
    assert "invalid_b8_squared_ratio_recomputation_certificate_status" in codes
    assert "invalid_b8_figure_panel_artifact_status" in codes
    assert "missing_b8_witness_claim_boundary" in codes
    assert "missing_b8_witness_id" in codes


def test_appendix_b_registry_requires_b5_source_formulation(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b5 = next(family for family in data["families"] if family["id"] == "erdos_minimum_overlap")
    evidence = b5["source_formulation_evidence"]
    evidence["function_pair_domain"] = "[0, 1]"
    evidence["known_lower_bound"] = 0.4
    evidence["reduced_step_function_domain"] = "[-1, 1]"
    b5["artifact_schema"]["construction"] = "finite_set_construction"
    b5["artifact_schema"]["certificate"] = "exact_overlap_verification"
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_b5_function_pair_domain" in codes
    assert "invalid_b5_known_lower_bound" in codes
    assert "invalid_b5_reduced_step_function_domain" in codes
    assert "invalid_b5_bound_order" in codes
    assert "invalid_b5_artifact_construction" in codes
    assert "invalid_b5_artifact_certificate" in codes


def test_appendix_b_registry_requires_b5_source_formulation_object(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b5 = next(family for family in data["families"] if family["id"] == "erdos_minimum_overlap")
    del b5["source_formulation_evidence"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_b5_source_formulation"]
    assert report.issues[0].family_id == "erdos_minimum_overlap"


def test_appendix_b_registry_requires_b5_step_function_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b5 = next(family for family in data["families"] if family["id"] == "erdos_minimum_overlap")
    boundary = b5["step_function_result_boundary"]
    boundary["status"] = "recorded"
    boundary["step_function_domain"] = "[-1, 1]"
    boundary["prior_upper_bound"] = 0.3809
    boundary["reported_upper_bound"] = 0.381
    boundary["required_payload_fields"] = ["result_id"]
    boundary["source_formulation_mapping_certificate_status"] = "recorded"
    boundary["equivalence_reference_artifact_status"] = "recorded"
    boundary["shift_parameter_domain_certificate_status"] = "recorded"
    boundary["step_function_payload_status"] = "recorded"
    boundary["value_range_certificate_status"] = "recorded"
    boundary["integral_normalization_certificate_status"] = "recorded"
    boundary["shift_objective_certificate_status"] = "recorded"
    boundary["recomputed_upper_bound_status"] = "recorded"
    boundary["figure_panel_artifact_status"] = "recorded"
    boundary["claim_boundary"] = "Figure 10 payload exists."
    b5["source_formulation_evidence"]["mapping_to_step_function_evidence"] = "different_result"
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_b5_step_function_status" in codes
    assert "invalid_b5_step_function_step_function_domain" in codes
    assert "invalid_b5_step_function_prior_upper_bound" in codes
    assert "invalid_b5_step_function_reported_upper_bound" in codes
    assert "invalid_b5_step_function_required_payload_fields" in codes
    assert "invalid_b5_step_function_source_formulation_mapping_certificate_status" in codes
    assert "invalid_b5_step_function_equivalence_reference_artifact_status" in codes
    assert "invalid_b5_step_function_shift_parameter_domain_certificate_status" in codes
    assert "invalid_b5_step_function_step_function_payload_status" in codes
    assert "invalid_b5_step_function_value_range_certificate_status" in codes
    assert "invalid_b5_step_function_integral_normalization_certificate_status" in codes
    assert "invalid_b5_step_function_shift_objective_certificate_status" in codes
    assert "invalid_b5_step_function_recomputed_upper_bound_status" in codes
    assert "invalid_b5_step_function_figure_panel_artifact_status" in codes
    assert "missing_b5_step_function_claim_boundary" in codes
    assert "b5_step_function_source_mapping_mismatch" in codes
    assert "invalid_b5_step_function_bound_order" in codes


def test_appendix_b_registry_requires_b5_step_function_boundary_object(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b5 = next(family for family in data["families"] if family["id"] == "erdos_minimum_overlap")
    del b5["step_function_result_boundary"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_b5_step_function_boundary"]
    assert report.issues[0].family_id == "erdos_minimum_overlap"


def test_appendix_b_registry_requires_b6_theorem_condition(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b6 = next(family for family in data["families"] if family["id"] == "sums_differences_finite_sets")
    theorem = b6["theorem_condition_evidence"]
    theorem["known_lower_bound"] = 1.4
    theorem["admissibility_condition"] = "|U - U| < 2 max(U)"
    theorem["witness_must_contain_zero"] = False
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_b6_theorem_known_lower_bound" in codes
    assert "invalid_b6_theorem_admissibility_condition" in codes
    assert "invalid_b6_theorem_witness_must_contain_zero" in codes
    assert "invalid_b6_theorem_bound_order" in codes


def test_appendix_b_registry_requires_b6_theorem_condition_object(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b6 = next(family for family in data["families"] if family["id"] == "sums_differences_finite_sets")
    del b6["theorem_condition_evidence"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert "missing_b6_theorem_condition" in [issue.code for issue in report.issues]
    assert report.issues[0].family_id == "sums_differences_finite_sets"


def test_appendix_b_registry_requires_b6_witness_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b6 = next(family for family in data["families"] if family["id"] == "sums_differences_finite_sets")
    boundary = b6["finite_set_witness_boundary"]
    boundary["status"] = "recorded"
    boundary["required_witness_fields"] = ["result_id"]
    boundary["theorem_condition_evidence"] = "wrong_theorem"
    first = boundary["missing_witnesses"][0]
    first["set_size"] = 2002
    first["reported_lower_bound"] = 1.1
    first["integer_set_artifact_status"] = "recorded"
    first["contains_zero_certificate_status"] = "recorded"
    first["non_negative_certificate_status"] = "recorded"
    first["sumset_cardinality_certificate_status"] = "recorded"
    first["difference_set_cardinality_certificate_status"] = "recorded"
    first["max_element_certificate_status"] = "recorded"
    first["lower_bound_formula_substitution_certificate_status"] = "recorded"
    first["claim_boundary"] = "Finite-set payload exists."
    boundary["missing_witnesses"] = boundary["missing_witnesses"][:1]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_b6_witness_boundary_status" in codes
    assert "invalid_b6_witness_required_fields" in codes
    assert "invalid_b6_witness_theorem_condition_evidence" in codes
    assert "b6_witness_theorem_mapping_mismatch" in codes
    assert "invalid_b6_missing_witness_count" in codes
    assert "invalid_b6_witness_set_size" in codes
    assert "invalid_b6_witness_reported_lower_bound" in codes
    assert "invalid_b6_integer_set_artifact_status" in codes
    assert "invalid_b6_contains_zero_certificate_status" in codes
    assert "invalid_b6_non_negative_certificate_status" in codes
    assert "invalid_b6_sumset_cardinality_certificate_status" in codes
    assert "invalid_b6_difference_set_cardinality_certificate_status" in codes
    assert "invalid_b6_max_element_certificate_status" in codes
    assert "invalid_b6_lower_bound_formula_substitution_certificate_status" in codes
    assert "missing_b6_witness_claim_boundary" in codes
    assert "invalid_b6_witness_bound_order" in codes
    assert "missing_b6_witness_id" in codes


def test_appendix_b_registry_requires_b6_witness_boundary_object(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b6 = next(family for family in data["families"] if family["id"] == "sums_differences_finite_sets")
    del b6["finite_set_witness_boundary"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_b6_witness_boundary"]
    assert report.issues[0].family_id == "sums_differences_finite_sets"


def test_appendix_b_registry_requires_b7_packing_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b7 = next(family for family in data["families"] if family["id"] == "regular_hexagon_packing")
    boundary = b7["packing_result_boundary"]
    boundary["status"] = "recorded"
    boundary["inner_side_length"] = 2.0
    boundary["required_witness_fields"] = ["result_id"]
    first = boundary["missing_witnesses"][0]
    first["hexagon_count"] = 10
    first["reported_outer_side_length"] = 3.95
    first["placement_artifact_status"] = "recorded"
    first["inner_hexagon_geometry_certificate_status"] = "recorded"
    first["outer_hexagon_geometry_certificate_status"] = "recorded"
    first["orientation_certificate_status"] = "recorded"
    first["side_length_recomputation_certificate_status"] = "recorded"
    first["figure_panel_artifact_status"] = "recorded"
    first["claim_boundary"] = "Placement exists."
    boundary["missing_witnesses"] = boundary["missing_witnesses"][:1]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_b7_packing_boundary_status" in codes
    assert "invalid_b7_packing_inner_side_length" in codes
    assert "invalid_b7_packing_required_fields" in codes
    assert "invalid_b7_missing_witness_count" in codes
    assert "invalid_b7_witness_hexagon_count" in codes
    assert "invalid_b7_witness_reported_outer_side_length" in codes
    assert "invalid_b7_placement_artifact_status" in codes
    assert "invalid_b7_inner_hexagon_geometry_certificate_status" in codes
    assert "invalid_b7_outer_hexagon_geometry_certificate_status" in codes
    assert "invalid_b7_orientation_certificate_status" in codes
    assert "invalid_b7_side_length_recomputation_certificate_status" in codes
    assert "invalid_b7_figure_panel_artifact_status" in codes
    assert "missing_b7_witness_claim_boundary" in codes
    assert "invalid_b7_improvement_direction" in codes
    assert "missing_b7_witness_id" in codes


def test_appendix_b_registry_requires_b7_packing_boundary_object(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    b7 = next(family for family in data["families"] if family["id"] == "regular_hexagon_packing")
    del b7["packing_result_boundary"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_b7_packing_boundary"]
    assert report.issues[0].family_id == "regular_hexagon_packing"


def test_appendix_b_registry_requires_heilbronn_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    family = next(family for family in data["families"] if family["id"] == "heilbronn_triangle")
    boundary = family["heilbronn_result_boundary"]
    boundary["status"] = "recorded"
    boundary["domain_area"] = 2.0
    boundary["required_witness_fields"] = ["result_id"]
    first = boundary["missing_witnesses"][0]
    first["point_count"] = 10
    first["reported_minimum_area"] = 0.035
    first["point_coordinate_artifact_status"] = "recorded"
    first["triple_count_enumeration_certificate_status"] = "recorded"
    first["minimum_area_witness_triangle_certificate_status"] = "recorded"
    first["reported_value_comparison_certificate_status"] = "recorded"
    first["figure_panel_artifact_status"] = "recorded"
    first["claim_boundary"] = "Coordinates exist."
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_heilbronn_boundary_status" in codes
    assert "invalid_heilbronn_domain_area" in codes
    assert "invalid_heilbronn_required_fields" in codes
    assert "invalid_heilbronn_witness_point_count" in codes
    assert "invalid_heilbronn_witness_reported_minimum_area" in codes
    assert "invalid_heilbronn_point_coordinate_artifact_status" in codes
    assert "invalid_heilbronn_triple_count_enumeration_certificate_status" in codes
    assert "invalid_heilbronn_minimum_area_witness_triangle_certificate_status" in codes
    assert "invalid_heilbronn_reported_value_comparison_certificate_status" in codes
    assert "invalid_heilbronn_figure_panel_artifact_status" in codes
    assert "missing_heilbronn_witness_claim_boundary" in codes
    assert "invalid_heilbronn_improvement_direction" in codes


def test_appendix_b_registry_requires_heilbronn_convex_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    family = next(family for family in data["families"] if family["id"] == "heilbronn_convex_region")
    boundary = family["heilbronn_result_boundary"]
    boundary["missing_witnesses"][0]["convexity_certificate_status"] = "recorded"
    boundary["missing_witnesses"] = boundary["missing_witnesses"][:1]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_heilbronn_convexity_certificate_status" in codes
    assert "invalid_heilbronn_missing_witness_count" in codes
    assert "missing_heilbronn_witness_id" in codes


def test_appendix_b_registry_requires_heilbronn_boundary_object(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    family = next(family for family in data["families"] if family["id"] == "heilbronn_triangle")
    del family["heilbronn_result_boundary"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_heilbronn_boundary"]
    assert report.issues[0].family_id == "heilbronn_triangle"


def test_appendix_b_registry_requires_b11_kissing_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    family = next(family for family in data["families"] if family["id"] == "kissing_number_d11")
    boundary = family["kissing_result_boundary"]
    boundary["status"] = "recorded"
    boundary["dimension"] = 10
    boundary["prior_lower_bound"] = 594
    boundary["required_witness_fields"] = ["result_id"]
    first = boundary["missing_witnesses"][0]
    first["vector_count"] = 592
    first["vector_artifact_status"] = "recorded"
    first["vector_count_certificate_status"] = "recorded"
    first["vector_dimension_certificate_status"] = "recorded"
    first["norm_matrix_artifact_status"] = "recorded"
    first["pairwise_distance_matrix_artifact_status"] = "recorded"
    first["max_norm_certificate_status"] = "recorded"
    first["max_norm_witness_vector_certificate_status"] = "recorded"
    first["min_pairwise_distance_certificate_status"] = "recorded"
    first["min_pairwise_distance_witness_certificate_status"] = "recorded"
    first["strict_norm_distance_inequality_certificate_status"] = "recorded"
    first["unit_sphere_normalization_certificate_status"] = "recorded"
    first["kissing_angle_certificate_status"] = "recorded"
    first["claim_boundary"] = "Vectors exist."
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_b11_kissing_boundary_status" in codes
    assert "invalid_b11_kissing_dimension" in codes
    assert "invalid_b11_kissing_prior_lower_bound" in codes
    assert "invalid_b11_kissing_required_fields" in codes
    assert "invalid_b11_kissing_improvement_direction" in codes
    assert "invalid_b11_kissing_witness_vector_count" in codes
    assert "invalid_b11_kissing_vector_artifact_status" in codes
    assert "invalid_b11_kissing_vector_count_certificate_status" in codes
    assert "invalid_b11_kissing_vector_dimension_certificate_status" in codes
    assert "invalid_b11_kissing_norm_matrix_artifact_status" in codes
    assert "invalid_b11_kissing_pairwise_distance_matrix_artifact_status" in codes
    assert "invalid_b11_kissing_max_norm_certificate_status" in codes
    assert "invalid_b11_kissing_max_norm_witness_vector_certificate_status" in codes
    assert "invalid_b11_kissing_min_pairwise_distance_certificate_status" in codes
    assert "invalid_b11_kissing_min_pairwise_distance_witness_certificate_status" in codes
    assert "invalid_b11_kissing_strict_norm_distance_inequality_certificate_status" in codes
    assert "invalid_b11_kissing_unit_sphere_normalization_certificate_status" in codes
    assert "invalid_b11_kissing_kissing_angle_certificate_status" in codes
    assert "missing_b11_kissing_claim_boundary" in codes


def test_appendix_b_registry_requires_b11_kissing_boundary_object(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    family = next(family for family in data["families"] if family["id"] == "kissing_number_d11")
    del family["kissing_result_boundary"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_b11_kissing_boundary"]
    assert report.issues[0].family_id == "kissing_number_d11"


def test_appendix_b_registry_requires_sum_of_radii_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    family = next(family for family in data["families"] if family["id"] == "circle_packing_unit_square")
    boundary = family["sum_of_radii_result_boundary"]
    boundary["status"] = "recorded"
    boundary["fixture_boundary"] = "Fixture is AlphaEvolve evidence."
    boundary["required_witness_fields"] = ["result_id"]
    first = boundary["missing_witnesses"][0]
    first["circle_count"] = 25
    first["reported_sum_of_radii"] = 2.0
    first["container_artifact_status"] = "recorded"
    first["circle_count_certificate_status"] = "recorded"
    first["circle_placement_artifact_status"] = "recorded"
    first["circle_schema_validation_certificate_status"] = "recorded"
    first["positive_radius_certificate_status"] = "recorded"
    first["sum_of_radii_formula_certificate_status"] = "recorded"
    first["figure_panel_artifact_status"] = "recorded"
    first["claim_boundary"] = "Placement exists."
    boundary["missing_witnesses"] = boundary["missing_witnesses"][:1]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_sum_of_radii_boundary_status" in codes
    assert "invalid_sum_of_radii_fixture_boundary" in codes
    assert "missing_sum_of_radii_fixture_boundary" in codes
    assert "invalid_sum_of_radii_required_fields" in codes
    assert "invalid_sum_of_radii_missing_witness_count" in codes
    assert "invalid_sum_of_radii_witness_circle_count" in codes
    assert "invalid_sum_of_radii_witness_reported_sum_of_radii" in codes
    assert "invalid_sum_of_radii_container_artifact_status" in codes
    assert "invalid_sum_of_radii_circle_count_certificate_status" in codes
    assert "invalid_sum_of_radii_circle_placement_artifact_status" in codes
    assert "invalid_sum_of_radii_circle_schema_validation_certificate_status" in codes
    assert "invalid_sum_of_radii_positive_radius_certificate_status" in codes
    assert "invalid_sum_of_radii_sum_of_radii_formula_certificate_status" in codes
    assert "invalid_sum_of_radii_figure_panel_artifact_status" in codes
    assert "missing_sum_of_radii_claim_boundary" in codes
    assert "invalid_sum_of_radii_improvement_direction" in codes
    assert "missing_sum_of_radii_witness_id" in codes


def test_appendix_b_registry_requires_rectangle_sum_of_radii_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    family = next(family for family in data["families"] if family["id"] == "circle_packing_perimeter4_rectangle")
    boundary = family["sum_of_radii_result_boundary"]
    boundary["missing_witnesses"][0]["rectangle_dimensions_status"] = "recorded"
    boundary["missing_witnesses"][0]["rectangle_perimeter_certificate_status"] = "recorded"
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_sum_of_radii_rectangle_dimensions_status" in codes
    assert "invalid_sum_of_radii_rectangle_perimeter_certificate_status" in codes
    assert report.issues[0].family_id == "circle_packing_perimeter4_rectangle"


def test_appendix_b_registry_requires_sum_of_radii_boundary_object(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    family = next(family for family in data["families"] if family["id"] == "circle_packing_unit_square")
    del family["sum_of_radii_result_boundary"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_sum_of_radii_boundary"]
    assert report.issues[0].family_id == "circle_packing_unit_square"


def test_appendix_b_registry_requires_figure5_b12_precision_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    family = next(family for family in data["families"] if family["id"] == "circle_packing_unit_square")
    boundary = family["figure5_b12_precision_boundary"]
    boundary["status"] = "reconciled"
    boundary["figure5_display_reported_sum_of_radii"] = "2.635"
    boundary["required_reconciliation_fields"] = ["figure5_source_locator"]
    boundary["source_locator_status"] = "recorded"
    boundary["figure5_panel_artifact_status"] = "recorded"
    boundary["figure5_value_extraction_certificate_status"] = "recorded"
    boundary["appendix_b12_value_extraction_certificate_status"] = "recorded"
    boundary["figure14_caption_extraction_certificate_status"] = "recorded"
    boundary["rounding_policy_status"] = "recorded"
    boundary["canonical_value_selection_status"] = "recorded"
    boundary["value_reconciliation_certificate_status"] = "recorded"
    boundary["claim_boundary"] = "The values are reconciled."
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_figure5_b12_precision_status" in codes
    assert "invalid_figure5_b12_precision_figure5_display_reported_sum_of_radii" in codes
    assert "invalid_figure5_b12_precision_required_reconciliation_fields" in codes
    assert "invalid_figure5_b12_precision_source_locator_status" in codes
    assert "invalid_figure5_b12_precision_figure5_panel_artifact_status" in codes
    assert "invalid_figure5_b12_precision_figure5_value_extraction_certificate_status" in codes
    assert "invalid_figure5_b12_precision_appendix_b12_value_extraction_certificate_status" in codes
    assert "invalid_figure5_b12_precision_figure14_caption_extraction_certificate_status" in codes
    assert "invalid_figure5_b12_precision_rounding_policy_status" in codes
    assert "invalid_figure5_b12_precision_canonical_value_selection_status" in codes
    assert "invalid_figure5_b12_precision_value_reconciliation_certificate_status" in codes
    assert "missing_figure5_b12_precision_claim_boundary" in codes
    assert report.issues[0].family_id == "circle_packing_unit_square"


def test_appendix_b_registry_requires_figure5_b12_precision_boundary_object(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    family = next(family for family in data["families"] if family["id"] == "circle_packing_unit_square")
    del family["figure5_b12_precision_boundary"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_appendix_b_registry(registry, repo_root=REGISTRY_PATH.parents[3])

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["missing_figure5_b12_precision_boundary"]
    assert report.issues[0].family_id == "circle_packing_unit_square"
