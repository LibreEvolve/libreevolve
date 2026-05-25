from __future__ import annotations
import dataclasses, json
from pathlib import Path
import shutil
import click
from dotenv import load_dotenv
from libreevolve.core.loop import evolve

load_dotenv(override=True)


@click.group()
def cli() -> None:
    """LibreEvolve -- LLM-guided evolutionary program discovery."""


@cli.command()
@click.argument("problem_dir", type=click.Path(exists=True, file_okay=False))
@click.option("--max-generations", "-g", type=int, default=None)
@click.option("--max-evaluations", type=int, default=None,
              help="Maximum number of validator evaluations, including seeds.")
@click.option("--max-evaluator-seconds", type=float, default=None,
              help="Maximum cumulative evaluator elapsed seconds.")
@click.option("--max-runtime-seconds", type=float, default=None,
              help="Maximum wall-clock seconds checked between evaluations.")
@click.option("--plugins",  "-p", multiple=True)
@click.option("--backends", "-b", multiple=True)
@click.option("--seed", type=int, default=None)
@click.option("--reasoning-effort", "-r", type=str, default=None,
              help="Reasoning effort for OpenAI reasoning models (e.g. low, medium, high, xhigh)")
@click.option("--explore-ratio", "-e", type=float, default=None,
              help="Probability of exploring (random parent) vs exploiting (best parent). Default: 0.3")
@click.option("--parent-selection-strategy",
              type=click.Choice(["mixed", "exploit", "explore", "metric", "novelty", "recency"]),
              default=None,
              help="Parent sampling policy. Default: mixed")
@click.option("--inspiration-strategy",
              type=click.Choice(["mixed", "random", "selection", "metric", "novelty", "recency"]),
              default=None,
              help="Inspiration sampling policy. Default: mixed")
@click.option("--mutation-mode", type=click.Choice(["diff", "full"]), default=None,
              help="Mutation response mode: SEARCH/REPLACE diffs or full code/block replacement.")
@click.option("--run-name", type=str, default=None,
              help="Custom name for this run (default: problem directory name)")
@click.option("--overwrite", is_flag=True,
              help="Delete existing run artifacts in the target run directory before starting.")
def run(problem_dir, max_generations, max_evaluations, max_evaluator_seconds,
        max_runtime_seconds, plugins, backends, seed, reasoning_effort,
        explore_ratio, parent_selection_strategy, inspiration_strategy,
        mutation_mode, run_name, overwrite):
    """Run evolution on a problem directory."""
    from libreevolve.core.config import ConfigError
    from libreevolve.problems.loader import load_problem
    problem = load_problem(problem_dir)
    if not problem.initial_programs:
        raise click.ClickException("No seed programs found.")
    try:
        config = _build_config(
            problem,
            max_generations,
            max_evaluations,
            max_evaluator_seconds,
            max_runtime_seconds,
            list(plugins),
            list(backends),
            seed,
            reasoning_effort,
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
        _prepare_run_dir_for_cli(config)
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc
    except FileExistsError as exc:
        raise click.ClickException(str(exc)) from exc
    active_plugins = _load_plugins(config.plugins)
    click.echo(f"Running {config.max_generations} generations on '{config.problem_name}'...")
    best = evolve(problem, config, active_plugins)
    if best is None:
        raise click.ClickException("Evolution produced no valid programs.")
    click.echo(f"\nBest fitness: {best.fitness:.6f}")
    run_dir = Path(config.log_dir) / config.problem_name
    best_py, best_workspace = _write_best_artifacts(best, run_dir)
    click.echo(f"Best program saved to: {best_py}")
    click.echo(f"Best workspace saved to: {best_workspace}")


@cli.command()
@click.argument("run_dir", type=click.Path(exists=True, file_okay=False))
def show(run_dir):
    """Inspect a previous run."""
    h = Path(run_dir) / "history.jsonl"
    if not h.exists():
        raise click.ClickException(f"No history.jsonl found in {run_dir}")
    records = [json.loads(l) for l in h.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not records:
        raise click.ClickException("history.jsonl is empty")
    has_archive_metadata = any(_has_archive_metadata(record) for record in records)
    if has_archive_metadata:
        eligible = [record for record in records if _is_archive_admitted_valid(record)]
        if not eligible:
            raise click.ClickException("No archive-admitted valid programs found")
        best = max(eligible, key=_record_selection_key)
        selection = "archive-admitted valid"
    else:
        best = max(records, key=lambda r: r["fitness"])
        selection = "legacy highest-fitness"
    click.echo(f"Total programs: {len(records)}")
    click.echo(f"Selection:      {selection}")
    click.echo(f"Best fitness:   {best['fitness']:.6f} (generation {best['generation']})")
    archive_summary = _archive_summary(best)
    if archive_summary:
        click.echo(archive_summary)
    if best.get("metrics"):
        click.echo(f"Metrics:        {json.dumps(best['metrics'], sort_keys=True)}")
    click.echo("\n--- Best program ---\n")
    click.echo(best["code"])


def _build_config(problem, max_generations, max_evaluations, max_evaluator_seconds,
                  max_runtime_seconds, plugins, backends, seed,
                  reasoning_effort=None, explore_ratio=None,
                  parent_selection_strategy=None, inspiration_strategy=None,
                  mutation_mode=None):
    import yaml
    from libreevolve.core.config import Config, ConfigError
    cfg: dict = {}
    cp = Path(problem.problem_dir) / "config.yaml"
    if cp.exists():
        try:
            loaded = yaml.safe_load(cp.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ConfigError(f"Failed to parse {cp}: {exc}") from exc
        if loaded is None:
            loaded = {}
        if not isinstance(loaded, dict):
            raise ConfigError(f"{cp} must contain a YAML mapping at the top level")
        cfg.update(loaded)
    valid = {f.name for f in dataclasses.fields(Config)}
    unknown = sorted(set(cfg) - valid)
    if unknown:
        raise ConfigError(f"Unknown config keys in {cp}: {unknown}")
    config = Config(**{k: v for k, v in cfg.items() if k in valid})
    if max_generations is not None: config.max_generations = max_generations
    if max_evaluations is not None: config.max_evaluations = max_evaluations
    if max_evaluator_seconds is not None: config.max_evaluator_seconds = max_evaluator_seconds
    if max_runtime_seconds is not None: config.max_runtime_seconds = max_runtime_seconds
    if plugins: config.plugins = list(plugins)
    if backends:
        bd = [{"type": t, "model": m} for b in backends for t, _, m in [b.partition(":")]]
        if reasoning_effort:
            for d in bd:
                if d.get("type") == "openai":
                    d["reasoning_effort"] = reasoning_effort
        config.backends = bd
    elif reasoning_effort:
        for backend in config.backends:
            if backend.get("type") == "openai":
                backend["reasoning_effort"] = reasoning_effort
    if seed is not None: config.seed = seed
    if explore_ratio is not None: config.explore_ratio = explore_ratio
    if parent_selection_strategy is not None:
        config.parent_selection_strategy = parent_selection_strategy
    if inspiration_strategy is not None:
        config.inspiration_strategy = inspiration_strategy
    if mutation_mode is not None: config.mutation_mode = mutation_mode
    config.problem_name = problem.name
    config.validate()
    return config


def _load_plugins(names: list[str]) -> list:
    if not names:
        return []
    from libreevolve.plugins import causal, deep_research, modular, ttt_rl
    reg = {"causal": causal.CausalPlugin, "deep_research": deep_research.DeepResearchPlugin,
           "modular": modular.ModularPlugin, "ttt_rl": ttt_rl.TTTRLPlugin}
    result = []
    for n in names:
        if n not in reg:
            raise click.ClickException(f"Unknown plugin: {n!r}. Available: {list(reg)}")
        result.append(reg[n]())
    return result


def _prepare_run_dir_for_cli(config) -> None:
    from libreevolve.core.database import prepare_run_directory

    prepare_run_directory(Path(config.log_dir) / config.problem_name, config.run_collision_policy)


def _has_archive_metadata(record: dict) -> bool:
    return isinstance(record.get("metadata"), dict) and "archive_admission" in record["metadata"]


def _is_archive_admitted_valid(record: dict) -> bool:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    admission = metadata.get("archive_admission") if isinstance(metadata, dict) else None
    evaluation = record.get("evaluation") if isinstance(record.get("evaluation"), dict) else {}
    return bool(isinstance(admission, dict) and admission.get("admitted")) and bool(
        evaluation.get("is_valid", True)
    )


def _record_selection_key(record: dict) -> tuple[float, float]:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    admission = metadata.get("archive_admission") if isinstance(metadata, dict) else {}
    raw = None
    if isinstance(admission, dict):
        raw = admission.get("selection_score")
    if not isinstance(raw, (int, float)) or isinstance(raw, bool):
        raw = metadata.get("selection_score") if isinstance(metadata, dict) else None
    selection_score = float(raw) if isinstance(raw, (int, float)) and not isinstance(raw, bool) else None
    if selection_score is None:
        selection_score = float(record.get("fitness", float("-inf")))
    return (selection_score, float(record.get("fitness", float("-inf"))))


def _archive_summary(record: dict) -> str | None:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    admission = metadata.get("archive_admission") if isinstance(metadata, dict) else None
    if not isinstance(admission, dict):
        return None
    parts = []
    if isinstance(admission.get("selection_score"), (int, float)) and not isinstance(
        admission.get("selection_score"), bool
    ):
        parts.append(f"selection_score={float(admission['selection_score']):.6f}")
    if isinstance(admission.get("island_id"), int):
        parts.append(f"island={admission['island_id']}")
    if isinstance(admission.get("cell"), list):
        parts.append(f"cell={admission['cell']}")
    descriptors = admission.get("descriptors")
    if isinstance(descriptors, dict) and descriptors:
        parts.append(f"descriptors={json.dumps(descriptors, sort_keys=True)}")
    return f"Archive:        {'; '.join(parts)}" if parts else None


def _write_best_artifacts(program, run_dir: Path) -> tuple[Path, Path]:
    run_dir.mkdir(parents=True, exist_ok=True)
    best_py = run_dir / "best.py"
    best_py.write_text(program.code, encoding="utf-8")

    workspace_dir = run_dir / "best_workspace"
    if workspace_dir.exists():
        shutil.rmtree(workspace_dir)
    program.workspace().materialize(workspace_dir)
    return best_py, workspace_dir
