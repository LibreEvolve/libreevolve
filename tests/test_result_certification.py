import hashlib
import json

from libreevolve.problems.benchmarks.result_certification import (
    CERTIFICATION_ARTIFACT_INVENTORY_SCHEMA,
    PAPER_CERTIFICATION_SCHEMA,
    certification_artifact_inventory,
    render_certification_summary,
    validate_certification_evidence_bundle,
    validate_paper_result_certification,
)


def _valid_certification() -> dict:
    return {
        "schema": PAPER_CERTIFICATION_SCHEMA,
        "claim_id": "circle26_sum_radii_run_001",
        "benchmark_id": "unit_square_circle_packing_26",
        "candidate_id": "program-000123",
        "certification_level": "paper_claim",
        "verdict": "passed",
        "verifier": {
            "kind": "independent_script",
            "name": "circle_packing_exact_checker",
            "independent_from_search": True,
            "version": "1.0.0",
        },
        "scope": {
            "claim": "26-circle unit-square construction satisfies non-overlap constraints",
            "pass_fail_scope": "pairwise non-overlap and in-container checks for the exported construction",
            "limitations": ["local deterministic checker only"],
        },
        "evidence": [
            {
                "kind": "verifier_output",
                "status": "passed",
                "path": "certifications/circle26/verifier-output.json",
                "sha256": "a" * 64,
                "bytes": 2048,
            }
        ],
        "artifacts": [
            {
                "kind": "verifier_log",
                "path": "certifications/circle26/verifier.log",
                "sha256": "c" * 64,
                "bytes": 1024,
            },
            {
                "kind": "certificate",
                "path": "certifications/circle26/certificate.json",
                "sha256": "b" * 64,
                "bytes": 4096,
            }
        ],
    }


def _write_certification_files(report: dict, root) -> None:
    for section in ("evidence", "artifacts"):
        for record in report[section]:
            path = root / record["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = f"{section}:{record['kind']}".encode("utf-8")
            path.write_bytes(raw)
            record["sha256"] = hashlib.sha256(raw).hexdigest()
            record["bytes"] = len(raw)


def test_paper_result_certification_validates_paper_claim_ready_record():
    validation = validate_paper_result_certification(_valid_certification())

    assert validation.ok is True
    assert validation.paper_claim_ready is True
    assert validation.claim_id == "circle26_sum_radii_run_001"
    assert validation.certification_level == "paper_claim"
    assert validation.verdict == "passed"
    assert validation.issues == []


def test_paper_result_certification_loads_json_file(tmp_path):
    path = tmp_path / "certification.json"
    path.write_text(json.dumps(_valid_certification()), encoding="utf-8")

    validation = validate_paper_result_certification(path)

    assert validation.ok is True
    assert validation.paper_claim_ready is True


def test_certification_artifact_inventory_verifies_evidence_and_artifacts(tmp_path):
    report = _valid_certification()
    _write_certification_files(report, tmp_path)

    inventory = certification_artifact_inventory(report, tmp_path)

    assert inventory["schema"] == CERTIFICATION_ARTIFACT_INVENTORY_SCHEMA
    assert inventory["report_schema"] == PAPER_CERTIFICATION_SCHEMA
    assert inventory["claim_id"] == "circle26_sum_radii_run_001"
    assert inventory["benchmark_id"] == "unit_square_circle_packing_26"
    assert inventory["candidate_id"] == "program-000123"
    assert inventory["artifact_root_policy"] == (
        "safe_relative_report_paths_under_artifact_root"
    )
    assert inventory["ok"] is True
    assert inventory["record_count"] == 3
    assert inventory["verified_count"] == 3
    assert inventory["missing_count"] == 0
    assert inventory["mismatch_count"] == 0
    assert inventory["invalid_count"] == 0
    assert {record["status"] for record in inventory["records"]} == {
        "verified"
    }
    assert {record["section"] for record in inventory["records"]} == {
        "evidence",
        "artifacts",
    }


def test_certification_evidence_bundle_validates_report_and_inventory(tmp_path):
    report = _valid_certification()
    _write_certification_files(report, tmp_path)
    inventory = certification_artifact_inventory(report, tmp_path)

    validation = validate_certification_evidence_bundle(report, inventory)

    assert validation.ok is True
    assert validation.claim_id == "circle26_sum_radii_run_001"
    assert validation.report_ok is True
    assert validation.inventory_ok is True
    assert validation.paper_claim_ready is True
    assert validation.issues == []


def test_certification_evidence_bundle_rejects_tampered_inventory(tmp_path):
    report = _valid_certification()
    _write_certification_files(report, tmp_path)
    inventory = certification_artifact_inventory(report, tmp_path)
    inventory["claim_id"] = "other_claim"
    inventory["ok"] = False
    inventory["missing_count"] = 1

    validation = validate_certification_evidence_bundle(report, inventory)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.report_ok is True
    assert validation.inventory_ok is False
    assert validation.paper_claim_ready is False
    assert "inventory_not_ok" in codes
    assert "inventory_claim_id_mismatch" in codes
    assert "inventory_missing_count_mismatch" in codes
    assert "inventory_missing_count_nonzero" in codes


def test_certification_artifact_inventory_reports_missing_mismatch_and_unsafe_paths(tmp_path):
    report = _valid_certification()
    evidence = report["evidence"][0]
    evidence_path = tmp_path / evidence["path"]
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text("wrong", encoding="utf-8")
    evidence["sha256"] = "b" * 64
    evidence["bytes"] = 999
    report["artifacts"][0]["path"] = "missing/verifier.log"
    report["artifacts"][1]["path"] = "../escape-certificate.json"

    inventory = certification_artifact_inventory(report, tmp_path)
    records = {
        (record["section"], record["kind"]): record
        for record in inventory["records"]
    }

    assert inventory["ok"] is False
    assert inventory["mismatch_count"] == 1
    assert inventory["missing_count"] == 1
    assert inventory["invalid_count"] == 1
    assert records[("evidence", "verifier_output")]["status"] == "hash_mismatch"
    assert "record_hash_mismatch" in records[("evidence", "verifier_output")]["issues"]
    assert "record_bytes_mismatch" in records[("evidence", "verifier_output")]["issues"]
    assert records[("artifacts", "verifier_log")]["status"] == "missing_file"
    assert records[("artifacts", "certificate")]["status"] == "unsafe_path"


def test_local_validator_record_is_valid_but_not_paper_claim_ready():
    report = _valid_certification()
    report["certification_level"] = "local_validator"
    report["verdict"] = "passed"
    report["verifier"] = {
        "kind": "local_evaluator",
        "name": "problem.validate",
        "independent_from_search": False,
    }

    validation = validate_paper_result_certification(report)

    assert validation.ok is True
    assert validation.paper_claim_ready is False


def test_paper_claim_rejects_local_or_unpassed_evidence():
    report = _valid_certification()
    report["verifier"] = {
        "kind": "local_evaluator",
        "name": "problem.validate",
        "independent_from_search": False,
    }
    report["verdict"] = "failed"
    report["evidence"][0]["status"] = "failed"

    validation = validate_paper_result_certification(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.paper_claim_ready is False
    assert "paper_claim_not_passed" in codes
    assert "paper_claim_local_verifier" in codes
    assert "paper_claim_not_independent" in codes
    assert "paper_claim_missing_passed_evidence" in codes


def test_paper_claim_requires_artifact_kind_matching_passed_evidence():
    report = _valid_certification()
    report["artifacts"] = [
        artifact for artifact in report["artifacts"]
        if artifact["kind"] != "verifier_log"
    ]

    validation = validate_paper_result_certification(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "paper_claim_missing_evidence_artifact" in codes


def test_certification_requires_safe_hashed_evidence_and_artifacts():
    report = _valid_certification()
    report["scope"]["claim"] = ""
    report["evidence"][0].update({"path": "../secret.json", "sha256": "bad", "bytes": 0})
    report["artifacts"][0].update({"path": "C:/secret.json", "sha256": "bad", "bytes": 0})

    validation = validate_paper_result_certification(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_scope_claim" in codes
    assert "invalid_evidence_path" in codes
    assert "invalid_evidence_hash" in codes
    assert "invalid_evidence_bytes" in codes
    assert "invalid_artifact_path" in codes
    assert "invalid_artifact_hash" in codes
    assert "invalid_artifact_bytes" in codes


def test_certification_summary_renders_claim_readiness():
    summary = render_certification_summary(_valid_certification())

    assert "Paper result certification: circle26_sum_radii_run_001" in summary
    assert "| schema_status | ok |" in summary
    assert "| paper_claim_ready | yes |" in summary
    assert "| certification_level | paper_claim |" in summary
    assert "| verdict | passed |" in summary
    assert "| verifier_kind | independent_script |" in summary
    assert "| evidence_count | 1 |" in summary
