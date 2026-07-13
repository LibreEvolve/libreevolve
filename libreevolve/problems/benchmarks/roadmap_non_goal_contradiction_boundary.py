from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_NON_GOAL_CONTRADICTION_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_non_goal_contradiction_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = "bounded_non_goal_inventory_without_full_contradiction_gate"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "stable_non_goal_ids",
    "roadmap_source_lines",
    "constrained_document_surfaces",
    "forbidden_claim_phrase_scan",
    "contradiction_count",
    "full_markdown_corpus_scan",
    "runtime_metadata_scan",
    "plugin_docstring_scan",
    "ci_non_goal_promotion_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "runtime_metadata_scan": "not_recorded_locally",
    "plugin_docstring_scan": "not_recorded_locally",
    "ci_non_goal_promotion_gate": "not_recorded_locally",
    "intentional_promotion_workflow": "not_recorded_locally",
}
MARKDOWN_CORPUS_SCAN_SIDECAR = "papers/roadmap_non_goal_markdown_scan_boundary.json"


NON_GOAL_SPECS = (
    {
        "non_goal_id": "normal_local_use_no_service_database_required",
        "roadmap_text": "Requiring a service database for normal local use.",
        "roadmap_anchor": "ROADMAP.md#non-goals-for-now",
        "constrained_surfaces": (
            {
                "path": "ROADMAP.md",
                "required_safe_phrase": "Requiring a service database for normal local use.",
                "forbidden_claim_phrases": (
                    "requires a service database for normal local use",
                    "normal local use requires a service database",
                ),
            },
            {
                "path": "README.md",
                "required_safe_phrase": "not a distributed service",
                "forbidden_claim_phrases": (
                    "requires a service database",
                    "service database is required",
                ),
            },
        ),
    },
    {
        "non_goal_id": "no_arbitrary_language_codebase_support_before_runners",
        "roadmap_text": (
            "Claiming arbitrary-language/codebase parity before portable "
            "toolchains, language-aware mutation, and representative validators "
            "exist."
        ),
        "roadmap_anchor": "ROADMAP.md#non-goals-for-now",
        "constrained_surfaces": (
            {
                "path": "ROADMAP.md",
                "required_safe_phrase": (
                    "Claiming arbitrary-language/codebase parity before portable "
                    "toolchains"
                ),
                "forbidden_claim_phrases": (
                    "arbitrary-language runners are implemented",
                    "arbitrary-language/build runners are implemented",
                    "arbitrary-language/codebase parity is implemented",
                ),
            },
            {
                "path": "README.md",
                "required_safe_phrase": (
                    "prove portable hermetic toolchain provisioning"
                ),
                "forbidden_claim_phrases": (
                    "arbitrary-language runners are implemented",
                    "build-system runners are implemented",
                    "supports arbitrary-language runners",
                ),
            },
            {
                "path": "docs/run-artifacts.md",
                "required_safe_phrase": (
                    "real-language codebase-scale evidence unsupported"
                ),
                "forbidden_claim_phrases": (
                    "arbitrary-language/build-runner execution is supported",
                    "arbitrary-language/codebase parity can be claimed now",
                ),
            },
        ),
    },
    {
        "non_goal_id": "paper_inspired_plugins_not_faithful_implementations",
        "roadmap_text": "Advertising paper-inspired plugins as faithful implementations.",
        "roadmap_anchor": "ROADMAP.md#non-goals-for-now",
        "constrained_surfaces": (
            {
                "path": "ROADMAP.md",
                "required_safe_phrase": (
                    "Advertising paper-inspired plugins as faithful implementations."
                ),
                "forbidden_claim_phrases": (
                    "paper-inspired plugins are faithful implementations",
                    "built-in paper-inspired plugins faithfully implement",
                ),
            },
            {
                "path": "README.md",
                "required_safe_phrase": "paper-inspired plugins are approximations",
                "forbidden_claim_phrases": (
                    "paper-inspired plugins are faithful implementations",
                    "plugins faithfully implement the papers",
                ),
            },
            {
                "path": "docs/architecture.md",
                "required_safe_phrase": (
                    "Plugin names are paper-inspired approximations unless "
                    "documented otherwise."
                ),
                "forbidden_claim_phrases": (
                    "plugin names are faithful implementations",
                    "paper-inspired plugins faithfully implement",
                ),
            },
            {
                "path": "docs/status.md",
                "required_safe_phrase": (
                    "Built-in paper-inspired plugins are approximations, not faithful"
                ),
                "forbidden_claim_phrases": (
                    "built-in paper-inspired plugins are faithful",
                    "paper-inspired plugins faithfully implement",
                ),
            },
        ),
    },
)


@dataclass(frozen=True)
class RoadmapNonGoalContradictionBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapNonGoalContradictionBoundaryValidation:
    ok: bool
    boundary_status: str | None
    non_goal_count: int
    contradiction_count: int
    missing_evidence_count: int
    issues: list[RoadmapNonGoalContradictionBoundaryIssue]


def roadmap_non_goal_contradiction_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP non-goal contradiction inventory."""

    root_path = Path(root)
    records = [_non_goal_record(root_path, spec) for spec in NON_GOAL_SPECS]
    contradiction_count = sum(
        len(surface["detected_forbidden_claims"])
        for record in records
        for surface in record["constrained_surfaces"]
    )
    constrained_surface_count = sum(
        len(record["constrained_surfaces"]) for record in records
    )
    return {
        "schema": ROADMAP_NON_GOAL_CONTRADICTION_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "non_goal_count": len(records),
        "constrained_surface_count": constrained_surface_count,
        "contradiction_count": contradiction_count,
        "non_goal_records": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "evidence_sidecars": {
            "full_markdown_corpus_scan": MARKDOWN_CORPUS_SCAN_SIDECAR,
        },
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary assigns stable ids to the three ROADMAP non-goals, "
            "checks selected constrained documentation surfaces for required "
            "safe-scope wording, and records exact forbidden support-claim "
            "phrase matches. The full Markdown corpus scan is tracked by "
            f"{MARKDOWN_CORPUS_SCAN_SIDECAR}. This boundary does not claim a "
            "runtime metadata scan, plugin docstring scan, CI promotion gate, "
            "or workflow for intentionally promoting a non-goal into active "
            "implementation scope."
        ),
    }


def validate_roadmap_non_goal_contradiction_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapNonGoalContradictionBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_non_goal_contradiction_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapNonGoalContradictionBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_non_goal_contradiction_boundary_record(root)
    issues: list[RoadmapNonGoalContradictionBoundaryIssue] = []
    if data.get("schema") != ROADMAP_NON_GOAL_CONTRADICTION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP non-goal boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP non-goal contradiction boundary must not claim full guardrail readiness"))
    for key in (
        "non_goal_count",
        "constrained_surface_count",
        "contradiction_count",
        "non_goal_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP non-goal inputs"))
    if data.get("contradiction_count") != 0:
        issues.append(_issue("contradiction_detected", "forbidden non-goal support claim phrases were detected"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "full Markdown corpus scan is tracked" not in boundary_text
        or "does not claim a runtime metadata scan" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded non-goal inventory from full contradiction coverage"))
    evidence_sidecars = data.get("evidence_sidecars")
    if not isinstance(evidence_sidecars, dict) or evidence_sidecars.get("full_markdown_corpus_scan") != MARKDOWN_CORPUS_SCAN_SIDECAR:
        issues.append(_issue("invalid_evidence_sidecars", "full Markdown corpus scan sidecar must be linked"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapNonGoalContradictionBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        non_goal_count=data.get("non_goal_count") if isinstance(data.get("non_goal_count"), int) else 0,
        contradiction_count=data.get("contradiction_count") if isinstance(data.get("contradiction_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_non_goal_contradiction_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_non_goal_contradiction_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP non-goal contradiction boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| non_goal_count | {validation.non_goal_count} |",
        f"| contradiction_count | {validation.contradiction_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _non_goal_record(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    surfaces = [
        _surface_record(root, surface)
        for surface in spec["constrained_surfaces"]
    ]
    return {
        "non_goal_id": spec["non_goal_id"],
        "roadmap_text": spec["roadmap_text"],
        "roadmap_anchor": spec["roadmap_anchor"],
        "constrained_surface_count": len(surfaces),
        "constrained_surfaces": surfaces,
        "contradiction_status": "no_forbidden_claim_phrases_detected",
    }


def _surface_record(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    path = spec["path"]
    text = _read_text(root / path)
    required_safe_phrase = spec["required_safe_phrase"]
    forbidden_claim_phrases = list(spec["forbidden_claim_phrases"])
    detected = [
        phrase
        for phrase in forbidden_claim_phrases
        if _contains_phrase(text, phrase)
    ]
    return {
        "path": path,
        "required_safe_phrase": required_safe_phrase,
        "required_safe_phrase_present": _contains_phrase(text, required_safe_phrase),
        "forbidden_claim_phrases": forbidden_claim_phrases,
        "detected_forbidden_claims": detected,
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _contains_phrase(text: str, phrase: str) -> bool:
    normalized_text = " ".join(text.casefold().split())
    normalized_phrase = " ".join(phrase.casefold().split())
    return normalized_phrase in normalized_text


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapNonGoalContradictionBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP non-goal contradiction boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapNonGoalContradictionBoundaryIssue],
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
    issues: list[RoadmapNonGoalContradictionBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapNonGoalContradictionBoundaryIssue:
    return RoadmapNonGoalContradictionBoundaryIssue(code=code, message=message)
