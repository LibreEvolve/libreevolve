from libreevolve.problems.benchmarks.sorting_network_source_citation_boundary import (
    SORTING_NETWORK_SOURCE_CITATION_BOUNDARY_SCHEMA,
    render_sorting_network_source_citation_boundary_summary,
    sorting_network_source_citation_boundary_record,
    validate_sorting_network_source_citation_boundary,
)


def test_sorting_network_source_citation_boundary_accepts_record():
    boundary = sorting_network_source_citation_boundary_record()

    validation = validate_sorting_network_source_citation_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "source_citations_recorded_without_run_certification"
    assert validation.problem_count == 2
    assert validation.citation_count == 3
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == SORTING_NETWORK_SOURCE_CITATION_BOUNDARY_SCHEMA
    assert boundary["source_citations"]["sorting_network_8_target"][
        "target_comparators"
    ] == 19
    assert boundary["source_citations"]["sorting_network_9_target"][
        "target_comparators"
    ] == 25
    assert boundary["claim_ready"] is False
    assert "does not claim" in boundary["claim_boundary"]


def test_sorting_network_source_citation_boundary_rejects_overclaim_and_drift():
    boundary = sorting_network_source_citation_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "certified_rediscovery"
    boundary["problem_ids"] = ["sorting_network_9"]
    boundary["source_citations"]["zero_one_principle"]["url"] = "missing"
    boundary["source_citations"]["sorting_network_8_target"][
        "target_comparators"
    ] = 20
    boundary["source_citations"]["sorting_network_9_target"]["sources"] = []
    boundary["missing_evidence"]["target_hit_rate_summary"] = "recorded"

    validation = validate_sorting_network_source_citation_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_problem_ids" in codes
    assert "invalid_zero_one_citation" in codes
    assert "invalid_sorting_network_8_target" in codes
    assert "missing_sorting_network_9_arxiv_citation" in codes
    assert "missing_sorting_network_9_jcss_doi" in codes
    assert "invalid_missing_evidence_target_hit_rate_summary" in codes


def test_render_sorting_network_source_citation_boundary_summary_reports_shape():
    summary = render_sorting_network_source_citation_boundary_summary(
        sorting_network_source_citation_boundary_record()
    )

    assert "Sorting-network source citation boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | source_citations_recorded_without_run_certification |" in summary
    assert "| problem_count | 2 |" in summary
    assert "| citation_count | 3 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
