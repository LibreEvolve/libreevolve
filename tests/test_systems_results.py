import json

from libreevolve.problems.benchmarks.systems_results import (
    SYSTEMS_RESULT_SCHEMA,
    render_systems_result_summary,
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
