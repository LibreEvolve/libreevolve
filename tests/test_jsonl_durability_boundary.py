from libreevolve.problems.benchmarks.jsonl_durability_boundary import (
    JSONL_DURABILITY_BOUNDARY_SCHEMA,
    jsonl_durability_boundary_record,
    render_jsonl_durability_boundary_summary,
    validate_jsonl_durability_boundary,
)


def test_jsonl_durability_boundary_accepts_strict_single_writer_scope():
    boundary = jsonl_durability_boundary_record()

    validation = validate_jsonl_durability_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "strict_single_writer_append_with_read_fail_closed_without_multi_writer_serialization"
    )
    assert validation.required_evidence_field_count == 20
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == JSONL_DURABILITY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert len(boundary["implemented_runtime_evidence"]) == 15
    assert (
        "default fail-closed unterminated-final-record handling"
        in boundary["claim_boundary"]
    )


def test_jsonl_durability_boundary_rejects_async_durability_overclaim():
    boundary = jsonl_durability_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "durable_async_jsonl_ready"
    boundary["missing_evidence"]["multi_writer_serialization"] = "recorded"
    boundary["required_evidence_fields"] = ["strict_json_serialization"]
    del boundary["implemented_runtime_evidence"]["fsync_after_append"]

    validation = validate_jsonl_durability_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_multi_writer_serialization" in codes
    assert "missing_required_evidence_field" in codes
    assert "missing_implemented_runtime_evidence" in codes


def test_render_jsonl_durability_boundary_summary_reports_shape():
    summary = render_jsonl_durability_boundary_summary(
        jsonl_durability_boundary_record()
    )

    assert "JSONL durability boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | strict_single_writer_append_with_read_fail_closed_without_multi_writer_serialization |"
        in summary
    )
    assert "| required_evidence_field_count | 20 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
