from __future__ import annotations

from copy import deepcopy

from libreevolve.llm.request_params import REQUEST_PARAMETER_FIELDS


BUILTIN_BACKEND_TYPES = ("anthropic", "codex", "openai", "ollama")
BACKEND_REGISTRY_SCHEMA = "libreevolve.backend_registry.v1"


def builtin_backend_registry() -> dict[str, dict]:
    """Return metadata for backend types constructed by LibreEvolve."""
    return {
        "anthropic": {
            "type": "anthropic",
            "constructor": "libreevolve.llm.anthropic:AnthropicBackend",
            "constructor_fields": [
                "model",
                "max_tokens",
                "timeout_sec",
                "provider_max_retries",
                "base_url",
                *sorted(REQUEST_PARAMETER_FIELDS),
            ],
            "schema": BACKEND_REGISTRY_SCHEMA,
        },
        "codex": {
            "type": "codex",
            "constructor": "libreevolve.llm.codex_cli:CodexCLIBackend",
            "constructor_fields": [
                "model",
                "max_tokens",
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
            ],
            "schema": BACKEND_REGISTRY_SCHEMA,
        },
        "openai": {
            "type": "openai",
            "constructor": "libreevolve.llm.openai:OpenAIBackend",
            "constructor_fields": [
                "model",
                "max_tokens",
                "timeout_sec",
                "provider_max_retries",
                "reasoning_effort",
                "api_mode",
                "base_url",
                "organization",
                "project",
                *sorted(REQUEST_PARAMETER_FIELDS),
            ],
            "schema": BACKEND_REGISTRY_SCHEMA,
        },
        "ollama": {
            "type": "ollama",
            "constructor": "libreevolve.llm.ollama:OllamaBackend",
            "constructor_fields": [
                "model",
                "max_tokens",
                "timeout_sec",
                "provider_max_retries",
                "host",
                *sorted(REQUEST_PARAMETER_FIELDS),
            ],
            "schema": BACKEND_REGISTRY_SCHEMA,
        },
    }


def validate_backend_registry_specs(specs: object) -> list[dict]:
    """Validate backend specs for registry-created provider constructors."""
    from libreevolve.llm.ensemble import validate_restored_backend_specs

    return validate_restored_backend_specs(specs)


def build_registry_backends(specs: object, *, prompt_roles: dict | None = None) -> tuple[list, list[dict]]:
    """Build backend objects and metadata from validated registry specs."""
    normalized = validate_backend_registry_specs(specs)
    backends = []
    for spec in normalized:
        backend_type = spec["type"]
        if backend_type == "custom":
            from libreevolve.llm.ensemble import build_custom_backend_from_spec

            backends.append(build_custom_backend_from_spec(spec))
            continue
        cls = _backend_class(backend_type)
        kwargs = {
            key: value
            for key, value in spec.items()
            if key in _constructor_fields(backend_type)
        }
        if prompt_roles:
            kwargs["prompt_roles"] = deepcopy(prompt_roles)
        backends.append(cls(**kwargs))
    metadata = [_backend_metadata_from_spec(spec) for spec in normalized]
    return backends, metadata


def _constructor_fields(backend_type: str) -> set[str]:
    registry = builtin_backend_registry()
    if backend_type not in registry:
        raise ValueError(
            f"Unknown backend type {backend_type!r}. Valid: ['anthropic', 'codex', 'custom', 'openai', 'ollama']"
        )
    return set(registry[backend_type]["constructor_fields"])


def _backend_class(backend_type: str):
    if backend_type == "anthropic":
        from libreevolve.llm.anthropic import AnthropicBackend

        return AnthropicBackend
    if backend_type == "openai":
        from libreevolve.llm.openai import OpenAIBackend

        return OpenAIBackend
    if backend_type == "codex":
        from libreevolve.llm.codex_cli import CodexCLIBackend

        return CodexCLIBackend
    if backend_type == "ollama":
        from libreevolve.llm.ollama import OllamaBackend

        return OllamaBackend
    raise ValueError(
        f"Unknown backend type {backend_type!r}. Valid: ['anthropic', 'codex', 'custom', 'openai', 'ollama']"
    )


def _backend_metadata_from_spec(spec: dict) -> dict:
    metadata = {
        "cost": spec.get("cost", 1.0),
        "latency": spec.get("latency", 1.0),
        "depth": spec.get("depth", 1.0),
        "role": spec.get("role", "general"),
    }
    if "cost_usd_per_million_tokens" in spec:
        metadata["cost_usd_per_million_tokens"] = spec[
            "cost_usd_per_million_tokens"
        ]
    if "prompt_max_estimated_tokens" in spec:
        metadata["prompt_max_estimated_tokens"] = spec[
            "prompt_max_estimated_tokens"
        ]
    if "context_window_tokens" in spec:
        metadata["context_window_tokens"] = spec["context_window_tokens"]
        metadata["reserved_output_tokens"] = spec.get(
            "reserved_output_tokens",
            spec.get("max_tokens", 0),
        )
    return metadata
