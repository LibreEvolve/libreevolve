from libreevolve.problems.benchmarks.non_jsonl_artifact_boundary import (
    NON_JSONL_ARTIFACT_BOUNDARY_SCHEMA,
    non_jsonl_artifact_boundary_record,
    render_non_jsonl_artifact_boundary_summary,
    validate_non_jsonl_artifact_boundary,
)


def test_non_jsonl_artifact_boundary_accepts_runtime_schema_scope():
    boundary = non_jsonl_artifact_boundary_record()

    validation = validate_non_jsonl_artifact_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "schema_checked_non_jsonl_artifacts_without_payload_replay_certification"
    )
    assert validation.artifact_count == 7
    assert validation.required_evidence_field_count == 21
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == NON_JSONL_ARTIFACT_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["artifact_names"] == [
        "best.py",
        "best_workspace",
        "evaluator_artifacts",
        "manifest.json",
        "paper_artifacts",
        "plugin_artifacts",
        "task_specification.json",
    ]
    assert boundary["non_jsonl_artifacts"]["manifest.json"]["hash_policy"] == (
        "self_describing_manifest_not_independently_self_hashed"
    )
    assert boundary["generated_inventory_records"]["paper_artifacts"][
        "schema_pointer"
    ] == 'artifact_schema.non_jsonl_artifacts["paper_artifacts"]'
    assert (
        "does not claim full restored-run payload replay"
        in boundary["claim_boundary"]
    )


def test_non_jsonl_artifact_boundary_rejects_payload_replay_overclaim():
    boundary = non_jsonl_artifact_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_payload_replay_certified"
    boundary["missing_evidence"]["artifact_payload_carry_forward"] = "recorded"
    boundary["required_evidence_fields"] = ["runtime_schema_pointer"]
    boundary["non_jsonl_artifacts"]["best.py"]["hash_policy"] = "unchecked"
    del boundary["generated_inventory_records"]["paper_artifacts"]

    validation = validate_non_jsonl_artifact_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_artifact_payload_carry_forward" in codes
    assert "missing_required_evidence_field" in codes
    assert "invalid_non_jsonl_artifacts" in codes
    assert "invalid_generated_inventory_records" in codes


def test_render_non_jsonl_artifact_boundary_summary_reports_shape():
    summary = render_non_jsonl_artifact_boundary_summary(
        non_jsonl_artifact_boundary_record()
    )

    assert "Non-JSONL artifact boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | schema_checked_non_jsonl_artifacts_without_payload_replay_certification |"
        in summary
    )
    assert "| artifact_count | 7 |" in summary
    assert "| required_evidence_field_count | 21 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
