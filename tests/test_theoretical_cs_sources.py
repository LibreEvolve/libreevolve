import copy
import json

from libreevolve.problems.benchmarks.theoretical_cs_sources import (
    ALPHAEVOLVE_THEORETICAL_CS_SOURCE_SCHEMA,
    alphaevolve_theoretical_cs_source_manifest_record,
    alphaevolve_theoretical_cs_source_record,
    validate_alphaevolve_theoretical_cs_source,
    validate_alphaevolve_theoretical_cs_source_manifest,
)


def test_validate_alphaevolve_theoretical_cs_source_accepts_builtin_record():
    recordset = alphaevolve_theoretical_cs_source_record()

    validation = validate_alphaevolve_theoretical_cs_source(recordset)

    assert recordset["schema"] == ALPHAEVOLVE_THEORETICAL_CS_SOURCE_SCHEMA
    assert validation.ok is True
    assert validation.source_count == 2
    assert validation.application_count == 3
    assert validation.local_pdf_cache_available is True
    assert validation.proof_element_boundary is True
    assert validation.issues == []


def test_validate_alphaevolve_theoretical_cs_source_manifest_accepts_builtin_record():
    recordset = alphaevolve_theoretical_cs_source_manifest_record()

    validation = validate_alphaevolve_theoretical_cs_source_manifest(recordset)

    assert validation.ok is True
    assert validation.source_count == 1
    assert validation.application_count == 3
    assert validation.local_pdf_cache_available is True
    assert validation.proof_element_boundary is True
    assert validation.issues == []


def test_validate_alphaevolve_theoretical_cs_source_loads_json_file(tmp_path):
    path = tmp_path / "theoretical_cs_sources.json"
    path.write_text(
        json.dumps(alphaevolve_theoretical_cs_source_manifest_record()),
        encoding="utf-8",
    )

    validation = validate_alphaevolve_theoretical_cs_source_manifest(path)

    assert validation.ok is True


def test_validate_alphaevolve_theoretical_cs_source_rejects_drift():
    recordset = copy.deepcopy(alphaevolve_theoretical_cs_source_record())
    recordset["article"]["url"] = "https://example.com"
    recordset["article"]["retrieval"]["html_sha256"] = "0" * 64
    recordset["paper"]["version"] = 6
    recordset["paper"]["local_cache"]["available"] = False
    recordset["source_claims"]["proof_elements_not_full_proofs"] = False
    recordset["applications"][0]["local_artifact_inventory_available"] = True
    recordset["claim_boundaries"]["not_formal_theorem_prover"] = False
    recordset["claim_categories"] = ["proof_element_application"]

    validation = validate_alphaevolve_theoretical_cs_source(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.local_pdf_cache_available is False
    assert "invalid_article_url" in codes
    assert "invalid_article_retrieval_html_sha256" in codes
    assert "invalid_paper_version" in codes
    assert "invalid_local_cache_available" in codes
    assert "invalid_source_claims_proof_elements_not_full_proofs" in codes
    assert "application_artifact_inventory_overclaim" in codes
    assert "invalid_claim_boundaries_not_formal_theorem_prover" in codes
    assert "claim_category_mismatch" in codes


def test_validate_alphaevolve_theoretical_cs_source_manifest_rejects_surface_and_policy_drift():
    recordset = alphaevolve_theoretical_cs_source_manifest_record()
    source = recordset["sources"][0]
    source["manifest_row_id"] = "2506.13131"
    source["theoretical_cs_source_id"] = "2509.18057v6"
    source["claim_artifact_links"]["theoretical_cs_source_used_by"] = ["README.md"]
    source["claim_artifact_links"]["policy"] = "proofs_are_implemented"
    source["evidence_policy"]["publication_ready_without_artifact_inventory"] = True
    source["evidence_policy"]["scope"] = "original AlphaEvolve specification"

    validation = validate_alphaevolve_theoretical_cs_source_manifest(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_manifest_manifest_row_id" in codes
    assert "invalid_manifest_theoretical_cs_source_id" in codes
    assert "claim_surface_mismatch" in codes
    assert "invalid_claim_policy" in codes
    assert "invalid_evidence_policy_publication_ready_without_artifact_inventory" in codes
    assert "invalid_evidence_policy_scope" in codes
