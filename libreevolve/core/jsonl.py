from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


class StrictJsonlError(ValueError):
    """Raised when a run record cannot be written as strict finite JSON."""


def strict_json_dumps(record: Any, **kwargs: Any) -> str:
    return json.dumps(record, allow_nan=False, **kwargs)


def strict_json_dump(record: Any, path: Path, **kwargs: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, allow_nan=False, **kwargs)


def append_strict_jsonl(
    path: Path, record: dict, quarantine_path: Path | None = None
) -> None:
    try:
        line = strict_json_dumps(record)
    except (TypeError, ValueError) as exc:
        if quarantine_path is not None:
            append_quarantine_record(quarantine_path, record, exc)
        raise StrictJsonlError(
            f"Could not serialize strict JSONL record for {path}: {exc}"
        ) from exc
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def append_quarantine_record(path: Path, record: dict, exc: Exception) -> None:
    details = _non_finite_details(record)
    message = str(exc)
    if details:
        message = f"{message}; non-finite values: {', '.join(details)}"
    diagnostic = {
        "error": exc.__class__.__name__,
        "message": message,
        "record_type": type(record).__name__,
        "record_repr": repr(record),
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(strict_json_dumps(diagnostic) + "\n")


def _non_finite_details(value: Any, path: str = "$") -> list[str]:
    if isinstance(value, float) and not math.isfinite(value):
        return [f"{path}={value!r}"]
    if isinstance(value, dict):
        details: list[str] = []
        for key, item in value.items():
            details.extend(_non_finite_details(item, f"{path}.{key}"))
        return details
    if isinstance(value, (list, tuple)):
        details = []
        for index, item in enumerate(value):
            details.extend(_non_finite_details(item, f"{path}[{index}]"))
        return details
    return []
