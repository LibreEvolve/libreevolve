from libreevolve.problems.benchmarks.tracked_legacy_surface_boundary import (
    TRACKED_LEGACY_SURFACE_BOUNDARY_SCHEMA,
    render_tracked_legacy_surface_boundary_summary,
    tracked_legacy_surface_boundary_record,
    validate_tracked_legacy_surface_boundary,
)


def test_tracked_legacy_surface_boundary_accepts_current_inventory():
    boundary = tracked_legacy_surface_boundary_record()

    validation = validate_tracked_legacy_surface_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "tracked_legacy_surface_inventory_without_owner_review_signoff"
    )
    assert boundary["schema"] == TRACKED_LEGACY_SURFACE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["legacy_root"] == "old"
    assert boundary["legacy_surface_count"] == 1
    assert boundary["archival_surface_count"] == 1
    assert boundary["missing_route_count"] == 0
    assert boundary["missing_route_records"] == []
    record = boundary["legacy_surface_records"][0]
    assert record["path"] == "old/superpowers/plans/2026-03-17-alphaevolve.md"
    assert record["classification"] == "archival_non_authoritative"
    assert record["self_classification_status"] == "self_classified_archival"
    assert record["routing_status"] == "legacy_surface_routed_as_archival"
    assert record["ci_path_filter_status"] == "legacy_path_filter_present"
    assert record["obsolete_alphaevolve_path_count"] > 0
    assert record["legacy_checkbox_count"] > 0
    assert boundary["missing_evidence"] == {
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "archival non-authoritative classification" in boundary["claim_boundary"]


def test_tracked_legacy_surface_boundary_rejects_overclaim_and_missing_route():
    boundary = tracked_legacy_surface_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "legacy_surfaces_owner_reviewed"
    boundary["archival_surface_count"] = 0
    boundary["missing_route_count"] = 1
    boundary["missing_route_records"] = [boundary["legacy_surface_records"][0]]
    boundary["legacy_surface_records"][0]["ci_path_filter_status"] = (
        "legacy_path_filter_missing"
    )
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["tracked_old_markdown_inventory"]

    validation = validate_tracked_legacy_surface_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_archival_surface_count" in codes
    assert "invalid_missing_route_count" in codes
    assert "invalid_missing_route_records" in codes
    assert "invalid_legacy_surface_records" in codes
    assert "unclassified_legacy_surface" in codes
    assert "missing_legacy_route" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_tracked_legacy_surface_boundary_summary_reports_shape():
    summary = render_tracked_legacy_surface_boundary_summary(
        tracked_legacy_surface_boundary_record()
    )

    assert "Tracked legacy surface boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | tracked_legacy_surface_inventory_without_owner_review_signoff |"
        in summary
    )
    assert "| legacy_surface_count | 1 |" in summary
    assert "| archival_surface_count | 1 |" in summary
    assert "| missing_route_count | 0 |" in summary
    assert "| missing_evidence_count | 1 |" in summary
