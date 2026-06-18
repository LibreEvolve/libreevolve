import json

from libreevolve.tools.sorting_network_source_refresh_gate import (
    compare_source_snapshots,
    main,
    run_refresh_gate,
    source_expectations,
)


def test_sorting_network_source_refresh_gate_accepts_expected_snapshots():
    report = run_refresh_gate()

    assert report["ok"] is True
    assert report["source_count"] == 5
    assert {check["source_id"] for check in report["checks"]} == {
        "zero_one_clrs",
        "schneider_kamp_bounds",
        "dobbelaere_list",
        "codish_arxiv",
        "codish_publication",
    }


def test_sorting_network_source_refresh_gate_detects_digest_drift():
    snapshots = {
        expectation["source_id"]: {
            "status": expectation["expected_status"],
            "content_type": expectation["expected_content_type"],
            "bytes": expectation["expected_bytes"],
            "sha256": expectation["expected_sha256"],
        }
        for expectation in source_expectations()
    }
    snapshots["codish_arxiv"]["sha256"] = "0" * 64

    report = compare_source_snapshots(snapshots)

    assert report["ok"] is False
    codish = next(check for check in report["checks"] if check["source_id"] == "codish_arxiv")
    assert codish["issues"] == ["sha256_drift"]


def test_sorting_network_source_refresh_gate_reports_missing_snapshot():
    snapshots = {
        expectation["source_id"]: {
            "status": expectation["expected_status"],
            "content_type": expectation["expected_content_type"],
            "bytes": expectation["expected_bytes"],
            "sha256": expectation["expected_sha256"],
        }
        for expectation in source_expectations()
    }
    snapshots.pop("zero_one_clrs")

    report = compare_source_snapshots(snapshots)

    zero_one = next(check for check in report["checks"] if check["source_id"] == "zero_one_clrs")
    assert report["ok"] is False
    assert zero_one["issues"] == ["missing_live_snapshot"]


def test_sorting_network_source_refresh_gate_cli_outputs_json(capsys):
    exit_code = main([])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["schema"] == "libreevolve.sorting_network_source_refresh_gate_report.v1"
    assert payload["ok"] is True
