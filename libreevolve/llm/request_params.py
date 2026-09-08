from __future__ import annotations

from collections.abc import Mapping

REQUEST_PARAMETER_FIELDS = {"temperature", "top_p", "stop", "seed"}


def validate_backend_request_parameters(
    spec: Mapping[str, object],
    *,
    field_prefix: str = "backend",
) -> dict[str, object]:
    unsupported = sorted(REQUEST_PARAMETER_FIELDS.intersection(spec))
    if unsupported:
        raise ValueError(f"{field_prefix} request parameters {unsupported} are not supported by Codex")
    return {}
