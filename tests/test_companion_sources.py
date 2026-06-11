import json

from libreevolve.problems.benchmarks.companion_sources import (
    ALPHAEVOLVE_COMPANION_COLAB_SCHEMA,
    alphaevolve_companion_artifact_rights_record,
    alphaevolve_companion_colab_source_record,
    alphaevolve_companion_selection_scope_record,
    alphaevolve_companion_source_manifest_record,
    validate_alphaevolve_companion_artifact_rights,
    render_alphaevolve_companion_colab_source_summary,
    validate_alphaevolve_companion_colab_source,
    validate_alphaevolve_companion_selection_scope,
    validate_alphaevolve_companion_source_manifest,
)
from libreevolve.problems.benchmarks.appendix_b_registry import EXPECTED_APPENDIX_B_RESULT_IDS


def test_validate_alphaevolve_companion_colab_source_accepts_builtin_record():
    recordset = alphaevolve_companion_colab_source_record()

    validation = validate_alphaevolve_companion_colab_source(recordset)

    assert recordset["schema"] == ALPHAEVOLVE_COMPANION_COLAB_SCHEMA
    assert validation.ok is True
    assert validation.artifact_count == 1
    assert validation.claim_mapping_count == 2
    assert validation.local_cache_available is False
    assert validation.issues == []
    appendix_b_mapping = next(
        mapping
        for mapping in recordset["claim_mappings"]
        if mapping["claim_id"] == "appendix_b_constructive_math_improved_results"
    )
    assert appendix_b_mapping["appendix_b_expected_result_count"] == len(EXPECTED_APPENDIX_B_RESULT_IDS)
    assert appendix_b_mapping["appendix_b_expected_result_ids"] == list(EXPECTED_APPENDIX_B_RESULT_IDS)
    assert appendix_b_mapping["appendix_b_result_inventory_source"] == "alphaevolve_appendix_b.json result_row_boundary"


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


def test_validate_alphaevolve_companion_selection_scope_accepts_included_improved_claim():
    recordset = alphaevolve_companion_selection_scope_record(
        "appendix_a_matrix_improved_decompositions"
    )

    validation = validate_alphaevolve_companion_selection_scope(recordset)

    assert validation.ok is True
    assert validation.artifact_count == 1
    assert validation.claim_mapping_count == 1
    assert validation.issues == []


def test_validate_alphaevolve_companion_selection_scope_accepts_matched_absence():
    recordset = alphaevolve_companion_selection_scope_record(
        "appendix_b_constructive_math_improved_results",
        paper_result_relation="matched_not_outperformed",
        companion_notebook_coverage="intentionally_absent",
        absence_reason="matched_but_not_outperformed_excluded_to_avoid_clutter",
    )

    validation = validate_alphaevolve_companion_selection_scope(recordset)

    assert validation.ok is True
    assert validation.claim_mapping_count == 1
    assert validation.issues == []


def test_validate_alphaevolve_companion_selection_scope_rejects_overclaims():
    recordset = alphaevolve_companion_selection_scope_record(
        "appendix_a_matrix_improved_decompositions"
    )
    recordset["companion_notebook_coverage"] = "intentionally_absent"
    recordset["absence_reason"] = "matched_but_not_outperformed_excluded_to_avoid_clutter"
    recordset["alphaevolve_runtime_code_available"] = True
    recordset["selection_policy"]["inclusion_rule"] = "all_results"

    validation = validate_alphaevolve_companion_selection_scope(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_improved_result_coverage" in codes
    assert "unexpected_absence_reason" in codes
    assert "runtime_code_overclaim" in codes
    assert "invalid_selection_policy_inclusion_rule" in codes


def test_validate_alphaevolve_companion_artifact_rights_accepts_local_generated_artifact():
    recordset = alphaevolve_companion_artifact_rights_record("notebook")

    validation = validate_alphaevolve_companion_artifact_rights(recordset)

    assert validation.ok is True
    assert validation.artifact_count == 1
    assert validation.issues == []


def test_validate_alphaevolve_companion_artifact_rights_accepts_companion_material():
    recordset = alphaevolve_companion_artifact_rights_record(
        "certificate",
        material_type="verification_code",
        source_relationship="adapted_from_companion_repository",
    )

    validation = validate_alphaevolve_companion_artifact_rights(recordset)

    assert validation.ok is True
    assert recordset["license"] == "Apache-2.0"
    assert recordset["rights_holder"] == "Google LLC"
    assert validation.issues == []


def test_validate_alphaevolve_companion_artifact_rights_rejects_license_and_boundary_drift():
    recordset = alphaevolve_companion_artifact_rights_record(
        "construction_data",
        material_type="construction_data",
        source_relationship="copied_from_companion_repository",
    )
    recordset["license"] = "MIT"
    recordset["rights_holder"] = "LibreEvolve"
    recordset["as_is_disclaimer_applies"] = False
    recordset["must_keep_source_pdf_rights_separate"] = False
    recordset["official_google_product"] = True

    validation = validate_alphaevolve_companion_artifact_rights(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_material_license" in codes
    assert "invalid_rights_holder" in codes
    assert "missing_as_is_disclaimer" in codes
    assert "invalid_must_keep_source_pdf_rights_separate" in codes
    assert "invalid_official_google_product" in codes


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


def test_validate_alphaevolve_companion_colab_source_rejects_appendix_b_inventory_drift():
    recordset = alphaevolve_companion_colab_source_record()
    mapping = next(
        mapping
        for mapping in recordset["claim_mappings"]
        if mapping["claim_id"] == "appendix_b_constructive_math_improved_results"
    )
    mapping["appendix_b_expected_result_count"] = 1
    mapping["appendix_b_expected_result_ids"] = ["b1_c1_600_interval_step_function"]
    mapping["appendix_b_result_inventory_source"] = "README.md"

    validation = validate_alphaevolve_companion_colab_source(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_appendix_b_expected_result_count" in codes
    assert "invalid_appendix_b_expected_result_ids" in codes
    assert "invalid_appendix_b_result_inventory_source" in codes


def test_render_alphaevolve_companion_colab_source_summary_reports_shape():
    summary = render_alphaevolve_companion_colab_source_summary(
        alphaevolve_companion_colab_source_record()
    )

    assert "AlphaEvolve companion Colab source evidence" in summary
    assert "| schema_status | ok |" in summary
    assert "| artifact_count | 1 |" in summary
    assert "| claim_mapping_count | 2 |" in summary
    assert "| local_cache_available | False |" in summary
