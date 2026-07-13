from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_non_goal_contradiction_boundary import (
    NON_GOAL_SPECS,
    roadmap_non_goal_contradiction_boundary_record,
)


ROADMAP_NON_GOAL_MARKDOWN_SCAN_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_non_goal_markdown_scan_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "markdown_corpus_scan_without_runtime_or_promotion_gate"
)
SOURCE_NON_GOAL_BOUNDARY_INPUT = "papers/roadmap_non_goal_contradiction_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "stable_non_goal_ids",
    "markdown_corpus_file_inventory",
    "forbidden_claim_phrase_scan",
    "line_level_hit_records",
    "contradiction_count",
    "runtime_metadata_scan",
    "plugin_docstring_scan",
    "ci_non_goal_promotion_gate",
    "intentional_promotion_workflow",
    "claim_surface_remediation",
    "runtime_plugin_scope_join",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "runtime_metadata_scan": "not_recorded_locally",
    "plugin_docstring_scan": "not_recorded_locally",
    "ci_non_goal_promotion_gate": "not_recorded_locally",
    "intentional_promotion_workflow": "not_recorded_locally",
    "claim_surface_remediation": "not_recorded_locally",
    "runtime_plugin_scope_join": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
EXCLUDED_MARKDOWN_DIR_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "runs",
    "venv",
}


@dataclass(frozen=True)
class RoadmapNonGoalMarkdownScanBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapNonGoalMarkdownScanBoundaryValidation:
    ok: bool
    boundary_status: str | None
    markdown_file_count: int
    non_goal_count: int
    forbidden_phrase_count: int
    contradiction_count: int
    missing_evidence_count: int
    issues: list[RoadmapNonGoalMarkdownScanBoundaryIssue]


def roadmap_non_goal_markdown_scan_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the ROADMAP non-goal Markdown corpus contradiction scan."""

    root_path = Path(root)
    source_boundary = roadmap_non_goal_contradiction_boundary_record(root_path)
    markdown_files = _markdown_corpus_files(root_path)
    markdown_texts, read_error_records = _read_markdown_files(
        root_path, markdown_files
    )
    non_goal_records = [
        _non_goal_scan_record(markdown_texts, spec)
        for spec in NON_GOAL_SPECS
    ]
    forbidden_phrase_count = sum(
        len(record["forbidden_claim_phrases"]) for record in non_goal_records
    )
    contradiction_count = sum(
        len(record["detected_forbidden_claim_records"])
        for record in non_goal_records
    )
    return {
        "schema": ROADMAP_NON_GOAL_MARKDOWN_SCAN_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_non_goal_boundary_input": SOURCE_NON_GOAL_BOUNDARY_INPUT,
        "source_non_goal_count": source_boundary["non_goal_count"],
        "source_constrained_surface_count": source_boundary[
            "constrained_surface_count"
        ],
        "markdown_corpus_status": "all_repo_markdown_files_scanned"
        if not read_error_records
        else "markdown_corpus_read_errors_recorded",
        "markdown_file_count": len(markdown_files),
        "readable_markdown_file_count": len(markdown_texts),
        "unreadable_markdown_file_count": len(read_error_records),
        "markdown_files": [str(path.as_posix()) for path in markdown_files],
        "markdown_read_error_records": read_error_records,
        "non_goal_count": len(non_goal_records),
        "forbidden_phrase_count": forbidden_phrase_count,
        "contradiction_count": contradiction_count,
        "non_goal_records": non_goal_records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary scans every Markdown file in the repository corpus "
            "for exact forbidden ROADMAP non-goal support-claim phrases and "
            "retains line-level hit records. It does not claim runtime metadata "
            "scanning, plugin docstring scanning, CI promotion enforcement, an "
            "intentional promotion workflow, joined runtime/plugin/docs/paper "
            "scope proof, or owner-reviewed remediation readiness."
        ),
    }


def validate_roadmap_non_goal_markdown_scan_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapNonGoalMarkdownScanBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_non_goal_markdown_scan_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapNonGoalMarkdownScanBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_non_goal_markdown_scan_boundary_record(root)
    issues: list[RoadmapNonGoalMarkdownScanBoundaryIssue] = []
    if data.get("schema") != ROADMAP_NON_GOAL_MARKDOWN_SCAN_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP non-goal Markdown scan schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "Markdown scan must not claim full non-goal promotion readiness"))
    for key in (
        "source_non_goal_count",
        "source_constrained_surface_count",
        "markdown_corpus_status",
        "markdown_file_count",
        "readable_markdown_file_count",
        "unreadable_markdown_file_count",
        "markdown_files",
        "markdown_read_error_records",
        "non_goal_count",
        "forbidden_phrase_count",
        "contradiction_count",
        "non_goal_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current Markdown corpus scan inputs"))
    if data.get("contradiction_count") != 0:
        issues.append(_issue("contradiction_detected", "forbidden non-goal support claim phrases were detected in Markdown corpus"))
    required_count = _validate_required_fields(
        data.get("required_evidence_fields"), issues
    )
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "every Markdown file in the repository corpus" not in boundary_text
        or "does not claim runtime metadata scanning" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate Markdown corpus scan from full promotion readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapNonGoalMarkdownScanBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        markdown_file_count=data.get("markdown_file_count") if isinstance(data.get("markdown_file_count"), int) else 0,
        non_goal_count=data.get("non_goal_count") if isinstance(data.get("non_goal_count"), int) else 0,
        forbidden_phrase_count=data.get("forbidden_phrase_count") if isinstance(data.get("forbidden_phrase_count"), int) else 0,
        contradiction_count=data.get("contradiction_count") if isinstance(data.get("contradiction_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_non_goal_markdown_scan_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_non_goal_markdown_scan_boundary(boundary)
    rows = [
        ("schema_status", "ok" if validation.ok else "invalid"),
        ("boundary_status", validation.boundary_status or "unknown"),
        ("markdown_file_count", str(validation.markdown_file_count)),
        ("non_goal_count", str(validation.non_goal_count)),
        ("forbidden_phrase_count", str(validation.forbidden_phrase_count)),
        ("contradiction_count", str(validation.contradiction_count)),
        ("missing_evidence_count", str(validation.missing_evidence_count)),
    ]
    lines = ["# ROADMAP non-goal Markdown scan boundary", "", "| Field | Value |", "| --- | --- |"]
    lines.extend(f"| {name} | {value} |" for name, value in rows)
    if validation.issues:
        lines.extend(["", "## Issues"])
        lines.extend(f"- `{issue.code}`: {issue.message}" for issue in validation.issues)
    return "\n".join(lines) + "\n"


def _markdown_corpus_files(root_path: Path) -> list[Path]:
    files: list[Path] = []
    for path in root_path.rglob("*.md"):
        try:
            relative = path.relative_to(root_path)
        except ValueError:
            continue
        if any(
            part in EXCLUDED_MARKDOWN_DIR_PARTS or part.endswith(".egg-info")
            for part in relative.parts
        ):
            continue
        files.append(relative)
    return sorted(files, key=lambda item: item.as_posix())


def _read_markdown_files(
    root_path: Path,
    markdown_files: list[Path],
) -> tuple[dict[Path, str], list[dict[str, Any]]]:
    texts: dict[Path, str] = {}
    read_error_records: list[dict[str, Any]] = []
    for relative_path in markdown_files:
        path = root_path / relative_path
        try:
            texts[relative_path] = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            read_error_records.append(
                {
                    "path": relative_path.as_posix(),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
    return texts, read_error_records


def _non_goal_scan_record(
    markdown_texts: dict[Path, str],
    spec: dict[str, Any],
) -> dict[str, Any]:
    phrases = sorted(
        {
            phrase
            for surface in spec["constrained_surfaces"]
            for phrase in surface["forbidden_claim_phrases"]
        }
    )
    hit_records: list[dict[str, Any]] = []
    for relative_path, text in sorted(
        markdown_texts.items(), key=lambda item: item[0].as_posix()
    ):
        lowered_lines = [line.lower() for line in text.splitlines()]
        for phrase in phrases:
            phrase_lower = phrase.lower()
            for line_number, line in enumerate(lowered_lines, start=1):
                column = line.find(phrase_lower)
                if column == -1:
                    continue
                hit_records.append(
                    {
                        "path": relative_path.as_posix(),
                        "line_start": line_number,
                        "phrase": phrase,
                        "column_start": column + 1,
                    }
                )
    return {
        "non_goal_id": spec["non_goal_id"],
        "roadmap_anchor": spec["roadmap_anchor"],
        "forbidden_claim_phrases": phrases,
        "detected_forbidden_claim_records": hit_records,
        "detected_forbidden_claim_count": len(hit_records),
        "scan_status": "no_forbidden_markdown_claims_detected"
        if not hit_records
        else "forbidden_markdown_claims_detected",
    }


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapNonGoalMarkdownScanBoundaryIssue]]:
    if isinstance(boundary, dict):
        return boundary, []
    if isinstance(boundary, (str, Path)):
        path = Path(boundary)
        try:
            return json.loads(path.read_text(encoding="utf-8")), []
        except OSError as exc:
            return None, [_issue("read_error", f"could not read boundary: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [_issue("json_error", f"could not parse boundary JSON: {exc}")]
    return None, [_issue("invalid_boundary_type", "boundary must be a dict or JSON path")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapNonGoalMarkdownScanBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    for field in EXPECTED_REQUIRED_EVIDENCE_FIELDS:
        if field not in value:
            issues.append(_issue("missing_required_evidence_field", f"missing required evidence field: {field}"))
    return len(value)


def _validate_missing_evidence(
    value: object,
    issues: list[RoadmapNonGoalMarkdownScanBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be a dict"))
        return 0
    for field, expected_status in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(field) != expected_status:
            issues.append(_issue(f"invalid_missing_evidence_{field}", f"missing_evidence[{field!r}] must be {expected_status!r}"))
    unexpected = sorted(set(value) - set(EXPECTED_MISSING_EVIDENCE))
    for field in unexpected:
        issues.append(_issue("unexpected_missing_evidence_field", f"unexpected missing evidence field: {field}"))
    return len(value)


def _issue(
    code: str,
    message: str,
) -> RoadmapNonGoalMarkdownScanBoundaryIssue:
    return RoadmapNonGoalMarkdownScanBoundaryIssue(code=code, message=message)
