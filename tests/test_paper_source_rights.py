import json

from libreevolve.problems.benchmarks.paper_source_rights import (
    ALPHAEVOLVE_SOURCE_PDF_RIGHTS_MANIFEST_SCHEMA,
    ALPHAEVOLVE_SOURCE_PDF_RIGHTS_SCHEMA,
    alphaevolve_source_pdf_rights_manifest_record,
    alphaevolve_source_pdf_rights_record,
    render_alphaevolve_source_pdf_rights_summary,
    validate_alphaevolve_source_pdf_rights_manifest,
    validate_alphaevolve_source_pdf_rights,
)


def test_validate_alphaevolve_source_pdf_rights_accepts_builtin_record():
    recordset = alphaevolve_source_pdf_rights_record()

    validation = validate_alphaevolve_source_pdf_rights(
        recordset,
        first_page_text="AlphaEvolve\n© 2025 Google DeepMind. All rights reserved",
    )

    assert recordset["schema"] == ALPHAEVOLVE_SOURCE_PDF_RIGHTS_SCHEMA
    assert validation.ok is True
    assert validation.rights_count == 1
    assert validation.rights_text_checked is True
    assert validation.issues == []


def test_validate_alphaevolve_source_pdf_rights_manifest_accepts_builtin_record():
    recordset = alphaevolve_source_pdf_rights_manifest_record()

    validation = validate_alphaevolve_source_pdf_rights_manifest(
        recordset,
        first_page_text="AlphaEvolve\n© 2025 Google DeepMind. All rights reserved",
    )

    assert recordset["schema"] == ALPHAEVOLVE_SOURCE_PDF_RIGHTS_MANIFEST_SCHEMA
    assert validation.ok is True
    assert validation.rights_count == 1
    assert validation.rights_text_checked is True
    assert validation.issues == []


def test_validate_alphaevolve_source_pdf_rights_manifest_rejects_policy_drift():
    recordset = alphaevolve_source_pdf_rights_manifest_record()
    source = recordset["sources"][0]
    source["source_identity_manifest"] = "papers/other.json"
    source["paper_derived_artifact_policy"]["artifact_classes"] = ["excerpt"]
    source["paper_derived_artifact_policy"]["reproduction_policy"] = "free_reuse"
    source["paper_derived_artifact_policy"]["publication_ready_without_rights_review"] = True
    source["paper_derived_artifact_policy"]["claim_surfaces"] = ["README.md"]

    validation = validate_alphaevolve_source_pdf_rights_manifest(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_source_identity_manifest" in codes
    assert "artifact_class_mismatch" in codes
    assert "invalid_reproduction_policy" in codes
    assert "invalid_publication_ready_without_rights_review" in codes
    assert "claim_surface_mismatch" in codes


def test_validate_alphaevolve_source_pdf_rights_loads_json_file(tmp_path):
    path = tmp_path / "source_rights.json"
    path.write_text(json.dumps(alphaevolve_source_pdf_rights_record()), encoding="utf-8")

    validation = validate_alphaevolve_source_pdf_rights(path)

    assert validation.ok is True
    assert validation.rights_text_checked is False


def test_validate_alphaevolve_source_pdf_rights_rejects_manifest_drift():
    recordset = alphaevolve_source_pdf_rights_record()
    recordset["manifest_row"]["id"] = "2506.99999"
    recordset["manifest_row"]["url"] = "https://arxiv.org/pdf/2506.99999.pdf"
    recordset["manifest_row"]["file"] = "papers/other.pdf"
    recordset["manifest_row"]["bytes"] = 1
    recordset["manifest_row"]["sha256"] = "0" * 64

    validation = validate_alphaevolve_source_pdf_rights(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_manifest_id" in codes
    assert "invalid_manifest_url" in codes
    assert "invalid_manifest_file" in codes
    assert "invalid_manifest_bytes" in codes
    assert "manifest_sha256_drift" in codes


def test_validate_alphaevolve_source_pdf_rights_rejects_rights_drift():
    recordset = alphaevolve_source_pdf_rights_record()
    recordset["rights"]["rights_holder"] = "LibreEvolve"
    recordset["rights"]["copyright_year"] = 2026
    recordset["rights"]["rights_statement"] = "MIT"
    recordset["rights"]["source_page"] = 2
    recordset["rights"]["license_identifier"] = "MIT"
    recordset["rights"]["open_license_declared_in_cached_pdf"] = True
    recordset["rights"]["arxiv_license_terms_recorded"] = True
    recordset["rights"]["reuse_policy"] = "free_reuse"

    validation = validate_alphaevolve_source_pdf_rights(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_rights_rights_holder" in codes
    assert "invalid_rights_copyright_year" in codes
    assert "invalid_rights_rights_statement" in codes
    assert "invalid_rights_source_page" in codes
    assert "invalid_rights_license_identifier" in codes
    assert "invalid_rights_open_license_declared_in_cached_pdf" in codes
    assert "invalid_rights_arxiv_license_terms_recorded" in codes
    assert "invalid_reuse_policy" in codes


def test_validate_alphaevolve_source_pdf_rights_rejects_boundary_overclaims():
    recordset = alphaevolve_source_pdf_rights_record()
    recordset["boundary"]["distinct_from_libreevolve_license"] = False
    recordset["boundary"]["distinct_from_companion_repository_license"] = False
    recordset["boundary"]["paper_derived_artifacts_must_carry_source_rights"] = False
    recordset["boundary"]["scope"] = "LibreEvolve repository licensing"

    validation = validate_alphaevolve_source_pdf_rights(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_boundary_distinct_from_libreevolve_license" in codes
    assert "invalid_boundary_distinct_from_companion_repository_license" in codes
    assert "invalid_boundary_paper_derived_artifacts_must_carry_source_rights" in codes
    assert "invalid_boundary_scope" in codes


def test_validate_alphaevolve_source_pdf_rights_rejects_missing_rights_text():
    recordset = alphaevolve_source_pdf_rights_record()

    validation = validate_alphaevolve_source_pdf_rights(
        recordset,
        first_page_text="AlphaEvolve without a rights line",
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.rights_text_checked is True
    assert "missing_expected_rights_statement" in codes


def test_render_alphaevolve_source_pdf_rights_summary_reports_shape():
    summary = render_alphaevolve_source_pdf_rights_summary(
        alphaevolve_source_pdf_rights_record()
    )

    assert "AlphaEvolve source-PDF rights evidence" in summary
    assert "| schema_status | ok |" in summary
    assert "| rights_count | 1 |" in summary
    assert "| rights_holder | Google DeepMind |" in summary
    assert "| copyright_year | 2025 |" in summary
