from libreevolve.problems.benchmarks.roadmap_readiness_publication_boundary import (
    ROADMAP_READINESS_PUBLICATION_BOUNDARY_SCHEMA,
    render_roadmap_readiness_publication_boundary_summary,
    roadmap_readiness_publication_boundary_record,
    validate_roadmap_readiness_publication_boundary,
)


def test_roadmap_readiness_publication_accepts_bounded_gate():
    boundary = roadmap_readiness_publication_boundary_record()

    validation = validate_roadmap_readiness_publication_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_readiness_publication_gate_without_semantic_alphaevolve_certification"
    )
    assert boundary["schema"] == ROADMAP_READINESS_PUBLICATION_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["source_readiness_boundary_input"] == "papers/roadmap_readiness_boundary.json"
    assert boundary["source_category_count"] == 4
    assert boundary["source_category_weight_total"] == 100
    assert boundary["source_missing_evidence_count"] == 6
    assert (
        boundary["source_readiness_percent_status"]
        == "todo_ledger_only_not_semantic_alphaevolve_readiness"
    )
    assert boundary["publication_criterion_count"] == 8
    assert boundary["sidecar_ref_count"] == 16
    assert boundary["active_todo_ref_count"] == 16
    assert [record["criterion_id"] for record in boundary["publication_criteria"]] == [
        "semantic_requirement_source_mapping",
        "canonical_gap_completion_policy",
        "per_category_evidence_gate",
        "benchmark_reproduction_certification",
        "operational_release_readiness_gate",
        "uncertainty_and_percentage_labels",
        "stale_count_detector",
        "publication_claim_boundary",
    ]
    assert all(
        sidecar["exists"]
        for record in boundary["publication_criteria"]
        for sidecar in record["sidecar_refs"]
    )
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in boundary["publication_criteria"]
        for ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "requirement_level_source_span_mapping": "not_recorded_locally",
        "canonical_underlying_gap_deduplication": "not_recorded_locally",
        "per_category_code_test_runtime_artifact_proof_map": "not_recorded_locally",
        "benchmark_reproduction_certification": "not_recorded_locally",
        "operational_release_readiness_gate": "not_recorded_locally",
        "readiness_uncertainty_labels": "not_recorded_locally",
        "stale_count_detector": "not_recorded_locally",
        "readiness_percentage_publication_policy": "not_recorded_locally",
    }
    assert "does not claim requirement-level source-span mapping" in boundary["claim_boundary"]
    assert "stale-count detector" in boundary["claim_boundary"]
    assert "semantic AlphaEvolve implementation parity" in boundary["claim_boundary"]


def test_roadmap_readiness_publication_rejects_overclaim_and_drift():
    boundary = roadmap_readiness_publication_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "semantic_alphaevolve_certification_ready"
    boundary["publication_criterion_count"] = 7
    boundary["source_category_count"] = 3
    boundary["publication_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["publication_criteria"][0]["active_todo_refs"][0][
        "required_phrase_present"
    ] = False
    boundary["missing_evidence"]["requirement_level_source_span_mapping"] = "recorded"
    boundary["required_evidence_fields"] = ["publication_criteria"]

    validation = validate_roadmap_readiness_publication_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_category_count" in codes
    assert "invalid_publication_criterion_count" in codes
    assert "invalid_publication_criteria" in codes
    assert "invalid_missing_evidence_requirement_level_source_span_mapping" in codes
    assert "missing_required_evidence_field" in codes
    assert "invalid_required_evidence_field_count" in codes


def test_render_roadmap_readiness_publication_summary_reports_shape():
    summary = render_roadmap_readiness_publication_boundary_summary(
        roadmap_readiness_publication_boundary_record()
    )

    assert "ROADMAP readiness publication boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_readiness_publication_gate_without_semantic_alphaevolve_certification |"
        in summary
    )
    assert "| publication_criterion_count | 8 |" in summary
    assert "| sidecar_ref_count | 16 |" in summary
    assert "| active_todo_ref_count | 16 |" in summary
    assert "| missing_evidence_count | 8 |" in summary
