from __future__ import annotations

import re

from libreevolve.core.redaction import redact_sensitive_text

_PROGRAM_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")


def validate_sample_count(k: object, label: str = "sample count") -> int:
    if isinstance(k, bool) or not isinstance(k, int) or k < 0:
        raise ValueError(f"{label} must be a non-negative integer")
    return k


def validate_exclude_ids(
    exclude_ids: object, label: str = "exclude_ids"
) -> frozenset[str]:
    if exclude_ids is None:
        return frozenset()
    if not isinstance(exclude_ids, (set, frozenset, list, tuple)):
        raise ValueError(f"{label} must be a collection of manifest-safe program ids")
    normalized: set[str] = set()
    for index, program_id in enumerate(exclude_ids):
        if not isinstance(program_id, str):
            raise ValueError(f"{label}[{index}] must be a manifest-safe program id")
        if redact_sensitive_text(program_id) != program_id:
            raise ValueError(f"{label}[{index}] must be a manifest-safe program id")
        if _PROGRAM_ID_RE.fullmatch(program_id) is None:
            raise ValueError(f"{label}[{index}] must be a manifest-safe program id")
        normalized.add(program_id)
    return frozenset(normalized)
