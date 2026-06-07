import json

from libreevolve.problems.benchmarks.benchmark_hardening import (
    BENCHMARK_HARDENING_SCHEMA,
    render_benchmark_hardening_summary,
    validate_benchmark_hardening_report,
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
