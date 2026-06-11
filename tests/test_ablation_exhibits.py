import json
import math

from libreevolve.problems.benchmarks.ablation_registry import EXPECTED_VARIANT_IDS
from libreevolve.problems.benchmarks.ablation_exhibits import (
    EXPECTED_LEGEND_LABELS,
    FIGURE8_ARTIFACT_BOUNDARY_SCHEMA,
    FIGURE8_EXHIBIT_SCHEMA,
    figure8_artifact_boundary_record,
    figure8_exhibit_from_ablation_report,
    render_figure8_artifact_boundary_summary,
    render_figure8_exhibit_summary,
    validate_figure8_artifact_boundary,
    validate_figure8_exhibit,
)
from libreevolve.problems.benchmarks.ablation_results import (
    ABLATION_RESULT_SCHEMA,
    REQUIRED_BUDGET_FRACTIONS,
)


def _artifact(path: str, sha: str = "a") -> dict:
    return {
        "path": path,
        "sha256": sha * 64,
        "bytes": 4096,
    }


def _series() -> list[dict]:
    return [
        {
            "variant_id": variant_id,
            "legend_label": legend_label,
            "curve_summary_ref": f"curve_summaries/{variant_id}.json",
            "raw_seed_trace_ref": f"raw/{variant_id}.jsonl",
            "style": {
                "color": f"c{index}",
                "std_band": True,
            },
        }
        for index, (variant_id, legend_label) in enumerate(EXPECTED_LEGEND_LABELS.items())
    ]


def _panel(panel_id: str, target_family: str) -> dict:
    return {
        "panel_id": panel_id,
        "target_family": target_family,
        "x_axis": {
            "label": "Fraction of compute budget",
            "scale": "linear",
            "unit": "fraction",
        },
        "y_axis": {
            "label": "Aggregated target metric",
            "direction": "higher_is_better",
            "normalization": "per_target_family_mean",
        },
        "series": _series(),
    }


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
            "description": "Small matrix target for Figure 8 exhibit tests.",
            "target_metric": {
                "name": "normalized_rank_improvement",
                "direction": "higher_is_better",
                "normalization": "per_target_baseline_delta",
            },
        },
        {
            "target_id": "kissing_n8",
            "target_family": "kissing_number_sphere_packing",
            "description": "Small kissing-number target for Figure 8 exhibit tests.",
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
        for variant_id in EXPECTED_VARIANT_IDS:
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
                **_artifact("ablations/figure8/curve_summary.json"),
            },
            {
                "kind": "raw_records",
                **_artifact("ablations/figure8/raw_records.jsonl", "b"),
            },
        ],
    }


def _valid_exhibit() -> dict:
    return {
        "schema": FIGURE8_EXHIBIT_SCHEMA,
        "exhibit_id": "figure8_ablation_curves",
        "source_paper_id": "2506.13131",
        "source_figure": "Figure 8",
        "source_caption_ref": "AlphaEvolve Figure 8 caption",
        "rendered_artifact": _artifact("figures/figure8_ablation_curves.png"),
        "source_links": {
            "ablation_report": _artifact("reports/figure8_ablation_report.json", "b"),
            "curve_summary": _artifact("reports/figure8_curve_summary.json", "c"),
            "raw_seed_traces": _artifact("reports/figure8_raw_seed_traces.jsonl", "d"),
        },
        "panels": [
            _panel("matrix_tensor_decomposition", "matrix_tensor_decomposition"),
            _panel("kissing_number_sphere_packing", "kissing_number_sphere_packing"),
        ],
    }


def test_validate_figure8_exhibit_accepts_paper_visual_metadata():
    validation = validate_figure8_exhibit(_valid_exhibit())

    assert validation.ok is True
    assert validation.panel_count == 2
    assert validation.series_count == 12
    assert validation.issues == []


def test_validate_figure8_artifact_boundary_accepts_absence_record():
    boundary = figure8_artifact_boundary_record()
    validation = validate_figure8_artifact_boundary(boundary)

    assert validation.ok is True
    assert validation.artifact_status == "not_emitted_by_local_report_export"
    assert validation.emitted_artifact_count == 0
    assert validation.required_field_count == 12
    assert boundary["schema"] == FIGURE8_ARTIFACT_BOUNDARY_SCHEMA
    assert "does not claim local report/export code emits" in boundary["claim_boundary"]


def test_validate_figure8_artifact_boundary_rejects_premature_emitted_claim():
    boundary = figure8_artifact_boundary_record()
    boundary["artifact_status"] = "emitted"
    boundary["required_artifact_fields"] = ["exhibit_id"]
    boundary["claim_boundary"] = "Figure 8 artifacts are emitted."

    validation = validate_figure8_artifact_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_figure8_artifacts" in codes
    assert "missing_required_artifact_field" in codes


def test_figure8_exhibit_builder_links_valid_ablation_report_artifacts():
    exhibit = figure8_exhibit_from_ablation_report(
        _valid_report(),
        rendered_artifact=_artifact("figures/figure8_ablation_curves.png", "c"),
        ablation_report_artifact=_artifact("reports/figure8_ablation_report.json", "d"),
        source_caption_ref="AlphaEvolve Figure 8 caption, page 15",
        rendering_parameters={"renderer": "matplotlib", "std_band": "filled"},
        run_links=[{"run_id": "figure8-fixture"}],
    )

    validation = validate_figure8_exhibit(exhibit)

    assert validation.ok is True
    assert exhibit["source_links"]["curve_summary"]["path"] == "ablations/figure8/curve_summary.json"
    assert exhibit["source_links"]["raw_seed_traces"]["path"] == "ablations/figure8/raw_records.jsonl"
    assert exhibit["source_links"]["ablation_report"]["path"] == "reports/figure8_ablation_report.json"
    assert exhibit["panels"][0]["target_ids"] == ["matrix_mm_2x2"]
    assert exhibit["panels"][1]["target_ids"] == ["kissing_n8"]
    assert exhibit["panels"][0]["series"][0]["curve_summary_ref"] == "curve_summary:matrix_tensor_decomposition:full_system"
    assert exhibit["rendering_parameters"]["renderer"] == "matplotlib"
    assert exhibit["run_links"] == [{"run_id": "figure8-fixture"}]


def test_figure8_exhibit_builder_rejects_invalid_report():
    report = _valid_report()
    report["records"] = []

    try:
        figure8_exhibit_from_ablation_report(
            report,
            rendered_artifact=_artifact("figures/figure8_ablation_curves.png", "c"),
            ablation_report_artifact=_artifact("reports/figure8_ablation_report.json", "d"),
        )
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("builder should reject invalid ablation reports")

    assert "ablation report is invalid" in message


def test_figure8_exhibit_builder_requires_raw_trace_artifact():
    report = _valid_report()
    report["artifacts"] = [artifact for artifact in report["artifacts"] if artifact.get("kind") != "raw_records"]

    try:
        figure8_exhibit_from_ablation_report(
            report,
            rendered_artifact=_artifact("figures/figure8_ablation_curves.png", "c"),
            ablation_report_artifact=_artifact("reports/figure8_ablation_report.json", "d"),
        )
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("builder should require raw_records artifacts")

    assert "raw_records artifact" in message


def test_validate_figure8_exhibit_loads_json_file(tmp_path):
    path = tmp_path / "figure8_exhibit.json"
    path.write_text(json.dumps(_valid_exhibit()), encoding="utf-8")

    validation = validate_figure8_exhibit(path)

    assert validation.ok is True


def test_validate_figure8_exhibit_rejects_missing_panel_and_wrong_legend():
    exhibit = _valid_exhibit()
    exhibit["panels"] = exhibit["panels"][:1]
    exhibit["panels"][0]["series"][0]["legend_label"] = "Full"
    exhibit["panels"][0]["series"][1]["style"]["std_band"] = False

    validation = validate_figure8_exhibit(exhibit)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_panel" in codes
    assert "invalid_legend_label" in codes
    assert "missing_std_band" in codes


def test_validate_figure8_exhibit_rejects_unsafe_artifact_and_axis_metadata():
    exhibit = _valid_exhibit()
    exhibit["rendered_artifact"] = _artifact("../escape.png", "nothex")
    exhibit["rendered_artifact"]["bytes"] = 0
    exhibit["panels"][0]["x_axis"]["label"] = "Generation"
    exhibit["panels"][0]["y_axis"]["direction"] = "lower_is_better"

    validation = validate_figure8_exhibit(exhibit)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_rendered_artifact_path" in codes
    assert "invalid_rendered_artifact_hash" in codes
    assert "invalid_rendered_artifact_bytes" in codes
    assert "invalid_x_axis_label" in codes
    assert "invalid_y_axis_direction" in codes


def test_render_figure8_exhibit_summary_reports_shape():
    summary = render_figure8_exhibit_summary(_valid_exhibit())

    assert "AlphaEvolve Figure 8 exhibit" in summary
    assert "| schema_status | ok |" in summary
    assert "| panel_count | 2 |" in summary
    assert "| series_count | 12 |" in summary


def test_render_figure8_artifact_boundary_summary_reports_absence_shape():
    summary = render_figure8_artifact_boundary_summary(figure8_artifact_boundary_record())

    assert "AlphaEvolve Figure 8 artifact boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| artifact_status | not_emitted_by_local_report_export |" in summary
    assert "| emitted_artifact_count | 0 |" in summary
