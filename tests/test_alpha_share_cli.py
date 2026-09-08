import json

from click.testing import CliRunner

from libreevolve.cli import cli
from libreevolve.alpha_share_record import payload_sha256
from tests.test_alpha_share_record import record


def test_inspect_and_render_cli(tmp_path):
    source = tmp_path / "input.json"
    source.write_text(json.dumps(record()), encoding="utf-8")
    runner = CliRunner()
    inspected = runner.invoke(cli, ["alpha", "share", "inspect", str(source)])
    assert inspected.exit_code == 0, inspected.output
    assert payload_sha256(record()) in inspected.output
    assert not (tmp_path / "public").exists()
    args = ["alpha", "share", "render", str(source), str(tmp_path / "public"),
            "--approve-sha256", payload_sha256(record()), "--approved-by", "private-operator",
            "--receipt", str(tmp_path / "private-receipt.json")]
    rendered = runner.invoke(cli, args)
    assert rendered.exit_code == 0, rendered.output
    assert "Nothing uploaded" in rendered.output
    receipt = json.loads((tmp_path / "private-receipt.json").read_text())
    assert receipt["approved_by"] == "private-operator"
    for output in (tmp_path / "public").iterdir():
        assert "private-operator" not in output.read_text()
    assert runner.invoke(cli, args).exit_code != 0


def test_missing_approval_or_inside_receipt_creates_nothing(tmp_path):
    source = tmp_path / "input.json"
    source.write_text(json.dumps(record()), encoding="utf-8")
    runner = CliRunner()
    prefix = ["alpha", "share", "render", str(source), str(tmp_path / "public")]
    assert runner.invoke(cli, prefix).exit_code != 0
    result = runner.invoke(cli, prefix + ["--approve-sha256", payload_sha256(record()),
                           "--approved-by", "operator", "--receipt", str(tmp_path / "public" / "receipt.json")])
    assert result.exit_code != 0
    assert not (tmp_path / "public").exists()


def test_help_exposes_no_upload_or_candidate_execution():
    result = CliRunner().invoke(cli, ["alpha", "share", "render", "--help"])
    assert result.exit_code == 0
    assert "--approve-sha256" in result.output
    assert "--approve-source-link" in result.output
    assert "No candidate code runs" in result.output


def test_prepare_requires_execution_ack_and_new_paths(tmp_path, monkeypatch):
    from libreevolve import alpha_share_prepare
    calls = []
    def prepare(*args, **kwargs):
        calls.append(kwargs)
        return record(), {"source_kind": "history", "private_note": "test-only"}
    monkeypatch.setattr(alpha_share_prepare, "prepare_run", prepare)
    runner = CliRunner()
    args = ["alpha", "share", "prepare", str(tmp_path), "--public-id", "synthetic",
            "--output", str(tmp_path / "proposal.json"), "--evidence", str(tmp_path / "private.json")]
    assert runner.invoke(cli, args).exit_code != 0
    assert calls == []
    result = runner.invoke(cli, args + ["--allow-local-execution"])
    assert result.exit_code == 0, result.output
    assert "Unapproved" in result.output
    assert "private_note" not in (tmp_path / "proposal.json").read_text()
    assert len(calls) == 1
    assert runner.invoke(cli, args + ["--allow-local-execution"]).exit_code != 0
    assert len(calls) == 1


def test_prepare_rejects_identical_output_paths_before_execution(tmp_path, monkeypatch):
    from libreevolve import alpha_share_prepare
    def forbidden(*args, **kwargs):
        raise AssertionError("invalid output must fail before candidate execution")
    monkeypatch.setattr(alpha_share_prepare, "prepare_run", forbidden)
    output = str(tmp_path / "same.json")
    result = CliRunner().invoke(cli, ["alpha", "share", "prepare", str(tmp_path),
        "--public-id", "synthetic", "--output", output, "--evidence", output, "--allow-local-execution"])
    assert result.exit_code != 0
    assert "distinct new" in result.output
