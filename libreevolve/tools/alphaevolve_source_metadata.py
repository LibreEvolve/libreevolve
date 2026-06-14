from __future__ import annotations

import argparse
import hashlib
import io
import json
import tarfile
from pathlib import Path
from typing import Any

from pypdf import PdfReader


REPORT_SCHEMA = "libreevolve.alphaevolve_source_metadata_extraction.v1"
ARXIV_ABSTRACT_HTML = "papers/arxiv_abstract_2506.13131v1.html"
CACHED_PDF = "papers/2506.13131__AlphaEvolve.pdf"
DATACITE_FULL_RESPONSE_BOUNDARY = "papers/alphaevolve_datacite_full_response_boundary.json"
LICENSE_PAGE_HTML = "papers/alphaevolve_license_page.html"
TEX_ARCHIVE = "papers/alphaevolve_tex_source_archive.tar.gz"


def build_alphaevolve_source_metadata_report(root: str | Path = ".") -> dict[str, Any]:
    """Build an offline metadata report from retained AlphaEvolve source artifacts."""

    root_path = Path(root)
    report = {
        "schema": REPORT_SCHEMA,
        "source_paper_id": "2506.13131",
        "source_version_id": "2506.13131v1",
        "script_artifact": _script_artifact(),
        "artifacts": {
            "arxiv_abstract_html": _html_artifact(root_path, ARXIV_ABSTRACT_HTML),
            "cached_pdf_first_page": _cached_pdf_artifact(root_path, CACHED_PDF),
            "datacite_full_response": _datacite_artifact(
                root_path, DATACITE_FULL_RESPONSE_BOUNDARY
            ),
            "license_page_html": _html_artifact(root_path, LICENSE_PAGE_HTML),
            "tex_archive": _tex_archive_artifact(root_path, TEX_ARCHIVE),
        },
        "claim_boundary": (
            "Offline extraction from retained local artifacts only; this report "
            "does not fetch live arXiv, DataCite, DOI, license, or e-print "
            "sources and is not an automated refresh gate."
        ),
    }
    report["artifact_count"] = len(report["artifacts"])
    report["ok"] = all(
        artifact.get("ok") is True for artifact in report["artifacts"].values()
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract AlphaEvolve source metadata from retained local artifacts."
    )
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--pretty", action="store_true", help="indent JSON output")
    args = parser.parse_args(argv)
    report = build_alphaevolve_source_metadata_report(args.root)
    indent = 2 if args.pretty else None
    print(json.dumps(report, indent=indent, sort_keys=True))
    return 0 if report["ok"] else 1


def _script_artifact() -> dict[str, Any]:
    path = Path(__file__).resolve()
    data = path.read_bytes()
    return {
        "path": "libreevolve/tools/alphaevolve_source_metadata.py",
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "entrypoint": "build_alphaevolve_source_metadata_report",
        "cli": "py -3.12 -m libreevolve.tools.alphaevolve_source_metadata --root .",
    }


def _html_artifact(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    try:
        data = path.read_bytes()
    except OSError as exc:
        return _error(relative_path, exc)
    text = data.decode("utf-8", errors="replace")
    return {
        "ok": True,
        "path": relative_path,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "markers": {
            "has_alphaevolve": "AlphaEvolve" in text,
            "has_arxiv_id": "2506.13131" in text,
            "has_doi": "10.48550" in text,
            "has_license": "creativecommons.org/licenses/by-nc-nd/4.0" in text,
        },
    }


def _cached_pdf_artifact(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    try:
        data = path.read_bytes()
        reader = PdfReader(io.BytesIO(data), strict=True)
        first_page_text = reader.pages[0].extract_text()
    except Exception as exc:  # pragma: no cover - exact pypdf errors vary.
        return _error(relative_path, exc)
    normalized_text = " ".join(first_page_text.split())
    return {
        "ok": True,
        "path": relative_path,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "first_page_text_chars": len(first_page_text),
        "normalized_first_page_text_chars": len(normalized_text),
        "first_page_text_sha256": hashlib.sha256(
            first_page_text.encode("utf-8")
        ).hexdigest(),
        "normalized_first_page_text_sha256": hashlib.sha256(
            normalized_text.encode("utf-8")
        ).hexdigest(),
        "markers": {
            "has_arxiv_header": "arXiv:2506.13131v1" in first_page_text
            and "[cs.AI]" in first_page_text
            and "16 Jun 2025" in first_page_text,
            "has_title": "AlphaEvolve" in first_page_text,
            "has_google_deepmind": "2025 Google DeepMind" in first_page_text,
            "has_rights_statement": "All rights reserved" in first_page_text,
        },
    }


def _datacite_artifact(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    try:
        boundary = json.loads(path.read_text(encoding="utf-8"))
        raw_body = boundary["raw_response_body"]
        data = raw_body.encode("utf-8")
        parsed = json.loads(raw_body)
        attributes = parsed["data"]["attributes"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return _error(relative_path, exc)
    return {
        "ok": True,
        "path": relative_path,
        "raw_response_bytes": len(data),
        "raw_response_sha256": hashlib.sha256(data).hexdigest(),
        "doi": attributes.get("doi"),
        "url": attributes.get("url"),
        "title": _first_title(attributes),
        "creator_count": len(attributes.get("creators", [])),
        "publication_year": attributes.get("publicationYear"),
        "version": attributes.get("version"),
    }


def _tex_archive_artifact(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    try:
        data = path.read_bytes()
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            members = archive.getmembers()
    except (OSError, tarfile.TarError) as exc:
        return _error(relative_path, exc)
    files = [member for member in members if member.isfile()]
    dirs = [member for member in members if member.isdir()]
    return {
        "ok": True,
        "path": relative_path,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "member_count": len(members),
        "file_count": len(files),
        "dir_count": len(dirs),
        "total_uncompressed_file_bytes": sum(member.size for member in files),
    }


def _first_title(attributes: dict[str, Any]) -> str | None:
    titles = attributes.get("titles")
    if not isinstance(titles, list) or not titles:
        return None
    first = titles[0]
    if not isinstance(first, dict):
        return None
    value = first.get("title")
    return value if isinstance(value, str) else None


def _error(relative_path: str, exc: BaseException) -> dict[str, Any]:
    return {
        "ok": False,
        "path": relative_path,
        "error": type(exc).__name__,
    }


if __name__ == "__main__":
    raise SystemExit(main())
