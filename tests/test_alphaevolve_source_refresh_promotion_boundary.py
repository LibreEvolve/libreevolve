from pathlib import Path

from libreevolve.problems.benchmarks.alphaevolve_source_refresh_promotion_boundary import (
    ALPHAEVOLVE_SOURCE_REFRESH_PROMOTION_BOUNDARY_SCHEMA,
    alphaevolve_source_refresh_promotion_boundary_record,
    render_alphaevolve_source_refresh_promotion_boundary_summary,
    validate_alphaevolve_source_refresh_promotion_boundary,
)


def test_alphaevolve_source_refresh_promotion_boundary_accepts_record():
    boundary = alphaevolve_source_refresh_promotion_boundary_record()

    validation = validate_alphaevolve_source_refresh_promotion_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "central_refresh_gate_coverage_recorded_without_individual_sidecar_promotion"
    )
    assert validation.source_count == 6
    assert validation.linked_sidecar_count == 10
    assert validation.missing_evidence_count == 1
    assert boundary["schema"] == ALPHAEVOLVE_SOURCE_REFRESH_PROMOTION_BOUNDARY_SCHEMA


def test_alphaevolve_source_refresh_promotion_boundary_rejects_overclaim():
    boundary = alphaevolve_source_refresh_promotion_boundary_record()
    boundary["claim_ready"] = True
    boundary["promotion_policy"] = "all_sidecars_individually_refresh_ready"
    boundary["source_sidecar_map"][0]["promotion_status"] = "refresh_ready"
    boundary["source_sidecar_map"][1]["sidecars"] = ["papers/wrong.json"]
    boundary["missing_evidence"]["scheduled_ci_refresh_run_history"] = "recorded"

    validation = validate_alphaevolve_source_refresh_promotion_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_promotion_policy" in codes
    assert "invalid_promotion_status" in codes
    assert "invalid_current_abstract_sidecars" in codes
    assert (
        "invalid_missing_evidence_scheduled_ci_refresh_run_history"
        in codes
    )


def test_alphaevolve_source_refresh_promotion_boundary_validates_repo_files():
    validation = validate_alphaevolve_source_refresh_promotion_boundary(
        "papers/alphaevolve_source_refresh_promotion_boundary.json"
    )

    assert validation.ok is True
    assert validation.linked_sidecars_checked is True


def test_alphaevolve_source_refresh_promotion_boundary_detects_missing_linked_file(tmp_path):
    source_root = Path(__file__).resolve().parents[1]
    sidecar = tmp_path / "papers" / "alphaevolve_source_refresh_promotion_boundary.json"
    sidecar.parent.mkdir()
    sidecar.write_text(
        (source_root / "papers" / "alphaevolve_source_refresh_promotion_boundary.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    validation = validate_alphaevolve_source_refresh_promotion_boundary(sidecar)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_linked_sidecar_file" in codes


def test_render_alphaevolve_source_refresh_promotion_boundary_summary_reports_shape():
    summary = render_alphaevolve_source_refresh_promotion_boundary_summary(
        alphaevolve_source_refresh_promotion_boundary_record()
    )

    assert "AlphaEvolve source refresh-promotion boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | central_refresh_gate_coverage_recorded_without_individual_sidecar_promotion |"
        in summary
    )
    assert "| source_count | 6 |" in summary
    assert "| linked_sidecar_count | 10 |" in summary
