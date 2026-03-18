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
    d = Path(problem_dir)
    if not d.is_dir():
        raise FileNotFoundError(f"Problem directory not found: {d}")
    task = (d / "task_description.txt").read_text(encoding="utf-8").strip()
    with open(d / "metrics.yaml", encoding="utf-8") as f:
        metrics: list[dict] = yaml.safe_load(f)["metrics"]
    primary = next((m for m in metrics if m.get("primary")), metrics[0])
    validate_path = d / "validate.py"
    if not validate_path.exists():
        raise FileNotFoundError(f"validate.py not found in {d}")
    seeds = sorted(p.read_text(encoding="utf-8") for p in (d / "initial_programs").glob("*.py"))
    if not seeds:
        raise ValueError(f"No seed programs (*.py) found in {d / 'initial_programs'}")
    return Problem(name=d.name, task_description=task, metrics=metrics,
                   primary_metric=primary["name"],
                   primary_bounds=tuple(primary.get("bounds", [0.0, 1.0])),
                   validate_path=validate_path, initial_programs=seeds, problem_dir=d)
