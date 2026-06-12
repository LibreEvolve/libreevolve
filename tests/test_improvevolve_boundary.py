from libreevolve.problems.benchmarks.improvevolve_boundary import (
    IMPROVEVOLVE_BOUNDARY_SCHEMA,
    improvevolve_boundary_record,
    render_improvevolve_boundary_summary,
    validate_improvevolve_boundary,
)


def test_improvevolve_boundary_accepts_absence_record():
    boundary = improvevolve_boundary_record()

    validation = validate_improvevolve_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "modular_prompting_inspiration_without_improvevolve_parity"
    )
    assert validation.component_count == 12
    assert validation.required_evidence_field_count == 21
    assert validation.missing_evidence_count == 16
    assert boundary["schema"] == IMPROVEVOLVE_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v1"
    assert "static prompt guidance, not ImprovEvolve execution" in boundary["claim_boundary"]


def test_improvevolve_boundary_rejects_premature_execution_claim():
    boundary = improvevolve_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][1]["status"] = "verified_local_runtime"
    boundary["framework_components"][1]["local_status"] = "implemented"
    boundary["local_evidence"]["interface_enforced"] = True
    boundary["missing_evidence"]["class_interface_enforcement"] = "implemented"

    validation = validate_improvevolve_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_interface_enforced_overclaim" in codes
    assert "invalid_missing_evidence_class_interface_enforcement" in codes


def test_render_improvevolve_boundary_summary_reports_shape():
    summary = render_improvevolve_boundary_summary(improvevolve_boundary_record())

    assert "ImprovEvolve boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | modular_prompting_inspiration_without_improvevolve_parity |"
        in summary
    )
    assert "| component_count | 12 |" in summary
