from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.appendix_a_matrix_registry import (
    TARGET_SUITE as APPENDIX_A_TARGET_SUITE,
    TABLE_2_SELECTED_TARGET_IDS,
    matrix_target_records,
)


FIGURE4_MATRIX_DISCOVERY_EXHIBIT_SCHEMA = "libreevolve.alphaevolve_figure4_matrix_discovery_exhibit.v1"
FIGURE9_MATRIX_DIFF_EXHIBIT_SCHEMA = "libreevolve.alphaevolve_figure9_matrix_diff_exhibit.v1"
MATRIX_RANK_TABLE_EXHIBIT_SCHEMA = "libreevolve.alphaevolve_matrix_rank_table_exhibit.v1"
MATRIX_RANK_TABLE_ARTIFACT_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_matrix_rank_table_artifact_boundary.v1"
EXPECTED_FIGURE4_EXHIBIT_ID = "figure4_matrix_discovery"
EXPECTED_FIGURE9_EXHIBIT_ID = "figure9_matrix_diff_magnified"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_FIGURE4_SOURCE_FIGURE = "Figure 4"
EXPECTED_SOURCE_FIGURE = "Figures 9a-9c"
EXPECTED_TARGET_ID = "mm_4x4x4"
EXPECTED_TARGET_DIMENSIONS = [4, 4, 4]
EXPECTED_RESULT_RANK = 48
EXPECTED_TABLE_IDS = frozenset({"table2_matrix_rank_selected", "appendix_a_table3_matrix_rank_full"})
EXPECTED_TABLE_PAGES = {
    "table2_matrix_rank_selected": 9,
    "appendix_a_table3_matrix_rank_full": 34,
}
EXPECTED_TABLE_SOURCE_NAMES = {
    "table2_matrix_rank_selected": "Table 2",
    "appendix_a_table3_matrix_rank_full": "Appendix A Table 3",
}
EXPECTED_COMPLEX_ROW_IDS = frozenset({"mm_3x4x7", "mm_4x4x4", "mm_4x4x8"})
EXPECTED_CONCURRENT_NOTE_TARGET_ID = "mm_4x5x6"
EXPECTED_OUTCOME_ENCODING = {
    "matched": "uncolored_or_neutral",
    "surpassed": "green",
    "fell_behind": "red",
}
MATRIX_RANK_TABLE_ARTIFACT_STATUSES = frozenset({"not_emitted_by_local_report_export", "emitted"})
MATRIX_RANK_TABLE_ARTIFACT_REQUIRED_FIELDS = (
    "table_id",
    "source_table",
    "source_pdf_page",
    "source_caption_ref",
    "row_count",
    "source_pdf_excerpt",
    "rendered_table_artifact",
    "ocr_text_artifact",
    "artifact_paths",
    "artifact_sha256",
    "matrix_rank_table_exhibit",
)
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


@dataclass(frozen=True)
class MatrixRankTableExhibitIssue:
    code: str
    message: str


@dataclass(frozen=True)
class MatrixRankTableExhibitValidation:
    ok: bool
    table_count: int
    row_count: int
    issues: list[MatrixRankTableExhibitIssue]


@dataclass(frozen=True)
class MatrixRankTableArtifactBoundaryValidation:
    ok: bool
    artifact_status: str | None
    emitted_artifact_count: int
    required_field_count: int
    issues: list[MatrixRankTableExhibitIssue]


def matrix_rank_table_artifact_boundary_record() -> dict[str, Any]:
    return {
        "schema": MATRIX_RANK_TABLE_ARTIFACT_BOUNDARY_SCHEMA,
        "exhibit_schema": MATRIX_RANK_TABLE_EXHIBIT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "target_suite": APPENDIX_A_TARGET_SUITE,
        "artifact_status": "not_emitted_by_local_report_export",
        "local_export_scope": "matrix_rank_table_report_export",
        "required_artifact_fields": list(MATRIX_RANK_TABLE_ARTIFACT_REQUIRED_FIELDS),
        "emitted_artifacts": [],
        "claim_boundary": (
            "This is a Table 2/Table 3 matrix-rank table artifact availability "
            "boundary. It does not claim local report/export code emits rendered "
            "table, OCR text, or source-excerpt artifacts."
        ),
    }


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


def validate_matrix_rank_table_exhibit(
    exhibit: object | str | Path,
) -> MatrixRankTableExhibitValidation:
    data, read_issues = _load_table_exhibit(exhibit)
    if read_issues:
        return MatrixRankTableExhibitValidation(False, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixRankTableExhibitIssue] = []
    if data.get("schema") != MATRIX_RANK_TABLE_EXHIBIT_SCHEMA:
        issues.append(MatrixRankTableExhibitIssue("invalid_schema", "unsupported matrix rank table exhibit schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(MatrixRankTableExhibitIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("target_suite") != APPENDIX_A_TARGET_SUITE:
        issues.append(MatrixRankTableExhibitIssue("invalid_target_suite", "target_suite must be alphaevolve_appendix_a"))
    _validate_table_evidence_links(data.get("evidence_links"), issues)
    table_count, row_count = _validate_rank_tables(data.get("tables"), issues)
    return MatrixRankTableExhibitValidation(
        ok=not issues,
        table_count=table_count,
        row_count=row_count,
        issues=issues,
    )


def validate_matrix_rank_table_artifact_boundary(
    boundary: object | str | Path | None = None,
) -> MatrixRankTableArtifactBoundaryValidation:
    if boundary is None:
        boundary = matrix_rank_table_artifact_boundary_record()
    data, read_issues = _load_table_boundary(boundary)
    if read_issues:
        return MatrixRankTableArtifactBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MatrixRankTableExhibitIssue] = []
    if data.get("schema") != MATRIX_RANK_TABLE_ARTIFACT_BOUNDARY_SCHEMA:
        issues.append(MatrixRankTableExhibitIssue("invalid_schema", "unsupported matrix rank table artifact boundary schema"))
    if data.get("exhibit_schema") != MATRIX_RANK_TABLE_EXHIBIT_SCHEMA:
        issues.append(MatrixRankTableExhibitIssue("invalid_exhibit_schema", "exhibit_schema must identify matrix-rank table exhibit records"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(MatrixRankTableExhibitIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("target_suite") != APPENDIX_A_TARGET_SUITE:
        issues.append(MatrixRankTableExhibitIssue("invalid_target_suite", "target_suite must be alphaevolve_appendix_a"))
    status = data.get("artifact_status")
    if status not in MATRIX_RANK_TABLE_ARTIFACT_STATUSES:
        issues.append(MatrixRankTableExhibitIssue("invalid_artifact_status", "artifact_status must be a known matrix-rank table artifact status"))
    if not isinstance(data.get("local_export_scope"), str) or not data["local_export_scope"].strip():
        issues.append(MatrixRankTableExhibitIssue("missing_local_export_scope", "local_export_scope is required"))
    required_fields = data.get("required_artifact_fields")
    required_field_count = _validate_rank_table_artifact_required_fields(required_fields, issues)
    artifacts = data.get("emitted_artifacts")
    if not isinstance(artifacts, list):
        issues.append(MatrixRankTableExhibitIssue("invalid_emitted_artifacts", "emitted_artifacts must be a list"))
        artifact_count = 0
    else:
        artifact_count = len(artifacts)
        if status == "not_emitted_by_local_report_export":
            if artifacts:
                issues.append(MatrixRankTableExhibitIssue("unexpected_emitted_artifacts", "absence boundary must not include emitted table artifacts"))
            boundary_text = data.get("claim_boundary")
            if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
                issues.append(MatrixRankTableExhibitIssue("missing_claim_boundary", "absence boundary must state that it does not claim local artifact emission"))
        elif status == "emitted":
            if not artifacts:
                issues.append(MatrixRankTableExhibitIssue("missing_matrix_rank_table_artifacts", "emitted status requires Table 2/Table 3 artifact records"))
            for artifact in artifacts:
                _validate_rank_table_artifact_record(artifact, issues)
    return MatrixRankTableArtifactBoundaryValidation(
        ok=not issues,
        artifact_status=status if isinstance(status, str) else None,
        emitted_artifact_count=artifact_count,
        required_field_count=required_field_count,
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


def render_matrix_rank_table_exhibit_summary(exhibit: dict[str, Any]) -> str:
    validation = validate_matrix_rank_table_exhibit(exhibit)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve matrix-rank table exhibit",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| table_count | {validation.table_count} |",
        f"| row_count | {validation.row_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def render_matrix_rank_table_artifact_boundary_summary(boundary: dict[str, Any] | None = None) -> str:
    if boundary is None:
        boundary = matrix_rank_table_artifact_boundary_record()
    validation = validate_matrix_rank_table_artifact_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve matrix-rank table artifact boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| artifact_status | {validation.artifact_status or '<unknown>'} |",
        f"| emitted_artifact_count | {validation.emitted_artifact_count} |",
        f"| required_field_count | {validation.required_field_count} |",
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


def _load_table_exhibit(
    exhibit: object | str | Path,
) -> tuple[dict[str, Any] | None, list[MatrixRankTableExhibitIssue]]:
    if isinstance(exhibit, dict):
        return dict(exhibit), []
    if isinstance(exhibit, (str, Path)):
        path = Path(exhibit)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [MatrixRankTableExhibitIssue("read_error", f"failed to read matrix-rank table exhibit: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [MatrixRankTableExhibitIssue("invalid_json", f"invalid matrix-rank table exhibit JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [MatrixRankTableExhibitIssue("invalid_shape", "matrix-rank table exhibit must be a JSON object")]


def _load_table_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[MatrixRankTableExhibitIssue]]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, (str, Path)):
        path = Path(boundary)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [MatrixRankTableExhibitIssue("read_error", f"failed to read matrix-rank table artifact boundary: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [MatrixRankTableExhibitIssue("invalid_json", f"invalid matrix-rank table artifact boundary JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [MatrixRankTableExhibitIssue("invalid_shape", "matrix-rank table artifact boundary must be a JSON object")]


def _validate_rank_table_artifact_required_fields(
    value: object,
    issues: list[MatrixRankTableExhibitIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(MatrixRankTableExhibitIssue("invalid_required_artifact_fields", "required_artifact_fields must be a non-empty list"))
        return 0
    seen: set[str] = set()
    for field in value:
        if not isinstance(field, str) or not field.strip():
            issues.append(MatrixRankTableExhibitIssue("invalid_required_artifact_field", "required artifact field names must be non-empty strings"))
            continue
        if field in seen:
            issues.append(MatrixRankTableExhibitIssue("duplicate_required_artifact_field", "required_artifact_fields must be unique"))
        seen.add(field)
    missing = sorted(set(MATRIX_RANK_TABLE_ARTIFACT_REQUIRED_FIELDS) - seen)
    if missing:
        issues.append(MatrixRankTableExhibitIssue("missing_required_artifact_field", "required_artifact_fields must include all matrix-rank table artifact fields"))
    return len(value)


def _validate_rank_table_artifact_record(
    artifact: object,
    issues: list[MatrixRankTableExhibitIssue],
) -> None:
    if not isinstance(artifact, dict):
        issues.append(MatrixRankTableExhibitIssue("invalid_matrix_rank_table_artifact", "emitted table artifact records must be objects"))
        return
    table_id = artifact.get("table_id")
    if table_id not in EXPECTED_TABLE_IDS:
        issues.append(MatrixRankTableExhibitIssue("invalid_artifact_table_id", "artifact table_id must identify Table 2 or Appendix A Table 3"))
    if table_id in EXPECTED_TABLE_IDS:
        if artifact.get("source_table") != EXPECTED_TABLE_SOURCE_NAMES[table_id]:
            issues.append(MatrixRankTableExhibitIssue("invalid_artifact_source_table", "artifact source_table must match the declared table"))
        if artifact.get("source_pdf_page") != EXPECTED_TABLE_PAGES[table_id]:
            issues.append(MatrixRankTableExhibitIssue("invalid_artifact_source_pdf_page", "artifact source_pdf_page must match the declared table"))
    if not isinstance(artifact.get("source_caption_ref"), str) or not artifact["source_caption_ref"].strip():
        issues.append(MatrixRankTableExhibitIssue("missing_artifact_source_caption_ref", "artifact source_caption_ref is required"))
    if isinstance(artifact.get("row_count"), bool) or not isinstance(artifact.get("row_count"), int) or artifact["row_count"] <= 0:
        issues.append(MatrixRankTableExhibitIssue("invalid_artifact_row_count", "artifact row_count must be a positive integer"))
    _validate_table_artifact(artifact.get("source_pdf_excerpt"), "artifact_source_pdf_excerpt", issues)
    _validate_table_artifact(artifact.get("rendered_table_artifact"), "artifact_rendered_table_artifact", issues)
    _validate_table_artifact(artifact.get("ocr_text_artifact"), "artifact_ocr_text_artifact", issues)
    _validate_rank_table_artifact_paths(artifact.get("artifact_paths"), issues)
    sha = artifact.get("artifact_sha256")
    if not isinstance(sha, str) or _SHA256_RE.fullmatch(sha) is None:
        issues.append(MatrixRankTableExhibitIssue("invalid_artifact_sha256", "artifact_sha256 must be a lowercase SHA-256 hex digest"))
    exhibit_report = validate_matrix_rank_table_exhibit(artifact.get("matrix_rank_table_exhibit"))
    issues.extend(
        MatrixRankTableExhibitIssue(f"invalid_nested_exhibit_{issue.code}", issue.message)
        for issue in exhibit_report.issues
    )


def _validate_rank_table_artifact_paths(
    value: object,
    issues: list[MatrixRankTableExhibitIssue],
) -> None:
    if not isinstance(value, list) or not value:
        issues.append(MatrixRankTableExhibitIssue("invalid_artifact_paths", "artifact_paths must be a non-empty list"))
        return
    seen: set[str] = set()
    for path in value:
        path_obj = Path(path) if isinstance(path, str) else None
        if (
            path_obj is None
            or not path
            or path_obj.is_absolute()
            or path.startswith(("/", "\\"))
            or ".." in path_obj.parts
        ):
            issues.append(MatrixRankTableExhibitIssue("invalid_artifact_path", "artifact_paths entries must be safe relative paths"))
            continue
        if path in seen:
            issues.append(MatrixRankTableExhibitIssue("duplicate_artifact_path", "artifact_paths entries must be unique"))
        seen.add(path)


def _validate_table_evidence_links(
    value: object,
    issues: list[MatrixRankTableExhibitIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixRankTableExhibitIssue("invalid_evidence_links", "evidence_links must be an object"))
        return
    for field in (
        "appendix_a_registry_ref",
        "subset_scope_ref",
        "row_note_ref",
        "scalar_field_evidence_ref",
        "companion_colab_ref",
    ):
        if not isinstance(value.get(field), str) or not value[field].strip():
            issues.append(MatrixRankTableExhibitIssue(f"missing_{field}", f"evidence_links.{field} is required"))


def _validate_rank_tables(
    value: object,
    issues: list[MatrixRankTableExhibitIssue],
) -> tuple[int, int]:
    if not isinstance(value, list) or not value:
        issues.append(MatrixRankTableExhibitIssue("invalid_tables", "tables must be a non-empty list"))
        return 0, 0
    seen: set[str] = set()
    row_count = 0
    for table in value:
        if not isinstance(table, dict):
            issues.append(MatrixRankTableExhibitIssue("invalid_table", "table entries must be objects"))
            continue
        table_id = table.get("table_id")
        if table_id not in EXPECTED_TABLE_IDS:
            issues.append(MatrixRankTableExhibitIssue("invalid_table_id", "table_id must identify Table 2 or Appendix A Table 3"))
            continue
        if isinstance(table_id, str):
            seen.add(table_id)
            row_count += _validate_rank_table(table, table_id, issues)
    for table_id in sorted(EXPECTED_TABLE_IDS - seen):
        issues.append(MatrixRankTableExhibitIssue("missing_table", "matrix-rank table exhibit must include Table 2 and Appendix A Table 3"))
    return len(value), row_count


def _validate_rank_table(
    table: dict[str, Any],
    table_id: str,
    issues: list[MatrixRankTableExhibitIssue],
) -> int:
    expected_rows = _expected_table_rows(table_id)
    if table.get("source_table") != EXPECTED_TABLE_SOURCE_NAMES[table_id]:
        issues.append(MatrixRankTableExhibitIssue("invalid_source_table", "source_table must match the declared matrix rank table"))
    if table.get("source_pdf_page") != EXPECTED_TABLE_PAGES[table_id]:
        issues.append(MatrixRankTableExhibitIssue("invalid_source_pdf_page", "source_pdf_page must match the local AlphaEvolve PDF table page"))
    caption = table.get("source_caption_ref")
    if not isinstance(caption, str) or not caption.strip():
        issues.append(MatrixRankTableExhibitIssue("missing_source_caption_ref", "source_caption_ref is required"))
    else:
        _validate_table_caption(table_id, caption, issues)
    membership = table.get("membership")
    expected_membership = "table_2_selected" if table_id == "table2_matrix_rank_selected" else "appendix_a_full"
    if membership != expected_membership:
        issues.append(MatrixRankTableExhibitIssue("invalid_membership", "membership must identify selected-row or full-table scope"))
    if table.get("row_count") != len(expected_rows):
        issues.append(MatrixRankTableExhibitIssue("invalid_row_count", "row_count must match expected table rows"))
    if table.get("outcome_counts") != _expected_outcome_counts(expected_rows):
        issues.append(MatrixRankTableExhibitIssue("invalid_outcome_counts", "outcome_counts must match expected table row outcomes"))
    if table.get("outcome_encoding") != EXPECTED_OUTCOME_ENCODING:
        issues.append(MatrixRankTableExhibitIssue("invalid_outcome_encoding", "outcome_encoding must preserve matched/surpassed/fell-behind color semantics"))
    expected_complex_ids = [row["target_id"] for row in expected_rows if row["target_id"] in EXPECTED_COMPLEX_ROW_IDS]
    if table.get("complex_valued_target_ids") != expected_complex_ids:
        issues.append(MatrixRankTableExhibitIssue("invalid_complex_valued_target_ids", "complex-valued annotations must match the paper-noted rows in this table"))
    expected_note_ids = [EXPECTED_CONCURRENT_NOTE_TARGET_ID] if any(row["target_id"] == EXPECTED_CONCURRENT_NOTE_TARGET_ID for row in expected_rows) else []
    if table.get("concurrent_note_target_ids") != expected_note_ids:
        issues.append(MatrixRankTableExhibitIssue("invalid_concurrent_note_target_ids", "concurrent-note annotations must match table rows"))
    _validate_table_artifacts(table.get("source_links"), issues)
    return _validate_table_rows(table.get("rows"), table_id, expected_rows, issues)


def _validate_table_caption(
    table_id: str,
    caption: str,
    issues: list[MatrixRankTableExhibitIssue],
) -> None:
    if table_id == "table2_matrix_rank_selected":
        if "Upper bounds on the rank" not in caption or "accompanying Google Colab" not in caption:
            issues.append(MatrixRankTableExhibitIssue("invalid_table2_caption", "Table 2 caption must preserve rank and Colab linkage"))
    elif table_id == "appendix_a_table3_matrix_rank_full":
        if "Full version of Table 2" not in caption or "38 cases" not in caption or "14 cases" not in caption or "2 cases" not in caption:
            issues.append(MatrixRankTableExhibitIssue("invalid_table3_caption", "Table 3 caption must preserve full-table aggregate counts"))


def _validate_table_artifacts(
    value: object,
    issues: list[MatrixRankTableExhibitIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixRankTableExhibitIssue("invalid_source_links", "source_links must be an object"))
        return
    for key in ("source_pdf_excerpt", "rendered_table_artifact", "ocr_text_artifact"):
        _validate_table_artifact(value.get(key), key, issues)


def _validate_table_artifact(
    value: object,
    label: str,
    issues: list[MatrixRankTableExhibitIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(MatrixRankTableExhibitIssue(f"invalid_{label}", f"{label} must be an object"))
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
        issues.append(MatrixRankTableExhibitIssue(f"invalid_{label}_path", f"{label} path must be safe and relative"))
    sha = value.get("sha256")
    if not isinstance(sha, str) or _SHA256_RE.fullmatch(sha) is None:
        issues.append(MatrixRankTableExhibitIssue(f"invalid_{label}_hash", f"{label} sha256 must be a lowercase SHA-256 hex digest"))
    byte_count = value.get("bytes")
    if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count <= 0:
        issues.append(MatrixRankTableExhibitIssue(f"invalid_{label}_bytes", f"{label} bytes must be a positive integer"))


def _validate_table_rows(
    value: object,
    table_id: str,
    expected_rows: list[dict[str, Any]],
    issues: list[MatrixRankTableExhibitIssue],
) -> int:
    if not isinstance(value, list) or not value:
        issues.append(MatrixRankTableExhibitIssue("invalid_rows", "rows must be a non-empty list"))
        return 0
    expected_by_id = {row["target_id"]: row for row in expected_rows}
    expected_order = [row["target_id"] for row in expected_rows]
    seen: list[str] = []
    for index, row in enumerate(value, start=1):
        if not isinstance(row, dict):
            issues.append(MatrixRankTableExhibitIssue("invalid_row", "table rows must be objects"))
            continue
        target_id = row.get("target_id")
        if not isinstance(target_id, str) or target_id not in expected_by_id:
            issues.append(MatrixRankTableExhibitIssue("unknown_row_target_id", "row target_id must belong to the declared table"))
            continue
        seen.append(target_id)
        expected = expected_by_id[target_id]
        if row.get("row_order") != index:
            issues.append(MatrixRankTableExhibitIssue("invalid_row_order", "row_order must preserve source table order"))
        expected_target = expected_order[index - 1] if index <= len(expected_order) else None
        if target_id != expected_target:
            issues.append(MatrixRankTableExhibitIssue("row_order_target_mismatch", "row target order must match source table order"))
        for field in ("dimensions", "best_known_rank", "alphaevolve_rank", "outcome"):
            if row.get(field) != expected[field]:
                issues.append(MatrixRankTableExhibitIssue(f"invalid_row_{field}", f"row {field} must match Appendix A registry"))
        if row.get("registry_ref") != target_id:
            issues.append(MatrixRankTableExhibitIssue("invalid_registry_ref", "row registry_ref must match target_id"))
        if row.get("complex_valued") != (target_id in EXPECTED_COMPLEX_ROW_IDS):
            issues.append(MatrixRankTableExhibitIssue("invalid_row_complex_annotation", "row complex_valued flag must match paper caveats"))
        expected_note_ref = "concurrent_work_rank90_mm_4x5x6" if target_id == EXPECTED_CONCURRENT_NOTE_TARGET_ID else None
        if row.get("concurrent_note_ref") != expected_note_ref:
            issues.append(MatrixRankTableExhibitIssue("invalid_row_concurrent_note_ref", "row concurrent_note_ref must match Appendix A row-note metadata"))
        for field in ("matrix_result_ref", "companion_colab_ref"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                issues.append(MatrixRankTableExhibitIssue(f"missing_row_{field}", f"row {field} is required"))
    if seen != expected_order:
        issues.append(MatrixRankTableExhibitIssue("table_row_set_mismatch", "table rows must exactly match expected source table membership and order"))
    return len(value)


def _expected_table_rows(table_id: str) -> list[dict[str, Any]]:
    records = matrix_target_records()
    records_by_id = {record["id"]: record for record in records if isinstance(record.get("id"), str)}
    if table_id == "table2_matrix_rank_selected":
        target_ids = list(TABLE_2_SELECTED_TARGET_IDS)
    else:
        target_ids = [record["id"] for record in records if isinstance(record.get("id"), str)]
    rows: list[dict[str, Any]] = []
    for target_id in target_ids:
        record = records_by_id[target_id]
        rows.append(
            {
                "target_id": target_id,
                "dimensions": record["dimensions"],
                "best_known_rank": record["best_known_rank"],
                "alphaevolve_rank": record["alphaevolve_rank"],
                "outcome": record["outcome"],
            }
        )
    return rows


def _expected_outcome_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"matched": 0, "surpassed": 0, "fell_behind": 0}
    for row in rows:
        outcome = row["outcome"]
        counts[outcome] += 1
    return counts


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
