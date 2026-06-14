import json

from libreevolve.tools.alphaevolve_source_refresh_gate import (
    compare_source_snapshots,
    main,
    run_refresh_gate,
    source_expectations,
)


def test_source_refresh_gate_accepts_expected_snapshots():
    report = run_refresh_gate()

    assert report["ok"] is True
    assert report["source_count"] == 6
    assert {check["source_id"] for check in report["checks"]} == {
        "versioned_abstract",
        "current_abstract",
        "floating_pdf",
        "datacite_api",
        "eprint_archive",
        "license_page",
    }


def test_source_refresh_gate_detects_digest_drift():
    snapshots = {
        expectation["source_id"]: {
            "status": expectation["expected_status"],
            "content_type": expectation["expected_content_type"],
            "bytes": expectation["expected_bytes"],
            "sha256": expectation["expected_sha256"],
        }
        for expectation in source_expectations()
    }
    snapshots["datacite_api"]["sha256"] = "0" * 64

    report = compare_source_snapshots(snapshots)

    assert report["ok"] is False
    datacite = next(check for check in report["checks"] if check["source_id"] == "datacite_api")
    assert datacite["issues"] == ["sha256_drift"]


def test_source_refresh_gate_reports_missing_snapshot():
    snapshots = {
        expectation["source_id"]: {
            "status": expectation["expected_status"],
            "content_type": expectation["expected_content_type"],
            "bytes": expectation["expected_bytes"],
            "sha256": expectation["expected_sha256"],
        }
        for expectation in source_expectations()
    }
    snapshots.pop("license_page")

    report = compare_source_snapshots(snapshots)

    assert report["ok"] is False
    license_check = next(check for check in report["checks"] if check["source_id"] == "license_page")
    assert license_check["issues"] == ["missing_live_snapshot"]


def test_source_refresh_gate_cli_outputs_json(capsys):
    exit_code = main([])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["schema"] == "libreevolve.alphaevolve_source_refresh_gate_report.v1"
    assert payload["ok"] is True
