from pathlib import Path

from libreevolve.problems.benchmarks.roadmap_non_goal_markdown_scan_boundary import (
    ROADMAP_NON_GOAL_MARKDOWN_SCAN_BOUNDARY_SCHEMA,
    _markdown_corpus_files,
    render_roadmap_non_goal_markdown_scan_boundary_summary,
    roadmap_non_goal_markdown_scan_boundary_record,
    validate_roadmap_non_goal_markdown_scan_boundary,
)


def test_roadmap_non_goal_markdown_scan_excludes_packaging_outputs(tmp_path):
    (tmp_path / "README.md").write_text("tracked\n", encoding="utf-8")
    for directory in ("build", "dist", "libreevolve.egg-info"):
        path = tmp_path / directory / "generated.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("generated\n", encoding="utf-8")

    assert _markdown_corpus_files(tmp_path) == [Path("README.md")]


def test_roadmap_non_goal_markdown_scan_accepts_current_corpus():
    boundary = roadmap_non_goal_markdown_scan_boundary_record()

    validation = validate_roadmap_non_goal_markdown_scan_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "markdown_corpus_scan_without_runtime_or_promotion_gate"
    )
    assert boundary["schema"] == ROADMAP_NON_GOAL_MARKDOWN_SCAN_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_non_goal_boundary_input"]
        == "papers/roadmap_non_goal_contradiction_boundary.json"
    )
    assert boundary["source_non_goal_count"] == 3
    assert boundary["source_constrained_surface_count"] == 9
    assert boundary["markdown_corpus_status"] == "all_repo_markdown_files_scanned"
    assert boundary["markdown_file_count"] == 27
    assert boundary["readable_markdown_file_count"] == 27
    assert boundary["unreadable_markdown_file_count"] == 0
    assert boundary["markdown_read_error_records"] == []
    assert "README.md" in boundary["markdown_files"]
    assert "ROADMAP.md" in boundary["markdown_files"]
    assert "papers/README.md" in boundary["markdown_files"]
    assert "docs/todo/roadmap.md" in boundary["markdown_files"]
    assert boundary["non_goal_count"] == 3
    assert boundary["forbidden_phrase_count"] == 17
    assert boundary["contradiction_count"] == 0
    assert all(
        record["detected_forbidden_claim_count"] == 0
        for record in boundary["non_goal_records"]
    )
    assert boundary["missing_evidence"] == {
        "runtime_metadata_scan": "not_recorded_locally",
        "plugin_docstring_scan": "not_recorded_locally",
        "ci_non_goal_promotion_gate": "not_recorded_locally",
        "intentional_promotion_workflow": "not_recorded_locally",
        "claim_surface_remediation": "not_recorded_locally",
        "runtime_plugin_scope_join": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "every Markdown file in the repository corpus" in boundary["claim_boundary"]


def test_roadmap_non_goal_markdown_scan_rejects_overclaim_and_drift():
    boundary = roadmap_non_goal_markdown_scan_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_non_goal_promotion_gate_ready"
    boundary["contradiction_count"] = 1
    boundary["non_goal_records"][0]["detected_forbidden_claim_records"] = [
        {
            "path": "README.md",
            "line_start": 1,
            "phrase": "requires a service database",
            "column_start": 1,
        }
    ]
    boundary["missing_evidence"]["runtime_metadata_scan"] = "recorded"
    boundary["required_evidence_fields"] = ["stable_non_goal_ids"]

    validation = validate_roadmap_non_goal_markdown_scan_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_contradiction_count" in codes
    assert "invalid_non_goal_records" in codes
    assert "contradiction_detected" in codes
    assert "invalid_missing_evidence_runtime_metadata_scan" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_non_goal_markdown_scan_summary_reports_shape():
    summary = render_roadmap_non_goal_markdown_scan_boundary_summary(
        roadmap_non_goal_markdown_scan_boundary_record()
    )

    assert "ROADMAP non-goal Markdown scan boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | markdown_corpus_scan_without_runtime_or_promotion_gate |"
        in summary
    )
    assert "| markdown_file_count | 27 |" in summary
    assert "| non_goal_count | 3 |" in summary
    assert "| forbidden_phrase_count | 17 |" in summary
    assert "| contradiction_count | 0 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
