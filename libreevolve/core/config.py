from __future__ import annotations
from dataclasses import dataclass, field
import math
from uuid import uuid4


class ConfigError(ValueError):
    """Raised when a run configuration is invalid."""

@dataclass
class Config:
    # Evolution
    max_generations:        int   = 1000
    max_evaluations:        int | None = None
    max_evaluator_seconds:  float | None = None
    max_runtime_seconds:    float | None = None
    num_inspirations:       int   = 3
    eval_timeout_sec:       float = 60.0
    validator_env_allowlist: list[str] = field(default_factory=list)
    evaluator_artifact_include: list[str] = field(default_factory=list)
    evaluator_artifact_exclude: list[str] = field(default_factory=list)
    evaluator_artifact_max_files: int = 20
    evaluator_artifact_max_bytes: int = 1_000_000
    evaluator_artifact_redact_secrets: bool = True
    explore_ratio:          float = 0.3
    parent_selection_strategy: str = "mixed"
    inspiration_strategy:   str = "mixed"
    mutation_mode:          str   = "diff"
    eval_stages:            list[dict] = field(default_factory=list)
    prompt_variants:        list[str] = field(default_factory=list)
    meta_prompt_evolution:  bool  = False
    meta_prompt_interval:   int   = 25
    prompt_reward_mode:     str   = "absolute"
    prompt_reward_bounds:   list[float] = field(default_factory=lambda: [0.0, 1.0])
    prompt_explore_coeff:   float = 1.0
    critique_enabled:       bool  = False
    critique_prompt:        str   = ""
    llm_feedback:           list[dict] = field(default_factory=list)
    capture_proposal_metadata: bool = False
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
    llm_max_retries:        int   = 0
    llm_fallback:           bool  = True
    # Plugins
    plugins:                list[str] = field(default_factory=list)
    # Logging
    log_dir:                str   = "runs/"
    problem_name:           str   = "unnamed"
    run_id:                 str   = field(default_factory=lambda: uuid4().hex)
    run_collision_policy:   str   = "fail"
    seed:                   int   = 42

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        _require_int("max_generations", self.max_generations, minimum=0)
        _require_optional_int("max_evaluations", self.max_evaluations, minimum=0)
        _require_optional_positive_number("max_evaluator_seconds", self.max_evaluator_seconds)
        _require_optional_positive_number("max_runtime_seconds", self.max_runtime_seconds)
        _require_int("num_inspirations", self.num_inspirations, minimum=0)
        _require_positive_number("eval_timeout_sec", self.eval_timeout_sec)
        _validate_string_list("validator_env_allowlist", self.validator_env_allowlist)
        _validate_string_list("evaluator_artifact_include", self.evaluator_artifact_include)
        _validate_string_list("evaluator_artifact_exclude", self.evaluator_artifact_exclude)
        _require_int("evaluator_artifact_max_files", self.evaluator_artifact_max_files, minimum=0)
        _require_int("evaluator_artifact_max_bytes", self.evaluator_artifact_max_bytes, minimum=0)
        _require_bool("evaluator_artifact_redact_secrets", self.evaluator_artifact_redact_secrets)
        _require_probability("explore_ratio", self.explore_ratio)
        _require_enum(
            "parent_selection_strategy",
            self.parent_selection_strategy,
            {"mixed", "exploit", "explore", "metric", "novelty", "recency"},
        )
        _require_enum(
            "inspiration_strategy",
            self.inspiration_strategy,
            {"mixed", "random", "selection", "metric", "novelty", "recency"},
        )
        _require_enum("mutation_mode", self.mutation_mode, {"diff", "full"})
        _require_int("meta_prompt_interval", self.meta_prompt_interval, minimum=0)
        _require_enum("prompt_reward_mode", self.prompt_reward_mode, {"absolute", "improvement"})
        _validate_prompt_reward_bounds(self.prompt_reward_bounds)
        _require_nonnegative_number("prompt_explore_coeff", self.prompt_explore_coeff)
        _require_int("n_islands", self.n_islands, minimum=1)
        _require_int("migration_interval", self.migration_interval, minimum=0)
        _require_probability("migration_ratio", self.migration_ratio)
        _require_int("map_elites_bins", self.map_elites_bins, minimum=1)
        _require_int("elite_archive_size", self.elite_archive_size, minimum=1)
        _require_nonnegative_number("ensemble_explore_coeff", self.ensemble_explore_coeff)
        _require_enum("ensemble_strategy", self.ensemble_strategy, {"ucb1", "throughput_depth"})
        _require_int("llm_max_retries", self.llm_max_retries, minimum=0)
        _require_bool("llm_fallback", self.llm_fallback)
        _validate_eval_stages(self.eval_stages)
        _validate_backends(self.backends)
        if not isinstance(self.prompt_variants, list) or not all(
            isinstance(item, str) for item in self.prompt_variants
        ):
            raise ConfigError("prompt_variants must be a list of strings")
        _validate_prompt_variants(self.prompt_variants)
        _validate_llm_feedback(self.llm_feedback)
        _require_bool("capture_proposal_metadata", self.capture_proposal_metadata)
        if not isinstance(self.plugins, list) or not all(isinstance(item, str) for item in self.plugins):
            raise ConfigError("plugins must be a list of strings")
        if not isinstance(self.run_id, str) or not self.run_id.strip():
            raise ConfigError("run_id must be a non-empty string")
        _require_enum("run_collision_policy", self.run_collision_policy, {"fail", "overwrite"})


def _require_int(name: str, value: object, minimum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ConfigError(f"{name} must be an integer >= {minimum}")


def _require_optional_int(name: str, value: object, minimum: int) -> None:
    if value is not None:
        _require_int(name, value, minimum)


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


def _require_optional_positive_number(name: str, value: object) -> None:
    if value is not None:
        _require_positive_number(name, value)


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


def _require_bool(name: str, value: object) -> None:
    if not isinstance(value, bool):
        raise ConfigError(f"{name} must be boolean")


def _validate_string_list(name: str, value: object) -> None:
    if not isinstance(value, list):
        raise ConfigError(f"{name} must be a list of strings")
    for item in value:
        if not isinstance(item, str) or not item.strip() or "=" in item:
            raise ConfigError(f"{name} must be a list of non-empty environment variable names")


def _validate_eval_stages(stages: object) -> None:
    if not isinstance(stages, list):
        raise ConfigError("eval_stages must be a list of mappings")
    for index, stage in enumerate(stages):
        label = f"eval_stages[{index}]"
        if not isinstance(stage, dict):
            raise ConfigError(f"{label} must be a mapping")
        unsupported = sorted(set(stage) - {
            "name",
            "validate_path",
            "timeout_sec",
            "min_score",
            "samples",
            "seeds",
            "retries",
            "artifact_include",
            "artifact_exclude",
            "artifact_max_files",
            "artifact_max_bytes",
            "artifact_redact_secrets",
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
        if "artifact_include" in stage:
            _validate_string_list(f"{label}.artifact_include", stage["artifact_include"])
        if "artifact_exclude" in stage:
            _validate_string_list(f"{label}.artifact_exclude", stage["artifact_exclude"])
        if "artifact_max_files" in stage:
            _require_int(f"{label}.artifact_max_files", stage["artifact_max_files"], minimum=0)
        if "artifact_max_bytes" in stage:
            _require_int(f"{label}.artifact_max_bytes", stage["artifact_max_bytes"], minimum=0)
        if "artifact_redact_secrets" in stage:
            _require_bool(f"{label}.artifact_redact_secrets", stage["artifact_redact_secrets"])
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


def _validate_prompt_variants(variants: list[str]) -> None:
    from libreevolve.core.prompt import PromptTemplateError, validate_prompt_template

    for index, template in enumerate(variants):
        try:
            validate_prompt_template(template)
        except PromptTemplateError as exc:
            raise ConfigError(f"prompt_variants[{index}]: {exc}") from exc


def _validate_prompt_reward_bounds(bounds: object) -> None:
    if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
        raise ConfigError("prompt_reward_bounds must be [lo, hi]")
    lo = _require_number("prompt_reward_bounds[0]", bounds[0])
    hi = _require_number("prompt_reward_bounds[1]", bounds[1])
    if lo >= hi:
        raise ConfigError("prompt_reward_bounds must be strictly increasing [lo, hi]")
