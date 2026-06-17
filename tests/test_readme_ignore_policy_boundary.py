from libreevolve.problems.benchmarks.readme_ignore_policy_boundary import (
    README_IGNORE_POLICY_BOUNDARY_SCHEMA,
    readme_ignore_policy_boundary_record,
    render_readme_ignore_policy_boundary_summary,
    validate_readme_ignore_policy_boundary,
)


def test_readme_ignore_policy_boundary_accepts_current_static_map():
    boundary = readme_ignore_policy_boundary_record()

    validation = validate_readme_ignore_policy_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_ignore_policy_static_inventory_with_rule_rationale_map_without_retention_drift_gate"
    )
    assert boundary["schema"] == README_IGNORE_POLICY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["gitignore_path"] == ".gitignore"
    assert validation.ignore_rule_count == 27
    assert validation.allowlist_rule_count == 5
    assert validation.missing_rule_count == 0
    assert validation.rule_rationale_map_count == 32
    assert boundary["missing_rule_records"] == []
    assert (
        boundary["rule_rationale_map_status"]
        == "all_expected_gitignore_rules_have_rationale_map"
    )
    assert boundary["rule_rationale_map_records"][0]["map_status"] == "mapped"
    assert boundary["rule_rationale_map_records"][0]["artifact_class"] == "python_cache"
    assert boundary["papers_ignore_rule_status"] == "papers_wildcard_ignored"
    assert boundary["paper_manifest_allowlist_status"] == (
        "core_paper_manifests_allowlisted"
    )
    assert boundary["gitignore_workflow_filter_status"] == (
        "gitignore_not_in_workflow_path_filters"
    )
    assert validation.evidence_anchor_count == 14
    assert validation.missing_evidence_anchor_count == 0
    assert boundary["missing_evidence_anchor_records"] == []
    assert boundary["ignore_policy_map_status"] == (
        "readme_ignore_policy_static_map_present_with_gitignore_filter_gap"
    )
    assert boundary["missing_evidence"] == {
        "tracked_vs_ignored_sidecar_inventory": "not_recorded_locally",
        "gitignore_workflow_path_filter": "not_recorded_locally",
        "retention_policy_drift_gate": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert ".gitignore ignore-rule inventory" in boundary["claim_boundary"]
    assert (
        ".gitignore is not currently included in workflow path filters"
        in boundary["claim_boundary"]
    )
    assert (
        "rationale map for every expected ignore and allowlist rule"
        in boundary["claim_boundary"]
    )


def test_readme_ignore_policy_boundary_rejects_overclaim_and_drift():
    boundary = readme_ignore_policy_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "readme_ignore_policy_retention_drift_gate_ready"
    boundary["ignore_rule_count"] = 0
    boundary["allowlist_rule_count"] = 0
    boundary["missing_rule_count"] = 1
    boundary["missing_rule_records"] = [boundary["ignore_rule_records"][0]]
    boundary["ignore_rule_records"][0]["rule_status"] = "rule_missing"
    boundary["rule_rationale_map_count"] = 0
    boundary["rule_rationale_map_status"] = "gitignore_rule_rationale_map_incomplete"
    boundary["rule_rationale_map_records"][0]["map_status"] = "missing_rationale_or_anchor"
    boundary["papers_ignore_rule_status"] = "papers_wildcard_not_ignored"
    boundary["paper_manifest_allowlist_status"] = "core_paper_manifests_not_allowlisted"
    boundary["gitignore_workflow_filter_status"] = "gitignore_in_workflow_path_filters"
    boundary["evidence_anchor_count"] = 0
    boundary["missing_evidence_anchor_count"] = 2
    boundary["missing_evidence_anchor_records"] = [
        boundary["evidence_anchor_records"][0]
    ]
    boundary["evidence_anchor_records"][0]["marker_status"] = "marker_missing"
    boundary["ignore_policy_map_status"] = "readme_ignore_policy_static_map_incomplete"
    boundary["missing_evidence"]["retention_policy_drift_gate"] = "recorded"
    boundary["required_evidence_fields"] = ["gitignore_ignore_rule_inventory"]

    validation = validate_readme_ignore_policy_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_ignore_rule_count" in codes
    assert "invalid_allowlist_rule_count" in codes
    assert "invalid_missing_rule_count" in codes
    assert "invalid_missing_rule_records" in codes
    assert "invalid_ignore_rule_records" in codes
    assert "missing_gitignore_rule" in codes
    assert "invalid_rule_rationale_map_count" in codes
    assert "invalid_rule_rationale_map_records" in codes
    assert "invalid_rule_rationale_map_status" in codes
    assert "invalid_papers_ignore_rule_status" in codes
    assert "invalid_paper_manifest_allowlist_status" in codes
    assert "invalid_gitignore_workflow_filter_status" in codes
    assert "unexpected_gitignore_workflow_filter_status" in codes
    assert "invalid_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_records" in codes
    assert "invalid_evidence_anchor_records" in codes
    assert "missing_ignore_policy_evidence_anchor" in codes
    assert "invalid_ignore_policy_map_status" in codes
    assert "invalid_missing_evidence_retention_policy_drift_gate" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_ignore_policy_boundary_summary_reports_shape():
    summary = render_readme_ignore_policy_boundary_summary(
        readme_ignore_policy_boundary_record()
    )

    assert "README ignore-policy boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_ignore_policy_static_inventory_with_rule_rationale_map_without_retention_drift_gate |"
        in summary
    )
    assert "| ignore_rule_count | 27 |" in summary
    assert "| allowlist_rule_count | 5 |" in summary
    assert "| missing_rule_count | 0 |" in summary
    assert "| rule_rationale_map_count | 32 |" in summary
    assert "| evidence_anchor_count | 14 |" in summary
    assert "| missing_evidence_anchor_count | 0 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
