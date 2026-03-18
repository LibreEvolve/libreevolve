from __future__ import annotations
import dataclasses, json
from pathlib import Path
import click
from alphaevolve.core.loop import evolve


@click.group()
def cli() -> None:
    """AlphaEvolve -- LLM-guided evolutionary program discovery."""


@cli.command()
@click.argument("problem_dir", type=click.Path(exists=True, file_okay=False))
@click.option("--max-generations", "-g", type=int, default=None)
@click.option("--plugins",  "-p", multiple=True)
@click.option("--backends", "-b", multiple=True)
@click.option("--seed", type=int, default=None)
def run(problem_dir, max_generations, plugins, backends, seed):
    """Run evolution on a problem directory."""
    from alphaevolve.core.config import Config
    from alphaevolve.problems.loader import load_problem
    problem = load_problem(problem_dir)
    if not problem.initial_programs:
        raise click.ClickException("No seed programs found.")
    config = _build_config(problem, max_generations, list(plugins), list(backends), seed)
    active_plugins = _load_plugins(config.plugins)
    click.echo(f"Running {config.max_generations} generations on '{problem.name}'...")
    best = evolve(problem, config, active_plugins)
    if best is None:
        raise click.ClickException("Evolution produced no valid programs.")
    click.echo(f"\nBest fitness: {best.fitness:.6f}")
    out = Path(config.log_dir) / problem.name / "best.py"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(best.code, encoding="utf-8")
    click.echo(f"Best program saved to: {out}")


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
    best = max(records, key=lambda r: r["fitness"])
    click.echo(f"Total programs: {len(records)}")
    click.echo(f"Best fitness:   {best['fitness']:.6f} (generation {best['generation']})")
    click.echo("\n--- Best program ---\n")
    click.echo(best["code"])


def _build_config(problem, max_generations, plugins, backends, seed):
    import yaml
    from alphaevolve.core.config import Config
    cfg: dict = {}
    cp = Path(problem.problem_dir) / "config.yaml"
    if cp.exists():
        cfg.update(yaml.safe_load(cp.read_text(encoding="utf-8")) or {})
    valid = {f.name for f in dataclasses.fields(Config)}
    config = Config(**{k: v for k, v in cfg.items() if k in valid})
    if max_generations is not None: config.max_generations = max_generations
    if plugins: config.plugins = list(plugins)
    if backends:
        config.backends = [{"type": t, "model": m}
                           for b in backends for t, _, m in [b.partition(":")]]
    if seed is not None: config.seed = seed
    config.problem_name = problem.name
    return config


def _load_plugins(names: list[str]) -> list:
    if not names:
        return []
    from alphaevolve.plugins import causal, deep_research, modular, ttt_rl
    reg = {"causal": causal.CausalPlugin, "deep_research": deep_research.DeepResearchPlugin,
           "modular": modular.ModularPlugin, "ttt_rl": ttt_rl.TTTRLPlugin}
    result = []
    for n in names:
        if n not in reg:
            raise click.ClickException(f"Unknown plugin: {n!r}. Available: {list(reg)}")
        result.append(reg[n]())
    return result
