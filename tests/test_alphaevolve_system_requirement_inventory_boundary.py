from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_system_requirement_inventory_boundary import (
    ALPHAEVOLVE_SYSTEM_REQUIREMENT_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_system_requirement_inventory_boundary_record,
    render_alphaevolve_system_requirement_inventory_boundary_summary,
    validate_alphaevolve_system_requirement_inventory_boundary,
)


def test_system_requirement_inventory_accepts_pdf_anchored_section_2_scope():
    boundary = alphaevolve_system_requirement_inventory_boundary_record()

    validation = validate_alphaevolve_system_requirement_inventory_boundary(boundary)

    assert validation.ok is True
    assert (
        boundary["schema"]
        == ALPHAEVOLVE_SYSTEM_REQUIREMENT_INVENTORY_BOUNDARY_SCHEMA
    )
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["section_2_requirement_inventory_ready"] is True
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert validation.requirement_count == 56
    assert validation.implemented_local_count == 14
    assert validation.implementation_gap_count == 42
    assert validation.missing_anchor_count == 0
    assert validation.missing_reference_count == 0
    assert boundary["todo_owned_gap_count"] == 42
    assert boundary["implementation_status_counts"] == {
        "implemented_local": 14,
        "not_demonstrated": 7,
        "not_implemented": 4,
        "partially_implemented": 31,
    }
    assert boundary["category_counts"] == {
        "creative_generation": 7,
        "distributed_pipeline": 3,
        "evaluation": 9,
        "evolution": 4,
        "platform_overview": 5,
        "prompt_sampling": 6,
        "table_1_capability": 8,
        "task_specification": 14,
    }
    assert boundary["requirement_records"][0]["requirement_id"] == (
        "table1_entire_code_file"
    )
    assert boundary["requirement_records"][-1]["requirement_id"] == (
        "distributed_throughput_budget_optimization"
    )
    assert all(
        record["source_anchor_present"]
        for record in boundary["requirement_records"]
    )
    assert "whole-paper claim-level exhaustiveness" in boundary["claim_boundary"]


def test_system_requirement_inventory_gives_every_incomplete_claim_todo_ownership():
    boundary = alphaevolve_system_requirement_inventory_boundary_record()

    incomplete = [
        record
        for record in boundary["requirement_records"]
        if record["implementation_status"] != "implemented_local"
    ]

    assert len(incomplete) == 42
    assert all(record["active_todo_refs"] for record in incomplete)
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in incomplete
        for ref in record["active_todo_refs"]
    )


def test_system_requirement_inventory_rejects_status_record_and_parity_drift():
    boundary = deepcopy(alphaevolve_system_requirement_inventory_boundary_record())
    boundary["requirement_records"][0]["implementation_status"] = (
        "implemented_local"
    )
    boundary["requirement_count"] = 49
    boundary["alphaevolve_parity_claim_ready"] = True

    validation = validate_alphaevolve_system_requirement_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_requirement_records" in codes
    assert "invalid_requirement_count" in codes
    assert "parity_overclaim" in codes


def test_system_requirement_inventory_rejects_missing_pinned_source(tmp_path):
    boundary = alphaevolve_system_requirement_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_system_requirement_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["section_2_requirement_inventory_ready"] is False
    assert "source_pdf_identity_mismatch" in codes
    assert "missing_source_anchor" in codes
    assert "missing_local_reference" in codes


def test_render_system_requirement_inventory_summary_reports_shape():
    summary = render_alphaevolve_system_requirement_inventory_boundary_summary(
        alphaevolve_system_requirement_inventory_boundary_record()
    )

    assert "AlphaEvolve system requirement inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| requirement_count | 56 |" in summary
    assert "| implemented_local_count | 14 |" in summary
    assert "| implementation_gap_count | 42 |" in summary
    assert "| missing_anchor_count | 0 |" in summary
