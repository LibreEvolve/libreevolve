from __future__ import annotations
from copy import deepcopy
import math
import time
import ollama as ollama_sdk
from libreevolve.llm.client_context import (
    copy_client_context,
    validate_backend_client_context,
)
from libreevolve.llm.ensemble import (
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
    copy_prompt_role_policy,
    ollama_messages,
    prompt_role_policy_record,
)

class OllamaBackend:
    def __init__(
        self,
        model: str = "llama3",
        max_tokens: int = 4096,
        temperature: float | None = None,
        top_p: float | None = None,
        stop: str | list[str] | None = None,
        seed: int | None = None,
        timeout_sec: float | None = None,
        host: str | None = None,
        provider_max_retries: int = DEFAULT_PROVIDER_MAX_RETRIES,
        prompt_roles: dict | None = None,
    ):
        self._model = validate_backend_model_id(model)
        self._max_tokens = validate_backend_max_tokens(max_tokens)
        client_spec = {"type": "ollama"}
        if host is not None:
            client_spec["host"] = host
        self._client_context = validate_backend_client_context(client_spec)
        request_spec = {"type": "ollama"}
        for key, value in {
            "temperature": temperature,
            "top_p": top_p,
            "stop": stop,
            "seed": seed,
        }.items():
            if value is not None:
                request_spec[key] = value
        self._request_parameters = validate_backend_request_parameters(request_spec)
        self._timeout_sec = _validate_timeout_sec(timeout_sec) if timeout_sec is not None else None
        self._provider_max_retries = validate_provider_max_retries(provider_max_retries)
        if "host" in self._client_context or self._timeout_sec is not None:
            client_kwargs = {}
            if "host" in self._client_context:
                client_kwargs["host"] = self._client_context["host"]
            if self._timeout_sec is not None:
                client_kwargs["timeout"] = self._timeout_sec
            self._client = ollama_sdk.Client(**client_kwargs)
        else:
            self._client = None
        self._prompt_roles = copy_prompt_role_policy(prompt_roles)
        self._provider_response_metadata: dict = {}
    @property
    def name(self) -> str: return f"ollama/{self._model}"
    @property
    def api_mode(self) -> str:
        return "chat"
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
                options = {"num_predict": self._max_tokens}
                options.update(
                    request_parameters_for_provider(
                        backend_type="ollama",
                        parameters=self._request_parameters,
                    )
                )
                chat = self._client.chat if self._client is not None else ollama_sdk.chat
                r = chat(model=self._model,
                         messages=ollama_messages(prompt, self._prompt_roles, role),
                         options=options)
                self._provider_response_metadata = _ollama_metadata(r)
                content = None
                if isinstance(r, dict):
                    message = r.get("message")
                    if isinstance(message, dict):
                        content = message.get("content")
                text = validate_llm_response_text(
                    content,
                    source="Ollama Chat",
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


def _ollama_metadata(response: object) -> dict:
    if not isinstance(response, dict):
        return {}
    input_tokens = _safe_int(response.get("prompt_eval_count"))
    output_tokens = _safe_int(response.get("eval_count"))
    usage = {}
    if input_tokens is not None:
        usage["input_tokens"] = input_tokens
    if output_tokens is not None:
        usage["output_tokens"] = output_tokens
    if input_tokens is not None and output_tokens is not None:
        usage["total_tokens"] = input_tokens + output_tokens
    return safe_provider_response_metadata(
        {
            "usage": usage or None,
            "finish_reason": _safe_text(response.get("done_reason")),
            "provider_diagnostics": _safe_provider_diagnostics(
                {
                    "model": response.get("model"),
                    "done": response.get("done"),
                    "total_duration": response.get("total_duration"),
                    "load_duration": response.get("load_duration"),
                    "prompt_eval_duration": response.get("prompt_eval_duration"),
                    "eval_duration": response.get("eval_duration"),
                }
            ),
        }
    )


def _safe_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value if value >= 0 else None


def _safe_text(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _safe_provider_diagnostics(values: dict[str, object]) -> dict | None:
    diagnostics = {}
    for key, value in values.items():
        if value is None:
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
