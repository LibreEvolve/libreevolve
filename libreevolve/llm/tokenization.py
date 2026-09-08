from __future__ import annotations

from collections.abc import Callable, Mapping


PROMPT_TOKEN_COUNTER_CAPABILITY_SCHEMA = (
    "libreevolve.prompt_token_counter_capability.v1"
)
PROMPT_TOKEN_COUNTER_CAPABILITY_POLICY = (
    "eligible_backend_common_provider_counter_optional_dependency_v1"
)


def discover_prompt_token_counter(
    backends: object,
    *,
    role: str = "mutation",
    role_backend_indices: Mapping[str, object] | None = None,
) -> tuple[Callable[[str], int] | None, dict]:
    """Return a safe prompt token counter shared by all eligible backends.

    This intentionally only enables counters that are locally available and
    common across the backend set that may receive the rendered prompt.
    """
    specs = _backend_specs(backends)
    eligible = _eligible_backend_indices(
        specs,
        role=role,
        role_backend_indices=role_backend_indices,
    )
    backend_records: list[dict] = []
    ready: list[tuple[int, str, Callable[[str], int]]] = []
    for index in eligible:
        counter, record = _backend_prompt_token_counter(specs[index], index)
        backend_records.append(record)
        if counter is not None:
            ready.append((index, record["counter_name"], counter))
    selected_counter: Callable[[str], int] | None = None
    status = "unavailable"
    reason = "no_eligible_backend_provider_counter"
    counter_name: str | None = None
    if ready and len(ready) == len(eligible):
        counter_names = {item[1] for item in ready}
        if len(counter_names) == 1:
            status = "ready"
            reason = "common_provider_counter_available"
            counter_name = ready[0][1]
            selected_counter = ready[0][2]
        else:
            reason = "eligible_backends_do_not_share_counter"
    elif ready:
        reason = "some_eligible_backends_lack_provider_counter"
    record = {
        "schema": PROMPT_TOKEN_COUNTER_CAPABILITY_SCHEMA,
        "policy": PROMPT_TOKEN_COUNTER_CAPABILITY_POLICY,
        "role": role,
        "status": status,
        "reason": reason,
        "counter_name": counter_name,
        "eligible_backend_indices": eligible,
        "selection_scope": (
            "role_scoped_backends" if _configured_role_indices(role_backend_indices, role) else
            "backend_metadata_role_match_when_available"
        ),
        "backends": backend_records,
    }
    return selected_counter, record


def _backend_specs(backends: object) -> list[Mapping[str, object]]:
    if not isinstance(backends, list):
        return []
    return [item for item in backends if isinstance(item, Mapping)]


def _eligible_backend_indices(
    specs: list[Mapping[str, object]],
    *,
    role: str,
    role_backend_indices: Mapping[str, object] | None,
) -> list[int]:
    configured = _configured_role_indices(role_backend_indices, role)
    if configured is not None:
        return [
            index
            for index in configured
            if isinstance(index, int)
            and not isinstance(index, bool)
            and 0 <= index < len(specs)
        ]
    role_matches = [
        index
        for index, spec in enumerate(specs)
        if isinstance(spec.get("role"), str) and spec.get("role") == role
    ]
    if role_matches:
        return role_matches
    return list(range(len(specs)))


def _configured_role_indices(
    role_backend_indices: Mapping[str, object] | None,
    role: str,
) -> list[int] | None:
    if not isinstance(role_backend_indices, Mapping) or role not in role_backend_indices:
        return None
    value = role_backend_indices[role]
    if not isinstance(value, (list, tuple)):
        return None
    return list(value)


def _backend_prompt_token_counter(
    spec: Mapping[str, object],
    index: int,
) -> tuple[Callable[[str], int] | None, dict]:
    backend_type = spec.get("type")
    model = spec.get("model")
    record = {
        "backend_idx": index,
        "type": backend_type if isinstance(backend_type, str) else "unknown",
        "model": model if isinstance(model, str) else None,
        "status": "unavailable",
        "source": None,
        "counter_name": None,
        "reason": "no_local_tokenizer_registered",
    }
    return None, record
