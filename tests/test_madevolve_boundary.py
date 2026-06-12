from libreevolve.problems.benchmarks.madevolve_boundary import (
    MADEVOLVE_BOUNDARY_SCHEMA,
    madevolve_boundary_record,
    render_madevolve_boundary_summary,
    validate_madevolve_boundary,
)


def test_madevolve_boundary_accepts_absence_record():
    boundary = madevolve_boundary_record()

    validation = validate_madevolve_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "domain_evolution_inspiration_without_madevolve_parity"
    )
    assert validation.component_count == 12
    assert validation.required_evidence_field_count == 26
    assert validation.missing_evidence_count == 18
    assert boundary["schema"] == MADEVOLVE_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v1"
    assert "does not claim free-parameter tracking" in boundary["claim_boundary"]


def test_madevolve_boundary_rejects_premature_domain_claim():
    boundary = madevolve_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][1]["status"] = "verified_local_framework_runtime"
    boundary["framework_components"][1]["local_status"] = "implemented"
    boundary["local_evidence"]["free_parameter_tracking_ready"] = True
    boundary["missing_evidence"]["free_parameter_tracking"] = "implemented"

    validation = validate_madevolve_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_free_parameter_tracking_ready_overclaim" in codes
    assert "invalid_missing_evidence_free_parameter_tracking" in codes


def test_render_madevolve_boundary_summary_reports_shape():
    summary = render_madevolve_boundary_summary(madevolve_boundary_record())

    assert "MadEvolve boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | domain_evolution_inspiration_without_madevolve_parity |"
        in summary
    )
    assert "| component_count | 12 |" in summary
