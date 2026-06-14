from pathlib import Path

from libreevolve.problems.benchmarks.alphaevolve_tex_archive_retention_boundary import (
    ALPHAEVOLVE_TEX_ARCHIVE_RETENTION_BOUNDARY_SCHEMA,
    alphaevolve_tex_archive_retention_boundary_record,
    render_alphaevolve_tex_archive_retention_boundary_summary,
    validate_alphaevolve_tex_archive_retention_boundary,
)


def test_alphaevolve_tex_archive_retention_boundary_accepts_record():
    boundary = alphaevolve_tex_archive_retention_boundary_record()

    validation = validate_alphaevolve_tex_archive_retention_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "tex_archive_retained_with_member_inventory_without_refresh_gate"
    )
    assert validation.archive_artifact_retained is True
    assert validation.member_count == 58
    assert validation.required_evidence_field_count == 15
    assert validation.missing_evidence_count == 2
    assert boundary["schema"] == ALPHAEVOLVE_TEX_ARCHIVE_RETENTION_BOUNDARY_SCHEMA
    assert boundary["archive_member_inventory"]["file_count"] == 54
    assert boundary["archive_member_inventory"]["dir_count"] == 4


def test_alphaevolve_tex_archive_retention_boundary_rejects_refresh_overclaim():
    boundary = alphaevolve_tex_archive_retention_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "tex_archive_refresh_gate_ready"
    boundary["archive_member_inventory"]["member_count"] = 1
    boundary["missing_evidence"]["tex_source_refresh_gate"] = "recorded"

    validation = validate_alphaevolve_tex_archive_retention_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_archive_member_inventory_member_count" in codes
    assert "invalid_missing_evidence_tex_source_refresh_gate" in codes


def test_alphaevolve_tex_archive_retention_boundary_validates_retained_file(tmp_path):
    repo_root = tmp_path
    papers_dir = repo_root / "papers"
    papers_dir.mkdir()
    source_root = Path(__file__).resolve().parents[1]
    archive_bytes = (source_root / "papers" / "alphaevolve_tex_source_archive.tar.gz").read_bytes()
    (papers_dir / "alphaevolve_tex_source_archive.tar.gz").write_bytes(archive_bytes)
    boundary_path = papers_dir / "alphaevolve_tex_archive_retention_boundary.json"
    boundary_path.write_text(
        Path(source_root / "papers" / "alphaevolve_tex_archive_retention_boundary.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    validation = validate_alphaevolve_tex_archive_retention_boundary(boundary_path)

    assert validation.ok is True
    assert validation.member_count == 58


def test_render_alphaevolve_tex_archive_retention_boundary_summary_reports_shape():
    summary = render_alphaevolve_tex_archive_retention_boundary_summary(
        alphaevolve_tex_archive_retention_boundary_record()
    )

    assert "AlphaEvolve TeX archive retention boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | tex_archive_retained_with_member_inventory_without_refresh_gate |"
        in summary
    )
    assert "| archive_artifact_retained | True |" in summary
    assert "| member_count | 58 |" in summary
