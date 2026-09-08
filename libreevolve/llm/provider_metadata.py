from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from collections.abc import Mapping
from copy import deepcopy

from libreevolve.core.redaction import redact_sensitive_text

PROVIDER_RESPONSE_METADATA_FIELDS = {
    "usage",
    "finish_reason",
    "request_id",
    "response_id",
    "adapter_retry",
    "provider_diagnostics",
}
PROVIDER_USAGE_FIELDS = {"input_tokens", "output_tokens", "total_tokens"}
PROVIDER_ADAPTER_RETRY_FIELDS = {
    "policy",
    "max_retries",
    "attempts",
    "failed_attempts",
    "failures",
}
PROVIDER_ADAPTER_RETRY_FAILURE_FIELDS = {"attempt", "error_type"}
PROVIDER_ADAPTER_RETRY_POLICY = "bounded_provider_internal_retries"
PROVIDER_DIAGNOSTICS_POLICY = "bounded_provider_diagnostics_v1"
PROVIDER_DIAGNOSTICS_FIELDS = {
    "policy",
    "max_items",
    "max_string_chars",
    "items",
    "omitted_items",
}
PROVIDER_DIAGNOSTIC_ITEM_FIELDS = {
    "key",
    "value",
    "value_type",
    "sha256",
    "chars",
    "stored_chars",
    "redacted",
    "truncated",
}
MAX_PROVIDER_DIAGNOSTIC_ITEMS = 8
MAX_PROVIDER_DIAGNOSTIC_STRING_CHARS = 200
_PROVIDER_LABEL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,191}")


def provider_response_metadata_defaults() -> dict:
    return {
        "usage": None,
        "finish_reason": None,
        "request_id": None,
        "response_id": None,
        "adapter_retry": None,
        "provider_diagnostics": None,
    }


def validate_provider_response_metadata(
    value: object,
    path: str = "provider_response_metadata",
    *,
    allow_raw_provider_diagnostics: bool = True,
) -> dict:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be a mapping")
    unsupported = sorted(set(value) - PROVIDER_RESPONSE_METADATA_FIELDS)
    if unsupported:
        raise ValueError(f"{path} has unsupported fields: {unsupported}")
    normalized: dict[str, object] = {}
    if "usage" in value:
        normalized["usage"] = _validate_usage(value["usage"], f"{path}.usage")
    if "adapter_retry" in value:
        normalized["adapter_retry"] = _validate_adapter_retry(
            value["adapter_retry"],
            f"{path}.adapter_retry",
        )
    if "provider_diagnostics" in value and value["provider_diagnostics"] is not None:
        normalized["provider_diagnostics"] = _provider_diagnostics_record(
            value["provider_diagnostics"],
            f"{path}.provider_diagnostics",
            allow_raw=allow_raw_provider_diagnostics,
        )
    for key in ("finish_reason", "request_id", "response_id"):
        if key in value:
            normalized[key] = _validate_provider_label(value[key], f"{path}.{key}")
    return normalized


def copy_provider_response_metadata(value: Mapping[str, object] | None) -> dict:
    return deepcopy(dict(value or {}))


def provider_response_metadata_record(value: object) -> dict:
    record = provider_response_metadata_defaults()
    record.update(validate_provider_response_metadata(value))
    return record


def safe_provider_response_metadata(value: object) -> dict:
    try:
        return validate_provider_response_metadata(value)
    except ValueError:
        return {}


def _validate_usage(value: object, path: str) -> dict:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be a mapping or null")
    unsupported = sorted(set(value) - PROVIDER_USAGE_FIELDS)
    if unsupported:
        raise ValueError(f"{path} has unsupported fields: {unsupported}")
    normalized: dict[str, int] = {}
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        if key not in value:
            continue
        token_count = value[key]
        if isinstance(token_count, bool) or not isinstance(token_count, int) or token_count < 0:
            raise ValueError(f"{path}.{key} must be a non-negative integer")
        normalized[key] = token_count
    return normalized


def _validate_provider_label(value: object, path: str) -> str | None:
    if value is None:
        return None
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or redact_sensitive_text(value) != value
        or any(_is_control_or_format(char) for char in value)
        or _PROVIDER_LABEL_RE.fullmatch(value) is None
    ):
        raise ValueError(f"{path} must be a manifest-safe provider label or null")
    return value


def _validate_adapter_retry(value: object, path: str) -> dict | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be a mapping or null")
    unsupported = sorted(set(value) - PROVIDER_ADAPTER_RETRY_FIELDS)
    if unsupported:
        raise ValueError(f"{path} has unsupported fields: {unsupported}")
    policy = value.get("policy")
    if policy != PROVIDER_ADAPTER_RETRY_POLICY:
        raise ValueError(f"{path}.policy must be {PROVIDER_ADAPTER_RETRY_POLICY!r}")
    max_retries = _validate_non_negative_int(
        value.get("max_retries"),
        f"{path}.max_retries",
    )
    attempts = _validate_positive_int(value.get("attempts"), f"{path}.attempts")
    if attempts > max_retries + 1:
        raise ValueError(f"{path}.attempts must be <= max_retries + 1")
    failed_attempts = _validate_non_negative_int(
        value.get("failed_attempts"),
        f"{path}.failed_attempts",
    )
    if failed_attempts > attempts:
        raise ValueError(f"{path}.failed_attempts must be <= attempts")
    failures_value = value.get("failures", [])
    if not isinstance(failures_value, list):
        raise ValueError(f"{path}.failures must be a list")
    if failed_attempts != len(failures_value):
        raise ValueError(f"{path}.failed_attempts must match failures length")
    failures = []
    for index, failure in enumerate(failures_value):
        failures.append(_validate_adapter_retry_failure(failure, f"{path}.failures[{index}]"))
    return {
        "policy": policy,
        "max_retries": max_retries,
        "attempts": attempts,
        "failed_attempts": failed_attempts,
        "failures": failures,
    }


def _validate_adapter_retry_failure(value: object, path: str) -> dict:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be a mapping")
    unsupported = sorted(set(value) - PROVIDER_ADAPTER_RETRY_FAILURE_FIELDS)
    if unsupported:
        raise ValueError(f"{path} has unsupported fields: {unsupported}")
    return {
        "attempt": _validate_non_negative_int(value.get("attempt"), f"{path}.attempt"),
        "error_type": _validate_provider_label(value.get("error_type"), f"{path}.error_type"),
    }


def _provider_diagnostics_record(
    value: object,
    path: str,
    *,
    allow_raw: bool,
) -> dict | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be a mapping or null")
    if value.get("policy") == PROVIDER_DIAGNOSTICS_POLICY:
        return _validate_provider_diagnostics_record(value, path)
    if not allow_raw:
        raise ValueError(f"{path}.policy must be {PROVIDER_DIAGNOSTICS_POLICY!r}")
    return _build_provider_diagnostics_record(value, path)


def _build_provider_diagnostics_record(value: Mapping[object, object], path: str) -> dict:
    items = []
    pairs = sorted(value.items(), key=lambda pair: str(pair[0]))
    for index, (key, item) in enumerate(pairs[:MAX_PROVIDER_DIAGNOSTIC_ITEMS]):
        label = _validate_provider_label(key, f"{path}.{index}.key")
        assert label is not None
        items.append(_provider_diagnostic_item(label, item, f"{path}.{label}"))
    return {
        "policy": PROVIDER_DIAGNOSTICS_POLICY,
        "max_items": MAX_PROVIDER_DIAGNOSTIC_ITEMS,
        "max_string_chars": MAX_PROVIDER_DIAGNOSTIC_STRING_CHARS,
        "items": items,
        "omitted_items": max(0, len(pairs) - MAX_PROVIDER_DIAGNOSTIC_ITEMS),
    }


def _provider_diagnostic_item(key: str, value: object, path: str) -> dict:
    if value is None:
        return {"key": key, "value": None, "value_type": "null"}
    if isinstance(value, bool):
        return {"key": key, "value": value, "value_type": "bool"}
    if isinstance(value, int) and not isinstance(value, bool):
        return {"key": key, "value": value, "value_type": "int"}
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path} must be finite")
        return {"key": key, "value": value, "value_type": "float"}
    if isinstance(value, str):
        redacted = redact_sensitive_text(value)
        clean = "".join(" " if _is_control_or_format(char) else char for char in redacted)
        truncated = len(clean) > MAX_PROVIDER_DIAGNOSTIC_STRING_CHARS
        retained = clean[:MAX_PROVIDER_DIAGNOSTIC_STRING_CHARS]
        return {
            "key": key,
            "value": retained,
            "value_type": "str",
            "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
            "chars": len(value),
            "stored_chars": len(retained),
            "redacted": clean != value,
            "truncated": truncated,
        }
    raise ValueError(f"{path} must be a scalar JSON-safe provider diagnostic")


def _validate_provider_diagnostics_record(value: Mapping[object, object], path: str) -> dict:
    unsupported = sorted(set(value) - PROVIDER_DIAGNOSTICS_FIELDS)
    if unsupported:
        raise ValueError(f"{path} has unsupported fields: {unsupported}")
    if value.get("policy") != PROVIDER_DIAGNOSTICS_POLICY:
        raise ValueError(f"{path}.policy must be {PROVIDER_DIAGNOSTICS_POLICY!r}")
    max_items = _validate_positive_int(value.get("max_items"), f"{path}.max_items")
    if max_items != MAX_PROVIDER_DIAGNOSTIC_ITEMS:
        raise ValueError(f"{path}.max_items is unsupported")
    max_string_chars = _validate_positive_int(
        value.get("max_string_chars"),
        f"{path}.max_string_chars",
    )
    if max_string_chars != MAX_PROVIDER_DIAGNOSTIC_STRING_CHARS:
        raise ValueError(f"{path}.max_string_chars is unsupported")
    omitted_items = _validate_non_negative_int(
        value.get("omitted_items"),
        f"{path}.omitted_items",
    )
    raw_items = value.get("items")
    if not isinstance(raw_items, list):
        raise ValueError(f"{path}.items must be a list")
    if len(raw_items) > max_items:
        raise ValueError(f"{path}.items exceeds max_items")
    items = [
        _validate_provider_diagnostic_record_item(item, f"{path}.items[{index}]")
        for index, item in enumerate(raw_items)
    ]
    return {
        "policy": PROVIDER_DIAGNOSTICS_POLICY,
        "max_items": max_items,
        "max_string_chars": max_string_chars,
        "items": items,
        "omitted_items": omitted_items,
    }


def _validate_provider_diagnostic_record_item(value: object, path: str) -> dict:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be a mapping")
    unsupported = sorted(set(value) - PROVIDER_DIAGNOSTIC_ITEM_FIELDS)
    if unsupported:
        raise ValueError(f"{path} has unsupported fields: {unsupported}")
    key = _validate_provider_label(value.get("key"), f"{path}.key")
    assert key is not None
    value_type = value.get("value_type")
    if value_type not in {"null", "bool", "int", "float", "str"}:
        raise ValueError(f"{path}.value_type is unsupported")
    raw_value = value.get("value")
    if value_type == "null":
        if raw_value is not None:
            raise ValueError(f"{path}.value must be null")
        return {"key": key, "value": None, "value_type": "null"}
    if value_type == "bool":
        if not isinstance(raw_value, bool):
            raise ValueError(f"{path}.value must be boolean")
        return {"key": key, "value": raw_value, "value_type": "bool"}
    if value_type == "int":
        if isinstance(raw_value, bool) or not isinstance(raw_value, int):
            raise ValueError(f"{path}.value must be integer")
        return {"key": key, "value": raw_value, "value_type": "int"}
    if value_type == "float":
        if (
            isinstance(raw_value, bool)
            or not isinstance(raw_value, (int, float))
            or not math.isfinite(float(raw_value))
        ):
            raise ValueError(f"{path}.value must be finite")
        return {"key": key, "value": float(raw_value), "value_type": "float"}
    return _validate_provider_diagnostic_string_item(value, path, key)


def _validate_provider_diagnostic_string_item(
    value: Mapping[object, object],
    path: str,
    key: str,
) -> dict:
    retained = value.get("value")
    if not isinstance(retained, str):
        raise ValueError(f"{path}.value must be a string")
    if any(_is_control_or_format(char) for char in retained):
        raise ValueError(f"{path}.value must not contain control or format characters")
    if len(retained) > MAX_PROVIDER_DIAGNOSTIC_STRING_CHARS:
        raise ValueError(f"{path}.value exceeds max_string_chars")
    sha256 = value.get("sha256")
    if not isinstance(sha256, str) or re.fullmatch(r"[0-9a-f]{64}", sha256) is None:
        raise ValueError(f"{path}.sha256 must be a SHA-256 hex digest")
    chars = _validate_non_negative_int(value.get("chars"), f"{path}.chars")
    stored_chars = _validate_non_negative_int(
        value.get("stored_chars"),
        f"{path}.stored_chars",
    )
    if stored_chars != len(retained):
        raise ValueError(f"{path}.stored_chars is inconsistent")
    if stored_chars > chars:
        raise ValueError(f"{path}.stored_chars must be <= chars")
    redacted = value.get("redacted")
    if not isinstance(redacted, bool):
        raise ValueError(f"{path}.redacted must be boolean")
    truncated = value.get("truncated")
    if not isinstance(truncated, bool):
        raise ValueError(f"{path}.truncated must be boolean")
    if redact_sensitive_text(retained) != retained:
        raise ValueError(f"{path}.value must not contain secret-like text")
    return {
        "key": key,
        "value": retained,
        "value_type": "str",
        "sha256": sha256,
        "chars": chars,
        "stored_chars": stored_chars,
        "redacted": redacted,
        "truncated": truncated,
    }


def _validate_non_negative_int(value: object, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{path} must be a non-negative integer")
    return value


def _validate_positive_int(value: object, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{path} must be a positive integer")
    return value


def _is_control_or_format(character: str) -> bool:
    return unicodedata.category(character).startswith("C")
