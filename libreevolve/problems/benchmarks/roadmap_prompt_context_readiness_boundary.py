from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_prompt_context_system_boundary import (
    roadmap_prompt_context_system_boundary_record,
)


ROADMAP_PROMPT_CONTEXT_READINESS_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_prompt_context_readiness_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_prompt_context_readiness_matrix_without_full_prompt_system_gate"
)
SOURCE_PROMPT_BOUNDARY_INPUT = "papers/roadmap_prompt_context_system_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "prompt_role_capability_matrix",
    "context_selection_and_summarization",
    "all_role_token_section_packing",
    "prompt_format_and_replay_retention",
    "retrieval_and_proposal_memory_integrity",
    "meta_prompt_and_prompt_database_lifecycle",
    "prompt_context_benchmark_evidence",
    "stale_readiness_and_owner_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "prompt_role_capability_matrix": "not_recorded_locally",
    "deterministic_context_summarization": "not_recorded_locally",
    "all_role_provider_token_section_packing": "not_recorded_locally",
    "separate_prompt_format_source_provenance": "not_recorded_locally",
    "full_prompt_replay_retention_policy": "not_recorded_locally",
    "audit_grade_retrieval_source_integrity": "not_recorded_locally",
    "semantic_proposal_memory": "not_recorded_locally",
    "calibrated_meta_prompt_rewards": "not_recorded_locally",
    "prompt_database_archive_lifecycle": "not_recorded_locally",
    "prompt_context_benchmark_evidence": "not_recorded_locally",
    "stale_readiness_detector": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "prompt_role_capability_matrix",
        "prompt_surface": "mutation, critique, feedback, meta-prompt, and custom role templates",
        "current_scope": "mutation-template schema/dry-run checks and bounded role evidence",
        "missing_readiness": "prompt-role capability matrix proving role-specific template compatibility and ownership",
        "sidecars": (
            "papers/roadmap_prompt_context_system_boundary.json",
            "papers/prompt_example_copy_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "prompt-role capability matrix",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "role-specific template compatibility",
            },
        ),
        "validation_gate": "prompt-role capability matrix",
        "readiness_status": "mutation_template_evidence_without_role_matrix",
    },
    {
        "criterion_id": "context_selection_and_summarization",
        "prompt_surface": "context source selection, ranking, truncation, and summarization",
        "current_scope": "deterministic include/source provenance and first-N truncation",
        "missing_readiness": "deterministic context summarization and source-selection policy",
        "sidecars": (
            "papers/task_specification_boundary.json",
            "papers/documentation_truthfulness_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "deterministic context summarization",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "context-source selection",
            },
        ),
        "validation_gate": "context-source selection and summarization policy",
        "readiness_status": "source_provenance_without_summarization_policy",
    },
    {
        "criterion_id": "all_role_token_section_packing",
        "prompt_surface": "selected-backend token caps and all prompt-role section packing",
        "current_scope": "mutation-path section packing and role token diagnostics",
        "missing_readiness": "all-role provider-token section packing",
        "sidecars": (
            "papers/prompt_section_packing_boundary.json",
            "papers/provider_diagnostics_replay_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "all-role provider-token section packing",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "token section packing",
            },
        ),
        "validation_gate": "all-role provider-token section packing",
        "readiness_status": "mutation_packing_without_all_role_provider_tokens",
    },
    {
        "criterion_id": "prompt_format_and_replay_retention",
        "prompt_surface": "prompt-format alternatives, source provenance, retained prompts, and replay policy",
        "current_scope": "effective prompt-format distribution plus bounded retention surfaces",
        "missing_readiness": "separate prompt-format source provenance and full prompt replay-retention policy",
        "sidecars": (
            "papers/stochastic_prompt_format_boundary.json",
            "papers/runtime_rng_replay_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "separate prompt-format source provenance",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "full prompt replay-retention policy",
            },
        ),
        "validation_gate": "prompt-format source provenance and replay-retention policy",
        "readiness_status": "effective_format_and_bounded_retention_only",
    },
    {
        "criterion_id": "retrieval_and_proposal_memory_integrity",
        "prompt_surface": "retrieval sources, proposal memory, hypotheses, and failed-proposal reuse",
        "current_scope": "bounded retrieval provenance and current-run proposal reports",
        "missing_readiness": "audit-grade retrieval source integrity and semantic proposal memory",
        "sidecars": (
            "papers/deepevolve_boundary.json",
            "papers/proposal_diversity_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "audit-grade retrieval source integrity",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "semantic proposal memory",
            },
        ),
        "validation_gate": "retrieval integrity and semantic proposal-memory policy",
        "readiness_status": "bounded_retrieval_and_exact_proposal_reports",
    },
    {
        "criterion_id": "meta_prompt_and_prompt_database_lifecycle",
        "prompt_surface": "meta-prompt rewards, PromptDatabase, prompt archives, and prompt-side replay",
        "current_scope": "child-score prompt rewards and local prompt-arm database",
        "missing_readiness": "calibrated meta-prompt rewards and prompt-database archive lifecycle",
        "sidecars": (
            "papers/llm_role_scheduler_boundary.json",
            "papers/implementation_evidence_map_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "calibrated meta-prompt rewards",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "prompt-database archive lifecycle",
            },
        ),
        "validation_gate": "meta-prompt reward calibration and prompt database lifecycle",
        "readiness_status": "child_score_rewards_and_local_prompt_arm_history",
    },
    {
        "criterion_id": "prompt_context_benchmark_evidence",
        "prompt_surface": "prompt/context benchmarks, ablations, and cross-document readiness claims",
        "current_scope": "bounded sidecars without prompt/context benchmark acceptance evidence",
        "missing_readiness": "prompt/context benchmark evidence before full prompt-system readiness claims",
        "sidecars": (
            "papers/roadmap_prompt_context_system_boundary.json",
            "papers/proposal_score_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "prompt/context benchmark evidence",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "complete AlphaEvolve prompt/context readiness",
            },
        ),
        "validation_gate": "prompt/context benchmark evidence",
        "readiness_status": "sidecar_matrix_without_benchmark_acceptance",
    },
    {
        "criterion_id": "stale_readiness_and_owner_signoff",
        "prompt_surface": "README, ROADMAP, papers, generated inventories, prompt docs, and owner readiness claims",
        "current_scope": "bounded inventories and TODO ownership sidecars without owner signoff",
        "missing_readiness": "stale-readiness detector and owner signoff before prompt/context parity claims",
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
class RoadmapPromptContextReadinessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapPromptContextReadinessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readiness_criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapPromptContextReadinessBoundaryIssue]


def roadmap_prompt_context_readiness_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP prompt/context readiness matrix."""

    root_path = Path(root)
    source_boundary = roadmap_prompt_context_system_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    return {
        "schema": ROADMAP_PROMPT_CONTEXT_READINESS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_prompt_boundary_input": SOURCE_PROMPT_BOUNDARY_INPUT,
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
            "This boundary records prompt/context readiness criteria tied to "
            "the bounded prompt/context-system matrix. It does not claim a "
            "prompt-role capability matrix, deterministic context "
            "summarization, all-role provider-token section packing, separate "
            "prompt-format source provenance, full prompt replay-retention "
            "policy, audit-grade retrieval source integrity, semantic proposal "
            "memory, calibrated meta-prompt rewards, prompt-database archive "
            "lifecycle, prompt/context benchmark evidence, stale-readiness "
            "detector, or owner review signoff."
        ),
    }


def validate_roadmap_prompt_context_readiness_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapPromptContextReadinessBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_prompt_context_readiness_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapPromptContextReadinessBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_prompt_context_readiness_boundary_record(root)
    issues: list[RoadmapPromptContextReadinessBoundaryIssue] = []
    if data.get("schema") != ROADMAP_PROMPT_CONTEXT_READINESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP prompt/context readiness boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP prompt/context readiness boundary must not claim prompt-system readiness"))
    for key in (
        "source_prompt_boundary_input",
        "source_criterion_count",
        "source_active_todo_ref_count",
        "source_sidecar_ref_count",
        "readiness_criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "readiness_criteria",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP prompt/context inputs"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a prompt-role capability matrix" not in boundary_text
        or "deterministic context summarization" not in boundary_text
        or "prompt/context benchmark evidence" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate readiness matrix from prompt/context parity"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapPromptContextReadinessBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readiness_criterion_count=data.get("readiness_criterion_count") if isinstance(data.get("readiness_criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_prompt_context_readiness_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_prompt_context_readiness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP prompt context readiness boundary",
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
        "prompt_surface": spec["prompt_surface"],
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
) -> tuple[dict[str, Any] | None, list[RoadmapPromptContextReadinessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP prompt/context readiness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapPromptContextReadinessBoundaryIssue],
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
    issues: list[RoadmapPromptContextReadinessBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapPromptContextReadinessBoundaryIssue:
    return RoadmapPromptContextReadinessBoundaryIssue(code=code, message=message)
