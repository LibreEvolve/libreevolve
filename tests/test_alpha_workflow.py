"""Exercise the actual engine, report and verified export without a provider."""

import hashlib
import json

from click.testing import CliRunner
import yaml

import libreevolve.cli as cli_module
from libreevolve.cli import cli


def test_seed_run_report_and_verified_export(tmp_path, monkeypatch):
    monkeypatch.setattr(cli_module, "_load_cli_dotenv", lambda: {})
    runner = CliRunner()
    task = tmp_path / "packing"
    init = runner.invoke(cli, ["alpha", "init", str(task), "--model", "offline-placeholder",
                              "--token-price", "10", "--budget-usd", "1"])
    assert init.exit_code == 0, init.output
    config_path = task / "config.yaml"
    config = yaml.safe_load(config_path.read_text())
    config["log_dir"] = str(tmp_path / "runs")
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    run = runner.invoke(cli, ["run", str(task), "--max-generations", "0", "--progress"])
    assert run.exit_code == 0, run.output
    run_dir = tmp_path / "runs" / "packing"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["runtime"]["consumed"]["llm_provider_attempts"] == 0
    output = tmp_path / "report.html"
    report = runner.invoke(cli, ["alpha", "report", str(run_dir), "--output", str(output)])
    assert report.exit_code == 0, report.output
    assert "<!doctype html>" in output.read_text().lower()
    export_path = tmp_path / "verified"
    export = runner.invoke(cli, ["alpha", "export", str(run_dir), str(export_path)])
    assert export.exit_code == 0, export.output
    evidence = json.loads((export_path / "verification.json").read_text())
    assert evidence["training"]["correctness"] is True
    assert evidence["holdout"]["correctness"] is True
    assert hashlib.sha256((export_path / "solution.py").read_bytes()).hexdigest() == evidence["code_sha256"]
    again = runner.invoke(cli, ["alpha", "export", str(run_dir), str(export_path)])
    assert again.exit_code != 0
    assert "exists" in again.output
