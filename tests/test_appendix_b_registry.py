import json

from libreevolve.problems.benchmarks.appendix_b_registry import (
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
    EXPECTED_AUTOCORRELATION_LABELS,
    EXPECTED_AUTOCORRELATION_STEP_EVIDENCE,
    EXPECTED_FAMILY_IDS,
    EXPECTED_HEILBRONN_IDS,
    EXPECTED_HEILBRONN_ROWS,
    EXPECTED_HEILBRONN_SUMMARIES,
    REGISTRY_PATH,
    validate_appendix_b_registry,
)


def test_appendix_b_registry_enumerates_all_alphaevolve_families():
    report = validate_appendix_b_registry()
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    family_ids = [family["id"] for family in data["families"]]

    assert report.ok is True
    assert report.family_count == 13
    assert tuple(family_ids) == EXPECTED_FAMILY_IDS
    assert report.implemented_count == 1
    assert report.planned_count == 12
    assert report.unsupported_count == 0
    assert family_ids.count("circle_packing_unit_square") == 1
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
    b8 = next(family for family in data["families"] if family["id"] == "max_min_distance_point_sets")
    assert b8["metric_convention_evidence"] == list(EXPECTED_B8_METRIC_CONVENTIONS)
    boundary = b8["witness_certificate_boundary"]
    assert boundary["status"] == "not_recorded_locally"
    assert boundary["required_witness_fields"] == list(EXPECTED_B8_WITNESS_REQUIRED_FIELDS)
    assert [row["result_id"] for row in boundary["missing_witnesses"]] == list(EXPECTED_B8_WITNESS_IDS)
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
    first["coordinate_artifact_status"] = "recorded"
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
    assert "invalid_b8_coordinate_artifact_status" in codes
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
