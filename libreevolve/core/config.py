from __future__ import annotations
from dataclasses import dataclass, field
import math
import os
import re
import unicodedata
from pathlib import Path
from uuid import uuid4

from libreevolve.core.candidate import DEFAULT_MAX_CANDIDATE_FILE_CHARS, DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES, DEFAULT_MAX_CANDIDATE_TOTAL_CHARS, DEFAULT_MAX_CANDIDATE_TOTAL_STATIC_BYTES, DEFAULT_MAX_CANDIDATE_WORKSPACE_FILES, MUTATION_MODES
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.llm.client_context import validate_backend_client_context
from libreevolve.llm.request_params import (
    REQUEST_PARAMETER_FIELDS,
    validate_backend_request_parameters,
)
from libreevolve.llm.prompt_roles import validate_prompt_role_policy
from libreevolve.population.program import validate_program_metrics

_WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
MAX_LLM_RETRIES = 10
MAX_LLM_CALL_ATTEMPTS = 32
MAX_EVAL_STAGE_RETRIES = 10
MAX_EVALUATOR_STDIN_CHARS = 100_000
CONFIGURED_MUTATION_MODES = MUTATION_MODES
MAX_ADAPTIVE_MUTATION_FAILURE_SWITCH_COUNT = 5


class ConfigError(ValueError):
    """Raised when a run configuration is invalid."""

@dataclass
class Config:
    # Evolution
    max_generations:        int   = 3
    max_evaluations:        int | None = 4
    max_evaluator_seconds:  float | None = None
    max_evaluator_subprocess_attempts: int | None = None
    max_evaluator_stage_samples: int | None = None
    max_evaluator_retry_attempts: int | None = None
    max_evaluator_timeouts: int | None = None
    max_evaluator_sample_budget_exhaustions: int | None = None
    max_evaluator_stage_budget_exhaustions: int | None = None
    max_runtime_seconds:    float | None = 900.0
    proposals_per_generation: int = 1
    num_inspirations:       int   = 3
    eval_timeout_sec:       float = 10.0
    validator_env_allowlist: list[str] = field(default_factory=list)
    validator_network_policy: str = "host"
    evaluator_artifact_include: list[str] = field(default_factory=list)
    evaluator_artifact_exclude: list[str] = field(default_factory=list)
    evaluator_artifact_max_files: int = 20
    evaluator_artifact_max_bytes: int = 1_000_000
    evaluator_artifact_redact_secrets: bool = True
    evaluator_data_include: list[str] = field(default_factory=list)
    evaluator_data_exclude: list[str] = field(default_factory=list)
    evaluator_output_max_chars: int = 20_000
    evaluator_stdin_text: str | None = None
    evaluator_stdin_file: str | None = None
    explore_ratio:          float = 0.3
    parent_selection_strategy: str = "mixed"
    inspiration_strategy:   str = "mixed"
    mutation_mode:          str   = "full"
    initial_program_validity_policy: str = "permissive_baseline"
    max_candidate_workspace_files: int = DEFAULT_MAX_CANDIDATE_WORKSPACE_FILES
    max_candidate_file_chars: int = DEFAULT_MAX_CANDIDATE_FILE_CHARS
    max_candidate_total_chars: int = DEFAULT_MAX_CANDIDATE_TOTAL_CHARS
    max_candidate_static_file_bytes: int = DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES
    max_candidate_total_static_bytes: int = DEFAULT_MAX_CANDIDATE_TOTAL_STATIC_BYTES
    eval_stages:            list[dict] = field(default_factory=list)
    prompt_variants:        list[str] = field(default_factory=list)
    prompt_variant_semantic_policy: str = "alphaevolve"
    prompt_format_options:  dict = field(default_factory=dict)
    prompt_max_chars:       int | None = None
    prompt_max_estimated_tokens: int | None = None
    prompt_artifact_content_mode: str = "excerpt"
    prompt_artifact_content_max_bytes: int = 4096
    prompt_artifact_content_max_chars: int = 1000
    mutation_prompt_retention_mode: str = "redacted"
    explicit_context_retention_mode: str = "redacted"
    quarantine_snapshot_retention_mode: str = "redacted"
    prompt_reward_mode:     str   = "absolute"
    prompt_reward_bounds:   list[float] = field(default_factory=lambda: [0.0, 1.0])
    prompt_explore_coeff:   float = 1.0
    capture_proposal_metadata: bool = False
    # Population
    n_islands:              int   = 5
    migration_interval:     int   = 25
    migration_ratio:        float = 0.10
    map_elites_bins:        int   = 10
    map_elites_complexity_max_chars: int = 100_000
    map_elites_descriptor_axes: list[str] = field(
        default_factory=lambda: ["performance", "complexity", "diversity"]
    )
    elite_archive_size:     int   = 50
    # LLM
    backends:               list[dict] = field(default_factory=lambda: [
                                {"type": "codex", "model": "gpt-5.6-luna", "reasoning_effort": "high"}
                            ])
    ensemble_explore_coeff: float = 1.0
    ensemble_strategy:      str   = "ucb1"
    llm_max_retries:        int   = 0
    llm_max_call_attempts:  int   = 1
    llm_fallback:           bool  = False
    llm_max_response_chars: int   = 100_000
    llm_call_history_max:   int   = 500
    llm_call_timeout_sec:   float | None = None
    provider_response_retention_mode: str = "hash_only"
    provider_error_retention_mode: str = "redacted"
    max_llm_calls:          int | None = 3
    max_llm_provider_attempts: int | None = 3
    max_llm_tokens:         int | None = None
    max_llm_cost_microusd:  int | None = None
    max_llm_seconds:        float | None = None
    llm_role_call_limits:   dict[str, int] = field(default_factory=dict)
    llm_role_provider_attempt_limits: dict[str, int] = field(default_factory=dict)
    llm_role_token_limits:  dict[str, int] = field(default_factory=dict)
    llm_role_cost_microusd_limits: dict[str, int] = field(default_factory=dict)
    llm_role_seconds_limits: dict[str, float] = field(default_factory=dict)
    llm_reward_accounted_roles: list[str] = field(default_factory=lambda: ["mutation"])
    llm_role_scheduler_scope: str = "shared"
    llm_role_backend_indices: dict[str, list[int]] = field(default_factory=dict)
    llm_role_failure_quarantine_after: dict[str, int] = field(default_factory=dict)
    llm_prompt_roles:       dict  = field(default_factory=dict)
    # Plugins
    # Logging
    log_dir:                str   = "runs/"
    problem_name:           str   = "unnamed"
    run_id:                 str   = field(default_factory=lambda: uuid4().hex)
    run_collision_policy:   str   = "fail"
    seed:                   int   = 42

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        for name in ("max_evaluations", "max_runtime_seconds", "max_llm_calls", "max_llm_provider_attempts"):
            if getattr(self, name) is None:
                raise ConfigError(f"Engineering-preview runs require an explicit {name} limit")
        if self.max_llm_tokens is not None or self.max_llm_cost_microusd is not None or self.llm_role_token_limits or self.llm_role_cost_microusd_limits:
            raise ConfigError("Codex preview runs do not support token or dollar caps; subscription charges are unknown")
        _require_int("max_generations", self.max_generations, minimum=0)
        _require_optional_int("max_evaluations", self.max_evaluations, minimum=0)
        _require_optional_positive_number("max_evaluator_seconds", self.max_evaluator_seconds)
        _require_optional_int(
            "max_evaluator_subprocess_attempts",
            self.max_evaluator_subprocess_attempts,
            minimum=0,
        )
        _require_optional_int(
            "max_evaluator_stage_samples",
            self.max_evaluator_stage_samples,
            minimum=0,
        )
        _require_optional_int(
            "max_evaluator_retry_attempts",
            self.max_evaluator_retry_attempts,
            minimum=0,
        )
        _require_optional_int(
            "max_evaluator_timeouts",
            self.max_evaluator_timeouts,
            minimum=0,
        )
        _require_optional_int(
            "max_evaluator_sample_budget_exhaustions",
            self.max_evaluator_sample_budget_exhaustions,
            minimum=0,
        )
        _require_optional_int(
            "max_evaluator_stage_budget_exhaustions",
            self.max_evaluator_stage_budget_exhaustions,
            minimum=0,
        )
        _require_optional_positive_number("max_runtime_seconds", self.max_runtime_seconds)
        _require_int("proposals_per_generation", self.proposals_per_generation, minimum=1)
        _require_int("num_inspirations", self.num_inspirations, minimum=0)
        _require_positive_number("eval_timeout_sec", self.eval_timeout_sec)
        self.validator_network_policy = _validate_validator_network_policy(
            self.validator_network_policy
        )
        self.validator_env_allowlist = canonicalize_env_var_allowlist(
            "validator_env_allowlist",
            self.validator_env_allowlist,
        )
        _validate_artifact_glob_list("evaluator_artifact_include", self.evaluator_artifact_include)
        _validate_artifact_glob_list("evaluator_artifact_exclude", self.evaluator_artifact_exclude)
        _validate_artifact_glob_list("evaluator_data_include", self.evaluator_data_include)
        _validate_artifact_glob_list("evaluator_data_exclude", self.evaluator_data_exclude)
        _require_int("evaluator_artifact_max_files", self.evaluator_artifact_max_files, minimum=0)
        _require_int("evaluator_artifact_max_bytes", self.evaluator_artifact_max_bytes, minimum=0)
        _require_bool("evaluator_artifact_redact_secrets", self.evaluator_artifact_redact_secrets)
        _require_int("evaluator_output_max_chars", self.evaluator_output_max_chars, minimum=0)
        _validate_evaluator_stdin_text("evaluator_stdin_text", self.evaluator_stdin_text)
        _validate_evaluator_stdin_file("evaluator_stdin_file", self.evaluator_stdin_file)
        _validate_evaluator_stdin_source_exclusive(
            "evaluator_stdin",
            self.evaluator_stdin_text,
            self.evaluator_stdin_file,
        )
        _require_probability("explore_ratio", self.explore_ratio)
        _require_enum(
            "parent_selection_strategy",
            self.parent_selection_strategy,
            {
                "mixed",
                "exploit",
                "explore",
                "metric",
                "frontier",
                "lineage",
                "novelty",
                "recency",
            },
        )
        _require_enum(
            "inspiration_strategy",
            self.inspiration_strategy,
            {
                "mixed",
                "random",
                "selection",
                "metric",
                "frontier",
                "lineage",
                "novelty",
                "recency",
            },
        )
        _require_enum(
            "mutation_mode",
            self.mutation_mode,
            CONFIGURED_MUTATION_MODES,
        )
        _require_enum(
            "initial_program_validity_policy",
            self.initial_program_validity_policy,
            {"permissive_baseline", "alphaevolve_strict"},
        )
        _require_int(
            "max_candidate_workspace_files",
            self.max_candidate_workspace_files,
            minimum=1,
        )
        _require_int("max_candidate_file_chars", self.max_candidate_file_chars, minimum=0)
        _require_int("max_candidate_total_chars", self.max_candidate_total_chars, minimum=0)
        _require_int(
            "max_candidate_static_file_bytes",
            self.max_candidate_static_file_bytes,
            minimum=0,
        )
        _require_int(
            "max_candidate_total_static_bytes",
            self.max_candidate_total_static_bytes,
            minimum=0,
        )
        _require_enum("prompt_reward_mode", self.prompt_reward_mode, {"absolute", "improvement"})
        _validate_prompt_reward_bounds(self.prompt_reward_bounds)
        _require_nonnegative_number("prompt_explore_coeff", self.prompt_explore_coeff)
        _require_int("n_islands", self.n_islands, minimum=1)
        _require_int("migration_interval", self.migration_interval, minimum=0)
        _require_probability("migration_ratio", self.migration_ratio)
        _require_int("map_elites_bins", self.map_elites_bins, minimum=1)
        _require_int(
            "map_elites_complexity_max_chars",
            self.map_elites_complexity_max_chars,
            minimum=1,
        )
        self.map_elites_descriptor_axes = _validate_map_elites_descriptor_axes(
            self.map_elites_descriptor_axes
        )
        _require_int("elite_archive_size", self.elite_archive_size, minimum=1)
        _require_nonnegative_number("ensemble_explore_coeff", self.ensemble_explore_coeff)
        _require_enum("ensemble_strategy", self.ensemble_strategy, {"ucb1", "throughput_depth"})
        _require_int("llm_max_retries", self.llm_max_retries, minimum=0)
        if self.llm_max_retries > MAX_LLM_RETRIES:
            raise ConfigError(f"llm_max_retries must be <= {MAX_LLM_RETRIES}")
        _require_int("llm_max_call_attempts", self.llm_max_call_attempts, minimum=1)
        if self.llm_max_call_attempts > MAX_LLM_CALL_ATTEMPTS:
            raise ConfigError(
                f"llm_max_call_attempts must be <= {MAX_LLM_CALL_ATTEMPTS}"
            )
        _require_bool("llm_fallback", self.llm_fallback)
        _require_int("llm_max_response_chars", self.llm_max_response_chars, minimum=1)
        _require_int("llm_call_history_max", self.llm_call_history_max, minimum=1)
        _require_optional_positive_number("llm_call_timeout_sec", self.llm_call_timeout_sec)
        _require_enum(
            "provider_response_retention_mode",
            self.provider_response_retention_mode,
            {"full", "redacted", "hash_only", "off"},
        )
        _require_enum(
            "provider_error_retention_mode",
            self.provider_error_retention_mode,
            {"full", "redacted", "hash_only", "off"},
        )
        _require_optional_int("max_llm_calls", self.max_llm_calls, minimum=0)
        _require_optional_int(
            "max_llm_provider_attempts",
            self.max_llm_provider_attempts,
            minimum=0,
        )
        _require_optional_int("max_llm_tokens", self.max_llm_tokens, minimum=0)
        _require_optional_int(
            "max_llm_cost_microusd",
            self.max_llm_cost_microusd,
            minimum=0,
        )
        if self.max_llm_seconds is not None:
            _require_nonnegative_number("max_llm_seconds", self.max_llm_seconds)
        self.llm_role_call_limits = _validate_llm_role_call_limits(
            self.llm_role_call_limits
        )
        self.llm_role_provider_attempt_limits = _validate_llm_role_budget_limits(
            self.llm_role_provider_attempt_limits,
            field="llm_role_provider_attempt_limits",
        )
        self.llm_role_token_limits = _validate_llm_role_budget_limits(
            self.llm_role_token_limits,
            field="llm_role_token_limits",
        )
        self.llm_role_cost_microusd_limits = _validate_llm_role_budget_limits(
            self.llm_role_cost_microusd_limits,
            field="llm_role_cost_microusd_limits",
        )
        self.llm_role_seconds_limits = _validate_llm_role_seconds_limits(
            self.llm_role_seconds_limits
        )
        self.llm_reward_accounted_roles = _validate_llm_reward_accounted_roles(
            self.llm_reward_accounted_roles
        )
        self.llm_role_scheduler_scope = _validate_llm_role_scheduler_scope(
            self.llm_role_scheduler_scope
        )
        self.llm_prompt_roles = _validate_llm_prompt_roles(self.llm_prompt_roles)
        _validate_eval_stages(self.eval_stages)
        _validate_backends(self.backends)
        self.llm_role_backend_indices = _validate_llm_role_backend_indices(
            self.llm_role_backend_indices,
            backend_count=len(self.backends),
        )
        self.llm_role_failure_quarantine_after = (
            _validate_llm_role_failure_quarantine_after(
                self.llm_role_failure_quarantine_after
            )
        )
        if not isinstance(self.prompt_variants, list) or not all(
            isinstance(item, str) for item in self.prompt_variants
        ):
            raise ConfigError("prompt_variants must be a list of strings")
        self.prompt_variant_semantic_policy = _validate_prompt_variant_semantic_policy(
            self.prompt_variant_semantic_policy
        )
        self.prompt_format_options = _validate_prompt_format_options(
            self.prompt_format_options
        )
        _validate_prompt_variants(
            self.prompt_variants,
            self.prompt_format_options,
            semantic_policy=self.prompt_variant_semantic_policy,
        )
        _require_optional_int("prompt_max_chars", self.prompt_max_chars, minimum=1)
        _require_optional_int(
            "prompt_max_estimated_tokens",
            self.prompt_max_estimated_tokens,
            minimum=1,
        )
        _require_enum(
            "prompt_artifact_content_mode",
            self.prompt_artifact_content_mode,
            {"excerpt", "bounded_file", "off"},
        )
        _require_int(
            "prompt_artifact_content_max_bytes",
            self.prompt_artifact_content_max_bytes,
            minimum=1,
        )
        _require_int(
            "prompt_artifact_content_max_chars",
            self.prompt_artifact_content_max_chars,
            minimum=1,
        )
        _require_enum(
            "mutation_prompt_retention_mode",
            self.mutation_prompt_retention_mode,
            {"full", "redacted", "hash_only", "off"},
        )
        _require_enum(
            "explicit_context_retention_mode",
            self.explicit_context_retention_mode,
            {"full", "redacted", "hash_only", "off"},
        )
        _require_enum(
            "quarantine_snapshot_retention_mode",
            self.quarantine_snapshot_retention_mode,
            {"full", "redacted", "hash_only", "off"},
        )
        _require_bool("capture_proposal_metadata", self.capture_proposal_metadata)
        self.log_dir = _normalize_path_string("log_dir", self.log_dir)
        self.problem_name = _require_run_name_component("problem_name", self.problem_name)
        _require_integer("seed", self.seed)
        self.run_id = _require_safe_identifier("run_id", self.run_id)
        _require_enum("run_collision_policy", self.run_collision_policy, {"fail", "overwrite"})


def _require_integer(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"{name} must be an integer")


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


def _require_string(name: str, value: object, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise ConfigError(f"{name} must be a string")
    if not allow_empty and not value.strip():
        raise ConfigError(f"{name} must be a non-empty string")
    return value


def _validate_evaluator_stdin_text(name: str, value: object) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        raise ConfigError(f"{name} must be a string or null")
    if len(value) > MAX_EVALUATOR_STDIN_CHARS:
        raise ConfigError(
            f"{name} must be <= {MAX_EVALUATOR_STDIN_CHARS} characters"
        )


def _validate_evaluator_stdin_file(name: str, value: object) -> None:
    if value is None:
        return
    _require_string(name, value)


def _validate_evaluator_stdin_source_exclusive(
    name: str,
    stdin_text: object,
    stdin_file: object,
) -> None:
    if stdin_text is not None and stdin_file is not None:
        raise ConfigError(f"{name} must not set both stdin_text and stdin_file")


def _normalize_path_string(name: str, value: object) -> str:
    if not isinstance(value, (str, os.PathLike)):
        raise ConfigError(f"{name} must be a non-empty path string")
    path = os.fspath(value)
    if not isinstance(path, str) or not path.strip():
        raise ConfigError(f"{name} must be a non-empty path string")
    if name == "log_dir":
        _validate_log_dir_path(path)
    return path


def _validate_log_dir_path(path: str) -> None:
    normalized = unicodedata.normalize("NFC", path)
    if normalized != path:
        raise ConfigError("log_dir must be a path-safe log directory")
    if path != path.strip():
        raise ConfigError("log_dir must be a path-safe log directory")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in path):
        raise ConfigError("log_dir must be a path-safe log directory")
    if any(unicodedata.category(ch) == "Cf" for ch in path):
        raise ConfigError("log_dir must be a display-safe log directory")
    parsed = Path(path)
    anchor = parsed.anchor
    for part in parsed.parts:
        if part == anchor:
            continue
        _validate_log_dir_component(part)


def _validate_log_dir_component(part: str) -> None:
    if part in {"", ".", ".."}:
        raise ConfigError("log_dir must be a path-safe log directory")
    if part != part.strip() or part.endswith("."):
        raise ConfigError("log_dir must be a path-safe log directory")
    if any(ch in part for ch in '<>:"|?*'):
        raise ConfigError("log_dir must be a path-safe log directory")
    stem = part.split(".", 1)[0].upper()
    if stem in _WINDOWS_RESERVED_NAMES:
        raise ConfigError("log_dir must be a path-safe log directory")


def _require_run_name_component(name: str, value: object) -> str:
    run_name = _require_string(name, value)
    if redact_sensitive_text(run_name) != run_name:
        raise ConfigError(f"{name} must be a secret-safe run-name component")
    normalized = unicodedata.normalize("NFC", run_name)
    if normalized != run_name:
        raise ConfigError(f"{name} must be a safe run-name component")
    if run_name != run_name.strip() or run_name.endswith("."):
        raise ConfigError(f"{name} must be a safe run-name component")
    if run_name in {".", ".."} or "/" in run_name or "\\" in run_name:
        raise ConfigError(f"{name} must be a safe run-name component")
    if any(ch in run_name for ch in '<>:"|?*') or any(ord(ch) < 32 or ord(ch) == 127 for ch in run_name):
        raise ConfigError(f"{name} must be a safe run-name component")
    if any(unicodedata.category(ch) == "Cf" for ch in run_name):
        raise ConfigError(f"{name} must be a safe run-name component")
    stem = run_name.split(".", 1)[0].upper()
    if stem in _WINDOWS_RESERVED_NAMES:
        raise ConfigError(f"{name} must be a safe run-name component")
    return run_name


def _require_safe_identifier(name: str, value: object) -> str:
    identifier = _require_string(name, value)
    if redact_sensitive_text(identifier) != identifier:
        raise ConfigError(f"{name} must be a manifest-safe identifier")
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", identifier) is None:
        raise ConfigError(f"{name} must be a manifest-safe identifier")
    return identifier


def _require_model_identifier(name: str, value: object) -> str:
    model = _require_string(name, value)
    if redact_sensitive_text(model) != model:
        raise ConfigError(f"{name} must be a manifest-safe model identifier")
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:/+-]{0,191}", model) is None:
        raise ConfigError(f"{name} must be a manifest-safe model identifier")
    return model


def _require_stage_label(name: str, value: object) -> str:
    label = _require_string(name, value)
    if redact_sensitive_text(label) != label:
        raise ConfigError(f"{name} must be a manifest-safe stage label")
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", label) is None:
        raise ConfigError(f"{name} must be a manifest-safe stage label")
    return label


def _require_role_label(name: str, value: object) -> str:
    if not isinstance(value, str):
        raise ConfigError(f"{name} must be a string")
    label = value
    if redact_sensitive_text(label) != label:
        raise ConfigError(f"{name} must be a manifest-safe role label")
    if re.fullmatch(r"(?!.*::)(?!.*:$)[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", label) is None:
        raise ConfigError(f"{name} must be a manifest-safe role label")
    return label


def _require_role_scope_label(name: str, value: object) -> str:
    if isinstance(value, str) and value.endswith(":*"):
        prefix = value[:-2]
        _require_role_label(name, prefix)
        return value
    return _require_role_label(name, value)


def _require_feedback_metric_label(name: str, value: object) -> str:
    if not isinstance(value, str):
        raise ConfigError(f"{name} must be a string")
    try:
        validate_program_metrics({value: 0.0})
    except ValueError as exc:
        raise ConfigError(f"{name} must be a manifest-safe metric name") from exc
    return value


def canonicalize_env_var_allowlist(name: str, value: object) -> list[str]:
    if not isinstance(value, list):
        raise ConfigError(f"{name} must be a list of strings")
    canonical: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            raise ConfigError(f"{name} must be a list of environment variable names")
        env_name = item.strip().upper()
        if re.fullmatch(r"[A-Z_][A-Z0-9_]{0,127}", env_name) is None:
            raise ConfigError(f"{name} must be a list of manifest-safe environment variable names")
        if env_name not in seen:
            seen.add(env_name)
            canonical.append(env_name)
    return canonical


def _validate_artifact_glob_list(name: str, value: object) -> None:
    if not isinstance(value, list):
        raise ConfigError(f"{name} must be a list of glob patterns")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ConfigError(f"{name} must be a list of non-empty glob patterns")
        if item != item.strip():
            raise ConfigError(f"{name} must be a list of path-safe glob patterns")
        if _has_unicode_format_control(item):
            raise ConfigError(f"{name} must be a list of display-safe glob patterns")
        if redact_sensitive_text(item) != item:
            raise ConfigError(f"{name} must be a list of manifest-safe glob patterns")
        _validate_artifact_glob_path(name, item)


def _validate_artifact_glob_path(name: str, pattern: str) -> None:
    if "\\" in pattern:
        raise ConfigError(f"{name} must be a list of path-safe glob patterns")
    if pattern.startswith("/"):
        raise ConfigError(f"{name} must be a list of path-safe glob patterns")
    if re.match(r"^[A-Za-z]:", pattern):
        raise ConfigError(f"{name} must be a list of path-safe glob patterns")
    parts = pattern.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ConfigError(f"{name} must be a list of path-safe glob patterns")


def _require_json_scalar(name: str, value: object) -> None:
    if value is None:
        return
    if isinstance(value, str):
        if redact_sensitive_text(value) != value:
            raise ConfigError(f"{name} must be a share-safe scalar seed")
        return
    if isinstance(value, bool):
        raise ConfigError(f"{name} must be a JSON-safe scalar seed")
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return
    raise ConfigError(f"{name} must be a JSON-safe scalar seed")


def _validate_json_safe_config_value(name: str, value: object) -> None:
    if value is None:
        return
    if isinstance(value, str):
        if redact_sensitive_text(value) != value:
            raise ConfigError(f"{name} must be JSON-safe config")
        if _has_unicode_format_control(value):
            raise ConfigError(f"{name} must be JSON-safe config")
        return
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ConfigError(f"{name} must be JSON-safe config")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_safe_config_value(f"{name}[{index}]", item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ConfigError(f"{name} keys must be strings")
            if redact_sensitive_text(key) != key or _has_unicode_format_control(key):
                raise ConfigError(f"{name} keys must be manifest-safe labels")
            _validate_json_safe_config_value(f"{name}.{key}", item)
        return
    raise ConfigError(f"{name} must be JSON-safe config")


def _validate_validator_network_policy(value: object) -> str:
    if not isinstance(value, str):
        raise ConfigError("validator_network_policy must be one of: host, deny")
    normalized = value.strip().lower()
    if normalized not in {"host", "deny"}:
        raise ConfigError("validator_network_policy must be one of: host, deny")
    return normalized


def _validate_map_elites_descriptor_axes(value: object) -> list[str]:
    field = "map_elites_descriptor_axes"
    if not isinstance(value, list) or len(value) != 3:
        raise ConfigError(f"{field} must be a list of exactly three descriptor axes")
    normalized: list[str] = []
    seen: set[str] = set()
    for index, raw_axis in enumerate(value):
        if not isinstance(raw_axis, str):
            raise ConfigError(f"{field}[{index}] must be a descriptor axis string")
        axis = raw_axis.strip()
        if not axis:
            raise ConfigError(f"{field}[{index}] must be a descriptor axis string")
        if axis in {"performance", "complexity", "diversity"}:
            normalized_axis = axis
        elif axis.startswith("metric:"):
            metric = _require_feedback_metric_label(f"{field}[{index}]", axis.split(":", 1)[1])
            normalized_axis = f"metric:{metric}"
        elif axis.startswith("evaluation_metadata:"):
            path = _require_descriptor_metadata_path(
                f"{field}[{index}]",
                axis.split(":", 1)[1],
            )
            normalized_axis = f"evaluation_metadata:{path}"
        elif axis.startswith("candidate_metadata:"):
            path = _require_descriptor_metadata_path(
                f"{field}[{index}]",
                axis.split(":", 1)[1],
            )
            normalized_axis = f"candidate_metadata:{path}"
        else:
            raise ConfigError(
                f"{field}[{index}] must be one of performance, complexity, diversity, "
                "metric:<name>, evaluation_metadata:<path>, or candidate_metadata:<path>"
            )
        if normalized_axis in seen:
            raise ConfigError(f"{field} must not contain duplicate descriptor axes")
        seen.add(normalized_axis)
        normalized.append(normalized_axis)
    return normalized


def _require_descriptor_metadata_path(name: str, value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{name} must be a manifest-safe metadata path")
    parts = value.split(".")
    if not parts:
        raise ConfigError(f"{name} must be a manifest-safe metadata path")
    for part in parts:
        _require_stage_label(name, part)
    return ".".join(parts)


def _validate_eval_stages(stages: object) -> None:
    if not isinstance(stages, list):
        raise ConfigError("eval_stages must be a list of mappings")
    reserved_stage_names = {"diff", "syntax", "validate"}
    stage_names: set[str] = set(reserved_stage_names)
    provenance_levels: list[int] = []
    for index, stage in enumerate(stages):
        label = f"eval_stages[{index}]"
        if not isinstance(stage, dict):
            raise ConfigError(f"{label} must be a mapping")
        unsupported = _unsupported_mapping_keys(label, stage, {
            "name",
            "role",
            "difficulty_or_scale",
            "test_set",
            "mode",
            "language_runner",
            "build_system",
            "validate_path",
            "eval_inputs",
            "timeout_sec",
            "max_sample_seconds",
            "max_stage_seconds",
            "min_score",
            "metric_aggregation",
            "metric_thresholds",
            "hypothesis_test",
            "min_artifacts",
            "program_output_checks",
            "require_program_output",
            "required_artifacts",
            "samples",
            "sample_workers",
            "seeds",
            "retries",
            "artifact_include",
            "artifact_exclude",
            "artifact_max_files",
            "artifact_max_bytes",
            "artifact_redact_secrets",
            "data_include",
            "data_exclude",
            "stdin_text",
            "stdin_file",
            "workload",
        })
        if unsupported:
            raise ConfigError(f"{label} has unsupported fields {unsupported}")
        mode = str(stage.get("mode", "external_validator"))
        if "mode" in stage:
            _require_enum(
                f"{label}.mode",
                stage["mode"],
                {"external_validator", "embedded_evaluate"},
            )
        if mode == "embedded_evaluate":
            if "validate_path" in stage:
                raise ConfigError(f"{label}.validate_path is not supported for embedded_evaluate stages")
            if "stdin_text" in stage or "stdin_file" in stage:
                raise ConfigError(f"{label}.stdin is not supported for embedded_evaluate stages")
            if "data_include" in stage or "data_exclude" in stage:
                raise ConfigError(f"{label}.data_include/data_exclude are not supported for embedded_evaluate stages")
        elif "eval_inputs" in stage:
            raise ConfigError(f"{label}.eval_inputs requires mode='embedded_evaluate'")
        if mode != "candidate_runner" and (
            "language_runner" in stage or "build_system" in stage
        ):
            raise ConfigError(
                f"{label}.language_runner/build_system require mode='candidate_runner'"
            )
        if "language_runner" in stage:
            _require_safe_identifier(
                f"{label}.language_runner", stage["language_runner"]
            )
        if "build_system" in stage:
            _require_safe_identifier(f"{label}.build_system", stage["build_system"])
        if "name" in stage:
            name = _require_stage_label(f"{label}.name", stage["name"])
            if name in stage_names:
                if name in reserved_stage_names:
                    raise ConfigError(f"{label}.name is reserved for a built-in eval stage: {name!r}")
                raise ConfigError(f"{label}.name duplicates an earlier eval stage: {name!r}")
            stage_names.add(name)
        if "role" in stage:
            _require_enum(
                f"{label}.role",
                stage["role"],
                {"small_scale_filter", "intermediate_filter", "main_test"},
            )
        has_difficulty = "difficulty_or_scale" in stage
        has_test_set = "test_set" in stage
        if has_difficulty != has_test_set:
            raise ConfigError(
                f"{label}.difficulty_or_scale and {label}.test_set must be "
                "configured together"
            )
        if has_difficulty:
            provenance_levels.append(
                _validate_stage_difficulty_or_scale(
                    f"{label}.difficulty_or_scale",
                    stage["difficulty_or_scale"],
                )
            )
            _validate_stage_test_set(
                f"{label}.test_set",
                stage["test_set"],
                stage,
            )
        if "validate_path" in stage:
            _require_string(f"{label}.validate_path", stage["validate_path"])
        if "eval_inputs" in stage:
            _validate_json_safe_config_value(f"{label}.eval_inputs", stage["eval_inputs"])
        if "timeout_sec" in stage:
            _require_positive_number(f"{label}.timeout_sec", stage["timeout_sec"])
        if "max_sample_seconds" in stage:
            _require_positive_number(f"{label}.max_sample_seconds", stage["max_sample_seconds"])
        if "max_stage_seconds" in stage:
            _require_positive_number(f"{label}.max_stage_seconds", stage["max_stage_seconds"])
        if "samples" in stage:
            _require_int(f"{label}.samples", stage["samples"], minimum=1)
        if "sample_workers" in stage:
            _require_int(f"{label}.sample_workers", stage["sample_workers"], minimum=1)
        if "retries" in stage:
            _require_int(f"{label}.retries", stage["retries"], minimum=0)
            if stage["retries"] > MAX_EVAL_STAGE_RETRIES:
                raise ConfigError(f"{label}.retries must be <= {MAX_EVAL_STAGE_RETRIES}")
        if "min_score" in stage:
            _require_number(f"{label}.min_score", stage["min_score"])
        if "metric_aggregation" in stage:
            _validate_metric_aggregation(f"{label}.metric_aggregation", stage["metric_aggregation"])
        if "metric_thresholds" in stage:
            _validate_metric_thresholds(f"{label}.metric_thresholds", stage["metric_thresholds"])
        if "hypothesis_test" in stage:
            _validate_stage_hypothesis_test(
                f"{label}.hypothesis_test",
                stage["hypothesis_test"],
                stage.get("samples"),
            )
            if (
                stage.get("sample_workers", 1) > 1
                and isinstance(stage["hypothesis_test"], dict)
                and stage["hypothesis_test"].get("sequential_stopping") is True
            ):
                raise ConfigError(
                    f"{label}.sample_workers is incompatible with "
                    "hypothesis_test.sequential_stopping"
                )
        if "min_artifacts" in stage:
            _require_int(f"{label}.min_artifacts", stage["min_artifacts"], minimum=0)
        if "require_program_output" in stage:
            _require_bool(f"{label}.require_program_output", stage["require_program_output"])
        if "required_artifacts" in stage:
            _validate_artifact_glob_list(f"{label}.required_artifacts", stage["required_artifacts"])
        if "program_output_checks" in stage:
            _validate_program_output_checks(f"{label}.program_output_checks", stage["program_output_checks"])
        if "artifact_include" in stage:
            _validate_artifact_glob_list(f"{label}.artifact_include", stage["artifact_include"])
        if "artifact_exclude" in stage:
            _validate_artifact_glob_list(f"{label}.artifact_exclude", stage["artifact_exclude"])
        if "artifact_max_files" in stage:
            _require_int(f"{label}.artifact_max_files", stage["artifact_max_files"], minimum=0)
        if "artifact_max_bytes" in stage:
            _require_int(f"{label}.artifact_max_bytes", stage["artifact_max_bytes"], minimum=0)
        if "artifact_redact_secrets" in stage:
            _require_bool(f"{label}.artifact_redact_secrets", stage["artifact_redact_secrets"])
        if "data_include" in stage:
            _validate_artifact_glob_list(f"{label}.data_include", stage["data_include"])
        if "data_exclude" in stage:
            _validate_artifact_glob_list(f"{label}.data_exclude", stage["data_exclude"])
        if "stdin_text" in stage:
            _validate_evaluator_stdin_text(f"{label}.stdin_text", stage["stdin_text"])
        if "stdin_file" in stage:
            _validate_evaluator_stdin_file(f"{label}.stdin_file", stage["stdin_file"])
        _validate_evaluator_stdin_source_exclusive(
            f"{label}.stdin",
            stage.get("stdin_text"),
            stage.get("stdin_file"),
        )
        if "workload" in stage:
            _validate_evaluator_workload(f"{label}.workload", stage["workload"])
        if "seeds" in stage:
            if not isinstance(stage["seeds"], list):
                raise ConfigError(f"{label}.seeds must be a list")
            for seed_index, seed in enumerate(stage["seeds"]):
                _require_json_scalar(f"{label}.seeds[{seed_index}]", seed)
            if "samples" in stage and stage["samples"] != len(stage["seeds"]):
                raise ConfigError(f"{label}.samples must match the number of seeds")
        if "name" not in stage:
            raise ConfigError(f"{label}.name is required for configured eval stages")
    if provenance_levels:
        if len(provenance_levels) != len(stages):
            raise ConfigError(
                "eval_stages difficulty_or_scale/test_set provenance must be "
                "configured for every stage"
            )
        if any(
            current <= previous
            for previous, current in zip(provenance_levels, provenance_levels[1:])
        ):
            raise ConfigError(
                "eval_stages difficulty_or_scale.level values must be strictly "
                "increasing"
            )


def _validate_stage_difficulty_or_scale(label: str, value: object) -> int:
    if not isinstance(value, dict):
        raise ConfigError(f"{label} must be a mapping")
    unsupported = _unsupported_mapping_keys(
        label,
        value,
        {"label", "level", "rationale", "estimated_cost"},
    )
    if unsupported:
        raise ConfigError(f"{label} has unsupported fields {unsupported}")
    for field in ("label", "level", "rationale"):
        if field not in value:
            raise ConfigError(f"{label}.{field} is required")
    _require_stage_label(f"{label}.label", value["label"])
    _require_int(f"{label}.level", value["level"], minimum=0)
    _require_string(f"{label}.rationale", value["rationale"])
    if "estimated_cost" in value:
        _require_positive_number(
            f"{label}.estimated_cost",
            value["estimated_cost"],
        )
    return int(value["level"])


def _validate_stage_test_set(
    label: str,
    value: object,
    stage: dict,
) -> None:
    if not isinstance(value, dict):
        raise ConfigError(f"{label} must be a mapping")
    unsupported = _unsupported_mapping_keys(
        label,
        value,
        {
            "id",
            "source",
            "split",
            "expected_file_count",
            "expected_aggregate_sha256",
        },
    )
    if unsupported:
        raise ConfigError(f"{label} has unsupported fields {unsupported}")
    for field in ("id", "source"):
        if field not in value:
            raise ConfigError(f"{label}.{field} is required")
    _require_stage_label(f"{label}.id", value["id"])
    _require_enum(
        f"{label}.source",
        value["source"],
        {"declared_data", "eval_inputs"},
    )
    source = value["source"]
    if "split" in value:
        _require_stage_label(f"{label}.split", value["split"])
    if "expected_file_count" in value:
        _require_int(
            f"{label}.expected_file_count",
            value["expected_file_count"],
            minimum=1,
        )
    if "expected_aggregate_sha256" in value:
        _require_sha256(
            f"{label}.expected_aggregate_sha256",
            value["expected_aggregate_sha256"],
        )
    if source == "declared_data":
        if not isinstance(stage.get("data_include"), list) or not stage["data_include"]:
            raise ConfigError(
                f"{label}.source='declared_data' requires stage data_include"
            )
    else:
        if "expected_file_count" in value:
            raise ConfigError(
                f"{label}.expected_file_count is unsupported for eval_inputs"
            )
        if stage.get("mode") != "embedded_evaluate" or "eval_inputs" not in stage:
            raise ConfigError(
                f"{label}.source='eval_inputs' requires mode='embedded_evaluate' "
                "and eval_inputs"
            )


def _validate_evaluator_workload(label: str, value: object) -> None:
    if not isinstance(value, dict):
        raise ConfigError(f"{label} must be a mapping")
    unsupported = _unsupported_mapping_keys(
        label,
        value,
        {
            "type",
            "datasets",
            "budget",
            "checkpoint_policy",
            "score_fields",
            "artifact_policy",
            "notes",
        },
    )
    if unsupported:
        raise ConfigError(f"{label} has unsupported fields {unsupported}")
    workload_type = value.get("type")
    _require_enum(
        f"{label}.type",
        workload_type,
        {"simple_check", "inner_search", "ml_training", "custom"},
    )
    if "datasets" in value:
        _validate_evaluator_workload_datasets(f"{label}.datasets", value["datasets"])
    if "budget" in value:
        _validate_evaluator_workload_budget(f"{label}.budget", value["budget"])
    if "checkpoint_policy" in value:
        _require_enum(
            f"{label}.checkpoint_policy",
            value["checkpoint_policy"],
            {"none", "not_retained", "retained_artifacts", "external"},
        )
    if "score_fields" in value:
        _validate_evaluator_workload_score_fields(f"{label}.score_fields", value["score_fields"])
    if "artifact_policy" in value:
        _require_string(f"{label}.artifact_policy", value["artifact_policy"])
    if "notes" in value:
        _require_string(f"{label}.notes", value["notes"])


def _validate_evaluator_workload_datasets(label: str, value: object) -> None:
    if not isinstance(value, list):
        raise ConfigError(f"{label} must be a list")
    for index, dataset in enumerate(value):
        item_label = f"{label}[{index}]"
        if not isinstance(dataset, dict):
            raise ConfigError(f"{item_label} must be a mapping")
        unsupported = _unsupported_mapping_keys(
            item_label,
            dataset,
            {"id", "split", "sha256", "source", "rows", "samples"},
        )
        if unsupported:
            raise ConfigError(f"{item_label} has unsupported fields {unsupported}")
        if "id" not in dataset:
            raise ConfigError(f"{item_label}.id is required")
        _require_stage_label(f"{item_label}.id", dataset["id"])
        if "split" in dataset:
            _require_stage_label(f"{item_label}.split", dataset["split"])
        if "sha256" in dataset:
            _require_sha256(f"{item_label}.sha256", dataset["sha256"])
        if "source" in dataset:
            _require_string(f"{item_label}.source", dataset["source"])
        if "rows" in dataset:
            _require_int(f"{item_label}.rows", dataset["rows"], minimum=0)
        if "samples" in dataset:
            _require_int(f"{item_label}.samples", dataset["samples"], minimum=0)


def _validate_evaluator_workload_budget(label: str, value: object) -> None:
    if not isinstance(value, dict):
        raise ConfigError(f"{label} must be a mapping")
    allowed = {
        "max_steps",
        "max_trials",
        "max_epochs",
        "max_samples",
        "max_seconds",
        "max_train_seconds",
        "max_eval_seconds",
        "accelerator",
    }
    unsupported = _unsupported_mapping_keys(label, value, allowed)
    if unsupported:
        raise ConfigError(f"{label} has unsupported fields {unsupported}")
    for key in ("max_steps", "max_trials", "max_epochs", "max_samples"):
        if key in value:
            _require_int(f"{label}.{key}", value[key], minimum=0)
    for key in ("max_seconds", "max_train_seconds", "max_eval_seconds"):
        if key in value:
            _require_positive_number(f"{label}.{key}", value[key])
    if "accelerator" in value:
        _require_string(f"{label}.accelerator", value["accelerator"])


def _validate_evaluator_workload_score_fields(label: str, value: object) -> None:
    if not isinstance(value, list):
        raise ConfigError(f"{label} must be a list")
    seen: set[str] = set()
    for index, metric in enumerate(value):
        if not isinstance(metric, str):
            raise ConfigError(f"{label}[{index}] must be a manifest-safe metric name")
        try:
            validate_program_metrics({metric: 0.0})
        except ValueError as exc:
            raise ConfigError(f"{label}[{index}] must be a manifest-safe metric name") from exc
        if metric in seen:
            raise ConfigError(f"{label} must not contain duplicate metric names")
        seen.add(metric)


def _require_sha256(label: str, value: object) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ConfigError(f"{label} must be a lowercase sha256 hex digest")
    return value


def _validate_metric_thresholds(label: str, value: object) -> None:
    if not isinstance(value, dict):
        raise ConfigError(f"{label} must be a mapping")
    for metric, spec in value.items():
        if not isinstance(metric, str):
            raise ConfigError(f"{label} keys must be strings")
        try:
            validate_program_metrics({metric: 0.0})
        except ValueError as exc:
            raise ConfigError(f"{label}.{metric!r} must be a manifest-safe metric name") from exc
        metric_label = f"{label}.{metric}"
        if not isinstance(spec, dict):
            raise ConfigError(f"{metric_label} must be a mapping with min and/or max")
        unsupported = _unsupported_mapping_keys(metric_label, spec, {"min", "max"})
        if unsupported:
            raise ConfigError(f"{metric_label} has unsupported fields {unsupported}")
        if "min" not in spec and "max" not in spec:
            raise ConfigError(f"{metric_label} must define min and/or max")
        if "min" in spec:
            _require_number(f"{metric_label}.min", spec["min"])
        if "max" in spec:
            _require_number(f"{metric_label}.max", spec["max"])
        if "min" in spec and "max" in spec and float(spec["min"]) > float(spec["max"]):
            raise ConfigError(f"{metric_label}.min must be <= max")


def _validate_stage_hypothesis_test(
    label: str,
    value: object,
    samples: object,
) -> None:
    if not isinstance(value, dict):
        raise ConfigError(f"{label} must be a mapping")
    unsupported = _unsupported_mapping_keys(
        label,
        value,
        {
            "type",
            "metric",
            "min",
            "min_success_rate",
            "success_threshold",
            "confidence",
            "min_samples",
            "sequential_stopping",
            "error_budget",
        },
    )
    if unsupported:
        raise ConfigError(f"{label} has unsupported fields {unsupported}")
    test_type = value.get("type")
    if test_type not in {
        "one_sided_lower_confidence_bound",
        "binomial_success_rate",
    }:
        raise ConfigError(
            f"{label}.type must be 'one_sided_lower_confidence_bound' or 'binomial_success_rate'"
        )
    if test_type == "one_sided_lower_confidence_bound":
        family_unsupported = sorted(
            key for key in ("min_success_rate", "success_threshold") if key in value
        )
        if family_unsupported:
            raise ConfigError(
                f"{label} has unsupported fields for one_sided_lower_confidence_bound {family_unsupported}"
            )
    if test_type == "binomial_success_rate" and "min" in value:
        raise ConfigError(
            f"{label}.min is unsupported for binomial_success_rate; use success_threshold and min_success_rate"
        )
    metric = value.get("metric", "fitness")
    if metric not in {"fitness", "is_valid"}:
        if not isinstance(metric, str):
            raise ConfigError(f"{label}.metric must be a string")
        try:
            validate_program_metrics({metric: 0.0})
        except ValueError as exc:
            raise ConfigError(
                f"{label}.metric must be 'fitness', 'is_valid', or a manifest-safe metric name"
            ) from exc
    if test_type == "one_sided_lower_confidence_bound" and "min" not in value:
        raise ConfigError(f"{label}.min is required")
    if "min" in value:
        _require_number(f"{label}.min", value["min"])
    if test_type == "binomial_success_rate":
        if "min_success_rate" not in value:
            raise ConfigError(f"{label}.min_success_rate is required")
        min_success_rate = _require_number(
            f"{label}.min_success_rate",
            value["min_success_rate"],
        )
        if min_success_rate <= 0.0 or min_success_rate > 1.0:
            raise ConfigError(f"{label}.min_success_rate must be > 0 and <= 1")
        if "success_threshold" in value:
            _require_number(f"{label}.success_threshold", value["success_threshold"])
        elif metric != "is_valid":
            raise ConfigError(
                f"{label}.success_threshold is required unless metric is 'is_valid'"
            )
    confidence = _require_number(f"{label}.confidence", value.get("confidence", 0.95))
    if confidence <= 0.5 or confidence >= 1.0:
        raise ConfigError(f"{label}.confidence must be > 0.5 and < 1.0")
    min_samples = value.get("min_samples", 2)
    _require_int(f"{label}.min_samples", min_samples, minimum=2)
    if samples is None:
        raise ConfigError(f"{label}.samples must be configured")
    _require_int(f"{label}.samples", samples, minimum=1)
    if int(samples) < int(min_samples):
        raise ConfigError(f"{label}.samples must be >= min_samples")
    if "sequential_stopping" in value:
        _require_bool(f"{label}.sequential_stopping", value["sequential_stopping"])
    if "error_budget" in value:
        _validate_stage_hypothesis_error_budget(
            f"{label}.error_budget",
            value["error_budget"],
            confidence=confidence,
        )


def _validate_stage_hypothesis_error_budget(
    label: str,
    value: object,
    *,
    confidence: float,
) -> None:
    if not isinstance(value, dict):
        raise ConfigError(f"{label} must be a mapping")
    unsupported = _unsupported_mapping_keys(
        label,
        value,
        {"max_false_promotion_rate", "max_false_rejection_rate", "min_effect_size"},
    )
    if unsupported:
        raise ConfigError(f"{label} has unsupported fields {unsupported}")
    if not value:
        raise ConfigError(f"{label} must define at least one budget")
    max_false_promotion_rate = value.get("max_false_promotion_rate")
    if max_false_promotion_rate is not None:
        max_false_promotion_rate = _require_number(
            f"{label}.max_false_promotion_rate",
            max_false_promotion_rate,
        )
        if max_false_promotion_rate <= 0.0 or max_false_promotion_rate >= 0.5:
            raise ConfigError(
                f"{label}.max_false_promotion_rate must be > 0 and < 0.5"
            )
        if (1.0 - confidence) > max_false_promotion_rate + 1e-12:
            raise ConfigError(
                f"{label}.max_false_promotion_rate must be >= 1 - confidence"
            )
    max_false_rejection_rate = value.get("max_false_rejection_rate")
    if max_false_rejection_rate is not None:
        max_false_rejection_rate = _require_number(
            f"{label}.max_false_rejection_rate",
            max_false_rejection_rate,
        )
        if max_false_rejection_rate <= 0.0 or max_false_rejection_rate >= 1.0:
            raise ConfigError(
                f"{label}.max_false_rejection_rate must be > 0 and < 1"
            )
        if "min_effect_size" not in value:
            raise ConfigError(
                f"{label}.min_effect_size is required when max_false_rejection_rate is set"
            )
    if "min_effect_size" in value:
        min_effect_size = _require_number(
            f"{label}.min_effect_size",
            value["min_effect_size"],
        )
        if min_effect_size <= 0.0:
            raise ConfigError(f"{label}.min_effect_size must be > 0")


def _validate_metric_aggregation(label: str, value: object) -> None:
    if not isinstance(value, dict):
        raise ConfigError(f"{label} must be a mapping")
    allowed = {"mean", "min", "max", "all", "any", "last", "quantile"}
    for metric, policy in value.items():
        if not isinstance(metric, str):
            raise ConfigError(f"{label} keys must be strings")
        try:
            validate_program_metrics({metric: True if metric == "is_valid" else 0.0})
        except ValueError as exc:
            raise ConfigError(f"{label}.{metric!r} must be a manifest-safe metric name") from exc
        if isinstance(policy, str):
            if policy not in allowed - {"quantile"}:
                raise ConfigError(
                    f"{label}.{metric} must be one of {sorted(allowed - {'quantile'})} or a quantile mapping"
                )
            continue
        if not isinstance(policy, dict):
            raise ConfigError(
                f"{label}.{metric} must be one of {sorted(allowed - {'quantile'})} or a quantile mapping"
            )
        metric_label = f"{label}.{metric}"
        unsupported = _unsupported_mapping_keys(metric_label, policy, {"policy", "q"})
        if unsupported:
            raise ConfigError(f"{metric_label} has unsupported fields {unsupported}")
        if policy.get("policy") != "quantile":
            raise ConfigError(f"{metric_label}.policy must be 'quantile'")
        if "q" not in policy:
            raise ConfigError(f"{metric_label}.q is required for quantile aggregation")
        q = _require_number(f"{metric_label}.q", policy["q"])
        if q < 0.0 or q > 1.0:
            raise ConfigError(f"{metric_label}.q must be between 0 and 1")


def _validate_program_output_checks(label: str, value: object) -> None:
    if not isinstance(value, list):
        raise ConfigError(f"{label} must be a list of mappings")
    allowed = {"path", "equals"}
    for index, check in enumerate(value):
        item_label = f"{label}[{index}]"
        if not isinstance(check, dict):
            raise ConfigError(f"{item_label} must be a mapping")
        unsupported = _unsupported_mapping_keys(item_label, check, allowed)
        if unsupported:
            raise ConfigError(f"{item_label} has unsupported fields {unsupported}")
        path = _require_string(f"{item_label}.path", check.get("path"))
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", path):
            raise ConfigError(f"{item_label}.path must be a dotted manifest-safe path")
        if "equals" not in check:
            raise ConfigError(f"{item_label}.equals is required")
        _require_output_check_scalar(f"{item_label}.equals", check["equals"])


def _require_output_check_scalar(name: str, value: object) -> None:
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, str):
        if redact_sensitive_text(value) != value:
            raise ConfigError(f"{name} must be a share-safe scalar")
        return
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
        return
    raise ConfigError(f"{name} must be a JSON-safe scalar")


def _validate_backends(backends: object) -> None:
    if not isinstance(backends, list) or len(backends) != 1:
        raise ConfigError("The engineering preview requires one Codex gpt-5.6-luna/high backend")
    allowed_types = {"codex"}
    common_keys = {
        "type",
        "model",
        "max_tokens",
        "cost",
        "cost_usd_per_million_tokens",
        "prompt_max_estimated_tokens",
        "context_window_tokens",
        "reserved_output_tokens",
        "latency",
        "depth",
        "role",
        *REQUEST_PARAMETER_FIELDS,
    }
    for index, backend in enumerate(backends):
        label = f"backends[{index}]"
        if not isinstance(backend, dict):
            raise ConfigError(f"{label} must be a mapping")
        _require_string_mapping_keys(label, backend)
        if backend.get("type") not in allowed_types:
            raise ConfigError(f"{label}.type must be one of {sorted(allowed_types)}")
        _require_model_identifier(f"{label}.model", backend.get("model"))
        if backend["model"] != "gpt-5.6-luna" or backend.get("reasoning_effort") != "high":
            raise ConfigError("The engineering preview supports the validated Codex gpt-5.6-luna/high lane")
        if backend.get("cost_usd_per_million_tokens") is not None:
            raise ConfigError("Codex subscription charges are unknown; a per-token price is not supported")
        allowed = set(common_keys)
        if backend["type"] == "codex":
            allowed.update(
                {
                    "cwd",
                    "sandbox",
                    "timeout_sec",
                    "reasoning_effort",
                    "transcript_dir",
                    "codex_home",
                    "auth_name",
                    "auth_homes",
                    "auth_registry_path",
                    "profile",
                    "approval_policy",
                    "ignore_user_config",
                    "ignore_rules",
                    "ephemeral",
                    "output_json_field",
                    "enable_features",
                    "disable_features",
                }
            )
        unsupported = _unsupported_mapping_keys(label, backend, allowed)
        if unsupported:
            raise ConfigError(f"{label} has unsupported fields {unsupported}")
        if "max_tokens" in backend:
            _require_int(f"{label}.max_tokens", backend["max_tokens"], minimum=1)
        if "timeout_sec" in backend:
            _require_positive_number(f"{label}.timeout_sec", backend["timeout_sec"])
        for field_name in ("cost", "latency", "depth"):
            if field_name in backend:
                _require_positive_number(f"{label}.{field_name}", backend[field_name])
        if "cost_usd_per_million_tokens" in backend:
            _require_positive_number(
                f"{label}.cost_usd_per_million_tokens",
                backend["cost_usd_per_million_tokens"],
            )
        if "prompt_max_estimated_tokens" in backend:
            _require_int(
                f"{label}.prompt_max_estimated_tokens",
                backend["prompt_max_estimated_tokens"],
                minimum=1,
            )
        if "context_window_tokens" in backend:
            _require_int(
                f"{label}.context_window_tokens",
                backend["context_window_tokens"],
                minimum=1,
            )
        if "reserved_output_tokens" in backend:
            _require_int(
                f"{label}.reserved_output_tokens",
                backend["reserved_output_tokens"],
                minimum=0,
            )
            if "context_window_tokens" not in backend:
                raise ConfigError(
                    f"{label}.reserved_output_tokens requires "
                    f"{label}.context_window_tokens"
                )
        if "context_window_tokens" in backend:
            reserved_output_tokens = backend.get(
                "reserved_output_tokens",
                backend.get("max_tokens", 0),
            )
            if (
                isinstance(reserved_output_tokens, bool)
                or not isinstance(reserved_output_tokens, int)
                or reserved_output_tokens >= backend["context_window_tokens"]
            ):
                raise ConfigError(
                    f"{label}.reserved_output_tokens must be less than "
                    f"{label}.context_window_tokens"
                )
        if "role" in backend:
            _require_role_label(f"{label}.role", backend["role"])
        if backend["type"] == "codex" and "reasoning_effort" in backend:
            _require_string(f"{label}.reasoning_effort", backend["reasoning_effort"])
        try:
            validate_backend_request_parameters(backend, field_prefix=label)
        except ValueError as exc:
            raise ConfigError(str(exc)) from exc
        try:
            validate_backend_client_context(backend, field_prefix=label)
        except ValueError as exc:
            raise ConfigError(str(exc)) from exc


def _validate_prompt_variants(
    variants: list[str],
    prompt_format_options: dict,
    *,
    semantic_policy: str,
) -> None:
    from libreevolve.core.prompt import PromptTemplateError, validate_prompt_variants

    try:
        validate_prompt_variants(
            variants,
            prompt_format_options=prompt_format_options,
            semantic_policy=semantic_policy,
        )
    except PromptTemplateError as exc:
        raise ConfigError(f"prompt_variants: {exc}") from exc


def _validate_prompt_variant_semantic_policy(value: object) -> str:
    from libreevolve.core.prompt import (
        PromptTemplateError,
        validate_prompt_variant_semantic_policy,
    )

    try:
        return validate_prompt_variant_semantic_policy(value)
    except PromptTemplateError as exc:
        raise ConfigError(str(exc)) from exc


def _validate_llm_prompt_roles(value: object) -> dict:
    try:
        return validate_prompt_role_policy(value)
    except ValueError as exc:
        raise ConfigError(str(exc)) from exc


def _validate_llm_role_call_limits(value: object) -> dict[str, int]:
    return _validate_llm_role_budget_limits(value, field="llm_role_call_limits")


def _validate_llm_role_budget_limits(value: object, *, field: str) -> dict[str, int]:
    if not isinstance(value, dict):
        raise ConfigError(f"{field} must be a mapping of role labels to integer limits")
    normalized: dict[str, int] = {}
    for raw_role, raw_limit in value.items():
        role = _require_role_scope_label(f"{field} key", raw_role)
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise ConfigError(
                f"{field}[{role!r}] must be a non-negative integer"
            )
        normalized[role] = raw_limit
    return dict(sorted(normalized.items()))


def _validate_llm_role_seconds_limits(value: object) -> dict[str, float]:
    field = "llm_role_seconds_limits"
    if not isinstance(value, dict):
        raise ConfigError(f"{field} must be a mapping of role labels to second limits")
    normalized: dict[str, float] = {}
    for raw_role, raw_limit in value.items():
        role = _require_role_scope_label(f"{field} key", raw_role)
        if isinstance(raw_limit, bool) or not isinstance(raw_limit, (int, float)):
            raise ConfigError(f"{field}[{role!r}] must be a finite non-negative number")
        limit = float(raw_limit)
        if not math.isfinite(limit) or limit < 0.0:
            raise ConfigError(f"{field}[{role!r}] must be a finite non-negative number")
        normalized[role] = limit
    return dict(sorted(normalized.items()))


def _validate_llm_reward_accounted_roles(value: object) -> list[str]:
    if not isinstance(value, list):
        raise ConfigError("llm_reward_accounted_roles must be a list of role labels")
    if not value:
        raise ConfigError("llm_reward_accounted_roles must include at least one role")
    normalized: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        role = _require_role_label(f"llm_reward_accounted_roles[{index}]", item)
        if role not in seen:
            seen.add(role)
            normalized.append(role)
    return normalized


def _validate_llm_role_scheduler_scope(value: object) -> str:
    if value not in {"shared", "role_scoped"}:
        raise ConfigError(
            "llm_role_scheduler_scope must be one of ['role_scoped', 'shared']"
        )
    assert isinstance(value, str)
    return value


def _validate_llm_role_backend_indices(
    value: object,
    *,
    backend_count: int,
) -> dict[str, list[int]]:
    field = "llm_role_backend_indices"
    if not isinstance(value, dict):
        raise ConfigError(f"{field} must be a mapping of role labels to backend index lists")
    normalized: dict[str, list[int]] = {}
    for raw_role, raw_indices in value.items():
        role = _require_role_label(f"{field} key", raw_role)
        if not isinstance(raw_indices, list) or not raw_indices:
            raise ConfigError(f"{field}[{role!r}] must be a non-empty list of backend indices")
        indices: list[int] = []
        seen: set[int] = set()
        for index, raw_index in enumerate(raw_indices):
            if (
                isinstance(raw_index, bool)
                or not isinstance(raw_index, int)
                or raw_index < 0
                or raw_index >= backend_count
            ):
                raise ConfigError(
                    f"{field}[{role!r}][{index}] must be a backend index between 0 and {backend_count - 1}"
                )
            if raw_index not in seen:
                seen.add(raw_index)
                indices.append(raw_index)
        normalized[role] = indices
    return dict(sorted(normalized.items()))


def _validate_llm_role_failure_quarantine_after(value: object) -> dict[str, int]:
    field = "llm_role_failure_quarantine_after"
    if not isinstance(value, dict):
        raise ConfigError(f"{field} must be a mapping of role labels to positive integers")
    normalized: dict[str, int] = {}
    for raw_role, raw_count in value.items():
        role = _require_role_label(f"{field} key", raw_role)
        if (
            isinstance(raw_count, bool)
            or not isinstance(raw_count, int)
            or raw_count <= 0
        ):
            raise ConfigError(f"{field}[{role!r}] must be a positive integer")
        normalized[role] = raw_count
    return dict(sorted(normalized.items()))


def _validate_prompt_format_options(options: object) -> dict:
    from libreevolve.core.prompt import (
        PromptTemplateError,
        validate_prompt_format_options,
    )

    try:
        return validate_prompt_format_options(options)
    except PromptTemplateError as exc:
        raise ConfigError(str(exc)) from exc


def _require_string_mapping_keys(label: str, mapping: dict) -> None:
    non_string = [key for key in mapping if not isinstance(key, str)]
    if non_string:
        formatted = ", ".join(sorted(repr(key) for key in non_string))
        raise ConfigError(f"{label} keys must be strings; got {formatted}")


def _unsupported_mapping_keys(label: str, mapping: dict, allowed: set[str]) -> list[str]:
    _require_string_mapping_keys(label, mapping)
    return sorted(set(mapping) - allowed)


def _has_unicode_format_control(value: str) -> bool:
    return any(unicodedata.category(ch) == "Cf" for ch in value)


def _validate_prompt_reward_bounds(bounds: object) -> None:
    if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
        raise ConfigError("prompt_reward_bounds must be [lo, hi]")
    lo = _require_number("prompt_reward_bounds[0]", bounds[0])
    hi = _require_number("prompt_reward_bounds[1]", bounds[1])
    if lo >= hi:
        raise ConfigError("prompt_reward_bounds must be strictly increasing [lo, hi]")
