from libreevolve.problems.benchmarks.thetaevolve_boundary import (
    THETAEVOLVE_BOUNDARY_SCHEMA,
    render_thetaevolve_boundary_summary,
    thetaevolve_boundary_record,
    validate_thetaevolve_boundary,
)


def test_thetaevolve_boundary_accepts_absence_record():
    boundary = thetaevolve_boundary_record()

    validation = validate_thetaevolve_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "test_time_training_inspiration_without_thetaevolve_parity"
    )
    assert validation.component_count == 12
    assert validation.required_evidence_field_count == 24
    assert validation.missing_evidence_count == 16
    assert boundary["schema"] == THETAEVOLVE_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v1"
    assert "clipped-reward JSONL export, not model training" in boundary["claim_boundary"]


def test_thetaevolve_boundary_rejects_premature_training_claim():
    boundary = thetaevolve_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][0]["status"] = "verified_local_runtime"
    boundary["framework_components"][7]["local_status"] = "implemented"
    boundary["local_evidence"]["grpo_ready"] = True
    boundary["missing_evidence"]["grpo_rl_training"] = "implemented"

    validation = validate_thetaevolve_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_grpo_ready_overclaim" in codes
    assert "invalid_missing_evidence_grpo_rl_training" in codes


def test_render_thetaevolve_boundary_summary_reports_shape():
    summary = render_thetaevolve_boundary_summary(thetaevolve_boundary_record())

    assert "ThetaEvolve boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | test_time_training_inspiration_without_thetaevolve_parity |"
        in summary
    )
    assert "| component_count | 12 |" in summary
