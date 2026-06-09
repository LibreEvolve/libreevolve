from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_THEORETICAL_CS_SOURCE_SCHEMA = (
    "libreevolve.alphaevolve_theoretical_cs_source.v1"
)
ALPHAEVOLVE_THEORETICAL_CS_SOURCE_MANIFEST_SCHEMA = (
    "libreevolve.alphaevolve_theoretical_cs_source_manifest.v1"
)
EXPECTED_THEORETICAL_CS_SOURCE_MANIFEST_FILE = "papers/theoretical_cs_sources.json"
EXPECTED_THEORETICAL_CS_ARXIV_ID = "2509.18057"
EXPECTED_THEORETICAL_CS_VERSION = 7
EXPECTED_THEORETICAL_CS_VERSIONED_ID = "2509.18057v7"
EXPECTED_THEORETICAL_CS_TITLE = (
    "Reinforced Generation of Combinatorial Structures: Hardness of Approximation"
)
EXPECTED_THEORETICAL_CS_SUBMITTED_DATE = "2025-09-22T17:30:33+00:00"
EXPECTED_THEORETICAL_CS_REVISED_DATE = "2026-03-09T21:00:18+00:00"
EXPECTED_THEORETICAL_CS_AUTHORS = (
    "Ansh Nagda",
    "Prabhakar Raghavan",
    "Abhradeep Thakurta",
)
EXPECTED_THEORETICAL_CS_ARTICLE_URL = (
    "https://research.google/blog/ai-as-a-research-partner-"
    "advancing-theoretical-computer-science-with-alphaevolve/"
)
EXPECTED_THEORETICAL_CS_ARTICLE_TITLE = (
    "AI as a research partner: Advancing theoretical computer science with AlphaEvolve"
)
EXPECTED_THEORETICAL_CS_ARTICLE_DATE = "2025-09-30"
EXPECTED_THEORETICAL_CS_ARTICLE_AUTHORS = (
    "Ansh Nagda",
    "Abhradeep Thakurta",
    "Prabhakar Raghavan",
)
EXPECTED_THEORETICAL_CS_ARTICLE_BYTES = 179266
EXPECTED_THEORETICAL_CS_ARTICLE_SHA256 = (
    "79a54f404ac1e1e919682e7b109ede01b02e7fc002551d7964474b658bde4721"
)
EXPECTED_THEORETICAL_CS_ABS_BYTES = 50195
EXPECTED_THEORETICAL_CS_ABS_SHA256 = (
    "afc6f0deeaa3d86a7f5db9e04135fc2bbb081454a3eb02f084dedcb557c5dc0b"
)
EXPECTED_THEORETICAL_CS_PDF_FILE = "papers/2509.18057__Hardness_of_Approximation.pdf"
EXPECTED_THEORETICAL_CS_PDF_BYTES = 7719868
EXPECTED_THEORETICAL_CS_PDF_SHA256 = (
    "32eb8c787527bf8674ec22fd08ee6e1108179e88d97300e110286270c041e842"
)
EXPECTED_THEORETICAL_CS_CATEGORIES = (
    "proof_element_application",
    "lifting_framework",
    "verification_speedup",
    "final_independent_verification",
    "artifact_inventory_gap",
)
EXPECTED_THEORETICAL_CS_SURFACES = {
    "README.md",
    "ROADMAP.md",
    "papers/README.md",
    "docs/todo/code.md",
    "docs/todo/papers.md",
    "docs/todo/readme.md",
    "docs/todo/roadmap.md",
}
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class AlphaEvolveTheoreticalCsIssue:
    code: str
    message: str
    source_id: str | None = None


@dataclass(frozen=True)
class AlphaEvolveTheoreticalCsValidation:
    ok: bool
    source_count: int
    application_count: int
    local_pdf_cache_available: bool
    proof_element_boundary: bool
    issues: list[AlphaEvolveTheoreticalCsIssue]


def alphaevolve_theoretical_cs_source_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_THEORETICAL_CS_SOURCE_SCHEMA,
        "source_family": "alphaevolve_theoretical_cs_proof_elements",
        "source_paper_id": EXPECTED_THEORETICAL_CS_ARXIV_ID,
        "article": {
            "title": EXPECTED_THEORETICAL_CS_ARTICLE_TITLE,
            "url": EXPECTED_THEORETICAL_CS_ARTICLE_URL,
            "date": EXPECTED_THEORETICAL_CS_ARTICLE_DATE,
            "authors": list(EXPECTED_THEORETICAL_CS_ARTICLE_AUTHORS),
            "retrieval": {
                "retrieved_on": "2026-06-09",
                "html_bytes": EXPECTED_THEORETICAL_CS_ARTICLE_BYTES,
                "html_sha256": EXPECTED_THEORETICAL_CS_ARTICLE_SHA256,
                "hash_algorithm": "sha256",
            },
        },
        "paper": {
            "arxiv_id": EXPECTED_THEORETICAL_CS_ARXIV_ID,
            "version": EXPECTED_THEORETICAL_CS_VERSION,
            "versioned_id": EXPECTED_THEORETICAL_CS_VERSIONED_ID,
            "title": EXPECTED_THEORETICAL_CS_TITLE,
            "authors": list(EXPECTED_THEORETICAL_CS_AUTHORS),
            "submitted_date": EXPECTED_THEORETICAL_CS_SUBMITTED_DATE,
            "latest_revision_date": EXPECTED_THEORETICAL_CS_REVISED_DATE,
            "abs_url": f"https://arxiv.org/abs/{EXPECTED_THEORETICAL_CS_ARXIV_ID}",
            "versioned_abs_url": (
                f"https://arxiv.org/abs/{EXPECTED_THEORETICAL_CS_VERSIONED_ID}"
            ),
            "pdf_url": f"https://arxiv.org/pdf/{EXPECTED_THEORETICAL_CS_ARXIV_ID}.pdf",
            "doi": f"10.48550/arXiv.{EXPECTED_THEORETICAL_CS_ARXIV_ID}",
            "subjects": ["cs.LG", "cs.AI", "cs.CC", "math.CO"],
            "abs_snapshot": {
                "retrieved_on": "2026-06-09",
                "html_bytes": EXPECTED_THEORETICAL_CS_ABS_BYTES,
                "html_sha256": EXPECTED_THEORETICAL_CS_ABS_SHA256,
                "hash_algorithm": "sha256",
            },
            "local_cache": {
                "available": True,
                "manifest_row_present": True,
                "file": EXPECTED_THEORETICAL_CS_PDF_FILE,
                "bytes": EXPECTED_THEORETICAL_CS_PDF_BYTES,
                "sha256": EXPECTED_THEORETICAL_CS_PDF_SHA256,
            },
        },
        "source_claims": {
            "alphaevolve_llm_code_mutation_agent": True,
            "finite_structures_as_proof_elements": True,
            "proof_elements_not_full_proofs": True,
            "lifting_framework_required": True,
            "automatically_verified_proof_elements": True,
            "final_bruteforce_verification_required": True,
            "verifier_speedup_claim": "up_to_10000x",
        },
        "applications": [
            {
                "application_id": "max_k_cut_gadget_reductions",
                "source_surface": "article_and_arxiv",
                "problem_ids": ["MAX-4-CUT", "MAX-3-CUT"],
                "artifact_types": ["gadget_reduction", "weighted_graph"],
                "reported_results": [
                    "MAX-4-CUT hardness factor 0.987",
                    "MAX-3-CUT hardness factor 0.9649",
                ],
                "local_artifact_inventory_available": False,
            },
            {
                "application_id": "average_case_random_graph_certification",
                "source_surface": "article_and_arxiv",
                "problem_ids": ["MAX-CUT", "MAX-Independent Set"],
                "artifact_types": ["Ramanujan graph", "finite graph certificate"],
                "reported_results": [
                    "Ramanujan graphs on as many as 163 vertices",
                    "upper and lower bounds match to the third decimal place",
                ],
                "local_artifact_inventory_available": False,
            },
            {
                "application_id": "metric_tsp_gadget_reduction",
                "source_surface": "arxiv_v7",
                "problem_ids": ["metric Traveling Salesman Problem"],
                "artifact_types": ["gadget_reduction"],
                "reported_results": ["TSP hardness factor 111/110"],
                "local_artifact_inventory_available": False,
            },
        ],
        "claim_boundaries": {
            "not_original_alphaevolve_specification": True,
            "not_constructive_math_67_problem_source": True,
            "not_formal_theorem_prover": True,
            "not_local_graph_certification_benchmark": True,
            "local_graph_or_gadget_artifacts_absent": True,
            "source_code_or_repository_not_pinned": True,
            "proof_claims_require_external_paper_and_artifacts": True,
        },
        "claim_categories": list(EXPECTED_THEORETICAL_CS_CATEGORIES),
        "remaining_work": [
            "locate_or_pin_source_repository_or_artifact_archive",
            "inventory_graph_and_gadget_artifacts",
            "record_alphaevolve_search_code_and_verifier_code",
            "record_original_bruteforce_verifier_provenance",
            "add_local_graph_certification_benchmarks",
        ],
    }


def alphaevolve_theoretical_cs_source_manifest_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_THEORETICAL_CS_SOURCE_MANIFEST_SCHEMA,
        "theoretical_cs_source_count": 1,
        "sources": [
            {
                "manifest_row_id": EXPECTED_THEORETICAL_CS_ARXIV_ID,
                "theoretical_cs_source_id": EXPECTED_THEORETICAL_CS_VERSIONED_ID,
                "source_record": alphaevolve_theoretical_cs_source_record(),
                "claim_artifact_links": {
                    "theoretical_cs_source_used_by": sorted(EXPECTED_THEORETICAL_CS_SURFACES),
                    "policy": (
                        "theoretical_cs_proof_element_claims_require_paper_"
                        "article_artifact_and_verifier_boundaries"
                    ),
                },
                "evidence_policy": {
                    "local_pdf_cache_required": True,
                    "graph_or_gadget_artifacts_required_for_benchmark_claims": True,
                    "publication_ready_without_artifact_inventory": False,
                    "scope": (
                        "theoretical-CS proof-element source evidence, not original "
                        "AlphaEvolve specification or constructive-math source coverage"
                    ),
                },
            }
        ],
    }


def validate_alphaevolve_theoretical_cs_source(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveTheoreticalCsValidation:
    data, read_issues = _load_theoretical_cs_recordset(recordset)
    if read_issues:
        return AlphaEvolveTheoreticalCsValidation(False, 0, 0, False, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveTheoreticalCsIssue] = []
    if data.get("schema") != ALPHAEVOLVE_THEORETICAL_CS_SOURCE_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported theoretical-CS source schema"))
    if data.get("source_family") != "alphaevolve_theoretical_cs_proof_elements":
        issues.append(_issue("invalid_source_family", "source_family must identify theoretical-CS proof elements"))
    if data.get("source_paper_id") != EXPECTED_THEORETICAL_CS_ARXIV_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2509.18057"))
    _validate_article(data.get("article"), issues)
    local_pdf_cache_available = _validate_paper(data.get("paper"), issues)
    _validate_source_claims(data.get("source_claims"), issues)
    application_count = _validate_applications(data.get("applications"), issues)
    proof_element_boundary = _validate_claim_boundaries(data.get("claim_boundaries"), issues)
    _validate_claim_categories(data.get("claim_categories"), issues)
    _validate_remaining_work(data.get("remaining_work"), issues)
    return AlphaEvolveTheoreticalCsValidation(
        ok=not issues,
        source_count=2 if isinstance(data.get("article"), dict) and isinstance(data.get("paper"), dict) else 0,
        application_count=application_count,
        local_pdf_cache_available=local_pdf_cache_available,
        proof_element_boundary=proof_element_boundary,
        issues=issues,
    )


def validate_alphaevolve_theoretical_cs_source_manifest(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveTheoreticalCsValidation:
    data, read_issues = _load_theoretical_cs_manifest_recordset(recordset)
    if read_issues:
        return AlphaEvolveTheoreticalCsValidation(False, 0, 0, False, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveTheoreticalCsIssue] = []
    if data.get("schema") != ALPHAEVOLVE_THEORETICAL_CS_SOURCE_MANIFEST_SCHEMA:
        issues.append(_issue("invalid_manifest_schema", "unsupported theoretical-CS source manifest schema"))
    sources = data.get("sources")
    if not isinstance(sources, list):
        issues.append(_issue("invalid_manifest_sources", "theoretical-CS manifest sources must be a list"))
        sources = []
    source_count = len(sources)
    if data.get("theoretical_cs_source_count") != source_count:
        issues.append(_issue("invalid_source_count", "theoretical_cs_source_count must equal the number of source records"))
    if source_count != 1:
        issues.append(_issue("invalid_manifest_source_count", "theoretical-CS manifest must contain the arXiv/article source row"))
    application_count = 0
    local_pdf_cache_available = False
    proof_element_boundary = False
    for index, source in enumerate(sources):
        report = _validate_manifest_source(source, issues, index)
        application_count += report.application_count
        local_pdf_cache_available = (
            local_pdf_cache_available or report.local_pdf_cache_available
        )
        proof_element_boundary = proof_element_boundary or report.proof_element_boundary
    return AlphaEvolveTheoreticalCsValidation(
        ok=not issues,
        source_count=source_count,
        application_count=application_count,
        local_pdf_cache_available=local_pdf_cache_available,
        proof_element_boundary=proof_element_boundary,
        issues=issues,
    )


def _load_theoretical_cs_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveTheoreticalCsIssue]]:
    if recordset is None:
        return alphaevolve_theoretical_cs_source_record(), []
    return _load_recordset(recordset)


def _load_theoretical_cs_manifest_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveTheoreticalCsIssue]]:
    if recordset is None:
        return alphaevolve_theoretical_cs_source_manifest_record(), []
    return _load_recordset(recordset)


def _load_recordset(
    recordset: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveTheoreticalCsIssue]]:
    if isinstance(recordset, dict):
        return recordset, []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_recordset", f"could not read theoretical-CS source recordset: {exc}")]
        if not isinstance(data, dict):
            return None, [_issue("invalid_recordset", "theoretical-CS source recordset must be a JSON object")]
        return data, []
    return None, [_issue("invalid_recordset", "theoretical-CS source recordset must be an object or path")]


def _validate_article(
    value: object,
    issues: list[AlphaEvolveTheoreticalCsIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_article", "article must be an object"))
        return
    expected = {
        "title": EXPECTED_THEORETICAL_CS_ARTICLE_TITLE,
        "url": EXPECTED_THEORETICAL_CS_ARTICLE_URL,
        "date": EXPECTED_THEORETICAL_CS_ARTICLE_DATE,
        "authors": list(EXPECTED_THEORETICAL_CS_ARTICLE_AUTHORS),
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_article_{field}", f"article.{field} must match the Google Research source"))
    retrieval = value.get("retrieval")
    if not isinstance(retrieval, dict):
        issues.append(_issue("invalid_article_retrieval", "article.retrieval must be an object"))
        return
    expected_retrieval = {
        "retrieved_on": "2026-06-09",
        "html_bytes": EXPECTED_THEORETICAL_CS_ARTICLE_BYTES,
        "html_sha256": EXPECTED_THEORETICAL_CS_ARTICLE_SHA256,
        "hash_algorithm": "sha256",
    }
    _validate_expected_fields(retrieval, expected_retrieval, "article_retrieval", issues)


def _validate_paper(
    value: object,
    issues: list[AlphaEvolveTheoreticalCsIssue],
) -> bool:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_paper", "paper must be an object"))
        return False
    expected = {
        "arxiv_id": EXPECTED_THEORETICAL_CS_ARXIV_ID,
        "version": EXPECTED_THEORETICAL_CS_VERSION,
        "versioned_id": EXPECTED_THEORETICAL_CS_VERSIONED_ID,
        "title": EXPECTED_THEORETICAL_CS_TITLE,
        "authors": list(EXPECTED_THEORETICAL_CS_AUTHORS),
        "submitted_date": EXPECTED_THEORETICAL_CS_SUBMITTED_DATE,
        "latest_revision_date": EXPECTED_THEORETICAL_CS_REVISED_DATE,
        "abs_url": f"https://arxiv.org/abs/{EXPECTED_THEORETICAL_CS_ARXIV_ID}",
        "versioned_abs_url": f"https://arxiv.org/abs/{EXPECTED_THEORETICAL_CS_VERSIONED_ID}",
        "pdf_url": f"https://arxiv.org/pdf/{EXPECTED_THEORETICAL_CS_ARXIV_ID}.pdf",
        "doi": f"10.48550/arXiv.{EXPECTED_THEORETICAL_CS_ARXIV_ID}",
        "subjects": ["cs.LG", "cs.AI", "cs.CC", "math.CO"],
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_paper_{field}", f"paper.{field} must match arXiv 2509.18057v7"))
    abs_snapshot = value.get("abs_snapshot")
    if not isinstance(abs_snapshot, dict):
        issues.append(_issue("invalid_abs_snapshot", "paper.abs_snapshot must be an object"))
    else:
        expected_abs = {
            "retrieved_on": "2026-06-09",
            "html_bytes": EXPECTED_THEORETICAL_CS_ABS_BYTES,
            "html_sha256": EXPECTED_THEORETICAL_CS_ABS_SHA256,
            "hash_algorithm": "sha256",
        }
        _validate_expected_fields(abs_snapshot, expected_abs, "abs_snapshot", issues)
    cache = value.get("local_cache")
    if not isinstance(cache, dict):
        issues.append(_issue("invalid_local_cache", "paper.local_cache must be an object"))
        return False
    expected_cache = {
        "available": True,
        "manifest_row_present": True,
        "file": EXPECTED_THEORETICAL_CS_PDF_FILE,
        "bytes": EXPECTED_THEORETICAL_CS_PDF_BYTES,
        "sha256": EXPECTED_THEORETICAL_CS_PDF_SHA256,
    }
    _validate_expected_fields(cache, expected_cache, "local_cache", issues)
    return cache.get("available") is True


def _validate_source_claims(
    value: object,
    issues: list[AlphaEvolveTheoreticalCsIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_source_claims", "source_claims must be an object"))
        return
    expected = {
        "alphaevolve_llm_code_mutation_agent": True,
        "finite_structures_as_proof_elements": True,
        "proof_elements_not_full_proofs": True,
        "lifting_framework_required": True,
        "automatically_verified_proof_elements": True,
        "final_bruteforce_verification_required": True,
        "verifier_speedup_claim": "up_to_10000x",
    }
    _validate_expected_fields(value, expected, "source_claims", issues)


def _validate_applications(
    value: object,
    issues: list[AlphaEvolveTheoreticalCsIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_applications", "applications must be a list"))
        return 0
    expected_ids = {
        "max_k_cut_gadget_reductions",
        "average_case_random_graph_certification",
        "metric_tsp_gadget_reduction",
    }
    ids = {item.get("application_id") for item in value if isinstance(item, dict)}
    if ids != expected_ids:
        issues.append(_issue("application_id_mismatch", "applications must preserve MAX-k-CUT, random-graph, and TSP source rows"))
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_application", "application entries must be objects"))
            continue
        for field in ("application_id", "source_surface"):
            if not isinstance(item.get(field), str) or not item[field]:
                issues.append(_issue(f"invalid_application_{field}", f"application.{field} must be a non-empty string"))
        for field in ("problem_ids", "artifact_types", "reported_results"):
            if not isinstance(item.get(field), list) or not all(isinstance(entry, str) for entry in item[field]):
                issues.append(_issue(f"invalid_application_{field}", f"application.{field} must list source strings"))
        if item.get("local_artifact_inventory_available") is not False:
            issues.append(_issue("application_artifact_inventory_overclaim", "local artifact inventories must remain absent in this source-tracking slice"))
    return len(value)


def _validate_claim_boundaries(
    value: object,
    issues: list[AlphaEvolveTheoreticalCsIssue],
) -> bool:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_claim_boundaries", "claim_boundaries must be an object"))
        return False
    expected = {
        "not_original_alphaevolve_specification": True,
        "not_constructive_math_67_problem_source": True,
        "not_formal_theorem_prover": True,
        "not_local_graph_certification_benchmark": True,
        "local_graph_or_gadget_artifacts_absent": True,
        "source_code_or_repository_not_pinned": True,
        "proof_claims_require_external_paper_and_artifacts": True,
    }
    _validate_expected_fields(value, expected, "claim_boundaries", issues)
    return value.get("proof_claims_require_external_paper_and_artifacts") is True


def _validate_claim_categories(
    value: object,
    issues: list[AlphaEvolveTheoreticalCsIssue],
) -> None:
    if value != list(EXPECTED_THEORETICAL_CS_CATEGORIES):
        issues.append(_issue("claim_category_mismatch", "claim_categories must preserve proof-element, lifting, verification, and artifact-gap taxonomy"))


def _validate_remaining_work(
    value: object,
    issues: list[AlphaEvolveTheoreticalCsIssue],
) -> None:
    expected = {
        "locate_or_pin_source_repository_or_artifact_archive",
        "inventory_graph_and_gadget_artifacts",
        "record_alphaevolve_search_code_and_verifier_code",
        "record_original_bruteforce_verifier_provenance",
        "add_local_graph_certification_benchmarks",
    }
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(_issue("invalid_remaining_work", "remaining_work must list source-tracking follow-ups"))
        return
    if set(value) != expected:
        issues.append(_issue("remaining_work_mismatch", "remaining_work must preserve artifact, verifier, and benchmark follow-ups"))


def _validate_manifest_source(
    value: object,
    issues: list[AlphaEvolveTheoreticalCsIssue],
    index: int,
) -> AlphaEvolveTheoreticalCsValidation:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_manifest_source", f"manifest source {index} must be an object"))
        return AlphaEvolveTheoreticalCsValidation(False, 0, 0, False, False, [])
    expected = {
        "manifest_row_id": EXPECTED_THEORETICAL_CS_ARXIV_ID,
        "theoretical_cs_source_id": EXPECTED_THEORETICAL_CS_VERSIONED_ID,
    }
    _validate_expected_fields(value, expected, "manifest", issues)
    report = validate_alphaevolve_theoretical_cs_source(value.get("source_record"))
    issues.extend(report.issues)
    _validate_claim_artifact_links(value.get("claim_artifact_links"), issues)
    _validate_evidence_policy(value.get("evidence_policy"), issues)
    return report


def _validate_claim_artifact_links(
    value: object,
    issues: list[AlphaEvolveTheoreticalCsIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_claim_artifact_links", "claim_artifact_links must be an object"))
        return
    surfaces = value.get("theoretical_cs_source_used_by")
    if not isinstance(surfaces, list) or not all(isinstance(item, str) for item in surfaces):
        issues.append(_issue("invalid_claim_surfaces", "theoretical_cs_source_used_by must list docs, papers, and active TODO surfaces"))
    elif set(surfaces) != EXPECTED_THEORETICAL_CS_SURFACES:
        issues.append(_issue("claim_surface_mismatch", "theoretical_cs_source_used_by must cover docs, papers, and active TODO evidence"))
    if value.get("policy") != (
        "theoretical_cs_proof_element_claims_require_paper_"
        "article_artifact_and_verifier_boundaries"
    ):
        issues.append(_issue("invalid_claim_policy", "claim policy must require article, paper, artifact, and verifier boundaries"))


def _validate_evidence_policy(
    value: object,
    issues: list[AlphaEvolveTheoreticalCsIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_evidence_policy", "evidence_policy must be an object"))
        return
    expected = {
        "local_pdf_cache_required": True,
        "graph_or_gadget_artifacts_required_for_benchmark_claims": True,
        "publication_ready_without_artifact_inventory": False,
    }
    _validate_expected_fields(value, expected, "evidence_policy", issues)
    scope = value.get("scope")
    if not isinstance(scope, str) or "not original AlphaEvolve specification" not in scope:
        issues.append(_issue("invalid_evidence_policy_scope", "evidence_policy.scope must distinguish later theoretical-CS evidence from the original specification"))


def _validate_expected_fields(
    value: dict[str, Any],
    expected: dict[str, Any],
    prefix: str,
    issues: list[AlphaEvolveTheoreticalCsIssue],
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_{prefix}_{field}", f"{prefix}.{field} must match pinned theoretical-CS source evidence"))
    for field in ("sha256", "html_sha256"):
        digest = value.get(field)
        if digest is not None and (not isinstance(digest, str) or _SHA256_RE.fullmatch(digest) is None):
            issues.append(_issue(f"invalid_{prefix}_{field}_format", f"{prefix}.{field} must be a SHA-256 digest"))


def _issue(code: str, message: str, source_id: str | None = None) -> AlphaEvolveTheoreticalCsIssue:
    return AlphaEvolveTheoreticalCsIssue(code, message, source_id)
