from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_OFFICIAL_BLOG_SOURCE_SCHEMA = (
    "libreevolve.alphaevolve_official_blog_source.v1"
)
ALPHAEVOLVE_OFFICIAL_BLOG_MANIFEST_SCHEMA = (
    "libreevolve.alphaevolve_official_blog_manifest.v1"
)
EXPECTED_OFFICIAL_BLOG_MANIFEST_FILE = "papers/official_deepmind_blog.json"
EXPECTED_OFFICIAL_BLOG_URL = (
    "https://deepmind.google/blog/"
    "alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/"
)
EXPECTED_OFFICIAL_BLOG_LEGACY_URL = (
    "https://deepmind.google/discover/blog/"
    "alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/"
)
EXPECTED_OFFICIAL_BLOG_TITLE = (
    "AlphaEvolve: A Gemini-powered coding agent for designing advanced algorithms"
)
EXPECTED_OFFICIAL_BLOG_DATE = "2025-05-14"
EXPECTED_OFFICIAL_BLOG_AUTHOR = "AlphaEvolve team"
EXPECTED_OFFICIAL_BLOG_SECTION = "Science"
EXPECTED_OFFICIAL_BLOG_BYTES = 151583
EXPECTED_OFFICIAL_BLOG_SHA256 = (
    "d1ea39bd7839134f917225330de16cd7399f494d1d3a677ef029b3d7d3d41c29"
)
EXPECTED_WHITEPAPER_URL = (
    "https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/"
    "alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/"
    "AlphaEvolve.pdf"
)
EXPECTED_COLAB_URL = (
    "https://colab.research.google.com/github/google-deepmind/alphaevolve_results/"
    "blob/master/mathematical_results.ipynb"
)
EXPECTED_EARLY_ACCESS_URL = "https://forms.gle/WyqAoh1ixdfq6tgN8"
EXPECTED_BLOG_CLAIM_IDS = (
    "architecture_gemini_evaluators_evolution",
    "whole_codebase_evolution",
    "borg_over_year_0_7_percent",
    "tpu_verilog_rewrite",
    "gemini_kernel_23_percent_training_1_percent",
    "kernel_engineering_weeks_to_days",
    "flashattention_32_5_percent",
    "matrix_4x4_complex_rank_48",
    "math_50_plus_75_percent_20_percent",
    "early_access_ui_availability",
    "announcement_and_illustration_roles",
)
EXPECTED_OFFICIAL_BLOG_SURFACES = {
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
class AlphaEvolveOfficialBlogIssue:
    code: str
    message: str
    source_id: str | None = None


@dataclass(frozen=True)
class AlphaEvolveOfficialBlogValidation:
    ok: bool
    source_count: int
    claim_count: int
    linked_whitepaper: bool
    announcement_boundary: bool
    issues: list[AlphaEvolveOfficialBlogIssue]


def alphaevolve_official_blog_source_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_OFFICIAL_BLOG_SOURCE_SCHEMA,
        "source_family": "alphaevolve_official_deepmind_announcement",
        "source_paper_id": "2506.13131",
        "article": {
            "title": EXPECTED_OFFICIAL_BLOG_TITLE,
            "url": EXPECTED_OFFICIAL_BLOG_URL,
            "legacy_url": EXPECTED_OFFICIAL_BLOG_LEGACY_URL,
            "date": EXPECTED_OFFICIAL_BLOG_DATE,
            "author": EXPECTED_OFFICIAL_BLOG_AUTHOR,
            "section": EXPECTED_OFFICIAL_BLOG_SECTION,
            "retrieval": {
                "retrieved_on": "2026-06-09",
                "html_bytes": EXPECTED_OFFICIAL_BLOG_BYTES,
                "html_sha256": EXPECTED_OFFICIAL_BLOG_SHA256,
                "hash_algorithm": "sha256",
            },
        },
        "linked_sources": {
            "whitepaper_url": EXPECTED_WHITEPAPER_URL,
            "whitepaper_id": "2506.13131",
            "mathematical_results_colab_url": EXPECTED_COLAB_URL,
            "alphaevolve_results_repository": "https://github.com/google-deepmind/alphaevolve_results",
            "early_access_form_url": EXPECTED_EARLY_ACCESS_URL,
        },
        "claim_variants": [
            {
                "claim_id": "architecture_gemini_evaluators_evolution",
                "source": "blog",
                "category": "architecture",
                "value": "Gemini models plus automated evaluators and evolutionary framework",
                "unit": "description",
                "reconciliation_status": "white_paper_aligned_summary",
            },
            {
                "claim_id": "whole_codebase_evolution",
                "source": "blog",
                "category": "scope",
                "value": "beyond single function discovery to evolve entire codebases",
                "unit": "description",
                "reconciliation_status": "announcement_scope_claim",
            },
            {
                "claim_id": "borg_over_year_0_7_percent",
                "source": "blog",
                "category": "systems_result",
                "value": 0.7,
                "unit": "percent_worldwide_compute_recovered",
                "reconciliation_status": "requires_white_paper_metric_mapping",
            },
            {
                "claim_id": "tpu_verilog_rewrite",
                "source": "blog",
                "category": "systems_result",
                "value": "Verilog rewrite for a TPU arithmetic circuit",
                "unit": "description",
                "reconciliation_status": "requires_white_paper_metric_mapping",
            },
            {
                "claim_id": "gemini_kernel_23_percent_training_1_percent",
                "source": "blog",
                "category": "systems_result",
                "value": "23% kernel speedup and 1% Gemini training-time reduction",
                "unit": "percent",
                "reconciliation_status": "requires_white_paper_metric_mapping",
            },
            {
                "claim_id": "kernel_engineering_weeks_to_days",
                "source": "blog",
                "category": "claim_variant",
                "value": "weeks of expert effort to days of automated experiments",
                "unit": "time_phrase",
                "whitepaper_variant": "months of engineering effort to days",
                "reconciliation_status": "blog_whitepaper_wording_variant",
            },
            {
                "claim_id": "flashattention_32_5_percent",
                "source": "blog",
                "category": "claim_variant",
                "value": 32.5,
                "unit": "percent_speedup",
                "whitepaper_variant": "32%",
                "reconciliation_status": "blog_whitepaper_value_variant",
            },
            {
                "claim_id": "matrix_4x4_complex_rank_48",
                "source": "blog",
                "category": "math_result",
                "value": "4x4 complex matrices using 48 scalar multiplications",
                "unit": "description",
                "reconciliation_status": "requires_white_paper_and_colab_mapping",
            },
            {
                "claim_id": "math_50_plus_75_percent_20_percent",
                "source": "blog",
                "category": "math_summary",
                "value": "over 50 problems; 75% rediscovered SOTA; 20% improved best known",
                "unit": "percent",
                "reconciliation_status": "requires_white_paper_and_colab_mapping",
            },
            {
                "claim_id": "early_access_ui_availability",
                "source": "blog",
                "category": "availability",
                "value": "Early Access Program for selected academic users and broader availability exploration",
                "unit": "description",
                "reconciliation_status": "blog_only_availability_statement",
            },
            {
                "claim_id": "announcement_and_illustration_roles",
                "source": "blog",
                "category": "acknowledgement",
                "value": "announcement feedback/help and illustration/figure contributors",
                "unit": "role_metadata",
                "reconciliation_status": "blog_only_role_statement",
            },
        ],
        "role_metadata": {
            "announcement_feedback_and_help": [
                "Armin Senoner",
                "Juanita Bawagan",
                "Jane Park",
                "Arielle Bier",
                "Molly Beck",
            ],
            "illustrations_and_figures": [
                "William Hood",
                "Irina Andronic",
                "Victoria Johnston",
                "Lucas Dixon",
                "Adam Connors",
                "Jimbo Wilson",
            ],
        },
        "claim_boundary": {
            "official_announcement_source": True,
            "not_whitepaper_specification": True,
            "not_reproduced_libreevolve_evidence": True,
            "blog_metric_variants_require_reconciliation": True,
            "early_access_not_local_availability": True,
            "outbound_links_require_separate_source_records": True,
        },
        "remaining_work": [
            "map_blog_claims_to_whitepaper_sections",
            "map_blog_claims_to_colab_artifacts",
            "record_blog_update_metadata_if_published",
            "reconcile_blog_flashattention_and_kernel_effort_variants",
            "link_blog_acknowledgement_roles_to_artifacts",
        ],
    }


def alphaevolve_official_blog_manifest_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_OFFICIAL_BLOG_MANIFEST_SCHEMA,
        "official_blog_source_count": 1,
        "sources": [
            {
                "manifest_row_id": "2506.13131",
                "official_blog_source_id": "deepmind_alphaevolve_2025_05_14",
                "source_record": alphaevolve_official_blog_source_record(),
                "claim_artifact_links": {
                    "official_blog_used_by": sorted(EXPECTED_OFFICIAL_BLOG_SURFACES),
                    "policy": (
                        "official_blog_claims_are_announcement_evidence_not_"
                        "whitepaper_spec_or_reproduced_libreevolve_evidence"
                    ),
                },
                "evidence_policy": {
                    "announcement_source_recorded": True,
                    "whitepaper_specification_separate": True,
                    "publication_ready_without_variant_reconciliation": False,
                    "scope": (
                        "official DeepMind announcement source provenance and "
                        "claim variants, not audited white-paper specification"
                    ),
                },
            }
        ],
    }


def validate_alphaevolve_official_blog_source(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveOfficialBlogValidation:
    data, read_issues = _load_blog_recordset(recordset)
    if read_issues:
        return AlphaEvolveOfficialBlogValidation(False, 0, 0, False, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveOfficialBlogIssue] = []
    if data.get("schema") != ALPHAEVOLVE_OFFICIAL_BLOG_SOURCE_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported official blog source schema"))
    if data.get("source_family") != "alphaevolve_official_deepmind_announcement":
        issues.append(_issue("invalid_source_family", "source_family must identify the official DeepMind announcement"))
    if data.get("source_paper_id") != "2506.13131":
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    _validate_article(data.get("article"), issues)
    linked_whitepaper = _validate_linked_sources(data.get("linked_sources"), issues)
    claim_count = _validate_claim_variants(data.get("claim_variants"), issues)
    _validate_role_metadata(data.get("role_metadata"), issues)
    announcement_boundary = _validate_claim_boundary(data.get("claim_boundary"), issues)
    _validate_remaining_work(data.get("remaining_work"), issues)
    return AlphaEvolveOfficialBlogValidation(
        ok=not issues,
        source_count=1,
        claim_count=claim_count,
        linked_whitepaper=linked_whitepaper,
        announcement_boundary=announcement_boundary,
        issues=issues,
    )


def validate_alphaevolve_official_blog_manifest(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveOfficialBlogValidation:
    data, read_issues = _load_blog_manifest_recordset(recordset)
    if read_issues:
        return AlphaEvolveOfficialBlogValidation(False, 0, 0, False, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveOfficialBlogIssue] = []
    if data.get("schema") != ALPHAEVOLVE_OFFICIAL_BLOG_MANIFEST_SCHEMA:
        issues.append(_issue("invalid_manifest_schema", "unsupported official blog manifest schema"))
    sources = data.get("sources")
    if not isinstance(sources, list):
        issues.append(_issue("invalid_manifest_sources", "official blog manifest sources must be a list"))
        sources = []
    source_count = len(sources)
    if data.get("official_blog_source_count") != source_count:
        issues.append(_issue("invalid_source_count", "official_blog_source_count must equal the number of sources"))
    if source_count != 1:
        issues.append(_issue("invalid_manifest_source_count", "official blog manifest must contain the DeepMind announcement row"))
    claim_count = 0
    linked_whitepaper = False
    announcement_boundary = False
    for index, source in enumerate(sources):
        report = _validate_manifest_source(source, issues, index)
        claim_count += report.claim_count
        linked_whitepaper = linked_whitepaper or report.linked_whitepaper
        announcement_boundary = announcement_boundary or report.announcement_boundary
    return AlphaEvolveOfficialBlogValidation(
        ok=not issues,
        source_count=source_count,
        claim_count=claim_count,
        linked_whitepaper=linked_whitepaper,
        announcement_boundary=announcement_boundary,
        issues=issues,
    )


def _load_blog_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveOfficialBlogIssue]]:
    if recordset is None:
        return alphaevolve_official_blog_source_record(), []
    return _load_recordset(recordset)


def _load_blog_manifest_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveOfficialBlogIssue]]:
    if recordset is None:
        return alphaevolve_official_blog_manifest_record(), []
    return _load_recordset(recordset)


def _load_recordset(
    recordset: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveOfficialBlogIssue]]:
    if isinstance(recordset, dict):
        return recordset, []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_recordset", f"could not read official blog recordset: {exc}")]
        if not isinstance(data, dict):
            return None, [_issue("invalid_recordset", "official blog recordset must be a JSON object")]
        return data, []
    return None, [_issue("invalid_recordset", "official blog recordset must be an object or path")]


def _validate_article(
    value: object,
    issues: list[AlphaEvolveOfficialBlogIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_article", "article must be an object"))
        return
    expected = {
        "title": EXPECTED_OFFICIAL_BLOG_TITLE,
        "url": EXPECTED_OFFICIAL_BLOG_URL,
        "legacy_url": EXPECTED_OFFICIAL_BLOG_LEGACY_URL,
        "date": EXPECTED_OFFICIAL_BLOG_DATE,
        "author": EXPECTED_OFFICIAL_BLOG_AUTHOR,
        "section": EXPECTED_OFFICIAL_BLOG_SECTION,
    }
    _validate_expected_fields(value, expected, "article", issues)
    retrieval = value.get("retrieval")
    if not isinstance(retrieval, dict):
        issues.append(_issue("invalid_article_retrieval", "article.retrieval must be an object"))
        return
    expected_retrieval = {
        "retrieved_on": "2026-06-09",
        "html_bytes": EXPECTED_OFFICIAL_BLOG_BYTES,
        "html_sha256": EXPECTED_OFFICIAL_BLOG_SHA256,
        "hash_algorithm": "sha256",
    }
    _validate_expected_fields(retrieval, expected_retrieval, "article_retrieval", issues)


def _validate_linked_sources(
    value: object,
    issues: list[AlphaEvolveOfficialBlogIssue],
) -> bool:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_linked_sources", "linked_sources must be an object"))
        return False
    expected = {
        "whitepaper_url": EXPECTED_WHITEPAPER_URL,
        "whitepaper_id": "2506.13131",
        "mathematical_results_colab_url": EXPECTED_COLAB_URL,
        "alphaevolve_results_repository": "https://github.com/google-deepmind/alphaevolve_results",
        "early_access_form_url": EXPECTED_EARLY_ACCESS_URL,
    }
    _validate_expected_fields(value, expected, "linked_sources", issues)
    return value.get("whitepaper_url") == EXPECTED_WHITEPAPER_URL


def _validate_claim_variants(
    value: object,
    issues: list[AlphaEvolveOfficialBlogIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_claim_variants", "claim_variants must be a list"))
        return 0
    ids = [claim.get("claim_id") for claim in value if isinstance(claim, dict)]
    if tuple(ids) != EXPECTED_BLOG_CLAIM_IDS:
        issues.append(_issue("claim_id_mismatch", "claim_variants must preserve the official blog claim id taxonomy"))
    variant_ids = {"kernel_engineering_weeks_to_days", "flashattention_32_5_percent"}
    for claim in value:
        if not isinstance(claim, dict):
            issues.append(_issue("invalid_claim_variant", "claim variants must be objects"))
            continue
        claim_id = claim.get("claim_id")
        for field in ("claim_id", "source", "category", "unit", "reconciliation_status"):
            if not isinstance(claim.get(field), str) or not claim[field]:
                issues.append(_issue(f"invalid_claim_{field}", f"claim.{field} must be a non-empty string"))
        if claim.get("source") != "blog":
            issues.append(_issue("invalid_claim_source", "official blog claim variants must identify blog source"))
        if claim_id in variant_ids and "whitepaper_variant" not in claim:
            issues.append(_issue("missing_claim_whitepaper_variant", "blog-versus-white-paper metric variants must name the white-paper variant"))
    return len(value)


def _validate_role_metadata(
    value: object,
    issues: list[AlphaEvolveOfficialBlogIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_role_metadata", "role_metadata must be an object"))
        return
    expected = {
        "announcement_feedback_and_help": [
            "Armin Senoner",
            "Juanita Bawagan",
            "Jane Park",
            "Arielle Bier",
            "Molly Beck",
        ],
        "illustrations_and_figures": [
            "William Hood",
            "Irina Andronic",
            "Victoria Johnston",
            "Lucas Dixon",
            "Adam Connors",
            "Jimbo Wilson",
        ],
    }
    _validate_expected_fields(value, expected, "role_metadata", issues)


def _validate_claim_boundary(
    value: object,
    issues: list[AlphaEvolveOfficialBlogIssue],
) -> bool:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_claim_boundary", "claim_boundary must be an object"))
        return False
    expected = {
        "official_announcement_source": True,
        "not_whitepaper_specification": True,
        "not_reproduced_libreevolve_evidence": True,
        "blog_metric_variants_require_reconciliation": True,
        "early_access_not_local_availability": True,
        "outbound_links_require_separate_source_records": True,
    }
    _validate_expected_fields(value, expected, "claim_boundary", issues)
    return value.get("not_whitepaper_specification") is True


def _validate_remaining_work(
    value: object,
    issues: list[AlphaEvolveOfficialBlogIssue],
) -> None:
    expected = {
        "map_blog_claims_to_whitepaper_sections",
        "map_blog_claims_to_colab_artifacts",
        "record_blog_update_metadata_if_published",
        "reconcile_blog_flashattention_and_kernel_effort_variants",
        "link_blog_acknowledgement_roles_to_artifacts",
    }
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(_issue("invalid_remaining_work", "remaining_work must list official blog follow-ups"))
        return
    if set(value) != expected:
        issues.append(_issue("remaining_work_mismatch", "remaining_work must preserve blog mapping, variant reconciliation, and role-linking follow-ups"))


def _validate_manifest_source(
    value: object,
    issues: list[AlphaEvolveOfficialBlogIssue],
    index: int,
) -> AlphaEvolveOfficialBlogValidation:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_manifest_source", f"official blog manifest source {index} must be an object"))
        return AlphaEvolveOfficialBlogValidation(False, 0, 0, False, False, [])
    expected = {
        "manifest_row_id": "2506.13131",
        "official_blog_source_id": "deepmind_alphaevolve_2025_05_14",
    }
    _validate_expected_fields(value, expected, "manifest", issues)
    report = validate_alphaevolve_official_blog_source(value.get("source_record"))
    issues.extend(report.issues)
    _validate_claim_artifact_links(value.get("claim_artifact_links"), issues)
    _validate_evidence_policy(value.get("evidence_policy"), issues)
    return report


def _validate_claim_artifact_links(
    value: object,
    issues: list[AlphaEvolveOfficialBlogIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_claim_artifact_links", "claim_artifact_links must be an object"))
        return
    surfaces = value.get("official_blog_used_by")
    if not isinstance(surfaces, list) or not all(isinstance(item, str) for item in surfaces):
        issues.append(_issue("invalid_claim_surfaces", "official_blog_used_by must list docs, papers, and active TODO surfaces"))
    elif set(surfaces) != EXPECTED_OFFICIAL_BLOG_SURFACES:
        issues.append(_issue("claim_surface_mismatch", "official_blog_used_by must cover docs, papers, and active TODO evidence"))
    if value.get("policy") != (
        "official_blog_claims_are_announcement_evidence_not_"
        "whitepaper_spec_or_reproduced_libreevolve_evidence"
    ):
        issues.append(_issue("invalid_claim_policy", "claim policy must separate announcement evidence from white-paper spec and reproduced evidence"))


def _validate_evidence_policy(
    value: object,
    issues: list[AlphaEvolveOfficialBlogIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_evidence_policy", "evidence_policy must be an object"))
        return
    expected = {
        "announcement_source_recorded": True,
        "whitepaper_specification_separate": True,
        "publication_ready_without_variant_reconciliation": False,
    }
    _validate_expected_fields(value, expected, "evidence_policy", issues)
    scope = value.get("scope")
    if not isinstance(scope, str) or "not audited white-paper specification" not in scope:
        issues.append(_issue("invalid_evidence_policy_scope", "evidence_policy.scope must distinguish announcement provenance from white-paper specification"))


def _validate_expected_fields(
    value: dict[str, Any],
    expected: dict[str, Any],
    prefix: str,
    issues: list[AlphaEvolveOfficialBlogIssue],
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_{prefix}_{field}", f"{prefix}.{field} must match the official blog source evidence"))
    for field in ("sha256", "html_sha256"):
        digest = value.get(field)
        if digest is not None and (not isinstance(digest, str) or _SHA256_RE.fullmatch(digest) is None):
            issues.append(_issue(f"invalid_{prefix}_{field}_format", f"{prefix}.{field} must be a SHA-256 digest"))


def _issue(code: str, message: str, source_id: str | None = None) -> AlphaEvolveOfficialBlogIssue:
    return AlphaEvolveOfficialBlogIssue(code, message, source_id)
