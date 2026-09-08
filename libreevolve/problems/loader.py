from __future__ import annotations
import base64
from dataclasses import dataclass, field
from types import MappingProxyType
from collections.abc import Mapping
import fnmatch
import hashlib
import math
from pathlib import Path
import re
import unicodedata
import yaml
from libreevolve.core.candidate import (
    CandidateWorkspace,
    DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES,
    normalize_candidate_path,
    validate_evolve_blocks,
)
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.core.yaml_utils import redacted_yaml_error, safe_load_unique

_SEED_POLICY_MANIFEST_NAMES = ("seed_policy.yaml", "seed_policy.yml")
_CONTEXT_MANIFEST_NAMES = ("context.yaml", "context.yml")
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
    if _problem_file_exists_or_is_invalid(validate_path):
        _require_problem_file(validate_path, "validate.py")
    elif not _problem_config_declares_embedded_only_evaluation(d):
        _require_problem_file(validate_path, "validate.py")
    seed_dir = d / "initial_programs"
    workspaces, seed_sources, seed_skipped, seed_policy = _load_initial_workspaces(seed_dir)
    seeds = [workspace.code for workspace in workspaces]
    if not seeds:
        detail = _seed_skipped_error_detail(seed_skipped)
        raise ValueError(
            f"No seed programs (*.py) or configured seed workspaces found in "
            f"{seed_dir}{detail}"
        )
    context_files, context_sources, context_policy = {}, [], {}
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
                   )


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
        if source not in {"evaluator", "final_fitness"}:
            raise ValueError(
                f"metrics.yaml in {problem_dir}: metric {name!r} source must be "
                "'evaluator' or 'final_fitness'"
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


def _problem_file_exists_or_is_invalid(path: Path) -> bool:
    if _is_link(path):
        return True
    try:
        return path.exists()
    except OSError:
        return True


def _problem_config_declares_embedded_only_evaluation(problem_dir: Path) -> bool:
    path = problem_dir / "config.yaml"
    if _is_link(path):
        return False
    try:
        if not path.exists() or not path.is_file():
            return False
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    try:
        raw = safe_load_unique(text) if text.strip() else {}
    except yaml.YAMLError:
        return False
    if not isinstance(raw, dict) or not all(isinstance(key, str) for key in raw):
        return False
    stages = raw.get("eval_stages")
    if not isinstance(stages, list) or not stages:
        return False
    for stage in stages:
        if (
            not isinstance(stage, dict)
            or not all(isinstance(key, str) for key in stage)
            or stage.get("mode") != "embedded_evaluate"
        ):
            return False
    return True


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
                preferred = _seed_workspace_primary_file(
                    files,
                    configured=seed_policy.get("primary_file"),
                )
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
    unsupported = sorted(set(raw) - {"include", "exclude", "primary_file"})
    if unsupported:
        raise ValueError(f"{policy_path}: unsupported seed policy fields {unsupported}")
    include = _seed_policy_pattern_list(policy_path, raw.get("include", []), "include")
    exclude = _seed_policy_pattern_list(policy_path, raw.get("exclude", []), "exclude")
    primary_file = _seed_policy_primary_file(policy_path, raw.get("primary_file"))
    return _seed_workspace_policy(
        policy_path.name,
        include=include,
        exclude=exclude,
        primary_file=primary_file,
    )


def _seed_workspace_policy(
    source: str | None,
    *,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    primary_file: str | None = None,
) -> dict:
    policy = {
        "policy": "skip_reserved_seed_paths_by_default",
        "reserved_components": ["dot-prefixed", "__pycache__"],
        "source": source,
        "include": list(include or []),
        "exclude": list(exclude or []),
        "exclude_precedence": True,
    }
    if primary_file is not None:
        policy["primary_file"] = primary_file
    return policy


def _seed_policy_primary_file(path: Path, value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{path}: seed policy primary_file must be a non-empty path")
    try:
        return normalize_candidate_path(value)
    except ValueError as exc:
        raise ValueError(
            f"{path}: seed policy primary_file must be a safe candidate path: {exc}"
        ) from exc


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


def _matches_any(rel_path: str, patterns: list[str]) -> bool:
    return any(_matches(rel_path, pattern) for pattern in patterns)


def _matches(rel_path: str, pattern: str) -> bool:
    path_parts = [part for part in unicodedata.normalize("NFC", rel_path).split("/") if part]
    pattern_parts = [part for part in unicodedata.normalize("NFC", pattern).split("/") if part]
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


def _seed_workspace_primary_file(
    files: dict[str, str],
    *,
    configured: object = None,
) -> str | None:
    if configured is not None:
        if not isinstance(configured, str) or configured not in files:
            raise ValueError(
                "Configured seed workspace primary_file is not present in every "
                f"seed directory: {configured!r}"
            )
        return configured
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
