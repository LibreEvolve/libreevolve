import hashlib
import json
import math

from libreevolve.problems.benchmarks.ablation_registry import (
    EXPECTED_VARIANT_IDS_BY_TARGET_FAMILY,
)
from libreevolve.problems.benchmarks.ablation_results import (
    ABLATION_ARTIFACT_INVENTORY_SCHEMA,
    ABLATION_RESULT_SCHEMA,
    REQUIRED_BUDGET_FRACTIONS,
    ablation_result_artifact_inventory,
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
    targets = [
        {
            "target_id": "matrix_mm_2x2",
            "target_family": "matrix_tensor_decomposition",
            "description": "Small matrix target for ablation-report contract tests.",
            "target_metric": {
                "name": "normalized_rank_improvement",
                "direction": "higher_is_better",
                "normalization": "per_target_baseline_delta",
            },
        },
        {
            "target_id": "kissing_n8",
            "target_family": "kissing_number_sphere_packing",
            "description": "Small kissing-number target for ablation-report contract tests.",
            "target_metric": {
                "name": "normalized_lower_bound_improvement",
                "direction": "higher_is_better",
                "normalization": "per_target_baseline_delta",
            },
        },
    ]
    records = []
    curve_summaries = []
    for target in targets:
        target_id = target["target_id"]
        target_family = target["target_family"]
        for variant_id in EXPECTED_VARIANT_IDS_BY_TARGET_FAMILY[target_family]:
            for seed in (101, 102, 103):
                for fraction in REQUIRED_BUDGET_FRACTIONS:
                    records.append(_record(variant_id, target_id, seed, fraction))
            for fraction in REQUIRED_BUDGET_FRACTIONS:
                scores = [float(seed) + fraction for seed in (101, 102, 103)]
                mean = sum(scores) / len(scores)
                std = math.sqrt(sum((score - mean) ** 2 for score in scores) / len(scores))
                curve_summaries.append(
                    {
                        "variant_id": variant_id,
                        "target_id": target_id,
                        "budget_fraction": fraction,
                        "mean_score": mean,
                        "std_score": std,
                        "seed_count": 3,
                    }
                )
    return {
        "schema": ABLATION_RESULT_SCHEMA,
        "budget_axis": "fraction_of_equal_compute_budget",
        "targets": targets,
        "records": records,
        "curve_summaries": curve_summaries,
        "artifacts": [
            {
                "kind": "curve_summary",
                "path": "ablations/figure8/curve_summary.json",
                "sha256": "a" * 64,
                "bytes": 4096,
            }
        ],
    }


def test_ablation_result_report_validates_equal_budget_curve_contract():
    validation = validate_ablation_result_report(_valid_report())

    assert validation.ok is True
    assert validation.equal_budget_ready is True
    assert validation.target_count == 2
    assert validation.record_count == (6 + 3) * 3 * 5
    assert validation.issues == []


def test_ablation_result_report_loads_json_file(tmp_path):
    path = tmp_path / "ablation_results.json"
    path.write_text(json.dumps(_valid_report()), encoding="utf-8")

    validation = validate_ablation_result_report(path)

    assert validation.ok is True
    assert validation.equal_budget_ready is True


def test_ablation_result_artifact_inventory_verifies_declared_files(tmp_path):
    report = _valid_report()
    report["artifacts"].append(
        {
            "kind": "raw_records",
            "path": "ablations/figure8/raw_records.jsonl",
            "sha256": "b" * 64,
            "bytes": 2048,
        }
    )
    for artifact in report["artifacts"]:
        path = tmp_path / artifact["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = f"{artifact['kind']} artifact".encode("utf-8")
        path.write_bytes(raw)
        artifact["sha256"] = hashlib.sha256(raw).hexdigest()
        artifact["bytes"] = len(raw)

    inventory = ablation_result_artifact_inventory(report, tmp_path)

    assert inventory["schema"] == ABLATION_ARTIFACT_INVENTORY_SCHEMA
    assert inventory["report_schema"] == ABLATION_RESULT_SCHEMA
    assert inventory["budget_axis"] == "fraction_of_equal_compute_budget"
    assert inventory["artifact_root_policy"] == (
        "safe_relative_report_paths_under_artifact_root"
    )
    assert inventory["ok"] is True
    assert inventory["artifact_count"] == 2
    assert inventory["verified_count"] == 2
    assert inventory["missing_count"] == 0
    assert inventory["mismatch_count"] == 0
    assert inventory["invalid_count"] == 0
    assert {record["status"] for record in inventory["artifacts"]} == {
        "verified"
    }
    assert all("actual_sha256" in artifact for artifact in inventory["artifacts"])


def test_ablation_result_artifact_inventory_reports_missing_mismatch_and_unsafe_paths(tmp_path):
    report = _valid_report()
    report["artifacts"].extend(
        [
            {
                "kind": "raw_records",
                "path": "missing/raw_records.jsonl",
                "sha256": "b" * 64,
                "bytes": 2048,
            },
            {
                "kind": "plot",
                "path": "../escape-plot.png",
                "sha256": "c" * 64,
                "bytes": 1024,
            },
        ]
    )
    first = report["artifacts"][0]
    first_path = tmp_path / first["path"]
    first_path.parent.mkdir(parents=True, exist_ok=True)
    first_path.write_text("wrong", encoding="utf-8")
    first["sha256"] = "d" * 64
    first["bytes"] = 999

    inventory = ablation_result_artifact_inventory(report, tmp_path)
    records = {artifact["kind"]: artifact for artifact in inventory["artifacts"]}

    assert inventory["ok"] is False
    assert inventory["mismatch_count"] == 1
    assert inventory["missing_count"] == 1
    assert inventory["invalid_count"] == 1
    assert records["curve_summary"]["status"] == "hash_mismatch"
    assert "artifact_hash_mismatch" in records["curve_summary"]["issues"]
    assert "artifact_bytes_mismatch" in records["curve_summary"]["issues"]
    assert records["raw_records"]["status"] == "missing_file"
    assert records["plot"]["status"] == "unsafe_path"


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


def test_ablation_result_report_rejects_matrix_only_variant_for_kissing_panel():
    report = _valid_report()
    report["records"].append(
        _record("no_meta_prompt_evolution", "kissing_n8", 101, 0.0)
    )
    report["curve_summaries"].append(
        {
            "variant_id": "no_meta_prompt_evolution",
            "target_id": "kissing_n8",
            "budget_fraction": 0.0,
            "mean_score": 101.0,
            "std_score": 0.0,
            "seed_count": 3,
        }
    )

    validation = validate_ablation_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_figure8_variant_target_pair" in codes
    assert "invalid_figure8_curve_variant_target_pair" in codes


def test_ablation_result_report_requires_figure8_target_metadata():
    report = _valid_report()
    report["targets"] = [report["targets"][0]]
    report["targets"][0]["target_family"] = "hello_world"
    report["targets"][0]["target_metric"]["direction"] = "lower_is_better"
    report["targets"][0]["target_metric"]["normalization"] = ""

    validation = validate_ablation_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_target_family" in codes
    assert "missing_figure8_target_family" in codes
    assert "invalid_target_metric_direction" in codes
    assert "missing_target_metric_normalization" in codes


def test_ablation_result_report_validates_curve_summaries_against_seed_records():
    report = _valid_report()
    report["curve_summaries"] = [
        summary for summary in report["curve_summaries"]
        if not (
            summary["variant_id"] == "no_evolution"
            and summary["target_id"] == "matrix_mm_2x2"
            and summary["budget_fraction"] == 0.5
        )
    ]
    report["curve_summaries"][0]["mean_score"] += 1.0
    report["curve_summaries"][1]["std_score"] += 1.0

    validation = validate_ablation_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_curve_summary" in codes
    assert "curve_mean_mismatch" in codes
    assert "curve_std_mismatch" in codes


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
            and record["target_id"] == "matrix_mm_2x2"
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
            and record["target_id"] == "matrix_mm_2x2"
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
    assert "| target_count | 2 |" in summary
    assert "| record_count | 135 |" in summary
