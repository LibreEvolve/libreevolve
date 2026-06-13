from libreevolve.problems.benchmarks.arxiv_abstract_snapshot import (
    ALPHAEVOLVE_ARXIV_ABSTRACT_SNAPSHOT_SCHEMA,
    alphaevolve_arxiv_abstract_snapshot_record,
    render_alphaevolve_arxiv_abstract_snapshot_summary,
    validate_alphaevolve_arxiv_abstract_snapshot,
)


def test_alphaevolve_arxiv_abstract_snapshot_accepts_pinned_metadata():
    snapshot = alphaevolve_arxiv_abstract_snapshot_record()

    validation = validate_alphaevolve_arxiv_abstract_snapshot(snapshot)

    assert validation.ok is True
    assert validation.metadata_checked is True
    assert validation.live_refresh_checked is False
    assert validation.author_count == 18
    assert validation.subject_count == 3
    assert validation.missing_evidence_count == 5
    assert snapshot["schema"] == ALPHAEVOLVE_ARXIV_ABSTRACT_SNAPSHOT_SCHEMA
    assert snapshot["html_snapshot"]["bytes"] == 50098
    assert (
        snapshot["html_snapshot"]["sha256"]
        == "ab39ec118afe0874f34179b5a06c42a57799b1103f027942a1ecd54dc3d95471"
    )
    assert snapshot["normalized_metadata"]["subject_codes"] == ["cs.AI", "cs.LG", "cs.NE"]
    assert "does not commit the full HTML body" in snapshot["claim_boundary"]


def test_alphaevolve_arxiv_abstract_snapshot_rejects_digest_and_metadata_drift():
    snapshot = alphaevolve_arxiv_abstract_snapshot_record()
    snapshot["html_snapshot"]["sha256"] = "0" * 64
    snapshot["normalized_metadata"]["author_count"] = 17
    snapshot["missing_evidence"]["tex_source_archive_digest"] = "recorded"

    validation = validate_alphaevolve_arxiv_abstract_snapshot(snapshot)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_html_snapshot_sha256" in codes
    assert "invalid_metadata_author_count" in codes
    assert "invalid_missing_evidence_tex_source_archive_digest" in codes


def test_alphaevolve_arxiv_abstract_snapshot_live_refresh_detects_drift():
    snapshot = alphaevolve_arxiv_abstract_snapshot_record()
    live_snapshot = {
        "html_snapshot": dict(snapshot["html_snapshot"], bytes=50099),
        "normalized_metadata": dict(snapshot["normalized_metadata"]),
    }

    validation = validate_alphaevolve_arxiv_abstract_snapshot(
        snapshot,
        live_snapshot=live_snapshot,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.live_refresh_checked is True
    assert "live_html_snapshot_drift" in codes


def test_render_alphaevolve_arxiv_abstract_snapshot_summary_reports_shape():
    summary = render_alphaevolve_arxiv_abstract_snapshot_summary(
        alphaevolve_arxiv_abstract_snapshot_record()
    )

    assert "AlphaEvolve arXiv abstract snapshot" in summary
    assert "| schema_status | ok |" in summary
    assert "| metadata_checked | True |" in summary
    assert "| author_count | 18 |" in summary
    assert "| subject_count | 3 |" in summary
