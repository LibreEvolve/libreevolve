from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.alphaevolve_source_refresh_gate_boundary import (
    EXPECTED_ARCHIVED_OUTCOME_PATH,
    EXPECTED_WORKFLOW_PATH,
    source_expectations,
)


ALPHAEVOLVE_SOURCE_REFRESH_PROMOTION_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_source_refresh_promotion_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_VERSION_ID = "2506.13131v1"
EXPECTED_BOUNDARY_STATUS = (
    "central_refresh_gate_coverage_recorded_without_individual_sidecar_promotion"
)
EXPECTED_GATE_SIDEcar = "papers/alphaevolve_source_refresh_gate_boundary.json"
EXPECTED_PROMOTION_POLICY = "central_gate_covers_sources_sidecars_remain_snapshots"
EXPECTED_SOURCE_SIDECARS = {
    "versioned_abstract": [
        "papers/arxiv_abstract_snapshot.json",
    ],
    "current_abstract": [
        "papers/alphaevolve_current_version_boundary.json",
    ],
    "floating_pdf": [
        "papers/alphaevolve_current_version_boundary.json",
        "papers/alphaevolve_cached_pdf_header_consistency_boundary.json",
    ],
    "datacite_api": [
        "papers/alphaevolve_datacite_doi_boundary.json",
        "papers/alphaevolve_datacite_full_response_boundary.json",
    ],
    "eprint_archive": [
        "papers/alphaevolve_tex_source_boundary.json",
        "papers/alphaevolve_tex_archive_retention_boundary.json",
    ],
    "license_page": [
        "papers/alphaevolve_license_page_boundary.json",
        "papers/alphaevolve_license_page_html_retention_boundary.json",
    ],
}
EXPECTED_MISSING_EVIDENCE = {
    "scheduled_ci_refresh_run_history": "not_recorded_locally",
}


@dataclass(frozen=True)
class AlphaEvolveSourceRefreshPromotionBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveSourceRefreshPromotionBoundaryValidation:
    ok: bool
    boundary_status: str | None
    source_count: int
    linked_sidecar_count: int
    linked_sidecars_checked: bool
    missing_evidence_count: int
    issues: list[AlphaEvolveSourceRefreshPromotionBoundaryIssue]


def alphaevolve_source_refresh_promotion_boundary_record() -> dict[str, Any]:
    """Return the per-source refresh promotion policy boundary."""

    return {
        "schema": ALPHAEVOLVE_SOURCE_REFRESH_PROMOTION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_version_id": EXPECTED_SOURCE_VERSION_ID,
        "source_claim": (
            "Per-source AlphaEvolve source sidecars should either be promoted "
            "to refresh-ready evidence or explicitly kept as bounded snapshots "
            "covered by the central refresh gate."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "promotion_policy": EXPECTED_PROMOTION_POLICY,
        "central_refresh_gate": {
            "path": EXPECTED_GATE_SIDEcar,
            "workflow_path": EXPECTED_WORKFLOW_PATH,
            "archived_manual_run_path": EXPECTED_ARCHIVED_OUTCOME_PATH,
        },
        "source_sidecar_map": [
            {
                "source_id": source_id,
                "promotion_status": "covered_by_central_refresh_gate_not_individually_promoted",
                "sidecars": list(sidecars),
            }
            for source_id, sidecars in EXPECTED_SOURCE_SIDECARS.items()
        ],
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the decision not to relabel older "
            "per-source snapshot sidecars as standalone refresh-ready evidence. "
            "Each source id checked by the central AlphaEvolve refresh gate is "
            "mapped to the paper sidecars it covers, while scheduled CI "
            "refresh-run history remains outside the committed evidence."
        ),
    }


def validate_alphaevolve_source_refresh_promotion_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveSourceRefreshPromotionBoundaryValidation:
    data, read_issues, base_dir = _load_boundary(
        alphaevolve_source_refresh_promotion_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveSourceRefreshPromotionBoundaryValidation(
            False, None, 0, 0, False, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveSourceRefreshPromotionBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_SOURCE_REFRESH_PROMOTION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported source refresh promotion boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_version_id") != EXPECTED_SOURCE_VERSION_ID:
        issues.append(_issue("invalid_source_version_id", "source_version_id must be 2506.13131v1"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "bounded snapshots" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must separate refresh-ready evidence from bounded snapshots"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "promotion boundary must not claim scheduled refresh history"))
    if data.get("promotion_policy") != EXPECTED_PROMOTION_POLICY:
        issues.append(_issue("invalid_promotion_policy", f"promotion_policy must be {EXPECTED_PROMOTION_POLICY}"))
    _validate_central_refresh_gate(data.get("central_refresh_gate"), issues)
    source_count, sidecar_count = _validate_source_sidecar_map(data.get("source_sidecar_map"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "decision not to relabel older per-source snapshot sidecars" not in boundary_text
        or "mapped to the paper sidecars it covers" not in boundary_text
        or "scheduled CI refresh-run history remains outside" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must describe central-gate coverage without individual sidecar promotion"))
    checked = False
    if base_dir is not None:
        checked = _validate_linked_sidecar_files(base_dir, issues)
    return AlphaEvolveSourceRefreshPromotionBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        source_count=source_count,
        linked_sidecar_count=sidecar_count,
        linked_sidecars_checked=checked,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_source_refresh_promotion_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_source_refresh_promotion_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve source refresh-promotion boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| source_count | {validation.source_count} |",
        f"| linked_sidecar_count | {validation.linked_sidecar_count} |",
        f"| linked_sidecars_checked | {validation.linked_sidecars_checked} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _validate_central_refresh_gate(
    value: object,
    issues: list[AlphaEvolveSourceRefreshPromotionBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_central_refresh_gate", "central_refresh_gate must be an object"))
        return
    expected = {
        "path": EXPECTED_GATE_SIDEcar,
        "workflow_path": EXPECTED_WORKFLOW_PATH,
        "archived_manual_run_path": EXPECTED_ARCHIVED_OUTCOME_PATH,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_central_refresh_gate_{field}", f"central_refresh_gate.{field} must be {expected_value}"))


def _validate_source_sidecar_map(
    value: object,
    issues: list[AlphaEvolveSourceRefreshPromotionBoundaryIssue],
) -> tuple[int, int]:
    if not isinstance(value, list):
        issues.append(_issue("invalid_source_sidecar_map", "source_sidecar_map must be a list"))
        return 0, 0
    expected_ids = [expectation["source_id"] for expectation in source_expectations()]
    expected_by_id = dict(EXPECTED_SOURCE_SIDECARS)
    actual_by_id: dict[str, list[str]] = {}
    sidecar_count = 0
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_source_sidecar_map_entry", "source_sidecar_map entries must be objects"))
            continue
        source_id = item.get("source_id")
        sidecars = item.get("sidecars")
        if item.get("promotion_status") != "covered_by_central_refresh_gate_not_individually_promoted":
            issues.append(_issue("invalid_promotion_status", "each source must remain covered but not individually promoted"))
        if not isinstance(source_id, str):
            issues.append(_issue("invalid_source_id", "source_id must be a string"))
            continue
        if not isinstance(sidecars, list) or not all(isinstance(path, str) for path in sidecars):
            issues.append(_issue(f"invalid_{source_id}_sidecars", f"{source_id} sidecars must be a list of paths"))
            continue
        actual_by_id[source_id] = sidecars
        sidecar_count += len(sidecars)
    if list(actual_by_id) != expected_ids:
        issues.append(_issue("invalid_source_order", "source_sidecar_map must follow source refresh gate source order"))
    for source_id, expected_sidecars in expected_by_id.items():
        if actual_by_id.get(source_id) != expected_sidecars:
            issues.append(_issue(f"invalid_{source_id}_sidecars", f"{source_id} sidecars must match the expected coverage map"))
    extra = sorted(set(actual_by_id) - set(expected_by_id))
    if extra:
        issues.append(_issue("extra_source_id", f"unexpected source ids: {', '.join(extra)}"))
    return len(actual_by_id), sidecar_count


def _validate_missing_evidence(
    value: object,
    issues: list[AlphaEvolveSourceRefreshPromotionBoundaryIssue],
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


def _validate_linked_sidecar_files(
    base_dir: Path,
    issues: list[AlphaEvolveSourceRefreshPromotionBoundaryIssue],
) -> bool:
    required_paths = {
        EXPECTED_GATE_SIDEcar,
        EXPECTED_ARCHIVED_OUTCOME_PATH,
        EXPECTED_WORKFLOW_PATH,
    }
    for sidecars in EXPECTED_SOURCE_SIDECARS.values():
        required_paths.update(sidecars)
    for relative_path in sorted(required_paths):
        if not (base_dir / relative_path).exists():
            issues.append(_issue("missing_linked_sidecar_file", f"{relative_path} must exist"))
    return True


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveSourceRefreshPromotionBoundaryIssue], Path | None]:
    base_dir: Path | None = None
    if isinstance(boundary, dict):
        return dict(boundary), [], None
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")], None
    else:
        try:
            path = Path(boundary)
            data = json.loads(path.read_text(encoding="utf-8"))
            base_dir = path.parent.parent
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")], None
    if isinstance(data, dict):
        return data, [], base_dir
    return None, [_issue("invalid_shape", "source refresh promotion boundary must be a JSON object")], base_dir


def _issue(code: str, message: str) -> AlphaEvolveSourceRefreshPromotionBoundaryIssue:
    return AlphaEvolveSourceRefreshPromotionBoundaryIssue(code, message)
