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
    no_context = next(variant for variant in data["variants"] if variant["id"] == "no_context_in_prompt")
    assert no_context["paper_scope_boundary"]["alphaevolve_setup"] == "explicit_problem_specific_context_removed"
    assert no_context["paper_scope_boundary"]["paper_match_status"] == "over_broad_not_equivalent"
    no_full_file = next(variant for variant in data["variants"] if variant["id"] == "no_full_file_evolution")
    assert no_full_file["paper_scope_boundary"]["alphaevolve_setup"] == "tensor_decomposition_loss_function_only"
    assert no_full_file["paper_scope_boundary"]["paper_match_status"] == "not_equivalent"
    small_base = next(variant for variant in data["variants"] if variant["id"] == "small_base_llm_only")
    assert small_base["paper_scope_boundary"]["alphaevolve_setup"] == "single_small_base_model_generation_only"
    assert small_base["paper_scope_boundary"]["paper_match_status"] == "telemetry_unproven"


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


def test_ablation_registry_requires_no_full_file_scope_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    for variant in data["variants"]:
        if variant["id"] == "no_full_file_evolution":
            variant["paper_scope_boundary"]["paper_match_status"] = "equivalent"
            variant["paper_scope_boundary"]["required_future_evidence"] = ["executed_prompt_history"]
            break
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_ablation_registry(registry)
    issue_codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_no_full_file_scope_boundary" in issue_codes
    assert "invalid_no_full_file_future_evidence" in issue_codes


def test_ablation_registry_requires_no_context_scope_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    for variant in data["variants"]:
        if variant["id"] == "no_context_in_prompt":
            variant["paper_scope_boundary"]["paper_match_status"] = "equivalent"
            variant["paper_scope_boundary"]["required_future_evidence"] = ["prompt_section_classification"]
            break
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_ablation_registry(registry)
    issue_codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_no_context_scope_boundary" in issue_codes
    assert "invalid_no_context_future_evidence" in issue_codes


def test_ablation_registry_requires_small_base_llm_scope_boundary(tmp_path):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    for variant in data["variants"]:
        if variant["id"] == "small_base_llm_only":
            variant["paper_scope_boundary"]["paper_match_status"] = "proved"
            variant["paper_scope_boundary"]["required_future_evidence"] = ["backend_capability_metadata"]
            break
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    report = validate_ablation_registry(registry)
    issue_codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_small_base_llm_scope_boundary" in issue_codes
    assert "invalid_small_base_llm_future_evidence" in issue_codes
