from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SORTING_NETWORK_SOURCE_CITATION_BOUNDARY_SCHEMA = (
    "libreevolve.sorting_network_source_citation_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_PROBLEM_IDS = ("sorting_network_8", "sorting_network_9")
EXPECTED_BOUNDARY_STATUS = "source_citations_recorded_without_run_certification"
EXPECTED_MISSING_EVIDENCE = {
    "local_source_snapshots": "not_recorded_locally",
    "independent_target_proof_extraction": "not_recorded_locally",
    "repeated_seed_run_tables": "not_recorded_locally",
    "target_hit_rate_summary": "not_recorded_locally",
    "run_tied_paper_certification": "not_recorded_locally",
}
EXPECTED_ZERO_ONE_URL = "https://bobson.ludost.net/books/algo/book6/chap28.htm"
EXPECTED_DOBBELAERE_URL = "https://bertdobbelaere.github.io/sorting_networks.html"
EXPECTED_CODISH_ARXIV_URL = "https://arxiv.org/abs/1405.5754"
EXPECTED_CODISH_DOI = "10.1016/j.jcss.2015.11.014"


@dataclass(frozen=True)
class SortingNetworkSourceCitationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SortingNetworkSourceCitationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    problem_count: int
    citation_count: int
    missing_evidence_count: int
    issues: list[SortingNetworkSourceCitationBoundaryIssue]


def sorting_network_source_citation_boundary_record() -> dict[str, Any]:
    """Return source citations for sorting-network benchmark calibration."""

    return {
        "schema": SORTING_NETWORK_SOURCE_CITATION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "problem_ids": list(EXPECTED_PROBLEM_IDS),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "citation_scope": (
            "Source citations calibrate the zero-one verifier and the 8- and "
            "9-input comparator targets only; they are not authenticated "
            "LibreEvolve run evidence."
        ),
        "source_citations": {
            "zero_one_principle": {
                "source": "CLRS sorting-network chapter mirror",
                "url": EXPECTED_ZERO_ONE_URL,
                "evidence": (
                    "Chapter 28.2 states that a network sorting all binary "
                    "inputs sorts arbitrary ordered inputs."
                ),
                "used_for": "exhaustive Boolean evaluator scope",
            },
            "sorting_network_8_target": {
                "target_comparators": 19,
                "sources": [
                    {
                        "source": "Peter Schneider-Kamp sorting network bounds",
                        "url": "https://imada.sdu.dk/u/petersk/sn/",
                        "evidence": (
                            "The table gives matching upper and lower bounds "
                            "of 19 comparators for n=8."
                        ),
                    },
                    {
                        "source": "Bert Dobbelaere sorting network list",
                        "url": EXPECTED_DOBBELAERE_URL,
                        "evidence": (
                            "The maintained list includes an 8-input network "
                            "with 19 comparators."
                        ),
                    },
                ],
                "used_for": "known target comparator check",
            },
            "sorting_network_9_target": {
                "target_comparators": 25,
                "sources": [
                    {
                        "source": "Codish et al. arXiv preprint",
                        "url": EXPECTED_CODISH_ARXIV_URL,
                        "doi": "10.48550/arXiv.1405.5754",
                        "evidence": (
                            "The abstract states that 24-comparator networks "
                            "do not exist and 25 comparators are optimal for "
                            "nine inputs."
                        ),
                    },
                    {
                        "source": "Codish et al. JCSS publication",
                        "url": "https://pure.itu.dk/en/publications/sorting-nine-inputs-requires-twenty-five-comparisons/",
                        "doi": EXPECTED_CODISH_DOI,
                        "evidence": (
                            "The publication record identifies the peer-"
                            "reviewed JCSS article and DOI for the nine-input "
                            "25-comparator optimality result."
                        ),
                    },
                    {
                        "source": "Bert Dobbelaere sorting network list",
                        "url": EXPECTED_DOBBELAERE_URL,
                        "evidence": (
                            "The maintained list includes a 9-input network "
                            "with 25 comparators."
                        ),
                    },
                ],
                "used_for": "known target comparator check",
            },
        },
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This sidecar records source citations for verifier and target "
            "calibration, but does not claim local source snapshots, "
            "independent proof extraction, repeated LibreEvolve runs, target "
            "hit-rate summaries, run-tied hardening, paper certification, or "
            "novel SOTA results."
        ),
    }


def validate_sorting_network_source_citation_boundary(
    boundary: object | str | Path | None = None,
) -> SortingNetworkSourceCitationBoundaryValidation:
    data, read_issues = _load_boundary(
        sorting_network_source_citation_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return SortingNetworkSourceCitationBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[SortingNetworkSourceCitationBoundaryIssue] = []
    if data.get("schema") != SORTING_NETWORK_SOURCE_CITATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported sorting-network source citation boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    problem_count = _validate_problem_ids(data.get("problem_ids"), issues)
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "source citations alone must not claim benchmark certification"))
    citation_count = _validate_source_citations(data.get("source_citations"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must preserve non-certification status"))
    return SortingNetworkSourceCitationBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        problem_count=problem_count,
        citation_count=citation_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_sorting_network_source_citation_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_sorting_network_source_citation_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Sorting-network source citation boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| problem_count | {validation.problem_count} |",
        f"| citation_count | {validation.citation_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[SortingNetworkSourceCitationBoundaryIssue]]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")]
    else:
        try:
            data = json.loads(Path(boundary).read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")]
    if isinstance(data, dict):
        return data, []
    return None, [_issue("invalid_shape", "sorting-network source citation boundary must be a JSON object")]


def _validate_problem_ids(
    value: object,
    issues: list[SortingNetworkSourceCitationBoundaryIssue],
) -> int:
    if value != list(EXPECTED_PROBLEM_IDS):
        issues.append(_issue("invalid_problem_ids", "problem_ids must list sorting_network_8 and sorting_network_9 in order"))
        return len(value) if isinstance(value, list) else 0
    return len(EXPECTED_PROBLEM_IDS)


def _validate_source_citations(
    value: object,
    issues: list[SortingNetworkSourceCitationBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_source_citations", "source_citations must be an object"))
        return 0
    expected_keys = {
        "zero_one_principle",
        "sorting_network_8_target",
        "sorting_network_9_target",
    }
    actual_keys = set(value)
    if actual_keys != expected_keys:
        issues.append(_issue("invalid_source_citation_keys", "source_citations must cover zero-one, n=8, and n=9 targets"))
    zero_one = value.get("zero_one_principle")
    if not isinstance(zero_one, dict) or zero_one.get("url") != EXPECTED_ZERO_ONE_URL:
        issues.append(_issue("invalid_zero_one_citation", "zero-one citation must point to the CLRS sorting-network chapter"))
    n8 = value.get("sorting_network_8_target")
    if not isinstance(n8, dict) or n8.get("target_comparators") != 19:
        issues.append(_issue("invalid_sorting_network_8_target", "sorting_network_8 target must be 19 comparators"))
    elif EXPECTED_DOBBELAERE_URL not in _source_urls(n8):
        issues.append(_issue("missing_sorting_network_8_network_list_citation", "sorting_network_8 target must cite the Dobbelaere network list"))
    n9 = value.get("sorting_network_9_target")
    if not isinstance(n9, dict) or n9.get("target_comparators") != 25:
        issues.append(_issue("invalid_sorting_network_9_target", "sorting_network_9 target must be 25 comparators"))
    else:
        urls = _source_urls(n9)
        dois = _source_dois(n9)
        if EXPECTED_CODISH_ARXIV_URL not in urls:
            issues.append(_issue("missing_sorting_network_9_arxiv_citation", "sorting_network_9 target must cite Codish et al. arXiv"))
        if EXPECTED_CODISH_DOI not in dois:
            issues.append(_issue("missing_sorting_network_9_jcss_doi", "sorting_network_9 target must cite the JCSS DOI"))
    return len(actual_keys)


def _validate_missing_evidence(
    value: object,
    issues: list[SortingNetworkSourceCitationBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    if actual_keys != expected_keys:
        issues.append(_issue("invalid_missing_evidence_keys", "missing_evidence must preserve the expected absence boundary"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _source_urls(citation: dict[str, Any]) -> set[str]:
    return {
        source.get("url")
        for source in citation.get("sources", [])
        if isinstance(source, dict) and isinstance(source.get("url"), str)
    }


def _source_dois(citation: dict[str, Any]) -> set[str]:
    return {
        source.get("doi")
        for source in citation.get("sources", [])
        if isinstance(source, dict) and isinstance(source.get("doi"), str)
    }


def _issue(code: str, message: str) -> SortingNetworkSourceCitationBoundaryIssue:
    return SortingNetworkSourceCitationBoundaryIssue(code, message)
