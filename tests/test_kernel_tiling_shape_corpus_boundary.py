from libreevolve.problems.benchmarks.kernel_tiling_shape_corpus_boundary import (
    KERNEL_TILING_SHAPE_CORPUS_BOUNDARY_SCHEMA,
    kernel_tiling_shape_corpus_boundary_record,
    render_kernel_tiling_shape_corpus_boundary_summary,
    validate_kernel_tiling_shape_corpus_boundary,
)


def test_kernel_tiling_shape_corpus_boundary_accepts_generic_kernel_boundary():
    boundary = kernel_tiling_shape_corpus_boundary_record()

    validation = validate_kernel_tiling_shape_corpus_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "generic_kernel_gates_without_pallas_shape_corpus"
    )
    assert validation.required_evidence_field_count == 20
    assert validation.missing_evidence_count == 16
    assert boundary["schema"] == KERNEL_TILING_SHAPE_CORPUS_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["3.3.2"]
    assert boundary["claim_ready"] is False
    assert "does not claim collected input shape corpora" in boundary["claim_boundary"]


def test_kernel_tiling_shape_corpus_boundary_rejects_pallas_overclaim():
    boundary = kernel_tiling_shape_corpus_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "pallas_shape_corpus_runtime_ready"
    boundary["missing_evidence"]["real_accelerator_runtime_artifacts"] = "recorded"
    boundary["required_evidence_fields"] = ["kernel_domain_gate_records"]

    validation = validate_kernel_tiling_shape_corpus_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_real_accelerator_runtime_artifacts" in codes
    assert "missing_required_evidence_field" in codes


def test_render_kernel_tiling_shape_corpus_boundary_summary_reports_shape():
    summary = render_kernel_tiling_shape_corpus_boundary_summary(
        kernel_tiling_shape_corpus_boundary_record()
    )

    assert "Kernel tiling shape-corpus boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | generic_kernel_gates_without_pallas_shape_corpus |"
        in summary
    )
    assert "| required_evidence_field_count | 20 |" in summary
    assert "| missing_evidence_count | 16 |" in summary
