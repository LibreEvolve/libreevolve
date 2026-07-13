from __future__ import annotations

import json
import unicodedata
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from libreevolve.problems.benchmarks.alphaevolve_source_inventory_boundary import (
    EXPECTED_NAMED_SOURCE_SPAN_IDS,
    SOURCE_PAPER_ID,
    SOURCE_PDF_PATH,
    alphaevolve_source_inventory_boundary_record,
)


ALPHAEVOLVE_SCHEDULING_CLAIM_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_scheduling_claim_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "section_3_3_1_figure_6_claim_inventory_complete_without_"
    "borg_fixture_or_result_reproduction"
)
EXPECTED_CLAIM_COUNT = 45
IMPLEMENTED_STATUS = "implemented_local"
INCOMPLETE_STATUSES = frozenset(
    {"partially_implemented", "not_implemented", "not_demonstrated"}
)


_TODO_SPECS = {
    "application": (
        "docs/todo/code.md",
        "Populate application-owner and domain-review provenance for practical",
    ),
    "calibration": (
        "docs/todo/code.md",
        "Populate Section 3.3 result-claim calibration fields for systems reports.",
    ),
    "comparator": (
        "docs/todo/code.md",
        "Add Borg incumbent-evolution and learned-policy comparator provenance.",
    ),
    "deployment": (
        "docs/todo/code.md",
        "Populate scheduling interpretability and deployment-readiness evidence",
    ),
    "figure6": (
        "docs/todo/code.md",
        "Add Figure 6 scheduling-heuristic exhibit provenance and heatmap",
    ),
    "formulation": (
        "docs/todo/code.md",
        "Populate Borg scheduling problem-formulation provenance.",
    ),
    "safety": (
        "docs/todo/code.md",
        "Populate scheduling ranking-only safety provenance for Borg-style",
    ),
    "systems_fixtures": (
        "docs/todo/code.md",
        "Connect real systems fixtures to held-out and reference-correctness",
    ),
}


def _claim(
    claim_id: str,
    source_span_id: str,
    source_page: int,
    source_anchor: str,
    claim: str,
    category: str,
    implementation_status: str,
    evidence_paths: tuple[str, ...],
    todo_ids: tuple[str, ...],
    roadmap_section_id: str = "representative_benchmarks",
    roadmap_phase: str = "longer_term",
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "source_span_id": source_span_id,
        "source_page": source_page,
        "source_anchor": source_anchor,
        "claim": claim,
        "category": category,
        "implementation_status": implementation_status,
        "roadmap_section_id": roadmap_section_id,
        "roadmap_phase": roadmap_phase,
        "evidence_paths": evidence_paths,
        "todo_ids": todo_ids,
    }


_SYSTEMS_EVIDENCE = (
    "libreevolve/problems/benchmarks/systems_results.py",
    "papers/systems_result_readiness_boundary.json",
)
_FIGURE6_EVIDENCE = (
    "papers/figure6_scheduling_exhibit_boundary.json",
    "papers/systems_result_readiness_boundary.json",
)


SCHEDULING_CLAIM_SPECS = (
    _claim(
        "section3_3_mission_critical_infrastructure_real_world_impact",
        "section_3_3",
        13,
        "improve performance of mission-critical infrastructure and deliver real-world impact",
        "Demonstrate performance improvements to mission-critical infrastructure with real-world impact.",
        "systems_application_scope",
        "not_demonstrated",
        ("papers/systems_result_readiness_boundary.json",),
        ("systems_fixtures", "application"),
    ),
    _claim(
        "section3_3_1_google_scale_borg_scheduling_problem",
        "section_3_3_1",
        13,
        "Efficiently scheduling compute jobs onto a cluster of machines is a critical optimization problem",
        "Provide a Google-scale Borg-style compute-job scheduling problem.",
        "scheduling_problem_context",
        "not_implemented",
        ("papers/systems_result_readiness_boundary.json",),
        ("systems_fixtures", "formulation"),
    ),
    _claim(
        "section3_3_1_assign_jobs_from_requirements_and_capacity",
        "section_3_3_1",
        13,
        "assigning jobs to available machines based on job resource requirements and machine capacity",
        "Implement scheduling over available machines using job requirements and machine capacity.",
        "scheduling_problem_context",
        "not_implemented",
        _SYSTEMS_EVIDENCE,
        ("systems_fixtures", "formulation"),
    ),
    _claim(
        "section3_3_1_inefficient_assignments_strand_resources",
        "section_3_3_1",
        13,
        "Inefficient assignments can result in stranded resources",
        "Represent stranded resources as the scheduling optimization motivation.",
        "scheduling_problem_context",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("formulation",),
    ),
    _claim(
        "section3_3_1_one_resource_exhausted_other_resource_free",
        "section_3_3_1",
        13,
        "when a machine can no longer accept jobs because it has run out of one kind of resource",
        "Model machines that cannot accept jobs after one resource is exhausted while another remains free.",
        "scheduling_problem_context",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("formulation",),
    ),
    _claim(
        "section3_3_1_more_jobs_same_compute_footprint",
        "section_3_3_1",
        13,
        "allowing more jobs to be completed on the same amount",
        "Measure whether recovered stranded resources complete more jobs within the same compute footprint.",
        "scheduling_problem_context",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("formulation", "calibration"),
    ),
    _claim(
        "section3_3_1_growth_without_proportional_resource_increase",
        "section_3_3_1",
        14,
        "accommodate growing compute needs without a proportional increase in resource consumption",
        "Calibrate scheduling efficiency against growth without proportional resource consumption.",
        "scheduling_problem_context",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("formulation", "calibration"),
    ),
    _claim(
        "section3_3_1_debuggability_scale_and_bin_packing_challenge",
        "section_3_3_1",
        14,
        "debuggability and scale, on top of the classically difficult bin-packing problem",
        "Preserve debuggability, scale, and bin-packing difficulty in scheduling evidence.",
        "scheduling_problem_context",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("formulation", "deployment"),
    ),
    _claim(
        "section3_3_1_online_two_variable_vector_bin_packing",
        "section_3_3_1",
        14,
        "framing the online job scheduling problem as a vector bin-packing problem with two variables",
        "Require an online two-variable vector-bin-packing formulation.",
        "scheduling_formulation",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("formulation",),
    ),
    _claim(
        "section3_3_1_machines_bins_cpu_memory_capacity",
        "section_3_3_1",
        14,
        "machines represent bins with defined capacities for CPU and memory",
        "Represent machines as bins with CPU and memory capacities.",
        "scheduling_formulation",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("formulation",),
    ),
    _claim(
        "section3_3_1_jobs_items_resource_demands",
        "section_3_3_1",
        14,
        "incoming jobs are items with specific resource demands",
        "Represent incoming jobs as items with CPU and memory demands.",
        "scheduling_formulation",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("formulation",),
    ),
    _claim(
        "section3_3_1_heuristic_required_and_free_inputs",
        "section_3_3_1",
        14,
        "takes as input a pending job's CPU and memory requirements and a potential machine's CPU and memory availability",
        "Define heuristic inputs for pending-job requirements and candidate-machine availability.",
        "scheduling_formulation",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("formulation", "figure6"),
    ),
    _claim(
        "section3_3_1_heuristic_outputs_machine_priority",
        "section_3_3_1",
        14,
        "outputs a priority score for the machine",
        "Constrain the evolved heuristic to output a machine-priority score.",
        "scheduling_formulation",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("formulation", "safety"),
    ),
    _claim(
        "section3_3_1_borg_uses_highest_priority_among_other_objectives",
        "section_3_3_1",
        14,
        "assigns the pending job to the machine with the highest priority score as determined by the heuristic function, among other objectives",
        "Record that Borg combines the heuristic's highest-priority ranking with other scheduler objectives.",
        "scheduling_formulation",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("formulation", "safety"),
    ),
    _claim(
        "section3_3_1_rank_only_borg_feasible_machines",
        "section_3_3_1",
        14,
        "only influences the ranking of machines already determined by Borg to be available and capable of running each pending job",
        "Limit the heuristic to ranking machines already declared feasible by the scheduler.",
        "scheduling_safety",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("safety",),
    ),
    _claim(
        "section3_3_1_effectively_correct_by_construction",
        "section_3_3_1",
        14,
        "scheduling decisions are effectively correct by construction",
        "Support correctness-by-construction claims with ranking-only and feasibility-boundary evidence.",
        "scheduling_safety",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("safety",),
    ),
    _claim(
        "section3_3_1_early_alphaevolve_version",
        "section_3_3_1",
        14,
        "An early version of AlphaEvolve was used",
        "Record the AlphaEvolve version and run identity used for scheduling discovery.",
        "scheduling_discovery_and_evaluation",
        "not_demonstrated",
        _FIGURE6_EVIDENCE,
        ("figure6", "application"),
    ),
    _claim(
        "section3_3_1_simple_effective_heuristic_discovery",
        "section_3_3_1",
        14,
        "discover a remarkably simple yet effective heuristic function",
        "Demonstrate discovery of a simple and effective scheduling heuristic.",
        "scheduling_discovery_and_evaluation",
        "not_demonstrated",
        _FIGURE6_EVIDENCE,
        ("figure6", "systems_fixtures"),
    ),
    _claim(
        "section3_3_1_evolved_from_production_incumbent",
        "section_3_3_1",
        14,
        "evolving from the existing one in production",
        "Prove that the discovered heuristic evolved from the identified production incumbent.",
        "scheduling_discovery_and_evaluation",
        "not_demonstrated",
        _FIGURE6_EVIDENCE,
        ("comparator", "figure6"),
    ),
    _claim(
        "section3_3_1_historical_fleet_snapshot_simulator_feedback",
        "section_3_3_1",
        14,
        "historical snapshots of workloads and capacity across Google's fleet",
        "Implement simulator feedback from historical fleet workload and capacity snapshots.",
        "scheduling_discovery_and_evaluation",
        "not_implemented",
        _SYSTEMS_EVIDENCE,
        ("systems_fixtures", "formulation"),
    ),
    _claim(
        "section3_3_1_unseen_recent_workload_capacity_generalization",
        "section_3_3_1",
        14,
        "unseen test dataset of recent workloads and capacity to ensure generalization",
        "Require an unseen recent workload/capacity test set for scheduling generalization.",
        "scheduling_discovery_and_evaluation",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("systems_fixtures", "calibration"),
    ),
    _claim(
        "section3_3_1_outperforms_production_heuristic",
        "section_3_3_1",
        14,
        "outperforms the one in production",
        "Demonstrate that the evolved heuristic outperforms the production incumbent.",
        "scheduling_production_result",
        "not_demonstrated",
        _FIGURE6_EVIDENCE,
        ("calibration", "comparator"),
    ),
    _claim(
        "section3_3_1_entire_fleet_rollout",
        "section_3_3_1",
        14,
        "rolled out AlphaEvolve's heuristic function to the entire fleet",
        "Provide reviewed evidence for fleet-wide deployment of the evolved heuristic.",
        "scheduling_production_result",
        "not_demonstrated",
        _FIGURE6_EVIDENCE,
        ("deployment", "application"),
    ),
    _claim(
        "section3_3_1_post_deployment_confirms_simulator",
        "section_3_3_1",
        14,
        "Post-deployment measurements across Google's fleet confirmed the simulator results",
        "Join post-deployment fleet measurements to simulator predictions and confirm agreement.",
        "scheduling_production_result",
        "not_demonstrated",
        _FIGURE6_EVIDENCE,
        ("systems_fixtures", "calibration", "application"),
    ),
    _claim(
        "section3_3_1_continuous_average_point_7_percent_recovery",
        "section_3_3_1",
        14,
        "continuously recovers on average 0.7% of Google's fleet-wide compute resources",
        "Reproduce the continuous average 0.7% fleet-wide compute-resource recovery claim.",
        "scheduling_production_result",
        "not_demonstrated",
        _FIGURE6_EVIDENCE,
        ("calibration", "figure6"),
    ),
    _claim(
        "section3_3_1_recovered_resources_otherwise_stranded",
        "section_3_3_1",
        14,
        "which would otherwise be stranded",
        "Tie the recovered-resource metric to resources that would otherwise remain stranded.",
        "scheduling_production_result",
        "not_demonstrated",
        _FIGURE6_EVIDENCE,
        ("calibration", "formulation"),
    ),
    _claim(
        "section3_3_1_chosen_over_deep_reinforcement_learning",
        "section_3_3_1",
        14,
        "AlphaEvolve was chosen over a deep reinforcement learning approach",
        "Record a matched selection decision between the code heuristic and deep reinforcement learning.",
        "scheduling_comparator_and_deployment",
        "not_demonstrated",
        _SYSTEMS_EVIDENCE,
        ("comparator", "deployment"),
    ),
    _claim(
        "section3_3_1_code_solution_better_performance",
        "section_3_3_1",
        14,
        "code solution not only leads to better performance",
        "Demonstrate the code solution's performance advantage over the learned-policy comparator.",
        "scheduling_comparator_and_deployment",
        "not_demonstrated",
        _SYSTEMS_EVIDENCE,
        ("comparator", "calibration"),
    ),
    _claim(
        "section3_3_1_interpretability_advantage",
        "section_3_3_1",
        14,
        "advantages in interpretability",
        "Require reviewed interpretability evidence for mission-critical scheduling.",
        "scheduling_comparator_and_deployment",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("deployment", "comparator"),
    ),
    _claim(
        "section3_3_1_debuggability_advantage",
        "section_3_3_1",
        14,
        "debuggability",
        "Require reviewed debuggability evidence for mission-critical scheduling.",
        "scheduling_comparator_and_deployment",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("deployment", "comparator"),
    ),
    _claim(
        "section3_3_1_predictability_advantage",
        "section_3_3_1",
        14,
        "predictability",
        "Require predictable-behavior checks for mission-critical scheduling.",
        "scheduling_comparator_and_deployment",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("deployment", "comparator"),
    ),
    _claim(
        "section3_3_1_ease_of_deployment_advantage",
        "section_3_3_1",
        14,
        "ease of deployment",
        "Require deployment-ergonomics evidence for mission-critical scheduling.",
        "scheduling_comparator_and_deployment",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("deployment", "comparator"),
    ),
    _claim(
        "section3_3_1_mission_critical_operational_qualities",
        "section_3_3_1",
        14,
        "essential qualities for a mission-critical system",
        "Tie interpretability, debuggability, predictability, and deployment evidence to mission-critical readiness.",
        "scheduling_comparator_and_deployment",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("deployment", "application"),
    ),
    _claim(
        "figure6_function_signature",
        "figure_6",
        14,
        "def alpha_evolve_score(required, free):",
        "Reproduce the Figure 6 alpha_evolve_score(required, free) function identity.",
        "figure_6_code",
        "not_implemented",
        _FIGURE6_EVIDENCE,
        ("figure6",),
    ),
    _claim(
        "figure6_cpu_residual_definition",
        "figure_6",
        14,
        "cpu_residual = required.cpu / free.cpu",
        "Reproduce the required.cpu/free.cpu residual definition.",
        "figure_6_code",
        "not_implemented",
        _FIGURE6_EVIDENCE,
        ("figure6",),
    ),
    _claim(
        "figure6_memory_residual_definition",
        "figure_6",
        14,
        "mem_residual = required.mem / free.mem",
        "Reproduce the required.mem/free.mem residual definition.",
        "figure_6_code",
        "not_implemented",
        _FIGURE6_EVIDENCE,
        ("figure6",),
    ),
    _claim(
        "figure6_negative_residual_sum",
        "figure_6",
        14,
        "return -1.0 * (cpu_residual + mem_residual +",
        "Reproduce the negative sum over CPU residual, memory residual, and cross-ratio terms.",
        "figure_6_code",
        "not_implemented",
        _FIGURE6_EVIDENCE,
        ("figure6",),
    ),
    _claim(
        "figure6_memory_over_cpu_cross_ratio",
        "figure_6",
        14,
        "mem_residual / cpu_residual",
        "Reproduce the memory-residual over CPU-residual cross-ratio term.",
        "figure_6_code",
        "not_implemented",
        _FIGURE6_EVIDENCE,
        ("figure6",),
    ),
    _claim(
        "figure6_cpu_over_memory_cross_ratio",
        "figure_6",
        14,
        "cpu_residual / mem_residual",
        "Reproduce the CPU-residual over memory-residual cross-ratio term.",
        "figure_6_code",
        "not_implemented",
        _FIGURE6_EVIDENCE,
        ("figure6",),
    ),
    _claim(
        "figure6_tailored_google_workloads_and_capacity",
        "figure_6",
        14,
        "tailored to Google's workloads and capacity",
        "Demonstrate that the displayed heuristic is tailored to the declared workloads and capacity.",
        "figure_6_exhibit",
        "not_demonstrated",
        _FIGURE6_EVIDENCE,
        ("figure6", "formulation"),
    ),
    _claim(
        "figure6_scoring_function_visualization",
        "figure_6",
        14,
        "Visualization of the heuristic scoring function",
        "Generate the Figure 6 scoring-function visualization from retained data and rendering parameters.",
        "figure_6_exhibit",
        "not_implemented",
        _FIGURE6_EVIDENCE,
        ("figure6",),
    ),
    _claim(
        "figure6_yellow_regions_high_scores",
        "figure_6",
        14,
        "Yellow regions represent high scores",
        "Preserve the yellow-is-high legend semantics in the reproduced heatmap.",
        "figure_6_exhibit",
        "not_implemented",
        _FIGURE6_EVIDENCE,
        ("figure6",),
    ),
    _claim(
        "figure6_purple_regions_low_scores",
        "figure_6",
        14,
        "purple regions represent low scores",
        "Preserve the purple-is-low legend semantics in the reproduced heatmap.",
        "figure_6_exhibit",
        "not_implemented",
        _FIGURE6_EVIDENCE,
        ("figure6",),
    ),
    _claim(
        "figure6_cpu_residual_axis_zero_to_one_hundred_percent",
        "figure_6",
        14,
        "0% 25% 50% 75% 100% CPU residual",
        "Preserve the Figure 6 CPU-residual axis and its 0%-100% range.",
        "figure_6_exhibit",
        "not_implemented",
        _FIGURE6_EVIDENCE,
        ("figure6",),
    ),
    _claim(
        "figure6_memory_residual_axis_zero_to_one_hundred_percent",
        "figure_6",
        14,
        "0% 25% 50% 75% 100% Memory residual",
        "Preserve the Figure 6 memory-residual axis and its 0%-100% range.",
        "figure_6_exhibit",
        "not_implemented",
        _FIGURE6_EVIDENCE,
        ("figure6",),
    ),
)


EXPECTED_CLAIM_IDS = tuple(spec["claim_id"] for spec in SCHEDULING_CLAIM_SPECS)


@dataclass(frozen=True)
class AlphaEvolveSchedulingClaimInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveSchedulingClaimInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    claim_count: int
    implemented_local_count: int
    implementation_gap_count: int
    missing_anchor_count: int
    missing_reference_count: int
    issues: list[AlphaEvolveSchedulingClaimInventoryBoundaryIssue]


def alphaevolve_scheduling_claim_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded Section 3.3.1 and Figure 6 claim inventory."""

    root_path = Path(root)
    source_inventory = alphaevolve_source_inventory_boundary_record(root_path)
    page_texts = _source_page_texts(root_path)
    records = [
        _claim_record(root_path, spec, page_texts)
        for spec in SCHEDULING_CLAIM_SPECS
    ]
    status_counts = Counter(record["implementation_status"] for record in records)
    category_counts = Counter(record["category"] for record in records)
    missing_anchor_count = sum(
        1 for record in records if not record["source_anchor_present"]
    )
    missing_reference_count = sum(
        1
        for record in records
        for ref in (*record["evidence_refs"], *record["active_todo_refs"])
        if not ref["exists"]
        or (
            "required_phrase_present" in ref
            and not ref["required_phrase_present"]
        )
    )
    implementation_gap_count = sum(
        1
        for record in records
        if record["implementation_status"] != IMPLEMENTED_STATUS
    )
    todo_owned_gap_count = sum(
        1
        for record in records
        if record["implementation_status"] != IMPLEMENTED_STATUS
        and record["active_todo_refs"]
        and all(
            ref["exists"] and ref["required_phrase_present"]
            for ref in record["active_todo_refs"]
        )
    )
    source_artifact = source_inventory["source_artifact"]
    inventory_ready = (
        source_artifact["identity_ok"]
        and source_inventory["named_structure_inventory_ready"]
        and len(records) == EXPECTED_CLAIM_COUNT
        and missing_anchor_count == 0
        and missing_reference_count == 0
        and todo_owned_gap_count == implementation_gap_count
    )
    return {
        "schema": ALPHAEVOLVE_SCHEDULING_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "scheduling_claim_inventory_ready": inventory_ready,
        "alphaevolve_scheduling_result_reproduction_claim_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_inventory_schema": source_inventory["schema"],
        "source_inventory_span_count": source_inventory["span_count"],
        "source_span_ids": ["section_3_3", "section_3_3_1", "figure_6"],
        "inventory_scope": {
            "included": [
                "the Section 3.3 opening mission-critical-infrastructure claim",
                "all substantive Section 3.3.1 scheduling context, formulation, safety, discovery, evaluation, production-result, comparator, and deployment claims",
                "Figure 6 function signature, two residual definitions, negative score sum, both cross-ratio terms, workload/capacity tailoring, visualization, axis ranges, and legend semantics",
            ],
            "excluded": [
                "Sections 3.3.2 through 3.3.4 and Figure 7",
                "Sections 4 through 6, Figures 8 through 14, Table 3, appendices, citations, and bibliography details",
                "a real Borg-compatible scheduler, Google workload/capacity data, simulator, production incumbent, deep-reinforcement-learning comparator, or fleet deployment",
                "independent reproduction of Figure 6, the 0.7% result, or any production claim",
                "AlphaEvolve production scale or system parity",
            ],
        },
        "claim_count": len(records),
        "expected_claim_count": EXPECTED_CLAIM_COUNT,
        "category_counts": dict(sorted(category_counts.items())),
        "implementation_status_counts": dict(sorted(status_counts.items())),
        "implemented_local_count": status_counts[IMPLEMENTED_STATUS],
        "implementation_gap_count": implementation_gap_count,
        "todo_owned_gap_count": todo_owned_gap_count,
        "missing_anchor_count": missing_anchor_count,
        "missing_reference_count": missing_reference_count,
        "claim_records": records,
        "claim_boundary": (
            "This sidecar certifies a bounded claim-level inventory of 45 "
            "AlphaEvolve scheduling claims from the Section 3.3 opening, "
            "Section 3.3.1, and Figure 6. Status labels distinguish local "
            "report/exhibit schema support from absent scheduling runtime "
            "behavior and undemonstrated published production outcomes. It "
            "does not claim a Borg fixture, workload/capacity data, simulator, "
            "production or learned-policy comparator artifacts, fleet "
            "deployment, Figure 6 reproduction, the 0.7% result, production "
            "scale, or AlphaEvolve system parity."
        ),
    }


def validate_alphaevolve_scheduling_claim_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveSchedulingClaimInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_scheduling_claim_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveSchedulingClaimInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_scheduling_claim_inventory_boundary_record(root)
    issues: list[AlphaEvolveSchedulingClaimInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_SCHEDULING_CLAIM_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported scheduling claim inventory schema"))
    if data.get("source_paper_id") != SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(
            _issue(
                "invalid_boundary_status",
                f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}",
            )
        )
    if data.get("alphaevolve_scheduling_result_reproduction_claim_ready") is not False:
        issues.append(
            _issue(
                "result_reproduction_overclaim",
                "scheduling inventory must not claim result reproduction",
            )
        )
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(
            _issue(
                "parity_overclaim",
                "scheduling inventory must not claim AlphaEvolve parity",
            )
        )
    for key in (
        "source_artifact",
        "source_inventory_schema",
        "source_inventory_span_count",
        "source_span_ids",
        "inventory_scope",
        "claim_count",
        "expected_claim_count",
        "category_counts",
        "implementation_status_counts",
        "implemented_local_count",
        "implementation_gap_count",
        "todo_owned_gap_count",
        "missing_anchor_count",
        "missing_reference_count",
        "claim_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(
                _issue(
                    f"invalid_{key}",
                    f"{key} drifted from the bounded scheduling claim inventory",
                )
            )
    if len(EXPECTED_CLAIM_IDS) != EXPECTED_CLAIM_COUNT:
        issues.append(_issue("invalid_spec_count", "scheduling claim count must remain 45"))
    if len(set(EXPECTED_CLAIM_IDS)) != len(EXPECTED_CLAIM_IDS):
        issues.append(_issue("duplicate_claim_id", "scheduling claim ids must be unique"))
    unknown_spans = sorted(
        {
            spec["source_span_id"]
            for spec in SCHEDULING_CLAIM_SPECS
            if spec["source_span_id"] not in EXPECTED_NAMED_SOURCE_SPAN_IDS
        }
    )
    if unknown_spans:
        issues.append(
            _issue(
                "unknown_source_span",
                f"unknown source spans: {', '.join(unknown_spans)}",
            )
        )
    unsupported_statuses = sorted(
        {
            spec["implementation_status"]
            for spec in SCHEDULING_CLAIM_SPECS
            if spec["implementation_status"]
            not in INCOMPLETE_STATUSES | {IMPLEMENTED_STATUS}
        }
    )
    if unsupported_statuses:
        issues.append(
            _issue(
                "unsupported_implementation_status",
                f"unsupported statuses: {', '.join(unsupported_statuses)}",
            )
        )
    unowned_gaps = sorted(
        record["claim_id"]
        for record in expected["claim_records"]
        if record["implementation_status"] != IMPLEMENTED_STATUS
        and not record["active_todo_refs"]
    )
    if unowned_gaps:
        issues.append(
            _issue(
                "unowned_implementation_gap",
                f"claims lack active TODO ownership: {', '.join(unowned_gaps)}",
            )
        )
    if not expected["source_artifact"]["identity_ok"]:
        issues.append(
            _issue(
                "source_pdf_identity_mismatch",
                "retained AlphaEvolve PDF identity does not match the pinned source",
            )
        )
    if expected["missing_anchor_count"]:
        issues.append(
            _issue(
                "missing_source_anchor",
                f"{expected['missing_anchor_count']} scheduling claim anchors were not found",
            )
        )
    if expected["missing_reference_count"]:
        issues.append(
            _issue(
                "missing_local_reference",
                f"{expected['missing_reference_count']} evidence or TODO references are stale",
            )
        )
    expected_ready = (
        expected["source_artifact"]["identity_ok"]
        and expected["claim_count"] == EXPECTED_CLAIM_COUNT
        and expected["missing_anchor_count"] == 0
        and expected["missing_reference_count"] == 0
        and expected["todo_owned_gap_count"] == expected["implementation_gap_count"]
    )
    if data.get("scheduling_claim_inventory_ready") is not expected_ready:
        issues.append(
            _issue(
                "invalid_scheduling_claim_inventory_ready",
                "scheduling_claim_inventory_ready does not match source, reference, and ownership checks",
            )
        )
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "45" not in claim_boundary
        or "Borg fixture" not in claim_boundary
        or "Figure 6 reproduction" not in claim_boundary
        or "0.7% result" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(
            _issue(
                "missing_claim_boundary",
                "claim_boundary must separate bounded scheduling claims from Borg, Figure 6, result, and parity proof",
            )
        )
    return AlphaEvolveSchedulingClaimInventoryBoundaryValidation(
        ok=not issues,
        boundary_status=(
            data.get("boundary_status")
            if isinstance(data.get("boundary_status"), str)
            else None
        ),
        claim_count=(
            data.get("claim_count") if isinstance(data.get("claim_count"), int) else 0
        ),
        implemented_local_count=(
            data.get("implemented_local_count")
            if isinstance(data.get("implemented_local_count"), int)
            else 0
        ),
        implementation_gap_count=(
            data.get("implementation_gap_count")
            if isinstance(data.get("implementation_gap_count"), int)
            else 0
        ),
        missing_anchor_count=expected["missing_anchor_count"],
        missing_reference_count=expected["missing_reference_count"],
        issues=issues,
    )


def render_alphaevolve_scheduling_claim_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_scheduling_claim_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve scheduling claim inventory boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| claim_count | {validation.claim_count} |",
        f"| implemented_local_count | {validation.implemented_local_count} |",
        f"| implementation_gap_count | {validation.implementation_gap_count} |",
        f"| missing_anchor_count | {validation.missing_anchor_count} |",
        f"| missing_reference_count | {validation.missing_reference_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _claim_record(
    root: Path,
    spec: dict[str, Any],
    page_texts: tuple[str, ...],
) -> dict[str, Any]:
    page_number = spec["source_page"]
    page_text = page_texts[page_number - 1] if page_number <= len(page_texts) else ""
    evidence_refs = [_evidence_ref(root, path) for path in spec["evidence_paths"]]
    active_todo_refs = []
    for todo_id in spec["todo_ids"]:
        path_label, phrase = _TODO_SPECS[todo_id]
        path = root / path_label
        text = _read_text(path)
        active_todo_refs.append(
            {
                "todo_id": todo_id,
                "path": path_label,
                "required_phrase": phrase,
                "exists": _safe_is_file(path),
                "required_phrase_present": phrase in text,
            }
        )
    return {
        "claim_id": spec["claim_id"],
        "source_span_id": spec["source_span_id"],
        "source_page": page_number,
        "source_anchor": spec["source_anchor"],
        "source_anchor_present": _canonical(spec["source_anchor"])
        in _canonical(page_text),
        "claim": spec["claim"],
        "category": spec["category"],
        "implementation_status": spec["implementation_status"],
        "roadmap_section_id": spec["roadmap_section_id"],
        "roadmap_phase": spec["roadmap_phase"],
        "evidence_refs": evidence_refs,
        "active_todo_refs": active_todo_refs,
    }


def _evidence_ref(root: Path, path_label: str) -> dict[str, Any]:
    path = root / path_label
    record: dict[str, Any] = {
        "path": path_label,
        "exists": _safe_is_file(path),
    }
    if path.suffix.casefold() == ".json" and record["exists"]:
        payload = _read_json(path)
        if isinstance(payload, dict):
            for key in (
                "schema",
                "boundary_status",
                "artifact_status",
                "runtime_emission_status",
                "claim_ready",
            ):
                value = payload.get(key)
                if isinstance(value, (str, bool)):
                    record[key] = value
    return record


def _source_page_texts(root: Path) -> tuple[str, ...]:
    path = root / SOURCE_PDF_PATH
    try:
        stat = path.stat()
    except OSError:
        return ()
    return _cached_source_page_texts(str(path.resolve()), stat.st_mtime_ns, stat.st_size)


@lru_cache(maxsize=8)
def _cached_source_page_texts(
    resolved_path: str,
    _mtime_ns: int,
    _size: int,
) -> tuple[str, ...]:
    try:
        reader = PdfReader(Path(resolved_path), strict=True)
        return tuple(page.extract_text() or "" for page in reader.pages)
    except Exception:  # pragma: no cover - exact pypdf errors vary.
        return ()


def _canonical(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).casefold()
    return "".join(character for character in normalized if character.isalnum())


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def _safe_is_file(path: Path) -> bool:
    try:
        return path.is_file()
    except OSError:
        return False


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[
    dict[str, Any] | None,
    list[AlphaEvolveSchedulingClaimInventoryBoundaryIssue],
]:
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
            return None, [
                _issue("unreadable_boundary", f"boundary could not be loaded: {exc}")
            ]
    if isinstance(data, dict):
        return data, []
    return None, [
        _issue(
            "invalid_shape",
            "scheduling claim inventory boundary must be a JSON object",
        )
    ]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveSchedulingClaimInventoryBoundaryIssue:
    return AlphaEvolveSchedulingClaimInventoryBoundaryIssue(code, message)
