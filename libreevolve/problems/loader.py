from __future__ import annotations
from dataclasses import dataclass, field
import math
from pathlib import Path
import yaml
from libreevolve.core.candidate import CandidateWorkspace

_CONTEXT_EXTENSIONS = {".txt", ".md", ".py", ".pdf"}
_MAX_CONTEXT_CHARS = 6000

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
    initial_workspaces: list[CandidateWorkspace] = field(default_factory=list)

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
    metrics = _validate_metric_schema(metrics, d)
    primary = next((m for m in metrics if m.get("primary")), metrics[0])
    validate_path = d / "validate.py"
    if not validate_path.exists():
        raise FileNotFoundError(f"validate.py not found in {d}")
    seed_dir = d / "initial_programs"
    workspaces = _load_initial_workspaces(seed_dir)
    seeds = [workspace.code for workspace in workspaces]
    if not seeds:
        raise ValueError(f"No seed programs (*.py) or seed directories found in {seed_dir}")
    primary_bounds = (float(primary["bounds"][0]), float(primary["bounds"][1]))
    context_files = _load_context_files(d)
    return Problem(name=d.name, task_description=task, metrics=metrics,
                   primary_metric=primary["name"],
                   primary_bounds=primary_bounds,
                   validate_path=validate_path, initial_programs=seeds,
                   problem_dir=d, context_files=context_files,
                   initial_workspaces=workspaces)


def _validate_metric_schema(metrics: list[dict], problem_dir: Path) -> list[dict]:
    normalized: list[dict] = []
    names: set[str] = set()
    primaries = 0
    for index, metric in enumerate(metrics):
        if not isinstance(metric, dict):
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric #{index + 1} must be a mapping"
            )
        unsupported = sorted(set(metric) - {"name", "direction", "primary", "bounds"})
        if unsupported:
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric #{index + 1} has unsupported "
                f"fields {unsupported}"
            )
        name = metric.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric #{index + 1} needs a non-empty name"
            )
        if name in names:
            raise ValueError(f"metrics.yaml in {problem_dir}: duplicate metric name {name!r}")
        names.add(name)

        direction = metric.get("direction", "maximize")
        if direction not in {"maximize", "minimize"}:
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric {name!r} direction must be "
                "'maximize' or 'minimize'"
            )

        if metric.get("primary"):
            primaries += 1

        raw_bounds = metric.get("bounds", [0.0, 1.0])
        if not isinstance(raw_bounds, (list, tuple)) or len(raw_bounds) != 2:
            raise ValueError(f"Metric {name!r} bounds must be [lo, hi], got {raw_bounds}")
        try:
            bounds = (float(raw_bounds[0]), float(raw_bounds[1]))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Metric {name!r} bounds must be numeric [lo, hi], got {raw_bounds}"
            ) from exc
        if not all(math.isfinite(value) for value in bounds):
            raise ValueError(f"Metric {name!r} bounds must be finite, got {raw_bounds}")

        normalized_metric = dict(metric)
        normalized_metric["name"] = name
        normalized_metric["direction"] = direction
        normalized_metric["bounds"] = [bounds[0], bounds[1]]
        normalized.append(normalized_metric)

    if primaries > 1:
        raise ValueError(f"metrics.yaml in {problem_dir}: only one metric can be primary")
    return normalized


def _load_initial_workspaces(seed_dir: Path) -> list[CandidateWorkspace]:
    if not seed_dir.is_dir():
        return []
    workspaces: list[CandidateWorkspace] = []
    for path in sorted(seed_dir.iterdir()):
        if path.is_file() and path.suffix == ".py":
            workspaces.append(CandidateWorkspace.from_code(
                path.read_text(encoding="utf-8"), path.name
            ))
        elif path.is_dir():
            files: dict[str, str] = {}
            for child in sorted(p for p in path.rglob("*") if p.is_file()):
                if any(part.startswith(".") or part == "__pycache__" for part in child.relative_to(path).parts):
                    continue
                rel = child.relative_to(path).as_posix()
                files[rel] = child.read_text(encoding="utf-8")
            if files:
                preferred = next(
                    (p for p in ("main.py", "seed.py") if p in files),
                    next((p for p in sorted(files) if p.endswith(".py")), sorted(files)[0]),
                )
                workspaces.append(CandidateWorkspace(files, preferred))
    return workspaces


def _load_context_files(problem_dir: Path) -> dict[str, str]:
    context_dir = problem_dir / "context"
    if not context_dir.is_dir():
        return {}
    result: dict[str, str] = {}
    for path in sorted(context_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in _CONTEXT_EXTENSIONS:
            continue
        if path.suffix.lower() == ".pdf":
            result[path.name] = _summarize_context_text(_read_pdf_text(path), path.name)
        else:
            result[path.name] = _summarize_context_text(
                path.read_text(encoding="utf-8").strip(), path.name
            )
    return result


def _read_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        return text or "(no extractable text)"
    except Exception as exc:
        return f"(PDF extraction failed: {exc.__class__.__name__}: {exc})"


def _summarize_context_text(text: str, source: str) -> str:
    if len(text) <= _MAX_CONTEXT_CHARS:
        return text
    return (
        f"[{source}: showing first {_MAX_CONTEXT_CHARS} of {len(text)} characters]\n"
        f"{text[:_MAX_CONTEXT_CHARS]}"
    )
