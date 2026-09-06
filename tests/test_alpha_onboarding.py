"""Contracts for bounded onboarding without provider requests."""

import pytest
from click.testing import CliRunner

from libreevolve.alpha import alpha_config
from libreevolve.cli import cli


@pytest.mark.parametrize("price,budget", [(0, 1), (-1, 1), (float("nan"), 1),
                                         (1, float("inf")), (1, 0), (1, 1e308)])
def test_invalid_price_and_budget_do_not_create_task(tmp_path, price, budget):
    with pytest.raises(ValueError):
        alpha_config("account-model", price, budget)
    assert list(tmp_path.iterdir()) == []


def test_oversized_budget_is_actionable_cli_error(tmp_path):
    destination = tmp_path / "experiment"
    result = CliRunner().invoke(cli, [
        "alpha", "init", str(destination), "--model", "account-model",
        "--token-price", "10", "--budget-usd", "1e308",
    ])
    assert result.exit_code == 1
    assert "too large" in result.output
    assert not destination.exists()


def test_initialized_task_has_bounded_config_and_no_credentials(tmp_path):
    import yaml
    destination = tmp_path / "experiment"
    runner = CliRunner()
    result = runner.invoke(cli, ["alpha", "init", str(destination), "--model", "account-model",
                                 "--token-price", "10", "--budget-usd", "1"])
    assert result.exit_code == 0, result.output
    config = yaml.safe_load((destination / "config.yaml").read_text())
    assert config["max_llm_cost_microusd"] == 1_000_000
    assert config["max_llm_provider_attempts"] == 10
    assert "api_key" not in (destination / "config.yaml").read_text()
    assert (destination / "validate.py").is_file()
    assert not (destination / "initial_programs" / "validate.py").exists()
    again = runner.invoke(cli, ["alpha", "init", str(destination), "--model", "account-model",
                                "--token-price", "10", "--budget-usd", "1"])
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
    result = runner.invoke(cli, ["alpha", "init", str(destination), "--model", "account-model",
                                 "--token-price", "10", "--budget-usd", "1"])
    assert result.exit_code == 0, result.output
    path = destination / "config.yaml"
    config = yaml.safe_load(path.read_text())
    del config["max_llm_tokens"]
    path.write_text(yaml.safe_dump(config))
    result = runner.invoke(cli, ["alpha", "doctor", str(destination), "--offline"])
    assert result.exit_code != 0
    assert "explicit" in result.output


def test_cli_cancellation_points_to_partial_results(tmp_path, monkeypatch):
    import libreevolve.cli as cli_module
    runner = CliRunner()
    destination = tmp_path / "experiment"
    result = runner.invoke(cli, ["alpha", "init", str(destination), "--model", "account-model",
                                 "--token-price", "10", "--budget-usd", "1"])
    assert result.exit_code == 0, result.output
    monkeypatch.setattr(cli_module, "_load_cli_dotenv", lambda: {})
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
                                   "max_llm_provider_attempts", "max_llm_tokens",
                                   "max_llm_cost_microusd"])
def test_doctor_does_not_claim_skipped_provider_setup_passed(tmp_path, monkeypatch, limit):
    import yaml
    import libreevolve.cli as cli_module
    runner = CliRunner()
    destination = tmp_path / "experiment"
    result = runner.invoke(cli, ["alpha", "init", str(destination), "--model", "account-model",
                                 "--token-price", "10", "--budget-usd", "1"])
    assert result.exit_code == 0, result.output
    path = destination / "config.yaml"
    config = yaml.safe_load(path.read_text())
    config[limit] = 0
    path.write_text(yaml.safe_dump(config))
    def unexpected():
        raise AssertionError("Disabled mutation must not inspect credential files")
    monkeypatch.setattr(cli_module, "_load_cli_dotenv", unexpected)
    result = runner.invoke(cli, ["alpha", "doctor", str(destination)])
    assert result.exit_code == 0, result.output
    assert "skipped (mutation disabled" in result.output
    assert "Local provider setup: passed" not in result.output
