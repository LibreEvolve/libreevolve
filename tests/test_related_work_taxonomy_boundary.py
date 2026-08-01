from libreevolve.problems.benchmarks.related_work_taxonomy_boundary import (
    RELATED_WORK_TAXONOMY_BOUNDARY_SCHEMA,
    related_work_taxonomy_boundary_record,
    render_related_work_taxonomy_boundary_summary,
    validate_related_work_taxonomy_boundary,
)


def test_related_work_taxonomy_boundary_accepts_bounded_taxonomy_boundary():
    boundary = related_work_taxonomy_boundary_record()

    validation = validate_related_work_taxonomy_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "related_work_taxonomy_records_without_positioning_readiness"
    )
    assert validation.required_evidence_field_count == 16
    assert validation.missing_evidence_count == 4
    assert boundary["schema"] == RELATED_WORK_TAXONOMY_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["5"]
    assert boundary["taxonomy_record_count"] == 11
    assert {record["source_id"] for record in boundary["taxonomy_records"]} >= {
        "alphaevolve",
        "funsearch",
        "ai_coscientist",
        "continuous_llm_finetuning",
        "llm_directed_concept_learning",
    }
    assert (
        boundary["claim_gates"]["readme_related_work_summary_gate"]
        == "scoped_to_taxonomy_boundary"
    )
    assert boundary["claim_ready"] is False
    assert (
        "bounded Section 5 Related Work taxonomy records"
        in boundary["claim_boundary"]
    )
    records = {record["source_id"]: record for record in boundary["taxonomy_records"]}
    assert records["alphaevolve"]["source_location"].endswith("PDF pages 18-20")
    assert records["ai_coscientist"]["source_location"].endswith("PDF page 19")
    assert records["continuous_llm_finetuning"]["source_location"].endswith(
        "PDF page 19"
    )
    assert records["llm_directed_concept_learning"]["source_location"].endswith(
        "PDF page 19"
    )


def test_related_work_taxonomy_boundary_rejects_positioning_overclaim():
    boundary = related_work_taxonomy_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "related_work_taxonomy_ready"
    boundary["source_section_ids"] = ["4"]
    boundary["missing_evidence"]["local_implementation_parity_evidence"] = "recorded"
    boundary["required_evidence_fields"] = ["source_paper_inventory"]
    boundary["taxonomy_records"][0]["local_implementation_status"] = "implemented_full"
    boundary["taxonomy_records"][1]["source_location"] = "README"
    boundary["claim_gates"]["readme_related_work_summary_gate"] = "ready"

    validation = validate_related_work_taxonomy_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_local_implementation_parity_evidence" in codes
    assert "missing_required_evidence_field" in codes
    assert "invalid_taxonomy_record_local_status" in codes
    assert "invalid_taxonomy_record_source_location" in codes
    assert "invalid_claim_gate_readme_related_work_summary_gate" in codes


def test_render_related_work_taxonomy_boundary_summary_reports_shape():
    summary = render_related_work_taxonomy_boundary_summary(
        related_work_taxonomy_boundary_record()
    )

    assert "Related Work taxonomy boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | related_work_taxonomy_records_without_positioning_readiness |"
        in summary
    )
    assert "| required_evidence_field_count | 16 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
