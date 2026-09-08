"""Contracts for bounded onboarding without provider requests."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from libreevolve.alpha import alpha_config
from libreevolve.cli import cli


@pytest.mark.parametrize("model", ["account-model", "", "gpt-6-astra"])
def test_unvalidated_model_does_not_create_task(tmp_path, model):
    with pytest.raises(ValueError, match="validated"):
        alpha_config(model)
    destination = tmp_path / "experiment"
    result = CliRunner().invoke(cli, [
        "alpha", "init", str(destination), "--model", model,
    ])
    assert result.exit_code != 0
    assert not destination.exists()


def test_codex_config_uses_bounded_subscription_semantics():
    settings = alpha_config("gpt-5.6-luna")
    backend = settings["backends"][0]
    assert settings["max_generations"] == 3
    assert settings["max_evaluations"] == 4
    assert settings["max_runtime_seconds"] == 900
    assert settings["max_llm_calls"] == 3
    assert settings["max_llm_provider_attempts"] == 3
    assert settings["llm_call_timeout_sec"] is None
    assert "max_llm_tokens" not in settings
    assert "max_llm_cost_microusd" not in settings
    assert backend == {
        "type": "codex",
        "model": "gpt-5.6-luna",
        "cwd": ".codex-alpha-workspace",
        "sandbox": "read-only",
        "timeout_sec": 180,
        "reasoning_effort": "high",
        "auth_name": "current",
        "ignore_user_config": True,
        "ignore_rules": True,
        "ephemeral": True,
        "output_json_field": "program",
        "disable_features": ["shell_tool"],
        "approval_policy": "never",
    }


def test_codex_init_creates_empty_isolated_cwd_without_cost_claims(tmp_path):
    import yaml

    destination = tmp_path / "codex-experiment"
    result = CliRunner().invoke(
        cli,
        [
            "alpha",
            "init",
            str(destination),
            "--model",
            "gpt-5.6-luna",
        ],
    )
    assert result.exit_code == 0, result.output
    config = yaml.safe_load((destination / "config.yaml").read_text())
    backend = config["backends"][0]
    assert config["llm_call_timeout_sec"] is None
    assert backend["timeout_sec"] == 180
    assert backend["type"] == "codex"
    assert backend["model"] == "gpt-5.6-luna"
    assert backend["reasoning_effort"] == "high"
    assert backend["sandbox"] == "read-only"
    assert backend["auth_name"] == "current"
    assert backend["ignore_user_config"] is True
    assert backend["ignore_rules"] is True
    assert backend["ephemeral"] is True
    assert Path(backend["cwd"]).resolve() == (destination / ".codex-alpha-workspace").resolve()
    isolated = destination / ".codex-alpha-workspace"
    assert isolated.is_dir()
    assert list(isolated.iterdir()) == []
    assert "max_llm_tokens" not in config
    assert "max_llm_cost_microusd" not in config
    assert "per-token price" in result.output
    assert "dollar cap" in result.output


@pytest.mark.parametrize("flag", ["--token-price", "--budget-usd"])
def test_codex_rejects_dollar_cap_options(tmp_path, flag):
    destination = tmp_path / flag.lstrip("-")
    result = CliRunner().invoke(
        cli,
        [
            "alpha",
            "init",
            str(destination),
            "--model",
            "gpt-5.6-luna",
            flag,
            "1",
        ],
    )
    assert result.exit_code == 2, result.output
    assert "No such option" in result.output
    assert not destination.exists()


def test_codex_doctor_checks_resolved_oauth_home_without_provider_request(tmp_path, monkeypatch):
    import subprocess
    import types
    import yaml

    import libreevolve.alpha as alpha_module
    import libreevolve.cli as cli_module
    import libreevolve.llm.codex_cli as codex_module

    destination = tmp_path / "codex-doctor"
    created = CliRunner().invoke(
        cli,
        [
            "alpha",
            "init",
            str(destination),
            "--model",
            "gpt-5.6-luna",
        ],
    )
    assert created.exit_code == 0, created.output
    config_path = destination / "config.yaml"
    config = yaml.safe_load(config_path.read_text())
    auth_home = tmp_path / "oauth-current"
    config["backends"][0]["auth_homes"] = {"current": str(auth_home)}
    config_path.write_text(yaml.safe_dump(config))

    seen = {}

    class _StatusResult:
        returncode = 0
        stdout = "Logged in using ChatGPT\n"
        stderr = ""

    def fake_run(command, **kwargs):
        seen["command"] = command
        seen.update(kwargs)
        return _StatusResult()

    fake_subprocess = types.SimpleNamespace(
        run=fake_run,
        TimeoutExpired=subprocess.TimeoutExpired,
    )
    monkeypatch.setattr(alpha_module, "subprocess", fake_subprocess)
    monkeypatch.setattr(codex_module, "_resolve_codex_command", lambda: "codex")
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-reach-codex-status")

    def unexpected_dotenv():
        raise AssertionError("Codex doctor must not load OpenAI .env credentials")

    result = CliRunner().invoke(cli, ["alpha", "doctor", str(destination)])
    assert result.exit_code == 0, result.output
    assert seen["command"] == ["codex", "login", "status"]
    assert seen["timeout"] == 5.0
    assert seen["env"]["CODEX_HOME"] == str(auth_home.resolve())
    assert "OPENAI_API_KEY" not in seen["env"]
    assert "exec" not in seen["command"]
    assert "Codex executable/login status: passed" in result.output
    assert "no provider request" in result.output
    assert "subscription-backed" in result.output


def test_codex_doctor_rejects_api_key_status_without_printing_status_output(tmp_path, monkeypatch):
    import subprocess
    import types

    import libreevolve.alpha as alpha_module
    import libreevolve.llm.codex_cli as codex_module

    destination = tmp_path / "codex-api-key"
    created = CliRunner().invoke(
        cli,
        [
            "alpha",
            "init",
            str(destination),
            "--model",
            "gpt-5.6-luna",
        ],
    )
    assert created.exit_code == 0, created.output

    class _StatusResult:
        returncode = 0
        stdout = "Logged in using an API key: sk-test-secret\n"
        stderr = ""

    fake_subprocess = types.SimpleNamespace(
        run=lambda *args, **kwargs: _StatusResult(),
        TimeoutExpired=subprocess.TimeoutExpired,
    )
    monkeypatch.setattr(alpha_module, "subprocess", fake_subprocess)
    monkeypatch.setattr(codex_module, "_resolve_codex_command", lambda: "codex")
    result = CliRunner().invoke(cli, ["alpha", "doctor", str(destination)])
    assert result.exit_code == 1
    assert "ChatGPT OAuth" in result.output
    assert "sk-test-secret" not in result.output


def test_initialized_task_has_bounded_config_and_no_credentials(tmp_path):
    import yaml
    destination = tmp_path / "experiment"
    runner = CliRunner()
    result = runner.invoke(cli, ["alpha", "init", str(destination), "--model", "gpt-5.6-luna"])
    assert result.exit_code == 0, result.output
    config = yaml.safe_load((destination / "config.yaml").read_text())
    assert "max_llm_cost_microusd" not in config
    assert config["max_llm_provider_attempts"] == 3
    assert "api_key" not in (destination / "config.yaml").read_text()
    assert (destination / "validate.py").is_file()
    assert not (destination / "initial_programs" / "validate.py").exists()
    again = runner.invoke(cli, ["alpha", "init", str(destination), "--model", "gpt-5.6-luna"])
    assert again.exit_code != 0
    assert "already exists" in again.output
    check = runner.invoke(cli, ["alpha", "doctor", str(destination), "--offline"])
    assert check.exit_code == 0, check.output
    assert "Credential checks: skipped" in check.output
    assert "unverified" in check.output


def test_doctor_rejects_unbounded_config(tmp_path):
    import yaml
    runner = CliRunner()
    destination = tmp_path / "experiment"
    result = runner.invoke(cli, ["alpha", "init", str(destination), "--model", "gpt-5.6-luna"])
    assert result.exit_code == 0, result.output
    path = destination / "config.yaml"
    config = yaml.safe_load(path.read_text())
    config["max_llm_calls"] = None
    path.write_text(yaml.safe_dump(config))
    result = runner.invoke(cli, ["alpha", "doctor", str(destination), "--offline"])
    assert result.exit_code != 0
    assert "explicit" in result.output


def test_cli_cancellation_points_to_partial_results(tmp_path, monkeypatch):
    import libreevolve.cli as cli_module
    runner = CliRunner()
    destination = tmp_path / "experiment"
    result = runner.invoke(cli, ["alpha", "init", str(destination), "--model", "gpt-5.6-luna"])
    assert result.exit_code == 0, result.output
    monkeypatch.setattr(cli_module, "_preflight_llm_backends_if_needed", lambda *a: None)
    monkeypatch.setattr(cli_module, "_prepare_run_dir_for_cli", lambda *a: None)
    def cancel(*args, **kwargs):
        raise KeyboardInterrupt
    monkeypatch.setattr(cli_module, "evolve", cancel)
    result = runner.invoke(cli, ["run", str(destination)])
    assert result.exit_code == 130
    assert "Cancelled" in result.output
    assert "may be incomplete" in result.output


@pytest.mark.parametrize("limit", ["max_generations", "max_llm_calls",
                                   "max_llm_provider_attempts"])
def test_doctor_does_not_claim_skipped_provider_setup_passed(tmp_path, monkeypatch, limit):
    import yaml
    import libreevolve.cli as cli_module
    runner = CliRunner()
    destination = tmp_path / "experiment"
    result = runner.invoke(cli, ["alpha", "init", str(destination), "--model", "gpt-5.6-luna"])
    assert result.exit_code == 0, result.output
    path = destination / "config.yaml"
    config = yaml.safe_load(path.read_text())
    config[limit] = 0
    path.write_text(yaml.safe_dump(config))
    def unexpected():
        raise AssertionError("Disabled mutation must not inspect credential files")
    result = runner.invoke(cli, ["alpha", "doctor", str(destination)])
    assert result.exit_code == 0, result.output
    assert "skipped (mutation disabled" in result.output
    assert "Local provider setup: passed" not in result.output
