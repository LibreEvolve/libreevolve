from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_ARXIV_ABSTRACT_SNAPSHOT_SCHEMA = (
    "libreevolve.alphaevolve_arxiv_abstract_snapshot.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_VERSIONED_ID = "2506.13131v1"
EXPECTED_ABSTRACT_URL = "https://arxiv.org/abs/2506.13131v1"
EXPECTED_FINAL_URL = EXPECTED_ABSTRACT_URL
EXPECTED_CONTENT_TYPE = "text/html; charset=utf-8"
EXPECTED_HTML_BYTES = 50098
EXPECTED_HTML_SHA256 = (
    "ab39ec118afe0874f34179b5a06c42a57799b1103f027942a1ecd54dc3d95471"
)
EXPECTED_RETRIEVED_AT_UTC = "2026-06-13T20:42:36Z"
EXPECTED_TITLE = "AlphaEvolve: A coding agent for scientific and algorithmic discovery"
EXPECTED_AUTHORS = (
    "Alexander Novikov",
    "Ng\u00e2n V\u0169",
    "Marvin Eisenberger",
    "Emilien Dupont",
    "Po-Sen Huang",
    "Adam Zsolt Wagner",
    "Sergey Shirobokov",
    "Borislav Kozlovskii",
    "Francisco J. R. Ruiz",
    "Abbas Mehrabian",
    "M. Pawan Kumar",
    "Abigail See",
    "Swarat Chaudhuri",
    "George Holland",
    "Alex Davies",
    "Sebastian Nowozin",
    "Pushmeet Kohli",
    "Matej Balog",
)
EXPECTED_SUBJECTS = ("cs.AI", "cs.LG", "cs.NE")
EXPECTED_SUBJECTS_TEXT = (
    "Artificial Intelligence (cs.AI) ; Machine Learning (cs.LG); "
    "Neural and Evolutionary Computing (cs.NE)"
)
EXPECTED_DOI = "10.48550/arXiv.2506.13131"
EXPECTED_DOI_URL = "https://doi.org/10.48550/arXiv.2506.13131"
EXPECTED_SUBMITTED_DATE = "16 Jun 2025"
EXPECTED_SUBMITTED_TIMESTAMP_UTC = "2025-06-16T06:37:18Z"
EXPECTED_TEX_SOURCE_URL = "https://arxiv.org/src/2506.13131v1"
EXPECTED_LICENSE_HREF = "http://creativecommons.org/licenses/by-nc-nd/4.0/"
EXPECTED_NORMALIZED_LICENSE_URL = "https://creativecommons.org/licenses/by-nc-nd/4.0/"
EXPECTED_HISTORY = (
    {
        "version": "v1",
        "timestamp_utc": EXPECTED_SUBMITTED_TIMESTAMP_UTC,
        "size_label": "2,574 KB",
    },
)
EXPECTED_MISSING_EVIDENCE = {
    "full_html_artifact_committed": "not_recorded_locally",
    "datacite_doi_resolution_snapshot": "not_recorded_locally",
    "tex_source_archive_digest": "not_recorded_locally",
    "license_page_snapshot": "not_recorded_locally",
    "automated_live_refresh_ci_gate": "not_recorded_locally",
}


@dataclass(frozen=True)
class AlphaEvolveArxivAbstractSnapshotIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveArxivAbstractSnapshotValidation:
    ok: bool
    metadata_checked: bool
    live_refresh_checked: bool
    author_count: int
    subject_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveArxivAbstractSnapshotIssue]


def alphaevolve_arxiv_abstract_snapshot_record() -> dict[str, Any]:
    """Return the pinned arXiv abstract-page metadata snapshot boundary."""

    return {
        "schema": ALPHAEVOLVE_ARXIV_ABSTRACT_SNAPSHOT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_version_id": EXPECTED_VERSIONED_ID,
        "abstract_url": EXPECTED_ABSTRACT_URL,
        "retrieved_at_utc": EXPECTED_RETRIEVED_AT_UTC,
        "retrieval_method": "urllib_request_user_agent_metadata_audit",
        "html_snapshot": {
            "final_url": EXPECTED_FINAL_URL,
            "content_type": EXPECTED_CONTENT_TYPE,
            "bytes": EXPECTED_HTML_BYTES,
            "sha256": EXPECTED_HTML_SHA256,
            "full_html_committed": False,
        },
        "normalized_metadata": {
            "title": EXPECTED_TITLE,
            "authors": list(EXPECTED_AUTHORS),
            "author_count": len(EXPECTED_AUTHORS),
            "subjects_text": EXPECTED_SUBJECTS_TEXT,
            "subject_codes": list(EXPECTED_SUBJECTS),
            "doi": EXPECTED_DOI,
            "doi_url": EXPECTED_DOI_URL,
            "submitted_date": EXPECTED_SUBMITTED_DATE,
            "submitted_timestamp_utc": EXPECTED_SUBMITTED_TIMESTAMP_UTC,
            "tex_source_url": EXPECTED_TEX_SOURCE_URL,
            "license_href": EXPECTED_LICENSE_HREF,
            "normalized_license_url": EXPECTED_NORMALIZED_LICENSE_URL,
            "submission_history": list(EXPECTED_HISTORY),
        },
        "source_version_boundary_link": {
            "source_versions_file": "papers/source_versions.json",
            "expected_abstract_page_metadata_status": (
                "manual_current_as_of_2026-06-13_without_html_snapshot"
            ),
            "updates_manual_metadata_with_html_digest": True,
        },
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "refresh_gate": {
            "live_refresh_supported_by_validator": True,
            "manifest_validation_uses_committed_snapshot_only": True,
            "live_snapshot_input_required_for_network_refresh": True,
            "drift_policy": "fail_if_live_html_digest_or_normalized_metadata_differs",
        },
        "claim_boundary": (
            "This boundary records an arXiv abstract-page HTML byte count, "
            "SHA-256 digest, and normalized source metadata for AlphaEvolve "
            "2506.13131v1. It does not commit the full HTML body, resolve "
            "DataCite DOI metadata, cache the TeX source archive, cache the "
            "license page, or install an automated live-refresh CI gate."
        ),
    }


def validate_alphaevolve_arxiv_abstract_snapshot(
    snapshot: object | str | Path | None = None,
    *,
    live_snapshot: dict[str, Any] | None = None,
) -> AlphaEvolveArxivAbstractSnapshotValidation:
    data, read_issues = _load_snapshot(
        alphaevolve_arxiv_abstract_snapshot_record() if snapshot is None else snapshot
    )
    if read_issues:
        return AlphaEvolveArxivAbstractSnapshotValidation(False, False, False, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveArxivAbstractSnapshotIssue] = []
    if data.get("schema") != ALPHAEVOLVE_ARXIV_ABSTRACT_SNAPSHOT_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported AlphaEvolve arXiv abstract snapshot schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_version_id") != EXPECTED_VERSIONED_ID:
        issues.append(_issue("invalid_source_version_id", "source_version_id must be 2506.13131v1"))
    if data.get("abstract_url") != EXPECTED_ABSTRACT_URL:
        issues.append(_issue("invalid_abstract_url", "abstract_url must be the pinned v1 arXiv abstract URL"))
    if data.get("retrieved_at_utc") != EXPECTED_RETRIEVED_AT_UTC:
        issues.append(_issue("invalid_retrieved_at_utc", "retrieved_at_utc must match the pinned audit timestamp"))
    if data.get("retrieval_method") != "urllib_request_user_agent_metadata_audit":
        issues.append(_issue("invalid_retrieval_method", "retrieval_method must identify the bounded metadata audit fetch"))
    _validate_html_snapshot(data.get("html_snapshot"), issues)
    author_count, subject_count = _validate_normalized_metadata(data.get("normalized_metadata"), issues)
    _validate_source_version_boundary_link(data.get("source_version_boundary_link"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    _validate_refresh_gate(data.get("refresh_gate"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not commit the full HTML body" not in boundary_text
        or "DataCite DOI metadata" not in boundary_text
        or "automated live-refresh CI gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate the HTML digest snapshot from uncached source artifacts"))
    live_checked = live_snapshot is not None
    if live_snapshot is not None:
        _validate_live_snapshot(data, live_snapshot, issues)
    return AlphaEvolveArxivAbstractSnapshotValidation(
        ok=not issues,
        metadata_checked=True,
        live_refresh_checked=live_checked,
        author_count=author_count,
        subject_count=subject_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_arxiv_abstract_snapshot_summary(
    snapshot: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_arxiv_abstract_snapshot(snapshot)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve arXiv abstract snapshot",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| metadata_checked | {validation.metadata_checked} |",
        f"| live_refresh_checked | {validation.live_refresh_checked} |",
        f"| author_count | {validation.author_count} |",
        f"| subject_count | {validation.subject_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_snapshot(
    snapshot: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveArxivAbstractSnapshotIssue]]:
    if isinstance(snapshot, dict):
        return dict(snapshot), []
    if isinstance(snapshot, str) and snapshot.strip().startswith("{"):
        try:
            data = json.loads(snapshot)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"snapshot JSON is invalid: {exc}")]
    else:
        try:
            data = json.loads(Path(snapshot).read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_snapshot", f"snapshot could not be loaded: {exc}")]
    if isinstance(data, dict):
        return data, []
    return None, [_issue("invalid_shape", "arXiv abstract snapshot must be a JSON object")]


def _validate_html_snapshot(
    value: object,
    issues: list[AlphaEvolveArxivAbstractSnapshotIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_html_snapshot", "html_snapshot must be an object"))
        return
    expected = {
        "final_url": EXPECTED_FINAL_URL,
        "content_type": EXPECTED_CONTENT_TYPE,
        "bytes": EXPECTED_HTML_BYTES,
        "sha256": EXPECTED_HTML_SHA256,
        "full_html_committed": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_html_snapshot_{field}", f"html_snapshot.{field} must match the pinned arXiv fetch"))


def _validate_normalized_metadata(
    value: object,
    issues: list[AlphaEvolveArxivAbstractSnapshotIssue],
) -> tuple[int, int]:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_normalized_metadata", "normalized_metadata must be an object"))
        return 0, 0
    expected = {
        "title": EXPECTED_TITLE,
        "authors": list(EXPECTED_AUTHORS),
        "author_count": len(EXPECTED_AUTHORS),
        "subjects_text": EXPECTED_SUBJECTS_TEXT,
        "subject_codes": list(EXPECTED_SUBJECTS),
        "doi": EXPECTED_DOI,
        "doi_url": EXPECTED_DOI_URL,
        "submitted_date": EXPECTED_SUBMITTED_DATE,
        "submitted_timestamp_utc": EXPECTED_SUBMITTED_TIMESTAMP_UTC,
        "tex_source_url": EXPECTED_TEX_SOURCE_URL,
        "license_href": EXPECTED_LICENSE_HREF,
        "normalized_license_url": EXPECTED_NORMALIZED_LICENSE_URL,
        "submission_history": list(EXPECTED_HISTORY),
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_metadata_{field}", f"normalized_metadata.{field} must match the pinned arXiv abstract metadata"))
    authors = value.get("authors")
    subjects = value.get("subject_codes")
    return (
        len(authors) if isinstance(authors, list) else 0,
        len(subjects) if isinstance(subjects, list) else 0,
    )


def _validate_source_version_boundary_link(
    value: object,
    issues: list[AlphaEvolveArxivAbstractSnapshotIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_source_version_boundary_link", "source_version_boundary_link must be an object"))
        return
    expected = {
        "source_versions_file": "papers/source_versions.json",
        "expected_abstract_page_metadata_status": "manual_current_as_of_2026-06-13_without_html_snapshot",
        "updates_manual_metadata_with_html_digest": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_source_version_boundary_link_{field}", f"source_version_boundary_link.{field} must match the source-version boundary"))


def _validate_missing_evidence(
    value: object,
    issues: list[AlphaEvolveArxivAbstractSnapshotIssue],
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


def _validate_refresh_gate(
    value: object,
    issues: list[AlphaEvolveArxivAbstractSnapshotIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_refresh_gate", "refresh_gate must be an object"))
        return
    expected = {
        "live_refresh_supported_by_validator": True,
        "manifest_validation_uses_committed_snapshot_only": True,
        "live_snapshot_input_required_for_network_refresh": True,
        "drift_policy": "fail_if_live_html_digest_or_normalized_metadata_differs",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_refresh_gate_{field}", f"refresh_gate.{field} must preserve the arXiv refresh policy"))


def _validate_live_snapshot(
    committed: dict[str, Any],
    live_snapshot: dict[str, Any],
    issues: list[AlphaEvolveArxivAbstractSnapshotIssue],
) -> None:
    for field in ("html_snapshot", "normalized_metadata"):
        if live_snapshot.get(field) != committed.get(field):
            issues.append(_issue(f"live_{field}_drift", f"live {field} must match the committed arXiv abstract snapshot"))


def _issue(code: str, message: str) -> AlphaEvolveArxivAbstractSnapshotIssue:
    return AlphaEvolveArxivAbstractSnapshotIssue(code, message)
