import json

from libreevolve.problems.benchmarks.paper_source_versions import (
    ALPHAEVOLVE_SOURCE_PDF_VERSION_MANIFEST_SCHEMA,
    ALPHAEVOLVE_SOURCE_PDF_VERSION_SCHEMA,
    alphaevolve_source_pdf_version_manifest_record,
    alphaevolve_source_pdf_version_record,
    render_alphaevolve_source_pdf_version_summary,
    validate_alphaevolve_source_pdf_version_manifest,
    validate_alphaevolve_source_pdf_version,
)


def test_validate_alphaevolve_source_pdf_version_accepts_builtin_record():
    recordset = alphaevolve_source_pdf_version_record()

    validation = validate_alphaevolve_source_pdf_version(
        recordset,
        first_page_text="arXiv:2506.13131v1  [cs.AI]  16 Jun 2025\nAlphaEvolve",
    )

    assert recordset["schema"] == ALPHAEVOLVE_SOURCE_PDF_VERSION_SCHEMA
    assert validation.ok is True
    assert validation.source_count == 1
    assert validation.header_checked is True
    assert validation.issues == []
    assert recordset["arxiv_source"]["subjects"] == ["cs.AI", "cs.LG", "cs.NE"]
    assert recordset["arxiv_source"]["doi"] == "10.48550/arXiv.2506.13131"
    assert recordset["arxiv_source"]["author_count"] == 18
    assert recordset["arxiv_source"]["license_url"] == (
        "https://creativecommons.org/licenses/by-nc-nd/4.0/"
    )


def test_validate_alphaevolve_source_pdf_version_manifest_accepts_builtin_record():
    recordset = alphaevolve_source_pdf_version_manifest_record()

    validation = validate_alphaevolve_source_pdf_version_manifest(
        recordset,
        first_page_text="arXiv:2506.13131v1  [cs.AI]  16 Jun 2025\nAlphaEvolve",
    )

    assert recordset["schema"] == ALPHAEVOLVE_SOURCE_PDF_VERSION_MANIFEST_SCHEMA
    assert validation.ok is True
    assert validation.source_count == 1
    assert validation.header_checked is True
    assert validation.issues == []


def test_validate_alphaevolve_source_pdf_version_manifest_rejects_claim_link_drift():
    recordset = alphaevolve_source_pdf_version_manifest_record()
    source = recordset["sources"][0]
    source["source_version_id"] = "2506.13131v2"
    source["claim_artifact_links"]["source_version_used_by"] = ["README.md"]
    source["claim_artifact_links"]["policy"] = "optional"

    validation = validate_alphaevolve_source_pdf_version_manifest(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_manifest_source_version_id" in codes
    assert "claim_artifact_surface_mismatch" in codes
    assert "invalid_claim_artifact_policy" in codes


def test_validate_alphaevolve_source_pdf_version_loads_json_file(tmp_path):
    path = tmp_path / "source_version.json"
    path.write_text(json.dumps(alphaevolve_source_pdf_version_record()), encoding="utf-8")

    validation = validate_alphaevolve_source_pdf_version(path)

    assert validation.ok is True
    assert validation.header_checked is False


def test_validate_alphaevolve_source_pdf_version_rejects_manifest_drift():
    recordset = alphaevolve_source_pdf_version_record()
    recordset["manifest_row"]["id"] = "2506.99999"
    recordset["manifest_row"]["url"] = "https://arxiv.org/pdf/2506.99999.pdf"
    recordset["manifest_row"]["file"] = "papers/other.pdf"
    recordset["manifest_row"]["bytes"] = 1
    recordset["manifest_row"]["sha256"] = "0" * 64

    validation = validate_alphaevolve_source_pdf_version(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_manifest_id" in codes
    assert "invalid_manifest_url" in codes
    assert "invalid_manifest_file" in codes
    assert "invalid_manifest_bytes" in codes
    assert "manifest_sha256_drift" in codes


def test_validate_alphaevolve_source_pdf_version_rejects_arxiv_version_drift():
    recordset = alphaevolve_source_pdf_version_record()
    recordset["arxiv_source"]["version"] = 2
    recordset["arxiv_source"]["versioned_id"] = "2506.13131v2"
    recordset["arxiv_source"]["category"] = "cs.SE"
    recordset["arxiv_source"]["subjects"] = ["cs.SE"]
    recordset["arxiv_source"]["posted_date"] = "2025-06-17"
    recordset["arxiv_source"]["submitted_timestamp_utc"] = "2025-06-17T00:00:00Z"
    recordset["arxiv_source"]["doi"] = "10.48550/arXiv.2506.99999"
    recordset["arxiv_source"]["author_count"] = 1
    recordset["arxiv_source"]["tex_source_url"] = "https://example.test/source"
    recordset["arxiv_source"]["license_url"] = "https://example.test/license"
    recordset["arxiv_source"]["abstract_page_metadata_status"] = "snapshotted"
    recordset["arxiv_source"]["expected_header_phrase"] = "arXiv:2506.13131v2 [cs.SE] 17 Jun 2025"

    validation = validate_alphaevolve_source_pdf_version(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_arxiv_version" in codes
    assert "invalid_arxiv_versioned_id" in codes
    assert "invalid_arxiv_category" in codes
    assert "invalid_arxiv_subjects" in codes
    assert "invalid_arxiv_posted_date" in codes
    assert "invalid_arxiv_submitted_timestamp_utc" in codes
    assert "invalid_arxiv_doi" in codes
    assert "invalid_arxiv_author_count" in codes
    assert "invalid_arxiv_tex_source_url" in codes
    assert "invalid_arxiv_license_url" in codes
    assert "invalid_arxiv_abstract_page_metadata_status" in codes
    assert "invalid_arxiv_expected_header_phrase" in codes


def test_validate_alphaevolve_source_pdf_version_rejects_missing_header_phrase():
    recordset = alphaevolve_source_pdf_version_record()

    validation = validate_alphaevolve_source_pdf_version(
        recordset,
        first_page_text="AlphaEvolve without the source header",
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.header_checked is True
    assert "missing_expected_header_phrase" in codes


def test_validate_alphaevolve_source_pdf_version_rejects_audit_policy_drift():
    recordset = alphaevolve_source_pdf_version_record()
    recordset["audit_policy"]["manifest_url_requires_header_version_check"] = False
    recordset["audit_policy"]["claim_audits_must_name_source_version"] = False
    recordset["audit_policy"]["floating_url_refresh_is_not_silent_version_change"] = False
    recordset["audit_policy"]["arxiv_abs_html_snapshot_required_for_live_metadata_claims"] = False
    recordset["audit_policy"]["datacite_doi_resolution_not_snapshotted"] = False
    recordset["audit_policy"]["tex_source_not_cached"] = False
    recordset["audit_policy"]["arxiv_license_page_not_cached"] = False
    recordset["audit_policy"]["submission_history_refresh_gate_not_implemented"] = False
    recordset["audit_policy"]["scope"] = "result-version provenance"

    validation = validate_alphaevolve_source_pdf_version(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_audit_policy_manifest_url_requires_header_version_check" in codes
    assert "invalid_audit_policy_claim_audits_must_name_source_version" in codes
    assert "invalid_audit_policy_floating_url_refresh_is_not_silent_version_change" in codes
    assert (
        "invalid_audit_policy_arxiv_abs_html_snapshot_required_for_live_metadata_claims"
        in codes
    )
    assert "invalid_audit_policy_datacite_doi_resolution_not_snapshotted" in codes
    assert "invalid_audit_policy_tex_source_not_cached" in codes
    assert "invalid_audit_policy_arxiv_license_page_not_cached" in codes
    assert (
        "invalid_audit_policy_submission_history_refresh_gate_not_implemented"
        in codes
    )
    assert "invalid_audit_policy_scope" in codes


def test_render_alphaevolve_source_pdf_version_summary_reports_shape():
    summary = render_alphaevolve_source_pdf_version_summary(
        alphaevolve_source_pdf_version_record()
    )

    assert "AlphaEvolve source-PDF version evidence" in summary
    assert "| schema_status | ok |" in summary
    assert "| source_count | 1 |" in summary
    assert "| arxiv_version | v1 |" in summary
    assert "| posted_date | 2025-06-16 |" in summary
