"""Problem-local context ingestion and normalized source records.

This module is intentionally independent from the evolution runtime.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
from pathlib import Path
import re
import unicodedata

import yaml

from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.core.yaml_utils import redacted_yaml_error, safe_load_unique

_CONTEXT_EXTENSIONS = {".txt", ".md", ".py", ".pdf"}
_MAX_CONTEXT_CHARS = 6000
_MAX_CONTEXT_SOURCE_BYTES = 1_000_000
_MAX_CONTEXT_TOTAL_BYTES = 10_000_000
_MAX_CONTEXT_PDF_PAGES = 100
_MAX_CONTEXT_PDF_CHARS = 500_000
_MAX_CONTEXT_ENTRIES = 1_000
_MAX_CONTEXT_DEPTH = 8
_MAX_CONTEXT_SKIPPED_DIAGNOSTICS = 500
_MAX_CONTEXT_PROVENANCE_CHARS = 200_000
_CONTEXT_MANIFEST_NAMES = ("context.yaml", "context.yml")
_CONTEXT_EXPLICIT_FAILURE_POLICIES = {"error", "warn"}
_CONTEXT_EXCERPT_POLICIES = {"head", "head_tail", "term_ranked"}
_CONTEXT_SOURCE_SELECTION_POLICIES = {"path_order", "term_ranked"}
_CONTEXT_SOURCE_ROLES = {
    "human_instruction",
    "equation",
    "code_snippet",
    "literature_pdf",
    "background_reference",
}


def _is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (is_junction is not None and is_junction())


def load_context_files(
    problem_dir: Path,
    *,
    task_description: str = "",
) -> tuple[dict[str, str], list[dict], dict]:
    context_dir = problem_dir / "context"
    if _is_link(context_dir):
        raise ValueError(f"Context links are not supported: {context_dir}")
    if not context_dir.is_dir():
        return {}, [], _context_policy(False)
    manifest = _load_context_manifest(context_dir)
    max_chars = manifest["max_chars_per_source"]
    excerpt_policy = manifest["excerpt_policy"]
    max_pdf_pages = manifest["max_pdf_pages"]
    max_pdf_chars = manifest["max_pdf_chars"]
    result: dict[str, str] = {}
    sources: list[dict] = []
    loaded_context_records: list[dict] = []
    selected, skipped, include_patterns = _select_context_paths(context_dir, manifest)
    display_paths: dict[str, str] = {}
    explicit_context_failures: list[dict] = []
    for path in selected:
        raw_rel = path.relative_to(context_dir).as_posix()
        rel = _context_display_path(raw_rel)
        previous = display_paths.get(rel)
        if previous is not None:
            raise ValueError(
                f"{context_dir}: duplicate context source path after Unicode "
                f"normalization: {previous!r} and {raw_rel!r} -> {rel!r}"
            )
        display_paths[rel] = raw_rel
        rendered, metadata = _read_context_source(
            path,
            rel,
            max_chars,
            excerpt_policy=excerpt_policy,
            query_text=task_description,
            raw_rel_path=raw_rel,
            max_pdf_pages=max_pdf_pages,
            max_pdf_chars=max_pdf_chars,
        )
        role_metadata = manifest["source_roles"].get(rel)
        if role_metadata is not None:
            metadata["source_role"] = dict(role_metadata)
            metadata["source_role_status"] = "classified"
        else:
            metadata["source_role"] = None
            metadata["source_role_status"] = "unclassified"
        if metadata.get("extraction_status") != "ok":
            diagnostic = _context_extraction_diagnostic(metadata)
            matched_include_patterns = _matched_context_include_patterns(
                rel,
                manifest["include"],
            )
            if matched_include_patterns:
                diagnostic["explicit_include"] = True
                diagnostic["matched_include_patterns"] = matched_include_patterns
                explicit_context_failures.append(
                    _explicit_context_failure_record(
                        diagnostic,
                        matched_include_patterns,
                    )
                )
            skipped.append(diagnostic)
            continue
        loaded_context_records.append({
            "path": rel,
            "rendered": rendered,
            "metadata": metadata,
        })
    retained_context_records, source_selection = _select_context_source_records(
        loaded_context_records,
        manifest,
        query_text=task_description,
    )
    for record in retained_context_records:
        rel = record["path"]
        result[rel] = record["rendered"]
        sources.append(record["metadata"])
    policy = _context_policy(
        True,
        manifest=manifest["manifest"],
        include=manifest["include"],
        exclude=manifest["exclude"],
        max_chars_per_source=max_chars,
        excerpt_policy=excerpt_policy,
        max_bytes_per_source=manifest["max_bytes_per_source"],
        max_total_bytes=manifest["max_total_bytes"],
        max_pdf_pages=max_pdf_pages,
        max_pdf_chars=max_pdf_chars,
        max_context_entries=manifest["max_context_entries"],
        max_context_depth=manifest["max_context_depth"],
        max_skipped_diagnostics=manifest["max_skipped_diagnostics"],
        max_context_provenance_chars=manifest["max_context_provenance_chars"],
        source_selection_policy=manifest["source_selection_policy"],
        max_selected_context_sources=manifest["max_selected_context_sources"],
        source_selection=source_selection,
        selected_count=len(sources),
        skipped=skipped,
        include_patterns=include_patterns,
        on_explicit_context_failure=manifest["on_explicit_context_failure"],
        explicit_context_failures=explicit_context_failures,
        source_roles=manifest["source_roles"],
    )
    if (
        explicit_context_failures
        and manifest["on_explicit_context_failure"] == "error"
    ):
        _raise_explicit_context_failure(context_dir, explicit_context_failures)
    return result, sources, policy


def _load_context_manifest(context_dir: Path) -> dict:
    raw: dict = {}
    for name in _CONTEXT_MANIFEST_NAMES:
        path = context_dir / name
        if _is_link(path):
            raise ValueError(f"Context links are not supported: {path}")
        if path.exists() and not path.is_file():
            raise ValueError(f"{path}: context manifest must be a regular file")
    manifest_paths = [
        context_dir / name
        for name in _CONTEXT_MANIFEST_NAMES
        if (context_dir / name).exists()
    ]
    if len(manifest_paths) > 1:
        names = ", ".join(path.name for path in manifest_paths)
        raise ValueError(f"{context_dir}: use only one context manifest, found {names}")
    manifest_record = None
    for name in _CONTEXT_MANIFEST_NAMES:
        path = context_dir / name
        if path.exists():
            try:
                raw_bytes = path.read_bytes()
            except OSError as exc:
                raise ValueError(
                    f"{path}: context manifest could not be read: "
                    f"{redact_sensitive_text(str(exc))}"
                ) from exc
            manifest_record = {
                "path": path.relative_to(context_dir).as_posix(),
                "sha256": hashlib.sha256(raw_bytes).hexdigest(),
                "bytes": len(raw_bytes),
            }
            try:
                manifest_text = raw_bytes.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError(f"{path}: context manifest must be valid UTF-8") from exc
            try:
                loaded = safe_load_unique(manifest_text)
                if loaded is None and not manifest_text.strip():
                    loaded = {}
            except yaml.YAMLError as exc:
                raise ValueError(
                    f"{path}: invalid context manifest YAML: {redacted_yaml_error(exc)}"
                ) from exc
            if not isinstance(loaded, dict):
                raise ValueError(f"{path} must contain a mapping")
            raw = loaded
            break
    if not all(isinstance(key, str) for key in raw):
        raise ValueError(f"{context_dir}: context manifest keys must be strings")
    supported_fields = {
        "include",
        "exclude",
        "max_chars_per_source",
        "max_bytes_per_source",
        "max_total_bytes",
        "max_pdf_pages",
        "max_pdf_chars",
        "max_context_entries",
        "max_context_depth",
        "max_skipped_diagnostics",
        "max_context_provenance_chars",
        "on_explicit_context_failure",
        "excerpt_policy",
        "source_selection_policy",
        "max_selected_context_sources",
        "source_roles",
    }
    unsupported = sorted(set(raw) - supported_fields)
    if unsupported:
        raise ValueError(f"{context_dir}: unsupported context manifest fields {unsupported}")
    include = raw.get("include")
    exclude = raw.get("exclude", [])
    if include is not None and (
        not isinstance(include, list) or not all(isinstance(item, str) for item in include)
    ):
        raise ValueError(f"{context_dir}: context include must be a list of strings")
    if not isinstance(exclude, list) or not all(isinstance(item, str) for item in exclude):
        raise ValueError(f"{context_dir}: context exclude must be a list of strings")
    _validate_context_patterns(context_dir, "include", include or [])
    _validate_context_patterns(context_dir, "exclude", exclude)
    on_explicit_context_failure = raw.get("on_explicit_context_failure", "error")
    if on_explicit_context_failure not in _CONTEXT_EXPLICIT_FAILURE_POLICIES:
        raise ValueError(
            f"{context_dir}: on_explicit_context_failure must be one of "
            f"{sorted(_CONTEXT_EXPLICIT_FAILURE_POLICIES)}, got "
            f"{on_explicit_context_failure!r}"
        )
    max_chars = raw.get("max_chars_per_source", _MAX_CONTEXT_CHARS)
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or max_chars <= 0:
        raise ValueError(f"{context_dir}: max_chars_per_source must be a positive integer")
    excerpt_policy = raw.get("excerpt_policy", "head")
    if not isinstance(excerpt_policy, str) or excerpt_policy not in _CONTEXT_EXCERPT_POLICIES:
        raise ValueError(
            f"{context_dir}: excerpt_policy must be one of "
            f"{sorted(_CONTEXT_EXCERPT_POLICIES)}, got {excerpt_policy!r}"
        )
    source_selection_policy = raw.get("source_selection_policy", "path_order")
    if (
        not isinstance(source_selection_policy, str)
        or source_selection_policy not in _CONTEXT_SOURCE_SELECTION_POLICIES
    ):
        raise ValueError(
            f"{context_dir}: source_selection_policy must be one of "
            f"{sorted(_CONTEXT_SOURCE_SELECTION_POLICIES)}, got "
            f"{source_selection_policy!r}"
        )
    max_selected_context_sources = _optional_positive_context_int(
        context_dir,
        raw,
        "max_selected_context_sources",
    )
    max_bytes = _positive_context_int(
        context_dir,
        raw,
        "max_bytes_per_source",
        _MAX_CONTEXT_SOURCE_BYTES,
    )
    max_total_bytes = _positive_context_int(
        context_dir,
        raw,
        "max_total_bytes",
        _MAX_CONTEXT_TOTAL_BYTES,
    )
    max_pdf_pages = _positive_context_int(
        context_dir,
        raw,
        "max_pdf_pages",
        _MAX_CONTEXT_PDF_PAGES,
    )
    max_pdf_chars = _positive_context_int(
        context_dir,
        raw,
        "max_pdf_chars",
        _MAX_CONTEXT_PDF_CHARS,
    )
    max_context_entries = _positive_context_int(
        context_dir,
        raw,
        "max_context_entries",
        _MAX_CONTEXT_ENTRIES,
    )
    max_context_depth = _positive_context_int(
        context_dir,
        raw,
        "max_context_depth",
        _MAX_CONTEXT_DEPTH,
    )
    max_skipped_diagnostics = _positive_context_int(
        context_dir,
        raw,
        "max_skipped_diagnostics",
        _MAX_CONTEXT_SKIPPED_DIAGNOSTICS,
    )
    max_context_provenance_chars = _positive_context_int(
        context_dir,
        raw,
        "max_context_provenance_chars",
        _MAX_CONTEXT_PROVENANCE_CHARS,
    )
    source_roles = _validate_context_source_roles(
        context_dir,
        raw.get("source_roles", {}),
    )
    return {
        "manifest": manifest_record,
        "include": include,
        "exclude": exclude,
        "max_chars_per_source": max_chars,
        "excerpt_policy": excerpt_policy,
        "max_bytes_per_source": max_bytes,
        "max_total_bytes": max_total_bytes,
        "max_pdf_pages": max_pdf_pages,
        "max_pdf_chars": max_pdf_chars,
        "max_context_entries": max_context_entries,
        "max_context_depth": max_context_depth,
        "max_skipped_diagnostics": max_skipped_diagnostics,
        "max_context_provenance_chars": max_context_provenance_chars,
        "on_explicit_context_failure": on_explicit_context_failure,
        "source_selection_policy": source_selection_policy,
        "max_selected_context_sources": max_selected_context_sources,
        "source_roles": source_roles,
    }


def _positive_context_int(context_dir: Path, raw: dict, field: str, default: int) -> int:
    value = raw.get(field, default)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{context_dir}: {field} must be a positive integer")
    return value


def _optional_positive_context_int(
    context_dir: Path,
    raw: dict,
    field: str,
) -> int | None:
    value = raw.get(field)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{context_dir}: {field} must be a positive integer or null")
    return value


def _validate_context_source_roles(context_dir: Path, value: object) -> dict[str, dict]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{context_dir}: source_roles must be a mapping")
    normalized: dict[str, dict] = {}
    for raw_path, raw_metadata in value.items():
        if not isinstance(raw_path, str):
            raise ValueError(f"{context_dir}: source_roles keys must be strings")
        _validate_context_manifest_source_role_path(context_dir, raw_path)
        path = _context_display_path(raw_path)
        if path in normalized:
            raise ValueError(
                f"{context_dir}: duplicate source_roles path after Unicode "
                f"normalization: {raw_path!r}"
            )
        if not isinstance(raw_metadata, dict):
            raise ValueError(
                f"{context_dir}: source_roles[{raw_path!r}] must be a mapping"
            )
        if not all(isinstance(key, str) for key in raw_metadata):
            raise ValueError(
                f"{context_dir}: source_roles[{raw_path!r}] keys must be strings"
            )
        unsupported = sorted(
            set(raw_metadata)
            - {"role", "topic", "section", "page", "pages", "span", "notes"}
        )
        if unsupported:
            raise ValueError(
                f"{context_dir}: source_roles[{raw_path!r}] has unsupported "
                f"fields {unsupported}"
            )
        role = raw_metadata.get("role")
        if not isinstance(role, str) or role not in _CONTEXT_SOURCE_ROLES:
            raise ValueError(
                f"{context_dir}: source_roles[{raw_path!r}].role must be one of "
                f"{sorted(_CONTEXT_SOURCE_ROLES)}"
            )
        topic = _validate_context_role_text(
            context_dir,
            raw_path,
            raw_metadata.get("topic"),
            "topic",
            required=True,
        )
        record = {
            "role": role,
            "topic": topic,
        }
        for field in ("section", "span", "notes"):
            if field in raw_metadata:
                record[field] = _validate_context_role_text(
                    context_dir,
                    raw_path,
                    raw_metadata[field],
                    field,
                    required=False,
                )
        if "page" in raw_metadata:
            page = raw_metadata["page"]
            if isinstance(page, bool) or not isinstance(page, int) or page <= 0:
                raise ValueError(
                    f"{context_dir}: source_roles[{raw_path!r}].page must be a "
                    "positive integer"
                )
            record["page"] = page
        if "pages" in raw_metadata:
            pages = raw_metadata["pages"]
            if (
                not isinstance(pages, list)
                or not pages
                or any(isinstance(page, bool) or not isinstance(page, int) or page <= 0 for page in pages)
            ):
                raise ValueError(
                    f"{context_dir}: source_roles[{raw_path!r}].pages must be a "
                    "non-empty list of positive integers"
                )
            record["pages"] = list(pages)
        if not any(field in record for field in ("section", "page", "pages", "span")):
            raise ValueError(
                f"{context_dir}: source_roles[{raw_path!r}] must include at "
                "least one source locator: section, page, pages, or span"
            )
        normalized[path] = record
    return normalized


def _validate_context_manifest_source_role_path(context_dir: Path, path: str) -> None:
    if _unsafe_context_pattern(path):
        raise ValueError(
            f"{context_dir}: source_roles path must be a safe problem-relative "
            f"context path: {path!r}"
        )
    if any(char in path for char in "*?[]"):
        raise ValueError(
            f"{context_dir}: source_roles path must name one context source, "
            f"not a glob pattern: {path!r}"
        )


def _validate_context_role_text(
    context_dir: Path,
    path: str,
    value: object,
    field: str,
    *,
    required: bool,
) -> str:
    if not isinstance(value, str) or not value.strip():
        qualifier = "a non-empty string" if required else "a non-empty string when provided"
        raise ValueError(
            f"{context_dir}: source_roles[{path!r}].{field} must be {qualifier}"
        )
    redacted = redact_sensitive_text(value.strip())
    if redacted != value.strip():
        raise ValueError(
            f"{context_dir}: source_roles[{path!r}].{field} must not look "
            "secret-like"
        )
    if len(redacted) > 500:
        raise ValueError(
            f"{context_dir}: source_roles[{path!r}].{field} must be at most "
            "500 characters"
        )
    if any(ord(char) < 32 or ord(char) == 127 or unicodedata.category(char) == "Cf" for char in redacted):
        raise ValueError(
            f"{context_dir}: source_roles[{path!r}].{field} must not contain "
            "unsafe control characters"
        )
    return redacted


def _validate_context_patterns(context_dir: Path, field: str, patterns: list[str]) -> None:
    for pattern in patterns:
        if _unsafe_context_pattern(pattern):
            raise ValueError(
                f"{context_dir}: context {field} pattern must be a safe "
                f"problem-relative glob: {pattern!r}"
            )


def _unsafe_context_pattern(pattern: str) -> bool:
    normalized = pattern.replace("\\", "/")
    if redact_sensitive_text(normalized) != normalized:
        return True
    if not pattern or pattern != normalized:
        return True
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
        return True
    if any(
        ord(char) < 32
        or ord(char) == 127
        or unicodedata.category(char) == "Cf"
        for char in normalized
    ):
        return True
    parts = [part for part in normalized.split("/") if part]
    return any(part == ".." for part in parts)


class _ContextSkippedDiagnostics:
    def __init__(self, max_records: int):
        self.max_records = max_records
        self.records: list[dict] = []
        self.total_count = 0
        self.omitted_count = 0
        self.reason_counts: dict[str, int] = {}
        self.omitted_reasons: dict[str, int] = {}

    def append(self, record: dict) -> None:
        reason = str(record.get("reason", "unknown"))
        self.total_count += 1
        self.reason_counts[reason] = self.reason_counts.get(reason, 0) + 1
        if len(self.records) < self.max_records:
            self.records.append(record)
            return
        self.omitted_count += 1
        self.omitted_reasons[reason] = self.omitted_reasons.get(reason, 0) + 1


def _select_context_paths(
    context_dir: Path, manifest: dict
) -> tuple[list[Path], "_ContextSkippedDiagnostics", list[dict]]:
    selected = []
    skipped = _ContextSkippedDiagnostics(int(manifest["max_skipped_diagnostics"]))
    include = manifest["include"]
    selected_bytes = 0
    max_bytes = int(manifest["max_bytes_per_source"])
    max_total_bytes = int(manifest["max_total_bytes"])
    include_match_counts = [0 for _ in include] if include is not None else []
    include_selected_counts = [0 for _ in include] if include is not None else []
    for path in _iter_context_entries(
        context_dir,
        max_entries=int(manifest["max_context_entries"]),
        max_depth=int(manifest["max_context_depth"]),
        skipped=skipped,
    ):
        if path.name in _CONTEXT_MANIFEST_NAMES:
            continue
        try:
            is_file = path.is_file()
        except OSError as exc:
            skipped.append(_context_stat_error_diagnostic(path, context_dir, exc))
            continue
        if not is_file:
            continue
        rel = path.relative_to(context_dir).as_posix()
        if path.suffix.lower() not in _CONTEXT_EXTENSIONS:
            skipped.append(
                _context_file_diagnostic(
                    path,
                    context_dir,
                    "unsupported_extension",
                    max_bytes=max_bytes,
                )
            )
            continue
        matched_include_indexes: list[int] = []
        if include is not None:
            matched_include_indexes = [
                index for index, pattern in enumerate(include) if _matches(rel, pattern)
            ]
            for index in matched_include_indexes:
                include_match_counts[index] += 1
            if not matched_include_indexes:
                skipped.append(
                    _context_file_diagnostic(
                        path,
                        context_dir,
                        "not_included",
                        max_bytes=max_bytes,
                    )
                )
                continue
        if _is_hidden_context_path(rel) and not _hidden_context_explicitly_included(
            include, matched_include_indexes
        ):
            skipped.append(
                _context_file_diagnostic(
                    path,
                    context_dir,
                    "hidden_not_included",
                    max_bytes=max_bytes,
                )
            )
            continue
        if _matches_any(rel, manifest["exclude"]):
            skipped.append(
                _context_file_diagnostic(
                    path,
                    context_dir,
                    "excluded",
                    max_bytes=max_bytes,
                )
            )
            continue
        try:
            size = path.stat().st_size
        except OSError as exc:
            skipped.append(_context_stat_error_diagnostic(path, context_dir, exc))
            continue
        if size > max_bytes:
            skipped.append(
                _context_resource_diagnostic(
                    path,
                    context_dir,
                    "max_source_bytes",
                    max_bytes=max_bytes,
                    bytes_value=size,
                )
            )
            continue
        if selected_bytes + size > max_total_bytes:
            skipped.append(
                _context_resource_diagnostic(
                    path,
                    context_dir,
                    "max_total_bytes",
                    max_bytes=max_total_bytes,
                    bytes_value=size,
                    total_before=selected_bytes,
                )
            )
            continue
        selected_bytes += size
        for index in matched_include_indexes:
            include_selected_counts[index] += 1
        selected.append(path)
    include_patterns = _context_include_pattern_records(
        include,
        include_match_counts,
        include_selected_counts,
    )
    return selected, skipped, include_patterns


def _context_policy(
    present: bool,
    *,
    manifest: dict | None = None,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    max_chars_per_source: int = _MAX_CONTEXT_CHARS,
    excerpt_policy: str = "head",
    max_bytes_per_source: int = _MAX_CONTEXT_SOURCE_BYTES,
    max_total_bytes: int = _MAX_CONTEXT_TOTAL_BYTES,
    max_pdf_pages: int = _MAX_CONTEXT_PDF_PAGES,
    max_pdf_chars: int = _MAX_CONTEXT_PDF_CHARS,
    max_context_entries: int = _MAX_CONTEXT_ENTRIES,
    max_context_depth: int = _MAX_CONTEXT_DEPTH,
    max_skipped_diagnostics: int = _MAX_CONTEXT_SKIPPED_DIAGNOSTICS,
    max_context_provenance_chars: int = _MAX_CONTEXT_PROVENANCE_CHARS,
    source_selection_policy: str = "path_order",
    max_selected_context_sources: int | None = None,
    source_selection: dict | None = None,
    selected_count: int = 0,
    skipped: _ContextSkippedDiagnostics | None = None,
    include_patterns: list[dict] | None = None,
    on_explicit_context_failure: str = "error",
    explicit_context_failures: list[dict] | None = None,
    source_roles: dict[str, dict] | None = None,
) -> dict:
    skipped = skipped or _ContextSkippedDiagnostics(max_skipped_diagnostics)
    include_patterns = include_patterns or []
    explicit_context_failures = explicit_context_failures or []
    source_roles = source_roles or {}
    policy = {
        "present": present,
        "supported_extensions": sorted(_CONTEXT_EXTENSIONS),
        "manifest": manifest,
        "include": include,
        "exclude": exclude or [],
        "max_chars_per_source": max_chars_per_source,
        "excerpt_policy": excerpt_policy,
        "max_bytes_per_source": max_bytes_per_source,
        "max_total_bytes": max_total_bytes,
        "max_pdf_pages": max_pdf_pages,
        "max_pdf_chars": max_pdf_chars,
        "max_context_entries": max_context_entries,
        "max_context_depth": max_context_depth,
        "max_skipped_diagnostics": max_skipped_diagnostics,
        "max_context_provenance_chars": max_context_provenance_chars,
        "source_selection_policy": source_selection_policy,
        "max_selected_context_sources": max_selected_context_sources,
        "source_selection": source_selection
        or _empty_context_source_selection_policy(
            source_selection_policy,
            max_selected_context_sources,
        ),
        "hidden_source_policy": "skip_unless_explicitly_included",
        "on_explicit_context_failure": on_explicit_context_failure,
        "explicit_context_failure_count": len(explicit_context_failures),
        "explicit_context_failures": list(explicit_context_failures),
        "source_roles": dict(sorted(source_roles.items())),
        "source_role_count": len(source_roles),
        "selected_count": selected_count,
        "usable_selected_count": selected_count,
        "skipped_count": skipped.total_count,
        "skipped_record_count": len(skipped.records),
        "skipped_records_truncated": skipped.omitted_count > 0,
        "skipped_records_omitted": skipped.omitted_count,
        "skipped_omitted_reasons": dict(sorted(skipped.omitted_reasons.items())),
        "failed_extraction_count": sum(
            skipped.reason_counts.get(reason, 0)
            for reason in {
                "extraction_failed",
                "extraction_resource_limit",
                "no_extractable_text",
            }
        ),
        "skipped": list(skipped.records),
        "include_patterns": include_patterns,
        "unmatched_includes": [
            record["pattern"] for record in include_patterns if record["matches"] == 0
        ],
    }
    _enforce_context_policy_provenance_limit(policy, max_context_provenance_chars)
    return policy


def _empty_context_source_selection_policy(
    policy: str,
    max_selected_context_sources: int | None,
) -> dict:
    return {
        "schema": "libreevolve.context_source_selection_policy.v1",
        "policy": policy,
        "max_selected_context_sources": max_selected_context_sources,
        "candidate_count": 0,
        "selected_count": 0,
        "omitted_count": 0,
        "ranking_policy": "none",
        "query_terms_sha256": hashlib.sha256(b"").hexdigest(),
        "query_term_count": 0,
        "ranking_fallback": "no_context_sources",
        "selected_sources": [],
        "omitted_sources": [],
    }


def _select_context_source_records(
    records: list[dict],
    manifest: dict,
    *,
    query_text: str,
) -> tuple[list[dict], dict]:
    policy = str(manifest["source_selection_policy"])
    max_selected_context_sources = manifest["max_selected_context_sources"]
    if not records:
        return [], _empty_context_source_selection_policy(
            policy,
            max_selected_context_sources,
        )
    query_terms = _context_excerpt_query_terms(query_text)
    query_hash = hashlib.sha256(" ".join(query_terms).encode("utf-8")).hexdigest()
    candidates = []
    for index, record in enumerate(records):
        metadata = record["metadata"]
        rendered = record["rendered"]
        score = _context_excerpt_chunk_score(rendered, query_terms) if query_terms else 0
        candidates.append({
            "path": record["path"],
            "sha256": metadata.get("sha256"),
            "chars_rendered": metadata.get("chars_rendered", len(rendered)),
            "excerpt_policy": metadata.get("excerpt_policy"),
            "source_role": metadata.get("source_role"),
            "source_role_status": metadata.get("source_role_status", "unclassified"),
            "score": score,
            "original_index": index,
        })
    if policy == "term_ranked":
        ordered_candidates = sorted(
            candidates,
            key=lambda item: (-item["score"], item["original_index"], item["path"]),
        )
        ranking_policy = "term_overlap_selected_excerpt_v1"
    else:
        ordered_candidates = sorted(candidates, key=lambda item: item["original_index"])
        ranking_policy = "path_order_v1"
    if max_selected_context_sources is None:
        selected_candidates = ordered_candidates
    else:
        selected_candidates = ordered_candidates[:max_selected_context_sources]
    selected_paths = {item["path"] for item in selected_candidates}
    record_by_path = {record["path"]: record for record in records}
    retained_records = [record_by_path[item["path"]] for item in selected_candidates]
    selected_source_records = []
    for rank, candidate in enumerate(selected_candidates, start=1):
        record = record_by_path[candidate["path"]]
        record["metadata"] = {
            **record["metadata"],
            "source_selection_policy": policy,
            "source_selection_rank": rank,
            "source_selection_score": candidate["score"],
            "source_selection_ranking_policy": ranking_policy,
            "source_selection_query_terms_sha256": query_hash,
            "source_selection_query_term_count": len(query_terms),
        }
        selected_source_records.append(_context_source_selection_record(candidate, rank))
    omitted_source_records = [
        _context_source_selection_record(candidate, None, reason="max_selected_context_sources")
        for candidate in ordered_candidates
        if candidate["path"] not in selected_paths
    ]
    selection = {
        "schema": "libreevolve.context_source_selection_policy.v1",
        "policy": policy,
        "max_selected_context_sources": max_selected_context_sources,
        "candidate_count": len(candidates),
        "selected_count": len(selected_source_records),
        "omitted_count": len(omitted_source_records),
        "ranking_policy": ranking_policy,
        "query_terms_sha256": query_hash,
        "query_term_count": len(query_terms),
        "ranking_fallback": "empty_query_terms" if not query_terms else None,
        "selected_sources": selected_source_records,
        "omitted_sources": omitted_source_records,
    }
    if selection["ranking_fallback"] is None:
        del selection["ranking_fallback"]
    return retained_records, selection


def _context_source_selection_record(
    candidate: dict,
    rank: int | None,
    *,
    reason: str | None = None,
) -> dict:
    record = {
        "path": candidate["path"],
        "sha256": candidate["sha256"],
        "chars_rendered": candidate["chars_rendered"],
        "excerpt_policy": candidate["excerpt_policy"],
        "score": candidate["score"],
    }
    if candidate.get("source_role") is not None:
        record["source_role"] = candidate.get("source_role")
        record["source_role_status"] = candidate.get(
            "source_role_status",
            "classified",
        )
    if rank is not None:
        record["rank"] = rank
    if reason is not None:
        record["reason"] = reason
    return record


def _enforce_context_policy_provenance_limit(policy: dict, max_chars: int) -> None:
    policy["context_provenance_truncated"] = False
    policy["context_provenance_chars"] = _context_policy_json_chars(policy)
    while policy["context_provenance_chars"] > max_chars and policy["skipped"]:
        record = policy["skipped"].pop()
        reason = str(record.get("reason", "unknown"))
        policy["skipped_record_count"] = len(policy["skipped"])
        policy["skipped_records_truncated"] = True
        policy["skipped_records_omitted"] += 1
        omitted = dict(policy["skipped_omitted_reasons"])
        omitted[reason] = omitted.get(reason, 0) + 1
        policy["skipped_omitted_reasons"] = dict(sorted(omitted.items()))
        policy["context_provenance_truncated"] = True
        policy["context_provenance_chars"] = _context_policy_json_chars(policy)
    if policy["context_provenance_chars"] > max_chars:
        policy["context_provenance_over_limit"] = True


def _context_policy_json_chars(policy: dict) -> int:
    return len(json.dumps(policy, sort_keys=True, allow_nan=False, separators=(",", ":")))


def _context_display_path_metadata(rel_path: str) -> dict:
    display_path = _context_display_path(rel_path)
    if display_path == rel_path:
        return {}
    return {"display_path": display_path}


def _context_resource_diagnostic(
    path: Path,
    context_dir: Path,
    reason: str,
    *,
    max_bytes: int,
    bytes_value: int,
    total_before: int | None = None,
) -> dict:
    rel_path = _context_diagnostic_rel_path(path, context_dir)
    diagnostic = {
        "path": rel_path,
        **_context_display_path_metadata(rel_path),
        "reason": reason,
        "source_type": path.suffix.lower().lstrip("."),
        "bytes": bytes_value,
        "max_bytes": max_bytes,
        "hidden": _is_hidden_context_path(rel_path),
        "sha256": None,
        "hash_omitted_reason": reason,
    }
    if total_before is not None:
        diagnostic["total_bytes_before"] = total_before
    return diagnostic


def _context_file_diagnostic(
    path: Path,
    context_dir: Path,
    reason: str,
    *,
    max_bytes: int,
) -> dict:
    rel_path = _context_diagnostic_rel_path(path, context_dir)
    source_type = path.suffix.lower().lstrip(".")
    hidden = _is_hidden_context_path(rel_path)
    try:
        size = path.stat().st_size
    except OSError as exc:
        return {
            "path": rel_path,
            **_context_display_path_metadata(rel_path),
            "reason": reason,
            "source_type": source_type,
            "sha256": None,
            "bytes": None,
            "hidden": hidden,
            "read_status": "stat_error",
            "error_type": exc.__class__.__name__,
            "error": redact_sensitive_text(str(exc)),
        }
    if size > max_bytes:
        return {
            "path": rel_path,
            **_context_display_path_metadata(rel_path),
            "reason": reason,
            "source_type": source_type,
            "sha256": None,
            "bytes": size,
            "max_bytes": max_bytes,
            "hidden": hidden,
            "read_status": "not_read",
            "hash_omitted_reason": "max_source_bytes",
        }
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        return {
            "path": rel_path,
            **_context_display_path_metadata(rel_path),
            "reason": reason,
            "source_type": source_type,
            "sha256": None,
            "bytes": None,
            "hidden": hidden,
            "read_status": "read_error",
            "error_type": exc.__class__.__name__,
            "error": redact_sensitive_text(str(exc)),
        }
    return {
        "path": rel_path,
        **_context_display_path_metadata(rel_path),
        "reason": reason,
        "source_type": source_type,
        "sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "bytes": len(raw_bytes),
        "hidden": hidden,
    }


def _context_stat_error_diagnostic(path: Path, context_dir: Path, exc: OSError) -> dict:
    rel_path = _context_diagnostic_rel_path(path, context_dir)
    return {
        "path": rel_path,
        **_context_display_path_metadata(rel_path),
        "reason": "stat_error",
        "source_type": path.suffix.lower().lstrip("."),
        "sha256": None,
        "bytes": None,
        "hidden": _is_hidden_context_path(rel_path),
        "error_type": exc.__class__.__name__,
        "error": redact_sensitive_text(str(exc)),
    }


def _context_extraction_diagnostic(metadata: dict) -> dict:
    status = str(metadata.get("extraction_status", "failed"))
    if status == "no_extractable_text":
        reason = "no_extractable_text"
    elif status == "resource_limit":
        reason = "extraction_resource_limit"
    elif status == "read_error":
        reason = "read_error"
    else:
        reason = "extraction_failed"
    diagnostic = {
        "path": metadata.get("path"),
        "reason": reason,
        "source_type": metadata.get("source_type"),
        "sha256": metadata.get("sha256"),
        "bytes": metadata.get("bytes"),
        "hidden": bool(metadata.get("hidden", False)),
        "extraction_status": status,
        "chars_original": metadata.get("chars_original"),
        "chars_rendered": metadata.get("chars_rendered"),
    }
    if "filesystem_path" in metadata:
        diagnostic["filesystem_path"] = metadata["filesystem_path"]
    if "pages" in metadata:
        diagnostic["pages"] = metadata["pages"]
    for key in ("max_pdf_pages", "max_pdf_chars", "extracted_chars"):
        if key in metadata:
            diagnostic[key] = metadata[key]
    if "error_type" in metadata:
        diagnostic["error_type"] = metadata["error_type"]
    if "error" in metadata:
        diagnostic["error"] = redact_sensitive_text(str(metadata["error"]))
    return diagnostic


def _matched_context_include_patterns(
    rel_path: str, include: list[str] | None
) -> list[str]:
    if include is None:
        return []
    return [pattern for pattern in include if _matches(rel_path, pattern)]


def _explicit_context_failure_record(
    diagnostic: dict, matched_include_patterns: list[str]
) -> dict:
    record = {
        "path": diagnostic.get("path"),
        "reason": diagnostic.get("reason"),
        "source_type": diagnostic.get("source_type"),
        "extraction_status": diagnostic.get("extraction_status"),
        "matched_include_patterns": list(matched_include_patterns),
    }
    for key in (
        "bytes",
        "sha256",
        "pages",
        "max_pdf_pages",
        "max_pdf_chars",
        "extracted_chars",
        "error_type",
        "error",
    ):
        if key in diagnostic:
            record[key] = diagnostic[key]
    return record


def _raise_explicit_context_failure(
    context_dir: Path, failures: list[dict]
) -> None:
    displayed = ", ".join(str(item.get("path", "<unknown>")) for item in failures[:3])
    if len(failures) > 3:
        displayed += f", ... ({len(failures) - 3} more)"
    raise ValueError(
        f"{context_dir}: explicit context extraction failed for "
        f"{len(failures)} included source(s): {displayed}; set "
        "on_explicit_context_failure: warn to allow degraded context"
    )


def _iter_context_entries(
    root: Path,
    *,
    max_entries: int,
    max_depth: int,
    skipped: _ContextSkippedDiagnostics,
) -> list[Path]:
    entries: list[Path] = []
    stopped = False

    def walk(directory: Path) -> None:
        nonlocal stopped
        if stopped:
            return
        try:
            children = sorted(directory.iterdir(), key=_context_sort_key)
        except OSError as exc:
            skipped.append(_context_directory_listing_diagnostic(directory, root, exc))
            return
        for path in children:
            if stopped:
                return
            if path.name in _CONTEXT_MANIFEST_NAMES:
                continue
            if _is_link(path):
                raise ValueError(f"Context links are not supported: {path}")
            rel_parts = path.relative_to(root).parts
            depth = len(rel_parts)
            if depth > max_depth:
                skipped.append(
                    _context_traversal_limit_diagnostic(
                        path,
                        root,
                        "max_context_depth",
                        depth=depth,
                        max_depth=max_depth,
                    )
                )
                continue
            if len(entries) >= max_entries:
                skipped.append(
                    _context_traversal_limit_diagnostic(
                        path,
                        root,
                        "max_context_entries",
                        max_entries=max_entries,
                        entries_before=len(entries),
                    )
                )
                stopped = True
                return
            try:
                is_directory = path.is_dir()
            except OSError as exc:
                skipped.append(_context_stat_error_diagnostic(path, root, exc))
                continue
            entries.append(path)
            if is_directory:
                walk(path)

    walk(root)
    return entries


def _context_directory_listing_diagnostic(
    path: Path,
    context_dir: Path,
    exc: OSError,
) -> dict:
    rel_path = _context_diagnostic_rel_path(path, context_dir)
    return {
        "path": rel_path,
        "reason": "directory_listing_error",
        "source_type": "directory",
        "hidden": _is_hidden_context_path(rel_path),
        "sha256": None,
        "error_type": exc.__class__.__name__,
        "error": redact_sensitive_text(str(exc)),
    }


def _context_traversal_limit_diagnostic(
    path: Path,
    context_dir: Path,
    reason: str,
    *,
    depth: int | None = None,
    max_depth: int | None = None,
    max_entries: int | None = None,
    entries_before: int | None = None,
) -> dict:
    rel_path = _context_diagnostic_rel_path(path, context_dir)
    diagnostic = {
        "path": rel_path,
        "reason": reason,
        "source_type": "directory" if path.is_dir() else path.suffix.lower().lstrip("."),
        "hidden": _is_hidden_context_path(rel_path),
        "sha256": None,
    }
    if depth is not None:
        diagnostic["depth"] = depth
    if max_depth is not None:
        diagnostic["max_depth"] = max_depth
    if max_entries is not None:
        diagnostic["max_entries"] = max_entries
    if entries_before is not None:
        diagnostic["entries_before"] = entries_before
    return diagnostic


def _context_diagnostic_rel_path(path: Path, context_dir: Path) -> str:
    rel_path = path.relative_to(context_dir).as_posix()
    if redact_sensitive_text(rel_path) != rel_path:
        raise ValueError(
            "skipped context source path must not contain secret-like text"
        )
    return rel_path


def _context_sort_key(path: Path) -> str:
    return path.as_posix()


def _matches_any(rel_path: str, patterns: list[str]) -> bool:
    return any(_matches(rel_path, pattern) for pattern in patterns)


def _matches(rel_path: str, pattern: str) -> bool:
    path_parts = [part for part in _context_display_path(rel_path).split("/") if part]
    pattern_parts = [part for part in _context_display_path(pattern).split("/") if part]
    return _matches_path_parts(path_parts, pattern_parts)


def _matches_path_parts(path_parts: list[str], pattern_parts: list[str]) -> bool:
    if not pattern_parts:
        return not path_parts
    pattern_head = pattern_parts[0]
    if pattern_head == "**":
        if len(pattern_parts) == 1:
            return True
        return any(
            _matches_path_parts(path_parts[index:], pattern_parts[1:])
            for index in range(len(path_parts) + 1)
        )
    if not path_parts:
        return False
    return fnmatch.fnmatchcase(path_parts[0], pattern_head) and _matches_path_parts(
        path_parts[1:],
        pattern_parts[1:],
    )


def _is_hidden_context_path(rel_path: str) -> bool:
    return any(part.startswith(".") for part in rel_path.split("/") if part)


def _hidden_context_explicitly_included(
    include: list[str] | None,
    matched_include_indexes: list[int],
) -> bool:
    if include is None:
        return False
    return any(
        _pattern_has_hidden_component(include[index])
        for index in matched_include_indexes
    )


def _pattern_has_hidden_component(pattern: str) -> bool:
    return any(part.startswith(".") for part in pattern.split("/") if part)


def _context_include_pattern_records(
    include: list[str] | None, match_counts: list[int], selected_counts: list[int]
) -> list[dict]:
    if include is None:
        return []
    return [
        {
            "pattern": pattern,
            "matches": match_counts[index],
            "selected_matches": selected_counts[index],
        }
        for index, pattern in enumerate(include)
    ]


def _read_context_source(
    path: Path,
    rel_path: str,
    max_chars: int,
    *,
    excerpt_policy: str,
    query_text: str = "",
    raw_rel_path: str | None = None,
    max_pdf_pages: int,
    max_pdf_chars: int,
) -> tuple[str, dict]:
    _validate_context_source_path(path, rel_path, raw_rel_path=raw_rel_path)
    source_type = path.suffix.lower().lstrip(".")
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        metadata = {
            "path": rel_path,
            "source_type": source_type,
            "sha256": None,
            "bytes": None,
            "chars_original": 0,
            "chars_rendered": 0,
            "truncated": False,
            "excerpt_start": 0,
            "excerpt_end": 0,
            "excerpt_policy": excerpt_policy,
            "max_chars": max_chars,
            "extraction_status": "read_error",
            "error_type": exc.__class__.__name__,
            "error": redact_sensitive_text(str(exc)),
        }
        if raw_rel_path is not None and raw_rel_path != rel_path:
            metadata["filesystem_path"] = raw_rel_path
        if _is_hidden_context_path(rel_path):
            metadata["hidden"] = True
        return "", metadata
    sha256 = hashlib.sha256(raw_bytes).hexdigest()
    if path.suffix.lower() == ".pdf":
        text, extraction = _read_pdf_text(
            path,
            max_pages=max_pdf_pages,
            max_chars=max_pdf_chars,
        )
    else:
        text, extraction = _read_text_context(raw_bytes)
    rendered, excerpt = _summarize_context_text(
        text,
        rel_path,
        max_chars,
        excerpt_policy=excerpt_policy,
        query_text=query_text,
    )
    if source_type == "pdf":
        excerpt_page_record = _pdf_excerpt_page_record(
            extraction.get("page_char_spans"),
            excerpt["start"],
            excerpt["end"],
            excerpt_spans=excerpt["spans"],
        )
        extraction = {**extraction, **excerpt_page_record}
    metadata = {
        "path": rel_path,
        "source_type": source_type,
        "sha256": sha256,
        "bytes": len(raw_bytes),
        "chars_original": len(text),
        "chars_rendered": len(rendered),
        "truncated": excerpt["truncated"],
        "excerpt_start": excerpt["start"],
        "excerpt_end": excerpt["end"],
        "excerpt_spans": excerpt["spans"],
        "excerpt_policy": excerpt["policy"],
        "omitted_chars": excerpt["omitted_chars"],
        "max_chars": max_chars,
        **extraction,
    }
    for key in (
        "ranking_policy",
        "ranking_fallback",
        "query_terms_sha256",
        "query_term_count",
        "selected_chunks",
        "omitted_chunk_count",
    ):
        if key in excerpt:
            metadata[f"excerpt_{key}"] = excerpt[key]
    if raw_rel_path is not None and raw_rel_path != rel_path:
        metadata["filesystem_path"] = raw_rel_path
    if _is_hidden_context_path(rel_path):
        metadata["hidden"] = True
    return rendered, metadata


def _context_display_path(rel_path: str) -> str:
    return unicodedata.normalize("NFC", rel_path)


def _validate_context_source_path(
    path: Path, rel_path: str, *, raw_rel_path: str | None = None
) -> None:
    if redact_sensitive_text(rel_path) != rel_path or (
        raw_rel_path is not None and redact_sensitive_text(raw_rel_path) != raw_rel_path
    ):
        raise ValueError(
            f"{path}: context source path must not contain secret-like text"
        )


def _read_text_context(raw_bytes: bytes) -> tuple[str, dict]:
    try:
        text = raw_bytes.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        return text, {"extraction_status": "ok"}
    except UnicodeDecodeError as exc:
        error = f"{exc.__class__.__name__}: {exc}"
        return (
            f"(text extraction failed: {error})",
            {"extraction_status": "failed", "error": error},
        )


def _read_pdf_text(path: Path, *, max_pages: int, max_chars: int) -> tuple[str, dict]:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        page_count = len(reader.pages)
        if page_count > max_pages:
            return "", {
                "extraction_status": "resource_limit",
                "error": f"PDF page count {page_count} exceeds max_pdf_pages {max_pages}",
                "pages": [1, page_count],
                "max_pdf_pages": max_pages,
            }
        segments: list[tuple[int, str]] = []
        extracted_chars = 0
        for index, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                extracted_chars += len(page_text)
                if extracted_chars > max_chars:
                    return "", {
                        "extraction_status": "resource_limit",
                        "error": (
                            f"PDF extracted text exceeds max_pdf_chars {max_chars}"
                        ),
                        "pages": [1, page_count],
                        "max_pdf_chars": max_chars,
                        "extracted_chars": extracted_chars,
                    }
                segments.append((index, page_text))
        if segments:
            parts: list[str] = []
            spans: list[dict] = []
            position = 0
            for segment_index, (page_number, page_text) in enumerate(segments):
                if segment_index > 0:
                    parts.append("\n")
                    position += 1
                start = position
                parts.append(page_text)
                position += len(page_text)
                spans.append({"page": page_number, "start": start, "end": position})
            text = "".join(parts)
            return text, {
                "extraction_status": "ok",
                "pages": [1, page_count],
                "extracted_pages": [page_number for page_number, _ in segments],
                "extracted_page_range": [segments[0][0], segments[-1][0]],
                "page_char_spans": spans,
            }
        return "(no extractable text)", {
            "extraction_status": "no_extractable_text",
            "pages": [1, page_count],
        }
    except Exception as exc:
        error = f"{exc.__class__.__name__}: {exc}"
        return (
            f"(PDF extraction failed: {error})",
            {"extraction_status": "failed", "error": error},
        )


def _pdf_excerpt_page_record(
    page_char_spans: object,
    excerpt_start: int,
    excerpt_end: int,
    *,
    excerpt_spans: list[dict] | None = None,
) -> dict:
    if not isinstance(page_char_spans, list) or not page_char_spans:
        return {}
    requested_spans = excerpt_spans or [{"start": excerpt_start, "end": excerpt_end}]
    overlaps = []
    for item in page_char_spans:
        if not isinstance(item, dict):
            continue
        page = item.get("page")
        start = item.get("start")
        end = item.get("end")
        if not isinstance(page, int) or not isinstance(start, int) or not isinstance(end, int):
            continue
        for requested in requested_spans:
            requested_start = requested.get("start")
            requested_end = requested.get("end")
            if not isinstance(requested_start, int) or not isinstance(requested_end, int):
                continue
            overlap_start = max(start, requested_start)
            overlap_end = min(end, requested_end)
            if overlap_start < overlap_end:
                page_local_start = overlap_start - start
                page_local_end = overlap_end - start
                overlaps.append({
                    "page": page,
                    "excerpt_start": overlap_start,
                    "excerpt_end": overlap_end,
                    "page_excerpt_start": page_local_start,
                    "page_excerpt_end": page_local_end,
                })
    if not overlaps:
        return {}
    return {
        "excerpt_pages": [item["page"] for item in overlaps],
        "excerpt_page_spans": overlaps,
    }


def _summarize_context_text(
    text: str,
    source: str,
    max_chars: int,
    *,
    excerpt_policy: str,
    query_text: str = "",
) -> tuple[str, dict]:
    if len(text) <= max_chars:
        return text, {
            "start": 0,
            "end": len(text),
            "spans": [{"start": 0, "end": len(text)}],
            "truncated": False,
            "policy": excerpt_policy,
            "omitted_chars": 0,
        }
    if excerpt_policy == "term_ranked":
        return _summarize_context_text_by_term_rank(
            text,
            source,
            max_chars,
            query_text=query_text,
        )
    if excerpt_policy == "head_tail":
        head_chars = (max_chars + 1) // 2
        tail_chars = max_chars - head_chars
        head = text[:head_chars]
        tail = text[-tail_chars:] if tail_chars > 0 else ""
        spans = [{"start": 0, "end": head_chars}]
        if tail_chars > 0:
            tail_start = len(text) - tail_chars
            spans.append({"start": tail_start, "end": len(text)})
        return (
            f"[{source}: showing first {head_chars} and last {tail_chars} "
            f"of {len(text)} characters]\n{head}\n...\n{tail}",
            {
                "start": 0,
                "end": len(text),
                "spans": spans,
                "truncated": True,
                "policy": excerpt_policy,
                "omitted_chars": len(text) - max_chars,
            },
        )
    return (
        f"[{source}: showing first {max_chars} of {len(text)} characters]\n"
        f"{text[:max_chars]}",
        {
            "start": 0,
            "end": max_chars,
            "spans": [{"start": 0, "end": max_chars}],
            "truncated": True,
            "policy": excerpt_policy,
            "omitted_chars": len(text) - max_chars,
        },
    )


def _summarize_context_text_by_term_rank(
    text: str,
    source: str,
    max_chars: int,
    *,
    query_text: str,
) -> tuple[str, dict]:
    query_terms = _context_excerpt_query_terms(query_text)
    query_hash = hashlib.sha256(
        " ".join(query_terms).encode("utf-8")
    ).hexdigest()
    if not query_terms:
        rendered, excerpt = _summarize_context_text(
            text,
            source,
            max_chars,
            excerpt_policy="head",
            query_text=query_text,
        )
        return rendered, {
            **excerpt,
            "policy": "term_ranked",
            "ranking_policy": "term_overlap_fixed_window_v1",
            "ranking_fallback": "head_empty_query_terms",
            "query_terms_sha256": query_hash,
            "query_term_count": 0,
            "selected_chunks": [],
            "omitted_chunk_count": 0,
        }
    chunks = _context_excerpt_chunks(text, max_chars)
    ranked = sorted(
        (
            {
                **chunk,
                "score": _context_excerpt_chunk_score(chunk["text"], query_terms),
            }
            for chunk in chunks
        ),
        key=lambda chunk: (-chunk["score"], chunk["start"], chunk["end"]),
    )
    selected = ranked[0]
    selected_text = text[selected["start"] : selected["end"]]
    omitted_count = max(0, len(chunks) - 1)
    rendered = (
        f"[{source}: showing term-ranked chunk {selected['index']} "
        f"({selected['start']}:{selected['end']}) of {len(text)} characters; "
        f"score={selected['score']}]\n{selected_text}"
    )
    selected_chunk = {
        "index": selected["index"],
        "start": selected["start"],
        "end": selected["end"],
        "score": selected["score"],
    }
    return rendered, {
        "start": selected["start"],
        "end": selected["end"],
        "spans": [{"start": selected["start"], "end": selected["end"]}],
        "truncated": True,
        "policy": "term_ranked",
        "omitted_chars": len(text) - len(selected_text),
        "ranking_policy": "term_overlap_fixed_window_v1",
        "query_terms_sha256": query_hash,
        "query_term_count": len(query_terms),
        "selected_chunks": [selected_chunk],
        "omitted_chunk_count": omitted_count,
    }


def _context_excerpt_query_terms(text: str) -> list[str]:
    terms = {
        match.group(0).lower()
        for match in re.finditer(r"[A-Za-z0-9_]{3,}", text)
    }
    return sorted(terms)[:256]


def _context_excerpt_chunks(text: str, max_chars: int) -> list[dict]:
    chunks = []
    for index, start in enumerate(range(0, len(text), max_chars)):
        end = min(len(text), start + max_chars)
        chunks.append({
            "index": index,
            "start": start,
            "end": end,
            "text": text[start:end],
        })
    return chunks


def _context_excerpt_chunk_score(text: str, query_terms: list[str]) -> int:
    chunk_terms = {
        match.group(0).lower()
        for match in re.finditer(r"[A-Za-z0-9_]{3,}", text)
    }
    return sum(1 for term in query_terms if term in chunk_terms)
