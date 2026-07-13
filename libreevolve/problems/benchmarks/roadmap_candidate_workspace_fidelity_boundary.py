from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_CANDIDATE_WORKSPACE_FIDELITY_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_candidate_workspace_fidelity_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_candidate_workspace_fidelity_matrix_without_alphaevolve_workspace_readiness"
)
EXPECTED_ROADMAP_HEADING = "### 1. Finish candidate workspace fidelity"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "criterion_records",
    "roadmap_section_presence",
    "language_build_runner_policy",
    "candidate_abstraction_policy",
    "marker_materialization_policy",
    "embedded_evaluator_policy",
    "codebase_scale_fixture_policy",
    "mutation_operator_provenance_policy",
    "prompt_example_copy_policy",
    "cross_file_consistency_policy",
    "initial_pool_static_binary_policy",
    "workspace_resume_replay_policy",
    "stale_readiness_detector",
)
EXPECTED_MISSING_EVIDENCE = {
    "portable_hermetic_replayable_build_runner_evidence": (
        "host_c_compiler_smoke_recorded_portable_replay_not_recorded"
    ),
    "flexible_solution_abstraction_api": "not_recorded_locally",
    "candidate_embedded_evaluator_contracts": "not_recorded_locally",
    "realistic_codebase_fixtures": "not_recorded_locally",
    "benchmark_calibrated_adaptive_mutation_mode_policy": "not_recorded_locally",
    "mutation_operator_family_provenance": "not_recorded_locally",
    "semantic_prompt_example_copy_detection": "not_recorded_locally",
    "cross_file_consistency_benchmark_evidence": "not_recorded_locally",
    "initial_pool_divergence_benchmark_evidence": "not_recorded_locally",
    "static_binary_replay_policy": "not_recorded_locally",
    "topology_resume_replay_proof": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "language_build_runner_support",
        "search_surface": "candidate language/build/runner declarations and execution policy",
        "current_scope": "task-primary local expression and host C build/runner/scorer execution with toolchain identity but without portable replay parity",
        "missing_readiness": "portable hermetic and broader language runners, replayable build-system contracts, isolation, and codebase-scale capability evidence",
        "roadmap_required_phrase": "compiled and interpreted language/package-manager fixtures",
        "current_sidecars": ("papers/candidate_language_runner_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "portable hermetic compiler/package-manager",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "broader real-language and build-system contracts",
            },
        ),
        "validation_gate": "portable hermetic replay and broader-language contract tests with manifest evidence",
        "readiness_status": "local_expression_and_host_c_partial_without_portable_toolchain_gate",
    },
    {
        "criterion_id": "candidate_abstraction_api",
        "search_surface": "problem-defined solution abstraction choices",
        "current_scope": "task-primary bounded text-workspace abstraction plus design/bias matrices",
        "missing_readiness": "typed problem-defined abstraction APIs and equal-budget abstraction-choice evidence",
        "roadmap_required_phrase": "problem-defined candidate abstraction hooks",
        "current_sidecars": (
            "papers/candidate_abstraction_boundary.json",
            "papers/candidate_abstraction_bias_matrix.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "problem-level abstraction rationale",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "benchmark metadata for candidate abstraction family",
            },
        ),
        "validation_gate": "problem-declared abstraction schema and benchmarked alternatives",
        "readiness_status": "code_file_set_abstraction_only",
    },
    {
        "criterion_id": "marker_materialization_policy",
        "search_surface": "evolve-block markers, workspace topology, and materialization diagnostics",
        "current_scope": "Python evolve-block handling and bounded workspace topology diagnostics",
        "missing_readiness": "language-aware marker grammars and materialization diagnostics across future workspace surfaces",
        "roadmap_required_phrase": "language-aware evolve-block marker grammars",
        "current_sidecars": ("papers/workspace_materialization_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "future topology surfaces",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "future topology surfaces",
            },
        ),
        "validation_gate": "language-aware marker/materialization tests and topology diagnostics",
        "readiness_status": "python_marker_and_bounded_topology_only",
    },
    {
        "criterion_id": "embedded_evaluator_boundary",
        "search_surface": "candidate-owned evaluator loading and Figure 3 parity",
        "current_scope": "external validator contract with candidate-embedded evaluator absence boundary",
        "missing_readiness": "default candidate-owned evaluator loading and sandboxed evaluator contract tests",
        "roadmap_required_phrase": "evaluator-workload",
        "current_sidecars": ("papers/embedded_evaluator_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "candidate-owned evaluation",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "default candidate-owned evaluator loading",
            },
        ),
        "validation_gate": "candidate-embedded evaluator lifecycle and isolation evidence",
        "readiness_status": "external_validator_contract_only",
    },
    {
        "criterion_id": "codebase_scale_fixtures",
        "search_surface": "multi-component generated codebase fixtures and Table 1 capability claims",
        "current_scope": "workspace_math smoke fixture and codebase-scale absence sidecar",
        "missing_readiness": "realistic codebase-scale fixtures, dependencies, runners, artifacts, and sample-efficiency evidence",
        "roadmap_required_phrase": "realistic codebase-scale fixtures",
        "current_sidecars": (
            "papers/codebase_scale_benchmark_boundary.json",
            "papers/existing_codebase_integration_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add codebase-scale benchmark evidence",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "paper-facing codebase-scale fixture",
            },
        ),
        "validation_gate": "external or realistic multi-component benchmark fixture with retained artifacts",
        "readiness_status": "smoke_fixture_without_table1_parity",
    },
    {
        "criterion_id": "mutation_mode_operator_provenance",
        "search_surface": "diff/full/file/block/topology mutation modes and operator-family evidence",
        "current_scope": "per-candidate shape/task/failure diff-full selection plus fixed parser surfaces without calibrated policy or operator-family provenance",
        "missing_readiness": "benchmark-calibrated adaptive mutation-mode policy and LLM-constructed operator-family provenance",
        "roadmap_required_phrase": "proposal-level operator-family provenance",
        "current_sidecars": (
            "papers/adaptive_mutation_mode_boundary.json",
            "papers/mutation_operator_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Calibrate and evaluate the adaptive mutation-output policy",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "proposal-level operator-family provenance",
            },
        ),
        "validation_gate": "calibrated adaptive mode policy plus operator-family scoring/telemetry",
        "readiness_status": "adaptive_format_selection_without_calibration_or_operator_family_policy",
    },
    {
        "criterion_id": "prompt_example_copy_guard",
        "search_surface": "prompt examples and generated-payload copy diagnostics",
        "current_scope": "built-in exact/normalized/skeleton diagnostics without hard or semantic guard",
        "missing_readiness": "configurable acceptance policy, custom example inventories, and semantic renamed-copy detection",
        "roadmap_required_phrase": "concrete prompt examples",
        "current_sidecars": ("papers/prompt_example_copy_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "extend prompt-example copy evidence",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "prompt-example compatibility",
            },
        ),
        "validation_gate": "configurable semantic example-copy guard with custom prompt-template coverage",
        "readiness_status": "built_in_diagnostics_only",
    },
    {
        "criterion_id": "cross_file_mutation_consistency",
        "search_surface": "multi-edit consistency and cross-file dependency evidence",
        "current_scope": "best-effort Python AST symbol diagnostics and evaluator taxonomy",
        "missing_readiness": "language-aware scope resolution, companion-edit inference, and benchmark-calibrated gating",
        "roadmap_required_phrase": "cross-file dataflow/import resolution",
        "current_sidecars": ("papers/mutation_consistency_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "cross-file dataflow/import resolution",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "cross-file consistency benchmark evidence",
            },
        ),
        "validation_gate": "cross-file consistency benchmark with optional admission gate",
        "readiness_status": "diagnostic_python_symbol_scan_only",
    },
    {
        "criterion_id": "initial_pool_static_binary_handling",
        "search_surface": "initial-pool divergence, program output, and static/binary candidate handling",
        "current_scope": "bounded syntactic/metric initial-pool telemetry and copy-only static asset handling",
        "missing_readiness": "functional/output discovery-distance evidence and richer binary mutation/replay policy",
        "roadmap_required_phrase": "richer binary mutation/replay policy",
        "current_sidecars": (
            "papers/initial_pool_divergence_boundary.json",
            "papers/program_output_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Extend initial-pool divergence reporting",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "binary/static replay policy",
            },
        ),
        "validation_gate": "functional discovery-distance metrics plus static/binary replay policy",
        "readiness_status": "syntactic_metric_distance_and_copy_only_static_assets",
    },
    {
        "criterion_id": "workspace_source_integrity_resume",
        "search_surface": "whole-run source/workspace integrity, archive restore, and migration replay",
        "current_scope": "source/workspace payload-shape reports and snapshot restore plus audit-only archive-event reconciliation",
        "missing_readiness": "ordered migration-event replay, controller queue restore, and pending-work resume",
        "roadmap_required_phrase": "ordered migration-event replay",
        "current_sidecars": (
            "papers/whole_run_source_workspace_integrity_boundary.json",
            "papers/archive_event_replay_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Replay archive event logs as an ordered migration restore engine",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "whole-run source/workspace integrity reports",
            },
        ),
        "validation_gate": "ordered event-stream restore engine and full resume replay proof",
        "readiness_status": "snapshot_restore_and_payload_shape_only",
    },
)


@dataclass(frozen=True)
class RoadmapCandidateWorkspaceFidelityBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapCandidateWorkspaceFidelityBoundaryValidation:
    ok: bool
    boundary_status: str | None
    criterion_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapCandidateWorkspaceFidelityBoundaryIssue]


def roadmap_candidate_workspace_fidelity_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP candidate-workspace fidelity criteria map."""

    root_path = Path(root)
    roadmap_text = _read_text(root_path / "ROADMAP.md")
    records = [_criterion_record(root_path, roadmap_text, spec) for spec in CRITERION_SPECS]
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    sidecar_ref_count = sum(len(record["current_sidecar_refs"]) for record in records)
    return {
        "schema": ROADMAP_CANDIDATE_WORKSPACE_FIDELITY_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "roadmap_heading": EXPECTED_ROADMAP_HEADING,
        "roadmap_heading_present": _contains_phrase(roadmap_text, EXPECTED_ROADMAP_HEADING),
        "criterion_count": len(records),
        "active_todo_ref_count": active_todo_ref_count,
        "sidecar_ref_count": sidecar_ref_count,
        "criterion_records": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a ROADMAP-level candidate-workspace fidelity "
            "criteria map for language/build runners, candidate abstraction, "
            "marker and materialization policy, embedded evaluators, codebase "
            "scale, mutation-mode/operator provenance, prompt-example-copy "
            "guards, cross-file consistency, initial-pool/static-binary "
            "handling, and workspace resume integrity. It does not claim "
            "portable hermetic replayable build-runner evidence, flexible solution abstraction "
            "APIs, candidate-embedded evaluator contracts, realistic codebase "
            "fixtures, benchmark-calibrated adaptive mutation-mode policy, mutation-operator "
            "family provenance, semantic prompt-example-copy detection, "
            "cross-file consistency benchmark evidence, initial-pool divergence "
            "benchmark evidence, static/binary replay policy, topology resume "
            "replay proof, or owner review signoff."
        ),
    }


def validate_roadmap_candidate_workspace_fidelity_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapCandidateWorkspaceFidelityBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_candidate_workspace_fidelity_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapCandidateWorkspaceFidelityBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_candidate_workspace_fidelity_boundary_record(root)
    issues: list[RoadmapCandidateWorkspaceFidelityBoundaryIssue] = []
    if data.get("schema") != ROADMAP_CANDIDATE_WORKSPACE_FIDELITY_BOUNDARY_SCHEMA:
        issues.append(
            _issue("invalid_schema", "unsupported ROADMAP candidate-workspace fidelity boundary schema")
        )
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(
            _issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}")
        )
    if data.get("claim_ready") is not False:
        issues.append(
            _issue("claim_ready_overclaim", "ROADMAP candidate-workspace fidelity boundary must not claim full readiness")
        )
    for key in (
        "roadmap_heading",
        "roadmap_heading_present",
        "criterion_count",
        "active_todo_ref_count",
        "sidecar_ref_count",
        "criterion_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP/TODO inputs"))
    if data.get("roadmap_heading_present") is not True:
        issues.append(_issue("missing_roadmap_heading", "candidate-workspace fidelity heading was not found"))
    if data.get("criterion_count") != len(CRITERION_SPECS):
        issues.append(_issue("invalid_criterion_count", "criterion count changed"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim portable hermetic replayable build-runner evidence" not in boundary_text
        or "candidate-embedded evaluator contracts" not in boundary_text
        or "topology resume replay proof" not in boundary_text
    ):
        issues.append(
            _issue("missing_claim_boundary", "claim_boundary must separate bounded criteria from candidate-workspace readiness")
        )
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapCandidateWorkspaceFidelityBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        criterion_count=data.get("criterion_count") if isinstance(data.get("criterion_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_candidate_workspace_fidelity_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_roadmap_candidate_workspace_fidelity_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP candidate workspace fidelity boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| criterion_count | {validation.criterion_count} |",
        f"| active_todo_ref_count | {validation.active_todo_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _criterion_record(root: Path, roadmap_text: str, spec: dict[str, Any]) -> dict[str, Any]:
    todo_refs = [_local_ref_record(root, todo_ref) for todo_ref in spec["active_todos"]]
    sidecar_refs = [{"path": path, "exists": (root / path).exists()} for path in spec["current_sidecars"]]
    return {
        "criterion_id": spec["criterion_id"],
        "search_surface": spec["search_surface"],
        "current_scope": spec["current_scope"],
        "missing_readiness": spec["missing_readiness"],
        "roadmap_required_phrase": spec["roadmap_required_phrase"],
        "roadmap_phrase_present": _contains_phrase(roadmap_text, spec["roadmap_required_phrase"]),
        "current_sidecar_refs": sidecar_refs,
        "active_todo_refs": todo_refs,
        "active_todo_ref_count": len(todo_refs),
        "validation_gate": spec["validation_gate"],
        "readiness_status": spec["readiness_status"],
    }


def _local_ref_record(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = spec["path"]
    text = _read_text(root / path)
    return {
        "path": path,
        "required_phrase": spec["required_phrase"],
        "required_phrase_present": _contains_phrase(text, spec["required_phrase"]),
        "exists": (root / path).exists(),
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
) -> tuple[dict[str, Any] | None, list[RoadmapCandidateWorkspaceFidelityBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP candidate-workspace fidelity boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapCandidateWorkspaceFidelityBoundaryIssue],
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
    issues: list[RoadmapCandidateWorkspaceFidelityBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapCandidateWorkspaceFidelityBoundaryIssue:
    return RoadmapCandidateWorkspaceFidelityBoundaryIssue(code=code, message=message)
