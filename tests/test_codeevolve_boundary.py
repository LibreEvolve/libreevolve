from libreevolve.problems.benchmarks.codeevolve_boundary import (
    CODEEVOLVE_BOUNDARY_SCHEMA,
    codeevolve_boundary_record,
    render_codeevolve_boundary_summary,
    validate_codeevolve_boundary,
)


def test_codeevolve_boundary_accepts_absence_record():
    boundary = codeevolve_boundary_record()

    validation = validate_codeevolve_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "agentic_code_evolution_inspiration_without_codeevolve_parity"
    )
    assert validation.component_count == 12
    assert validation.required_evidence_field_count == 24
    assert validation.missing_evidence_count == 16
    assert boundary["schema"] == CODEEVOLVE_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v4"
    assert "does not claim CodeEvolve prompt/solution dual fitness" in boundary["claim_boundary"]


def test_codeevolve_boundary_rejects_premature_framework_parity_claim():
    boundary = codeevolve_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][0]["status"] = "verified_local_runtime"
    boundary["framework_components"][4]["local_status"] = "implemented"
    boundary["local_evidence"]["semantic_crossover_ready"] = True
    boundary["missing_evidence"]["semantic_inspiration_crossover"] = "implemented"

    validation = validate_codeevolve_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_semantic_crossover_ready_overclaim" in codes
    assert "invalid_missing_evidence_semantic_inspiration_crossover" in codes


def test_render_codeevolve_boundary_summary_reports_shape():
    summary = render_codeevolve_boundary_summary(codeevolve_boundary_record())

    assert "CodeEvolve boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | agentic_code_evolution_inspiration_without_codeevolve_parity |"
        in summary
    )
    assert "| component_count | 12 |" in summary
