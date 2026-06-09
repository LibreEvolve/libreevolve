import copy
import json

from libreevolve.problems.benchmarks.official_deepmind_blog import (
    ALPHAEVOLVE_OFFICIAL_BLOG_SOURCE_SCHEMA,
    alphaevolve_official_blog_manifest_record,
    alphaevolve_official_blog_source_record,
    validate_alphaevolve_official_blog_manifest,
    validate_alphaevolve_official_blog_source,
)


def test_validate_alphaevolve_official_blog_source_accepts_builtin_record():
    recordset = alphaevolve_official_blog_source_record()

    validation = validate_alphaevolve_official_blog_source(recordset)

    assert recordset["schema"] == ALPHAEVOLVE_OFFICIAL_BLOG_SOURCE_SCHEMA
    assert validation.ok is True
    assert validation.source_count == 1
    assert validation.claim_count == 11
    assert validation.linked_whitepaper is True
    assert validation.announcement_boundary is True
    assert validation.issues == []


def test_validate_alphaevolve_official_blog_manifest_accepts_builtin_record():
    recordset = alphaevolve_official_blog_manifest_record()

    validation = validate_alphaevolve_official_blog_manifest(recordset)

    assert validation.ok is True
    assert validation.source_count == 1
    assert validation.claim_count == 11
    assert validation.linked_whitepaper is True
    assert validation.announcement_boundary is True
    assert validation.issues == []


def test_validate_alphaevolve_official_blog_manifest_loads_json_file(tmp_path):
    path = tmp_path / "official_deepmind_blog.json"
    path.write_text(json.dumps(alphaevolve_official_blog_manifest_record()), encoding="utf-8")

    validation = validate_alphaevolve_official_blog_manifest(path)

    assert validation.ok is True


def test_validate_alphaevolve_official_blog_source_rejects_source_and_claim_drift():
    recordset = copy.deepcopy(alphaevolve_official_blog_source_record())
    recordset["article"]["date"] = "2025-05-15"
    recordset["article"]["retrieval"]["html_sha256"] = "0" * 64
    recordset["linked_sources"]["whitepaper_url"] = "https://example.com/whitepaper.pdf"
    recordset["claim_variants"][5].pop("whitepaper_variant")
    recordset["claim_variants"][6]["source"] = "white_paper"
    recordset["role_metadata"]["illustrations_and_figures"] = ["Someone Else"]
    recordset["claim_boundary"]["not_whitepaper_specification"] = False

    validation = validate_alphaevolve_official_blog_source(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.linked_whitepaper is False
    assert validation.announcement_boundary is False
    assert "invalid_article_date" in codes
    assert "invalid_article_retrieval_html_sha256" in codes
    assert "invalid_linked_sources_whitepaper_url" in codes
    assert "missing_claim_whitepaper_variant" in codes
    assert "invalid_claim_source" in codes
    assert "invalid_role_metadata_illustrations_and_figures" in codes
    assert "invalid_claim_boundary_not_whitepaper_specification" in codes


def test_validate_alphaevolve_official_blog_manifest_rejects_surface_and_policy_drift():
    recordset = alphaevolve_official_blog_manifest_record()
    source = recordset["sources"][0]
    source["manifest_row_id"] = "2511.02864"
    source["official_blog_source_id"] = "other"
    source["claim_artifact_links"]["official_blog_used_by"] = ["README.md"]
    source["claim_artifact_links"]["policy"] = "blog_is_whitepaper_spec"
    source["evidence_policy"]["publication_ready_without_variant_reconciliation"] = True
    source["evidence_policy"]["scope"] = "audited white-paper specification"

    validation = validate_alphaevolve_official_blog_manifest(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_manifest_manifest_row_id" in codes
    assert "invalid_manifest_official_blog_source_id" in codes
    assert "claim_surface_mismatch" in codes
    assert "invalid_claim_policy" in codes
    assert "invalid_evidence_policy_publication_ready_without_variant_reconciliation" in codes
    assert "invalid_evidence_policy_scope" in codes
