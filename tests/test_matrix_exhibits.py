import json

from libreevolve.problems.benchmarks.matrix_exhibits import (
    FIGURE9_MATRIX_DIFF_EXHIBIT_SCHEMA,
    render_figure9_matrix_diff_exhibit_summary,
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
