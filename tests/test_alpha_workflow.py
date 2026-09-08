"""Exercise the actual engine, report and verified export without a provider."""

import hashlib
import json

from click.testing import CliRunner
import yaml

import libreevolve.cli as cli_module
from libreevolve.cli import cli


def test_seed_run_report_and_verified_export(tmp_path, monkeypatch):
    runner = CliRunner()
    task = tmp_path / "packing"
    init = runner.invoke(cli, ["alpha", "init", str(task), "--model", "gpt-5.6-luna"])
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
    # A reviewed, manually modified workspace must not silently export history.
    candidate = run_dir / "best_workspace" / "seed.py"
    original_code = candidate.read_bytes()
    modified_code = original_code + b"\n# reviewed local variant\n"
    candidate.write_bytes(modified_code)
    conflict = runner.invoke(cli, ["alpha", "export", str(run_dir), str(tmp_path / "conflict")])
    assert conflict.exit_code != 0
    assert "differs from saved history" in conflict.output
    assert not (tmp_path / "conflict").exists()
    chosen = tmp_path / "chosen"
    result = runner.invoke(cli, ["alpha", "export", str(run_dir), str(chosen), "--source", "workspace"])
    assert result.exit_code == 0, result.output
    assert (chosen / "solution.py").read_bytes() == modified_code
    chosen_evidence = json.loads((chosen / "verification.json").read_text())
    assert chosen_evidence["matches_history"] is False
    assert chosen_evidence["source_program_id"] is None
    assert chosen_evidence["code_sha256"] == hashlib.sha256(modified_code).hexdigest()
    historical = tmp_path / "historical"
    result = runner.invoke(cli, ["alpha", "export", str(run_dir), str(historical),
                                 "--source", "history"])
    assert result.exit_code == 0, result.output
    assert (historical / "solution.py").read_bytes().replace(b"\r\n", b"\n") == original_code.replace(b"\r\n", b"\n")
    history_evidence = json.loads((historical / "verification.json").read_text())
    assert history_evidence["matches_history"] is True
    assert history_evidence["source_program_id"] is not None
    # Windows line-ending changes alone are equivalent, but raw export hashes
    # must still describe the actual reviewed workspace bytes.
    crlf_code = original_code.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    candidate.write_bytes(crlf_code)
    equivalent = tmp_path / "equivalent"
    result = runner.invoke(cli, ["alpha", "export", str(run_dir), str(equivalent)])
    assert result.exit_code == 0, result.output
    assert (equivalent / "solution.py").read_bytes() == crlf_code
    equivalent_evidence = json.loads((equivalent / "verification.json").read_text())
    assert equivalent_evidence["matches_history"] is True
    assert equivalent_evidence["code_sha256"] == hashlib.sha256(crlf_code).hexdigest()
