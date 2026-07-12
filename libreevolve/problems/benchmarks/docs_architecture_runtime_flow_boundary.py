from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DOCS_ARCHITECTURE_RUNTIME_FLOW_BOUNDARY_SCHEMA = (
    "libreevolve.docs_architecture_runtime_flow_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "docs_architecture_runtime_flow_recorded_without_semantic_flow_verifier"
)
ARCHITECTURE_PATH = "docs/architecture.md"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "architecture_section_inventory",
    "runtime_flow_step_inventory",
    "source_link_existence_checks",
    "known_gap_marker_inventory",
    "readme_architecture_route",
    "docs_index_architecture_route",
    "active_todo_owner_anchor",
    "flow_order_semantic_verifier",
    "source_function_semantic_verifier",
    "runtime_manifest_field_verifier",
    "architecture_limitation_freshness_matrix",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "flow_order_semantic_verifier": "not_recorded_locally",
    "source_function_semantic_verifier": "not_recorded_locally",
    "runtime_manifest_field_verifier": "not_recorded_locally",
    "architecture_limitation_freshness_matrix": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
EXPECTED_SECTIONS = (
    {
        "section_id": "top_level_flow",
        "heading": "## Top-level flow",
        "markers": (
            "libreevolve/cli.py",
            "load_problem()",
            "evolve(problem, config)",
            "runs/<problem_name>/best.py",
            "runs/<problem_name>/best_workspace/",
        ),
        "source_paths": (
            "libreevolve/cli.py",
            "libreevolve/problems/loader.py",
            "libreevolve/core/loop.py",
        ),
    },
    {
        "section_id": "problem_loading",
        "heading": "## Problem loading",
        "markers": (
            "load_problem()",
            "task_description.txt",
            "metrics.yaml",
            "validate.py",
            "context/*.{txt,md,py,pdf}",
            "preflight default and staged evaluator",
        ),
        "source_paths": (
            "libreevolve/problems/loader.py",
            "libreevolve/core/evaluator.py",
        ),
    },
    {
        "section_id": "candidate_representation",
        "heading": "## Candidate representation",
        "markers": (
            "CandidateWorkspace",
            "Program.code",
            "EVOLVE-BLOCK-START",
            "Mutation application lives",
            "SEARCH/REPLACE",
            "full",
        ),
        "source_paths": (
            "libreevolve/core/candidate.py",
            "libreevolve/population/program.py",
        ),
    },
    {
        "section_id": "evolution_loop",
        "heading": "## Evolution loop",
        "markers": (
            "libreevolve/core/loop.py",
            "samples a parent",
            "runs plugin start hooks",
            "calls the LLM ensemble",
            "archives valid programs",
            "This is local candidate-evaluation overlap, not full asynchronous evolution",
        ),
        "source_paths": (
            "libreevolve/core/loop.py",
            "libreevolve/core/database.py",
            "libreevolve/plugins/base.py",
        ),
    },
    {
        "section_id": "prompt_sampling",
        "heading": "## Prompt sampling",
        "markers": (
            "libreevolve/core/prompt.py",
            "PromptSampler",
            "prompt_max_chars",
            "prompt_max_estimated_tokens",
            "runtime.prompt_section_packing",
            "failure_history.jsonl",
        ),
        "source_paths": (
            "libreevolve/core/prompt.py",
            "libreevolve/core/meta_prompt.py",
            "libreevolve/llm/ensemble.py",
        ),
    },
    {
        "section_id": "evaluation",
        "heading": "## Evaluation",
        "markers": (
            "libreevolve/core/evaluator.py",
            "EvaluationResult",
            "mutation/diff penalty",
            "Python syntax check",
            "subprocess execution of `validate.py`",
            "llm_feedback",
            "on_evaluated()",
        ),
        "source_paths": (
            "libreevolve/core/evaluator.py",
            "libreevolve/core/feedback.py",
            "libreevolve/plugins/base.py",
        ),
    },
    {
        "section_id": "population_model",
        "heading": "## Population model",
        "markers": (
            "Program",
            "MAPElites",
            "IslandModel",
            "runtime.history.archive_state",
            "archive_events.jsonl",
            "migration rows",
        ),
        "source_paths": (
            "libreevolve/population/program.py",
            "libreevolve/population/map_elites.py",
            "libreevolve/population/islands.py",
        ),
    },
    {
        "section_id": "backend_selection",
        "heading": "## Backend selection",
        "markers": (
            "libreevolve/llm/ensemble.py",
            "OpenAI",
            "Anthropic",
            "Ollama",
            "one or more backends",
            "verified reproduction of AlphaEvolve's Gemini Flash/Pro policy",
        ),
        "source_paths": (
            "libreevolve/llm/ensemble.py",
            "libreevolve/llm/openai.py",
            "libreevolve/llm/anthropic.py",
            "libreevolve/llm/ollama.py",
            "libreevolve/llm/backend_registry.py",
        ),
    },
    {
        "section_id": "logging_and_artifacts",
        "heading": "## Logging and artifacts",
        "markers": (
            "libreevolve/core/database.py",
            "manifest.json",
            "history.jsonl",
            "prompt_history.jsonl",
            "best.py",
            "best_workspace/",
        ),
        "source_paths": (
            "libreevolve/core/database.py",
            "docs/run-artifacts.md",
        ),
    },
    {
        "section_id": "known_gaps",
        "heading": "## Known gaps",
        "markers": (
            "Candidate workspaces are local text file sets",
            "Proposal generation and LLM work remain sequential",
            "Archive cell/island state is persisted",
            "Plugin names are paper-inspired approximations",
        ),
        "source_paths": (
            "docs/todo/code.md",
            "docs/todo/readme.md",
            "docs/todo/papers.md",
        ),
    },
)
EXPECTED_ROUTE_MARKERS = (
    {
        "route_id": "readme_documentation_map_architecture",
        "source_path": "README.md",
        "marker": "[docs/architecture.md](docs/architecture.md)",
    },
    {
        "route_id": "docs_index_architecture_route",
        "source_path": "docs/README.md",
        "marker": "[Architecture](./architecture.md)",
    },
    {
        "route_id": "todo_architecture_runtime_flow_owner",
        "source_path": "docs/todo/readme.md",
        "marker": "Add architecture-guide runtime-flow drift evidence.",
    },
)


@dataclass(frozen=True)
class DocsArchitectureRuntimeFlowBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class DocsArchitectureRuntimeFlowBoundaryValidation:
    ok: bool
    boundary_status: str | None
    section_record_count: int
    missing_section_record_count: int
    missing_source_path_count: int
    missing_evidence_count: int
    issues: list[DocsArchitectureRuntimeFlowBoundaryIssue]


def docs_architecture_runtime_flow_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded docs/architecture.md runtime-flow inventory."""

    root_path = Path(root)
    architecture_text = _read_text(root_path / ARCHITECTURE_PATH)
    section_records = [
        _section_record(root_path, architecture_text, section)
        for section in EXPECTED_SECTIONS
    ]
    missing_section_records = [
        record
        for record in section_records
        if record["section_status"] != "section_markers_and_sources_present"
    ]
    route_records = [_route_record(root_path, route) for route in EXPECTED_ROUTE_MARKERS]
    missing_route_records = [
        record for record in route_records if record["marker_status"] != "marker_present"
    ]
    missing_source_paths = sorted(
        {
            path
            for record in section_records
            for path in record["missing_source_paths"]
        }
    )
    return {
        "schema": DOCS_ARCHITECTURE_RUNTIME_FLOW_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "architecture_path": ARCHITECTURE_PATH,
        "architecture_heading_status": (
            "heading_present" if "# Architecture" in architecture_text else "heading_missing"
        ),
        "section_record_count": len(section_records),
        "missing_section_record_count": len(missing_section_records),
        "missing_section_records": missing_section_records,
        "section_records": section_records,
        "missing_source_path_count": len(missing_source_paths),
        "missing_source_paths": missing_source_paths,
        "route_record_count": len(route_records),
        "missing_route_record_count": len(missing_route_records),
        "missing_route_records": missing_route_records,
        "route_records": route_records,
        "known_gap_section_status": _section_status(section_records, "known_gaps"),
        "sync_runtime_boundary_status": (
            "local_candidate_async_runtime_boundary_present"
            if "opt-in candidate-level asyncio" in architecture_text
            else "local_candidate_async_runtime_boundary_missing"
        ),
        "alphaevolve_parity_boundary_status": (
            "alphaevolve_parity_boundary_present"
            if "verified reproduction of AlphaEvolve's Gemini Flash/Pro policy"
            in architecture_text
            else "alphaevolve_parity_boundary_missing"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records docs/architecture.md section headings, "
            "runtime-flow markers, source-link/path existence checks, route "
            "markers from README and docs/README.md, the active TODO owner "
            "anchor, known-gap markers, the local candidate-async runtime boundary, and "
            "the AlphaEvolve provider-parity boundary. It does not claim "
            "semantic flow-order verification, source-function semantic "
            "verification, runtime manifest field verification, architecture "
            "limitation freshness, or owner review signoff."
        ),
    }


def validate_docs_architecture_runtime_flow_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> DocsArchitectureRuntimeFlowBoundaryValidation:
    data, read_issues = _load_boundary(
        docs_architecture_runtime_flow_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return DocsArchitectureRuntimeFlowBoundaryValidation(False, None, 0, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = docs_architecture_runtime_flow_boundary_record(root)
    issues: list[DocsArchitectureRuntimeFlowBoundaryIssue] = []
    if data.get("schema") != DOCS_ARCHITECTURE_RUNTIME_FLOW_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported docs/architecture runtime-flow boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "architecture runtime-flow boundary must not claim semantic flow proof"))
    for key in (
        "architecture_path",
        "architecture_heading_status",
        "section_record_count",
        "missing_section_record_count",
        "missing_section_records",
        "section_records",
        "missing_source_path_count",
        "missing_source_paths",
        "route_record_count",
        "missing_route_record_count",
        "missing_route_records",
        "route_records",
        "known_gap_section_status",
        "sync_runtime_boundary_status",
        "alphaevolve_parity_boundary_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current architecture inputs"))
    if data.get("architecture_heading_status") != "heading_present":
        issues.append(_issue("missing_architecture_heading", "docs/architecture.md must keep the Architecture heading"))
    if data.get("missing_section_record_count") != 0:
        issues.append(_issue("missing_architecture_section_marker", "architecture sections are missing headings, markers, or source paths"))
    if data.get("missing_source_path_count") != 0:
        issues.append(_issue("missing_architecture_source_path", "architecture source paths must exist"))
    if data.get("missing_route_record_count") != 0:
        issues.append(_issue("missing_architecture_route_marker", "architecture guide routes or TODO owner marker are incomplete"))
    if data.get("sync_runtime_boundary_status") != (
        "local_candidate_async_runtime_boundary_present"
    ):
        issues.append(
            _issue(
                "missing_sync_runtime_boundary",
                "architecture guide must preserve the scoped local candidate-async runtime boundary",
            )
        )
    if data.get("alphaevolve_parity_boundary_status") != "alphaevolve_parity_boundary_present":
        issues.append(_issue("missing_alphaevolve_parity_boundary", "architecture guide must preserve AlphaEvolve provider parity boundary"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "docs/architecture.md section headings" not in boundary_text
        or "local candidate-async runtime boundary" not in boundary_text
        or "does not claim semantic flow-order verification" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate architecture inventory from semantic flow proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return DocsArchitectureRuntimeFlowBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        section_record_count=data.get("section_record_count") if isinstance(data.get("section_record_count"), int) else 0,
        missing_section_record_count=(
            data.get("missing_section_record_count")
            if isinstance(data.get("missing_section_record_count"), int)
            else 0
        ),
        missing_source_path_count=(
            data.get("missing_source_path_count")
            if isinstance(data.get("missing_source_path_count"), int)
            else 0
        ),
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_docs_architecture_runtime_flow_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_docs_architecture_runtime_flow_boundary(boundary)
    lines = [
        "Docs architecture runtime-flow boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| section_record_count | {validation.section_record_count} |",
        f"| missing_section_record_count | {validation.missing_section_record_count} |",
        f"| missing_source_path_count | {validation.missing_source_path_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _section_record(root: Path, architecture_text: str, section: dict[str, Any]) -> dict[str, Any]:
    heading = str(section["heading"])
    section_text = _section_text(architecture_text, heading)
    missing_markers = [marker for marker in section["markers"] if marker not in section_text]
    source_paths = [str(path) for path in section["source_paths"]]
    missing_source_paths = [path for path in source_paths if not (root / path).exists()]
    heading_present = bool(section_text)
    section_status = (
        "section_markers_and_sources_present"
        if heading_present and not missing_markers and not missing_source_paths
        else "section_markers_or_sources_missing"
    )
    return {
        "section_id": section["section_id"],
        "heading": heading,
        "heading_status": "heading_present" if heading_present else "heading_missing",
        "missing_markers": missing_markers,
        "source_paths": source_paths,
        "missing_source_paths": missing_source_paths,
        "section_status": section_status,
    }


def _section_text(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    next_heading = text.find("\n## ", start + len(heading))
    if next_heading < 0:
        return text[start:]
    return text[start:next_heading]


def _route_record(root: Path, route: dict[str, str]) -> dict[str, Any]:
    source_path = route["source_path"]
    text = _read_text(root / source_path)
    marker = route["marker"]
    return {
        "route_id": route["route_id"],
        "source_path": source_path,
        "target_path": ARCHITECTURE_PATH,
        "marker": marker,
        "marker_status": "marker_present" if marker in text else "marker_missing",
    }


def _section_status(section_records: list[dict[str, Any]], section_id: str) -> str:
    for record in section_records:
        if record["section_id"] == section_id:
            return str(record["section_status"])
    return "section_missing"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[DocsArchitectureRuntimeFlowBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "docs/architecture runtime-flow boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[DocsArchitectureRuntimeFlowBoundaryIssue],
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
    issues: list[DocsArchitectureRuntimeFlowBoundaryIssue],
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


def _issue(code: str, message: str) -> DocsArchitectureRuntimeFlowBoundaryIssue:
    return DocsArchitectureRuntimeFlowBoundaryIssue(code, message)
