from libreevolve.problems.benchmarks.alphaevolve_tex_source_boundary import (
    ALPHAEVOLVE_TEX_SOURCE_BOUNDARY_SCHEMA,
    alphaevolve_tex_source_boundary_record,
    render_alphaevolve_tex_source_boundary_summary,
    validate_alphaevolve_tex_source_boundary,
)


def test_alphaevolve_tex_source_boundary_accepts_eprint_digest_record():
    boundary = alphaevolve_tex_source_boundary_record()

    validation = validate_alphaevolve_tex_source_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "tex_eprint_digest_without_archive_retention_or_refresh_gate"
    )
    assert validation.required_evidence_field_count == 15
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == ALPHAEVOLVE_TEX_SOURCE_BOUNDARY_SCHEMA
    assert boundary["tex_eprint_snapshot"]["response_bytes"] == 2635462
    assert (
        boundary["tex_eprint_snapshot"]["response_sha256"]
        == "a3ea37c5b6fe967fba459f0daca8548a78e2a1eac45e5c2aac83051ef113f21d"
    )


def test_alphaevolve_tex_source_boundary_rejects_archive_overclaim():
    boundary = alphaevolve_tex_source_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_tex_source_archive_refresh_gate_ready"
    boundary["tex_eprint_snapshot"]["response_bytes"] = 1
    boundary["missing_evidence"]["full_raw_archive_artifact"] = "recorded"

    validation = validate_alphaevolve_tex_source_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_snapshot_response_bytes" in codes
    assert "invalid_missing_evidence_full_raw_archive_artifact" in codes


def test_render_alphaevolve_tex_source_boundary_summary_reports_shape():
    summary = render_alphaevolve_tex_source_boundary_summary(
        alphaevolve_tex_source_boundary_record()
    )

    assert "AlphaEvolve TeX source boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | tex_eprint_digest_without_archive_retention_or_refresh_gate |"
        in summary
    )
    assert "| required_evidence_field_count | 15 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
