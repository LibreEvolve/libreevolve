import json

from libreevolve.problems.benchmarks.matrix_exhibits import (
    FIGURE4_MATRIX_DISCOVERY_EXHIBIT_SCHEMA,
    FIGURE9_MATRIX_DIFF_EXHIBIT_SCHEMA,
    render_figure4_matrix_discovery_exhibit_summary,
    render_figure9_matrix_diff_exhibit_summary,
    validate_figure4_matrix_discovery_exhibit,
    validate_figure9_matrix_diff_exhibit,
)


def _artifact(path: str, sha: str = "a") -> dict:
    return {
        "path": path,
        "sha256": sha * 64,
        "bytes": 4096,
    }


def _panel(
    panel_id: str,
    order: int,
    page: int,
    line_start: int,
    line_end: int,
    components: list[str],
    sweep_fields: list[str] | None = None,
) -> dict:
    panel = {
        "panel_id": panel_id,
        "panel_order": order,
        "source_pdf_page": page,
        "caption_ref": "Magnified version of Figure 4(left), giving the program that discovers a faster algorithm.",
        "code_line_span": {
            "start": line_start,
            "end": line_end,
        },
        "source_diff_excerpt": _artifact(f"figures/{panel_id}_diff.txt", "b"),
        "rendered_image_artifact": _artifact(f"figures/{panel_id}.png", "c"),
        "rendered_text_artifact": _artifact(f"figures/{panel_id}_ocr.txt", "d"),
        "semantic_components": components,
    }
    if sweep_fields is not None:
        panel["sweep_fields"] = sweep_fields
    return panel


def _valid_exhibit() -> dict:
    return {
        "schema": FIGURE9_MATRIX_DIFF_EXHIBIT_SCHEMA,
        "exhibit_id": "figure9_matrix_diff_magnified",
        "source_paper_id": "2506.13131",
        "source_figure": "Figures 9a-9c",
        "source_caption_ref": "Magnified version of Figure 4 (left), split across Figures 9a to 9c.",
        "target_mapping": {
            "target_suite": "alphaevolve_appendix_a",
            "target_id": "mm_4x4x4",
            "dimensions": [4, 4, 4],
            "result_rank": 48,
            "matrix_result_ref": "reports/mm_4x4x4_result.json",
            "sweep_space_ref": "reports/mm_4x4x4_sweep_space.json",
            "exactness_certificate_ref": "certificates/mm_4x4x4.json",
            "companion_notebook_ref": "notebooks/mm_4x4x4.ipynb",
        },
        "source_links": {
            "source_pdf_excerpt": _artifact("figures/figure9_pdf_excerpt.txt", "e"),
            "rendered_panel_set": _artifact("figures/figure9_panels.png", "f"),
            "ocr_text": _artifact("figures/figure9_ocr.txt", "1"),
        },
        "panels": [
            _panel(
                "figure9a",
                1,
                35,
                1,
                65,
                ["optimizer", "initialization", "noise", "clipping"],
            ),
            _panel(
                "figure9b",
                2,
                36,
                66,
                130,
                ["loss", "discretization", "noise"],
            ),
            _panel(
                "figure9c",
                3,
                37,
                131,
                193,
                ["sweep", "loss", "clipping"],
                ["lr", "weight_decay", "clip_min", "clip_max", "grad_noise_std"],
            ),
        ],
    }


def _figure4_region(region_id: str, label: str, components: list[str]) -> dict:
    return {
        "region_id": region_id,
        "caption_label": label,
        "source_diff_excerpt": _artifact(f"figures/figure4_{region_id}_diff.txt", "2"),
        "rendered_region_artifact": _artifact(f"figures/figure4_{region_id}.png", "3"),
        "semantic_components": components,
    }


def _valid_figure4_exhibit() -> dict:
    return {
        "schema": FIGURE4_MATRIX_DISCOVERY_EXHIBIT_SCHEMA,
        "exhibit_id": "figure4_matrix_discovery",
        "source_paper_id": "2506.13131",
        "source_figure": "Figure 4",
        "source_pdf_page": 11,
        "source_caption_ref": "Changes proposed by AlphaEvolve to discover faster matrix multiplication algorithms.",
        "mutation_count": 15,
        "target_mapping": {
            "target_suite": "alphaevolve_appendix_a",
            "target_id": "mm_4x4x4",
            "dimensions": [4, 4, 4],
            "result_rank": 48,
            "matrix_result_ref": "reports/mm_4x4x4_result.json",
            "figure9_exhibit_ref": "reports/figure9_matrix_diff_exhibit.json",
            "sweep_space_ref": "reports/mm_4x4x4_sweep_space.json",
            "exactness_certificate_ref": "certificates/mm_4x4x4.json",
            "companion_notebook_ref": "notebooks/mm_4x4x4.ipynb",
        },
        "source_links": {
            "rendered_figure": _artifact("figures/figure4_matrix_discovery.png", "4"),
            "left_diff_outline": _artifact("figures/figure4_left_diff.txt", "5"),
            "highlighted_excerpts": _artifact("figures/figure4_highlights.json", "6"),
            "paper_text_excerpt": _artifact("figures/figure4_caption.txt", "7"),
        },
        "highlight_regions": [
            _figure4_region(
                "left_full_diff_outline",
                "Full diff outlined on the left",
                ["optimizer", "initialization", "noise", "clipping", "loss", "discretization", "sweep"],
            ),
            _figure4_region(
                "top_right_optimizer_initialization",
                "Optimizer and weight initialization",
                ["optimizer", "initialization"],
            ),
            _figure4_region(
                "middle_right_loss_function",
                "Loss function",
                ["loss", "discretization"],
            ),
            _figure4_region(
                "bottom_right_hyperparameter_sweep",
                "Hyperparameter sweep",
                ["sweep"],
            ),
        ],
    }


def test_validate_figure4_matrix_discovery_exhibit_accepts_main_text_metadata():
    validation = validate_figure4_matrix_discovery_exhibit(_valid_figure4_exhibit())

    assert validation.ok is True
    assert validation.region_count == 4
    assert validation.semantic_component_count == 7
    assert validation.issues == []


def test_validate_figure4_matrix_discovery_exhibit_loads_json_file(tmp_path):
    path = tmp_path / "figure4_exhibit.json"
    path.write_text(json.dumps(_valid_figure4_exhibit()), encoding="utf-8")

    validation = validate_figure4_matrix_discovery_exhibit(path)

    assert validation.ok is True


def test_validate_figure4_matrix_discovery_exhibit_rejects_target_and_caption_drift():
    exhibit = _valid_figure4_exhibit()
    exhibit["source_pdf_page"] = 10
    exhibit["source_caption_ref"] = "Other figure"
    exhibit["mutation_count"] = 14
    exhibit["target_mapping"]["target_id"] = "mm_2x2x2"
    exhibit["target_mapping"]["result_rank"] = 49

    validation = validate_figure4_matrix_discovery_exhibit(exhibit)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_source_pdf_page" in codes
    assert "invalid_source_caption_ref" in codes
    assert "invalid_mutation_count" in codes
    assert "invalid_target_id" in codes
    assert "invalid_result_rank" in codes


def test_validate_figure4_matrix_discovery_exhibit_rejects_missing_region_and_bad_artifact():
    exhibit = _valid_figure4_exhibit()
    exhibit["highlight_regions"] = exhibit["highlight_regions"][:3]
    exhibit["source_links"]["rendered_figure"] = _artifact("../escape.png", "nothex")
    exhibit["source_links"]["rendered_figure"]["bytes"] = 0

    validation = validate_figure4_matrix_discovery_exhibit(exhibit)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_highlight_region" in codes
    assert "invalid_rendered_figure_path" in codes
    assert "invalid_rendered_figure_hash" in codes
    assert "invalid_rendered_figure_bytes" in codes


def test_render_figure4_matrix_discovery_exhibit_summary_reports_shape():
    summary = render_figure4_matrix_discovery_exhibit_summary(_valid_figure4_exhibit())

    assert "AlphaEvolve Figure 4 matrix-discovery exhibit" in summary
    assert "| schema_status | ok |" in summary
    assert "| region_count | 4 |" in summary
    assert "| semantic_component_count | 7 |" in summary


def test_validate_figure9_matrix_diff_exhibit_accepts_panel_metadata():
    validation = validate_figure9_matrix_diff_exhibit(_valid_exhibit())

    assert validation.ok is True
    assert validation.panel_count == 3
    assert validation.semantic_component_count == 7
    assert validation.issues == []


def test_validate_figure9_matrix_diff_exhibit_loads_json_file(tmp_path):
    path = tmp_path / "figure9_exhibit.json"
    path.write_text(json.dumps(_valid_exhibit()), encoding="utf-8")

    validation = validate_figure9_matrix_diff_exhibit(path)

    assert validation.ok is True


def test_validate_figure9_matrix_diff_exhibit_rejects_missing_panel_and_bad_order():
    exhibit = _valid_exhibit()
    exhibit["panels"] = exhibit["panels"][:2]
    exhibit["panels"][0]["panel_order"] = 2
    exhibit["panels"][1]["source_pdf_page"] = 35

    validation = validate_figure9_matrix_diff_exhibit(exhibit)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_panel" in codes
    assert "invalid_panel_order" in codes
    assert "invalid_panel_page" in codes
    assert "incomplete_panel_continuity" in codes


def test_validate_figure9_matrix_diff_exhibit_rejects_artifact_and_span_drift():
    exhibit = _valid_exhibit()
    exhibit["target_mapping"]["target_id"] = "mm_2x2x2"
    exhibit["source_links"]["rendered_panel_set"] = _artifact("../escape.png", "nothex")
    exhibit["source_links"]["rendered_panel_set"]["bytes"] = 0
    exhibit["panels"][0]["code_line_span"]["end"] = 0

    validation = validate_figure9_matrix_diff_exhibit(exhibit)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_target_id" in codes
    assert "invalid_rendered_panel_set_path" in codes
    assert "invalid_rendered_panel_set_hash" in codes
    assert "invalid_rendered_panel_set_bytes" in codes
    assert "invalid_line_span" in codes


def test_validate_figure9_matrix_diff_exhibit_rejects_missing_semantic_coverage():
    exhibit = _valid_exhibit()
    exhibit["panels"][1]["semantic_components"] = ["loss", "noise"]
    exhibit["panels"][2]["semantic_components"] = ["sweep"]
    exhibit["panels"][2]["sweep_fields"] = []

    validation = validate_figure9_matrix_diff_exhibit(exhibit)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_semantic_component" in codes
    assert "invalid_sweep_fields" in codes


def test_render_figure9_matrix_diff_exhibit_summary_reports_shape():
    summary = render_figure9_matrix_diff_exhibit_summary(_valid_exhibit())

    assert "AlphaEvolve Figure 9 matrix-diff exhibit" in summary
    assert "| schema_status | ok |" in summary
    assert "| panel_count | 3 |" in summary
    assert "| semantic_component_count | 7 |" in summary
