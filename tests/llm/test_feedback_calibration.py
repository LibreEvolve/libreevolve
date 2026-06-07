import hashlib
import json

from libreevolve.llm.feedback_calibration import (
    LLM_FEEDBACK_CALIBRATION_ARTIFACT_INVENTORY_SCHEMA,
    LLM_FEEDBACK_CALIBRATION_SCHEMA,
    feedback_calibration_artifact_inventory,
    render_feedback_calibration_summary,
    validate_feedback_calibration_report,
)


def _artifact(kind: str, path: str) -> dict:
    return {
        "kind": kind,
        "path": path,
        "sha256": "a" * 64,
        "bytes": 1024,
    }


def _valid_report() -> dict:
    return {
        "schema": LLM_FEEDBACK_CALIBRATION_SCHEMA,
        "report_id": "feedback_calibration_2026_06_07",
        "calibration_ready": True,
        "graders": [
            {
                "name": "correctness",
                "metric": "correctness_score",
                "normalization": "configured_bounds_to_unit_interval",
                "direction": "maximize",
            }
        ],
        "tasks": [
            {"task_id": "hello_world", "family": "smoke"},
            {"task_id": "sorting", "family": "smoke"},
        ],
        "records": [
            {
                "grader": "correctness",
                "task_id": "hello_world",
                "seed": 101,
                "expected_normalized_score": 0.75,
                "observed_normalized_score": 0.7,
                "absolute_error": 0.05,
            },
            {
                "grader": "correctness",
                "task_id": "sorting",
                "seed": 101,
                "expected_normalized_score": 0.3,
                "observed_normalized_score": 0.4,
                "absolute_error": 0.1,
            },
        ],
        "artifacts": [
            _artifact("calibration_report", "feedback/calibration.json"),
            _artifact("raw_records", "feedback/raw-records.jsonl"),
        ],
    }


def test_feedback_calibration_report_validates_multi_task_ready_record():
    validation = validate_feedback_calibration_report(_valid_report())

    assert validation.ok is True
    assert validation.calibration_ready is True
    assert validation.grader_count == 1
    assert validation.task_count == 2
    assert validation.record_count == 2
    assert validation.issues == []


def test_feedback_calibration_report_loads_json_file(tmp_path):
    path = tmp_path / "feedback-calibration.json"
    path.write_text(json.dumps(_valid_report()), encoding="utf-8")

    validation = validate_feedback_calibration_report(path)

    assert validation.ok is True
    assert validation.calibration_ready is True


def test_feedback_calibration_artifact_inventory_verifies_declared_files(tmp_path):
    report = _valid_report()
    for artifact in report["artifacts"]:
        path = tmp_path / artifact["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = f"{artifact['kind']} evidence".encode("utf-8")
        path.write_bytes(raw)
        artifact["sha256"] = hashlib.sha256(raw).hexdigest()
        artifact["bytes"] = len(raw)

    inventory = feedback_calibration_artifact_inventory(report, tmp_path)

    assert inventory["schema"] == LLM_FEEDBACK_CALIBRATION_ARTIFACT_INVENTORY_SCHEMA
    assert inventory["report_schema"] == LLM_FEEDBACK_CALIBRATION_SCHEMA
    assert inventory["report_id"] == "feedback_calibration_2026_06_07"
    assert inventory["artifact_root_policy"] == (
        "safe_relative_calibration_paths_under_artifact_root"
    )
    assert inventory["ok"] is True
    assert inventory["artifact_count"] == 2
    assert inventory["verified_count"] == 2
    assert inventory["missing_count"] == 0
    assert inventory["mismatch_count"] == 0
    assert inventory["invalid_count"] == 0
    assert {record["status"] for record in inventory["artifacts"]} == {
        "verified"
    }


def test_feedback_calibration_artifact_inventory_reports_bad_references(tmp_path):
    report = _valid_report()
    report["artifacts"].extend(
        [
            _artifact("plot", "feedback/missing.png"),
            _artifact("grader_config", "../escape.json"),
        ]
    )
    first = report["artifacts"][0]
    first_path = tmp_path / first["path"]
    first_path.parent.mkdir(parents=True, exist_ok=True)
    first_path.write_text("wrong", encoding="utf-8")
    first["sha256"] = "b" * 64
    first["bytes"] = 999

    inventory = feedback_calibration_artifact_inventory(report, tmp_path)
    records = {record["kind"]: record for record in inventory["artifacts"]}

    assert inventory["ok"] is False
    assert inventory["mismatch_count"] == 1
    assert inventory["missing_count"] == 2
    assert inventory["invalid_count"] == 1
    assert records["calibration_report"]["status"] == "hash_mismatch"
    assert "artifact_hash_mismatch" in records["calibration_report"]["issues"]
    assert "artifact_bytes_mismatch" in records["calibration_report"]["issues"]
    assert records["raw_records"]["status"] == "missing_file"
    assert records["grader_config"]["status"] == "unsafe_path"


def test_feedback_calibration_ready_requires_multiple_tasks_records_and_artifacts():
    report = _valid_report()
    report["tasks"] = [{"task_id": "hello_world"}]
    report["records"] = []
    report["artifacts"] = []

    validation = validate_feedback_calibration_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.calibration_ready is False
    assert "insufficient_ready_tasks" in codes
    assert "missing_ready_records" in codes
    assert "missing_ready_artifacts" in codes


def test_feedback_calibration_rejects_bad_scores_and_missing_coverage():
    report = _valid_report()
    report["records"] = [
        {
            "grader": "correctness",
            "task_id": "hello_world",
            "seed": 101,
            "expected_normalized_score": 0.25,
            "observed_normalized_score": 0.75,
            "absolute_error": 0.1,
        }
    ]

    validation = validate_feedback_calibration_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.calibration_ready is False
    assert "absolute_error_mismatch" in codes
    assert "missing_grader_task_coverage" in codes


def test_feedback_calibration_summary_renders_readiness():
    summary = render_feedback_calibration_summary(_valid_report())

    assert "LLM feedback calibration: feedback_calibration_2026_06_07" in summary
    assert "| schema_status | ok |" in summary
    assert "| calibration_ready | yes |" in summary
    assert "| grader_count | 1 |" in summary
