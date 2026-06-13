from libreevolve.problems.benchmarks.archive_event_replay_boundary import (
    ARCHIVE_EVENT_REPLAY_BOUNDARY_SCHEMA,
    archive_event_replay_boundary_record,
    render_archive_event_replay_boundary_summary,
    validate_archive_event_replay_boundary,
)


def test_archive_event_replay_boundary_accepts_snapshot_restore_record():
    boundary = archive_event_replay_boundary_record()

    validation = validate_archive_event_replay_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "archive_snapshot_restore_with_audit_only_event_replay"
    )
    assert validation.required_evidence_field_count == 16
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == ARCHIVE_EVENT_REPLAY_BOUNDARY_SCHEMA
    assert "archive_event_replay_audit_schema" in boundary["required_evidence_fields"]
    assert "does not claim ordered archive-event restore-engine support" in (
        boundary["claim_boundary"]
    )


def test_archive_event_replay_boundary_rejects_restore_engine_overclaim():
    boundary = archive_event_replay_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "ordered_archive_event_restore_engine_ready"
    boundary["missing_evidence"]["ordered_archive_event_restore_engine"] = "recorded"
    boundary["required_evidence_fields"] = ["archive_events_jsonl_schema_validation"]

    validation = validate_archive_event_replay_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_ordered_archive_event_restore_engine" in codes
    assert "missing_required_evidence_field" in codes


def test_render_archive_event_replay_boundary_summary_reports_shape():
    summary = render_archive_event_replay_boundary_summary(
        archive_event_replay_boundary_record()
    )

    assert "Archive-event replay boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | archive_snapshot_restore_with_audit_only_event_replay |"
        in summary
    )
    assert "| required_evidence_field_count | 16 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
