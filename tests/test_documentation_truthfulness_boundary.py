from libreevolve.problems.benchmarks.documentation_truthfulness_boundary import (
    DOCUMENTATION_TRUTHFULNESS_BOUNDARY_SCHEMA,
    documentation_truthfulness_boundary_record,
    render_documentation_truthfulness_boundary_summary,
    validate_documentation_truthfulness_boundary,
)


def test_documentation_truthfulness_boundary_accepts_cross_document_guards():
    boundary = documentation_truthfulness_boundary_record()

    validation = validate_documentation_truthfulness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "cross_document_guards_without_semantic_claim_proof"
    )
    assert validation.required_evidence_field_count == 32
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == DOCUMENTATION_TRUTHFULNESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "documentation_claim_inventory" in boundary["required_evidence_fields"]
    assert "tracked_legacy_surface_inventory" in boundary["required_evidence_fields"]
    assert "docs_index_reader_path_inventory" in boundary["required_evidence_fields"]
    assert "docs_status_ledger_inventory" in boundary["required_evidence_fields"]
    assert "docs_architecture_runtime_flow_inventory" in boundary["required_evidence_fields"]
    assert "readme_agent_routing_inventory" in boundary["required_evidence_fields"]
    assert "readme_documentation_map_inventory" in boundary["required_evidence_fields"]
    assert "readme_repository_layout_inventory" in boundary["required_evidence_fields"]
    assert "readme_quick_start_smoke_inventory" in boundary["required_evidence_fields"]
    assert "readme_install_smoke_inventory" in boundary["required_evidence_fields"]
    assert "readme_provider_auth_inventory" in boundary["required_evidence_fields"]
    assert "readme_provider_example_matrix_inventory" in boundary["required_evidence_fields"]
    assert "readme_paper_cache_topic_inventory" in boundary["required_evidence_fields"]
    assert "readme_paper_cache_rehydrate_inventory" in boundary["required_evidence_fields"]
    assert (
        "does not claim semantic documentation-claim verification"
        in boundary["claim_boundary"]
    )
    assert "tracked legacy-surface inventory" in boundary["claim_boundary"]
    assert "docs-index reader-path inventory" in boundary["claim_boundary"]
    assert "docs/architecture.md runtime-flow inventory" in boundary["claim_boundary"]
    assert "docs/status.md ledger inventory" in boundary["claim_boundary"]
    assert "README AGENTS.md routing inventory" in boundary["claim_boundary"]
    assert "README Documentation Map inventory" in boundary["claim_boundary"]
    assert "README Repository Layout inventory" in boundary["claim_boundary"]
    assert "README quick-start smoke inventory" in boundary["claim_boundary"]
    assert "README install-smoke inventory" in boundary["claim_boundary"]
    assert "README provider-auth setup inventory" in boundary["claim_boundary"]
    assert "README provider-example matrix inventory" in boundary["claim_boundary"]
    assert "README paper-cache topic inventory" in boundary["claim_boundary"]
    assert "README paper-cache rehydrate inventory" in boundary["claim_boundary"]


def test_documentation_truthfulness_boundary_rejects_semantic_proof_overclaim():
    boundary = documentation_truthfulness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_semantic_documentation_truth_proof_ready"
    boundary["missing_evidence"]["semantic_claim_verifier"] = "recorded"
    boundary["required_evidence_fields"] = ["readme_status_scope"]

    validation = validate_documentation_truthfulness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_semantic_claim_verifier" in codes
    assert "missing_required_evidence_field" in codes


def test_render_documentation_truthfulness_boundary_summary_reports_shape():
    summary = render_documentation_truthfulness_boundary_summary(
        documentation_truthfulness_boundary_record()
    )

    assert "Documentation truthfulness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | cross_document_guards_without_semantic_claim_proof |"
        in summary
    )
    assert "| required_evidence_field_count | 32 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
