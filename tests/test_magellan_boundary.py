from libreevolve.problems.benchmarks.magellan_boundary import (
    MAGELLAN_BOUNDARY_SCHEMA,
    magellan_boundary_record,
    render_magellan_boundary_summary,
    validate_magellan_boundary,
)


def test_magellan_boundary_accepts_absence_record():
    boundary = magellan_boundary_record()

    validation = validate_magellan_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "compiler_optimization_context_without_magellan_runtime_parity"
    )
    assert validation.component_count == 14
    assert validation.required_evidence_field_count == 27
    assert validation.missing_evidence_count == 20
    assert boundary["schema"] == MAGELLAN_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v1"
    assert boundary["source_accepted_venue"] == "C4ML@CGO'26"
    assert boundary["local_evidence"]["compiler_pass_runner_ready"] is False
    assert "does not claim executable C++ decision-logic" in boundary["claim_boundary"]


def test_magellan_boundary_rejects_premature_compiler_runtime_claims():
    boundary = magellan_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][3]["status"] = "verified_local_runtime"
    boundary["framework_components"][0]["local_status"] = "implemented"
    boundary["local_evidence"]["compiler_pass_runner_ready"] = True
    boundary["local_evidence"]["repository_runtime_verified"] = True
    boundary["missing_evidence"]["compiler_pass_runner"] = "implemented"

    validation = validate_magellan_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_compiler_pass_runner_ready_overclaim" in codes
    assert "local_evidence_repository_runtime_verified_overclaim" in codes
    assert "invalid_missing_evidence_compiler_pass_runner" in codes


def test_render_magellan_boundary_summary_reports_shape():
    summary = render_magellan_boundary_summary(magellan_boundary_record())

    assert "Magellan boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | compiler_optimization_context_without_magellan_runtime_parity |"
        in summary
    )
    assert "| component_count | 14 |" in summary
