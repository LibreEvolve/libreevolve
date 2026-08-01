from libreevolve.problems.benchmarks.alphaevolve_related_work_claim_inventory_boundary import (
    ALPHAEVOLVE_RELATED_WORK_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_related_work_claim_inventory_boundary_record,
    render_alphaevolve_related_work_claim_inventory_boundary_summary,
    validate_alphaevolve_related_work_claim_inventory_boundary,
)


def test_related_work_claim_inventory_accepts_exact_section_5_inventory():
    boundary = alphaevolve_related_work_claim_inventory_boundary_record()

    validation = validate_alphaevolve_related_work_claim_inventory_boundary(boundary)

    assert validation.ok is True
    assert boundary["schema"] == ALPHAEVOLVE_RELATED_WORK_CLAIM_INVENTORY_BOUNDARY_SCHEMA
    assert boundary["related_work_claim_inventory_ready"] is True
    assert boundary["alphaevolve_related_work_positioning_claim_ready"] is False
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert boundary["source_span_ids"] == ["section_5"]
    assert boundary["claim_count"] == 85
    assert boundary["implementation_relevant_claim_count"] == 26
    assert boundary["source_context_claim_count"] == 59
    assert boundary["implementation_status_counts"] == {
        "implemented_local": 6,
        "not_demonstrated": 7,
        "not_implemented": 4,
        "partially_implemented": 9,
        "source_context_only": 59,
    }
    assert boundary["implementation_gap_count"] == 20
    assert boundary["todo_owned_gap_count"] == 20
    assert boundary["missing_anchor_count"] == 0
    assert boundary["missing_reference_count"] == 0


def test_related_work_claim_inventory_separates_context_from_parity_requirements():
    boundary = alphaevolve_related_work_claim_inventory_boundary_record()
    records = {record["claim_id"]: record for record in boundary["claim_records"]}

    assert records["pre_llm_systematic_enumeration"]["implementation_relevance"] == (
        "source_context_only"
    )
    assert records["pre_llm_systematic_enumeration"]["active_todo_refs"] == []
    assert records["alphaevolve_entire_codebases"]["implementation_status"] == (
        "partially_implemented"
    )
    assert records["alphaevolve_entire_codebases"]["active_todo_refs"]
    assert records["alphaevolve_code_superoptimization_view"][
        "implementation_status"
    ] == "implemented_local"
    assert records["programmatic_choice_sidesteps_hallucinations"][
        "implementation_status"
    ] == "not_demonstrated"
    assert records["continuous_llm_finetuning_rl"]["implementation_status"] == (
        "not_implemented"
    )


def test_related_work_claim_inventory_rejects_overclaim_and_record_drift():
    boundary = alphaevolve_related_work_claim_inventory_boundary_record()
    boundary["alphaevolve_related_work_positioning_claim_ready"] = True
    boundary["alphaevolve_parity_claim_ready"] = True
    boundary["claim_count"] = 84
    boundary["implementation_relevant_claim_count"] = 85
    boundary["claim_records"][0]["source_anchor_present"] = False

    validation = validate_alphaevolve_related_work_claim_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "positioning_overclaim" in codes
    assert "parity_overclaim" in codes
    assert "invalid_claim_count" in codes
    assert "invalid_implementation_relevant_claim_count" in codes
    assert "invalid_claim_records" in codes


def test_related_work_claim_inventory_rejects_readiness_drift():
    boundary = alphaevolve_related_work_claim_inventory_boundary_record()
    boundary["related_work_claim_inventory_ready"] = False
    boundary["source_context_claim_count"] = 0
    boundary["todo_owned_gap_count"] = 0

    validation = validate_alphaevolve_related_work_claim_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_related_work_claim_inventory_ready" in codes
    assert "invalid_source_context_claim_count" in codes
    assert "invalid_todo_owned_gap_count" in codes


def test_render_related_work_claim_inventory_summary_reports_shape():
    summary = render_alphaevolve_related_work_claim_inventory_boundary_summary(
        alphaevolve_related_work_claim_inventory_boundary_record()
    )

    assert "AlphaEvolve related-work claim inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| claim_count | 85 |" in summary
    assert "| implementation_relevant_claim_count | 26 |" in summary
    assert "| source_context_claim_count | 59 |" in summary
    assert "| implemented_local_count | 6 |" in summary
    assert "| implementation_gap_count | 20 |" in summary
    assert "| missing_anchor_count | 0 |" in summary
    assert "| missing_reference_count | 0 |" in summary
