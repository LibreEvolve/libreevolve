from pathlib import Path

from libreevolve.problems.benchmarks.alphaevolve_cached_pdf_header_consistency_boundary import (
    ALPHAEVOLVE_CACHED_PDF_HEADER_CONSISTENCY_BOUNDARY_SCHEMA,
    alphaevolve_cached_pdf_header_consistency_boundary_record,
    render_alphaevolve_cached_pdf_header_consistency_boundary_summary,
    validate_alphaevolve_cached_pdf_header_consistency_boundary,
)


def test_alphaevolve_cached_pdf_header_consistency_boundary_accepts_record():
    boundary = alphaevolve_cached_pdf_header_consistency_boundary_record()

    validation = validate_alphaevolve_cached_pdf_header_consistency_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "cached_pdf_header_consistency_recorded_without_refresh_gate"
    )
    assert validation.header_checked is False
    assert validation.missing_evidence_count == 1
    assert boundary["schema"] == ALPHAEVOLVE_CACHED_PDF_HEADER_CONSISTENCY_BOUNDARY_SCHEMA
    assert boundary["pdf_artifact"]["artifact_retained"] is True
    assert boundary["first_page_extraction"]["required_markers"]["has_arxiv_header"] is True


def test_alphaevolve_cached_pdf_header_consistency_boundary_rejects_overclaim():
    boundary = alphaevolve_cached_pdf_header_consistency_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "cached_pdf_header_refresh_gate_ready"
    boundary["first_page_extraction"]["normalized_text_sha256"] = "0" * 64
    boundary["missing_evidence"]["automated_cached_pdf_header_refresh_gate"] = "recorded"

    validation = validate_alphaevolve_cached_pdf_header_consistency_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_first_page_extraction_normalized_text_sha256" in codes
    assert "invalid_missing_evidence_automated_cached_pdf_header_refresh_gate" in codes


def test_alphaevolve_cached_pdf_header_consistency_boundary_validates_pdf_file(tmp_path):
    repo_root = tmp_path
    papers_dir = repo_root / "papers"
    papers_dir.mkdir()
    source_root = Path(__file__).resolve().parents[1]
    (papers_dir / "2506.13131__AlphaEvolve.pdf").write_bytes(
        (source_root / "papers" / "2506.13131__AlphaEvolve.pdf").read_bytes()
    )
    boundary_path = papers_dir / "alphaevolve_cached_pdf_header_consistency_boundary.json"
    boundary_path.write_text(
        (source_root / "papers" / "alphaevolve_cached_pdf_header_consistency_boundary.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    validation = validate_alphaevolve_cached_pdf_header_consistency_boundary(boundary_path)

    assert validation.ok is True
    assert validation.header_checked is True
    assert validation.missing_evidence_count == 1


def test_render_alphaevolve_cached_pdf_header_consistency_boundary_summary_reports_shape():
    summary = render_alphaevolve_cached_pdf_header_consistency_boundary_summary(
        alphaevolve_cached_pdf_header_consistency_boundary_record()
    )

    assert "AlphaEvolve cached-PDF header consistency boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | cached_pdf_header_consistency_recorded_without_refresh_gate |"
        in summary
    )
    assert "| missing_evidence_count | 1 |" in summary
