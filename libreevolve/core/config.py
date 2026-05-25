from __future__ import annotations
from dataclasses import dataclass, field
import math


class ConfigError(ValueError):
    """Raised when a run configuration is invalid."""

@dataclass
class Config:
    # Evolution
    max_generations:        int   = 1000
    num_inspirations:       int   = 3
    eval_timeout_sec:       float = 60.0
    explore_ratio:          float = 0.3
    mutation_mode:          str   = "diff"
    eval_stages:            list[dict] = field(default_factory=list)
    prompt_variants:        list[str] = field(default_factory=list)
    meta_prompt_evolution:  bool  = False
    meta_prompt_interval:   int   = 25
    critique_enabled:       bool  = False
    critique_prompt:        str   = ""
    llm_feedback:           list[dict] = field(default_factory=list)
    # Population
    n_islands:              int   = 5
    migration_interval:     int   = 25
    migration_ratio:        float = 0.10
    map_elites_bins:        int   = 10
    elite_archive_size:     int   = 50
    # LLM
    backends:               list[dict] = field(default_factory=lambda: [
                                {"type": "anthropic", "model": "claude-sonnet-4-6"}
                            ])
    ensemble_explore_coeff: float = 1.0
    ensemble_strategy:      str   = "ucb1"
    # Plugins
    plugins:                list[str] = field(default_factory=list)
    # Logging
    log_dir:                str   = "runs/"
    problem_name:           str   = "unnamed"
    seed:                   int   = 42

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        _require_int("max_generations", self.max_generations, minimum=0)
        _require_int("num_inspirations", self.num_inspirations, minimum=0)
        _require_positive_number("eval_timeout_sec", self.eval_timeout_sec)
        _require_probability("explore_ratio", self.explore_ratio)
        _require_enum("mutation_mode", self.mutation_mode, {"diff", "full"})
        _require_int("meta_prompt_interval", self.meta_prompt_interval, minimum=0)
        _require_int("n_islands", self.n_islands, minimum=1)
        _require_int("migration_interval", self.migration_interval, minimum=0)
        _require_probability("migration_ratio", self.migration_ratio)
        _require_int("map_elites_bins", self.map_elites_bins, minimum=1)
        _require_int("elite_archive_size", self.elite_archive_size, minimum=1)
        _require_nonnegative_number("ensemble_explore_coeff", self.ensemble_explore_coeff)
        _require_enum("ensemble_strategy", self.ensemble_strategy, {"ucb1", "throughput_depth"})
        _validate_eval_stages(self.eval_stages)
        _validate_backends(self.backends)
        if not isinstance(self.prompt_variants, list) or not all(
            isinstance(item, str) for item in self.prompt_variants
        ):
            raise ConfigError("prompt_variants must be a list of strings")
        _validate_llm_feedback(self.llm_feedback)
        if not isinstance(self.plugins, list) or not all(isinstance(item, str) for item in self.plugins):
            raise ConfigError("plugins must be a list of strings")


def _require_int(name: str, value: object, minimum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ConfigError(f"{name} must be an integer >= {minimum}")


def _require_number(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{name} must be a finite number")
    value = float(value)
    if not math.isfinite(value):
        raise ConfigError(f"{name} must be a finite number")
    return value


def _require_positive_number(name: str, value: object) -> None:
    if _require_number(name, value) <= 0:
        raise ConfigError(f"{name} must be > 0")


def _require_nonnegative_number(name: str, value: object) -> None:
    if _require_number(name, value) < 0:
        raise ConfigError(f"{name} must be >= 0")


def _require_probability(name: str, value: object) -> None:
    numeric = _require_number(name, value)
    if numeric < 0.0 or numeric > 1.0:
        raise ConfigError(f"{name} must be between 0 and 1")


def _require_enum(name: str, value: object, allowed: set[str]) -> None:
    if value not in allowed:
        raise ConfigError(f"{name} must be one of {sorted(allowed)}, got {value!r}")


def _validate_eval_stages(stages: object) -> None:
    if not isinstance(stages, list):
        raise ConfigError("eval_stages must be a list of mappings")
    for index, stage in enumerate(stages):
        label = f"eval_stages[{index}]"
        if not isinstance(stage, dict):
            raise ConfigError(f"{label} must be a mapping")
        unsupported = sorted(set(stage) - {
            "name", "validate_path", "timeout_sec", "min_score", "samples", "seeds", "retries"
        })
        if unsupported:
            raise ConfigError(f"{label} has unsupported fields {unsupported}")
        if "timeout_sec" in stage:
            _require_positive_number(f"{label}.timeout_sec", stage["timeout_sec"])
        if "samples" in stage:
            _require_int(f"{label}.samples", stage["samples"], minimum=1)
        if "retries" in stage:
            _require_int(f"{label}.retries", stage["retries"], minimum=0)
        if "min_score" in stage:
            _require_number(f"{label}.min_score", stage["min_score"])
        if "seeds" in stage:
            if not isinstance(stage["seeds"], list):
                raise ConfigError(f"{label}.seeds must be a list")
            if "samples" in stage and stage["samples"] != len(stage["seeds"]):
                raise ConfigError(f"{label}.samples must match the number of seeds")


def _validate_backends(backends: object) -> None:
    if not isinstance(backends, list) or not backends:
        raise ConfigError("backends must be a non-empty list of mappings")
    allowed_types = {"anthropic", "openai", "ollama"}
    common_keys = {"type", "model", "max_tokens", "cost", "latency", "depth", "role"}
    for index, backend in enumerate(backends):
        label = f"backends[{index}]"
        if not isinstance(backend, dict):
            raise ConfigError(f"{label} must be a mapping")
        if backend.get("type") not in allowed_types:
            raise ConfigError(f"{label}.type must be one of {sorted(allowed_types)}")
        if not isinstance(backend.get("model"), str) or not backend["model"].strip():
            raise ConfigError(f"{label}.model must be a non-empty string")
        allowed = set(common_keys)
        if backend["type"] == "openai":
            allowed.add("reasoning_effort")
        unsupported = sorted(set(backend) - allowed)
        if unsupported:
            raise ConfigError(f"{label} has unsupported fields {unsupported}")
        if "max_tokens" in backend:
            _require_int(f"{label}.max_tokens", backend["max_tokens"], minimum=1)
        for field_name in ("cost", "latency", "depth"):
            if field_name in backend:
                _require_positive_number(f"{label}.{field_name}", backend[field_name])
        if "role" in backend and not isinstance(backend["role"], str):
            raise ConfigError(f"{label}.role must be a string")
        if "reasoning_effort" in backend:
            _require_enum(
                f"{label}.reasoning_effort",
                backend["reasoning_effort"],
                {"low", "medium", "high", "xhigh"},
            )


def _validate_llm_feedback(graders: object) -> None:
    if not isinstance(graders, list):
        raise ConfigError("llm_feedback must be a list of mappings")
    allowed = {"name", "metric", "weight", "min_score", "prompt", "include_invalid"}
    for index, grader in enumerate(graders):
        label = f"llm_feedback[{index}]"
        if not isinstance(grader, dict):
            raise ConfigError(f"{label} must be a mapping")
        unsupported = sorted(set(grader) - allowed)
        if unsupported:
            raise ConfigError(f"{label} has unsupported fields {unsupported}")
        for field_name in ("name", "metric", "prompt"):
            if field_name in grader and not isinstance(grader[field_name], str):
                raise ConfigError(f"{label}.{field_name} must be a string")
        if "weight" in grader:
            _require_number(f"{label}.weight", grader["weight"])
        if "min_score" in grader:
            _require_number(f"{label}.min_score", grader["min_score"])
        if "include_invalid" in grader and not isinstance(grader["include_invalid"], bool):
            raise ConfigError(f"{label}.include_invalid must be boolean")
