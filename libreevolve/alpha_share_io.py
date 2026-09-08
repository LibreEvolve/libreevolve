"""Explicit local file boundary for frozen result rendering; never uploads.

Rejects existing destinations and symlink/reparse-point paths. Callers must own
the parent directory: this is not containment against a malicious concurrent
filesystem actor. Partial outputs are retained on failure for inspection.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import stat

from libreevolve.alpha_share_record import MAX_RECORD_BYTES, admit_record
from libreevolve.alpha_share_render import render_public


PUBLIC_FILENAMES = frozenset({"index.html", "card.svg", "result.txt", "result.json"})


def checked_path(value: str | Path, *, must_exist: bool) -> Path:
    raw = Path(value)
    if ".." in raw.parts:
        raise ValueError("Parent traversal is not accepted")
    path = raw.absolute()
    chain = [*reversed(path.parents), path]
    for index, component in enumerate(chain):
        try:
            observed = component.lstat()
        except FileNotFoundError:
            if index != len(chain) - 1 or must_exist:
                raise ValueError("Input and destination parent must already exist") from None
            continue
        if stat.S_ISLNK(observed.st_mode) or getattr(observed, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
            raise ValueError("Symlink and reparse-point paths are not accepted")
        if index != len(chain) - 1 and not stat.S_ISDIR(observed.st_mode):
            raise ValueError("Parent must be a directory")
    return path


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _constant(value):
    raise ValueError("Non-finite JSON constant")


def load_record(path: str | Path) -> dict:
    source = checked_path(path, must_exist=True)
    if not stat.S_ISREG(source.lstat().st_mode):
        raise ValueError("Record input must be a regular file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(source, flags)
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("Record input must remain a regular file")
        raw = stream.read(MAX_RECORD_BYTES + 1)
    if len(raw) > MAX_RECORD_BYTES:
        raise ValueError("Record exceeds input size limit")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_constant)
        return admit_record(value)
    except (UnicodeError, RecursionError) as exc:
        raise ValueError("Record encoding or nesting is invalid") from exc


def export_public(record_path: str | Path, destination: str | Path, *,
                  approved_sha256: str, approved_by: str,
                  approve_source_link: bool = False) -> dict:
    """Write only four public files; return the private receipt to the caller.

    Review/approval and rendering finish before any destination is created.
    An error after creation leaves a partial directory, never a success receipt.
    Existing paths are never overwritten or removed, even when empty.
    """
    target = checked_path(destination, must_exist=False)
    if target.exists():
        raise ValueError("Destination already exists; choose a new directory")
    files, receipt = render_public(load_record(record_path), approved_sha256=approved_sha256,
                                  approved_by=approved_by, approve_source_link=approve_source_link)
    if set(files) != PUBLIC_FILENAMES:
        raise ValueError("Unexpected public output files")
    target.mkdir(mode=0o700, parents=False, exist_ok=False)
    for name in sorted(PUBLIC_FILENAMES):
        checked_path(target, must_exist=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(target / name, flags, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(files[name])
    return receipt
