from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REGISTRY_PATH = Path(__file__).with_name("alphaevolve_ablations.json")
REGISTRY_SCHEMA = "libreevolve.alphaevolve_ablation_registry.v1"
REPORT_SCHEMA = "libreevolve.alphaevolve_ablation_report.v1"
EXPECTED_VARIANT_IDS = (
    "full_system",
    "no_evolution",
    "no_context_in_prompt",
    "no_meta_prompt_evolution",
    "no_full_file_evolution",
    "small_base_llm_only",
)
STATUSES = frozenset({"definition_only", "implemented", "reported"})
VARIANT_ROLES = frozenset({"baseline", "ablation"})
ASSERTION_OPERATORS = frozenset({"equals", "not_equals", "in", "gt", "gte", "lt", "lte"})
NO_FULL_FILE_EVOLUTION_SCOPE_BOUNDARY = {
    "alphaevolve_setup": "tensor_decomposition_loss_function_only",
    "current_scope": "localized_diff_single_primary_python_file_no_topology",
    "paper_match_status": "not_equivalent",
}
NO_FULL_FILE_EVOLUTION_REQUIRED_EVIDENCE = frozenset({
    "tensor_decomposition_benchmark_target",
    "loss_function_only_edit_surface",
    "executed_prompt_history",
    "candidate_edit_surface_audit",
})
NO_CONTEXT_IN_PROMPT_SCOPE_BOUNDARY = {
    "alphaevolve_setup": "explicit_problem_specific_context_removed",
    "current_scope": "parent_inspiration_failure_plugin_context_disabled",
    "paper_match_status": "over_broad_not_equivalent",
}
NO_CONTEXT_IN_PROMPT_REQUIRED_EVIDENCE = frozenset({
    "explicit_context_source_absence_prompt_history",
    "prompt_section_classification",
    "core_evolutionary_prompt_ingredients_audit",
    "no_evolution_separation",
})
SMALL_BASE_LLM_ONLY_SCOPE_BOUNDARY = {
    "alphaevolve_setup": "single_small_base_model_generation_only",
    "current_scope": "declarative_single_backend_small_base_labels",
    "paper_match_status": "telemetry_unproven",
}
SMALL_BASE_LLM_ONLY_REQUIRED_EVIDENCE = frozenset({
    "backend_capability_metadata",
    "mutation_generation_call_ledger",
    "no_large_model_route_or_fallback",
    "role_scope_generation_only",
})
REQUIRED_REPORT_FIELDS = frozenset({
    "variant_id",
    "target_id",
    "seed",
    "budget_fraction",
    "score",
    "consumed_budget",
    "component_assertions",
})
_ID_RE = re.compile(r"[a-z][a-z0-9_]{1,79}")


@dataclass(frozen=True)
class AblationRegistryIssue:
    code: str
    message: str
    variant_id: str | None = None


@dataclass(frozen=True)
class AblationRegistryReport:
    ok: bool
    variant_count: int
    baseline_count: int
    ablation_count: int
    issues: list[AblationRegistryIssue]


def validate_ablation_registry(path: str | Path = REGISTRY_PATH) -> AblationRegistryReport:
    registry_path = Path(path)
    issues: list[AblationRegistryIssue] = []
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return AblationRegistryReport(False, 0, 0, 0, [
            AblationRegistryIssue("read_error", f"failed to read registry: {exc}")
        ])
    except json.JSONDecodeError as exc:
        return AblationRegistryReport(False, 0, 0, 0, [
            AblationRegistryIssue("invalid_json", f"invalid registry JSON: {exc.msg}")
        ])
    if not isinstance(data, dict):
        return AblationRegistryReport(False, 0, 0, 0, [
            AblationRegistryIssue("invalid_shape", "registry must be a JSON object")
        ])
    if data.get("schema") != REGISTRY_SCHEMA:
        issues.append(AblationRegistryIssue("invalid_schema", "unsupported registry schema"))
    if data.get("source_paper_id") != "2506.13131":
        issues.append(AblationRegistryIssue("invalid_source", "source_paper_id must be 2506.13131"))
    _validate_report_contract(data.get("report_contract"), issues)
    variants = data.get("variants")
    if not isinstance(variants, list):
        return AblationRegistryReport(False, 0, 0, 0, issues + [
            AblationRegistryIssue("invalid_variants", "variants must be a list")
        ])

    seen: set[str] = set()
    baseline_count = 0
    ablation_count = 0
    for index, variant in enumerate(variants):
        variant_id = _variant_id(variant, index)
        if not isinstance(variant, dict):
            issues.append(AblationRegistryIssue("invalid_variant", "variant must be an object", variant_id))
            continue
        _validate_variant(variant, variant_id, issues)
        if variant_id in seen:
            issues.append(AblationRegistryIssue("duplicate_variant", "duplicate variant id", variant_id))
        seen.add(variant_id)
        if variant.get("variant_role") == "baseline":
            baseline_count += 1
        elif variant.get("variant_role") == "ablation":
            ablation_count += 1
    missing = set(EXPECTED_VARIANT_IDS) - seen
    extra = seen - set(EXPECTED_VARIANT_IDS)
    for variant_id in sorted(missing):
        issues.append(AblationRegistryIssue("missing_variant", "missing AlphaEvolve ablation variant", variant_id))
    for variant_id in sorted(extra):
        issues.append(AblationRegistryIssue("extra_variant", "unknown AlphaEvolve ablation variant", variant_id))
    if baseline_count != 1:
        issues.append(AblationRegistryIssue("invalid_baseline_count", "registry must contain exactly one baseline variant"))
    return AblationRegistryReport(
        ok=not issues,
        variant_count=len(variants),
        baseline_count=baseline_count,
        ablation_count=ablation_count,
        issues=issues,
    )


def _validate_report_contract(value: object, issues: list[AblationRegistryIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AblationRegistryIssue("invalid_report_contract", "report_contract must be an object"))
        return
    if value.get("schema") != REPORT_SCHEMA:
        issues.append(AblationRegistryIssue("invalid_report_schema", "unsupported report schema"))
    if value.get("budget_axis") != "fraction_of_equal_compute_budget":
        issues.append(AblationRegistryIssue("invalid_budget_axis", "budget axis must be fraction_of_equal_compute_budget"))
    fractions = value.get("required_budget_fractions")
    if not isinstance(fractions, list) or not fractions:
        issues.append(AblationRegistryIssue("invalid_budget_fractions", "required_budget_fractions must be a non-empty list"))
    else:
        previous = -1.0
        for fraction in fractions:
            if isinstance(fraction, bool) or not isinstance(fraction, (int, float)):
                issues.append(AblationRegistryIssue("invalid_budget_fraction", "budget fractions must be numeric"))
                continue
            numeric = float(fraction)
            if numeric < 0.0 or numeric > 1.0 or numeric <= previous:
                issues.append(AblationRegistryIssue("invalid_budget_fraction", "budget fractions must increase within [0, 1]"))
            previous = numeric
    seed_policy = value.get("seed_policy")
    if not isinstance(seed_policy, dict) or seed_policy.get("independent_seed_count") != 3:
        issues.append(AblationRegistryIssue("invalid_seed_policy", "seed_policy must require three independent seeds"))
    target_policy = value.get("target_policy")
    if not isinstance(target_policy, dict) or not isinstance(target_policy.get("target_set"), str):
        issues.append(AblationRegistryIssue("invalid_target_policy", "target_policy.target_set is required"))
    fields = value.get("required_result_fields")
    if not isinstance(fields, list) or set(fields) != REQUIRED_REPORT_FIELDS:
        issues.append(AblationRegistryIssue("invalid_required_result_fields", "required_result_fields must match the ablation report contract"))


def _validate_variant(
    variant: dict[str, Any],
    variant_id: str,
    issues: list[AblationRegistryIssue],
) -> None:
    if _ID_RE.fullmatch(variant_id) is None:
        issues.append(AblationRegistryIssue("invalid_variant_id", "variant id must be snake_case", variant_id))
    _require_text(variant, "name", variant_id, issues)
    if variant.get("status") not in STATUSES:
        issues.append(AblationRegistryIssue("invalid_status", "invalid variant status", variant_id))
    role = variant.get("variant_role")
    if role not in VARIANT_ROLES:
        issues.append(AblationRegistryIssue("invalid_variant_role", "invalid variant role", variant_id))
    components = variant.get("disable_components")
    if not isinstance(components, list) or not all(isinstance(item, str) and item for item in components):
        issues.append(AblationRegistryIssue("invalid_disable_components", "disable_components must be a list of non-empty strings", variant_id))
    elif role == "ablation" and not components:
        issues.append(AblationRegistryIssue("missing_disabled_component", "ablation variants must disable at least one component", variant_id))
    elif role == "baseline" and components:
        issues.append(AblationRegistryIssue("unexpected_disabled_component", "baseline variant must not disable components", variant_id))
    assertions = variant.get("required_config_assertions")
    if not isinstance(assertions, list) or not assertions:
        issues.append(AblationRegistryIssue("missing_config_assertions", "required_config_assertions must be non-empty", variant_id))
    else:
        for assertion in assertions:
            _validate_assertion(assertion, variant_id, issues)
    _require_text(variant, "paper_label", variant_id, issues)
    _require_text(variant, "rationale", variant_id, issues)
    citations = variant.get("paper_citations")
    if not isinstance(citations, list) or "2506.13131" not in citations:
        issues.append(AblationRegistryIssue("missing_alphaevolve_citation", "paper_citations must include 2506.13131", variant_id))
    if variant_id == "no_full_file_evolution":
        _validate_variant_scope_boundary(
            variant.get("paper_scope_boundary"),
            variant_id,
            expected_fields=NO_FULL_FILE_EVOLUTION_SCOPE_BOUNDARY,
            expected_evidence=NO_FULL_FILE_EVOLUTION_REQUIRED_EVIDENCE,
            missing_code="missing_no_full_file_scope_boundary",
            invalid_boundary_code="invalid_no_full_file_scope_boundary",
            invalid_evidence_code="invalid_no_full_file_future_evidence",
            missing_message="No full-file evolution must record its AlphaEvolve loss-function-only boundary",
            evidence_message="No full-file evolution boundary must list the required future evidence",
            issues=issues,
        )
    if variant_id == "no_context_in_prompt":
        _validate_variant_scope_boundary(
            variant.get("paper_scope_boundary"),
            variant_id,
            expected_fields=NO_CONTEXT_IN_PROMPT_SCOPE_BOUNDARY,
            expected_evidence=NO_CONTEXT_IN_PROMPT_REQUIRED_EVIDENCE,
            missing_code="missing_no_context_scope_boundary",
            invalid_boundary_code="invalid_no_context_scope_boundary",
            invalid_evidence_code="invalid_no_context_future_evidence",
            missing_message="No context in the prompt must record its explicit-context boundary",
            evidence_message="No context in the prompt boundary must list the required future evidence",
            issues=issues,
        )
    if variant_id == "small_base_llm_only":
        _validate_variant_scope_boundary(
            variant.get("paper_scope_boundary"),
            variant_id,
            expected_fields=SMALL_BASE_LLM_ONLY_SCOPE_BOUNDARY,
            expected_evidence=SMALL_BASE_LLM_ONLY_REQUIRED_EVIDENCE,
            missing_code="missing_small_base_llm_scope_boundary",
            invalid_boundary_code="invalid_small_base_llm_scope_boundary",
            invalid_evidence_code="invalid_small_base_llm_future_evidence",
            missing_message="Small base LLM only must record its backend-telemetry boundary",
            evidence_message="Small base LLM only boundary must list the required future evidence",
            issues=issues,
        )


def _validate_assertion(
    assertion: object,
    variant_id: str,
    issues: list[AblationRegistryIssue],
) -> None:
    if not isinstance(assertion, dict):
        issues.append(AblationRegistryIssue("invalid_config_assertion", "config assertion must be an object", variant_id))
        return
    if not isinstance(assertion.get("field"), str) or not assertion["field"]:
        issues.append(AblationRegistryIssue("invalid_assertion_field", "config assertion field is required", variant_id))
    if assertion.get("operator") not in ASSERTION_OPERATORS:
        issues.append(AblationRegistryIssue("invalid_assertion_operator", "unsupported config assertion operator", variant_id))
    if "value" not in assertion:
        issues.append(AblationRegistryIssue("missing_assertion_value", "config assertion value is required", variant_id))


def _validate_variant_scope_boundary(
    value: object,
    variant_id: str,
    *,
    expected_fields: dict[str, str],
    expected_evidence: frozenset[str],
    missing_code: str,
    invalid_boundary_code: str,
    invalid_evidence_code: str,
    missing_message: str,
    evidence_message: str,
    issues: list[AblationRegistryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(AblationRegistryIssue(
            missing_code,
            missing_message,
            variant_id,
        ))
        return
    for field, expected in expected_fields.items():
        if value.get(field) != expected:
            issues.append(AblationRegistryIssue(
                invalid_boundary_code,
                f"paper_scope_boundary.{field} must be {expected}",
                variant_id,
            ))
    evidence = value.get("required_future_evidence")
    if not isinstance(evidence, list) or set(evidence) != expected_evidence:
        issues.append(AblationRegistryIssue(
            invalid_evidence_code,
            evidence_message,
            variant_id,
        ))


def _variant_id(variant: object, index: int) -> str:
    if isinstance(variant, dict) and isinstance(variant.get("id"), str):
        return variant["id"]
    return f"variant_{index}"


def _require_text(
    value: dict[str, Any],
    field: str,
    variant_id: str,
    issues: list[AblationRegistryIssue],
) -> None:
    raw = value.get(field)
    if not isinstance(raw, str) or not raw.strip():
        issues.append(AblationRegistryIssue(f"missing_{field}", f"{field} is required", variant_id))
