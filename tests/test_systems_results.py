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
    return {
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


def test_non_ready_report_can_reference_pending_certification():
    report = _valid_report()
    report["alphaevolve_ready"] = False
    report["gates"][1]["status"] = "failed"
    report["certification"]["paper_claim_ready"] = False

    validation = validate_systems_result_report(report)

    assert validation.ok is True
    assert validation.alphaevolve_ready is False


def test_not_applicable_gate_requires_rationale_but_can_be_ready():
    report = _valid_report()
    report["domain"] = "scheduling"
    report["gates"][2] = {
        "name": "reference_correctness",
        "status": "not_applicable",
        "case_set_id": "not_applicable_reference",
        "rationale": "Scheduling simulator has no reference-code equivalence oracle.",
    }

    validation = validate_systems_result_report(report)

    assert validation.ok is True
    assert validation.alphaevolve_ready is True

    report["gates"][2].pop("rationale")
    validation = validate_systems_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_reference_correctness_rationale" in codes


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
    assert "optimization=passed" in summary
    assert "heldout=passed" in summary
    assert "reference_correctness=passed" in summary
