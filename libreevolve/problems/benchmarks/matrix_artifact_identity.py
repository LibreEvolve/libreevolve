"""Low-level identity helpers for matrix publication artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from libreevolve.problems.benchmarks._path_policy import safe_relative_path


def write_canonical_json(path: Path, payload: dict[str, Any]) -> tuple[str, int]:
    """Write deterministic, newline-terminated JSON and return its identity."""
    raw = json.dumps(payload, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest(), len(raw)


def file_digest_and_size(path: Path) -> tuple[str, int]:
    """Return a file's SHA-256 and byte count, or empty identity on read failure."""
    try:
        raw = path.read_bytes()
    except OSError:
        return "", 0
    return hashlib.sha256(raw).hexdigest(), len(raw)


def stable_json_sha256(value: object) -> str:
    """Return the SHA-256 of compact, key-sorted JSON."""
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def safe_relative_artifact_path(value: object) -> Path | None:
    """Return an artifact path accepted under both POSIX and Windows grammar."""
    return safe_relative_path(value)


def matrix_artifact_inventory_record(
    artifact: object,
    root: Path,
    *,
    validate_source_rights: Callable[[dict[str, Any]], Any],
) -> dict[str, Any]:
    """Build one concrete-file identity record for a declared artifact."""
    if not isinstance(artifact, dict):
        return {
            "kind": "unknown",
            "path": "",
            "status": "invalid_artifact",
            "issues": ["invalid_artifact"],
        }
    kind = artifact.get("kind")
    path = artifact.get("path")
    expected_sha = artifact.get("sha256")
    expected_bytes = artifact.get("bytes")
    rights = artifact.get("source_rights")
    record: dict[str, Any] = {
        "kind": kind if isinstance(kind, str) else "unknown",
        "path": path if isinstance(path, str) else "",
        "expected_sha256": expected_sha if isinstance(expected_sha, str) else "",
        "expected_bytes": (
            expected_bytes
            if isinstance(expected_bytes, int) and not isinstance(expected_bytes, bool)
            else None
        ),
        "source_rights": rights if isinstance(rights, dict) else None,
        "status": "verified",
        "issues": [],
    }
    if not isinstance(rights, dict):
        record["status"] = "invalid_artifact"
        record["issues"].append("source_rights_missing")
    else:
        rights_report = validate_source_rights(rights)
        if not rights_report.ok:
            record["status"] = "invalid_artifact"
            record["issues"].extend(
                f"source_rights_{issue.code}" for issue in rights_report.issues
            )
    path_obj = safe_relative_artifact_path(path)
    if path_obj is None:
        record["status"] = "unsafe_path"
        record["issues"].append("invalid_artifact_path")
        return record
    try:
        resolved_root = root.resolve()
        resolved_path = (resolved_root / path_obj).resolve(strict=False)
    except OSError:
        record["status"] = "unsafe_path"
        record["issues"].append("invalid_artifact_path")
        return record
    if not resolved_path.is_relative_to(resolved_root):
        record["status"] = "unsafe_path"
        record["issues"].append("artifact_path_outside_root")
        return record
    if not resolved_path.exists():
        record["status"] = "missing_file"
        record["issues"].append("missing_artifact_file")
        return record
    if not resolved_path.is_file():
        record["status"] = "unsafe_path"
        record["issues"].append("artifact_path_not_file")
        return record
    try:
        raw = resolved_path.read_bytes()
    except OSError:
        record["status"] = "read_error"
        record["issues"].append("artifact_read_error")
        return record
    actual_sha = hashlib.sha256(raw).hexdigest()
    actual_bytes = len(raw)
    record["actual_sha256"] = actual_sha
    record["actual_bytes"] = actual_bytes
    if not isinstance(expected_sha, str) or len(expected_sha) != 64 or any(
        character not in "0123456789abcdef" for character in expected_sha
    ):
        record["status"] = "hash_mismatch"
        record["issues"].append("invalid_expected_artifact_hash")
    elif actual_sha != expected_sha:
        record["status"] = "hash_mismatch"
        record["issues"].append("artifact_hash_mismatch")
    if isinstance(expected_bytes, bool) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
        if record["status"] == "verified":
            record["status"] = "bytes_mismatch"
        record["issues"].append("invalid_expected_artifact_bytes")
    elif actual_bytes != expected_bytes:
        if record["status"] == "verified":
            record["status"] = "bytes_mismatch"
        record["issues"].append("artifact_bytes_mismatch")
    return record
