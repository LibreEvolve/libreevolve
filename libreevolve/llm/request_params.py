from __future__ import annotations

import math
import unicodedata
from collections.abc import Mapping
from typing import Any

from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.llm.openai_compat import resolve_openai_api_mode

REQUEST_PARAMETER_FIELDS = {"temperature", "top_p", "stop", "seed"}
OPENAI_CHAT_ONLY_REQUEST_PARAMETER_FIELDS = {"stop", "seed"}


def validate_backend_request_parameters(
    spec: Mapping[str, object],
    *,
    field_prefix: str = "backend",
) -> dict[str, object]:
    backend_type = spec.get("type")
    normalized: dict[str, object] = {}
    if "temperature" in spec:
        normalized["temperature"] = validate_temperature(
            spec["temperature"],
            field=f"{field_prefix}.temperature",
            backend_type=backend_type,
        )
    if "top_p" in spec:
        normalized["top_p"] = validate_top_p(spec["top_p"], field=f"{field_prefix}.top_p")
    if "stop" in spec:
        normalized["stop"] = validate_stop_sequences(
            spec["stop"],
            field=f"{field_prefix}.stop",
        )
    if "seed" in spec:
        normalized["seed"] = validate_request_seed(spec["seed"], field=f"{field_prefix}.seed")
    _validate_provider_support(
        backend_type,
        spec,
        normalized,
        field_prefix=field_prefix,
    )
    return normalized


def validate_temperature(
    value: object,
    *,
    field: str = "temperature",
    backend_type: object = None,
) -> float:
    numeric = _finite_number(value, field)
    upper = 2.0 if backend_type in {"openai", "ollama"} else 1.0
    if numeric < 0.0 or numeric > upper:
        raise ValueError(f"{field} must be between 0 and {upper:g}")
    return numeric


def validate_top_p(value: object, *, field: str = "top_p") -> float:
    numeric = _finite_number(value, field)
    if numeric <= 0.0 or numeric > 1.0:
        raise ValueError(f"{field} must be > 0 and <= 1")
    return numeric


def validate_stop_sequences(value: object, *, field: str = "stop") -> list[str]:
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, list):
        items = list(value)
    else:
        raise ValueError(f"{field} must be a string or list of strings")
    if not items:
        raise ValueError(f"{field} must include at least one stop sequence")
    if len(items) > 16:
        raise ValueError(f"{field} must include at most 16 stop sequences")
    normalized: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, str):
            raise ValueError(f"{field}[{index}] must be a string")
        if not item:
            raise ValueError(f"{field}[{index}] must be non-empty")
        if redact_sensitive_text(item) != item or any(_is_control_or_format(char) for char in item):
            raise ValueError(f"{field}[{index}] must be JSON-safe request text")
        if item not in seen:
            seen.add(item)
            normalized.append(item)
    return normalized


def validate_request_seed(value: object, *, field: str = "seed") -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    if value > 2_147_483_647:
        raise ValueError(f"{field} must be <= 2147483647")
    return value


def request_parameters_for_provider(
    *,
    backend_type: str,
    api_mode: str | None = None,
    parameters: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    parameters = dict(parameters or {})
    if backend_type == "openai":
        payload: dict[str, Any] = {}
        for key in ("temperature", "top_p"):
            if key in parameters:
                payload[key] = parameters[key]
        if api_mode == "chat_completions":
            if "stop" in parameters:
                payload["stop"] = list(parameters["stop"])
            if "seed" in parameters:
                payload["seed"] = parameters["seed"]
        return payload
    if backend_type == "anthropic":
        payload = {}
        for key in ("temperature", "top_p"):
            if key in parameters:
                payload[key] = parameters[key]
        if "stop" in parameters:
            payload["stop_sequences"] = list(parameters["stop"])
        return payload
    if backend_type == "ollama":
        payload = {}
        for key in ("temperature", "top_p", "seed"):
            if key in parameters:
                payload[key] = parameters[key]
        if "stop" in parameters:
            payload["stop"] = list(parameters["stop"])
        return payload
    return dict(parameters)


def _validate_provider_support(
    backend_type: object,
    spec: Mapping[str, object],
    normalized: Mapping[str, object],
    *,
    field_prefix: str,
) -> None:
    if not normalized:
        return
    if backend_type == "custom":
        raise ValueError(
            f"{field_prefix} request parameters are not supported for custom backends; "
            "use kwargs for custom provider-specific settings"
        )
    if backend_type == "anthropic" and "seed" in normalized:
        raise ValueError(f"{field_prefix}.seed is not supported for anthropic backends")
    if backend_type == "openai" and OPENAI_CHAT_ONLY_REQUEST_PARAMETER_FIELDS & set(normalized):
        api_mode = resolve_openai_api_mode(
            spec.get("api_mode"),
            reasoning_effort=spec.get("reasoning_effort"),
        )
        if api_mode != "chat_completions":
            fields = sorted(OPENAI_CHAT_ONLY_REQUEST_PARAMETER_FIELDS & set(normalized))
            raise ValueError(
                f"{field_prefix} fields {fields} are supported only for OpenAI "
                "Chat Completions mode"
            )


def _finite_number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a finite number")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{field} must be a finite number")
    return numeric


def _is_control_or_format(character: str) -> bool:
    return unicodedata.category(character).startswith("C")
