"""Raw, newline-terminated JSONL storage primitives.

This module deliberately has no knowledge of JSONL schemas, quarantine
records, redaction, locking, ordering, or repair policy.  The compatibility
façade in :mod:`libreevolve.core.jsonl` owns those decisions and supplies the
I/O callables so its existing fault-injection and import anchors remain
observable.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any


def append_serialized_jsonl_line(
    path: Path,
    line: str,
    *,
    open_fn: Callable[..., Any] | None = None,
    fsync_fn: Callable[[int], Any] | None = None,
) -> None:
    """Append one already-serialized line and durably flush its file.

    Serialization, validation, locking, parent-directory preparation, and
    newline ordering remain caller responsibilities.  The default callables
    are resolved at call time so this primitive is also straightforward to
    exercise with an alternate platform or fault-injected file object.
    """
    if open_fn is None:
        open_fn = open
    if fsync_fn is None:
        fsync_fn = os.fsync
    with open_fn(path, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")
        handle.flush()
        fsync_fn(handle.fileno())
