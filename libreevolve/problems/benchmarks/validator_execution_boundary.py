from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


VALIDATOR_EXECUTION_BOUNDARY_SCHEMA = "libreevolve.validator_execution_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.4", "2.6", "4")
EXPECTED_POLICY_SCHEMA = "libreevolve.validator_execution_policy.v1"
EXPECTED_BOUNDARY_STATUS = (
    "local_subprocess_validator_policy_without_os_container_sandbox"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "startup_validator_execution_policy_schema",
    "attempt_validator_boundary_metadata",
    "validator_boundary_consistency_schema",
    "run_artifact_validator_boundary_scan",
    "local_subprocess_execution_boundary",
    "candidate_root_cwd_policy",
    "declared_problem_file_access_policy",
    "filesystem_capabilities_record",
    "validator_network_policy_record",
    "python_socket_denial_metadata",
    "minimal_environment_secret_boundary",
    "stdout_stderr_redaction",
    "wall_clock_timeout_cleanup",
    "resource_limit_policy_record",
    "os_container_sandbox_enforcement",
    "kernel_or_container_network_egress_control",
    "os_enforced_filesystem_capabilities",
    "cpu_memory_gpu_disk_process_quotas",
    "native_extension_network_denial_proof",
    "distributed_evaluator_worker_resume_state",
)
EXPECTED_MISSING_EVIDENCE = {
    "os_container_sandbox_enforcement": "not_recorded_locally",
    "kernel_or_container_network_egress_control": "not_recorded_locally",
    "os_enforced_filesystem_capabilities": "not_recorded_locally",
    "cpu_memory_gpu_disk_process_quotas": "not_recorded_locally",
    "native_extension_network_denial_proof": "not_recorded_locally",
    "distributed_evaluator_worker_resume_state": "not_recorded_locally",
}


@dataclass(frozen=True)
class ValidatorExecutionBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ValidatorExecutionBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ValidatorExecutionBoundaryIssue]


def validator_execution_boundary_record() -> dict[str, Any]:
    """Return the validator execution and sandbox/resource boundary."""

    return {
        "schema": VALIDATOR_EXECUTION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve evaluates generated programs against existing "
            "codebases and expensive systems tasks, so validator execution "
            "evidence must separate local subprocess policy metadata from "
            "real OS/container sandboxing and resource enforcement."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "validator_execution_policy_schema": EXPECTED_POLICY_SCHEMA,
        "validator_boundary_consistency_schema": (
            "libreevolve.validator_boundary_consistency.v1"
        ),
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve emits and validates "
            "startup policies.validator_execution, per-attempt "
            "evaluation.metadata.validator_boundary records, run-artifact "
            "validator-boundary scans, local subprocess execution scope, "
            "candidate-root cwd policy, declared problem-file access policy, "
            "filesystem_capabilities records, validator_network_policy records, "
            "Python socket-denial metadata, minimal environment and redacted "
            "output secret boundaries, wall-clock timeout cleanup, and "
            "resource_limit_policy metadata. It does not claim OS/container "
            "sandbox enforcement, kernel or container network egress control, "
            "OS-enforced filesystem capabilities, CPU/memory/GPU/disk/process "
            "quotas, native-extension network denial proof, or distributed "
            "evaluator-worker resume state."
        ),
    }


def validate_validator_execution_boundary(
    boundary: object | str | Path | None = None,
) -> ValidatorExecutionBoundaryValidation:
    data, read_issues = _load_boundary(
        validator_execution_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ValidatorExecutionBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ValidatorExecutionBoundaryIssue] = []
    if data.get("schema") != VALIDATOR_EXECUTION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported validator execution boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.4, 2.6, and 4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "validator execution evidence" not in source_claim
        or "local subprocess policy metadata" not in source_claim
        or "resource enforcement" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must separate local policy metadata from sandbox/resource enforcement"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("validator_execution_policy_schema") != EXPECTED_POLICY_SCHEMA:
        issues.append(_issue("invalid_validator_execution_policy_schema", f"validator execution policy schema must be {EXPECTED_POLICY_SCHEMA}"))
    if (
        data.get("validator_boundary_consistency_schema")
        != "libreevolve.validator_boundary_consistency.v1"
    ):
        issues.append(_issue("invalid_validator_boundary_consistency_schema", "validator boundary consistency schema must be linked"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "validator execution boundary must not claim sandbox/resource readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim OS/container sandbox enforcement" not in boundary_text
        or "CPU/memory/GPU/disk/process quotas" not in boundary_text
        or "native-extension network denial proof" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate local validator policy metadata from sandbox/resource enforcement"))
    return ValidatorExecutionBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_validator_execution_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_validator_execution_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Validator execution boundary",
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
) -> tuple[dict[str, Any] | None, list[ValidatorExecutionBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "validator execution boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ValidatorExecutionBoundaryIssue],
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
    issues: list[ValidatorExecutionBoundaryIssue],
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


def _issue(code: str, message: str) -> ValidatorExecutionBoundaryIssue:
    return ValidatorExecutionBoundaryIssue(code, message)
