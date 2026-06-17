from libreevolve.problems.benchmarks.alphaevolve_ui_api_attribution_boundary import (
    ALPHAEVOLVE_UI_API_ATTRIBUTION_BOUNDARY_SCHEMA,
    alphaevolve_ui_api_attribution_boundary_record,
    render_alphaevolve_ui_api_attribution_boundary_summary,
    validate_alphaevolve_ui_api_attribution_boundary,
)


def test_alphaevolve_ui_api_attribution_boundary_accepts_source_scope():
    boundary = alphaevolve_ui_api_attribution_boundary_record()

    validation = validate_alphaevolve_ui_api_attribution_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "official_impact_attribution_without_ui_api_artifact_inventory"
    )
    assert validation.ui_collaborator_count == 13
    assert validation.api_cloud_collaborator_count == 14
    assert validation.required_evidence_field_count == 22
    assert validation.missing_evidence_count == 12
    assert boundary["schema"] == ALPHAEVOLVE_UI_API_ATTRIBUTION_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "attribution evidence only" in boundary["claim_boundary"]
    assert "role-to-artifact link table" in boundary["claim_boundary"]


def test_alphaevolve_ui_api_attribution_boundary_rejects_artifact_overclaim():
    boundary = alphaevolve_ui_api_attribution_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "ui_api_artifacts_verified"
    boundary["missing_evidence"]["api_endpoint_schema_inventory"] = "recorded"
    boundary["required_evidence_fields"] = ["impact_article_url"]
    boundary["ui_collaborators"][0] = "Untracked Person"
    boundary["artifact_policy"]["role_links"] = "ready"

    validation = validate_alphaevolve_ui_api_attribution_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_api_endpoint_schema_inventory" in codes
    assert "missing_required_evidence_field" in codes
    assert "invalid_ui_collaborators_roster" in codes
    assert "invalid_artifact_policy_role_links" in codes


def test_render_alphaevolve_ui_api_attribution_boundary_summary_reports_shape():
    summary = render_alphaevolve_ui_api_attribution_boundary_summary(
        alphaevolve_ui_api_attribution_boundary_record()
    )

    assert "AlphaEvolve UI/API attribution boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| ui_collaborator_count | 13 |" in summary
    assert "| api_cloud_collaborator_count | 14 |" in summary
    assert "| required_evidence_field_count | 22 |" in summary
    assert "| missing_evidence_count | 12 |" in summary
