import copy
import json

from libreevolve.problems.benchmarks.follow_on_sources import (
    ALPHAEVOLVE_FOLLOW_ON_MATH_SOURCE_SCHEMA,
    alphaevolve_follow_on_math_source_record,
    render_alphaevolve_follow_on_math_source_summary,
    validate_alphaevolve_follow_on_math_source,
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


def test_validate_alphaevolve_follow_on_math_source_loads_json_file(tmp_path):
    path = tmp_path / "follow_on_source.json"
    path.write_text(json.dumps(alphaevolve_follow_on_math_source_record()), encoding="utf-8")

    validation = validate_alphaevolve_follow_on_math_source(path)

    assert validation.ok is True


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
    claims["numbered_page_inventory_validated"] = True
    claims["notebook_coverage"] = "all"
    claims["runtime_code_available"] = True
    claims["status_artifact_inventory_validated"] = True
    claims["notebook_artifact_kinds"] = ["problem_pages"]

    validation = validate_alphaevolve_follow_on_math_source(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_repository_claims_declared_problem_count" in codes
    assert "per_problem_inventory_validated_overclaim" in codes
    assert "numbered_page_inventory_validated_overclaim" in codes
    assert "invalid_repository_claims_notebook_coverage" in codes
    assert "runtime_code_overclaim" in codes
    assert "status_artifact_inventory_validated_overclaim" in codes
    assert "invalid_notebook_artifact_kinds" in codes


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
