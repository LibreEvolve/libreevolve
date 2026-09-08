"""Small onboarding surface for the local alpha workflow."""

from __future__ import annotations

from importlib.resources import files
import json
import os
from pathlib import Path
import shutil
import subprocess

import click
import yaml

from libreevolve.core.config import Config
from libreevolve.core.redaction import redact_sensitive_text


_CODEX_CWD_NAME = ".codex-alpha-workspace"
_CODEX_LOGIN_STATUS_TIMEOUT_SECONDS = 5.0


def alpha_config(
    model: str,
    *,
    codex_cwd: str | None = None,
) -> dict:
    """Create a bounded engineering-preview config for subscription-backed Codex.

    Codex OAuth has no provider price or dollar-quota signal, so this config
    deliberately leaves token and cost budgets unset and bounds only local
    work (calls, evaluations, and wall-clock time).
    """
    if model != "gpt-5.6-luna":
        raise ValueError("The engineering preview supports the validated gpt-5.6-luna/high lane.")

    settings = {
        "max_generations": 3,
        "max_evaluations": 4,
        "max_runtime_seconds": 900,
        "eval_timeout_sec": 10,
        "max_llm_calls": 3,
        "max_llm_provider_attempts": 3,
        "llm_max_retries": 0,
        "llm_max_call_attempts": 1,
        "llm_fallback": False,
        # Codex owns the subprocess timeout; the run deadline can also cancel
        # the CLI process tree through the ensemble worker.
        "llm_call_timeout_sec": None,
        "mutation_mode": "full",
        "seed": 42,
    }

    settings.update(
        backends=[{
                "type": "codex", "model": model,
                "cwd": codex_cwd or _CODEX_CWD_NAME,
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
        }],
    )
    Config(**settings).validate()
    return settings


@click.group()
def alpha() -> None:
    """Set up and check a bounded local optimization experiment."""


@alpha.command("init")
@click.argument("destination", type=click.Path(path_type=Path))
@click.option("--model", type=click.Choice(["gpt-5.6-luna"]), default="gpt-5.6-luna",
              show_default=True, help="Validated engineering-preview model; reasoning is high.")
def initialize(
    destination: Path,
    model: str,
) -> None:
    """Create a bin-packing task in a new directory. Makes no provider calls."""
    try:
        if destination.exists() or destination.is_symlink():
            raise ValueError("Destination already exists. Choose a new directory.")
        codex_cwd = (
            str((destination / _CODEX_CWD_NAME).resolve())
        )
        settings = alpha_config(
            model,
            codex_cwd=codex_cwd,
        )
        source = files("libreevolve.problems.examples").joinpath("bin_packing")
        # Wheels are installed as ordinary directories; copy only task assets.
        shutil.copytree(Path(str(source)), destination,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        # Keep the Codex process rooted outside the evaluator/holdout directory.
        (destination / _CODEX_CWD_NAME).mkdir()
        (destination / "config.yaml").write_text(
            yaml.safe_dump(settings, sort_keys=False), encoding="utf-8"
        )
    except (OSError, ValueError) as exc:
        raise click.ClickException(redact_sensitive_text(str(exc))) from exc
    click.echo(f"Created {destination}")
    click.echo("Use an existing Codex ChatGPT/OAuth login, then run:")
    click.echo(f'  libreevolve alpha doctor "{destination}"')
    click.echo(f'  libreevolve run "{destination}" --run-name first-experiment --progress')
    click.echo(
        "Codex uses subscription usage: token usage may be reported, but no "
        "per-token price, dollar cap, or hard token bound is configured. "
        "Call and runtime limits are local bounds; quota and charges remain unknown."
    )


@alpha.command("doctor")
@click.argument("problem_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--offline", is_flag=True, help="Skip credential/client checks; make no provider calls.")
def doctor(problem_dir: Path, offline: bool) -> None:
    """Check task/configuration and local provider setup without generating candidates."""
    # Lazy import avoids coupling module registration to the CLI's helpers.
    from libreevolve.cli import (
        _build_config,
        _preflight_run_contracts, _mutation_llm_can_run,
    )
    from libreevolve.problems.loader import load_problem

    try:
        problem = load_problem(problem_dir)
        config = _build_config(problem)
        config.validate()
        if (
            len(config.backends) != 1
            or config.backends[0].get("type") != "codex"
            or config.backends[0].get("model") != "gpt-5.6-luna"
            or config.backends[0].get("reasoning_effort") != "high"
        ):
            raise ValueError("The engineering preview supports one Codex gpt-5.6-luna/high backend.")
        provider = config.backends[0]["type"]
        limits = (
            "max_evaluations",
            "max_runtime_seconds",
            "max_llm_calls",
            "max_llm_provider_attempts",
        )
        if any(getattr(config, name) is None for name in limits):
            raise ValueError("Alpha runs require explicit evaluation, runtime, call and provider-attempt limits.")
        if (
            config.max_llm_tokens is not None
            or config.max_llm_cost_microusd is not None
            or config.llm_role_token_limits
            or config.llm_role_cost_microusd_limits
            or config.backends[0].get("cost_usd_per_million_tokens") is not None
        ):
            raise ValueError(
                "Codex alpha runs do not support token or dollar caps; "
                "subscription usage and cost are not observable."
            )
        _preflight_run_contracts(problem, config)
        mutation_enabled = _mutation_llm_can_run(problem, config)
        if not offline and mutation_enabled:
            ok, status = _codex_login_status(config.backends[0])
            if not ok:
                raise ValueError(f"Codex local setup check failed: {status}")
    except (OSError, ValueError) as exc:
        raise click.ClickException(redact_sensitive_text(str(exc))) from exc
    click.echo("Task and evaluator contract: passed (local subprocess).")
    click.echo(f"Provider: {provider}; model: {config.backends[0]['model']}")
    for name in limits:
        click.echo(f"{name}: {getattr(config, name)}")
    if offline:
        click.echo("Credential checks: skipped (offline)")
    elif not mutation_enabled:
        click.echo("Local provider setup: skipped (mutation disabled by configured limits)")
    else:
        click.echo("Codex executable/login status: passed (local bounded check; no provider request)")
    click.echo(
        "Codex usage: subscription-backed; reported tokens are observational only, "
        "with no hard token bound or per-token price."
    )
    click.echo("Codex cost/quota: unknown; this configuration makes no dollar-cap claim.")
    click.echo("Model access and billing remain unverified until a real request succeeds.")
    click.echo("Candidate execution inherits host access. Use a trusted local task.")


def _codex_login_status(backend: dict | None = None) -> tuple[bool, str]:
    """Check local Codex OAuth status without invoking a model request.

    The status command owns any credential inspection. This helper only sees
    its exit status and bounded, generic diagnostics; it never opens auth
    files or prints command output. The selected auth home is resolved from
    the same backend fields used by the actual Codex adapter, and the child
    cannot fall back to an inherited OpenAI API key.
    """
    backend = backend or {"auth_name": "current"}
    try:
        from libreevolve.llm.codex_cli import _resolve_codex_command

        command = _resolve_codex_command()
    except (OSError, RuntimeError, ValueError):
        return False, "Codex executable was not found on PATH"
    try:
        from libreevolve.llm.codex_cli import _resolve_codex_auth

        auth = _resolve_codex_auth(
            codex_home=backend.get("codex_home"),
            auth_name=backend.get("auth_name"),
            auth_homes=backend.get("auth_homes"),
            auth_registry_path=backend.get("auth_registry_path"),
        )
    except (OSError, RuntimeError, ValueError):
        return False, "Codex auth selection could not be resolved"
    env = os.environ.copy()
    env.pop("OPENAI_API_KEY", None)
    if auth.home:
        env["CODEX_HOME"] = auth.home
    try:
        result = subprocess.run(
            [command, "login", "status"],
            capture_output=True,
            text=True,
            timeout=_CODEX_LOGIN_STATUS_TIMEOUT_SECONDS,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return False, (
            "Codex login status timed out after "
            f"{_CODEX_LOGIN_STATUS_TIMEOUT_SECONDS:g} seconds"
        )
    except (FileNotFoundError, OSError):
        return False, "Codex login status could not be started"
    if result.returncode != 0:
        return False, "Codex login status reported no usable local login"
    status_text = "\n".join(
        value for value in (result.stdout or "", result.stderr or "") if value
    )
    if "chatgpt" not in status_text.casefold():
        return False, "Codex login status did not report a ChatGPT OAuth login"
    return True, "Codex login status reported a local login"


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
@click.option("--source", type=click.Choice(["auto", "history", "workspace"]), default="auto",
              help="Require an explicit choice if the on-disk export differs from history.")
def export_command(run_dir: Path, destination: Path, source: str) -> None:
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
        code = workspace[primary].encode("utf-8")
        source_kind = "history"
        exported = run_dir / "best_workspace" / primary
        if source == "workspace" or (source == "auto" and exported.exists()):
            exported.resolve().relative_to(run_dir.resolve())
            with exported.open("rb") as stream:
                exported_code = stream.read(1_000_001)
            if len(exported_code) > 1_000_000:
                raise ValueError("Exported candidate exceeds the alpha size limit.")
            if (source == "auto" and exported_code.replace(b"\r\n", b"\n")
                    != code.replace(b"\r\n", b"\n")):
                raise ValueError("The workspace differs from saved history. The report reviews "
                                 "workspace bytes. Choose --source workspace to export those bytes "
                                 "or --source history to export the recorded candidate.")
            code = exported_code
            source_kind = "workspace"
        verification = verify_candidate(code)
        if any(verification[split].get("status") != "completed"
               or verification[split].get("correctness") is not True
               for split in ("training", "holdout")):
            raise ValueError("Independent training/held-out verification did not pass; no export created.")
        destination.mkdir(parents=False)
        # Fixed export filename avoids applying historical path names to disk.
        (destination / "solution.py").write_bytes(code)
        history_match = code.replace(b"\r\n", b"\n") == workspace[primary].encode("utf-8").replace(b"\r\n", b"\n")
        verification.update(source_program_id=inspection.best.get("id") if history_match else None,
                            source_kind=source_kind, matches_history=history_match,
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
