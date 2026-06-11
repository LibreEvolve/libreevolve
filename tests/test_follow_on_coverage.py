import copy
import json

from libreevolve.problems.benchmarks.follow_on_coverage import (
    ALPHAEVOLVE_FOLLOW_ON_PROBLEM_COVERAGE_SCHEMA,
    alphaevolve_follow_on_problem_coverage_record,
    render_alphaevolve_follow_on_problem_coverage_summary,
    validate_alphaevolve_follow_on_problem_coverage,
)


def test_validate_alphaevolve_follow_on_problem_coverage_accepts_builtin_record():
    recordset = alphaevolve_follow_on_problem_coverage_record()

    validation = validate_alphaevolve_follow_on_problem_coverage(recordset)

    assert recordset["schema"] == ALPHAEVOLVE_FOLLOW_ON_PROBLEM_COVERAGE_SCHEMA
    assert validation.ok is True
    assert validation.declared_problem_count == 67
    assert validation.listed_status_count == 43
    assert validation.unclassified_problem_count == 24
    assert validation.status_artifact_count == 3
    assert validation.observed_numbered_html_count == 68
    assert validation.issues == []
    diagnostics = recordset["page_discrepancy_diagnostics"]
    assert diagnostics["classification"] == "page_68_extra_numbered_duplicate_title_outside_declared_67_navigation"
    assert diagnostics["classification_complete"] is True
    assert diagnostics["all_page_diagnostics_complete"] is False
    assert diagnostics["duplicate_title_groups"] == [
        {"title": "Logic puzzles", "page_ids": [67, 68], "paper_section": "6.44"}
    ]
    page68 = diagnostics["pages"][1]
    assert page68["page_id"] == 68
    assert page68["colab_link_status"] == "generic_colab_landing_page"
    assert page68["paper_link_status"] == "placeholder"
    link = recordset["notebook_inventory_link"]
    assert link["source_manifest"] == "papers/follow_on_runtime_absence.json"
    assert link["pinned_notebook_path_count"] == 28
    assert link["problem_id_mapping_complete"] is False
    assert link["sha256_inventory_complete"] is False
    assert link["absence_reason_inventory_complete"] is False


def test_validate_alphaevolve_follow_on_problem_coverage_loads_json_file(tmp_path):
    path = tmp_path / "follow_on_coverage.json"
    path.write_text(json.dumps(alphaevolve_follow_on_problem_coverage_record()), encoding="utf-8")

    validation = validate_alphaevolve_follow_on_problem_coverage(path)

    assert validation.ok is True


def test_validate_alphaevolve_follow_on_problem_coverage_rejects_repository_drift():
    recordset = copy.deepcopy(alphaevolve_follow_on_problem_coverage_record())
    recordset["repository"]["commit"] = "0" * 40
    recordset["repository"]["snapshot_date"] = "2026-06-09"
    recordset["repository"]["live_update_policy"] = "floating"

    validation = validate_alphaevolve_follow_on_problem_coverage(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_repository_commit" in codes
    assert "invalid_repository_snapshot_date" in codes
    assert "invalid_repository_live_update_policy" in codes


def test_validate_alphaevolve_follow_on_problem_coverage_rejects_status_artifact_drift():
    recordset = copy.deepcopy(alphaevolve_follow_on_problem_coverage_record())
    recordset["status_artifacts"][0]["sha256"] = "0" * 64
    recordset["status_artifacts"][1]["bytes"] = 1
    recordset["status_artifacts"].append(
        {"path": "assets/status_grid.png", "kind": "status_grid_image", "bytes": 1, "sha256": "1" * 64}
    )

    validation = validate_alphaevolve_follow_on_problem_coverage(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "status_artifact_sha256_drift" in codes
    assert "invalid_status_artifact_bytes" in codes
    assert "unexpected_status_artifact" in codes


def test_validate_alphaevolve_follow_on_problem_coverage_rejects_bucket_drift():
    recordset = copy.deepcopy(alphaevolve_follow_on_problem_coverage_record())
    recordset["status_buckets"]["world_record"].append(12)
    recordset["status_buckets"]["former_record"].append(12)
    recordset["status_buckets"]["matched_optimal"].append(68)
    recordset["status_summary"]["listed_problem_count"] = 46
    recordset["status_summary"]["unclassified_problem_ids"] = [13]
    recordset["status_summary"]["unclassified_problem_count"] = 1

    validation = validate_alphaevolve_follow_on_problem_coverage(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "status_bucket_membership_drift" in codes
    assert "duplicate_status_problem_id" in codes
    assert "status_problem_id_out_of_range" in codes
    assert "invalid_listed_status_count" in codes
    assert "invalid_status_summary_listed_problem_count" in codes
    assert "invalid_status_summary_unclassified_problem_ids" in codes
    assert "invalid_status_summary_unclassified_problem_count" in codes


def test_validate_alphaevolve_follow_on_problem_coverage_rejects_inventory_overclaims():
    recordset = copy.deepcopy(alphaevolve_follow_on_problem_coverage_record())
    scope = recordset["coverage_scope"]
    scope["notebook_inventory_complete"] = True
    scope["page_hash_inventory_complete"] = True
    scope["notebook_hash_inventory_complete"] = True
    scope["artifact_presence_matrix_complete"] = True
    link = recordset["notebook_inventory_link"]
    link["pinned_notebook_path_count"] = 67
    link["problem_id_mapping_complete"] = True
    link["sha256_inventory_complete"] = True
    link["absence_reason_inventory_complete"] = True
    link["claim_boundary"] = "Every problem has a mapped notebook."
    inventory = recordset["numbered_page_inventory"]
    inventory["observed_numbered_html_count"] = 67
    inventory["extra_numbered_page_ids"] = []
    inventory["full_page_link_diagnostics_complete"] = True
    diagnostics = recordset["page_discrepancy_diagnostics"]
    diagnostics["classification"] = "complete_declared_problem"
    diagnostics["all_page_diagnostics_complete"] = True
    diagnostics["duplicate_title_groups"] = []
    diagnostics["pages"][1]["colab_link_status"] = "valid_notebook"
    diagnostics["pages"][1]["paper_link_status"] = "valid"
    recordset["remaining_coverage_work"] = ["classify_extra_numbered_page_68"]

    validation = validate_alphaevolve_follow_on_problem_coverage(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "notebook_inventory_complete_overclaim" in codes
    assert "page_hash_inventory_complete_overclaim" in codes
    assert "notebook_hash_inventory_complete_overclaim" in codes
    assert "artifact_presence_matrix_complete_overclaim" in codes
    assert "invalid_notebook_inventory_link_pinned_notebook_path_count" in codes
    assert "notebook_inventory_link_problem_id_mapping_complete_overclaim" in codes
    assert "notebook_inventory_link_sha256_inventory_complete_overclaim" in codes
    assert "notebook_inventory_link_absence_reason_inventory_complete_overclaim" in codes
    assert "missing_notebook_inventory_link_claim_boundary" in codes
    assert "invalid_numbered_page_inventory_observed_numbered_html_count" in codes
    assert "invalid_numbered_page_inventory_extra_numbered_page_ids" in codes
    assert "full_page_link_diagnostics_overclaim" in codes
    assert "invalid_page_discrepancy_diagnostics_classification" in codes
    assert "page_discrepancy_all_page_diagnostics_overclaim" in codes
    assert "invalid_page_discrepancy_duplicate_title_groups" in codes
    assert "invalid_page_discrepancy_page_colab_link_status" in codes
    assert "invalid_page_discrepancy_page_paper_link_status" in codes
    assert "missing_remaining_coverage_work" in codes


def test_render_alphaevolve_follow_on_problem_coverage_summary_reports_shape():
    summary = render_alphaevolve_follow_on_problem_coverage_summary()

    assert "AlphaEvolve follow-on problem coverage evidence" in summary
    assert "| schema_status | ok |" in summary
    assert "| declared_problem_count | 67 |" in summary
    assert "| listed_status_count | 43 |" in summary
    assert "| unclassified_problem_count | 24 |" in summary
    assert "| status_artifact_count | 3 |" in summary
    assert "| observed_numbered_html_count | 68 |" in summary
