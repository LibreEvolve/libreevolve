from __future__ import annotations
from copy import deepcopy
import math
import time
import openai as openai_sdk
from libreevolve.llm.client_context import (
    copy_client_context,
    validate_backend_client_context,
)
from libreevolve.llm.ensemble import (
    ProviderResponseError,
    validate_backend_max_tokens,
    validate_backend_model_id,
    validate_llm_prompt,
    validate_llm_response_text,
    validate_openai_api_mode,
    validate_openai_reasoning_effort,
)
from libreevolve.llm.openai_compat import resolve_openai_api_mode
from libreevolve.llm.provider_metadata import (
    copy_provider_response_metadata,
    safe_provider_response_metadata,
)
from libreevolve.llm.provider_retry import (
    DEFAULT_PROVIDER_MAX_RETRIES,
    provider_retry_failure,
    validate_provider_max_retries,
    with_provider_retry_metadata,
)
from libreevolve.llm.prompt_roles import (
    copy_prompt_role_policy,
    openai_chat_messages,
    openai_responses_input,
    prompt_role_policy_record,
)
from libreevolve.llm.request_params import (
    request_parameters_for_provider,
    validate_backend_request_parameters,
)

class OpenAIBackend:
    def __init__(self, model: str = "gpt-4o", max_tokens: int = 4096,
                 reasoning_effort: str | None = None,
                 api_mode: str | None = None,
                 temperature: float | None = None,
                 top_p: float | None = None,
                 stop: str | list[str] | None = None,
                 seed: int | None = None,
                 timeout_sec: float | None = None,
                 base_url: str | None = None,
                 organization: str | None = None,
                 project: str | None = None,
                 provider_max_retries: int = DEFAULT_PROVIDER_MAX_RETRIES,
                 prompt_roles: dict | None = None):
        self._model = validate_backend_model_id(model)
        self._max_tokens = validate_backend_max_tokens(max_tokens)
        self._reasoning_effort = validate_openai_reasoning_effort(
            reasoning_effort,
            model=self._model,
        )
        self._api_mode_policy = validate_openai_api_mode(
            api_mode,
            reasoning_effort=self._reasoning_effort,
        )
        self._api_mode = resolve_openai_api_mode(
            self._api_mode_policy,
            reasoning_effort=self._reasoning_effort,
        )
        client_spec = {"type": "openai"}
        for key, value in {
            "base_url": base_url,
            "organization": organization,
            "project": project,
        }.items():
            if value is not None:
                client_spec[key] = value
        self._client_context = validate_backend_client_context(client_spec)
        request_spec = {
            "type": "openai",
            "api_mode": self._api_mode_policy,
            "reasoning_effort": self._reasoning_effort,
        }
        for key, value in {
            "temperature": temperature,
            "top_p": top_p,
            "stop": stop,
            "seed": seed,
        }.items():
            if value is not None:
                request_spec[key] = value
        self._request_parameters = validate_backend_request_parameters(request_spec)
        client_kwargs = dict(self._client_context)
        if timeout_sec is not None:
            client_kwargs["timeout"] = _validate_timeout_sec(timeout_sec)
        self._timeout_sec = client_kwargs.get("timeout")
        self._provider_max_retries = validate_provider_max_retries(provider_max_retries)
        self._prompt_roles = copy_prompt_role_policy(prompt_roles)
        self._client = openai_sdk.OpenAI(**client_kwargs)
        self._provider_response_metadata: dict = {}
    @property
    def name(self) -> str: return f"openai/{self._model}"
    @property
    def api_mode(self) -> str:
        return self._api_mode
    @property
    def request_parameters(self) -> dict:
        return deepcopy(self._request_parameters)
    @property
    def backend_defaults(self) -> dict:
        return {
            "policy": "effective_backend_generation_defaults_v1",
            "max_tokens": self._max_tokens,
            "provider_max_retries": self._provider_max_retries,
            "timeout_sec": self._timeout_sec,
            "api_mode": self._api_mode,
            "api_mode_policy": self._api_mode_policy,
            "reasoning_effort": self._reasoning_effort,
        }
    @property
    def client_context(self) -> dict:
        return copy_client_context(self._client_context)
    @property
    def provider_response_metadata(self) -> dict:
        return copy_provider_response_metadata(self._provider_response_metadata)
    def prompt_role_policy_for_role(self, role: str) -> dict:
        return prompt_role_policy_record(self._prompt_roles, role)
    def generate(self, prompt: str, **kwargs) -> str:
        prompt = validate_llm_prompt(prompt)
        role = kwargs.get("role", "mutation")
        self._provider_response_metadata = {}
        failures: list[dict] = []
        for attempt in range(self._provider_max_retries + 1):
            try:
                if self._api_mode == "responses":
                    text = self._generate_responses(prompt, role=role)
                else:
                    text = self._generate_chat(prompt, role=role)
                self._provider_response_metadata = with_provider_retry_metadata(
                    self._provider_response_metadata,
                    max_retries=self._provider_max_retries,
                    attempts=attempt + 1,
                    failures=failures,
                )
                return text
            except Exception as exc:
                failures.append(provider_retry_failure(attempt, exc))
                self._provider_response_metadata = with_provider_retry_metadata(
                    self._provider_response_metadata,
                    max_retries=self._provider_max_retries,
                    attempts=attempt + 1,
                    failures=failures,
                )
                if attempt >= self._provider_max_retries:
                    raise
                time.sleep(2 ** attempt)
        raise RuntimeError("unreachable")

    def _generate_chat(self, prompt: str, *, role: str) -> str:
        payload = {
            "model": self._model,
            "max_completion_tokens": self._max_tokens,
            "messages": openai_chat_messages(prompt, self._prompt_roles, role),
        }
        payload.update(
            request_parameters_for_provider(
                backend_type="openai",
                api_mode="chat_completions",
                parameters=self._request_parameters,
            )
        )
        r = self._client.chat.completions.create(**payload)
        self._provider_response_metadata = _openai_chat_metadata(r)
        message = r.choices[0].message
        content = getattr(message, "content", None)
        if _has_provider_signal(getattr(message, "refusal", None)):
            raise ProviderResponseError(
                "OpenAI Chat Completions returned a refusal without output text",
                category="refusal",
                source="OpenAI Chat Completions",
            )
        if _has_provider_signal(getattr(message, "tool_calls", None)) and not content:
            raise ProviderResponseError(
                "OpenAI Chat Completions returned only tool calls without output text",
                category="tool_call_only",
                source="OpenAI Chat Completions",
            )
        return validate_llm_response_text(
            content,
            source="OpenAI Chat Completions",
            max_chars=None,
        )

    def _generate_responses(self, prompt: str, *, role: str) -> str:
        payload = {
            "model": self._model,
            "max_output_tokens": self._max_tokens,
            "input": openai_responses_input(prompt, self._prompt_roles, role),
        }
        payload.update(
            request_parameters_for_provider(
                backend_type="openai",
                api_mode="responses",
                parameters=self._request_parameters,
            )
        )
        if self._reasoning_effort is not None:
            payload["reasoning"] = {"effort": self._reasoning_effort}
        r = self._client.responses.create(**payload)
        self._provider_response_metadata = _openai_responses_metadata(r)
        # Extract text from response output items
        saw_refusal = False
        saw_tool_call = False
        for item in r.output:
            item_type = getattr(item, "type", None)
            if item_type in {"function_call", "tool_call"}:
                saw_tool_call = True
            if item.type == "message":
                for part in item.content:
                    part_type = getattr(part, "type", None)
                    if part_type == "output_text":
                        return validate_llm_response_text(
                            part.text,
                            source="OpenAI Responses",
                            max_chars=None,
                        )
                    if part_type == "refusal":
                        saw_refusal = True
                    elif part_type in {"tool_call", "function_call"}:
                        saw_tool_call = True
        if saw_refusal:
            raise ProviderResponseError(
                "OpenAI Responses returned a refusal without output text",
                category="refusal",
                source="OpenAI Responses",
            )
        if saw_tool_call:
            raise ProviderResponseError(
                "OpenAI Responses returned only tool calls without output text",
                category="tool_call_only",
                source="OpenAI Responses",
            )
        return validate_llm_response_text("", source="OpenAI Responses", max_chars=None)


def _has_provider_signal(value: object) -> bool:
    if value is None:
        return False
    if value.__class__.__module__.startswith("unittest.mock"):
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _openai_chat_metadata(response: object) -> dict:
    choice = _first_choice(response)
    finish_reason = _safe_text(getattr(choice, "finish_reason", None))
    return safe_provider_response_metadata(
        {
            "usage": _usage_from_object(
                getattr(response, "usage", None),
                input_attr="prompt_tokens",
                output_attr="completion_tokens",
            ),
            "finish_reason": finish_reason,
            "request_id": _safe_text(getattr(response, "_request_id", None)),
            "response_id": _safe_text(getattr(response, "id", None)),
            "provider_diagnostics": _safe_provider_diagnostics(
                {
                    "system_fingerprint": getattr(response, "system_fingerprint", None),
                    "service_tier": getattr(response, "service_tier", None),
                    "has_choice_logprobs": (
                        True if _has_provider_signal(getattr(choice, "logprobs", None)) else None
                    ),
                }
            ),
        }
    )


def _openai_responses_metadata(response: object) -> dict:
    return safe_provider_response_metadata(
        {
            "usage": _usage_from_object(
                getattr(response, "usage", None),
                input_attr="input_tokens",
                output_attr="output_tokens",
            ),
            "finish_reason": _safe_text(getattr(response, "status", None)),
            "request_id": _safe_text(getattr(response, "_request_id", None)),
            "response_id": _safe_text(getattr(response, "id", None)),
            "provider_diagnostics": _safe_provider_diagnostics(
                {
                    "parallel_tool_calls": getattr(response, "parallel_tool_calls", None),
                    "created_at": getattr(response, "created_at", None),
                }
            ),
        }
    )


def _usage_from_object(usage: object, *, input_attr: str, output_attr: str) -> dict | None:
    input_tokens = _safe_int(getattr(usage, input_attr, None))
    output_tokens = _safe_int(getattr(usage, output_attr, None))
    total_tokens = _safe_int(getattr(usage, "total_tokens", None))
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    metadata = {}
    if input_tokens is not None:
        metadata["input_tokens"] = input_tokens
    if output_tokens is not None:
        metadata["output_tokens"] = output_tokens
    if total_tokens is not None:
        metadata["total_tokens"] = total_tokens
    return metadata or None


def _first_choice(response: object) -> object | None:
    choices = getattr(response, "choices", None)
    if isinstance(choices, (list, tuple)) and choices:
        return choices[0]
    return None


def _safe_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value if value >= 0 else None


def _safe_text(value: object) -> str | None:
    if value is None or value.__class__.__module__.startswith("unittest.mock"):
        return None
    return value if isinstance(value, str) and value else None


def _safe_provider_diagnostics(values: dict[str, object]) -> dict | None:
    diagnostics = {}
    for key, value in values.items():
        if value is None or value.__class__.__module__.startswith("unittest.mock"):
            continue
        if isinstance(value, float) and not math.isfinite(value):
            continue
        if isinstance(value, (str, bool, int, float)) and value != "":
            diagnostics[key] = value
    return diagnostics or None


def _validate_timeout_sec(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("timeout_sec must be a finite number > 0")
    timeout = float(value)
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout_sec must be a finite number > 0")
    return timeout
