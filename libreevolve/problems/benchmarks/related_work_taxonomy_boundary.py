from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RELATED_WORK_TAXONOMY_BOUNDARY_SCHEMA = (
    "libreevolve.related_work_taxonomy_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("5",)
EXPECTED_BOUNDARY_STATUS = (
    "related_work_taxonomy_records_without_positioning_readiness"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_paper_inventory",
    "paper_index_status_rows",
    "individual_source_gap_todos",
    "related_work_taxonomy_records",
    "related_work_source_id_map",
    "method_family_taxonomy",
    "candidate_representation_taxonomy",
    "feedback_signal_taxonomy",
    "task_stage_taxonomy",
    "comparison_axis_taxonomy",
    "source_category_citations",
    "alphaevolve_positioning_claim_table",
    "readme_related_work_summary_gate",
    "roadmap_related_work_summary_gate",
    "paper_index_related_work_summary_gate",
    "local_implementation_status_taxonomy",
)
EXPECTED_MISSING_EVIDENCE = {
    "exhaustive_reference_level_coverage": "not_recorded_locally",
    "independent_positioning_review": "not_recorded_locally",
    "local_implementation_parity_evidence": "not_recorded_locally",
    "benchmark_reproduction_evidence": "not_recorded_locally",
}
EXPECTED_TAXONOMY_RECORD_IDS = (
    "alphaevolve",
    "pre_llm_superoptimization",
    "alphatensor",
    "funsearch",
    "gpu_kernel_llm_agents",
    "multi_agent_llm_problem_solving",
    "ai_coscientist",
    "broader_ai_for_science",
    "formal_and_informal_proof_search",
    "continuous_llm_finetuning",
    "llm_directed_concept_learning",
)
EXPECTED_CLAIM_GATES = {
    "readme_related_work_summary_gate": "scoped_to_taxonomy_boundary",
    "roadmap_related_work_summary_gate": "scoped_to_taxonomy_boundary",
    "paper_index_related_work_summary_gate": "scoped_to_taxonomy_boundary",
}


def _related_work_taxonomy_records() -> list[dict[str, str]]:
    return [
        {
            "source_id": "alphaevolve",
            "source_location": "AlphaEvolve Section 5 Related Work, PDF pages 18-20",
            "method_family": "execution_feedback_code_superoptimization",
            "candidate_representation": "executable_code_programs",
            "feedback_or_evidence_mode": "code_execution_and_programmatic_evaluation",
            "task_stage": "algorithm_discovery_and_scientific_optimization",
            "comparison_axis": "central_method_positioning",
            "comparison_claim": (
                "AlphaEvolve iteratively improves programs using execution feedback"
            ),
            "complementary_mechanism_status": "primary_system",
            "proof_or_witness_status": "not_a_proof_search_system",
            "local_implementation_status": "partial_local_surface",
        },
        {
            "source_id": "pre_llm_superoptimization",
            "source_location": "AlphaEvolve Section 5 Related Work, PDF page 20",
            "method_family": "enumeration_genetic_monte_carlo_deep_rl",
            "candidate_representation": "programs_or_search_states",
            "feedback_or_evidence_mode": "programmatic_objective_feedback",
            "task_stage": "pre_llm_code_superoptimization",
            "comparison_axis": "historical_baseline_methods",
            "comparison_claim": (
                "pre-LLM superoptimization included enumeration, genetic search, "
                "Monte Carlo sampling, and deep reinforcement learning"
            ),
            "complementary_mechanism_status": "background_baseline",
            "proof_or_witness_status": "not_classified_as_proof_search",
            "local_implementation_status": "background_only",
        },
        {
            "source_id": "alphatensor",
            "source_location": "AlphaEvolve Section 5 Related Work, PDF page 20",
            "method_family": "limited_domain_algorithm_discovery",
            "candidate_representation": "tensor_decomposition_algorithms",
            "feedback_or_evidence_mode": "domain_programmatic_correctness",
            "task_stage": "matrix_multiplication_algorithm_discovery",
            "comparison_axis": "single_problem_algorithm_discovery_baseline",
            "comparison_claim": (
                "AlphaTensor is cited as a limited-setting system that discovered "
                "provably correct algorithms"
            ),
            "complementary_mechanism_status": "background_baseline",
            "proof_or_witness_status": "provably_correct_algorithm_context",
            "local_implementation_status": "background_only",
        },
        {
            "source_id": "funsearch",
            "source_location": "AlphaEvolve Section 5 Related Work, PDF pages 19-20",
            "method_family": "llm_guided_program_evolution",
            "candidate_representation": "single_python_function",
            "feedback_or_evidence_mode": "programmatic_evaluator_feedback",
            "task_stage": "mathematical_witness_discovery",
            "comparison_axis": "direct_predecessor_and_complement",
            "comparison_claim": (
                "AlphaEvolve extends FunSearch beyond single-function, "
                "single-objective, code-trained-LLM constraints"
            ),
            "complementary_mechanism_status": "predecessor_and_complement",
            "proof_or_witness_status": "witness_or_counterexample_discovery",
            "local_implementation_status": "partial_local_surface",
        },
        {
            "source_id": "gpu_kernel_llm_agents",
            "source_location": "AlphaEvolve Section 5 Related Work, PDF page 20",
            "method_family": "llm_code_optimization_agents",
            "candidate_representation": "gpu_kernel_or_operation_code",
            "feedback_or_evidence_mode": "execution_performance_feedback",
            "task_stage": "systems_code_optimization",
            "comparison_axis": "adjacent_llm_superoptimization",
            "comparison_claim": (
                "LLM agents have optimized attention kernels and user-specified "
                "operations in narrower systems settings"
            ),
            "complementary_mechanism_status": "adjacent_background",
            "proof_or_witness_status": "not_classified_as_proof_search",
            "local_implementation_status": "background_only",
        },
        {
            "source_id": "multi_agent_llm_problem_solving",
            "source_location": "AlphaEvolve Section 5 Related Work, PDF page 20",
            "method_family": "llm_multi_agent_problem_solving",
            "candidate_representation": "agent_conversation_outputs",
            "feedback_or_evidence_mode": "conversation_and_task_feedback",
            "task_stage": "problem_solving_coordination",
            "comparison_axis": "adjacent_llm_agent_method",
            "comparison_claim": (
                "multi-agent LLM systems are related but are not the same as "
                "AlphaEvolve's execution-grounded program evolution loop"
            ),
            "complementary_mechanism_status": "adjacent_background",
            "proof_or_witness_status": "not_classified_as_proof_search",
            "local_implementation_status": "background_only",
        },
        {
            "source_id": "ai_coscientist",
            "source_location": "AlphaEvolve Section 5 Related Work, PDF page 19",
            "method_family": "ai_for_science_hypothesis_generation",
            "candidate_representation": "natural_language_hypotheses",
            "feedback_or_evidence_mode": "natural_language_or_literature_evidence",
            "task_stage": "scientific_hypothesis_generation",
            "comparison_axis": "representation_and_evaluation_contrast",
            "comparison_claim": (
                "AlphaEvolve differs from most scientific-discovery systems by "
                "using programmatic representations and evaluation metrics"
            ),
            "complementary_mechanism_status": "possible_future_combination",
            "proof_or_witness_status": "not_classified_as_proof_search",
            "local_implementation_status": "not_implemented",
        },
        {
            "source_id": "broader_ai_for_science",
            "source_location": "AlphaEvolve Section 5 Related Work, PDF page 20",
            "method_family": "ai_for_science",
            "candidate_representation": "domain_specific_hypotheses_or_artifacts",
            "feedback_or_evidence_mode": "domain_experiment_or_model_evidence",
            "task_stage": "scientific_discovery_support",
            "comparison_axis": "broader_research_context",
            "comparison_claim": (
                "AlphaEvolve is positioned within AI-for-science while emphasizing "
                "programmatic hypothesis representations and metrics"
            ),
            "complementary_mechanism_status": "background_context",
            "proof_or_witness_status": "varies_by_source",
            "local_implementation_status": "background_only",
        },
        {
            "source_id": "formal_and_informal_proof_search",
            "source_location": "AlphaEvolve Section 5 Related Work, PDF page 20",
            "method_family": "proof_search",
            "candidate_representation": "formal_or_informal_proofs",
            "feedback_or_evidence_mode": "proof_validation_or_human_reasoning",
            "task_stage": "mathematical_proof_discovery",
            "comparison_axis": "proof_versus_witness_distinction",
            "comparison_claim": (
                "witness and counterexample discovery is complementary to formal "
                "and informal proof search"
            ),
            "complementary_mechanism_status": "complementary",
            "proof_or_witness_status": "proof_search_context",
            "local_implementation_status": "not_implemented",
        },
        {
            "source_id": "continuous_llm_finetuning",
            "source_location": "AlphaEvolve Section 5 Related Work, PDF page 19",
            "method_family": "llm_finetuning",
            "candidate_representation": "model_policy_updates",
            "feedback_or_evidence_mode": "reinforcement_learning_signal",
            "task_stage": "search_policy_improvement",
            "comparison_axis": "complementary_mechanism",
            "comparison_claim": (
                "continuous LLM fine-tuning through reinforcement learning is an "
                "adjacent idea needing more investigation at AlphaEvolve scale"
            ),
            "complementary_mechanism_status": "needs_scale_investigation",
            "proof_or_witness_status": "not_classified_as_proof_search",
            "local_implementation_status": "not_implemented",
        },
        {
            "source_id": "llm_directed_concept_learning",
            "source_location": "AlphaEvolve Section 5 Related Work, PDF page 19",
            "method_family": "concept_learning",
            "candidate_representation": "concepts_over_high_performing_programs",
            "feedback_or_evidence_mode": "program_population_analysis",
            "task_stage": "search_guidance_from_elites",
            "comparison_axis": "complementary_mechanism",
            "comparison_claim": (
                "LLM-directed concept learning over high-performing programs is "
                "an adjacent idea needing more investigation at AlphaEvolve scale"
            ),
            "complementary_mechanism_status": "needs_scale_investigation",
            "proof_or_witness_status": "not_classified_as_proof_search",
            "local_implementation_status": "not_implemented",
        },
    ]


@dataclass(frozen=True)
class RelatedWorkTaxonomyBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RelatedWorkTaxonomyBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[RelatedWorkTaxonomyBoundaryIssue]


def related_work_taxonomy_boundary_record() -> dict[str, Any]:
    """Return the Related Work taxonomy boundary."""

    return {
        "schema": RELATED_WORK_TAXONOMY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 5 Related Work positions the system as "
            "execution-feedback code superoptimization and algorithm discovery "
            "against pre-LLM search, AlphaTensor, GPU-kernel and LLM-agent "
            "optimizers, AI-for-science systems, and proof discovery"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "paper_index_status": "taxonomy_records_with_individual_gap_rows",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "taxonomy_record_count": len(EXPECTED_TAXONOMY_RECORD_IDS),
        "taxonomy_records": _related_work_taxonomy_records(),
        "claim_gates": dict(EXPECTED_CLAIM_GATES),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has a source-paper "
            "inventory, paper-index status rows, individual source-gap TODOs, "
            "and bounded Section 5 Related Work taxonomy records covering "
            "method family, representation, evidence mode, task stage, "
            "comparison axis, complementary-mechanism status, proof/witness "
            "status, and local implementation status. It does not claim "
            "exhaustive reference-level coverage, independent positioning "
            "review, local implementation parity, benchmark reproduction, or "
            "release-ready AlphaEvolve positioning claims."
        ),
    }


def validate_related_work_taxonomy_boundary(
    boundary: object | str | Path | None = None,
) -> RelatedWorkTaxonomyBoundaryValidation:
    data, read_issues = _load_boundary(
        related_work_taxonomy_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return RelatedWorkTaxonomyBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[RelatedWorkTaxonomyBoundaryIssue] = []
    if data.get("schema") != RELATED_WORK_TAXONOMY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported related-work taxonomy boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['5']"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "Related Work" not in source_claim
        or "execution-feedback code superoptimization" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve Related Work positioning"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("paper_index_status") != "taxonomy_records_with_individual_gap_rows":
        issues.append(_issue("invalid_paper_index_status", "paper_index_status must record taxonomy rows with individual gap rows"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "related-work taxonomy boundary must not claim positioning readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    _validate_taxonomy_records(data.get("taxonomy_records"), data.get("taxonomy_record_count"), issues)
    _validate_claim_gates(data.get("claim_gates"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "bounded Section 5 Related Work taxonomy records" not in boundary_text
        or "does not claim exhaustive reference-level coverage" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate taxonomy records from positioning-readiness claims"))
    return RelatedWorkTaxonomyBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_related_work_taxonomy_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_related_work_taxonomy_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Related Work taxonomy boundary",
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
) -> tuple[dict[str, Any] | None, list[RelatedWorkTaxonomyBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "related-work taxonomy boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RelatedWorkTaxonomyBoundaryIssue],
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


def _validate_taxonomy_records(
    records: object,
    record_count: object,
    issues: list[RelatedWorkTaxonomyBoundaryIssue],
) -> None:
    if not isinstance(records, list):
        issues.append(_issue("invalid_taxonomy_records", "taxonomy_records must be a list"))
        return
    if record_count != len(records):
        issues.append(
            _issue(
                "invalid_taxonomy_record_count",
                "taxonomy_record_count must match taxonomy_records",
            )
        )
    required_fields = {
        "source_id",
        "source_location",
        "method_family",
        "candidate_representation",
        "feedback_or_evidence_mode",
        "task_stage",
        "comparison_axis",
        "comparison_claim",
        "complementary_mechanism_status",
        "proof_or_witness_status",
        "local_implementation_status",
    }
    observed_ids: set[str] = set()
    allowed_local_status = {
        "partial_local_surface",
        "background_only",
        "not_implemented",
    }
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append(_issue("invalid_taxonomy_record", f"taxonomy record {index} must be an object"))
            continue
        missing_fields = sorted(
            field
            for field in required_fields
            if not isinstance(record.get(field), str) or not record.get(field)
        )
        if missing_fields:
            issues.append(
                _issue(
                    "invalid_taxonomy_record_field",
                    f"taxonomy record {index} has missing fields: {', '.join(missing_fields)}",
                )
            )
        source_id = record.get("source_id")
        if isinstance(source_id, str):
            observed_ids.add(source_id)
        if "Section 5" not in str(record.get("source_location", "")):
            issues.append(
                _issue(
                    "invalid_taxonomy_record_source_location",
                    f"taxonomy record {index} must cite Section 5",
                )
            )
        if record.get("local_implementation_status") not in allowed_local_status:
            issues.append(
                _issue(
                    "invalid_taxonomy_record_local_status",
                    f"taxonomy record {index} local implementation status is unsupported",
                )
            )
        if record.get("local_implementation_status") == "implemented_full":
            issues.append(
                _issue(
                    "taxonomy_record_implementation_overclaim",
                    f"taxonomy record {index} must not claim full implementation",
                )
            )
    expected_ids = set(EXPECTED_TAXONOMY_RECORD_IDS)
    missing_ids = sorted(expected_ids - observed_ids)
    extra_ids = sorted(observed_ids - expected_ids)
    if missing_ids:
        issues.append(_issue("missing_taxonomy_record", f"missing taxonomy records: {', '.join(missing_ids)}"))
    if extra_ids:
        issues.append(_issue("extra_taxonomy_record", f"unknown taxonomy records: {', '.join(extra_ids)}"))


def _validate_claim_gates(
    gates: object,
    issues: list[RelatedWorkTaxonomyBoundaryIssue],
) -> None:
    if not isinstance(gates, dict):
        issues.append(_issue("invalid_claim_gates", "claim_gates must be an object"))
        return
    expected_keys = set(EXPECTED_CLAIM_GATES)
    actual_keys = set(gates)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_claim_gate", f"claim_gates lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_claim_gate", f"claim_gates has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_CLAIM_GATES.items():
        if gates.get(key) != expected_value:
            issues.append(_issue(f"invalid_claim_gate_{key}", f"claim_gates.{key} must be {expected_value}"))


def _validate_missing_evidence(
    value: object,
    issues: list[RelatedWorkTaxonomyBoundaryIssue],
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


def _issue(code: str, message: str) -> RelatedWorkTaxonomyBoundaryIssue:
    return RelatedWorkTaxonomyBoundaryIssue(code, message)
