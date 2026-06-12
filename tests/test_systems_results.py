import hashlib
import json

from libreevolve.problems.benchmarks.systems_results import (
    SYSTEMS_ARTIFACT_INVENTORY_SCHEMA,
    SYSTEMS_EVIDENCE_BUNDLE_SCHEMA,
    SYSTEMS_RESULT_SCHEMA,
    render_systems_result_summary,
    systems_result_artifact_inventory,
    validate_systems_evidence_bundle,
    validate_systems_evidence_bundle_record,
    validate_systems_result_report,
)


def _gate(name: str, case_set: str, status: str = "passed") -> dict:
    return {
        "name": name,
        "status": status,
        "case_set_id": case_set,
        "sample_count": 8,
        "case_set_sha256": "a" * 64,
        "seeds": [11, 12],
        "metrics": {"pass_rate": 1.0, "speedup": 1.2},
    }


def _valid_report() -> dict:
    report = {
        "schema": SYSTEMS_RESULT_SCHEMA,
        "benchmark_id": "flashattention_ir_micro",
        "candidate_id": "program-000234",
        "domain": "kernel",
        "alphaevolve_ready": True,
        "gates": [
            _gate("optimization", "train_shapes"),
            _gate("heldout", "heldout_shapes"),
            _gate("reference_correctness", "random_reference_inputs"),
        ],
        "certification": {
            "schema": "libreevolve.paper_result_certification.v1",
            "claim_id": "flashattention_ir_micro_001",
            "paper_claim_ready": True,
        },
        "artifacts": [
            {
                "kind": "metrics",
                "path": "systems/flashattention/optimization-metrics.json",
                "sha256": "d" * 64,
                "bytes": 1024,
            },
            {
                "kind": "heldout_report",
                "path": "systems/flashattention/heldout.json",
                "sha256": "b" * 64,
                "bytes": 4096,
            },
            {
                "kind": "reference_report",
                "path": "systems/flashattention/reference.json",
                "sha256": "c" * 64,
                "bytes": 2048,
            },
        ],
    }
    report["application_provenance"] = {
        "boundary_statement": (
            "Local benchmark evidence is separate from domain-owner validated "
            "production claims."
        ),
        "records": [
            {
                "record_id": "kernel-owner",
                "role": "application_colead",
                "domain": "kernel",
                "responsible_label": "kernel application owner",
                "review_scope": "reviewed optimized kernel claim scope",
                "ownership_scope": "kernel benchmark and production workflow",
                "approval_state": "approved",
                "claim_links": ["flashattention_ir_micro"],
                "artifact_refs": ["systems/flashattention/optimization-metrics.json"],
            },
            {
                "record_id": "kernel-reviewer",
                "role": "domain_reviewer",
                "domain": "kernel",
                "responsible_label": "kernel domain reviewer",
                "review_scope": "reviewed held-out shape behavior",
                "ownership_scope": "kernel correctness review",
                "approval_state": "reviewed",
                "claim_links": ["flashattention_ir_micro"],
                "artifact_refs": ["systems/flashattention/heldout.json"],
            },
            {
                "record_id": "kernel-validation-owner",
                "role": "validation_infrastructure_owner",
                "domain": "kernel",
                "responsible_label": "kernel validation owner",
                "review_scope": "reviewed reference input validation",
                "ownership_scope": "reference runner infrastructure",
                "approval_state": "reviewed",
                "claim_links": ["flashattention_ir_micro"],
                "artifact_refs": ["systems/flashattention/reference.json"],
            },
            {
                "record_id": "kernel-approver",
                "role": "production_approver",
                "domain": "kernel",
                "responsible_label": "kernel production approver",
                "review_scope": "approved production-facing claim boundary",
                "ownership_scope": "deployment approval path",
                "approval_state": "approved",
                "claim_links": ["flashattention_ir_micro_001"],
                "artifact_refs": ["systems/flashattention/optimization-metrics.json"],
            },
        ],
    }
    report["claim_calibration"] = {
        "boundary_statement": (
            "Finite local gate metrics are separate from AlphaEvolve Section 3.3 "
            "result magnitudes unless calibrated here."
        ),
        "records": [
            {
                "claim_id": "flashattention_ir_micro_kernel_speedup",
                "domain": "kernel",
                "claim_kind": "kernel_speedup",
                "gate_name": "optimization",
                "metric_name": "speedup",
                "reported_value": 1.2,
                "unit": "speedup ratio",
                "baseline_label": "local baseline kernel",
                "denominator": "held shape corpus",
                "comparison_window": "single benchmark window",
                "aggregation_method": "arithmetic mean over shapes",
                "runtime_context": "local microbenchmark runtime",
                "claim_scope": "local kernel speedup smoke claim",
                "source_ref": "AlphaEvolve Section 3.3 systems-result pattern",
                "artifact_refs": ["systems/flashattention/optimization-metrics.json"],
            }
        ],
    }
    return report


def _valid_scheduling_report() -> dict:
    report = _valid_report()
    report["domain"] = "scheduling"
    for record in report["application_provenance"]["records"]:
        record["domain"] = "scheduling"
    for record in report["claim_calibration"]["records"]:
        record["domain"] = "scheduling"
        record["claim_kind"] = "scheduling_resource_recovery"
        record["unit"] = "resource recovery percentage"
        record["denominator"] = "historical workload and capacity snapshot"
    report["gates"][2] = {
        "name": "reference_correctness",
        "status": "not_applicable",
        "case_set_id": "not_applicable_reference",
        "rationale": "Scheduling heuristic only ranks feasible machines.",
    }
    report["scheduling_formulation"] = {
        "problem_class": "online_vector_bin_packing",
        "machine_role": "bin",
        "job_role": "item",
        "objective": "stranded_resource_minimization",
        "resource_dimensions": [
            {
                "name": "cpu",
                "unit": "normalized cpu",
                "capacity_field": "machine.cpu_capacity",
                "required_field": "job.required_cpu",
                "free_field": "machine.free_cpu",
            },
            {
                "name": "memory",
                "unit": "normalized memory",
                "capacity_field": "machine.memory_capacity",
                "required_field": "job.required_memory",
                "free_field": "machine.free_memory",
            },
        ],
        "snapshot_provenance": [
            {
                "snapshot_id": "historical-workload-capacity",
                "workload_source": "historical pending-job workload",
                "capacity_source": "historical machine capacity snapshot",
                "simulator_input_sha256": "e" * 64,
            }
        ],
        "stranded_resource_definition": (
            "unused CPU or memory that cannot be paired with pending job demand"
        ),
        "feature_mapping": (
            "heuristic required/free features map to CPU and memory demand and capacity"
        ),
        "artifact_refs": ["systems/flashattention/reference.json"],
    }
    report["scheduling_safety"] = {
        "feasibility_filter_id": "borg-feasible-machine-filter",
        "candidate_set_source": "machines already available and capable",
        "simulator_boundary": "historical workload simulator owns feasibility",
        "admission_boundary": "external scheduler admits or rejects jobs",
        "placement_boundary": "external scheduler performs placement",
        "ranking_function_scope": "score feasible machines only",
        "ranking_only": True,
        "can_admit_jobs": False,
        "can_reject_jobs": False,
        "can_place_jobs": False,
        "resource_invariants": [
            "candidate machine has sufficient CPU",
            "candidate machine has sufficient memory",
        ],
        "artifact_refs": ["systems/flashattention/reference.json"],
    }
    report["scheduling_deployment_readiness"] = {
        "heuristic_structure": "small readable scoring function over cpu and memory",
        "operator_review": "operator reviewed scheduling behavior and rollout boundary",
        "debuggability_notes": "score terms can be inspected per feasible machine",
        "deployment_ergonomics": "code heuristic can be deployed in scheduler path",
        "rollout_risk_controls": "staged rollout with rollback and shadow checks",
        "learned_policy_comparison": (
            "less interpretable learned baseline was rejected for operations"
        ),
        "predictability_checks": [
            "edge-capacity cases preserve feasible-machine ordering contract",
            "resource residual terms remain finite",
        ],
        "human_reviewed": True,
        "black_box_baseline_compared": True,
        "rollout_risk_reviewed": True,
        "artifact_refs": ["systems/flashattention/heldout.json"],
    }
    return report


def _valid_compiler_report() -> dict:
    report = _valid_report()
    report["domain"] = "compiler"
    for record in report["application_provenance"]["records"]:
        record["domain"] = "compiler"
    for record in report["claim_calibration"]["records"]:
        record["domain"] = "compiler"
        record["claim_kind"] = "compiler_kernel_speedup"
        record["claim_scope"] = "local compiler IR speedup smoke claim"
    report["compiler_ir_provenance"] = {
        "boundary_statement": (
            "Compiler IR provenance is separate from final speedup evidence."
        ),
        "ir_origin": "XLA-generated FlashAttention IR",
        "editability_boundary": (
            "IR is generated for debugging and not a stable developer API."
        ),
        "baseline_provenance": "compiler-generated already-optimized baseline",
        "reference_implementation_sha256": "1" * 64,
        "randomized_input_generator_id": "flashattention_random_inputs",
        "randomized_input_generator_sha256": "2" * 64,
        "numerical_tolerance_policy": "float32 atol=1e-5 rtol=1e-5",
        "final_expert_confirmation_scope": "expert reviewed all-input claim scope",
        "edit_records": [
            {
                "edit_id": "edit_001",
                "abstraction_level": "kernel_ir",
                "randomized_seed_count": 128,
                "reference_check_passed": True,
                "artifact_refs": ["systems/flashattention/reference.json"],
            }
        ],
    }
    report["compiler_stack_provenance"] = {
        "boundary_statement": (
            "Compiler stack provenance is separate from per-edit reference checks."
        ),
        "workload_model_configuration": "FlashAttention inference workload",
        "flashattention_kernel_identity": "flashattention_pallas_kernel_v1",
        "pallas_kernel_source_identity": "pallas kernel source module",
        "pallas_kernel_source_sha256": "3" * 64,
        "jax_preprocessing_boundary": "JAX wrapper prepares attention inputs",
        "jax_preprocessing_artifact_sha256": "4" * 64,
        "jax_postprocessing_boundary": "JAX wrapper restores output layout",
        "jax_postprocessing_artifact_sha256": "5" * 64,
        "xla_lowering_stage": "XLA GPU lowered IR",
        "hardware_target": "gpu inference configuration",
        "lowered_ir_sha256": "6" * 64,
        "optimization_decision_category": "memory_access_orchestration",
        "artifact_refs": ["systems/flashattention/reference.json"],
    }
    report["compiler_adoption_provenance"] = {
        "adoption_path": "existing_compiler_specific_use_case",
        "target_compiler": "XLA",
        "target_compiler_version": "debug-provenance-build",
        "target_pass_or_component": "FlashAttention GPU lowering",
        "use_case_scope": "bounded FlashAttention inference workload",
        "optimization_artifact_identity": "flashattention_lowering_candidate",
        "optimization_artifact_sha256": "7" * 64,
        "integration_owner": "compiler integration reviewer",
        "reviewer_signoff_scope": "reviewed use-case scoped integration path",
        "adoption_state": "reviewed",
        "rollout_or_revert_state": "not deployed; revert path documented",
        "workflow_handoff_boundary": (
            "records existing-compiler adoption separately from compiler-loop integration"
        ),
        "artifact_refs": ["systems/flashattention/reference.json"],
    }
    return report


def _valid_hardware_report() -> dict:
    report = _valid_report()
    report["domain"] = "hardware"
    for record in report["application_provenance"]["records"]:
        record["domain"] = "hardware"
    for record in report["claim_calibration"]["records"]:
        record["domain"] = "hardware"
        record["claim_kind"] = "hardware_power_area"
        record["claim_scope"] = "local RTL PPA smoke claim"
        record["unit"] = "power-area improvement"
        record["denominator"] = "single arithmetic-circuit synthesis context"
    report["hardware_rtl_eda_provenance"] = {
        "hdl_language": "verilog",
        "rtl_source_boundary": "already optimized TPU arithmetic-circuit RTL",
        "source_rtl_sha256": "8" * 64,
        "arithmetic_circuit_identity": "matrix multiplication unit arithmetic circuit",
        "synthesis_toolchain": "bounded synthesis and PPA flow",
        "synthesis_report_sha256": "9" * 64,
        "ppa_metric_provenance": "power, area, and timing report provenance",
        "ppa_report_sha256": "a" * 64,
        "timing_constraint_provenance": "timing constraints reviewed for target TPU",
        "power_area_constraint_provenance": "power and area constraints reviewed",
        "equivalence_method": "formal equivalence and robust RTL simulation",
        "formal_verification_artifact_sha256": "b" * 64,
        "equivalence_check_passed": True,
        "formal_verification_passed": True,
        "designer_review_scope": "TPU designer reviewed functionality and PPA scope",
        "designer_validated": True,
        "downstream_synthesis_tool": "independent downstream synthesis flow",
        "downstream_synthesis_confirmation": (
            "downstream synthesis independently found the same simplification"
        ),
        "downstream_synthesis_report_sha256": "c" * 64,
        "downstream_synthesis_confirmed": True,
        "rtl_flow_placement": "early RTL-stage contribution before synthesis",
        "standard_language_adoption_rationale": (
            "Verilog communication supports hardware-engineer trust"
        ),
        "integration_target": "upcoming TPU arithmetic circuit",
        "deployment_time_to_market_impact": (
            "records potential time-to-market impact separately from local metrics"
        ),
        "artifact_refs": ["systems/flashattention/reference.json"],
    }
    report["hardware_rewrite_provenance"] = {
        "source_verilog_sha256": "d" * 64,
        "modified_verilog_sha256": "e" * 64,
        "rewrite_diff_sha256": "f" * 64,
        "component_id": "tpu_matrix_multiply_arithmetic_circuit",
        "matrix_unit_context": "key arithmetic circuit in matrix multiplication unit",
        "semantic_rewrite_category": "unnecessary_bit_removal",
        "rewrite_rationale": "removed unused high-order bits while preserving function",
        "ppa_linkage": "removed bits link to power and area report deltas",
        "verification_linkage": "removed bits link to formal and reference checks",
        "changed_spans": [
            {
                "file": "rtl/tpu_arithmetic.v",
                "span_kind": "verilog_diff",
                "start_line": 42,
                "end_line": 47,
            }
        ],
        "removed_bits": [
            {
                "signal_id": "partial_product_unused",
                "bit_range": "[15:12]",
                "removal_rationale": "bits do not affect arithmetic output",
                "ppa_artifact_refs": ["systems/flashattention/optimization-metrics.json"],
                "verification_artifact_refs": ["systems/flashattention/reference.json"],
            }
        ],
        "artifact_refs": ["systems/flashattention/reference.json"],
    }
    return report


def _write_systems_files(report: dict, root) -> None:
    for artifact in report["artifacts"]:
        path = root / artifact["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = f"{artifact['kind']} evidence".encode("utf-8")
        path.write_bytes(raw)
        artifact["sha256"] = hashlib.sha256(raw).hexdigest()
        artifact["bytes"] = len(raw)


def _payload_hash(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _valid_bundle(tmp_path) -> dict:
    report = _valid_report()
    _write_systems_files(report, tmp_path)
    inventory = systems_result_artifact_inventory(report, tmp_path)
    return {
        "schema": SYSTEMS_EVIDENCE_BUNDLE_SCHEMA,
        "benchmark_id": report["benchmark_id"],
        "candidate_id": report["candidate_id"],
        "domain": report["domain"],
        "alphaevolve_ready": True,
        "report_sha256": _payload_hash(report),
        "inventory_sha256": _payload_hash(inventory),
        "inventory_records_sha256": inventory["records_sha256"],
        "report": report,
        "inventory": inventory,
    }


def test_systems_result_report_validates_heldout_and_reference_gates():
    validation = validate_systems_result_report(_valid_report())

    assert validation.ok is True
    assert validation.alphaevolve_ready is True
    assert validation.benchmark_id == "flashattention_ir_micro"
    assert validation.domain == "kernel"
    assert validation.issues == []


def test_systems_result_report_loads_json_file(tmp_path):
    path = tmp_path / "systems_report.json"
    path.write_text(json.dumps(_valid_report()), encoding="utf-8")

    validation = validate_systems_result_report(path)

    assert validation.ok is True
    assert validation.alphaevolve_ready is True


def test_systems_result_artifact_inventory_verifies_declared_files(tmp_path):
    report = _valid_report()
    _write_systems_files(report, tmp_path)

    inventory = systems_result_artifact_inventory(report, tmp_path)

    assert inventory["schema"] == SYSTEMS_ARTIFACT_INVENTORY_SCHEMA
    assert inventory["report_schema"] == SYSTEMS_RESULT_SCHEMA
    assert inventory["benchmark_id"] == "flashattention_ir_micro"
    assert inventory["candidate_id"] == "program-000234"
    assert inventory["artifact_root_policy"] == (
        "safe_relative_report_paths_under_artifact_root"
    )
    assert inventory["ok"] is True
    assert inventory["verified_count"] == 3
    assert inventory["missing_count"] == 0
    assert inventory["mismatch_count"] == 0
    assert inventory["invalid_count"] == 0
    assert {record["status"] for record in inventory["artifacts"]} == {
        "verified"
    }
    assert all("actual_sha256" in artifact for artifact in inventory["artifacts"])


def test_systems_evidence_bundle_validates_report_and_inventory(tmp_path):
    report = _valid_report()
    _write_systems_files(report, tmp_path)
    inventory = systems_result_artifact_inventory(report, tmp_path)

    validation = validate_systems_evidence_bundle(report, inventory)

    assert validation.ok is True
    assert validation.benchmark_id == "flashattention_ir_micro"
    assert validation.report_ok is True
    assert validation.inventory_ok is True
    assert validation.alphaevolve_ready is True
    assert validation.issues == []


def test_systems_evidence_bundle_record_validates_embedded_hashes(tmp_path):
    bundle = _valid_bundle(tmp_path)

    validation = validate_systems_evidence_bundle_record(bundle)

    assert validation.ok is True
    assert validation.benchmark_id == "flashattention_ir_micro"
    assert validation.report_ok is True
    assert validation.inventory_ok is True
    assert validation.alphaevolve_ready is True
    assert validation.issues == []


def test_systems_evidence_bundle_record_rejects_tampering(tmp_path):
    bundle = _valid_bundle(tmp_path)
    bundle["report"]["candidate_id"] = "program-tampered"

    validation = validate_systems_evidence_bundle_record(bundle)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "inventory_candidate_id_mismatch" in codes
    assert "bundle_candidate_id_mismatch" in codes
    assert "bundle_report_hash_mismatch" in codes


def test_systems_evidence_bundle_rejects_tampered_inventory(tmp_path):
    report = _valid_report()
    _write_systems_files(report, tmp_path)
    inventory = systems_result_artifact_inventory(report, tmp_path)
    inventory["benchmark_id"] = "other_benchmark"
    inventory["ok"] = False
    inventory["missing_count"] = 1

    validation = validate_systems_evidence_bundle(report, inventory)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.report_ok is True
    assert validation.inventory_ok is False
    assert validation.alphaevolve_ready is False
    assert "inventory_not_ok" in codes
    assert "inventory_benchmark_id_mismatch" in codes
    assert "inventory_missing_count_mismatch" in codes
    assert "inventory_missing_count_nonzero" in codes


def test_systems_result_artifact_inventory_reports_missing_mismatch_and_unsafe_paths(tmp_path):
    report = _valid_report()
    first = report["artifacts"][0]
    first_path = tmp_path / first["path"]
    first_path.parent.mkdir(parents=True, exist_ok=True)
    first_path.write_text("wrong", encoding="utf-8")
    first["sha256"] = "b" * 64
    first["bytes"] = 999
    report["artifacts"][1]["path"] = "missing/heldout.json"
    report["artifacts"][2]["path"] = "../escape-reference.json"

    inventory = systems_result_artifact_inventory(report, tmp_path)
    records = {artifact["kind"]: artifact for artifact in inventory["artifacts"]}

    assert inventory["ok"] is False
    assert inventory["mismatch_count"] == 1
    assert inventory["missing_count"] == 1
    assert inventory["invalid_count"] == 1
    assert records["metrics"]["status"] == "hash_mismatch"
    assert "artifact_hash_mismatch" in records["metrics"]["issues"]
    assert "artifact_bytes_mismatch" in records["metrics"]["issues"]
    assert records["heldout_report"]["status"] == "missing_file"
    assert records["reference_report"]["status"] == "unsafe_path"


def test_systems_result_report_rejects_ready_claim_without_required_gates():
    report = _valid_report()
    report["gates"] = [_gate("optimization", "train_shapes")]

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "missing_gate" in codes
    assert "invalid_alphaevolve_ready" in codes


def test_ready_report_requires_artifacts_for_passed_gates():
    report = _valid_report()
    report["artifacts"] = [
        artifact for artifact in report["artifacts"]
        if artifact["kind"] != "heldout_report"
    ]

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "missing_ready_gate_artifact" in codes


def test_ready_report_rejects_contradictory_certification_reference():
    report = _valid_report()
    report["certification"]["paper_claim_ready"] = False

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "invalid_ready_certification" in codes


def test_ready_report_requires_claim_calibration():
    report = _valid_report()
    report.pop("claim_calibration")

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "missing_claim_calibration" in codes
    assert "invalid_ready_claim_calibration" in codes


def test_claim_calibration_requires_metric_context_and_artifacts():
    report = _valid_report()
    record = report["claim_calibration"]["records"][0]
    record["metric_name"] = "not_a_metric"
    record["artifact_refs"] = ["systems/flashattention/missing.json"]
    record["unit"] = ""

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "invalid_claim_metric" in codes
    assert "invalid_claim_artifact_ref" in codes
    assert "invalid_claim_unit" in codes


def test_ready_report_requires_application_owner_reviewer_provenance():
    report = _valid_report()
    report.pop("application_provenance")

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "missing_application_provenance" in codes
    assert "invalid_ready_application_provenance" in codes


def test_application_provenance_requires_role_coverage_and_artifact_links():
    report = _valid_report()
    report["application_provenance"]["records"] = [
        report["application_provenance"]["records"][0]
    ]
    report["application_provenance"]["records"][0]["artifact_refs"] = [
        "systems/flashattention/missing-artifact.json"
    ]

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "missing_application_role_coverage" in codes
    assert "invalid_application_artifact_ref" in codes


def test_non_ready_report_can_reference_pending_certification():
    report = _valid_report()
    report["alphaevolve_ready"] = False
    report["gates"][1]["status"] = "failed"
    report["certification"]["paper_claim_ready"] = False
    report.pop("application_provenance")
    report.pop("claim_calibration")

    validation = validate_systems_result_report(report)

    assert validation.ok is True
    assert validation.alphaevolve_ready is False


def test_not_applicable_gate_requires_rationale_but_can_be_ready():
    report = _valid_scheduling_report()

    validation = validate_systems_result_report(report)

    assert validation.ok is True
    assert validation.alphaevolve_ready is True

    report["gates"][2].pop("rationale")
    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_reference_correctness_rationale" in codes


def test_ready_systems_report_rejects_domain_required_not_applicable_gates():
    cases = [
        ("kernel", "heldout", "invalid_ready_domain_heldout_gate"),
        (
            "compiler",
            "reference_correctness",
            "invalid_ready_domain_reference_correctness_gate",
        ),
        (
            "hardware",
            "reference_correctness",
            "invalid_ready_domain_reference_correctness_gate",
        ),
        ("systems", "heldout", "invalid_ready_domain_heldout_gate"),
        (
            "systems",
            "reference_correctness",
            "invalid_ready_domain_reference_correctness_gate",
        ),
    ]
    for domain, gate_name, issue_code in cases:
        report = _valid_report()
        report["domain"] = domain
        for record in report["application_provenance"]["records"]:
            record["domain"] = domain
        for record in report["claim_calibration"]["records"]:
            record["domain"] = domain
        gate = next(item for item in report["gates"] if item["name"] == gate_name)
        gate.clear()
        gate.update(
            {
                "name": gate_name,
                "status": "not_applicable",
                "case_set_id": f"not_applicable_{gate_name}",
                "rationale": "generic rationale is not enough for this domain",
            }
        )

        validation = validate_systems_result_report(report)
        codes = {issue.code for issue in validation.issues}

        assert validation.ok is False
        assert validation.alphaevolve_ready is False
        assert issue_code in codes


def test_ready_compiler_report_requires_ir_provenance():
    report = _valid_compiler_report()

    validation = validate_systems_result_report(report)

    assert validation.ok is True
    assert validation.alphaevolve_ready is True

    report.pop("compiler_ir_provenance")
    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "missing_compiler_ir_provenance" in codes
    assert "invalid_ready_compiler_ir_provenance" in codes


def test_ready_compiler_report_requires_stack_provenance():
    report = _valid_compiler_report()

    report.pop("compiler_stack_provenance")
    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "missing_compiler_stack_provenance" in codes
    assert "invalid_ready_compiler_stack_provenance" in codes


def test_compiler_ir_provenance_rejects_bad_edit_reference_checks():
    report = _valid_compiler_report()
    report["compiler_ir_provenance"]["reference_implementation_sha256"] = "bad"
    report["compiler_ir_provenance"]["edit_records"][0]["abstraction_level"] = (
        "source_python"
    )
    report["compiler_ir_provenance"]["edit_records"][0][
        "randomized_seed_count"
    ] = 0
    report["compiler_ir_provenance"]["edit_records"][0][
        "reference_check_passed"
    ] = False
    report["compiler_ir_provenance"]["edit_records"][0]["artifact_refs"] = [
        "systems/flashattention/missing.json"
    ]

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "invalid_compiler_ir_reference_hash" in codes
    assert "invalid_compiler_ir_abstraction_level" in codes
    assert "invalid_compiler_ir_randomized_seed_count" in codes
    assert "invalid_compiler_ir_reference_check" in codes
    assert "invalid_compiler_ir_artifact_ref" in codes


def test_compiler_stack_provenance_rejects_bad_stack_context():
    report = _valid_compiler_report()
    report["compiler_stack_provenance"]["workload_model_configuration"] = ""
    report["compiler_stack_provenance"]["pallas_kernel_source_sha256"] = "bad"
    report["compiler_stack_provenance"][
        "optimization_decision_category"
    ] = "loop_unrolling"
    report["compiler_stack_provenance"]["artifact_refs"] = [
        "systems/flashattention/missing.json"
    ]

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "invalid_compiler_stack_workload_model_configuration" in codes
    assert "invalid_compiler_stack_pallas_kernel_source_sha256" in codes
    assert "invalid_compiler_stack_decision_category" in codes
    assert "invalid_compiler_stack_artifact_ref" in codes


def test_ready_compiler_report_requires_adoption_provenance():
    report = _valid_compiler_report()

    report.pop("compiler_adoption_provenance")
    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "missing_compiler_adoption_provenance" in codes
    assert "invalid_ready_compiler_adoption_provenance" in codes


def test_compiler_adoption_provenance_rejects_bad_integration_path():
    report = _valid_compiler_report()
    adoption = report["compiler_adoption_provenance"]
    adoption["adoption_path"] = "direct_production_patch"
    adoption["target_pass_or_component"] = ""
    adoption["optimization_artifact_sha256"] = "bad"
    adoption["adoption_state"] = "rolled_out"
    adoption["artifact_refs"] = ["systems/flashattention/missing.json"]

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "invalid_compiler_adoption_path" in codes
    assert "invalid_compiler_adoption_target_pass_or_component" in codes
    assert "invalid_compiler_adoption_optimization_artifact_sha256" in codes
    assert "invalid_compiler_adoption_state" in codes
    assert "invalid_compiler_adoption_artifact_ref" in codes


def test_ready_hardware_report_requires_rtl_eda_provenance():
    report = _valid_hardware_report()

    validation = validate_systems_result_report(report)

    assert validation.ok is True
    assert validation.alphaevolve_ready is True

    report.pop("hardware_rtl_eda_provenance")
    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "missing_hardware_rtl_eda_provenance" in codes
    assert "invalid_ready_hardware_rtl_eda_provenance" in codes


def test_hardware_rtl_eda_provenance_rejects_bad_verification_context():
    report = _valid_hardware_report()
    rtl = report["hardware_rtl_eda_provenance"]
    rtl["hdl_language"] = "vhdl"
    rtl["synthesis_report_sha256"] = "bad"
    rtl["designer_validated"] = False
    rtl["downstream_synthesis_confirmed"] = False
    rtl["artifact_refs"] = ["systems/flashattention/missing.json"]

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "invalid_hardware_hdl_language" in codes
    assert "invalid_hardware_rtl_eda_synthesis_report_sha256" in codes
    assert "invalid_hardware_rtl_eda_designer_validated" in codes
    assert "invalid_hardware_rtl_eda_downstream_synthesis_confirmed" in codes
    assert "invalid_hardware_rtl_eda_artifact_ref" in codes


def test_ready_hardware_report_requires_rewrite_provenance():
    report = _valid_hardware_report()

    report.pop("hardware_rewrite_provenance")
    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "missing_hardware_rewrite_provenance" in codes
    assert "invalid_ready_hardware_rewrite_provenance" in codes


def test_hardware_rewrite_provenance_rejects_bad_bit_removal_context():
    report = _valid_hardware_report()
    rewrite = report["hardware_rewrite_provenance"]
    rewrite["source_verilog_sha256"] = "bad"
    rewrite["semantic_rewrite_category"] = "timing_retune"
    rewrite["changed_spans"][0]["start_line"] = 50
    rewrite["changed_spans"][0]["end_line"] = 40
    rewrite["removed_bits"][0]["bit_range"] = ""
    rewrite["removed_bits"][0]["ppa_artifact_refs"] = [
        "systems/flashattention/missing.json"
    ]

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "invalid_hardware_rewrite_source_verilog_sha256" in codes
    assert "invalid_hardware_rewrite_category" in codes
    assert "invalid_hardware_rewrite_changed_span_end" in codes
    assert "invalid_hardware_rewrite_removed_bit_bit_range" in codes
    assert "invalid_hardware_rewrite_removed_bit_ppa_ref" in codes


def test_ready_scheduling_report_requires_ranking_only_safety():
    report = _valid_scheduling_report()
    report.pop("scheduling_safety")

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "missing_scheduling_safety" in codes
    assert "invalid_ready_scheduling_safety" in codes


def test_ready_scheduling_report_requires_vector_bin_packing_formulation():
    report = _valid_scheduling_report()
    report.pop("scheduling_formulation")

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "missing_scheduling_formulation" in codes
    assert "invalid_ready_scheduling_formulation" in codes


def test_scheduling_formulation_requires_cpu_memory_snapshots_and_refs():
    report = _valid_scheduling_report()
    report["scheduling_formulation"]["resource_dimensions"] = [
        report["scheduling_formulation"]["resource_dimensions"][0]
    ]
    report["scheduling_formulation"]["snapshot_provenance"][0][
        "simulator_input_sha256"
    ] = "bad"
    report["scheduling_formulation"]["artifact_refs"] = [
        "systems/flashattention/missing.json"
    ]

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "missing_scheduling_resource_dimension" in codes
    assert "invalid_scheduling_simulator_input_hash" in codes
    assert "invalid_scheduling_formulation_artifact_ref" in codes


def test_scheduling_safety_rejects_direct_authority_and_bad_refs():
    report = _valid_scheduling_report()
    report["scheduling_safety"]["can_place_jobs"] = True
    report["scheduling_safety"]["resource_invariants"] = []
    report["scheduling_safety"]["artifact_refs"] = [
        "systems/flashattention/missing.json"
    ]

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "invalid_scheduling_placement_authority" in codes
    assert "invalid_scheduling_resource_invariants" in codes
    assert "invalid_scheduling_artifact_ref" in codes


def test_ready_scheduling_report_requires_deployment_readiness():
    report = _valid_scheduling_report()
    report.pop("scheduling_deployment_readiness")

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "missing_scheduling_deployment_readiness" in codes
    assert "invalid_ready_scheduling_deployment_readiness" in codes


def test_scheduling_deployment_readiness_requires_review_controls_and_refs():
    report = _valid_scheduling_report()
    report["scheduling_deployment_readiness"]["human_reviewed"] = False
    report["scheduling_deployment_readiness"]["predictability_checks"] = []
    report["scheduling_deployment_readiness"]["artifact_refs"] = [
        "systems/flashattention/missing.json"
    ]

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_ready is False
    assert "invalid_scheduling_human_reviewed" in codes
    assert "invalid_scheduling_predictability_checks" in codes
    assert "invalid_scheduling_deployment_artifact_ref" in codes


def test_non_ready_scheduling_report_can_omit_safety_provenance():
    report = _valid_scheduling_report()
    report["alphaevolve_ready"] = False
    report["gates"][1]["status"] = "failed"
    report["certification"]["paper_claim_ready"] = False
    report.pop("scheduling_safety")
    report.pop("scheduling_formulation")
    report.pop("scheduling_deployment_readiness")

    validation = validate_systems_result_report(report)

    assert validation.ok is True
    assert validation.alphaevolve_ready is False


def test_non_scheduling_report_rejects_scheduling_safety_block():
    report = _valid_report()
    report["scheduling_safety"] = _valid_scheduling_report()["scheduling_safety"]

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "unexpected_scheduling_safety" in codes


def test_non_scheduling_report_rejects_scheduling_formulation_block():
    report = _valid_report()
    report["scheduling_formulation"] = _valid_scheduling_report()[
        "scheduling_formulation"
    ]

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "unexpected_scheduling_formulation" in codes


def test_non_scheduling_report_rejects_scheduling_deployment_block():
    report = _valid_report()
    report["scheduling_deployment_readiness"] = _valid_scheduling_report()[
        "scheduling_deployment_readiness"
    ]

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "unexpected_scheduling_deployment_readiness" in codes


def test_systems_result_report_rejects_unsafe_artifacts_and_bad_metrics():
    report = _valid_report()
    report["gates"][1]["sample_count"] = 0
    report["gates"][1]["case_set_sha256"] = "bad"
    report["gates"][1]["metrics"] = {"pass_rate": float("nan")}
    report["artifacts"][0].update({"path": "C:/secret.json", "sha256": "bad", "bytes": 0})

    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_heldout_sample_count" in codes
    assert "invalid_heldout_case_set_hash" in codes
    assert "invalid_heldout_metrics" in codes
    assert "invalid_artifact_path" in codes
    assert "invalid_artifact_hash" in codes
    assert "invalid_artifact_bytes" in codes


def test_systems_result_summary_renders_gates_and_readiness():
    summary = render_systems_result_summary(_valid_report())

    assert "Systems result report: flashattention_ir_micro" in summary
    assert "| schema_status | ok |" in summary
    assert "| alphaevolve_ready | yes |" in summary
    assert "| claim_calibration_records | 1 |" in summary
    assert "| application_provenance_records | 4 |" in summary
    assert "| scheduling_formulation | absent |" in summary
    assert "| scheduling_safety | absent |" in summary
    assert "| scheduling_deployment_readiness | absent |" in summary
    assert "| compiler_ir_provenance | absent |" in summary
    assert "| compiler_stack_provenance | absent |" in summary
    assert "| compiler_adoption_provenance | absent |" in summary
    assert "| hardware_rtl_eda_provenance | absent |" in summary
    assert "| hardware_rewrite_provenance | absent |" in summary
    assert "optimization=passed" in summary
    assert "heldout=passed" in summary
    assert "reference_correctness=passed" in summary
