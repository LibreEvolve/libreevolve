from libreevolve.problems.benchmarks.map_elites_descriptor_boundary import (
    MAP_ELITES_DESCRIPTOR_BOUNDARY_SCHEMA,
    map_elites_descriptor_boundary_record,
    render_map_elites_descriptor_boundary_summary,
    validate_map_elites_descriptor_boundary,
)


def test_map_elites_descriptor_boundary_accepts_snapshot_descriptor_boundary():
    boundary = map_elites_descriptor_boundary_record()

    validation = validate_map_elites_descriptor_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "insertion_time_local_descriptor_snapshots_only"
    assert validation.required_evidence_field_count == 17
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == MAP_ELITES_DESCRIPTOR_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        "does not claim stable task behavior descriptor contracts"
        in boundary["claim_boundary"]
    )


def test_map_elites_descriptor_boundary_rejects_stable_descriptor_overclaim():
    boundary = map_elites_descriptor_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "stable_behavior_descriptor_and_rebin_ready"
    boundary["missing_evidence"]["learned_descriptor_model"] = "recorded"
    boundary["required_evidence_fields"] = ["descriptor_policy_axes"]

    validation = validate_map_elites_descriptor_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_learned_descriptor_model" in codes
    assert "missing_required_evidence_field" in codes


def test_render_map_elites_descriptor_boundary_summary_reports_shape():
    summary = render_map_elites_descriptor_boundary_summary(
        map_elites_descriptor_boundary_record()
    )

    assert "MAP-Elites descriptor boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | insertion_time_local_descriptor_snapshots_only |" in summary
    assert "| required_evidence_field_count | 17 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
