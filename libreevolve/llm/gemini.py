from __future__ import annotations

from copy import deepcopy
import enum
import math
import os
import time

from google import genai as genai_sdk
from google.genai import types as genai_types

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
from libreevolve.llm.prompt_roles import (
    copy_prompt_role_policy,
    gemini_system,
    prompt_role_policy_record,
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
from libreevolve.llm.request_params import (
    request_parameters_for_provider,
    validate_backend_request_parameters,
)


DEFAULT_GEMINI_API_VERSION = "v1beta"
SUPPORTED_GEMINI_API_VERSIONS = {"v1", "v1alpha", "v1beta"}
_BLOCKED_FINISH_REASONS = {
    "BLOCKLIST",
    "IMAGE_PROHIBITED_CONTENT",
    "IMAGE_RECITATION",
    "IMAGE_SAFETY",
    "PROHIBITED_CONTENT",
    "RECITATION",
    "SAFETY",
    "SPII",
}
_INCOMPLETE_FINISH_REASONS = {
    "FINISH_REASON_UNSPECIFIED",
    "LANGUAGE",
    "MALFORMED_FUNCTION_CALL",
    "MAX_TOKENS",
    "NO_IMAGE",
    "OTHER",
    "UNEXPECTED_TOOL_CALL",
}


class GeminiBackend:
    """Gemini Developer API text backend using the Google Gen AI SDK."""

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        max_tokens: int = 4096,
        temperature: float | None = None,
        top_p: float | None = None,
        stop: str | list[str] | None = None,
        seed: int | None = None,
        timeout_sec: float | None = None,
        api_version: str = DEFAULT_GEMINI_API_VERSION,
        provider_max_retries: int = DEFAULT_PROVIDER_MAX_RETRIES,
        prompt_roles: dict | None = None,
    ):
        self._model = validate_backend_model_id(model)
        self._max_tokens = validate_backend_max_tokens(max_tokens)
        self._api_version = validate_gemini_api_version(api_version)
        self._client_context = validate_backend_client_context(
            {"type": "gemini", "api_version": self._api_version}
        )
        request_spec = {"type": "gemini"}
        for key, value in {
            "temperature": temperature,
            "top_p": top_p,
            "stop": stop,
            "seed": seed,
        }.items():
            if value is not None:
                request_spec[key] = value
        self._request_parameters = validate_backend_request_parameters(request_spec)
        self._timeout_sec = (
            _validate_timeout_sec(timeout_sec) if timeout_sec is not None else None
        )
        self._provider_max_retries = validate_provider_max_retries(
            provider_max_retries
        )
        self._prompt_roles = copy_prompt_role_policy(prompt_roles)
        http_options = genai_types.HttpOptions(
            api_version=self._api_version,
            timeout=(
                int(math.ceil(self._timeout_sec * 1000.0))
                if self._timeout_sec is not None
                else None
            ),
        )
        self._client = genai_sdk.Client(
            api_key=_gemini_api_key_from_environment(),
            http_options=http_options,
        )
        self._provider_response_metadata: dict = {}

    @property
    def name(self) -> str:
        return f"gemini/{self._model}"

    @property
    def api_mode(self) -> str:
        return "generate_content"

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
            "api_version": self._api_version,
            "provider_service": "gemini_developer_api",
            "model_lane": gemini_model_lane(self._model),
        }

    @property
    def client_context(self) -> dict:
        return copy_client_context(self._client_context)

    @property
    def provider_response_metadata(self) -> dict:
        return copy_provider_response_metadata(self._provider_response_metadata)

    def prompt_role_policy_for_role(self, role: str) -> dict:
        return prompt_role_policy_record(self._prompt_roles, role)

    def generate(self, prompt: str, **kwargs: object) -> str:
        prompt = validate_llm_prompt(prompt)
        role = kwargs.get("role", "mutation")
        self._provider_response_metadata = {}
        failures: list[dict] = []
        for attempt in range(self._provider_max_retries + 1):
            try:
                config = {
                    "max_output_tokens": self._max_tokens,
                    **request_parameters_for_provider(
                        backend_type="gemini",
                        parameters=self._request_parameters,
                    ),
                }
                system = gemini_system(self._prompt_roles, role)
                if system is not None:
                    config["system_instruction"] = system
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(**config),
                )
                self._provider_response_metadata = _gemini_metadata(response)
                text = _gemini_response_text(response)
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
                time.sleep(2**attempt)
        raise RuntimeError("unreachable")


def validate_gemini_api_version(
    value: object,
    *,
    field: str = "api_version",
) -> str:
    if not isinstance(value, str) or value not in SUPPORTED_GEMINI_API_VERSIONS:
        raise ValueError(
            f"{field} must be one of {sorted(SUPPORTED_GEMINI_API_VERSIONS)}"
        )
    return value


def gemini_model_lane(model: object) -> str:
    text = model.lower() if isinstance(model, str) else ""
    if "flash" in text:
        return "flash"
    if "pro" in text:
        return "pro"
    return "general"


def _gemini_api_key_from_environment() -> str:
    # The SDK gives GOOGLE_API_KEY precedence when both variables are present.
    for name in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
        value = os.getenv(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError(
        "gemini backend requires GOOGLE_API_KEY or GEMINI_API_KEY"
    )


def _gemini_response_text(response: object) -> str:
    candidates = getattr(response, "candidates", None)
    if not isinstance(candidates, (list, tuple)) or not candidates:
        block_reason = _enum_label(
            getattr(getattr(response, "prompt_feedback", None), "block_reason", None)
        )
        if block_reason:
            raise ProviderResponseError(
                "Gemini GenerateContent blocked the prompt without a candidate",
                category="refusal",
                source="Gemini GenerateContent",
            )
        raise ProviderResponseError(
            "Gemini GenerateContent returned no candidates",
            category="empty_response",
            source="Gemini GenerateContent",
        )
    candidate = candidates[0]
    finish_reason = _enum_label(getattr(candidate, "finish_reason", None))
    if finish_reason in _BLOCKED_FINISH_REASONS:
        raise ProviderResponseError(
            f"Gemini GenerateContent blocked candidate output ({finish_reason})",
            category="refusal",
            source="Gemini GenerateContent",
        )
    if finish_reason != "STOP":
        category = (
            "incomplete"
            if finish_reason in _INCOMPLETE_FINISH_REASONS or finish_reason is None
            else "unsupported_completion_state"
        )
        raise ProviderResponseError(
            "Gemini GenerateContent did not return a complete STOP candidate",
            category=category,
            source="Gemini GenerateContent",
        )
    content = getattr(candidate, "content", None)
    parts = getattr(content, "parts", None)
    if not isinstance(parts, (list, tuple)):
        parts = []
    text_parts: list[str] = []
    saw_tool = False
    for part in parts:
        text = getattr(part, "text", None)
        if isinstance(text, str) and text:
            text_parts.append(text)
        if _has_provider_signal(getattr(part, "function_call", None)) or _has_provider_signal(
            getattr(part, "tool_call", None)
        ):
            saw_tool = True
    if saw_tool and text_parts:
        raise ProviderResponseError(
            "Gemini GenerateContent returned mixed text and tool-call output",
            category="mixed_content",
            source="Gemini GenerateContent",
        )
    if saw_tool:
        raise ProviderResponseError(
            "Gemini GenerateContent returned only tool calls without output text",
            category="tool_call_only",
            source="Gemini GenerateContent",
        )
    return validate_llm_response_text(
        "".join(text_parts),
        source="Gemini GenerateContent",
        max_chars=None,
    )


def _gemini_metadata(response: object) -> dict:
    candidates = getattr(response, "candidates", None)
    candidate_rows = (
        list(candidates) if isinstance(candidates, (list, tuple)) else []
    )
    first = candidate_rows[0] if candidate_rows else None
    parts = getattr(getattr(first, "content", None), "parts", None)
    part_rows = list(parts) if isinstance(parts, (list, tuple)) else []
    usage = getattr(response, "usage_metadata", None)
    return safe_provider_response_metadata(
        {
            "usage": _gemini_usage(usage),
            "finish_reason": _enum_label(getattr(first, "finish_reason", None)),
            "response_id": _safe_text(getattr(response, "response_id", None)),
            "provider_diagnostics": {
                "model_version": getattr(response, "model_version", None),
                "candidate_count": len(candidate_rows),
                "content_part_count": len(part_rows),
                "text_part_count": sum(
                    1 for part in part_rows if isinstance(getattr(part, "text", None), str)
                ),
                "tool_call_part_count": sum(
                    1
                    for part in part_rows
                    if _has_provider_signal(getattr(part, "function_call", None))
                    or _has_provider_signal(getattr(part, "tool_call", None))
                ),
                "prompt_block_reason": _enum_label(
                    getattr(
                        getattr(response, "prompt_feedback", None),
                        "block_reason",
                        None,
                    )
                ),
                "thoughts_token_count": _safe_int(
                    getattr(usage, "thoughts_token_count", None)
                ),
            },
        }
    )


def _gemini_usage(usage: object) -> dict | None:
    input_tokens = _safe_int(getattr(usage, "prompt_token_count", None))
    output_tokens = _safe_int(getattr(usage, "candidates_token_count", None))
    total_tokens = _safe_int(getattr(usage, "total_token_count", None))
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    result = {}
    if input_tokens is not None:
        result["input_tokens"] = input_tokens
    if output_tokens is not None:
        result["output_tokens"] = output_tokens
    if total_tokens is not None:
        result["total_tokens"] = total_tokens
    return result or None


def _enum_label(value: object) -> str | None:
    if isinstance(value, enum.Enum):
        value = value.value
    if not isinstance(value, str) or not value:
        return None
    if "." in value:
        value = value.rsplit(".", 1)[-1]
    return value if value else None


def _safe_text(value: object) -> str | None:
    if value is None or value.__class__.__module__.startswith("unittest.mock"):
        return None
    return value if isinstance(value, str) and value else None


def _safe_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value if value >= 0 else None


def _has_provider_signal(value: object) -> bool:
    if value is None or value.__class__.__module__.startswith("unittest.mock"):
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _validate_timeout_sec(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("timeout_sec must be a finite number > 0")
    timeout = float(value)
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout_sec must be a finite number > 0")
    return timeout
