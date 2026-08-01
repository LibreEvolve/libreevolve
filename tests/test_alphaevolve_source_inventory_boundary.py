from libreevolve.problems.benchmarks.alphaevolve_source_inventory_boundary import (
    ALPHAEVOLVE_SOURCE_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_source_inventory_boundary_record,
    render_alphaevolve_source_inventory_boundary_summary,
    validate_alphaevolve_source_inventory_boundary,
)


def test_alphaevolve_source_inventory_accepts_pdf_verified_named_structure():
    boundary = alphaevolve_source_inventory_boundary_record()

    validation = validate_alphaevolve_source_inventory_boundary(boundary)

    assert validation.ok is True
    assert boundary["schema"] == ALPHAEVOLVE_SOURCE_INVENTORY_BOUNDARY_SCHEMA
    assert (
        validation.boundary_status
        == "complete_named_structure_inventory_without_claim_level_exhaustiveness"
    )
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["source_artifact"]["page_count"] == 44
    assert boundary["named_structure_inventory_ready"] is True
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert validation.span_count == 55
    assert validation.anchor_count == 57
    assert validation.missing_anchor_count == 0
    assert validation.missing_reference_count == 0
    assert boundary["source_kind_counts"] == {
        "figure": 14,
        "structure": 38,
        "table": 3,
    }
    assert boundary["span_records"][0]["span_id"] == "abstract"
    assert boundary["span_records"][-1]["span_id"] == "table_3"
    figure_9 = next(
        record for record in boundary["span_records"] if record["span_id"] == "figure_9"
    )
    assert [anchor["page"] for anchor in figure_9["anchor_checks"]] == [35, 36, 37]
    section_5 = next(
        record for record in boundary["span_records"] if record["span_id"] == "section_5"
    )
    assert section_5["local_status"] == (
        "mixed_implemented_partial_missing_undemonstrated_and_background_context"
    )
    assert "papers/alphaevolve_related_work_claim_inventory_boundary.json" in {
        ref["path"] for ref in section_5["sidecar_refs"]
    }
    assert len(section_5["active_todo_refs"]) == 2
    assert "requirement-level exhaustiveness" in boundary["claim_boundary"]


def test_alphaevolve_source_inventory_rejects_span_and_parity_drift():
    boundary = alphaevolve_source_inventory_boundary_record()
    boundary["span_records"] = boundary["span_records"][1:]
    boundary["span_count"] = 54
    boundary["alphaevolve_parity_claim_ready"] = True

    validation = validate_alphaevolve_source_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_span_records" in codes
    assert "invalid_span_count" in codes
    assert "parity_overclaim" in codes


def test_alphaevolve_source_inventory_rejects_missing_pinned_source(tmp_path):
    boundary = alphaevolve_source_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_source_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["named_structure_inventory_ready"] is False
    assert "source_pdf_identity_mismatch" in codes
    assert "missing_source_anchor" in codes
    assert "missing_local_reference" in codes


def test_render_alphaevolve_source_inventory_summary_reports_shape():
    summary = render_alphaevolve_source_inventory_boundary_summary(
        alphaevolve_source_inventory_boundary_record()
    )

    assert "AlphaEvolve source inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| span_count | 55 |" in summary
    assert "| anchor_count | 57 |" in summary
    assert "| missing_anchor_count | 0 |" in summary
