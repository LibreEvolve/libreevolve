from __future__ import annotations

import json
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
    diagnostic = {
        "error": exc.__class__.__name__,
        "message": str(exc),
        "record_type": type(record).__name__,
        "record_repr": repr(record),
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(strict_json_dumps(diagnostic) + "\n")
