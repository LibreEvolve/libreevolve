from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RELEASE_CHECKLIST_DOCUMENTATION_BOUNDARY_SCHEMA = (
    "libreevolve.release_checklist_documentation_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "release_checklist_static_drift_record_without_signed_release_proof"
)
CHECKLIST_PATH = "docs/release-checklist.md"
WORKFLOW_PATH = ".github/workflows/tests.yml"
PROVENANCE_TOOL_PATH = "libreevolve/tools/release_artifact_provenance.py"
RELEASE_BOUNDARY_PATH = "papers/release_artifact_reproducibility_boundary.json"
CI_BOUNDARY_PATH = "papers/ci_workflow_coverage_boundary.json"
AGENTS_TEST_PATH = "tests/test_agents_docs.py"
DEVELOPMENT_DOC_PATH = "docs/development.md"
RUN_ARTIFACTS_DOC_PATH = "docs/run-artifacts.md"
ROADMAP_PATH = "ROADMAP.md"
PAPERS_README_PATH = "papers/README.md"
README_TODO_PATH = "docs/todo/readme.md"

EXPECTED_REQUIRED_LOCAL_EVIDENCE_MARKERS = (
    "Build exactly one wheel and one source distribution",
    "Verify every file under the `libreevolve/` package tree",
    "Install the built wheel into an isolated virtual environment",
    "Smoke both command entrypoints",
    "Write `dist/release_artifact_provenance.json`",
    "Upload or otherwise preserve the wheel",
)
EXPECTED_OUTSIDE_CHECKLIST_MARKERS = (
    "Signed release provenance",
    "Published-index or private-index artifact verification",
    "A maintainer-approved release event",
)
EXPECTED_WORKFLOW_MARKERS = (
    "release_artifact:",
    "Release Artifact Smoke",
    "python -m build --wheel --sdist",
    "expected one wheel and one sdist",
    "Path(\"libreevolve\").rglob(\"*\")",
    "wheel is missing package files",
    "sdist is missing package files",
    "python -m libreevolve.tools.release_artifact_provenance --root .",
    "actions/upload-artifact@v4",
    "libreevolve-release-smoke-artifacts",
    "python -m venv .venv-wheel-smoke",
    "python -m pip install dist/*.whl",
    "libreevolve --help",
    "python -m libreevolve --help",
)
EXPECTED_PROVENANCE_TOOL_MARKERS = (
    "RELEASE_ARTIFACT_PROVENANCE_SCHEMA",
    "*.whl",
    "*.tar.gz",
    "pyproject.toml",
    "MANIFEST.in",
    ".github/workflows/tests.yml",
    "dist/release_artifact_provenance.json",
    "provenance must include at least one wheel and one sdist",
)
EXPECTED_EVIDENCE_ANCHORS = (
    ("development_release_checklist_route", DEVELOPMENT_DOC_PATH, "[docs/release-checklist.md](release-checklist.md)"),
    ("run_artifacts_release_boundary", RUN_ARTIFACTS_DOC_PATH, RELEASE_BOUNDARY_PATH),
    ("roadmap_release_scope", ROADMAP_PATH, "release-smoke checklist is documented"),
    ("papers_release_scope", PAPERS_README_PATH, "the local release-smoke checklist is documented"),
    ("release_boundary_claim", "libreevolve/problems/benchmarks/release_artifact_reproducibility_boundary.py", "docs/release-checklist.md records the local release-smoke checklist"),
    ("ci_boundary_claim", "papers/ci_workflow_coverage_boundary.json", "release-artifact smoke job"),
    ("agents_release_tests", AGENTS_TEST_PATH, "test_release_checklist_documents_smoke_and_remaining_release_gates"),
    ("readme_todo_owner", README_TODO_PATH, "Add release-checklist documentation drift evidence."),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "release_checklist_required_local_evidence_bullets",
    "release_checklist_outside_scope_bullets",
    "workflow_release_artifact_job_markers",
    "release_artifact_provenance_tool_markers",
    "release_boundary_sidecar_anchor",
    "ci_boundary_sidecar_anchor",
    "development_and_run_artifact_doc_anchors",
    "agent_doc_tests",
    "active_todo_owner_anchor",
    "per_checklist_bullet_to_workflow_step_map",
    "provenance_schema_field_map",
    "signed_release_provenance",
    "published_index_verification",
    "maintainer_release_event",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "per_checklist_bullet_to_workflow_step_map": "not_recorded_locally",
    "provenance_schema_field_map": "not_recorded_locally",
    "signed_release_provenance": "not_recorded_locally",
    "published_index_verification": "not_recorded_locally",
    "maintainer_release_event": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReleaseChecklistDocumentationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReleaseChecklistDocumentationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_local_evidence_count: int
    outside_scope_count: int
    workflow_marker_count: int
    provenance_tool_marker_count: int
    evidence_anchor_count: int
    missing_marker_count: int
    missing_evidence_count: int
    issues: list[ReleaseChecklistDocumentationBoundaryIssue]


def release_checklist_documentation_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the release-checklist documentation drift record."""

    root_path = Path(root)
    checklist_text = _read_text(root_path / CHECKLIST_PATH)
    workflow_text = _read_text(root_path / WORKFLOW_PATH)
    provenance_tool_text = _read_text(root_path / PROVENANCE_TOOL_PATH)
    texts = {
        DEVELOPMENT_DOC_PATH: _read_text(root_path / DEVELOPMENT_DOC_PATH),
        RUN_ARTIFACTS_DOC_PATH: _read_text(root_path / RUN_ARTIFACTS_DOC_PATH),
        ROADMAP_PATH: _read_text(root_path / ROADMAP_PATH),
        PAPERS_README_PATH: _read_text(root_path / PAPERS_README_PATH),
        "libreevolve/problems/benchmarks/release_artifact_reproducibility_boundary.py": _read_text(
            root_path / "libreevolve/problems/benchmarks/release_artifact_reproducibility_boundary.py"
        ),
        CI_BOUNDARY_PATH: _read_text(root_path / CI_BOUNDARY_PATH),
        AGENTS_TEST_PATH: _read_text(root_path / AGENTS_TEST_PATH),
        README_TODO_PATH: _read_text(root_path / README_TODO_PATH),
    }
    required_bullets = _section_bullets(checklist_text, "## Required Local Evidence")
    outside_bullets = _section_bullets(checklist_text, "## Evidence Still Outside This Checklist")
    required_records = [
        _marker_record(f"required_local_evidence_{index}", CHECKLIST_PATH, checklist_text, marker)
        for index, marker in enumerate(EXPECTED_REQUIRED_LOCAL_EVIDENCE_MARKERS)
    ]
    outside_records = [
        _marker_record(f"outside_scope_{index}", CHECKLIST_PATH, checklist_text, marker)
        for index, marker in enumerate(EXPECTED_OUTSIDE_CHECKLIST_MARKERS)
    ]
    workflow_records = [
        _marker_record(f"workflow_release_artifact_{index}", WORKFLOW_PATH, workflow_text, marker)
        for index, marker in enumerate(EXPECTED_WORKFLOW_MARKERS)
    ]
    provenance_tool_records = [
        _marker_record(f"provenance_tool_{index}", PROVENANCE_TOOL_PATH, provenance_tool_text, marker)
        for index, marker in enumerate(EXPECTED_PROVENANCE_TOOL_MARKERS)
    ]
    evidence_anchor_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_EVIDENCE_ANCHORS
    ]
    all_marker_records = (
        required_records
        + outside_records
        + workflow_records
        + provenance_tool_records
        + evidence_anchor_records
    )
    missing_marker_records = [
        record for record in all_marker_records if record["marker_status"] != "marker_present"
    ]
    return {
        "schema": RELEASE_CHECKLIST_DOCUMENTATION_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "checklist_path": CHECKLIST_PATH,
        "workflow_path": WORKFLOW_PATH,
        "provenance_tool_path": PROVENANCE_TOOL_PATH,
        "release_boundary_path": RELEASE_BOUNDARY_PATH,
        "ci_boundary_path": CI_BOUNDARY_PATH,
        "agent_docs_test_path": AGENTS_TEST_PATH,
        "todo_path": README_TODO_PATH,
        "required_local_evidence_count": len(required_bullets),
        "required_local_evidence_bullets": required_bullets,
        "expected_required_local_evidence_count": len(EXPECTED_REQUIRED_LOCAL_EVIDENCE_MARKERS),
        "outside_scope_count": len(outside_bullets),
        "outside_scope_bullets": outside_bullets,
        "expected_outside_scope_count": len(EXPECTED_OUTSIDE_CHECKLIST_MARKERS),
        "required_local_evidence_records": required_records,
        "outside_scope_records": outside_records,
        "workflow_marker_count": len(workflow_records),
        "workflow_marker_records": workflow_records,
        "provenance_tool_marker_count": len(provenance_tool_records),
        "provenance_tool_marker_records": provenance_tool_records,
        "evidence_anchor_count": len(evidence_anchor_records),
        "evidence_anchor_records": evidence_anchor_records,
        "missing_marker_count": len(missing_marker_records),
        "missing_marker_records": missing_marker_records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records static release-checklist documentation "
            "evidence: the required local smoke bullets, out-of-scope signed/"
            "published/approved release bullets, release_artifact workflow "
            "markers, release_artifact_provenance tool markers, release "
            "reproducibility and CI sidecar anchors, development/run-artifact/"
            "ROADMAP/papers anchors, focused agent-doc tests, and active TODO "
            "ownership. It does not claim a per-checklist-bullet workflow-step "
            "map, provenance schema field map, signed release provenance, "
            "published-index verification, maintainer release event, or owner "
            "review signoff."
        ),
    }


def validate_release_checklist_documentation_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReleaseChecklistDocumentationBoundaryValidation:
    data, read_issues = _load_boundary(
        release_checklist_documentation_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return ReleaseChecklistDocumentationBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = release_checklist_documentation_boundary_record(root)
    issues: list[ReleaseChecklistDocumentationBoundaryIssue] = []
    if data.get("schema") != RELEASE_CHECKLIST_DOCUMENTATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported release-checklist documentation boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "release checklist boundary must not claim release readiness"))
    for key in (
        "checklist_path",
        "workflow_path",
        "provenance_tool_path",
        "release_boundary_path",
        "ci_boundary_path",
        "agent_docs_test_path",
        "todo_path",
        "required_local_evidence_count",
        "required_local_evidence_bullets",
        "expected_required_local_evidence_count",
        "outside_scope_count",
        "outside_scope_bullets",
        "expected_outside_scope_count",
        "required_local_evidence_records",
        "outside_scope_records",
        "workflow_marker_count",
        "workflow_marker_records",
        "provenance_tool_marker_count",
        "provenance_tool_marker_records",
        "evidence_anchor_count",
        "evidence_anchor_records",
        "missing_marker_count",
        "missing_marker_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current release-checklist inputs"))
    if data.get("required_local_evidence_count") != 6:
        issues.append(_issue("invalid_required_local_evidence_count", "release checklist should record six required local evidence bullets"))
    if data.get("outside_scope_count") != 3:
        issues.append(_issue("invalid_outside_scope_count", "release checklist should record three out-of-scope evidence bullets"))
    if data.get("missing_marker_count") != 0:
        issues.append(_issue("missing_release_checklist_marker", "release checklist documentation anchors are incomplete"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "static release-checklist documentation evidence" not in boundary_text
        or "does not claim a per-checklist-bullet workflow-step map" not in boundary_text
        or "signed release provenance" not in boundary_text
        or "published-index verification" not in boundary_text
        or "maintainer release event" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate release-checklist smoke evidence from release proof"))
    return ReleaseChecklistDocumentationBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        required_local_evidence_count=data.get("required_local_evidence_count") if isinstance(data.get("required_local_evidence_count"), int) else 0,
        outside_scope_count=data.get("outside_scope_count") if isinstance(data.get("outside_scope_count"), int) else 0,
        workflow_marker_count=data.get("workflow_marker_count") if isinstance(data.get("workflow_marker_count"), int) else 0,
        provenance_tool_marker_count=data.get("provenance_tool_marker_count") if isinstance(data.get("provenance_tool_marker_count"), int) else 0,
        evidence_anchor_count=data.get("evidence_anchor_count") if isinstance(data.get("evidence_anchor_count"), int) else 0,
        missing_marker_count=data.get("missing_marker_count") if isinstance(data.get("missing_marker_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_release_checklist_documentation_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_release_checklist_documentation_boundary(boundary)
    lines = [
        "Release checklist documentation boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| required_local_evidence_count | {validation.required_local_evidence_count} |",
        f"| outside_scope_count | {validation.outside_scope_count} |",
        f"| workflow_marker_count | {validation.workflow_marker_count} |",
        f"| provenance_tool_marker_count | {validation.provenance_tool_marker_count} |",
        f"| evidence_anchor_count | {validation.evidence_anchor_count} |",
        f"| missing_marker_count | {validation.missing_marker_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _section_bullets(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    bullets: list[str] = []
    in_section = False
    current: list[str] = []
    for line in lines:
        if line.startswith("## "):
            if in_section and current:
                bullets.append(" ".join(current))
                current = []
            in_section = line.strip() == heading
            continue
        if not in_section:
            continue
        if line.startswith("- "):
            if current:
                bullets.append(" ".join(current))
            current = [line[2:].strip()]
        elif current and line.startswith("  "):
            current.append(line.strip())
    if in_section and current:
        bullets.append(" ".join(current))
    return bullets


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
) -> tuple[dict[str, Any] | None, list[ReleaseChecklistDocumentationBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "release-checklist documentation boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReleaseChecklistDocumentationBoundaryIssue],
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
    issues: list[ReleaseChecklistDocumentationBoundaryIssue],
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


def _issue(code: str, message: str) -> ReleaseChecklistDocumentationBoundaryIssue:
    return ReleaseChecklistDocumentationBoundaryIssue(code, message)
