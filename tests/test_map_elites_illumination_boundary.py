from libreevolve.problems.benchmarks.map_elites_illumination_boundary import (
    MAP_ELITES_ILLUMINATION_BOUNDARY_SCHEMA,
    map_elites_illumination_boundary_record,
    render_map_elites_illumination_boundary_summary,
    validate_map_elites_illumination_boundary,
)


def test_map_elites_illumination_boundary_accepts_absence_record():
    boundary = map_elites_illumination_boundary_record()

    validation = validate_map_elites_illumination_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "local_3d_archive_without_full_illumination_evidence"
    )
    assert validation.default_axis_count == 3
    assert validation.required_evidence_field_count == 22
    assert validation.missing_evidence_count == 14
    assert boundary["schema"] == MAP_ELITES_ILLUMINATION_BOUNDARY_SCHEMA
    assert "does not claim full Mouret-Clune illumination-algorithm parity" in (
        boundary["claim_boundary"]
    )


def test_map_elites_illumination_boundary_rejects_premature_parity_claim():
    boundary = map_elites_illumination_boundary_record()
    boundary["claim_ready"] = True
    boundary["local_archive_evidence"]["full_p_x_map_export_ready"] = True
    boundary["local_archive_evidence"]["illumination_metrics_ready"] = True
    boundary["missing_evidence"]["illumination_metric_reports"] = "recorded"

    validation = validate_map_elites_illumination_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "full_p_x_map_export_ready_overclaim" in codes
    assert "illumination_metrics_ready_overclaim" in codes
    assert "invalid_missing_evidence_illumination_metric_reports" in codes


def test_render_map_elites_illumination_boundary_summary_reports_shape():
    summary = render_map_elites_illumination_boundary_summary(
        map_elites_illumination_boundary_record()
    )

    assert "MAP-Elites illumination boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | local_3d_archive_without_full_illumination_evidence |"
        in summary
    )
    assert "| default_axis_count | 3 |" in summary
