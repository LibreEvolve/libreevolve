from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_candidate_language_runner_boundary.v1"
)
CANDIDATE_LANGUAGE_POLICY_SCHEMA = "libreevolve.candidate_language_policy.v1"
CANDIDATE_LANGUAGE_RUNNER_CONTRACT_REPORT_SCHEMA = (
    "libreevolve.candidate_language_runner_contract_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.1", "2.2")
EXPECTED_BOUNDARY_STATUS = "digest_pinned_oci_candidate_execution_partial"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "candidate_language",
    "runner_id",
    "runner_kind",
    "marker_grammar_id",
    "validator_runner_contract",
    "build_system_contract",
    "build_command",
    "runtime_command",
    "dependency_manifest",
    "toolchain_candidates",
    "toolchain_version_probe",
    "toolchain_executable_sha256",
    "toolchain_version_output_sha256",
    "dependency_lock_sha256",
    "toolchain_replay_scope",
    "execution_environment_type",
    "oci_image_manifest_digest",
    "container_runtime_identity",
    "container_provisioning_status",
    "candidate_network_policy",
    "container_resource_policy",
    "declared_workspace_path_match",
    "generated_artifact_path",
    "generated_artifact_hash",
    "language_runner_ready",
    "build_runner_ready",
    "task_abstraction_hook",
    "runner_environment_provenance",
)
EXPECTED_MISSING_EVIDENCE = {
    "configured_non_python_language_runners": (
        "expression_host_c_and_digest_pinned_oci_python_smoke_contracts_recorded_language_and_codebase_breadth_not_recorded"
    ),
    "build_system_runner_contracts": (
        "host_c_compiler_and_single_digest_pinned_oci_python_build_contract_recorded_broader_toolchain_parity_not_recorded"
    ),
    "language_aware_marker_grammars": "not_recorded_locally",
    "arbitrary_language_validator_contracts": (
        "problem_owned_python_scoring_for_expression_and_c_recorded_arbitrary_language_contract_not_recorded"
    ),
    "task_defined_candidate_abstraction_hooks": "not_recorded_locally",
    "runner_environment_artifacts": (
        "host_toolchain_hashes_and_oci_runtime_image_provisioning_isolation_records_available_full_environment_replay_not_recorded"
    ),
    "generated_build_artifact_records": (
        "bounded_expression_and_c_binary_build_artifacts_recorded_codebase_scale_not_recorded"
    ),
    "portable_hermetic_toolchain_provisioning": (
        "single_digest_pinned_oci_image_pull_contract_recorded_package_manager_and_multi_platform_restore_not_recorded"
    ),
    "exact_cross_host_toolchain_replay": (
        "digest_pinned_oci_replay_scope_recorded_daemon_platform_and_cross_host_certification_not_recorded"
    ),
    "os_sandboxed_runner_isolation": (
        "candidate_oci_process_network_rootfs_capability_and_resource_controls_recorded_hostile_code_security_not_certified"
    ),
}


@dataclass(frozen=True)
class CandidateLanguageRunnerBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CandidateLanguageRunnerBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[CandidateLanguageRunnerBoundaryIssue]


def candidate_language_runner_boundary_record() -> dict[str, Any]:
    """Return the current local language/build-runner partial boundary."""

    return {
        "schema": CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_SCHEMA,
        "policy_schema": CANDIDATE_LANGUAGE_POLICY_SCHEMA,
        "runtime_report_schema": CANDIDATE_LANGUAGE_RUNNER_CONTRACT_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "tasks define the program artifact and evaluator interface, and "
            "AlphaEvolve can operate on existing codebases and task-specific "
            "program representations rather than only one Python-primary "
            "workspace shape"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "candidate_language_runner_contract_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has a validated task-primary "
            "candidate-language policy, stage-bound local build and runner commands, "
            "problem-owned scoring, bounded generated-artifact capture, and an "
            "executed non-Python expression fixture, one checked host C compiler "
            "fixture with toolchain/lock identity, and optional exact-pin "
            "enforcement. It also records one digest-pinned OCI Python fixture "
            "contract with immutable image identity, optional pull-if-missing, "
            "network-disabled read-only-rootfs candidate build/run processes, "
            "bounded resources, ordered in-image toolchain probes, and values-"
            "redacted runtime connectivity metadata. The live OCI integration "
            "test remains opt-in and is not a committed cross-host certification. "
            "This does not claim "
            "AlphaEvolve-style arbitrary language or build-system parity with "
            "language-aware marker grammars, hostile-code sandboxing, broad "
            "package-manager provisioning, deterministic cross-platform replay, "
            "task-defined abstraction hooks, arbitrary-runner environment "
            "artifacts, or codebase-scale generated build-artifact evidence."
        ),
    }


def validate_candidate_language_runner_boundary(
    boundary: object | str | Path | None = None,
) -> CandidateLanguageRunnerBoundaryValidation:
    data, read_issues = _load_boundary(
        candidate_language_runner_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return CandidateLanguageRunnerBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CandidateLanguageRunnerBoundaryIssue] = []
    if data.get("schema") != CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported candidate language runner boundary schema"))
    if data.get("policy_schema") != CANDIDATE_LANGUAGE_POLICY_SCHEMA:
        issues.append(_issue("invalid_policy_schema", "policy schema must identify candidate-language policies"))
    if data.get("runtime_report_schema") != CANDIDATE_LANGUAGE_RUNNER_CONTRACT_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify candidate-language runner reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.1', '2.2']"))
    if not isinstance(data.get("source_claim"), str) or "existing codebases" not in data["source_claim"]:
        issues.append(_issue("invalid_source_claim", "source_claim must identify existing-codebase program artifacts"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "candidate_language_runner_contract_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to candidate-language runner contract reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "candidate language runner boundary must not claim paper readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim arbitrary-language runner parity"))
    return CandidateLanguageRunnerBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_candidate_language_runner_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_candidate_language_runner_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve candidate language runner boundary",
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
) -> tuple[dict[str, Any] | None, list[CandidateLanguageRunnerBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "candidate language runner boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[CandidateLanguageRunnerBoundaryIssue],
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
    issues: list[CandidateLanguageRunnerBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    raw_keys = set(value)
    if any(not isinstance(key, str) for key in raw_keys):
        issues.append(
            _issue(
                "invalid_missing_evidence_key",
                "missing_evidence keys must be strings",
            )
        )
    actual_keys = {key for key in raw_keys if isinstance(key, str)}
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


def _issue(code: str, message: str) -> CandidateLanguageRunnerBoundaryIssue:
    return CandidateLanguageRunnerBoundaryIssue(code, message)
