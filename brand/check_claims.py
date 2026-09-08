#!/usr/bin/env python3
"""Validate the small, reviewable W01 claim and copy registries.

The checker is deliberately stdlib-only.  It validates JSON data supplied by the
caller; it never imports product code, executes candidate code, or makes network
requests.  The marketing checks are conservative heuristics, not semantic proof.
Human review is still required before a draft is published.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
import json
import math
from pathlib import Path
import re
import sys
from typing import Any


SCHEMA_VERSION = "1.0"
SOURCE_REPOSITORY = "https://github.com/LibreEvolve/libreevolve"
DEFAULT_CLAIMS_PATH = Path(__file__).resolve().with_name("claims-summary.json")
DEFAULT_COPY_PATH = Path(__file__).resolve().with_name("copy-registry.json")

VALID_STATUSES = {"draft", "reviewed"}
VALID_KINDS = {"brand", "product", "outcome", "roadmap"}

VALIDATION_NOTICE = (
    "Forbidden-marketing checks are conservative heuristics, not semantic proof; "
    "manual review remains required."
)


class JsonDocumentError(ValueError):
    """Raised when a JSON document violates the loader's safety rules."""


def _object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build an object while rejecting duplicate keys at every nesting level."""

    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise JsonDocumentError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise JsonDocumentError(f"non-finite JSON number: {value}")


def _check_finite(value: Any, location: str = "$") -> None:
    """Reject finite-looking JSON numbers that overflowed to infinity."""

    if isinstance(value, float) and not math.isfinite(value):
        raise JsonDocumentError(f"non-finite JSON number at {location}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _check_finite(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _check_finite(child, f"{location}[{index}]")


def load_json(path: str | Path) -> dict[str, Any]:
    """Load one registry with duplicate-key and non-finite-number rejection."""

    source = Path(path)
    try:
        raw = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise JsonDocumentError(f"cannot read {source}: {exc}") from exc
    try:
        value = json.loads(
            raw,
            object_pairs_hook=_object_pairs,
            parse_constant=_reject_constant,
        )
    except JsonDocumentError:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise JsonDocumentError(f"invalid JSON in {source}: {exc}") from exc
    _check_finite(value)
    if not isinstance(value, dict):
        raise JsonDocumentError(f"{source}: top-level JSON value must be an object")
    return value


def _error(errors: list[str], location: str, message: str) -> None:
    errors.append(f"{location}: {message}")


def _nonempty_text(
    value: Any,
    location: str,
    errors: list[str],
) -> bool:
    if not isinstance(value, str):
        _error(errors, location, "must be a string")
        return False
    if not value.strip():
        _error(errors, location, "must not be empty")
        return False
    return True


def _string_list(value: Any, location: str, errors: list[str]) -> bool:
    if not isinstance(value, list):
        _error(errors, location, "must be an array of strings")
        return False
    valid = True
    for index, item in enumerate(value):
        if not _nonempty_text(item, f"{location}[{index}]", errors):
            valid = False
    return valid


def _valid_sha(value: Any, location: str, errors: list[str]) -> bool:
    if not isinstance(value, str):
        _error(errors, location, "must be a 40-character hexadecimal commit")
        return False
    if re.fullmatch(r"[0-9a-fA-F]{40}", value) is None:
        _error(errors, location, "must be a 40-character hexadecimal commit")
        return False
    return True


def _safe_source_path(value: Any, location: str, errors: list[str]) -> bool:
    """Accept repository-relative POSIX paths and reject traversal/URI paths."""

    if not _nonempty_text(value, location, errors):
        return False
    assert isinstance(value, str)
    path = value.strip()
    unsafe = (
        "\x00" in path
        or "\\" in path
        or path.startswith("/")
        or path.startswith("~")
        or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", path) is not None
        or any(part in {"", ".", ".."} for part in path.split("/"))
    )
    if unsafe:
        _error(errors, location, "must be a safe repository-relative path")
        return False
    return True


def _line_number(value: Any, location: str, errors: list[str]) -> bool:
    if type(value) is not int or value < 1:
        _error(errors, location, "must be a positive integer line number")
        return False
    return True


def _status(value: Any, location: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or value not in VALID_STATUSES:
        _error(errors, location, "must be 'draft' or 'reviewed'")
        return False
    return True


_NEGATION_RE = re.compile(
    r"\b(?:no|not|never|without|cannot|can't|doesn[’']t|does\s+not|"
    r"isn[’']t|is\s+not|aren[’']t|are\s+not|unknown|unvalidated|"
    r"unsupported|unproven|incomplete|rather\s+than|instead\s+of)\b",
    re.IGNORECASE,
)
_CONTRAST_RE = re.compile(r",\s*(?:but|however|although|yet|while)\b", re.IGNORECASE)
_COORDINATOR_RE = re.compile(r"\b(?:and|or|but|however|although|yet|while)\b", re.IGNORECASE)
_CAPABILITY_WORD_RE = re.compile(r"\b(?:dollar|token|spend|cost|usage|cap|limit)\b", re.IGNORECASE)
_DIRECT_SUFFIX_RE = re.compile(
    r"^\s*(?:(?::|,)\s*)?"
    r"(?:(?:is|are|was|were|remains?|may|might|can)\s+(?:be\s+)?)?"
    r"(?:unknown|unvalidated|unverified|unavailable|unsupported|"
    r"not\s+(?:provided|available|supported|offered|claimed|guaranteed)|"
    r"(?:status|availability|support|claim|value)\s+(?:is\s+)?unknown)\b",
    re.IGNORECASE,
)


def _preceding_clause(text: str, start: int) -> str:
    prefix = text[:start]
    boundaries = [match.end() for match in re.finditer(r"[.!?;\n]", prefix)]
    boundaries.extend(match.end() for match in _CONTRAST_RE.finditer(prefix))
    return prefix[max(boundaries, default=0):]


def _has_limitation_context(
    text: str,
    start: int,
    end: int,
    label: str,
) -> bool:
    """Allow only a direct limitation attached to the matched phrase.

    The check intentionally does not attempt general natural-language
    understanding.  It recognizes a bounded preceding negation (including
    ``rather than`` constructions) or a short, direct suffix such as
    ``is not provided``/``may be unknown``.  A prior sentence or a contrast
    clause cannot excuse a positive claim.
    """

    clause = _preceding_clause(text, start)
    negations = list(_NEGATION_RE.finditer(clause))
    if negations:
        negation = negations[-1]
        between = clause[negation.end():]
        if len(between) <= 64 and not _COORDINATOR_RE.search(between):
            return True
        # ``No hard token or dollar cap claim`` is one coordinated
        # limitation.  Do not generalize this exception to other claims.
        if (
            label == "hard dollar/token cap assertion"
            and len(between) <= 64
            and "or" in between.lower()
            and _CAPABILITY_WORD_RE.search(between)
            and not re.search(r"[.!?;,\n]", between)
        ):
            return True

    suffix = text[end:]
    return _DIRECT_SUFFIX_RE.match(suffix) is not None


_COUNT_NUMBER = (
    r"(?:\d{1,3}(?:,\d{3})+|\d+|one|two|three|four|five|six|seven|eight|"
    r"nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
    r"eighteen|nineteen|twenty)"
)

_FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "historical numeric test/provider/plugin/example count",
        re.compile(
            rf"\b{_COUNT_NUMBER}(?:\s+\w+){{0,2}}\s+"
            rf"(?:tests?|test\s+cases?|providers?|plugins?|examples?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "guaranteed-improvement assertion",
        re.compile(
            r"\b(?:guarantee(?:d|s)?|always|will\s+always)\b"
            r"(?:\s+\w+){0,6}\s+\bimprov\w*\b",
            re.IGNORECASE,
        ),
    ),
    (
        "guaranteed-improvement assertion",
        re.compile(
            r"\b(?:improv\w*|better)\b(?:\s+\w+){0,6}\s+"
            r"\b(?:every|all|any|guarantee(?:d|s)?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "secure-sandbox assertion",
        re.compile(r"\b(?:secure|hardened|safe|security)\s+(?:code\s+)?sandbox\b", re.IGNORECASE),
    ),
    (
        "production-ready assertion",
        re.compile(r"\bproduction[ -]ready\b", re.IGNORECASE),
    ),
    (
        "free-use assertion",
        re.compile(
            r"\b(?:free\s+(?:use|to\s+use|usage|of\s+charge|subscription)|"
            r"zero[ -]?cost|no[ -]?cost)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "hard dollar/token cap assertion",
        re.compile(
            r"\b(?:hard|fixed|guaranteed|maximum|max)\s+"
            r"(?:dollar|token)(?:\s+or\s+(?:dollar|token))?\s+"
            r"(?:cap|limit|ceiling)s?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "hard dollar/token cap assertion",
        re.compile(
            r"\b(?:hard|fixed|guaranteed|maximum|max)\s+"
            r"(?:spend|cost|usage)\s+(?:cap|limit|ceiling)s?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "hard dollar/token cap assertion",
        re.compile(r"\b(?:dollar|token)\s+(?:cap|limit)\b", re.IGNORECASE),
    ),
)


def _scan_marketing_text(value: Any, location: str, errors: list[str]) -> None:
    if not isinstance(value, str):
        return
    seen: set[str] = set()
    for label, pattern in _FORBIDDEN_PATTERNS:
        for match in pattern.finditer(value):
            # Numeric historical counts are forbidden evidence-shaped
            # marketing regardless of nearby prose or negation.
            if label != "historical numeric test/provider/plugin/example count" and _has_limitation_context(
                value, match.start(), match.end(), label
            ):
                continue
            if label not in seen:
                _error(errors, location, f"contains forbidden {label}")
                seen.add(label)
            break


def _validate_claims_document(claims: Any, errors: list[str]) -> tuple[str | None, set[str]]:
    if not isinstance(claims, Mapping):
        _error(errors, "claims", "must be a JSON object")
        return None, set()

    if claims.get("schema_version") != SCHEMA_VERSION:
        _error(errors, "claims.schema_version", f"must be {SCHEMA_VERSION!r}")
    if claims.get("source_repository") != SOURCE_REPOSITORY:
        _error(errors, "claims.source_repository", f"must be {SOURCE_REPOSITORY!r}")
    commit = claims.get("source_commit")
    commit_ok = _valid_sha(commit, "claims.source_commit", errors)
    raw_claims = claims.get("claims")
    if not isinstance(raw_claims, list):
        _error(errors, "claims.claims", "must be a non-empty array")
        return (commit if commit_ok else None), set()
    if not raw_claims:
        _error(errors, "claims.claims", "must not be empty")

    identifiers: set[str] = set()
    for index, claim in enumerate(raw_claims):
        location = f"claims.claims[{index}]"
        if not isinstance(claim, Mapping):
            _error(errors, location, "must be an object")
            continue

        claim_id = claim.get("id")
        if _nonempty_text(claim_id, f"{location}.id", errors):
            assert isinstance(claim_id, str)
            if claim_id in identifiers:
                _error(errors, f"{location}.id", f"duplicate claim id {claim_id!r}")
            identifiers.add(claim_id)
        for field in ("wording", "scope"):
            if _nonempty_text(claim.get(field), f"{location}.{field}", errors):
                _scan_marketing_text(claim[field], f"{location}.{field}", errors)
        if claim.get("evidence_tier") != "source":
            _error(errors, f"{location}.evidence_tier", "must be 'source'")
        _status(claim.get("status"), f"{location}.status", errors)

        refs = claim.get("source_refs")
        if not isinstance(refs, list):
            _error(errors, f"{location}.source_refs", "must be a non-empty array")
            continue
        if not refs:
            _error(errors, f"{location}.source_refs", "must not be empty")
        for ref_index, ref in enumerate(refs):
            ref_location = f"{location}.source_refs[{ref_index}]"
            if not isinstance(ref, Mapping):
                _error(errors, ref_location, "must be an object")
                continue
            _safe_source_path(ref.get("path"), f"{ref_location}.path", errors)
            start_ok = _line_number(ref.get("start_line"), f"{ref_location}.start_line", errors)
            end_ok = _line_number(ref.get("end_line"), f"{ref_location}.end_line", errors)
            if start_ok and end_ok and ref["start_line"] > ref["end_line"]:
                _error(errors, ref_location, "start_line must not exceed end_line")

    return (commit if commit_ok else None), identifiers


def _validate_copy_document(
    copy_registry: Any,
    claim_ids: set[str],
    errors: list[str],
) -> str | None:
    if not isinstance(copy_registry, Mapping):
        _error(errors, "copy", "must be a JSON object")
        return None

    if copy_registry.get("schema_version") != SCHEMA_VERSION:
        _error(errors, "copy.schema_version", f"must be {SCHEMA_VERSION!r}")
    commit = copy_registry.get("source_commit")
    commit_ok = _valid_sha(commit, "copy.source_commit", errors)
    units = copy_registry.get("units")
    if not isinstance(units, list):
        _error(errors, "copy.units", "must be a non-empty array")
        return (commit if commit_ok else None)
    if not units:
        _error(errors, "copy.units", "must not be empty")

    identifiers: set[str] = set()
    for index, unit in enumerate(units):
        location = f"copy.units[{index}]"
        if not isinstance(unit, Mapping):
            _error(errors, location, "must be an object")
            continue

        unit_id = unit.get("id")
        if _nonempty_text(unit_id, f"{location}.id", errors):
            assert isinstance(unit_id, str)
            if unit_id in identifiers:
                _error(errors, f"{location}.id", f"duplicate unit id {unit_id!r}")
            identifiers.add(unit_id)

        surfaces = unit.get("surfaces")
        if not isinstance(surfaces, list):
            _error(errors, f"{location}.surfaces", "must be a non-empty array of strings")
        elif not surfaces:
            _error(errors, f"{location}.surfaces", "must not be empty")
        else:
            _string_list(surfaces, f"{location}.surfaces", errors)

        kind = unit.get("kind")
        if not isinstance(kind, str) or kind not in VALID_KINDS:
            _error(errors, f"{location}.kind", "must be brand, product, outcome, or roadmap")
        text_ok = _nonempty_text(unit.get("text"), f"{location}.text", errors)
        if text_ok:
            _scan_marketing_text(unit["text"], f"{location}.text", errors)

        if "usage_condition" in unit:
            usage_condition = unit["usage_condition"]
            if _nonempty_text(usage_condition, f"{location}.usage_condition", errors):
                _scan_marketing_text(usage_condition, f"{location}.usage_condition", errors)
        elif kind == "outcome":
            _error(errors, f"{location}.usage_condition", "is required for outcome units")

        _status(unit.get("status"), f"{location}.status", errors)
        raw_claim_ids = unit.get("claim_ids")
        if not isinstance(raw_claim_ids, list):
            _error(errors, f"{location}.claim_ids", "must be an array of claim ids")
            continue
        if any(not _nonempty_text(item, f"{location}.claim_ids[{i}]", errors)
               for i, item in enumerate(raw_claim_ids)):
            continue
        seen_claim_ids: set[str] = set()
        known_reference_count = 0
        for ref_index, claim_id in enumerate(raw_claim_ids):
            assert isinstance(claim_id, str)
            if claim_id in seen_claim_ids:
                _error(errors, f"{location}.claim_ids[{ref_index}]", f"duplicate claim id {claim_id!r}")
            seen_claim_ids.add(claim_id)
            if claim_id not in claim_ids:
                _error(errors, f"{location}.claim_ids[{ref_index}]", f"unknown claim id {claim_id!r}")
            else:
                known_reference_count += 1
        if isinstance(kind, str) and kind in {"product", "outcome"} and known_reference_count == 0:
            _error(errors, f"{location}.claim_ids", f"{kind} units require at least one known claim reference")

    return (commit if commit_ok else None)


def validate(
    claims: Any,
    copy: Any,
    *,
    require_reviewed: bool = False,
) -> list[str]:
    """Return deterministic validation errors for two already-loaded registries.

    ``claims`` and ``copy`` must be decoded JSON objects.  Use :func:`load_json`
    for files when duplicate-key and non-finite-number rejection is required.
    The function performs no imports beyond this stdlib module and no I/O.
    """

    errors: list[str] = []
    claims_commit, claim_ids = _validate_claims_document(claims, errors)
    copy_commit = _validate_copy_document(copy, claim_ids, errors)
    if claims_commit is not None and copy_commit is not None:
        if claims_commit.lower() != copy_commit.lower():
            _error(errors, "source_commit", "claims and copy source commits must match")

    if require_reviewed:
        for document_name, document in (("claims", claims), ("copy", copy)):
            if not isinstance(document, Mapping):
                continue
            entries_key = "claims" if document_name == "claims" else "units"
            entries = document.get(entries_key)
            if not isinstance(entries, list):
                continue
            for index, entry in enumerate(entries):
                if isinstance(entry, Mapping) and entry.get("status") == "draft":
                    _error(errors, f"{document_name}.{entries_key}[{index}].status", "draft is rejected by --require-reviewed")

    return errors


def validate_files(
    claims_path: str | Path,
    copy_path: str | Path,
    *,
    require_reviewed: bool = False,
) -> list[str]:
    """Load and validate registry files, returning errors instead of raising."""

    errors: list[str] = []
    try:
        claims = load_json(claims_path)
    except JsonDocumentError as exc:
        errors.append(f"claims: {exc}")
        claims = None
    try:
        copy_registry = load_json(copy_path)
    except JsonDocumentError as exc:
        errors.append(f"copy: {exc}")
        copy_registry = None
    if claims is not None and copy_registry is not None:
        errors.extend(validate(claims, copy_registry, require_reviewed=require_reviewed))
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--claims",
        type=Path,
        default=DEFAULT_CLAIMS_PATH,
        help=f"claims JSON (default: {DEFAULT_CLAIMS_PATH})",
    )
    parser.add_argument(
        "--copy",
        dest="copy_path",
        type=Path,
        default=DEFAULT_COPY_PATH,
        help=f"copy JSON (default: {DEFAULT_COPY_PATH})",
    )
    parser.add_argument(
        "--require-reviewed",
        action="store_true",
        help="reject draft claims and copy units",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    errors = validate_files(args.claims, args.copy_path, require_reviewed=args.require_reviewed)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(VALIDATION_NOTICE, file=sys.stderr)
        return 1
    print("Validation passed.")
    print(VALIDATION_NOTICE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
