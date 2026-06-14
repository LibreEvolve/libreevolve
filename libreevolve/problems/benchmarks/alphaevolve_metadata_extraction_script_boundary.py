from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.tools.alphaevolve_source_metadata import (
    build_alphaevolve_source_metadata_report,
)


ALPHAEVOLVE_METADATA_EXTRACTION_SCRIPT_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_metadata_extraction_script_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_VERSION_ID = "2506.13131v1"
EXPECTED_SCRIPT_PATH = "libreevolve/tools/alphaevolve_source_metadata.py"
EXPECTED_SCRIPT_BYTES = 7272
EXPECTED_SCRIPT_SHA256 = (
    "7c9aa25e86c60d62187d9fc86d8010b482d85b6c329e8765ed2e7b992a4badf5"
)
EXPECTED_BOUNDARY_STATUS = (
    "offline_metadata_extraction_script_recorded_without_refresh_gate"
)
EXPECTED_ARTIFACTS = {
    "arxiv_abstract_html": "papers/arxiv_abstract_2506.13131v1.html",
    "cached_pdf_first_page": "papers/2506.13131__AlphaEvolve.pdf",
    "datacite_full_response": "papers/alphaevolve_datacite_full_response_boundary.json",
    "license_page_html": "papers/alphaevolve_license_page.html",
    "tex_archive": "papers/alphaevolve_tex_source_archive.tar.gz",
}
EXPECTED_MISSING_EVIDENCE = {
    "automated_live_refresh_ci_gate": "not_recorded_locally",
}


@dataclass(frozen=True)
class AlphaEvolveMetadataExtractionScriptBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveMetadataExtractionScriptBoundaryValidation:
    ok: bool
    boundary_status: str | None
    script_artifact_checked: bool
    extraction_report_checked: bool
    artifact_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveMetadataExtractionScriptBoundaryIssue]


def alphaevolve_metadata_extraction_script_boundary_record() -> dict[str, Any]:
    """Return the AlphaEvolve offline metadata extraction-script boundary."""

    return {
        "schema": ALPHAEVOLVE_METADATA_EXTRACTION_SCRIPT_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_version_id": EXPECTED_SOURCE_VERSION_ID,
        "source_claim": (
            "AlphaEvolve source metadata should have a reusable local script "
            "artifact that extracts retained source evidence without network "
            "access."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "script_artifact": {
            "path": EXPECTED_SCRIPT_PATH,
            "bytes": EXPECTED_SCRIPT_BYTES,
            "sha256": EXPECTED_SCRIPT_SHA256,
            "entrypoint": "build_alphaevolve_source_metadata_report",
            "cli": "py -3.12 -m libreevolve.tools.alphaevolve_source_metadata --root .",
        },
        "supported_artifacts": dict(EXPECTED_ARTIFACTS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a reusable offline metadata extraction-script "
            "artifact for retained AlphaEvolve source files. It does not fetch "
            "live arXiv, DataCite, DOI, license, or e-print sources and does "
            "not install an automated live refresh CI gate."
        ),
    }


def validate_alphaevolve_metadata_extraction_script_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveMetadataExtractionScriptBoundaryValidation:
    data, read_issues, base_dir = _load_boundary(
        alphaevolve_metadata_extraction_script_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveMetadataExtractionScriptBoundaryValidation(
            False, None, False, False, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveMetadataExtractionScriptBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_METADATA_EXTRACTION_SCRIPT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported metadata extraction-script boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_version_id") != EXPECTED_SOURCE_VERSION_ID:
        issues.append(_issue("invalid_source_version_id", "source_version_id must be 2506.13131v1"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "reusable local script artifact" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must describe the reusable local script artifact"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "metadata extraction script boundary must not claim refresh readiness"))
    _validate_script_artifact(data.get("script_artifact"), issues)
    artifact_count = _validate_supported_artifacts(data.get("supported_artifacts"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "offline metadata extraction-script artifact" not in boundary_text
        or "does not fetch live" not in boundary_text
        or "automated live refresh CI gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate offline extraction from live refresh"))
    script_checked = False
    report_checked = False
    if base_dir is not None:
        script_checked = _validate_script_file(base_dir, issues)
        report_checked = _validate_extraction_report(base_dir, issues)
    return AlphaEvolveMetadataExtractionScriptBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        script_artifact_checked=script_checked,
        extraction_report_checked=report_checked,
        artifact_count=artifact_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_metadata_extraction_script_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_metadata_extraction_script_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve metadata extraction-script boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| script_artifact_checked | {validation.script_artifact_checked} |",
        f"| extraction_report_checked | {validation.extraction_report_checked} |",
        f"| artifact_count | {validation.artifact_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _validate_script_artifact(
    value: object,
    issues: list[AlphaEvolveMetadataExtractionScriptBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_script_artifact", "script_artifact must be an object"))
        return
    expected = {
        "path": EXPECTED_SCRIPT_PATH,
        "bytes": EXPECTED_SCRIPT_BYTES,
        "sha256": EXPECTED_SCRIPT_SHA256,
        "entrypoint": "build_alphaevolve_source_metadata_report",
        "cli": "py -3.12 -m libreevolve.tools.alphaevolve_source_metadata --root .",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_script_artifact_{field}", f"script_artifact.{field} must be {expected_value}"))


def _validate_supported_artifacts(
    value: object,
    issues: list[AlphaEvolveMetadataExtractionScriptBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_supported_artifacts", "supported_artifacts must be an object"))
        return 0
    if value != EXPECTED_ARTIFACTS:
        issues.append(_issue("invalid_supported_artifacts", "supported_artifacts must list the retained AlphaEvolve source artifacts"))
    return len(value)


def _validate_missing_evidence(
    value: object,
    issues: list[AlphaEvolveMetadataExtractionScriptBoundaryIssue],
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


def _validate_script_file(
    base_dir: Path,
    issues: list[AlphaEvolveMetadataExtractionScriptBoundaryIssue],
) -> bool:
    path = base_dir / EXPECTED_SCRIPT_PATH
    try:
        data = path.read_bytes()
    except OSError as exc:
        issues.append(_issue("unreadable_script_artifact_file", f"script artifact file could not be read: {exc}"))
        return False
    if len(data) != EXPECTED_SCRIPT_BYTES:
        issues.append(_issue("invalid_script_artifact_file_bytes", f"script artifact file must be {EXPECTED_SCRIPT_BYTES} bytes"))
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SCRIPT_SHA256:
        issues.append(_issue("invalid_script_artifact_file_sha256", f"script artifact file SHA-256 must be {EXPECTED_SCRIPT_SHA256}"))
    return True


def _validate_extraction_report(
    base_dir: Path,
    issues: list[AlphaEvolveMetadataExtractionScriptBoundaryIssue],
) -> bool:
    report = build_alphaevolve_source_metadata_report(base_dir)
    if report.get("schema") != "libreevolve.alphaevolve_source_metadata_extraction.v1":
        issues.append(_issue("invalid_extraction_report_schema", "extraction report schema is incorrect"))
    if report.get("ok") is not True:
        issues.append(_issue("invalid_extraction_report_status", "extraction report must be ok"))
    if report.get("artifact_count") != len(EXPECTED_ARTIFACTS):
        issues.append(_issue("invalid_extraction_report_artifact_count", "extraction report must cover all retained artifacts"))
    script = report.get("script_artifact")
    if not isinstance(script, dict) or script.get("sha256") != EXPECTED_SCRIPT_SHA256:
        issues.append(_issue("invalid_extraction_report_script_sha256", "extraction report must identify the pinned script SHA-256"))
    artifacts = report.get("artifacts")
    if not isinstance(artifacts, dict):
        issues.append(_issue("invalid_extraction_report_artifacts", "extraction report artifacts must be an object"))
        return False
    for artifact_id, artifact_path in EXPECTED_ARTIFACTS.items():
        artifact = artifacts.get(artifact_id)
        if not isinstance(artifact, dict) or artifact.get("path") != artifact_path or artifact.get("ok") is not True:
            issues.append(_issue(f"invalid_extraction_report_{artifact_id}", f"extraction report must validate {artifact_path}"))
    return True


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveMetadataExtractionScriptBoundaryIssue], Path | None]:
    base_dir: Path | None = None
    if isinstance(boundary, dict):
        return dict(boundary), [], None
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")], None
    else:
        try:
            path = Path(boundary)
            data = json.loads(path.read_text(encoding="utf-8"))
            base_dir = path.parent.parent
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")], None
    if isinstance(data, dict):
        return data, [], base_dir
    return None, [_issue("invalid_shape", "metadata extraction-script boundary must be a JSON object")], base_dir


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveMetadataExtractionScriptBoundaryIssue:
    return AlphaEvolveMetadataExtractionScriptBoundaryIssue(code, message)
