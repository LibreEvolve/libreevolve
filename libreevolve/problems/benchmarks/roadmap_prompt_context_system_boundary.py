from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_PROMPT_CONTEXT_SYSTEM_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_prompt_context_system_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_prompt_context_system_matrix_without_full_prompt_system_readiness"
)
EXPECTED_ROADMAP_HEADING = "### 4. Prompt and context work"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "criterion_records",
    "roadmap_section_presence",
    "prompt_role_capability_matrix",
    "context_source_selection_policy",
    "token_counter_authority_policy",
    "section_packing_coverage_policy",
    "retention_replay_policy",
    "retrieval_provenance_policy",
    "proposal_memory_semantics",
    "meta_prompt_reward_policy",
    "prompt_database_lifecycle_policy",
    "benchmark_evidence_policy",
    "stale_readiness_detector",
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
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "role_template_compatibility",
        "prompt_surface": "mutation, critique, feedback, and meta-prompt templates",
        "current_scope": "schema/dry-run mutation-template checks plus parent-placeholder retention",
        "missing_readiness": "role-specific compatibility policies and custom template inventories",
        "roadmap_required_phrase": "role-specific compatibility policies",
        "current_sidecars": (
            "papers/prompt_example_copy_boundary.json",
            "papers/figure3_supervised_exhibit_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Extend prompt-template compatibility beyond current mutation-template",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Extend prompt-template compatibility evidence beyond mutation-template",
            },
        ),
        "validation_gate": "role-specific prompt-template compatibility matrix",
        "readiness_status": "mutation_template_only",
    },
    {
        "criterion_id": "context_source_selection",
        "prompt_surface": "local PDFs, extracted text, files, and explicit context",
        "current_scope": "first-N truncation and deterministic include/source provenance",
        "missing_readiness": "deterministic summarization/ranking and semantic source selection",
        "roadmap_required_phrase": "deterministic summarization/ranking",
        "current_sidecars": (
            "papers/task_specification_boundary.json",
            "papers/documentation_truthfulness_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "deterministic context summarization",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "retrieval/summarization policy",
            },
        ),
        "validation_gate": "source-selection and summarization policy artifacts",
        "readiness_status": "deterministic_inclusion_without_summarization",
    },
    {
        "criterion_id": "token_section_packing",
        "prompt_surface": "prompt caps, context windows, and section priority packing",
        "current_scope": "mutation-path section packing plus final-prompt role token diagnostics",
        "missing_readiness": "selected-backend provider-token section packing across all prompt roles",
        "roadmap_required_phrase": "selected-backend provider-token section packing across all prompt roles",
        "current_sidecars": ("papers/prompt_section_packing_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Complete provider-token prompt section fitting beyond mutation prompts",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Complete full validator-metadata rendering and provider-token prompt",
            },
        ),
        "validation_gate": "all-role selected-backend exact token packing",
        "readiness_status": "mutation_section_packing_boundary",
    },
    {
        "criterion_id": "stochastic_prompt_format_provenance",
        "prompt_surface": "configured prompt-format alternatives and weights",
        "current_scope": "effective-config distribution and selected alternative hashes",
        "missing_readiness": "separate source-file attribution, author/reviewer metadata, and revision history",
        "roadmap_required_phrase": "separate source-file attribution",
        "current_sidecars": ("papers/stochastic_prompt_format_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add separate-source provenance for stochastic prompt-format",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Track stochastic prompt-format separate config-file provenance",
            },
        ),
        "validation_gate": "separate prompt-format source provenance",
        "readiness_status": "effective_config_distribution_only",
    },
    {
        "criterion_id": "retention_replay_context_policy",
        "prompt_surface": "prompt history, provider text, plugin context, and quarantine snapshots",
        "current_scope": "bounded configurable retention surfaces and context-policy capability hashes",
        "missing_readiness": "full replay-retention policy and non-PromptSampler role ownership",
        "roadmap_required_phrase": "replay-retention policy and richer context-policy ownership",
        "current_sidecars": (
            "papers/runtime_rng_replay_boundary.json",
            "papers/provider_diagnostics_replay_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Extend structured prompt context policy beyond validated current fields.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Extend meta-prompt context policy beyond validated current fields.",
            },
        ),
        "validation_gate": "role-owned prompt retention and replay policy",
        "readiness_status": "bounded_retention_without_full_replay",
    },
    {
        "criterion_id": "retrieval_integrity",
        "prompt_surface": "DeepResearch and DeepEvolve-inspired retrieval context",
        "current_scope": "bounded retrieval provenance and source-ranking overclaim audits",
        "missing_readiness": "raw/source payload integrity, learned ranking evidence, and replayable transport policy",
        "roadmap_required_phrase": "audit-grade source integrity",
        "current_sidecars": ("papers/deepevolve_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Persist unbounded raw retrieval evidence and learned ranking provenance.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Make DeepEvolve-inspired live retrieval transport audit-grade.",
            },
        ),
        "validation_gate": "audit-grade retrieval source and ranking artifacts",
        "readiness_status": "bounded_retrieval_provenance_only",
    },
    {
        "criterion_id": "proposal_memory_semantics",
        "prompt_surface": "proposal metadata, hypothesis history, and backtracking evidence",
        "current_scope": "exact duplicate/proposal-score reports and bounded hypothesis summaries",
        "missing_readiness": "semantic proposal index, near-duplicate families, quality models, and cross-run tables",
        "roadmap_required_phrase": "semantically searchable proposal memory",
        "current_sidecars": (
            "papers/proposal_score_boundary.json",
            "papers/proposal_diversity_boundary.json",
            "papers/natural_language_preamble_boundary.json",
            "papers/controller_backtracking_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "semantic failed-proposal retrieval",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Extend creative-generation proposal diversity evidence beyond exact",
            },
        ),
        "validation_gate": "semantic proposal memory and cross-run retrieval",
        "readiness_status": "bounded_current_run_proposal_reports",
    },
    {
        "criterion_id": "meta_prompt_reward_evidence",
        "prompt_surface": "meta-prompt mutation, scoring, and prompt-arm selection",
        "current_scope": "absolute/improvement child-score rewards and UCB-style prompt-arm selection",
        "missing_readiness": "calibrated prompt rewards, prompt-lineage ablations, and attribution reports",
        "roadmap_required_phrase": "calibrated reward signals plus ablation reporting",
        "current_sidecars": (
            "papers/llm_role_scheduler_boundary.json",
            "papers/ucb1_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Calibrate meta-prompt scoring beyond absolute/improvement child rewards.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Calibrate meta-prompt rewards and add prompt-lineage ablation evidence.",
            },
        ),
        "validation_gate": "calibrated meta-prompt reward and lineage ablation reports",
        "readiness_status": "child_score_reward_only",
    },
    {
        "criterion_id": "prompt_database_lifecycle",
        "prompt_surface": "PromptDatabase, prompt history, and prompt-side archive policy",
        "current_scope": "local deterministic prompt-arm history and scoring",
        "missing_readiness": "prompt-side archive, retention, descriptors/objectives, events, replay, migration, async resume, and benchmarks",
        "roadmap_required_phrase": "Promote the current local `PromptDatabase` beyond prompt-arm history",
        "current_sidecars": (
            "papers/implementation_evidence_map_boundary.json",
            "papers/roadmap_backend_scheduling_critique_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Promote the prompt-program store to a solution-database-equivalent",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Separate prompt-database parity from local prompt-arm selection.",
            },
        ),
        "validation_gate": "prompt-side archive lifecycle and replay benchmark evidence",
        "readiness_status": "local_prompt_arm_selector_only",
    },
)


@dataclass(frozen=True)
class RoadmapPromptContextSystemBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapPromptContextSystemBoundaryValidation:
    ok: bool
    boundary_status: str | None
    criterion_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapPromptContextSystemBoundaryIssue]


def roadmap_prompt_context_system_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP prompt/context-system criteria map."""

    root_path = Path(root)
    roadmap_text = _read_text(root_path / "ROADMAP.md")
    records = [_criterion_record(root_path, roadmap_text, spec) for spec in CRITERION_SPECS]
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    sidecar_ref_count = sum(len(record["current_sidecar_refs"]) for record in records)
    return {
        "schema": ROADMAP_PROMPT_CONTEXT_SYSTEM_BOUNDARY_SCHEMA,
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
            "This boundary records a ROADMAP-level prompt/context-system "
            "criteria map for templates, context-source selection, token "
            "packing, stochastic prompt-format provenance, retention/replay, "
            "retrieval integrity, proposal memory, meta-prompt rewards, and "
            "PromptDatabase lifecycle. It does not claim a prompt-role "
            "capability matrix, deterministic context summarization, all-role "
            "provider-token section packing, separate prompt-format source "
            "provenance, full prompt replay retention, audit-grade retrieval "
            "source integrity, semantic proposal memory, calibrated "
            "meta-prompt rewards, prompt-database archive lifecycle, "
            "prompt/context benchmark evidence, or owner review signoff."
        ),
    }


def validate_roadmap_prompt_context_system_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapPromptContextSystemBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_prompt_context_system_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return RoadmapPromptContextSystemBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = roadmap_prompt_context_system_boundary_record(root)
    issues: list[RoadmapPromptContextSystemBoundaryIssue] = []
    if data.get("schema") != ROADMAP_PROMPT_CONTEXT_SYSTEM_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP prompt/context system boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP prompt/context system boundary must not claim full readiness"))
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
        issues.append(_issue("missing_roadmap_heading", "prompt and context work heading was not found"))
    if data.get("criterion_count") != len(CRITERION_SPECS):
        issues.append(_issue("invalid_criterion_count", "criterion count changed"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a prompt-role capability matrix" not in boundary_text
        or "semantic proposal memory" not in boundary_text
        or "prompt-database archive lifecycle" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded criteria from prompt-system readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapPromptContextSystemBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        criterion_count=data.get("criterion_count") if isinstance(data.get("criterion_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_prompt_context_system_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_roadmap_prompt_context_system_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP prompt context system boundary",
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
        "prompt_surface": spec["prompt_surface"],
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
) -> tuple[dict[str, Any] | None, list[RoadmapPromptContextSystemBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP prompt/context system boundary must be a JSON object")]


def _validate_required_fields(value: object, issues: list[RoadmapPromptContextSystemBoundaryIssue]) -> int:
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


def _validate_missing_evidence(value: object, issues: list[RoadmapPromptContextSystemBoundaryIssue]) -> int:
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


def _issue(code: str, message: str) -> RoadmapPromptContextSystemBoundaryIssue:
    return RoadmapPromptContextSystemBoundaryIssue(code=code, message=message)
