from __future__ import annotations

from copy import deepcopy
import hashlib
import re
from typing import Iterable

from libreevolve.core.redaction import redact_sensitive_text


PROMPT_ROLE_FIELDS = {"system", "developer"}
MAX_PROMPT_ROLE_TEXT_CHARS = 4000
_ROLE_RE = re.compile(r"(?!.*::)(?!.*:$)[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")


def validate_prompt_role_policy(value: object, *, field: str = "llm_prompt_roles") -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a mapping")
    normalized: dict[str, dict[str, str]] = {}
    for role, spec in value.items():
        role = validate_prompt_role_label(role, field=f"{field} role")
        if not isinstance(spec, dict):
            raise ValueError(f"{field}.{role} must be a mapping")
        unsupported = sorted(set(spec) - PROMPT_ROLE_FIELDS)
        if unsupported:
            raise ValueError(f"{field}.{role} has unsupported fields {unsupported}")
        item: dict[str, str] = {}
        for name in ("system", "developer"):
            if name not in spec:
                continue
            item[name] = validate_prompt_role_text(
                spec[name],
                field=f"{field}.{role}.{name}",
            )
        if not item:
            raise ValueError(f"{field}.{role} must define system and/or developer text")
        normalized[role] = item
    return normalized


def validate_prompt_role_label(value: object, *, field: str = "role") -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    if redact_sensitive_text(value) != value:
        raise ValueError(f"{field} must be a manifest-safe role label")
    if _ROLE_RE.fullmatch(value) is None:
        raise ValueError(f"{field} must be a manifest-safe role label")
    return value


def validate_prompt_role_text(value: object, *, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    if not value.strip():
        raise ValueError(f"{field} must be non-empty text")
    if len(value) > MAX_PROMPT_ROLE_TEXT_CHARS:
        raise ValueError(
            f"{field} must be at most {MAX_PROMPT_ROLE_TEXT_CHARS} characters"
        )
    return value


def prompt_role_spec_for_role(policy: dict | None, role: str | None) -> dict:
    if not isinstance(role, str):
        return {}
    validated_policy = validate_prompt_role_policy(policy or {})
    return deepcopy(validated_policy.get(role, {}))


def prompt_role_policy_record(policy: dict | None, role: str | None) -> dict:
    role = validate_prompt_role_label(role or "mutation", field="role")
    spec = prompt_role_spec_for_role(policy, role)
    if not spec:
        return {
            "policy": "single_user_message",
            "matched_role": None,
            "message_roles": ["user"],
            "instruction_fields": [],
            "instruction_metadata": {},
        }
    fields = [name for name in ("system", "developer") if name in spec]
    return {
        "policy": "configured_structured_messages",
        "matched_role": role,
        "message_roles": [*fields, "user"],
        "instruction_fields": fields,
        "instruction_metadata": {
            name: _text_metadata(spec[name])
            for name in fields
        },
    }


def _text_metadata(text: str) -> dict:
    return {
        "chars": len(text),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "redacted": redact_sensitive_text(text) != text,
    }
