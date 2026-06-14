from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from typing import Any
from urllib.request import Request, urlopen

from libreevolve.problems.benchmarks.alphaevolve_current_version_boundary import (
    EXPECTED_CURRENT_ABS_BYTES,
    EXPECTED_CURRENT_ABS_CONTENT_TYPE,
    EXPECTED_CURRENT_ABS_SHA256,
    EXPECTED_CURRENT_ABS_STATUS,
    EXPECTED_CURRENT_ABS_URL,
    EXPECTED_FLOATING_PDF_BYTES,
    EXPECTED_FLOATING_PDF_CONTENT_TYPE,
    EXPECTED_FLOATING_PDF_SHA256,
    EXPECTED_FLOATING_PDF_STATUS,
    EXPECTED_FLOATING_PDF_URL,
)
from libreevolve.problems.benchmarks.alphaevolve_datacite_full_response_boundary import (
    EXPECTED_API_URL as EXPECTED_DATACITE_API_URL,
    EXPECTED_RESPONSE_BYTES as EXPECTED_DATACITE_BYTES,
    EXPECTED_RESPONSE_SHA256 as EXPECTED_DATACITE_SHA256,
)
from libreevolve.problems.benchmarks.alphaevolve_license_page_boundary import (
    EXPECTED_CONTENT_TYPE as EXPECTED_LICENSE_CONTENT_TYPE,
    EXPECTED_HTTP_STATUS as EXPECTED_LICENSE_STATUS,
    EXPECTED_LICENSE_URL,
    EXPECTED_RESPONSE_BYTES as EXPECTED_LICENSE_BYTES,
    EXPECTED_RESPONSE_SHA256 as EXPECTED_LICENSE_SHA256,
)
from libreevolve.problems.benchmarks.alphaevolve_tex_source_boundary import (
    EXPECTED_CONTENT_TYPE as EXPECTED_EPRINT_CONTENT_TYPE,
    EXPECTED_EPRINT_URL,
    EXPECTED_HTTP_STATUS as EXPECTED_EPRINT_STATUS,
    EXPECTED_RESPONSE_BYTES as EXPECTED_EPRINT_BYTES,
    EXPECTED_RESPONSE_SHA256 as EXPECTED_EPRINT_SHA256,
)
from libreevolve.problems.benchmarks.arxiv_abstract_snapshot import (
    EXPECTED_ABSTRACT_URL,
    EXPECTED_CONTENT_TYPE as EXPECTED_VERSIONED_ABS_CONTENT_TYPE,
    EXPECTED_HTML_BYTES as EXPECTED_VERSIONED_ABS_BYTES,
    EXPECTED_HTML_SHA256 as EXPECTED_VERSIONED_ABS_SHA256,
)


REPORT_SCHEMA = "libreevolve.alphaevolve_source_refresh_gate_report.v1"
USER_AGENT = "LibreEvolve source refresh gate (+https://github.com/romgenie/libreevolve)"


@dataclass(frozen=True)
class SourceExpectation:
    source_id: str
    url: str
    expected_status: int
    expected_content_type: str
    expected_bytes: int
    expected_sha256: str


def source_expectations() -> list[dict[str, Any]]:
    """Return the pinned AlphaEvolve source responses checked by the gate."""

    return [
        _expectation(
            "versioned_abstract",
            EXPECTED_ABSTRACT_URL,
            200,
            EXPECTED_VERSIONED_ABS_CONTENT_TYPE,
            EXPECTED_VERSIONED_ABS_BYTES,
            EXPECTED_VERSIONED_ABS_SHA256,
        ),
        _expectation(
            "current_abstract",
            EXPECTED_CURRENT_ABS_URL,
            EXPECTED_CURRENT_ABS_STATUS,
            EXPECTED_CURRENT_ABS_CONTENT_TYPE,
            EXPECTED_CURRENT_ABS_BYTES,
            EXPECTED_CURRENT_ABS_SHA256,
        ),
        _expectation(
            "floating_pdf",
            EXPECTED_FLOATING_PDF_URL,
            EXPECTED_FLOATING_PDF_STATUS,
            EXPECTED_FLOATING_PDF_CONTENT_TYPE,
            EXPECTED_FLOATING_PDF_BYTES,
            EXPECTED_FLOATING_PDF_SHA256,
        ),
        _expectation(
            "datacite_api",
            EXPECTED_DATACITE_API_URL,
            200,
            "application/json",
            EXPECTED_DATACITE_BYTES,
            EXPECTED_DATACITE_SHA256,
        ),
        _expectation(
            "eprint_archive",
            EXPECTED_EPRINT_URL,
            EXPECTED_EPRINT_STATUS,
            EXPECTED_EPRINT_CONTENT_TYPE,
            EXPECTED_EPRINT_BYTES,
            EXPECTED_EPRINT_SHA256,
        ),
        _expectation(
            "license_page",
            EXPECTED_LICENSE_URL,
            EXPECTED_LICENSE_STATUS,
            EXPECTED_LICENSE_CONTENT_TYPE,
            EXPECTED_LICENSE_BYTES,
            EXPECTED_LICENSE_SHA256,
        ),
    ]


def compare_source_snapshots(
    live_snapshots: dict[str, dict[str, Any]],
    *,
    expectations: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compare live source snapshots against pinned AlphaEvolve expectations."""

    expected = source_expectations() if expectations is None else expectations
    checks = []
    for expectation in expected:
        source_id = expectation["source_id"]
        live = live_snapshots.get(source_id)
        if not isinstance(live, dict):
            checks.append(
                {
                    "source_id": source_id,
                    "ok": False,
                    "issues": ["missing_live_snapshot"],
                }
            )
            continue
        checks.append(_compare_one(expectation, live))
    return {
        "schema": REPORT_SCHEMA,
        "mode": "provided_snapshots",
        "source_count": len(expected),
        "ok": all(check["ok"] is True for check in checks),
        "checks": checks,
        "claim_boundary": (
            "Compares live response status, content type, byte count, and "
            "SHA-256 digest against committed AlphaEvolve source boundaries."
        ),
    }


def fetch_live_source_snapshots(timeout: float = 30.0) -> dict[str, dict[str, Any]]:
    """Fetch current network snapshots for the AlphaEvolve source URLs."""

    snapshots = {}
    for expectation in source_expectations():
        snapshots[expectation["source_id"]] = _fetch_one(expectation["url"], timeout)
    return snapshots


def run_refresh_gate(*, live: bool = False, timeout: float = 30.0) -> dict[str, Any]:
    """Run the refresh gate in live-network or fixture mode."""

    if live:
        report = compare_source_snapshots(fetch_live_source_snapshots(timeout=timeout))
        report["mode"] = "live_network"
        return report
    snapshots = {
        expectation["source_id"]: {
            "status": expectation["expected_status"],
            "content_type": expectation["expected_content_type"],
            "bytes": expectation["expected_bytes"],
            "sha256": expectation["expected_sha256"],
        }
        for expectation in source_expectations()
    }
    return compare_source_snapshots(snapshots)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail when AlphaEvolve live source metadata drifts from committed boundaries."
    )
    parser.add_argument("--live", action="store_true", help="fetch live source URLs")
    parser.add_argument("--timeout", type=float, default=30.0, help="network timeout seconds")
    parser.add_argument("--fixture-json", help="compare snapshots from a JSON file")
    parser.add_argument("--pretty", action="store_true", help="indent JSON output")
    args = parser.parse_args(argv)
    if args.fixture_json:
        with open(args.fixture_json, encoding="utf-8") as handle:
            snapshots = json.load(handle)
        report = compare_source_snapshots(snapshots)
        report["mode"] = "fixture_json"
    else:
        report = run_refresh_gate(live=args.live, timeout=args.timeout)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if report["ok"] else 1


def _expectation(
    source_id: str,
    url: str,
    status: int,
    content_type: str,
    bytes_value: int,
    sha256: str,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "url": url,
        "expected_status": status,
        "expected_content_type": content_type,
        "expected_bytes": bytes_value,
        "expected_sha256": sha256,
    }


def _compare_one(expectation: dict[str, Any], live: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if live.get("status") != expectation["expected_status"]:
        issues.append("status_drift")
    content_type = live.get("content_type")
    if not isinstance(content_type, str) or not content_type.startswith(
        expectation["expected_content_type"]
    ):
        issues.append("content_type_drift")
    if live.get("bytes") != expectation["expected_bytes"]:
        issues.append("bytes_drift")
    if live.get("sha256") != expectation["expected_sha256"]:
        issues.append("sha256_drift")
    if live.get("error"):
        issues.append("fetch_error")
    return {
        "source_id": expectation["source_id"],
        "url": expectation["url"],
        "ok": not issues,
        "issues": issues,
        "expected": {
            "status": expectation["expected_status"],
            "content_type": expectation["expected_content_type"],
            "bytes": expectation["expected_bytes"],
            "sha256": expectation["expected_sha256"],
        },
        "observed": {
            "status": live.get("status"),
            "content_type": live.get("content_type"),
            "bytes": live.get("bytes"),
            "sha256": live.get("sha256"),
        },
    }


def _fetch_one(url: str, timeout: float) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            data = response.read()
            content_type = response.headers.get("content-type", "")
            return {
                "status": response.status,
                "final_url": response.geturl(),
                "content_type": content_type,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
    except Exception as exc:  # pragma: no cover - network errors vary.
        return {"status": None, "content_type": "", "bytes": 0, "sha256": "", "error": type(exc).__name__}


if __name__ == "__main__":
    raise SystemExit(main())
