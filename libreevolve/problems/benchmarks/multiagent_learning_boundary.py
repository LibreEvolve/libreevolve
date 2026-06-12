from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MULTIAGENT_LEARNING_BOUNDARY_SCHEMA = "libreevolve.multiagent_learning_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2602.16928"
EXPECTED_SOURCE_TITLE = "Discovering Multiagent Learning Algorithms with Large Language Models"
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2602.16928.pdf"
EXPECTED_SOURCE_FILE = "papers/2602.16928__Multiagent_Learning.pdf"
EXPECTED_SOURCE_SHA256 = (
    "21b4d32be45ead4199d348c60e8671b0c9b5e0d3ca6c16381e27c7e1e2fafd48"
)
EXPECTED_SOURCE_BYTES = 2196483
EXPECTED_BOUNDARY_STATUS = "marl_algorithm_context_without_cfr_psro_runtime_parity"
EXPECTED_COMPONENT_IDS = (
    "cfr_candidate_classes",
    "psro_meta_strategy_classes",
    "open_spiel_game_suite",
    "train_test_game_splits",
    "exploitability_metric",
    "exact_best_response_oracle",
    "vad_cfr_result_rows",
    "shor_psro_result_rows",
    "wop_cfr_distillation_rows",
    "pm_psro_distillation_rows",
    "human_baseline_comparisons",
    "iqm_ablation_audit",
    "random_normal_form_validation",
    "algorithm_artifact_provenance",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "alphaevolve_relation",
    "marl_fixture_policy",
    "cfr_candidate_schema",
    "psro_candidate_schema",
    "open_spiel_environment_records",
    "game_suite_taxonomy",
    "train_game_split_records",
    "test_game_split_records",
    "cfr_iteration_budget_records",
    "psro_iteration_budget_records",
    "exploitability_metric_definition",
    "exact_oracle_psro_records",
    "baseline_solver_identities",
    "vad_cfr_result_rows",
    "shor_psro_result_rows",
    "wop_cfr_distillation_rows",
    "pm_psro_distillation_rows",
    "iqm_log_improvement_ablation_records",
    "mechanism_coupling_records",
    "random_normal_form_validation_rows",
    "algorithm_source_artifact_hashes",
    "seed_and_budget_records",
    "open_spiel_version_records",
    "independent_checker_outputs",
)
EXPECTED_MISSING_EVIDENCE = {
    "cfr_candidate_schema": "not_implemented_locally",
    "psro_candidate_schema": "not_implemented_locally",
    "open_spiel_game_suite": "not_implemented_locally",
    "imperfect_information_game_fixture": "not_implemented_locally",
    "cfr_runtime_harness": "not_implemented_locally",
    "psro_runtime_harness": "not_implemented_locally",
    "exploitability_metric_records": "not_recorded_locally",
    "exact_best_response_oracle_records": "not_recorded_locally",
    "train_test_split_records": "not_recorded_locally",
    "baseline_solver_ledger": "not_recorded_locally",
    "vad_cfr_result_rows": "not_recorded_locally",
    "shor_psro_result_rows": "not_recorded_locally",
    "wop_cfr_distillation_rows": "not_recorded_locally",
    "pm_psro_distillation_rows": "not_recorded_locally",
    "iqm_ablation_records": "not_recorded_locally",
    "mechanism_coupling_records": "not_recorded_locally",
    "random_normal_form_validation_rows": "not_recorded_locally",
    "algorithm_artifact_hashes": "not_recorded_locally",
    "open_spiel_version_records": "not_recorded_locally",
    "seed_budget_records": "not_recorded_locally",
    "independent_checker_outputs": "not_recorded_locally",
    "dedicated_multiagent_learning_runtime_repository": "not_found_in_extracted_links",
}


@dataclass(frozen=True)
class MultiagentLearningBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class MultiagentLearningBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[MultiagentLearningBoundaryIssue]


def multiagent_learning_boundary_record() -> dict[str, Any]:
    """Return the current CFR/PSRO MARL absence boundary."""

    return {
        "schema": MULTIAGENT_LEARNING_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": [
            "Zun Li",
            "John Schultz",
            "Daniel Hennes",
            "Marc Lanctot",
        ],
        "source_version": "v3",
        "source_submitted_date": "2026-02-18",
        "source_last_revised_date": "2026-05-07",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://creativecommons.org/licenses/by/4.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2602.16928v3",
                "status": "source_version_reference_only",
            },
            {
                "url": "<no_dedicated_multiagent_learning_code_repository_extracted>",
                "status": "not_found_in_extracted_links",
            },
        ],
        "framework_components": [
            {
                "component_id": "cfr_candidate_classes",
                "paper_role": "evolvable RegretAccumulator, PolicyFromRegretAccumulator, and PolicyAccumulator classes",
                "local_status": "not_implemented",
            },
            {
                "component_id": "psro_meta_strategy_classes",
                "paper_role": "evolvable TrainMetaStrategySolver and EvalMetaStrategySolver classes",
                "local_status": "not_implemented",
            },
            {
                "component_id": "open_spiel_game_suite",
                "paper_role": "OpenSpiel imperfect-information game environments",
                "local_status": "not_implemented",
            },
            {
                "component_id": "train_test_game_splits",
                "paper_role": "four training games and fourteen held-out test games",
                "local_status": "not_recorded",
            },
            {
                "component_id": "exploitability_metric",
                "paper_role": "exact exploitability and negative-exploitability fitness",
                "local_status": "not_recorded",
            },
            {
                "component_id": "exact_best_response_oracle",
                "paper_role": "exact PSRO best-response oracle and payoff tensor updates",
                "local_status": "not_recorded",
            },
            {
                "component_id": "vad_cfr_result_rows",
                "paper_role": "VAD-CFR evolved regret-minimization result rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "shor_psro_result_rows",
                "paper_role": "SHOR-PSRO evolved meta-strategy result rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "wop_cfr_distillation_rows",
                "paper_role": "WOP-CFR distilled solver generalization rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "pm_psro_distillation_rows",
                "paper_role": "PM-PSRO distilled solver generalization rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "human_baseline_comparisons",
                "paper_role": "CFR/CFR+/LCFR/DCFR/PCFR+/DPCFR+/HS-PCFR+ and Uniform/Nash/AlphaRank/PRD/RM baselines",
                "local_status": "not_recorded",
            },
            {
                "component_id": "iqm_ablation_audit",
                "paper_role": "IQM log-improvement ablation and distillation audit",
                "local_status": "not_recorded",
            },
            {
                "component_id": "random_normal_form_validation",
                "paper_role": "random normal-form game validation rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "algorithm_artifact_provenance",
                "paper_role": "generated solver source listings, hashes, seeds, and budgets",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_marl_runner": "<none>",
            "current_candidate_language_scope": "python_primary_generic_workspace_not_cfr_psro_solver_api",
            "cfr_candidate_schema_ready": False,
            "psro_candidate_schema_ready": False,
            "open_spiel_fixture_ready": False,
            "game_suite_ready": False,
            "exploitability_metric_ready": False,
            "exact_oracle_ready": False,
            "cfr_result_rows_ready": False,
            "psro_result_rows_ready": False,
            "ablation_audit_ready": False,
            "distillation_rows_ready": False,
            "random_normal_form_rows_ready": False,
            "repository_runtime_verified": False,
        },
        "reported_tasks": [
            "CFR algorithm discovery over regret-minimization classes",
            "PSRO meta-strategy solver discovery",
            "18-game imperfect-information evaluation suite",
            "train-test split ablation and distillation",
            "random normal-form generalization validation",
        ],
        "reported_algorithms": [
            "VAD-CFR",
            "SHOR-PSRO",
            "WOP-CFR",
            "PM-PSRO",
        ],
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records Multiagent Learning as AlphaEvolve MARL "
            "algorithm-discovery context only. LibreEvolve currently does not "
            "claim CFR or PSRO candidate schemas, OpenSpiel imperfect-"
            "information game fixtures, exploitability metrics, exact "
            "best-response oracle records, VAD-CFR or SHOR-PSRO result rows, "
            "WOP-CFR or PM-PSRO distillation evidence, IQM ablation audits, "
            "random normal-form validation rows, human-designed baseline "
            "comparisons, generated solver artifact hashes, or reproducible "
            "CFR/PSRO runtime evidence."
        ),
    }


def validate_multiagent_learning_boundary(
    boundary: object | str | Path | None = None,
) -> MultiagentLearningBoundaryValidation:
    data, read_issues = _load_boundary(
        multiagent_learning_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MultiagentLearningBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MultiagentLearningBoundaryIssue] = []
    if data.get("schema") != MULTIAGENT_LEARNING_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Multiagent Learning boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2602.16928"))
    if data.get("source_title") != EXPECTED_SOURCE_TITLE:
        issues.append(_issue("invalid_source_title", "source_title must identify Multiagent Learning"))
    if data.get("source_version") != "v3":
        issues.append(_issue("invalid_source_version", "source_version must be v3"))
    if data.get("source_submitted_date") != "2026-02-18":
        issues.append(_issue("invalid_source_submitted_date", "source_submitted_date must be 2026-02-18"))
    if data.get("source_last_revised_date") != "2026-05-07":
        issues.append(_issue("invalid_source_last_revised_date", "source_last_revised_date must be 2026-05-07"))
    if data.get("source_url") != EXPECTED_SOURCE_URL:
        issues.append(_issue("invalid_source_url", "source_url must identify the arXiv PDF"))
    if data.get("source_file") != EXPECTED_SOURCE_FILE:
        issues.append(_issue("invalid_source_file", "source_file must identify the cached PDF"))
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
        issues.append(_issue("claim_ready_overclaim", "Multiagent Learning boundary must not claim CFR/PSRO runtime parity"))
    _validate_source_links(data.get("source_links"), issues)
    component_count = _validate_framework_components(data.get("framework_components"), issues)
    _validate_local_evidence(data.get("local_evidence"), issues)
    _validate_reported_tasks(data.get("reported_tasks"), issues)
    _validate_reported_algorithms(data.get("reported_algorithms"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that CFR/PSRO parity is not claimed"))
    return MultiagentLearningBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        component_count=component_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_multiagent_learning_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_multiagent_learning_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Multiagent Learning boundary",
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
) -> tuple[dict[str, Any] | None, list[MultiagentLearningBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Multiagent Learning boundary must be a JSON object")]


def _validate_source_links(value: object, issues: list[MultiagentLearningBoundaryIssue]) -> None:
    if not isinstance(value, list):
        issues.append(_issue("invalid_source_links", "source_links must be a list"))
        return
    urls = {item.get("url") for item in value if isinstance(item, dict)}
    expected_urls = {
        "https://arxiv.org/abs/2602.16928v3",
        "<no_dedicated_multiagent_learning_code_repository_extracted>",
    }
    if urls != expected_urls:
        issues.append(_issue("source_link_mismatch", "source_links must preserve Multiagent Learning source status"))
    allowed_statuses = {
        "source_version_reference_only",
        "not_found_in_extracted_links",
    }
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_source_link", "source link records must be objects"))
            continue
        if item.get("status") not in allowed_statuses:
            issues.append(_issue("source_link_status_overclaim", "source link status must not claim local CFR/PSRO runtime"))


def _validate_framework_components(value: object, issues: list[MultiagentLearningBoundaryIssue]) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_framework_components", "framework_components must be a list"))
        return 0
    ids = [item.get("component_id") for item in value if isinstance(item, dict)]
    if tuple(ids) != EXPECTED_COMPONENT_IDS:
        issues.append(_issue("framework_component_id_mismatch", "framework_components must preserve the Multiagent Learning component set"))
    allowed_statuses = {"not_implemented", "not_recorded"}
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_framework_component", "framework component records must be objects"))
            continue
        if item.get("component_id") in EXPECTED_COMPONENT_IDS and item.get("local_status") not in allowed_statuses:
            issues.append(_issue("framework_component_overclaim", "framework component local_status must not claim CFR/PSRO parity"))
    return len(value)


def _validate_local_evidence(value: object, issues: list[MultiagentLearningBoundaryIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_evidence", "local_evidence must be an object"))
        return
    expected = {
        "current_marl_runner": "<none>",
        "current_candidate_language_scope": "python_primary_generic_workspace_not_cfr_psro_solver_api",
        "cfr_candidate_schema_ready": False,
        "psro_candidate_schema_ready": False,
        "open_spiel_fixture_ready": False,
        "game_suite_ready": False,
        "exploitability_metric_ready": False,
        "exact_oracle_ready": False,
        "cfr_result_rows_ready": False,
        "psro_result_rows_ready": False,
        "ablation_audit_ready": False,
        "distillation_rows_ready": False,
        "random_normal_form_rows_ready": False,
        "repository_runtime_verified": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            suffix = "overclaim" if expected_value is False else "mismatch"
            issues.append(_issue(f"local_evidence_{field}_{suffix}", f"local_evidence.{field} must preserve current Multiagent Learning boundary"))


def _validate_reported_tasks(value: object, issues: list[MultiagentLearningBoundaryIssue]) -> None:
    expected = [
        "CFR algorithm discovery over regret-minimization classes",
        "PSRO meta-strategy solver discovery",
        "18-game imperfect-information evaluation suite",
        "train-test split ablation and distillation",
        "random normal-form generalization validation",
    ]
    if value != expected:
        issues.append(_issue("reported_task_mismatch", "reported_tasks must preserve Multiagent Learning task labels"))


def _validate_reported_algorithms(value: object, issues: list[MultiagentLearningBoundaryIssue]) -> None:
    expected = [
        "VAD-CFR",
        "SHOR-PSRO",
        "WOP-CFR",
        "PM-PSRO",
    ]
    if value != expected:
        issues.append(_issue("reported_algorithm_mismatch", "reported_algorithms must preserve Multiagent Learning algorithm labels"))


def _validate_required_fields(
    value: object,
    issues: list[MultiagentLearningBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    if seen != expected:
        issues.append(_issue("required_evidence_field_mismatch", "required_evidence_fields must preserve Multiagent Learning evidence gates"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[MultiagentLearningBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    if set(value) != set(EXPECTED_MISSING_EVIDENCE):
        issues.append(_issue("missing_evidence_key_mismatch", "missing_evidence must preserve Multiagent Learning artifact-gap keys"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(value)


def _issue(code: str, message: str) -> MultiagentLearningBoundaryIssue:
    return MultiagentLearningBoundaryIssue(code, message)
