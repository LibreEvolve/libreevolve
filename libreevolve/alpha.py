"""Small onboarding surface for the local alpha workflow."""

from __future__ import annotations

from importlib.resources import files
import json
import math
from pathlib import Path
import shutil

import click
import yaml

from libreevolve.core.config import Config
from libreevolve.core.redaction import redact_sensitive_text


def alpha_config(model: str, token_price: float, budget_usd: float) -> dict:
    """Create explicit limits; prices are supplied by the user, not guessed."""
    if not math.isfinite(token_price) or token_price <= 0:
        raise ValueError("Token price must be finite and greater than zero.")
    if not math.isfinite(budget_usd) or budget_usd < 0.000001:
        raise ValueError("Estimated budget must be finite and at least $0.000001.")
    settings = {
        "max_generations": 10,
        "max_evaluations": 11,
        "max_runtime_seconds": 900,
        "eval_timeout_sec": 10,
        "max_llm_calls": 10,
        "max_llm_provider_attempts": 10,
        "max_llm_tokens": 60000,
        "max_llm_cost_microusd": int(budget_usd * 1_000_000),
        "llm_max_retries": 0,
        "llm_max_call_attempts": 1,
        "llm_fallback": False,
        "llm_call_timeout_sec": 60,
        "mutation_mode": "full",
        "seed": 42,
        "backends": [{
            "type": "openai", "model": model, "api_mode": "responses",
            "max_tokens": 2048, "timeout_sec": 60, "provider_max_retries": 0,
            "cost_usd_per_million_tokens": token_price,
        }],
    }
    Config(**settings).validate()
    return settings


@click.group()
def alpha() -> None:
    """Set up and check a bounded local optimization experiment."""


@alpha.command("init")
@click.argument("destination", type=click.Path(path_type=Path))
@click.option("--model", required=True, help="OpenAI model available to your account.")
@click.option("--token-price", required=True, type=float,
              help="Conservative USD per million tokens; use the higher input/output rate.")
@click.option("--budget-usd", required=True, type=float,
              help="Estimated per-run cost threshold, not a guaranteed billing cap.")
def initialize(destination: Path, model: str, token_price: float, budget_usd: float) -> None:
    """Create a bin-packing task in a new directory. Makes no provider calls."""
    try:
        settings = alpha_config(model, token_price, budget_usd)
        if destination.exists() or destination.is_symlink():
            raise ValueError("Destination already exists. Choose a new directory.")
        source = files("libreevolve.problems.examples").joinpath("bin_packing")
        # Wheels are installed as ordinary directories; copy only task assets.
        shutil.copytree(Path(str(source)), destination,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (destination / "config.yaml").write_text(
            yaml.safe_dump(settings, sort_keys=False), encoding="utf-8"
        )
    except (OSError, ValueError) as exc:
        raise click.ClickException(redact_sensitive_text(str(exc))) from exc
    click.echo(f"Created {destination}")
    click.echo("Set OPENAI_API_KEY, then run:")
    click.echo(f'  libreevolve alpha doctor "{destination}"')
    click.echo(f'  libreevolve run "{destination}" --run-name first-experiment --progress')
    click.echo("Estimated cost limits use configured prices and reported usage; "
               "an in-flight call may exceed a threshold. Provider billing can differ.")


@alpha.command("doctor")
@click.argument("problem_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--offline", is_flag=True, help="Skip credential/client checks; make no provider calls.")
def doctor(problem_dir: Path, offline: bool) -> None:
    """Check task/configuration and local provider setup without generating candidates."""
    # Lazy import avoids coupling module registration to the CLI's helpers.
    from libreevolve.cli import (
        _build_config, _load_cli_dotenv, _preflight_llm_backends_if_needed,
        _preflight_run_contracts,
    )
    from libreevolve.problems.loader import load_problem

    try:
        problem = load_problem(problem_dir)
        config = _build_config(problem, None, None, None, None, None, [], [], None)
        config.validate()
        if len(config.backends) != 1 or config.backends[0]["type"] != "openai":
            raise ValueError("The alpha onboarding path supports one OpenAI backend.")
        limits = ("max_evaluations", "max_runtime_seconds", "max_llm_calls",
                  "max_llm_provider_attempts", "max_llm_tokens", "max_llm_cost_microusd")
        if any(getattr(config, name) is None for name in limits):
            raise ValueError("Alpha runs require explicit evaluation, runtime, call, token and cost limits.")
        if not config.backends[0].get("cost_usd_per_million_tokens"):
            raise ValueError("Set cost_usd_per_million_tokens using current provider pricing.")
        _preflight_run_contracts(problem, config)
        if not offline:
            _load_cli_dotenv()
            _preflight_llm_backends_if_needed(problem, config)
    except (OSError, ValueError) as exc:
        raise click.ClickException(redact_sensitive_text(str(exc))) from exc
    click.echo("Task and evaluator contract: passed (local subprocess).")
    click.echo(f"Provider: openai; model: {config.backends[0]['model']}")
    for name in limits:
        click.echo(f"{name}: {getattr(config, name)}")
    click.echo("Credential checks: skipped" if offline else "Local provider setup: passed")
    click.echo("Model access and billing remain unverified until a real request succeeds.")
    click.echo("Candidate execution inherits host access. Use a trusted local task.")


def register_alpha(cli: click.Group) -> None:
    cli.add_command(alpha)


@alpha.command("report")
@click.argument("run_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path),
              help="New HTML file for the report; existing files are never overwritten.")
def report_command(run_dir: Path, output: Path) -> None:
    """Reevaluate the exported bin-packing candidate and write a local report.

    Executes candidate Python in timed local subprocesses with host access.
    """
    from libreevolve.alpha_report import build_report, render_html

    if output.suffix.lower() != ".html":
        raise click.ClickException("Choose a new .html output file.")
    if output.exists() or output.is_symlink():
        raise click.ClickException("Report output already exists. Choose a new path.")
    try:
        report = build_report(run_dir)
        content = render_html(report)
        with output.open("x", encoding="utf-8") as stream:
            stream.write(content)
    except (OSError, ValueError) as exc:
        raise click.ClickException(redact_sensitive_text(str(exc))) from exc
    click.echo(f"Report saved to {output}")
    click.echo("Review independent correctness, run status and usage before using the candidate.")


@alpha.command("export")
@click.argument("run_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("destination", type=click.Path(path_type=Path))
def export_command(run_dir: Path, destination: Path) -> None:
    """Verify and export a single-file bin-packing candidate from saved history.

    Also supports inspectable cancelled runs. Executes candidate code locally.
    """
    from libreevolve.alpha_report import verify_candidate
    from libreevolve.core.run_inspection import inspect_run

    if destination.exists() or destination.is_symlink():
        raise click.ClickException("Export destination exists. Choose a new directory.")
    try:
        inspection = inspect_run(run_dir)
        if inspection.workspace is None:
            raise ValueError("Run has no recoverable candidate workspace.")
        primary, workspace = inspection.workspace
        if set(workspace) != {primary} or not primary.endswith(".py"):
            raise ValueError("Alpha export supports the single-file Python bin-packing task.")
        verification = verify_candidate(workspace[primary])
        if any(verification[split].get("status") != "completed"
               or verification[split].get("correctness") is not True
               for split in ("training", "holdout")):
            raise ValueError("Independent training/held-out verification did not pass; no export created.")
        destination.mkdir(parents=False)
        # Fixed export filename avoids applying historical path names to disk.
        (destination / "solution.py").write_text(workspace[primary], encoding="utf-8", newline="")
        verification.update(source_program_id=inspection.best.get("id"),
                            source_runtime_status=inspection.runtime_status,
                            exported_filename="solution.py")
        (destination / "verification.json").write_text(
            json.dumps(verification, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError) as exc:
        raise click.ClickException(redact_sensitive_text(str(exc))) from exc
    click.echo(f"Verified export: {destination / 'solution.py'}")
    click.echo(f"Code SHA-256: {verification['code_sha256']}")
    click.echo(f"Source run: {inspection.runtime_status}")
