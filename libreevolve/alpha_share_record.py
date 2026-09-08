"""Strict frozen public records and local, payload-bound approval receipts.

No candidate execution, imports, file reads or network requests. Approval is an
operator safety interlock, not authentication, a signature or factual attestation.
Never serialize an approval receipt into the public result directory.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import math
import re
import unicodedata
from urllib.parse import urlsplit

from libreevolve.alpha_share_metrics import MAX_COUNT, admit_metrics, compare_metrics


MAX_RECORD_BYTES = 65_536
RECORD_KEYS = frozenset({
    "schema_version", "public_result_id", "product_status", "evidence_class",
    "run_status", "selected_source", "candidate_retention", "baseline", "candidate", "checks", "observed_activity",
    "usage", "public_provenance", "approved_source_url", "limitations",
})


def _object(value, keys, label):
    if type(value) is not dict or value.keys() != set(keys):
        raise ValueError(f"{label}: unexpected or missing fields")
    return value


def _text(value, label, limit=240):
    if (type(value) is not str or not value.strip() or len(value) > limit
            or any(unicodedata.category(char) in {"Cc", "Cf", "Cs", "Zl", "Zp"} for char in value)):
        raise ValueError(f"{label}: expected bounded, nonempty single-line text")
    return value


def _enum(value, choices, label):
    if type(value) is not str or value not in choices:
        raise ValueError(f"{label}: invalid value")
    return value


def _count(value, label):
    if value is not None and (type(value) is not int or not 0 <= value <= MAX_COUNT):
        raise ValueError(f"{label}: expected a bounded nonnegative integer or null")
    return value


def _amount(value, label):
    if value is not None and (type(value) not in (int, float)
                              or not 0 <= value <= MAX_COUNT or not math.isfinite(value)):
        raise ValueError(f"{label}: expected a bounded finite amount or null")
    return value


def _hash(value, length, label):
    if value is not None and (type(value) is not str
                             or re.fullmatch(f"[0-9a-f]{{{length}}}", value) is None):
        raise ValueError(f"{label}: invalid hash")
    return value


def source_url(value):
    """Admit only ordinary public HTTPS links; never resolve or fetch them."""
    if value is None:
        return None
    _text(value, "source URL", 500)
    if any(char.isspace() for char in value) or "\\" in value or "%" in value:
        raise ValueError("source URL: ambiguous encoding is not accepted")
    try:
        parts = urlsplit(value)
        host = parts.hostname or ""
        if (parts.scheme != "https" or parts.username is not None or parts.password is not None
                or parts.port not in (None, 443) or parts.query or parts.fragment
                or re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?", host) is None
                or "." not in host or ".." in host or host.endswith((".local", ".localhost", ".internal", ".test", ".invalid"))
                or any(piece in {".", ".."} for piece in parts.path.split("/"))):
            raise ValueError("source URL: expected a public HTTPS URL without credentials or query")
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            raise ValueError("source URL: IP literals are not accepted")
    except (ValueError, UnicodeError) as exc:
        raise ValueError("source URL: invalid public link") from exc
    return value


def admit_record(value: object) -> dict:
    """Construct a fresh allowlisted record; it is not approved for output yet.

    Text is still untrusted and must be escaped at rendering. A human must
    review its meaning/privacy before approving this exact payload.
    """
    v = _object(value, RECORD_KEYS, "record")
    _enum(v["schema_version"], {"libreevolve.public_result.v1"}, "schema")
    public_id = v["public_result_id"]
    if type(public_id) is not str or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", public_id) is None:
        raise ValueError("public_result_id must be a public slug, not a private run path")
    result = {
        "schema_version": v["schema_version"], "public_result_id": public_id,
        "product_status": _enum(v["product_status"], {"engineering preview"}, "product status"),
        "evidence_class": _enum(v["evidence_class"], {"synthetic_fixture", "observed_local_checks"}, "evidence class"),
        "run_status": _enum(v["run_status"], {"completed", "aborted", "incomplete", "unknown"}, "run status"),
        "selected_source": _enum(v["selected_source"], {"workspace", "history", "unknown"}, "selected source"),
        "candidate_retention": _enum(v["candidate_retention"], {"retained", "not_established", "unknown"}, "retention"),
        "baseline": admit_metrics(v["baseline"]), "candidate": admit_metrics(v["candidate"]),
    }
    checks = v["checks"]
    if type(checks) is not list or len(checks) > 16:
        raise ValueError("checks: expected at most 16 named checks")
    result["checks"] = []
    for check in checks:
        c = _object(check, {"name", "split", "status"}, "check")
        result["checks"].append({
            "name": _text(c["name"], "check name", 80),
            "split": _enum(c["split"], {"training", "holdout"}, "check split"),
            "status": _enum(c["status"], {"passed", "failed", "incomplete", "unknown"}, "check status"),
        })
    activity = _object(v["observed_activity"], {"calls", "elapsed_seconds"}, "activity")
    result["observed_activity"] = {"calls": _count(activity["calls"], "calls"),
                                   "elapsed_seconds": _amount(activity["elapsed_seconds"], "elapsed time")}
    usage = _object(v["usage"], {"tokens", "cost_usd", "status"}, "usage")
    result["usage"] = {"tokens": _count(usage["tokens"], "tokens"),
                       "cost_usd": _amount(usage["cost_usd"], "cost"),
                       "status": _enum(usage["status"], {"complete", "partial", "unknown"}, "usage status")}
    if usage["status"] == "complete" and (usage["tokens"] is None or usage["cost_usd"] is None):
        raise ValueError("complete usage requires both amounts; missing is unknown")
    if usage["status"] == "unknown" and (usage["tokens"] is not None or usage["cost_usd"] is not None):
        raise ValueError("unknown usage cannot contain known amounts; use partial")
    provenance = _object(v["public_provenance"], {"source_commit", "candidate_sha256", "validator_sha256"}, "provenance")
    result["public_provenance"] = {key: _hash(provenance[key], 40 if key == "source_commit" else 64, key)
                                   for key in sorted(provenance)}
    result["approved_source_url"] = source_url(v["approved_source_url"])
    limitations = v["limitations"]
    if type(limitations) is not list or not 1 <= len(limitations) <= 12:
        raise ValueError("limitations: require one to twelve explicit limitations")
    result["limitations"] = [_text(item, "limitation") for item in limitations]
    if len(canonical_bytes(result)) > MAX_RECORD_BYTES:
        raise ValueError("record exceeds public size limit")
    return result


def canonical_bytes(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def payload_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(admit_record(value))).hexdigest()


def approve_record(value: object, *, approved_sha256: str, approved_by: str,
                   approve_source_link: bool = False) -> tuple[dict, dict]:
    """Bind affirmative local approval to every public byte, including hashes.

    The returned receipt contains operator identity: keep it private. A source
    link needs a separate affirmative flag. No source code is ever accepted.
    """
    record = admit_record(value)
    digest = hashlib.sha256(canonical_bytes(record)).hexdigest()
    if type(approved_sha256) is not str or approved_sha256 != digest:
        raise ValueError("approval does not match this exact public payload")
    _text(approved_by, "approver", 80)
    if type(approve_source_link) is not bool:
        raise ValueError("source link approval must be boolean")
    if record["approved_source_url"] is not None and not approve_source_link:
        raise ValueError("source publication requires separate explicit approval")
    receipt = {"payload_sha256": digest, "approved_by": approved_by,
               "source_link_approved": approve_source_link,
               "scope": "local rendering only; no upload or independent authentication"}
    return record, receipt


def comparison(value: object) -> dict:
    record = admit_record(value)
    return compare_metrics(record["baseline"], record["candidate"])
