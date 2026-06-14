from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_CURRENT_VERSION_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_current_version_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_VERSION_ID = "2506.13131v1"
EXPECTED_CURRENT_ABS_URL = "https://arxiv.org/abs/2506.13131"
EXPECTED_FLOATING_PDF_URL = "https://arxiv.org/pdf/2506.13131.pdf"
EXPECTED_RETRIEVED_ON = "2026-06-14"
EXPECTED_CURRENT_ABS_STATUS = 200
EXPECTED_CURRENT_ABS_CONTENT_TYPE = "text/html; charset=utf-8"
EXPECTED_CURRENT_ABS_BYTES = 49939
EXPECTED_CURRENT_ABS_SHA256 = (
    "707d6aa982e50eca955e6cf7f4a86d2bce2ca6cea543827fea22537ef68d87bb"
)
EXPECTED_CURRENT_ABS_TITLE = (
    "[2506.13131] AlphaEvolve: A coding agent for scientific and algorithmic discovery"
)
EXPECTED_CURRENT_VERSION = 1
EXPECTED_FLOATING_PDF_STATUS = 200
EXPECTED_FLOATING_PDF_CONTENT_TYPE = "application/pdf"
EXPECTED_FLOATING_PDF_BYTES = 3525764
EXPECTED_FLOATING_PDF_SHA256 = (
    "f092c8cbd65da89951ee6496374da9a54963f9035758c25ac6e4625f506df9ad"
)
EXPECTED_FLOATING_PDF_ARTIFACT_PATH = "papers/2506.13131__AlphaEvolve.pdf"
EXPECTED_BOUNDARY_STATUS = (
    "current_v1_and_floating_pdf_retained_without_refresh_gate"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "current_abs_url",
    "retrieved_on",
    "current_abs_http_status",
    "current_abs_content_type",
    "current_abs_response_bytes",
    "current_abs_sha256",
    "current_abs_title",
    "resolved_current_version",
    "expected_source_version_id",
    "floating_pdf_url",
    "floating_pdf_http_status",
    "floating_pdf_content_type",
    "floating_pdf_response_bytes",
    "floating_pdf_sha256",
    "floating_pdf_artifact_path",
    "floating_pdf_artifact_retained",
    "floating_pdf_artifact_bytes",
    "floating_pdf_artifact_sha256",
    "cached_pdf_response_bytes",
    "cached_pdf_sha256",
    "floating_pdf_matches_cached_pdf",
    "raw_http_headers",
    "full_current_abs_html_artifact",
    "full_floating_pdf_response_artifact",
    "automated_current_version_refresh_gate",
    "cached_pdf_header_text_consistency",
)
EXPECTED_MISSING_EVIDENCE = {
    "full_current_abs_html_artifact": "not_recorded_locally",
    "automated_current_version_refresh_gate": "not_recorded_locally",
    "cached_pdf_header_text_consistency": "not_recorded_locally",
}


@dataclass(frozen=True)
class AlphaEvolveCurrentVersionBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveCurrentVersionBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveCurrentVersionBoundaryIssue]


def alphaevolve_current_version_boundary_record() -> dict[str, Any]:
    """Return current-version and floating-PDF digest evidence for AlphaEvolve."""

    return {
        "schema": ALPHAEVOLVE_CURRENT_VERSION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve source metadata should distinguish the floating arXiv "
            "abstract/PDF URLs from the cached versioned PDF evidence."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "current_abs_snapshot": {
            "url": EXPECTED_CURRENT_ABS_URL,
            "retrieved_on": EXPECTED_RETRIEVED_ON,
            "http_status": EXPECTED_CURRENT_ABS_STATUS,
            "content_type": EXPECTED_CURRENT_ABS_CONTENT_TYPE,
            "response_bytes": EXPECTED_CURRENT_ABS_BYTES,
            "response_sha256": EXPECTED_CURRENT_ABS_SHA256,
            "title": EXPECTED_CURRENT_ABS_TITLE,
            "resolved_current_version": EXPECTED_CURRENT_VERSION,
            "expected_source_version_id": EXPECTED_SOURCE_VERSION_ID,
        },
        "floating_pdf_snapshot": {
            "url": EXPECTED_FLOATING_PDF_URL,
            "retrieved_on": EXPECTED_RETRIEVED_ON,
            "http_status": EXPECTED_FLOATING_PDF_STATUS,
            "content_type": EXPECTED_FLOATING_PDF_CONTENT_TYPE,
            "response_bytes": EXPECTED_FLOATING_PDF_BYTES,
            "response_sha256": EXPECTED_FLOATING_PDF_SHA256,
            "artifact_path": EXPECTED_FLOATING_PDF_ARTIFACT_PATH,
            "artifact_retained": True,
            "artifact_bytes": EXPECTED_FLOATING_PDF_BYTES,
            "artifact_sha256": EXPECTED_FLOATING_PDF_SHA256,
            "cached_pdf_response_bytes": EXPECTED_FLOATING_PDF_BYTES,
            "cached_pdf_sha256": EXPECTED_FLOATING_PDF_SHA256,
            "floating_pdf_matches_cached_pdf": True,
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that the floating arXiv abstract URL still "
            "resolves to version 1 and that the retained floating PDF response "
            "artifact matches the cached PDF, and is paired with the raw HTTP "
            "headers sidecar. It "
            "does not claim full current-abstract HTML retention, full "
            "floating-abstract HTML retention, an automated current-version "
            "refresh gate, or cached PDF header text consistency."
        ),
    }


def validate_alphaevolve_current_version_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveCurrentVersionBoundaryValidation:
    data, read_issues, base_dir = _load_boundary(
        alphaevolve_current_version_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return AlphaEvolveCurrentVersionBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveCurrentVersionBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_CURRENT_VERSION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported current-version boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "floating arXiv" not in source_claim
        or "cached versioned PDF" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must separate floating arXiv URLs from cached versioned PDF evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "current-version boundary must not claim automated refresh readiness"))
    _validate_current_abs_snapshot(data.get("current_abs_snapshot"), issues)
    _validate_floating_pdf_snapshot(data.get("floating_pdf_snapshot"), issues)
    if base_dir is not None:
        _validate_retained_floating_pdf_file(data.get("floating_pdf_snapshot"), base_dir, issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "raw HTTP headers sidecar" not in boundary_text
        or "retained floating PDF response artifact" not in boundary_text
        or "automated current-version refresh gate" not in boundary_text
        or "cached PDF header text consistency" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate digest evidence from full refresh/header evidence"))
    return AlphaEvolveCurrentVersionBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_current_version_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_current_version_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve current-version boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _validate_current_abs_snapshot(
    value: object,
    issues: list[AlphaEvolveCurrentVersionBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_current_abs_snapshot", "current_abs_snapshot must be an object"))
        return
    expected = {
        "url": EXPECTED_CURRENT_ABS_URL,
        "retrieved_on": EXPECTED_RETRIEVED_ON,
        "http_status": EXPECTED_CURRENT_ABS_STATUS,
        "content_type": EXPECTED_CURRENT_ABS_CONTENT_TYPE,
        "response_bytes": EXPECTED_CURRENT_ABS_BYTES,
        "response_sha256": EXPECTED_CURRENT_ABS_SHA256,
        "title": EXPECTED_CURRENT_ABS_TITLE,
        "resolved_current_version": EXPECTED_CURRENT_VERSION,
        "expected_source_version_id": EXPECTED_SOURCE_VERSION_ID,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_current_abs_{key}", f"current_abs_snapshot.{key} must be {expected_value}"))


def _validate_floating_pdf_snapshot(
    value: object,
    issues: list[AlphaEvolveCurrentVersionBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_floating_pdf_snapshot", "floating_pdf_snapshot must be an object"))
        return
    expected = {
        "url": EXPECTED_FLOATING_PDF_URL,
        "retrieved_on": EXPECTED_RETRIEVED_ON,
        "http_status": EXPECTED_FLOATING_PDF_STATUS,
        "content_type": EXPECTED_FLOATING_PDF_CONTENT_TYPE,
        "response_bytes": EXPECTED_FLOATING_PDF_BYTES,
        "response_sha256": EXPECTED_FLOATING_PDF_SHA256,
        "artifact_path": EXPECTED_FLOATING_PDF_ARTIFACT_PATH,
        "artifact_retained": True,
        "artifact_bytes": EXPECTED_FLOATING_PDF_BYTES,
        "artifact_sha256": EXPECTED_FLOATING_PDF_SHA256,
        "cached_pdf_response_bytes": EXPECTED_FLOATING_PDF_BYTES,
        "cached_pdf_sha256": EXPECTED_FLOATING_PDF_SHA256,
        "floating_pdf_matches_cached_pdf": True,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_floating_pdf_{key}", f"floating_pdf_snapshot.{key} must be {expected_value}"))


def _validate_retained_floating_pdf_file(
    value: object,
    base_dir: Path,
    issues: list[AlphaEvolveCurrentVersionBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        return
    artifact_value = value.get("artifact_path")
    if not isinstance(artifact_value, str):
        return
    artifact_path = base_dir / artifact_value
    try:
        pdf_bytes = artifact_path.read_bytes()
    except OSError as exc:
        issues.append(_issue("missing_floating_pdf_artifact", f"floating PDF artifact could not be read: {exc}"))
        return
    if len(pdf_bytes) != EXPECTED_FLOATING_PDF_BYTES:
        issues.append(_issue("invalid_floating_pdf_artifact_bytes", f"floating PDF artifact must be {EXPECTED_FLOATING_PDF_BYTES} bytes"))
    digest = hashlib.sha256(pdf_bytes).hexdigest()
    if digest != EXPECTED_FLOATING_PDF_SHA256:
        issues.append(_issue("invalid_floating_pdf_artifact_sha256", f"floating PDF artifact SHA-256 must be {EXPECTED_FLOATING_PDF_SHA256}"))
    if not pdf_bytes.startswith(b"%PDF"):
        issues.append(_issue("invalid_floating_pdf_artifact_magic", "floating PDF artifact must start with a PDF header"))


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveCurrentVersionBoundaryIssue], Path | None]:
    if isinstance(boundary, dict):
        return dict(boundary), [], None
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")], None
        base_dir = None
    else:
        path = Path(boundary)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")], None
        base_dir = path.parent.parent
    if isinstance(data, dict):
        return data, [], base_dir
    return None, [_issue("invalid_shape", "current-version boundary must be a JSON object")], None


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveCurrentVersionBoundaryIssue],
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
    issues: list[AlphaEvolveCurrentVersionBoundaryIssue],
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


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveCurrentVersionBoundaryIssue:
    return AlphaEvolveCurrentVersionBoundaryIssue(code, message)
