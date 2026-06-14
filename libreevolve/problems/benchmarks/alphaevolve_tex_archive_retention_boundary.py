from __future__ import annotations

import hashlib
import io
import json
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_TEX_ARCHIVE_RETENTION_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_tex_archive_retention_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_EPRINT_URL = "https://arxiv.org/e-print/2506.13131"
EXPECTED_RETRIEVED_AT_UTC = "2026-06-14T02:53:10Z"
EXPECTED_RESPONSE_BYTES = 2635462
EXPECTED_RESPONSE_SHA256 = (
    "a3ea37c5b6fe967fba459f0daca8548a78e2a1eac45e5c2aac83051ef113f21d"
)
EXPECTED_BOUNDARY_STATUS = "tex_archive_retained_with_member_inventory_without_refresh_gate"
EXPECTED_ARCHIVE_ARTIFACT_PATH = "papers/alphaevolve_tex_source_archive.tar.gz"
EXPECTED_MEMBER_COUNT = 58
EXPECTED_FILE_COUNT = 54
EXPECTED_DIR_COUNT = 4
EXPECTED_TOTAL_UNCOMPRESSED_FILE_BYTES = 3026002
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "eprint_url",
    "retrieved_at_utc",
    "http_status",
    "content_type",
    "content_disposition",
    "response_bytes",
    "response_sha256",
    "archive_artifact_path",
    "archive_artifact_retained",
    "archive_artifact_bytes",
    "archive_artifact_sha256",
    "arxiv_versioned_id",
    "archive_member_inventory",
    "extraction_script_artifact",
    "tex_source_refresh_gate",
    "cached_pdf_header_consistency",
)
EXPECTED_MISSING_EVIDENCE = {
    "extraction_script_artifact": "not_recorded_locally",
    "tex_source_refresh_gate": "not_recorded_locally",
    "cached_pdf_header_consistency": "not_recorded_locally",
}


@dataclass(frozen=True)
class AlphaEvolveTexArchiveRetentionBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveTexArchiveRetentionBoundaryValidation:
    ok: bool
    boundary_status: str | None
    archive_artifact_retained: bool
    member_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveTexArchiveRetentionBoundaryIssue]


def alphaevolve_tex_archive_retention_boundary_record() -> dict[str, Any]:
    """Return the committed AlphaEvolve TeX archive retention evidence."""

    return _load_committed_record()


def validate_alphaevolve_tex_archive_retention_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveTexArchiveRetentionBoundaryValidation:
    data, read_issues, base_dir = _load_boundary(
        alphaevolve_tex_archive_retention_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveTexArchiveRetentionBoundaryValidation(
            False, None, False, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveTexArchiveRetentionBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_TEX_ARCHIVE_RETENTION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported TeX archive retention boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "full arXiv TeX/e-print source archive" not in source_claim
        or "archive member inventory" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must describe full archive retention and member inventory"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "TeX archive retention boundary must not claim refresh readiness"))
    archive_retained = _validate_archive_snapshot(data.get("archive_snapshot"), issues)
    member_count = _validate_member_inventory(data.get("archive_member_inventory"), issues)
    if base_dir is not None:
        _validate_retained_archive_file(data, base_dir, issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "full arXiv TeX/e-print archive artifact" not in boundary_text
        or "archive member inventory" not in boundary_text
        or "automated TeX-source refresh gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate retained archive evidence from refresh/extraction evidence"))
    return AlphaEvolveTexArchiveRetentionBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        archive_artifact_retained=archive_retained,
        member_count=member_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_tex_archive_retention_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_tex_archive_retention_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve TeX archive retention boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| archive_artifact_retained | {validation.archive_artifact_retained} |",
        f"| member_count | {validation.member_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_committed_record() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[3] / "papers" / "alphaevolve_tex_archive_retention_boundary.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return data
    raise ValueError("alphaevolve_tex_archive_retention_boundary.json must contain an object")


def _validate_archive_snapshot(
    value: object,
    issues: list[AlphaEvolveTexArchiveRetentionBoundaryIssue],
) -> bool:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_archive_snapshot", "archive_snapshot must be an object"))
        return False
    expected = {
        "eprint_url": EXPECTED_EPRINT_URL,
        "retrieved_at_utc": EXPECTED_RETRIEVED_AT_UTC,
        "http_status": 200,
        "content_type": "application/gzip",
        "content_disposition": 'attachment; filename="arXiv-2506.13131v1.tar.gz"',
        "response_bytes": EXPECTED_RESPONSE_BYTES,
        "response_sha256": EXPECTED_RESPONSE_SHA256,
        "archive_artifact_path": EXPECTED_ARCHIVE_ARTIFACT_PATH,
        "archive_artifact_retained": True,
        "archive_artifact_bytes": EXPECTED_RESPONSE_BYTES,
        "archive_artifact_sha256": EXPECTED_RESPONSE_SHA256,
        "arxiv_versioned_id": "2506.13131v1",
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_archive_snapshot_{key}", f"archive_snapshot.{key} must be {expected_value}"))
    return value.get("archive_artifact_retained") is True


def _validate_member_inventory(
    value: object,
    issues: list[AlphaEvolveTexArchiveRetentionBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_archive_member_inventory", "archive_member_inventory must be an object"))
        return 0
    expected = {
        "member_count": EXPECTED_MEMBER_COUNT,
        "file_count": EXPECTED_FILE_COUNT,
        "dir_count": EXPECTED_DIR_COUNT,
        "total_uncompressed_file_bytes": EXPECTED_TOTAL_UNCOMPRESSED_FILE_BYTES,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_archive_member_inventory_{key}", f"archive_member_inventory.{key} must be {expected_value}"))
    members = value.get("members")
    if not isinstance(members, list):
        issues.append(_issue("invalid_archive_members", "archive_member_inventory.members must be a list"))
        return 0
    if len(members) != EXPECTED_MEMBER_COUNT:
        issues.append(_issue("invalid_archive_members_count", f"archive_member_inventory.members must contain {EXPECTED_MEMBER_COUNT} entries"))
    seen_names: set[str] = set()
    for index, member in enumerate(members):
        if not isinstance(member, dict):
            issues.append(_issue("invalid_archive_member", f"archive member {index} must be an object"))
            continue
        name = member.get("name")
        member_type = member.get("type")
        if not isinstance(name, str) or not name:
            issues.append(_issue("invalid_archive_member_name", f"archive member {index} must have a non-empty name"))
        elif name in seen_names:
            issues.append(_issue("duplicate_archive_member_name", f"archive member {name} is duplicated"))
        else:
            seen_names.add(name)
        if member_type not in {"file", "dir", "other"}:
            issues.append(_issue("invalid_archive_member_type", f"archive member {name or index} has invalid type"))
        if not isinstance(member.get("size"), int) or member["size"] < 0:
            issues.append(_issue("invalid_archive_member_size", f"archive member {name or index} must have non-negative integer size"))
        if member_type == "file":
            digest = member.get("sha256")
            if not isinstance(digest, str) or len(digest) != 64:
                issues.append(_issue("invalid_archive_member_sha256", f"file archive member {name or index} must have a SHA-256 digest"))
    return len(members)


def _validate_retained_archive_file(
    data: dict[str, Any],
    base_dir: Path,
    issues: list[AlphaEvolveTexArchiveRetentionBoundaryIssue],
) -> None:
    snapshot = data.get("archive_snapshot")
    inventory = data.get("archive_member_inventory")
    if not isinstance(snapshot, dict) or not isinstance(inventory, dict):
        return
    artifact_value = snapshot.get("archive_artifact_path")
    if not isinstance(artifact_value, str):
        return
    artifact_path = base_dir / artifact_value
    try:
        archive_bytes = artifact_path.read_bytes()
    except OSError as exc:
        issues.append(_issue("missing_archive_artifact", f"archive artifact could not be read: {exc}"))
        return
    if len(archive_bytes) != EXPECTED_RESPONSE_BYTES:
        issues.append(_issue("invalid_archive_artifact_bytes", f"archive artifact must be {EXPECTED_RESPONSE_BYTES} bytes"))
    digest = hashlib.sha256(archive_bytes).hexdigest()
    if digest != EXPECTED_RESPONSE_SHA256:
        issues.append(_issue("invalid_archive_artifact_sha256", f"archive artifact SHA-256 must be {EXPECTED_RESPONSE_SHA256}"))
    try:
        actual_members = _archive_members_from_bytes(archive_bytes)
    except tarfile.TarError as exc:
        issues.append(_issue("invalid_archive_artifact_tar", f"archive artifact must be a readable tar.gz file: {exc}"))
        return
    if actual_members != inventory.get("members"):
        issues.append(_issue("archive_member_inventory_drift", "archive member inventory must match the retained archive artifact"))


def _archive_members_from_bytes(archive_bytes: bytes) -> list[dict[str, Any]]:
    members: list[dict[str, Any]] = []
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        for member in archive.getmembers():
            entry: dict[str, Any] = {
                "name": member.name,
                "type": "file" if member.isfile() else "dir" if member.isdir() else "other",
                "size": member.size,
            }
            if member.isfile():
                extracted = archive.extractfile(member)
                data = extracted.read() if extracted is not None else b""
                entry["sha256"] = hashlib.sha256(data).hexdigest()
            members.append(entry)
    return members


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveTexArchiveRetentionBoundaryIssue], Path | None]:
    if isinstance(boundary, dict):
        return dict(boundary), [], None
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")], None
        return data if isinstance(data, dict) else None, [] if isinstance(data, dict) else [_issue("invalid_shape", "TeX archive retention boundary must be a JSON object")], None
    path = Path(boundary)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")], None
    if isinstance(data, dict):
        return data, [], path.parent.parent
    return None, [_issue("invalid_shape", "TeX archive retention boundary must be a JSON object")], None


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveTexArchiveRetentionBoundaryIssue],
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
    issues: list[AlphaEvolveTexArchiveRetentionBoundaryIssue],
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
) -> AlphaEvolveTexArchiveRetentionBoundaryIssue:
    return AlphaEvolveTexArchiveRetentionBoundaryIssue(code, message)
