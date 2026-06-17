from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.alphaevolve_2026_impact_boundary import (
    EXPECTED_ARTICLE_URL,
    EXPECTED_CLAIM_IDS,
    EXPECTED_HTML_SHA256,
    alphaevolve_2026_impact_boundary_record,
)


ALPHAEVOLVE_IMPACT_CLAIM_POLICY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_impact_claim_policy_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "normalized_source_claim_rows_without_release_note_promotion_eligibility"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "canonical_claim_id",
    "source_url",
    "source_retrieval_hash",
    "raw_value",
    "value_type",
    "unit",
    "denominator_or_population",
    "baseline_identity",
    "comparison_direction",
    "approximation_wording",
    "result_class",
    "source_snapshot_status",
    "local_fixture_status",
    "reproduction_artifact_links",
    "customer_confirmation_status",
    "independent_verification_status",
    "unsupported_local_evidence_flag",
    "release_note_eligibility",
    "readme_roadmap_paper_index_constraint",
    "downgrade_wording",
)
EXPECTED_MISSING_EVIDENCE = {
    "per_claim_linked_source_snapshots": "not_recorded_locally",
    "local_fixture_status_by_claim": "not_implemented_locally",
    "reproduction_artifact_links": "not_recorded_locally",
    "customer_confirmation_status": "not_recorded_locally",
    "independent_verification_status": "not_recorded_locally",
    "release_note_promotion_gate": "not_implemented_locally",
}


@dataclass(frozen=True)
class AlphaEvolveImpactClaimPolicyBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveImpactClaimPolicyBoundaryValidation:
    ok: bool
    boundary_status: str | None
    normalized_claim_count: int
    release_note_eligible_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveImpactClaimPolicyBoundaryIssue]


def alphaevolve_impact_claim_policy_boundary_record() -> dict[str, Any]:
    """Return the 2026 impact-claim normalization and promotion boundary."""

    impact = alphaevolve_2026_impact_boundary_record()
    claims = impact["claim_registry"]
    return {
        "schema": ALPHAEVOLVE_IMPACT_CLAIM_POLICY_BOUNDARY_SCHEMA,
        "source_id": "google-deepmind-alphaevolve-impact-2026-claim-policy",
        "source_family": "official_google_deepmind_alphaevolve_impact_article",
        "source_relation": (
            "normalization and release-note gating for source-reported 2026 "
            "impact claims, not local reproduction evidence"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "policy": {
            "promotion_rule": (
                "A source-reported impact value may not be described as "
                "implemented, reproduced, benchmarked, or LibreEvolve-supported "
                "unless the normalized row has source snapshots, local fixture "
                "evidence, reproduction artifacts, independent verification, and "
                "customer confirmation where relevant."
            ),
            "default_downgrade_wording": (
                "source-reported official AlphaEvolve impact claim; not "
                "reproduced or supported by LibreEvolve"
            ),
            "release_note_gate_status": "not_implemented_locally",
        },
        "normalized_claim_rows": [
            _normalized_claim_row(claim)
            for claim in claims
        ],
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary normalizes the 22 official 2026 AlphaEvolve impact "
            "claim values for comparison and release-note review only. It does "
            "not claim linked source snapshots, local fixtures, reproduction "
            "artifacts, customer confirmation, independent verification, or "
            "release-note eligibility for any impact claim."
        ),
    }


def validate_alphaevolve_impact_claim_policy_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveImpactClaimPolicyBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_impact_claim_policy_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return AlphaEvolveImpactClaimPolicyBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveImpactClaimPolicyBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_IMPACT_CLAIM_POLICY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported impact claim policy boundary schema"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "impact claim policy must not claim release-note readiness"))
    _validate_policy(data.get("policy"), issues)
    normalized_count, eligible_count = _validate_normalized_claim_rows(
        data.get("normalized_claim_rows"), issues
    )
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "normalizes the 22 official 2026 AlphaEvolve impact claim values" not in boundary_text
        or "does not claim linked source snapshots" not in boundary_text
        or "release-note eligibility" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must prevent impact claim promotion"))
    return AlphaEvolveImpactClaimPolicyBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        normalized_claim_count=normalized_count,
        release_note_eligible_count=eligible_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_impact_claim_policy_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_impact_claim_policy_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve impact claim policy boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| normalized_claim_count | {validation.normalized_claim_count} |",
        f"| release_note_eligible_count | {validation.release_note_eligible_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _normalized_claim_row(claim: dict[str, Any]) -> dict[str, Any]:
    raw_value = claim["value"]
    result_class = _result_class(claim)
    return {
        "claim_id": claim["claim_id"],
        "source_url": EXPECTED_ARTICLE_URL,
        "source_retrieval_hash": EXPECTED_HTML_SHA256,
        "raw_value": raw_value,
        "value_type": _value_type(raw_value, claim["unit"]),
        "unit": claim["unit"],
        "denominator_or_population": _denominator_or_population(claim),
        "baseline_identity": claim["baseline"],
        "comparison_direction": _comparison_direction(claim["unit"]),
        "approximation_wording": _approximation_wording(raw_value, claim["unit"]),
        "result_class": result_class,
        "source_snapshot_status": "impact_article_snapshot_recorded",
        "local_fixture_status": "not_implemented_locally",
        "reproduction_artifact_links": [],
        "customer_confirmation_status": (
            "not_recorded_locally" if result_class == "customer_reported" else "not_applicable"
        ),
        "independent_verification_status": "not_recorded_locally",
        "unsupported_local_evidence_flag": True,
        "release_note_eligible": False,
        "readme_roadmap_paper_index_constraint": "source_scoped_only",
        "downgrade_wording": (
            "source-reported official AlphaEvolve impact claim; not reproduced "
            "or supported by LibreEvolve"
        ),
    }


def _value_type(raw_value: object, unit: str) -> str:
    if isinstance(raw_value, (int, float)) and not isinstance(raw_value, bool):
        if "x_" in unit or unit.startswith("roughly_x"):
            return "speedup_numeric"
        if "percent" in unit:
            return "percentage_numeric"
        return "numeric"
    text = str(raw_value)
    if text.startswith("14_to_over_"):
        return "range_text"
    if "two_days" in text:
        return "time_comparison_text"
    if "multi_fold" in text:
        return "speedup_qualitative"
    return "qualitative_text"


def _denominator_or_population(claim: dict[str, Any]) -> str:
    unit = str(claim["unit"])
    if "percent" in unit:
        return str(claim["baseline"])
    if "x_" in unit or unit.startswith("roughly_x"):
        return str(claim["baseline"])
    return "not_specified_in_boundary"


def _comparison_direction(unit: str) -> str:
    if "reduction" in unit or "lower_error" in unit:
        return "lower_is_better"
    if "gain" in unit or "improvement" in unit or "feasible" in unit or "speedup" in unit:
        return "higher_is_better"
    if "time_to_result" in unit:
        return "shorter_is_better"
    return "descriptive"


def _approximation_wording(raw_value: object, unit: str) -> str:
    if isinstance(raw_value, str) and ("over" in raw_value or "roughly" in unit or "multi" in raw_value):
        return "approximate_or_range"
    if "nearly" in unit or "roughly" in unit:
        return "approximate_or_range"
    return "exact_as_source_boundary"


def _result_class(claim: dict[str, Any]) -> str:
    evidence = str(claim["evidence_status"])
    if evidence == "customer_source_required":
        return "customer_reported"
    if evidence in {"deployment_evidence_required", "linked_source_required", "gallery_snapshot_required"}:
        return "source_reported_external"
    return "source_reported_metric"


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveImpactClaimPolicyBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "impact claim policy boundary must be a JSON object")]


def _validate_policy(
    value: object,
    issues: list[AlphaEvolveImpactClaimPolicyBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_policy", "policy must be an object"))
        return
    promotion_rule = value.get("promotion_rule")
    downgrade = value.get("default_downgrade_wording")
    if (
        not isinstance(promotion_rule, str)
        or "implemented, reproduced, benchmarked, or LibreEvolve-supported" not in promotion_rule
        or "independent verification" not in promotion_rule
    ):
        issues.append(_issue("invalid_promotion_rule", "promotion rule must require full evidence before promotion"))
    if not isinstance(downgrade, str) or "not reproduced or supported by LibreEvolve" not in downgrade:
        issues.append(_issue("invalid_downgrade_wording", "downgrade wording must keep claims source-scoped"))
    if value.get("release_note_gate_status") != "not_implemented_locally":
        issues.append(_issue("invalid_release_note_gate_status", "release note gate must remain not implemented locally"))


def _validate_normalized_claim_rows(
    value: object,
    issues: list[AlphaEvolveImpactClaimPolicyBoundaryIssue],
) -> tuple[int, int]:
    if not isinstance(value, list):
        issues.append(_issue("invalid_normalized_claim_rows", "normalized_claim_rows must be a list"))
        return 0, 0
    claim_ids = []
    eligible_count = 0
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_normalized_claim_row", "normalized claim rows must be objects"))
            continue
        claim_id = item.get("claim_id")
        if isinstance(claim_id, str):
            claim_ids.append(claim_id)
        required = {
            "source_url",
            "source_retrieval_hash",
            "value_type",
            "unit",
            "baseline_identity",
            "comparison_direction",
            "result_class",
            "source_snapshot_status",
            "local_fixture_status",
            "independent_verification_status",
            "readme_roadmap_paper_index_constraint",
            "downgrade_wording",
        }
        for key in required:
            if not isinstance(item.get(key), str) or not item[key]:
                issues.append(_issue("invalid_normalized_claim_field", f"normalized claim row must include {key}"))
                break
        if item.get("source_url") != EXPECTED_ARTICLE_URL:
            issues.append(_issue("invalid_claim_source_url", "normalized claim rows must use the official impact article URL"))
        if item.get("source_retrieval_hash") != EXPECTED_HTML_SHA256:
            issues.append(_issue("invalid_claim_source_hash", "normalized claim rows must preserve the impact article retrieval hash"))
        if item.get("local_fixture_status") != "not_implemented_locally":
            issues.append(_issue("claim_local_fixture_overclaim", "claim rows must not claim local fixtures"))
        if item.get("independent_verification_status") != "not_recorded_locally":
            issues.append(_issue("claim_independent_verification_overclaim", "claim rows must not claim independent verification"))
        if item.get("unsupported_local_evidence_flag") is not True:
            issues.append(_issue("missing_unsupported_local_evidence_flag", "claim rows must flag unsupported local evidence"))
        if item.get("release_note_eligible") is True:
            eligible_count += 1
            issues.append(_issue("release_note_eligibility_overclaim", "impact claims must not be release-note eligible"))
        links = item.get("reproduction_artifact_links")
        if not isinstance(links, list) or links:
            issues.append(_issue("reproduction_artifact_link_overclaim", "reproduction artifact links must be an empty list"))
    if tuple(claim_ids) != EXPECTED_CLAIM_IDS:
        issues.append(_issue("claim_id_mismatch", "normalized claim rows must preserve the official impact claim ids"))
    return len(claim_ids), eligible_count


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveImpactClaimPolicyBoundaryIssue],
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
    issues: list[AlphaEvolveImpactClaimPolicyBoundaryIssue],
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


def _issue(code: str, message: str) -> AlphaEvolveImpactClaimPolicyBoundaryIssue:
    return AlphaEvolveImpactClaimPolicyBoundaryIssue(code, message)
