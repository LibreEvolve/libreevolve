from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class Problem:
    name:             str
    task_description: str
    metrics:          list[dict]
    primary_metric:   str
    primary_bounds:   tuple[float, float]
    validate_path:    Path
    initial_programs: list[str]
    problem_dir:      Path

def load_problem(problem_dir: str | Path) -> Problem:
    d = Path(problem_dir).resolve()
    if not d.is_dir():
        raise FileNotFoundError(f"Problem directory not found: {d}")
    task = (d / "task_description.txt").read_text(encoding="utf-8").strip()
    with open(d / "metrics.yaml", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if not isinstance(raw, dict) or "metrics" not in raw:
        raise ValueError(f"metrics.yaml in {d} must contain a top-level 'metrics' list")
    metrics: list[dict] = raw["metrics"]
    if not isinstance(metrics, list) or not metrics:
        raise ValueError(f"metrics.yaml in {d}: 'metrics' must be a non-empty list")
    primary = next((m for m in metrics if m.get("primary")), metrics[0])
    validate_path = d / "validate.py"
    if not validate_path.exists():
        raise FileNotFoundError(f"validate.py not found in {d}")
    seeds = sorted(p.read_text(encoding="utf-8") for p in (d / "initial_programs").glob("*.py"))
    if not seeds:
        raise ValueError(f"No seed programs (*.py) found in {d / 'initial_programs'}")
    raw_bounds = primary.get("bounds", [0.0, 1.0])
    if len(raw_bounds) != 2:
        raise ValueError(
            f"Metric '{primary['name']}' bounds must be [lo, hi], got {raw_bounds}"
        )
    primary_bounds = (float(raw_bounds[0]), float(raw_bounds[1]))
    return Problem(name=d.name, task_description=task, metrics=metrics,
                   primary_metric=primary["name"],
                   primary_bounds=primary_bounds,
                   validate_path=validate_path, initial_programs=seeds, problem_dir=d)
