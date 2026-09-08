from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Mapping
from copy import deepcopy
from urllib.parse import urlparse

from libreevolve.core.redaction import redact_sensitive_text

CLIENT_CONTEXT_FIELDS = {"api_version", "base_url", "organization", "project", "host"}
_CLIENT_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")


def validate_backend_client_context(
    spec: Mapping[str, object],
    *,
    field_prefix: str = "backend",
) -> dict[str, object]:
    unsupported = sorted(set(spec) & CLIENT_CONTEXT_FIELDS)
    if unsupported:
        raise ValueError(f"{field_prefix} has unsupported client context fields {unsupported}")
    return {}


def validate_endpoint_url(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty URL string")
    if value != value.strip() or len(value) > 512:
        raise ValueError(f"{field} must be a manifest-safe endpoint URL")
    if redact_sensitive_text(value) != value or any(_is_control_or_format(char) for char in value):
        raise ValueError(f"{field} must be a manifest-safe endpoint URL")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"{field} must be an http(s) URL with a host")
    if parsed.username or parsed.password or parsed.params or parsed.query or parsed.fragment:
        raise ValueError(f"{field} must not include credentials, params, query, or fragment")
    if parsed.hostname != parsed.hostname.strip():
        raise ValueError(f"{field} must include a manifest-safe host")
    if redact_sensitive_text(parsed.hostname) != parsed.hostname:
        raise ValueError(f"{field} must include a manifest-safe host")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"{field} port must be between 1 and 65535") from exc
    if port is not None and not (1 <= port <= 65535):
        raise ValueError(f"{field} port must be between 1 and 65535")
    if parsed.path and not _safe_url_path(parsed.path):
        raise ValueError(f"{field} must include a path-safe URL path")
    return value


def validate_client_context_label(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty manifest-safe label")
    if value != value.strip() or len(value) > 128:
        raise ValueError(f"{field} must be a manifest-safe label")
    if redact_sensitive_text(value) != value or any(_is_control_or_format(char) for char in value):
        raise ValueError(f"{field} must be a manifest-safe label")
    if _CLIENT_ID_RE.fullmatch(value) is None:
        raise ValueError(f"{field} must be a manifest-safe label")
    return value


def endpoint_summary(url: str) -> dict:
    parsed = urlparse(url)
    summary = {
        "scheme": parsed.scheme,
        "host": parsed.hostname or "",
        "path": parsed.path or "",
        "sha256": hashlib.sha256(url.encode("utf-8")).hexdigest(),
    }
    port = parsed.port
    if port is not None:
        summary["port"] = port
    return summary


def client_context_summary(context: Mapping[str, object] | None) -> dict:
    context = dict(context or {})
    summary: dict[str, object] = {}
    if "base_url" in context:
        summary["base_url"] = endpoint_summary(str(context["base_url"]))
    if "host" in context:
        summary["host"] = endpoint_summary(str(context["host"]))
    if "api_version" in context:
        summary["api_version"] = context["api_version"]
    for key in ("organization", "project"):
        if key in context:
            summary[key] = context[key]
    return summary


def copy_client_context(context: Mapping[str, object] | None) -> dict:
    return deepcopy(dict(context or {}))


def _safe_url_path(path: str) -> bool:
    if any(_is_control_or_format(char) for char in path):
        return False
    if any(char.isspace() for char in path):
        return False
    return redact_sensitive_text(path) == path


def _is_control_or_format(character: str) -> bool:
    return unicodedata.category(character).startswith("C")
