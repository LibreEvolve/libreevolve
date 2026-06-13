import hashlib
import json

from libreevolve.problems.benchmarks.benchmark_hardening import (
    BENCHMARK_HARDENING_BUNDLE_SCHEMA,
    BENCHMARK_HARDENING_ARTIFACT_INVENTORY_SCHEMA,
    BENCHMARK_HARDENING_SCHEMA,
    benchmark_hardening_artifact_inventory,
    render_benchmark_hardening_summary,
    validate_benchmark_evidence_scope,
    validate_benchmark_hardening_report,
    write_matrix_smoke_hardening_bundle,
    write_sorting_network_hardening_bundle,
)
from libreevolve.problems.benchmarks.example_scope import (
    example_benchmark_scope_records,
)


def _threat(
    category: str,
    kind: str = "static_ast",
    protected_signal_ids: list[str] | None = None,
) -> dict:
    return {
        "category": category,
        "protected_signal_ids": protected_signal_ids or [
            "matmul_operation_count",
            "matmul_correctness",
        ],
        "detector": {
            "kind": kind,
            "description": f"Detects {category} attempts.",
        },
    }


def _negative_fixture(category: str, fixture_id: str | None = None, status: str = "passed") -> dict:
    fixture_id = fixture_id or f"reject_{category}"
    return {
        "id": fixture_id,
        "category": category,
        "status": status,
        "path": f"hardening/{fixture_id}.json",
        "sha256": "a" * 64,
        "bytes": 1024,
    }


def _valid_report() -> dict:
    return {
        "schema": BENCHMARK_HARDENING_SCHEMA,
        "benchmark_id": "matrix_multiplication_smoke",
        "level": "benchmark",
        "protected_signals": [
            {
                "id": "matmul_operation_count",
                "kind": "operation_count",
                "description": "Counts scalar multiplications in the candidate matmul implementation.",
            },
            {
                "id": "matmul_correctness",
                "kind": "correctness",
                "description": "Requires exact matrix multiplication on validator cases.",
            },
        ],
        "shortcut_threats": [
            _threat("hardcoded_cases", "randomized_cases"),
            _threat("library_delegation", "static_ast"),
            _threat("dead_code_counter", "static_ast"),
        ],
        "negative_fixtures": [
            _negative_fixture("hardcoded_cases"),
            _negative_fixture("library_delegation"),
            _negative_fixture("dead_code_counter"),
        ],
        "artifacts": [
            {
                "kind": "hardening_report",
                "path": "hardening/matrix_smoke/report.json",
                "sha256": "b" * 64,
                "bytes": 2048,
            }
        ],
    }


def _matrix_scope_record() -> dict:
    return next(
        record
        for record in example_benchmark_scope_records()
        if record["problem_id"] == "matrix_multiplication"
    )


def _write_report_files(report: dict, root) -> None:
    for section in ("negative_fixtures", "artifacts"):
        for record in report[section]:
            path = root / record["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            label = record.get("kind", record.get("category", "unknown"))
            raw = f"{section}:{label}".encode("utf-8")
            path.write_bytes(raw)
            record["sha256"] = hashlib.sha256(raw).hexdigest()
            record["bytes"] = len(raw)


def test_benchmark_hardening_validates_benchmark_ready_report():
    validation = validate_benchmark_hardening_report(_valid_report())

    assert validation.ok is True
    assert validation.benchmark_ready is True
    assert validation.benchmark_id == "matrix_multiplication_smoke"
    assert validation.level == "benchmark"
    assert validation.issues == []


def test_benchmark_hardening_loads_json_file(tmp_path):
    path = tmp_path / "hardening.json"
    path.write_text(json.dumps(_valid_report()), encoding="utf-8")

    validation = validate_benchmark_hardening_report(path)

    assert validation.ok is True
    assert validation.benchmark_ready is True


def test_benchmark_hardening_artifact_inventory_verifies_fixture_and_artifact_files(tmp_path):
    report = _valid_report()
    _write_report_files(report, tmp_path)

    inventory = benchmark_hardening_artifact_inventory(report, tmp_path)

    assert inventory["schema"] == BENCHMARK_HARDENING_ARTIFACT_INVENTORY_SCHEMA
    assert inventory["report_schema"] == BENCHMARK_HARDENING_SCHEMA
    assert inventory["benchmark_id"] == "matrix_multiplication_smoke"
    assert inventory["level"] == "benchmark"
    assert inventory["artifact_root_policy"] == (
        "safe_relative_report_paths_under_artifact_root"
    )
    assert inventory["ok"] is True
    assert inventory["record_count"] == 4
    assert inventory["verified_count"] == 4
    assert inventory["missing_count"] == 0
    assert inventory["mismatch_count"] == 0
    assert inventory["invalid_count"] == 0
    assert {record["status"] for record in inventory["records"]} == {
        "verified"
    }
    assert {record["section"] for record in inventory["records"]} == {
        "negative_fixtures",
        "artifacts",
    }


def test_benchmark_evidence_scope_allows_smoke_hardening_for_smoke_example(tmp_path):
    report = _valid_report()
    report["level"] = "smoke"
    _write_report_files(report, tmp_path)
    inventory = benchmark_hardening_artifact_inventory(report, tmp_path)

    validation = validate_benchmark_evidence_scope(
        report,
        _matrix_scope_record(),
        inventory,
    )

    assert validation.ok is True
    assert validation.hardening_ok is True
    assert validation.inventory_ok is True
    assert validation.benchmark_id == "matrix_multiplication_smoke"
    assert validation.scope_level == "smoke"
    assert validation.hardening_level == "smoke"
    assert validation.alphaevolve_comparable is False
    assert validation.issues == []


def test_benchmark_evidence_scope_rejects_smoke_example_promotion(tmp_path):
    report = _valid_report()
    _write_report_files(report, tmp_path)
    inventory = benchmark_hardening_artifact_inventory(report, tmp_path)

    validation = validate_benchmark_evidence_scope(
        report,
        _matrix_scope_record(),
        inventory,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.hardening_ok is True
    assert validation.inventory_ok is True
    assert "smoke_scope_promoted" in codes


def test_benchmark_evidence_scope_rejects_bad_inventory(tmp_path):
    report = _valid_report()
    report["level"] = "smoke"
    _write_report_files(report, tmp_path)
    inventory = benchmark_hardening_artifact_inventory(report, tmp_path)
    inventory["ok"] = False
    inventory["missing_count"] = 1

    validation = validate_benchmark_evidence_scope(
        report,
        _matrix_scope_record(),
        inventory,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.hardening_ok is True
    assert validation.inventory_ok is False
    assert "inventory_not_ok" in codes
    assert "inventory_missing_count_mismatch" in codes
    assert "inventory_missing_count_nonzero" in codes


def test_benchmark_hardening_artifact_inventory_reports_missing_mismatch_and_unsafe_paths(tmp_path):
    report = _valid_report()
    first = report["negative_fixtures"][0]
    first_path = tmp_path / first["path"]
    first_path.parent.mkdir(parents=True, exist_ok=True)
    first_path.write_text("wrong", encoding="utf-8")
    first["sha256"] = "b" * 64
    first["bytes"] = 999
    report["negative_fixtures"][1]["path"] = "missing/library-delegation.json"
    third = report["negative_fixtures"][2]
    third_path = tmp_path / third["path"]
    third_path.parent.mkdir(parents=True, exist_ok=True)
    third_raw = b"dead code counter fixture"
    third_path.write_bytes(third_raw)
    third["sha256"] = hashlib.sha256(third_raw).hexdigest()
    third["bytes"] = len(third_raw)
    report["artifacts"][0]["path"] = "../escape-hardening.json"

    inventory = benchmark_hardening_artifact_inventory(report, tmp_path)
    records = {
        (record["section"], record["kind"]): record
        for record in inventory["records"]
    }

    assert inventory["ok"] is False
    assert inventory["mismatch_count"] == 1
    assert inventory["missing_count"] == 1
    assert inventory["invalid_count"] == 1
    assert records[("negative_fixtures", "hardcoded_cases")]["status"] == "hash_mismatch"
    assert "record_hash_mismatch" in records[("negative_fixtures", "hardcoded_cases")]["issues"]
    assert "record_bytes_mismatch" in records[("negative_fixtures", "hardcoded_cases")]["issues"]
    assert records[("negative_fixtures", "library_delegation")]["status"] == "missing_file"
    assert records[("artifacts", "hardening_report")]["status"] == "unsafe_path"


def test_smoke_level_can_be_valid_without_full_negative_fixture_coverage():
    report = _valid_report()
    report["level"] = "smoke"
    report["negative_fixtures"] = [_negative_fixture("hardcoded_cases")]

    validation = validate_benchmark_hardening_report(report)

    assert validation.ok is True
    assert validation.benchmark_ready is False


def test_benchmark_level_requires_passed_negative_fixture_per_shortcut():
    report = _valid_report()
    report["negative_fixtures"] = [
        _negative_fixture("hardcoded_cases"),
        _negative_fixture("library_delegation", status="failed"),
    ]

    validation = validate_benchmark_hardening_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.benchmark_ready is False
    assert "missing_negative_fixture" in codes


def test_shortcut_threats_must_link_known_protected_signals():
    report = _valid_report()
    del report["shortcut_threats"][0]["protected_signal_ids"]
    report["shortcut_threats"][1]["protected_signal_ids"] = ["unknown_signal"]
    report["shortcut_threats"][2]["protected_signal_ids"] = [
        "matmul_correctness",
        "matmul_correctness",
    ]

    validation = validate_benchmark_hardening_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_shortcut_protected_signals" in codes
    assert "unknown_shortcut_protected_signal" in codes
    assert "duplicate_shortcut_protected_signal_id" in codes


def test_benchmark_hardening_rejects_bad_detector_signal_and_paths():
    report = _valid_report()
    report["protected_signals"][0]["kind"] = "not-a-signal"
    report["shortcut_threats"][0]["detector"]["kind"] = "not-a-detector"
    report["shortcut_threats"][0]["protected_signal_ids"] = [123]
    report["negative_fixtures"][0].update({"path": "../secret.json", "sha256": "bad", "bytes": 0})
    report["artifacts"][0].update({"path": "C:/secret.json", "sha256": "bad", "bytes": 0})

    validation = validate_benchmark_hardening_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_protected_signal_kind" in codes
    assert "invalid_detector_kind" in codes
    assert "invalid_shortcut_protected_signal_id" in codes
    assert "invalid_negative_fixture_path" in codes
    assert "invalid_negative_fixture_hash" in codes
    assert "invalid_negative_fixture_bytes" in codes
    assert "invalid_artifact_path" in codes
    assert "invalid_artifact_hash" in codes
    assert "invalid_artifact_bytes" in codes


def test_benchmark_hardening_summary_renders_coverage_counts():
    summary = render_benchmark_hardening_summary(_valid_report())

    assert "Benchmark hardening report: matrix_multiplication_smoke" in summary
    assert "| schema_status | ok |" in summary
    assert "| benchmark_ready | yes |" in summary
    assert "| protected_signal_count | 2 |" in summary
    assert "| shortcut_threat_count | 3 |" in summary
    assert "| negative_fixture_count | 3 |" in summary


def test_matrix_smoke_hardening_bundle_writes_scope_checked_evidence(tmp_path):
    bundle = write_matrix_smoke_hardening_bundle(tmp_path)
    report = bundle["report"]
    inventory = bundle["inventory"]

    assert bundle["schema"] == BENCHMARK_HARDENING_BUNDLE_SCHEMA
    assert bundle["benchmark_id"] == "matrix_multiplication_smoke"
    assert bundle["level"] == "smoke"
    assert bundle["alphaevolve_comparable"] is False
    assert bundle["scope_validation"]["ok"] is True
    assert bundle["scope_validation"]["scope_level"] == "smoke"
    assert bundle["scope_validation"]["hardening_level"] == "smoke"
    assert validate_benchmark_hardening_report(report).ok is True
    assert inventory["ok"] is True
    assert inventory["record_count"] == 4
    assert {record["status"] for record in inventory["records"]} == {"verified"}

    report_path = tmp_path / bundle["report_path"]
    inventory_path = tmp_path / bundle["inventory_path"]
    summary_path = tmp_path / bundle["summary_path"]
    scope_path = tmp_path / bundle["scope_validation_path"]
    assert report_path.exists()
    assert inventory_path.exists()
    assert summary_path.exists()
    assert scope_path.exists()
    assert hashlib.sha256(report_path.read_bytes()).hexdigest() == bundle["report_sha256"]
    assert hashlib.sha256(inventory_path.read_bytes()).hexdigest() == bundle["inventory_sha256"]
    assert hashlib.sha256(summary_path.read_bytes()).hexdigest() == bundle["summary_sha256"]
    assert "Benchmark hardening report: matrix_multiplication_smoke" in summary_path.read_text(
        encoding="utf-8"
    )


def test_sorting_network_8_hardening_bundle_writes_benchmark_evidence(tmp_path):
    bundle = write_sorting_network_hardening_bundle(tmp_path, "sorting_network_8")
    report = bundle["report"]
    inventory = bundle["inventory"]

    assert bundle["schema"] == BENCHMARK_HARDENING_BUNDLE_SCHEMA
    assert bundle["benchmark_id"] == "sorting_network_8_benchmark"
    assert bundle["problem_id"] == "sorting_network_8"
    assert bundle["level"] == "benchmark"
    assert bundle["wire_count"] == 8
    assert bundle["target_comparators"] == 19
    assert bundle["seed_comparators"] == 28
    assert bundle["alphaevolve_comparable"] is False
    assert bundle["scope_validation"]["ok"] is True
    assert bundle["scope_validation"]["scope_level"] == "benchmark"
    assert bundle["scope_validation"]["hardening_level"] == "benchmark"
    assert validate_benchmark_hardening_report(report).ok is True
    assert validate_benchmark_hardening_report(report).benchmark_ready is True
    assert inventory["ok"] is True
    assert inventory["record_count"] == 4
    assert {record["status"] for record in inventory["records"]} == {"verified"}
    assert {fixture["category"] for fixture in report["negative_fixtures"]} == {
        "hardcoded_cases",
        "library_delegation",
        "invalid_artifact",
    }

    summary_path = tmp_path / bundle["summary_path"]
    assert summary_path.exists()
    assert "Benchmark hardening report: sorting_network_8_benchmark" in summary_path.read_text(
        encoding="utf-8"
    )


def test_sorting_network_9_hardening_bundle_writes_benchmark_evidence(tmp_path):
    bundle = write_sorting_network_hardening_bundle(tmp_path, "sorting_network_9")

    assert bundle["benchmark_id"] == "sorting_network_9_benchmark"
    assert bundle["problem_id"] == "sorting_network_9"
    assert bundle["wire_count"] == 9
    assert bundle["target_comparators"] == 25
    assert bundle["seed_comparators"] == 36
    assert bundle["scope_validation"]["ok"] is True
    assert bundle["inventory"]["ok"] is True
    assert validate_benchmark_hardening_report(bundle["report"]).benchmark_ready is True


def test_sorting_network_hardening_bundle_rejects_unknown_problem(tmp_path):
    try:
        write_sorting_network_hardening_bundle(tmp_path, "sorting_network_10")
    except ValueError as exc:
        assert "sorting_network_8 or sorting_network_9" in str(exc)
    else:
        raise AssertionError("expected ValueError")
