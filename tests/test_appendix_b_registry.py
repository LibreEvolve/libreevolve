import json

from libreevolve.problems.benchmarks.appendix_b_registry import (
    EXPECTED_B8_METRIC_CONVENTIONS,
    EXPECTED_B8_WITNESS_IDS,
    EXPECTED_B8_WITNESS_REQUIRED_FIELDS,
    EXPECTED_AUTOCORRELATION_LABELS,
    EXPECTED_AUTOCORRELATION_STEP_EVIDENCE,
    EXPECTED_FAMILY_IDS,
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
