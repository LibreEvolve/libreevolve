from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.appendix_a_matrix_registry import (
    TARGET_SUITE as APPENDIX_A_TARGET_SUITE,
)


FIGURE4_MATRIX_DISCOVERY_EXHIBIT_SCHEMA = "libreevolve.alphaevolve_figure4_matrix_discovery_exhibit.v1"
FIGURE9_MATRIX_DIFF_EXHIBIT_SCHEMA = "libreevolve.alphaevolve_figure9_matrix_diff_exhibit.v1"
EXPECTED_FIGURE4_EXHIBIT_ID = "figure4_matrix_discovery"
EXPECTED_FIGURE9_EXHIBIT_ID = "figure9_matrix_diff_magnified"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_FIGURE4_SOURCE_FIGURE = "Figure 4"
EXPECTED_SOURCE_FIGURE = "Figures 9a-9c"
EXPECTED_TARGET_ID = "mm_4x4x4"
EXPECTED_TARGET_DIMENSIONS = [4, 4, 4]
EXPECTED_RESULT_RANK = 48
EXPECTED_FIGURE4_PAGE = 11
EXPECTED_FIGURE4_MUTATION_COUNT = 15
EXPECTED_FIGURE4_REGION_IDS = frozenset(
    {
        "left_full_diff_outline",
        "top_right_optimizer_initialization",
        "middle_right_loss_function",
        "bottom_right_hyperparameter_sweep",
    }
)
EXPECTED_FIGURE4_HIGHLIGHT_COMPONENTS = frozenset(
    {
        "optimizer",
        "initialization",
        "loss",
        "sweep",
    }
)
EXPECTED_PANEL_ORDER = {
    "figure9a": 1,
    "figure9b": 2,
    "figure9c": 3,
}
EXPECTED_PANEL_PAGES = {
    "figure9a": 35,
    "figure9b": 36,
    "figure9c": 37,
}
EXPECTED_SEMANTIC_COMPONENTS = frozenset(
    {
        "optimizer",
        "initialization",
        "noise",
        "clipping",
        "loss",
        "discretization",
        "sweep",
    }
)
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class Figure9MatrixDiffExhibitIssue:
    code: str
    message: str


@dataclass(frozen=True)
class Figure9MatrixDiffExhibitValidation:
    ok: bool
    panel_count: int
    semantic_component_count: int
    issues: list[Figure9MatrixDiffExhibitIssue]


@dataclass(frozen=True)
class Figure4MatrixDiscoveryExhibitIssue:
    code: str
    message: str


@dataclass(frozen=True)
class Figure4MatrixDiscoveryExhibitValidation:
    ok: bool
    region_count: int
    semantic_component_count: int
    issues: list[Figure4MatrixDiscoveryExhibitIssue]


def validate_figure4_matrix_discovery_exhibit(
    exhibit: object | str | Path,
) -> Figure4MatrixDiscoveryExhibitValidation:
    data, read_issues = _load_figure4_exhibit(exhibit)
    if read_issues:
        return Figure4MatrixDiscoveryExhibitValidation(False, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[Figure4MatrixDiscoveryExhibitIssue] = []
    if data.get("schema") != FIGURE4_MATRIX_DISCOVERY_EXHIBIT_SCHEMA:
        issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_schema", "unsupported Figure 4 matrix-discovery exhibit schema"))
    if data.get("exhibit_id") != EXPECTED_FIGURE4_EXHIBIT_ID:
        issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_exhibit_id", "exhibit_id must identify the Figure 4 matrix discovery exhibit"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_figure") != EXPECTED_FIGURE4_SOURCE_FIGURE:
        issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_source_figure", "source_figure must be Figure 4"))
    if data.get("source_pdf_page") != EXPECTED_FIGURE4_PAGE:
        issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_source_pdf_page", "source_pdf_page must be 11"))
    caption = data.get("source_caption_ref")
    if not isinstance(caption, str) or "Changes proposed by" not in caption or "matrix multiplication" not in caption:
        issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_source_caption_ref", "source_caption_ref must cite the Figure 4 matrix multiplication caption"))
    if data.get("mutation_count") != EXPECTED_FIGURE4_MUTATION_COUNT:
        issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_mutation_count", "Figure 4 caption requires 15 mutations"))
    _validate_figure4_target_mapping(data.get("target_mapping"), issues)
    _validate_figure4_source_links(data.get("source_links"), issues)
    region_count, semantic_components = _validate_figure4_regions(data.get("highlight_regions"), issues)
    missing_components = sorted(EXPECTED_FIGURE4_HIGHLIGHT_COMPONENTS - semantic_components)
    if missing_components:
        issues.append(
            Figure4MatrixDiscoveryExhibitIssue(
                "missing_semantic_component",
                "Figure 4 highlighted regions must cover optimizer, initialization, loss, and sweep changes",
            )
        )
    return Figure4MatrixDiscoveryExhibitValidation(
        ok=not issues,
        region_count=region_count,
        semantic_component_count=len(semantic_components),
        issues=issues,
    )


def validate_figure9_matrix_diff_exhibit(
    exhibit: object | str | Path,
) -> Figure9MatrixDiffExhibitValidation:
    data, read_issues = _load_exhibit(exhibit)
    if read_issues:
        return Figure9MatrixDiffExhibitValidation(False, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[Figure9MatrixDiffExhibitIssue] = []
    if data.get("schema") != FIGURE9_MATRIX_DIFF_EXHIBIT_SCHEMA:
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_schema", "unsupported Figure 9 matrix-diff exhibit schema"))
    if data.get("exhibit_id") != EXPECTED_FIGURE9_EXHIBIT_ID:
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_exhibit_id", "exhibit_id must identify the Figure 9 magnified matrix diff"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_figure") != EXPECTED_SOURCE_FIGURE:
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_source_figure", "source_figure must identify Figures 9a-9c"))
    if not isinstance(data.get("source_caption_ref"), str) or "Magnified version of Figure 4" not in data["source_caption_ref"]:
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_source_caption_ref", "source_caption_ref must cite the Figure 9 magnified Figure 4 caption"))
    _validate_target_mapping(data.get("target_mapping"), issues)
    _validate_source_links(data.get("source_links"), issues)
    panel_count, semantic_components = _validate_panels(data.get("panels"), issues)
    missing_components = sorted(EXPECTED_SEMANTIC_COMPONENTS - semantic_components)
    if missing_components:
        issues.append(
            Figure9MatrixDiffExhibitIssue(
                "missing_semantic_component",
                "Figure 9 panels must cover optimizer, initialization, noise, clipping, loss, discretization, and sweep changes",
            )
        )
    return Figure9MatrixDiffExhibitValidation(
        ok=not issues,
        panel_count=panel_count,
        semantic_component_count=len(semantic_components),
        issues=issues,
    )


def render_figure4_matrix_discovery_exhibit_summary(exhibit: dict[str, Any]) -> str:
    validation = validate_figure4_matrix_discovery_exhibit(exhibit)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve Figure 4 matrix-discovery exhibit",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| region_count | {validation.region_count} |",
        f"| semantic_component_count | {validation.semantic_component_count} |",
        f"| source_figure | {exhibit.get('source_figure', '<unknown>')} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_figure9_matrix_diff_exhibit_summary(exhibit: dict[str, Any]) -> str:
    validation = validate_figure9_matrix_diff_exhibit(exhibit)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve Figure 9 matrix-diff exhibit",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| panel_count | {validation.panel_count} |",
        f"| semantic_component_count | {validation.semantic_component_count} |",
        f"| source_figure | {exhibit.get('source_figure', '<unknown>')} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_figure4_exhibit(
    exhibit: object | str | Path,
) -> tuple[dict[str, Any] | None, list[Figure4MatrixDiscoveryExhibitIssue]]:
    if isinstance(exhibit, dict):
        return dict(exhibit), []
    if isinstance(exhibit, (str, Path)):
        path = Path(exhibit)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [Figure4MatrixDiscoveryExhibitIssue("read_error", f"failed to read Figure 4 exhibit: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [Figure4MatrixDiscoveryExhibitIssue("invalid_json", f"invalid Figure 4 exhibit JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [Figure4MatrixDiscoveryExhibitIssue("invalid_shape", "Figure 4 exhibit must be a JSON object")]


def _load_exhibit(
    exhibit: object | str | Path,
) -> tuple[dict[str, Any] | None, list[Figure9MatrixDiffExhibitIssue]]:
    if isinstance(exhibit, dict):
        return dict(exhibit), []
    if isinstance(exhibit, (str, Path)):
        path = Path(exhibit)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [Figure9MatrixDiffExhibitIssue("read_error", f"failed to read Figure 9 exhibit: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [Figure9MatrixDiffExhibitIssue("invalid_json", f"invalid Figure 9 exhibit JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [Figure9MatrixDiffExhibitIssue("invalid_shape", "Figure 9 exhibit must be a JSON object")]


def _validate_figure4_target_mapping(value: object, issues: list[Figure4MatrixDiscoveryExhibitIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_target_mapping", "target_mapping must be an object"))
        return
    if value.get("target_suite") != APPENDIX_A_TARGET_SUITE:
        issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_target_suite", "target_suite must be alphaevolve_appendix_a"))
    if value.get("target_id") != EXPECTED_TARGET_ID:
        issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_target_id", "target_id must be mm_4x4x4"))
    if value.get("dimensions") != EXPECTED_TARGET_DIMENSIONS:
        issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_target_dimensions", "dimensions must be [4, 4, 4]"))
    if value.get("result_rank") != EXPECTED_RESULT_RANK:
        issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_result_rank", "result_rank must be 48"))
    for field in (
        "matrix_result_ref",
        "figure9_exhibit_ref",
        "sweep_space_ref",
        "exactness_certificate_ref",
        "companion_notebook_ref",
    ):
        if not isinstance(value.get(field), str) or not value[field].strip():
            issues.append(Figure4MatrixDiscoveryExhibitIssue(f"missing_{field}", f"target_mapping.{field} is required"))


def _validate_target_mapping(value: object, issues: list[Figure9MatrixDiffExhibitIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_target_mapping", "target_mapping must be an object"))
        return
    if value.get("target_suite") != APPENDIX_A_TARGET_SUITE:
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_target_suite", "target_suite must be alphaevolve_appendix_a"))
    if value.get("target_id") != EXPECTED_TARGET_ID:
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_target_id", "target_id must be mm_4x4x4"))
    if value.get("dimensions") != EXPECTED_TARGET_DIMENSIONS:
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_target_dimensions", "dimensions must be [4, 4, 4]"))
    if value.get("result_rank") != EXPECTED_RESULT_RANK:
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_result_rank", "result_rank must be 48"))
    for field in ("matrix_result_ref", "sweep_space_ref", "exactness_certificate_ref", "companion_notebook_ref"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            issues.append(Figure9MatrixDiffExhibitIssue(f"missing_{field}", f"target_mapping.{field} is required"))


def _validate_figure4_source_links(value: object, issues: list[Figure4MatrixDiscoveryExhibitIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_source_links", "source_links must be an object"))
        return
    for key in ("rendered_figure", "left_diff_outline", "highlighted_excerpts", "paper_text_excerpt"):
        _validate_figure4_artifact(value.get(key), key, issues)


def _validate_source_links(value: object, issues: list[Figure9MatrixDiffExhibitIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_source_links", "source_links must be an object"))
        return
    for key in ("source_pdf_excerpt", "rendered_panel_set", "ocr_text"):
        _validate_artifact(value.get(key), key, issues)


def _validate_figure4_regions(
    value: object,
    issues: list[Figure4MatrixDiscoveryExhibitIssue],
) -> tuple[int, set[str]]:
    if not isinstance(value, list):
        issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_highlight_regions", "highlight_regions must be a list"))
        return 0, set()
    seen_regions: set[str] = set()
    semantic_components: set[str] = set()
    for region in value:
        if not isinstance(region, dict):
            issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_highlight_region", "highlight region must be an object"))
            continue
        region_id = region.get("region_id")
        if region_id not in EXPECTED_FIGURE4_REGION_IDS:
            issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_region_id", "region_id must match a Figure 4 highlighted region"))
        elif isinstance(region_id, str):
            seen_regions.add(region_id)
        if not isinstance(region.get("caption_label"), str) or not region["caption_label"].strip():
            issues.append(Figure4MatrixDiscoveryExhibitIssue("missing_caption_label", "highlight region caption_label is required"))
        _validate_figure4_artifact(region.get("source_diff_excerpt"), "region_source_diff_excerpt", issues)
        _validate_figure4_artifact(region.get("rendered_region_artifact"), "region_rendered_artifact", issues)
        components = region.get("semantic_components")
        if not isinstance(components, list) or not components:
            issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_semantic_components", "semantic_components must be a non-empty list"))
        else:
            for component in components:
                if component not in EXPECTED_SEMANTIC_COMPONENTS:
                    issues.append(Figure4MatrixDiscoveryExhibitIssue("invalid_semantic_component", "semantic component must match the matrix diff taxonomy"))
                elif isinstance(component, str):
                    semantic_components.add(component)
    for region_id in EXPECTED_FIGURE4_REGION_IDS:
        if region_id not in seen_regions:
            issues.append(Figure4MatrixDiscoveryExhibitIssue("missing_highlight_region", "Figure 4 exhibit must include left diff plus three highlighted regions"))
    return len(value), semantic_components


def _validate_panels(
    value: object,
    issues: list[Figure9MatrixDiffExhibitIssue],
) -> tuple[int, set[str]]:
    if not isinstance(value, list):
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_panels", "panels must be a list"))
        return 0, set()
    seen_panels: set[str] = set()
    seen_orders: set[int] = set()
    semantic_components: set[str] = set()
    for panel in value:
        if not isinstance(panel, dict):
            issues.append(Figure9MatrixDiffExhibitIssue("invalid_panel", "panel must be an object"))
            continue
        panel_id = panel.get("panel_id")
        if panel_id not in EXPECTED_PANEL_ORDER:
            issues.append(Figure9MatrixDiffExhibitIssue("invalid_panel_id", "panel_id must be figure9a, figure9b, or figure9c"))
        else:
            seen_panels.add(panel_id)
            expected_order = EXPECTED_PANEL_ORDER[panel_id]
            expected_page = EXPECTED_PANEL_PAGES[panel_id]
            if panel.get("panel_order") != expected_order:
                issues.append(Figure9MatrixDiffExhibitIssue("invalid_panel_order", "panel_order must match Figure 9a-9c order"))
            else:
                seen_orders.add(expected_order)
            if panel.get("source_pdf_page") != expected_page:
                issues.append(Figure9MatrixDiffExhibitIssue("invalid_panel_page", "source_pdf_page must match the local PDF page for the panel"))
        if not isinstance(panel.get("caption_ref"), str) or "Magnified version of Figure 4" not in panel["caption_ref"]:
            issues.append(Figure9MatrixDiffExhibitIssue("invalid_panel_caption_ref", "panel caption_ref must cite the magnified Figure 4 caption"))
        _validate_line_span(panel.get("code_line_span"), issues)
        _validate_artifact(panel.get("source_diff_excerpt"), "source_diff_excerpt", issues)
        _validate_artifact(panel.get("rendered_image_artifact"), "rendered_image_artifact", issues)
        _validate_artifact(panel.get("rendered_text_artifact"), "rendered_text_artifact", issues)
        panel_components = panel.get("semantic_components")
        if not isinstance(panel_components, list) or not panel_components:
            issues.append(Figure9MatrixDiffExhibitIssue("invalid_semantic_components", "semantic_components must be a non-empty list"))
        else:
            for component in panel_components:
                if component not in EXPECTED_SEMANTIC_COMPONENTS:
                    issues.append(Figure9MatrixDiffExhibitIssue("invalid_semantic_component", "semantic component must match Figure 9 matrix diff taxonomy"))
                elif isinstance(component, str):
                    semantic_components.add(component)
        sweep_fields = panel.get("sweep_fields")
        if sweep_fields is not None:
            _validate_sweep_fields(sweep_fields, issues)
    for panel_id in EXPECTED_PANEL_ORDER:
        if panel_id not in seen_panels:
            issues.append(Figure9MatrixDiffExhibitIssue("missing_panel", "Figure 9 exhibit must include panels 9a, 9b, and 9c"))
    if seen_orders and seen_orders != {1, 2, 3}:
        issues.append(Figure9MatrixDiffExhibitIssue("incomplete_panel_continuity", "panel orders must cover 1, 2, and 3"))
    return len(value), semantic_components


def _validate_line_span(value: object, issues: list[Figure9MatrixDiffExhibitIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_line_span", "code_line_span must be an object"))
        return
    start = value.get("start")
    end = value.get("end")
    if (
        isinstance(start, bool)
        or isinstance(end, bool)
        or not isinstance(start, int)
        or not isinstance(end, int)
        or start <= 0
        or end < start
    ):
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_line_span", "line span start/end must be positive and ordered"))


def _validate_figure4_artifact(
    value: object,
    label: str,
    issues: list[Figure4MatrixDiscoveryExhibitIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(Figure4MatrixDiscoveryExhibitIssue(f"invalid_{label}", f"{label} must be an object"))
        return
    path = value.get("path")
    path_obj = Path(path) if isinstance(path, str) else None
    if (
        path_obj is None
        or not path
        or path_obj.is_absolute()
        or path.startswith(("/", "\\"))
        or ".." in path_obj.parts
    ):
        issues.append(Figure4MatrixDiscoveryExhibitIssue(f"invalid_{label}_path", f"{label} path must be safe and relative"))
    sha = value.get("sha256")
    if not isinstance(sha, str) or _SHA256_RE.fullmatch(sha) is None:
        issues.append(Figure4MatrixDiscoveryExhibitIssue(f"invalid_{label}_hash", f"{label} sha256 must be a lowercase SHA-256 hex digest"))
    byte_count = value.get("bytes")
    if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count <= 0:
        issues.append(Figure4MatrixDiscoveryExhibitIssue(f"invalid_{label}_bytes", f"{label} bytes must be a positive integer"))


def _validate_sweep_fields(value: object, issues: list[Figure9MatrixDiffExhibitIssue]) -> None:
    if not isinstance(value, list) or not value:
        issues.append(Figure9MatrixDiffExhibitIssue("invalid_sweep_fields", "sweep_fields must be a non-empty list when present"))
        return
    for field in value:
        if not isinstance(field, str) or not field.strip():
            issues.append(Figure9MatrixDiffExhibitIssue("invalid_sweep_field", "sweep field names must be non-empty strings"))


def _validate_artifact(
    value: object,
    label: str,
    issues: list[Figure9MatrixDiffExhibitIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(Figure9MatrixDiffExhibitIssue(f"invalid_{label}", f"{label} must be an object"))
        return
    path = value.get("path")
    path_obj = Path(path) if isinstance(path, str) else None
    if (
        path_obj is None
        or not path
        or path_obj.is_absolute()
        or path.startswith(("/", "\\"))
        or ".." in path_obj.parts
    ):
        issues.append(Figure9MatrixDiffExhibitIssue(f"invalid_{label}_path", f"{label} path must be safe and relative"))
    sha = value.get("sha256")
    if not isinstance(sha, str) or _SHA256_RE.fullmatch(sha) is None:
        issues.append(Figure9MatrixDiffExhibitIssue(f"invalid_{label}_hash", f"{label} sha256 must be a lowercase SHA-256 hex digest"))
    byte_count = value.get("bytes")
    if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count <= 0:
        issues.append(Figure9MatrixDiffExhibitIssue(f"invalid_{label}_bytes", f"{label} bytes must be a positive integer"))
