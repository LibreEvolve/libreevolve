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


ALPHAEVOLVE_COMPILER_CLAIM_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_compiler_claim_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "section_3_3_4_claim_inventory_complete_without_executable_compiler_ir_"
    "fixture_or_result_reproduction"
)
EXPECTED_CLAIM_COUNT = 44
IMPLEMENTED_STATUS = "implemented_local"
INCOMPLETE_STATUSES = frozenset(
    {"partially_implemented", "not_implemented", "not_demonstrated"}
)


_TODO_SPECS = {
    "fixture": (
        "docs/todo/code.md",
        "Add an executable XLA/MLIR compiler-IR optimization benchmark contract.",
    ),
    "reference": (
        "docs/todo/code.md",
        "Add per-edit reference-check provenance for compiler-generated IR tasks.",
    ),
    "stack": (
        "docs/todo/code.md",
        "Add FlashAttention compiler-stack context provenance.",
    ),
    "adoption": (
        "docs/todo/code.md",
        "Add compiler-adoption path provenance for discovered optimizations.",
    ),
    "calibration": (
        "docs/todo/code.md",
        "Populate Section 3.3 result-claim calibration fields for systems reports.",
    ),
    "systems_fixtures": (
        "docs/todo/code.md",
        "Connect real systems fixtures to held-out and reference-correctness",
    ),
}


def _claim(
    claim_id: str,
    source_anchor: str,
    claim: str,
    category: str,
    implementation_status: str,
    evidence_paths: tuple[str, ...],
    todo_ids: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "source_span_id": "section_3_3_4",
        "source_page": 17,
        "source_anchor": source_anchor,
        "claim": claim,
        "category": category,
        "implementation_status": implementation_status,
        "roadmap_section_id": "representative_benchmarks",
        "roadmap_phase": "longer_term",
        "evidence_paths": evidence_paths,
        "todo_ids": todo_ids,
    }


_WORKSPACE_EVIDENCE = (
    "libreevolve/problems/loader.py",
    "libreevolve/core/evaluator.py",
    "libreevolve/problems/examples/candidate_runner_c/config.yaml",
)
_STACK_EVIDENCE = (
    "libreevolve/problems/benchmarks/systems_results.py",
    "papers/compiler_stack_context_boundary.json",
    "papers/systems_result_readiness_boundary.json",
)
_REFERENCE_EVIDENCE = (
    "libreevolve/problems/benchmarks/systems_results.py",
    "papers/compiler_ir_reference_check_boundary.json",
    "papers/systems_result_readiness_boundary.json",
)
_ADOPTION_EVIDENCE = (
    "libreevolve/problems/benchmarks/systems_results.py",
    "papers/compiler_adoption_path_boundary.json",
    "papers/systems_result_readiness_boundary.json",
)
_RESULT_EVIDENCE = _REFERENCE_EVIDENCE + (
    "papers/compiler_stack_context_boundary.json",
)


COMPILER_CLAIM_SPECS = (
    _claim(
        "transformer_majority_modern_neural_networks",
        "used in the majority of modern neural networks",
        "Preserve the paper's majority-of-modern-neural-networks statement as source context, not a local measurement.",
        "transformer_attention_context",
        "not_demonstrated",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "transformer_range_llms_to_alphafold",
        "ranging from LLMs to AlphaFold",
        "Preserve the source examples spanning LLMs through AlphaFold without treating that range as local workload coverage.",
        "transformer_attention_context",
        "not_demonstrated",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "attention_core_transformer_computation",
        "The core computation of transformers is the attention mechanism",
        "Record attention as the source's core transformer computation context.",
        "transformer_attention_context",
        "not_demonstrated",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "attention_most_commonly_flashattention",
        "most commonly implemented using FlashAttention",
        "Preserve the qualified claim that attention is most commonly implemented with FlashAttention, not universally implemented that way.",
        "transformer_attention_context",
        "not_demonstrated",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "flashattention_accelerator_kernel_in_stack",
        "implemented as an accelerator kernel",
        "Provide an executable accelerator-kernel workload rather than compiler-stack metadata alone.",
        "compiler_stack_context",
        "not_implemented",
        _WORKSPACE_EVIDENCE + _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "pallas_flashattention_implementation",
        "accelerator kernel in Pallas",
        "Provide the Pallas kernel source or an explicitly labeled open analogue.",
        "compiler_stack_context",
        "not_implemented",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "higher_level_jax_wrapper",
        "wrapped by higher-level code in JAX",
        "Provide executable higher-level wrapper code around the candidate kernel.",
        "compiler_stack_context",
        "not_implemented",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "jax_input_preparation",
        "handles input preparation",
        "Attribute input-preparation code and artifacts separately from the kernel candidate.",
        "compiler_stack_context",
        "partially_implemented",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "jax_output_postprocessing",
        "output postprocessing",
        "Attribute output-postprocessing code and artifacts separately from the kernel candidate.",
        "compiler_stack_context",
        "partially_implemented",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "xla_machine_learning_compiler",
        "The machine learning compiler (XLA",
        "Provide an executable XLA or clearly labeled open compiler-IR toolchain.",
        "compiler_stack_context",
        "not_implemented",
        _WORKSPACE_EVIDENCE + _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "xla_sequence_of_intermediate_representations",
        "sequence of intermediate representations",
        "Emit and validate at least one concrete lowered-IR sequence rather than only naming its stage in metadata.",
        "compiler_stack_context",
        "not_implemented",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "ir_adds_hardware_execution_detail",
        "each adding more detail for execution on particular hardware",
        "Demonstrate an IR lowering sequence that adds hardware-execution detail.",
        "compiler_stack_context",
        "not_implemented",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "particular_hardware_target",
        "execution on particular hardware",
        "Bind compiler artifacts and measurements to an identified hardware target.",
        "compiler_stack_context",
        "partially_implemented",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "memory_access_decisions_can_reduce_runtime",
        "improved decisions on memory access orchestration",
        "Represent memory-access orchestration as a potential optimization category without attributing every reported edit to it.",
        "compiler_stack_context",
        "partially_implemented",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "scheduling_decisions_can_reduce_runtime",
        "or computation scheduling",
        "Represent computation scheduling as a potential optimization category without attributing every reported edit to it.",
        "compiler_stack_context",
        "partially_implemented",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "specific_hardware_runtime_context",
        "reduce runtime on specific hardware",
        "Measure runtime in a declared hardware and compiler context.",
        "compiler_stack_context",
        "partially_implemented",
        _STACK_EVIDENCE,
        ("fixture", "stack", "calibration"),
    ),
    _claim(
        "direct_optimize_xla_generated_irs",
        "directly optimize the XLA-generated IRs",
        "Execute direct candidate edits against compiler-generated IR rather than generic source text alone.",
        "compiler_optimization_task",
        "partially_implemented",
        _WORKSPACE_EVIDENCE + _REFERENCE_EVIDENCE,
        ("fixture", "reference"),
    ),
    _claim(
        "ir_encapsulates_flashattention_kernel",
        "IRs encapsulating the FlashAttention kernel",
        "Make the kernel-bearing IR a first-class candidate artifact.",
        "compiler_optimization_task",
        "partially_implemented",
        _WORKSPACE_EVIDENCE + _STACK_EVIDENCE,
        ("fixture", "reference", "stack"),
    ),
    _claim(
        "ir_includes_pre_and_postprocessing",
        "along with pre- and postprocessing code",
        "Include surrounding pre/postprocessing code in the task workspace and attribution model.",
        "compiler_optimization_task",
        "partially_implemented",
        _WORKSPACE_EVIDENCE + _STACK_EVIDENCE,
        ("fixture", "reference", "stack"),
    ),
    _claim(
        "highly_impactful_transformer_configuration",
        "highly impactful transformer model",
        "Do not claim a highly impactful model configuration without identified workload and deployment evidence.",
        "compiler_optimization_task",
        "not_demonstrated",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "inference_at_scale",
        "used for inference at scale",
        "Do not claim inference-at-scale relevance from a smoke fixture or metadata-only workload record.",
        "compiler_optimization_task",
        "not_demonstrated",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "gpu_execution_target",
        "inference at scale on GPUs",
        "Bind the executable task and benchmark evidence to an identified GPU target or label a substitute target explicitly.",
        "compiler_optimization_task",
        "partially_implemented",
        _STACK_EVIDENCE,
        ("fixture", "stack"),
    ),
    _claim(
        "minimize_overall_module_execution_time",
        "minimizing the module's overall execution time",
        "Use overall module execution time as a calibrated optimization objective with a fixed baseline and measurement protocol.",
        "compiler_optimization_task",
        "partially_implemented",
        _WORKSPACE_EVIDENCE + _RESULT_EVIDENCE,
        ("fixture", "calibration"),
    ),
    _claim(
        "compiler_ir_task_particularly_challenging",
        "particularly challenging task",
        "Keep the paper's qualitative difficulty statement contextual unless a matched local baseline supports it.",
        "compiler_optimization_task",
        "not_demonstrated",
        _REFERENCE_EVIDENCE,
        ("fixture", "reference"),
    ),
    _claim(
        "ir_designed_for_debugging",
        "IR is designed for debugging purposes",
        "Record whether the candidate IR is a debugging representation and preserve its origin evidence.",
        "compiler_optimization_task",
        "partially_implemented",
        _REFERENCE_EVIDENCE,
        ("fixture", "reference"),
    ),
    _claim(
        "ir_not_for_direct_developer_editing",
        "rather than for direct editing by developers",
        "Record the direct-editing boundary for compiler-generated IR candidates.",
        "compiler_optimization_task",
        "partially_implemented",
        _REFERENCE_EVIDENCE,
        ("fixture", "reference"),
    ),
    _claim(
        "compiler_generated_baseline",
        "it is compiler-generated",
        "Prove the baseline IR was emitted by the declared compiler and lowering stage.",
        "compiler_optimization_task",
        "partially_implemented",
        _REFERENCE_EVIDENCE,
        ("fixture", "reference"),
    ),
    _claim(
        "already_highly_optimized_baseline",
        "already highly optimized",
        "Document the baseline optimization pipeline before describing the candidate as already highly optimized.",
        "compiler_optimization_task",
        "partially_implemented",
        _REFERENCE_EVIDENCE,
        ("fixture", "reference"),
    ),
    _claim(
        "each_modification_reference_checked",
        "Each modification proposed by AlphaEvolve was checked",
        "Emit a reference-correctness record for every proposed modification, not only the final candidate.",
        "compiler_optimization_task",
        "partially_implemented",
        _REFERENCE_EVIDENCE,
        ("reference", "systems_fixtures"),
    ),
    _claim(
        "unmodified_reference_code",
        "reference (unmodified) code",
        "Pin the unmodified reference implementation and its content identity.",
        "compiler_optimization_task",
        "partially_implemented",
        _REFERENCE_EVIDENCE,
        ("fixture", "reference"),
    ),
    _claim(
        "randomized_input_reference_checks",
        "on randomized inputs",
        "Generate deterministic, recorded randomized inputs for per-edit reference checks.",
        "compiler_optimization_task",
        "partially_implemented",
        _REFERENCE_EVIDENCE,
        ("fixture", "reference", "systems_fixtures"),
    ),
    _claim(
        "numerical_correctness_throughout_optimization",
        "ensure numerical correctness throughout optimization",
        "Gate every accepted compiler-IR edit on declared numerical correctness tolerances.",
        "compiler_optimization_task",
        "partially_implemented",
        _REFERENCE_EVIDENCE,
        ("fixture", "reference", "systems_fixtures"),
    ),
    _claim(
        "final_human_expert_confirmation",
        "rigorously confirmed by human experts",
        "Do not claim final human-expert confirmation without scoped reviewer and signoff artifacts.",
        "compiler_optimization_task",
        "not_demonstrated",
        _REFERENCE_EVIDENCE,
        ("reference", "systems_fixtures"),
    ),
    _claim(
        "correct_for_all_possible_inputs",
        "correct for all possible inputs",
        "Do not claim all-input correctness without the paper's expert scope or an independently justified exhaustive proof.",
        "compiler_optimization_task",
        "not_demonstrated",
        _REFERENCE_EVIDENCE,
        ("reference", "systems_fixtures"),
    ),
    _claim(
        "meaningful_optimizations_both_abstraction_levels",
        "meaningful optimizations for both levels of abstraction",
        "Do not claim optimization at both abstraction levels without attributed candidate and measurement artifacts.",
        "compiler_result",
        "not_demonstrated",
        _RESULT_EVIDENCE,
        ("fixture", "calibration", "systems_fixtures"),
    ),
    _claim(
        "flashattention_kernel_optimization_result",
        "Firstly, the FlashAttention kernel",
        "Do not claim a FlashAttention kernel improvement without a real kernel artifact and calibrated baseline.",
        "compiler_result",
        "not_demonstrated",
        _RESULT_EVIDENCE,
        ("fixture", "calibration", "systems_fixtures"),
    ),
    _claim(
        "kernel_speedup_32_percent",
        "sped up by 32%",
        "Do not claim the paper's 32% kernel speedup without matched configuration, runtime, and repeated-measurement evidence.",
        "compiler_result",
        "not_demonstrated",
        _RESULT_EVIDENCE,
        ("fixture", "calibration", "systems_fixtures"),
    ),
    _claim(
        "kernel_configuration_of_interest_scope",
        "kernel for the configuration of interest",
        "Record the exact configuration to which any kernel speedup applies.",
        "compiler_result",
        "not_demonstrated",
        _RESULT_EVIDENCE,
        ("fixture", "stack", "calibration"),
    ),
    _claim(
        "pre_postprocessing_improvements_found",
        "found improvements in pre- and postprocessing",
        "Do not claim pre/postprocessing improvements without exact wrapper edits and attributed measurements.",
        "compiler_result",
        "not_demonstrated",
        _RESULT_EVIDENCE,
        ("fixture", "reference", "calibration"),
    ),
    _claim(
        "pre_postprocessing_speedup_15_percent",
        "resulting in a 15% speed up in this part",
        "Do not claim the paper's 15% pre/postprocessing speedup without an isolated baseline and measurement bundle.",
        "compiler_result",
        "not_demonstrated",
        _RESULT_EVIDENCE,
        ("fixture", "calibration", "systems_fixtures"),
    ),
    _claim(
        "compiler_generated_code_optimization_demonstrated",
        "demonstrate the ability of AlphaEvolve to optimize compiler-generated code",
        "Do not transfer the paper's demonstrated capability to LibreEvolve until an executable compiler-IR run is reproduced.",
        "compiler_result",
        "not_demonstrated",
        _RESULT_EVIDENCE,
        ("fixture", "calibration", "systems_fixtures"),
    ),
    _claim(
        "existing_compiler_incorporation_potential",
        "incorporating discovered optimizations into existing compilers",
        "Record concrete transfer of a discovered optimization into an existing compiler before claiming adoption.",
        "compiler_adoption",
        "partially_implemented",
        _ADOPTION_EVIDENCE,
        ("adoption",),
    ),
    _claim(
        "existing_compiler_specific_use_cases",
        "for specific use cases",
        "Bound any existing-compiler adoption claim to an identified use case and rollout scope.",
        "compiler_adoption",
        "partially_implemented",
        _ADOPTION_EVIDENCE,
        ("adoption",),
    ),
    _claim(
        "alphaevolve_in_compiler_workflow_longer_term",
        "in the longer term, incorporating AlphaEvolve into the compiler workflow itself",
        "Keep AlphaEvolve-in-the-compiler-workflow as a distinct longer-term adoption path with integration evidence.",
        "compiler_adoption",
        "partially_implemented",
        _ADOPTION_EVIDENCE,
        ("adoption",),
    ),
)

EXPECTED_CLAIM_IDS = tuple(spec["claim_id"] for spec in COMPILER_CLAIM_SPECS)


@dataclass(frozen=True)
class AlphaEvolveCompilerClaimInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveCompilerClaimInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    claim_count: int
    implemented_local_count: int
    implementation_gap_count: int
    missing_anchor_count: int
    missing_reference_count: int
    issues: list[AlphaEvolveCompilerClaimInventoryBoundaryIssue]


def alphaevolve_compiler_claim_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the Section 3.3.4 compiler claim-level implementation audit."""

    root_path = Path(root)
    source_inventory = alphaevolve_source_inventory_boundary_record(root_path)
    page_texts = _source_page_texts(root_path)
    records = [
        _claim_record(root_path, spec, page_texts) for spec in COMPILER_CLAIM_SPECS
    ]
    category_counts = Counter(record["category"] for record in records)
    status_counts = Counter(record["implementation_status"] for record in records)
    missing_anchor_count = sum(
        1 for record in records if not record["source_anchor_present"]
    )
    missing_reference_count = sum(
        1
        for record in records
        for ref in record["evidence_refs"]
        if not ref["exists"]
    ) + sum(
        1
        for record in records
        for ref in record["active_todo_refs"]
        if not ref["exists"] or not ref["required_phrase_present"]
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
        "schema": ALPHAEVOLVE_COMPILER_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "compiler_claim_inventory_ready": inventory_ready,
        "alphaevolve_compiler_result_reproduction_claim_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_inventory_schema": source_inventory["schema"],
        "source_inventory_span_count": source_inventory["span_count"],
        "source_span_ids": ["section_3_3_4"],
        "inventory_scope": {
            "included": [
                "all substantive Section 3.3.4 transformer/attention context, Pallas/JAX/XLA stack, compiler-IR task, correctness, result, and adoption claims",
                "source-fidelity distinctions between most-common and universal FlashAttention use, possible optimization categories and attributed edits, metadata support and executable stack evidence, and reported paper outcomes and local reproduction",
            ],
            "excluded": [
                "Section 4 through Section 5 and Figures 8 through 14",
                "Table 3, detailed appendices, citations, and bibliography details",
                "a proprietary FlashAttention configuration, executable XLA/MLIR/StableHLO analogue, Pallas/JAX stack, GPU benchmark, or human-expert signoff record",
                "independent reproduction of the 32 percent kernel speedup, 15 percent pre/postprocessing speedup, all-input correctness, or compiler adoption paths",
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
            "This sidecar certifies a bounded claim-level inventory of 44 "
            "AlphaEvolve compiler-generated-code claims from Section 3.3.4. "
            "Status labels distinguish generic workspace/candidate-runner and "
            "compiler-report metadata support from absent executable XLA/MLIR "
            "behavior and undemonstrated paper outcomes. It does not claim a "
            "FlashAttention/Pallas/JAX workload, lowered IR, GPU runtime, per-edit "
            "randomized reference results, expert all-input confirmation, the "
            "32 percent kernel or 15 percent pre/postprocessing speedups, compiler "
            "adoption, production scale, or AlphaEvolve system parity."
        ),
    }


def validate_alphaevolve_compiler_claim_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveCompilerClaimInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_compiler_claim_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveCompilerClaimInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_compiler_claim_inventory_boundary_record(root)
    issues: list[AlphaEvolveCompilerClaimInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_COMPILER_CLAIM_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported compiler claim inventory schema"))
    if data.get("source_paper_id") != SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(
            _issue(
                "invalid_boundary_status",
                f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}",
            )
        )
    if data.get("alphaevolve_compiler_result_reproduction_claim_ready") is not False:
        issues.append(
            _issue(
                "result_reproduction_overclaim",
                "compiler inventory must not claim result reproduction",
            )
        )
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(
            _issue(
                "parity_overclaim",
                "compiler inventory must not claim AlphaEvolve parity",
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
                    f"{key} drifted from the bounded compiler claim inventory",
                )
            )
    if len(EXPECTED_CLAIM_IDS) != EXPECTED_CLAIM_COUNT:
        issues.append(_issue("invalid_spec_count", "compiler claim count must remain 44"))
    if len(set(EXPECTED_CLAIM_IDS)) != len(EXPECTED_CLAIM_IDS):
        issues.append(_issue("duplicate_claim_id", "compiler claim ids must be unique"))
    unknown_spans = sorted(
        {
            spec["source_span_id"]
            for spec in COMPILER_CLAIM_SPECS
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
            for spec in COMPILER_CLAIM_SPECS
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
                f"{expected['missing_anchor_count']} compiler claim anchors were not found",
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
    if data.get("compiler_claim_inventory_ready") is not expected_ready:
        issues.append(
            _issue(
                "invalid_compiler_claim_inventory_ready",
                "compiler_claim_inventory_ready does not match source, reference, and ownership checks",
            )
        )
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "44" not in claim_boundary
        or "XLA/MLIR behavior" not in claim_boundary
        or "per-edit randomized reference results" not in claim_boundary
        or "32 percent kernel" not in claim_boundary
        or "15 percent pre/postprocessing" not in claim_boundary
        or "compiler adoption" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(
            _issue(
                "missing_claim_boundary",
                "claim_boundary must separate bounded compiler claims from executable IR, correctness, result, adoption, and parity proof",
            )
        )
    return AlphaEvolveCompilerClaimInventoryBoundaryValidation(
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


def render_alphaevolve_compiler_claim_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_compiler_claim_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve compiler claim inventory boundary",
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
    record: dict[str, Any] = {"path": path_label, "exists": _safe_is_file(path)}
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
    list[AlphaEvolveCompilerClaimInventoryBoundaryIssue],
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
            "compiler claim inventory boundary must be a JSON object",
        )
    ]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveCompilerClaimInventoryBoundaryIssue:
    return AlphaEvolveCompilerClaimInventoryBoundaryIssue(code, message)
