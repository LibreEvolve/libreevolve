import json

from libreevolve.problems.benchmarks.ablation_registry import (
    EXPECTED_VARIANT_IDS,
    REGISTRY_PATH,
    validate_ablation_registry,
)


def test_ablation_registry_enumerates_alphaevolve_figure8_variants():
    report = validate_ablation_registry()
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    variant_ids = [variant["id"] for variant in data["variants"]]

    assert report.ok is True
    assert report.variant_count == 6
    assert report.baseline_count == 1
    assert report.ablation_count == 5
    assert tuple(variant_ids) == EXPECTED_VARIANT_IDS
    assert data["report_contract"]["seed_policy"]["independent_seed_count"] == 3
    assert data["report_contract"]["budget_axis"] == "fraction_of_equal_compute_budget"


def test_ablation_registry_requires_each_named_variant(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    data["variants"] = [
        variant for variant in data["variants"] if variant["id"] != "no_evolution"
    ]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_ablation_registry(registry)

    assert report.ok is False
    assert any(
        issue.code == "missing_variant" and issue.variant_id == "no_evolution"
        for issue in report.issues
    )


def test_ablation_registry_requires_ablation_disable_assertions(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    for variant in data["variants"]:
        if variant["id"] == "no_context_in_prompt":
            variant["disable_components"] = []
            variant["required_config_assertions"] = []
            break
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_ablation_registry(registry)
    issue_codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "missing_disabled_component" in issue_codes
    assert "missing_config_assertions" in issue_codes


def test_ablation_registry_requires_report_contract_fields(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    data["report_contract"]["required_result_fields"] = ["variant_id"]
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_ablation_registry(registry)

    assert report.ok is False
    assert [issue.code for issue in report.issues] == ["invalid_required_result_fields"]
