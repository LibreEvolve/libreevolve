import json

from libreevolve.problems.benchmarks.ablation_exhibits import (
    EXPECTED_LEGEND_LABELS,
    FIGURE8_EXHIBIT_SCHEMA,
    render_figure8_exhibit_summary,
    validate_figure8_exhibit,
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
