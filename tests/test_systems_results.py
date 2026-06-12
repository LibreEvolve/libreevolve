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
    assert "optimization=passed" in summary
    assert "heldout=passed" in summary
    assert "reference_correctness=passed" in summary
