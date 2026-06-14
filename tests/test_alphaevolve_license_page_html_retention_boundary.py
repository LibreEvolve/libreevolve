from pathlib import Path

from libreevolve.problems.benchmarks.alphaevolve_license_page_html_retention_boundary import (
    ALPHAEVOLVE_LICENSE_PAGE_HTML_RETENTION_BOUNDARY_SCHEMA,
    alphaevolve_license_page_html_retention_boundary_record,
    render_alphaevolve_license_page_html_retention_boundary_summary,
    validate_alphaevolve_license_page_html_retention_boundary,
)


def test_alphaevolve_license_page_html_retention_boundary_accepts_record():
    boundary = alphaevolve_license_page_html_retention_boundary_record()

    validation = validate_alphaevolve_license_page_html_retention_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "license_page_html_retained_without_refresh_gate"
    assert validation.html_artifact_retained is True
    assert validation.html_artifact_bytes == 36988
    assert validation.required_evidence_field_count == 16
    assert validation.missing_evidence_count == 1
    assert boundary["schema"] == ALPHAEVOLVE_LICENSE_PAGE_HTML_RETENTION_BOUNDARY_SCHEMA
    assert boundary["html_content_markers"]["has_license_title"] is True


def test_alphaevolve_license_page_html_retention_boundary_rejects_refresh_overclaim():
    boundary = alphaevolve_license_page_html_retention_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "license_page_refresh_gate_ready"
    boundary["html_content_markers"]["has_license_title"] = False
    boundary["missing_evidence"]["license_page_refresh_gate"] = "recorded"

    validation = validate_alphaevolve_license_page_html_retention_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_html_content_marker_has_license_title" in codes
    assert "invalid_missing_evidence_license_page_refresh_gate" in codes


def test_alphaevolve_license_page_html_retention_boundary_validates_retained_file(tmp_path):
    repo_root = tmp_path
    papers_dir = repo_root / "papers"
    papers_dir.mkdir()
    source_root = Path(__file__).resolve().parents[1]
    (papers_dir / "alphaevolve_license_page.html").write_bytes(
        (source_root / "papers" / "alphaevolve_license_page.html").read_bytes()
    )
    boundary_path = papers_dir / "alphaevolve_license_page_html_retention_boundary.json"
    boundary_path.write_text(
        Path(source_root / "papers" / "alphaevolve_license_page_html_retention_boundary.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    validation = validate_alphaevolve_license_page_html_retention_boundary(boundary_path)

    assert validation.ok is True
    assert validation.html_artifact_bytes == 36988


def test_render_alphaevolve_license_page_html_retention_boundary_summary_reports_shape():
    summary = render_alphaevolve_license_page_html_retention_boundary_summary(
        alphaevolve_license_page_html_retention_boundary_record()
    )

    assert "AlphaEvolve license-page HTML retention boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | license_page_html_retained_without_refresh_gate |" in summary
    assert "| html_artifact_retained | True |" in summary
    assert "| html_artifact_bytes | 36988 |" in summary
