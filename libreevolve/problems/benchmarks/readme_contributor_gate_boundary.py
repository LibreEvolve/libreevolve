from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_CONTRIBUTOR_GATE_BOUNDARY_SCHEMA = (
    "libreevolve.readme_contributor_gate_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "readme_contributor_gate_static_map_without_policy_drift_proof"
)
README_PATH = "README.md"
DEVELOPMENT_PATH = "docs/development.md"
PRE_COMMIT_PATH = ".pre-commit-config.yaml"
SECRETS_BASELINE_PATH = ".secrets.baseline"
WORKFLOW_PATH = ".github/workflows/tests.yml"
AGENTS_TEST_PATH = "tests/test_agents_docs.py"
README_TODO_PATH = "docs/todo/readme.md"
CI_BOUNDARY_PATH = "papers/ci_workflow_coverage_boundary.json"

EXPECTED_README_MARKERS = (
    ("contributing_heading", "## Contributing"),
    ("readme_scope", "Keep the root README practical and short."),
    ("docs_scope", "Detailed behavior belongs in `docs/`"),
    (
        "papers_scope",
        "paper-boundary evidence belongs in `papers/README.md` and JSON sidecars",
    ),
    (
        "roadmap_todo_scope",
        "long-term implementation status belongs in `ROADMAP.md` or `docs/todo/`",
    ),
    ("focused_tests", "Before opening a change, run focused tests for touched code"),
    (
        "paper_manifest_gate",
        "paper\nmanifest check when source-boundary files change",
    ),
    ("secret_baseline", "The secret scan uses `.secrets.baseline`"),
    ("allowlist_pragma", "# pragma: allowlist secret"),
    (
        "baseline_stage_policy",
        "regenerated baselines\nmust be staged with the code that needs them",
    ),
)
EXPECTED_EVIDENCE_ANCHORS = (
    ("development_precommit_command", DEVELOPMENT_PATH, "py -3.12 -m pre_commit run --all-files"),
    ("development_secret_baseline", DEVELOPMENT_PATH, "The secret scan uses `.secrets.baseline`."),
    ("development_allowlist_pragma", DEVELOPMENT_PATH, "# pragma: allowlist secret"),
    ("development_unstaged_policy", DEVELOPMENT_PATH, "An\nunstaged baseline update is a validation failure"),
    ("development_paper_manifest_command", DEVELOPMENT_PATH, "py -3.12 -m libreevolve.tools.paper_manifest"),
    ("precommit_detect_secrets_hook", PRE_COMMIT_PATH, "id: detect-secrets"),
    ("precommit_baseline_arg", PRE_COMMIT_PATH, ".secrets.baseline"),
    ("precommit_ip_detector_disable", PRE_COMMIT_PATH, "IPPublicDetector"),
    ("secrets_baseline_plugins", SECRETS_BASELINE_PATH, '"plugins_used"'),
    ("secrets_baseline_openai_detector", SECRETS_BASELINE_PATH, '"OpenAIDetector"'),
    ("workflow_secret_scan_job", WORKFLOW_PATH, "name: Secret Scan"),
    ("workflow_detect_secrets_run", WORKFLOW_PATH, "python -m pre_commit run detect-secrets --all-files --show-diff-on-failure"),
    ("workflow_secret_baseline_path_filter", WORKFLOW_PATH, '".secrets.baseline"'),
    ("workflow_readme_path_filter", WORKFLOW_PATH, '"README.md"'),
    ("workflow_docs_path_filter", WORKFLOW_PATH, '"docs/**"'),
    ("workflow_papers_path_filter", WORKFLOW_PATH, '"papers/**"'),
    ("workflow_paper_manifest_gate", WORKFLOW_PATH, "python -m libreevolve.tools.paper_manifest --root ."),
    ("workflow_boundary_tests", WORKFLOW_PATH, 'Path("tests").glob("test_*boundary.py")'),
    ("agents_secret_scan_test", AGENTS_TEST_PATH, "test_development_docs_track_detect_secrets_baseline_workflow"),
    ("agents_secret_baseline_assertion", AGENTS_TEST_PATH, 'assert ".secrets.baseline" in text'),
    ("agents_allowlist_assertion", AGENTS_TEST_PATH, 'assert "# pragma: allowlist secret" in text'),
    ("agents_workflow_path_filter_test", AGENTS_TEST_PATH, "test_tests_workflow_covers_docs_papers_and_todo_changes"),
    ("ci_workflow_boundary_secret_scan", CI_BOUNDARY_PATH, "secret scan job"),
    ("ci_workflow_boundary_paper_docs", CI_BOUNDARY_PATH, "paper/docs job"),
    ("readme_todo_owner", README_TODO_PATH, "Add README contributor-gate and secret-scan evidence mapping."),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_contributing_markers",
    "docs_scope_routing_markers",
    "focused_test_guidance",
    "paper_manifest_source_boundary_guidance",
    "secret_scan_baseline_policy",
    "allowlist_pragma_policy",
    "baseline_staging_policy",
    "development_guide_secret_scan_anchors",
    "precommit_detect_secrets_hook",
    "secrets_baseline_detector_inventory",
    "github_actions_secret_scan_job",
    "github_actions_paper_docs_job",
    "agents_docs_drift_assertions",
    "ci_workflow_boundary_anchor",
    "active_todo_owner_anchor",
    "complete_sentence_to_artifact_map",
    "precommit_drift_gate",
    "source_boundary_file_change_detector",
    "semantic_secret_policy_verifier",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "complete_sentence_to_artifact_map": "not_recorded_locally",
    "precommit_drift_gate": "not_recorded_locally",
    "source_boundary_file_change_detector": "not_recorded_locally",
    "semantic_secret_policy_verifier": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmeContributorGateBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeContributorGateBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readme_marker_count: int
    missing_readme_marker_count: int
    evidence_anchor_count: int
    missing_evidence_anchor_count: int
    missing_evidence_count: int
    issues: list[ReadmeContributorGateBoundaryIssue]


def readme_contributor_gate_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the README contributor-gate static evidence map."""

    root_path = Path(root)
    readme_text = _read_text(root_path / README_PATH)
    texts = {
        path: _read_text(root_path / path)
        for path in (
            DEVELOPMENT_PATH,
            PRE_COMMIT_PATH,
            SECRETS_BASELINE_PATH,
            WORKFLOW_PATH,
            AGENTS_TEST_PATH,
            README_TODO_PATH,
            CI_BOUNDARY_PATH,
        )
    }
    readme_marker_records = [
        _marker_record(record_id, README_PATH, readme_text, marker)
        for record_id, marker in EXPECTED_README_MARKERS
    ]
    evidence_anchor_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_EVIDENCE_ANCHORS
    ]
    missing_readme_markers = [
        record for record in readme_marker_records if record["marker_status"] != "marker_present"
    ]
    missing_evidence_anchors = [
        record for record in evidence_anchor_records if record["marker_status"] != "marker_present"
    ]
    return {
        "schema": README_CONTRIBUTOR_GATE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "development_path": DEVELOPMENT_PATH,
        "precommit_path": PRE_COMMIT_PATH,
        "secret_scan_path": SECRETS_BASELINE_PATH,
        "workflow_path": WORKFLOW_PATH,
        "agent_docs_test_path": AGENTS_TEST_PATH,
        "sidecar_paths": [CI_BOUNDARY_PATH],
        "todo_paths": [README_TODO_PATH],
        "readme_marker_count": len(readme_marker_records),
        "missing_readme_marker_count": len(missing_readme_markers),
        "missing_readme_marker_records": missing_readme_markers,
        "readme_marker_records": readme_marker_records,
        "evidence_anchor_count": len(evidence_anchor_records),
        "missing_evidence_anchor_count": len(missing_evidence_anchors),
        "missing_evidence_anchor_records": missing_evidence_anchors,
        "evidence_anchor_records": evidence_anchor_records,
        "contributor_gate_map_status": (
            "readme_contributor_gate_static_map_present"
            if not missing_readme_markers and not missing_evidence_anchors
            else "readme_contributor_gate_static_map_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records README Contributing markers, docs/papers/"
            "ROADMAP/TODO routing markers, focused-test and paper-manifest "
            "guidance, secret-scan baseline policy, allowlist-pragma policy, "
            "baseline-staging policy, development-guide secret-scan anchors, "
            "the pre-commit detect-secrets hook, .secrets.baseline detector "
            "inventory markers, GitHub Actions secret-scan and paper/docs jobs, "
            "tests/test_agents_docs.py drift assertions, CI workflow sidecar "
            "anchors, and active TODO ownership. It does not claim a complete "
            "sentence-to-artifact map, pre-commit drift gate, source-boundary "
            "file-change detector, semantic secret-policy verifier, or owner "
            "review signoff."
        ),
    }


def validate_readme_contributor_gate_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeContributorGateBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_contributor_gate_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeContributorGateBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = readme_contributor_gate_boundary_record(root)
    issues: list[ReadmeContributorGateBoundaryIssue] = []
    if data.get("schema") != README_CONTRIBUTOR_GATE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README contributor-gate boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README contributor-gate boundary must not claim policy drift proof"))
    for key in (
        "readme_path",
        "development_path",
        "precommit_path",
        "secret_scan_path",
        "workflow_path",
        "agent_docs_test_path",
        "sidecar_paths",
        "todo_paths",
        "readme_marker_count",
        "missing_readme_marker_count",
        "missing_readme_marker_records",
        "readme_marker_records",
        "evidence_anchor_count",
        "missing_evidence_anchor_count",
        "missing_evidence_anchor_records",
        "evidence_anchor_records",
        "contributor_gate_map_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current contributor-gate inputs"))
    if data.get("missing_readme_marker_count") != 0:
        issues.append(_issue("missing_readme_contributor_marker", "README contributor markers are incomplete"))
    if data.get("missing_evidence_anchor_count") != 0:
        issues.append(_issue("missing_contributor_gate_evidence_anchor", "README contributor evidence anchors are incomplete"))
    if data.get("contributor_gate_map_status") != "readme_contributor_gate_static_map_present":
        issues.append(_issue("invalid_contributor_gate_map_status", "README contributor static map must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "README Contributing markers" not in boundary_text
        or "pre-commit detect-secrets hook" not in boundary_text
        or "does not claim a complete sentence-to-artifact map" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate contributor static map from policy drift proof"))
    return ReadmeContributorGateBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readme_marker_count=data.get("readme_marker_count") if isinstance(data.get("readme_marker_count"), int) else 0,
        missing_readme_marker_count=data.get("missing_readme_marker_count") if isinstance(data.get("missing_readme_marker_count"), int) else 0,
        evidence_anchor_count=data.get("evidence_anchor_count") if isinstance(data.get("evidence_anchor_count"), int) else 0,
        missing_evidence_anchor_count=data.get("missing_evidence_anchor_count") if isinstance(data.get("missing_evidence_anchor_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_contributor_gate_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_contributor_gate_boundary(boundary)
    lines = [
        "README contributor-gate boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| readme_marker_count | {validation.readme_marker_count} |",
        f"| missing_readme_marker_count | {validation.missing_readme_marker_count} |",
        f"| evidence_anchor_count | {validation.evidence_anchor_count} |",
        f"| missing_evidence_anchor_count | {validation.missing_evidence_anchor_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


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
) -> tuple[dict[str, Any] | None, list[ReadmeContributorGateBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README contributor-gate boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeContributorGateBoundaryIssue],
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
    issues: list[ReadmeContributorGateBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeContributorGateBoundaryIssue:
    return ReadmeContributorGateBoundaryIssue(code, message)
