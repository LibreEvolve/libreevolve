from __future__ import annotations
from copy import deepcopy
import math
import time
import anthropic as anthropic_sdk
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
)
from libreevolve.llm.request_params import (
    request_parameters_for_provider,
    validate_backend_request_parameters,
)
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
    anthropic_messages,
    anthropic_system,
    copy_prompt_role_policy,
    prompt_role_policy_record,
)

class AnthropicBackend:
    def __init__(
        self,
        model: str = "claude-sonnet-4-6",
        max_tokens: int = 4096,
        temperature: float | None = None,
        top_p: float | None = None,
        stop: str | list[str] | None = None,
        seed: int | None = None,
        timeout_sec: float | None = None,
        base_url: str | None = None,
        provider_max_retries: int = DEFAULT_PROVIDER_MAX_RETRIES,
        prompt_roles: dict | None = None,
    ):
        self._model = validate_backend_model_id(model)
        self._max_tokens = validate_backend_max_tokens(max_tokens)
        client_spec = {"type": "anthropic"}
        if base_url is not None:
            client_spec["base_url"] = base_url
        self._client_context = validate_backend_client_context(client_spec)
        request_spec = {"type": "anthropic"}
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
        self._client = anthropic_sdk.Anthropic(**client_kwargs)
        self._provider_response_metadata: dict = {}
    @property
    def name(self) -> str: return f"anthropic/{self._model}"
    @property
    def api_mode(self) -> str:
        return "messages"
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
            "api_mode": self.api_mode,
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
                payload = {
                    "model": self._model,
                    "max_tokens": self._max_tokens,
                    "messages": anthropic_messages(prompt),
                }
                system = anthropic_system(self._prompt_roles, role)
                if system is not None:
                    payload["system"] = system
                payload.update(
                    request_parameters_for_provider(
                        backend_type="anthropic",
                        parameters=self._request_parameters,
                    )
                )
                msg = self._client.messages.create(**payload)
                self._provider_response_metadata = _anthropic_metadata(msg)
                content = getattr(msg, "content", None)
                text = None
                saw_refusal = False
                saw_tool_use = False
                if isinstance(content, (list, tuple)) and content:
                    for block in content:
                        block_type = getattr(block, "type", None)
                        if block_type == "refusal":
                            saw_refusal = True
                            continue
                        if block_type == "tool_use":
                            saw_tool_use = True
                            continue
                        block_text = getattr(block, "text", None)
                        if block_text is not None:
                            text = block_text
                            break
                if text is None and saw_refusal:
                    raise ProviderResponseError(
                        "Anthropic Messages returned a refusal without output text",
                        category="refusal",
                        source="Anthropic Messages",
                    )
                if text is None and saw_tool_use:
                    raise ProviderResponseError(
                        "Anthropic Messages returned only tool use without output text",
                        category="tool_call_only",
                        source="Anthropic Messages",
                    )
                text = validate_llm_response_text(
                    text,
                    source="Anthropic Messages",
                    max_chars=None,
                )
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


def _anthropic_metadata(message: object) -> dict:
    usage = getattr(message, "usage", None)
    input_tokens = _safe_int(getattr(usage, "input_tokens", None))
    output_tokens = _safe_int(getattr(usage, "output_tokens", None))
    usage_metadata = {}
    if input_tokens is not None:
        usage_metadata["input_tokens"] = input_tokens
    if output_tokens is not None:
        usage_metadata["output_tokens"] = output_tokens
    if input_tokens is not None and output_tokens is not None:
        usage_metadata["total_tokens"] = input_tokens + output_tokens
    return safe_provider_response_metadata(
        {
            "usage": usage_metadata or None,
            "finish_reason": _safe_text(getattr(message, "stop_reason", None)),
            "request_id": _safe_text(getattr(message, "_request_id", None)),
            "response_id": _safe_text(getattr(message, "id", None)),
            "provider_diagnostics": _safe_provider_diagnostics(
                {
                    "model": getattr(message, "model", None),
                    "type": getattr(message, "type", None),
                }
            ),
        }
    )


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
