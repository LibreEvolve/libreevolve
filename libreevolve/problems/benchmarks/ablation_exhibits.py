from __future__ import annotations

import json
import re
import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ablation_registry import EXPECTED_VARIANT_IDS
from .ablation_results import FIGURE8_TARGET_FAMILIES, validate_ablation_result_report


FIGURE8_EXHIBIT_SCHEMA = "libreevolve.alphaevolve_figure8_exhibit.v1"
EXPECTED_EXHIBIT_ID = "figure8_ablation_curves"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_FIGURE = "Figure 8"
EXPECTED_PANEL_IDS = ("matrix_tensor_decomposition", "kissing_number_sphere_packing")
EXPECTED_LEGEND_LABELS = {
    "full_system": "Full method",
    "no_evolution": "No evolution",
    "no_context_in_prompt": "No context in the prompt",
    "no_meta_prompt_evolution": "No meta prompt evolution",
    "no_full_file_evolution": "No full-file evolution",
    "small_base_llm_only": "Small base LLM only",
}
EXPECTED_SERIES_COLORS = {
    "full_system": "#1f77b4",
    "no_evolution": "#ff7f0e",
    "no_context_in_prompt": "#2ca02c",
    "no_meta_prompt_evolution": "#d62728",
    "no_full_file_evolution": "#9467bd",
    "small_base_llm_only": "#8c564b",
}
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class Figure8ExhibitIssue:
    code: str
    message: str


@dataclass(frozen=True)
class Figure8ExhibitValidation:
    ok: bool
    panel_count: int
    series_count: int
    issues: list[Figure8ExhibitIssue]


def figure8_exhibit_from_ablation_report(
    report: object | str | Path,
    *,
    rendered_artifact: dict[str, Any],
    ablation_report_artifact: dict[str, Any],
    source_caption_ref: str = "AlphaEvolve Figure 8 caption",
    rendering_parameters: dict[str, Any] | None = None,
    run_links: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a Figure 8 exhibit record from a validated ablation report."""
    report_validation = validate_ablation_result_report(report)
    if not report_validation.ok:
        messages = "; ".join(issue.message for issue in report_validation.issues)
        raise ValueError(f"ablation report is invalid: {messages}")
    data = _load_valid_report_data(report)
    curve_artifact = _artifact_with_kind(data, "curve_summary")
    raw_artifact = _artifact_with_kind(data, "raw_records")
    if curve_artifact is None:
        raise ValueError("ablation report must declare a curve_summary artifact")
    if raw_artifact is None:
        raise ValueError("ablation report must declare a raw_records artifact")
    panels = [
        _panel_from_report(data, panel_id)
        for panel_id in EXPECTED_PANEL_IDS
    ]
    exhibit: dict[str, Any] = {
        "schema": FIGURE8_EXHIBIT_SCHEMA,
        "exhibit_id": EXPECTED_EXHIBIT_ID,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_figure": EXPECTED_SOURCE_FIGURE,
        "source_caption_ref": source_caption_ref,
        "rendered_artifact": copy.deepcopy(rendered_artifact),
        "source_links": {
            "ablation_report": copy.deepcopy(ablation_report_artifact),
            "curve_summary": _artifact_link(curve_artifact),
            "raw_seed_traces": _artifact_link(raw_artifact),
        },
        "ablation_report_schema": data.get("schema"),
        "budget_axis": data.get("budget_axis"),
        "rendering_parameters": copy.deepcopy(
            rendering_parameters
            if rendering_parameters is not None
            else {
                "curve_source": "report.curve_summaries",
                "std_band_source": "curve_summary.std_score",
            }
        ),
        "run_links": copy.deepcopy(run_links or []),
        "panels": panels,
    }
    validation = validate_figure8_exhibit(exhibit)
    if not validation.ok:
        messages = "; ".join(issue.message for issue in validation.issues)
        raise ValueError(f"Figure 8 exhibit is invalid: {messages}")
    return exhibit


def validate_figure8_exhibit(exhibit: object | str | Path) -> Figure8ExhibitValidation:
    data, read_issues = _load_exhibit(exhibit)
    if read_issues:
        return Figure8ExhibitValidation(False, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[Figure8ExhibitIssue] = []
    if data.get("schema") != FIGURE8_EXHIBIT_SCHEMA:
        issues.append(Figure8ExhibitIssue("invalid_schema", "unsupported Figure 8 exhibit schema"))
    if data.get("exhibit_id") != EXPECTED_EXHIBIT_ID:
        issues.append(Figure8ExhibitIssue("invalid_exhibit_id", "exhibit_id must identify Figure 8 ablation curves"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(Figure8ExhibitIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_figure") != EXPECTED_SOURCE_FIGURE:
        issues.append(Figure8ExhibitIssue("invalid_source_figure", "source_figure must be Figure 8"))
    if not isinstance(data.get("source_caption_ref"), str) or not data["source_caption_ref"].strip():
        issues.append(Figure8ExhibitIssue("missing_source_caption_ref", "source_caption_ref is required"))
    _validate_rendered_artifact(data.get("rendered_artifact"), "rendered_artifact", issues)
    _validate_source_links(data.get("source_links"), issues)
    panels = data.get("panels")
    panel_count, series_count = _validate_panels(panels, issues)
    return Figure8ExhibitValidation(
        ok=not issues,
        panel_count=panel_count,
        series_count=series_count,
        issues=issues,
    )


def render_figure8_exhibit_summary(exhibit: dict[str, Any]) -> str:
    validation = validate_figure8_exhibit(exhibit)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve Figure 8 exhibit",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| panel_count | {validation.panel_count} |",
        f"| series_count | {validation.series_count} |",
        f"| source_figure | {exhibit.get('source_figure', '<unknown>')} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_exhibit(exhibit: object | str | Path) -> tuple[dict[str, Any] | None, list[Figure8ExhibitIssue]]:
    if isinstance(exhibit, dict):
        return dict(exhibit), []
    if isinstance(exhibit, (str, Path)):
        path = Path(exhibit)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [Figure8ExhibitIssue("read_error", f"failed to read Figure 8 exhibit: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [Figure8ExhibitIssue("invalid_json", f"invalid Figure 8 exhibit JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [Figure8ExhibitIssue("invalid_shape", "Figure 8 exhibit must be a JSON object")]


def _load_valid_report_data(report: object | str | Path) -> dict[str, Any]:
    if isinstance(report, dict):
        return copy.deepcopy(report)
    path = Path(report)
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_with_kind(report: dict[str, Any], kind: str) -> dict[str, Any] | None:
    artifacts = report.get("artifacts")
    if not isinstance(artifacts, list):
        return None
    for artifact in artifacts:
        if isinstance(artifact, dict) and artifact.get("kind") == kind:
            return artifact
    return None


def _artifact_link(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": artifact.get("path"),
        "sha256": artifact.get("sha256"),
        "bytes": artifact.get("bytes"),
    }


def _panel_from_report(report: dict[str, Any], panel_id: str) -> dict[str, Any]:
    target_ids = [
        target["target_id"]
        for target in report.get("targets", [])
        if isinstance(target, dict) and target.get("target_family") == panel_id
    ]
    return {
        "panel_id": panel_id,
        "target_family": panel_id,
        "target_ids": sorted(target_ids),
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
        "series": [
            {
                "variant_id": variant_id,
                "legend_label": EXPECTED_LEGEND_LABELS[variant_id],
                "curve_summary_ref": f"curve_summary:{panel_id}:{variant_id}",
                "raw_seed_trace_ref": f"raw_seed_trace:{panel_id}:{variant_id}",
                "style": {
                    "color": EXPECTED_SERIES_COLORS[variant_id],
                    "std_band": True,
                },
            }
            for variant_id in EXPECTED_VARIANT_IDS
        ],
    }


def _validate_panels(value: object, issues: list[Figure8ExhibitIssue]) -> tuple[int, int]:
    if not isinstance(value, list):
        issues.append(Figure8ExhibitIssue("invalid_panels", "panels must be a list"))
        return 0, 0
    seen_panels: set[str] = set()
    series_count = 0
    for panel in value:
        if not isinstance(panel, dict):
            issues.append(Figure8ExhibitIssue("invalid_panel", "panel must be an object"))
            continue
        panel_id = panel.get("panel_id")
        if panel_id not in EXPECTED_PANEL_IDS:
            issues.append(Figure8ExhibitIssue("invalid_panel_id", "panel_id must match a Figure 8 panel"))
        elif isinstance(panel_id, str):
            seen_panels.add(panel_id)
        if panel.get("target_family") not in FIGURE8_TARGET_FAMILIES:
            issues.append(Figure8ExhibitIssue("invalid_panel_target_family", "panel target_family must match Figure 8"))
        _validate_axis(panel.get("x_axis"), axis="x", issues=issues)
        _validate_axis(panel.get("y_axis"), axis="y", issues=issues)
        panel_series = panel.get("series")
        series_count += _validate_series(panel_series, issues)
    for panel_id in EXPECTED_PANEL_IDS:
        if panel_id not in seen_panels:
            issues.append(Figure8ExhibitIssue("missing_panel", "Figure 8 exhibit must include both panels"))
    return len(value), series_count


def _validate_axis(value: object, *, axis: str, issues: list[Figure8ExhibitIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(Figure8ExhibitIssue(f"invalid_{axis}_axis", f"{axis}_axis must be an object"))
        return
    if axis == "x":
        if value.get("label") != "Fraction of compute budget":
            issues.append(Figure8ExhibitIssue("invalid_x_axis_label", "x-axis label must be Fraction of compute budget"))
        if value.get("scale") != "linear":
            issues.append(Figure8ExhibitIssue("invalid_x_axis_scale", "x-axis scale must be linear"))
        if value.get("unit") != "fraction":
            issues.append(Figure8ExhibitIssue("invalid_x_axis_unit", "x-axis unit must be fraction"))
    else:
        if not isinstance(value.get("label"), str) or not value["label"].strip():
            issues.append(Figure8ExhibitIssue("missing_y_axis_label", "y-axis label is required"))
        if value.get("direction") != "higher_is_better":
            issues.append(Figure8ExhibitIssue("invalid_y_axis_direction", "y-axis direction must be higher_is_better"))
        if not isinstance(value.get("normalization"), str) or not value["normalization"].strip():
            issues.append(Figure8ExhibitIssue("missing_y_axis_normalization", "y-axis normalization is required"))


def _validate_series(value: object, issues: list[Figure8ExhibitIssue]) -> int:
    if not isinstance(value, list):
        issues.append(Figure8ExhibitIssue("invalid_series", "series must be a list"))
        return 0
    seen: set[str] = set()
    for series in value:
        if not isinstance(series, dict):
            issues.append(Figure8ExhibitIssue("invalid_series_entry", "series entry must be an object"))
            continue
        variant_id = series.get("variant_id")
        if variant_id not in EXPECTED_VARIANT_IDS:
            issues.append(Figure8ExhibitIssue("invalid_series_variant", "series variant_id must match Figure 8 registry"))
        elif isinstance(variant_id, str):
            seen.add(variant_id)
            if series.get("legend_label") != EXPECTED_LEGEND_LABELS[variant_id]:
                issues.append(Figure8ExhibitIssue("invalid_legend_label", "legend_label must match the paper legend"))
        if not isinstance(series.get("curve_summary_ref"), str) or not series["curve_summary_ref"].strip():
            issues.append(Figure8ExhibitIssue("missing_curve_summary_ref", "curve_summary_ref is required"))
        if not isinstance(series.get("raw_seed_trace_ref"), str) or not series["raw_seed_trace_ref"].strip():
            issues.append(Figure8ExhibitIssue("missing_raw_seed_trace_ref", "raw_seed_trace_ref is required"))
        style = series.get("style")
        if not isinstance(style, dict) or not isinstance(style.get("color"), str) or not style["color"].strip():
            issues.append(Figure8ExhibitIssue("missing_series_style", "series style color is required"))
        if not isinstance(style, dict) or style.get("std_band") is not True:
            issues.append(Figure8ExhibitIssue("missing_std_band", "series must declare std_band true"))
    for variant_id in EXPECTED_VARIANT_IDS:
        if variant_id not in seen:
            issues.append(Figure8ExhibitIssue("missing_series_variant", "each panel must include every Figure 8 variant"))
    return len(value)


def _validate_source_links(value: object, issues: list[Figure8ExhibitIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(Figure8ExhibitIssue("invalid_source_links", "source_links must be an object"))
        return
    for key in ("ablation_report", "curve_summary", "raw_seed_traces"):
        _validate_rendered_artifact(value.get(key), key, issues)


def _validate_rendered_artifact(value: object, label: str, issues: list[Figure8ExhibitIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(Figure8ExhibitIssue(f"invalid_{label}", f"{label} must be an object"))
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
        issues.append(Figure8ExhibitIssue(f"invalid_{label}_path", f"{label} path must be safe and relative"))
    sha = value.get("sha256")
    if not isinstance(sha, str) or _SHA256_RE.fullmatch(sha) is None:
        issues.append(Figure8ExhibitIssue(f"invalid_{label}_hash", f"{label} sha256 must be a lowercase SHA-256 hex digest"))
    byte_count = value.get("bytes")
    if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count <= 0:
        issues.append(Figure8ExhibitIssue(f"invalid_{label}_bytes", f"{label} bytes must be a positive integer"))
