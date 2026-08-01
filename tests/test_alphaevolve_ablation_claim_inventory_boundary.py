from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_ablation_claim_inventory_boundary import (
    ALPHAEVOLVE_ABLATION_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_ablation_claim_inventory_boundary_record,
    render_alphaevolve_ablation_claim_inventory_boundary_summary,
    validate_alphaevolve_ablation_claim_inventory_boundary,
)


def test_ablation_claim_inventory_accepts_pdf_anchored_scope():
    boundary = alphaevolve_ablation_claim_inventory_boundary_record()

    validation = validate_alphaevolve_ablation_claim_inventory_boundary(boundary)

    assert validation.ok is True
    assert boundary["schema"] == ALPHAEVOLVE_ABLATION_CLAIM_INVENTORY_BOUNDARY_SCHEMA
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["ablation_claim_inventory_ready"] is True
    assert boundary["alphaevolve_ablation_result_reproduction_claim_ready"] is False
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert validation.claim_count == 51
    assert validation.implemented_local_count == 2
    assert validation.implementation_gap_count == 49
    assert validation.missing_anchor_count == 0
    assert validation.missing_reference_count == 0
    assert boundary["todo_owned_gap_count"] == 49
    assert boundary["implementation_status_counts"] == {
        "implemented_local": 2,
        "not_demonstrated": 7,
        "not_implemented": 6,
        "partially_implemented": 36,
    }
    assert boundary["category_counts"] == {
        "ablation_result": 2,
        "ablation_setup": 6,
        "evolution_ablation": 5,
        "figure8_exhibit": 18,
        "full_file_ablation": 6,
        "meta_prompt_ablation": 5,
        "model_mix_ablation": 4,
        "prompt_context_ablation": 5,
    }
    assert boundary["figure8_source_shape"]["matches_source"] is True
    assert boundary["figure8_source_shape"]["expected_series_count"] == 9
    assert boundary["figure8_source_shape"]["expected_panel_variant_ids"][
        "kissing_number_sphere_packing"
    ] == ["full_system", "no_context_in_prompt", "no_evolution"]
    assert all(record["source_anchor_present"] for record in boundary["claim_records"])
    assert "six matrix series" in boundary["claim_boundary"]
    assert "three kissing-number series" in boundary["claim_boundary"]


def test_ablation_claim_inventory_gives_every_gap_todo_ownership():
    boundary = alphaevolve_ablation_claim_inventory_boundary_record()

    incomplete = [
        record
        for record in boundary["claim_records"]
        if record["implementation_status"] != "implemented_local"
    ]

    assert len(incomplete) == 49
    assert all(record["active_todo_refs"] for record in incomplete)
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in incomplete
        for ref in record["active_todo_refs"]
    )


def test_ablation_claim_inventory_rejects_record_shape_and_overclaim_drift():
    boundary = deepcopy(alphaevolve_ablation_claim_inventory_boundary_record())
    boundary["claim_records"][0]["implementation_status"] = "implemented_local"
    boundary["figure8_source_shape"]["registry_panel_variant_ids"][
        "kissing_number_sphere_packing"
    ].append("small_base_llm_only")
    boundary["claim_count"] = 50
    boundary["alphaevolve_ablation_result_reproduction_claim_ready"] = True
    boundary["alphaevolve_parity_claim_ready"] = True

    validation = validate_alphaevolve_ablation_claim_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_claim_records" in codes
    assert "invalid_figure8_source_shape" in codes
    assert "invalid_claim_count" in codes
    assert "result_reproduction_overclaim" in codes
    assert "parity_overclaim" in codes


def test_ablation_claim_inventory_rejects_missing_pinned_source(tmp_path):
    boundary = alphaevolve_ablation_claim_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_ablation_claim_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["ablation_claim_inventory_ready"] is False
    assert "source_pdf_identity_mismatch" in codes
    assert "missing_source_anchor" in codes
    assert "missing_local_reference" in codes


def test_render_ablation_claim_inventory_summary_reports_shape():
    summary = render_alphaevolve_ablation_claim_inventory_boundary_summary(
        alphaevolve_ablation_claim_inventory_boundary_record()
    )

    assert "AlphaEvolve ablation claim inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| claim_count | 51 |" in summary
    assert "| implemented_local_count | 2 |" in summary
    assert "| implementation_gap_count | 49 |" in summary
    assert "| missing_anchor_count | 0 |" in summary
