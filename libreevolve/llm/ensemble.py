from __future__ import annotations
from collections.abc import Callable, Mapping
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import queue
import re
import threading
import time
import unicodedata

from libreevolve.core.artifact_schema import (
    ARTIFACT_SCHEMA_VERSION,
    LLM_CALL_RECORD_SCHEMA,
    LLM_REWARD_RECORD_SCHEMA,
)
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.core.config import MAX_LLM_CALL_ATTEMPTS, MAX_LLM_RETRIES
from libreevolve.llm.base import LLMBackend
from libreevolve.llm.client_context import (
    CLIENT_CONTEXT_FIELDS,
    validate_backend_client_context,
    validate_client_context_label,
    validate_endpoint_url,
)
from libreevolve.llm.request_params import (
    REQUEST_PARAMETER_FIELDS,
    validate_backend_request_parameters,
)
from libreevolve.llm.provider_metadata import (
    provider_response_metadata_record,
    validate_provider_response_metadata,
)
from libreevolve.llm.provider_retry import validate_provider_max_retries
from libreevolve.llm.prompt_roles import (
    prompt_role_policy_record,
    validate_prompt_role_policy,
)
from libreevolve.llm.tokenization import discover_prompt_token_counter

MAX_REWARD = 1.0
MAX_PROVIDER_ERROR_CHARS = 500
DEFAULT_MAX_RESPONSE_CHARS = 100_000
DEFAULT_MAX_CALL_HISTORY = 500
DEFAULT_MAX_PROMPT_CHARS: int | None = None
DEFAULT_REWARD_ACCOUNTED_ROLES = ("mutation",)
LLM_PROVIDER_DIAGNOSTICS_SCHEMA = "libreevolve.llm_provider_diagnostics.v1"
LLM_PROVIDER_PRICING_READINESS_SCHEMA = (
    "libreevolve.llm_provider_pricing_readiness.v1"
)
PROVIDER_RESPONSE_ERROR_CATEGORIES = {
    "non_text",
    "empty_text",
    "empty_response",
    "incomplete",
    "mixed_content",
    "oversized_text",
    "refusal",
    "tool_call_only",
    "unsupported_completion_state",
}
PROVIDER_FAILURE_CATEGORIES = {
    "provider_response",
    "timeout",
    "rate_limit",
    "transport",
    "provider_server_error",
    "provider_client_error",
    "unknown",
}
_CALL_ROLE_RE = re.compile(r"(?!.*::)(?!.*:$)[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
_METADATA_KEY_RE = re.compile(r"(?!.*::)(?!.*:$)[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
_MODEL_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/+-]{0,191}")
_ENSEMBLE_STRATEGIES = {"ucb1", "throughput_depth"}
_ROLE_SCHEDULER_SCOPES = {"shared", "role_scoped"}
_THROUGHPUT_DEPTH_WEIGHTS = {"depth": 0.10, "cost": -0.05, "latency": -0.05}
_THROUGHPUT_DEPTH_NORMALIZATION = "per_selection_minmax"
_NEUTRAL_NORMALIZED_METADATA = 0.5
_COST_USD_PER_MILLION_TOKENS_FIELD = "cost_usd_per_million_tokens"
_PROMPT_MAX_ESTIMATED_TOKENS_FIELD = "prompt_max_estimated_tokens"
_CONTEXT_WINDOW_TOKENS_FIELD = "context_window_tokens"
_RESERVED_OUTPUT_TOKENS_FIELD = "reserved_output_tokens"


class LLMEnsemble:
    """UCB-style routing layer over one or more LLMBackend instances.

    Sources: UCB1 (Auer, Cesa-Bianchi & Fischer, 2002), with adjacent
    code-evolution scheduling inspiration. This implementation is a heuristic
    adaptation over caller-provided reward updates, currently admission-gated
    fitness improvements in the evolution loop, not a canonical regret-analyzed
    UCB1 implementation or a MadEvolve reproduction.
    """

    def __init__(
        self,
        backends: list[LLMBackend],
        explore_coeff: float = 1.0,
        strategy: str = "ucb1",
        backend_metadata: list[dict] | None = None,
        max_retries: int = 0,
        max_call_attempts: int = MAX_LLM_CALL_ATTEMPTS,
        fallback: bool = True,
        max_response_chars: int = DEFAULT_MAX_RESPONSE_CHARS,
        max_call_history: int = DEFAULT_MAX_CALL_HISTORY,
        call_timeout_sec: float | None = None,
        provider_response_retention_mode: str = "hash_only",
        provider_error_retention_mode: str = "redacted",
        max_prompt_chars: int | None = DEFAULT_MAX_PROMPT_CHARS,
        max_prompt_estimated_tokens: int | None = None,
        reward_accounted_roles: list[str] | tuple[str, ...] = DEFAULT_REWARD_ACCOUNTED_ROLES,
        role_scheduler_scope: str = "shared",
        max_calls_by_role: Mapping[str, int] | None = None,
        role_backend_indices: Mapping[str, list[int] | tuple[int, ...]] | None = None,
        role_failure_quarantine_after: Mapping[str, int] | None = None,
    ):
        if not backends:
            raise ValueError("LLMEnsemble requires at least one backend.")
        self.backends = list(backends)
        self.c = _validate_explore_coeff(explore_coeff)
        self.strategy = _validate_strategy(strategy)
        self._backend_metadata = _validate_backend_metadata(backend_metadata, len(backends))
        self.max_retries = _validate_max_retries(max_retries)
        self.max_call_attempts = _validate_max_call_attempts(max_call_attempts)
        self.fallback = _validate_fallback(fallback)
        self.max_response_chars = _validate_max_response_chars(max_response_chars)
        self.max_call_history = _validate_max_call_history(max_call_history)
        self.call_timeout_sec = _validate_optional_call_timeout(call_timeout_sec)
        self.provider_response_retention_mode = _validate_retention_mode(
            provider_response_retention_mode,
            field="provider_response_retention_mode",
        )
        self.provider_error_retention_mode = _validate_retention_mode(
            provider_error_retention_mode,
            field="provider_error_retention_mode",
        )
        self.max_prompt_chars = _validate_optional_max_prompt_chars(max_prompt_chars)
        self.max_prompt_estimated_tokens = _validate_optional_max_prompt_estimated_tokens(
            max_prompt_estimated_tokens
        )
        self._reward_accounted_roles = _validate_reward_accounted_roles(
            reward_accounted_roles
        )
        self.role_scheduler_scope = _validate_role_scheduler_scope(role_scheduler_scope)
        self.max_calls_by_role = _validate_max_calls_by_role(max_calls_by_role)
        self.role_failure_quarantine_after = _validate_role_quarantine_thresholds(
            role_failure_quarantine_after
        )
        self._configured_role_backend_indices = _validate_role_backend_indices_policy(
            role_backend_indices,
            backend_count=len(backends),
        )
        self._counts: list[int] = [0] * len(backends)
        self._wins: list[float] = [0.0] * len(backends)
        self._total: int = 0
        self._call_history: list[dict] = []
        self._last_call: dict | None = None
        self._call_history_total_records: int = 0
        self._call_history_dropped_records: int = 0
        self._call_record_sink: Callable[[dict], None] | None = None
        self._unrewarded_success_call_ids: list[list[str]] = [[] for _ in backends]
        self._rewarded_call_ids: set[str] = set()
        self._role_accounting: dict[str, dict[str, int | float]] = {}
        self._role_scheduler_state: dict[str, dict] = {}
        self._logical_role_calls: dict[str, int] = {}
        self._provider_failure_state: dict[str, dict[int, dict]] = {}
        self._call_id_namespace: str | None = None

    def generate(self, prompt: str, role: str = "mutation") -> tuple[str, int]:
        """Returns (diff_text, backend_index)."""
        role = validate_llm_call_role(role)
        role_backend_indices = self._role_backend_indices(role)
        effective_prompt_token_limit = self._effective_prompt_estimated_token_limit(
            role_backend_indices
        )
        prompt_token_counter, prompt_token_counter_capability = (
            self._prompt_token_counter_for_role(role, role_backend_indices)
        )
        prompt = validate_llm_prompt(
            prompt,
            max_chars=self.max_prompt_chars,
            max_estimated_tokens=effective_prompt_token_limit,
            prompt_token_counter=prompt_token_counter,
        )
        prompt_provider_tokens = (
            _provider_prompt_token_count(prompt, prompt_token_counter)
            if prompt_token_counter is not None
            else None
        )
        self._enforce_role_call_limit(role)
        self._logical_role_calls[role] = self._logical_role_calls.get(role, 0) + 1
        excluded: set[int] = set(self._quarantined_backend_indices(role))
        backend_attempts = len(self.backends) if self.fallback else 1
        last_exc: Exception | None = None
        attempt_index = 0
        reward_accounted = self._is_reward_accounted_role(role)
        for fallback_attempt in range(backend_attempts):
            if attempt_index >= self.max_call_attempts:
                break
            if role_backend_indices is not None and not (
                role_backend_indices - excluded
            ):
                break
            selection_record = (
                self._role_scheduler_record(role)
                if reward_accounted and self.role_scheduler_scope == "role_scoped"
                else None
            )
            idx = self._ucb1_select(
                exclude=excluded,
                allowed_indices=role_backend_indices,
                account_selection=reward_accounted,
                selection_record=selection_record,
            )
            if reward_accounted:
                if selection_record is None:
                    self._record_role_scheduler_selection(role, idx)
                else:
                    self._total += 1
            backend = self.backends[idx]
            for retry_attempt in range(self.max_retries + 1):
                if attempt_index >= self.max_call_attempts:
                    break
                started = time.perf_counter()
                record = self._call_record(
                    role=role,
                    backend_idx=idx,
                    prompt=prompt,
                    counts_before=list(self._counts),
                    retry_attempt=retry_attempt,
                    fallback_attempt=fallback_attempt,
                    attempt_index=attempt_index,
                    role_backend_indices=role_backend_indices,
                    effective_prompt_token_limit=effective_prompt_token_limit,
                    prompt_token_counter_capability=prompt_token_counter_capability,
                    prompt_provider_tokens=prompt_provider_tokens,
                )
                attempt_index += 1
                try:
                    response = _call_backend_generate(
                        backend,
                        prompt,
                        role=role,
                        timeout_sec=self.call_timeout_sec,
                    )
                    response = _require_response_text(
                        response,
                        max_chars=self.max_response_chars,
                    )
                    output_text, output_retention = _provider_response_retention_record(
                        response,
                        mode=self.provider_response_retention_mode,
                    )
                except Exception as exc:
                    last_exc = exc
                    error_text, error_retention = _provider_error_retention_record(
                        exc,
                        mode=self.provider_error_retention_mode,
                    )
                    provider_metadata, provider_metadata_diagnostic = (
                        _backend_provider_response_metadata_telemetry(backend)
                    )
                    if provider_metadata_diagnostic:
                        record["backend_telemetry_diagnostics"].append(
                            provider_metadata_diagnostic
                        )
                    attempts_remaining = attempt_index < self.max_call_attempts
                    will_retry = retry_attempt < self.max_retries and attempts_remaining
                    will_fallback = (
                        retry_attempt >= self.max_retries
                        and self.fallback
                        and fallback_attempt < backend_attempts - 1
                        and attempts_remaining
                    )
                    if reward_accounted and not will_retry:
                        self._counts[idx] += 1
                        self._record_role_scheduler_count(role, idx)
                    failure_category = _provider_failure_category(exc)
                    failure_policy_state = self._record_provider_failure_policy_state(
                        role=role,
                        backend_idx=idx,
                        category=failure_category,
                        will_retry=will_retry,
                        reward_accounted=reward_accounted,
                    )
                    cost_estimate = _provider_cost_estimate_record(
                        record["backend_metadata"],
                        provider_metadata.get("usage"),
                    )
                    record.update(
                        {
                            "status": "error",
                            "scheduler_accounting": (
                                "rewarded" if reward_accounted else "telemetry_only"
                            ),
                            "latency_sec": time.perf_counter() - started,
                            "error_type": exc.__class__.__name__,
                            "error": error_text,
                            "error_retention": error_retention,
                            "provider_failure_category": failure_category,
                            "provider_status_code": _provider_status_code(exc),
                            "provider_response_error": _provider_response_error_record(exc),
                            "provider_failure_policy": _provider_failure_policy_record(
                                role=role,
                                category=failure_category,
                                will_retry=will_retry,
                                will_fallback=will_fallback,
                                state=failure_policy_state,
                            ),
                            "cancellation_record": _provider_cancellation_record(
                                record,
                                exc,
                                will_retry=will_retry,
                                will_fallback=will_fallback,
                            ),
                            "cost_estimate": cost_estimate,
                            "cost_estimate_status": _provider_cost_estimate_status_record(
                                record["backend_metadata"],
                                provider_metadata.get("usage"),
                                cost_estimate,
                            ),
                            **provider_metadata,
                            "counts_after": list(self._counts),
                            "will_retry": will_retry,
                            "will_fallback": will_fallback,
                        }
                    )
                    self._append_call_record(record)
                    continue
                provider_metadata, provider_metadata_diagnostic = (
                    _backend_provider_response_metadata_telemetry(backend)
                )
                if provider_metadata_diagnostic:
                    record["backend_telemetry_diagnostics"].append(
                        provider_metadata_diagnostic
                    )
                if reward_accounted:
                    self._counts[idx] += 1
                    self._record_role_scheduler_count(role, idx)
                self._record_provider_success(role, idx)
                cost_estimate = _provider_cost_estimate_record(
                    record["backend_metadata"],
                    provider_metadata.get("usage"),
                )
                record.update(
                    {
                        "status": "ok",
                        "scheduler_accounting": (
                            "rewarded" if reward_accounted else "telemetry_only"
                        ),
                        "latency_sec": time.perf_counter() - started,
                        "output": output_text,
                        "output_retention": output_retention,
                        "output_chars": len(response),
                        "output_sha256": hashlib.sha256(response.encode("utf-8")).hexdigest(),
                        "cost_estimate": cost_estimate,
                        "cost_estimate_status": _provider_cost_estimate_status_record(
                            record["backend_metadata"],
                            provider_metadata.get("usage"),
                            cost_estimate,
                        ),
                        **provider_metadata,
                        "counts_after": list(self._counts),
                        "will_retry": False,
                        "will_fallback": False,
                    }
                )
                self._append_call_record(record)
                if reward_accounted:
                    self._unrewarded_success_call_ids[idx].append(record["id"])
                    self._record_role_scheduler_unrewarded_success(
                        role,
                        idx,
                        record["id"],
                    )
                return response, idx
            excluded.add(idx)
        assert last_exc is not None
        raise last_exc

    @property
    def call_history(self) -> list[dict]:
        return deepcopy(self._call_history)

    @property
    def last_call(self) -> dict | None:
        return deepcopy(self._last_call)

    @property
    def call_history_retention(self) -> dict:
        return {
            "policy": "bounded_in_memory_window",
            "max_records": self.max_call_history,
            "retained_records": len(self._call_history),
            "total_records": self._call_history_total_records,
            "dropped_records": self._call_history_dropped_records,
        }

    @property
    def provider_diagnostics_summary(self) -> dict:
        return _provider_diagnostics_summary(
            self._call_history,
            self.call_history_retention,
        )

    @property
    def backend_metadata(self) -> list[dict]:
        return deepcopy(self._backend_metadata)

    @property
    def counts(self) -> list[int]:
        return list(self._counts)

    @property
    def wins(self) -> list[float]:
        return list(self._wins)

    @property
    def total(self) -> int:
        return self._total

    @property
    def scheduler_state(self) -> dict:
        return {
            "counts": list(self._counts),
            "wins": list(self._wins),
            "total": self._total,
            "unrewarded_success_call_ids": deepcopy(self._unrewarded_success_call_ids),
            "rewarded_call_ids": sorted(self._rewarded_call_ids),
            "call_history_retention": self.call_history_retention,
            "reward_accounting_policy": {
                "policy": "configured_reward_accounted_roles_v1",
                "reward_accounted_roles": sorted(self._reward_accounted_roles),
            },
            "role_scheduler_scope": self.role_scheduler_scope,
            "role_accounting": deepcopy(self._role_accounting),
            "role_scheduler_state": deepcopy(self._role_scheduler_state),
            "role_call_limits": {
                "policy": "logical_generate_call_limits_by_role_v1",
                "max_calls_by_role": dict(self.max_calls_by_role),
                "logical_calls_by_role": dict(sorted(self._logical_role_calls.items())),
            },
            "role_backend_policy": {
                "policy": "explicit_role_backend_indices_else_backend_metadata_else_global_v1",
                "configured_role_backend_indices": {
                    role: list(indices)
                    for role, indices in self._configured_role_backend_indices.items()
                },
                "metadata_role_backend_indices": _metadata_role_backend_indices(
                    self._backend_metadata
                ),
                "fallback_policy": "use_backend_metadata_then_global_bandit_when_role_not_configured",
            },
            "provider_failure_policy_state": self._provider_failure_policy_state_snapshot(),
        }

    def restore_scheduler_state(self, state: object) -> None:
        has_role_call_limits = isinstance(state, dict) and "role_call_limits" in state
        has_provider_failure_policy_state = (
            isinstance(state, dict) and "provider_failure_policy_state" in state
        )
        (
            counts,
            wins,
            total,
            unrewarded,
            rewarded,
            role_accounting,
            role_scheduler_state,
            reward_accounted_roles,
            role_scheduler_scope,
            max_calls_by_role,
            logical_role_calls,
            role_failure_quarantine_after,
            provider_failure_state,
        ) = _validate_scheduler_state(
            state,
            len(self.backends),
        )
        self._counts = counts
        self._wins = wins
        self._total = total
        self._unrewarded_success_call_ids = unrewarded
        self._rewarded_call_ids = rewarded
        self._role_accounting = role_accounting
        self._role_scheduler_state = role_scheduler_state
        self._reward_accounted_roles = reward_accounted_roles
        self.role_scheduler_scope = role_scheduler_scope
        if has_role_call_limits:
            self.max_calls_by_role = max_calls_by_role
        self._logical_role_calls = logical_role_calls
        if has_provider_failure_policy_state:
            self.role_failure_quarantine_after = role_failure_quarantine_after
        self._provider_failure_state = provider_failure_state

    def set_call_record_sink(self, sink: Callable[[dict], None] | None) -> None:
        if sink is not None and not callable(sink):
            raise ValueError("LLM call record sink must be callable or None")
        self._call_record_sink = sink

    def set_call_id_namespace(self, namespace: str | None) -> None:
        if self._call_history_total_records:
            raise ValueError("LLM call id namespace must be set before generation")
        self._call_id_namespace = _validate_call_id_namespace(namespace)

    def record_reward(self, idx: int, reward: float, call_id: str | None = None) -> dict:
        """Record a finite non-negative reward, capped to the scheduler range."""
        _validate_scheduler_state(self.scheduler_state, len(self.backends))
        if isinstance(idx, bool) or not isinstance(idx, int) or idx < 0 or idx >= len(self.backends):
            raise ValueError(f"backend reward index out of range: {idx!r}")
        if isinstance(reward, bool) or not isinstance(reward, (int, float)):
            raise ValueError(f"backend reward must be numeric, got {reward!r}")
        numeric = float(reward)
        if not math.isfinite(numeric):
            raise ValueError(f"backend reward must be finite, got {reward!r}")
        if numeric < 0.0:
            raise ValueError(f"backend reward must be non-negative, got {reward!r}")
        reward_call_id = self._claim_reward_call_id(idx, call_id)
        reward_role = self._claim_role_reward_call_id(idx, reward_call_id)
        applied = min(numeric, MAX_REWARD)
        self._wins[idx] += applied
        if reward_role is not None:
            self._role_scheduler_state[reward_role]["wins"][idx] += applied
        for record in self._call_history:
            if record["id"] == reward_call_id:
                record["reward"] = applied
                record["reward_raw"] = numeric
                record["rewarded"] = True
                if self._last_call is not None and self._last_call.get("id") == reward_call_id:
                    self._last_call = deepcopy(record)
                break
        event = {
            "record_type": "reward",
            "call_id": reward_call_id,
            "backend_idx": idx,
            "reward": applied,
            "reward_raw": numeric,
            "rewarded": True,
        }
        if self._call_record_sink is not None:
            self._call_record_sink(deepcopy(event))
        return event

    def _append_call_record(self, record: dict) -> None:
        record = dict(record)
        record["sequence_id"] = self._call_history_total_records + 1
        self._call_history_total_records += 1
        _add_role_accounting_record(self._role_accounting, record)
        self._last_call = deepcopy(record)
        self._call_history.append(record)
        if len(self._call_history) > self.max_call_history:
            self._call_history.pop(0)
            self._call_history_dropped_records += 1
        if self._call_record_sink is not None:
            self._call_record_sink(deepcopy(record))

    def _enforce_role_call_limit(self, role: str) -> None:
        for scope, limit in self.max_calls_by_role.items():
            if not _role_scope_matches(scope, role):
                continue
            consumed = _role_scope_consumed(self._logical_role_calls, scope)
            if consumed < limit:
                continue
            raise LLMRoleCallLimitError(
                f"LLM call budget exhausted before {role}: "
                f"llm_role_call_limits[{scope}]={limit}"
            )

    def _claim_reward_call_id(self, idx: int, call_id: str | None) -> str:
        available = self._unrewarded_success_call_ids[idx]
        if call_id is None:
            if not available:
                raise ValueError(f"no unrewarded successful call for backend {idx}")
            reward_call_id = available.pop(0)
        else:
            if not isinstance(call_id, str) or not call_id.strip():
                raise ValueError("reward call_id must be a non-empty string")
            reward_call_id = call_id
            if reward_call_id in self._rewarded_call_ids:
                raise ValueError(f"backend call {reward_call_id!r} has already been rewarded")
            if reward_call_id not in available:
                matching = next(
                    (record for record in self._call_history if record["id"] == reward_call_id),
                    None,
                )
                if matching is None:
                    raise ValueError(f"backend call {reward_call_id!r} was not found")
                if matching["backend_idx"] != idx:
                    raise ValueError(
                        f"backend call {reward_call_id!r} belongs to backend {matching['backend_idx']}"
                    )
                if matching["status"] != "ok":
                    raise ValueError(f"backend call {reward_call_id!r} is not a successful call")
                raise ValueError(f"backend call {reward_call_id!r} is not rewardable")
            available.remove(reward_call_id)
        self._rewarded_call_ids.add(reward_call_id)
        return reward_call_id

    def _claim_role_reward_call_id(self, idx: int, call_id: str) -> str | None:
        for role, state in self._role_scheduler_state.items():
            available = state["unrewarded_success_call_ids"][idx]
            if call_id not in available:
                continue
            available.remove(call_id)
            state["rewarded_call_ids"].append(call_id)
            state["rewarded_call_ids"] = sorted(set(state["rewarded_call_ids"]))
            return role
        return None

    def _record_role_scheduler_selection(self, role: str, idx: int) -> None:
        state = self._role_scheduler_record(role)
        state["total"] += 1

    def _record_role_scheduler_count(self, role: str, idx: int) -> None:
        state = self._role_scheduler_record(role)
        state["counts"][idx] += 1

    def _record_role_scheduler_unrewarded_success(
        self,
        role: str,
        idx: int,
        call_id: str,
    ) -> None:
        state = self._role_scheduler_record(role)
        state["unrewarded_success_call_ids"][idx].append(call_id)

    def _role_scheduler_record(self, role: str) -> dict:
        role = validate_llm_call_role(role)
        return self._role_scheduler_state.setdefault(
            role,
            _empty_role_scheduler_record(
                len(self.backends),
                selection_policy=(
                    "role_owned_bandit_selection_state"
                    if self.role_scheduler_scope == "role_scoped"
                    else "backend_metadata_role_scoped_when_configured_else_global"
                ),
            ),
        )

    def _ucb1_select(
        self,
        exclude: set[int] | None = None,
        *,
        allowed_indices: set[int] | None = None,
        account_selection: bool = True,
        selection_record: dict | None = None,
    ) -> int:
        _validate_scheduler_state(self.scheduler_state, len(self.backends))
        exclude = exclude or set()
        eligible = (
            set(range(len(self.backends)))
            if allowed_indices is None
            else set(allowed_indices)
        )
        eligible -= exclude
        if not eligible:
            raise ValueError("no eligible LLM backend remains for selection")
        counts = self._counts if selection_record is None else selection_record["counts"]
        wins = self._wins if selection_record is None else selection_record["wins"]
        current_total = self._total if selection_record is None else selection_record["total"]
        effective_total = current_total + 1
        if account_selection:
            if selection_record is None:
                self._total = effective_total
            else:
                selection_record["total"] = effective_total
        untried = [
            i for i in range(len(self.backends))
            if i in eligible and counts[i] == 0
        ]
        if untried:
            return untried[0]

        scores = []
        for i in range(len(self.backends)):
            if i not in eligible:
                scores.append(float("-inf"))
                continue
            scores.append(
                (wins[i] / max(counts[i], 1))
                + self.c * math.sqrt(math.log(effective_total) / max(counts[i], 1))
            )
        # Tiebreaker: prefer arms with fewer pulls (argmax breaks ties by first index,
        # so we use a tuple (score, -count) to prefer lower counts on ties)
        best_idx = 0
        best_score = (scores[0], -counts[0])
        for i in range(1, len(self.backends)):
            current_score = (scores[i], -counts[i])
            if current_score > best_score:
                best_score = current_score
                best_idx = i
        if self.strategy == "throughput_depth":
            return self._throughput_depth_select(
                scores,
                exclude=set(range(len(self.backends))) - eligible,
            )
        return best_idx

    def _is_reward_accounted_role(self, role: str) -> bool:
        return role in self._reward_accounted_roles

    def _role_backend_indices(self, role: str) -> set[int] | None:
        configured = self._configured_role_backend_indices.get(role)
        if configured is not None:
            return set(configured)
        matches = {
            index
            for index, metadata in enumerate(self._backend_metadata)
            if metadata.get("role") == role
        }
        return matches or None

    def _record_provider_failure_policy_state(
        self,
        *,
        role: str,
        backend_idx: int,
        category: str,
        will_retry: bool,
        reward_accounted: bool,
    ) -> dict:
        threshold = self.role_failure_quarantine_after.get(role)
        if threshold is None:
            return {
                "quarantine_policy": "disabled",
                "quarantine_decision": "not_quarantined_by_ensemble_policy",
                "penalty_policy": "disabled",
                "penalty_decision": "not_penalized_by_ensemble_policy",
                "quarantine_threshold": None,
                "consecutive_failures": None,
                "backend_quarantined": False,
            }
        if will_retry:
            existing = self._provider_failure_state.get(role, {}).get(backend_idx, {})
            return {
                "quarantine_policy": "role_backend_consecutive_failure_threshold",
                "quarantine_decision": "not_quarantined_retry_pending",
                "penalty_policy": "zero_reward_on_exhausted_reward_accounted_failure",
                "penalty_decision": "not_penalized_retry_pending",
                "quarantine_threshold": threshold,
                "consecutive_failures": int(existing.get("consecutive_failures", 0)),
                "backend_quarantined": bool(existing.get("quarantined", False)),
            }
        role_state = self._provider_failure_state.setdefault(role, {})
        backend_state = role_state.setdefault(
            backend_idx,
            {
                "backend_idx": backend_idx,
                "total_failures": 0,
                "consecutive_failures": 0,
                "quarantined": False,
                "last_failure_category": None,
            },
        )
        backend_state["total_failures"] += 1
        backend_state["consecutive_failures"] += 1
        backend_state["last_failure_category"] = category
        if backend_state["consecutive_failures"] >= threshold:
            backend_state["quarantined"] = True
            quarantine_decision = "quarantined_role_backend_after_threshold"
        else:
            quarantine_decision = "not_quarantined_below_role_threshold"
        penalty_decision = (
            "zero_reward_scheduler_penalty"
            if reward_accounted
            else "not_penalized_telemetry_only_role"
        )
        return {
            "quarantine_policy": "role_backend_consecutive_failure_threshold",
            "quarantine_decision": quarantine_decision,
            "penalty_policy": "zero_reward_on_exhausted_reward_accounted_failure",
            "penalty_decision": penalty_decision,
            "quarantine_threshold": threshold,
            "consecutive_failures": int(backend_state["consecutive_failures"]),
            "backend_quarantined": bool(backend_state["quarantined"]),
        }

    def _record_provider_success(self, role: str, backend_idx: int) -> None:
        role_state = self._provider_failure_state.get(role)
        if role_state is None:
            return
        backend_state = role_state.get(backend_idx)
        if backend_state is None:
            return
        backend_state["consecutive_failures"] = 0
        backend_state["quarantined"] = False

    def _quarantined_backend_indices(self, role: str) -> set[int]:
        if role not in self.role_failure_quarantine_after:
            return set()
        return {
            idx
            for idx, state in self._provider_failure_state.get(role, {}).items()
            if state.get("quarantined") is True
        }

    def _provider_failure_policy_state_snapshot(self) -> dict:
        roles: dict[str, dict] = {}
        for role, role_state in sorted(self._provider_failure_state.items()):
            backends = []
            for idx in sorted(role_state):
                item = role_state[idx]
                backends.append({
                    "backend_idx": idx,
                    "total_failures": int(item.get("total_failures", 0)),
                    "consecutive_failures": int(item.get("consecutive_failures", 0)),
                    "quarantined": bool(item.get("quarantined", False)),
                    "last_failure_category": item.get("last_failure_category"),
                })
            if backends:
                roles[role] = {"backends": backends}
        return {
            "schema": "libreevolve.provider_failure_policy_state.v1",
            "policy": "role_backend_consecutive_failure_quarantine_v1",
            "role_quarantine_after": dict(
                sorted(self.role_failure_quarantine_after.items())
            ),
            "roles": roles,
        }

    def _effective_prompt_estimated_token_limit(
        self,
        role_backend_indices: set[int] | None,
    ) -> int | None:
        limits: list[int] = []
        if self.max_prompt_estimated_tokens is not None:
            limits.append(self.max_prompt_estimated_tokens)
        eligible = (
            range(len(self.backends))
            if role_backend_indices is None
            else sorted(role_backend_indices)
        )
        for idx in eligible:
            metadata = self._backend_metadata[idx]
            limit = metadata.get(_PROMPT_MAX_ESTIMATED_TOKENS_FIELD)
            if limit is not None:
                limits.append(limit)
            context_window_limit = _backend_context_window_prompt_limit(metadata)
            if context_window_limit is not None:
                limits.append(context_window_limit)
        return min(limits) if limits else None

    def _prompt_token_counter_for_role(
        self,
        role: str,
        role_backend_indices: set[int] | None,
    ) -> tuple[Callable[[str], int] | None, dict]:
        scoped_indices = (
            {role: sorted(role_backend_indices)}
            if role_backend_indices is not None
            else None
        )
        return discover_prompt_token_counter(
            self._backend_metadata,
            role=role,
            role_backend_indices=scoped_indices,
        )

    def _call_record(
        self,
        *,
        role: str,
        backend_idx: int,
        prompt: str,
        counts_before: list[int],
        retry_attempt: int = 0,
        fallback_attempt: int = 0,
        attempt_index: int = 0,
        role_backend_indices: set[int] | None = None,
        effective_prompt_token_limit: int | None = None,
        prompt_token_counter_capability: dict | None = None,
        prompt_provider_tokens: int | None = None,
    ) -> dict:
        backend = self.backends[backend_idx]
        metadata = (
            deepcopy(self._backend_metadata[backend_idx])
            if backend_idx < len(self._backend_metadata)
            else {}
        )
        backend_name, telemetry_diagnostics = _backend_name_telemetry(backend)
        api_mode, api_mode_diagnostic = _backend_api_mode_telemetry(backend)
        if api_mode_diagnostic:
            telemetry_diagnostics.append(api_mode_diagnostic)
        request_parameters, request_parameter_diagnostic = _backend_request_parameters_telemetry(
            backend
        )
        if request_parameter_diagnostic:
            telemetry_diagnostics.append(request_parameter_diagnostic)
        backend_defaults, backend_defaults_diagnostic = _backend_defaults_telemetry(
            backend
        )
        if backend_defaults_diagnostic:
            telemetry_diagnostics.append(backend_defaults_diagnostic)
        client_context, client_context_diagnostic = _backend_client_context_telemetry(backend)
        if client_context_diagnostic:
            telemetry_diagnostics.append(client_context_diagnostic)
        prompt_role_policy, prompt_role_policy_diagnostic = _backend_prompt_role_policy_telemetry(
            backend,
            role,
        )
        if prompt_role_policy_diagnostic:
            telemetry_diagnostics.append(prompt_role_policy_diagnostic)
        prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        planned_sequence_id = self._call_history_total_records + 1
        return {
            "id": _deterministic_call_id(
                sequence_id=planned_sequence_id,
                role=role,
                backend_idx=backend_idx,
                prompt_sha256=prompt_sha256,
                retry_attempt=retry_attempt,
                fallback_attempt=fallback_attempt,
                attempt_index=attempt_index,
                namespace=self._call_id_namespace,
            ),
            "role": role,
            "backend_idx": backend_idx,
            "backend_name": backend_name,
            "backend_metadata": metadata,
            "backend_telemetry_diagnostics": telemetry_diagnostics,
            "strategy": self.strategy,
            "scheduler_policy": self._scheduler_policy_record(
                role=role,
                role_backend_indices=role_backend_indices,
            ),
            "api_mode": api_mode,
            "request_parameters": request_parameters,
            "backend_defaults": backend_defaults,
            "client_context": client_context,
            "prompt_role_policy": prompt_role_policy,
            "call_timeout_sec": self.call_timeout_sec,
            "max_prompt_chars": self.max_prompt_chars,
            "max_prompt_estimated_tokens": effective_prompt_token_limit,
            "configured_max_prompt_estimated_tokens": self.max_prompt_estimated_tokens,
            "backend_prompt_max_estimated_tokens": metadata.get(
                _PROMPT_MAX_ESTIMATED_TOKENS_FIELD
            ),
            "backend_context_window_tokens": metadata.get(
                _CONTEXT_WINDOW_TOKENS_FIELD
            ),
            "backend_reserved_output_tokens": metadata.get(
                _RESERVED_OUTPUT_TOKENS_FIELD
            ),
            "backend_context_window_prompt_estimated_tokens": (
                _backend_context_window_prompt_limit(metadata)
            ),
            "prompt_chars": len(prompt),
            "prompt_estimated_tokens": _estimate_prompt_tokens(len(prompt)),
            "prompt_token_count_policy": (
                "provider_token_counter"
                if prompt_provider_tokens is not None
                else "heuristic_chars_div_4"
            ),
            "prompt_provider_tokens": prompt_provider_tokens,
            "prompt_token_limit_count": (
                prompt_provider_tokens
                if prompt_provider_tokens is not None
                else _estimate_prompt_tokens(len(prompt))
            ),
            "prompt_token_counter_capability": deepcopy(
                prompt_token_counter_capability
            )
            if prompt_token_counter_capability is not None
            else None,
            "prompt_sha256": prompt_sha256,
            "output": None,
            "output_retention": None,
            "output_chars": 0,
            "output_sha256": None,
            "usage": None,
            "cost_estimate": None,
            "cost_estimate_status": None,
            "finish_reason": None,
            "request_id": None,
            "response_id": None,
            "adapter_retry": None,
            "provider_diagnostics": None,
            "reward": None,
            "reward_raw": None,
            "rewarded": False,
            "latency_sec": 0.0,
            "status": "pending",
            "error_type": None,
            "error": None,
            "error_retention": None,
            "provider_failure_category": None,
            "provider_status_code": None,
            "provider_response_error": None,
            "provider_failure_policy": None,
            "cancellation_record": None,
            "retry_attempt": retry_attempt,
            "fallback_attempt": fallback_attempt,
            "attempt_index": attempt_index,
            "max_call_attempts": self.max_call_attempts,
            "will_retry": False,
            "will_fallback": False,
            "counts_before": counts_before,
            "counts_after": None,
        }

    def _throughput_depth_select(
        self, ucb_scores: list[float], exclude: set[int] | None = None
    ) -> int:
        """Cost/depth-aware scheduler layered over UCB scores.

        Metadata keys are optional:
        - `cost`: relative cost, lower is better
        - `latency`: relative latency, lower is better
        - `depth`: relative capability/depth, higher is better
        """
        exclude = exclude or set()
        available = [i for i in range(len(self.backends)) if i not in exclude]
        normalized = {
            field: self._normalized_scheduler_metadata(field, available)
            for field in _THROUGHPUT_DEPTH_WEIGHTS
        }
        best_idx = available[0] if available else 0
        best_score = float("-inf")
        for i, base_score in enumerate(ucb_scores):
            if i in exclude:
                continue
            metadata_score = sum(
                _THROUGHPUT_DEPTH_WEIGHTS[field] * normalized[field][i]
                for field in _THROUGHPUT_DEPTH_WEIGHTS
            )
            score = base_score + metadata_score
            if score > best_score:
                best_score = score
                best_idx = i
        return best_idx

    def _normalized_scheduler_metadata(self, field: str, indexes: list[int]) -> dict[int, float]:
        values = {
            i: float(self._backend_metadata[i].get(field, 1.0))
            for i in indexes
            if i < len(self._backend_metadata)
        }
        if not values:
            return {}
        minimum = min(values.values())
        maximum = max(values.values())
        if maximum == minimum:
            return {i: _NEUTRAL_NORMALIZED_METADATA for i in values}
        span = maximum - minimum
        return {i: (value - minimum) / span for i, value in values.items()}

    def _scheduler_policy_record(
        self,
        *,
        role: str | None = None,
        role_backend_indices: set[int] | None = None,
    ) -> dict:
        reward_accounted = role is not None and role in self._reward_accounted_roles
        policy = {
            "strategy": self.strategy,
            "selection_scope": "global_backend_bandit",
            "role_selection_policy": "shared_selection_reward_accounting_configurable_by_role",
            "reward_accounted_roles": sorted(self._reward_accounted_roles),
            "role_reward_accounting": (
                "rewarded" if reward_accounted else "telemetry_only"
            ),
            "role_reward_contract": _scheduler_reward_contract_record(),
            "role_quota_policy": self._role_quota_policy_record(role),
            "role_scheduler_scope": self.role_scheduler_scope,
            "role_selection_state_owner": _role_selection_state_owner(
                role=role,
                reward_accounted=reward_accounted,
                role_scheduler_scope=self.role_scheduler_scope,
            ),
            "explore_coeff": self.c,
            "max_retries": self.max_retries,
            "max_call_attempts": self.max_call_attempts,
            "fallback": self.fallback,
            "call_timeout_sec": self.call_timeout_sec,
            "max_prompt_chars": self.max_prompt_chars,
            "max_prompt_estimated_tokens": self.max_prompt_estimated_tokens,
        }
        if role_backend_indices is not None:
            policy["selection_scope"] = "role_scoped_backend_bandit"
            configured = role in self._configured_role_backend_indices
            policy["role_selection_policy"] = (
                "explicit_role_backend_indices"
                if configured
                else "backend_metadata_role_match_when_available"
            )
            if (
                role is not None
                and role in self._reward_accounted_roles
                and self.role_scheduler_scope == "role_scoped"
            ):
                policy["selection_scope"] = "role_owned_backend_bandit"
                policy["role_selection_policy"] = (
                    f"{policy['role_selection_policy']}_with_role_owned_counts"
                )
            policy["role"] = role
            policy["role_matched_backend_indices"] = sorted(role_backend_indices)
            policy["role_backend_policy"] = (
                "config.llm_role_backend_indices"
                if configured
                else "backend_metadata.role"
            )
            policy["role_fallback_policy"] = (
                "use_backend_metadata_then_global_bandit_when_role_not_configured"
            )
        if self.strategy == "throughput_depth":
            policy["metadata_normalization"] = _THROUGHPUT_DEPTH_NORMALIZATION
            policy["metadata_weights"] = dict(_THROUGHPUT_DEPTH_WEIGHTS)
            policy["neutral_normalized_metadata"] = _NEUTRAL_NORMALIZED_METADATA
            policy["throughput_depth_lane_evidence"] = (
                self._throughput_depth_lane_evidence(role_backend_indices)
            )
        if (
            role is not None
            and role in self._reward_accounted_roles
            and self.role_scheduler_scope == "role_scoped"
            and role_backend_indices is None
        ):
            policy["selection_scope"] = "role_owned_backend_bandit"
            policy["role_selection_policy"] = "role_owned_counts_global_backend_eligibility"
            policy["role"] = role
        return policy

    def _role_quota_policy_record(self, role: str | None) -> dict:
        record: dict = {
            "policy": "pre_selection_logical_call_limits_v1",
            "enforcement": "checked_before_backend_selection",
            "matching_scopes": [],
            "unmatched_policy": "unbounded_by_role_call_limit",
        }
        if role is None:
            return record
        for scope, limit in sorted(self.max_calls_by_role.items()):
            if not _role_scope_matches(scope, role):
                continue
            record["matching_scopes"].append({"scope": scope, "limit": limit})
        if record["matching_scopes"]:
            record["unmatched_policy"] = "bounded_by_matching_role_call_limits"
        return record

    def _throughput_depth_lane_evidence(
        self,
        role_backend_indices: set[int] | None,
    ) -> dict:
        eligible = (
            list(range(len(self.backends)))
            if role_backend_indices is None
            else sorted(role_backend_indices)
        )
        normalized = {
            field: self._normalized_scheduler_metadata(field, eligible)
            for field in ("cost", "latency", "depth")
        }
        lanes = []
        for index in eligible:
            metadata = self._backend_metadata[index]
            missing_defaults = [
                field
                for field in ("cost", "latency", "depth")
                if field not in metadata
            ]
            lanes.append(
                {
                    "backend_idx": index,
                    "metadata_role": metadata.get("role"),
                    "metadata_model_lane": metadata.get("model_lane"),
                    "lane": _classify_model_mix_lane(metadata),
                    "cost": float(metadata.get("cost", 1.0)),
                    "latency": float(metadata.get("latency", 1.0)),
                    "depth": float(metadata.get("depth", 1.0)),
                    "normalized_cost": normalized["cost"].get(
                        index,
                        _NEUTRAL_NORMALIZED_METADATA,
                    ),
                    "normalized_latency": normalized["latency"].get(
                        index,
                        _NEUTRAL_NORMALIZED_METADATA,
                    ),
                    "normalized_depth": normalized["depth"].get(
                        index,
                        _NEUTRAL_NORMALIZED_METADATA,
                    ),
                    "missing_metadata_defaults": missing_defaults,
                }
            )
        return {
            "policy": "throughput_depth_backend_metadata_lane_evidence_v1",
            "status": "metadata_trace_not_experiment_report",
            "eligible_backend_indices": eligible,
            "lane_source": "backend_metadata.model_lane_or_role",
            "lanes": lanes,
            "has_fast_breadth_lane": any(
                lane["lane"] == "fast_breadth" for lane in lanes
            ),
            "has_strong_depth_lane": any(
                lane["lane"] == "strong_depth" for lane in lanes
            ),
            "claim_ready": False,
            "remaining_gaps": [
                "experiment_level_selection_traces",
                "equal_budget_scheduler_comparisons",
                "candidate_throughput_and_quality_outcomes",
            ],
        }


class LLMCallLedgerError(ValueError):
    """Raised when llm_calls.jsonl cannot be replayed safely."""


class ProviderResponseError(ValueError):
    """Raised when a provider response cannot be treated as generated text."""

    def __init__(
        self,
        message: str,
        *,
        category: str,
        source: str,
        value_type: str | None = None,
    ) -> None:
        if category not in PROVIDER_RESPONSE_ERROR_CATEGORIES:
            raise ValueError(f"unsupported provider response error category: {category!r}")
        super().__init__(message)
        self.category = category
        self.source = source
        self.value_type = value_type


class LLMRoleCallLimitError(RuntimeError):
    """Raised when a configured logical call quota for an LLM role is exhausted."""


class ProviderCallTimeoutError(TimeoutError):
    """Raised when an ensemble-level backend call deadline is exceeded."""

    def __init__(self, timeout_sec: float) -> None:
        super().__init__(f"LLM backend call timed out after {timeout_sec:.6g} seconds")
        self.timeout_sec = timeout_sec
        self.in_flight_cancellation = "unsupported_daemon_worker_may_continue"


def _deterministic_call_id(
    *,
    sequence_id: int,
    role: str,
    backend_idx: int,
    prompt_sha256: str,
    retry_attempt: int,
    fallback_attempt: int,
    attempt_index: int,
    namespace: str | None = None,
) -> str:
    payload = {
        "sequence_id": sequence_id,
        "role": role,
        "backend_idx": backend_idx,
        "prompt_sha256": prompt_sha256,
        "retry_attempt": retry_attempt,
        "fallback_attempt": fallback_attempt,
        "attempt_index": attempt_index,
    }
    if namespace is not None:
        payload["namespace"] = namespace
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"llm-call-{hashlib.sha256(encoded).hexdigest()}"


def _validate_call_id_namespace(value: object) -> str | None:
    if value is None:
        return None
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 128
        or re.fullmatch(r"[A-Za-z0-9_.:-]+", value) is None
    ):
        raise ValueError(
            "LLM call id namespace must match [A-Za-z0-9_.:-]+ and be at most 128 characters"
        )
    return value


def _validate_sha256(value: object, line_number: int, field: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise LLMCallLedgerError(
            f"Malformed llm_calls.jsonl at line {line_number}: {field} must be a SHA-256 hex digest"
        )


def _backend_name_telemetry(backend: object) -> tuple[str, list[dict]]:
    fallback = _safe_backend_class_name(backend)
    try:
        value = getattr(backend, "name")
    except Exception as exc:
        return fallback, [
            {
                "field": "backend_name",
                "reason": "attribute_error",
                "error_type": exc.__class__.__name__,
            }
        ]
    if _is_safe_backend_name(value):
        return value, []
    return fallback, [
        {
            "field": "backend_name",
            "reason": "unsafe_or_non_string",
            "value_type": type(value).__name__,
        }
    ]


def _backend_request_parameters_telemetry(backend: object) -> tuple[dict, dict | None]:
    try:
        value = getattr(backend, "request_parameters", {})
    except Exception as exc:
        return {}, {
            "field": "request_parameters",
            "reason": "attribute_error",
            "error_type": exc.__class__.__name__,
        }
    if value.__class__.__module__.startswith("unittest.mock"):
        return {}, None
    try:
        return _validate_request_parameters_telemetry(value, "request_parameters"), None
    except ValueError:
        return {}, {
            "field": "request_parameters",
            "reason": "unsafe_or_non_string",
            "value_type": type(value).__name__,
        }


def _backend_defaults_telemetry(backend: object) -> tuple[dict, dict | None]:
    try:
        value = getattr(backend, "backend_defaults", {})
    except Exception as exc:
        return {}, {
            "field": "backend_defaults",
            "reason": "attribute_error",
            "error_type": exc.__class__.__name__,
        }
    if value.__class__.__module__.startswith("unittest.mock"):
        return {}, None
    try:
        return _validate_backend_defaults_telemetry(value, "backend_defaults"), None
    except ValueError:
        return {}, {
            "field": "backend_defaults",
            "reason": "unsafe_or_non_string",
            "value_type": type(value).__name__,
        }


def _backend_client_context_telemetry(backend: object) -> tuple[dict, dict | None]:
    try:
        value = getattr(backend, "client_context", {})
    except Exception as exc:
        return {}, {
            "field": "client_context",
            "reason": "attribute_error",
            "error_type": exc.__class__.__name__,
        }
    if value.__class__.__module__.startswith("unittest.mock"):
        return {}, None
    try:
        return _validate_client_context_telemetry(value, "client_context"), None
    except ValueError:
        return {}, {
            "field": "client_context",
            "reason": "unsafe_or_non_string",
            "value_type": type(value).__name__,
        }


def _backend_provider_response_metadata_telemetry(
    backend: object,
) -> tuple[dict, dict | None]:
    try:
        value = getattr(backend, "provider_response_metadata", {})
    except Exception as exc:
        return provider_response_metadata_record({}), {
            "field": "provider_response_metadata",
            "reason": "attribute_error",
            "error_type": exc.__class__.__name__,
        }
    if value.__class__.__module__.startswith("unittest.mock"):
        return provider_response_metadata_record({}), None
    try:
        return provider_response_metadata_record(value), None
    except ValueError:
        return provider_response_metadata_record({}), {
            "field": "provider_response_metadata",
            "reason": "unsafe_or_non_string",
            "value_type": type(value).__name__,
        }


def _provider_cost_estimate_record(
    backend_metadata: object,
    usage: object,
) -> dict | None:
    if not isinstance(backend_metadata, dict) or not isinstance(usage, dict):
        return None
    rate = backend_metadata.get(_COST_USD_PER_MILLION_TOKENS_FIELD)
    total_tokens = usage.get("total_tokens")
    if (
        isinstance(rate, bool)
        or not isinstance(rate, (int, float))
        or not math.isfinite(float(rate))
        or float(rate) <= 0.0
        or isinstance(total_tokens, bool)
        or not isinstance(total_tokens, int)
        or total_tokens < 0
    ):
        return None
    cost_microusd = int(round(total_tokens * float(rate)))
    return {
        "policy": "backend_metadata_cost_per_million_tokens_v1",
        "source": "backend_metadata.cost_usd_per_million_tokens",
        "pricing_source": "configured_backend_metadata",
        "pricing_status": "configured_estimate_not_live_provider_pricing",
        "token_count_source": "provider_response_metadata.usage.total_tokens",
        "cost_usd_per_million_tokens": float(rate),
        "total_tokens": total_tokens,
        "cost_microusd": max(0, cost_microusd),
    }


def _provider_cost_estimate_status_record(
    backend_metadata: object,
    usage: object,
    cost_estimate: object,
) -> dict:
    status = "estimated"
    reason = "estimated_from_configured_rate_and_provider_total_tokens"
    if cost_estimate is None:
        if not isinstance(backend_metadata, dict) or (
            _COST_USD_PER_MILLION_TOKENS_FIELD not in backend_metadata
        ):
            status = "not_estimated"
            reason = "missing_configured_backend_cost_rate"
        else:
            rate = backend_metadata.get(_COST_USD_PER_MILLION_TOKENS_FIELD)
            if (
                isinstance(rate, bool)
                or not isinstance(rate, (int, float))
                or not math.isfinite(float(rate))
                or float(rate) <= 0.0
            ):
                status = "not_estimated"
                reason = "invalid_configured_backend_cost_rate"
            elif not isinstance(usage, dict):
                status = "not_estimated"
                reason = "missing_provider_usage"
            elif "total_tokens" not in usage:
                status = "not_estimated"
                reason = "missing_provider_total_tokens"
            else:
                total_tokens = usage.get("total_tokens")
                if (
                    isinstance(total_tokens, bool)
                    or not isinstance(total_tokens, int)
                    or total_tokens < 0
                ):
                    status = "not_estimated"
                    reason = "invalid_provider_total_tokens"
    return {
        "policy": "backend_metadata_cost_estimate_status_v1",
        "status": status,
        "reason": reason,
        "pricing_source": "configured_backend_metadata",
        "token_count_source": "provider_response_metadata.usage.total_tokens",
        "live_pricing_status": "not_fetched",
    }


def _backend_prompt_role_policy_telemetry(
    backend: object,
    role: str,
) -> tuple[dict, dict | None]:
    getter = getattr(backend, "prompt_role_policy_for_role", None)
    if getter is None or getter.__class__.__module__.startswith("unittest.mock"):
        return prompt_role_policy_record({}, role), None
    try:
        value = getter(role)
    except Exception as exc:
        return prompt_role_policy_record({}, role), {
            "field": "prompt_role_policy",
            "reason": "attribute_error",
            "error_type": _safe_type_name(exc),
        }
    try:
        return _validate_prompt_role_policy_telemetry(value, "prompt_role_policy"), None
    except ValueError:
        return prompt_role_policy_record({}, role), {
            "field": "prompt_role_policy",
            "reason": "unsafe_or_non_string",
            "value_type": type(value).__name__,
        }


def _backend_api_mode_telemetry(backend: object) -> tuple[str | None, dict | None]:
    try:
        value = getattr(backend, "api_mode", None)
    except Exception as exc:
        return None, {
            "field": "api_mode",
            "reason": "attribute_error",
            "error_type": exc.__class__.__name__,
        }
    if value is None:
        return None, None
    if _is_safe_api_mode(value):
        return value, None
    return None, {
        "field": "api_mode",
        "reason": "unsafe_or_non_string",
        "value_type": type(value).__name__,
    }


def _safe_backend_class_name(backend: object) -> str:
    name = backend.__class__.__name__
    if _is_safe_api_mode(name):
        return name
    return "backend"


def _is_safe_backend_name(value: object) -> bool:
    return (
        isinstance(value, str)
        and redact_sensitive_text(value) == value
        and _MODEL_ID_RE.fullmatch(value) is not None
    )


def _is_safe_api_mode(value: object) -> bool:
    return (
        isinstance(value, str)
        and redact_sensitive_text(value) == value
        and _METADATA_KEY_RE.fullmatch(value) is not None
    )


def _provider_error_retention_record(exc: Exception, *, mode: str) -> tuple[str | None, dict]:
    mode = _validate_retention_mode(mode, field="provider_error_retention_mode")
    try:
        raw = str(exc)
    except Exception as format_exc:
        raw = (
            f"<exception message unavailable; __str__ raised "
            f"{format_exc.__class__.__name__}>"
        )
    raw_sha256 = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if mode == "off":
        return None, {
            "retention_mode": mode,
            "retention_policy": "off_no_text_or_hash",
            "sha256": None,
            "chars": None,
            "stored_chars": 0,
            "redacted": False,
            "truncated": False,
        }
    redacted = redact_sensitive_text(raw)
    if mode == "hash_only":
        return None, {
            "retention_mode": mode,
            "retention_policy": "hash_only_with_raw_sha256",
            "sha256": raw_sha256,
            "chars": len(raw),
            "stored_chars": 0,
            "redacted": redacted != raw,
            "truncated": False,
        }
    text = redacted
    truncated = False
    policy = "full_secret_redacted_text_with_raw_sha256"
    if mode == "redacted":
        policy = "redact_then_prefix_truncate_with_raw_sha256"
        if len(text) > MAX_PROVIDER_ERROR_CHARS:
            text = text[:MAX_PROVIDER_ERROR_CHARS] + "...[truncated]"
            truncated = True
    return text, {
        "retention_mode": mode,
        "retention_policy": policy,
        "sha256": raw_sha256,
        "chars": len(raw),
        "stored_chars": len(text),
        "redacted": redacted != raw,
        "truncated": truncated,
    }


def _provider_response_retention_record(response: str, *, mode: str) -> tuple[str | None, dict]:
    mode = _validate_retention_mode(mode, field="provider_response_retention_mode")
    raw_sha256 = hashlib.sha256(response.encode("utf-8")).hexdigest()
    if mode == "off":
        return None, {
            "retention_mode": mode,
            "retention_policy": "off_no_text_or_hash",
            "sha256": None,
            "chars": None,
            "stored_chars": 0,
            "redacted": False,
            "truncated": False,
        }
    redacted = redact_sensitive_text(response)
    if mode == "hash_only":
        return None, {
            "retention_mode": mode,
            "retention_policy": "hash_only_with_raw_sha256",
            "sha256": raw_sha256,
            "chars": len(response),
            "stored_chars": 0,
            "redacted": redacted != response,
            "truncated": False,
        }
    return redacted, {
        "retention_mode": mode,
        "retention_policy": (
            "full_secret_redacted_text_with_raw_sha256"
            if mode == "full"
            else "redact_only_with_raw_sha256"
        ),
        "sha256": raw_sha256,
        "chars": len(response),
        "stored_chars": len(redacted),
        "redacted": redacted != response,
        "truncated": False,
    }


def _safe_type_name(value: object) -> str:
    return _provider_response_source_label(value.__class__.__name__)


def _provider_failure_category(exc: Exception) -> str:
    if isinstance(exc, ProviderResponseError):
        return "provider_response"
    type_name = _safe_type_name(exc).lower()
    status_code = getattr(exc, "status_code", None)
    if _is_timeout_exception(exc, type_name):
        return "timeout"
    if _is_rate_limit_exception(status_code, type_name):
        return "rate_limit"
    if _is_transport_exception(exc, type_name):
        return "transport"
    if isinstance(status_code, int) and 500 <= status_code <= 599:
        return "provider_server_error"
    if isinstance(status_code, int) and 400 <= status_code <= 499:
        return "provider_client_error"
    return "unknown"


def _provider_failure_policy_record(
    *,
    role: str,
    category: str,
    will_retry: bool,
    will_fallback: bool,
    state: dict,
) -> dict:
    record = {
        "schema": "libreevolve.provider_failure_policy.v1",
        "scope": "ensemble_call_local_retry_fallback_policy",
        "role": role,
        "provider_failure_category": category,
        "retry_decision": "retry" if will_retry else "no_retry",
        "fallback_decision": "fallback" if will_fallback else "no_fallback",
        "quarantine_decision": state["quarantine_decision"],
        "penalty_decision": state["penalty_decision"],
        "remaining_gap": "provider_output_replay_and_hard_cancellation_not_implemented",
    }
    if state["quarantine_policy"] != "disabled":
        record.update({
            "quarantine_policy": state["quarantine_policy"],
            "penalty_policy": state["penalty_policy"],
            "quarantine_threshold": state["quarantine_threshold"],
            "consecutive_failures": state["consecutive_failures"],
            "backend_quarantined": state["backend_quarantined"],
            "remaining_gap": (
                "role_specific_quarantine_penalty_and_cross_run_resume_policy_not_implemented"
            ),
        })
    return record


def _provider_cancellation_record(
    record: dict,
    exc: Exception,
    *,
    will_retry: bool,
    will_fallback: bool,
) -> dict | None:
    if not isinstance(exc, ProviderCallTimeoutError):
        return None
    if will_retry:
        budget_action = "retry"
    elif will_fallback:
        budget_action = "fallback"
    else:
        budget_action = "telemetry_only"
    return {
        "schema": "libreevolve.provider_cancellation_record.v1",
        "scope": "ensemble_call_timeout",
        "role": record["role"],
        "backend_idx": record["backend_idx"],
        "call_id": record["id"],
        "cancellation_kind": "ensemble_wait_deadline",
        "timeout_sec": exc.timeout_sec,
        "status": "deadline_exceeded",
        "budget_action": budget_action,
        "hard_cancel_ready": False,
        "in_flight_cancellation": exc.in_flight_cancellation,
        "remaining_gap": (
            "provider_sdk_hard_cancellation_not_implemented"
            if exc.in_flight_cancellation == "unsupported_daemon_worker_may_continue"
            else "remote_provider_cancellation_unverified"
        ),
    }


def _provider_status_code(exc: Exception) -> int | None:
    status_code = getattr(exc, "status_code", None)
    if isinstance(status_code, bool) or not isinstance(status_code, int):
        return None
    if status_code < 100 or status_code > 599:
        return None
    return status_code


def _is_timeout_exception(exc: Exception, type_name: str) -> bool:
    return isinstance(exc, TimeoutError) or "timeout" in type_name


def _is_rate_limit_exception(status_code: object, type_name: str) -> bool:
    return (
        status_code == 429
        or "ratelimit" in type_name
        or "rate_limit" in type_name
        or "too_many" in type_name
        or "toomany" in type_name
    )


def _is_transport_exception(exc: Exception, type_name: str) -> bool:
    if isinstance(exc, ConnectionError):
        return True
    return any(
        marker in type_name
        for marker in (
            "connection",
            "connecterror",
            "network",
            "transport",
            "readerror",
            "writeerror",
        )
    )


def _provider_response_error_record(exc: Exception) -> dict | None:
    if not isinstance(exc, ProviderResponseError):
        return None
    record = {
        "category": exc.category,
        "source": _provider_response_source_label(exc.source),
    }
    if exc.value_type is not None:
        record["value_type"] = _provider_response_source_label(exc.value_type)
    return record


def _provider_response_source_label(value: object) -> str:
    if isinstance(value, str):
        normalized = re.sub(r"[^A-Za-z0-9_.:-]+", "_", value.strip())
        normalized = normalized.strip("_")
        if _is_safe_api_mode(normalized):
            return normalized
    return "provider"


def validate_llm_prompt(
    prompt: object,
    *,
    max_chars: int | None = None,
    max_estimated_tokens: int | None = None,
    prompt_token_counter: Callable[[str], int] | None = None,
) -> str:
    if not isinstance(prompt, str):
        raise ValueError(f"LLM prompt must be text, got {type(prompt).__name__}")
    if not prompt.strip():
        raise ValueError("LLM prompt must be non-empty text")
    limit = _validate_optional_max_prompt_chars(max_chars)
    if limit is not None and len(prompt) > limit:
        raise ValueError(
            f"LLM prompt exceeds max_prompt_chars ({len(prompt)} > {limit})"
        )
    token_limit = _validate_optional_max_prompt_estimated_tokens(max_estimated_tokens)
    token_count = (
        _provider_prompt_token_count(prompt, prompt_token_counter)
        if prompt_token_counter is not None
        else _estimate_prompt_tokens(len(prompt))
    )
    if token_limit is not None and token_count > token_limit:
        raise ValueError(
            "LLM prompt exceeds max_prompt_estimated_tokens "
            f"({token_count} > {token_limit})"
        )
    return prompt


def validate_backend_model_id(model: object, *, field: str = "model") -> str:
    if not isinstance(model, str):
        raise ValueError(f"{field} must be a manifest-safe model identifier")
    if redact_sensitive_text(model) != model:
        raise ValueError(f"{field} must be a manifest-safe model identifier")
    if _MODEL_ID_RE.fullmatch(model) is None:
        raise ValueError(f"{field} must be a manifest-safe model identifier")
    return model


def validate_backend_max_tokens(max_tokens: object, *, field: str = "max_tokens") -> int:
    if isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or max_tokens < 1:
        raise ValueError(f"{field} must be a positive integer")
    return max_tokens


def validate_restored_backend_specs(backends: object) -> list[dict]:
    """Validate backend specs loaded from future replay/resume state.

    This intentionally shares the same normalization boundary as live
    `build_llm()` construction so restored specs cannot bypass model-id,
    token-limit, request-parameter, or client-context checks.
    """
    return deepcopy(_normalize_backend_specs(backends))


def validate_llm_call_role(role: object) -> str:
    if not isinstance(role, str):
        raise ValueError(f"LLM call role must be a manifest-safe role label, got {role!r}")
    if redact_sensitive_text(role) != role:
        raise ValueError("LLM call role must be a manifest-safe role label")
    if _CALL_ROLE_RE.fullmatch(role) is None:
        raise ValueError("LLM call role must be a manifest-safe role label")
    return role


def _validate_strategy(strategy: object) -> str:
    if not isinstance(strategy, str) or strategy not in _ENSEMBLE_STRATEGIES:
        raise ValueError(f"ensemble strategy must be one of {sorted(_ENSEMBLE_STRATEGIES)}")
    return strategy


def _validate_role_scheduler_scope(scope: object) -> str:
    if not isinstance(scope, str) or scope not in _ROLE_SCHEDULER_SCOPES:
        raise ValueError(
            "llm role_scheduler_scope must be one of ['role_scoped', 'shared']"
        )
    return scope


def _validate_explore_coeff(explore_coeff: object) -> float:
    if isinstance(explore_coeff, bool) or not isinstance(explore_coeff, (int, float)):
        raise ValueError("ensemble exploration coefficient must be a finite non-negative number")
    value = float(explore_coeff)
    if not math.isfinite(value) or value < 0.0:
        raise ValueError("ensemble exploration coefficient must be a finite non-negative number")
    return value


def _validate_max_retries(max_retries: object) -> int:
    if isinstance(max_retries, bool) or not isinstance(max_retries, int) or max_retries < 0:
        raise ValueError("llm max_retries must be a non-negative integer")
    if max_retries > MAX_LLM_RETRIES:
        raise ValueError(f"llm max_retries must be <= {MAX_LLM_RETRIES}")
    return max_retries


def _validate_max_call_attempts(max_call_attempts: object) -> int:
    if (
        isinstance(max_call_attempts, bool)
        or not isinstance(max_call_attempts, int)
        or max_call_attempts < 1
    ):
        raise ValueError("llm max_call_attempts must be a positive integer")
    if max_call_attempts > MAX_LLM_CALL_ATTEMPTS:
        raise ValueError(
            f"llm max_call_attempts must be <= {MAX_LLM_CALL_ATTEMPTS}"
        )
    return max_call_attempts


def _validate_max_response_chars(max_response_chars: object) -> int:
    if (
        isinstance(max_response_chars, bool)
        or not isinstance(max_response_chars, int)
        or max_response_chars <= 0
    ):
        raise ValueError("llm max_response_chars must be a positive integer")
    return max_response_chars


def _validate_optional_max_prompt_chars(max_prompt_chars: object) -> int | None:
    if max_prompt_chars is None:
        return None
    if (
        isinstance(max_prompt_chars, bool)
        or not isinstance(max_prompt_chars, int)
        or max_prompt_chars <= 0
    ):
        raise ValueError("llm max_prompt_chars must be a positive integer or None")
    return max_prompt_chars


def _validate_optional_max_prompt_estimated_tokens(value: object) -> int | None:
    if value is None:
        return None
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        raise ValueError(
            "llm max_prompt_estimated_tokens must be a positive integer or None"
        )
    return value


def _estimate_prompt_tokens(chars: int) -> int:
    return max(1, math.ceil(chars / 4)) if chars > 0 else 0


def _provider_prompt_token_count(
    prompt: str,
    prompt_token_counter: Callable[[str], int],
) -> int:
    count = prompt_token_counter(prompt)
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError(
            "provider prompt token counter must return a non-negative integer"
        )
    return count


def _validate_role_backend_indices_policy(
    value: Mapping[str, list[int] | tuple[int, ...]] | None,
    *,
    backend_count: int,
) -> dict[str, tuple[int, ...]]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError("llm role_backend_indices must be a mapping")
    normalized: dict[str, tuple[int, ...]] = {}
    for raw_role, raw_indices in value.items():
        role = validate_llm_call_role(raw_role)
        if not isinstance(raw_indices, (list, tuple)) or not raw_indices:
            raise ValueError(
                f"llm role_backend_indices[{role!r}] must be a non-empty list of backend indices"
            )
        indices: list[int] = []
        seen: set[int] = set()
        for index, raw_index in enumerate(raw_indices):
            if (
                isinstance(raw_index, bool)
                or not isinstance(raw_index, int)
                or raw_index < 0
                or raw_index >= backend_count
            ):
                raise ValueError(
                    "llm role_backend_indices"
                    f"[{role!r}][{index}] must be a backend index between 0 and {backend_count - 1}"
                )
            if raw_index not in seen:
                seen.add(raw_index)
                indices.append(raw_index)
        normalized[role] = tuple(indices)
    return dict(sorted(normalized.items()))


def _metadata_role_backend_indices(metadata: list[dict]) -> dict[str, list[int]]:
    grouped: dict[str, list[int]] = {}
    for index, item in enumerate(metadata):
        role = item.get("role")
        if isinstance(role, str):
            grouped.setdefault(role, []).append(index)
    return dict(sorted(grouped.items()))


def _validate_max_call_history(max_call_history: object) -> int:
    if (
        isinstance(max_call_history, bool)
        or not isinstance(max_call_history, int)
        or max_call_history <= 0
    ):
        raise ValueError("llm max_call_history must be a positive integer")
    return max_call_history


def _validate_retention_mode(value: object, *, field: str) -> str:
    if value not in {"full", "redacted", "hash_only", "off"}:
        raise ValueError(
            f"{field} must be one of ['full', 'hash_only', 'off', 'redacted']"
        )
    assert isinstance(value, str)
    return value


def _validate_optional_call_timeout(timeout_sec: object) -> float | None:
    if timeout_sec is None:
        return None
    if isinstance(timeout_sec, bool) or not isinstance(timeout_sec, (int, float)):
        raise ValueError("llm call_timeout_sec must be a positive finite number or None")
    numeric = float(timeout_sec)
    if not math.isfinite(numeric) or numeric <= 0.0:
        raise ValueError("llm call_timeout_sec must be a positive finite number or None")
    return numeric


def validate_scheduler_state_snapshot(state: object, backend_count: int) -> None:
    """Validate state accepted by LLMEnsemble.restore_scheduler_state()."""
    _validate_scheduler_state(state, backend_count)


def _validate_scheduler_state(
    state: object,
    backend_count: int,
) -> tuple[
    list[int],
    list[float],
    int,
    list[list[str]],
    set[str],
    dict[str, dict[str, int | float]],
    dict[str, dict],
    set[str],
    str,
    dict[str, int],
    dict[str, int],
    dict[str, int],
    dict[str, dict[int, dict]],
]:
    if not isinstance(state, dict):
        raise ValueError("scheduler state must be a mapping")
    supported_fields = {
        "counts",
        "wins",
        "total",
        "unrewarded_success_call_ids",
        "rewarded_call_ids",
        "call_history_retention",
        "reward_accounting_policy",
        "role_scheduler_scope",
        "role_accounting",
        "role_scheduler_state",
        "role_call_limits",
        "role_backend_policy",
        "provider_failure_policy_state",
    }
    unsupported = sorted(set(state) - supported_fields)
    if unsupported:
        raise ValueError(f"scheduler state has unsupported fields: {unsupported}")
    if "counts" not in state or "wins" not in state or "total" not in state:
        raise ValueError("scheduler state must include counts, wins, and total")
    counts_raw = state["counts"]
    wins_raw = state["wins"]
    total_raw = state["total"]
    counts = _validate_scheduler_count_vector(counts_raw, backend_count, "counts")
    wins = _validate_scheduler_win_vector(wins_raw, backend_count, "wins")
    if isinstance(total_raw, bool) or not isinstance(total_raw, int) or total_raw < 0:
        raise ValueError("scheduler total must be a non-negative integer")
    if total_raw < sum(counts):
        raise ValueError("scheduler total must be >= the sum of backend counts")
    unrewarded = _validate_unrewarded_call_ids(
        state.get("unrewarded_success_call_ids"),
        backend_count,
    )
    rewarded = _validate_rewarded_call_ids(state.get("rewarded_call_ids"))
    all_unrewarded = [call_id for per_backend in unrewarded for call_id in per_backend]
    duplicate_unrewarded = _first_duplicate(all_unrewarded)
    if duplicate_unrewarded is not None:
        raise ValueError(f"scheduler call id appears more than once: {duplicate_unrewarded!r}")
    overlap = sorted(set(all_unrewarded) & rewarded)
    if overlap:
        raise ValueError(f"scheduler call id cannot be both rewarded and unrewarded: {overlap[0]!r}")
    if "call_history_retention" in state:
        _validate_call_history_retention_state(state["call_history_retention"])
    reward_accounted_roles = _validate_reward_accounting_policy(
        state.get("reward_accounting_policy")
    )
    role_scheduler_scope = _validate_role_scheduler_scope(
        state.get("role_scheduler_scope", "shared")
    )
    role_accounting = _validate_role_accounting_state(state.get("role_accounting"))
    role_scheduler_state = _validate_role_scheduler_state(
        state.get("role_scheduler_state"),
        backend_count,
    )
    max_calls_by_role, logical_role_calls = _validate_role_call_limits_state(
        state.get("role_call_limits")
    )
    _validate_role_backend_policy_state(
        state.get("role_backend_policy"),
        backend_count=backend_count,
    )
    (
        role_failure_quarantine_after,
        provider_failure_state,
    ) = _validate_provider_failure_policy_state(
        state.get("provider_failure_policy_state"),
        backend_count=backend_count,
    )
    return (
        counts,
        wins,
        total_raw,
        unrewarded,
        rewarded,
        role_accounting,
        role_scheduler_state,
        reward_accounted_roles,
        role_scheduler_scope,
        max_calls_by_role,
        logical_role_calls,
        role_failure_quarantine_after,
        provider_failure_state,
    )


def _validate_scheduler_count_vector(
    raw: object,
    backend_count: int,
    field: str,
) -> list[int]:
    if not isinstance(raw, list) or len(raw) != backend_count:
        raise ValueError(
            f"scheduler {field} must contain one integer per backend"
        )
    counts: list[int] = []
    for index, count in enumerate(raw):
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(
                f"scheduler {field}[{index}] must be a non-negative integer"
            )
        counts.append(count)
    return counts


def _validate_scheduler_win_vector(
    raw: object,
    backend_count: int,
    field: str,
) -> list[float]:
    if not isinstance(raw, list) or len(raw) != backend_count:
        raise ValueError(
            f"scheduler {field} must contain one finite number per backend"
        )
    wins: list[float] = []
    for index, win in enumerate(raw):
        if isinstance(win, bool) or not isinstance(win, (int, float)):
            raise ValueError(
                f"scheduler {field}[{index}] must be a finite non-negative number"
            )
        numeric = float(win)
        if not math.isfinite(numeric) or numeric < 0.0:
            raise ValueError(
                f"scheduler {field}[{index}] must be a finite non-negative number"
            )
        wins.append(numeric)
    return wins


def _empty_role_scheduler_record(
    backend_count: int,
    *,
    selection_policy: str = "backend_metadata_role_scoped_when_configured_else_global",
) -> dict:
    return {
        "policy": "per_role_scheduler_audit_state_not_selection_policy",
        "selection_policy": selection_policy,
        "counts": [0] * backend_count,
        "wins": [0.0] * backend_count,
        "total": 0,
        "unrewarded_success_call_ids": [[] for _ in range(backend_count)],
        "rewarded_call_ids": [],
    }


def _scheduler_reward_contract_record() -> dict:
    return {
        "policy": "finite_non_negative_reward_clipped_to_max_reward_v1",
        "reward_update_api": "LLMEnsemble.record_reward",
        "raw_reward": "finite_non_negative_number",
        "applied_reward": "min(raw_reward, max_reward)",
        "max_reward": MAX_REWARD,
    }


def _role_selection_state_owner(
    *,
    role: str | None,
    reward_accounted: bool,
    role_scheduler_scope: str,
) -> str:
    if role is None:
        return "global_scheduler_state"
    if not reward_accounted:
        return "none_telemetry_only"
    if role_scheduler_scope == "role_scoped":
        return "role_scheduler_state"
    return "global_scheduler_state"


def _classify_model_mix_lane(metadata: Mapping[str, object]) -> str:
    raw = metadata.get("model_lane", metadata.get("role"))
    if not isinstance(raw, str):
        return "unclassified"
    normalized = raw.lower().replace("-", "_").replace(" ", "_")
    if normalized in {"fast", "breadth", "fast_breadth", "flash"}:
        return "fast_breadth"
    if normalized in {"strong", "depth", "strong_depth", "pro"}:
        return "strong_depth"
    return "unclassified"


def _empty_role_accounting_record() -> dict[str, int | float]:
    return {
        "calls": 0,
        "successes": 0,
        "failures": 0,
        "reward_accounted_calls": 0,
        "telemetry_only_calls": 0,
        "ensemble_retry_attempts": 0,
        "ensemble_fallback_attempts": 0,
        "provider_internal_attempts": 0,
        "provider_internal_failed_attempts": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cost_microusd": 0,
        "wall_clock_seconds": 0.0,
        "provider_response_failures": 0,
        "timeout_failures": 0,
        "rate_limit_failures": 0,
        "transport_failures": 0,
        "provider_server_error_failures": 0,
        "provider_client_error_failures": 0,
        "unknown_failures": 0,
    }


def _add_role_accounting_record(
    role_accounting: dict[str, dict[str, int | float]],
    record: dict,
) -> None:
    role = validate_llm_call_role(record.get("role"))
    summary = role_accounting.setdefault(role, _empty_role_accounting_record())
    summary["calls"] += 1
    if record.get("status") == "ok":
        summary["successes"] += 1
    else:
        summary["failures"] += 1
    if record.get("scheduler_accounting", "rewarded") == "rewarded":
        summary["reward_accounted_calls"] += 1
    else:
        summary["telemetry_only_calls"] += 1
    if _positive_int_record_field(record, "retry_attempt"):
        summary["ensemble_retry_attempts"] += 1
    if _positive_int_record_field(record, "fallback_attempt"):
        summary["ensemble_fallback_attempts"] += 1
    adapter_retry = record.get("adapter_retry")
    if isinstance(adapter_retry, dict):
        attempts = adapter_retry.get("attempts")
        failed_attempts = adapter_retry.get("failed_attempts")
        if isinstance(attempts, int) and not isinstance(attempts, bool) and attempts > 0:
            summary["provider_internal_attempts"] += attempts
        if (
            isinstance(failed_attempts, int)
            and not isinstance(failed_attempts, bool)
            and failed_attempts > 0
        ):
            summary["provider_internal_failed_attempts"] += failed_attempts
    usage = record.get("usage")
    if isinstance(usage, dict):
        for source, target in (
            ("input_tokens", "input_tokens"),
            ("output_tokens", "output_tokens"),
            ("total_tokens", "total_tokens"),
        ):
            token_count = usage.get(source)
            if (
                isinstance(token_count, int)
                and not isinstance(token_count, bool)
                and token_count > 0
            ):
                summary[target] += token_count
    cost_estimate = record.get("cost_estimate")
    if isinstance(cost_estimate, dict):
        cost_microusd = cost_estimate.get("cost_microusd")
        if (
            isinstance(cost_microusd, int)
            and not isinstance(cost_microusd, bool)
            and cost_microusd > 0
        ):
            summary["cost_microusd"] += cost_microusd
    latency_sec = record.get("latency_sec")
    if isinstance(latency_sec, (int, float)) and not isinstance(latency_sec, bool):
        latency = float(latency_sec)
        if math.isfinite(latency) and latency > 0.0:
            summary["wall_clock_seconds"] += latency
    provider_failure_category = record.get("provider_failure_category")
    if isinstance(provider_failure_category, str):
        failure_field = _provider_failure_category_role_field(provider_failure_category)
        if failure_field is not None:
            summary[failure_field] += 1


def _positive_int_record_field(record: dict, field: str) -> bool:
    value = record.get(field)
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _provider_diagnostics_summary(
    call_history: list[dict],
    retention: dict,
) -> dict:
    groups: dict[str, dict] = {}
    totals = {
        "call_count": len(call_history),
        "usage_record_count": 0,
        "provider_response_retention_record_count": 0,
        "provider_response_hash_count": 0,
        "provider_response_text_retained_count": 0,
        "provider_response_stored_chars": 0,
        "provider_response_redacted_count": 0,
        "provider_response_truncated_count": 0,
        "provider_response_retention_modes": {},
        "provider_response_retention_policies": {},
        "provider_error_retention_record_count": 0,
        "provider_error_hash_count": 0,
        "provider_error_text_retained_count": 0,
        "provider_error_stored_chars": 0,
        "provider_error_redacted_count": 0,
        "provider_error_truncated_count": 0,
        "provider_error_retention_modes": {},
        "provider_error_retention_policies": {},
        "provider_diagnostics_record_count": 0,
        "provider_diagnostic_item_count": 0,
        "provider_diagnostic_omitted_item_count": 0,
        "cost_estimate_count": 0,
        "cost_not_estimated_count": 0,
        "configured_pricing_estimate_count": 0,
        "live_pricing_record_count": 0,
        "backend_defaults_record_count": 0,
    }
    for record in call_history:
        if not isinstance(record, dict):
            continue
        group = _provider_diagnostics_group(groups, record)
        group["calls"] += 1
        if record.get("status") == "ok":
            group["successes"] += 1
        elif record.get("status") == "error":
            group["failures"] += 1
        usage = record.get("usage")
        if isinstance(usage, dict):
            totals["usage_record_count"] += 1
            group["usage_record_count"] += 1
            for source, target in (
                ("input_tokens", "input_tokens"),
                ("output_tokens", "output_tokens"),
                ("total_tokens", "total_tokens"),
            ):
                token_count = usage.get(source)
                if (
                    isinstance(token_count, int)
                    and not isinstance(token_count, bool)
                    and token_count > 0
                ):
                    group[target] += token_count
        _add_provider_retention_summary(
            totals,
            group,
            record.get("output_retention"),
            prefix="provider_response",
        )
        _add_provider_retention_summary(
            totals,
            group,
            record.get("error_retention"),
            prefix="provider_error",
        )
        diagnostics = record.get("provider_diagnostics")
        if isinstance(diagnostics, dict):
            totals["provider_diagnostics_record_count"] += 1
            group["provider_diagnostics_record_count"] += 1
            items = diagnostics.get("items")
            if isinstance(items, list):
                totals["provider_diagnostic_item_count"] += len(items)
                group["provider_diagnostic_item_count"] += len(items)
                for item in items:
                    if isinstance(item, dict) and isinstance(item.get("key"), str):
                        _increment_summary_counter(group["diagnostic_keys"], item["key"])
            omitted_items = diagnostics.get("omitted_items")
            if (
                isinstance(omitted_items, int)
                and not isinstance(omitted_items, bool)
                and omitted_items > 0
            ):
                totals["provider_diagnostic_omitted_item_count"] += omitted_items
                group["provider_diagnostic_omitted_item_count"] += omitted_items
        cost_estimate = record.get("cost_estimate")
        if isinstance(cost_estimate, dict):
            totals["cost_estimate_count"] += 1
            group["cost_estimate_count"] += 1
            source = cost_estimate.get("pricing_source")
            if source == "configured_backend_metadata":
                totals["configured_pricing_estimate_count"] += 1
                group["configured_pricing_estimate_count"] += 1
            elif source == "live_provider_pricing":
                totals["live_pricing_record_count"] += 1
                group["live_pricing_record_count"] += 1
        cost_status = record.get("cost_estimate_status")
        if isinstance(cost_status, dict):
            if cost_status.get("status") == "not_estimated":
                totals["cost_not_estimated_count"] += 1
                group["cost_not_estimated_count"] += 1
            reason = cost_status.get("reason")
            if isinstance(reason, str):
                _increment_summary_counter(group["cost_status_reasons"], reason)
        backend_defaults = record.get("backend_defaults")
        if isinstance(backend_defaults, dict):
            totals["backend_defaults_record_count"] += 1
            group["backend_defaults_record_count"] += 1
            api_mode = backend_defaults.get("api_mode")
            if isinstance(api_mode, str):
                _increment_summary_counter(group["backend_default_api_modes"], api_mode)
    totals["provider_response_retention_modes"] = dict(
        sorted(totals["provider_response_retention_modes"].items())
    )
    totals["provider_response_retention_policies"] = dict(
        sorted(totals["provider_response_retention_policies"].items())
    )
    totals["provider_error_retention_modes"] = dict(
        sorted(totals["provider_error_retention_modes"].items())
    )
    totals["provider_error_retention_policies"] = dict(
        sorted(totals["provider_error_retention_policies"].items())
    )
    group_records = []
    for group in groups.values():
        group["provider_response_retention_modes"] = dict(
            sorted(group["provider_response_retention_modes"].items())
        )
        group["provider_response_retention_policies"] = dict(
            sorted(group["provider_response_retention_policies"].items())
        )
        group["provider_error_retention_modes"] = dict(
            sorted(group["provider_error_retention_modes"].items())
        )
        group["provider_error_retention_policies"] = dict(
            sorted(group["provider_error_retention_policies"].items())
        )
        group["diagnostic_keys"] = dict(sorted(group["diagnostic_keys"].items()))
        group["cost_status_reasons"] = dict(sorted(group["cost_status_reasons"].items()))
        group["backend_default_api_modes"] = dict(
            sorted(group["backend_default_api_modes"].items())
        )
        group_records.append(group)
    group_records.sort(
        key=lambda item: (
            item["backend_idx"] if isinstance(item.get("backend_idx"), int) else 999_999,
            str(item.get("backend_name", "")),
            str(item.get("api_mode", "")),
        )
    )
    payload = json.dumps(group_records, sort_keys=True, separators=(",", ":"))
    return {
        "schema": LLM_PROVIDER_DIAGNOSTICS_SCHEMA,
        "policy": "bounded_retained_call_history_provider_diagnostics",
        "status": "snapshot",
        "source": "LLMEnsemble.call_history",
        "call_history_retention": deepcopy(retention),
        "totals": totals,
        "backend_count": len(group_records),
        "backends": group_records,
        "records_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "pricing_readiness": {
            "schema": LLM_PROVIDER_PRICING_READINESS_SCHEMA,
            "live_provider_pricing": False,
            "provider_default_rate_capture": False,
            "account_model_specific_pricing": False,
            "remaining_gap": [
                "live_provider_pricing",
                "provider_default_rate_capture",
                "account_model_specific_pricing",
            ],
        },
        "limitations": [
            "retained_call_history_window_only",
            "provider_response_error_text_retention_follows_configured_modes",
            "bounded_scalar_provider_diagnostics_not_full_raw_provider_payloads",
            "configured_cost_estimates_not_live_provider_pricing",
            "local_backend_defaults_not_remote_provider_defaults",
        ],
    }


def _add_provider_retention_summary(
    totals: dict,
    group: dict,
    retention: object,
    *,
    prefix: str,
) -> None:
    if not isinstance(retention, dict):
        return
    totals[f"{prefix}_retention_record_count"] += 1
    group[f"{prefix}_retention_record_count"] += 1
    mode = retention.get("retention_mode")
    if isinstance(mode, str):
        _increment_summary_counter(totals[f"{prefix}_retention_modes"], mode)
        _increment_summary_counter(group[f"{prefix}_retention_modes"], mode)
    policy = retention.get("retention_policy")
    if isinstance(policy, str):
        _increment_summary_counter(totals[f"{prefix}_retention_policies"], policy)
        _increment_summary_counter(group[f"{prefix}_retention_policies"], policy)
    if isinstance(retention.get("sha256"), str):
        totals[f"{prefix}_hash_count"] += 1
        group[f"{prefix}_hash_count"] += 1
    stored_chars = retention.get("stored_chars")
    if (
        isinstance(stored_chars, int)
        and not isinstance(stored_chars, bool)
        and stored_chars > 0
    ):
        totals[f"{prefix}_text_retained_count"] += 1
        totals[f"{prefix}_stored_chars"] += stored_chars
        group[f"{prefix}_text_retained_count"] += 1
        group[f"{prefix}_stored_chars"] += stored_chars
    if retention.get("redacted") is True:
        totals[f"{prefix}_redacted_count"] += 1
        group[f"{prefix}_redacted_count"] += 1
    if retention.get("truncated") is True:
        totals[f"{prefix}_truncated_count"] += 1
        group[f"{prefix}_truncated_count"] += 1


def _provider_diagnostics_group(groups: dict[str, dict], record: dict) -> dict:
    backend_idx = record.get("backend_idx")
    if isinstance(backend_idx, bool) or not isinstance(backend_idx, int):
        backend_idx = None
    backend_name = record.get("backend_name")
    if not isinstance(backend_name, str) or not backend_name:
        backend_name = "not_recorded"
    api_mode = record.get("api_mode")
    if not isinstance(api_mode, str) or not api_mode:
        api_mode = "unknown"
    key = f"{backend_idx}:{backend_name}:{api_mode}"
    return groups.setdefault(
        key,
        {
            "backend_idx": backend_idx,
            "backend_name": backend_name,
            "api_mode": api_mode,
            "calls": 0,
            "successes": 0,
            "failures": 0,
            "usage_record_count": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "provider_response_retention_record_count": 0,
            "provider_response_hash_count": 0,
            "provider_response_text_retained_count": 0,
            "provider_response_stored_chars": 0,
            "provider_response_redacted_count": 0,
            "provider_response_truncated_count": 0,
            "provider_response_retention_modes": {},
            "provider_response_retention_policies": {},
            "provider_error_retention_record_count": 0,
            "provider_error_hash_count": 0,
            "provider_error_text_retained_count": 0,
            "provider_error_stored_chars": 0,
            "provider_error_redacted_count": 0,
            "provider_error_truncated_count": 0,
            "provider_error_retention_modes": {},
            "provider_error_retention_policies": {},
            "provider_diagnostics_record_count": 0,
            "provider_diagnostic_item_count": 0,
            "provider_diagnostic_omitted_item_count": 0,
            "diagnostic_keys": {},
            "cost_estimate_count": 0,
            "cost_not_estimated_count": 0,
            "configured_pricing_estimate_count": 0,
            "live_pricing_record_count": 0,
            "cost_status_reasons": {},
            "backend_defaults_record_count": 0,
            "backend_default_api_modes": {},
        },
    )


def _increment_summary_counter(counter: dict[str, int], key: str) -> None:
    counter[key] = counter.get(key, 0) + 1


def _provider_failure_category_role_field(category: str) -> str | None:
    if category not in PROVIDER_FAILURE_CATEGORIES:
        return None
    return f"{category}_failures"


def _validate_role_accounting_state(raw: object) -> dict[str, dict[str, int | float]]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("scheduler role_accounting must be a mapping")
    normalized: dict[str, dict[str, int | float]] = {}
    expected = set(_empty_role_accounting_record())
    for role, value in raw.items():
        role = validate_llm_call_role(role)
        if not isinstance(value, dict):
            raise ValueError(f"scheduler role_accounting[{role!r}] must be a mapping")
        missing = sorted(expected - set(value))
        if missing:
            raise ValueError(
                f"scheduler role_accounting[{role!r}] missing fields: {missing}"
            )
        unsupported = sorted(set(value) - expected)
        if unsupported:
            raise ValueError(
                f"scheduler role_accounting[{role!r}] has unsupported fields: {unsupported}"
            )
        item: dict[str, int | float] = {}
        for field in sorted(expected):
            count = value[field]
            if field == "wall_clock_seconds":
                if (
                    isinstance(count, bool)
                    or not isinstance(count, (int, float))
                    or not math.isfinite(float(count))
                    or float(count) < 0.0
                ):
                    raise ValueError(
                        f"scheduler role_accounting[{role!r}].{field} must be a finite non-negative number"
                    )
                item[field] = float(count)
                continue
            if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                raise ValueError(
                    f"scheduler role_accounting[{role!r}].{field} must be a non-negative integer"
                )
            item[field] = count
        if item["successes"] + item["failures"] != item["calls"]:
            raise ValueError(
                f"scheduler role_accounting[{role!r}] status counts must sum to calls"
            )
        if (
            item["reward_accounted_calls"] + item["telemetry_only_calls"]
            != item["calls"]
        ):
            raise ValueError(
                f"scheduler role_accounting[{role!r}] accounting counts must sum to calls"
            )
        normalized[role] = item
    return normalized


def _validate_role_scheduler_state(raw: object, backend_count: int) -> dict[str, dict]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("scheduler role_scheduler_state must be a mapping")
    normalized: dict[str, dict] = {}
    expected = set(_empty_role_scheduler_record(backend_count))
    for role, value in raw.items():
        role = validate_llm_call_role(role)
        if not isinstance(value, dict):
            raise ValueError(
                f"scheduler role_scheduler_state[{role!r}] must be a mapping"
            )
        missing = sorted(expected - set(value))
        if missing:
            raise ValueError(
                f"scheduler role_scheduler_state[{role!r}] missing fields: {missing}"
            )
        unsupported = sorted(set(value) - expected)
        if unsupported:
            raise ValueError(
                f"scheduler role_scheduler_state[{role!r}] has unsupported fields: {unsupported}"
            )
        if value["policy"] != "per_role_scheduler_audit_state_not_selection_policy":
            raise ValueError(
                f"scheduler role_scheduler_state[{role!r}].policy is unsupported"
            )
        selection_policy = value["selection_policy"]
        if selection_policy not in {
            "backend_metadata_role_scoped_when_configured_else_global",
            "global_ensemble_selection_state_is_authoritative",
            "role_owned_bandit_selection_state",
        }:
            raise ValueError(
                "scheduler role_scheduler_state"
                f"[{role!r}].selection_policy is unsupported"
            )
        counts = _validate_scheduler_count_vector(
            value["counts"],
            backend_count,
            f"role_scheduler_state[{role!r}].counts",
        )
        wins = _validate_scheduler_win_vector(
            value["wins"],
            backend_count,
            f"role_scheduler_state[{role!r}].wins",
        )
        total = value["total"]
        if isinstance(total, bool) or not isinstance(total, int) or total < 0:
            raise ValueError(
                f"scheduler role_scheduler_state[{role!r}].total must be a non-negative integer"
            )
        if total < sum(counts):
            raise ValueError(
                f"scheduler role_scheduler_state[{role!r}].total must be >= counts sum"
            )
        unrewarded = _validate_unrewarded_call_ids(
            value["unrewarded_success_call_ids"],
            backend_count,
        )
        rewarded = sorted(_validate_rewarded_call_ids(value["rewarded_call_ids"]))
        all_unrewarded = [
            call_id for per_backend in unrewarded for call_id in per_backend
        ]
        duplicate_unrewarded = _first_duplicate(all_unrewarded)
        if duplicate_unrewarded is not None:
            raise ValueError(
                "scheduler role_scheduler_state"
                f"[{role!r}] call id appears more than once: {duplicate_unrewarded!r}"
            )
        overlap = sorted(set(all_unrewarded) & set(rewarded))
        if overlap:
            raise ValueError(
                "scheduler role_scheduler_state"
                f"[{role!r}] call id cannot be both rewarded and unrewarded: {overlap[0]!r}"
            )
        normalized[role] = {
            "policy": value["policy"],
            "selection_policy": selection_policy,
            "counts": counts,
            "wins": wins,
            "total": total,
            "unrewarded_success_call_ids": unrewarded,
            "rewarded_call_ids": rewarded,
        }
    return normalized


def _validate_reward_accounting_policy(raw: object) -> set[str]:
    if raw is None:
        return set(DEFAULT_REWARD_ACCOUNTED_ROLES)
    if not isinstance(raw, dict):
        raise ValueError("scheduler reward_accounting_policy must be a mapping")
    required = {"policy", "reward_accounted_roles"}
    missing = sorted(required - set(raw))
    if missing:
        raise ValueError(f"scheduler reward_accounting_policy missing fields: {missing}")
    unsupported = sorted(set(raw) - required)
    if unsupported:
        raise ValueError(
            f"scheduler reward_accounting_policy has unsupported fields: {unsupported}"
        )
    if raw["policy"] != "configured_reward_accounted_roles_v1":
        raise ValueError("scheduler reward_accounting_policy policy is unsupported")
    roles = _validate_reward_accounted_roles(raw["reward_accounted_roles"])
    return set(roles)


def _validate_role_call_limits_state(
    raw: object,
) -> tuple[dict[str, int], dict[str, int]]:
    if raw is None:
        return {}, {}
    if not isinstance(raw, dict):
        raise ValueError("scheduler role_call_limits must be a mapping")
    required = {"policy", "max_calls_by_role", "logical_calls_by_role"}
    missing = sorted(required - set(raw))
    if missing:
        raise ValueError(f"scheduler role_call_limits missing fields: {missing}")
    unsupported = sorted(set(raw) - required)
    if unsupported:
        raise ValueError(f"scheduler role_call_limits has unsupported fields: {unsupported}")
    if raw["policy"] != "logical_generate_call_limits_by_role_v1":
        raise ValueError("scheduler role_call_limits policy is unsupported")
    max_calls_by_role = _validate_max_calls_by_role(raw["max_calls_by_role"])
    logical_calls_by_role = _validate_nonnegative_call_count_mapping(
        "scheduler role_call_limits.logical_calls_by_role",
        raw["logical_calls_by_role"],
    )
    for scope, limit in max_calls_by_role.items():
        consumed = _role_scope_consumed(logical_calls_by_role, scope)
        if consumed > limit:
            raise ValueError(
                "scheduler role_call_limits logical_calls_by_role"
                f" exceeds max_calls_by_role[{scope!r}]"
            )
    return max_calls_by_role, logical_calls_by_role


def _validate_role_backend_policy_state(
    raw: object,
    *,
    backend_count: int,
) -> None:
    if raw is None:
        return
    if not isinstance(raw, dict):
        raise ValueError("scheduler role_backend_policy must be a mapping")
    expected = {
        "policy",
        "configured_role_backend_indices",
        "metadata_role_backend_indices",
        "fallback_policy",
    }
    missing = sorted(expected - set(raw))
    if missing:
        raise ValueError(f"scheduler role_backend_policy missing fields: {missing}")
    unsupported = sorted(set(raw) - expected)
    if unsupported:
        raise ValueError(f"scheduler role_backend_policy has unsupported fields: {unsupported}")
    if raw["policy"] != "explicit_role_backend_indices_else_backend_metadata_else_global_v1":
        raise ValueError("scheduler role_backend_policy policy is unsupported")
    if (
        raw["fallback_policy"]
        != "use_backend_metadata_then_global_bandit_when_role_not_configured"
    ):
        raise ValueError("scheduler role_backend_policy fallback_policy is unsupported")
    _validate_role_backend_indices_snapshot(
        raw["configured_role_backend_indices"],
        field="scheduler role_backend_policy.configured_role_backend_indices",
        backend_count=backend_count,
    )
    _validate_role_backend_indices_snapshot(
        raw["metadata_role_backend_indices"],
        field="scheduler role_backend_policy.metadata_role_backend_indices",
        backend_count=backend_count,
    )


def _validate_role_backend_indices_snapshot(
    raw: object,
    *,
    field: str,
    backend_count: int,
) -> None:
    if not isinstance(raw, dict):
        raise ValueError(f"{field} must be a mapping")
    for raw_role, raw_indices in raw.items():
        role = validate_llm_call_role(raw_role)
        if not isinstance(raw_indices, list):
            raise ValueError(f"{field}[{role!r}] must be a list")
        seen: set[int] = set()
        for index, raw_index in enumerate(raw_indices):
            if (
                isinstance(raw_index, bool)
                or not isinstance(raw_index, int)
                or raw_index < 0
                or raw_index >= backend_count
            ):
                raise ValueError(
                    f"{field}[{role!r}][{index}] must be a backend index between 0 and {backend_count - 1}"
                )
            if raw_index in seen:
                raise ValueError(
                    f"{field}[{role!r}] contains duplicate backend index {raw_index}"
                )
            seen.add(raw_index)


def _validate_provider_failure_policy_state(
    raw: object,
    *,
    backend_count: int,
) -> tuple[dict[str, int], dict[str, dict[int, dict]]]:
    if raw is None:
        return {}, {}
    if not isinstance(raw, dict):
        raise ValueError("scheduler provider_failure_policy_state must be a mapping")
    expected = {"schema", "policy", "role_quarantine_after", "roles"}
    missing = sorted(expected - set(raw))
    if missing:
        raise ValueError(
            f"scheduler provider_failure_policy_state missing fields: {missing}"
        )
    unsupported = sorted(set(raw) - expected)
    if unsupported:
        raise ValueError(
            f"scheduler provider_failure_policy_state has unsupported fields: {unsupported}"
        )
    if raw["schema"] != "libreevolve.provider_failure_policy_state.v1":
        raise ValueError("scheduler provider_failure_policy_state schema is unsupported")
    if raw["policy"] != "role_backend_consecutive_failure_quarantine_v1":
        raise ValueError("scheduler provider_failure_policy_state policy is unsupported")
    thresholds = _validate_role_quarantine_thresholds(raw["role_quarantine_after"])
    roles = raw["roles"]
    if not isinstance(roles, dict):
        raise ValueError("scheduler provider_failure_policy_state.roles must be a mapping")
    normalized: dict[str, dict[int, dict]] = {}
    for raw_role, raw_role_state in roles.items():
        role = validate_llm_call_role(raw_role)
        if role not in thresholds:
            raise ValueError(
                "scheduler provider_failure_policy_state role has no quarantine threshold"
            )
        if not isinstance(raw_role_state, dict):
            raise ValueError(
                f"scheduler provider_failure_policy_state.roles[{role!r}] must be a mapping"
            )
        if set(raw_role_state) != {"backends"}:
            raise ValueError(
                f"scheduler provider_failure_policy_state.roles[{role!r}] has unsupported fields"
            )
        backends = raw_role_state["backends"]
        if not isinstance(backends, list):
            raise ValueError(
                f"scheduler provider_failure_policy_state.roles[{role!r}].backends must be a list"
            )
        role_records: dict[int, dict] = {}
        for index, item in enumerate(backends):
            if not isinstance(item, dict):
                raise ValueError(
                    "scheduler provider_failure_policy_state"
                    f".roles[{role!r}].backends[{index}] must be a mapping"
                )
            expected_item = {
                "backend_idx",
                "total_failures",
                "consecutive_failures",
                "quarantined",
                "last_failure_category",
            }
            missing_item = sorted(expected_item - set(item))
            if missing_item:
                raise ValueError(
                    "scheduler provider_failure_policy_state"
                    f".roles[{role!r}].backends[{index}] missing fields: {missing_item}"
                )
            unsupported_item = sorted(set(item) - expected_item)
            if unsupported_item:
                raise ValueError(
                    "scheduler provider_failure_policy_state"
                    f".roles[{role!r}].backends[{index}] has unsupported fields: "
                    f"{unsupported_item}"
                )
            backend_idx = item["backend_idx"]
            if (
                isinstance(backend_idx, bool)
                or not isinstance(backend_idx, int)
                or backend_idx < 0
                or backend_idx >= backend_count
            ):
                raise ValueError(
                    "scheduler provider_failure_policy_state backend_idx is invalid"
                )
            if backend_idx in role_records:
                raise ValueError(
                    "scheduler provider_failure_policy_state backend_idx appears more than once"
                )
            total_failures = item["total_failures"]
            consecutive_failures = item["consecutive_failures"]
            if (
                isinstance(total_failures, bool)
                or not isinstance(total_failures, int)
                or total_failures < 0
            ):
                raise ValueError(
                    "scheduler provider_failure_policy_state total_failures is invalid"
                )
            if (
                isinstance(consecutive_failures, bool)
                or not isinstance(consecutive_failures, int)
                or consecutive_failures < 0
                or consecutive_failures > total_failures
            ):
                raise ValueError(
                    "scheduler provider_failure_policy_state consecutive_failures is invalid"
                )
            if not isinstance(item["quarantined"], bool):
                raise ValueError(
                    "scheduler provider_failure_policy_state quarantined is invalid"
                )
            category = item["last_failure_category"]
            if category is not None and category not in PROVIDER_FAILURE_CATEGORIES:
                raise ValueError(
                    "scheduler provider_failure_policy_state last_failure_category is invalid"
                )
            role_records[backend_idx] = {
                "backend_idx": backend_idx,
                "total_failures": total_failures,
                "consecutive_failures": consecutive_failures,
                "quarantined": item["quarantined"],
                "last_failure_category": category,
            }
        if role_records:
            normalized[role] = role_records
    return thresholds, normalized


def _validate_max_calls_by_role(raw: object) -> dict[str, int]:
    if raw is None:
        return {}
    return _validate_nonnegative_call_scope_mapping(
        "llm max_calls_by_role",
        raw,
    )


def _validate_role_quarantine_thresholds(raw: object) -> dict[str, int]:
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise ValueError(
            "llm role_failure_quarantine_after must be a mapping of role labels to integer thresholds"
        )
    normalized: dict[str, int] = {}
    for raw_role, raw_count in raw.items():
        role = validate_llm_call_role(raw_role)
        if (
            isinstance(raw_count, bool)
            or not isinstance(raw_count, int)
            or raw_count <= 0
        ):
            raise ValueError(
                f"llm role_failure_quarantine_after[{role!r}] must be a positive integer"
            )
        normalized[role] = raw_count
    return dict(sorted(normalized.items()))


def _validate_nonnegative_call_count_mapping(
    field: str,
    raw: object,
) -> dict[str, int]:
    if not isinstance(raw, Mapping):
        raise ValueError(f"{field} must be a mapping of role labels to integer limits")
    normalized: dict[str, int] = {}
    for raw_role, raw_count in raw.items():
        role = validate_llm_call_role(raw_role)
        if (
            isinstance(raw_count, bool)
            or not isinstance(raw_count, int)
            or raw_count < 0
        ):
            raise ValueError(f"{field}[{role!r}] must be a non-negative integer")
        normalized[role] = raw_count
    return dict(sorted(normalized.items()))


def _validate_nonnegative_call_scope_mapping(
    field: str,
    raw: object,
) -> dict[str, int]:
    if not isinstance(raw, Mapping):
        raise ValueError(f"{field} must be a mapping of role labels to integer limits")
    normalized: dict[str, int] = {}
    for raw_role, raw_count in raw.items():
        role = validate_llm_role_scope(raw_role)
        if (
            isinstance(raw_count, bool)
            or not isinstance(raw_count, int)
            or raw_count < 0
        ):
            raise ValueError(f"{field}[{role!r}] must be a non-negative integer")
        normalized[role] = raw_count
    return dict(sorted(normalized.items()))


def validate_llm_role_scope(role: object) -> str:
    if isinstance(role, str) and role.endswith(":*"):
        validate_llm_call_role(role[:-2])
        return role
    return validate_llm_call_role(role)


def _role_scope_matches(scope: str, role: str) -> bool:
    if scope.endswith(":*"):
        return role.startswith(scope[:-1])
    return scope == role


def _role_scope_consumed(consumed: Mapping[str, int], scope: str) -> int:
    if scope.endswith(":*"):
        return sum(value for role, value in consumed.items() if _role_scope_matches(scope, role))
    return consumed.get(scope, 0)


def _validate_reward_accounted_roles(raw: object) -> tuple[str, ...]:
    if not isinstance(raw, (list, tuple)):
        raise ValueError("llm reward_accounted_roles must be a list of role labels")
    if not raw:
        raise ValueError("llm reward_accounted_roles must include at least one role")
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw:
        role = validate_llm_call_role(item)
        if role not in seen:
            seen.add(role)
            normalized.append(role)
    return tuple(normalized)


def _validate_call_history_retention_state(raw: object) -> None:
    if not isinstance(raw, dict):
        raise ValueError("scheduler call_history_retention must be a mapping")
    required = {
        "policy",
        "max_records",
        "retained_records",
        "total_records",
        "dropped_records",
    }
    missing = sorted(required - set(raw))
    if missing:
        raise ValueError(f"scheduler call_history_retention missing fields: {missing}")
    unsupported = sorted(set(raw) - required)
    if unsupported:
        raise ValueError(f"scheduler call_history_retention has unsupported fields: {unsupported}")
    if raw["policy"] != "bounded_in_memory_window":
        raise ValueError("scheduler call_history_retention policy is unsupported")
    max_records = _validate_retention_counter("max_records", raw["max_records"], minimum=1)
    retained_records = _validate_retention_counter("retained_records", raw["retained_records"])
    total_records = _validate_retention_counter("total_records", raw["total_records"])
    dropped_records = _validate_retention_counter("dropped_records", raw["dropped_records"])
    if retained_records > max_records:
        raise ValueError("scheduler call_history_retention retained_records exceeds max_records")
    if dropped_records > total_records:
        raise ValueError("scheduler call_history_retention dropped_records exceeds total_records")


def _validate_retention_counter(name: str, raw: object, *, minimum: int = 0) -> int:
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < minimum:
        raise ValueError(f"scheduler call_history_retention {name} must be an integer >= {minimum}")
    return raw


def _validate_unrewarded_call_ids(raw: object, backend_count: int) -> list[list[str]]:
    if raw is None:
        return [[] for _ in range(backend_count)]
    if not isinstance(raw, list) or len(raw) != backend_count:
        raise ValueError("scheduler unrewarded_success_call_ids must contain one list per backend")
    normalized: list[list[str]] = []
    for backend_idx, call_ids in enumerate(raw):
        if not isinstance(call_ids, list):
            raise ValueError(
                f"scheduler unrewarded_success_call_ids[{backend_idx}] must be a list"
            )
        normalized.append(
            [
                _validate_scheduler_call_id(
                    call_id,
                    f"scheduler unrewarded_success_call_ids[{backend_idx}]",
                )
                for call_id in call_ids
            ]
        )
    return normalized


def _validate_rewarded_call_ids(raw: object) -> set[str]:
    if raw is None:
        return set()
    if not isinstance(raw, list):
        raise ValueError("scheduler rewarded_call_ids must be a list")
    normalized = [
        _validate_scheduler_call_id(call_id, "scheduler rewarded_call_ids")
        for call_id in raw
    ]
    duplicate = _first_duplicate(normalized)
    if duplicate is not None:
        raise ValueError(f"scheduler call id appears more than once: {duplicate!r}")
    return set(normalized)


def _validate_scheduler_call_id(raw: object, field: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError(f"{field} must contain non-empty call ids")
    return raw


def _first_duplicate(values: list[str]) -> str | None:
    seen: set[str] = set()
    for value in values:
        if value in seen:
            return value
        seen.add(value)
    return None


def _validate_fallback(fallback: object) -> bool:
    if not isinstance(fallback, bool):
        raise ValueError("llm fallback must be boolean")
    return fallback


def _validate_backend_metadata(metadata: object, backend_count: int) -> list[dict]:
    if metadata is None:
        return [{} for _ in range(backend_count)]
    if not isinstance(metadata, list):
        raise ValueError("backend_metadata must be a list of mappings")
    if len(metadata) != backend_count:
        raise ValueError("backend_metadata must contain one mapping per backend")
    normalized: list[dict] = []
    for index, item in enumerate(metadata):
        if not isinstance(item, dict):
            raise ValueError(f"backend_metadata[{index}] must be a mapping")
        normalized.append(_validate_metadata_mapping(item, f"backend_metadata[{index}]"))
    return normalized


def _validate_metadata_mapping(mapping: dict, path: str) -> dict:
    normalized: dict = {}
    for key, value in mapping.items():
        key = _validate_metadata_key(key, path)
        if key in {"cost", "latency", "depth", _COST_USD_PER_MILLION_TOKENS_FIELD}:
            normalized[key] = _validate_positive_metadata_number(f"{path}.{key}", value)
        elif key in {
            _PROMPT_MAX_ESTIMATED_TOKENS_FIELD,
            _CONTEXT_WINDOW_TOKENS_FIELD,
        }:
            normalized[key] = validate_backend_max_tokens(value, field=f"{path}.{key}")
        elif key == _RESERVED_OUTPUT_TOKENS_FIELD:
            normalized[key] = _validate_non_negative_metadata_int(
                f"{path}.{key}",
                value,
            )
        elif key == "role":
            normalized[key] = validate_llm_call_role(value)
        else:
            normalized[key] = _validate_json_safe_metadata_value(value, f"{path}.{key}")
    _validate_backend_context_window_budget(normalized, path)
    return normalized


def _validate_request_parameters_telemetry(value: object, path: str) -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be a mapping")
    supported = REQUEST_PARAMETER_FIELDS
    unsupported = sorted(set(value) - supported)
    if unsupported:
        raise ValueError(f"{path} has unsupported fields: {unsupported}")
    normalized = validate_backend_request_parameters(
        {"type": "codex", **value},
        field_prefix=path,
    )
    return normalized


def _validate_backend_defaults_telemetry(value: object, path: str) -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be a mapping")
    if not value:
        return {}
    supported = {
        "policy",
        "max_tokens",
        "provider_max_retries",
        "timeout_sec",
        "api_mode",
        "api_mode_policy",
        "reasoning_effort",
    }
    unsupported = sorted(set(value) - supported)
    if unsupported:
        raise ValueError(f"{path} has unsupported fields: {unsupported}")
    if value.get("policy") != "effective_backend_generation_defaults_v1":
        raise ValueError(f"{path}.policy is unsupported")
    normalized: dict[str, object] = {
        "policy": value["policy"],
        "max_tokens": validate_backend_max_tokens(
            value.get("max_tokens"),
            field=f"{path}.max_tokens",
        ),
        "provider_max_retries": validate_provider_max_retries(
            value.get("provider_max_retries"),
            field=f"{path}.provider_max_retries",
        ),
    }
    timeout = value.get("timeout_sec")
    if timeout is None:
        normalized["timeout_sec"] = None
    else:
        normalized["timeout_sec"] = _validate_positive_metadata_number(
            f"{path}.timeout_sec",
            timeout,
        )
    for field in ("api_mode", "api_mode_policy", "reasoning_effort"):
        item = value.get(field)
        if item is None:
            normalized[field] = None
        elif _is_safe_api_mode(item):
            normalized[field] = item
        else:
            raise ValueError(f"{path}.{field} must be a manifest-safe label or null")
    return normalized


def _validate_client_context_telemetry(value: object, path: str) -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be a mapping")
    unsupported = sorted(set(value) - CLIENT_CONTEXT_FIELDS)
    if unsupported:
        raise ValueError(f"{path} has unsupported fields: {unsupported}")
    normalized: dict = {}
    if "base_url" in value:
        normalized["base_url"] = validate_endpoint_url(value["base_url"], field=f"{path}.base_url")
    if "host" in value:
        normalized["host"] = validate_endpoint_url(value["host"], field=f"{path}.host")
    for key in ("organization", "project"):
        if key in value:
            normalized[key] = validate_client_context_label(value[key], field=f"{path}.{key}")
    return normalized


def _validate_prompt_role_policy_telemetry(value: object, path: str) -> dict:
    if value is None:
        return prompt_role_policy_record({}, "mutation")
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be a mapping")
    allowed = {
        "policy",
        "matched_role",
        "message_roles",
        "instruction_fields",
        "instruction_metadata",
    }
    unsupported = sorted(set(value) - allowed)
    if unsupported:
        raise ValueError(f"{path} has unsupported fields: {unsupported}")
    policy = value.get("policy")
    if policy not in {"single_user_message", "configured_structured_messages"}:
        raise ValueError(f"{path}.policy is unsupported")
    matched_role = value.get("matched_role")
    if matched_role is not None:
        matched_role = validate_llm_call_role(matched_role)
    message_roles = _validate_prompt_message_roles(
        value.get("message_roles"),
        f"{path}.message_roles",
    )
    instruction_fields = _validate_prompt_instruction_fields(
        value.get("instruction_fields"),
        f"{path}.instruction_fields",
    )
    metadata = _validate_prompt_instruction_metadata(
        value.get("instruction_metadata", {}),
        f"{path}.instruction_metadata",
    )
    if policy == "single_user_message":
        if matched_role is not None or message_roles != ["user"] or instruction_fields or metadata:
            raise ValueError(f"{path} single_user_message payload is inconsistent")
    else:
        if matched_role is None:
            raise ValueError(f"{path}.matched_role is required for structured messages")
        if not instruction_fields:
            raise ValueError(f"{path}.instruction_fields must not be empty")
        if message_roles != [*instruction_fields, "user"]:
            raise ValueError(f"{path}.message_roles must match instruction fields plus user")
        if set(metadata) != set(instruction_fields):
            raise ValueError(f"{path}.instruction_metadata must match instruction fields")
    return {
        "policy": policy,
        "matched_role": matched_role,
        "message_roles": message_roles,
        "instruction_fields": instruction_fields,
        "instruction_metadata": metadata,
    }


def _validate_prompt_message_roles(value: object, path: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{path} must be a list")
    allowed = {"system", "developer", "user"}
    normalized: list[str] = []
    for index, item in enumerate(value):
        if item not in allowed:
            raise ValueError(f"{path}[{index}] is unsupported")
        normalized.append(item)
    if normalized.count("user") != 1 or normalized[-1] != "user":
        raise ValueError(f"{path} must end with exactly one user role")
    return normalized


def _validate_prompt_instruction_fields(value: object, path: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{path} must be a list")
    allowed = {"system", "developer"}
    normalized: list[str] = []
    for index, item in enumerate(value):
        if item not in allowed:
            raise ValueError(f"{path}[{index}] is unsupported")
        if item in normalized:
            raise ValueError(f"{path} must not contain duplicate fields")
        normalized.append(item)
    if normalized != [field for field in ("system", "developer") if field in normalized]:
        raise ValueError(f"{path} must preserve system/developer order")
    return normalized


def _validate_prompt_instruction_metadata(value: object, path: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be a mapping")
    normalized: dict = {}
    for key, item in value.items():
        if key not in {"system", "developer"}:
            raise ValueError(f"{path} keys are unsupported")
        if not isinstance(item, dict):
            raise ValueError(f"{path}.{key} must be a mapping")
        unsupported = sorted(set(item) - {"chars", "sha256", "redacted"})
        if unsupported:
            raise ValueError(f"{path}.{key} has unsupported fields: {unsupported}")
        chars = item.get("chars")
        if isinstance(chars, bool) or not isinstance(chars, int) or chars <= 0:
            raise ValueError(f"{path}.{key}.chars must be a positive integer")
        sha256 = item.get("sha256")
        if not isinstance(sha256, str) or re.fullmatch(r"[0-9a-f]{64}", sha256) is None:
            raise ValueError(f"{path}.{key}.sha256 must be a SHA-256 hex digest")
        redacted = item.get("redacted")
        if not isinstance(redacted, bool):
            raise ValueError(f"{path}.{key}.redacted must be boolean")
        normalized[key] = {"chars": chars, "sha256": sha256, "redacted": redacted}
    return normalized


def _validate_metadata_key(key: object, path: str) -> str:
    if not isinstance(key, str) or not key:
        raise ValueError(f"{path} keys must be non-empty strings")
    if redact_sensitive_text(key) != key:
        raise ValueError(f"{path} keys must be manifest-safe metadata labels")
    if _METADATA_KEY_RE.fullmatch(key) is None:
        raise ValueError(f"{path} keys must be manifest-safe metadata labels")
    return key


def _validate_positive_metadata_number(path: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{path} must be a finite positive number")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric <= 0.0:
        raise ValueError(f"{path} must be a finite positive number")
    return numeric


def _validate_non_negative_metadata_int(path: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{path} must be a non-negative integer")
    return value


def _validate_backend_context_window_budget(metadata: dict, path: str) -> None:
    context_window = metadata.get(_CONTEXT_WINDOW_TOKENS_FIELD)
    if context_window is None and _RESERVED_OUTPUT_TOKENS_FIELD in metadata:
        raise ValueError(
            f"{path}.{_RESERVED_OUTPUT_TOKENS_FIELD} requires "
            f"{path}.{_CONTEXT_WINDOW_TOKENS_FIELD}"
        )
    if context_window is None:
        return
    reserved = metadata.get(_RESERVED_OUTPUT_TOKENS_FIELD, 0)
    if not isinstance(reserved, int) or isinstance(reserved, bool) or reserved < 0:
        raise ValueError(
            f"{path}.{_RESERVED_OUTPUT_TOKENS_FIELD} must be a non-negative integer"
        )
    if reserved >= context_window:
        raise ValueError(
            f"{path}.{_RESERVED_OUTPUT_TOKENS_FIELD} must be less than "
            f"{path}.{_CONTEXT_WINDOW_TOKENS_FIELD}"
        )


def _backend_context_window_prompt_limit(metadata: object) -> int | None:
    if not isinstance(metadata, dict):
        return None
    context_window = metadata.get(_CONTEXT_WINDOW_TOKENS_FIELD)
    if context_window is None:
        return None
    reserved = metadata.get(_RESERVED_OUTPUT_TOKENS_FIELD, 0)
    if (
        isinstance(context_window, bool)
        or not isinstance(context_window, int)
        or context_window < 1
        or isinstance(reserved, bool)
        or not isinstance(reserved, int)
        or reserved < 0
        or reserved >= context_window
    ):
        return None
    return context_window - reserved


def _validate_json_safe_metadata_value(value: object, path: str) -> object:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        if redact_sensitive_text(value) != value:
            raise ValueError(f"{path} must not contain secret-like text")
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path} must be finite")
        return value
    if isinstance(value, list):
        return [
            _validate_json_safe_metadata_value(item, f"{path}[{index}]")
            for index, item in enumerate(value)
        ]
    if isinstance(value, dict):
        return _validate_metadata_mapping(value, path)
    raise ValueError(f"{path} must be JSON-safe metadata")


def validate_llm_response_text(
    response: object,
    *,
    source: str = "LLM backend",
    max_chars: int | None = DEFAULT_MAX_RESPONSE_CHARS,
) -> str:
    if not isinstance(response, str):
        raise ProviderResponseError(
            f"{source} returned non-text output: {type(response).__name__}",
            category="non_text",
            source=source,
            value_type=type(response).__name__,
        )
    if not response.strip():
        raise ProviderResponseError(
            f"{source} returned empty output",
            category="empty_text",
            source=source,
        )
    if max_chars is not None:
        limit = _validate_max_response_chars(max_chars)
        if len(response) > limit:
            raise ProviderResponseError(
                f"{source} response exceeded maximum accepted size: "
                f"{len(response)} chars > {limit}",
                category="oversized_text",
                source=source,
            )
    return response


def _require_response_text(
    response: object,
    *,
    max_chars: int = DEFAULT_MAX_RESPONSE_CHARS,
) -> str:
    return validate_llm_response_text(response, max_chars=max_chars)


def _call_backend_generate(
    backend: LLMBackend,
    prompt: str,
    *,
    role: str,
    timeout_sec: float | None,
) -> object:
    if timeout_sec is None:
        return backend.generate(prompt, role=role)

    result_queue: queue.Queue[tuple[str, object]] = queue.Queue(maxsize=1)
    # Require an explicitly declared method, not a dynamically fabricated
    # attribute on proxy/mock backends that never opted into cancellation.
    cancellable_generate = (
        getattr(backend, "generate_cancellable")
        if callable(getattr(type(backend), "generate_cancellable", None)) else None
    )
    cancel_event = threading.Event() if callable(cancellable_generate) else None

    def run_call() -> None:
        try:
            if cancel_event is None:
                response = backend.generate(prompt, role=role)
            else:
                response = cancellable_generate(prompt, cancel_event=cancel_event, role=role)
            result_queue.put(("ok", response))
        except Exception as exc:
            result_queue.put(("error", exc))

    worker = threading.Thread(
        target=run_call,
        name="libreevolve-llm-call",
        daemon=True,
    )
    def cancel_local_worker() -> str:
        if cancel_event is None:
            return "unsupported_daemon_worker_may_continue"
        # Allocate the event before starting: cancellation must not be lost
        # when the worker has not entered its backend yet. The bounded join
        # allows the local CLI's five-second bounded reap to finish.
        cancel_event.set()
        if worker.ident is not None:
            worker.join(timeout=6.0)
        return (
            "cooperative_backend_worker_may_continue" if worker.is_alive()
            else "cooperative_backend_worker_finished"
        )

    try:
        worker.start()
        status, payload = result_queue.get(timeout=timeout_sec)
    except queue.Empty as exc:
        error = ProviderCallTimeoutError(timeout_sec)
        error.in_flight_cancellation = cancel_local_worker()
        raise error from exc
    except BaseException:
        cancel_local_worker()
        raise
    if status == "error":
        assert isinstance(payload, Exception)
        raise payload
    return payload


def build_llm(config) -> LLMEnsemble:
    """Instantiate LLMEnsemble from config.backends."""
    prompt_roles = validate_prompt_role_policy(
        getattr(config, "llm_prompt_roles", {}),
        field="llm_prompt_roles",
    )
    from libreevolve.llm.backend_registry import build_registry_backends

    backends, metadata = build_registry_backends(
        config.backends,
        prompt_roles=prompt_roles,
    )
    return LLMEnsemble(
        backends,
        explore_coeff=config.ensemble_explore_coeff,
        strategy=config.ensemble_strategy,
        backend_metadata=metadata,
        max_retries=config.llm_max_retries,
        max_call_attempts=config.llm_max_call_attempts,
        fallback=config.llm_fallback,
        max_response_chars=config.llm_max_response_chars,
        max_call_history=config.llm_call_history_max,
        call_timeout_sec=config.llm_call_timeout_sec,
        provider_response_retention_mode=config.provider_response_retention_mode,
        provider_error_retention_mode=config.provider_error_retention_mode,
        max_prompt_chars=config.prompt_max_chars,
        max_prompt_estimated_tokens=config.prompt_max_estimated_tokens,
        reward_accounted_roles=config.llm_reward_accounted_roles,
        role_scheduler_scope=config.llm_role_scheduler_scope,
        max_calls_by_role=config.llm_role_call_limits,
        role_backend_indices=config.llm_role_backend_indices,
        role_failure_quarantine_after=config.llm_role_failure_quarantine_after,
    )


def _normalize_backend_specs(backends: object) -> list[dict]:
    if not isinstance(backends, list) or not backends:
        raise ValueError("backends must be a non-empty list of mappings")
    allowed_types = {"codex"}
    common_keys = {
        "type",
        "model",
        "max_tokens",
        "cost",
        _COST_USD_PER_MILLION_TOKENS_FIELD,
        _PROMPT_MAX_ESTIMATED_TOKENS_FIELD,
        _CONTEXT_WINDOW_TOKENS_FIELD,
        _RESERVED_OUTPUT_TOKENS_FIELD,
        "latency",
        "depth",
        "role",
        *REQUEST_PARAMETER_FIELDS,
    }
    normalized: list[dict] = []
    for index, spec in enumerate(backends):
        label = f"backends[{index}]"
        if not isinstance(spec, dict):
            raise ValueError(f"{label} must be a mapping")
        if not all(isinstance(key, str) for key in spec):
            raise ValueError(f"{label} keys must be strings")
        backend_type = spec.get("type")
        if backend_type not in allowed_types:
            raise ValueError(f"{label}.type must be one of {sorted(allowed_types)}")
        allowed = set(common_keys)
        if backend_type == "codex":
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
        unsupported = sorted(set(spec) - allowed)
        if unsupported:
            raise ValueError(f"{label} has unsupported fields {unsupported}")
        item = {
            "type": backend_type,
            "model": validate_backend_model_id(spec.get("model"), field=f"{label}.model"),
        }
        if "max_tokens" in spec:
            item["max_tokens"] = validate_backend_max_tokens(
                spec["max_tokens"],
                field=f"{label}.max_tokens",
            )
        if "timeout_sec" in spec:
            item["timeout_sec"] = _validate_positive_metadata_number(
                f"{label}.timeout_sec",
                spec["timeout_sec"],
            )
        if backend_type == "codex":
            for field_name in (
                "cwd",
                "sandbox",
                "reasoning_effort",
                "transcript_dir",
                "codex_home",
                "auth_name",
                "auth_registry_path",
                "profile",
                "approval_policy",
                "output_json_field",
                "enable_features",
                "disable_features",
            ):
                if field_name in spec:
                    item[field_name] = spec[field_name]
            if "auth_homes" in spec:
                item["auth_homes"] = deepcopy(spec["auth_homes"])
            for field_name in ("ignore_user_config", "ignore_rules", "ephemeral"):
                if field_name in spec:
                    item[field_name] = bool(spec[field_name])
        for field_name in ("cost", "latency", "depth"):
            if field_name in spec:
                item[field_name] = _validate_positive_metadata_number(
                    f"{label}.{field_name}",
                    spec[field_name],
                )
        if _COST_USD_PER_MILLION_TOKENS_FIELD in spec:
            item[_COST_USD_PER_MILLION_TOKENS_FIELD] = (
                _validate_positive_metadata_number(
                    f"{label}.{_COST_USD_PER_MILLION_TOKENS_FIELD}",
                    spec[_COST_USD_PER_MILLION_TOKENS_FIELD],
                )
            )
        if _PROMPT_MAX_ESTIMATED_TOKENS_FIELD in spec:
            item[_PROMPT_MAX_ESTIMATED_TOKENS_FIELD] = validate_backend_max_tokens(
                spec[_PROMPT_MAX_ESTIMATED_TOKENS_FIELD],
                field=f"{label}.{_PROMPT_MAX_ESTIMATED_TOKENS_FIELD}",
            )
        if _CONTEXT_WINDOW_TOKENS_FIELD in spec:
            item[_CONTEXT_WINDOW_TOKENS_FIELD] = validate_backend_max_tokens(
                spec[_CONTEXT_WINDOW_TOKENS_FIELD],
                field=f"{label}.{_CONTEXT_WINDOW_TOKENS_FIELD}",
            )
        if _RESERVED_OUTPUT_TOKENS_FIELD in spec:
            item[_RESERVED_OUTPUT_TOKENS_FIELD] = _validate_non_negative_metadata_int(
                f"{label}.{_RESERVED_OUTPUT_TOKENS_FIELD}",
                spec[_RESERVED_OUTPUT_TOKENS_FIELD],
            )
        elif _CONTEXT_WINDOW_TOKENS_FIELD in item and "max_tokens" in item:
            item[_RESERVED_OUTPUT_TOKENS_FIELD] = item["max_tokens"]
        _validate_backend_context_window_budget(item, label)
        if "role" in spec:
            item["role"] = validate_llm_call_role(spec["role"])
        item.update(validate_backend_request_parameters({**spec, **item}, field_prefix=label))
        item.update(validate_backend_client_context({**spec, **item}, field_prefix=label))
        normalized.append(item)
    return normalized


def _is_control_or_format(character: str) -> bool:
    return unicodedata.category(character).startswith("C")
