from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_AGENT_ROUTING_BOUNDARY_SCHEMA = "libreevolve.readme_agent_routing_boundary.v1"
EXPECTED_BOUNDARY_STATUS = (
    "agent_operating_contract_routed_without_full_instruction_drift_map"
)
README_PATH = "README.md"
DOCS_README_PATH = "docs/README.md"
DEVELOPMENT_PATH = "docs/development.md"
AGENTS_PATH = "AGENTS.md"
WORKFLOW_PATH = ".github/workflows/tests.yml"
AGENTS_TEST_PATH = "tests/test_agents_docs.py"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_documentation_map_route",
    "docs_readme_reader_path_route",
    "development_ci_agent_path_scope",
    "agents_operating_contract_surface",
    "agents_docs_test_gate",
    "github_actions_agents_path_filter",
    "command_instruction_links",
    "test_instruction_links",
    "backend_instruction_links",
    "artifact_instruction_links",
    "alphaevolve_boundary_instruction_links",
    "complete_instruction_drift_map",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "complete_instruction_drift_map": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
INSTRUCTION_LINK_MARKERS = {
    "command_instruction_links": (
        "py -3.12 -m pytest tests/ -m \"not integration\" --tb=short",
        "docs/development.md",
    ),
    "test_instruction_links": (
        "tests/test_agents_docs.py",
        ".github/workflows/tests.yml",
    ),
    "backend_instruction_links": (
        "docs/backends.md",
        "OpenAI, Anthropic, Google Gemini, Ollama",
    ),
    "artifact_instruction_links": (
        "docs/run-artifacts.md",
        "archive_events.jsonl",
        "llm_calls.jsonl",
        "best_workspace/",
    ),
    "alphaevolve_boundary_instruction_links": (
        "papers/README.md",
        "SEARCH/REPLACE",
        "AlphaEvolve",
    ),
}


@dataclass(frozen=True)
class ReadmeAgentRoutingBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeAgentRoutingBoundaryValidation:
    ok: bool
    boundary_status: str | None
    route_record_count: int
    missing_route_count: int
    instruction_link_record_count: int
    missing_instruction_link_count: int
    missing_evidence_count: int
    issues: list[ReadmeAgentRoutingBoundaryIssue]


def readme_agent_routing_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded README AGENTS.md routing evidence record."""

    root_path = Path(root)
    readme_text = _read_text(root_path / README_PATH)
    docs_readme_text = _read_text(root_path / DOCS_README_PATH)
    development_text = _read_text(root_path / DEVELOPMENT_PATH)
    agents_text = _read_text(root_path / AGENTS_PATH)
    workflow_text = _read_text(root_path / WORKFLOW_PATH)
    test_text = _read_text(root_path / AGENTS_TEST_PATH)
    route_records = [
        _marker_record(
            "readme_documentation_map_route",
            README_PATH,
            readme_text,
            ("[AGENTS.md](AGENTS.md)", "agent-facing operating contract"),
        ),
        _marker_record(
            "docs_readme_reader_path_route",
            DOCS_README_PATH,
            docs_readme_text,
            ("[AGENTS.md](../AGENTS.md)", "agent-facing operating contract"),
        ),
        _marker_record(
            "development_ci_agent_path_scope",
            DEVELOPMENT_PATH,
            development_text,
            ("agent-facing instructions", "AGENTS.md"),
        ),
        _marker_record(
            "agents_operating_contract_surface",
            AGENTS_PATH,
            agents_text,
            ("# AGENTS.md", "Running Tests", "Running the Tool"),
        ),
        _marker_record(
            "agents_docs_test_gate",
            AGENTS_TEST_PATH,
            test_text,
            ("test_agents_instructions", "AGENTS.md"),
        ),
        _marker_record(
            "github_actions_agents_path_filter",
            WORKFLOW_PATH,
            workflow_text,
            ("AGENTS.md", "tests/test_agents_docs.py"),
        ),
    ]
    instruction_link_records = [
        _marker_record(kind, AGENTS_PATH, agents_text, markers)
        for kind, markers in INSTRUCTION_LINK_MARKERS.items()
    ]
    missing_route_records = [
        record
        for record in route_records
        if record["record_status"] != "all_markers_present"
    ]
    missing_instruction_link_records = [
        record
        for record in instruction_link_records
        if record["record_status"] != "all_markers_present"
    ]
    return {
        "schema": README_AGENT_ROUTING_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "docs_readme_path": DOCS_README_PATH,
        "development_path": DEVELOPMENT_PATH,
        "agents_path": AGENTS_PATH,
        "workflow_path": WORKFLOW_PATH,
        "agents_test_path": AGENTS_TEST_PATH,
        "route_record_count": len(route_records),
        "missing_route_count": len(missing_route_records),
        "missing_route_records": missing_route_records,
        "route_records": route_records,
        "instruction_link_record_count": len(instruction_link_records),
        "missing_instruction_link_count": len(missing_instruction_link_records),
        "missing_instruction_link_records": missing_instruction_link_records,
        "instruction_link_records": instruction_link_records,
        "routing_status": (
            "agents_operating_contract_routed"
            if not missing_route_records and not missing_instruction_link_records
            else "agents_operating_contract_routing_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records README/docs routing for AGENTS.md as an "
            "agent-facing operating contract, development-guide CI path scope, "
            "GitHub Actions AGENTS.md path-filter coverage, tests/test_agents_docs.py "
            "coverage, and bounded command, test, backend, artifact, and "
            "AlphaEvolve instruction links. It does not claim a complete instruction-drift "
            "map or owner review signoff."
        ),
    }


def validate_readme_agent_routing_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeAgentRoutingBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_agent_routing_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeAgentRoutingBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = readme_agent_routing_boundary_record(root)
    issues: list[ReadmeAgentRoutingBoundaryIssue] = []
    if data.get("schema") != README_AGENT_ROUTING_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README AGENTS routing boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README AGENTS routing boundary must not claim full instruction drift proof"))
    for key in (
        "readme_path",
        "docs_readme_path",
        "development_path",
        "agents_path",
        "workflow_path",
        "agents_test_path",
        "route_record_count",
        "missing_route_count",
        "missing_route_records",
        "route_records",
        "instruction_link_record_count",
        "missing_instruction_link_count",
        "missing_instruction_link_records",
        "instruction_link_records",
        "routing_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current AGENTS routing inputs"))
    if data.get("missing_route_count") != 0:
        issues.append(_issue("missing_agent_route", "README/docs/workflow AGENTS routing markers are incomplete"))
    if data.get("missing_instruction_link_count") != 0:
        issues.append(_issue("missing_instruction_link", "bounded AGENTS instruction links are incomplete"))
    if data.get("routing_status") != "agents_operating_contract_routed":
        issues.append(_issue("invalid_routing_status", "AGENTS operating contract must be routed"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "README/docs routing for AGENTS.md" not in boundary_text
        or "agent-facing operating contract" not in boundary_text
        or "tests/test_agents_docs.py" not in boundary_text
        or "does not claim a complete instruction-drift map" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate routing evidence from full instruction-drift proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return ReadmeAgentRoutingBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        route_record_count=data.get("route_record_count") if isinstance(data.get("route_record_count"), int) else 0,
        missing_route_count=data.get("missing_route_count") if isinstance(data.get("missing_route_count"), int) else 0,
        instruction_link_record_count=data.get("instruction_link_record_count") if isinstance(data.get("instruction_link_record_count"), int) else 0,
        missing_instruction_link_count=data.get("missing_instruction_link_count") if isinstance(data.get("missing_instruction_link_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_agent_routing_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_agent_routing_boundary(boundary)
    lines = [
        "README AGENTS routing boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| route_record_count | {validation.route_record_count} |",
        f"| missing_route_count | {validation.missing_route_count} |",
        f"| instruction_link_record_count | {validation.instruction_link_record_count} |",
        f"| missing_instruction_link_count | {validation.missing_instruction_link_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _marker_record(
    kind: str,
    path: str,
    text: str,
    markers: tuple[str, ...],
) -> dict[str, Any]:
    missing = [marker for marker in markers if marker not in text]
    return {
        "record_kind": kind,
        "path": path,
        "required_markers": list(markers),
        "missing_markers": missing,
        "record_status": "all_markers_present" if not missing else "markers_missing",
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ReadmeAgentRoutingBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README AGENTS routing boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeAgentRoutingBoundaryIssue],
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
    issues: list[ReadmeAgentRoutingBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeAgentRoutingBoundaryIssue:
    return ReadmeAgentRoutingBoundaryIssue(code, message)
