from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_hardware_claim_inventory_boundary import (
    ALPHAEVOLVE_HARDWARE_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_hardware_claim_inventory_boundary_record,
    render_alphaevolve_hardware_claim_inventory_boundary_summary,
    validate_alphaevolve_hardware_claim_inventory_boundary,
)


def test_hardware_claim_inventory_accepts_pdf_anchored_scope():
    boundary = alphaevolve_hardware_claim_inventory_boundary_record()

    validation = validate_alphaevolve_hardware_claim_inventory_boundary(boundary)

    assert validation.ok is True
    assert boundary["schema"] == ALPHAEVOLVE_HARDWARE_CLAIM_INVENTORY_BOUNDARY_SCHEMA
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["hardware_claim_inventory_ready"] is True
    assert boundary["alphaevolve_hardware_result_reproduction_claim_ready"] is False
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert validation.claim_count == 35
    assert validation.implemented_local_count == 0
    assert validation.implementation_gap_count == 35
    assert validation.missing_anchor_count == 0
    assert validation.missing_reference_count == 0
    assert boundary["todo_owned_gap_count"] == 35
    assert boundary["implementation_status_counts"] == {
        "not_demonstrated": 19,
        "not_implemented": 4,
        "partially_implemented": 12,
    }
    assert boundary["category_counts"] == {
        "hardware_adoption": 6,
        "hardware_deployment_and_attribution": 4,
        "hardware_design_context": 2,
        "hardware_design_flow": 2,
        "hardware_discovery_result": 4,
        "hardware_optimization_task": 6,
        "hardware_verification": 2,
        "hardware_workflow_context": 9,
    }
    assert boundary["claim_records"][0]["claim_id"] == (
        "specialized_hardware_tpu_example"
    )
    assert boundary["claim_records"][-1]["claim_id"] == (
        "potential_time_to_market_reduction"
    )
    assert all(record["source_anchor_present"] for record in boundary["claim_records"])
    assert "Verilog/RTL behavior" in boundary["claim_boundary"]
    assert "time-to-market improvement" in boundary["claim_boundary"]


def test_hardware_claim_inventory_gives_every_gap_todo_ownership():
    boundary = alphaevolve_hardware_claim_inventory_boundary_record()

    incomplete = [
        record
        for record in boundary["claim_records"]
        if record["implementation_status"] != "implemented_local"
    ]

    assert len(incomplete) == 35
    assert all(record["active_todo_refs"] for record in incomplete)
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in incomplete
        for ref in record["active_todo_refs"]
    )


def test_hardware_claim_inventory_rejects_record_and_overclaim_drift():
    boundary = deepcopy(alphaevolve_hardware_claim_inventory_boundary_record())
    boundary["claim_records"][0]["implementation_status"] = "implemented_local"
    boundary["claim_count"] = 34
    boundary["alphaevolve_hardware_result_reproduction_claim_ready"] = True
    boundary["alphaevolve_parity_claim_ready"] = True

    validation = validate_alphaevolve_hardware_claim_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_claim_records" in codes
    assert "invalid_claim_count" in codes
    assert "result_reproduction_overclaim" in codes
    assert "parity_overclaim" in codes


def test_hardware_claim_inventory_rejects_missing_pinned_source(tmp_path):
    boundary = alphaevolve_hardware_claim_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_hardware_claim_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["hardware_claim_inventory_ready"] is False
    assert "source_pdf_identity_mismatch" in codes
    assert "missing_source_anchor" in codes
    assert "missing_local_reference" in codes


def test_render_hardware_claim_inventory_summary_reports_shape():
    summary = render_alphaevolve_hardware_claim_inventory_boundary_summary(
        alphaevolve_hardware_claim_inventory_boundary_record()
    )

    assert "AlphaEvolve hardware claim inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| claim_count | 35 |" in summary
    assert "| implemented_local_count | 0 |" in summary
    assert "| implementation_gap_count | 35 |" in summary
    assert "| missing_anchor_count | 0 |" in summary
