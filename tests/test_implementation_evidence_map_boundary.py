from libreevolve.problems.benchmarks.implementation_evidence_map_boundary import (
    IMPLEMENTATION_EVIDENCE_MAP_BOUNDARY_SCHEMA,
    implementation_evidence_map_boundary_record,
    render_implementation_evidence_map_boundary_summary,
    validate_implementation_evidence_map_boundary,
)


def test_implementation_evidence_map_boundary_accepts_core_requirement_anchors():
    boundary = implementation_evidence_map_boundary_record()

    validation = validate_implementation_evidence_map_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "verified_core_anchors_plus_833_bounded_claims_and_195_citation_uses_without_whole_paper_exhaustiveness"
    )
    assert validation.requirement_count == 6
    assert validation.reference_check_count == 81
    assert validation.missing_evidence_count == 10
    assert boundary["schema"] == IMPLEMENTATION_EVIDENCE_MAP_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["context_claim_inventory_ref"] == (
        "papers/alphaevolve_context_claim_inventory_boundary.json"
    )
    assert boundary["matrix_result_claim_inventory_ref"] == (
        "papers/alphaevolve_matrix_result_claim_inventory_boundary.json"
    )
    assert boundary["math_result_claim_inventory_ref"] == (
        "papers/alphaevolve_math_result_claim_inventory_boundary.json"
    )
    assert boundary["scheduling_claim_inventory_ref"] == (
        "papers/alphaevolve_scheduling_claim_inventory_boundary.json"
    )
    assert boundary["kernel_claim_inventory_ref"] == (
        "papers/alphaevolve_kernel_claim_inventory_boundary.json"
    )
    assert boundary["hardware_claim_inventory_ref"] == (
        "papers/alphaevolve_hardware_claim_inventory_boundary.json"
    )
    assert boundary["compiler_claim_inventory_ref"] == (
        "papers/alphaevolve_compiler_claim_inventory_boundary.json"
    )
    assert boundary["ablation_claim_inventory_ref"] == (
        "papers/alphaevolve_ablation_claim_inventory_boundary.json"
    )
    assert boundary["related_work_claim_inventory_ref"] == (
        "papers/alphaevolve_related_work_claim_inventory_boundary.json"
    )
    assert boundary["appendix_a_claim_inventory_ref"] == (
        "papers/alphaevolve_appendix_a_claim_inventory_boundary.json"
    )
    assert boundary["appendix_b_claim_inventory_ref"] == (
        "papers/alphaevolve_appendix_b_claim_inventory_boundary.json"
    )
    assert boundary["citation_use_inventory_ref"] == (
        "papers/alphaevolve_citation_use_inventory_boundary.json"
    )
    assert boundary["recorded_evidence"]["lexical_citation_use_inventory"] == (
        "195_tex_citation_uses_240_key_links_and_120_compiled_references"
    )
    assert boundary["missing_evidence"]["citation_semantic_mapping"] == (
        "195_citation_uses_lexically_linked_without_supported_proposition_source_sufficiency_or_implementation_relevance_classification"
    )
    requirement_ids = {
        requirement["requirement_id"] for requirement in boundary["requirements"]
    }
    assert "alphaevolve_program_markers" in requirement_ids
    assert "alphaevolve_published_benchmarks" in requirement_ids
    requirement_by_id = {
        requirement["requirement_id"]: requirement
        for requirement in boundary["requirements"]
    }
    assert requirement_by_id["alphaevolve_evaluator_cascade"]["source_refs"] == [
        "2506.13131:Section 2.4"
    ]
    assert requirement_by_id["alphaevolve_llm_sampling_and_prompting"][
        "source_span_ids"
    ] == ["section_2_2", "section_2_3"]
    assert requirement_by_id["alphaevolve_evolutionary_database"][
        "source_refs"
    ][0] == "2506.13131:Section 2.5"
    assert requirement_by_id["alphaevolve_async_distributed_pipeline"][
        "source_refs"
    ][1] == "2506.13131:Section 2.6"
    assert (
        boundary["missing_evidence"]["status_cell_semantic_verifier"]
        == "not_recorded_locally"
    )
    assert (
        boundary["missing_evidence"]["implemented_benchmark_bullet_semantic_verifier"]
        == "not_recorded_locally"
    )
    assert "does not claim a whole-paper exhaustive requirement inventory" in boundary["claim_boundary"]
    assert "whole-paper claim-level source-span coverage matrix" in boundary["claim_boundary"]
    assert "absence-sentence freshness matrix" in boundary["claim_boundary"]
    assert "does not classify citation semantics" in boundary["claim_boundary"]


def test_implementation_evidence_map_boundary_rejects_exhaustive_overclaim():
    boundary = implementation_evidence_map_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "exhaustive_alphaevolve_implementation_audit_ready"
    boundary["missing_evidence"]["exhaustive_requirement_inventory"] = "recorded"
    boundary["requirements"] = boundary["requirements"][1:]

    validation = validate_implementation_evidence_map_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_exhaustive_requirement_inventory" in codes
    assert "missing_requirement_id" in codes


def test_implementation_evidence_map_boundary_rejects_anchor_drift():
    boundary = implementation_evidence_map_boundary_record()
    boundary["requirements"][0]["module_refs"] = ["libreevolve/core/loop.py"]

    validation = validate_implementation_evidence_map_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_alphaevolve_program_markers_module_refs" in codes


def test_implementation_evidence_map_boundary_rejects_missing_local_reference():
    boundary = implementation_evidence_map_boundary_record()
    boundary["requirements"][0]["test_refs"] = ["tests/does_not_exist.py"]

    validation = validate_implementation_evidence_map_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_alphaevolve_program_markers_test_refs" in codes
    assert "missing_test_ref" in codes


def test_render_implementation_evidence_map_boundary_summary_reports_shape():
    summary = render_implementation_evidence_map_boundary_summary(
        implementation_evidence_map_boundary_record()
    )

    assert "Implementation evidence map boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | verified_core_anchors_plus_833_bounded_claims_and_195_citation_uses_without_whole_paper_exhaustiveness |"
        in summary
    )
    assert "| requirement_count | 6 |" in summary
    assert "| reference_check_count | 81 |" in summary
    assert "| missing_evidence_count | 10 |" in summary
