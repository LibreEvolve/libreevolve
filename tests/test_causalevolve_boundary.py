from libreevolve.problems.benchmarks.causalevolve_boundary import (
    CAUSALEVOLVE_BOUNDARY_SCHEMA,
    causalevolve_boundary_record,
    render_causalevolve_boundary_summary,
    validate_causalevolve_boundary,
)


def test_causalevolve_boundary_accepts_absence_record():
    boundary = causalevolve_boundary_record()

    validation = validate_causalevolve_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "causal_guidance_inspiration_without_causalevolve_scratchpad_parity"
    )
    assert validation.component_count == 12
    assert validation.required_evidence_field_count == 22
    assert validation.missing_evidence_count == 16
    assert boundary["schema"] == CAUSALEVOLVE_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v2"
    assert "fixed token-pattern guidance" in boundary["claim_boundary"]


def test_causalevolve_boundary_rejects_premature_scratchpad_claim():
    boundary = causalevolve_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][1]["status"] = "verified_local_runtime"
    boundary["framework_components"][1]["local_status"] = "implemented"
    boundary["local_evidence"]["causal_scratchpad_ready"] = True
    boundary["missing_evidence"]["causal_scratchpad_schema"] = "implemented"

    validation = validate_causalevolve_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_causal_scratchpad_ready_overclaim" in codes
    assert "invalid_missing_evidence_causal_scratchpad_schema" in codes


def test_render_causalevolve_boundary_summary_reports_shape():
    summary = render_causalevolve_boundary_summary(causalevolve_boundary_record())

    assert "CausalEvolve boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | causal_guidance_inspiration_without_causalevolve_scratchpad_parity |"
        in summary
    )
    assert "| component_count | 12 |" in summary
