import json

from libreevolve.problems.benchmarks.ablation_registry import EXPECTED_VARIANT_IDS
from libreevolve.problems.benchmarks.ablation_results import (
    ABLATION_RESULT_SCHEMA,
    REQUIRED_BUDGET_FRACTIONS,
    render_ablation_result_summary,
    validate_ablation_result_report,
)


def _record(variant_id: str, target_id: str, seed: int, fraction: float) -> dict:
    return {
        "variant_id": variant_id,
        "target_id": target_id,
        "seed": seed,
        "budget_fraction": fraction,
        "score": float(seed) + fraction,
        "consumed_budget": {
            "unit": "evaluations",
            "consumed": fraction * 100,
            "limit": 100,
        },
        "component_assertions": [
            {"field": "variant_config", "passed": True},
        ],
    }


def _valid_report() -> dict:
    target_id = "hello_world"
    records = []
    for variant_id in EXPECTED_VARIANT_IDS:
        for seed in (101, 102, 103):
            for fraction in REQUIRED_BUDGET_FRACTIONS:
                records.append(_record(variant_id, target_id, seed, fraction))
    return {
        "schema": ABLATION_RESULT_SCHEMA,
        "budget_axis": "fraction_of_equal_compute_budget",
        "targets": [
            {"target_id": target_id, "description": "Small deterministic target for ablation-report contract tests."}
        ],
        "records": records,
        "artifacts": [
            {
                "kind": "curve_summary",
                "path": "ablations/hello_world/curve_summary.json",
                "sha256": "a" * 64,
                "bytes": 4096,
            }
        ],
    }


def test_ablation_result_report_validates_equal_budget_curve_contract():
    validation = validate_ablation_result_report(_valid_report())

    assert validation.ok is True
    assert validation.equal_budget_ready is True
    assert validation.target_count == 1
    assert validation.record_count == 6 * 3 * 5
    assert validation.issues == []


def test_ablation_result_report_loads_json_file(tmp_path):
    path = tmp_path / "ablation_results.json"
    path.write_text(json.dumps(_valid_report()), encoding="utf-8")

    validation = validate_ablation_result_report(path)

    assert validation.ok is True
    assert validation.equal_budget_ready is True


def test_ablation_result_report_requires_all_variants_seeds_and_fractions():
    report = _valid_report()
    report["records"] = [
        record for record in report["records"]
        if not (
            record["variant_id"] == "no_evolution"
            and record["seed"] == 101
            and record["budget_fraction"] == 0.5
        )
    ]

    validation = validate_ablation_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.equal_budget_ready is False
    assert "invalid_budget_fraction_coverage" in codes


def test_ablation_result_report_rejects_budget_mismatch_and_failed_assertions():
    report = _valid_report()
    report["records"][0]["consumed_budget"]["consumed"] = 13
    report["records"][0]["component_assertions"][0]["passed"] = False
    report["records"][1]["score"] = float("nan")

    validation = validate_ablation_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "budget_fraction_mismatch" in codes
    assert "component_assertion_not_passed" in codes
    assert "invalid_score" in codes


def test_ablation_result_report_requires_consistent_seed_budget_unit_and_limit():
    report = _valid_report()
    for record in report["records"]:
        if (
            record["variant_id"] == "full_system"
            and record["target_id"] == "hello_world"
            and record["seed"] == 101
            and record["budget_fraction"] == 0.25
        ):
            record["consumed_budget"] = {
                "unit": "llm_calls",
                "consumed": 25,
                "limit": 100,
            }
            break

    validation = validate_ablation_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "inconsistent_seed_budget" in codes


def test_ablation_result_report_requires_consistent_target_budget_unit_and_limit():
    report = _valid_report()
    for record in report["records"]:
        if (
            record["variant_id"] == "no_context_in_prompt"
            and record["target_id"] == "hello_world"
            and record["seed"] == 101
        ):
            record["consumed_budget"] = {
                "unit": "evaluations",
                "consumed": record["budget_fraction"] * 200,
                "limit": 200,
            }

    validation = validate_ablation_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "inconsistent_target_budget" in codes


def test_ablation_result_report_rejects_unsafe_artifacts():
    report = _valid_report()
    report["artifacts"][0].update({"path": "C:/secret.json", "sha256": "bad", "bytes": 0})

    validation = validate_ablation_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_artifact_path" in codes
    assert "invalid_artifact_hash" in codes
    assert "invalid_artifact_bytes" in codes


def test_ablation_result_summary_renders_equal_budget_readiness():
    summary = render_ablation_result_summary(_valid_report())

    assert "AlphaEvolve ablation result report" in summary
    assert "| schema_status | ok |" in summary
    assert "| equal_budget_ready | yes |" in summary
    assert "| target_count | 1 |" in summary
    assert "| record_count | 90 |" in summary
