from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RUNTIME_RNG_REPLAY_BOUNDARY_SCHEMA = "libreevolve.runtime_rng_replay_boundary_paper.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.6", "4")
EXPECTED_RUNTIME_BOUNDARY_SCHEMA = "libreevolve.runtime_rng_replay_boundary.v1"
EXPECTED_BOUNDARY_STATUS = (
    "framework_rng_snapshot_restore_without_full_resumed_trace_replay"
)
EXPECTED_OWNED_SURFACES = (
    "loop_parent_explore_exploit_choice",
    "prompt_template_sampling",
    "program_database_sampling",
    "island_sampling",
    "map_elites_sampling",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "runtime_rng_snapshot_schema",
    "runtime_rng_state_sha256",
    "random_setstate_restore_entrypoint",
    "direct_evolve_rng_restore_entrypoint",
    "cli_restore_rng_from_manifest_entrypoint",
    "seed_mismatch_rejection",
    "runtime_rng_replay_boundary_schema",
    "framework_owned_surface_list",
    "process_global_rng_isolation",
    "full_resume_bundle_rng_boundary_linkage",
    "llm_provider_output_replay_or_exclusion",
    "plugin_internal_rng_capture_or_exclusion",
    "validator_subprocess_rng_capture_or_exclusion",
    "controller_pending_work_rng_linkage",
    "end_to_end_sampling_continuity_trace",
)
EXPECTED_MISSING_EVIDENCE = {
    "llm_provider_output_replay_or_exclusion": "not_composed_in_resumed_trace",
    "plugin_internal_rng_capture_or_exclusion": "not_composed_in_resumed_trace",
    "validator_subprocess_rng_capture_or_exclusion": "not_composed_in_resumed_trace",
    "controller_pending_work_rng_linkage": "not_recorded_locally",
    "end_to_end_sampling_continuity_trace": "not_recorded_locally",
}


@dataclass(frozen=True)
class RuntimeRngReplayBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RuntimeRngReplayBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[RuntimeRngReplayBoundaryIssue]


def runtime_rng_replay_boundary_record() -> dict[str, Any]:
    """Return the framework RNG replay boundary for paper claims."""

    return {
        "schema": RUNTIME_RNG_REPLAY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve-style long-running experiments should preserve "
            "framework-owned stochastic state without implying that provider, "
            "plugin, validator, controller, or resumed-trace randomness is "
            "fully replayed."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_rng_snapshot_schema": "python.random.mt19937.v1",
        "runtime_rng_replay_boundary_schema": EXPECTED_RUNTIME_BOUNDARY_SCHEMA,
        "owned_rng": "framework_run_random",
        "owned_surfaces": list(EXPECTED_OWNED_SURFACES),
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve persists a checked "
            "python.random.mt19937.v1 runtime RNG snapshot with state_sha256, "
            "uses random.Random.setstate as the restore entrypoint, supports "
            "direct evolve() and CLI --restore-rng-from-manifest restore, "
            "rejects seed mismatches, records a "
            "libreevolve.runtime_rng_replay_boundary.v1 runtime boundary, "
            "keeps framework-owned parent/prompt/database/island/MAP-Elites "
            "sampling surfaces explicit, avoids perturbing process-global RNG, "
            "and includes the RNG boundary in full-runtime restore bundles. It "
            "does not claim LLM provider output replay or resumed-trace "
            "exclusion, plugin internal RNG capture or resumed-trace exclusion, "
            "validator subprocess RNG capture or resumed-trace exclusion, "
            "controller pending-work RNG linkage, or end-to-end sampling "
            "continuity trace proof."
        ),
    }


def validate_runtime_rng_replay_boundary(
    boundary: object | str | Path | None = None,
) -> RuntimeRngReplayBoundaryValidation:
    data, read_issues = _load_boundary(
        runtime_rng_replay_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return RuntimeRngReplayBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[RuntimeRngReplayBoundaryIssue] = []
    if data.get("schema") != RUNTIME_RNG_REPLAY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported runtime RNG replay boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.6 and 4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "framework-owned stochastic state" not in source_claim
        or "provider, plugin, validator, controller" not in source_claim
        or "fully replayed" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify framework RNG versus external replay surfaces"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_rng_snapshot_schema") != "python.random.mt19937.v1":
        issues.append(_issue("invalid_runtime_rng_snapshot_schema", "runtime RNG snapshot schema must be python.random.mt19937.v1"))
    if data.get("runtime_rng_replay_boundary_schema") != EXPECTED_RUNTIME_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_runtime_rng_replay_boundary_schema", f"runtime RNG replay boundary schema must be {EXPECTED_RUNTIME_BOUNDARY_SCHEMA}"))
    if data.get("owned_rng") != "framework_run_random":
        issues.append(_issue("invalid_owned_rng", "owned_rng must be framework_run_random"))
    _validate_owned_surfaces(data.get("owned_surfaces"), issues)
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "runtime RNG boundary must not claim full replay readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "process-global RNG" not in boundary_text
        or "plugin internal RNG capture" not in boundary_text
        or "end-to-end sampling continuity trace proof" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate framework RNG restore from full sampling replay"))
    return RuntimeRngReplayBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_runtime_rng_replay_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_runtime_rng_replay_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Runtime RNG replay boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RuntimeRngReplayBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "runtime RNG replay boundary must be a JSON object")]


def _validate_owned_surfaces(
    value: object,
    issues: list[RuntimeRngReplayBoundaryIssue],
) -> None:
    if not isinstance(value, list):
        issues.append(_issue("invalid_owned_surfaces", "owned_surfaces must be a list"))
        return
    if value != list(EXPECTED_OWNED_SURFACES):
        issues.append(_issue("invalid_owned_surfaces", "owned_surfaces must match the runtime RNG replay surfaces"))


def _validate_required_fields(
    value: object,
    issues: list[RuntimeRngReplayBoundaryIssue],
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
    issues: list[RuntimeRngReplayBoundaryIssue],
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


def _issue(code: str, message: str) -> RuntimeRngReplayBoundaryIssue:
    return RuntimeRngReplayBoundaryIssue(code, message)
