from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any

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
):
    path = Path(path)
    label = stream_name or path.name
    try:
        handle = path.open("rb")
    except OSError as exc:
        message = _bounded_redacted_text(str(exc), _MAX_JSON_ERROR_MESSAGE_CHARS)
        raise StrictJsonlError(
            f"Failed to read {label}: {exc.__class__.__name__}: {message}"
        ) from exc
    with handle:
        for line_number, raw_line in enumerate(handle, start=1):
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
    repair_trailing_partial_jsonl(
        path,
        quarantine_path=quarantine_path,
        quarantine_snapshot_retention_mode=retention_mode,
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
    repair_trailing_partial_jsonl(
        path,
        quarantine_snapshot_retention_mode=retention_mode,
    )
    _append_serialized_jsonl_line(path, strict_json_dumps(diagnostic))


def repair_trailing_partial_jsonl(
    path: Path,
    *,
    quarantine_path: Path | None = None,
    quarantine_snapshot_retention_mode: str = "redacted",
) -> dict[str, Any]:
    """Truncate an unterminated final JSONL fragment and log a diagnostic.

    Managed JSONL appends always write a newline-terminated record. A non-empty
    final fragment without a newline is therefore treated as a torn append from
    a prior interrupted write, not as a valid complete record.
    """
    path = Path(path)
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


def _append_serialized_jsonl_line(path: Path, line: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())


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
