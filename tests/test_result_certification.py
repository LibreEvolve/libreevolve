import json

from libreevolve.problems.benchmarks.result_certification import (
    PAPER_CERTIFICATION_SCHEMA,
    render_certification_summary,
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
