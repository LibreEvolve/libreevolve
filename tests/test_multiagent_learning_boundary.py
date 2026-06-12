from libreevolve.problems.benchmarks.multiagent_learning_boundary import (
    MULTIAGENT_LEARNING_BOUNDARY_SCHEMA,
    multiagent_learning_boundary_record,
    render_multiagent_learning_boundary_summary,
    validate_multiagent_learning_boundary,
)


def test_multiagent_learning_boundary_accepts_absence_record():
    boundary = multiagent_learning_boundary_record()

    validation = validate_multiagent_learning_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "marl_algorithm_context_without_cfr_psro_runtime_parity"
    )
    assert validation.component_count == 14
    assert validation.required_evidence_field_count == 25
    assert validation.missing_evidence_count == 22
    assert boundary["schema"] == MULTIAGENT_LEARNING_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v3"
    assert boundary["source_last_revised_date"] == "2026-05-07"
    assert boundary["local_evidence"]["cfr_candidate_schema_ready"] is False
    assert "does not claim CFR or PSRO candidate schemas" in boundary["claim_boundary"]


def test_multiagent_learning_boundary_rejects_premature_runtime_claims():
    boundary = multiagent_learning_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][1]["status"] = "verified_local_runtime"
    boundary["framework_components"][0]["local_status"] = "implemented"
    boundary["local_evidence"]["cfr_candidate_schema_ready"] = True
    boundary["local_evidence"]["repository_runtime_verified"] = True
    boundary["missing_evidence"]["cfr_candidate_schema"] = "implemented"

    validation = validate_multiagent_learning_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_cfr_candidate_schema_ready_overclaim" in codes
    assert "local_evidence_repository_runtime_verified_overclaim" in codes
    assert "invalid_missing_evidence_cfr_candidate_schema" in codes


def test_render_multiagent_learning_boundary_summary_reports_shape():
    summary = render_multiagent_learning_boundary_summary(
        multiagent_learning_boundary_record()
    )

    assert "Multiagent Learning boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | marl_algorithm_context_without_cfr_psro_runtime_parity |"
        in summary
    )
    assert "| component_count | 14 |" in summary
