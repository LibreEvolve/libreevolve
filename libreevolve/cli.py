from __future__ import annotations
import dataclasses, hashlib, json
from pathlib import Path
import click
from libreevolve.core.jsonl import StrictJsonlError, load_strict_json_object
from libreevolve.core.loop import evolve
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.core import run_inspection as _run_inspection
from libreevolve.core.run_inspection import RunInspectionError
from libreevolve.core.yaml_utils import redacted_yaml_error

_SHOW_SOURCE_DISPLAY_LIMIT = 4096

# Compatibility source anchor for the README legacy-show boundary. Runtime
# status rendering remains owned by ``libreevolve.core.run_inspection``.
_LEGACY_HISTORY_ONLY_STATUS_SOURCE_ANCHOR = (
    "legacy history-only (manifest.json missing)"
)


@click.group()
def cli() -> None:
    """LibreEvolve engineering preview -- bounded local bin-packing optimization."""


from libreevolve.alpha import register_alpha

register_alpha(cli)


@cli.command()
@click.argument("problem_dir", type=click.Path(exists=True, file_okay=False))
@click.option("--max-generations", "-g", type=int, default=None)
@click.option("--max-evaluations", type=int, default=None,
              help="Maximum number of seed/candidate evaluations.")
@click.option("--max-runtime-seconds", type=float, default=None,
              help="Maximum local run duration.")
@click.option("--max-llm-calls", type=int, default=None)
@click.option("--max-llm-provider-attempts", type=int, default=None)
@click.option("--seed", type=int, default=None)
@click.option("--run-name", type=str, default=None, help="New output directory name under runs/.")
@click.option("--progress", is_flag=True, help="Print evaluated candidate counts, generations, and scores.")
def run(problem_dir, max_generations, max_evaluations, max_runtime_seconds,
        max_llm_calls, max_llm_provider_attempts, seed, run_name, progress=False):
    """Run bounded bin-packing optimization through Codex OAuth."""
    from libreevolve.core.config import ConfigError
    from libreevolve.problems.loader import load_problem
    try:
        problem = load_problem(problem_dir)
        if not problem.initial_programs:
            raise click.ClickException("No seed programs found.")
        config = _build_config(
            problem,
            max_generations=max_generations,
            max_evaluations=max_evaluations,
            max_runtime_seconds=max_runtime_seconds,
            max_llm_calls=max_llm_calls,
            max_llm_provider_attempts=max_llm_provider_attempts,
            seed=seed,
        )
        if run_name:
            config.problem_name = run_name
        config.validate()
        _preflight_run_contracts(problem, config)
        _preflight_llm_backends_if_needed(problem, config)
        _prepare_run_dir_for_cli(config)
    except (ConfigError, OSError, ValueError) as exc:
        raise click.ClickException(redact_sensitive_text(str(exc))) from exc
    run_dir = Path(config.log_dir) / config.problem_name
    click.echo(f"Running {config.max_generations} generations on '{config.problem_name}'...")
    click.echo(f"Run artifacts: {run_dir}. Press Ctrl+C to cancel.")
    from libreevolve.alpha_progress import observe_progress
    try:
        with observe_progress(run_dir, progress):
            best = evolve(problem, config)
    except KeyboardInterrupt:
        click.echo(f"Cancelled. Inspect saved state in {run_dir}; "
                   "the latest work may be incomplete.", err=True)
        raise click.exceptions.Exit(130)
    except Exception as exc:
        message = redact_sensitive_text(str(exc))[:1000]
        raise click.ClickException(
            f"Run failed: {message}. Inspect saved state in {run_dir}."
        ) from exc
    if best is None:
        raise click.ClickException("Evolution produced no valid programs.")
    click.echo(f"\nBest fitness: {best.fitness:.6f}")
    export = _load_best_artifact_export_record(run_dir)
    if export.get("status") not in {"completed", "failed"}:
        raise click.ClickException(f"Best artifact export was not finalized. Inspect saved state in {run_dir}.")
    if export.get("status") == "failed":
        message = _bounded_redacted_cli_text(str(export.get("error", "")))
        raise click.ClickException(f"Best artifact export failed: {message}")
    best_py = run_dir / "best.py"
    best_workspace = run_dir / "best_workspace"
    click.echo(f"Best program saved to: {best_py}")
    click.echo(f"Best workspace saved to: {best_workspace}")


@cli.command()
@click.argument("run_dir", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--source-display-chars",
    type=click.IntRange(1, 1_000_000),
    default=_SHOW_SOURCE_DISPLAY_LIMIT,
    show_default=True,
    help="Maximum characters to print per source body before truncation.",
)
@click.option(
    "--full-source",
    is_flag=True,
    help="Print complete selected source bodies instead of truncating them.",
)
@click.option(
    "--redact-source",
    is_flag=True,
    help="Redact secret-like source text before printing or truncating it.",
)
def show(run_dir, source_display_chars, full_source, redact_source):
    """Inspect a previous run."""
    run_path = Path(run_dir)
    try:
        inspection = _run_inspection.inspect_run(run_path)
    except RunInspectionError as exc:
        raise click.ClickException(str(exc)) from exc
    best = inspection.best
    click.echo(f"Total programs: {inspection.total}")
    click.echo(f"Run status:     {inspection.runtime_status}")
    click.echo(f"Selection:      {inspection.selection}")
    click.echo(f"Best fitness:   {best['fitness']:.6f} (generation {best['generation']})")
    for summary in (
        inspection.archive_summary,
        inspection.lineage_summary,
        inspection.prompt_summary,
        inspection.evaluation_summary,
        inspection.feedback_summary,
        inspection.failure_summary,
        inspection.validator_boundary_summary,
        inspection.run_artifact_bundle_summary,
        inspection.quarantine_summary,
        inspection.non_jsonl_artifact_summary,
    ):
        if summary:
            click.echo(summary)
    if inspection.metrics:
        click.echo(
            "Metrics:        "
            f"{json.dumps(inspection.metrics, sort_keys=True, allow_nan=False)}"
        )
    if inspection.workspace is None:
        click.echo("\n--- Best program ---\n")
        click.echo(
            _show_source_text(
                best["code"],
                display_limit=None if full_source else source_display_chars,
                redact=redact_source,
            )
        )
    else:
        primary_file, files = inspection.workspace
        paths = [primary_file] + [
            path for path in sorted(files) if path != primary_file
        ]
        click.echo("\n--- Best workspace ---\n")
        click.echo(f"Primary file:   {primary_file}")
        click.echo(f"Files:          {', '.join(paths)}")
        for path in paths:
            suffix = " (primary)" if path == primary_file else ""
            click.echo(f"\n--- {path}{suffix} ---\n")
            click.echo(
                _show_source_text(
                    files[path],
                    path=path,
                    display_limit=None if full_source else source_display_chars,
                    redact=redact_source,
                )
            )


def _read_show_manifest(path: Path) -> dict:
    try:
        return _run_inspection.read_manifest(path)
    except RunInspectionError as exc:
        raise click.ClickException(str(exc)) from exc


def _iter_history_records(path: Path, *, archive_cell_upper_bound: int | None = None):
    """Compatibility seam for the generated run-artifact inventory."""
    return _run_inspection._iter_history_records(
        path,
        archive_cell_upper_bound=archive_cell_upper_bound,
    )


def _validator_boundary_artifact_summary(run_dir: Path) -> str | None:
    """Compatibility seam for the generated run-artifact inventory."""
    return _run_inspection._validator_boundary_artifact_summary(run_dir)


def _validate_manifest_run_artifact_bundle_report(
    manifest: dict,
    *,
    error_prefix: str,
) -> None:
    try:
        _run_inspection.validate_manifest_run_artifact_bundle_report(
            manifest,
            error_prefix=error_prefix,
        )
    except RunInspectionError as exc:
        raise click.ClickException(str(exc)) from exc


def _show_source_text(
    source: str,
    *,
    path: str | None = None,
    display_limit: int | None = _SHOW_SOURCE_DISPLAY_LIMIT,
    redact: bool = False,
) -> str:
    return _run_inspection.render_source(
        source,
        path=path,
        display_limit=display_limit,
        redact=redact,
    )


def _build_config(
    problem, *, max_generations=None, max_evaluations=None,
    max_runtime_seconds=None, max_llm_calls=None, max_llm_provider_attempts=None,
    seed=None,
):
    import yaml
    from libreevolve.core.config import Config, ConfigError
    from libreevolve.core.yaml_utils import safe_load_unique
    cp = Path(problem.problem_dir) / "config.yaml"
    cfg, config_source = _load_problem_config_yaml(cp, safe_load_unique, yaml)
    problem.config_source = config_source
    valid = {f.name for f in dataclasses.fields(Config)}
    non_string_keys = [key for key in cfg if not isinstance(key, str)]
    if non_string_keys:
        formatted = _redacted_config_values(non_string_keys)
        raise ConfigError(f"config.yaml top-level config keys must be strings; got {formatted}")
    unknown = sorted(set(cfg) - valid)
    if unknown:
        raise ConfigError(f"Unknown config keys in config.yaml: {_redacted_config_values(unknown)}")
    if "problem_name" in cfg:
        raise ConfigError(
            "config.yaml problem_name is not used by the CLI; use --run-name "
            "to choose the run directory"
        )
    effective = {k: v for k, v in cfg.items() if k in valid}
    for name, value in (
        ("max_generations", max_generations),
        ("max_evaluations", max_evaluations),
        ("max_runtime_seconds", max_runtime_seconds),
        ("max_llm_calls", max_llm_calls),
        ("max_llm_provider_attempts", max_llm_provider_attempts),
        ("seed", seed),
    ):
        if value is not None:
            effective[name] = value
    effective["problem_name"] = "unnamed"
    config = Config(**effective)
    config.problem_name = problem.name
    return config


def _load_problem_config_yaml(path: Path, safe_load_unique, yaml_module) -> tuple[dict, dict]:
    if _is_link(path):
        raise _config_file_error("config.yaml links are not supported")
    if not path.exists():
        return {}, {"path": "config.yaml", "status": "absent"}
    if not path.is_file():
        raise _config_file_error("config.yaml must be a regular file")
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        raise _config_file_error(f"Failed to read config.yaml: {exc}", path) from exc
    source = {
        "path": "config.yaml",
        "status": "ok",
        "sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "bytes": len(raw_bytes),
    }
    try:
        raw_config = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _config_file_error(f"Failed to read config.yaml as UTF-8: {exc}", path) from exc
    try:
        loaded = safe_load_unique(raw_config)
    except yaml_module.YAMLError as exc:
        raise _config_file_error(
            f"Failed to parse config.yaml: {redacted_yaml_error(exc)}",
            path,
        ) from exc
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        raise _config_file_error("config.yaml must contain a YAML mapping at the top level")
    return dict(loaded), source


def _config_file_error(message: str, path: Path | None = None):
    from libreevolve.core.config import ConfigError

    text = str(message)
    if path is not None:
        text = text.replace(str(path), "config.yaml")
        try:
            resolved_path = str(path.resolve(strict=False))
        except OSError:
            resolved_path = ""
        if resolved_path:
            text = text.replace(resolved_path, "config.yaml")
    return ConfigError(redact_sensitive_text(text))


def _redacted_config_values(values: list[object]) -> str:
    rendered = ", ".join(sorted(repr(value) for value in values))
    return redact_sensitive_text(rendered)


def _is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (is_junction is not None and is_junction())


def _prepare_run_dir_for_cli(config) -> None:
    from libreevolve.core.database import prepare_run_directory, validate_run_directory_path

    log_root = Path(config.log_dir)
    run_dir = log_root / config.problem_name
    validate_run_directory_path(log_root, run_dir)
    prepare_run_directory(run_dir, config.run_collision_policy)


def _preflight_run_contracts(problem, config) -> None:
    from libreevolve.core.evaluator import preflight_evaluator_contracts

    preflight_evaluator_contracts(
        problem,
        config.eval_stages,
        validator_env_allowlist=config.validator_env_allowlist,
    )


def _preflight_llm_backends_if_needed(problem, config) -> None:
    if not _mutation_llm_can_run(problem, config):
        return
    from libreevolve.llm.ensemble import build_llm

    try:
        build_llm(config)
    except Exception as exc:
        raise click.ClickException(f"LLM backend preflight failed: {exc}") from exc


def _mutation_llm_can_run(problem, config) -> bool:
    if config.max_generations <= 0:
        return False
    if config.max_llm_calls is not None and config.max_llm_calls <= 0:
        return False
    if (
        config.max_llm_provider_attempts is not None
        and config.max_llm_provider_attempts <= 0
    ):
        return False
    if config.max_llm_tokens is not None and config.max_llm_tokens <= 0:
        return False
    if (
        config.max_llm_cost_microusd is not None
        and config.max_llm_cost_microusd <= 0
    ):
        return False
    if config.max_llm_seconds is not None and config.max_llm_seconds <= 0:
        return False
    if config.llm_role_provider_attempt_limits.get("mutation") == 0:
        return False
    if config.llm_role_token_limits.get("mutation") == 0:
        return False
    if config.llm_role_cost_microusd_limits.get("mutation") == 0:
        return False
    if config.llm_role_seconds_limits.get("mutation") == 0:
        return False
    seed_count = len(problem.initial_workspaces or problem.initial_programs)
    if config.max_evaluations is not None and config.max_evaluations <= seed_count:
        return False
    return True


def _bounded_redacted_cli_text(text: str, limit: int = 1000) -> str:
    rendered = redact_sensitive_text(text)
    if len(rendered) <= limit:
        return rendered
    return rendered[:limit] + "...<truncated>"


def _load_best_artifact_export_record(run_dir: Path) -> dict:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        manifest = load_strict_json_object(
            manifest_path,
            source="manifest.json",
        )
    except StrictJsonlError as exc:
        return {
            "status": "failed",
            "error": f"manifest read failed: {_bounded_redacted_cli_text(str(exc))}",
        }
    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        return {}
    export = runtime.get("best_artifact_export")
    return export if isinstance(export, dict) else {}
