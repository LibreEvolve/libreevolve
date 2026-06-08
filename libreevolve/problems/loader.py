from __future__ import annotations
import base64
from dataclasses import dataclass, field
from types import MappingProxyType
from collections.abc import Mapping
import fnmatch
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata
import yaml
from libreevolve.core.candidate import (
    CandidateWorkspace,
    DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES,
    validate_evolve_blocks,
)
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.core.yaml_utils import redacted_yaml_error, safe_load_unique

_CONTEXT_EXTENSIONS = {".txt", ".md", ".py", ".pdf"}
_MAX_CONTEXT_CHARS = 6000
_MAX_CONTEXT_SOURCE_BYTES = 1_000_000
_MAX_CONTEXT_TOTAL_BYTES = 10_000_000
_MAX_CONTEXT_PDF_PAGES = 100
_MAX_CONTEXT_PDF_CHARS = 500_000
_MAX_CONTEXT_ENTRIES = 1_000
_MAX_CONTEXT_DEPTH = 8
_MAX_CONTEXT_SKIPPED_DIAGNOSTICS = 500
_MAX_CONTEXT_PROVENANCE_CHARS = 200_000
_CONTEXT_MANIFEST_NAMES = ("context.yaml", "context.yml")
_SEED_POLICY_MANIFEST_NAMES = ("seed_policy.yaml", "seed_policy.yml")
_FORMULATION_METADATA_NAMES = ("formulation.yaml", "formulation.yml")
_COLLABORATOR_FEEDBACK_METADATA_NAMES = (
    "collaborator_feedback.yaml",
    "collaborator_feedback.yml",
)
_ACKNOWLEDGEMENT_METADATA_NAMES = ("acknowledgements.yaml", "acknowledgements.yml")
_CONTEXT_EXPLICIT_FAILURE_POLICIES = {"error", "warn"}
_CONTEXT_EXCERPT_POLICIES = {"head", "head_tail", "term_ranked"}
_CONTEXT_SOURCE_SELECTION_POLICIES = {"path_order", "term_ranked"}
_METRIC_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*){0,7}")

@dataclass
class Problem:
    name:             str
    task_description: str
    metrics:          list[dict] | tuple[Mapping[str, object], ...]
    primary_metric:   str
    primary_bounds:   tuple[float, float]
    validate_path:    Path
    initial_programs: list[str]
    problem_dir:      Path
    context_files:    dict[str, str] = field(default_factory=dict)
    context_sources:  list[dict] = field(default_factory=list)
    context_policy:   dict = field(default_factory=dict)
    initial_workspaces: list[CandidateWorkspace] = field(default_factory=list)
    initial_workspace_sources: list[dict] = field(default_factory=list)
    initial_workspace_skipped: list[dict] = field(default_factory=list)
    initial_workspace_policy: dict = field(default_factory=dict)
    formulation_metadata: dict = field(default_factory=dict)
    collaborator_feedback_metadata: dict = field(default_factory=dict)
    acknowledgement_metadata: dict = field(default_factory=dict)
    config_source:    dict = field(
        default_factory=lambda: {"path": "config.yaml", "status": "not_loaded"}
    )

    def __post_init__(self) -> None:
        configured_primary_bounds = self.primary_bounds
        metrics, primary_metric, primary_bounds = _normalize_metric_schema(
            self.metrics,
            Path(self.problem_dir),
            primary_metric=self.primary_metric,
        )
        _validate_direct_primary_bounds(configured_primary_bounds, primary_bounds)
        self.metrics = _freeze_metric_schema(metrics)
        self.primary_metric = primary_metric
        self.primary_bounds = primary_bounds
        self.validate_path = Path(self.validate_path)
        self.problem_dir = Path(self.problem_dir)

    def metric(self, name: str) -> Mapping[str, object]:
        for metric in self.metrics:
            if metric.get("name") == name:
                return metric
        raise KeyError(f"Unknown metric {name!r}")

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

    def objective_schema(self) -> dict:
        return {
            "metrics": [_metric_schema_record(metric) for metric in self.metrics],
            "primary_metric": self.primary_metric,
            "primary_bounds": [self.primary_bounds[0], self.primary_bounds[1]],
            "metric_count": len(self.metrics),
        }

def load_problem(problem_dir: str | Path) -> Problem:
    raw_dir = Path(problem_dir)
    if _is_link(raw_dir):
        raise ValueError(f"Problem directory links are not supported: {raw_dir}")
    d = raw_dir.resolve()
    if not d.is_dir():
        raise FileNotFoundError(f"Problem directory not found: {d}")
    task_path = d / "task_description.txt"
    _require_problem_file(task_path, "task_description.txt")
    task = _read_problem_text(task_path)
    if not task.strip():
        raise ValueError(f"{task_path} must contain a non-empty task description")
    metrics_path = d / "metrics.yaml"
    _require_problem_file(metrics_path, "metrics.yaml")
    raw = _load_metrics_yaml(metrics_path)
    if not isinstance(raw, dict):
        raise ValueError(f"metrics.yaml in {d} must contain a top-level 'metrics' list")
    if not all(isinstance(key, str) for key in raw):
        raise ValueError(f"{metrics_path}: top-level metrics.yaml keys must be strings")
    unsupported_root = sorted(set(raw) - {"metrics"})
    if unsupported_root:
        raise ValueError(
            f"{metrics_path}: unsupported top-level metrics.yaml fields {unsupported_root}"
        )
    if "metrics" not in raw:
        raise ValueError(f"metrics.yaml in {d} must contain a top-level 'metrics' list")
    metrics: list[dict] = raw["metrics"]
    if not isinstance(metrics, list) or not metrics:
        raise ValueError(f"metrics.yaml in {d}: 'metrics' must be a non-empty list")
    metrics, primary_metric, primary_bounds = _normalize_metric_schema(metrics, d)
    validate_path = d / "validate.py"
    _require_problem_file(validate_path, "validate.py")
    seed_dir = d / "initial_programs"
    workspaces, seed_sources, seed_skipped, seed_policy = _load_initial_workspaces(seed_dir)
    seeds = [workspace.code for workspace in workspaces]
    if not seeds:
        detail = _seed_skipped_error_detail(seed_skipped)
        raise ValueError(
            f"No seed programs (*.py) or seed directories found in {seed_dir}{detail}"
        )
    context_files, context_sources, context_policy = _load_context_files(
        d,
        task_description=task,
    )
    formulation_metadata = _load_formulation_metadata(d)
    collaborator_feedback_metadata = _load_collaborator_feedback_metadata(d)
    acknowledgement_metadata = _load_acknowledgement_metadata(d)
    return Problem(name=d.name, task_description=task, metrics=metrics,
                   primary_metric=primary_metric,
                   primary_bounds=primary_bounds,
                   validate_path=validate_path, initial_programs=seeds,
                   problem_dir=d, context_files=context_files,
                   context_sources=context_sources,
                   context_policy=context_policy,
                   initial_workspaces=workspaces,
                   initial_workspace_sources=seed_sources,
                   initial_workspace_skipped=seed_skipped,
                   initial_workspace_policy=seed_policy,
                   formulation_metadata=formulation_metadata,
                   collaborator_feedback_metadata=collaborator_feedback_metadata,
                   acknowledgement_metadata=acknowledgement_metadata)


def _validate_metric_schema(metrics: list[dict], problem_dir: Path) -> list[dict]:
    return _normalize_metric_schema(metrics, problem_dir)[0]


def _normalize_metric_schema(
    metrics: object,
    problem_dir: Path,
    *,
    primary_metric: str | None = None,
) -> tuple[list[dict], str, tuple[float, float]]:
    if not isinstance(metrics, list) or not metrics:
        raise ValueError(f"metrics.yaml in {problem_dir}: 'metrics' must be a non-empty list")
    normalized: list[dict] = []
    names: set[str] = set()
    primary_names: list[str] = []
    for index, metric in enumerate(metrics):
        if not isinstance(metric, dict):
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric #{index + 1} must be a mapping"
            )
        if not all(isinstance(key, str) for key in metric):
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric #{index + 1} keys must be strings"
            )
        unsupported = sorted(
            set(metric) - {"name", "direction", "primary", "bounds", "source", "weight"}
        )
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
        if any(unicodedata.category(char) == "Cf" for char in name):
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric {name!r} uses unsafe Unicode format controls"
            )
        if _METRIC_NAME_RE.fullmatch(name) is None:
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric {name!r} must be a safe metric name"
            )
        if name in names:
            raise ValueError(f"metrics.yaml in {problem_dir}: duplicate metric name {name!r}")
        if name == "is_valid":
            raise ValueError(
                f"metrics.yaml in {problem_dir}: 'is_valid' is reserved for evaluator validity"
            )
        names.add(name)

        direction = metric.get("direction", "maximize")
        if direction not in {"maximize", "minimize"}:
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric {name!r} direction must be "
                "'maximize' or 'minimize'"
            )

        primary_value = metric.get("primary", False)
        if not isinstance(primary_value, bool):
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric {name!r} primary must be boolean"
            )
        if primary_value:
            primary_names.append(name)

        source = metric.get("source", "evaluator")
        if source not in {"evaluator", "feedback", "plugin", "final_fitness"}:
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric {name!r} source must be "
                "'evaluator', 'feedback', 'plugin', or 'final_fitness'"
            )
        if primary_value and source != "evaluator":
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric {name!r} primary metric "
                "must use source 'evaluator'"
            )

        raw_weight = metric.get("weight", 1.0)
        if isinstance(raw_weight, bool) or not isinstance(raw_weight, (int, float)):
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric {name!r} weight must be "
                "a finite non-negative number"
            )
        weight = float(raw_weight)
        if not math.isfinite(weight) or weight < 0.0:
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric {name!r} weight must be "
                "a finite non-negative number"
            )

        raw_bounds = metric.get("bounds", [0.0, 1.0])
        if not isinstance(raw_bounds, (list, tuple)) or len(raw_bounds) != 2:
            raise ValueError(f"Metric {name!r} bounds must be [lo, hi], got {raw_bounds}")
        if isinstance(raw_bounds[0], bool) or isinstance(raw_bounds[1], bool):
            raise ValueError(
                f"Metric {name!r} bounds must be numeric [lo, hi], got {raw_bounds}"
            )
        try:
            bounds = (float(raw_bounds[0]), float(raw_bounds[1]))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Metric {name!r} bounds must be numeric [lo, hi], got {raw_bounds}"
            ) from exc
        if not all(math.isfinite(value) for value in bounds):
            raise ValueError(f"Metric {name!r} bounds must be finite, got {raw_bounds}")
        if bounds[0] >= bounds[1]:
            raise ValueError(
                f"Metric {name!r} bounds must be strictly increasing [lo, hi], "
                f"got {raw_bounds}"
            )

        normalized_metric = dict(metric)
        normalized_metric["name"] = name
        normalized_metric["direction"] = direction
        normalized_metric["bounds"] = [bounds[0], bounds[1]]
        normalized_metric["source"] = source
        normalized_metric["weight"] = weight
        normalized.append(normalized_metric)

    if len(primary_names) > 1:
        raise ValueError(f"metrics.yaml in {problem_dir}: only one metric can be primary")
    if primary_metric is not None:
        if not isinstance(primary_metric, str) or primary_metric not in names:
            raise ValueError(
                f"metrics.yaml in {problem_dir}: primary_metric must reference a declared metric"
            )
        if primary_names and primary_names[0] != primary_metric:
            raise ValueError(
                f"metrics.yaml in {problem_dir}: primary_metric {primary_metric!r} "
                f"conflicts with primary metric {primary_names[0]!r}"
            )
        effective_primary = primary_metric
    else:
        effective_primary = primary_names[0] if primary_names else normalized[0]["name"]
    for metric in normalized:
        metric["primary"] = metric["name"] == effective_primary
        if metric["primary"] and metric["source"] != "evaluator":
            raise ValueError(
                f"metrics.yaml in {problem_dir}: primary metric {metric['name']!r} "
                "must use source 'evaluator'"
            )
    primary_bounds = next(
        (tuple(metric["bounds"]) for metric in normalized if metric["name"] == effective_primary),
        None,
    )
    if primary_bounds is None:
        raise ValueError(
            f"metrics.yaml in {problem_dir}: primary_metric must reference a declared metric"
        )
    return normalized, effective_primary, (float(primary_bounds[0]), float(primary_bounds[1]))


def _freeze_metric_schema(metrics: list[dict]) -> tuple[Mapping[str, object], ...]:
    frozen: list[Mapping[str, object]] = []
    for metric in metrics:
        record = dict(metric)
        bounds = record.get("bounds")
        if isinstance(bounds, list):
            record["bounds"] = tuple(bounds)
        frozen.append(MappingProxyType(record))
    return tuple(frozen)


def _metric_schema_record(metric: Mapping[str, object]) -> dict:
    record = dict(metric)
    bounds = record.get("bounds")
    if isinstance(bounds, tuple):
        record["bounds"] = list(bounds)
    return record


def _validate_direct_primary_bounds(value: object, expected: tuple[float, float]) -> None:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError("primary_bounds must be numeric finite [lo, hi]")
    normalized: list[float] = []
    for bound in value:
        if isinstance(bound, bool) or not isinstance(bound, (int, float)):
            raise ValueError("primary_bounds must be numeric finite [lo, hi]")
        number = float(bound)
        if not math.isfinite(number):
            raise ValueError("primary_bounds must be numeric finite [lo, hi]")
        normalized.append(number)
    if normalized[0] >= normalized[1]:
        raise ValueError("primary_bounds must be strictly increasing [lo, hi]")
    if (normalized[0], normalized[1]) != expected:
        raise ValueError("primary_bounds must match declared primary metric bounds")


def _load_metrics_yaml(path: Path) -> object:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(
            f"{path}: metrics.yaml could not be read: {redact_sensitive_text(str(exc))}"
        ) from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path}: metrics.yaml must be valid UTF-8") from exc
    try:
        return safe_load_unique(text)
    except yaml.YAMLError as exc:
        raise ValueError(
            f"{path}: invalid metrics.yaml YAML: {redacted_yaml_error(exc)}"
        ) from exc


def _load_formulation_metadata(problem_dir: Path) -> dict:
    paths = [problem_dir / name for name in _FORMULATION_METADATA_NAMES]
    existing = [path for path in paths if path.exists()]
    if not existing:
        return {}
    if len(existing) > 1:
        labels = [path.name for path in existing]
        raise ValueError(
            f"{problem_dir}: use only one problem formulation metadata file from {labels}"
        )
    path = existing[0]
    if _is_link(path):
        raise ValueError(f"{path}: formulation metadata links are not supported")
    if not path.is_file():
        raise ValueError(f"{path}: formulation metadata must be a file")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(
            f"{path}: formulation metadata could not be read: "
            f"{redact_sensitive_text(str(exc))}"
        ) from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path}: formulation metadata must be valid UTF-8") from exc
    try:
        raw = safe_load_unique(text) if text.strip() else {}
    except yaml.YAMLError as exc:
        raise ValueError(
            f"{path}: invalid formulation metadata YAML: {redacted_yaml_error(exc)}"
        ) from exc
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: formulation metadata must be a mapping")
    if not all(isinstance(key, str) for key in raw):
        raise ValueError(f"{path}: formulation metadata keys must be strings")
    return dict(raw)


def _load_collaborator_feedback_metadata(problem_dir: Path) -> dict:
    paths = [problem_dir / name for name in _COLLABORATOR_FEEDBACK_METADATA_NAMES]
    existing = [path for path in paths if path.exists()]
    if not existing:
        return {}
    if len(existing) > 1:
        labels = [path.name for path in existing]
        raise ValueError(
            f"{problem_dir}: use only one collaborator feedback metadata file from {labels}"
        )
    path = existing[0]
    if _is_link(path):
        raise ValueError(f"{path}: collaborator feedback metadata links are not supported")
    if not path.is_file():
        raise ValueError(f"{path}: collaborator feedback metadata must be a file")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(
            f"{path}: collaborator feedback metadata could not be read: "
            f"{redact_sensitive_text(str(exc))}"
        ) from exc
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"{path}: collaborator feedback metadata must be valid UTF-8"
        ) from exc
    try:
        raw = safe_load_unique(text) if text.strip() else {}
    except yaml.YAMLError as exc:
        raise ValueError(
            f"{path}: invalid collaborator feedback metadata YAML: "
            f"{redacted_yaml_error(exc)}"
        ) from exc
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: collaborator feedback metadata must be a mapping")
    if not all(isinstance(key, str) for key in raw):
        raise ValueError(f"{path}: collaborator feedback metadata keys must be strings")
    return dict(raw)


def _load_acknowledgement_metadata(problem_dir: Path) -> dict:
    paths = [problem_dir / name for name in _ACKNOWLEDGEMENT_METADATA_NAMES]
    existing = [path for path in paths if path.exists()]
    if not existing:
        return {}
    if len(existing) > 1:
        labels = [path.name for path in existing]
        raise ValueError(
            f"{problem_dir}: use only one acknowledgement metadata file from {labels}"
        )
    path = existing[0]
    if _is_link(path):
        raise ValueError(f"{path}: acknowledgement metadata links are not supported")
    if not path.is_file():
        raise ValueError(f"{path}: acknowledgement metadata must be a file")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(
            f"{path}: acknowledgement metadata could not be read: "
            f"{redact_sensitive_text(str(exc))}"
        ) from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path}: acknowledgement metadata must be valid UTF-8") from exc
    try:
        raw = safe_load_unique(text) if text.strip() else {}
    except yaml.YAMLError as exc:
        raise ValueError(
            f"{path}: invalid acknowledgement metadata YAML: "
            f"{redacted_yaml_error(exc)}"
        ) from exc
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: acknowledgement metadata must be a mapping")
    if not all(isinstance(key, str) for key in raw):
        raise ValueError(f"{path}: acknowledgement metadata keys must be strings")
    return dict(raw)


def _require_problem_file(path: Path, label: str) -> None:
    if _is_link(path):
        raise ValueError(f"{path}: {label} links are not supported")
    try:
        exists = path.exists()
        is_file = path.is_file() if exists else False
    except OSError as exc:
        raise ValueError(
            f"{path}: {label} could not be inspected: "
            f"{redact_sensitive_text(str(exc))}"
        ) from exc
    if not exists:
        raise FileNotFoundError(f"{label} not found in {path.parent}")
    if not is_file:
        raise ValueError(f"{path}: {label} must be a regular file")


def _load_initial_workspaces(seed_dir: Path) -> tuple[list[CandidateWorkspace], list[dict], list[dict], dict]:
    if _is_link(seed_dir):
        raise ValueError(f"Seed root links are not supported: {seed_dir}")
    if not seed_dir.is_dir():
        return [], [], [], _seed_workspace_policy(None)
    workspaces: list[CandidateWorkspace] = []
    sources: list[dict] = []
    skipped: list[dict] = []
    seed_policy = _load_seed_workspace_policy(seed_dir)
    try:
        seed_entries = sorted(seed_dir.iterdir())
    except OSError as exc:
        raise ValueError(
            f"{seed_dir}: initial_programs could not be listed: "
            f"{redact_sensitive_text(str(exc))}"
        ) from exc
    for path in seed_entries:
        if path.name in _SEED_POLICY_MANIFEST_NAMES:
            continue
        rel_path = path.relative_to(seed_dir).as_posix()
        if _seed_path_excluded(rel_path, seed_policy):
            skipped.append(
                _seed_skipped_record(
                    seed_dir,
                    path,
                    "seed_policy_excluded",
                    entry_type=_seed_entry_type(path),
                )
            )
            continue
        if _is_ignored_seed_component(path.name) and not _seed_path_included(rel_path, seed_policy):
            skipped.append(
                _seed_skipped_record(
                    seed_dir,
                    path,
                    _ignored_seed_reason(path.name, top_level=True),
                    entry_type=_seed_entry_type(path),
                )
            )
            continue
        if _is_link(path):
            raise ValueError(f"Seed path links are not supported: {path}")
        if path.is_file() and path.suffix == ".py":
            code = _read_problem_text(path)
            _validate_seed_evolve_blocks(path, code)
            allowed_reserved_paths = (
                frozenset({path.name})
                if _is_reserved_seed_path(path.name)
                else frozenset()
            )
            workspace = CandidateWorkspace(
                {path.name: code},
                path.name,
                allowed_reserved_paths=allowed_reserved_paths,
            )
            workspaces.append(workspace)
            sources.append(
                _seed_source_record(
                    seed_dir,
                    path,
                    len(workspaces) - 1,
                    "file",
                    workspace,
                )
            )
        elif path.is_dir():
            files: dict[str, str] = {}
            static_files: list[dict[str, str | int]] = []
            allowed_reserved_paths: set[str] = set()
            skipped_before = len(skipped)
            for child in sorted(path.rglob("*")):
                rel_parts = child.relative_to(path).parts
                child_rel_to_seed = child.relative_to(seed_dir).as_posix()
                if _seed_path_excluded(child_rel_to_seed, seed_policy):
                    skipped.append(
                        _seed_skipped_record(
                            seed_dir,
                            child,
                            "seed_policy_excluded",
                            entry_type=_seed_entry_type(child),
                        )
                    )
                    continue
                if (
                    any(_is_ignored_seed_component(part) for part in rel_parts)
                    and not _seed_path_included(child_rel_to_seed, seed_policy)
                ):
                    skipped.append(
                        _seed_skipped_record(
                            seed_dir,
                            child,
                            _ignored_seed_reason(next(
                                part for part in rel_parts if _is_ignored_seed_component(part)
                            )),
                            entry_type=_seed_entry_type(child),
                        )
                    )
                    continue
                if _is_link(child):
                    raise ValueError(f"Seed workspace links are not supported: {child}")
                if not child.is_file():
                    continue
                rel = child.relative_to(path).as_posix()
                content = _read_seed_workspace_text(
                    seed_dir,
                    child,
                    skipped,
                    static_files=static_files,
                    static_base=path,
                )
                if content is None:
                    continue
                _validate_seed_evolve_blocks(child, content)
                files[rel] = content
                if _is_reserved_seed_path(rel):
                    allowed_reserved_paths.add(rel)
            if files:
                preferred = _seed_workspace_primary_file(files)
                if preferred is None:
                    skipped.append(
                        _seed_skipped_record(
                            seed_dir,
                            path,
                            "no_python_seed_primary",
                            entry_type="directory",
                            file_count=len(files),
                        )
                    )
                    continue
                workspace = CandidateWorkspace(
                    files,
                    preferred,
                    allowed_reserved_paths=frozenset(allowed_reserved_paths),
                    static_files=static_files,
                )
                workspaces.append(workspace)
                sources.append(
                    _seed_source_record(
                        seed_dir,
                        path,
                        len(workspaces) - 1,
                        "directory",
                        workspace,
                    )
                )
            else:
                reason = (
                    "all_seed_workspace_files_skipped"
                    if len(skipped) > skipped_before
                    else "empty_seed_workspace"
                )
                skipped.append(
                    _seed_skipped_record(
                        seed_dir,
                        path,
                        reason,
                        entry_type="directory",
                        skipped_file_count=len(skipped) - skipped_before,
                    )
                )
        elif path.is_file():
            skipped.append(
                _seed_skipped_record(
                    seed_dir,
                    path,
                    "unsupported_top_level_seed_file",
                    entry_type="file",
                    source_type=path.suffix.lstrip(".") or "none",
                )
            )
    return workspaces, sources, skipped, seed_policy


def _load_seed_workspace_policy(seed_dir: Path) -> dict:
    policy_paths = [
        seed_dir / name
        for name in _SEED_POLICY_MANIFEST_NAMES
        if (seed_dir / name).exists() or (seed_dir / name).is_symlink()
    ]
    if not policy_paths:
        return _seed_workspace_policy(None)
    if len(policy_paths) > 1:
        names = [path.name for path in policy_paths]
        raise ValueError(f"{seed_dir}: only one seed policy file is allowed, found {names}")
    policy_path = policy_paths[0]
    if _is_link(policy_path):
        raise ValueError(f"{policy_path}: seed policy links are not supported")
    text = _read_problem_text(policy_path)
    try:
        raw = safe_load_unique(text) if text.strip() else {}
    except yaml.YAMLError as exc:
        raise ValueError(
            f"{policy_path}: invalid seed policy YAML: {redacted_yaml_error(exc)}"
        ) from exc
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError(f"{policy_path}: seed policy must be a mapping")
    if not all(isinstance(key, str) for key in raw):
        raise ValueError(f"{policy_path}: seed policy keys must be strings")
    unsupported = sorted(set(raw) - {"include", "exclude"})
    if unsupported:
        raise ValueError(f"{policy_path}: unsupported seed policy fields {unsupported}")
    include = _seed_policy_pattern_list(policy_path, raw.get("include", []), "include")
    exclude = _seed_policy_pattern_list(policy_path, raw.get("exclude", []), "exclude")
    return _seed_workspace_policy(policy_path.name, include=include, exclude=exclude)


def _seed_workspace_policy(
    source: str | None,
    *,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> dict:
    return {
        "policy": "skip_reserved_seed_paths_by_default",
        "reserved_components": ["dot-prefixed", "__pycache__"],
        "source": source,
        "include": list(include or []),
        "exclude": list(exclude or []),
        "exclude_precedence": True,
    }


def _seed_policy_pattern_list(path: Path, value: object, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{path}: seed policy {field_name} must be a list of path patterns")
    return [
        _normalize_seed_policy_pattern(path, pattern, field_name, index)
        for index, pattern in enumerate(value)
    ]


def _normalize_seed_policy_pattern(
    path: Path,
    pattern: str,
    field_name: str,
    index: int,
) -> str:
    label = f"{field_name}[{index}]"
    raw = pattern.replace("\\", "/")
    if not raw or raw.startswith("/") or redact_sensitive_text(raw) != raw:
        raise ValueError(f"{path}: seed policy {label} must be a safe relative pattern")
    normalized = unicodedata.normalize("NFC", raw)
    if unicodedata.normalize("NFKC", normalized) != normalized:
        raise ValueError(f"{path}: seed policy {label} must be compatibility-normalized")
    parts = [part for part in normalized.split("/") if part]
    if not parts or len(parts) != len(normalized.split("/")):
        raise ValueError(f"{path}: seed policy {label} must be a safe relative pattern")
    if any(part in {".", ".."} for part in parts):
        raise ValueError(f"{path}: seed policy {label} must not contain dot traversal")
    if any(
        any(ord(char) < 32 or ord(char) == 127 for char in part)
        or any(unicodedata.category(char) in {"Cf", "Cs"} for char in part)
        for part in parts
    ):
        raise ValueError(f"{path}: seed policy {label} contains unsafe characters")
    return "/".join(parts)


def _seed_path_excluded(rel_path: str, policy: dict) -> bool:
    return _matches_any(rel_path, policy.get("exclude", []))


def _seed_path_included(rel_path: str, policy: dict) -> bool:
    include = policy.get("include", [])
    if not _is_reserved_seed_path(rel_path):
        return _matches_any(rel_path, include)
    return any(
        _matches(rel_path, pattern) and _seed_policy_pattern_has_reserved_component(pattern)
        for pattern in include
    )


def _is_reserved_seed_path(rel_path: str) -> bool:
    return any(_is_ignored_seed_component(part) for part in rel_path.split("/"))


def _seed_policy_pattern_has_reserved_component(pattern: str) -> bool:
    return any(_is_ignored_seed_component(part) for part in pattern.split("/"))


def _is_ignored_seed_component(part: str) -> bool:
    return part.startswith(".") or part == "__pycache__"


def _ignored_seed_reason(part: str, *, top_level: bool = False) -> str:
    if part == "__pycache__":
        return "top_level_seed_cache" if top_level else "seed_workspace_cache_path"
    return "top_level_hidden_seed_entry" if top_level else "hidden_seed_workspace_path"


def _seed_workspace_primary_file(files: dict[str, str]) -> str | None:
    return next(
        (p for p in ("main.py", "seed.py") if p in files),
        next((p for p in sorted(files) if p.endswith(".py")), None),
    )


def _seed_entry_type(path: Path) -> str:
    if path.is_dir():
        return "directory"
    if path.is_file():
        return "file"
    return "other"


def _seed_skipped_record(
    seed_dir: Path,
    path: Path,
    reason: str,
    *,
    entry_type: str,
    source_type: str | None = None,
    skipped_file_count: int | None = None,
    file_count: int | None = None,
    byte_count: int | None = None,
    sha256: str | None = None,
    hash_scope: str | None = None,
) -> dict:
    raw_path = path.relative_to(seed_dir.parent).as_posix()
    display_path = redact_sensitive_text(raw_path)
    record = {
        "seed_source_path": display_path,
        "reason": reason,
        "entry_type": entry_type,
    }
    if display_path != raw_path:
        record["seed_source_path_hash"] = hashlib.sha256(
            raw_path.encode("utf-8")
        ).hexdigest()
        record["seed_source_path_redacted"] = True
    if source_type is not None:
        record["source_type"] = source_type
    if skipped_file_count is not None:
        record["skipped_file_count"] = skipped_file_count
    if file_count is not None:
        record["file_count"] = file_count
    if byte_count is not None:
        record["bytes"] = byte_count
    if sha256 is not None:
        record["sha256"] = sha256
    if hash_scope is not None:
        record["hash_scope"] = hash_scope
    return record


def _seed_skipped_error_detail(skipped: list[dict]) -> str:
    if not skipped:
        return ""
    previews = [
        f"{record.get('seed_source_path', '<unknown>')}:{record.get('reason', 'skipped')}"
        for record in skipped[:5]
    ]
    omitted = len(skipped) - len(previews)
    suffix = f"; omitted={omitted}" if omitted > 0 else ""
    return f"; skipped seed entries: {', '.join(previews)}{suffix}"


def _seed_source_record(
    seed_dir: Path,
    source_path: Path,
    index: int,
    kind: str,
    workspace: CandidateWorkspace,
) -> dict:
    seed_source_path = _seed_source_label(seed_dir, source_path)
    record = {
        "seed_index": index,
        "seed_source_path": seed_source_path,
        "seed_source_kind": kind,
        "primary_file": workspace.primary_file,
        "file_count": len(workspace.files),
        "files": sorted(workspace.files),
    }
    if workspace.allowed_reserved_paths:
        record["allowed_reserved_paths"] = sorted(workspace.allowed_reserved_paths)
    if workspace.static_files:
        record["static_file_count"] = len(workspace.static_files)
        record["static_files"] = sorted(item["path"] for item in workspace.static_files)
    return record


def _seed_source_label(seed_dir: Path, source_path: Path) -> str:
    label = source_path.relative_to(seed_dir.parent).as_posix()
    if redact_sensitive_text(label) != label:
        raise ValueError("Seed source path must not contain secret-like text")
    return label


def _read_problem_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(
            f"{path}: could not be read: {redact_sensitive_text(str(exc))}"
        ) from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path}: must be valid UTF-8") from exc


def _read_seed_workspace_text(
    seed_dir: Path,
    path: Path,
    skipped: list[dict],
    *,
    static_files: list[dict[str, str | int]] | None = None,
    static_base: Path | None = None,
) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(
            f"{path}: could not be read: {redact_sensitive_text(str(exc))}"
        ) from exc
    except UnicodeDecodeError:
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise ValueError(
                f"{path}: could not be read: {redact_sensitive_text(str(exc))}"
            ) from exc
        sha256 = hashlib.sha256(raw).hexdigest()
        skipped.append(
            _seed_skipped_record(
                seed_dir,
                path,
                "non_utf8_seed_workspace_file",
                entry_type="file",
                source_type=path.suffix.lstrip(".") or "none",
                byte_count=len(raw),
                sha256=sha256,
                hash_scope="file_bytes",
            )
        )
        if static_files is not None and static_base is not None:
            static_record = {
                "path": path.relative_to(static_base).as_posix(),
                "kind": "binary",
                "sha256": sha256,
                "bytes": len(raw),
                "source_kind": "seed_workspace_file",
                "source_path": path.relative_to(seed_dir.parent).as_posix(),
                "mutation_policy": "immutable",
            }
            if len(raw) <= DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES:
                static_record["content_b64"] = base64.b64encode(raw).decode("ascii")
            static_files.append(static_record)
        return None


def _validate_seed_evolve_blocks(path: Path, content: str) -> None:
    marker_error = validate_evolve_blocks(content)
    if marker_error is not None:
        raise ValueError(f"{path}: malformed evolve-block markers: {marker_error}")


def _is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (is_junction is not None and is_junction())


def _load_context_files(
    problem_dir: Path,
    *,
    task_description: str = "",
) -> tuple[dict[str, str], list[dict], dict]:
    context_dir = problem_dir / "context"
    if _is_link(context_dir):
        raise ValueError(f"Context links are not supported: {context_dir}")
    if not context_dir.is_dir():
        return {}, [], _context_policy(False)
    manifest = _load_context_manifest(context_dir)
    max_chars = manifest["max_chars_per_source"]
    excerpt_policy = manifest["excerpt_policy"]
    max_pdf_pages = manifest["max_pdf_pages"]
    max_pdf_chars = manifest["max_pdf_chars"]
    result: dict[str, str] = {}
    sources: list[dict] = []
    loaded_context_records: list[dict] = []
    selected, skipped, include_patterns = _select_context_paths(context_dir, manifest)
    display_paths: dict[str, str] = {}
    explicit_context_failures: list[dict] = []
    for path in selected:
        raw_rel = path.relative_to(context_dir).as_posix()
        rel = _context_display_path(raw_rel)
        previous = display_paths.get(rel)
        if previous is not None:
            raise ValueError(
                f"{context_dir}: duplicate context source path after Unicode "
                f"normalization: {previous!r} and {raw_rel!r} -> {rel!r}"
            )
        display_paths[rel] = raw_rel
        rendered, metadata = _read_context_source(
            path,
            rel,
            max_chars,
            excerpt_policy=excerpt_policy,
            query_text=task_description,
            raw_rel_path=raw_rel,
            max_pdf_pages=max_pdf_pages,
            max_pdf_chars=max_pdf_chars,
        )
        if metadata.get("extraction_status") != "ok":
            diagnostic = _context_extraction_diagnostic(metadata)
            matched_include_patterns = _matched_context_include_patterns(
                rel,
                manifest["include"],
            )
            if matched_include_patterns:
                diagnostic["explicit_include"] = True
                diagnostic["matched_include_patterns"] = matched_include_patterns
                explicit_context_failures.append(
                    _explicit_context_failure_record(
                        diagnostic,
                        matched_include_patterns,
                    )
                )
            skipped.append(diagnostic)
            continue
        loaded_context_records.append({
            "path": rel,
            "rendered": rendered,
            "metadata": metadata,
        })
    retained_context_records, source_selection = _select_context_source_records(
        loaded_context_records,
        manifest,
        query_text=task_description,
    )
    for record in retained_context_records:
        rel = record["path"]
        result[rel] = record["rendered"]
        sources.append(record["metadata"])
    policy = _context_policy(
        True,
        manifest=manifest["manifest"],
        include=manifest["include"],
        exclude=manifest["exclude"],
        max_chars_per_source=max_chars,
        excerpt_policy=excerpt_policy,
        max_bytes_per_source=manifest["max_bytes_per_source"],
        max_total_bytes=manifest["max_total_bytes"],
        max_pdf_pages=max_pdf_pages,
        max_pdf_chars=max_pdf_chars,
        max_context_entries=manifest["max_context_entries"],
        max_context_depth=manifest["max_context_depth"],
        max_skipped_diagnostics=manifest["max_skipped_diagnostics"],
        max_context_provenance_chars=manifest["max_context_provenance_chars"],
        source_selection_policy=manifest["source_selection_policy"],
        max_selected_context_sources=manifest["max_selected_context_sources"],
        source_selection=source_selection,
        selected_count=len(sources),
        skipped=skipped,
        include_patterns=include_patterns,
        on_explicit_context_failure=manifest["on_explicit_context_failure"],
        explicit_context_failures=explicit_context_failures,
    )
    if (
        explicit_context_failures
        and manifest["on_explicit_context_failure"] == "error"
    ):
        _raise_explicit_context_failure(context_dir, explicit_context_failures)
    return result, sources, policy


def _load_context_manifest(context_dir: Path) -> dict:
    raw: dict = {}
    for name in _CONTEXT_MANIFEST_NAMES:
        path = context_dir / name
        if _is_link(path):
            raise ValueError(f"Context links are not supported: {path}")
        if path.exists() and not path.is_file():
            raise ValueError(f"{path}: context manifest must be a regular file")
    manifest_paths = [
        context_dir / name
        for name in _CONTEXT_MANIFEST_NAMES
        if (context_dir / name).exists()
    ]
    if len(manifest_paths) > 1:
        names = ", ".join(path.name for path in manifest_paths)
        raise ValueError(f"{context_dir}: use only one context manifest, found {names}")
    manifest_record = None
    for name in _CONTEXT_MANIFEST_NAMES:
        path = context_dir / name
        if path.exists():
            try:
                raw_bytes = path.read_bytes()
            except OSError as exc:
                raise ValueError(
                    f"{path}: context manifest could not be read: "
                    f"{redact_sensitive_text(str(exc))}"
                ) from exc
            manifest_record = {
                "path": path.relative_to(context_dir).as_posix(),
                "sha256": hashlib.sha256(raw_bytes).hexdigest(),
                "bytes": len(raw_bytes),
            }
            try:
                manifest_text = raw_bytes.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError(f"{path}: context manifest must be valid UTF-8") from exc
            try:
                loaded = safe_load_unique(manifest_text) or {}
            except yaml.YAMLError as exc:
                raise ValueError(
                    f"{path}: invalid context manifest YAML: {redacted_yaml_error(exc)}"
                ) from exc
            if not isinstance(loaded, dict):
                raise ValueError(f"{path} must contain a mapping")
            raw = loaded
            break
    if not all(isinstance(key, str) for key in raw):
        raise ValueError(f"{context_dir}: context manifest keys must be strings")
    supported_fields = {
        "include",
        "exclude",
        "max_chars_per_source",
        "max_bytes_per_source",
        "max_total_bytes",
        "max_pdf_pages",
        "max_pdf_chars",
        "max_context_entries",
        "max_context_depth",
        "max_skipped_diagnostics",
        "max_context_provenance_chars",
        "on_explicit_context_failure",
        "excerpt_policy",
        "source_selection_policy",
        "max_selected_context_sources",
    }
    unsupported = sorted(set(raw) - supported_fields)
    if unsupported:
        raise ValueError(f"{context_dir}: unsupported context manifest fields {unsupported}")
    include = raw.get("include")
    exclude = raw.get("exclude", [])
    if include is not None and (
        not isinstance(include, list) or not all(isinstance(item, str) for item in include)
    ):
        raise ValueError(f"{context_dir}: context include must be a list of strings")
    if not isinstance(exclude, list) or not all(isinstance(item, str) for item in exclude):
        raise ValueError(f"{context_dir}: context exclude must be a list of strings")
    _validate_context_patterns(context_dir, "include", include or [])
    _validate_context_patterns(context_dir, "exclude", exclude)
    on_explicit_context_failure = raw.get("on_explicit_context_failure", "error")
    if on_explicit_context_failure not in _CONTEXT_EXPLICIT_FAILURE_POLICIES:
        raise ValueError(
            f"{context_dir}: on_explicit_context_failure must be one of "
            f"{sorted(_CONTEXT_EXPLICIT_FAILURE_POLICIES)}, got "
            f"{on_explicit_context_failure!r}"
        )
    max_chars = raw.get("max_chars_per_source", _MAX_CONTEXT_CHARS)
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or max_chars <= 0:
        raise ValueError(f"{context_dir}: max_chars_per_source must be a positive integer")
    excerpt_policy = raw.get("excerpt_policy", "head")
    if not isinstance(excerpt_policy, str) or excerpt_policy not in _CONTEXT_EXCERPT_POLICIES:
        raise ValueError(
            f"{context_dir}: excerpt_policy must be one of "
            f"{sorted(_CONTEXT_EXCERPT_POLICIES)}, got {excerpt_policy!r}"
        )
    source_selection_policy = raw.get("source_selection_policy", "path_order")
    if (
        not isinstance(source_selection_policy, str)
        or source_selection_policy not in _CONTEXT_SOURCE_SELECTION_POLICIES
    ):
        raise ValueError(
            f"{context_dir}: source_selection_policy must be one of "
            f"{sorted(_CONTEXT_SOURCE_SELECTION_POLICIES)}, got "
            f"{source_selection_policy!r}"
        )
    max_selected_context_sources = _optional_positive_context_int(
        context_dir,
        raw,
        "max_selected_context_sources",
    )
    max_bytes = _positive_context_int(
        context_dir,
        raw,
        "max_bytes_per_source",
        _MAX_CONTEXT_SOURCE_BYTES,
    )
    max_total_bytes = _positive_context_int(
        context_dir,
        raw,
        "max_total_bytes",
        _MAX_CONTEXT_TOTAL_BYTES,
    )
    max_pdf_pages = _positive_context_int(
        context_dir,
        raw,
        "max_pdf_pages",
        _MAX_CONTEXT_PDF_PAGES,
    )
    max_pdf_chars = _positive_context_int(
        context_dir,
        raw,
        "max_pdf_chars",
        _MAX_CONTEXT_PDF_CHARS,
    )
    max_context_entries = _positive_context_int(
        context_dir,
        raw,
        "max_context_entries",
        _MAX_CONTEXT_ENTRIES,
    )
    max_context_depth = _positive_context_int(
        context_dir,
        raw,
        "max_context_depth",
        _MAX_CONTEXT_DEPTH,
    )
    max_skipped_diagnostics = _positive_context_int(
        context_dir,
        raw,
        "max_skipped_diagnostics",
        _MAX_CONTEXT_SKIPPED_DIAGNOSTICS,
    )
    max_context_provenance_chars = _positive_context_int(
        context_dir,
        raw,
        "max_context_provenance_chars",
        _MAX_CONTEXT_PROVENANCE_CHARS,
    )
    return {
        "manifest": manifest_record,
        "include": include,
        "exclude": exclude,
        "max_chars_per_source": max_chars,
        "excerpt_policy": excerpt_policy,
        "max_bytes_per_source": max_bytes,
        "max_total_bytes": max_total_bytes,
        "max_pdf_pages": max_pdf_pages,
        "max_pdf_chars": max_pdf_chars,
        "max_context_entries": max_context_entries,
        "max_context_depth": max_context_depth,
        "max_skipped_diagnostics": max_skipped_diagnostics,
        "max_context_provenance_chars": max_context_provenance_chars,
        "on_explicit_context_failure": on_explicit_context_failure,
        "source_selection_policy": source_selection_policy,
        "max_selected_context_sources": max_selected_context_sources,
    }


def _positive_context_int(context_dir: Path, raw: dict, field: str, default: int) -> int:
    value = raw.get(field, default)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{context_dir}: {field} must be a positive integer")
    return value


def _optional_positive_context_int(
    context_dir: Path,
    raw: dict,
    field: str,
) -> int | None:
    value = raw.get(field)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{context_dir}: {field} must be a positive integer or null")
    return value


def _validate_context_patterns(context_dir: Path, field: str, patterns: list[str]) -> None:
    for pattern in patterns:
        if _unsafe_context_pattern(pattern):
            raise ValueError(
                f"{context_dir}: context {field} pattern must be a safe "
                f"problem-relative glob: {pattern!r}"
            )


def _unsafe_context_pattern(pattern: str) -> bool:
    normalized = pattern.replace("\\", "/")
    if redact_sensitive_text(normalized) != normalized:
        return True
    if not pattern or pattern != normalized:
        return True
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
        return True
    if any(
        ord(char) < 32
        or ord(char) == 127
        or unicodedata.category(char) == "Cf"
        for char in normalized
    ):
        return True
    parts = [part for part in normalized.split("/") if part]
    return any(part == ".." for part in parts)


class _ContextSkippedDiagnostics:
    def __init__(self, max_records: int):
        self.max_records = max_records
        self.records: list[dict] = []
        self.total_count = 0
        self.omitted_count = 0
        self.reason_counts: dict[str, int] = {}
        self.omitted_reasons: dict[str, int] = {}

    def append(self, record: dict) -> None:
        reason = str(record.get("reason", "unknown"))
        self.total_count += 1
        self.reason_counts[reason] = self.reason_counts.get(reason, 0) + 1
        if len(self.records) < self.max_records:
            self.records.append(record)
            return
        self.omitted_count += 1
        self.omitted_reasons[reason] = self.omitted_reasons.get(reason, 0) + 1


def _select_context_paths(
    context_dir: Path, manifest: dict
) -> tuple[list[Path], "_ContextSkippedDiagnostics", list[dict]]:
    selected = []
    skipped = _ContextSkippedDiagnostics(int(manifest["max_skipped_diagnostics"]))
    include = manifest["include"]
    selected_bytes = 0
    max_bytes = int(manifest["max_bytes_per_source"])
    max_total_bytes = int(manifest["max_total_bytes"])
    include_match_counts = [0 for _ in include] if include is not None else []
    include_selected_counts = [0 for _ in include] if include is not None else []
    for path in _iter_context_entries(
        context_dir,
        max_entries=int(manifest["max_context_entries"]),
        max_depth=int(manifest["max_context_depth"]),
        skipped=skipped,
    ):
        if path.name in _CONTEXT_MANIFEST_NAMES:
            continue
        try:
            is_file = path.is_file()
        except OSError as exc:
            skipped.append(_context_stat_error_diagnostic(path, context_dir, exc))
            continue
        if not is_file:
            continue
        rel = path.relative_to(context_dir).as_posix()
        if path.suffix.lower() not in _CONTEXT_EXTENSIONS:
            skipped.append(
                _context_file_diagnostic(
                    path,
                    context_dir,
                    "unsupported_extension",
                    max_bytes=max_bytes,
                )
            )
            continue
        matched_include_indexes: list[int] = []
        if include is not None:
            matched_include_indexes = [
                index for index, pattern in enumerate(include) if _matches(rel, pattern)
            ]
            for index in matched_include_indexes:
                include_match_counts[index] += 1
            if not matched_include_indexes:
                skipped.append(
                    _context_file_diagnostic(
                        path,
                        context_dir,
                        "not_included",
                        max_bytes=max_bytes,
                    )
                )
                continue
        if _is_hidden_context_path(rel) and not _hidden_context_explicitly_included(
            include, matched_include_indexes
        ):
            skipped.append(
                _context_file_diagnostic(
                    path,
                    context_dir,
                    "hidden_not_included",
                    max_bytes=max_bytes,
                )
            )
            continue
        if _matches_any(rel, manifest["exclude"]):
            skipped.append(
                _context_file_diagnostic(
                    path,
                    context_dir,
                    "excluded",
                    max_bytes=max_bytes,
                )
            )
            continue
        try:
            size = path.stat().st_size
        except OSError as exc:
            skipped.append(_context_stat_error_diagnostic(path, context_dir, exc))
            continue
        if size > max_bytes:
            skipped.append(
                _context_resource_diagnostic(
                    path,
                    context_dir,
                    "max_source_bytes",
                    max_bytes=max_bytes,
                    bytes_value=size,
                )
            )
            continue
        if selected_bytes + size > max_total_bytes:
            skipped.append(
                _context_resource_diagnostic(
                    path,
                    context_dir,
                    "max_total_bytes",
                    max_bytes=max_total_bytes,
                    bytes_value=size,
                    total_before=selected_bytes,
                )
            )
            continue
        selected_bytes += size
        for index in matched_include_indexes:
            include_selected_counts[index] += 1
        selected.append(path)
    include_patterns = _context_include_pattern_records(
        include,
        include_match_counts,
        include_selected_counts,
    )
    return selected, skipped, include_patterns


def _context_policy(
    present: bool,
    *,
    manifest: dict | None = None,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    max_chars_per_source: int = _MAX_CONTEXT_CHARS,
    excerpt_policy: str = "head",
    max_bytes_per_source: int = _MAX_CONTEXT_SOURCE_BYTES,
    max_total_bytes: int = _MAX_CONTEXT_TOTAL_BYTES,
    max_pdf_pages: int = _MAX_CONTEXT_PDF_PAGES,
    max_pdf_chars: int = _MAX_CONTEXT_PDF_CHARS,
    max_context_entries: int = _MAX_CONTEXT_ENTRIES,
    max_context_depth: int = _MAX_CONTEXT_DEPTH,
    max_skipped_diagnostics: int = _MAX_CONTEXT_SKIPPED_DIAGNOSTICS,
    max_context_provenance_chars: int = _MAX_CONTEXT_PROVENANCE_CHARS,
    source_selection_policy: str = "path_order",
    max_selected_context_sources: int | None = None,
    source_selection: dict | None = None,
    selected_count: int = 0,
    skipped: _ContextSkippedDiagnostics | None = None,
    include_patterns: list[dict] | None = None,
    on_explicit_context_failure: str = "error",
    explicit_context_failures: list[dict] | None = None,
) -> dict:
    skipped = skipped or _ContextSkippedDiagnostics(max_skipped_diagnostics)
    include_patterns = include_patterns or []
    explicit_context_failures = explicit_context_failures or []
    policy = {
        "present": present,
        "supported_extensions": sorted(_CONTEXT_EXTENSIONS),
        "manifest": manifest,
        "include": include,
        "exclude": exclude or [],
        "max_chars_per_source": max_chars_per_source,
        "excerpt_policy": excerpt_policy,
        "max_bytes_per_source": max_bytes_per_source,
        "max_total_bytes": max_total_bytes,
        "max_pdf_pages": max_pdf_pages,
        "max_pdf_chars": max_pdf_chars,
        "max_context_entries": max_context_entries,
        "max_context_depth": max_context_depth,
        "max_skipped_diagnostics": max_skipped_diagnostics,
        "max_context_provenance_chars": max_context_provenance_chars,
        "source_selection_policy": source_selection_policy,
        "max_selected_context_sources": max_selected_context_sources,
        "source_selection": source_selection
        or _empty_context_source_selection_policy(
            source_selection_policy,
            max_selected_context_sources,
        ),
        "hidden_source_policy": "skip_unless_explicitly_included",
        "on_explicit_context_failure": on_explicit_context_failure,
        "explicit_context_failure_count": len(explicit_context_failures),
        "explicit_context_failures": list(explicit_context_failures),
        "selected_count": selected_count,
        "usable_selected_count": selected_count,
        "skipped_count": skipped.total_count,
        "skipped_record_count": len(skipped.records),
        "skipped_records_truncated": skipped.omitted_count > 0,
        "skipped_records_omitted": skipped.omitted_count,
        "skipped_omitted_reasons": dict(sorted(skipped.omitted_reasons.items())),
        "failed_extraction_count": sum(
            skipped.reason_counts.get(reason, 0)
            for reason in {
                "extraction_failed",
                "extraction_resource_limit",
                "no_extractable_text",
            }
        ),
        "skipped": list(skipped.records),
        "include_patterns": include_patterns,
        "unmatched_includes": [
            record["pattern"] for record in include_patterns if record["matches"] == 0
        ],
    }
    _enforce_context_policy_provenance_limit(policy, max_context_provenance_chars)
    return policy


def _empty_context_source_selection_policy(
    policy: str,
    max_selected_context_sources: int | None,
) -> dict:
    return {
        "schema": "libreevolve.context_source_selection_policy.v1",
        "policy": policy,
        "max_selected_context_sources": max_selected_context_sources,
        "candidate_count": 0,
        "selected_count": 0,
        "omitted_count": 0,
        "ranking_policy": "none",
        "query_terms_sha256": hashlib.sha256(b"").hexdigest(),
        "query_term_count": 0,
        "ranking_fallback": "no_context_sources",
        "selected_sources": [],
        "omitted_sources": [],
    }


def _select_context_source_records(
    records: list[dict],
    manifest: dict,
    *,
    query_text: str,
) -> tuple[list[dict], dict]:
    policy = str(manifest["source_selection_policy"])
    max_selected_context_sources = manifest["max_selected_context_sources"]
    if not records:
        return [], _empty_context_source_selection_policy(
            policy,
            max_selected_context_sources,
        )
    query_terms = _context_excerpt_query_terms(query_text)
    query_hash = hashlib.sha256(" ".join(query_terms).encode("utf-8")).hexdigest()
    candidates = []
    for index, record in enumerate(records):
        metadata = record["metadata"]
        rendered = record["rendered"]
        score = _context_excerpt_chunk_score(rendered, query_terms) if query_terms else 0
        candidates.append({
            "path": record["path"],
            "sha256": metadata.get("sha256"),
            "chars_rendered": metadata.get("chars_rendered", len(rendered)),
            "excerpt_policy": metadata.get("excerpt_policy"),
            "score": score,
            "original_index": index,
        })
    if policy == "term_ranked":
        ordered_candidates = sorted(
            candidates,
            key=lambda item: (-item["score"], item["original_index"], item["path"]),
        )
        ranking_policy = "term_overlap_selected_excerpt_v1"
    else:
        ordered_candidates = sorted(candidates, key=lambda item: item["original_index"])
        ranking_policy = "path_order_v1"
    if max_selected_context_sources is None:
        selected_candidates = ordered_candidates
    else:
        selected_candidates = ordered_candidates[:max_selected_context_sources]
    selected_paths = {item["path"] for item in selected_candidates}
    record_by_path = {record["path"]: record for record in records}
    retained_records = [record_by_path[item["path"]] for item in selected_candidates]
    selected_source_records = []
    for rank, candidate in enumerate(selected_candidates, start=1):
        record = record_by_path[candidate["path"]]
        record["metadata"] = {
            **record["metadata"],
            "source_selection_policy": policy,
            "source_selection_rank": rank,
            "source_selection_score": candidate["score"],
            "source_selection_ranking_policy": ranking_policy,
            "source_selection_query_terms_sha256": query_hash,
            "source_selection_query_term_count": len(query_terms),
        }
        selected_source_records.append(_context_source_selection_record(candidate, rank))
    omitted_source_records = [
        _context_source_selection_record(candidate, None, reason="max_selected_context_sources")
        for candidate in ordered_candidates
        if candidate["path"] not in selected_paths
    ]
    selection = {
        "schema": "libreevolve.context_source_selection_policy.v1",
        "policy": policy,
        "max_selected_context_sources": max_selected_context_sources,
        "candidate_count": len(candidates),
        "selected_count": len(selected_source_records),
        "omitted_count": len(omitted_source_records),
        "ranking_policy": ranking_policy,
        "query_terms_sha256": query_hash,
        "query_term_count": len(query_terms),
        "ranking_fallback": "empty_query_terms" if not query_terms else None,
        "selected_sources": selected_source_records,
        "omitted_sources": omitted_source_records,
    }
    if selection["ranking_fallback"] is None:
        del selection["ranking_fallback"]
    return retained_records, selection


def _context_source_selection_record(
    candidate: dict,
    rank: int | None,
    *,
    reason: str | None = None,
) -> dict:
    record = {
        "path": candidate["path"],
        "sha256": candidate["sha256"],
        "chars_rendered": candidate["chars_rendered"],
        "excerpt_policy": candidate["excerpt_policy"],
        "score": candidate["score"],
    }
    if rank is not None:
        record["rank"] = rank
    if reason is not None:
        record["reason"] = reason
    return record


def _enforce_context_policy_provenance_limit(policy: dict, max_chars: int) -> None:
    policy["context_provenance_truncated"] = False
    policy["context_provenance_chars"] = _context_policy_json_chars(policy)
    while policy["context_provenance_chars"] > max_chars and policy["skipped"]:
        record = policy["skipped"].pop()
        reason = str(record.get("reason", "unknown"))
        policy["skipped_record_count"] = len(policy["skipped"])
        policy["skipped_records_truncated"] = True
        policy["skipped_records_omitted"] += 1
        omitted = dict(policy["skipped_omitted_reasons"])
        omitted[reason] = omitted.get(reason, 0) + 1
        policy["skipped_omitted_reasons"] = dict(sorted(omitted.items()))
        policy["context_provenance_truncated"] = True
        policy["context_provenance_chars"] = _context_policy_json_chars(policy)
    if policy["context_provenance_chars"] > max_chars:
        policy["context_provenance_over_limit"] = True


def _context_policy_json_chars(policy: dict) -> int:
    return len(json.dumps(policy, sort_keys=True, allow_nan=False, separators=(",", ":")))


def _context_display_path_metadata(rel_path: str) -> dict:
    display_path = _context_display_path(rel_path)
    if display_path == rel_path:
        return {}
    return {"display_path": display_path}


def _context_resource_diagnostic(
    path: Path,
    context_dir: Path,
    reason: str,
    *,
    max_bytes: int,
    bytes_value: int,
    total_before: int | None = None,
) -> dict:
    rel_path = _context_diagnostic_rel_path(path, context_dir)
    diagnostic = {
        "path": rel_path,
        **_context_display_path_metadata(rel_path),
        "reason": reason,
        "source_type": path.suffix.lower().lstrip("."),
        "bytes": bytes_value,
        "max_bytes": max_bytes,
        "hidden": _is_hidden_context_path(rel_path),
        "sha256": None,
        "hash_omitted_reason": reason,
    }
    if total_before is not None:
        diagnostic["total_bytes_before"] = total_before
    return diagnostic


def _context_file_diagnostic(
    path: Path,
    context_dir: Path,
    reason: str,
    *,
    max_bytes: int,
) -> dict:
    rel_path = _context_diagnostic_rel_path(path, context_dir)
    source_type = path.suffix.lower().lstrip(".")
    hidden = _is_hidden_context_path(rel_path)
    try:
        size = path.stat().st_size
    except OSError as exc:
        return {
            "path": rel_path,
            **_context_display_path_metadata(rel_path),
            "reason": reason,
            "source_type": source_type,
            "sha256": None,
            "bytes": None,
            "hidden": hidden,
            "read_status": "stat_error",
            "error_type": exc.__class__.__name__,
            "error": redact_sensitive_text(str(exc)),
        }
    if size > max_bytes:
        return {
            "path": rel_path,
            **_context_display_path_metadata(rel_path),
            "reason": reason,
            "source_type": source_type,
            "sha256": None,
            "bytes": size,
            "max_bytes": max_bytes,
            "hidden": hidden,
            "read_status": "not_read",
            "hash_omitted_reason": "max_source_bytes",
        }
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        return {
            "path": rel_path,
            **_context_display_path_metadata(rel_path),
            "reason": reason,
            "source_type": source_type,
            "sha256": None,
            "bytes": None,
            "hidden": hidden,
            "read_status": "read_error",
            "error_type": exc.__class__.__name__,
            "error": redact_sensitive_text(str(exc)),
        }
    return {
        "path": rel_path,
        **_context_display_path_metadata(rel_path),
        "reason": reason,
        "source_type": source_type,
        "sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "bytes": len(raw_bytes),
        "hidden": hidden,
    }


def _context_stat_error_diagnostic(path: Path, context_dir: Path, exc: OSError) -> dict:
    rel_path = _context_diagnostic_rel_path(path, context_dir)
    return {
        "path": rel_path,
        **_context_display_path_metadata(rel_path),
        "reason": "stat_error",
        "source_type": path.suffix.lower().lstrip("."),
        "sha256": None,
        "bytes": None,
        "hidden": _is_hidden_context_path(rel_path),
        "error_type": exc.__class__.__name__,
        "error": redact_sensitive_text(str(exc)),
    }


def _context_extraction_diagnostic(metadata: dict) -> dict:
    status = str(metadata.get("extraction_status", "failed"))
    if status == "no_extractable_text":
        reason = "no_extractable_text"
    elif status == "resource_limit":
        reason = "extraction_resource_limit"
    elif status == "read_error":
        reason = "read_error"
    else:
        reason = "extraction_failed"
    diagnostic = {
        "path": metadata.get("path"),
        "reason": reason,
        "source_type": metadata.get("source_type"),
        "sha256": metadata.get("sha256"),
        "bytes": metadata.get("bytes"),
        "hidden": bool(metadata.get("hidden", False)),
        "extraction_status": status,
        "chars_original": metadata.get("chars_original"),
        "chars_rendered": metadata.get("chars_rendered"),
    }
    if "filesystem_path" in metadata:
        diagnostic["filesystem_path"] = metadata["filesystem_path"]
    if "pages" in metadata:
        diagnostic["pages"] = metadata["pages"]
    for key in ("max_pdf_pages", "max_pdf_chars", "extracted_chars"):
        if key in metadata:
            diagnostic[key] = metadata[key]
    if "error_type" in metadata:
        diagnostic["error_type"] = metadata["error_type"]
    if "error" in metadata:
        diagnostic["error"] = redact_sensitive_text(str(metadata["error"]))
    return diagnostic


def _matched_context_include_patterns(
    rel_path: str, include: list[str] | None
) -> list[str]:
    if include is None:
        return []
    return [pattern for pattern in include if _matches(rel_path, pattern)]


def _explicit_context_failure_record(
    diagnostic: dict, matched_include_patterns: list[str]
) -> dict:
    record = {
        "path": diagnostic.get("path"),
        "reason": diagnostic.get("reason"),
        "source_type": diagnostic.get("source_type"),
        "extraction_status": diagnostic.get("extraction_status"),
        "matched_include_patterns": list(matched_include_patterns),
    }
    for key in (
        "bytes",
        "sha256",
        "pages",
        "max_pdf_pages",
        "max_pdf_chars",
        "extracted_chars",
        "error_type",
        "error",
    ):
        if key in diagnostic:
            record[key] = diagnostic[key]
    return record


def _raise_explicit_context_failure(
    context_dir: Path, failures: list[dict]
) -> None:
    displayed = ", ".join(str(item.get("path", "<unknown>")) for item in failures[:3])
    if len(failures) > 3:
        displayed += f", ... ({len(failures) - 3} more)"
    raise ValueError(
        f"{context_dir}: explicit context extraction failed for "
        f"{len(failures)} included source(s): {displayed}; set "
        "on_explicit_context_failure: warn to allow degraded context"
    )


def _iter_context_entries(
    root: Path,
    *,
    max_entries: int,
    max_depth: int,
    skipped: _ContextSkippedDiagnostics,
) -> list[Path]:
    entries: list[Path] = []
    stopped = False

    def walk(directory: Path) -> None:
        nonlocal stopped
        if stopped:
            return
        try:
            children = sorted(directory.iterdir(), key=_context_sort_key)
        except OSError as exc:
            skipped.append(_context_directory_listing_diagnostic(directory, root, exc))
            return
        for path in children:
            if stopped:
                return
            if path.name in _CONTEXT_MANIFEST_NAMES:
                continue
            if _is_link(path):
                raise ValueError(f"Context links are not supported: {path}")
            rel_parts = path.relative_to(root).parts
            depth = len(rel_parts)
            if depth > max_depth:
                skipped.append(
                    _context_traversal_limit_diagnostic(
                        path,
                        root,
                        "max_context_depth",
                        depth=depth,
                        max_depth=max_depth,
                    )
                )
                continue
            if len(entries) >= max_entries:
                skipped.append(
                    _context_traversal_limit_diagnostic(
                        path,
                        root,
                        "max_context_entries",
                        max_entries=max_entries,
                        entries_before=len(entries),
                    )
                )
                stopped = True
                return
            try:
                is_directory = path.is_dir()
            except OSError as exc:
                skipped.append(_context_stat_error_diagnostic(path, root, exc))
                continue
            entries.append(path)
            if is_directory:
                walk(path)

    walk(root)
    return entries


def _context_directory_listing_diagnostic(
    path: Path,
    context_dir: Path,
    exc: OSError,
) -> dict:
    rel_path = _context_diagnostic_rel_path(path, context_dir)
    return {
        "path": rel_path,
        "reason": "directory_listing_error",
        "source_type": "directory",
        "hidden": _is_hidden_context_path(rel_path),
        "sha256": None,
        "error_type": exc.__class__.__name__,
        "error": redact_sensitive_text(str(exc)),
    }


def _context_traversal_limit_diagnostic(
    path: Path,
    context_dir: Path,
    reason: str,
    *,
    depth: int | None = None,
    max_depth: int | None = None,
    max_entries: int | None = None,
    entries_before: int | None = None,
) -> dict:
    rel_path = _context_diagnostic_rel_path(path, context_dir)
    diagnostic = {
        "path": rel_path,
        "reason": reason,
        "source_type": "directory" if path.is_dir() else path.suffix.lower().lstrip("."),
        "hidden": _is_hidden_context_path(rel_path),
        "sha256": None,
    }
    if depth is not None:
        diagnostic["depth"] = depth
    if max_depth is not None:
        diagnostic["max_depth"] = max_depth
    if max_entries is not None:
        diagnostic["max_entries"] = max_entries
    if entries_before is not None:
        diagnostic["entries_before"] = entries_before
    return diagnostic


def _context_diagnostic_rel_path(path: Path, context_dir: Path) -> str:
    rel_path = path.relative_to(context_dir).as_posix()
    if redact_sensitive_text(rel_path) != rel_path:
        raise ValueError(
            "skipped context source path must not contain secret-like text"
        )
    return rel_path


def _context_sort_key(path: Path) -> str:
    return path.as_posix()


def _matches_any(rel_path: str, patterns: list[str]) -> bool:
    return any(_matches(rel_path, pattern) for pattern in patterns)


def _matches(rel_path: str, pattern: str) -> bool:
    path_parts = [part for part in _context_display_path(rel_path).split("/") if part]
    pattern_parts = [part for part in _context_display_path(pattern).split("/") if part]
    return _matches_path_parts(path_parts, pattern_parts)


def _matches_path_parts(path_parts: list[str], pattern_parts: list[str]) -> bool:
    if not pattern_parts:
        return not path_parts
    pattern_head = pattern_parts[0]
    if pattern_head == "**":
        if len(pattern_parts) == 1:
            return True
        return any(
            _matches_path_parts(path_parts[index:], pattern_parts[1:])
            for index in range(len(path_parts) + 1)
        )
    if not path_parts:
        return False
    return fnmatch.fnmatchcase(path_parts[0], pattern_head) and _matches_path_parts(
        path_parts[1:],
        pattern_parts[1:],
    )


def _is_hidden_context_path(rel_path: str) -> bool:
    return any(part.startswith(".") for part in rel_path.split("/") if part)


def _hidden_context_explicitly_included(
    include: list[str] | None,
    matched_include_indexes: list[int],
) -> bool:
    if include is None:
        return False
    return any(
        _pattern_has_hidden_component(include[index])
        for index in matched_include_indexes
    )


def _pattern_has_hidden_component(pattern: str) -> bool:
    return any(part.startswith(".") for part in pattern.split("/") if part)


def _context_include_pattern_records(
    include: list[str] | None, match_counts: list[int], selected_counts: list[int]
) -> list[dict]:
    if include is None:
        return []
    return [
        {
            "pattern": pattern,
            "matches": match_counts[index],
            "selected_matches": selected_counts[index],
        }
        for index, pattern in enumerate(include)
    ]


def _read_context_source(
    path: Path,
    rel_path: str,
    max_chars: int,
    *,
    excerpt_policy: str,
    query_text: str = "",
    raw_rel_path: str | None = None,
    max_pdf_pages: int,
    max_pdf_chars: int,
) -> tuple[str, dict]:
    _validate_context_source_path(path, rel_path, raw_rel_path=raw_rel_path)
    source_type = path.suffix.lower().lstrip(".")
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        metadata = {
            "path": rel_path,
            "source_type": source_type,
            "sha256": None,
            "bytes": None,
            "chars_original": 0,
            "chars_rendered": 0,
            "truncated": False,
            "excerpt_start": 0,
            "excerpt_end": 0,
            "excerpt_policy": excerpt_policy,
            "max_chars": max_chars,
            "extraction_status": "read_error",
            "error_type": exc.__class__.__name__,
            "error": redact_sensitive_text(str(exc)),
        }
        if raw_rel_path is not None and raw_rel_path != rel_path:
            metadata["filesystem_path"] = raw_rel_path
        if _is_hidden_context_path(rel_path):
            metadata["hidden"] = True
        return "", metadata
    sha256 = hashlib.sha256(raw_bytes).hexdigest()
    if path.suffix.lower() == ".pdf":
        text, extraction = _read_pdf_text(
            path,
            max_pages=max_pdf_pages,
            max_chars=max_pdf_chars,
        )
    else:
        text, extraction = _read_text_context(raw_bytes)
    rendered, excerpt = _summarize_context_text(
        text,
        rel_path,
        max_chars,
        excerpt_policy=excerpt_policy,
        query_text=query_text,
    )
    if source_type == "pdf":
        excerpt_page_record = _pdf_excerpt_page_record(
            extraction.get("page_char_spans"),
            excerpt["start"],
            excerpt["end"],
            excerpt_spans=excerpt["spans"],
        )
        extraction = {**extraction, **excerpt_page_record}
    metadata = {
        "path": rel_path,
        "source_type": source_type,
        "sha256": sha256,
        "bytes": len(raw_bytes),
        "chars_original": len(text),
        "chars_rendered": len(rendered),
        "truncated": excerpt["truncated"],
        "excerpt_start": excerpt["start"],
        "excerpt_end": excerpt["end"],
        "excerpt_spans": excerpt["spans"],
        "excerpt_policy": excerpt["policy"],
        "omitted_chars": excerpt["omitted_chars"],
        "max_chars": max_chars,
        **extraction,
    }
    for key in (
        "ranking_policy",
        "ranking_fallback",
        "query_terms_sha256",
        "query_term_count",
        "selected_chunks",
        "omitted_chunk_count",
    ):
        if key in excerpt:
            metadata[f"excerpt_{key}"] = excerpt[key]
    if raw_rel_path is not None and raw_rel_path != rel_path:
        metadata["filesystem_path"] = raw_rel_path
    if _is_hidden_context_path(rel_path):
        metadata["hidden"] = True
    return rendered, metadata


def _context_display_path(rel_path: str) -> str:
    return unicodedata.normalize("NFC", rel_path)


def _validate_context_source_path(
    path: Path, rel_path: str, *, raw_rel_path: str | None = None
) -> None:
    if redact_sensitive_text(rel_path) != rel_path or (
        raw_rel_path is not None and redact_sensitive_text(raw_rel_path) != raw_rel_path
    ):
        raise ValueError(
            f"{path}: context source path must not contain secret-like text"
        )


def _read_text_context(raw_bytes: bytes) -> tuple[str, dict]:
    try:
        text = raw_bytes.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        return text, {"extraction_status": "ok"}
    except UnicodeDecodeError as exc:
        error = f"{exc.__class__.__name__}: {exc}"
        return (
            f"(text extraction failed: {error})",
            {"extraction_status": "failed", "error": error},
        )


def _read_pdf_text(path: Path, *, max_pages: int, max_chars: int) -> tuple[str, dict]:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        page_count = len(reader.pages)
        if page_count > max_pages:
            return "", {
                "extraction_status": "resource_limit",
                "error": f"PDF page count {page_count} exceeds max_pdf_pages {max_pages}",
                "pages": [1, page_count],
                "max_pdf_pages": max_pages,
            }
        segments: list[tuple[int, str]] = []
        extracted_chars = 0
        for index, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                extracted_chars += len(page_text)
                if extracted_chars > max_chars:
                    return "", {
                        "extraction_status": "resource_limit",
                        "error": (
                            f"PDF extracted text exceeds max_pdf_chars {max_chars}"
                        ),
                        "pages": [1, page_count],
                        "max_pdf_chars": max_chars,
                        "extracted_chars": extracted_chars,
                    }
                segments.append((index, page_text))
        if segments:
            parts: list[str] = []
            spans: list[dict] = []
            position = 0
            for segment_index, (page_number, page_text) in enumerate(segments):
                if segment_index > 0:
                    parts.append("\n")
                    position += 1
                start = position
                parts.append(page_text)
                position += len(page_text)
                spans.append({"page": page_number, "start": start, "end": position})
            text = "".join(parts)
            return text, {
                "extraction_status": "ok",
                "pages": [1, page_count],
                "extracted_pages": [page_number for page_number, _ in segments],
                "extracted_page_range": [segments[0][0], segments[-1][0]],
                "page_char_spans": spans,
            }
        return "(no extractable text)", {
            "extraction_status": "no_extractable_text",
            "pages": [1, page_count],
        }
    except Exception as exc:
        error = f"{exc.__class__.__name__}: {exc}"
        return (
            f"(PDF extraction failed: {error})",
            {"extraction_status": "failed", "error": error},
        )


def _pdf_excerpt_page_record(
    page_char_spans: object,
    excerpt_start: int,
    excerpt_end: int,
    *,
    excerpt_spans: list[dict] | None = None,
) -> dict:
    if not isinstance(page_char_spans, list) or not page_char_spans:
        return {}
    requested_spans = excerpt_spans or [{"start": excerpt_start, "end": excerpt_end}]
    overlaps = []
    for item in page_char_spans:
        if not isinstance(item, dict):
            continue
        page = item.get("page")
        start = item.get("start")
        end = item.get("end")
        if not isinstance(page, int) or not isinstance(start, int) or not isinstance(end, int):
            continue
        for requested in requested_spans:
            requested_start = requested.get("start")
            requested_end = requested.get("end")
            if not isinstance(requested_start, int) or not isinstance(requested_end, int):
                continue
            overlap_start = max(start, requested_start)
            overlap_end = min(end, requested_end)
            if overlap_start < overlap_end:
                page_local_start = overlap_start - start
                page_local_end = overlap_end - start
                overlaps.append({
                    "page": page,
                    "excerpt_start": overlap_start,
                    "excerpt_end": overlap_end,
                    "page_excerpt_start": page_local_start,
                    "page_excerpt_end": page_local_end,
                })
    if not overlaps:
        return {}
    return {
        "excerpt_pages": [item["page"] for item in overlaps],
        "excerpt_page_spans": overlaps,
    }


def _summarize_context_text(
    text: str,
    source: str,
    max_chars: int,
    *,
    excerpt_policy: str,
    query_text: str = "",
) -> tuple[str, dict]:
    if len(text) <= max_chars:
        return text, {
            "start": 0,
            "end": len(text),
            "spans": [{"start": 0, "end": len(text)}],
            "truncated": False,
            "policy": excerpt_policy,
            "omitted_chars": 0,
        }
    if excerpt_policy == "term_ranked":
        return _summarize_context_text_by_term_rank(
            text,
            source,
            max_chars,
            query_text=query_text,
        )
    if excerpt_policy == "head_tail":
        head_chars = (max_chars + 1) // 2
        tail_chars = max_chars - head_chars
        head = text[:head_chars]
        tail = text[-tail_chars:] if tail_chars > 0 else ""
        spans = [{"start": 0, "end": head_chars}]
        if tail_chars > 0:
            tail_start = len(text) - tail_chars
            spans.append({"start": tail_start, "end": len(text)})
        return (
            f"[{source}: showing first {head_chars} and last {tail_chars} "
            f"of {len(text)} characters]\n{head}\n...\n{tail}",
            {
                "start": 0,
                "end": len(text),
                "spans": spans,
                "truncated": True,
                "policy": excerpt_policy,
                "omitted_chars": len(text) - max_chars,
            },
        )
    return (
        f"[{source}: showing first {max_chars} of {len(text)} characters]\n"
        f"{text[:max_chars]}",
        {
            "start": 0,
            "end": max_chars,
            "spans": [{"start": 0, "end": max_chars}],
            "truncated": True,
            "policy": excerpt_policy,
            "omitted_chars": len(text) - max_chars,
        },
    )


def _summarize_context_text_by_term_rank(
    text: str,
    source: str,
    max_chars: int,
    *,
    query_text: str,
) -> tuple[str, dict]:
    query_terms = _context_excerpt_query_terms(query_text)
    query_hash = hashlib.sha256(
        " ".join(query_terms).encode("utf-8")
    ).hexdigest()
    if not query_terms:
        rendered, excerpt = _summarize_context_text(
            text,
            source,
            max_chars,
            excerpt_policy="head",
            query_text=query_text,
        )
        return rendered, {
            **excerpt,
            "policy": "term_ranked",
            "ranking_policy": "term_overlap_fixed_window_v1",
            "ranking_fallback": "head_empty_query_terms",
            "query_terms_sha256": query_hash,
            "query_term_count": 0,
            "selected_chunks": [],
            "omitted_chunk_count": 0,
        }
    chunks = _context_excerpt_chunks(text, max_chars)
    ranked = sorted(
        (
            {
                **chunk,
                "score": _context_excerpt_chunk_score(chunk["text"], query_terms),
            }
            for chunk in chunks
        ),
        key=lambda chunk: (-chunk["score"], chunk["start"], chunk["end"]),
    )
    selected = ranked[0]
    selected_text = text[selected["start"] : selected["end"]]
    omitted_count = max(0, len(chunks) - 1)
    rendered = (
        f"[{source}: showing term-ranked chunk {selected['index']} "
        f"({selected['start']}:{selected['end']}) of {len(text)} characters; "
        f"score={selected['score']}]\n{selected_text}"
    )
    selected_chunk = {
        "index": selected["index"],
        "start": selected["start"],
        "end": selected["end"],
        "score": selected["score"],
    }
    return rendered, {
        "start": selected["start"],
        "end": selected["end"],
        "spans": [{"start": selected["start"], "end": selected["end"]}],
        "truncated": True,
        "policy": "term_ranked",
        "omitted_chars": len(text) - len(selected_text),
        "ranking_policy": "term_overlap_fixed_window_v1",
        "query_terms_sha256": query_hash,
        "query_term_count": len(query_terms),
        "selected_chunks": [selected_chunk],
        "omitted_chunk_count": omitted_count,
    }


def _context_excerpt_query_terms(text: str) -> list[str]:
    terms = {
        match.group(0).lower()
        for match in re.finditer(r"[A-Za-z0-9_]{3,}", text)
    }
    return sorted(terms)[:256]


def _context_excerpt_chunks(text: str, max_chars: int) -> list[dict]:
    chunks = []
    for index, start in enumerate(range(0, len(text), max_chars)):
        end = min(len(text), start + max_chars)
        chunks.append({
            "index": index,
            "start": start,
            "end": end,
            "text": text[start:end],
        })
    return chunks


def _context_excerpt_chunk_score(text: str, query_terms: list[str]) -> int:
    chunk_terms = {
        match.group(0).lower()
        for match in re.finditer(r"[A-Za-z0-9_]{3,}", text)
    }
    return sum(1 for term in query_terms if term in chunk_terms)
