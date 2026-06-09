import json

from libreevolve.problems.benchmarks.companion_sources import (
    ALPHAEVOLVE_COMPANION_COLAB_SCHEMA,
    alphaevolve_companion_colab_source_record,
    alphaevolve_companion_source_manifest_record,
    render_alphaevolve_companion_colab_source_summary,
    validate_alphaevolve_companion_colab_source,
    validate_alphaevolve_companion_source_manifest,
)


def test_validate_alphaevolve_companion_colab_source_accepts_builtin_record():
    recordset = alphaevolve_companion_colab_source_record()

    validation = validate_alphaevolve_companion_colab_source(recordset)

    assert recordset["schema"] == ALPHAEVOLVE_COMPANION_COLAB_SCHEMA
    assert validation.ok is True
    assert validation.artifact_count == 1
    assert validation.claim_mapping_count == 2
    assert validation.local_cache_available is False
    assert validation.issues == []


def test_validate_alphaevolve_companion_colab_source_loads_json_file(tmp_path):
    path = tmp_path / "companion_source.json"
    path.write_text(json.dumps(alphaevolve_companion_colab_source_record()), encoding="utf-8")

    validation = validate_alphaevolve_companion_colab_source(path)

    assert validation.ok is True


def test_validate_alphaevolve_companion_source_manifest_accepts_builtin_record():
    recordset = alphaevolve_companion_source_manifest_record()

    validation = validate_alphaevolve_companion_source_manifest(recordset)

    assert validation.ok is True
    assert validation.artifact_count == 1
    assert validation.claim_mapping_count == 2
    assert validation.local_cache_available is False
    assert validation.issues == []


def test_validate_alphaevolve_companion_source_manifest_rejects_surface_and_policy_drift():
    recordset = alphaevolve_companion_source_manifest_record()
    source = recordset["sources"][0]
    source["manifest_row_id"] = "2506.99999"
    source["companion_source_id"] = "other"
    source["claim_artifact_links"]["companion_source_used_by"] = ["README.md"]
    source["claim_artifact_links"]["policy"] = "same_as_local_export"
    source["local_cache_policy"]["cache_required_for_manifest_validation"] = True
    source["local_cache_policy"]["scope"] = "local export evidence"

    validation = validate_alphaevolve_companion_source_manifest(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_manifest_source_row_id" in codes
    assert "invalid_manifest_companion_source_id" in codes
    assert "claim_artifact_surface_mismatch" in codes
    assert "invalid_claim_artifact_policy" in codes
    assert "invalid_local_cache_policy_cache_required_for_manifest_validation" in codes
    assert "invalid_local_cache_policy_scope" in codes


def test_validate_alphaevolve_companion_colab_source_rejects_repository_and_digest_drift():
    recordset = alphaevolve_companion_colab_source_record()
    recordset["repository"]["commit"] = "0" * 40
    recordset["notebook"]["raw_url"] = "https://example.com/mathematical_results.ipynb"
    recordset["notebook"]["sha256"] = "1" * 64
    recordset["notebook"]["bytes"] = 0
    recordset["notebook"]["nbformat"] = 3
    recordset["notebook"]["cell_count"] = 1
    recordset["notebook"]["readability_check"] = "unchecked"

    validation = validate_alphaevolve_companion_colab_source(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "repository_commit_drift" in codes
    assert "invalid_raw_url" in codes
    assert "invalid_notebook_sha256" in codes
    assert "invalid_notebook_bytes" in codes
    assert "invalid_nbformat" in codes
    assert "invalid_cell_count" in codes
    assert "invalid_readability_check" in codes


def test_validate_alphaevolve_companion_colab_source_rejects_selection_overclaims():
    recordset = alphaevolve_companion_colab_source_record()
    recordset["selection_policy"]["inclusion_rule"] = "all_results"
    recordset["selection_policy"]["excluded_result_policy"] = "none_excluded"
    recordset["selection_policy"]["runtime_code_available"] = True
    recordset["selection_policy"]["readme_source_phrase"] = "all results"
    recordset["selection_policy"]["readme_exclusion_phrase"] = "nothing excluded"
    recordset["selection_policy"]["runtime_absence_phrase"] = "runtime included"

    validation = validate_alphaevolve_companion_colab_source(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_inclusion_rule" in codes
    assert "invalid_excluded_result_policy" in codes
    assert "runtime_code_overclaim" in codes
    assert "missing_selection_source_phrase" in codes
    assert "missing_exclusion_source_phrase" in codes
    assert "missing_runtime_absence_phrase" in codes


def test_validate_alphaevolve_companion_colab_source_rejects_rights_drift():
    recordset = alphaevolve_companion_colab_source_record()
    recordset["rights"]["rights_holder"] = "LibreEvolve"
    recordset["rights"]["software_license"] = "MIT"
    recordset["rights"]["materials_license"] = "MIT"
    recordset["rights"]["as_is_disclaimer"] = False
    recordset["rights"]["official_google_product"] = True
    recordset["rights"]["source_phrase"] = "official product"
    recordset["rights"]["artifact_license_mapping"]["construction_data"] = "Apache-2.0"

    validation = validate_alphaevolve_companion_colab_source(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_rights_rights_holder" in codes
    assert "invalid_rights_software_license" in codes
    assert "invalid_rights_materials_license" in codes
    assert "invalid_rights_as_is_disclaimer" in codes
    assert "invalid_rights_official_google_product" in codes
    assert "artifact_license_mapping_mismatch" in codes
    assert "missing_rights_source_phrase" in codes


def test_validate_alphaevolve_companion_colab_source_rejects_claim_mapping_overclaims():
    recordset = alphaevolve_companion_colab_source_record()
    recordset["claim_mappings"] = recordset["claim_mappings"][:1]
    recordset["claim_mappings"][0]["coverage_status"] = "all_paper_results"
    recordset["claim_mappings"][0]["cell_markers"] = []
    recordset["claim_mappings"][0]["source_artifact_ref"] = "local.ipynb"
    recordset["claim_mappings"][0]["local_reproduction_artifact_ref"] = "runs/out.ipynb"
    recordset["claim_mappings"][0]["local_export_equivalent"] = True

    validation = validate_alphaevolve_companion_colab_source(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_claim_mapping" in codes
    assert "invalid_coverage_status" in codes
    assert "invalid_cell_markers" in codes
    assert "invalid_source_artifact_ref" in codes
    assert "local_reproduction_overclaim" in codes
    assert "local_export_overclaim" in codes


def test_render_alphaevolve_companion_colab_source_summary_reports_shape():
    summary = render_alphaevolve_companion_colab_source_summary(
        alphaevolve_companion_colab_source_record()
    )

    assert "AlphaEvolve companion Colab source evidence" in summary
    assert "| schema_status | ok |" in summary
    assert "| artifact_count | 1 |" in summary
    assert "| claim_mapping_count | 2 |" in summary
    assert "| local_cache_available | False |" in summary
