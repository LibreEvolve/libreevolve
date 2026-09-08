from __future__ import annotations

import base64
import binascii
from collections.abc import Mapping
from dataclasses import dataclass, field
import hashlib
import io
from pathlib import Path
import re
import shutil
import tempfile
import tokenize
import unicodedata

from libreevolve.core.diff import (
    apply_diff,
    parse_diff_blocks,
    _line_ending_tolerant_matches,
    _replace_line_ending_tolerant,
    _strip_fences,
    strip_allowed_leading_preamble,
    strip_proposal_metadata,
)
from libreevolve.core.redaction import redact_sensitive_text

EVOLVE_BLOCK_START = "# EVOLVE-BLOCK-START"
EVOLVE_BLOCK_END = "# EVOLVE-BLOCK-END"
MUTATION_MODES = {"diff", "full"}
_BLOCK_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]+$")
_NON_PYTHON_EVOLVE_MARKER_PREFIXES = ("#", "//", "/*", "*", "<!--")
_HOST_INVALID_CHARS = set('<>"|?*')
_MAX_CANDIDATE_PATH_COMPONENT_CHARS = 255
_MAX_CANDIDATE_PATH_CHARS = 1024
DEFAULT_MAX_CANDIDATE_WORKSPACE_FILES = 256
DEFAULT_MAX_CANDIDATE_FILE_CHARS = 1_000_000
DEFAULT_MAX_CANDIDATE_TOTAL_CHARS = 2_000_000
DEFAULT_MAX_MUTATION_PAYLOAD_CHARS = 2_000_000
DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES = 2_000_000
DEFAULT_MAX_CANDIDATE_TOTAL_STATIC_BYTES = 10_000_000
_STATIC_MEMBER_KINDS = frozenset({"static", "binary", "fixture", "artifact"})
_STATIC_MEMBER_SOURCE_KINDS = frozenset(
    {
        "unknown",
        "direct_workspace_record",
        "seed_workspace_file",
        "generated_artifact",
        "copied_static_asset",
    }
)
_STATIC_MEMBER_MUTATION_POLICIES = frozenset(
    {"immutable", "metadata_only", "llm_editable"}
)
_SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
_WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}

_BLOCK_SECTION_PATTERN = re.compile(
    r"^<<<BLOCK[ \t]*(.*?)\n(.*?)\n^>>>BLOCK[ \t]*(?:\n|$)",
    re.DOTALL | re.MULTILINE,
)
_FILE_SECTION_PATTERN = re.compile(
    r"^<<<FILE[ \t]*(.*?)\n(.*?)^>>>FILE[ \t]*(?:\n|$)",
    re.DOTALL | re.MULTILINE,
)


class CandidateMaterializationError(ValueError):
    """Structured materialization failure for candidate workspaces."""

    def __init__(
        self,
        message: str,
        *,
        reason: str,
        paths: tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)
        self.reason = reason
        self.paths = paths


@dataclass
class CandidateWorkspace:
    """A candidate represented as a text file set.

    The `primary_file` keeps the existing single-string API meaningful: legacy
    validators and prompts still see the primary file as `code`.
    """

    files: dict[str, str | bytes | bytearray] = field(default_factory=dict)
    primary_file: str = "main.py"
    allowed_reserved_paths: frozenset[str] = field(default_factory=frozenset)
    static_files: tuple[dict[str, str | int], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.files, Mapping):
            raise ValueError("Candidate workspace files must be a mapping")
        if not isinstance(self.primary_file, str):
            raise ValueError("Candidate workspace primary_file must be a string")
        allowed_reserved_paths = _normalize_allowed_reserved_paths(
            self.allowed_reserved_paths
        )
        normalized_files: dict[str, str] = {}
        raw_binary_static_files: list[dict[str, str | int]] = []
        for raw_path, content in self.files.items():
            if not isinstance(raw_path, str):
                raise ValueError("Candidate workspace file paths must be strings")
            path = normalize_candidate_path(
                raw_path,
                allowed_reserved_paths=allowed_reserved_paths,
            )
            if isinstance(content, (bytes, bytearray)):
                raw_binary_static_files.append(
                    _raw_binary_static_file_record(path, bytes(content))
                )
                continue
            if not isinstance(content, str):
                raise ValueError(
                    "Candidate workspace file content must be a string or bytes: "
                    f"{raw_path!r}"
                )
            _validate_candidate_text_utf8(raw_path, content)
            if path in normalized_files:
                raise ValueError(
                    "Duplicate candidate path after normalization: "
                    f"{raw_path!r} -> {path!r}"
                )
            normalized_files[path] = content
        self.files = normalized_files
        self.allowed_reserved_paths = frozenset(allowed_reserved_paths)
        self.primary_file = normalize_candidate_path(
            self.primary_file,
            allowed_reserved_paths=allowed_reserved_paths,
        )
        if self.primary_file in {str(item["path"]) for item in raw_binary_static_files}:
            raise ValueError("Candidate workspace primary_file cannot be a binary member")
        if not self.files:
            self.files[self.primary_file] = ""
        if self.primary_file not in self.files:
            raise ValueError(
                f"Primary file {self.primary_file!r} is not present in candidate files"
            )
        static_records = _append_static_file_records(
            self.static_files,
            raw_binary_static_files,
        )
        self.static_files = _normalize_static_file_records(
            static_records,
            allowed_reserved_paths=allowed_reserved_paths,
            text_paths=self.files,
        )
        validate_candidate_workspace_limits(self.files, static_files=self.static_files)

    @classmethod
    def from_code(cls, code: str, path: str = "main.py") -> "CandidateWorkspace":
        path = normalize_candidate_path(path)
        return cls(files={path: code}, primary_file=path)

    @classmethod
    def from_dict(cls, data: dict) -> "CandidateWorkspace":
        if not isinstance(data, Mapping):
            raise ValueError("Candidate workspace record must be a mapping")
        files = data.get("files", {})
        if not isinstance(files, Mapping):
            raise ValueError("Candidate workspace files must be a mapping")
        primary_file = data.get("primary_file", "main.py")
        if not isinstance(primary_file, str):
            raise ValueError("Candidate workspace primary_file must be a string")
        allowed_reserved_paths = data.get("allowed_reserved_paths", ())
        return cls(
            files=dict(files),
            primary_file=primary_file,
            allowed_reserved_paths=allowed_reserved_paths,
            static_files=data.get("static_files", ()),
        )

    @property
    def code(self) -> str:
        files, primary_file, _static_files = self._validated_state()
        return files[primary_file]

    def to_dict(self) -> dict:
        files, primary_file, static_files = self._validated_state()
        record = {"primary_file": primary_file, "files": files}
        if self.allowed_reserved_paths:
            record["allowed_reserved_paths"] = sorted(self.allowed_reserved_paths)
        if static_files:
            record["static_files"] = [dict(item) for item in static_files]
        return record

    def materialize(self, root: Path) -> Path:
        files, primary_file, static_files = self._validated_state()
        root = _prepare_materialization_root(Path(root))
        targets: dict[str, str] = {}
        for rel in files:
            safe_candidate_path(
                root,
                rel,
                allowed_reserved_paths=self.allowed_reserved_paths,
            )
            key = _candidate_path_collision_key(rel)
            if key in targets:
                raise CandidateMaterializationError(
                    "Candidate paths collide when materialized: "
                    f"{targets[key]!r} and {rel!r}",
                    reason="candidate_path_collision",
                    paths=(targets[key], rel),
                )
            targets[key] = rel
        materialized_static_files = [
            item
            for item in static_files
            if isinstance(item.get("content_b64"), str)
            or isinstance(item.get("source_copy_path"), str)
        ]
        for item in materialized_static_files:
            rel = str(item["path"])
            safe_candidate_path(
                root,
                rel,
                allowed_reserved_paths=self.allowed_reserved_paths,
            )
            key = _candidate_path_collision_key(rel)
            if key in targets:
                raise CandidateMaterializationError(
                    "Candidate paths collide when materialized: "
                    f"{targets[key]!r} and {rel!r}",
                    reason="candidate_path_collision",
                    paths=(targets[key], rel),
                )
            targets[key] = rel
        temp_root = _make_materialization_sibling(root, "tmp")
        backup_root: Path | None = None
        root_moved_to_backup = False
        for rel, content in files.items():
            target = safe_candidate_path(
                temp_root,
                rel,
                allowed_reserved_paths=self.allowed_reserved_paths,
            )
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content.encode("utf-8"))
            except OSError as exc:
                _remove_materialization_tree(temp_root, root.parent)
                raise CandidateMaterializationError(
                    f"Candidate file could not be written: {rel}: {exc}",
                    reason="candidate_file_write_failed",
                    paths=(rel,),
                ) from exc
            except BaseException:
                _remove_materialization_tree(temp_root, root.parent)
                raise
        for item in materialized_static_files:
            rel = str(item["path"])
            target = safe_candidate_path(
                temp_root,
                rel,
                allowed_reserved_paths=self.allowed_reserved_paths,
            )
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(_static_file_materialization_bytes(item))
            except CandidateMaterializationError:
                _remove_materialization_tree(temp_root, root.parent)
                raise
            except OSError as exc:
                _remove_materialization_tree(temp_root, root.parent)
                raise CandidateMaterializationError(
                    f"Candidate static file could not be written: {rel}: {exc}",
                    reason="candidate_static_file_write_failed",
                    paths=(rel,),
                ) from exc
            except BaseException:
                _remove_materialization_tree(temp_root, root.parent)
                raise
        try:
            if root.exists():
                backup_root = _make_materialization_sibling(root, "backup")
                try:
                    backup_root.rmdir()
                except OSError as exc:
                    raise CandidateMaterializationError(
                        "Candidate workspace backup placeholder could not be removed: "
                        f"{backup_root}: {exc}",
                        reason="materialization_backup_placeholder_delete_failed",
                        paths=(str(backup_root),),
                    ) from exc
                try:
                    root.rename(backup_root)
                    root_moved_to_backup = True
                except OSError as exc:
                    raise CandidateMaterializationError(
                        "Candidate workspace root could not be moved to backup: "
                        f"{root} -> {backup_root}: {exc}",
                        reason="materialization_existing_root_backup_failed",
                        paths=(str(root), str(backup_root)),
                    ) from exc
            try:
                temp_root.rename(root)
            except OSError as exc:
                raise CandidateMaterializationError(
                    "Candidate workspace temporary root could not be swapped into place: "
                    f"{temp_root} -> {root}: {exc}",
                    reason="materialization_swap_failed",
                    paths=(str(temp_root), str(root)),
                ) from exc
        except BaseException:
            if root_moved_to_backup and root.exists():
                _remove_materialization_tree(root, root.parent)
            if root_moved_to_backup and backup_root is not None and backup_root.exists():
                try:
                    backup_root.rename(root)
                except OSError as exc:
                    raise CandidateMaterializationError(
                        "Candidate workspace backup could not be restored: "
                        f"{backup_root} -> {root}: {exc}",
                        reason="materialization_restore_failed",
                        paths=(str(backup_root), str(root)),
                    ) from exc
            _remove_materialization_tree(temp_root, root.parent)
            raise
        if backup_root is not None and backup_root.exists():
            try:
                _remove_materialization_tree(backup_root, root.parent)
            except OSError:
                pass
        return safe_candidate_path(
            root,
            primary_file,
            allowed_reserved_paths=self.allowed_reserved_paths,
        )

    def _validated_state(self) -> tuple[dict[str, str], str, tuple[dict[str, str | int], ...]]:
        snapshot = CandidateWorkspace(
            files=self.files,
            primary_file=self.primary_file,
            allowed_reserved_paths=self.allowed_reserved_paths,
            static_files=self.static_files,
        )
        return dict(snapshot.files), snapshot.primary_file, snapshot.static_files


def normalize_candidate_path(
    path: str,
    *,
    allowed_reserved_paths: frozenset[str] | set[str] | tuple[str, ...] | list[str] = (),
) -> str:
    normalized = _normalize_candidate_path_text(path)
    allowed_reserved = _normalize_allowed_reserved_paths(allowed_reserved_paths)
    parts = normalized.split("/")
    if (
        not parts
        or len(normalized) > _MAX_CANDIDATE_PATH_CHARS
        or any(p == "" or p == "." for p in parts)
        or any(
            _unsafe_candidate_path_component(
                p,
                allow_reserved=normalized in allowed_reserved,
            )
            for p in parts
        )
    ):
        raise ValueError(f"Unsafe candidate path: {path!r}")
    return "/".join(parts)


def _normalize_static_file_records(
    records: object,
    *,
    allowed_reserved_paths: frozenset[str],
    text_paths: Mapping[str, str],
) -> tuple[dict[str, str | int], ...]:
    if records is None:
        return ()
    if not isinstance(records, (list, tuple)):
        raise ValueError("Candidate workspace static_files must be a list")
    normalized: dict[str, dict[str, str | int]] = {}
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise ValueError(
                f"Candidate workspace static_files[{index}] must be a mapping"
            )
        raw_path = record.get("path")
        if not isinstance(raw_path, str):
            raise ValueError(
                f"Candidate workspace static_files[{index}].path must be a string"
            )
        path = normalize_candidate_path(
            raw_path,
            allowed_reserved_paths=allowed_reserved_paths,
        )
        if path in text_paths:
            raise ValueError(
                "Candidate workspace static file collides with text file: "
                f"{path!r}"
            )
        if path in normalized:
            raise ValueError(f"Duplicate candidate static file path: {path!r}")
        kind = record.get("kind")
        if kind not in _STATIC_MEMBER_KINDS:
            raise ValueError(
                f"Candidate workspace static_files[{index}].kind must be one of "
                f"{sorted(_STATIC_MEMBER_KINDS)!r}"
            )
        sha256 = record.get("sha256")
        if not isinstance(sha256, str):
            raise ValueError(
                f"Candidate workspace static_files[{index}].sha256 must be a string"
            )
        sha256 = sha256.lower()
        if _SHA256_HEX_RE.fullmatch(sha256) is None:
            raise ValueError(
                f"Candidate workspace static_files[{index}].sha256 must be 64 hex characters"
            )
        byte_count = record.get("bytes")
        if (
            isinstance(byte_count, bool)
            or not isinstance(byte_count, int)
            or byte_count < 0
        ):
            raise ValueError(
                f"Candidate workspace static_files[{index}].bytes must be a non-negative integer"
            )
        normalized_record: dict[str, str | int] = {
            "path": path,
            "kind": kind,
            "sha256": sha256,
            "bytes": byte_count,
            "source_kind": _normalize_static_member_enum(
                record,
                "source_kind",
                _STATIC_MEMBER_SOURCE_KINDS,
                default="unknown",
                index=index,
            ),
            "mutation_policy": _normalize_static_member_enum(
                record,
                "mutation_policy",
                _STATIC_MEMBER_MUTATION_POLICIES,
                default="immutable",
                index=index,
            ),
        }
        source_path = record.get("source_path")
        if source_path is not None:
            normalized_record["source_path"] = _normalize_static_member_label(
                source_path,
                f"Candidate workspace static_files[{index}].source_path",
            )
        if "content_b64" in record:
            content_b64 = record.get("content_b64")
            if not isinstance(content_b64, str):
                raise ValueError(
                    f"Candidate workspace static_files[{index}].content_b64 must be a string"
                )
            raw = _decode_static_file_content(
                content_b64,
                label=f"Candidate workspace static_files[{index}].content_b64",
            )
            if len(raw) > DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES:
                raise ValueError(
                    f"Candidate workspace static_files[{index}].content_b64 exceeds "
                    f"{DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES} decoded bytes"
                )
            if len(raw) != byte_count:
                raise ValueError(
                    f"Candidate workspace static_files[{index}].content_b64 byte count "
                    "does not match bytes"
                )
            if hashlib.sha256(raw).hexdigest() != sha256:
                raise ValueError(
                    f"Candidate workspace static_files[{index}].content_b64 sha256 "
                    "does not match sha256"
                )
            normalized_record["content_b64"] = content_b64
        if "source_copy_path" in record:
            source_copy_path = record.get("source_copy_path")
            normalized_record["source_copy_path"] = _normalize_static_member_label(
                source_copy_path,
                f"Candidate workspace static_files[{index}].source_copy_path",
            )
        normalized[path] = normalized_record
    return tuple(normalized[path] for path in sorted(normalized))


def _append_static_file_records(
    records: object,
    generated: list[dict[str, str | int]],
) -> object:
    if not generated:
        return records
    if records is None:
        return generated
    if not isinstance(records, (list, tuple)):
        return records
    return [*records, *generated]


def _raw_binary_static_file_record(path: str, raw: bytes) -> dict[str, str | int]:
    encoded = base64.b64encode(raw).decode("ascii")
    return {
        "path": path,
        "kind": "binary",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "source_kind": "direct_workspace_record",
        "mutation_policy": "immutable",
        "content_b64": encoded,
    }


def _normalize_static_member_enum(
    record: Mapping,
    field_name: str,
    allowed: frozenset[str],
    *,
    default: str,
    index: int,
) -> str:
    value = record.get(field_name, default)
    if value not in allowed:
        raise ValueError(
            f"Candidate workspace static_files[{index}].{field_name} must be one of "
            f"{sorted(allowed)!r}"
        )
    return str(value)


def _normalize_static_member_label(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    if len(value) > _MAX_CANDIDATE_PATH_CHARS:
        raise ValueError(f"{label} is too long")
    if redact_sensitive_text(value) != value:
        raise ValueError(f"{label} must not contain secret-like text")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError(f"{label} must be display-safe")
    normalized = unicodedata.normalize("NFC", value)
    if unicodedata.normalize("NFKC", normalized) != normalized:
        raise ValueError(f"{label} must be compatibility-normalized")
    return normalized


def _decode_static_file_content(content_b64: str, *, label: str) -> bytes:
    try:
        return base64.b64decode(content_b64.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error) as exc:
        raise ValueError(f"{label} must be valid base64") from exc


def _static_file_content_bytes(record: Mapping[str, str | int]) -> bytes:
    content_b64 = record.get("content_b64")
    if not isinstance(content_b64, str):
        raise ValueError(f"Static file {record.get('path')!r} has no encoded content")
    return _decode_static_file_content(
        content_b64,
        label=f"Static file {record.get('path')!r} content_b64",
    )


def _static_file_materialization_bytes(record: Mapping[str, str | int]) -> bytes:
    if isinstance(record.get("content_b64"), str):
        return _static_file_content_bytes(record)
    source_copy_path = record.get("source_copy_path")
    if not isinstance(source_copy_path, str):
        raise CandidateMaterializationError(
            f"Static file {record.get('path')!r} has no materializable content",
            reason="static_source_copy_missing_content",
            paths=_materialization_paths(record.get("path")),
        )
    source = Path(source_copy_path)
    if _path_is_link(source):
        raise CandidateMaterializationError(
            f"Static file {record.get('path')!r} source_copy_path cannot be a link",
            reason="static_source_copy_link",
            paths=_materialization_paths(record.get("path"), source_copy_path),
        )
    linked_ancestor = _linked_existing_ancestor(source)
    if linked_ancestor is not None:
        raise CandidateMaterializationError(
            f"Static file {record.get('path')!r} source_copy_path contains "
            f"a linked ancestor: {linked_ancestor}",
            reason="static_source_copy_linked_ancestor",
            paths=_materialization_paths(record.get("path"), str(linked_ancestor)),
        )
    try:
        if not source.is_file():
            raise CandidateMaterializationError(
                f"Static file {record.get('path')!r} source_copy_path is not a file",
                reason="static_source_copy_not_file",
                paths=_materialization_paths(record.get("path"), source_copy_path),
            )
        raw = source.read_bytes()
    except OSError as exc:
        raise CandidateMaterializationError(
            f"Static file {record.get('path')!r} source_copy_path could not be read",
            reason="static_source_copy_read_failed",
            paths=_materialization_paths(record.get("path"), source_copy_path),
        ) from exc
    expected_bytes = record.get("bytes")
    if len(raw) != expected_bytes:
        raise CandidateMaterializationError(
            f"Static file {record.get('path')!r} source_copy_path byte count "
            "does not match bytes",
            reason="static_source_copy_byte_count_mismatch",
            paths=_materialization_paths(record.get("path"), source_copy_path),
        )
    expected_sha256 = record.get("sha256")
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise CandidateMaterializationError(
            f"Static file {record.get('path')!r} source_copy_path sha256 "
            "does not match sha256",
            reason="static_source_copy_sha256_mismatch",
            paths=_materialization_paths(record.get("path"), source_copy_path),
        )
    return raw


def _materialization_paths(*values: object) -> tuple[str, ...]:
    return tuple(str(value) for value in values if isinstance(value, (str, Path)))


def _normalize_candidate_path_text(path: str) -> str:
    raw = path.replace("\\", "/")
    if redact_sensitive_text(raw) != raw:
        raise ValueError("Candidate workspace path must not contain secret-like text")
    if raw.startswith("/"):
        raise ValueError(f"Unsafe candidate path: {path!r}")
    if any(unicodedata.normalize("NFC", char) != char for char in raw):
        raise ValueError("Candidate workspace path must be compatibility-normalized")
    normalized = unicodedata.normalize("NFC", raw)
    if unicodedata.normalize("NFKC", normalized) != normalized:
        raise ValueError("Candidate workspace path must be compatibility-normalized")
    return normalized


def _unsafe_candidate_path_component(component: str, *, allow_reserved: bool = False) -> bool:
    if (
        component == ".."
        or ":" in component
    ):
        return True
    if not allow_reserved and (component == "__pycache__" or component.startswith(".")):
        return True
    if len(component) > _MAX_CANDIDATE_PATH_COMPONENT_CHARS:
        return True
    if component != component.strip(" ") or component != component.rstrip("."):
        return True
    if any(ord(char) < 32 or ord(char) == 127 for char in component):
        return True
    if any(
        unicodedata.category(char) == "Cf"
        or unicodedata.category(char) == "Cs"
        or (unicodedata.category(char) == "Zs" and char != " ")
        for char in component
    ):
        return True
    if any(char in _HOST_INVALID_CHARS for char in component):
        return True
    stem = component.split(".", 1)[0].upper()
    return stem in _WINDOWS_RESERVED_NAMES


def safe_candidate_path(
    root: Path,
    rel_path: str,
    *,
    allowed_reserved_paths: frozenset[str] | set[str] | tuple[str, ...] | list[str] = (),
) -> Path:
    rel = normalize_candidate_path(
        rel_path,
        allowed_reserved_paths=allowed_reserved_paths,
    )
    root_resolved = root.resolve()
    target = (root_resolved / rel).resolve()
    if root_resolved != target and root_resolved not in target.parents:
        raise ValueError(f"Candidate path escapes workspace: {rel_path!r}")
    return target


def _normalize_allowed_reserved_paths(
    paths: frozenset[str] | set[str] | tuple[str, ...] | list[str],
) -> frozenset[str]:
    if paths in (None, ""):
        return frozenset()
    if isinstance(paths, str) or not isinstance(paths, (set, frozenset, tuple, list)):
        raise ValueError("Candidate workspace allowed_reserved_paths must be a list of paths")
    normalized: set[str] = set()
    for raw_path in paths:
        if not isinstance(raw_path, str):
            raise ValueError("Candidate workspace allowed_reserved_paths must be strings")
        path = _normalize_candidate_path_text(raw_path)
        parts = path.split("/")
        if (
            not parts
            or len(path) > _MAX_CANDIDATE_PATH_CHARS
            or any(p == "" or p == "." for p in parts)
            or any(_unsafe_candidate_path_component(p, allow_reserved=True) for p in parts)
        ):
            raise ValueError(f"Unsafe candidate path: {raw_path!r}")
        if not _candidate_path_has_reserved_component(path):
            raise ValueError(
                "Candidate workspace allowed_reserved_paths must name reserved paths"
            )
        normalized.add(path)
    return frozenset(normalized)


def _candidate_path_has_reserved_component(path: str) -> bool:
    return any(
        part == "__pycache__" or part.startswith(".")
        for part in path.split("/")
    )


def validate_candidate_workspace_limits(
    files: Mapping[str, str],
    *,
    static_files: tuple[dict[str, str | int], ...] | list[dict[str, str | int]] = (),
    max_files: int = DEFAULT_MAX_CANDIDATE_WORKSPACE_FILES,
    max_file_chars: int = DEFAULT_MAX_CANDIDATE_FILE_CHARS,
    max_total_chars: int = DEFAULT_MAX_CANDIDATE_TOTAL_CHARS,
    max_static_file_bytes: int = DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES,
    max_total_static_bytes: int = DEFAULT_MAX_CANDIDATE_TOTAL_STATIC_BYTES,
) -> dict:
    """Validate candidate size limits and return a compact size summary."""
    if isinstance(max_files, bool) or not isinstance(max_files, int) or max_files < 1:
        raise ValueError("max_candidate_workspace_files must be an integer >= 1")
    if (
        isinstance(max_file_chars, bool)
        or not isinstance(max_file_chars, int)
        or max_file_chars < 0
    ):
        raise ValueError("max_candidate_file_chars must be an integer >= 0")
    if (
        isinstance(max_total_chars, bool)
        or not isinstance(max_total_chars, int)
        or max_total_chars < 0
    ):
        raise ValueError("max_candidate_total_chars must be an integer >= 0")
    if (
        isinstance(max_static_file_bytes, bool)
        or not isinstance(max_static_file_bytes, int)
        or max_static_file_bytes < 0
    ):
        raise ValueError("max_candidate_static_file_bytes must be an integer >= 0")
    if (
        isinstance(max_total_static_bytes, bool)
        or not isinstance(max_total_static_bytes, int)
        or max_total_static_bytes < 0
    ):
        raise ValueError("max_candidate_total_static_bytes must be an integer >= 0")
    static_file_count = len(static_files)
    file_count = len(files) + static_file_count
    if file_count > max_files:
        raise ValueError(
            "Candidate workspace file count exceeds max_candidate_workspace_files "
            f"({file_count} > {max_files})"
        )
    total_chars = 0
    largest_file_chars = 0
    largest_file = None
    for path, content in files.items():
        char_count = len(content)
        if char_count > max_file_chars:
            raise ValueError(
                "Candidate workspace file exceeds max_candidate_file_chars "
                f"({path!r}: {char_count} > {max_file_chars})"
            )
        total_chars += char_count
        if total_chars > max_total_chars:
            raise ValueError(
                "Candidate workspace total text exceeds max_candidate_total_chars "
                f"({total_chars} > {max_total_chars})"
            )
        if char_count > largest_file_chars:
            largest_file_chars = char_count
            largest_file = path
    total_static_bytes = 0
    largest_static_file_bytes = 0
    largest_static_file = None
    for item in static_files:
        path = str(item.get("path"))
        byte_count = item.get("bytes")
        if (
            isinstance(byte_count, bool)
            or not isinstance(byte_count, int)
            or byte_count < 0
        ):
            raise ValueError("Candidate workspace static file bytes must be non-negative integers")
        if byte_count > max_static_file_bytes:
            raise ValueError(
                "Candidate workspace static file exceeds max_candidate_static_file_bytes "
                f"({path!r}: {byte_count} > {max_static_file_bytes})"
            )
        total_static_bytes += byte_count
        if total_static_bytes > max_total_static_bytes:
            raise ValueError(
                "Candidate workspace total static bytes exceeds "
                "max_candidate_total_static_bytes "
                f"({total_static_bytes} > {max_total_static_bytes})"
            )
        if byte_count > largest_static_file_bytes:
            largest_static_file_bytes = byte_count
            largest_static_file = path
    return {
        "file_count": file_count,
        "text_file_count": len(files),
        "static_file_count": static_file_count,
        "total_chars": total_chars,
        "total_static_bytes": total_static_bytes,
        "largest_file": largest_file,
        "largest_file_chars": largest_file_chars,
        "largest_static_file": largest_static_file,
        "largest_static_file_bytes": largest_static_file_bytes,
        "max_files": max_files,
        "max_file_chars": max_file_chars,
        "max_total_chars": max_total_chars,
        "max_static_file_bytes": max_static_file_bytes,
        "max_total_static_bytes": max_total_static_bytes,
        "policy": "reject_oversized_text_and_static_workspace",
    }


def _prepare_materialization_root(root: Path) -> Path:
    root = root.absolute()
    if _path_is_link(root):
        raise CandidateMaterializationError(
            f"Candidate workspace root cannot be a link: {root}",
            reason="candidate_root_link",
            paths=(str(root),),
        )
    linked_ancestor = _linked_existing_ancestor(root)
    if linked_ancestor is not None:
        raise CandidateMaterializationError(
            f"Candidate workspace root contains a linked ancestor: {linked_ancestor}",
            reason="candidate_root_linked_ancestor",
            paths=(str(linked_ancestor),),
        )
    root = root.resolve()
    if root.exists() and not root.is_dir():
        raise CandidateMaterializationError(
            f"Candidate workspace root must be a directory: {root}",
            reason="candidate_root_not_directory",
            paths=(str(root),),
        )
    try:
        root.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise CandidateMaterializationError(
            f"Candidate workspace root parent could not be created: {root.parent}",
            reason="candidate_root_parent_create_failed",
            paths=(str(root.parent),),
        ) from exc
    if root.exists():
        _reject_linked_materialization_entries(root)
    return root


def _make_materialization_sibling(root: Path, label: str) -> Path:
    try:
        return Path(
            tempfile.mkdtemp(
                prefix=f".{root.name}.{label}-",
                dir=root.parent,
            )
        )
    except OSError as exc:
        raise CandidateMaterializationError(
            f"Candidate workspace {label} directory could not be created: {root.parent}",
            reason=f"materialization_{label}_root_create_failed",
            paths=(str(root.parent),),
        ) from exc


def _remove_materialization_tree(path: Path, parent: Path) -> None:
    if not path.exists():
        return
    _reject_linked_materialization_entries(path)
    resolved = path.resolve()
    parent_resolved = parent.resolve()
    if resolved == parent_resolved or parent_resolved not in resolved.parents:
        raise CandidateMaterializationError(
            f"Refusing to remove path outside materialization parent: {path}",
            reason="materialization_cleanup_outside_parent",
            paths=(str(path), str(parent)),
        )
    try:
        shutil.rmtree(resolved)
    except OSError as exc:
        raise CandidateMaterializationError(
            f"Candidate workspace materialization tree could not be removed: {path}",
            reason="materialization_cleanup_delete_failed",
            paths=(str(path),),
        ) from exc


def _path_is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (is_junction is not None and is_junction())


def _reject_linked_materialization_entries(root: Path) -> None:
    stack = [root]
    while stack:
        current = stack.pop()
        if _path_is_link(current):
            raise CandidateMaterializationError(
                f"Candidate workspace root contains a link: {current}",
                reason="candidate_root_contains_link",
                paths=(str(current),),
            )
        try:
            children = list(current.iterdir())
        except OSError as exc:
            raise CandidateMaterializationError(
                f"Candidate workspace root could not be inspected: {current}",
                reason="candidate_root_inspection_failed",
                paths=(str(current),),
            ) from exc
        for child in children:
            if _path_is_link(child):
                raise CandidateMaterializationError(
                    f"Candidate workspace root contains a link: {child}",
                    reason="candidate_root_contains_link",
                    paths=(str(child),),
                )
            if child.is_dir():
                stack.append(child)


def _linked_existing_ancestor(path: Path) -> Path | None:
    current = path.parent
    while current != current.parent:
        if _path_is_link(current):
            return current
        current = current.parent
    if _path_is_link(current):
        return current
    return None


def _validate_candidate_text_utf8(rel_path: str, content: str) -> None:
    try:
        content.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError(
            f"Candidate workspace file content must be UTF-8 encodable: {rel_path!r}"
        ) from exc


def _candidate_text_utf8_error(content: str) -> str | None:
    try:
        content.encode("utf-8")
    except UnicodeEncodeError:
        return "non_utf8_content"
    return None


@dataclass(frozen=True)
class EvolveBlock:
    name: str
    start: int
    content_start: int
    content_end: int
    end: int
    content: str


@dataclass(frozen=True)
class _EvolveMarker:
    text: str
    line_start: int
    line_end: int


def extract_evolve_blocks(code: str) -> list[EvolveBlock]:
    """Return marked evolvable regions while preserving surrounding skeleton."""
    return _parse_evolve_blocks(code)[0]


def validate_evolve_blocks(code: str) -> str | None:
    """Return an error code when EVOLVE-BLOCK markers are malformed."""
    return _parse_evolve_blocks(code)[1]


def has_evolve_blocks(code: str) -> bool:
    return bool(extract_evolve_blocks(code))


def apply_candidate_mutation(
    code: str,
    mutation_text: object,
    mutation_mode: str = "diff",
    *,
    allow_blank_payload: bool = False,
) -> tuple[str, str | None]:
    """Apply an LLM mutation response to a candidate program.

    `diff` mode applies SEARCH/REPLACE blocks. When EVOLVE-BLOCK markers are
    present, matches are restricted to marked regions so the skeleton is
    preserved.

    `full` mode replaces the whole candidate when no evolve blocks are present.
    With one evolve block, it replaces only that block's content. With multiple
    evolve blocks, the response must contain one or more named sections:

        <<<BLOCK block_0
        replacement code
        >>>BLOCK
    """
    content_error = _candidate_text_utf8_error(code)
    if content_error is not None:
        return code, content_error
    mutation_text, payload_error = _validate_mutation_payload(
        mutation_text, allow_blank=allow_blank_payload
    )
    if payload_error is not None:
        return code, payload_error
    marker_error = validate_evolve_blocks(code)
    if marker_error is not None:
        return code, f"malformed_evolve_blocks:{marker_error}"
    if mutation_mode == "diff":
        result, err = _apply_diff_to_candidate(code, mutation_text)
    elif mutation_mode == "full":
        result, err = _apply_full_replacement(code, mutation_text)
    else:
        return code, "unknown_mutation_mode"
    if err is None and _candidate_text_utf8_error(result) is not None:
        return code, "non_utf8_content"
    return result, err


def apply_workspace_mutation(
    workspace: CandidateWorkspace, mutation_text: object, mutation_mode: str = "diff"
) -> tuple[CandidateWorkspace, str | None]:
    """Apply a mutation to one or more files in a workspace candidate.

    Without `<<<FILE path ... >>>FILE` sections, mutation applies to the primary
    file for backward compatibility. With file sections, each section is routed
    to that file; unknown files can be created by `full` mode. File-section
    headers can also request topology operations:

        <<<FILE DELETE path/to/file.py
        >>>FILE

        <<<FILE MOVE old.py -> new.py
        >>>FILE

        <<<FILE PRIMARY path/to/main.py
        >>>FILE

        <<<FILE STATIC fixture.bin
        base64-encoded bytes for a generated static member, or replacement
        bytes for an existing llm_editable static member
        >>>FILE

        <<<FILE PATH DELETE helper.py
        replacement for a literal file named "DELETE helper.py"
        >>>FILE
    """

    mutation_text, payload_error = _validate_mutation_payload(mutation_text)
    if payload_error is not None:
        return workspace, payload_error
    marker_error = validate_workspace_unsupported_evolve_markers(workspace.files)
    if marker_error is not None:
        return workspace, marker_error
    normalized_text = _strip_fences(mutation_text.replace("\r\n", "\n"))
    envelope_error = _validate_section_envelopes(
        normalized_text, "<<<FILE", ">>>FILE", "file"
    )
    if envelope_error is not None:
        return workspace, envelope_error
    consumed_error = _validate_consumed_section_text(
        normalized_text, _FILE_SECTION_PATTERN, "file"
    )
    if consumed_error is not None:
        return workspace, consumed_error
    sections = _parse_file_sections(normalized_text)
    if not sections:
        code, err = apply_candidate_mutation(
            workspace.code, mutation_text, mutation_mode=mutation_mode
        )
        if err is not None:
            return workspace, err
        files = dict(workspace.files)
        files[workspace.primary_file] = code
        marker_error = validate_workspace_evolve_blocks(files)
        if marker_error is not None:
            return workspace, marker_error
        return CandidateWorkspace(
            files,
            workspace.primary_file,
            allowed_reserved_paths=workspace.allowed_reserved_paths,
            static_files=workspace.static_files,
        ), None

    parsed_sections: list[tuple[dict, str]] = []
    for header, body in sections:
        spec, err = _parse_file_section_header(
            header,
            allowed_reserved_paths=workspace.allowed_reserved_paths,
        )
        if err is not None:
            return workspace, err
        parsed_sections.append((spec, body))
    section_conflict = _find_section_path_conflict(parsed_sections)
    if section_conflict is not None:
        return workspace, section_conflict
    command_body_error = _validate_topology_command_bodies(parsed_sections)
    if command_body_error is not None:
        return workspace, command_body_error
    static_files = [dict(item) for item in workspace.static_files]
    static_mutation_error = _validate_static_member_mutation_policy(
        parsed_sections,
        tuple(static_files),
    )
    if static_mutation_error is not None:
        return workspace, static_mutation_error

    files = dict(workspace.files)
    static_by_path = {str(item["path"]): index for index, item in enumerate(static_files)}
    primary_file: str | None = workspace.primary_file
    explicit_primary = _explicit_primary_target(parsed_sections)
    changed = False
    for spec, body in parsed_sections:
        op = spec["op"]
        rel_path = spec["path"]
        if op == "static":
            if rel_path in files:
                return workspace, f"{rel_path}:target_exists"
            static_index = static_by_path.get(rel_path)
            payload = body.strip()
            if not payload:
                return workspace, f"{rel_path}:blank_static_content"
            try:
                raw_static = _decode_static_file_content(
                    payload,
                    label=f"{rel_path}:content_b64",
                )
            except ValueError as exc:
                return workspace, str(exc)
            if len(raw_static) > DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES:
                return (
                    workspace,
                    f"{rel_path}:content_b64 exceeds "
                    f"{DEFAULT_MAX_CANDIDATE_STATIC_FILE_BYTES} decoded bytes",
                )
            if static_index is None:
                current_static = {
                    "path": rel_path,
                    "kind": spec.get("kind", "static"),
                    "mutation_policy": "llm_editable",
                }
            else:
                current_static = static_files[static_index]
            new_static = {
                key: value
                for key, value in current_static.items()
                if key not in {"source_path", "content_b64"}
            }
            new_static.update(
                {
                    "sha256": hashlib.sha256(raw_static).hexdigest(),
                    "bytes": len(raw_static),
                    "source_kind": "generated_artifact",
                    "content_b64": payload,
                }
            )
            if new_static != current_static:
                if static_index is None:
                    static_by_path[rel_path] = len(static_files)
                    static_files.append(new_static)
                else:
                    static_files[static_index] = new_static
                changed = True
            continue

        if op == "delete":
            if rel_path not in files:
                return workspace, f"{rel_path}:missing_source"
            if len(files) == 1:
                return workspace, f"{rel_path}:cannot_delete_last_file"
            del files[rel_path]
            if primary_file == rel_path:
                primary_file = None
            changed = True
            continue

        if op == "move":
            target_path = spec["target"]
            if rel_path not in files:
                return workspace, f"{rel_path}:missing_source"
            if target_path in files:
                return workspace, f"{target_path}:target_exists"
            files[target_path] = files.pop(rel_path)
            if primary_file == rel_path:
                primary_file = target_path
            changed = True
            continue

        if op == "primary":
            continue

        file_exists = rel_path in files
        current = files.get(rel_path, "")
        if mutation_mode == "full" and not file_exists:
            new_code, err = body, None
        else:
            new_code, err = apply_candidate_mutation(
                current, body, mutation_mode, allow_blank_payload=True
            )
        if err is not None:
            return workspace, f"{rel_path}:{err}"
        if _candidate_text_utf8_error(new_code) is not None:
            return workspace, f"{rel_path}:non_utf8_content"
        if not file_exists or new_code != current:
            files[rel_path] = new_code
            changed = True
    if explicit_primary is not None:
        if explicit_primary not in files:
            return workspace, f"{explicit_primary}:missing_primary"
        if primary_file != explicit_primary:
            primary_file = explicit_primary
            changed = True
    elif primary_file is None:
        return workspace, f"{workspace.primary_file}:primary_deleted_requires_primary"
    if not changed:
        return workspace, "no_valid_changes"
    host_collision = _workspace_host_path_collision(files, tuple(static_files))
    if host_collision is not None:
        _existing, colliding = host_collision
        return workspace, f"{colliding}:host_path_collision"
    marker_error = validate_workspace_evolve_blocks(files)
    if marker_error is not None:
        return workspace, marker_error
    try:
        return CandidateWorkspace(
            files,
            primary_file,
            allowed_reserved_paths=workspace.allowed_reserved_paths,
            static_files=tuple(static_files),
        ), None
    except ValueError as exc:
        return workspace, f"candidate_workspace_error:{exc}"


def _validate_static_member_mutation_policy(
    sections: list[tuple[dict, str]],
    static_files: tuple[dict[str, str | int], ...],
) -> str | None:
    if not static_files:
        return None
    static_paths = {str(item["path"]): item for item in static_files}
    for spec, _body in sections:
        op = spec["op"]
        path = spec["path"]
        if path in static_paths:
            policy = static_paths[path].get("mutation_policy", "immutable")
            if policy != "llm_editable":
                return f"{path}:static_member_{policy}"
            if op == "static":
                continue
            return f"{path}:static_member_llm_editing_not_supported"
        if op == "move":
            target = spec["target"]
            if target in static_paths:
                policy = static_paths[target].get("mutation_policy", "immutable")
                if policy != "llm_editable":
                    return f"{target}:static_member_{policy}"
                return f"{target}:static_member_llm_editing_not_supported"
    return None


def _workspace_host_path_collision(
    files: Mapping[str, str],
    static_files: tuple[dict[str, str | int], ...],
) -> tuple[str, str] | None:
    """Detect collisions under the cross-platform materialization policy."""
    paths = list(files)
    paths.extend(_materializable_static_file_paths(static_files))
    seen: dict[str, str] = {}
    for rel_path in paths:
        key = _candidate_path_collision_key(rel_path)
        existing = seen.get(key)
        if existing is not None and existing != rel_path:
            return existing, rel_path
        seen[key] = rel_path
    return None


def _candidate_path_collision_key(rel_path: str) -> str:
    """Return a deterministic key for filesystem-compatible path collisions."""
    return unicodedata.normalize("NFC", rel_path).casefold()


def _materializable_static_file_paths(
    static_files: tuple[dict[str, str | int], ...],
) -> list[str]:
    return [
        str(item["path"])
        for item in static_files
        if isinstance(item.get("content_b64"), str)
        or isinstance(item.get("source_copy_path"), str)
    ]


def validate_workspace_evolve_blocks(files: Mapping[str, str]) -> str | None:
    for rel_path in sorted(files):
        marker_error = _unsupported_evolve_marker_error(rel_path, files[rel_path])
        if marker_error is not None:
            return f"{rel_path}:{marker_error}"
        marker_error = validate_evolve_blocks(files[rel_path])
        if marker_error is not None:
            return f"{rel_path}:malformed_evolve_blocks:{marker_error}"
    return None


def validate_workspace_unsupported_evolve_markers(
    files: Mapping[str, str],
) -> str | None:
    for rel_path in sorted(files):
        marker_error = _unsupported_evolve_marker_error(rel_path, files[rel_path])
        if marker_error is not None:
            return f"{rel_path}:{marker_error}"
    return None


def _unsupported_evolve_marker_error(rel_path: str, content: str) -> str | None:
    if _supports_python_evolve_markers(rel_path):
        return None
    for line in content.splitlines():
        stripped = line.strip()
        if _non_python_marker_line(stripped):
            return "unsupported_evolve_block_marker_syntax"
    return None


def _supports_python_evolve_markers(rel_path: str) -> bool:
    return Path(rel_path).suffix.lower() == ".py"


def _non_python_marker_line(stripped: str) -> bool:
    if stripped.startswith(("EVOLVE-BLOCK-START", "EVOLVE-BLOCK-END")):
        return True
    for prefix in _NON_PYTHON_EVOLVE_MARKER_PREFIXES:
        if not stripped.startswith(prefix):
            continue
        marker = stripped[len(prefix) :].lstrip()
        if marker.startswith(("EVOLVE-BLOCK-START", "EVOLVE-BLOCK-END")):
            return True
    return False


def _parse_file_sections(mutation_text: str) -> list[tuple[str, str]]:
    text = _strip_fences(mutation_text.replace("\r\n", "\n"))
    return [(name.strip(), body) for name, body in _FILE_SECTION_PATTERN.findall(text)]


def _parse_file_section_header(
    header: str,
    *,
    allowed_reserved_paths: frozenset[str] = frozenset(),
) -> tuple[dict, str | None]:
    raw = header.strip()
    if not raw:
        return {}, "empty_path:unsafe_path"

    command, _, remainder = raw.partition(" ")
    command_upper = command.upper()
    if command_upper == "PATH":
        if not remainder.strip():
            return {}, "empty_path:unsafe_path"
        try:
            return {
                "op": "edit",
                "path": normalize_candidate_path(
                    remainder,
                    allowed_reserved_paths=allowed_reserved_paths,
                ),
            }, None
        except ValueError as exc:
            return {}, _file_section_unsafe_path_error(remainder.strip(), exc)
    if command_upper == "DELETE":
        return _parse_single_path_op(
            "delete",
            remainder,
            allowed_reserved_paths=allowed_reserved_paths,
        )
    if command_upper in {"MOVE", "RENAME"}:
        return _parse_move_op(remainder, allowed_reserved_paths=allowed_reserved_paths)
    if command_upper == "PRIMARY":
        return _parse_single_path_op(
            "primary",
            remainder,
            allowed_reserved_paths=allowed_reserved_paths,
        )
    if command_upper in {"STATIC", "BINARY"}:
        spec, err = _parse_single_path_op(
            "static",
            remainder,
            allowed_reserved_paths=allowed_reserved_paths,
        )
        if err is None:
            spec["kind"] = "binary" if command_upper == "BINARY" else "static"
        return spec, err
    try:
        return {
            "op": "edit",
            "path": normalize_candidate_path(
                raw,
                allowed_reserved_paths=allowed_reserved_paths,
            ),
        }, None
    except ValueError as exc:
        return {}, _file_section_unsafe_path_error(raw, exc)


def _find_section_path_conflict(sections: list[tuple[dict, str]]) -> str | None:
    edit_seen: set[str] = set()
    topology_sources: set[str] = set()
    move_targets: set[str] = set()
    edit_paths: set[str] = set()
    primary_count = 0
    for spec, _ in sections:
        op = spec.get("op")
        path = spec["path"]
        if op == "primary":
            primary_count += 1
            if primary_count > 1:
                return "primary:duplicate_primary_section"
            continue
        if op in {"edit", "static"}:
            if path in edit_seen:
                return f"{path}:duplicate_file_section"
            edit_seen.add(path)
            edit_paths.add(path)
        else:
            if path in topology_sources:
                return f"{path}:duplicate_topology_section"
            topology_sources.add(path)
            if op == "move":
                target = spec["target"]
                if target in move_targets:
                    return f"{target}:duplicate_move_target"
                move_targets.add(target)
    conflicting_edits = sorted(edit_paths & (topology_sources | move_targets))
    if conflicting_edits:
        return f"{conflicting_edits[0]}:conflicting_file_operations"
    chained_topology = sorted(move_targets & topology_sources)
    if chained_topology:
        return f"{chained_topology[0]}:conflicting_file_operations"
    return None


def _validate_topology_command_bodies(sections: list[tuple[dict, str]]) -> str | None:
    for spec, body in sections:
        if spec.get("op") in {"delete", "move", "primary"} and body.strip():
            return f"{spec['path']}:unexpected_command_body"
    return None


def _explicit_primary_target(sections: list[tuple[dict, str]]) -> str | None:
    for spec, _ in sections:
        if spec.get("op") == "primary":
            return spec["path"]
    return None


def _parse_single_path_op(
    op: str,
    raw_path: str,
    *,
    allowed_reserved_paths: frozenset[str] = frozenset(),
) -> tuple[dict, str | None]:
    raw_path = raw_path.strip()
    if not raw_path:
        return {}, f"{op}:empty_path"
    try:
        return {
            "op": op,
            "path": normalize_candidate_path(
                raw_path,
                allowed_reserved_paths=allowed_reserved_paths,
            ),
        }, None
    except ValueError as exc:
        return {}, _file_section_unsafe_path_error(raw_path, exc)


def _parse_move_op(
    remainder: str,
    *,
    allowed_reserved_paths: frozenset[str] = frozenset(),
) -> tuple[dict, str | None]:
    source, sep, target = remainder.partition("->")
    if not sep:
        return {}, "move:missing_target"
    source = source.strip()
    target = target.strip()
    if not source:
        return {}, "move:empty_source"
    if not target:
        return {}, "move:empty_target"
    try:
        source_path = normalize_candidate_path(
            source,
            allowed_reserved_paths=allowed_reserved_paths,
        )
        target_path = normalize_candidate_path(
            target,
            allowed_reserved_paths=allowed_reserved_paths,
        )
    except ValueError as exc:
        bad_path = source if "source_path" not in locals() else target
        return {}, _file_section_unsafe_path_error(bad_path, exc)
    if source_path == target_path:
        return {}, f"{source_path}:no_valid_changes"
    return {"op": "move", "path": source_path, "target": target_path}, None


def _file_section_unsafe_path_error(path: str, exc: ValueError) -> str:
    if "secret-like text" in str(exc):
        return "secret_like_path:unsafe_path"
    return f"{path}:unsafe_path"


def _validate_section_envelopes(
    text: str, start_marker: str, end_marker: str, label: str
) -> str | None:
    same_line_error = _same_line_section_envelope_error(
        text, start_marker, end_marker, label
    )
    if same_line_error is not None:
        return same_line_error
    open_section = False
    matches = sorted(
        [(start, "start") for start in _line_marker_starts(text, start_marker)]
        + [(start, "end") for start in _line_marker_starts(text, end_marker)]
    )
    for _, kind in matches:
        if kind == "start":
            if open_section:
                return f"malformed_{label}_sections:nested_start"
            open_section = True
        else:
            if not open_section:
                return f"malformed_{label}_sections:orphan_end"
            open_section = False
    if open_section:
        return f"malformed_{label}_sections:missing_end"
    return None


def _validate_consumed_section_text(
    text: str, pattern: re.Pattern, label: str
) -> str | None:
    matches = list(pattern.finditer(text))
    if not matches:
        return None
    outside: list[str] = []
    cursor = 0
    for match in matches:
        outside.append(text[cursor:match.start()])
        cursor = match.end()
    outside.append(text[cursor:])
    leading = strip_allowed_leading_preamble(outside[0])
    remainder = leading + "".join(strip_proposal_metadata(segment) for segment in outside[1:])
    if remainder.strip():
        return f"malformed_{label}_sections:unconsumed_text"
    return None


def _same_line_section_envelope_error(
    text: str, start_marker: str, end_marker: str, label: str
) -> str | None:
    for start in _line_marker_starts(text, start_marker):
        line_end = text.find("\n", start + len(start_marker))
        search_end = len(text) if line_end == -1 else line_end
        if text.find(end_marker, start + len(start_marker), search_end) != -1:
            return f"malformed_{label}_sections:same_line"
    return None


def _line_marker_starts(text: str, marker: str) -> list[int]:
    pattern = re.compile(rf"(?m)^{re.escape(marker)}(?=$|[ \t\n])")
    return [match.start() for match in pattern.finditer(text)]


def _validate_block_name(name: str) -> str | None:
    if any(unicodedata.category(char) == "Cf" for char in name):
        return "unsafe_name"
    if redact_sensitive_text(name) != name:
        return "unsafe_name"
    if not _BLOCK_NAME_PATTERN.fullmatch(name):
        return "invalid_name"
    return None


def _parse_evolve_blocks(code: str) -> tuple[list[EvolveBlock], str | None]:
    blocks: list[EvolveBlock] = []
    seen_names: set[str] = set()
    open_block: tuple[str, int, int] | None = None
    idx = 0
    lines = code.splitlines(keepends=True)
    markers, tokenizer_failed = _evolve_marker_comments(code, lines)
    if tokenizer_failed and _has_raw_evolve_marker_lines(lines):
        return blocks, "tokenize_error"
    for marker in markers:
        stripped = marker.text.strip()
        if stripped == EVOLVE_BLOCK_START or (
            stripped.startswith(EVOLVE_BLOCK_START)
            and stripped[len(EVOLVE_BLOCK_START)] in {" ", "\t"}
        ):
            if open_block is not None:
                return blocks, "nested_start"
            raw_name = stripped[len(EVOLVE_BLOCK_START):].strip()
            name = raw_name or f"block_{idx}"
            name_error = _validate_block_name(name)
            if name_error is not None:
                return blocks, name_error
            if name in seen_names:
                return blocks, "duplicate_name"
            content_start = marker.line_end
            open_block = (name, marker.line_start, content_start)
        elif stripped.startswith(EVOLVE_BLOCK_START):
            return blocks, "invalid_start_marker"
        elif stripped.startswith(EVOLVE_BLOCK_END):
            if stripped != EVOLVE_BLOCK_END:
                return blocks, "invalid_end_marker"
            if open_block is None:
                return blocks, "orphan_end"
            name, start, content_start = open_block
            content_end = marker.line_start
            if content_end > content_start and code[content_end - 1] == "\n":
                content_end -= 1
            end = marker.line_end
            blocks.append(
                EvolveBlock(
                    name=name,
                    start=start,
                    content_start=content_start,
                    content_end=content_end,
                    end=end,
                    content=code[content_start:content_end],
                )
            )
            seen_names.add(name)
            idx += 1
            open_block = None
    if open_block is not None:
        return blocks, "missing_end"
    return blocks, None


def _evolve_marker_comments(code: str, lines: list[str]) -> tuple[list[_EvolveMarker], bool]:
    line_offsets: list[int] = []
    offset = 0
    for line in lines:
        line_offsets.append(offset)
        offset += len(line)

    markers: list[_EvolveMarker] = []
    tokenizer_failed = False
    try:
        tokens = tokenize.generate_tokens(io.StringIO(code).readline)
        for token in tokens:
            if token.type != tokenize.COMMENT:
                continue
            row, col = token.start
            if row < 1 or row > len(lines):
                continue
            if lines[row - 1][:col].strip():
                continue
            text = token.string.strip()
            if not (
                text.startswith(EVOLVE_BLOCK_START)
                or text.startswith(EVOLVE_BLOCK_END)
            ):
                continue
            line_start = line_offsets[row - 1]
            markers.append(
                _EvolveMarker(
                    text=text,
                    line_start=line_start,
                    line_end=line_start + len(lines[row - 1]),
                )
            )
    except (IndentationError, tokenize.TokenError):
        tokenizer_failed = True
    return markers, tokenizer_failed


def _has_raw_evolve_marker_lines(lines: list[str]) -> bool:
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(EVOLVE_BLOCK_START) or stripped.startswith(EVOLVE_BLOCK_END):
            return True
    return False


def _apply_diff_to_candidate(code: str, diff_text: str) -> tuple[str, str | None]:
    blocks = extract_evolve_blocks(code)
    if not blocks:
        return apply_diff(code, diff_text)

    diff_blocks = _parse_diff_blocks(diff_text)
    if not diff_blocks:
        return code, "no_diff_blocks"
    result = code
    for search, replace in diff_blocks:
        if not search.strip():
            return code, "search_not_found"
        matches: list[EvolveBlock] = []
        for block in extract_evolve_blocks(result):
            count = _line_ending_tolerant_matches(block.content, search)
            if count > 1:
                return code, "ambiguous_search_match"
            if count == 1:
                matches.append(block)
        if not matches:
            return code, "search_not_found"
        if len(matches) > 1:
            return code, "ambiguous_search_match"
        block = matches[0]
        for current_block in extract_evolve_blocks(result):
            if current_block.name == block.name:
                block = current_block
                new_content = _replace_line_ending_tolerant(
                    block.content, search, replace
                )
                result = (
                    result[: block.content_start]
                    + new_content
                    + result[block.content_end :]
                )
                break
    if result == code:
        return code, "no_valid_changes"
    return result, None


def _parse_diff_blocks(diff_text: str) -> list[tuple[str, str]]:
    return parse_diff_blocks(diff_text)


def _validate_mutation_payload(
    mutation_text: object, *, allow_blank: bool = False
) -> tuple[str, str | None]:
    if not isinstance(mutation_text, str):
        return "", "non_text_mutation_payload"
    if len(mutation_text) > DEFAULT_MAX_MUTATION_PAYLOAD_CHARS:
        return "", "oversized_mutation_payload"
    normalized = _strip_fences(mutation_text.replace("\r\n", "\n"))
    if not allow_blank and not normalized.strip():
        return "", "blank_mutation_payload"
    return mutation_text, None


def _apply_full_replacement(code: str, mutation_text: str) -> tuple[str, str | None]:
    replacement = _strip_fences(mutation_text.replace("\r\n", "\n"))
    same_line_block_error = _same_line_section_envelope_error(
        replacement, "<<<BLOCK", ">>>BLOCK", "block"
    )
    if same_line_block_error is not None:
        return code, same_line_block_error
    blocks = extract_evolve_blocks(code)
    if not blocks:
        return (replacement, None) if replacement != code else (code, "no_valid_changes")
    has_block_sections = bool(
        _line_marker_starts(replacement, "<<<BLOCK")
        or _line_marker_starts(replacement, ">>>BLOCK")
    )
    if has_block_sections:
        return _apply_named_block_replacement(code, blocks, replacement)
    if len(blocks) == 1:
        block = blocks[0]
        if replacement == block.content:
            return code, "no_valid_changes"
        return code[: block.content_start] + replacement + code[block.content_end :], None

    return code, "missing_block_sections"


def _apply_named_block_replacement(
    code: str, blocks: list[EvolveBlock], replacement: str
) -> tuple[str, str | None]:

    envelope_error = _validate_section_envelopes(
        replacement, "<<<BLOCK", ">>>BLOCK", "block"
    )
    if envelope_error is not None:
        return code, envelope_error
    consumed_error = _validate_consumed_section_text(
        replacement, _BLOCK_SECTION_PATTERN, "block"
    )
    if consumed_error is not None:
        return code, consumed_error
    sections: dict[str, str] = {}
    for raw_name, body in _BLOCK_SECTION_PATTERN.findall(replacement):
        name = raw_name.strip()
        if not name:
            return code, "malformed_block_sections:empty_name"
        name_error = _validate_block_name(name)
        if name_error is not None:
            return code, f"malformed_block_sections:{name_error}"
        if name in sections:
            return code, "malformed_block_sections:duplicate_name"
        sections[name] = body
    if not sections:
        return code, "missing_block_sections"
    known_names = {block.name for block in blocks}
    if any(name not in known_names for name in sections):
        return code, "malformed_block_sections:unknown_name"
    result = code
    for block in reversed(blocks):
        if block.name not in sections:
            continue
        result = result[: block.content_start] + sections[block.name] + result[block.content_end :]
    if result == code:
        return code, "no_valid_changes"
    return result, None
