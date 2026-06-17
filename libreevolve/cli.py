from __future__ import annotations
import dataclasses, hashlib, json, math, re
import os
from pathlib import Path
import shutil
from uuid import uuid4
import click
from dotenv import dotenv_values, find_dotenv, load_dotenv
from libreevolve.core.best_artifacts import (
    BestArtifactExportError,
    STATIC_WORKSPACE_MANIFEST_NAME,
    _remove_best_artifact_temp,
    _write_best_artifacts,
)
from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.jsonl import (
    StrictJsonlError,
    load_strict_json_object,
    strict_json_dump,
)
from libreevolve.core.artifact_schema import (
    validate_paper_artifact_lifecycle_manifest,
)
from libreevolve.core.loop import (
    RuntimeBudgetStateError,
    RuntimeFullResumeBundleError,
    RuntimeLLMSchedulerStateError,
    RuntimeRngStateError,
    evolve,
    load_full_resume_bundle,
    load_runtime_budget_state_snapshot,
    load_runtime_llm_scheduler_state_snapshot,
    load_runtime_rng_state_snapshot,
)
from libreevolve.core.database import (
    ArchiveStateRestoreError,
    HistoryRestoreError,
    load_archive_restore_bundle,
    load_runtime_archive_state_snapshot,
)
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.core.validator_policy import (
    validate_run_artifact_validator_boundary_consistency,
)
from libreevolve.core.yaml_utils import redacted_yaml_error
from libreevolve.population.program import validate_program_identity, validate_program_metrics

_ARCHIVE_DESCRIPTOR_PREVIEW_LIMIT = 8
_ARCHIVE_DESCRIPTOR_LABEL_DISPLAY_LIMIT = 48
_ARCHIVE_DESCRIPTOR_JSON_DISPLAY_LIMIT = 512
_SHOW_DIAGNOSTIC_LABEL_DISPLAY_LIMIT = 64
_SHOW_DIAGNOSTIC_BUCKET_LIMIT = 5
_SHOW_SOURCE_DISPLAY_LIMIT = 4096


@click.group()
def cli() -> None:
    """LibreEvolve -- LLM-guided evolutionary program discovery."""


@cli.command()
@click.argument("problem_dir", type=click.Path(exists=True, file_okay=False))
@click.option("--max-generations", "-g", type=int, default=None)
@click.option("--max-evaluations", type=int, default=None,
              help="Maximum number of seed/candidate evaluations.")
@click.option("--max-evaluator-seconds", type=float, default=None,
              help="Maximum cumulative evaluator elapsed seconds.")
@click.option("--max-runtime-seconds", type=float, default=None,
              help="Maximum wall-clock seconds checked between evaluations.")
@click.option("--proposals-per-generation", type=int, default=None,
              help="Sequential mutation proposals to evaluate inside each generation.")
@click.option("--plugins",  "-p", multiple=True)
@click.option("--backends", "-b", multiple=True)
@click.option("--seed", type=int, default=None)
@click.option("--reasoning-effort", "-r", type=str, default=None,
              help="Reasoning effort for OpenAI reasoning models (none, minimal, low, medium, high, xhigh; model-aware validation applies)")
@click.option("--llm-max-retries", type=int, default=None,
              help="Retry attempts on the same selected LLM backend before fallback/failure.")
@click.option("--llm-max-call-attempts", type=int, default=None,
              help="Maximum total original/retry/fallback attempts per LLM call.")
@click.option("--llm-fallback/--no-llm-fallback", default=None,
              help="Enable or disable fallback to another LLM backend after retries.")
@click.option("--llm-max-response-chars", type=int, default=None,
              help="Maximum accepted LLM response characters before retry/fallback failure.")
@click.option("--llm-call-history-max", type=int, default=None,
              help="Maximum retained in-memory LLM call telemetry records.")
@click.option("--llm-call-timeout-sec", type=float, default=None,
              help="Optional ensemble-level timeout seconds for each LLM backend call.")
@click.option("--max-llm-calls", type=int, default=None,
              help="Maximum logical LLM generate calls before stopping the run.")
@click.option("--max-llm-provider-attempts", type=int, default=None,
              help="Maximum provider adapter attempts before stopping the run.")
@click.option("--max-llm-tokens", type=int, default=None,
              help="Maximum provider-reported total tokens before stopping the run.")
@click.option("--max-llm-cost-microusd", type=int, default=None,
              help="Maximum configured estimated LLM cost in micro-USD before stopping.")
@click.option("--max-llm-seconds", type=float, default=None,
              help="Maximum cumulative LLM call latency seconds before stopping.")
@click.option("--prompt-max-chars", type=int, default=None,
              help="Maximum rendered mutation prompt characters before deterministic truncation.")
@click.option("--prompt-max-estimated-tokens", type=int, default=None,
              help="Maximum heuristic estimated prompt tokens before deterministic truncation.")
@click.option("--explore-ratio", "-e", type=float, default=None,
              help="Probability of exploring (random parent) vs exploiting (best parent). Default: 0.3")
@click.option("--parent-selection-strategy",
              type=click.Choice(["mixed", "exploit", "explore", "metric", "frontier", "lineage", "novelty", "recency"]),
              default=None,
              help="Parent sampling policy. Default: mixed")
@click.option("--inspiration-strategy",
              type=click.Choice(["mixed", "random", "selection", "metric", "frontier", "lineage", "novelty", "recency"]),
              default=None,
              help="Inspiration sampling policy. Default: mixed")
@click.option("--mutation-mode", type=click.Choice(["diff", "full"]), default=None,
              help="Mutation response mode: SEARCH/REPLACE diffs or full code/block replacement.")
@click.option("--run-name", type=str, default=None,
              help="Custom name for this run (default: problem directory name)")
@click.option(
    "--restore-runtime-from-manifest",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help=(
        "Restore all currently compatible runtime surfaces from one previous "
        "manifest.json plus sibling history.jsonl and controller_budget_events.jsonl. "
        "This composes RNG, LLM scheduler, archive contents, and budget counters; "
        "it does not replay provider outputs or pending controller work."
    ),
)
@click.option(
    "--restore-rng-from-manifest",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help=(
        "Restore the framework run RNG from a previous manifest.json runtime.rng "
        "snapshot. This does not restore archive or controller state."
    ),
)
@click.option(
    "--restore-llm-scheduler-from-manifest",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help=(
        "Restore LLM ensemble scheduler state from a previous manifest.json "
        "runtime.llm_scheduler snapshot. This does not replay provider outputs "
        "or controller queues."
    ),
)
@click.option(
    "--restore-archive-cursor-from-manifest",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help=(
        "Restore only the compact island cursor/counter state from a previous "
        "manifest.json runtime.history.archive_state snapshot. This does not "
        "restore MAP-Elites cells, elites, or controller state."
    ),
)
@click.option(
    "--restore-archive-from-manifest",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help=(
        "Restore MAP-Elites archive cells/elites from a previous manifest.json "
        "runtime.history.archive_state snapshot and sibling history.jsonl. "
        "This does not replay migration events or controller queues."
    ),
)
@click.option(
    "--restore-budget-from-manifest",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help=(
        "Restore consumed runtime budget counters from a previous manifest.json "
        "top-level runtime budget snapshot before new seed/generation work."
    ),
)
@click.option("--overwrite", is_flag=True,
              help="Delete existing run artifacts in the target run directory before starting.")
def run(problem_dir, max_generations, max_evaluations, max_evaluator_seconds,
        max_runtime_seconds, proposals_per_generation, plugins, backends, seed, reasoning_effort,
        llm_max_retries, llm_max_call_attempts, llm_fallback,
        llm_max_response_chars, llm_call_history_max, llm_call_timeout_sec,
        max_llm_calls, max_llm_provider_attempts, max_llm_tokens,
        max_llm_cost_microusd, max_llm_seconds,
        prompt_max_chars, prompt_max_estimated_tokens, explore_ratio,
        parent_selection_strategy, inspiration_strategy, mutation_mode,
        run_name, restore_runtime_from_manifest,
        restore_rng_from_manifest, restore_llm_scheduler_from_manifest,
        restore_archive_cursor_from_manifest,
        restore_archive_from_manifest, restore_budget_from_manifest, overwrite):
    """Run evolution on a problem directory."""
    from libreevolve.core.config import ConfigError
    from libreevolve.problems.loader import load_problem
    try:
        problem = load_problem(problem_dir)
        problem.dotenv_source = _load_cli_dotenv()
        if not problem.initial_programs:
            raise click.ClickException("No seed programs found.")
        config = _build_config(
            problem,
            max_generations,
            max_evaluations,
            max_evaluator_seconds,
            max_runtime_seconds,
            proposals_per_generation,
            list(plugins),
            list(backends),
            seed,
            reasoning_effort,
            llm_max_retries,
            llm_max_call_attempts,
            llm_fallback,
            llm_max_response_chars,
            llm_call_history_max,
            llm_call_timeout_sec,
            max_llm_calls,
            max_llm_provider_attempts,
            max_llm_tokens,
            max_llm_cost_microusd,
            max_llm_seconds,
            prompt_max_chars,
            prompt_max_estimated_tokens,
            explore_ratio,
            parent_selection_strategy,
            inspiration_strategy,
            mutation_mode,
        )
        if run_name:
            config.problem_name = run_name
        if overwrite:
            config.run_collision_policy = "overwrite"
        config.validate()
        _validate_plugin_names(config.plugins)
        _preflight_run_contracts(problem, config)
        _preflight_llm_backends_if_needed(problem, config)
        _validate_cli_runtime_restore_flags(
            restore_runtime_from_manifest,
            restore_rng_from_manifest,
            restore_llm_scheduler_from_manifest,
            restore_archive_cursor_from_manifest,
            restore_archive_from_manifest,
            restore_budget_from_manifest,
        )
        if restore_runtime_from_manifest:
            resume_bundle = _load_cli_full_resume_bundle(restore_runtime_from_manifest)
            evolve_kwargs = resume_bundle["evolve_kwargs"]
            runtime_rng_state_snapshot = evolve_kwargs["runtime_rng_state_snapshot"]
            if runtime_rng_state_snapshot["seed"] != config.seed:
                raise click.ClickException(
                    "Runtime manifest restore failed: snapshot seed "
                    f"{runtime_rng_state_snapshot['seed']} does not match "
                    f"configured seed {config.seed}"
                )
            runtime_llm_scheduler_state_snapshot = evolve_kwargs[
                "runtime_llm_scheduler_state_snapshot"
            ]
            runtime_budget_state_snapshot = evolve_kwargs[
                "runtime_budget_state_snapshot"
            ]
            runtime_archive_state_snapshot = evolve_kwargs[
                "runtime_archive_state_snapshot"
            ]
            runtime_archive_programs_by_id = evolve_kwargs[
                "runtime_archive_programs_by_id"
            ]
        else:
            runtime_rng_state_snapshot = _load_cli_runtime_rng_snapshot(
                restore_rng_from_manifest,
                seed=config.seed,
            )
            runtime_llm_scheduler_state_snapshot = (
                _load_cli_runtime_llm_scheduler_snapshot(
                    restore_llm_scheduler_from_manifest
                )
            )
            runtime_budget_state_snapshot = _load_cli_runtime_budget_snapshot(
                restore_budget_from_manifest
            )
            if restore_archive_cursor_from_manifest and restore_archive_from_manifest:
                raise click.ClickException(
                    "Use either --restore-archive-cursor-from-manifest or "
                    "--restore-archive-from-manifest, not both"
                )
            runtime_archive_programs_by_id = None
            if restore_archive_from_manifest:
                archive_bundle = _load_cli_archive_restore_bundle(
                    restore_archive_from_manifest
                )
                runtime_archive_state_snapshot = archive_bundle["archive_state_snapshot"]
                runtime_archive_programs_by_id = archive_bundle["archive_programs_by_id"]
            else:
                runtime_archive_state_snapshot = _load_cli_runtime_archive_state_snapshot(
                    restore_archive_cursor_from_manifest
                )
        _prepare_run_dir_for_cli(config)
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc
    except (FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    except FileExistsError as exc:
        raise click.ClickException(str(exc)) from exc
    run_dir = Path(config.log_dir) / config.problem_name
    click.echo(f"Running {config.max_generations} generations on '{config.problem_name}'...")
    best = evolve(
        problem,
        config,
        runtime_rng_state_snapshot=runtime_rng_state_snapshot,
        runtime_llm_scheduler_state_snapshot=runtime_llm_scheduler_state_snapshot,
        runtime_archive_state_snapshot=runtime_archive_state_snapshot,
        runtime_archive_programs_by_id=runtime_archive_programs_by_id,
        runtime_budget_state_snapshot=runtime_budget_state_snapshot,
    )
    if best is None:
        raise click.ClickException("Evolution produced no valid programs.")
    click.echo(f"\nBest fitness: {best.fitness:.6f}")
    export = _load_best_artifact_export_record(run_dir)
    if export.get("status") not in {"completed", "failed"}:
        export = _materialize_missing_best_artifact_export(best, run_dir)
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
    h = run_path / "history.jsonl"
    if not h.exists():
        raise click.ClickException(f"No history.jsonl found in {run_dir}")
    total = 0
    has_archive_metadata = False
    first_modern_line = None
    first_legacy_line = None
    best_modern = None
    best_legacy = None
    archive_cell_upper_bound = _show_archive_cell_upper_bound(run_path)
    for line_number, record in _iter_history_records(
        h,
        archive_cell_upper_bound=archive_cell_upper_bound,
    ):
        total += 1
        is_modern = _has_archive_metadata(record)
        if is_modern:
            if first_modern_line is None:
                first_modern_line = line_number
            if first_legacy_line is not None:
                _raise_mixed_history_schema(
                    line_number, first_legacy_line, first_modern_line
                )
            has_archive_metadata = True
            if _is_archive_admitted_valid(record):
                best_modern = _select_better_record(
                    best_modern,
                    (line_number, record),
                    lambda item: _record_selection_key(item[1]),
                )
        else:
            if first_legacy_line is None:
                first_legacy_line = line_number
            if first_modern_line is not None:
                _raise_mixed_history_schema(
                    line_number, first_legacy_line, first_modern_line
                )
        best_legacy = _select_better_record(
            best_legacy,
            (line_number, record),
            lambda item: float(item[1].get("fitness", float("-inf"))),
        )
    if total == 0:
        raise click.ClickException("history.jsonl is empty")
    if has_archive_metadata:
        if best_modern is None:
            raise click.ClickException("No archive-retained valid programs found")
        best_line_number, best = best_modern
        selection = "archive-retained valid"
    else:
        best_line_number, best = best_legacy
        selection = "legacy highest-fitness"
    runtime_status = _show_runtime_status(run_path, total)
    _validate_display_record(best, best_line_number)
    archive_summary = _archive_summary(
        best,
        best_line_number,
        archive_cell_upper_bound=archive_cell_upper_bound,
    )
    lineage_summary = _lineage_summary(best)
    prompt_summary = _prompt_summary(best, best_line_number)
    evaluation_summary = _evaluation_diagnostics_summary(best, best_line_number)
    feedback_summary = _feedback_summary(best, best_line_number)
    failure_summary = _failure_statistics_summary(run_path)
    validator_boundary_summary = _validator_boundary_artifact_summary(run_path)
    paper_artifact_summary = _paper_artifact_lifecycle_summary(run_path)
    metrics = best.get("metrics")
    workspace = _history_record_workspace(best, best_line_number)
    click.echo(f"Total programs: {total}")
    click.echo(f"Run status:     {runtime_status}")
    click.echo(f"Selection:      {selection}")
    click.echo(f"Best fitness:   {best['fitness']:.6f} (generation {best['generation']})")
    if archive_summary:
        click.echo(archive_summary)
    if lineage_summary:
        click.echo(lineage_summary)
    if prompt_summary:
        click.echo(prompt_summary)
    if evaluation_summary:
        click.echo(evaluation_summary)
    if feedback_summary:
        click.echo(feedback_summary)
    if failure_summary:
        click.echo(failure_summary)
    if validator_boundary_summary:
        click.echo(validator_boundary_summary)
    if paper_artifact_summary:
        click.echo(paper_artifact_summary)
    if metrics:
        click.echo(f"Metrics:        {json.dumps(metrics, sort_keys=True, allow_nan=False)}")
    if workspace is None:
        click.echo("\n--- Best program ---\n")
        click.echo(
            _show_source_text(
                best["code"],
                display_limit=None if full_source else source_display_chars,
                redact=redact_source,
            )
        )
    else:
        primary_file, files = workspace
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


def _show_runtime_status(run_dir: Path, history_rows: int) -> str:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return "legacy history-only (manifest.json missing)"
    manifest = _read_show_manifest(manifest_path)
    runtime = manifest.get("runtime")
    if runtime is None:
        return "partial best-so-far (manifest runtime missing)"
    if not isinstance(runtime, dict):
        raise click.ClickException("Malformed manifest.json: runtime must be an object")
    status = runtime.get("status")
    if status not in {"completed", "aborted"}:
        raise click.ClickException(
            "Malformed manifest.json: runtime.status must be 'completed' or 'aborted'"
        )
    stop_reason = runtime.get("stop_reason")
    if not _is_manifest_runtime_label(stop_reason):
        raise click.ClickException(
            "Malformed manifest.json: runtime.stop_reason must be a manifest-safe label"
        )
    _validate_show_manifest_history(runtime.get("history"), history_rows)
    if status == "completed":
        return f"completed (stop_reason: {stop_reason})"
    return f"aborted best-so-far (stop_reason: {stop_reason})"


def _validator_boundary_artifact_summary(run_dir: Path) -> str | None:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    validation = validate_run_artifact_validator_boundary_consistency(run_dir)
    if not validation.manifest_policy_present and not validation.issues:
        return None
    if not validation.ok:
        issue = validation.issues[0]
        location = issue.stream or "run artifacts"
        if issue.line_number is not None:
            location = f"{location} line {issue.line_number}"
        raise click.ClickException(
            "Validator boundary artifact validation failed: "
            f"{location}: {issue.code}: {issue.message}"
        )
    streams = ",".join(validation.checked_streams) or "none"
    return (
        "Validator boundary: "
        f"checked_attempts={validation.checked_attempts}; streams={streams}"
    )


def _paper_artifact_lifecycle_summary(run_dir: Path) -> str | None:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    manifest = _read_show_manifest(manifest_path)
    artifact_schema = manifest.get("artifact_schema")
    if (
        not isinstance(artifact_schema, dict)
        or "paper_artifact_subpaths" not in artifact_schema
    ):
        return None
    validation = validate_paper_artifact_lifecycle_manifest(
        manifest,
        run_artifacts_doc_text=_show_run_artifacts_doc_text(),
    )
    if not validation["ok"]:
        issue = validation["issues"][0]
        raise click.ClickException(
            "Paper artifact lifecycle validation failed: "
            f"{issue['code']}: {issue['message']}"
        )
    return (
        "Paper artifacts: "
        f"checked_paths={validation['emitted_path_count']}; "
        f"docs_refs={len(validation['documented_refs'])}"
    )


def _show_run_artifacts_doc_text() -> str | None:
    doc_path = Path(__file__).resolve().parents[1] / "docs" / "run-artifacts.md"
    try:
        return doc_path.read_text(encoding="utf-8")
    except OSError:
        return None


def _show_archive_cell_upper_bound(run_dir: Path) -> int | None:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    manifest = _read_show_manifest(manifest_path)
    config = manifest.get("config")
    if config is None:
        return None
    if not isinstance(config, dict):
        raise click.ClickException("Malformed manifest.json: config must be an object")
    bins = config.get("map_elites_bins")
    if bins is None:
        return None
    if isinstance(bins, bool) or not isinstance(bins, int) or bins < 1:
        raise click.ClickException(
            "Malformed manifest.json: config.map_elites_bins must be a positive integer"
        )
    return bins


def _read_show_manifest(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise click.ClickException(
            f"Malformed manifest.json: invalid UTF-8 ({exc.reason})"
        ) from exc
    except OSError as exc:
        raise click.ClickException(f"Failed to read manifest.json: {exc}") from exc
    try:
        manifest = json.loads(text, object_pairs_hook=_reject_duplicate_history_json_names)
    except _DuplicateHistoryJsonNameError as exc:
        raise click.ClickException(f"Malformed manifest.json: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"Malformed manifest.json: {exc.msg}") from exc
    if not isinstance(manifest, dict):
        raise click.ClickException("Malformed manifest.json: expected JSON object")
    return manifest


def _validate_show_manifest_history(history: object, history_rows: int) -> None:
    if history is None:
        return
    if not isinstance(history, dict):
        raise click.ClickException("Malformed manifest.json: runtime.history must be an object")
    programs_logged = history.get("programs_logged")
    if programs_logged is None:
        return
    if (
        isinstance(programs_logged, bool)
        or not isinstance(programs_logged, int)
        or programs_logged < 0
    ):
        raise click.ClickException(
            "Malformed manifest.json: runtime.history.programs_logged "
            "must be a non-negative integer"
        )
    if programs_logged != history_rows:
        raise click.ClickException(
            "Inconsistent manifest.json/runtime history: "
            f"programs_logged={programs_logged} but history.jsonl has {history_rows} row(s)"
        )


def _is_manifest_runtime_label(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if redact_sensitive_text(value) != value:
        return False
    return re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value) is not None


def _build_config(problem, max_generations, max_evaluations, max_evaluator_seconds,
                  max_runtime_seconds, proposals_per_generation, plugins, backends, seed,
                  reasoning_effort=None, llm_max_retries=None,
                  llm_max_call_attempts=None, llm_fallback=None,
                  llm_max_response_chars=None, llm_call_history_max=None,
                  llm_call_timeout_sec=None,
                  max_llm_calls=None,
                  max_llm_provider_attempts=None,
                  max_llm_tokens=None,
                  max_llm_cost_microusd=None,
                  max_llm_seconds=None,
                  prompt_max_chars=None, prompt_max_estimated_tokens=None,
                  explore_ratio=None, parent_selection_strategy=None,
                  inspiration_strategy=None, mutation_mode=None):
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
    if max_generations is not None: effective["max_generations"] = max_generations
    if max_evaluations is not None: effective["max_evaluations"] = max_evaluations
    if max_evaluator_seconds is not None: effective["max_evaluator_seconds"] = max_evaluator_seconds
    if max_runtime_seconds is not None: effective["max_runtime_seconds"] = max_runtime_seconds
    if proposals_per_generation is not None:
        effective["proposals_per_generation"] = proposals_per_generation
    if plugins: effective["plugins"] = list(plugins)
    if backends:
        bd = [{"type": t, "model": m} for b in backends for t, _, m in [b.partition(":")]]
        if reasoning_effort:
            for d in bd:
                if d.get("type") == "openai":
                    d["reasoning_effort"] = reasoning_effort
        effective["backends"] = bd
    elif reasoning_effort:
        configured_backends = [dict(backend) for backend in effective.get("backends", Config().backends)]
        for backend in configured_backends:
            if backend.get("type") == "openai":
                backend["reasoning_effort"] = reasoning_effort
        effective["backends"] = configured_backends
    if seed is not None: effective["seed"] = seed
    if llm_max_retries is not None: effective["llm_max_retries"] = llm_max_retries
    if llm_max_call_attempts is not None:
        effective["llm_max_call_attempts"] = llm_max_call_attempts
    if llm_fallback is not None: effective["llm_fallback"] = llm_fallback
    if llm_max_response_chars is not None:
        effective["llm_max_response_chars"] = llm_max_response_chars
    if llm_call_history_max is not None:
        effective["llm_call_history_max"] = llm_call_history_max
    if llm_call_timeout_sec is not None:
        effective["llm_call_timeout_sec"] = llm_call_timeout_sec
    if max_llm_calls is not None:
        effective["max_llm_calls"] = max_llm_calls
    if max_llm_provider_attempts is not None:
        effective["max_llm_provider_attempts"] = max_llm_provider_attempts
    if max_llm_tokens is not None:
        effective["max_llm_tokens"] = max_llm_tokens
    if max_llm_cost_microusd is not None:
        effective["max_llm_cost_microusd"] = max_llm_cost_microusd
    if max_llm_seconds is not None:
        effective["max_llm_seconds"] = max_llm_seconds
    if prompt_max_chars is not None:
        effective["prompt_max_chars"] = prompt_max_chars
    if prompt_max_estimated_tokens is not None:
        effective["prompt_max_estimated_tokens"] = prompt_max_estimated_tokens
    if explore_ratio is not None: effective["explore_ratio"] = explore_ratio
    if parent_selection_strategy is not None:
        effective["parent_selection_strategy"] = parent_selection_strategy
    if inspiration_strategy is not None:
        effective["inspiration_strategy"] = inspiration_strategy
    if mutation_mode is not None: effective["mutation_mode"] = mutation_mode
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


def _load_cli_dotenv() -> dict:
    record = {
        "path": ".env",
        "status": "absent",
        "override": True,
        "load_phase": "cli_run_command",
        "scope": "run_command_provider_setup",
    }
    dotenv_path = find_dotenv(usecwd=True)
    if not dotenv_path:
        return record
    path = Path(dotenv_path)
    record["path"] = _display_dotenv_path(path)
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        record["status"] = "unreadable"
        record["error_type"] = exc.__class__.__name__
        record["message"] = _bounded_redacted_cli_text(str(exc))
        return record
    values = dotenv_values(path)
    loaded = load_dotenv(dotenv_path=path, override=True)
    record.update(
        {
            "status": "loaded" if loaded else "present_no_values",
            "sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "bytes": len(raw_bytes),
            "keys": sorted(
                redact_sensitive_text(str(key))
                for key in values
                if isinstance(key, str) and key
            ),
        }
    )
    return record


def _display_dotenv_path(path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(Path.cwd().resolve()).as_posix()
    except (OSError, ValueError):
        return "<external-dotenv>"


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


def _load_plugins(names: list[str], run_dir: Path | None = None) -> list:
    from libreevolve.plugins.registry import load_plugins

    return load_plugins(names, run_dir=run_dir)


def _validate_plugin_names(names: list[str]) -> None:
    from libreevolve.plugins.registry import validate_plugin_specs

    validate_plugin_specs(names)


def _plugin_registry() -> dict:
    from libreevolve.plugins.registry import plugin_class_registry

    return plugin_class_registry()


def _unknown_plugin(name: str, registry: dict) -> click.ClickException:
    return click.ClickException(f"Unknown plugin: {name!r}. Available: {list(registry)}")


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
    required_env = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}
    missing = []
    for backend in config.backends:
        env_name = required_env.get(backend.get("type"))
        if env_name and not _has_nonblank_env(env_name):
            missing.append(f"{backend.get('type')} backend {backend.get('model')!r} requires {env_name}")
    if missing:
        raise click.ClickException("LLM backend preflight failed: " + "; ".join(missing))
    from libreevolve.llm.ensemble import build_llm

    try:
        build_llm(config)
    except Exception as exc:
        raise click.ClickException(f"LLM backend preflight failed: {exc}") from exc


def _has_nonblank_env(name: str) -> bool:
    value = os.getenv(name)
    return isinstance(value, str) and bool(value.strip())


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


def _load_cli_runtime_rng_snapshot(path: str | None, *, seed: int) -> dict | None:
    if path is None:
        return None
    _validate_cli_paper_artifact_restore_manifest(
        path,
        error_prefix="Runtime RNG manifest restore failed",
    )
    try:
        snapshot = load_runtime_rng_state_snapshot(path)
    except RuntimeRngStateError as exc:
        message = _bounded_redacted_cli_text(str(exc))
        raise click.ClickException(
            f"Runtime RNG manifest restore failed: {message}"
        ) from exc
    if snapshot["seed"] != seed:
        raise click.ClickException(
            "Runtime RNG manifest restore failed: snapshot seed "
            f"{snapshot['seed']} does not match configured seed {seed}"
        )
    return snapshot


def _load_cli_runtime_llm_scheduler_snapshot(path: str | None) -> dict | None:
    if path is None:
        return None
    _validate_cli_paper_artifact_restore_manifest(
        path,
        error_prefix="LLM scheduler manifest restore failed",
    )
    try:
        return load_runtime_llm_scheduler_state_snapshot(path)
    except RuntimeLLMSchedulerStateError as exc:
        message = _bounded_redacted_cli_text(str(exc))
        raise click.ClickException(
            f"LLM scheduler manifest restore failed: {message}"
        ) from exc


def _load_cli_runtime_budget_snapshot(path: str | None) -> dict | None:
    if path is None:
        return None
    _validate_cli_paper_artifact_restore_manifest(
        path,
        error_prefix="Runtime budget manifest restore failed",
    )
    try:
        return load_runtime_budget_state_snapshot(path)
    except RuntimeBudgetStateError as exc:
        message = _redacted_exception_message(exc)
        raise click.ClickException(
            f"Runtime budget manifest restore failed: {message}"
        ) from exc


def _validate_cli_runtime_restore_flags(
    restore_runtime_from_manifest: str | None,
    restore_rng_from_manifest: str | None,
    restore_llm_scheduler_from_manifest: str | None,
    restore_archive_cursor_from_manifest: str | None,
    restore_archive_from_manifest: str | None,
    restore_budget_from_manifest: str | None,
) -> None:
    if restore_runtime_from_manifest is None:
        return
    individual = [
        flag
        for flag, value in (
            ("--restore-rng-from-manifest", restore_rng_from_manifest),
            (
                "--restore-llm-scheduler-from-manifest",
                restore_llm_scheduler_from_manifest,
            ),
            (
                "--restore-archive-cursor-from-manifest",
                restore_archive_cursor_from_manifest,
            ),
            ("--restore-archive-from-manifest", restore_archive_from_manifest),
            ("--restore-budget-from-manifest", restore_budget_from_manifest),
        )
        if value is not None
    ]
    if individual:
        raise click.ClickException(
            "--restore-runtime-from-manifest cannot be combined with "
            + ", ".join(individual)
        )


def _load_cli_full_resume_bundle(path: str) -> dict:
    _validate_cli_paper_artifact_restore_manifest(
        path,
        error_prefix="Runtime manifest restore failed",
    )
    try:
        return load_full_resume_bundle(path)
    except RuntimeFullResumeBundleError as exc:
        message = _bounded_redacted_cli_text(str(exc))
        raise click.ClickException(
            f"Runtime manifest restore failed: {message}"
        ) from exc


def _load_cli_runtime_archive_state_snapshot(path: str | None) -> dict | None:
    if path is None:
        return None
    _validate_cli_paper_artifact_restore_manifest(
        path,
        error_prefix="Archive cursor manifest restore failed",
    )
    try:
        return load_runtime_archive_state_snapshot(path)
    except ArchiveStateRestoreError as exc:
        message = _bounded_redacted_cli_text(str(exc))
        raise click.ClickException(
            f"Archive cursor manifest restore failed: {message}"
        ) from exc


def _load_cli_archive_restore_bundle(path: str | None) -> dict | None:
    if path is None:
        return None
    manifest_path = Path(path)
    _validate_cli_paper_artifact_restore_manifest(
        manifest_path,
        error_prefix="Archive manifest restore failed",
    )
    history_path = manifest_path.parent / "history.jsonl"
    try:
        return load_archive_restore_bundle(manifest_path, history_path)
    except (ArchiveStateRestoreError, HistoryRestoreError, ValueError) as exc:
        message = _bounded_redacted_cli_text(str(exc))
        raise click.ClickException(
            f"Archive manifest restore failed: {message}"
        ) from exc


def _validate_cli_paper_artifact_restore_manifest(
    path: str | Path,
    *,
    error_prefix: str,
) -> None:
    try:
        manifest = _read_show_manifest(Path(path))
    except click.ClickException:
        return
    if not _manifest_has_paper_artifact_lifecycle_surface(manifest):
        return
    validation = validate_paper_artifact_lifecycle_manifest(
        manifest,
        run_artifacts_doc_text=_show_run_artifacts_doc_text(),
    )
    if validation["ok"]:
        return
    issue = validation["issues"][0]
    raise click.ClickException(
        f"{error_prefix}: paper artifact lifecycle validation failed: "
        f"{issue['code']}: {issue['message']}"
    )


def _manifest_has_paper_artifact_lifecycle_surface(manifest: dict) -> bool:
    artifact_schema = manifest.get("artifact_schema")
    if (
        not isinstance(artifact_schema, dict)
        or "paper_artifact_subpaths" not in artifact_schema
    ):
        return False
    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        return False
    history = runtime.get("history")
    if not isinstance(history, dict):
        return False
    return any(
        key in history
        for key in (
            "marker_spelling_provenance_report",
            "alphaevolve_process_exhibit_report",
            "alphaevolve_table1_capability_exhibit_report",
        )
    )


def _has_archive_metadata(record: dict) -> bool:
    return isinstance(record.get("metadata"), dict) and "archive_admission" in record["metadata"]


def _raise_mixed_history_schema(
    line_number: int, first_legacy_line: int, first_modern_line: int
) -> None:
    raise click.ClickException(
        "Malformed history.jsonl at line "
        f"{line_number}: mixed legacy/current history schemas "
        f"(first legacy row line {first_legacy_line}, "
        f"first archive_admission row line {first_modern_line})"
    )


def _iter_history_records(path: Path, *, archive_cell_upper_bound: int | None = None):
    try:
        handle = path.open("rb")
    except OSError as exc:
        raise click.ClickException(f"Failed to read history.jsonl: {exc}") from exc
    seen_ids: dict[str, int] = {}
    with handle:
        for line_number, raw_line in enumerate(handle, start=1):
            try:
                line = raw_line.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise click.ClickException(
                    "Malformed history.jsonl at line "
                    f"{line_number}: invalid UTF-8 ({exc.reason})"
                ) from exc
            if not line.strip():
                continue
            try:
                record = json.loads(
                    line,
                    object_pairs_hook=_reject_duplicate_history_json_names,
                )
            except _DuplicateHistoryJsonNameError as exc:
                raise click.ClickException(
                    f"Malformed history.jsonl at line {line_number}: {exc}"
                ) from exc
            except json.JSONDecodeError as exc:
                raise click.ClickException(
                    f"Malformed history.jsonl at line {line_number}: {exc.msg}"
                ) from exc
            if not isinstance(record, dict):
                raise click.ClickException(
                    f"Malformed history.jsonl at line {line_number}: expected JSON object"
                )
            _validate_history_fitness(record, line_number)
            _validate_history_generation(record, line_number)
            _validate_history_identity(record, line_number, seen_ids)
            _validate_history_metrics(record, line_number)
            _validate_history_display_payload(record, line_number)
            if _has_archive_metadata(record):
                _validate_current_history_record(
                    record,
                    line_number,
                    archive_cell_upper_bound=archive_cell_upper_bound,
                )
            yield line_number, record


class _DuplicateHistoryJsonNameError(ValueError):
    pass


def _reject_duplicate_history_json_names(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateHistoryJsonNameError(
                f"duplicate JSON object name {key!r}"
            )
        result[key] = value
    return result


def _validate_history_fitness(record: dict, line_number: int) -> None:
    fitness = record.get("fitness")
    if (
        isinstance(fitness, bool)
        or not isinstance(fitness, (int, float))
        or not math.isfinite(float(fitness))
    ):
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: fitness must be a finite number"
        )


def _validate_history_generation(record: dict, line_number: int) -> None:
    generation = record.get("generation")
    if isinstance(generation, bool) or not isinstance(generation, int) or generation < 0:
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: generation must be a non-negative integer"
        )


def _validate_history_identity(
    record: dict, line_number: int, seen_ids: dict[str, int]
) -> None:
    try:
        validate_program_identity(record.get("id"), record.get("parent_id"), record.get("lineage"))
    except ValueError as exc:
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: {exc}"
        ) from exc
    program_id = record["id"]
    if program_id in seen_ids:
        raise click.ClickException(
            "Malformed history.jsonl at line "
            f"{line_number}: duplicate program id {program_id!r} "
            f"(first seen at line {seen_ids[program_id]})"
        )
    seen_ids[program_id] = line_number


def _validate_history_metrics(record: dict, line_number: int) -> None:
    metrics = record.get("metrics")
    if metrics is None:
        return
    if not isinstance(metrics, dict):
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: metrics must be an object"
        )
    try:
        record["metrics"] = validate_program_metrics(metrics)
    except ValueError as exc:
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: {exc}"
        ) from exc


def _validate_history_display_payload(record: dict, line_number: int) -> None:
    _history_record_workspace(record, line_number)


def _validate_current_history_record(
    record: dict,
    line_number: int,
    *,
    archive_cell_upper_bound: int | None = None,
) -> None:
    metadata = record.get("metadata")
    assert isinstance(metadata, dict)
    admission = metadata.get("archive_admission")
    if not isinstance(admission, dict):
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: archive_admission must be an object"
        )
    _validate_archive_admission_program_id(record, admission, line_number)
    evaluation = record.get("evaluation")
    if evaluation is not None and not isinstance(evaluation, dict):
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: evaluation must be an object"
        )
    if isinstance(evaluation, dict) and "is_valid" in evaluation and not isinstance(
        evaluation["is_valid"], bool
    ):
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: evaluation.is_valid must be a boolean"
        )
    admitted = _archive_bool(admission, "admitted", line_number)
    cell_admitted = _archive_bool(
        admission,
        "cell_admitted",
        line_number,
        fallback=admission.get("entered_cell"),
    )
    elite_retained = _archive_bool(
        admission,
        "elite_retained",
        line_number,
        fallback=admission.get("entered_elite"),
    )
    search_state_changed = _archive_bool(
        admission,
        "search_state_changed",
        line_number,
    )
    sampling_eligible = _archive_bool(
        admission,
        "sampling_eligible",
        line_number,
    )
    flags = [
        cell_admitted,
        elite_retained,
        search_state_changed,
        sampling_eligible,
    ]
    if admitted is True and any(flag is not None for flag in flags) and not any(
        flag is True for flag in flags
    ):
        raise click.ClickException(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.admitted is true but no "
            "retention/search-state flag is true"
        )
    _archive_summary(
        record,
        line_number,
        archive_cell_upper_bound=archive_cell_upper_bound,
    )


def _validate_archive_admission_program_id(
    record: dict, admission: dict, line_number: int
) -> None:
    admission_program_id = admission.get("program_id")
    if admission_program_id is None:
        return
    try:
        validate_program_identity(admission_program_id)
    except ValueError as exc:
        raise click.ClickException(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.program_id must be a "
            "manifest-safe identifier"
        ) from exc
    if admission_program_id != record["id"]:
        raise click.ClickException(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.program_id must match history row id"
        )


def _validate_display_record(record: dict, line_number: int) -> None:
    program_id = record.get("id")
    if not isinstance(program_id, str) or not program_id:
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: id must be a non-empty string"
        )
    generation = record.get("generation")
    if isinstance(generation, bool) or not isinstance(generation, int) or generation < 0:
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: generation must be a non-negative integer"
        )
    metrics = record.get("metrics")
    if metrics is not None and not isinstance(metrics, dict):
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: metrics must be an object"
        )


def _history_record_workspace(record: dict, line_number: int) -> tuple[str, dict[str, str]] | None:
    files = record.get("files")
    if files is None:
        code = record.get("code")
        if not isinstance(code, str):
            raise click.ClickException(
                f"Malformed history.jsonl at line {line_number}: code must be a string"
            )
        return None
    if not isinstance(files, dict):
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: files must be an object"
        )
    primary_file = record.get("primary_file", "main.py")
    if not isinstance(primary_file, str):
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: primary_file must be a string"
        )
    if primary_file not in files:
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: primary_file missing from files"
        )
    normalized: dict[str, str] = {}
    for path, content in files.items():
        if not isinstance(path, str) or not isinstance(content, str):
            raise click.ClickException(
                f"Malformed history.jsonl at line {line_number}: files must map strings to strings"
            )
        normalized[path] = content
    path_policy = record.get("workspace_path_policy")
    allowed_reserved_paths = []
    if isinstance(path_policy, dict):
        raw_allowed = path_policy.get("allowed_reserved_paths", [])
        if isinstance(raw_allowed, list) and all(isinstance(item, str) for item in raw_allowed):
            allowed_reserved_paths = raw_allowed
    try:
        workspace = CandidateWorkspace(
            normalized,
            primary_file,
            allowed_reserved_paths=frozenset(allowed_reserved_paths),
        )
    except ValueError as exc:
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: {exc}"
        ) from exc
    return workspace.primary_file, dict(workspace.files)


def _select_better_record(current, candidate, key):
    if current is None or key(candidate) > key(current):
        return candidate
    return current


def _is_archive_admitted_valid(record: dict) -> bool:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    admission = metadata.get("archive_admission") if isinstance(metadata, dict) else None
    evaluation = record.get("evaluation") if isinstance(record.get("evaluation"), dict) else {}
    return (
        isinstance(admission, dict)
        and admission.get("admitted") is True
        and evaluation.get("is_valid") is True
    )


def _record_selection_key(record: dict) -> tuple[float, float]:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    admission = metadata.get("archive_admission") if isinstance(metadata, dict) else {}
    raw = None
    if isinstance(admission, dict):
        raw = admission.get("selection_score")
    if not isinstance(raw, (int, float)) or isinstance(raw, bool):
        raw = metadata.get("selection_score") if isinstance(metadata, dict) else None
    selection_score = (
        float(raw)
        if isinstance(raw, (int, float)) and not isinstance(raw, bool) and math.isfinite(float(raw))
        else None
    )
    if selection_score is None:
        selection_score = float(record.get("fitness", float("-inf")))
    return (selection_score, float(record.get("fitness", float("-inf"))))


def _archive_summary(
    record: dict,
    line_number: int,
    *,
    archive_cell_upper_bound: int | None = None,
) -> str | None:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    admission = metadata.get("archive_admission") if isinstance(metadata, dict) else None
    if not isinstance(admission, dict):
        return None
    parts = []
    raw_selection_score = admission.get("selection_score")
    if raw_selection_score is not None and (
        isinstance(raw_selection_score, bool)
        or not isinstance(raw_selection_score, (int, float))
        or not math.isfinite(float(raw_selection_score))
    ):
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: archive_admission.selection_score must be a finite number"
        )
    if (
        isinstance(raw_selection_score, (int, float))
        and not isinstance(raw_selection_score, bool)
        and math.isfinite(float(raw_selection_score))
    ):
        parts.append(f"selection_score={float(raw_selection_score):.6f}")
    cell_admitted = _archive_bool(
        admission,
        "cell_admitted",
        line_number,
        fallback=admission.get("entered_cell"),
    )
    if cell_admitted is not None:
        parts.append(f"cell_admitted={cell_admitted}")
    elite_retained = _archive_bool(
        admission,
        "elite_retained",
        line_number,
        fallback=admission.get("entered_elite"),
    )
    if elite_retained is not None:
        parts.append(f"elite_retained={elite_retained}")
    search_state_changed = _archive_bool(
        admission,
        "search_state_changed",
        line_number,
        fallback=admission.get("admitted"),
    )
    if search_state_changed is not None:
        parts.append(f"search_state_changed={search_state_changed}")
    sampling_eligible = _archive_bool(
        admission,
        "sampling_eligible",
        line_number,
        fallback=admission.get("entered_cell"),
    )
    if sampling_eligible is not None:
        parts.append(f"sampling_eligible={sampling_eligible}")
    island_id = admission.get("island_id")
    if island_id is not None:
        if isinstance(island_id, bool) or not isinstance(island_id, int) or island_id < 0:
            raise click.ClickException(
                f"Malformed history.jsonl at line {line_number}: archive_admission.island_id must be a non-negative integer"
            )
        parts.append(f"island={island_id}")
    cell = admission.get("cell")
    if cell is not None:
        if (
            not isinstance(cell, list)
            or len(cell) != 3
            or any(
                isinstance(value, bool) or not isinstance(value, int) or value < 0
                for value in cell
            )
        ):
            raise click.ClickException(
                f"Malformed history.jsonl at line {line_number}: archive_admission.cell must be a list of three non-negative integers"
            )
        if archive_cell_upper_bound is not None and any(
            value >= archive_cell_upper_bound for value in cell
        ):
            raise click.ClickException(
                "Malformed history.jsonl at line "
                f"{line_number}: archive_admission.cell values must be less "
                "than manifest config.map_elites_bins "
                f"({archive_cell_upper_bound})"
            )
        parts.append(f"cell={cell}")
    descriptors = _validate_archive_descriptors(
        admission.get("descriptors"), line_number
    )
    if descriptors:
        parts.extend(_archive_descriptor_parts(descriptors))
    parts.extend(
        _archive_objective_vector_parts(
            admission.get("objective_vector"),
            line_number,
        )
    )
    return f"Archive:        {'; '.join(parts)}" if parts else None


def _archive_objective_vector_parts(value: object, line_number: int) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, dict):
        raise click.ClickException(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.objective_vector must be an object or null"
        )
    allowed = {"policy", "normalized_metrics", "selection_policy"}
    unsupported = sorted(set(value) - allowed)
    if unsupported:
        raise click.ClickException(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.objective_vector has unsupported fields: {unsupported}"
        )
    if value.get("policy") != "normalized_declared_metric_vector_v1":
        raise click.ClickException(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.objective_vector.policy is unsupported"
        )
    raw_metrics = value.get("normalized_metrics")
    if not isinstance(raw_metrics, dict):
        raise click.ClickException(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.objective_vector.normalized_metrics must be an object"
        )
    metrics: dict[str, float] = {}
    for name, score in raw_metrics.items():
        try:
            validate_program_metrics({name: 0.0})
        except ValueError as exc:
            raise click.ClickException(
                "Malformed history.jsonl at line "
                f"{line_number}: archive_admission.objective_vector metric names must be manifest-safe metric names"
            ) from exc
        if (
            isinstance(score, bool)
            or not isinstance(score, (int, float))
            or not math.isfinite(float(score))
            or not 0.0 <= float(score) <= 1.0
        ):
            raise click.ClickException(
                "Malformed history.jsonl at line "
                f"{line_number}: archive_admission.objective_vector metric values must be finite normalized scores"
            )
        metrics[name] = float(score)
    selection_policy = value.get("selection_policy")
    if selection_policy is not None and not isinstance(selection_policy, dict):
        raise click.ClickException(
            "Malformed history.jsonl at line "
            f"{line_number}: archive_admission.objective_vector.selection_policy must be an object"
        )
    parts = _objective_metric_vector_parts(metrics)
    if isinstance(selection_policy, dict):
        policy_type = selection_policy.get("type")
        if policy_type is not None:
            if not _is_manifest_runtime_label(policy_type):
                raise click.ClickException(
                    "Malformed history.jsonl at line "
                    f"{line_number}: archive_admission.objective_vector.selection_policy.type must be a manifest-safe label"
                )
            parts.append(f"objective_policy={policy_type}")
    return parts


def _objective_metric_vector_parts(metrics: dict[str, float]) -> list[str]:
    rendered = json.dumps(metrics, sort_keys=True, allow_nan=False)
    if (
        len(metrics) <= _ARCHIVE_DESCRIPTOR_PREVIEW_LIMIT
        and len(rendered) <= _ARCHIVE_DESCRIPTOR_JSON_DISPLAY_LIMIT
        and all(
            len(name) <= _ARCHIVE_DESCRIPTOR_LABEL_DISPLAY_LIMIT
            for name in metrics
        )
    ):
        return [f"objective_metrics={rendered}"]
    canonical = json.dumps(
        metrics,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    preview = {
        _descriptor_preview_label(name): value
        for name, value in sorted(metrics.items())[:_ARCHIVE_DESCRIPTOR_PREVIEW_LIMIT]
    }
    omitted = max(0, len(metrics) - len(preview))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return [
        f"objective_metrics_count={len(metrics)}",
        f"objective_metrics_preview={json.dumps(preview, sort_keys=True, allow_nan=False)}",
        f"objective_metrics_omitted={omitted}",
        f"objective_metrics_sha256={digest}",
    ]


def _validate_archive_descriptors(
    descriptors: object, line_number: int
) -> dict[str, int | float] | None:
    if descriptors is None:
        return None
    if not isinstance(descriptors, dict):
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: archive_admission.descriptors must map strings to finite numbers"
        )
    normalized: dict[str, int | float] = {}
    for name, value in descriptors.items():
        try:
            validate_program_metrics({name: 0.0})
        except ValueError as exc:
            raise click.ClickException(
                "Malformed history.jsonl at line "
                f"{line_number}: archive_admission.descriptor names must be "
                "manifest-safe metric names"
            ) from exc
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
        ):
            raise click.ClickException(
                f"Malformed history.jsonl at line {line_number}: archive_admission.descriptors must map strings to finite numbers"
            )
        normalized[name] = value
    return normalized


def _archive_descriptor_parts(descriptors: dict[str, int | float]) -> list[str]:
    rendered = json.dumps(descriptors, sort_keys=True, allow_nan=False)
    if (
        len(descriptors) <= _ARCHIVE_DESCRIPTOR_PREVIEW_LIMIT
        and len(rendered) <= _ARCHIVE_DESCRIPTOR_JSON_DISPLAY_LIMIT
        and all(
            len(name) <= _ARCHIVE_DESCRIPTOR_LABEL_DISPLAY_LIMIT
            for name in descriptors
        )
    ):
        return [f"descriptors={rendered}"]
    canonical = json.dumps(
        descriptors,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    preview = {
        _descriptor_preview_label(name): value
        for name, value in sorted(descriptors.items())[
            :_ARCHIVE_DESCRIPTOR_PREVIEW_LIMIT
        ]
    }
    omitted = max(0, len(descriptors) - len(preview))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return [
        f"descriptors_count={len(descriptors)}",
        f"descriptors_preview={json.dumps(preview, sort_keys=True, allow_nan=False)}",
        f"descriptors_omitted={omitted}",
        f"descriptors_sha256={digest}",
    ]


def _descriptor_preview_label(name: str) -> str:
    if len(name) <= _ARCHIVE_DESCRIPTOR_LABEL_DISPLAY_LIMIT:
        return name
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]
    prefix_len = _ARCHIVE_DESCRIPTOR_LABEL_DISPLAY_LIMIT - len(digest) - 4
    return f"{name[:prefix_len]}...{digest}"


def _archive_bool(
    admission: dict, field: str, line_number: int, *, fallback: object = None
) -> bool | None:
    raw = admission.get(field, fallback)
    if raw is None:
        return None
    if not isinstance(raw, bool):
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: archive_admission.{field} must be a boolean"
        )
    return raw


def _lineage_summary(record: dict) -> str | None:
    parent_id = record.get("parent_id")
    lineage = record.get("lineage")
    if parent_id is None and lineage is None:
        return None
    parts = [f"parent={parent_id if parent_id is not None else '<root>'}"]
    if isinstance(lineage, list):
        parts.append(f"lineage_depth={len(lineage)}")
        if lineage:
            tail = lineage[-3:]
            prefix = "..." if len(lineage) > len(tail) else ""
            parts.append(f"lineage_tail={prefix}{'->'.join(tail)}")
    return f"Lineage:       {'; '.join(parts)}"


def _prompt_summary(record: dict, line_number: int) -> str | None:
    metadata = record.get("metadata")
    if not isinstance(metadata, dict):
        return None
    parts: list[str] = []
    prompt_program_id = metadata.get("prompt_program_id")
    if prompt_program_id is not None:
        try:
            validate_program_identity(prompt_program_id)
        except ValueError as exc:
            raise click.ClickException(
                f"Malformed history.jsonl at line {line_number}: prompt_program_id must be a manifest-safe identifier"
            ) from exc
        parts.append(f"prompt_program_id={prompt_program_id}")
    parent_selection = metadata.get("parent_selection")
    if parent_selection is not None:
        if not isinstance(parent_selection, dict):
            raise click.ClickException(
                f"Malformed history.jsonl at line {line_number}: parent_selection must be an object"
            )
        strategy = parent_selection.get("strategy")
        if strategy is not None:
            if not _is_manifest_runtime_label(strategy):
                raise click.ClickException(
                    f"Malformed history.jsonl at line {line_number}: parent_selection.strategy must be a manifest-safe label"
                )
            parts.append(f"parent_strategy={strategy}")
        selected = parent_selection.get("selected_program_id")
        if selected is not None:
            try:
                validate_program_identity(selected)
            except ValueError as exc:
                raise click.ClickException(
                    f"Malformed history.jsonl at line {line_number}: parent_selection.selected_program_id must be a manifest-safe identifier"
                ) from exc
            parts.append(f"selected_parent={selected}")
        target_metric = parent_selection.get("target_metric")
        if target_metric is not None:
            try:
                validate_program_metrics({target_metric: 0.0})
            except ValueError as exc:
                raise click.ClickException(
                    f"Malformed history.jsonl at line {line_number}: parent_selection.target_metric must be a manifest-safe metric name"
                ) from exc
            parts.append(f"target_metric={target_metric}")
    return f"Prompt:        {'; '.join(parts)}" if parts else None


def _evaluation_diagnostics_summary(record: dict, line_number: int) -> str | None:
    evaluation = record.get("evaluation")
    if not isinstance(evaluation, dict):
        return None
    parts: list[str] = []
    if "is_valid" in evaluation:
        parts.append(f"is_valid={evaluation['is_valid']}")
    stages = evaluation.get("stages")
    if stages is not None:
        if not isinstance(stages, list):
            raise click.ClickException(
                f"Malformed history.jsonl at line {line_number}: evaluation.stages must be a list"
            )
        failed = []
        for index, stage in enumerate(stages):
            if not isinstance(stage, dict):
                raise click.ClickException(
                    f"Malformed history.jsonl at line {line_number}: evaluation.stages[{index}] must be an object"
                )
            passed = stage.get("passed")
            if passed is not None and not isinstance(passed, bool):
                raise click.ClickException(
                    f"Malformed history.jsonl at line {line_number}: evaluation.stages[{index}].passed must be a boolean"
                )
            if passed is False:
                failed.append(_stage_failure_label(stage, index))
        parts.append(f"stages={len(stages)}")
        parts.append(f"failed={len(failed)}")
        if failed:
            parts.append(
                "failed_stages="
                + ",".join(failed[:_SHOW_DIAGNOSTIC_BUCKET_LIMIT])
            )
    accounting = evaluation.get("accounting")
    if accounting is not None:
        if not isinstance(accounting, dict):
            raise click.ClickException(
                f"Malformed history.jsonl at line {line_number}: evaluation.accounting must be an object"
            )
        for key in (
            "configured_stage_samples",
            "subprocess_attempts",
            "retry_attempts",
            "timeout_count",
            "sample_budget_exhaustions",
            "stage_budget_exhaustions",
        ):
            value = accounting.get(key)
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise click.ClickException(
                    f"Malformed history.jsonl at line {line_number}: evaluation.accounting.{key} must be a non-negative integer"
                )
            parts.append(f"{key}={value}")
    return f"Evaluation:    {'; '.join(parts)}" if parts else None


def _stage_failure_label(stage: dict, index: int) -> str:
    name = stage.get("name")
    if not isinstance(name, str) or not name:
        name = f"stage_{index}"
    error = stage.get("error")
    if isinstance(error, str) and error:
        return (
            f"{_diagnostic_label(name)}:{_diagnostic_label(error)}"
        )
    return _diagnostic_label(name)


def _feedback_summary(record: dict, line_number: int) -> str | None:
    evaluation = record.get("evaluation")
    if not isinstance(evaluation, dict):
        return None
    metadata = evaluation.get("metadata")
    if not isinstance(metadata, dict):
        return None
    feedback = metadata.get("llm_feedback")
    if feedback is None:
        return None
    if not isinstance(feedback, list):
        raise click.ClickException(
            f"Malformed history.jsonl at line {line_number}: evaluation.metadata.llm_feedback must be a list"
        )
    applied: list[str] = []
    failed: list[str] = []
    weighted_delta = 0.0
    for index, item in enumerate(feedback):
        if not isinstance(item, dict):
            raise click.ClickException(
                f"Malformed history.jsonl at line {line_number}: evaluation.metadata.llm_feedback[{index}] must be an object"
            )
        name = _diagnostic_label(str(item.get("name", f"feedback_{index}")))
        error = item.get("error")
        if isinstance(error, str) and error:
            failed.append(f"{name}:{_diagnostic_label(error)}")
        else:
            applied.append(name)
        delta = item.get("weighted_delta")
        if isinstance(delta, (int, float)) and not isinstance(delta, bool) and math.isfinite(float(delta)):
            weighted_delta += float(delta)
    parts = [f"llm_feedback={len(feedback)}"]
    if applied:
        parts.append(
            "applied=" + ",".join(applied[:_SHOW_DIAGNOSTIC_BUCKET_LIMIT])
        )
    if failed:
        parts.append(
            "failed=" + ",".join(failed[:_SHOW_DIAGNOSTIC_BUCKET_LIMIT])
        )
    if weighted_delta:
        parts.append(f"weighted_delta={weighted_delta:.6f}")
    return f"Feedback:      {'; '.join(parts)}"


def _failure_statistics_summary(run_dir: Path) -> str | None:
    failure_path = run_dir / "failure_history.jsonl"
    if not failure_path.exists():
        return None
    try:
        from libreevolve.core.database import (
            HistoryRestoreError,
            load_failure_history_records,
        )

        records = load_failure_history_records(failure_path)
    except HistoryRestoreError as exc:
        raise click.ClickException(str(exc)) from exc
    admission_reasons: dict[str, int] = {}
    errors: dict[str, int] = {}
    repeated_records = 0
    for record in records:
        _increment_bucket(admission_reasons, record.get("admission_reason"))
        _increment_bucket(errors, record.get("error"))
        repetition_count = record.get("repetition_count")
        if (
            isinstance(repetition_count, int)
            and not isinstance(repetition_count, bool)
            and repetition_count > 1
        ):
            repeated_records += 1
    parts = [f"total={len(records)}"]
    rendered_admission = _render_count_buckets(admission_reasons)
    if rendered_admission:
        parts.append(f"admission_reasons={rendered_admission}")
    rendered_errors = _render_count_buckets(errors)
    if rendered_errors:
        parts.append(f"errors={rendered_errors}")
    if repeated_records:
        parts.append(f"repeated_records={repeated_records}")
    return f"Failures:      {'; '.join(parts)}"


def _increment_bucket(buckets: dict[str, int], value: object) -> None:
    if not isinstance(value, str) or not value:
        value = "<none>"
    buckets[_diagnostic_label(value)] = buckets.get(_diagnostic_label(value), 0) + 1


def _render_count_buckets(buckets: dict[str, int]) -> str:
    if not buckets:
        return ""
    items = sorted(buckets.items(), key=lambda item: (-item[1], item[0]))
    rendered = ",".join(
        f"{label}:{count}" for label, count in items[:_SHOW_DIAGNOSTIC_BUCKET_LIMIT]
    )
    omitted = len(items) - _SHOW_DIAGNOSTIC_BUCKET_LIMIT
    if omitted > 0:
        rendered += f",+{omitted}_more"
    return rendered


def _diagnostic_label(value: str) -> str:
    safe = redact_sensitive_text(value).strip()
    safe = re.sub(r"\s+", "_", safe)
    if not safe:
        safe = "<empty>"
    if len(safe) <= _SHOW_DIAGNOSTIC_LABEL_DISPLAY_LIMIT:
        return safe
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]
    keep = _SHOW_DIAGNOSTIC_LABEL_DISPLAY_LIMIT - len(digest) - 4
    return f"{safe[:keep]}...{digest}"


def _show_source_text(
    source: str,
    *,
    path: str | None = None,
    display_limit: int | None = _SHOW_SOURCE_DISPLAY_LIMIT,
    redact: bool = False,
) -> str:
    rendered = redact_sensitive_text(source) if redact else source
    if display_limit is None or len(rendered) <= display_limit:
        return rendered
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
    omitted = len(rendered) - display_limit
    label = f" for {path}" if path is not None else ""
    redacted_line = "\nsource_redacted=True" if redact and rendered != source else ""
    notice = (
        "\n\n--- libreevolve show source truncated ---\n"
        f"source_truncated=True{label}{redacted_line}\n"
        f"source_chars={len(source)}\n"
        f"rendered_chars={len(rendered)}\n"
        f"displayed_chars={display_limit}\n"
        f"omitted_chars={omitted}\n"
        f"source_sha256={digest}\n"
        "full_source=history.jsonl"
    )
    return rendered[:display_limit] + notice


def _write_best_artifacts(program, run_dir: Path) -> tuple[Path, Path]:
    run_dir.mkdir(parents=True, exist_ok=True)
    best_py = run_dir / "best.py"
    workspace_dir = run_dir / "best_workspace"

    suffix = uuid4().hex
    tmp_py = run_dir / f".best-{suffix}.py.tmp"
    tmp_workspace = run_dir / f".best_workspace-{suffix}.tmp"
    backup_py = run_dir / f".best-{suffix}.py.bak"
    backup_workspace = run_dir / f".best_workspace-{suffix}.bak"
    installed_py = False
    installed_workspace = False
    _preflight_best_artifact_export_paths(
        run_dir=run_dir,
        paths=(best_py, workspace_dir, tmp_py, tmp_workspace, backup_py, backup_workspace),
    )

    try:
        tmp_py.write_text(program.code, encoding="utf-8")
        workspace = program.workspace()
        workspace.materialize(tmp_workspace)
        _write_static_workspace_manifest(workspace, tmp_workspace)

        if best_py.exists():
            best_py.replace(backup_py)
        if workspace_dir.exists():
            workspace_dir.replace(backup_workspace)

        tmp_workspace.replace(workspace_dir)
        installed_workspace = True
        tmp_py.replace(best_py)
        installed_py = True
    except Exception as exc:
        rollback = _rollback_best_artifact_export(
            best_py=best_py,
            workspace_dir=workspace_dir,
            backup_py=backup_py,
            backup_workspace=backup_workspace,
            installed_py=installed_py,
            installed_workspace=installed_workspace,
            run_dir=run_dir,
        )
        cleanup_errors = _cleanup_best_artifact_export_paths(
            (tmp_py, tmp_workspace, backup_py, backup_workspace),
            run_dir=run_dir,
            preserve_paths=rollback["preserve_paths"],
        )
        raise BestArtifactExportError(
            exc,
            rollback_errors=rollback["errors"],
            cleanup_errors=cleanup_errors,
            preserved_paths=rollback["preserved_paths"],
        ) from exc
    cleanup_errors = _cleanup_best_artifact_export_paths(
        (tmp_py, tmp_workspace, backup_py, backup_workspace),
        run_dir=run_dir,
        preserve_paths=(),
    )
    if cleanup_errors:
        raise BestArtifactExportError(
            cleanup_errors[0]["exception"],
            rollback_errors=(),
            cleanup_errors=cleanup_errors,
            preserved_paths=(),
        )
    return best_py, workspace_dir


def _write_static_workspace_manifest(workspace, root: Path) -> None:
    if not workspace.static_files:
        return
    strict_json_dump(
        {
            "schema": "libreevolve.static_workspace_files.v1",
            "note": (
                "Static files are immutable candidate members tracked by metadata; "
                "encoded static member bytes are materialized when present."
            ),
            "static_files": [_static_workspace_manifest_record(item) for item in workspace.static_files],
        },
        root / STATIC_WORKSPACE_MANIFEST_NAME,
        indent=2,
    )


def _static_workspace_manifest_record(record: dict) -> dict:
    return {key: value for key, value in record.items() if key != "content_b64"}


def _preflight_best_artifact_export_paths(
    *, run_dir: Path, paths: tuple[Path, ...]
) -> None:
    resolved_run_dir = run_dir.resolve(strict=False)
    for path in paths:
        if _path_is_present_or_link(path) and _path_is_link_like(path):
            raise OSError(
                "refusing to replace linked best artifact path "
                f"{_run_relative_path_label(path, run_dir)}"
            )
        resolved_path = path.resolve(strict=False)
        try:
            resolved_path.relative_to(resolved_run_dir)
        except ValueError as exc:
            raise OSError(
                "refusing best artifact path outside run directory "
                f"{_run_relative_path_label(path, run_dir)}"
            ) from exc


def _path_is_present_or_link(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _path_is_link_like(path: Path) -> bool:
    return path.is_symlink() or _path_is_junction(path)


def _record_best_artifact_export_success(
    run_dir: Path, best_py: Path, best_workspace: Path
) -> None:
    _update_best_artifact_export_manifest(
        run_dir,
        {
            "status": "completed",
            "paths": {
                "best.py": _best_artifact_path_record(best_py, run_dir),
                "best_workspace": _best_artifact_path_record(best_workspace, run_dir),
            },
        },
    )


def _record_best_artifact_export_failure(run_dir: Path, exc: BaseException) -> None:
    record = {
        "status": "failed",
        "error_type": exc.__class__.__name__,
        "error": _bounded_redacted_cli_text(str(exc)),
        "paths": {
            "best.py": _best_artifact_path_record(run_dir / "best.py", run_dir),
            "best_workspace": _best_artifact_path_record(
                run_dir / "best_workspace", run_dir
            ),
        },
    }
    if isinstance(exc, BestArtifactExportError):
        record.update(exc.to_manifest_record())
    _update_best_artifact_export_manifest(run_dir, record)


def _update_best_artifact_export_manifest(run_dir: Path, record: dict) -> None:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(manifest, dict):
        return
    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        return
    runtime["best_artifact_export"] = record
    artifacts = runtime.get("artifacts")
    if isinstance(artifacts, dict):
        artifacts["best.py"] = record["paths"]["best.py"]
        artifacts["best_workspace"] = record["paths"]["best_workspace"]
    strict_json_dump(manifest, manifest_path, indent=2)


def _best_artifact_path_record(path: Path, run_dir: Path) -> dict:
    is_symlink = path.is_symlink()
    is_junction = _path_is_junction(path)
    exists = path.exists()
    present = exists or is_symlink
    record = {
        "path": _run_relative_path_label(path, run_dir),
        "exists": exists,
        "present": present,
        "is_symlink": is_symlink,
        "is_junction": is_junction,
    }
    if is_symlink or is_junction:
        record["kind"] = "link"
        return record
    if path.is_dir():
        record["kind"] = "directory"
        record.update(_best_workspace_tree_record(path))
        return record
    if path.is_file():
        record["kind"] = "file"
        try:
            raw = path.read_bytes()
        except OSError as exc:
            record["inspection_error_type"] = exc.__class__.__name__
            record["inspection_error"] = _bounded_redacted_cli_text(str(exc))
            return record
        record["bytes"] = len(raw)
        record["sha256"] = hashlib.sha256(raw).hexdigest()
        return record
    record["kind"] = "missing"
    return record


def _best_workspace_tree_record(path: Path) -> dict:
    digest = hashlib.sha256()
    file_count = 0
    try:
        entries = sorted(path.rglob("*"), key=lambda item: item.as_posix())
    except OSError as exc:
        return {
            "tree_hash_status": "listing_error",
            "inspection_error_type": exc.__class__.__name__,
            "inspection_error": _bounded_redacted_cli_text(str(exc)),
        }
    for entry in entries:
        if entry.is_symlink() or _path_is_junction(entry):
            continue
        if not entry.is_file():
            continue
        try:
            rel = entry.relative_to(path).as_posix()
            raw = entry.read_bytes()
        except OSError as exc:
            return {
                "tree_hash_status": "read_error",
                "inspection_error_type": exc.__class__.__name__,
                "inspection_error": _bounded_redacted_cli_text(str(exc)),
            }
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(raw).hexdigest().encode("ascii"))
        digest.update(b"\0")
        file_count += 1
    return {
        "tree_hash_status": "ok",
        "tree_hash": digest.hexdigest(),
        "tree_hash_scope": "best_workspace_file_paths_and_sha256",
        "file_count": file_count,
    }


def _run_relative_path_label(path: Path, run_dir: Path) -> str:
    try:
        return path.relative_to(run_dir).as_posix()
    except ValueError:
        return redact_sensitive_text(str(path))


def _path_is_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction()) if callable(is_junction) else False


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


def _materialize_missing_best_artifact_export(best, run_dir: Path) -> dict:
    try:
        best_py, best_workspace = _write_best_artifacts(best, run_dir)
    except Exception as exc:
        _record_best_artifact_export_failure(run_dir, exc)
        return _load_best_artifact_export_record(run_dir) or {
            "status": "failed",
            "error": _bounded_redacted_cli_text(str(exc)),
        }
    _record_best_artifact_export_success(run_dir, best_py, best_workspace)
    return _load_best_artifact_export_record(run_dir) or {"status": "completed"}


class BestArtifactExportError(OSError):
    def __init__(
        self,
        original: BaseException,
        *,
        rollback_errors,
        cleanup_errors,
        preserved_paths,
    ) -> None:
        self.original_error_type = original.__class__.__name__
        self.original_error = _bounded_redacted_cli_text(str(original))
        self.rollback_errors = _manifest_error_records(rollback_errors)
        self.cleanup_errors = _manifest_error_records(cleanup_errors)
        self.preserved_paths = tuple(preserved_paths)
        parts = [f"{self.original_error_type}: {self.original_error}"]
        if self.rollback_errors:
            parts.append(f"rollback_errors={len(self.rollback_errors)}")
        if self.cleanup_errors:
            parts.append(f"cleanup_errors={len(self.cleanup_errors)}")
        if self.preserved_paths:
            parts.append(f"preserved_backups={len(self.preserved_paths)}")
        super().__init__("; ".join(parts))

    def to_manifest_record(self) -> dict:
        record = {
            "original_error_type": self.original_error_type,
            "original_error": self.original_error,
        }
        if self.rollback_errors:
            record["rollback_errors"] = self.rollback_errors
        if self.cleanup_errors:
            record["cleanup_errors"] = self.cleanup_errors
        if self.preserved_paths:
            record["preserved_backups"] = list(self.preserved_paths)
        return record


def _manifest_error_records(errors) -> list[dict]:
    records = []
    for error in errors:
        record = {
            "stage": error["stage"],
            "path": error["path"],
            "error_type": error["exception"].__class__.__name__,
            "error": _bounded_redacted_cli_text(str(error["exception"])),
        }
        records.append(record)
    return records


def _best_artifact_operation_error(
    *, stage: str, path: Path, run_dir: Path, exc: BaseException
) -> dict:
    return {
        "stage": stage,
        "path": _run_relative_path_label(path, run_dir),
        "exception": exc,
    }


def _rollback_best_artifact_export(
    *,
    best_py: Path,
    workspace_dir: Path,
    backup_py: Path,
    backup_workspace: Path,
    installed_py: bool,
    installed_workspace: bool,
    run_dir: Path,
) -> dict:
    errors = []
    preserve_paths: list[Path] = []
    preserved_paths: list[str] = []
    if installed_py and best_py.exists():
        try:
            _remove_best_artifact_temp(best_py)
        except OSError as exc:
            errors.append(
                _best_artifact_operation_error(
                    stage="remove_installed_best.py",
                    path=best_py,
                    run_dir=run_dir,
                    exc=exc,
                )
            )
    if installed_workspace and workspace_dir.exists():
        try:
            _remove_best_artifact_temp(workspace_dir)
        except OSError as exc:
            errors.append(
                _best_artifact_operation_error(
                    stage="remove_installed_best_workspace",
                    path=workspace_dir,
                    run_dir=run_dir,
                    exc=exc,
                )
            )
    if backup_py.exists():
        try:
            backup_py.replace(best_py)
        except OSError as exc:
            errors.append(
                _best_artifact_operation_error(
                    stage="restore_best.py",
                    path=backup_py,
                    run_dir=run_dir,
                    exc=exc,
                )
            )
            preserve_paths.append(backup_py)
            preserved_paths.append(_run_relative_path_label(backup_py, run_dir))
    if backup_workspace.exists():
        try:
            backup_workspace.replace(workspace_dir)
        except OSError as exc:
            errors.append(
                _best_artifact_operation_error(
                    stage="restore_best_workspace",
                    path=backup_workspace,
                    run_dir=run_dir,
                    exc=exc,
                )
            )
            preserve_paths.append(backup_workspace)
            preserved_paths.append(_run_relative_path_label(backup_workspace, run_dir))
    return {
        "errors": errors,
        "preserve_paths": tuple(preserve_paths),
        "preserved_paths": tuple(preserved_paths),
    }


def _cleanup_best_artifact_export_paths(
    paths: tuple[Path, ...], *, run_dir: Path, preserve_paths
) -> list[dict]:
    preserved = set(preserve_paths)
    errors = []
    for path in paths:
        if path in preserved:
            continue
        try:
            _remove_best_artifact_temp(path)
        except OSError as exc:
            errors.append(
                _best_artifact_operation_error(
                    stage="cleanup", path=path, run_dir=run_dir, exc=exc
                )
            )
    return errors


def _remove_best_artifact_temp(path: Path) -> None:
    if _path_is_link_like(path):
        raise OSError(
            "refusing to remove linked best artifact path "
            f"{redact_sensitive_text(str(path))}"
        )
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()
