import copy
import json

from libreevolve.problems.benchmarks.follow_on_sources import (
    ALPHAEVOLVE_FOLLOW_ON_MATH_SOURCE_SCHEMA,
    alphaevolve_follow_on_math_source_record,
    alphaevolve_follow_on_repository_rights_manifest_record,
    alphaevolve_follow_on_repository_rights_record,
    alphaevolve_follow_on_runtime_absence_manifest_record,
    alphaevolve_follow_on_runtime_absence_record,
    alphaevolve_follow_on_source_manifest_record,
    alphaevolve_follow_on_tao_blog_manifest_record,
    alphaevolve_follow_on_tao_blog_record,
    render_alphaevolve_follow_on_math_source_summary,
    validate_alphaevolve_follow_on_math_source,
    validate_alphaevolve_follow_on_repository_rights,
    validate_alphaevolve_follow_on_repository_rights_manifest,
    validate_alphaevolve_follow_on_runtime_absence,
    validate_alphaevolve_follow_on_runtime_absence_manifest,
    validate_alphaevolve_follow_on_source_manifest,
    validate_alphaevolve_follow_on_tao_blog,
    validate_alphaevolve_follow_on_tao_blog_manifest,
)
from libreevolve.tools.paper_manifest import validate_paper_manifest


def test_validate_alphaevolve_follow_on_math_source_accepts_builtin_record():
    recordset = alphaevolve_follow_on_math_source_record()

    validation = validate_alphaevolve_follow_on_math_source(recordset)

    assert recordset["schema"] == ALPHAEVOLVE_FOLLOW_ON_MATH_SOURCE_SCHEMA
    assert validation.ok is True
    assert validation.source_count == 2
    assert validation.repository_ref_pinned is True
    assert validation.local_pdf_cache_available is False
    assert validation.issues == []
    claims = recordset["repository_claims"]
    assert claims["numbered_page_inventory_validated"] is True
    coverage = recordset["problem_coverage_evidence"]
    assert coverage["schema"] == "libreevolve.alphaevolve_follow_on_problem_coverage.v1"
    assert coverage["observed_numbered_html_count"] == 68
    assert coverage["extra_numbered_page_ids"] == [68]
    assert coverage["page_68_classification_complete"] is True
    assert coverage["resource_link_diagnostics_complete_for_pages_67_68"] is True
    assert coverage["all_page_resource_link_diagnostics_complete"] is True
    assert coverage["per_problem_inventory_validated"] is False
    assert coverage["page_hash_inventory_complete"] is True


def test_validate_alphaevolve_follow_on_math_source_loads_json_file(tmp_path):
    path = tmp_path / "follow_on_source.json"
    path.write_text(json.dumps(alphaevolve_follow_on_math_source_record()), encoding="utf-8")

    validation = validate_alphaevolve_follow_on_math_source(path)

    assert validation.ok is True


def test_validate_alphaevolve_follow_on_source_manifest_accepts_builtin_record():
    recordset = alphaevolve_follow_on_source_manifest_record()

    validation = validate_alphaevolve_follow_on_source_manifest(recordset)

    assert validation.ok is True
    assert validation.source_count == 1
    assert validation.repository_ref_pinned is True
    assert validation.local_pdf_cache_available is False
    assert validation.issues == []


def test_validate_alphaevolve_follow_on_source_manifest_loads_json_file(tmp_path):
    path = tmp_path / "follow_on_sources.json"
    path.write_text(
        json.dumps(alphaevolve_follow_on_source_manifest_record()),
        encoding="utf-8",
    )

    validation = validate_alphaevolve_follow_on_source_manifest(path)

    assert validation.ok is True


def test_validate_alphaevolve_follow_on_source_manifest_rejects_surface_and_cache_policy_drift():
    recordset = alphaevolve_follow_on_source_manifest_record()
    source = recordset["sources"][0]
    source["manifest_row_id"] = "2506.13131"
    source["follow_on_source_id"] = "2511.02864v2"
    source["claim_artifact_links"]["follow_on_source_used_by"] = ["README.md"]
    source["claim_artifact_links"]["policy"] = "same_as_cached_pdf"
    source["cache_policy"]["paper_cache_manifest_row_required"] = True
    source["cache_policy"]["scope"] = "cached PDF evidence"
    source["remaining_work"] = ["build_per_problem_repository_inventory"]

    validation = validate_alphaevolve_follow_on_source_manifest(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_manifest_source_row_id" in codes
    assert "invalid_manifest_follow_on_source_id" in codes
    assert "claim_artifact_surface_mismatch" in codes
    assert "invalid_claim_artifact_policy" in codes
    assert "invalid_cache_policy_paper_cache_manifest_row_required" in codes
    assert "invalid_cache_policy_scope" in codes
    assert "manifest_remaining_work_mismatch" in codes


def test_validate_alphaevolve_follow_on_repository_rights_accepts_builtin_record():
    recordset = alphaevolve_follow_on_repository_rights_record()

    validation = validate_alphaevolve_follow_on_repository_rights(recordset)

    assert validation.ok is True
    assert validation.rights_count == 1
    assert validation.citation_required is True
    assert validation.artifact_license_mapping_count == 11
    assert validation.issues == []


def test_validate_alphaevolve_follow_on_repository_rights_manifest_accepts_builtin_record():
    recordset = alphaevolve_follow_on_repository_rights_manifest_record()

    validation = validate_alphaevolve_follow_on_repository_rights_manifest(recordset)

    assert validation.ok is True
    assert validation.rights_count == 1
    assert validation.citation_required is True
    assert validation.artifact_license_mapping_count == 11
    assert validation.issues == []


def test_validate_alphaevolve_follow_on_repository_rights_loads_json_file(tmp_path):
    path = tmp_path / "follow_on_repository_rights.json"
    path.write_text(
        json.dumps(alphaevolve_follow_on_repository_rights_manifest_record()),
        encoding="utf-8",
    )

    validation = validate_alphaevolve_follow_on_repository_rights_manifest(path)

    assert validation.ok is True


def test_validate_alphaevolve_follow_on_repository_rights_rejects_source_use_drift():
    recordset = copy.deepcopy(alphaevolve_follow_on_repository_rights_record())
    recordset["repository"]["commit"] = "0" * 40
    recordset["citation"]["required"] = False
    recordset["citation"]["arxiv_id"] = "2506.13131"
    recordset["rights"]["software_license"] = "MIT"
    recordset["rights"]["artifact_license_mapping"]["problem_pages"] = "Apache-2.0"
    recordset["disclaimers"]["official_google_product"] = True
    recordset["role_attribution"]["contributors"][0]["roles"] = ["review"]
    recordset["third_party_origins"][0]["url"] = "https://example.com"
    recordset["boundary"]["distinct_from_libreevolve_mit_license"] = False

    validation = validate_alphaevolve_follow_on_repository_rights(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_repository_rights_repository_commit" in codes
    assert "invalid_repository_rights_citation_required" in codes
    assert "invalid_repository_rights_citation_arxiv_id" in codes
    assert "invalid_repository_rights_software_license" in codes
    assert "repository_rights_artifact_license_mapping_mismatch" in codes
    assert "invalid_repository_rights_disclaimers_official_google_product" in codes
    assert "repository_rights_contributor_roles_mismatch" in codes
    assert "invalid_repository_rights_third_party_origin_url" in codes
    assert "invalid_repository_rights_boundary_distinct_from_libreevolve_mit_license" in codes


def test_validate_alphaevolve_follow_on_repository_rights_manifest_rejects_surface_and_policy_drift():
    recordset = alphaevolve_follow_on_repository_rights_manifest_record()
    source = recordset["sources"][0]
    source["manifest_row_id"] = "2506.13131"
    source["follow_on_source_manifest"] = "papers/companion_sources.json"
    source["repository_rights_id"] = "other"
    source["claim_artifact_links"]["repository_rights_used_by"] = ["README.md"]
    source["claim_artifact_links"]["policy"] = "same_as_libreevolve_license"
    source["reuse_policy"]["publication_ready_without_rights_review"] = True
    source["reuse_policy"]["scope"] = "LibreEvolve project licensing"

    validation = validate_alphaevolve_follow_on_repository_rights_manifest(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_repository_rights_manifest_manifest_row_id" in codes
    assert "invalid_repository_rights_manifest_follow_on_source_manifest" in codes
    assert "invalid_repository_rights_manifest_repository_rights_id" in codes
    assert "repository_rights_claim_surface_mismatch" in codes
    assert "invalid_repository_rights_claim_policy" in codes
    assert "invalid_repository_rights_reuse_policy_publication_ready_without_rights_review" in codes
    assert "invalid_repository_rights_reuse_policy_scope" in codes


def test_validate_alphaevolve_follow_on_runtime_absence_accepts_builtin_record():
    recordset = alphaevolve_follow_on_runtime_absence_record()

    validation = validate_alphaevolve_follow_on_runtime_absence(recordset)

    assert validation.ok is True
    assert validation.runtime_absence_count == 1
    assert validation.notebook_count == 28
    assert validation.alphaevolve_runtime_available is False
    assert validation.verifier_code_available is True
    assert validation.issues == []


def test_validate_alphaevolve_follow_on_runtime_absence_manifest_accepts_builtin_record():
    recordset = alphaevolve_follow_on_runtime_absence_manifest_record()

    validation = validate_alphaevolve_follow_on_runtime_absence_manifest(recordset)

    assert validation.ok is True
    assert validation.runtime_absence_count == 1
    assert validation.notebook_count == 28
    assert validation.alphaevolve_runtime_available is False
    assert validation.verifier_code_available is True
    assert validation.issues == []


def test_validate_alphaevolve_follow_on_runtime_absence_loads_json_file(tmp_path):
    path = tmp_path / "follow_on_runtime_absence.json"
    path.write_text(
        json.dumps(alphaevolve_follow_on_runtime_absence_manifest_record()),
        encoding="utf-8",
    )

    validation = validate_alphaevolve_follow_on_runtime_absence_manifest(path)

    assert validation.ok is True


def test_validate_alphaevolve_follow_on_runtime_absence_rejects_runtime_drift():
    recordset = copy.deepcopy(alphaevolve_follow_on_runtime_absence_record())
    recordset["repository"]["commit"] = "0" * 40
    recordset["notebook_inventory"]["notebooks"][0]["git_blob_sha"] = "0" * 40
    recordset["notebook_inventory"]["notebooks"][0]["artifact_kinds"] = ["runtime"]
    recordset["notebook_inventory"]["notebooks"][0]["alphaevolve_runtime_available"] = True
    recordset["runtime_boundary"]["alphaevolve_runtime_available"] = True
    recordset["runtime_boundary"]["verifier_is_not_runtime"] = False
    recordset["runtime_boundary"]["absence_source_phrase"] = "runtime included"

    validation = validate_alphaevolve_follow_on_runtime_absence(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_runtime_available is True
    assert "invalid_runtime_absence_repository_commit" in codes
    assert "invalid_runtime_absence_notebook_git_blob_sha" in codes
    assert "invalid_runtime_absence_notebook_artifact_kinds" in codes
    assert "runtime_absence_notebook_runtime_available_overclaim" in codes
    assert "runtime_absence_runtime_available_overclaim" in codes
    assert "runtime_absence_verifier_runtime_boundary_missing" in codes
    assert "invalid_runtime_absence_boundary_absence_source_phrase" in codes


def test_validate_alphaevolve_follow_on_runtime_absence_manifest_rejects_surface_and_policy_drift():
    recordset = alphaevolve_follow_on_runtime_absence_manifest_record()
    source = recordset["sources"][0]
    source["manifest_row_id"] = "2506.13131"
    source["follow_on_source_manifest"] = "papers/companion_sources.json"
    source["runtime_absence_id"] = "other"
    source["claim_artifact_links"]["runtime_absence_used_by"] = ["README.md"]
    source["claim_artifact_links"]["policy"] = "notebook_runtime"
    source["runtime_claim_policy"]["alphaevolve_runtime_available"] = True
    source["runtime_claim_policy"]["publication_ready_runtime_claim"] = True
    source["runtime_claim_policy"]["scope"] = "full notebook inventory"

    validation = validate_alphaevolve_follow_on_runtime_absence_manifest(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_runtime_absence_manifest_manifest_row_id" in codes
    assert "invalid_runtime_absence_manifest_follow_on_source_manifest" in codes
    assert "invalid_runtime_absence_manifest_runtime_absence_id" in codes
    assert "runtime_absence_claim_surface_mismatch" in codes
    assert "invalid_runtime_absence_claim_policy" in codes
    assert "invalid_runtime_claim_policy_alphaevolve_runtime_available" in codes
    assert "invalid_runtime_claim_policy_publication_ready_runtime_claim" in codes
    assert "invalid_runtime_claim_policy_scope" in codes


def test_validate_alphaevolve_follow_on_tao_blog_accepts_builtin_record():
    recordset = alphaevolve_follow_on_tao_blog_record()

    validation = validate_alphaevolve_follow_on_tao_blog(recordset)

    assert validation.ok is True
    assert validation.source_count == 1
    assert validation.claim_category_count == 6
    assert validation.linked_repository_pinned is True
    assert validation.commentary_secondary is True
    assert validation.issues == []


def test_validate_alphaevolve_follow_on_tao_blog_manifest_accepts_builtin_record():
    recordset = alphaevolve_follow_on_tao_blog_manifest_record()

    validation = validate_alphaevolve_follow_on_tao_blog_manifest(recordset)

    assert validation.ok is True
    assert validation.source_count == 1
    assert validation.claim_category_count == 6
    assert validation.linked_repository_pinned is True
    assert validation.commentary_secondary is True
    assert validation.issues == []


def test_validate_alphaevolve_follow_on_tao_blog_loads_json_file(tmp_path):
    path = tmp_path / "follow_on_tao_blog.json"
    path.write_text(
        json.dumps(alphaevolve_follow_on_tao_blog_manifest_record()),
        encoding="utf-8",
    )

    validation = validate_alphaevolve_follow_on_tao_blog_manifest(path)

    assert validation.ok is True


def test_validate_alphaevolve_follow_on_tao_blog_rejects_source_drift():
    recordset = copy.deepcopy(alphaevolve_follow_on_tao_blog_record())
    recordset["canonical_url"] = "https://example.com"
    recordset["post"]["post_date"] = "2025-11-06T00:00:00+00:00"
    recordset["retrieval"]["api_sha256"] = "0" * 64
    recordset["linked_sources"]["problem_repository_commit"] = "0" * 40
    recordset["claim_spans"][1]["category"] = "runtime_spec"
    recordset["claim_spans"][2]["requires_backing_artifact"] = False
    recordset["claim_boundary"]["blog_commentary_secondary"] = False

    validation = validate_alphaevolve_follow_on_tao_blog(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.linked_repository_pinned is False
    assert validation.commentary_secondary is False
    assert "invalid_tao_blog_canonical_url" in codes
    assert "invalid_tao_blog_post_post_date" in codes
    assert "invalid_tao_blog_retrieval_api_sha256" in codes
    assert "invalid_tao_blog_linked_problem_repository_commit" in codes
    assert "invalid_tao_blog_claim_category" in codes
    assert "tao_blog_claim_backing_artifact_missing" in codes
    assert "invalid_tao_blog_claim_boundary_blog_commentary_secondary" in codes


def test_validate_alphaevolve_follow_on_tao_blog_manifest_rejects_surface_and_policy_drift():
    recordset = alphaevolve_follow_on_tao_blog_manifest_record()
    source = recordset["sources"][0]
    source["manifest_row_id"] = "2506.13131"
    source["follow_on_source_manifest"] = "papers/companion_sources.json"
    source["tao_blog_source_id"] = "other"
    source["claim_artifact_links"]["tao_blog_used_by"] = ["README.md"]
    source["claim_artifact_links"]["policy"] = "blog_is_primary_spec"
    source["evidence_policy"]["publication_ready_without_backing_artifacts"] = True
    source["evidence_policy"]["comment_thread_included"] = True
    source["evidence_policy"]["scope"] = "original AlphaEvolve specification"

    validation = validate_alphaevolve_follow_on_tao_blog_manifest(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_tao_blog_manifest_manifest_row_id" in codes
    assert "invalid_tao_blog_manifest_follow_on_source_manifest" in codes
    assert "invalid_tao_blog_manifest_tao_blog_source_id" in codes
    assert "tao_blog_claim_surface_mismatch" in codes
    assert "invalid_tao_blog_claim_policy" in codes
    assert "invalid_tao_blog_evidence_policy_publication_ready_without_backing_artifacts" in codes
    assert "invalid_tao_blog_evidence_policy_comment_thread_included" in codes
    assert "invalid_tao_blog_evidence_policy_scope" in codes


def test_validate_alphaevolve_follow_on_math_source_rejects_paper_identity_and_cache_overclaims():
    recordset = copy.deepcopy(alphaevolve_follow_on_math_source_record())
    recordset["paper"]["version"] = 2
    recordset["paper"]["versioned_id"] = "2511.02864v2"
    recordset["paper"]["authors"] = ["Anonymous"]
    recordset["paper"]["local_cache"]["available"] = True
    recordset["paper"]["local_cache"]["manifest_row_present"] = True
    recordset["paper"]["local_cache"]["file"] = "papers/2511.02864.pdf"
    recordset["paper"]["local_cache"]["sha256"] = "0" * 64
    recordset["paper"]["local_cache"]["bytes"] = 1

    validation = validate_alphaevolve_follow_on_math_source(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_paper_version" in codes
    assert "invalid_paper_versioned_id" in codes
    assert "invalid_paper_authors" in codes
    assert "local_pdf_cache_overclaim" in codes
    assert "manifest_row_overclaim" in codes
    assert "local_cache_file_overclaim" in codes
    assert "local_cache_sha256_overclaim" in codes
    assert "local_cache_bytes_overclaim" in codes


def test_validate_alphaevolve_follow_on_math_source_rejects_repository_drift():
    recordset = copy.deepcopy(alphaevolve_follow_on_math_source_record())
    recordset["repository"]["default_branch"] = "master"
    recordset["repository"]["commit"] = "0" * 40
    recordset["repository"]["readme_sha256"] = "1" * 64
    recordset["repository"]["readme_bytes"] = 0
    recordset["repository"]["live_update_policy"] = "floating"

    validation = validate_alphaevolve_follow_on_math_source(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.repository_ref_pinned is False
    assert "invalid_repository_default_branch" in codes
    assert "repository_commit_drift" in codes
    assert "readme_sha256_drift" in codes
    assert "invalid_repository_readme_bytes" in codes
    assert "invalid_repository_live_update_policy" in codes


def test_validate_alphaevolve_follow_on_math_source_rejects_repository_claim_overclaims():
    recordset = copy.deepcopy(alphaevolve_follow_on_math_source_record())
    claims = recordset["repository_claims"]
    claims["declared_problem_count"] = 68
    claims["per_problem_inventory_validated"] = True
    claims["numbered_page_inventory_validated"] = False
    claims["notebook_coverage"] = "all"
    claims["runtime_code_available"] = True
    claims["status_artifact_inventory_validated"] = False
    claims["notebook_artifact_kinds"] = ["problem_pages"]
    coverage = recordset["problem_coverage_evidence"]
    coverage["observed_numbered_html_count"] = 67
    coverage["extra_numbered_page_ids"] = []
    coverage["page_68_classification_complete"] = False
    coverage["resource_link_diagnostics_complete_for_pages_67_68"] = False
    coverage["all_page_resource_link_diagnostics_complete"] = False
    coverage["per_problem_inventory_validated"] = True
    coverage["page_hash_inventory_complete"] = False
    coverage["claim_boundary"] = "Every numbered page is classified and hashed."

    validation = validate_alphaevolve_follow_on_math_source(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_repository_claims_declared_problem_count" in codes
    assert "per_problem_inventory_validated_overclaim" in codes
    assert "invalid_repository_claims_numbered_page_inventory_validated" in codes
    assert "invalid_repository_claims_notebook_coverage" in codes
    assert "runtime_code_overclaim" in codes
    assert "invalid_repository_claims_status_artifact_inventory_validated" in codes
    assert "invalid_notebook_artifact_kinds" in codes
    assert "invalid_problem_coverage_evidence_observed_numbered_html_count" in codes
    assert "invalid_problem_coverage_evidence_extra_numbered_page_ids" in codes
    assert "invalid_problem_coverage_evidence_page_68_classification_complete" in codes
    assert "invalid_problem_coverage_evidence_resource_link_diagnostics_complete_for_pages_67_68" in codes
    assert "invalid_problem_coverage_evidence_all_page_resource_link_diagnostics_complete" in codes
    assert "problem_coverage_evidence_per_problem_inventory_validated_overclaim" in codes
    assert "invalid_problem_coverage_evidence_page_hash_inventory_complete" in codes
    assert "missing_problem_coverage_claim_boundary" in codes


def test_validate_alphaevolve_follow_on_math_source_rejects_scope_and_source_use_drift():
    recordset = copy.deepcopy(alphaevolve_follow_on_math_source_record())
    recordset["scope_boundary"]["separates_original_spec_from_later_math_evidence"] = False
    recordset["scope_boundary"]["not_original_alphaevolve_runtime_spec"] = False
    recordset["source_use"]["repository_software_license"] = "MIT"
    recordset["source_use"]["repository_materials_license"] = "MIT"
    recordset["source_use"]["citation_required"] = False
    recordset["required_follow_on_work"] = ["build_per_problem_repository_inventory"]

    validation = validate_alphaevolve_follow_on_math_source(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_scope_boundary_separates_original_spec_from_later_math_evidence" in codes
    assert "invalid_scope_boundary_not_original_alphaevolve_runtime_spec" in codes
    assert "invalid_source_use_repository_software_license" in codes
    assert "invalid_source_use_repository_materials_license" in codes
    assert "invalid_source_use_citation_required" in codes
    assert "missing_required_follow_on_work" in codes


def test_render_alphaevolve_follow_on_math_source_summary_reports_shape():
    summary = render_alphaevolve_follow_on_math_source_summary()

    assert "AlphaEvolve follow-on math source evidence" in summary
    assert "| schema_status | ok |" in summary
    assert "| source_count | 2 |" in summary
    assert "| arxiv_version | v3 |" in summary
    assert "| declared_problem_count | 67 |" in summary
    assert "| repository_ref_pinned | True |" in summary
    assert "| local_pdf_cache_available | False |" in summary


def test_paper_manifest_rejects_follow_on_manifest_row_until_cache_boundary_updates(tmp_path):
    papers_dir = tmp_path / "papers"
    papers_dir.mkdir()
    row = {
        "id": "2511.02864",
        "title": "Mathematical exploration and discovery at scale",
        "url": "https://arxiv.org/pdf/2511.02864.pdf",
        "file": "papers/2511.02864.pdf",
        "ok": True,
        "bytes": 1,
        "sha256": "0" * 64,
        "message": "",
    }
    (papers_dir / "download_manifest.json").write_text(json.dumps([row]), encoding="utf-8")
    (papers_dir / "download_manifest.csv").write_text(
        "id,title,url,file,ok,bytes,sha256,message\n"
        "2511.02864,Mathematical exploration and discovery at scale,"
        "https://arxiv.org/pdf/2511.02864.pdf,papers/2511.02864.pdf,true,1,"
        f"{'0' * 64},\n",
        encoding="utf-8",
    )
    (papers_dir / "README.md").write_text(
        "## Implementation status\n\n"
        "| Paper | Status |\n"
        "|---|---|\n"
        "| `2511.02864` | tracked |\n\n"
        "## TODO coverage cross-references\n\n"
        "| Paper | Active TODOs | Completed TODOs |\n"
        "|---|---|---|\n"
        "| `2511.02864` | `docs/todo/papers.md` |  |\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert any(
        issue.code == "alphaevolve_follow_on_math_source_manifest_cache_boundary_mismatch"
        for issue in report.issues
    )
