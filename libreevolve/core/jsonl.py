from __future__ import annotations

import contextlib
import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from libreevolve.core import jsonl_storage as _jsonl_storage
from libreevolve.core.redaction import redact_sensitive_text


class StrictJsonlError(ValueError):
    """Raised when a run record cannot be written as strict finite JSON."""


class DuplicateJsonObjectNameError(ValueError):
    """Raised when JSON input contains duplicate names in one object."""


_MAX_JSON_ERROR_MESSAGE_CHARS = 1000
_MAX_RECORD_REPR_CHARS = 4000
_QUARANTINE_RETENTION_MODES = frozenset({"full", "redacted", "hash_only", "off"})
_REDACTED_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(?:api[_-]?key|token|secret|password)\s*[:=]\s*\[REDACTED\]"
)


def strict_json_dumps(record: Any, **kwargs: Any) -> str:
    _validate_strict_json_value(record)
    return json.dumps(record, allow_nan=False, **kwargs)


def strict_json_text_for_path(record: Any, path: Path, **kwargs: Any) -> str:
    try:
        return strict_json_dumps(record, **kwargs)
    except (TypeError, ValueError) as exc:
        raise StrictJsonlError(
            f"Could not serialize strict JSON for {path}: {_json_error_message(record, exc)}"
        ) from exc


def strict_json_dump(record: Any, path: Path, **kwargs: Any) -> None:
    path = Path(path)
    text = strict_json_text_for_path(record, path, **kwargs)
    _ensure_parent_directory(path, "strict JSON file")
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as f:
            tmp_path = Path(f.name)
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
        _fsync_parent_directory(path.parent)
    finally:
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink()


def reject_duplicate_json_object_names(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonObjectNameError(
                f"duplicate JSON object name {key!r}"
            )
        result[key] = value
    return result


def strict_json_loads_object(text: str, *, source: str = "JSON") -> dict[str, Any]:
    try:
        record = json.loads(
            text,
            object_pairs_hook=reject_duplicate_json_object_names,
        )
    except DuplicateJsonObjectNameError as exc:
        raise StrictJsonlError(f"Malformed {source}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise StrictJsonlError(f"Malformed {source}: {exc.msg}") from exc
    if not isinstance(record, dict):
        raise StrictJsonlError(f"Malformed {source}: expected JSON object")
    return record


def load_strict_json_object(path: Path, *, source: str | None = None) -> dict[str, Any]:
    path = Path(path)
    label = source or path.name
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        message = _bounded_redacted_text(str(exc), _MAX_JSON_ERROR_MESSAGE_CHARS)
        raise StrictJsonlError(
            f"Failed to read {label}: {exc.__class__.__name__}: {message}"
        ) from exc
    return strict_json_loads_object(text, source=label)


def iter_strict_jsonl_objects(
    path: Path,
    *,
    stream_name: str | None = None,
    repair_torn_final_record: bool = False,
    quarantine_path: Path | None = None,
    quarantine_snapshot_retention_mode: str = "redacted",
):
    path = Path(path)
    label = stream_name or path.name
    if repair_torn_final_record:
        repair_trailing_partial_jsonl(
            path,
            quarantine_path=quarantine_path,
            quarantine_snapshot_retention_mode=(
                quarantine_snapshot_retention_mode
            ),
        )
    try:
        handle = path.open("rb")
    except OSError as exc:
        message = _bounded_redacted_text(str(exc), _MAX_JSON_ERROR_MESSAGE_CHARS)
        raise StrictJsonlError(
            f"Failed to read {label}: {exc.__class__.__name__}: {message}"
        ) from exc
    with handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if raw_line and not raw_line.endswith(b"\n"):
                raise StrictJsonlError(
                    f"Malformed {label} at line {line_number}: "
                    "unterminated final JSONL record"
                )
            try:
                line = raw_line.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise StrictJsonlError(
                    f"Malformed {label} at line {line_number}: invalid UTF-8 ({exc.reason})"
                ) from exc
            if not line.strip():
                continue
            yield strict_json_loads_object(
                line,
                source=f"{label} at line {line_number}",
            )


def iter_quarantine_records(
    path: Path,
    *,
    stream_name: str | None = None,
):
    label = stream_name or Path(path).name
    for line_number, record in enumerate(
        iter_strict_jsonl_objects(path, stream_name=label),
        start=1,
    ):
        yield validate_quarantine_record(
            record,
            source=f"{label} at line {line_number}",
        )


def validate_quarantine_record(
    record: dict[str, Any],
    *,
    source: str = "quarantine record",
) -> dict[str, Any]:
    """Validate a strict JSONL quarantine diagnostic row.

    Quarantine streams intentionally carry diagnostics, not accepted runtime
    state. This validator keeps the supported row shapes explicit so audit code
    can distinguish rejected-record serialization diagnostics from torn-line
    repair diagnostics.
    """
    if not isinstance(record, dict):
        raise StrictJsonlError(f"Malformed {source}: expected JSON object")
    event = record.get("event")
    if event is None:
        _validate_rejected_record_quarantine_diagnostic(record, source=source)
    elif event == "jsonl_torn_final_record_repaired":
        _validate_torn_final_record_quarantine_diagnostic(record, source=source)
    else:
        raise StrictJsonlError(
            f"Malformed {source}: unsupported quarantine event {event!r}"
        )
    return record


def append_strict_jsonl(
    path: Path,
    record: dict,
    quarantine_path: Path | None = None,
    *,
    quarantine_snapshot_retention_mode: str = "redacted",
) -> None:
    path = Path(path)
    retention_mode = _validate_quarantine_retention_mode(
        quarantine_snapshot_retention_mode
    )
    try:
        line = strict_json_dumps(record)
    except (TypeError, ValueError) as exc:
        if quarantine_path is not None:
            append_quarantine_record(
                quarantine_path,
                record,
                exc,
                retention_mode=retention_mode,
            )
        raise StrictJsonlError(
            f"Could not serialize strict JSONL record for {path}: "
            f"{_json_error_message(record, exc)}"
        ) from exc
    _ensure_parent_directory(path, "strict JSONL file")
    with _locked_jsonl_paths(path, quarantine_path):
        repair_trailing_partial_jsonl(
            path,
            quarantine_path=quarantine_path,
            quarantine_snapshot_retention_mode=retention_mode,
            _lock_held=True,
        )
        _append_serialized_jsonl_line(path, line)


def append_quarantine_record(
    path: Path,
    record: dict,
    exc: Exception,
    *,
    retention_mode: str = "redacted",
) -> None:
    path = Path(path)
    retention_mode = _validate_quarantine_retention_mode(retention_mode)
    snapshot = _safe_record_repr(record, mode=retention_mode)
    diagnostic = {
        "error": exc.__class__.__name__,
        "message": _json_error_message(record, exc),
        "record_type": type(record).__name__,
        "record_repr_retention": snapshot["retention"],
    }
    if snapshot["text"] is not None:
        diagnostic["record_repr"] = snapshot["text"]
        diagnostic["record_repr_truncated"] = snapshot["truncated"]
    if snapshot["error"] is not None:
        diagnostic["record_repr_error"] = snapshot["error"]
    _ensure_parent_directory(path, "strict JSONL quarantine file")
    with _locked_jsonl_paths(path):
        repair_trailing_partial_jsonl(
            path,
            quarantine_snapshot_retention_mode=retention_mode,
            _lock_held=True,
        )
        _append_serialized_jsonl_line(path, strict_json_dumps(diagnostic))


def repair_trailing_partial_jsonl(
    path: Path,
    *,
    quarantine_path: Path | None = None,
    quarantine_snapshot_retention_mode: str = "redacted",
    _lock_held: bool = False,
) -> dict[str, Any]:
    """Truncate an unterminated final JSONL fragment and log a diagnostic.

    Managed JSONL appends always write a newline-terminated record. A non-empty
    final fragment without a newline is therefore treated as a torn append from
    a prior interrupted write, not as a valid complete record.
    """
    path = Path(path)
    if not _lock_held:
        with _locked_jsonl_paths(path, quarantine_path):
            return repair_trailing_partial_jsonl(
                path,
                quarantine_path=quarantine_path,
                quarantine_snapshot_retention_mode=(
                    quarantine_snapshot_retention_mode
                ),
                _lock_held=True,
            )
    if not path.exists():
        return {"status": "missing"}
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise StrictJsonlError(
            f"Could not inspect strict JSONL file at {_safe_path_text(path)}: "
            f"{exc.__class__.__name__}: {_bounded_redacted_text(str(exc), _MAX_JSON_ERROR_MESSAGE_CHARS)}"
        ) from exc
    if not payload or payload.endswith(b"\n"):
        return {"status": "unchanged"}
    retention_mode = _validate_quarantine_retention_mode(
        quarantine_snapshot_retention_mode
    )
    last_newline = payload.rfind(b"\n")
    keep_bytes = 0 if last_newline < 0 else last_newline + 1
    fragment = payload[keep_bytes:]
    with path.open("r+b") as handle:
        handle.truncate(keep_bytes)
        handle.flush()
        os.fsync(handle.fileno())
    diagnostic = _partial_jsonl_diagnostic(
        path,
        fragment,
        keep_bytes,
        retention_mode=retention_mode,
    )
    target = Path(quarantine_path) if quarantine_path is not None else path
    _ensure_parent_directory(target, "strict JSONL quarantine file")
    _append_serialized_jsonl_line(target, strict_json_dumps(diagnostic))
    return {
        "status": "repaired",
        "preserved_bytes": keep_bytes,
        "fragment_bytes": len(fragment),
        "quarantine_path": str(target),
    }


def _validate_rejected_record_quarantine_diagnostic(
    record: dict[str, Any],
    *,
    source: str,
) -> None:
    _require_string_field(record, "error", source)
    _require_string_field(record, "message", source)
    _require_string_field(record, "record_type", source)
    retention = _require_mapping_field(record, "record_repr_retention", source)
    retention_mode = _validate_quarantine_retention_metadata(
        retention,
        source=f"{source}.record_repr_retention",
    )
    text_allowed = retention_mode in {"full", "redacted"}
    if text_allowed:
        if "record_repr" not in record:
            raise StrictJsonlError(f"Malformed {source}: missing record_repr")
        _require_string_field(record, "record_repr", source)
        truncated = _require_bool_field(record, "record_repr_truncated", source)
        if truncated != retention.get("truncated"):
            raise StrictJsonlError(
                f"Malformed {source}: record_repr_truncated must match "
                "record_repr_retention.truncated"
            )
    else:
        for field in ("record_repr", "record_repr_truncated"):
            if field in record:
                raise StrictJsonlError(
                    f"Malformed {source}: {field} is not allowed when "
                    f"retention_mode is {retention_mode!r}"
                )
    if "record_repr_error" in record:
        _require_string_field(record, "record_repr_error", source)


def _validate_torn_final_record_quarantine_diagnostic(
    record: dict[str, Any],
    *,
    source: str,
) -> None:
    _require_string_value(
        record.get("event"),
        field="event",
        source=source,
        expected="jsonl_torn_final_record_repaired",
    )
    _require_string_field(record, "stream", source)
    _require_hash_field(record, "path_sha256", source)
    _require_string_value(
        record.get("repair_policy"),
        field="repair_policy",
        source=source,
        expected="truncate_unterminated_final_line",
    )
    _require_non_negative_int_field(record, "complete_bytes_preserved", source)
    fragment_bytes = _require_non_negative_int_field(
        record,
        "fragment_bytes",
        source,
    )
    if fragment_bytes == 0:
        raise StrictJsonlError(f"Malformed {source}: fragment_bytes must be positive")
    _require_bool_field(record, "fragment_utf8_valid", source)
    retention = _require_mapping_field(record, "fragment_retention", source)
    retention_mode = _validate_quarantine_retention_metadata(
        retention,
        source=f"{source}.fragment_retention",
    )
    if retention_mode in {"full", "redacted"}:
        _require_hash_field(record, "fragment_sha256", source)
        _require_string_field(record, "fragment_preview", source)
    elif retention_mode == "hash_only":
        _require_hash_field(record, "fragment_sha256", source)
        if "fragment_preview" in record:
            raise StrictJsonlError(
                f"Malformed {source}: fragment_preview is not allowed when "
                "retention_mode is 'hash_only'"
            )
    else:
        for field in ("fragment_sha256", "fragment_preview"):
            if field in record:
                raise StrictJsonlError(
                    f"Malformed {source}: {field} is not allowed when "
                    "retention_mode is 'off'"
                )


def _validate_quarantine_retention_metadata(
    retention: dict[str, Any],
    *,
    source: str,
) -> str:
    mode = retention.get("retention_mode")
    if not isinstance(mode, str) or mode not in _QUARANTINE_RETENTION_MODES:
        raise StrictJsonlError(
            f"Malformed {source}: retention_mode must be one of "
            f"{', '.join(sorted(_QUARANTINE_RETENTION_MODES))}"
        )
    expected_policy = {
        "full": "full_secret_redacted_text_with_raw_sha256",
        "redacted": "redact_then_prefix_truncate_with_sha256",
        "hash_only": "hash_only_with_raw_sha256",
        "off": "off_no_text_or_hash",
    }[mode]
    _require_string_value(
        retention.get("retention_policy"),
        field="retention_policy",
        source=source,
        expected=expected_policy,
    )
    if mode == "off":
        _require_none_field(retention, "sha256", source)
        _require_none_field(retention, "chars", source)
        _require_integer_value(
            retention.get("stored_chars"),
            "stored_chars",
            source,
            exact=0,
        )
        _require_none_field(retention, "redacted", source)
        _require_bool_value(
            retention.get("truncated"),
            "truncated",
            source,
            expected=False,
        )
    else:
        _require_hash_field(retention, "sha256", source)
        _require_non_negative_int_field(retention, "chars", source)
        stored_chars = _require_non_negative_int_field(
            retention,
            "stored_chars",
            source,
        )
        if mode == "hash_only" and stored_chars != 0:
            raise StrictJsonlError(
                f"Malformed {source}: stored_chars must be 0 for hash_only"
            )
        if mode in {"full", "redacted"}:
            _require_bool_field(retention, "redacted", source)
        else:
            _require_none_field(retention, "redacted", source)
        _require_bool_field(retention, "truncated", source)
    max_chars = _require_non_negative_int_field(retention, "max_chars", source)
    if max_chars == 0:
        raise StrictJsonlError(f"Malformed {source}: max_chars must be positive")
    return mode


def _require_mapping_field(
    record: dict[str, Any],
    field: str,
    source: str,
) -> dict[str, Any]:
    value = record.get(field)
    if not isinstance(value, dict):
        raise StrictJsonlError(f"Malformed {source}: {field} must be an object")
    return value


def _require_string_field(record: dict[str, Any], field: str, source: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value:
        raise StrictJsonlError(
            f"Malformed {source}: {field} must be a non-empty string"
        )
    return value


def _require_string_value(
    value: Any,
    *,
    field: str,
    source: str,
    expected: str,
) -> None:
    if value != expected:
        raise StrictJsonlError(
            f"Malformed {source}: {field} must be {expected!r}"
        )


def _require_hash_field(record: dict[str, Any], field: str, source: str) -> str:
    value = _require_string_field(record, field, source)
    if not re.fullmatch(r"[0-9a-f]{64}", value):
        raise StrictJsonlError(
            f"Malformed {source}: {field} must be a SHA-256 hex digest"
        )
    return value


def _require_bool_field(record: dict[str, Any], field: str, source: str) -> bool:
    value = record.get(field)
    return _require_bool_value(value, field, source)


def _require_bool_value(
    value: Any,
    field: str,
    source: str,
    *,
    expected: bool | None = None,
) -> bool:
    if not isinstance(value, bool):
        raise StrictJsonlError(f"Malformed {source}: {field} must be boolean")
    if expected is not None and value is not expected:
        raise StrictJsonlError(
            f"Malformed {source}: {field} must be {expected!r}"
        )
    return value


def _require_non_negative_int_field(
    record: dict[str, Any],
    field: str,
    source: str,
) -> int:
    return _require_integer_value(record.get(field), field, source)


def _require_integer_value(
    value: Any,
    field: str,
    source: str,
    *,
    exact: int | None = None,
) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise StrictJsonlError(
            f"Malformed {source}: {field} must be a non-negative integer"
        )
    if exact is not None and value != exact:
        raise StrictJsonlError(
            f"Malformed {source}: {field} must be {exact}"
        )
    return value


def _require_none_field(record: dict[str, Any], field: str, source: str) -> None:
    if record.get(field) is not None:
        raise StrictJsonlError(f"Malformed {source}: {field} must be null")


@contextlib.contextmanager
def _locked_jsonl_paths(*paths: Path | None):
    lock_paths: dict[str, Path] = {}
    for path in paths:
        if path is None:
            continue
        lock_path = _jsonl_lock_path(Path(path))
        key = os.path.normcase(str(lock_path.resolve(strict=False)))
        lock_paths[key] = lock_path
    handles = []
    try:
        for lock_path in [lock_paths[key] for key in sorted(lock_paths)]:
            _ensure_parent_directory(lock_path, "strict JSONL lock file")
            handle = lock_path.open("a+b")
            try:
                _acquire_jsonl_file_lock(handle, lock_path)
            except Exception:
                handle.close()
                raise
            handles.append((handle, lock_path))
        yield
    finally:
        release_error: StrictJsonlError | None = None
        for handle, lock_path in reversed(handles):
            try:
                _release_jsonl_file_lock(handle, lock_path)
            except StrictJsonlError as exc:
                if release_error is None:
                    release_error = exc
            finally:
                handle.close()
        if release_error is not None:
            raise release_error


def _jsonl_lock_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.lock")


def _acquire_jsonl_file_lock(handle, lock_path: Path) -> None:
    try:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
            os.fsync(handle.fileno())
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
    except OSError as exc:
        raise StrictJsonlError(
            f"Could not acquire strict JSONL lock at {_safe_path_text(lock_path)}: "
            f"{exc.__class__.__name__}: "
            f"{_bounded_redacted_text(str(exc), _MAX_JSON_ERROR_MESSAGE_CHARS)}"
        ) from exc


def _release_jsonl_file_lock(handle, lock_path: Path) -> None:
    try:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except OSError as exc:
        raise StrictJsonlError(
            f"Could not release strict JSONL lock at {_safe_path_text(lock_path)}: "
            f"{exc.__class__.__name__}: "
            f"{_bounded_redacted_text(str(exc), _MAX_JSON_ERROR_MESSAGE_CHARS)}"
        ) from exc


def _append_serialized_jsonl_line(path: Path, line: str) -> None:
    # Keep this façade wrapper as a private compatibility anchor.  In
    # particular, callers/tests may patch jsonl.open or jsonl.os.fsync while
    # the storage primitive remains deliberately unaware of JSONL policy.
    _jsonl_storage.append_serialized_jsonl_line(
        path,
        line,
        open_fn=open,
        fsync_fn=os.fsync,
    )


def _partial_jsonl_diagnostic(
    path: Path,
    fragment: bytes,
    keep_bytes: int,
    *,
    retention_mode: str = "redacted",
) -> dict:
    retention_mode = _validate_quarantine_retention_mode(retention_mode)
    try:
        fragment_text = fragment.decode("utf-8")
        fragment_utf8_valid = True
    except UnicodeDecodeError:
        fragment_text = fragment[:200].hex()
        fragment_utf8_valid = False
    retention = _retained_quarantine_text(
        fragment_text,
        mode=retention_mode,
        max_length=500,
    )
    diagnostic = {
        "event": "jsonl_torn_final_record_repaired",
        "stream": path.name,
        "path_sha256": hashlib.sha256(
            str(path.resolve(strict=False)).encode("utf-8")
        ).hexdigest(),
        "repair_policy": "truncate_unterminated_final_line",
        "complete_bytes_preserved": keep_bytes,
        "fragment_bytes": len(fragment),
        "fragment_utf8_valid": fragment_utf8_valid,
        "fragment_retention": retention["retention"],
    }
    if retention["sha256"] is not None:
        diagnostic["fragment_sha256"] = hashlib.sha256(fragment).hexdigest()
    if retention["text"] is not None:
        diagnostic["fragment_preview"] = retention["text"]
    return diagnostic


def _safe_path_text(path: Path) -> str:
    return _bounded_redacted_text(str(path), _MAX_JSON_ERROR_MESSAGE_CHARS)


def _ensure_parent_directory(path: Path, kind: str) -> None:
    parent = Path(path).parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        target = _bounded_redacted_text(str(path), _MAX_JSON_ERROR_MESSAGE_CHARS)
        message = _bounded_redacted_text(str(exc), _MAX_JSON_ERROR_MESSAGE_CHARS)
        raise StrictJsonlError(
            f"Could not prepare parent directory for {kind} at {target}: "
            f"{exc.__class__.__name__}: {message}"
        ) from exc


def _fsync_parent_directory(path: Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        try:
            os.fsync(fd)
        except OSError:
            return
    finally:
        os.close(fd)


def _json_error_message(record: Any, exc: Exception) -> str:
    details = _non_finite_details(record)
    message = str(exc)
    if details:
        message = f"{message}; non-finite values: {', '.join(details)}"
    return _bounded_redacted_text(message, _MAX_JSON_ERROR_MESSAGE_CHARS)


def _validate_strict_json_value(
    value: Any,
    path: str = "$",
    active: set[int] | None = None,
    depth: int = 0,
    max_depth: int = 100,
) -> None:
    if depth > max_depth:
        raise ValueError(f"JSON nesting exceeds maximum depth at {path}")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Out of range float values are not JSON compliant")
    if isinstance(value, dict):
        if active is None:
            active = set()
        obj_id = id(value)
        if obj_id in active:
            raise ValueError(f"Circular reference detected at {path}")
        active.add(obj_id)
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise TypeError(
                        f"JSON object key at {path} must be a string: "
                        f"{type(key).__name__} {_safe_inline_repr(key)}"
                    )
                _validate_strict_json_value(
                    item,
                    _json_path_child(path, key),
                    active,
                    depth + 1,
                    max_depth,
                )
        finally:
            active.remove(obj_id)
        return
    if isinstance(value, tuple):
        raise TypeError(f"JSON value at {path} must use list, not tuple")
    if isinstance(value, list):
        if active is None:
            active = set()
        obj_id = id(value)
        if obj_id in active:
            raise ValueError(f"Circular reference detected at {path}")
        active.add(obj_id)
        try:
            for index, item in enumerate(value):
                _validate_strict_json_value(
                    item, f"{path}[{index}]", active, depth + 1, max_depth
                )
        finally:
            active.remove(obj_id)


def _non_finite_details(
    value: Any,
    path: str = "$",
    active: set[int] | None = None,
    depth: int = 0,
    max_depth: int = 100,
) -> list[str]:
    if depth > max_depth:
        return []
    if isinstance(value, float) and not math.isfinite(value):
        return [f"{path}={value!r}"]
    if isinstance(value, dict):
        if active is None:
            active = set()
        obj_id = id(value)
        if obj_id in active:
            return []
        active.add(obj_id)
        details: list[str] = []
        try:
            for key, item in value.items():
                child_path = (
                    _json_path_child(path, key)
                    if isinstance(key, str)
                    else f"{path}.<non-string-key>"
                )
                details.extend(
                    _non_finite_details(item, child_path, active, depth + 1, max_depth)
                )
        finally:
            active.remove(obj_id)
        return details
    if isinstance(value, tuple):
        return []
    if isinstance(value, list):
        if active is None:
            active = set()
        obj_id = id(value)
        if obj_id in active:
            return []
        active.add(obj_id)
        details = []
        try:
            for index, item in enumerate(value):
                details.extend(
                    _non_finite_details(
                        item, f"{path}[{index}]", active, depth + 1, max_depth
                    )
                )
        finally:
            active.remove(obj_id)
        return details
    return []


def _json_path_child(path: str, key: str) -> str:
    if key.replace("_", "").isalnum() and key and not key[0].isdigit():
        return f"{path}.{key}"
    return f"{path}[{json.dumps(key, ensure_ascii=False)}]"


def _safe_record_repr(
    record: Any,
    max_length: int = _MAX_RECORD_REPR_CHARS,
    *,
    mode: str = "redacted",
) -> dict[str, Any]:
    mode = _validate_quarantine_retention_mode(mode)
    error: str | None = None
    try:
        original = repr(record)
    except Exception as exc:  # pragma: no cover - exact repr failures are caller-defined
        original = "<repr failed>"
        error = f"{exc.__class__.__name__}: {_safe_inline_repr(str(exc))}"
    if error is not None:
        error = redact_sensitive_text(error)
    retained = _retained_quarantine_text(original, mode=mode, max_length=max_length)
    return {
        "text": retained["text"],
        "truncated": retained["truncated"],
        "error": error,
        "retention": retained["retention"],
    }


def _retained_quarantine_text(
    text: str,
    *,
    mode: str,
    max_length: int,
) -> dict[str, Any]:
    mode = _validate_quarantine_retention_mode(mode)
    if mode == "off":
        return {
            "text": None,
            "sha256": None,
            "truncated": False,
            "retention": {
                "retention_mode": mode,
                "retention_policy": "off_no_text_or_hash",
                "sha256": None,
                "chars": None,
                "stored_chars": 0,
                "max_chars": max_length,
                "redacted": None,
                "truncated": False,
            },
        }
    raw_sha256 = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
    if mode == "hash_only":
        return {
            "text": None,
            "sha256": raw_sha256,
            "truncated": False,
            "retention": {
                "retention_mode": mode,
                "retention_policy": "hash_only_with_raw_sha256",
                "sha256": raw_sha256,
                "chars": len(text),
                "stored_chars": 0,
                "max_chars": max_length,
                "redacted": None,
                "truncated": False,
            },
        }
    redacted = redact_sensitive_text(text)
    truncated = mode != "full" and len(redacted) > max_length
    retained_text = (
        redacted[: max_length - 15] + "...<truncated>"
        if truncated
        else redacted
    )
    return {
        "text": retained_text,
        "sha256": raw_sha256,
        "truncated": truncated,
        "retention": {
            "retention_mode": mode,
            "retention_policy": (
                "full_secret_redacted_text_with_raw_sha256"
                if mode == "full"
                else "redact_then_prefix_truncate_with_sha256"
            ),
            "sha256": raw_sha256,
            "chars": len(text),
            "stored_chars": len(retained_text),
            "max_chars": max_length,
            "redacted": redacted != text,
            "truncated": truncated,
        },
    }


def _validate_quarantine_retention_mode(value: object) -> str:
    if not isinstance(value, str) or value not in _QUARANTINE_RETENTION_MODES:
        raise ValueError(
            "quarantine_snapshot_retention_mode must be one of: "
            f"{', '.join(sorted(_QUARANTINE_RETENTION_MODES))}"
        )
    return value


def _safe_inline_repr(value: Any, max_length: int = 120) -> str:
    try:
        text = repr(value)
    except Exception as exc:  # pragma: no cover - exact repr failures are caller-defined
        text = f"<repr failed: {exc.__class__.__name__}>"
    text = _redact_json_diagnostic_text(text)
    if len(text) > max_length:
        return text[: max_length - 15] + "...<truncated>"
    return text


def _bounded_redacted_text(text: str, max_length: int) -> str:
    text = _redact_json_diagnostic_text(text)
    if len(text) > max_length:
        return text[: max_length - 15] + "...<truncated>"
    return text


def _redact_json_diagnostic_text(text: str) -> str:
    text = redact_sensitive_text(text)
    return _REDACTED_SECRET_ASSIGNMENT.sub("[REDACTED]", text)
