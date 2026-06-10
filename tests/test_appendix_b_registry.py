import json

from libreevolve.problems.benchmarks.appendix_b_registry import (
    EXPECTED_AUTOCORRELATION_LABELS,
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
