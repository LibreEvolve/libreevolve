import json
from pathlib import Path

from libreevolve.problems.benchmarks.paper_source_identity import (
    PAPER_SOURCE_IDENTITY_MANIFEST_SCHEMA,
    paper_source_identity_manifest_record,
    validate_paper_source_identity_manifest,
)


def _manifest_rows():
    return json.loads(Path("papers/download_manifest.json").read_text(encoding="utf-8"))


def test_validate_paper_source_identity_accepts_generated_manifest():
    rows = _manifest_rows()
    recordset = paper_source_identity_manifest_record(rows)

    validation = validate_paper_source_identity_manifest(
        recordset,
        manifest_rows=rows,
    )

    assert recordset["schema"] == PAPER_SOURCE_IDENTITY_MANIFEST_SCHEMA
    assert validation.ok is True
    assert validation.source_identity_count == len(rows)
    assert validation.issues == []
    alphaevolve = recordset["sources"][0]
    assert alphaevolve["manifest_row_id"] == "2506.13131"
    assert alphaevolve["url_source_id"] == "2506.13131"
    assert alphaevolve["file_source_id"] == "2506.13131"
    assert alphaevolve["source_version_link"]["source_version_id"] == "2506.13131v1"


def test_validate_paper_source_identity_loads_checked_in_manifest():
    rows = _manifest_rows()

    validation = validate_paper_source_identity_manifest(
        "papers/row_identity.json",
        manifest_rows=rows,
    )

    assert validation.ok is True
    assert validation.source_identity_count == len(rows)


def test_validate_paper_source_identity_rejects_manifest_row_drift():
    rows = _manifest_rows()
    recordset = paper_source_identity_manifest_record(rows)
    recordset["sources"][0]["sha256"] = "0" * 64
    recordset["sources"][0]["source_version_link"] = None

    validation = validate_paper_source_identity_manifest(
        recordset,
        manifest_rows=rows,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "manifest_sha256_mismatch" in codes
    assert "missing_source_version_link" in codes


def test_validate_paper_source_identity_rejects_invalid_identity_checks():
    rows = _manifest_rows()
    recordset = paper_source_identity_manifest_record(rows)
    recordset["sources"][1]["url_source_id"] = "2506.13131"
    recordset["sources"][1]["identity_checks"]["source_identity_valid"] = False

    validation = validate_paper_source_identity_manifest(
        recordset,
        manifest_rows=rows,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "url_source_id_mismatch" in codes
    assert "invalid_source_identity_valid" in codes
    assert "source_identity_not_valid" in codes
