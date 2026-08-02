from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_appendix_a_claim_inventory_boundary import (
    ALPHAEVOLVE_APPENDIX_A_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_appendix_a_claim_inventory_boundary_record,
    render_alphaevolve_appendix_a_claim_inventory_boundary_summary,
    validate_alphaevolve_appendix_a_claim_inventory_boundary,
)


def test_appendix_a_claim_inventory_accepts_pdf_anchored_scope():
    boundary = alphaevolve_appendix_a_claim_inventory_boundary_record()

    validation = validate_alphaevolve_appendix_a_claim_inventory_boundary(boundary)

    assert validation.ok is True
    assert boundary["schema"] == ALPHAEVOLVE_APPENDIX_A_CLAIM_INVENTORY_BOUNDARY_SCHEMA
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["appendix_a_claim_inventory_ready"] is True
    assert boundary["alphaevolve_result_reproduction_claim_ready"] is False
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert validation.claim_count == 131
    assert validation.implemented_local_count == 0
    assert validation.implementation_gap_count == 131
    assert validation.missing_anchor_count == 0
    assert validation.missing_reference_count == 0
    assert boundary["todo_owned_gap_count"] == 131
    assert boundary["implementation_status_counts"] == {
        "not_demonstrated": 118,
        "partially_implemented": 13,
    }
    assert boundary["category_counts"] == {
        "aggregate_result": 4,
        "concurrent_work_result": 1,
        "exactness_result": 2,
        "figure_9_caption": 3,
        "figure_9_clipping": 5,
        "figure_9_discretization": 10,
        "figure_9_initialization": 2,
        "figure_9_loss": 8,
        "figure_9_noise": 4,
        "figure_9_optimizer": 2,
        "figure_9_result": 2,
        "figure_9_structure": 1,
        "figure_9_sweep": 14,
        "publication_artifact_result": 1,
        "resource_frontier": 6,
        "scalar_field_result": 3,
        "table_3_row_result": 54,
        "table_3_structure": 4,
        "target_suite_curation": 5,
    }
    assert boundary["claim_records"][0]["claim_id"] == "appendix_a_best_ranks_in_table3"
    assert boundary["claim_records"][-1]["claim_id"] == "figure9_hyper_user_provided_library"
    assert all(record["source_anchor_present"] for record in boundary["claim_records"])
    table_rows = [
        record
        for record in boundary["claim_records"]
        if record["category"] == "table_3_row_result"
    ]
    assert len(table_rows) == 54
    assert "54 result rows" in boundary["claim_boundary"]


def test_appendix_a_claim_inventory_gives_every_gap_todo_ownership():
    boundary = alphaevolve_appendix_a_claim_inventory_boundary_record()

    incomplete = [
        record
        for record in boundary["claim_records"]
        if record["implementation_status"] != "implemented_local"
    ]

    assert len(incomplete) == 131
    assert all(record["active_todo_refs"] for record in incomplete)
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in incomplete
        for ref in record["active_todo_refs"]
    )


def test_appendix_a_claim_inventory_rejects_record_and_overclaim_drift():
    boundary = deepcopy(alphaevolve_appendix_a_claim_inventory_boundary_record())
    boundary["claim_records"][0]["implementation_status"] = "implemented_local"
    boundary["claim_count"] = 130
    boundary["alphaevolve_result_reproduction_claim_ready"] = True
    boundary["alphaevolve_parity_claim_ready"] = True

    validation = validate_alphaevolve_appendix_a_claim_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_claim_records" in codes
    assert "invalid_claim_count" in codes
    assert "result_reproduction_overclaim" in codes
    assert "parity_overclaim" in codes


def test_appendix_a_claim_inventory_rejects_missing_pinned_source(tmp_path):
    boundary = alphaevolve_appendix_a_claim_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_appendix_a_claim_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["appendix_a_claim_inventory_ready"] is False
    assert "source_pdf_identity_mismatch" in codes
    assert "missing_source_anchor" in codes
    assert "missing_local_reference" in codes


def test_render_appendix_a_claim_inventory_summary_reports_shape():
    summary = render_alphaevolve_appendix_a_claim_inventory_boundary_summary(
        alphaevolve_appendix_a_claim_inventory_boundary_record()
    )

    assert "AlphaEvolve Appendix A claim inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| claim_count | 131 |" in summary
    assert "| implemented_local_count | 0 |" in summary
    assert "| implementation_gap_count | 131 |" in summary
    assert "| missing_anchor_count | 0 |" in summary
