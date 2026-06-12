from libreevolve.problems.benchmarks.gigaevo_boundary import (
    GIGAEVO_FRAMEWORK_BOUNDARY_SCHEMA,
    gigaevo_framework_boundary_record,
    render_gigaevo_framework_boundary_summary,
    validate_gigaevo_framework_boundary,
)


def test_gigaevo_boundary_accepts_absence_record():
    boundary = gigaevo_framework_boundary_record()

    validation = validate_gigaevo_framework_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "framework_inspiration_without_gigaevo_runtime_parity"
    )
    assert validation.component_count == 8
    assert validation.required_evidence_field_count == 16
    assert validation.missing_evidence_count == 12
    assert boundary["schema"] == GIGAEVO_FRAMEWORK_BOUNDARY_SCHEMA
    assert "does not claim Redis lifecycle storage" in boundary["claim_boundary"]


def test_gigaevo_boundary_rejects_premature_framework_parity_claim():
    boundary = gigaevo_framework_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][0]["status"] = "canonical_repository"
    boundary["framework_components"][0]["local_status"] = "implemented"
    boundary["local_evidence"]["asyncio_dag_ready"] = True
    boundary["missing_evidence"]["asyncio_dag_execution_engine"] = "implemented"

    validation = validate_gigaevo_framework_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_asyncio_dag_ready_overclaim" in codes
    assert "invalid_missing_evidence_asyncio_dag_execution_engine" in codes


def test_render_gigaevo_boundary_summary_reports_shape():
    summary = render_gigaevo_framework_boundary_summary(
        gigaevo_framework_boundary_record()
    )

    assert "GigaEvo framework boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | framework_inspiration_without_gigaevo_runtime_parity |"
        in summary
    )
    assert "| component_count | 8 |" in summary
