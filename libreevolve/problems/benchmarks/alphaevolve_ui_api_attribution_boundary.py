from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_UI_API_ATTRIBUTION_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_ui_api_attribution_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "official_impact_attribution_without_ui_api_artifact_inventory"
)
EXPECTED_UI_COLLABORATORS = (
    "Adam Connors",
    "Alex Bäuerle",
    "Anna Trostanetski",
    "Fernanda Viegas",
    "Gabi Cardoso",
    "Jonathan Caton",
    "Lucas Dixon",
    "Mariana Felix",
    "Martin Wattenberg",
    "Matin Akhlaghinia",
    "Richard Green",
    "Yosuke Ushigome",
    "Yunhan Xu",
)
EXPECTED_API_CLOUD_COLLABORATORS = (
    "Anant Nawalgaria",
    "Diego Ballesteros",
    "Gemma Jennings",
    "Jakob Oesinghaus",
    "Kartik Sanu",
    "Laurynas Tamulevičius",
    "Nicolas Stroppa",
    "Nishta Dhawan",
    "Oliver Hilsenbeck",
    "Puneet Jagralapudi",
    "Reah Miyara",
    "Skander Hannachi",
    "Tom Beyer",
    "Vishal Agarwal",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "impact_article_url",
    "impact_article_date",
    "impact_article_author_or_team",
    "impact_article_retrieval_html_sha256",
    "acknowledgements_section_snapshot",
    "role_category_definitions",
    "ui_collaborator_roster",
    "api_cloud_collaborator_roster",
    "product_team_attribution_boundary",
    "ui_surface_artifact_inventory",
    "ui_screenshot_or_source_snapshot",
    "interaction_flow_inventory",
    "api_endpoint_schema_inventory",
    "cloud_customer_engagement_artifacts",
    "role_to_artifact_link_table",
    "artifact_public_private_access_status",
    "privacy_contact_redaction_policy",
    "independent_artifact_verification",
    "local_ui_support_status",
    "local_managed_api_support_status",
    "local_customer_engagement_adapter_status",
    "readme_roadmap_paper_index_boundary",
)
EXPECTED_MISSING_EVIDENCE = {
    "ui_surface_artifact_inventory": "not_recorded_locally",
    "ui_screenshot_or_source_snapshot": "not_recorded_locally",
    "interaction_flow_inventory": "not_recorded_locally",
    "api_endpoint_schema_inventory": "not_recorded_locally",
    "cloud_customer_engagement_artifacts": "not_recorded_locally",
    "role_to_artifact_link_table": "not_recorded_locally",
    "artifact_public_private_access_status": "not_recorded_locally",
    "privacy_contact_redaction_policy": "not_recorded_locally",
    "independent_artifact_verification": "not_recorded_locally",
    "local_ui_support_status": "not_implemented_locally",
    "local_managed_api_support_status": "not_implemented_locally",
    "local_customer_engagement_adapter_status": "not_implemented_locally",
}


@dataclass(frozen=True)
class AlphaEvolveUiApiAttributionBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveUiApiAttributionBoundaryValidation:
    ok: bool
    boundary_status: str | None
    ui_collaborator_count: int
    api_cloud_collaborator_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveUiApiAttributionBoundaryIssue]


def alphaevolve_ui_api_attribution_boundary_record() -> dict[str, Any]:
    """Return the 2026 impact-article UI/API attribution boundary."""

    return {
        "schema": ALPHAEVOLVE_UI_API_ATTRIBUTION_BOUNDARY_SCHEMA,
        "source_id": "google-deepmind-alphaevolve-impact-2026-ui-api-attribution",
        "source_family": "official_google_deepmind_alphaevolve_impact_article",
        "source_relation": (
            "acknowledgement-role attribution, not local UI, API, managed "
            "service, or customer-engagement evidence"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "article": {
            "title": (
                "AlphaEvolve: How our Gemini-powered coding agent is scaling "
                "impact across fields"
            ),
            "url": "https://deepmind.google/blog/alphaevolve-impact/",
            "date": "2026-05-07",
            "author_or_team": "AlphaEvolve team",
            "section": "Science",
            "retrieved_on": "2026-06-17",
            "html_bytes": 156554,
            "html_sha256": (
                "2b56730407c01a316325222beda6c9c45727362505005c81a3"
                "bbc40bc5c4c97d"
            ),
        },
        "role_categories": {
            "ui_collaborators": (
                "people named by the article as collaborators on developing "
                "the AlphaEvolve UI"
            ),
            "api_cloud_collaborators": (
                "people named by the article as collaborators on developing "
                "the AlphaEvolve API and engaging with Google Cloud customers"
            ),
            "local_libreevolve_authorship": (
                "separate project authorship; source attribution does not imply "
                "LibreEvolve owns or implements those UI/API products"
            ),
        },
        "ui_collaborators": list(EXPECTED_UI_COLLABORATORS),
        "api_cloud_collaborators": list(EXPECTED_API_CLOUD_COLLABORATORS),
        "artifact_policy": {
            "ui_artifacts": "requires_screenshot_or_source_snapshot_inventory",
            "api_artifacts": "requires_endpoint_schema_and_access_model_inventory",
            "customer_engagement_artifacts": "requires_source_or_redacted_handoff_inventory",
            "role_links": "requires_role_to_artifact_link_table",
            "privacy": "requires_contact_and_private_artifact_redaction_policy",
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the official DeepMind impact article's UI "
            "and API/Google Cloud collaborator rosters as attribution evidence "
            "only. It does not claim LibreEvolve has an AlphaEvolve UI, managed "
            "AlphaEvolve API, Google Cloud customer-engagement adapter, UI "
            "artifact inventory, API endpoint/schema inventory, role-to-artifact "
            "link table, privacy/contact redaction policy, or independent "
            "artifact verification."
        ),
    }


def validate_alphaevolve_ui_api_attribution_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveUiApiAttributionBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_ui_api_attribution_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return AlphaEvolveUiApiAttributionBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveUiApiAttributionBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_UI_API_ATTRIBUTION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported UI/API attribution boundary schema"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "UI/API attribution boundary must not claim product artifacts"))
    _validate_article(data.get("article"), issues)
    _validate_role_categories(data.get("role_categories"), issues)
    ui_count = _validate_roster(
        data.get("ui_collaborators"), EXPECTED_UI_COLLABORATORS, "ui_collaborators", issues
    )
    api_count = _validate_roster(
        data.get("api_cloud_collaborators"),
        EXPECTED_API_CLOUD_COLLABORATORS,
        "api_cloud_collaborators",
        issues,
    )
    _validate_artifact_policy(data.get("artifact_policy"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "attribution evidence only" not in boundary_text
        or "managed AlphaEvolve API" not in boundary_text
        or "role-to-artifact link table" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must prevent UI/API product overclaims"))
    return AlphaEvolveUiApiAttributionBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        ui_collaborator_count=ui_count,
        api_cloud_collaborator_count=api_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_ui_api_attribution_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_ui_api_attribution_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve UI/API attribution boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| ui_collaborator_count | {validation.ui_collaborator_count} |",
        f"| api_cloud_collaborator_count | {validation.api_cloud_collaborator_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveUiApiAttributionBoundaryIssue]]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")]
    else:
        try:
            data = json.loads(Path(boundary).read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")]
    if isinstance(data, dict):
        return data, []
    return None, [_issue("invalid_shape", "UI/API attribution boundary must be a JSON object")]


def _validate_article(
    value: object,
    issues: list[AlphaEvolveUiApiAttributionBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_article", "article must be an object"))
        return
    expected = {
        "url": "https://deepmind.google/blog/alphaevolve-impact/",
        "date": "2026-05-07",
        "author_or_team": "AlphaEvolve team",
        "section": "Science",
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_article_{key}", f"article.{key} drifted"))
    if not isinstance(value.get("title"), str) or "scaling impact" not in value["title"]:
        issues.append(_issue("invalid_article_title", "article title must identify the impact article"))
    html_bytes = value.get("html_bytes")
    if isinstance(html_bytes, bool) or not isinstance(html_bytes, int) or html_bytes <= 0:
        issues.append(_issue("invalid_article_bytes", "article html_bytes must be a positive integer"))
    sha = value.get("html_sha256")
    if not isinstance(sha, str) or len(sha) != 64:
        issues.append(_issue("invalid_article_sha256", "article html_sha256 must be 64 hex characters"))


def _validate_role_categories(
    value: object,
    issues: list[AlphaEvolveUiApiAttributionBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_role_categories", "role_categories must be an object"))
        return
    checks = {
        "ui_collaborators": "AlphaEvolve UI",
        "api_cloud_collaborators": "AlphaEvolve API",
        "local_libreevolve_authorship": "separate project authorship",
    }
    for key, snippet in checks.items():
        text = value.get(key)
        if not isinstance(text, str) or snippet not in text:
            issues.append(_issue(f"invalid_role_category_{key}", f"role_categories.{key} must mention {snippet}"))


def _validate_roster(
    value: object,
    expected: tuple[str, ...],
    field_name: str,
    issues: list[AlphaEvolveUiApiAttributionBoundaryIssue],
) -> int:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(_issue(f"invalid_{field_name}", f"{field_name} must be a string list"))
        return 0
    if tuple(value) != expected:
        issues.append(_issue(f"invalid_{field_name}_roster", f"{field_name} roster drifted from source"))
    return len(value)


def _validate_artifact_policy(
    value: object,
    issues: list[AlphaEvolveUiApiAttributionBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_artifact_policy", "artifact_policy must be an object"))
        return
    expected = {
        "ui_artifacts": "requires_screenshot_or_source_snapshot_inventory",
        "api_artifacts": "requires_endpoint_schema_and_access_model_inventory",
        "customer_engagement_artifacts": "requires_source_or_redacted_handoff_inventory",
        "role_links": "requires_role_to_artifact_link_table",
        "privacy": "requires_contact_and_private_artifact_redaction_policy",
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_artifact_policy_{key}", f"artifact_policy.{key} must be {expected_value}"))


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveUiApiAttributionBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_required_evidence_field", f"missing required evidence fields: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_required_evidence_field", f"unknown required evidence fields: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[AlphaEvolveUiApiAttributionBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_missing_evidence_key", f"missing_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_missing_evidence_key", f"missing_evidence has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _issue(code: str, message: str) -> AlphaEvolveUiApiAttributionBoundaryIssue:
    return AlphaEvolveUiApiAttributionBoundaryIssue(code, message)
