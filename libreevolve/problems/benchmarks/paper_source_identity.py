from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse


PAPER_SOURCE_IDENTITY_MANIFEST_SCHEMA = (
    "libreevolve.paper_source_identity_manifest.v1"
)
PAPER_SOURCE_IDENTITY_MANIFEST_FILE = "papers/row_identity.json"
ALPHAEVOLVE_SOURCE_VERSION_MANIFEST_FILE = "papers/source_versions.json"
ALPHAEVOLVE_SOURCE_VERSION_ID = "2506.13131v1"
_ARXIV_ID_RE = re.compile(r"\d{4}\.\d{5}(?:v\d+)?")


@dataclass(frozen=True)
class PaperSourceIdentityIssue:
    code: str
    message: str
    row_id: str | None = None


@dataclass(frozen=True)
class PaperSourceIdentityValidation:
    ok: bool
    source_identity_count: int
    issues: list[PaperSourceIdentityIssue]


def paper_source_identity_manifest_record(
    manifest_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    records = [_source_identity_record(row) for row in manifest_rows]
    return {
        "schema": PAPER_SOURCE_IDENTITY_MANIFEST_SCHEMA,
        "source_identity_count": len(records),
        "source_identity_policy": "manifest_id_url_source_id_and_file_source_prefix_must_match_before_source_version_or_rights_claims",
        "sources": records,
    }


def validate_paper_source_identity_manifest(
    recordset: object | str | Path,
    *,
    manifest_rows: list[dict[str, Any]] | None = None,
) -> PaperSourceIdentityValidation:
    data, read_issues = _load_recordset(recordset)
    if read_issues:
        return PaperSourceIdentityValidation(False, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[PaperSourceIdentityIssue] = []
    if data.get("schema") != PAPER_SOURCE_IDENTITY_MANIFEST_SCHEMA:
        issues.append(
            PaperSourceIdentityIssue(
                "invalid_schema",
                "unsupported paper source-identity manifest schema",
            )
        )
    if data.get("source_identity_policy") != (
        "manifest_id_url_source_id_and_file_source_prefix_must_match_before_source_version_or_rights_claims"
    ):
        issues.append(
            PaperSourceIdentityIssue(
                "invalid_source_identity_policy",
                "source_identity_policy must preserve the row identity boundary",
            )
        )
    sources = data.get("sources")
    if not isinstance(sources, list):
        issues.append(
            PaperSourceIdentityIssue(
                "invalid_sources",
                "source-identity manifest sources must be a list",
            )
        )
        sources = []
    source_count = len(sources)
    if data.get("source_identity_count") != source_count:
        issues.append(
            PaperSourceIdentityIssue(
                "invalid_source_identity_count",
                "source_identity_count must equal the number of source records",
            )
        )
    records_by_id: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            issues.append(
                PaperSourceIdentityIssue(
                    "invalid_source_record",
                    f"source-identity record {index} must be an object",
                )
            )
            continue
        row_id = source.get("manifest_row_id")
        if not isinstance(row_id, str):
            issues.append(
                PaperSourceIdentityIssue(
                    "invalid_manifest_row_id",
                    "manifest_row_id must be a string",
                )
            )
            continue
        if row_id in records_by_id:
            issues.append(
                PaperSourceIdentityIssue(
                    "duplicate_manifest_row_id",
                    "source-identity manifest row ids must be unique",
                    row_id,
                )
            )
        records_by_id[row_id] = source
        _validate_source_record(source, issues)
    if manifest_rows is not None:
        _validate_against_manifest_rows(records_by_id, manifest_rows, issues)
    return PaperSourceIdentityValidation(
        ok=not issues,
        source_identity_count=source_count,
        issues=issues,
    )


def _source_identity_record(row: dict[str, Any]) -> dict[str, Any]:
    row_id = str(row["id"])
    url = str(row["url"])
    file_value = str(row["file"])
    parsed = urlparse(url)
    host = parsed.hostname.casefold() if parsed.hostname else None
    arxiv_id = _arxiv_id_from_url_path(parsed.path) if host in {"arxiv.org", "www.arxiv.org"} else None
    file_source_id = PurePosixPath(file_value).stem.split("__", 1)[0]
    source_kind = "arxiv" if arxiv_id is not None else "web"
    source_version_link = None
    if row_id == "2506.13131":
        source_version_link = {
            "source_version_id": ALPHAEVOLVE_SOURCE_VERSION_ID,
            "source_version_manifest": ALPHAEVOLVE_SOURCE_VERSION_MANIFEST_FILE,
        }
    return {
        "manifest_row_id": row_id,
        "title": row.get("title"),
        "url": url,
        "file": file_value,
        "sha256": row.get("sha256"),
        "source_kind": source_kind,
        "source_host": host,
        "url_source_id": arxiv_id.split("v", 1)[0] if arxiv_id else None,
        "url_versioned_id": arxiv_id,
        "file_source_id": file_source_id,
        "identity_checks": {
            "manifest_id_matches_url_source_id": (
                arxiv_id is None or arxiv_id.split("v", 1)[0] == row_id
            ),
            "manifest_id_matches_file_source_id": file_source_id == row_id,
            "source_identity_valid": (
                (arxiv_id is None or arxiv_id.split("v", 1)[0] == row_id)
                and file_source_id == row_id
            ),
        },
        "source_version_link": source_version_link,
    }


def _validate_source_record(
    source: dict[str, Any],
    issues: list[PaperSourceIdentityIssue],
) -> None:
    row_id = str(source.get("manifest_row_id"))
    required_strings = ("title", "url", "file", "sha256", "source_kind", "source_host", "file_source_id")
    for field in required_strings:
        if not isinstance(source.get(field), str):
            issues.append(
                PaperSourceIdentityIssue(
                    f"invalid_{field}",
                    f"{field} must be a string",
                    row_id,
                )
            )
    if source.get("source_kind") not in {"arxiv", "web"}:
        issues.append(
            PaperSourceIdentityIssue(
                "invalid_source_kind",
                "source_kind must be arxiv or web",
                row_id,
            )
        )
    parsed = urlparse(str(source.get("url", "")))
    host = parsed.hostname.casefold() if parsed.hostname else None
    arxiv_id = _arxiv_id_from_url_path(parsed.path) if host in {"arxiv.org", "www.arxiv.org"} else None
    expected_url_source_id = arxiv_id.split("v", 1)[0] if arxiv_id else None
    if source.get("url_source_id") != expected_url_source_id:
        issues.append(
            PaperSourceIdentityIssue(
                "url_source_id_mismatch",
                "url_source_id must match the id parsed from the source URL",
                row_id,
            )
        )
    if source.get("url_versioned_id") != arxiv_id:
        issues.append(
            PaperSourceIdentityIssue(
                "url_versioned_id_mismatch",
                "url_versioned_id must match the arXiv id parsed from the source URL",
                row_id,
            )
        )
    expected_file_source_id = PurePosixPath(str(source.get("file", ""))).stem.split("__", 1)[0]
    if source.get("file_source_id") != expected_file_source_id:
        issues.append(
            PaperSourceIdentityIssue(
                "file_source_id_mismatch",
                "file_source_id must match the local filename source prefix",
                row_id,
            )
        )
    checks = source.get("identity_checks")
    if not isinstance(checks, dict):
        issues.append(
            PaperSourceIdentityIssue(
                "invalid_identity_checks",
                "identity_checks must be an object",
                row_id,
            )
        )
        return
    expected_checks = {
        "manifest_id_matches_url_source_id": (
            expected_url_source_id is None or expected_url_source_id == row_id
        ),
        "manifest_id_matches_file_source_id": expected_file_source_id == row_id,
    }
    expected_checks["source_identity_valid"] = all(expected_checks.values())
    for field, expected_value in expected_checks.items():
        if checks.get(field) is not expected_value:
            issues.append(
                PaperSourceIdentityIssue(
                    f"invalid_{field}",
                    f"identity_checks.{field} must be {expected_value}",
                    row_id,
                )
            )
    if checks.get("source_identity_valid") is not True:
        issues.append(
            PaperSourceIdentityIssue(
                "source_identity_not_valid",
                "source identity must be valid before source-version or rights claims attach",
                row_id,
            )
        )
    _validate_source_version_link(source.get("source_version_link"), row_id, issues)


def _validate_against_manifest_rows(
    records_by_id: dict[str, dict[str, Any]],
    manifest_rows: list[dict[str, Any]],
    issues: list[PaperSourceIdentityIssue],
) -> None:
    manifest_ids = {str(row.get("id")) for row in manifest_rows}
    record_ids = set(records_by_id)
    for missing in sorted(manifest_ids - record_ids):
        issues.append(
            PaperSourceIdentityIssue(
                "missing_manifest_row",
                "source-identity manifest is missing a paper manifest row",
                missing,
            )
        )
    for extra in sorted(record_ids - manifest_ids):
        issues.append(
            PaperSourceIdentityIssue(
                "extra_manifest_row",
                "source-identity manifest row has no paper manifest row",
                extra,
            )
        )
    for row in manifest_rows:
        row_id = str(row.get("id"))
        record = records_by_id.get(row_id)
        if record is None:
            continue
        expected = _source_identity_record(row)
        for field in (
            "title",
            "url",
            "file",
            "sha256",
            "source_kind",
            "source_host",
            "url_source_id",
            "url_versioned_id",
            "file_source_id",
            "source_version_link",
        ):
            if record.get(field) != expected[field]:
                issues.append(
                    PaperSourceIdentityIssue(
                        f"manifest_{field}_mismatch",
                        f"source-identity {field} does not match the paper manifest row",
                        row_id,
                    )
                )


def _validate_source_version_link(
    value: object,
    row_id: str,
    issues: list[PaperSourceIdentityIssue],
) -> None:
    if row_id == "2506.13131":
        if not isinstance(value, dict):
            issues.append(
                PaperSourceIdentityIssue(
                    "missing_source_version_link",
                    "AlphaEvolve source identity must link to the source-version manifest",
                    row_id,
                )
            )
            return
        expected = {
            "source_version_id": ALPHAEVOLVE_SOURCE_VERSION_ID,
            "source_version_manifest": ALPHAEVOLVE_SOURCE_VERSION_MANIFEST_FILE,
        }
        for field, expected_value in expected.items():
            if value.get(field) != expected_value:
                issues.append(
                    PaperSourceIdentityIssue(
                        f"invalid_source_version_link_{field}",
                        f"source_version_link.{field} must identify the AlphaEvolve source version",
                        row_id,
                    )
                )
    elif value is not None:
        issues.append(
            PaperSourceIdentityIssue(
                "unexpected_source_version_link",
                "only the AlphaEvolve row has a pinned source-version link in this manifest",
                row_id,
            )
        )


def _load_recordset(
    recordset: object | str | Path,
) -> tuple[dict[str, Any] | None, list[PaperSourceIdentityIssue]]:
    if isinstance(recordset, dict):
        return dict(recordset), []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [PaperSourceIdentityIssue("read_error", f"failed to read source-identity manifest: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [PaperSourceIdentityIssue("invalid_json", f"invalid source-identity JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [PaperSourceIdentityIssue("invalid_shape", "source-identity manifest must be a JSON object")]


def _arxiv_id_from_url_path(path: str) -> str | None:
    parts = [part for part in PurePosixPath(path).parts if part not in {"/", ""}]
    if len(parts) < 2 or parts[0] not in {"abs", "pdf"}:
        return None
    candidate = parts[1]
    if candidate.endswith(".pdf"):
        candidate = candidate[:-4]
    if _ARXIV_ID_RE.fullmatch(candidate) is None:
        return None
    return candidate
