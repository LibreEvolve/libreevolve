from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_evaluation_cascade_boundary import (
    roadmap_evaluation_cascade_boundary_record,
)


ROADMAP_EVALUATION_CASCADE_READINESS_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_evaluation_cascade_readiness_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_evaluation_cascade_readiness_matrix_without_alphaevolve_cascade_gate"
)
SOURCE_CASCADE_BOUNDARY_INPUT = "papers/roadmap_evaluation_cascade_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "validator_authority_matrix",
    "artifact_and_budget_sufficiency",
    "feedback_and_statistical_promotion",
    "oracle_and_workload_contracts",
    "automated_environment_and_sandbox",
    "release_environment_reproducibility",
    "benchmark_sufficiency_signoff",
    "stale_readiness_and_owner_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "validator_authority_matrix": "not_recorded_locally",
    "complete_artifact_schema_hash_coverage": "not_recorded_locally",
    "accelerator_async_budget_ownership": "not_recorded_locally",
    "executed_feedback_calibration": "not_recorded_locally",
    "benchmark_calibrated_statistical_promotion": "not_recorded_locally",
    "independent_oracle_disagreement_records": "not_recorded_locally",
    "workload_specific_execution_contracts": "not_recorded_locally",
    "robust_automated_environment_fixtures": "not_recorded_locally",
    "os_container_resource_sandbox": "not_recorded_locally",
    "replayable_environment_release_bundle": "not_recorded_locally",
    "benchmark_sufficiency_signoff": "not_recorded_locally",
    "stale_readiness_detector": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "validator_authority_matrix",
        "cascade_surface": "validator authority, transition records, and promotion/prune decisions",
        "current_scope": "bounded cascade-transition and validator-artifact sidecars",
        "missing_readiness": "validator-authority matrix proving which evaluator can promote, reject, quarantine, or trigger further stages",
        "sidecars": (
            "papers/roadmap_evaluation_cascade_boundary.json",
            "papers/evaluation_cascade_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "validator-authority matrix",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "evaluator/oracle capability matrix",
            },
        ),
        "validation_gate": "validator authority and transition matrix",
        "readiness_status": "transition_sidecars_without_authority_matrix",
    },
    {
        "criterion_id": "artifact_and_budget_sufficiency",
        "cascade_surface": "candidate artifacts, evaluator artifacts, hashes, schemas, and budgets",
        "current_scope": "candidate artifact copy-out, selected sidecar hashes, and cooperative local budgets",
        "missing_readiness": "complete artifact schema/hash coverage and accelerator/async budget ownership",
        "sidecars": (
            "papers/validator_artifact_promotion_boundary.json",
            "papers/expensive_evaluation_budget_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "artifact-and-budget sufficiency checklist",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "accelerator/async budget ownership",
            },
        ),
        "validation_gate": "artifact/hash schema and budget sufficiency checklist",
        "readiness_status": "bounded_artifacts_and_local_budgets_only",
    },
    {
        "criterion_id": "feedback_and_statistical_promotion",
        "cascade_surface": "LLM feedback calibration, qualitative policy, and statistical promotion gates",
        "current_scope": "feedback report contracts, qualitative metadata, and configured statistical gates",
        "missing_readiness": "executed feedback calibration and benchmark-calibrated statistical promotion",
        "sidecars": (
            "papers/feedback_calibration_boundary.json",
            "papers/cascade_hypothesis_test_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "executed feedback calibration",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "benchmark-calibrated statistical promotion",
            },
        ),
        "validation_gate": "executed feedback calibration and benchmark-calibrated promotion",
        "readiness_status": "declared_feedback_and_policy_gates_without_calibration",
    },
    {
        "criterion_id": "oracle_and_workload_contracts",
        "cascade_surface": "independent oracles, disagreement records, and workload-specific evaluator contracts",
        "current_scope": "local arbitration matrix and declared workload metadata",
        "missing_readiness": "independent oracle disagreement records and workload-specific execution contracts",
        "sidecars": (
            "papers/evaluator_oracle_boundary.json",
            "papers/task_specification_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "independent oracle disagreement records",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "workload-specific execution contracts",
            },
        ),
        "validation_gate": "oracle disagreement and workload execution contracts",
        "readiness_status": "local_arbitration_and_declared_workload_metadata",
    },
    {
        "criterion_id": "automated_environment_and_sandbox",
        "cascade_surface": "automated evaluator fixtures, programmatic boundaries, validator subprocesses, and resource isolation",
        "current_scope": "scope classification, code-vs-NL reports, local subprocess policy, and dependency provenance",
        "missing_readiness": "robust automated environment fixtures and OS/container resource sandbox",
        "sidecars": (
            "papers/automated_evaluator_scope_boundary.json",
            "papers/validator_execution_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "robust automated environment fixtures",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "OS/container resource sandbox",
            },
        ),
        "validation_gate": "automated environment fixtures and OS/container resource sandbox",
        "readiness_status": "classification_and_subprocess_policy_only",
    },
    {
        "criterion_id": "release_environment_reproducibility",
        "cascade_surface": "release artifacts, config validation, package/version snapshots, and evaluator environment replay",
        "current_scope": "CI-smoke release packaging and bounded config/environment sidecars",
        "missing_readiness": "replayable environment/release bundle",
        "sidecars": (
            "papers/release_artifact_reproducibility_boundary.json",
            "papers/config_validation_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "replayable environment/release bundle",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "release artifacts",
            },
        ),
        "validation_gate": "replayable release and evaluator-environment bundle",
        "readiness_status": "ci_smoke_without_replayable_environment_bundle",
    },
    {
        "criterion_id": "benchmark_sufficiency_signoff",
        "cascade_surface": "benchmark cascade runs, matrix/tensor fixtures, workload-specific provenance, and sufficiency claims",
        "current_scope": "bounded benchmark sidecars without cascade-readiness signoff",
        "missing_readiness": "benchmark-sufficiency signoff proving cascade readiness across target workloads",
        "sidecars": (
            "papers/evaluation_cascade_boundary.json",
            "papers/programmatic_representation_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "benchmark-sufficiency signoff",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "matrix cascade runs",
            },
        ),
        "validation_gate": "benchmark-sufficiency signoff for cascade readiness",
        "readiness_status": "bounded_reports_without_benchmark_signoff",
    },
    {
        "criterion_id": "stale_readiness_and_owner_signoff",
        "cascade_surface": "README, ROADMAP, papers, evaluator docs, runtime metadata, and owner readiness claims",
        "current_scope": "bounded inventories and TODO ownership sidecars without owner signoff",
        "missing_readiness": "stale-readiness detector and owner signoff before cascade parity claims",
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
class RoadmapEvaluationCascadeReadinessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapEvaluationCascadeReadinessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readiness_criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapEvaluationCascadeReadinessBoundaryIssue]


def roadmap_evaluation_cascade_readiness_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP evaluation-cascade readiness matrix."""

    root_path = Path(root)
    source_boundary = roadmap_evaluation_cascade_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    return {
        "schema": ROADMAP_EVALUATION_CASCADE_READINESS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_cascade_boundary_input": SOURCE_CASCADE_BOUNDARY_INPUT,
        "source_criterion_count": source_boundary["criterion_count"],
        "source_active_todo_ref_count": source_boundary["active_todo_ref_count"],
        "source_sidecar_ref_count": source_boundary["sidecar_ref_count"],
        "readiness_criterion_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "readiness_criteria": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records evaluation-cascade readiness criteria tied "
            "to the bounded evaluation-cascade matrix. It does not claim a "
            "validator-authority matrix, complete artifact schema/hash "
            "coverage, accelerator/async budget ownership, executed feedback "
            "calibration, benchmark-calibrated statistical promotion, "
            "independent oracle disagreement records, workload-specific "
            "execution contracts, robust automated environment fixtures, "
            "OS/container resource sandbox, replayable environment/release "
            "bundle, benchmark-sufficiency signoff, stale-readiness detector, "
            "or owner review signoff."
        ),
    }


def validate_roadmap_evaluation_cascade_readiness_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapEvaluationCascadeReadinessBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_evaluation_cascade_readiness_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapEvaluationCascadeReadinessBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_evaluation_cascade_readiness_boundary_record(root)
    issues: list[RoadmapEvaluationCascadeReadinessBoundaryIssue] = []
    if data.get("schema") != ROADMAP_EVALUATION_CASCADE_READINESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP evaluation-cascade readiness boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP evaluation-cascade readiness boundary must not claim cascade readiness"))
    for key in (
        "source_cascade_boundary_input",
        "source_criterion_count",
        "source_active_todo_ref_count",
        "source_sidecar_ref_count",
        "readiness_criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "readiness_criteria",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP evaluation-cascade inputs"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a validator-authority matrix" not in boundary_text
        or "benchmark-calibrated statistical promotion" not in boundary_text
        or "benchmark-sufficiency signoff" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate readiness matrix from cascade parity"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapEvaluationCascadeReadinessBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readiness_criterion_count=data.get("readiness_criterion_count") if isinstance(data.get("readiness_criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_evaluation_cascade_readiness_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_evaluation_cascade_readiness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP evaluation cascade readiness boundary",
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
        "cascade_surface": spec["cascade_surface"],
        "current_scope": spec["current_scope"],
        "missing_readiness": spec["missing_readiness"],
        "sidecar_refs": [_sidecar_ref(root, path) for path in spec["sidecars"]],
        "active_todo_refs": [
            _active_todo_ref(root, todo) for todo in spec["active_todos"]
        ],
        "validation_gate": spec["validation_gate"],
        "readiness_status": spec["readiness_status"],
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
) -> tuple[dict[str, Any] | None, list[RoadmapEvaluationCascadeReadinessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP evaluation-cascade readiness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapEvaluationCascadeReadinessBoundaryIssue],
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
    issues: list[RoadmapEvaluationCascadeReadinessBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapEvaluationCascadeReadinessBoundaryIssue:
    return RoadmapEvaluationCascadeReadinessBoundaryIssue(code=code, message=message)
