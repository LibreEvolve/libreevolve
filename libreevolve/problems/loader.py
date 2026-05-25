from __future__ import annotations
from dataclasses import dataclass, field
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
    context_files:    dict[str, str] = field(default_factory=dict)

    def metric(self, name: str) -> dict:
        for metric in self.metrics:
            if metric.get("name") == name:
                return metric
        return {}

    def metric_bounds(self, name: str) -> tuple[float, float]:
        metric = self.metric(name)
        raw = metric.get("bounds", [0.0, 1.0])
        return (float(raw[0]), float(raw[1]))

    def metric_direction(self, name: str) -> str:
        return str(self.metric(name).get("direction", "maximize"))

    def normalize_metric(self, name: str, value: float) -> float:
        lo, hi = self.metric_bounds(name)
        rng = hi - lo
        if rng == 0:
            return 0.5
        if self.metric_direction(name) == "minimize":
            normalized = (hi - value) / rng
        else:
            normalized = (value - lo) / rng
        return max(0.0, min(1.0, normalized))

    def fitness_from_metrics(self, metrics: dict) -> float:
        return self.normalize_metric(self.primary_metric, float(metrics[self.primary_metric]))

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
    context_files = _load_context_files(d)
    return Problem(name=d.name, task_description=task, metrics=metrics,
                   primary_metric=primary["name"],
                   primary_bounds=primary_bounds,
                   validate_path=validate_path, initial_programs=seeds,
                   problem_dir=d, context_files=context_files)


def _load_context_files(problem_dir: Path) -> dict[str, str]:
    context_dir = problem_dir / "context"
    if not context_dir.is_dir():
        return {}
    result: dict[str, str] = {}
    for path in sorted(context_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in {".txt", ".md", ".py"}:
            result[path.name] = path.read_text(encoding="utf-8").strip()
    return result
