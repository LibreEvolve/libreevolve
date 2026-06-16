from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_NON_GOAL_CI_PROMOTION_GATE_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_non_goal_ci_promotion_gate_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "ci_non_goal_promotion_gate_recorded_without_intentional_workflow"
)
EXPECTED_WORKFLOW_PATH = ".github/workflows/tests.yml"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "workflow_path_filters_include_roadmap_docs_papers",
    "paper_docs_job_runs_manifest",
    "paper_docs_job_runs_boundary_tests",
    "non_goal_boundary_tests_exist",
    "non_goal_sidecars_exist",
    "intentional_promotion_workflow",
    "claim_surface_remediation",
    "runtime_plugin_scope_join",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "intentional_promotion_workflow": "not_recorded_locally",
    "claim_surface_remediation": "not_recorded_locally",
    "runtime_plugin_scope_join": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
EXPECTED_WORKFLOW_PHRASES = {
    "roadmap_path_filter": '- "ROADMAP.md"',
    "docs_path_filter": '- "docs/**"',
    "papers_path_filter": '- "papers/**"',
    "tests_path_filter": '- "tests/**"',
    "paper_docs_job": "paper_docs:",
    "paper_manifest_command": "python -m libreevolve.tools.paper_manifest --root .",
    "boundary_test_glob": 'Path("tests").glob("test_*boundary.py")',
}
EXPECTED_NON_GOAL_TESTS = (
    "tests/test_roadmap_non_goal_contradiction_boundary.py",
    "tests/test_roadmap_non_goal_drift_boundary.py",
    "tests/test_roadmap_non_goal_markdown_scan_boundary.py",
    "tests/test_roadmap_non_goal_plugin_docstring_boundary.py",
    "tests/test_roadmap_non_goal_runtime_metadata_boundary.py",
)
EXPECTED_NON_GOAL_SIDECARS = (
    "papers/roadmap_non_goal_contradiction_boundary.json",
    "papers/roadmap_non_goal_drift_boundary.json",
    "papers/roadmap_non_goal_markdown_scan_boundary.json",
    "papers/roadmap_non_goal_plugin_docstring_boundary.json",
    "papers/roadmap_non_goal_runtime_metadata_boundary.json",
)


@dataclass(frozen=True)
class RoadmapNonGoalCiPromotionGateBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapNonGoalCiPromotionGateBoundaryValidation:
    ok: bool
    boundary_status: str | None
    workflow_phrase_count: int
    non_goal_test_count: int
    sidecar_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapNonGoalCiPromotionGateBoundaryIssue]


def roadmap_non_goal_ci_promotion_gate_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded CI gate for ROADMAP non-goal promotion drift."""

    root_path = Path(root)
    workflow_path = root_path / EXPECTED_WORKFLOW_PATH
    workflow_text = _read_text(workflow_path)
    workflow_phrases = {
        name: {
            "phrase": phrase,
            "present": phrase in workflow_text,
        }
        for name, phrase in EXPECTED_WORKFLOW_PHRASES.items()
    }
    non_goal_tests = [
        {
            "path": path,
            "exists": (root_path / path).is_file(),
        }
        for path in EXPECTED_NON_GOAL_TESTS
    ]
    non_goal_sidecars = [
        {
            "path": path,
            "exists": (root_path / path).is_file(),
        }
        for path in EXPECTED_NON_GOAL_SIDECARS
    ]
    return {
        "schema": ROADMAP_NON_GOAL_CI_PROMOTION_GATE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "workflow_path": EXPECTED_WORKFLOW_PATH,
        "workflow_exists": workflow_path.is_file(),
        "workflow_phrase_count": len(workflow_phrases),
        "workflow_phrases": workflow_phrases,
        "non_goal_test_count": len(non_goal_tests),
        "non_goal_tests": non_goal_tests,
        "sidecar_ref_count": len(non_goal_sidecars),
        "non_goal_sidecars": non_goal_sidecars,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that the committed GitHub Actions paper_docs "
            "job is path-triggered by ROADMAP, docs, papers, tests, and source "
            "changes, runs the paper manifest, and runs the boundary verifier "
            "test set that includes ROADMAP non-goal contradiction, drift, "
            "Markdown, plugin docstring, and runtime metadata checks. It does "
            "not claim an intentional promotion workflow, claim-surface "
            "remediation, joined runtime/plugin/docs/paper scope proof, or "
            "owner review signoff."
        ),
    }


def validate_roadmap_non_goal_ci_promotion_gate_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapNonGoalCiPromotionGateBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_non_goal_ci_promotion_gate_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapNonGoalCiPromotionGateBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[RoadmapNonGoalCiPromotionGateBoundaryIssue] = []
    if data.get("schema") != ROADMAP_NON_GOAL_CI_PROMOTION_GATE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported CI promotion gate boundary schema"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "CI promotion gate boundary must not claim full non-goal lifecycle readiness"))
    if data.get("workflow_path") != EXPECTED_WORKFLOW_PATH or data.get("workflow_exists") is not True:
        issues.append(_issue("invalid_workflow_path", "boundary must point to the committed tests workflow"))

    workflow_count = _validate_workflow_phrases(data.get("workflow_phrases"), issues)
    test_count = _validate_path_records(
        data.get("non_goal_tests"),
        EXPECTED_NON_GOAL_TESTS,
        "non_goal_tests",
        issues,
    )
    sidecar_count = _validate_path_records(
        data.get("non_goal_sidecars"),
        EXPECTED_NON_GOAL_SIDECARS,
        "non_goal_sidecars",
        issues,
    )
    _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "paper_docs job is path-triggered" not in boundary_text
        or "runs the paper manifest" not in boundary_text
        or "ROADMAP non-goal contradiction, drift, Markdown, plugin docstring, and runtime metadata checks" not in boundary_text
        or "does not claim an intentional promotion workflow" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate CI gate evidence from full non-goal lifecycle readiness"))
    return RoadmapNonGoalCiPromotionGateBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        workflow_phrase_count=workflow_count,
        non_goal_test_count=test_count,
        sidecar_ref_count=sidecar_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_non_goal_ci_promotion_gate_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_non_goal_ci_promotion_gate_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP non-goal CI promotion gate boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| workflow_phrase_count | {validation.workflow_phrase_count} |",
        f"| non_goal_test_count | {validation.non_goal_test_count} |",
        f"| sidecar_ref_count | {validation.sidecar_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapNonGoalCiPromotionGateBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "CI promotion gate boundary must be a JSON object")]


def _validate_workflow_phrases(
    value: object,
    issues: list[RoadmapNonGoalCiPromotionGateBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_workflow_phrases", "workflow_phrases must be an object"))
        return 0
    expected_keys = set(EXPECTED_WORKFLOW_PHRASES)
    actual_keys = set(value)
    if expected_keys - actual_keys:
        issues.append(_issue("missing_workflow_phrase", "workflow phrase records are incomplete"))
    if actual_keys - expected_keys:
        issues.append(_issue("extra_workflow_phrase", "workflow phrase records include unknown keys"))
    for name, phrase in EXPECTED_WORKFLOW_PHRASES.items():
        record = value.get(name)
        if (
            not isinstance(record, dict)
            or record.get("phrase") != phrase
            or record.get("present") is not True
        ):
            issues.append(_issue(f"invalid_workflow_phrase_{name}", f"workflow phrase {name} must be present"))
    return len(actual_keys)


def _validate_path_records(
    value: object,
    expected_paths: tuple[str, ...],
    field: str,
    issues: list[RoadmapNonGoalCiPromotionGateBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue(f"invalid_{field}", f"{field} must be a list"))
        return 0
    records = {item.get("path"): item for item in value if isinstance(item, dict)}
    expected = set(expected_paths)
    actual = set(path for path in records if isinstance(path, str))
    if expected - actual:
        issues.append(_issue(f"missing_{field}", f"{field} lacks expected paths"))
    if actual - expected:
        issues.append(_issue(f"extra_{field}", f"{field} includes unknown paths"))
    for path in expected_paths:
        if records.get(path, {}).get("exists") is not True:
            issues.append(_issue(f"missing_{field}_path", f"{path} must exist"))
    if len(records) != len(value):
        issues.append(_issue(f"invalid_{field}_record", f"{field} records must be objects"))
    return len(actual)


def _validate_required_fields(
    value: object,
    issues: list[RoadmapNonGoalCiPromotionGateBoundaryIssue],
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
    issues: list[RoadmapNonGoalCiPromotionGateBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    if expected_keys - actual_keys:
        issues.append(_issue("missing_missing_evidence_key", "missing_evidence lacks expected keys"))
    if actual_keys - expected_keys:
        issues.append(_issue("extra_missing_evidence_key", "missing_evidence includes unknown keys"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _issue(code: str, message: str) -> RoadmapNonGoalCiPromotionGateBoundaryIssue:
    return RoadmapNonGoalCiPromotionGateBoundaryIssue(code, message)
