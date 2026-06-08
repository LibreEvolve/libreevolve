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
    inventory = recordset["numbered_page_inventory"]
    inventory["observed_numbered_html_count"] = 67
    inventory["extra_numbered_page_ids"] = []
    inventory["full_page_link_diagnostics_complete"] = True

    validation = validate_alphaevolve_follow_on_problem_coverage(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "notebook_inventory_complete_overclaim" in codes
    assert "page_hash_inventory_complete_overclaim" in codes
    assert "notebook_hash_inventory_complete_overclaim" in codes
    assert "artifact_presence_matrix_complete_overclaim" in codes
    assert "invalid_numbered_page_inventory_observed_numbered_html_count" in codes
    assert "invalid_numbered_page_inventory_extra_numbered_page_ids" in codes
    assert "full_page_link_diagnostics_overclaim" in codes


def test_render_alphaevolve_follow_on_problem_coverage_summary_reports_shape():
    summary = render_alphaevolve_follow_on_problem_coverage_summary()

    assert "AlphaEvolve follow-on problem coverage evidence" in summary
    assert "| schema_status | ok |" in summary
    assert "| declared_problem_count | 67 |" in summary
    assert "| listed_status_count | 43 |" in summary
    assert "| unclassified_problem_count | 24 |" in summary
    assert "| status_artifact_count | 3 |" in summary
    assert "| observed_numbered_html_count | 68 |" in summary
