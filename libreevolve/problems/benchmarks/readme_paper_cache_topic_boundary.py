from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_PAPER_CACHE_TOPIC_BOUNDARY_SCHEMA = (
    "libreevolve.readme_paper_cache_topic_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "readme_paper_cache_topic_markers_without_row_level_taxonomy"
)
README_PATH = "README.md"
PAPERS_README_PATH = "papers/README.md"
DOWNLOAD_MANIFEST_PATH = "papers/download_manifest.json"
EXPECTED_README_TOPIC_PHRASE = (
    "The local paper cache contains 53 PDFs on LLM-guided evolution, program\n"
    "synthesis, quality-diversity optimization, and related benchmarks."
)
EXPECTED_TOPIC_FAMILIES = (
    "llm_guided_evolution",
    "program_synthesis",
    "quality_diversity",
    "related_benchmarks",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_topic_sentence",
    "readme_manifest_count",
    "download_manifest_rows",
    "papers_status_table_rows",
    "papers_role_inventory",
    "heuristic_topic_family_signals",
    "row_level_topic_taxonomy",
    "topic_taxonomy_reviewer_signoff",
    "topic_phrase_semantic_verifier",
    "new_paper_out_of_scope_detector",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "row_level_topic_taxonomy": "not_recorded_locally",
    "topic_taxonomy_reviewer_signoff": "not_recorded_locally",
    "topic_phrase_semantic_verifier": "not_recorded_locally",
    "new_paper_out_of_scope_detector": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmePaperCacheTopicBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmePaperCacheTopicBoundaryValidation:
    ok: bool
    boundary_status: str | None
    manifest_row_count: int
    status_row_count: int
    topic_family_count: int
    missing_marker_count: int
    missing_evidence_count: int
    issues: list[ReadmePaperCacheTopicBoundaryIssue]


def readme_paper_cache_topic_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the README paper-cache topic boundary record."""

    root_path = Path(root)
    readme_text = _read_text(root_path / README_PATH)
    papers_readme_text = _read_text(root_path / PAPERS_README_PATH)
    manifest_rows = _manifest_rows(root_path / DOWNLOAD_MANIFEST_PATH)
    status_rows = _status_table_rows(papers_readme_text)
    manifest_count = len(manifest_rows)
    status_count = len(status_rows)
    role_counts = Counter(row["role"] for row in status_rows)
    topic_records = _topic_family_records(status_rows)
    missing_topic_families = [
        record
        for record in topic_records
        if record["row_signal_count"] <= 0
    ]
    marker_records = [
        _marker_record(
            "readme_topic_phrase",
            README_PATH,
            readme_text,
            EXPECTED_README_TOPIC_PHRASE,
        ),
        _marker_record(
            "papers_cache_count",
            PAPERS_README_PATH,
            papers_readme_text,
            "contains 53\nlocally cached PDFs",
        ),
        _marker_record(
            "papers_role_status_table",
            PAPERS_README_PATH,
            papers_readme_text,
            "| ID | Title | Role | Current LibreEvolve status |",
        ),
        _marker_record(
            "papers_role_taxonomy_statement",
            PAPERS_README_PATH,
            papers_readme_text,
            "the declared role taxonomy",
        ),
    ]
    missing_marker_records = [
        record for record in marker_records if record["marker_status"] != "marker_present"
    ]
    manifest_status = (
        "manifest_and_status_rows_aligned"
        if manifest_count == status_count and manifest_count > 0
        else "manifest_and_status_rows_misaligned"
    )
    return {
        "schema": README_PAPER_CACHE_TOPIC_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "papers_readme_path": PAPERS_README_PATH,
        "download_manifest_path": DOWNLOAD_MANIFEST_PATH,
        "readme_topic_phrase": EXPECTED_README_TOPIC_PHRASE,
        "manifest_row_count": manifest_count,
        "status_row_count": status_count,
        "manifest_status": manifest_status,
        "status_role_count": len(role_counts),
        "status_role_counts": dict(sorted(role_counts.items())),
        "topic_family_count": len(topic_records),
        "topic_family_records": topic_records,
        "missing_topic_family_count": len(missing_topic_families),
        "missing_topic_family_records": missing_topic_families,
        "marker_record_count": len(marker_records),
        "missing_marker_count": len(missing_marker_records),
        "missing_marker_records": missing_marker_records,
        "marker_records": marker_records,
        "topic_marker_status": (
            "readme_paper_cache_topic_markers_present"
            if not missing_marker_records
            and not missing_topic_families
            and manifest_status == "manifest_and_status_rows_aligned"
            else "readme_paper_cache_topic_markers_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the README paper-cache topic sentence, "
            "download-manifest row count, papers-index implementation-status "
            "row count, papers-index role inventory, and bounded heuristic "
            "topic-family signals for LLM-guided evolution, program synthesis, "
            "quality-diversity optimization, and related benchmarks. It does "
            "not claim a row-level reviewed topic taxonomy, taxonomy reviewer "
            "signoff, semantic verification of the README topic phrase, a "
            "new-paper out-of-scope detector, or owner review signoff."
        ),
    }


def validate_readme_paper_cache_topic_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmePaperCacheTopicBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_paper_cache_topic_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return ReadmePaperCacheTopicBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = readme_paper_cache_topic_boundary_record(root)
    issues: list[ReadmePaperCacheTopicBoundaryIssue] = []
    if data.get("schema") != README_PAPER_CACHE_TOPIC_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README paper-cache topic boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README paper-cache topic boundary must not claim semantic topic proof"))
    for key in (
        "readme_path",
        "papers_readme_path",
        "download_manifest_path",
        "readme_topic_phrase",
        "manifest_row_count",
        "status_row_count",
        "manifest_status",
        "status_role_count",
        "status_role_counts",
        "topic_family_count",
        "topic_family_records",
        "missing_topic_family_count",
        "missing_topic_family_records",
        "marker_record_count",
        "missing_marker_count",
        "missing_marker_records",
        "marker_records",
        "topic_marker_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current paper-cache topic inputs"))
    if data.get("manifest_row_count") != data.get("status_row_count"):
        issues.append(_issue("manifest_status_row_count_mismatch", "manifest and status-table row counts must match"))
    if data.get("manifest_row_count", 0) <= 0:
        issues.append(_issue("missing_manifest_rows", "paper manifest rows must be recorded"))
    if data.get("missing_marker_count") != 0:
        issues.append(_issue("missing_topic_marker", "README paper-cache topic markers are incomplete"))
    if data.get("missing_topic_family_count") != 0:
        issues.append(_issue("missing_topic_family_signal", "all README topic families need at least one bounded signal"))
    if data.get("topic_marker_status") != "readme_paper_cache_topic_markers_present":
        issues.append(_issue("invalid_topic_marker_status", "README paper-cache topic markers must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "README paper-cache topic sentence" not in boundary_text
        or "bounded heuristic topic-family signals" not in boundary_text
        or "does not claim a row-level reviewed topic taxonomy" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate topic markers from reviewed taxonomy proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return ReadmePaperCacheTopicBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        manifest_row_count=data.get("manifest_row_count") if isinstance(data.get("manifest_row_count"), int) else 0,
        status_row_count=data.get("status_row_count") if isinstance(data.get("status_row_count"), int) else 0,
        topic_family_count=data.get("topic_family_count") if isinstance(data.get("topic_family_count"), int) else 0,
        missing_marker_count=data.get("missing_marker_count") if isinstance(data.get("missing_marker_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_paper_cache_topic_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_paper_cache_topic_boundary(boundary)
    lines = [
        "README paper-cache topic boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| manifest_row_count | {validation.manifest_row_count} |",
        f"| status_row_count | {validation.status_row_count} |",
        f"| topic_family_count | {validation.topic_family_count} |",
        f"| missing_marker_count | {validation.missing_marker_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _manifest_rows(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]


def _status_table_rows(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    in_table = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("| ID | Title | Role | Current LibreEvolve status |"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table:
            if not line.startswith("|"):
                break
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) != 4:
                continue
            rows.append(
                {
                    "line": line_number,
                    "id": cells[0],
                    "title": cells[1],
                    "role": cells[2],
                    "status_preview": cells[3][:160],
                }
            )
    return rows


def _topic_family_records(status_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for family in EXPECTED_TOPIC_FAMILIES:
        signals = []
        for row in status_rows:
            haystack = " ".join(
                str(row.get(key, ""))
                for key in ("title", "role", "status_preview")
            ).lower()
            if _topic_family_matches(family, haystack):
                signals.append(
                    {
                        "id": row["id"],
                        "line": row["line"],
                        "role": row["role"],
                    }
                )
        records.append(
            {
                "topic_family": family,
                "classification_method": "bounded_keyword_signal_not_reviewed_taxonomy",
                "row_signal_count": len(signals),
                "row_signal_records": signals[:12],
            }
        )
    return records


def _topic_family_matches(family: str, text: str) -> bool:
    if family == "llm_guided_evolution":
        return any(term in text for term in ("evolve", "evolution", "alphaevolve", "llm", "agent"))
    if family == "program_synthesis":
        return any(term in text for term in ("program", "code", "compiler", "kernel", "verilog", "symbolic", "function"))
    if family == "quality_diversity":
        return any(term in text for term in ("map-elites", "quality-diversity", "archive", "diversity", "illumination"))
    if family == "related_benchmarks":
        return any(term in text for term in ("benchmark", "application context", "candidate", "source boundary", "framework context"))
    return False


def _marker_record(kind: str, path: str, text: str, marker: str) -> dict[str, Any]:
    return {
        "record_kind": kind,
        "path": path,
        "required_marker": marker,
        "marker_status": "marker_present" if marker in text else "marker_missing",
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ReadmePaperCacheTopicBoundaryIssue]]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")]
    else:
        try:
            data = json.loads(Path(boundary).read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")]
    if isinstance(data, dict):
        return data, []
    return None, [_issue("invalid_shape", "README paper-cache topic boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmePaperCacheTopicBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_required_evidence_field", f"missing required evidence fields: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_required_evidence_field", f"unknown required evidence fields: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[ReadmePaperCacheTopicBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_missing_evidence_key", f"missing_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_missing_evidence_key", f"missing_evidence has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _issue(code: str, message: str) -> ReadmePaperCacheTopicBoundaryIssue:
    return ReadmePaperCacheTopicBoundaryIssue(code, message)
