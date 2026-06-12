from libreevolve.problems.benchmarks.archagent_boundary import (
    ARCHAGENT_BOUNDARY_SCHEMA,
    archagent_boundary_record,
    render_archagent_boundary_summary,
    validate_archagent_boundary,
)


def test_archagent_boundary_accepts_absence_record():
    boundary = archagent_boundary_record()

    validation = validate_archagent_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "computer_architecture_context_without_archagent_runtime_parity"
    )
    assert validation.component_count == 14
    assert validation.required_evidence_field_count == 29
    assert validation.missing_evidence_count == 22
    assert boundary["schema"] == ARCHAGENT_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v1"
    assert boundary["source_submitted_date"] == "2026-02-25"
    assert boundary["local_evidence"]["champsim_runner_ready"] is False
    assert "does not claim generated C++ cache replacement policies" in boundary["claim_boundary"]


def test_archagent_boundary_rejects_premature_architecture_runtime_claims():
    boundary = archagent_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][3]["status"] = "verified_local_runtime"
    boundary["framework_components"][0]["local_status"] = "implemented"
    boundary["local_evidence"]["champsim_runner_ready"] = True
    boundary["local_evidence"]["repository_runtime_verified"] = True
    boundary["missing_evidence"]["champsim_policy_h_runner"] = "implemented"

    validation = validate_archagent_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_champsim_runner_ready_overclaim" in codes
    assert "local_evidence_repository_runtime_verified_overclaim" in codes
    assert "invalid_missing_evidence_champsim_policy_h_runner" in codes


def test_render_archagent_boundary_summary_reports_shape():
    summary = render_archagent_boundary_summary(archagent_boundary_record())

    assert "ArchAgent boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | computer_architecture_context_without_archagent_runtime_parity |"
        in summary
    )
    assert "| component_count | 14 |" in summary
