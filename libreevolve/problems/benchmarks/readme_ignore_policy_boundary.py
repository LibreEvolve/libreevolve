from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_IGNORE_POLICY_BOUNDARY_SCHEMA = "libreevolve.readme_ignore_policy_boundary.v1"
EXPECTED_BOUNDARY_STATUS = (
    "readme_ignore_policy_static_inventory_without_retention_drift_gate"
)
GITIGNORE_PATH = ".gitignore"
README_PATH = "README.md"
PAPERS_README_PATH = "papers/README.md"
WORKFLOW_PATH = ".github/workflows/tests.yml"
AGENTS_TEST_PATH = "tests/test_agents_docs.py"
README_TODO_PATH = "docs/todo/readme.md"

EXPECTED_IGNORE_RULES = (
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "/.pytest_cache/",
    "/.mypy_cache/",
    "/.ruff_cache/",
    "/.hypothesis/",
    "/.tox/",
    "/.nox/",
    "/.coverage",
    "/.coverage.*",
    "/htmlcov/",
    "/.venv/",
    "/venv/",
    "/build/",
    "/dist/",
    "/*.egg-info/",
    "/runs/",
    "/.env",
    "/.claude/",
    "/.worktrees/",
    "/branding-preview.html",
    "/assets/social-preview.html",
    "/docs/superpowers/plans/",
    "/docs/superpowers/specs/2026-03-18-libreevolve-branding.md",
    "/old/superpowers/specs/",
    "/papers/*",
)
EXPECTED_ALLOWLIST_RULES = (
    "!/papers/README.md",
    "!/papers/download_manifest.csv",
    "!/papers/download_manifest.json",
    "!/papers/benchmark_coverage_inventory.json",
    "!/papers/status_claim_inventory.json",
)
EXPECTED_EVIDENCE_ANCHORS = (
    ("readme_runs_gitignored", README_PATH, "Gitignored run artifacts under `runs/`."),
    ("readme_run_artifacts_gitignored", README_PATH, "Runs write to `runs/<run-name>/`, which is gitignored."),
    ("readme_paper_pdfs_gitignored", README_PATH, "The PDFs are\ngitignored"),
    ("readme_layout_papers_scope", README_PATH, "tracked manifests plus ignored PDF cache and retained source artifacts"),
    ("readme_layout_runs_scope", README_PATH, "runs/            gitignored run outputs"),
    ("papers_readme_pdf_policy", PAPERS_README_PATH, "PDFs are intentionally gitignored"),
    ("papers_readme_committed_policy", PAPERS_README_PATH, "The committed repository tracks this README, the CSV/JSON\nmanifests, sidecars, and that retained source artifact."),
    ("workflow_readme_path_filter", WORKFLOW_PATH, '"README.md"'),
    ("workflow_docs_path_filter", WORKFLOW_PATH, '"docs/**"'),
    ("workflow_papers_path_filter", WORKFLOW_PATH, '"papers/**"'),
    ("workflow_pyproject_path_filter", WORKFLOW_PATH, '"pyproject.toml"'),
    ("workflow_tests_path_filter", WORKFLOW_PATH, '"tests/**"'),
    ("agents_workflow_path_filter_test", AGENTS_TEST_PATH, "test_tests_workflow_covers_docs_papers_and_todo_changes"),
    ("readme_todo_owner", README_TODO_PATH, "Add repository ignore-policy evidence-retention drift check."),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "gitignore_ignore_rule_inventory",
    "gitignore_allowlist_rule_inventory",
    "run_artifact_local_only_policy",
    "paper_pdf_local_only_policy",
    "paper_manifest_allowlist_policy",
    "readme_repository_layout_ignore_markers",
    "papers_index_ignore_policy_markers",
    "github_actions_docs_papers_tests_path_filters",
    "active_todo_owner_anchor",
    "full_ignore_rule_rationale_map",
    "tracked_vs_ignored_sidecar_inventory",
    "gitignore_workflow_path_filter",
    "retention_policy_drift_gate",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "full_ignore_rule_rationale_map": "not_recorded_locally",
    "tracked_vs_ignored_sidecar_inventory": "not_recorded_locally",
    "gitignore_workflow_path_filter": "not_recorded_locally",
    "retention_policy_drift_gate": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmeIgnorePolicyBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeIgnorePolicyBoundaryValidation:
    ok: bool
    boundary_status: str | None
    ignore_rule_count: int
    allowlist_rule_count: int
    missing_rule_count: int
    evidence_anchor_count: int
    missing_evidence_anchor_count: int
    missing_evidence_count: int
    issues: list[ReadmeIgnorePolicyBoundaryIssue]


def readme_ignore_policy_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the README/.gitignore retention-policy static evidence map."""

    root_path = Path(root)
    gitignore_text = _read_text(root_path / GITIGNORE_PATH)
    rules = _gitignore_rules(gitignore_text)
    ignore_records = [_rule_record(rule, rules) for rule in EXPECTED_IGNORE_RULES]
    allowlist_records = [
        _rule_record(rule, rules) for rule in EXPECTED_ALLOWLIST_RULES
    ]
    missing_rule_records = [
        record
        for record in (*ignore_records, *allowlist_records)
        if record["rule_status"] != "rule_present"
    ]
    texts = {
        path: _read_text(root_path / path)
        for path in (
            README_PATH,
            PAPERS_README_PATH,
            WORKFLOW_PATH,
            AGENTS_TEST_PATH,
            README_TODO_PATH,
        )
    }
    evidence_anchor_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_EVIDENCE_ANCHORS
    ]
    missing_evidence_anchors = [
        record for record in evidence_anchor_records if record["marker_status"] != "marker_present"
    ]
    workflow_text = texts[WORKFLOW_PATH]
    gitignore_in_workflow = '".gitignore"' in workflow_text or "'.gitignore'" in workflow_text
    static_map_present = (
        not missing_rule_records
        and not missing_evidence_anchors
        and not gitignore_in_workflow
    )
    return {
        "schema": README_IGNORE_POLICY_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "gitignore_path": GITIGNORE_PATH,
        "readme_path": README_PATH,
        "papers_readme_path": PAPERS_README_PATH,
        "workflow_path": WORKFLOW_PATH,
        "agent_docs_test_path": AGENTS_TEST_PATH,
        "todo_paths": [README_TODO_PATH],
        "ignore_rule_count": len(ignore_records),
        "allowlist_rule_count": len(allowlist_records),
        "missing_rule_count": len(missing_rule_records),
        "missing_rule_records": missing_rule_records,
        "ignore_rule_records": ignore_records,
        "allowlist_rule_records": allowlist_records,
        "papers_ignore_rule_status": (
            "papers_wildcard_ignored"
            if "/papers/*" in rules
            else "papers_wildcard_not_ignored"
        ),
        "paper_manifest_allowlist_status": (
            "core_paper_manifests_allowlisted"
            if all(rule in rules for rule in EXPECTED_ALLOWLIST_RULES)
            else "core_paper_manifests_not_allowlisted"
        ),
        "gitignore_workflow_filter_status": (
            "gitignore_not_in_workflow_path_filters"
            if not gitignore_in_workflow
            else "gitignore_in_workflow_path_filters"
        ),
        "evidence_anchor_count": len(evidence_anchor_records),
        "missing_evidence_anchor_count": len(missing_evidence_anchors),
        "missing_evidence_anchor_records": missing_evidence_anchors,
        "evidence_anchor_records": evidence_anchor_records,
        "ignore_policy_map_status": (
            "readme_ignore_policy_static_map_present_with_gitignore_filter_gap"
            if static_map_present
            else "readme_ignore_policy_static_map_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the .gitignore ignore-rule inventory, "
            "paper-manifest allowlist rules, run-artifact local-only policy, "
            "paper-PDF local-only policy, README Repository Layout ignore "
            "markers, papers-index ignore-policy markers, GitHub Actions "
            "README/docs/papers/tests/pyproject path filters, existing agent-doc "
            "workflow assertions, and active TODO ownership. It also records "
            "that .gitignore is not currently included in workflow path filters. "
            "It does not claim a full ignore-rule rationale map, tracked-vs-"
            "ignored sidecar inventory, .gitignore workflow path-filter "
            "coverage, retention-policy drift gating, or owner review signoff."
        ),
    }


def validate_readme_ignore_policy_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeIgnorePolicyBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_ignore_policy_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeIgnorePolicyBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = readme_ignore_policy_boundary_record(root)
    issues: list[ReadmeIgnorePolicyBoundaryIssue] = []
    if data.get("schema") != README_IGNORE_POLICY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README ignore-policy boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README ignore-policy boundary must not claim retention drift gating"))
    for key in (
        "gitignore_path",
        "readme_path",
        "papers_readme_path",
        "workflow_path",
        "agent_docs_test_path",
        "todo_paths",
        "ignore_rule_count",
        "allowlist_rule_count",
        "missing_rule_count",
        "missing_rule_records",
        "ignore_rule_records",
        "allowlist_rule_records",
        "papers_ignore_rule_status",
        "paper_manifest_allowlist_status",
        "gitignore_workflow_filter_status",
        "evidence_anchor_count",
        "missing_evidence_anchor_count",
        "missing_evidence_anchor_records",
        "evidence_anchor_records",
        "ignore_policy_map_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ignore-policy inputs"))
    if data.get("missing_rule_count") != 0:
        issues.append(_issue("missing_gitignore_rule", "expected .gitignore rules are incomplete"))
    if data.get("missing_evidence_anchor_count") != 0:
        issues.append(_issue("missing_ignore_policy_evidence_anchor", "ignore-policy evidence anchors are incomplete"))
    if data.get("gitignore_workflow_filter_status") != "gitignore_not_in_workflow_path_filters":
        issues.append(_issue("unexpected_gitignore_workflow_filter_status", "current boundary expects the .gitignore path-filter gap to remain explicit"))
    if data.get("ignore_policy_map_status") != "readme_ignore_policy_static_map_present_with_gitignore_filter_gap":
        issues.append(_issue("invalid_ignore_policy_map_status", "README ignore-policy static map must be present with the current .gitignore filter gap"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or ".gitignore ignore-rule inventory" not in boundary_text
        or ".gitignore is not currently included in workflow path filters" not in boundary_text
        or "does not claim a full ignore-rule rationale map" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate ignore inventory from retention drift proof"))
    return ReadmeIgnorePolicyBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        ignore_rule_count=data.get("ignore_rule_count") if isinstance(data.get("ignore_rule_count"), int) else 0,
        allowlist_rule_count=data.get("allowlist_rule_count") if isinstance(data.get("allowlist_rule_count"), int) else 0,
        missing_rule_count=data.get("missing_rule_count") if isinstance(data.get("missing_rule_count"), int) else 0,
        evidence_anchor_count=data.get("evidence_anchor_count") if isinstance(data.get("evidence_anchor_count"), int) else 0,
        missing_evidence_anchor_count=data.get("missing_evidence_anchor_count") if isinstance(data.get("missing_evidence_anchor_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_ignore_policy_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_ignore_policy_boundary(boundary)
    lines = [
        "README ignore-policy boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| ignore_rule_count | {validation.ignore_rule_count} |",
        f"| allowlist_rule_count | {validation.allowlist_rule_count} |",
        f"| missing_rule_count | {validation.missing_rule_count} |",
        f"| evidence_anchor_count | {validation.evidence_anchor_count} |",
        f"| missing_evidence_anchor_count | {validation.missing_evidence_anchor_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _gitignore_rules(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _rule_record(rule: str, rules: list[str]) -> dict[str, Any]:
    return {
        "rule": rule,
        "rule_kind": "allowlist" if rule.startswith("!") else "ignore",
        "rule_status": "rule_present" if rule in rules else "rule_missing",
    }


def _marker_record(record_id: str, path: str, text: str, marker: str) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "path": path,
        "required_marker": marker,
        "marker_status": "marker_present" if marker in text else "marker_missing",
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ReadmeIgnorePolicyBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README ignore-policy boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeIgnorePolicyBoundaryIssue],
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
    issues: list[ReadmeIgnorePolicyBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeIgnorePolicyBoundaryIssue:
    return ReadmeIgnorePolicyBoundaryIssue(code, message)
