from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SORTING_NETWORK_REDISCOVERY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_sorting_network_rediscovery_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_PROBLEM_IDS = ("sorting_network_8", "sorting_network_9")
EXPECTED_BOUNDARY_STATUS = "executable_candidate_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "exhaustive_zero_one_validation",
    "known_comparator_target_checks",
    "valid_seed_network_provenance",
    "benchmark_scope_registry_records",
    "hardening_bundle_artifacts",
    "clean_checkout_run_contract",
    "benchmark_goal_prompt_artifact",
    "zero_one_principle_source_citation",
    "known_target_source_citations",
    "fixed_evaluator_model_budget_protocol",
    "repeated_seed_run_tables",
    "target_hit_rate_summary",
    "run_tied_hardening_certification",
    "best_candidate_artifact_hashes",
    "failure_and_invalid_candidate_summary",
    "paper_facing_certification_row",
    "rediscovery_not_sota_claim_boundary",
)
EXPECTED_MISSING_EVIDENCE = {
    "zero_one_principle_source_citation": "not_recorded_locally",
    "known_target_source_citations": "not_recorded_locally",
    "fixed_evaluator_model_budget_protocol": (
        "contract_recorded_no_authenticated_run_evidence"
    ),
    "repeated_seed_run_tables": "not_recorded_locally",
    "target_hit_rate_summary": "not_recorded_locally",
    "run_tied_hardening_certification": "not_recorded_locally",
    "best_candidate_artifact_hashes": "not_recorded_locally",
    "failure_and_invalid_candidate_summary": "not_recorded_locally",
    "paper_facing_certification_row": "not_recorded_locally",
}


@dataclass(frozen=True)
class SortingNetworkRediscoveryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SortingNetworkRediscoveryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    problem_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[SortingNetworkRediscoveryBoundaryIssue]


def sorting_network_rediscovery_boundary_record() -> dict[str, Any]:
    """Return the current sorting-network rediscovery evidence boundary."""

    return {
        "schema": SORTING_NETWORK_REDISCOVERY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "problem_ids": list(EXPECTED_PROBLEM_IDS),
        "source_claim": (
            "AlphaEvolve-style benchmark evidence needs automated verification, "
            "fixed run conditions, repeated-run outcomes, and paper-facing "
            "certification before local executable fixtures can be cited as "
            "rediscovery evidence"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "candidate_status": "bounded_sorting_network_fixtures_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "implemented_candidate_evidence": {
            "sorting_network_8": {
                "wire_count": 8,
                "binary_inputs_checked": 256,
                "valid_seed_comparators": 28,
                "known_target_comparators": 19,
                "scope": "non_comparable_benchmark_candidate",
            },
            "sorting_network_9": {
                "wire_count": 9,
                "binary_inputs_checked": 512,
                "valid_seed_comparators": 36,
                "known_target_comparators": 25,
                "scope": "non_comparable_benchmark_candidate",
                "clean_checkout_run_contract": (
                    "libreevolve/problems/examples/sorting_network_9/"
                    "run_contract.json"
                ),
                "benchmark_goal_prompt_artifact": (
                    "libreevolve/problems/examples/sorting_network_9/"
                    "benchmark_goal_prompt.json"
                ),
            },
        },
        "claim_boundary": (
            "This boundary records that LibreEvolve has executable 8- and "
            "9-input sorting-network benchmark candidates with exhaustive "
            "zero-one validation, valid baseline seeds, checked known target "
            "networks, helper-generated generic hardening artifacts, a clean-"
            "checkout run contract for sorting_network_9, and a bounded "
            "benchmark goal-prompt artifact, but does not claim source-cited "
            "benchmark calibration, fixed-budget repeated-run rediscovery, "
            "run-tied hardening certification, best candidate artifact hashes, "
            "failure/invalid-candidate summaries, paper-facing certification "
            "rows, or novel SOTA results."
        ),
    }


def validate_sorting_network_rediscovery_boundary(
    boundary: object | str | Path | None = None,
) -> SortingNetworkRediscoveryBoundaryValidation:
    data, read_issues = _load_boundary(
        sorting_network_rediscovery_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return SortingNetworkRediscoveryBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[SortingNetworkRediscoveryBoundaryIssue] = []
    if data.get("schema") != SORTING_NETWORK_REDISCOVERY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported sorting-network rediscovery boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    problem_count = _validate_problem_ids(data.get("problem_ids"), issues)
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "rediscovery evidence" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify rediscovery evidence requirements"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("candidate_status") != "bounded_sorting_network_fixtures_available":
        issues.append(_issue("invalid_candidate_status", "candidate_status must stay scoped to executable fixtures"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "sorting-network boundary must not claim certified rediscovery"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    _validate_candidate_evidence(data.get("implemented_candidate_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim certified rediscovery"))
    return SortingNetworkRediscoveryBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        problem_count=problem_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_sorting_network_rediscovery_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_sorting_network_rediscovery_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve sorting-network rediscovery boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| problem_count | {validation.problem_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[SortingNetworkRediscoveryBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "sorting-network rediscovery boundary must be a JSON object")]


def _validate_problem_ids(
    value: object,
    issues: list[SortingNetworkRediscoveryBoundaryIssue],
) -> int:
    if value != list(EXPECTED_PROBLEM_IDS):
        issues.append(_issue("invalid_problem_ids", "problem_ids must list sorting_network_8 and sorting_network_9 in order"))
        return len(value) if isinstance(value, list) else 0
    return len(EXPECTED_PROBLEM_IDS)


def _validate_required_fields(
    value: object,
    issues: list[SortingNetworkRediscoveryBoundaryIssue],
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
    issues: list[SortingNetworkRediscoveryBoundaryIssue],
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


def _validate_candidate_evidence(
    value: object,
    issues: list[SortingNetworkRediscoveryBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_candidate_evidence", "implemented_candidate_evidence must be an object"))
        return
    expected = {
        "sorting_network_8": (8, 256, 28, 19),
        "sorting_network_9": (9, 512, 36, 25),
    }
    for problem_id, (wire_count, inputs, seed, target) in expected.items():
        record = value.get(problem_id)
        if not isinstance(record, dict):
            issues.append(_issue(f"missing_candidate_{problem_id}", f"candidate evidence missing {problem_id}"))
            continue
        checks = {
            "wire_count": wire_count,
            "binary_inputs_checked": inputs,
            "valid_seed_comparators": seed,
            "known_target_comparators": target,
            "scope": "non_comparable_benchmark_candidate",
        }
        for key, expected_value in checks.items():
            if record.get(key) != expected_value:
                issues.append(_issue(f"invalid_candidate_{problem_id}_{key}", f"{problem_id}.{key} must be {expected_value!r}"))
        if problem_id == "sorting_network_9":
            expected_contract = (
                "libreevolve/problems/examples/sorting_network_9/"
                "run_contract.json"
            )
            if record.get("clean_checkout_run_contract") != expected_contract:
                issues.append(
                    _issue(
                        "invalid_candidate_sorting_network_9_clean_checkout_run_contract",
                        f"sorting_network_9.clean_checkout_run_contract must be {expected_contract!r}",
                    )
                )
            expected_prompt = (
                "libreevolve/problems/examples/sorting_network_9/"
                "benchmark_goal_prompt.json"
            )
            if record.get("benchmark_goal_prompt_artifact") != expected_prompt:
                issues.append(
                    _issue(
                        "invalid_candidate_sorting_network_9_benchmark_goal_prompt_artifact",
                        f"sorting_network_9.benchmark_goal_prompt_artifact must be {expected_prompt!r}",
                    )
                )


def _issue(code: str, message: str) -> SortingNetworkRediscoveryBoundaryIssue:
    return SortingNetworkRediscoveryBoundaryIssue(code, message)
