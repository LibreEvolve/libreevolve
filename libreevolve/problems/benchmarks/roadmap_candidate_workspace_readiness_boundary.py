from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_candidate_workspace_fidelity_boundary import (
    roadmap_candidate_workspace_fidelity_boundary_record,
)


ROADMAP_CANDIDATE_WORKSPACE_READINESS_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_candidate_workspace_readiness_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_candidate_workspace_readiness_matrix_without_alphaevolve_workspace_gate"
)
SOURCE_CANDIDATE_WORKSPACE_BOUNDARY_INPUT = (
    "papers/roadmap_candidate_workspace_fidelity_boundary.json"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "language_build_and_candidate_api",
    "embedded_evaluator_and_codebase_scale",
    "materialization_marker_and_topology",
    "mutation_mode_operator_provenance",
    "prompt_copy_and_cross_file_consistency",
    "initial_pool_static_binary_policy",
    "resume_replay_and_manifest_policy",
    "stale_readiness_and_owner_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "portable_hermetic_replayable_build_runner_evidence": (
        "host_c_and_single_digest_pinned_oci_smoke_recorded_broad_portable_replay_not_recorded"
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
    "stale_readiness_detector": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "language_build_and_candidate_api",
        "search_surface": "language/build runner contracts and problem-defined candidate abstraction APIs",
        "current_scope": "task-primary local expression, host C, and single digest-pinned OCI Python build/runner execution plus code-file-set abstraction without broad portable toolchain parity",
        "missing_readiness": "multi-platform package-restoring deterministic replay plus flexible solution abstraction API evidence",
        "sidecars": (
            "papers/candidate_language_runner_boundary.json",
            "papers/candidate_abstraction_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "portable hermetic and broader language/build runners",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "flexible solution abstraction API",
            },
        ),
        "validation_gate": "broad portable-toolchain runner and candidate abstraction readiness gate",
        "readiness_status": "host_and_single_digest_pinned_oci_runner_without_broad_portable_toolchain_gate",
    },
    {
        "criterion_id": "embedded_evaluator_and_codebase_scale",
        "search_surface": "candidate-owned evaluator contracts and realistic codebase-scale fixtures",
        "current_scope": "external validator contract, embedded-evaluator absence boundary, and smoke fixtures",
        "missing_readiness": "candidate-embedded evaluator contracts with realistic codebase fixtures",
        "sidecars": (
            "papers/embedded_evaluator_boundary.json",
            "papers/codebase_scale_benchmark_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "candidate-embedded evaluator contracts",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "realistic codebase fixtures",
            },
        ),
        "validation_gate": "embedded evaluator and codebase-scale fixture readiness gate",
        "readiness_status": "external_validator_and_smoke_fixture_only",
    },
    {
        "criterion_id": "materialization_marker_and_topology",
        "search_surface": "marker materialization, workspace topology diagnostics, and source/workspace integrity",
        "current_scope": "Python evolve-block handling, bounded topology diagnostics, and payload-shape integrity reports",
        "missing_readiness": "topology diagnostics that prove candidate workspace materialization and resume fidelity",
        "sidecars": (
            "papers/workspace_materialization_boundary.json",
            "papers/whole_run_source_workspace_integrity_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "topology diagnostics",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "topology resume replay proof",
            },
        ),
        "validation_gate": "workspace materialization and topology replay readiness gate",
        "readiness_status": "bounded_topology_diagnostics_without_replay_proof",
    },
    {
        "criterion_id": "mutation_mode_operator_provenance",
        "search_surface": "adaptive mutation mode selection and operator-family provenance",
        "current_scope": "per-candidate adaptive diff-full format selection plus fixed parser surfaces",
        "missing_readiness": "benchmark-calibrated adaptive mutation-mode policy with proposal-level operator-family provenance",
        "sidecars": (
            "papers/adaptive_mutation_mode_boundary.json",
            "papers/mutation_operator_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "benchmark-calibrated adaptive mutation-mode policy",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "mutation-operator family provenance",
            },
        ),
        "validation_gate": "calibrated adaptive mutation and operator provenance readiness gate",
        "readiness_status": "adaptive_format_selection_without_calibrated_operator_policy",
    },
    {
        "criterion_id": "prompt_copy_and_cross_file_consistency",
        "search_surface": "prompt-example copy detection and cross-file mutation consistency",
        "current_scope": "built-in copy diagnostics and best-effort Python AST symbol reports",
        "missing_readiness": "semantic prompt-example-copy detection and benchmarked cross-file consistency evidence",
        "sidecars": (
            "papers/prompt_example_copy_boundary.json",
            "papers/mutation_consistency_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "semantic prompt-example-copy detection",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "cross-file consistency benchmark evidence",
            },
        ),
        "validation_gate": "semantic copy and cross-file consistency readiness gate",
        "readiness_status": "diagnostic_reports_without_semantic_or_benchmark_gate",
    },
    {
        "criterion_id": "initial_pool_static_binary_policy",
        "search_surface": "initial-pool divergence, program output discovery distance, and static/binary candidates",
        "current_scope": "bounded syntactic/metric initial-pool telemetry and copy-only static asset handling",
        "missing_readiness": "initial-pool divergence benchmark evidence plus static/binary replay policy",
        "sidecars": (
            "papers/initial_pool_divergence_boundary.json",
            "papers/program_output_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "initial-pool divergence benchmark evidence",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "static/binary replay policy",
            },
        ),
        "validation_gate": "initial-pool and static/binary replay readiness gate",
        "readiness_status": "syntactic_pool_distance_and_copy_only_assets",
    },
    {
        "criterion_id": "resume_replay_and_manifest_policy",
        "search_surface": "archive-event replay, pending-work resume, run manifests, and workspace docs",
        "current_scope": "snapshot restore and audit-only archive-event reconciliation without full resume proof",
        "missing_readiness": "run-manifest and workspace-doc checks that prove replayable candidate-workspace resume semantics",
        "sidecars": (
            "papers/archive_event_replay_boundary.json",
            "papers/controller_pending_work_resume_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "run manifests",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "workspace docs",
            },
        ),
        "validation_gate": "resume replay, run-manifest, and workspace-doc readiness gate",
        "readiness_status": "snapshot_restore_without_full_resume_replay_gate",
    },
    {
        "criterion_id": "stale_readiness_and_owner_signoff",
        "search_surface": "README, ROADMAP, papers, run manifests, workspace docs, and owner readiness claims",
        "current_scope": "bounded inventories and TODO ownership sidecars without owner signoff",
        "missing_readiness": "stale-readiness detector and owner signoff before candidate-workspace fidelity claims",
        "sidecars": (
            "papers/documentation_claim_inventory.json",
            "papers/todo_ledger_ownership_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "stale-readiness detector",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "owner review signoff",
            },
        ),
        "validation_gate": "stale-readiness detector and owner signoff",
        "readiness_status": "inventory_without_readiness_signoff",
    },
)


@dataclass(frozen=True)
class RoadmapCandidateWorkspaceReadinessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapCandidateWorkspaceReadinessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readiness_criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapCandidateWorkspaceReadinessBoundaryIssue]


def roadmap_candidate_workspace_readiness_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP candidate-workspace readiness matrix."""

    root_path = Path(root)
    source_boundary = roadmap_candidate_workspace_fidelity_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    claim_guard = [_claim_guard_record(record) for record in records]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    return {
        "schema": ROADMAP_CANDIDATE_WORKSPACE_READINESS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_candidate_workspace_boundary_input": SOURCE_CANDIDATE_WORKSPACE_BOUNDARY_INPUT,
        "source_criterion_count": source_boundary["criterion_count"],
        "source_active_todo_ref_count": source_boundary["active_todo_ref_count"],
        "source_sidecar_ref_count": source_boundary["sidecar_ref_count"],
        "source_missing_evidence_count": len(source_boundary["missing_evidence"]),
        "readiness_criterion_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "readiness_criteria": records,
        "candidate_workspace_claim_guard": claim_guard,
        "candidate_workspace_claim_guard_count": len(claim_guard),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records candidate-workspace readiness criteria tied "
            "to the bounded candidate-workspace fidelity matrix, plus a claim "
            "guard for each workspace surface. It does not claim portable hermetic "
            "replayable build-runner evidence, flexible solution abstraction API, "
            "candidate-embedded evaluator contracts, realistic codebase "
            "fixtures, benchmark-calibrated adaptive mutation-mode policy, mutation-operator "
            "family provenance, semantic prompt-example-copy detection, "
            "cross-file consistency benchmark evidence, initial-pool "
            "divergence benchmark evidence, static/binary replay policy, "
            "topology resume replay proof, stale-readiness detector, or owner "
            "review signoff."
        ),
    }


def validate_roadmap_candidate_workspace_readiness_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapCandidateWorkspaceReadinessBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_candidate_workspace_readiness_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapCandidateWorkspaceReadinessBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_candidate_workspace_readiness_boundary_record(root)
    issues: list[RoadmapCandidateWorkspaceReadinessBoundaryIssue] = []
    if data.get("schema") != ROADMAP_CANDIDATE_WORKSPACE_READINESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP candidate-workspace readiness boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP candidate-workspace readiness boundary must not claim AlphaEvolve workspace readiness"))
    for key in (
        "source_candidate_workspace_boundary_input",
        "source_criterion_count",
        "source_active_todo_ref_count",
        "source_sidecar_ref_count",
        "source_missing_evidence_count",
        "readiness_criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "readiness_criteria",
        "candidate_workspace_claim_guard",
        "candidate_workspace_claim_guard_count",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP candidate-workspace inputs"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim portable hermetic replayable build-runner evidence" not in boundary_text
        or "claim guard for each workspace surface" not in boundary_text
        or "topology resume replay proof" not in boundary_text
        or "stale-readiness detector" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate readiness matrix from candidate-workspace fidelity"))
    if data.get("candidate_workspace_claim_guard_count") != len(CRITERION_SPECS):
        issues.append(_issue("invalid_candidate_workspace_claim_guard_count", "candidate-workspace claim guard count changed"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapCandidateWorkspaceReadinessBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readiness_criterion_count=data.get("readiness_criterion_count") if isinstance(data.get("readiness_criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_candidate_workspace_readiness_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_candidate_workspace_readiness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP candidate workspace readiness boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| readiness_criterion_count | {validation.readiness_criterion_count} |",
        f"| sidecar_ref_count | {validation.sidecar_ref_count} |",
        f"| active_todo_ref_count | {validation.active_todo_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _criterion_record(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "criterion_id": spec["criterion_id"],
        "search_surface": spec["search_surface"],
        "current_scope": spec["current_scope"],
        "missing_readiness": spec["missing_readiness"],
        "sidecar_refs": [_sidecar_ref(root, path) for path in spec["sidecars"]],
        "active_todo_refs": [
            _active_todo_ref(root, todo) for todo in spec["active_todos"]
        ],
        "validation_gate": spec["validation_gate"],
        "readiness_status": spec["readiness_status"],
    }


def _claim_guard_record(record: dict[str, Any]) -> dict[str, str]:
    return {
        "criterion_id": record["criterion_id"],
        "search_surface": record["search_surface"],
        "allowed_current_claim": record["current_scope"],
        "missing_before_parity_claim": record["missing_readiness"],
        "validation_gate": record["validation_gate"],
        "readiness_status": record["readiness_status"],
    }


def _sidecar_ref(root: Path, path: str) -> dict[str, Any]:
    return {"path": path, "exists": (root / path).exists()}


def _active_todo_ref(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = spec["path"]
    required_phrase = spec["required_phrase"]
    text = _read_text(root / path)
    return {
        "path": path,
        "required_phrase": required_phrase,
        "required_phrase_present": _contains_phrase(text, required_phrase),
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
) -> tuple[dict[str, Any] | None, list[RoadmapCandidateWorkspaceReadinessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP candidate-workspace readiness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapCandidateWorkspaceReadinessBoundaryIssue],
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
    issues: list[RoadmapCandidateWorkspaceReadinessBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapCandidateWorkspaceReadinessBoundaryIssue:
    return RoadmapCandidateWorkspaceReadinessBoundaryIssue(code=code, message=message)
