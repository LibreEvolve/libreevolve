from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


THETAEVOLVE_BOUNDARY_SCHEMA = "libreevolve.thetaevolve_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2511.23473"
EXPECTED_SOURCE_TITLE = "ThetaEvolve: Test-time Learning on Open Problems"
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2511.23473.pdf"
EXPECTED_SOURCE_FILE = "papers/2511.23473__ThetaEvolve.pdf"
EXPECTED_SOURCE_SHA256 = (
    "8e74933b2a4dddbf80a063fb88438c95b62b982a5167bbb77213ce1e3839715d"
)
EXPECTED_SOURCE_BYTES = 3949612
EXPECTED_BOUNDARY_STATUS = "test_time_training_inspiration_without_thetaevolve_parity"
EXPECTED_COMPONENT_IDS = (
    "dynamic_environment",
    "single_llm_runtime",
    "large_program_database",
    "batch_parent_response_sampling",
    "early_checks",
    "lazy_penalties",
    "reward_shaping",
    "grpo_rl_training",
    "checkpoint_lifecycle",
    "trained_checkpoint_inference",
    "throughput_pipeline",
    "benchmark_comparison_rows",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "dynamic_environment_schema",
    "single_llm_configuration",
    "program_database_size_records",
    "batch_prompt_sampling_records",
    "response_sampling_records",
    "early_check_penalty_schema",
    "lazy_penalty_schema",
    "reward_shaping_parameters",
    "grpo_training_run_telemetry",
    "asymmetric_clipping_configuration",
    "training_api_or_runtime_provenance",
    "checkpoint_artifact_lifecycle",
    "trained_checkpoint_inference_report",
    "transfer_generalization_report",
    "generated_program_sample_counts",
    "concurrent_verifier_telemetry",
    "sglang_vllm_throughput_report",
    "task_evaluator_compatibility_caveats",
    "alphaevolve_shinkaevolve_openevolve_baseline_rows",
    "open_problem_benchmark_rows",
    "database_design_ablation_rows",
    "reward_shaping_ablation_rows",
    "ttt_rl_export_separation_evidence",
)
EXPECTED_MISSING_EVIDENCE = {
    "dynamic_environment": "not_implemented_locally",
    "single_llm_thetaevolve_runtime": "not_implemented_locally",
    "large_program_database_scaling": "not_recorded_locally",
    "batch_parent_response_sampling": "not_implemented_locally",
    "early_check_penalties": "not_implemented_locally",
    "lazy_penalties": "not_implemented_locally",
    "reward_shaping": "not_implemented_locally",
    "grpo_rl_training": "not_implemented_locally",
    "asymmetric_clipping_configuration": "not_recorded_locally",
    "checkpoint_lifecycle": "not_implemented_locally",
    "trained_checkpoint_inference": "not_recorded_locally",
    "transfer_generalization": "not_recorded_locally",
    "concurrent_verifier_throughput": "not_recorded_locally",
    "benchmark_comparison_rows": "not_recorded_locally",
    "database_and_reward_ablations": "not_recorded_locally",
    "linked_code_status": "not_verified_as_local_runtime",
}


@dataclass(frozen=True)
class ThetaEvolveBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ThetaEvolveBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ThetaEvolveBoundaryIssue]


def thetaevolve_boundary_record() -> dict[str, Any]:
    """Return the current ThetaEvolve test-time-learning absence boundary."""

    return {
        "schema": THETAEVOLVE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_version": "v1",
        "source_submitted_date": "2025-11-28",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://creativecommons.org/licenses/by/4.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://github.com/ypwang61/ThetaEvolve",
                "status": "linked_in_paper_not_verified_as_local_runtime",
            }
        ],
        "framework_components": [
            {
                "component_id": "dynamic_environment",
                "paper_role": "AlphaEvolve-inspired dynamic environment for test-time learning",
                "local_status": "not_implemented",
            },
            {
                "component_id": "single_llm_runtime",
                "paper_role": "single-LLM runtime in place of a frontier-model ensemble",
                "local_status": "not_implemented",
            },
            {
                "component_id": "large_program_database",
                "paper_role": "large program database with population scaling reports",
                "local_status": "not_recorded",
            },
            {
                "component_id": "batch_parent_response_sampling",
                "paper_role": "batch prompt and response sampling over parents",
                "local_status": "not_implemented",
            },
            {
                "component_id": "early_checks",
                "paper_role": "early checks and penalty schema for malformed or weak candidates",
                "local_status": "not_implemented",
            },
            {
                "component_id": "lazy_penalties",
                "paper_role": "lazy penalties for unchanged or database-equivalent programs",
                "local_status": "not_implemented",
            },
            {
                "component_id": "reward_shaping",
                "paper_role": "optional reward shaping for stable RL signals",
                "local_status": "not_implemented",
            },
            {
                "component_id": "grpo_rl_training",
                "paper_role": "GRPO/RL training at test time",
                "local_status": "not_implemented",
            },
            {
                "component_id": "checkpoint_lifecycle",
                "paper_role": "RL-trained checkpoint and adapter lifecycle",
                "local_status": "not_implemented",
            },
            {
                "component_id": "trained_checkpoint_inference",
                "paper_role": "inference and transfer reports for trained checkpoints",
                "local_status": "not_recorded",
            },
            {
                "component_id": "throughput_pipeline",
                "paper_role": "SGLang/vLLM-style batch throughput and concurrent verifiers",
                "local_status": "not_recorded",
            },
            {
                "component_id": "benchmark_comparison_rows",
                "paper_role": "AlphaEvolve, ShinkaEvolve, and OpenEvolve comparison rows",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "ttt_rl_export_scope": "clipped_reward_jsonl_export_only_not_training",
            "current_plugin": "libreevolve/plugins/ttt_rl.py",
            "current_training_data_export": True,
            "online_rl_training_ready": False,
            "grpo_ready": False,
            "checkpoint_lifecycle_ready": False,
            "lazy_penalty_ready": False,
            "reward_shaping_ready": False,
            "batch_sampling_ready": False,
            "throughput_report_ready": False,
            "benchmark_comparison_ready": False,
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records ThetaEvolve as test-time-training "
            "inspiration only. It does not claim a ThetaEvolve dynamic "
            "environment, batch sampling, lazy penalties, reward shaping, "
            "online GRPO/RL training, checkpoint lifecycle, trained-checkpoint "
            "inference, throughput reproduction, or benchmark-comparison "
            "parity. LibreEvolve's current ttt_rl support is clipped-reward "
            "JSONL export, not model training."
        ),
    }


def validate_thetaevolve_boundary(
    boundary: object | str | Path | None = None,
) -> ThetaEvolveBoundaryValidation:
    data, read_issues = _load_boundary(
        thetaevolve_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ThetaEvolveBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ThetaEvolveBoundaryIssue] = []
    if data.get("schema") != THETAEVOLVE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ThetaEvolve boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2511.23473"))
    if data.get("source_title") != EXPECTED_SOURCE_TITLE:
        issues.append(_issue("invalid_source_title", "source_title must identify ThetaEvolve"))
    if data.get("source_version") != "v1":
        issues.append(_issue("invalid_source_version", "source_version must be v1"))
    if data.get("source_submitted_date") != "2025-11-28":
        issues.append(_issue("invalid_source_submitted_date", "source_submitted_date must be 2025-11-28"))
    if data.get("source_url") != EXPECTED_SOURCE_URL:
        issues.append(_issue("invalid_source_url", "source_url must identify the arXiv PDF"))
    if data.get("source_file") != EXPECTED_SOURCE_FILE:
        issues.append(_issue("invalid_source_file", "source_file must identify the cached ThetaEvolve PDF"))
    if data.get("source_sha256") != EXPECTED_SOURCE_SHA256:
        issues.append(_issue("invalid_source_sha256", "source_sha256 must match the cached PDF digest"))
    if data.get("source_bytes") != EXPECTED_SOURCE_BYTES:
        issues.append(_issue("invalid_source_bytes", "source_bytes must match the cached PDF size"))
    if data.get("source_license") != "http://creativecommons.org/licenses/by/4.0/":
        issues.append(_issue("invalid_source_license", "source_license must match the cached PDF metadata"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ThetaEvolve boundary must not claim test-time-learning parity"))
    _validate_source_links(data.get("source_links"), issues)
    component_count = _validate_framework_components(data.get("framework_components"), issues)
    _validate_local_evidence(data.get("local_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that ThetaEvolve parity is not claimed"))
    return ThetaEvolveBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        component_count=component_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_thetaevolve_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_thetaevolve_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ThetaEvolve boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| component_count | {validation.component_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ThetaEvolveBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ThetaEvolve boundary must be a JSON object")]


def _validate_source_links(value: object, issues: list[ThetaEvolveBoundaryIssue]) -> None:
    if not isinstance(value, list):
        issues.append(_issue("invalid_source_links", "source_links must be a list"))
        return
    urls = {item.get("url") for item in value if isinstance(item, dict)}
    if urls != {"https://github.com/ypwang61/ThetaEvolve"}:
        issues.append(_issue("source_link_mismatch", "source_links must preserve the ThetaEvolve GitHub URL"))
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_source_link", "source link records must be objects"))
            continue
        if item.get("status") != "linked_in_paper_not_verified_as_local_runtime":
            issues.append(_issue("source_link_status_overclaim", "source link status must remain unverified as local runtime evidence"))


def _validate_framework_components(value: object, issues: list[ThetaEvolveBoundaryIssue]) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_framework_components", "framework_components must be a list"))
        return 0
    ids = [item.get("component_id") for item in value if isinstance(item, dict)]
    if tuple(ids) != EXPECTED_COMPONENT_IDS:
        issues.append(_issue("framework_component_id_mismatch", "framework_components must preserve the ThetaEvolve component set"))
    allowed_statuses = {"not_implemented", "not_recorded"}
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_framework_component", "framework component records must be objects"))
            continue
        if item.get("component_id") in EXPECTED_COMPONENT_IDS and item.get("local_status") not in allowed_statuses:
            issues.append(_issue("framework_component_overclaim", "framework component local_status must not claim ThetaEvolve parity"))
    return len(value)


def _validate_local_evidence(value: object, issues: list[ThetaEvolveBoundaryIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_evidence", "local_evidence must be an object"))
        return
    expected = {
        "ttt_rl_export_scope": "clipped_reward_jsonl_export_only_not_training",
        "current_plugin": "libreevolve/plugins/ttt_rl.py",
        "current_training_data_export": True,
        "online_rl_training_ready": False,
        "grpo_ready": False,
        "checkpoint_lifecycle_ready": False,
        "lazy_penalty_ready": False,
        "reward_shaping_ready": False,
        "batch_sampling_ready": False,
        "throughput_report_ready": False,
        "benchmark_comparison_ready": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            suffix = "overclaim" if expected_value is False else "mismatch"
            issues.append(_issue(f"local_evidence_{field}_{suffix}", f"local_evidence.{field} must preserve current ThetaEvolve boundary"))


def _validate_required_fields(
    value: object,
    issues: list[ThetaEvolveBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    if seen != expected:
        issues.append(_issue("required_evidence_field_mismatch", "required_evidence_fields must preserve ThetaEvolve evidence gates"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[ThetaEvolveBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    if set(value) != set(EXPECTED_MISSING_EVIDENCE):
        issues.append(_issue("missing_evidence_key_mismatch", "missing_evidence must preserve ThetaEvolve artifact-gap keys"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(value)


def _issue(code: str, message: str) -> ThetaEvolveBoundaryIssue:
    return ThetaEvolveBoundaryIssue(code, message)
