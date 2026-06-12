from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MAGELLAN_BOUNDARY_SCHEMA = "libreevolve.magellan_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2601.21096"
EXPECTED_SOURCE_TITLE = (
    "Magellan: Autonomous Discovery of Novel Compiler Optimization Heuristics "
    "with AlphaEvolve"
)
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2601.21096.pdf"
EXPECTED_SOURCE_FILE = "papers/2601.21096__Magellan.pdf"
EXPECTED_SOURCE_SHA256 = (
    "4619366bb337eb723bbe882d9efd07d8f57dca53e95fb7e1de6788a011e7f8bb"
)
EXPECTED_SOURCE_BYTES = 1483119
EXPECTED_BOUNDARY_STATUS = "compiler_optimization_context_without_magellan_runtime_parity"
EXPECTED_COMPONENT_IDS = (
    "cxx_decision_logic_candidates",
    "compiler_pass_integration",
    "evolve_block_source_spans",
    "policy_proposal",
    "local_compiler_evaluation",
    "hyperparameter_tuning",
    "feedback_generation",
    "llvm_function_inlining_size",
    "llvm_function_inlining_performance",
    "register_allocation_priority_rule",
    "xla_graph_extraction",
    "xla_auto_sharding",
    "macro_benchmark_provenance",
    "baseline_and_generalization_rows",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "alphaevolve_relation",
    "compiler_fixture_policy",
    "cxx_decision_logic_candidate_schema",
    "compiler_pass_integration_points",
    "evolve_block_source_span_records",
    "compiler_flag_hyperparameter_schema",
    "policy_proposal_records",
    "local_compiler_rebuild_records",
    "macro_benchmark_dataset_provenance",
    "binary_size_metric_definition",
    "end_to_end_performance_metric_definition",
    "autotuner_identity_and_batch_records",
    "invalid_sample_rate_records",
    "feedback_generation_records",
    "llvm_partial_feature_inlining_rows",
    "llvm_full_api_inlining_rows",
    "register_allocation_priority_rule_rows",
    "xla_graph_extraction_rows",
    "xla_auto_sharding_rows",
    "expert_baseline_identity_rows",
    "neural_baseline_identity_rows",
    "temporal_generalization_rows",
    "domain_generalization_rows",
    "generated_policy_maintainability_rows",
    "compiler_environment_hashes",
    "independent_checker_outputs",
)
EXPECTED_MISSING_EVIDENCE = {
    "cxx_decision_logic_candidate_schema": "not_implemented_locally",
    "compiler_pass_runner": "not_implemented_locally",
    "evolve_block_compiler_source_spans": "not_recorded_locally",
    "compiler_flag_hyperparameter_schema": "not_recorded_locally",
    "policy_proposal_records": "not_recorded_locally",
    "local_compiler_rebuild_records": "not_recorded_locally",
    "macro_benchmark_harness": "not_implemented_locally",
    "binary_size_metric_records": "not_recorded_locally",
    "end_to_end_performance_metric_records": "not_recorded_locally",
    "vizier_autotuning_records": "not_recorded_locally",
    "invalid_sample_rate_records": "not_recorded_locally",
    "llvm_inlining_size_rows": "not_recorded_locally",
    "llvm_inlining_performance_rows": "not_recorded_locally",
    "register_allocation_rows": "not_recorded_locally",
    "xla_graph_extraction_rows": "not_recorded_locally",
    "xla_auto_sharding_rows": "not_recorded_locally",
    "expert_neural_baseline_rows": "not_recorded_locally",
    "temporal_domain_generalization_rows": "not_recorded_locally",
    "generated_policy_maintainability_rows": "not_recorded_locally",
    "dedicated_magellan_runtime_repository": "not_found_in_extracted_links",
}


@dataclass(frozen=True)
class MagellanBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class MagellanBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[MagellanBoundaryIssue]


def magellan_boundary_record() -> dict[str, Any]:
    """Return the current Magellan compiler-optimization absence boundary."""

    return {
        "schema": MAGELLAN_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": [
            "Hongzheng Chen",
            "Alexander Novikov",
            "Ngan Vu",
            "Hanna Alam",
            "Zhiru Zhang",
            "Aiden Grossman",
            "Mircea Trofin",
            "Amir Yazdanbakhsh",
        ],
        "source_version": "v1",
        "source_submitted_date": "2026-01-28",
        "source_accepted_venue": "C4ML@CGO'26",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://creativecommons.org/licenses/by/4.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2601.21096v1",
                "status": "source_version_reference_only",
            },
            {
                "url": "https://github.com/llvm/llvm-project/blob/main/llvm/lib/Analysis/InlineCost.cpp",
                "status": "paper_reference_only_not_magellan_runtime",
            },
            {
                "url": "https://github.com/llvm/llvm-project/blob/main/llvm/lib/CodeGen/RegAllocGreedy.cpp",
                "status": "paper_reference_only_not_magellan_runtime",
            },
            {
                "url": "<no_dedicated_magellan_code_repository_extracted>",
                "status": "not_found_in_extracted_links",
            },
        ],
        "framework_components": [
            {
                "component_id": "cxx_decision_logic_candidates",
                "paper_role": "executable C++ compiler-pass decision logic",
                "local_status": "not_implemented",
            },
            {
                "component_id": "compiler_pass_integration",
                "paper_role": "candidate insertion into LLVM or XLA compiler passes",
                "local_status": "not_implemented",
            },
            {
                "component_id": "evolve_block_source_spans",
                "paper_role": "EVOLVE-BLOCK-delimited compiler source regions",
                "local_status": "not_recorded",
            },
            {
                "component_id": "policy_proposal",
                "paper_role": "LLM-proposed heuristic templates with symbolic parameters",
                "local_status": "not_recorded",
            },
            {
                "component_id": "local_compiler_evaluation",
                "paper_role": "compiler rebuild plus macro-benchmark reward evaluation",
                "local_status": "not_implemented",
            },
            {
                "component_id": "hyperparameter_tuning",
                "paper_role": "external autotuner fills compiler-flag hyperparameters",
                "local_status": "not_implemented",
            },
            {
                "component_id": "feedback_generation",
                "paper_role": "best score, tuning logs, and profiling traces returned to AlphaEvolve",
                "local_status": "not_recorded",
            },
            {
                "component_id": "llvm_function_inlining_size",
                "paper_role": "LLVM inlining binary-size optimization task",
                "local_status": "not_recorded",
            },
            {
                "component_id": "llvm_function_inlining_performance",
                "paper_role": "LLVM inlining end-to-end performance optimization task",
                "local_status": "not_recorded",
            },
            {
                "component_id": "register_allocation_priority_rule",
                "paper_role": "RegAllocGreedy live-range priority policy",
                "local_status": "not_recorded",
            },
            {
                "component_id": "xla_graph_extraction",
                "paper_role": "XLA/e-graph extraction heuristic task",
                "local_status": "not_recorded",
            },
            {
                "component_id": "xla_auto_sharding",
                "paper_role": "XLA auto-sharding contest-style task",
                "local_status": "not_recorded",
            },
            {
                "component_id": "macro_benchmark_provenance",
                "paper_role": "production macro-benchmark and workload provenance",
                "local_status": "not_recorded",
            },
            {
                "component_id": "baseline_and_generalization_rows",
                "paper_role": "expert/neural baselines, temporal/domain generalization, maintainability rows",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_compiler_runner": "<none>",
            "current_candidate_language_scope": "python_primary_text_workspace_not_cxx_compiler_pass",
            "compiler_pass_runner_ready": False,
            "cxx_decision_logic_ready": False,
            "evolve_block_compiler_span_ready": False,
            "compiler_rebuild_ready": False,
            "macro_benchmark_ready": False,
            "autotuning_ready": False,
            "llvm_inlining_rows_ready": False,
            "register_allocation_rows_ready": False,
            "xla_rows_ready": False,
            "baseline_generalization_rows_ready": False,
            "repository_runtime_verified": False,
        },
        "reported_tasks": [
            "LLVM function inlining for binary size",
            "LLVM function inlining for end-to-end performance",
            "LLVM register-allocation live-range priority",
            "XLA graph extraction",
            "XLA auto-sharding",
        ],
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records Magellan as AlphaEvolve compiler-optimization "
            "application context only. LibreEvolve currently does not claim "
            "executable C++ decision-logic candidates, LLVM/XLA compiler-pass "
            "integration, compiler rebuilds, macro-benchmark evaluation, "
            "Vizier-style autotuning, EVOLVE-BLOCK compiler-source spans, "
            "function-inlining result rows, register-allocation rows, XLA "
            "portability rows, expert/neural baseline comparisons, "
            "temporal/domain generalization, or generated-policy "
            "maintainability evidence."
        ),
    }


def validate_magellan_boundary(
    boundary: object | str | Path | None = None,
) -> MagellanBoundaryValidation:
    data, read_issues = _load_boundary(
        magellan_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MagellanBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MagellanBoundaryIssue] = []
    if data.get("schema") != MAGELLAN_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Magellan boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2601.21096"))
    if data.get("source_title") != EXPECTED_SOURCE_TITLE:
        issues.append(_issue("invalid_source_title", "source_title must identify Magellan"))
    if data.get("source_version") != "v1":
        issues.append(_issue("invalid_source_version", "source_version must be v1"))
    if data.get("source_submitted_date") != "2026-01-28":
        issues.append(_issue("invalid_source_submitted_date", "source_submitted_date must be 2026-01-28"))
    if data.get("source_accepted_venue") != "C4ML@CGO'26":
        issues.append(_issue("invalid_source_accepted_venue", "source_accepted_venue must be C4ML@CGO'26"))
    if data.get("source_url") != EXPECTED_SOURCE_URL:
        issues.append(_issue("invalid_source_url", "source_url must identify the arXiv PDF"))
    if data.get("source_file") != EXPECTED_SOURCE_FILE:
        issues.append(_issue("invalid_source_file", "source_file must identify the cached Magellan PDF"))
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
        issues.append(_issue("claim_ready_overclaim", "Magellan boundary must not claim compiler runtime parity"))
    _validate_source_links(data.get("source_links"), issues)
    component_count = _validate_framework_components(data.get("framework_components"), issues)
    _validate_local_evidence(data.get("local_evidence"), issues)
    _validate_reported_tasks(data.get("reported_tasks"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that Magellan parity is not claimed"))
    return MagellanBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        component_count=component_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_magellan_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_magellan_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Magellan boundary",
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
) -> tuple[dict[str, Any] | None, list[MagellanBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Magellan boundary must be a JSON object")]


def _validate_source_links(value: object, issues: list[MagellanBoundaryIssue]) -> None:
    if not isinstance(value, list):
        issues.append(_issue("invalid_source_links", "source_links must be a list"))
        return
    urls = {item.get("url") for item in value if isinstance(item, dict)}
    expected_urls = {
        "https://arxiv.org/abs/2601.21096v1",
        "https://github.com/llvm/llvm-project/blob/main/llvm/lib/Analysis/InlineCost.cpp",
        "https://github.com/llvm/llvm-project/blob/main/llvm/lib/CodeGen/RegAllocGreedy.cpp",
        "<no_dedicated_magellan_code_repository_extracted>",
    }
    if urls != expected_urls:
        issues.append(_issue("source_link_mismatch", "source_links must preserve Magellan source status"))
    allowed_statuses = {
        "source_version_reference_only",
        "paper_reference_only_not_magellan_runtime",
        "not_found_in_extracted_links",
    }
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_source_link", "source link records must be objects"))
            continue
        if item.get("status") not in allowed_statuses:
            issues.append(_issue("source_link_status_overclaim", "source link status must not claim local Magellan runtime"))


def _validate_framework_components(value: object, issues: list[MagellanBoundaryIssue]) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_framework_components", "framework_components must be a list"))
        return 0
    ids = [item.get("component_id") for item in value if isinstance(item, dict)]
    if tuple(ids) != EXPECTED_COMPONENT_IDS:
        issues.append(_issue("framework_component_id_mismatch", "framework_components must preserve the Magellan component set"))
    allowed_statuses = {"not_implemented", "not_recorded"}
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_framework_component", "framework component records must be objects"))
            continue
        if item.get("component_id") in EXPECTED_COMPONENT_IDS and item.get("local_status") not in allowed_statuses:
            issues.append(_issue("framework_component_overclaim", "framework component local_status must not claim Magellan parity"))
    return len(value)


def _validate_local_evidence(value: object, issues: list[MagellanBoundaryIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_evidence", "local_evidence must be an object"))
        return
    expected = {
        "current_compiler_runner": "<none>",
        "current_candidate_language_scope": "python_primary_text_workspace_not_cxx_compiler_pass",
        "compiler_pass_runner_ready": False,
        "cxx_decision_logic_ready": False,
        "evolve_block_compiler_span_ready": False,
        "compiler_rebuild_ready": False,
        "macro_benchmark_ready": False,
        "autotuning_ready": False,
        "llvm_inlining_rows_ready": False,
        "register_allocation_rows_ready": False,
        "xla_rows_ready": False,
        "baseline_generalization_rows_ready": False,
        "repository_runtime_verified": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            suffix = "overclaim" if expected_value is False else "mismatch"
            issues.append(_issue(f"local_evidence_{field}_{suffix}", f"local_evidence.{field} must preserve current Magellan boundary"))


def _validate_reported_tasks(value: object, issues: list[MagellanBoundaryIssue]) -> None:
    expected = [
        "LLVM function inlining for binary size",
        "LLVM function inlining for end-to-end performance",
        "LLVM register-allocation live-range priority",
        "XLA graph extraction",
        "XLA auto-sharding",
    ]
    if value != expected:
        issues.append(_issue("reported_task_mismatch", "reported_tasks must preserve Magellan task labels"))


def _validate_required_fields(
    value: object,
    issues: list[MagellanBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    if seen != expected:
        issues.append(_issue("required_evidence_field_mismatch", "required_evidence_fields must preserve Magellan evidence gates"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[MagellanBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    if set(value) != set(EXPECTED_MISSING_EVIDENCE):
        issues.append(_issue("missing_evidence_key_mismatch", "missing_evidence must preserve Magellan artifact-gap keys"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(value)


def _issue(code: str, message: str) -> MagellanBoundaryIssue:
    return MagellanBoundaryIssue(code, message)
