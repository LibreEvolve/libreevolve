from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_EVALUATION_CASCADE_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_evaluation_cascade_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_evaluation_cascade_matrix_without_alphaevolve_cascade_readiness"
)
EXPECTED_ROADMAP_HEADING = "### 3. Expand evaluation cascades"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "criterion_records",
    "roadmap_section_presence",
    "validator_authority_matrix",
    "artifact_schema_hash_policy",
    "budget_ownership_policy",
    "feedback_calibration_policy",
    "statistical_promotion_policy",
    "oracle_independence_policy",
    "workload_execution_contract",
    "automated_environment_scope_policy",
    "sandbox_dependency_policy",
    "environment_release_reproducibility_policy",
    "benchmark_sufficiency_policy",
    "stale_readiness_detector",
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
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "cascade_transition_artifacts",
        "evaluation_surface": "configured validator stages and candidate promotion/prune flow",
        "current_scope": "runtime cascade summary with bounded candidate-stage records and absent-evidence labels",
        "missing_readiness": "candidate transition matrix, promotion/prune attribution, next-stage linkage, denominator reconciliation, and cost-savings proof",
        "roadmap_required_phrase": "candidate transition matrices",
        "current_sidecars": ("papers/evaluation_cascade_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Finish paper-facing evaluation-cascade promotion and attrition evidence.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Track evaluation-cascade promotion and attrition evidence.",
            },
        ),
        "validation_gate": "candidate transition matrix and promotion/prune proof",
        "readiness_status": "summary_without_transition_matrix",
    },
    {
        "criterion_id": "artifact_schema_hash_coverage",
        "evaluation_surface": "candidate, evaluator, and benchmark artifacts",
        "current_scope": "candidate-workspace artifact copy-out and selected hashed sidecars",
        "missing_readiness": "outside-workspace artifacts, aggregate emitted-artifact hashes, and benchmark artifact schemas",
        "roadmap_required_phrase": "outside-workspace artifacts",
        "current_sidecars": (
            "papers/evaluation_cascade_boundary.json",
            "papers/validator_artifact_promotion_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Bind evaluator artifact copy-out to stable source-file identity.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Track evaluation-cascade promotion and attrition evidence.",
            },
        ),
        "validation_gate": "stable artifact schemas and hash coverage for cascade decisions",
        "readiness_status": "bounded_copy_out_without_complete_schema",
    },
    {
        "criterion_id": "budget_ownership",
        "evaluation_surface": "generation, evaluator, provider, worker, and accelerator budgets",
        "current_scope": "cooperative local counters plus LLM budget snapshots",
        "missing_readiness": "compute-hour, worker/accelerator lease, async queue, partial-evaluation resume, and equal-budget accounting",
        "roadmap_required_phrase": "accelerator and async queue budgets",
        "current_sidecars": (
            "papers/expensive_evaluation_budget_boundary.json",
            "papers/llm_budget_policy_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add unified expensive-evaluation compute budgets and resumable state.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Complete accelerator/async budgets and executed ablation support.",
            },
        ),
        "validation_gate": "first-class async/accelerator/equal-budget enforcement",
        "readiness_status": "local_cooperative_budget_only",
    },
    {
        "criterion_id": "feedback_calibration",
        "evaluation_surface": "LLM feedback graders and qualitative criteria",
        "current_scope": "report contracts and declared qualitative policy metadata",
        "missing_readiness": "executed calibration task suites, grader ablations, and independent feedback-quality validation",
        "roadmap_required_phrase": "calibration/ablation runs for LLM feedback graders",
        "current_sidecars": (
            "papers/feedback_calibration_boundary.json",
            "papers/qualitative_feedback_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add qualitative LLM-feedback criterion provenance.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Track qualitative LLM-feedback criterion provenance.",
            },
        ),
        "validation_gate": "executed feedback calibration and ablation evidence",
        "readiness_status": "declared_policy_without_executed_calibration",
    },
    {
        "criterion_id": "statistical_promotion_policy",
        "evaluation_surface": "hypothesis-test gates and repeated-seed promotions",
        "current_scope": "configured lower-bound and binomial gates with runtime diagnostics",
        "missing_readiness": "benchmark-calibrated thresholds and repeated-seed matrix/tensor fixtures",
        "roadmap_required_phrase": "broader statistical hypothesis-test promotion policies",
        "current_sidecars": ("papers/cascade_hypothesis_test_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add statistical hypothesis-test gates to evaluation cascades.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Track statistical hypothesis-testing semantics for evaluation cascades.",
            },
        ),
        "validation_gate": "benchmark-calibrated promotion/rejection fixtures",
        "readiness_status": "configured_policy_gate_without_benchmark_calibration",
    },
    {
        "criterion_id": "oracle_independence",
        "evaluation_surface": "evaluator/oracle registry and cross-oracle disagreement",
        "current_scope": "local arbitration matrix plus optional synchronous feedback graders",
        "missing_readiness": "independent reference/statistical oracles and cross-oracle disagreement records",
        "roadmap_required_phrase": "evaluator/oracle registry",
        "current_sidecars": ("papers/evaluator_oracle_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "runtime.history.evaluator_oracle_registry",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "runtime.history.evaluator_oracle_registry",
            },
        ),
        "validation_gate": "independent oracle and disagreement-outcome evidence",
        "readiness_status": "local_arbitration_without_independent_oracles",
    },
    {
        "criterion_id": "workload_execution_contract",
        "evaluation_surface": "inner-search, ML-training, and custom evaluator workloads",
        "current_scope": "declared workload metadata and observed artifact/checkpoint evidence",
        "missing_readiness": "managed loop runners, checkpoint completeness checks, score-field causality, and stochastic re-evaluation policy",
        "roadmap_required_phrase": "evaluator-workload provenance",
        "current_sidecars": (
            "papers/task_specification_boundary.json",
            "papers/automated_evaluator_scope_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add evaluator workload provenance for inner search and ML-training tasks.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Track evaluator workload provenance for inner-search and ML-training",
            },
        ),
        "validation_gate": "workload-specific runner and checkpoint contract",
        "readiness_status": "declared_workload_metadata_only",
    },
    {
        "criterion_id": "automated_scope_programmatic_boundary",
        "evaluation_surface": "automated evaluator scope and executable-code versus NL hypothesis boundary",
        "current_scope": "machine-feedback/manual-experiment/LLM-feedback classification plus structural code-vs-NL reports",
        "missing_readiness": "robust environment fixtures, manual-to-code transition criteria, hallucination controls, and long-horizon evidence",
        "roadmap_required_phrase": "automated_evaluator_scope_report",
        "current_sidecars": (
            "papers/automated_evaluator_scope_boundary.json",
            "papers/programmatic_representation_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Extend automated-evaluator scope policy into robust environment fixtures.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Extend AlphaEvolve's automated-evaluator scope boundary into robust",
            },
        ),
        "validation_gate": "automated environment fixtures and NL-to-code boundary evidence",
        "readiness_status": "classification_without_robust_environment",
    },
    {
        "criterion_id": "validator_sandbox_dependency_boundary",
        "evaluation_surface": "validator subprocesses, filesystem/network access, and dependencies",
        "current_scope": "local subprocess policy, environment allowlisting, timeout cleanup, and problem-local dependency provenance",
        "missing_readiness": "OS/container sandboxing, CPU/memory/GPU/disk/process quotas, and promotion-time archival blocking",
        "roadmap_required_phrase": "OS/container-grade validator network isolation",
        "current_sidecars": ("papers/validator_execution_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Enforce validator container, filesystem-capability, and resource-limit policy.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Extend paper-facing validator-boundary consistency evidence beyond CLI",
            },
        ),
        "validation_gate": "container/resource sandbox and promotion-gate evidence",
        "readiness_status": "local_subprocess_policy_only",
    },
    {
        "criterion_id": "environment_release_reproducibility",
        "evaluation_surface": "release artifacts, packages, external build state, and accelerator environment",
        "current_scope": "CI-smoke release packaging and bounded package/version snapshots",
        "missing_readiness": "signed release provenance, install-source semantics, external build/package-source records, accelerator lease state, and replay checks",
        "roadmap_required_phrase": "release-artifact smoke CI jobs",
        "current_sidecars": (
            "papers/release_artifact_reproducibility_boundary.json",
            "papers/config_validation_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add release artifact and install-from-wheel verification.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Add replayable evaluator environment, package-source, and accelerator",
            },
        ),
        "validation_gate": "release/environment replay bundle with accelerator/package provenance",
        "readiness_status": "ci_smoke_and_bounded_environment_only",
    },
)


@dataclass(frozen=True)
class RoadmapEvaluationCascadeBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapEvaluationCascadeBoundaryValidation:
    ok: bool
    boundary_status: str | None
    criterion_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapEvaluationCascadeBoundaryIssue]


def roadmap_evaluation_cascade_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP evaluation-cascade criteria map."""

    root_path = Path(root)
    roadmap_text = _read_text(root_path / "ROADMAP.md")
    records = [_criterion_record(root_path, roadmap_text, spec) for spec in CRITERION_SPECS]
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    sidecar_ref_count = sum(len(record["current_sidecar_refs"]) for record in records)
    return {
        "schema": ROADMAP_EVALUATION_CASCADE_BOUNDARY_SCHEMA,
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
            "This boundary records a ROADMAP-level evaluation-cascade criteria "
            "map for cascade transitions, artifact schemas, budget ownership, "
            "feedback calibration, statistical promotion, oracle independence, "
            "workload contracts, automated evaluator scope, validator sandbox "
            "boundaries, and release/environment reproducibility. It does not "
            "claim a validator-authority matrix, complete artifact schema/hash "
            "coverage, accelerator or async budget ownership, executed feedback "
            "calibration, benchmark-calibrated statistical promotion, "
            "independent oracle disagreement records, workload-specific "
            "execution contracts, robust automated environment fixtures, "
            "OS/container resource sandboxing, replayable environment/release "
            "bundles, benchmark sufficiency signoff, or owner review signoff."
        ),
    }


def validate_roadmap_evaluation_cascade_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapEvaluationCascadeBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_evaluation_cascade_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return RoadmapEvaluationCascadeBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = roadmap_evaluation_cascade_boundary_record(root)
    issues: list[RoadmapEvaluationCascadeBoundaryIssue] = []
    if data.get("schema") != ROADMAP_EVALUATION_CASCADE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP evaluation-cascade boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP evaluation-cascade boundary must not claim full readiness"))
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
        issues.append(_issue("missing_roadmap_heading", "evaluation cascades heading was not found"))
    if data.get("criterion_count") != len(CRITERION_SPECS):
        issues.append(_issue("invalid_criterion_count", "criterion count changed"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a validator-authority matrix" not in boundary_text
        or "benchmark-calibrated statistical promotion" not in boundary_text
        or "OS/container resource sandboxing" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded criteria from cascade readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapEvaluationCascadeBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        criterion_count=data.get("criterion_count") if isinstance(data.get("criterion_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_evaluation_cascade_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_roadmap_evaluation_cascade_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP evaluation cascade boundary",
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
        "evaluation_surface": spec["evaluation_surface"],
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
) -> tuple[dict[str, Any] | None, list[RoadmapEvaluationCascadeBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP evaluation-cascade boundary must be a JSON object")]


def _validate_required_fields(value: object, issues: list[RoadmapEvaluationCascadeBoundaryIssue]) -> int:
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


def _validate_missing_evidence(value: object, issues: list[RoadmapEvaluationCascadeBoundaryIssue]) -> int:
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


def _issue(code: str, message: str) -> RoadmapEvaluationCascadeBoundaryIssue:
    return RoadmapEvaluationCascadeBoundaryIssue(code=code, message=message)
