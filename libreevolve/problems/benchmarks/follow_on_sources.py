from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_FOLLOW_ON_MATH_SOURCE_SCHEMA = "libreevolve.alphaevolve_follow_on_math_source.v1"
ALPHAEVOLVE_FOLLOW_ON_SOURCE_MANIFEST_SCHEMA = (
    "libreevolve.alphaevolve_follow_on_source_manifest.v1"
)
EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE = "papers/follow_on_sources.json"
EXPECTED_ORIGINAL_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_FOLLOW_ON_ARXIV_ID = "2511.02864"
EXPECTED_FOLLOW_ON_VERSION = 3
EXPECTED_FOLLOW_ON_VERSIONED_ID = "2511.02864v3"
EXPECTED_FOLLOW_ON_TITLE = "Mathematical exploration and discovery at scale"
EXPECTED_FOLLOW_ON_REVISION_DATE = "2025-12-22"
EXPECTED_FOLLOW_ON_CATEGORY = "cs.NE"
EXPECTED_FOLLOW_ON_AUTHORS = (
    "Bogdan Georgiev",
    "Javier Gomez-Serrano",
    "Terence Tao",
    "Adam Zsolt Wagner",
)
EXPECTED_REPOSITORY_NAME = "google-deepmind/alphaevolve_repository_of_problems"
EXPECTED_REPOSITORY_URL = f"https://github.com/{EXPECTED_REPOSITORY_NAME}"
EXPECTED_REPOSITORY_COMMIT = "".join(
    ["bfd2", "24d0", "e776", "3f89", "eb4a", "8efe", "93ac", "1260", "91f8", "5ed9"]
)
EXPECTED_README_SHA256 = "".join(
    [
        "cecf",
        "8d52",
        "3151",
        "ca5e",
        "174f",
        "306f",
        "a52e",
        "f804",
        "1350",
        "e3ac",
        "6128",
        "6cbb",
        "744a",
        "312a",
        "029a",
        "1543",
    ]
)
EXPECTED_README_BYTES = 4425
EXPECTED_DECLARED_PROBLEM_COUNT = 67
EXPECTED_ARTIFACT_KINDS = (
    "problem_pages",
    "colab_notebooks_many_not_all",
    "prompts",
    "verification_code",
    "initial_programs",
    "final_evolved_programs",
    "visualization_or_analysis_where_appropriate",
)
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_COMMIT_RE = re.compile(r"[0-9a-f]{40}")


@dataclass(frozen=True)
class AlphaEvolveFollowOnMathSourceIssue:
    code: str
    message: str
    source_id: str | None = None


@dataclass(frozen=True)
class AlphaEvolveFollowOnMathSourceValidation:
    ok: bool
    source_count: int
    repository_ref_pinned: bool
    local_pdf_cache_available: bool
    issues: list[AlphaEvolveFollowOnMathSourceIssue]


def alphaevolve_follow_on_math_source_record() -> dict[str, Any]:
    readme_raw_url = (
        "https://raw.githubusercontent.com/google-deepmind/"
        f"alphaevolve_repository_of_problems/{EXPECTED_REPOSITORY_COMMIT}/README.md"
    )
    return {
        "schema": ALPHAEVOLVE_FOLLOW_ON_MATH_SOURCE_SCHEMA,
        "source_family": "alphaevolve_follow_on_mathematics",
        "original_source_paper_id": EXPECTED_ORIGINAL_SOURCE_PAPER_ID,
        "scope_boundary": {
            "original_alphaevolve_spec_source": EXPECTED_ORIGINAL_SOURCE_PAPER_ID,
            "follow_on_evidence_source": EXPECTED_FOLLOW_ON_ARXIV_ID,
            "separates_original_spec_from_later_math_evidence": True,
            "not_original_alphaevolve_runtime_spec": True,
            "not_full_problem_inventory": True,
        },
        "paper": {
            "arxiv_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
            "version": EXPECTED_FOLLOW_ON_VERSION,
            "versioned_id": EXPECTED_FOLLOW_ON_VERSIONED_ID,
            "category": EXPECTED_FOLLOW_ON_CATEGORY,
            "latest_revision_date": EXPECTED_FOLLOW_ON_REVISION_DATE,
            "title": EXPECTED_FOLLOW_ON_TITLE,
            "authors": list(EXPECTED_FOLLOW_ON_AUTHORS),
            "abs_url": f"https://arxiv.org/abs/{EXPECTED_FOLLOW_ON_ARXIV_ID}",
            "versioned_abs_url": f"https://arxiv.org/abs/{EXPECTED_FOLLOW_ON_VERSIONED_ID}",
            "floating_pdf_url": f"https://arxiv.org/pdf/{EXPECTED_FOLLOW_ON_ARXIV_ID}.pdf",
            "versioned_pdf_url": f"https://arxiv.org/pdf/{EXPECTED_FOLLOW_ON_VERSIONED_ID}",
            "local_cache": {
                "available": False,
                "manifest_row_present": False,
                "file": None,
                "sha256": None,
                "bytes": None,
            },
        },
        "repository": {
            "name": EXPECTED_REPOSITORY_NAME,
            "url": EXPECTED_REPOSITORY_URL,
            "git_url": f"{EXPECTED_REPOSITORY_URL}.git",
            "default_branch": "main",
            "commit": EXPECTED_REPOSITORY_COMMIT,
            "snapshot_date": "2026-06-08",
            "live_update_policy": "live_repository_snapshot_required",
            "readme_url": f"{EXPECTED_REPOSITORY_URL}/blob/main/README.md",
            "readme_raw_url": readme_raw_url,
            "readme_sha256": EXPECTED_README_SHA256,
            "readme_bytes": EXPECTED_README_BYTES,
        },
        "repository_claims": {
            "declared_problem_count": EXPECTED_DECLARED_PROBLEM_COUNT,
            "problem_pages_declared_complete": True,
            "per_problem_inventory_validated": False,
            "numbered_page_inventory_validated": False,
            "notebook_coverage": "many_not_all",
            "runtime_code_available": False,
            "notebook_artifact_kinds": list(EXPECTED_ARTIFACT_KINDS),
            "hosted_problem_page_url_pattern": (
                "https://google-deepmind.github.io/"
                "alphaevolve_repository_of_problems/problems/{n}.html"
            ),
            "status_artifact_inventory_validated": True,
        },
        "source_use": {
            "repository_software_license": "Apache-2.0",
            "repository_materials_license": "CC-BY-4.0",
            "rights_holder": "Google LLC",
            "copyright_year": 2025,
            "citation_required": True,
            "citation_arxiv_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
        },
        "required_follow_on_work": [
            "build_per_problem_repository_inventory",
            "reconcile_numbered_problem_pages_with_declared_count",
            "validate_notebook_prompt_verifier_initial_final_artifacts",
            "map_original_appendix_b_claims_to_follow_on_problem_records",
            "attach_rights_attribution_to_generated_artifacts",
        ],
    }


def alphaevolve_follow_on_source_manifest_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_FOLLOW_ON_SOURCE_MANIFEST_SCHEMA,
        "follow_on_source_count": 1,
        "sources": [
            {
                "manifest_row_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
                "follow_on_source_id": EXPECTED_FOLLOW_ON_VERSIONED_ID,
                "source_record": alphaevolve_follow_on_math_source_record(),
                "claim_artifact_links": {
                    "follow_on_source_used_by": [
                        "README.md",
                        "ROADMAP.md",
                        "papers/README.md",
                        "docs/todo/code.md",
                        "docs/todo/papers.md",
                        "docs/todo/readme.md",
                        "docs/todo/roadmap.md",
                    ],
                    "policy": (
                        "follow_on_sources_must_not_be_treated_as_original_"
                        "alphaevolve_spec_or_cached_pdf"
                    ),
                },
                "cache_policy": {
                    "paper_cache_manifest_row_required": False,
                    "explicit_no_cache_policy_recorded": True,
                    "repository_snapshot_required": True,
                    "local_cache_status_field": "source_record.paper.local_cache",
                    "scope": (
                        "committed follow-on source provenance, not cached PDF "
                        "or per-problem inventory"
                    ),
                },
                "remaining_work": [
                    "build_per_problem_repository_inventory",
                    "reconcile_numbered_problem_pages_with_declared_count",
                    "validate_notebook_prompt_verifier_initial_final_artifacts",
                    "map_original_appendix_b_claims_to_follow_on_problem_records",
                    "attach_rights_attribution_to_generated_artifacts",
                ],
            }
        ],
    }


def validate_alphaevolve_follow_on_math_source(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveFollowOnMathSourceValidation:
    data, read_issues = _load_recordset(recordset)
    if read_issues:
        return AlphaEvolveFollowOnMathSourceValidation(False, 0, False, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveFollowOnMathSourceIssue] = []
    if data.get("schema") != ALPHAEVOLVE_FOLLOW_ON_MATH_SOURCE_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported AlphaEvolve follow-on math source schema"))
    if data.get("source_family") != "alphaevolve_follow_on_mathematics":
        issues.append(_issue("invalid_source_family", "source_family must identify follow-on AlphaEvolve mathematics evidence"))
    if data.get("original_source_paper_id") != EXPECTED_ORIGINAL_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_original_source_paper_id", "original_source_paper_id must be 2506.13131"))
    _validate_scope_boundary(data.get("scope_boundary"), issues)
    local_pdf_cache_available = _validate_paper(data.get("paper"), issues)
    repository_ref_pinned = _validate_repository(data.get("repository"), issues)
    _validate_repository_claims(data.get("repository_claims"), issues)
    _validate_source_use(data.get("source_use"), issues)
    _validate_required_follow_on_work(data.get("required_follow_on_work"), issues)
    source_count = sum(
        1
        for key in ("paper", "repository")
        if isinstance(data.get(key), dict)
    )
    return AlphaEvolveFollowOnMathSourceValidation(
        ok=not issues,
        source_count=source_count,
        repository_ref_pinned=repository_ref_pinned,
        local_pdf_cache_available=local_pdf_cache_available,
        issues=issues,
    )


def validate_alphaevolve_follow_on_source_manifest(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveFollowOnMathSourceValidation:
    data, read_issues = _load_manifest_recordset(recordset)
    if read_issues:
        return AlphaEvolveFollowOnMathSourceValidation(False, 0, False, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveFollowOnMathSourceIssue] = []
    if data.get("schema") != ALPHAEVOLVE_FOLLOW_ON_SOURCE_MANIFEST_SCHEMA:
        issues.append(_issue("invalid_manifest_schema", "unsupported AlphaEvolve follow-on source manifest schema"))
    sources = data.get("sources")
    if not isinstance(sources, list):
        issues.append(_issue("invalid_manifest_sources", "follow-on source manifest sources must be a list"))
        sources = []
    source_count = len(sources)
    if data.get("follow_on_source_count") != source_count:
        issues.append(
            _issue(
                "invalid_manifest_follow_on_source_count",
                "follow_on_source_count must equal the number of follow-on source records",
            )
        )
    if source_count != 1:
        issues.append(_issue("invalid_manifest_source_count", "follow-on source manifest must contain the math-scale paper/repository row"))
    repository_ref_pinned = False
    local_pdf_cache_available = False
    for index, source in enumerate(sources):
        source_report = _validate_follow_on_source_manifest_source(source, issues, index)
        repository_ref_pinned = repository_ref_pinned or source_report.repository_ref_pinned
        local_pdf_cache_available = local_pdf_cache_available or source_report.local_pdf_cache_available
    return AlphaEvolveFollowOnMathSourceValidation(
        ok=not issues,
        source_count=source_count,
        repository_ref_pinned=repository_ref_pinned,
        local_pdf_cache_available=local_pdf_cache_available,
        issues=issues,
    )


def render_alphaevolve_follow_on_math_source_summary(recordset: object | str | Path | None = None) -> str:
    validation = validate_alphaevolve_follow_on_math_source(recordset)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve follow-on math source evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| source_count | {validation.source_count} |",
        f"| arxiv_version | v{EXPECTED_FOLLOW_ON_VERSION} |",
        f"| latest_revision_date | {EXPECTED_FOLLOW_ON_REVISION_DATE} |",
        f"| declared_problem_count | {EXPECTED_DECLARED_PROBLEM_COUNT} |",
        f"| repository_ref_pinned | {validation.repository_ref_pinned} |",
        f"| local_pdf_cache_available | {validation.local_pdf_cache_available} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(
            f"- {issue.code}: {issue.message}"
            + (f" ({issue.source_id})" if issue.source_id else "")
            for issue in validation.issues
        )
    return "\n".join(lines)


def _load_manifest_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveFollowOnMathSourceIssue]]:
    if recordset is None:
        return alphaevolve_follow_on_source_manifest_record(), []
    return _load_recordset(recordset)


def _load_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveFollowOnMathSourceIssue]]:
    if recordset is None:
        return alphaevolve_follow_on_math_source_record(), []
    if isinstance(recordset, dict):
        return dict(recordset), []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [_issue("read_error", f"failed to read follow-on source record: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"invalid follow-on source JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [_issue("invalid_shape", "follow-on source record must be a JSON object")]


def _validate_scope_boundary(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_scope_boundary", "scope_boundary must be an object"))
        return
    expected = {
        "original_alphaevolve_spec_source": EXPECTED_ORIGINAL_SOURCE_PAPER_ID,
        "follow_on_evidence_source": EXPECTED_FOLLOW_ON_ARXIV_ID,
        "separates_original_spec_from_later_math_evidence": True,
        "not_original_alphaevolve_runtime_spec": True,
        "not_full_problem_inventory": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_scope_boundary_{field}", f"scope_boundary.{field} must preserve the follow-on source boundary"))


def _validate_paper(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> bool:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_paper", "paper must be an object", EXPECTED_FOLLOW_ON_ARXIV_ID))
        return False
    expected = {
        "arxiv_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
        "version": EXPECTED_FOLLOW_ON_VERSION,
        "versioned_id": EXPECTED_FOLLOW_ON_VERSIONED_ID,
        "category": EXPECTED_FOLLOW_ON_CATEGORY,
        "latest_revision_date": EXPECTED_FOLLOW_ON_REVISION_DATE,
        "title": EXPECTED_FOLLOW_ON_TITLE,
        "abs_url": f"https://arxiv.org/abs/{EXPECTED_FOLLOW_ON_ARXIV_ID}",
        "versioned_abs_url": f"https://arxiv.org/abs/{EXPECTED_FOLLOW_ON_VERSIONED_ID}",
        "floating_pdf_url": f"https://arxiv.org/pdf/{EXPECTED_FOLLOW_ON_ARXIV_ID}.pdf",
        "versioned_pdf_url": f"https://arxiv.org/pdf/{EXPECTED_FOLLOW_ON_VERSIONED_ID}",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_paper_{field}", f"paper.{field} must match the verified follow-on arXiv source", EXPECTED_FOLLOW_ON_ARXIV_ID))
    if tuple(value.get("authors") or ()) != EXPECTED_FOLLOW_ON_AUTHORS:
        issues.append(_issue("invalid_paper_authors", "paper.authors must match the verified follow-on author list", EXPECTED_FOLLOW_ON_ARXIV_ID))
    return _validate_local_cache(value.get("local_cache"), issues)


def _validate_local_cache(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> bool:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_cache", "paper.local_cache must be an object", EXPECTED_FOLLOW_ON_ARXIV_ID))
        return False
    available = value.get("available")
    manifest_row_present = value.get("manifest_row_present")
    if available is not False:
        issues.append(_issue("local_pdf_cache_overclaim", "paper.local_cache.available must remain false until a cache row is validated", EXPECTED_FOLLOW_ON_ARXIV_ID))
    if manifest_row_present is not False:
        issues.append(_issue("manifest_row_overclaim", "paper.local_cache.manifest_row_present must remain false until a paper manifest row exists", EXPECTED_FOLLOW_ON_ARXIV_ID))
    for field in ("file", "sha256", "bytes"):
        if value.get(field) is not None:
            issues.append(_issue(f"local_cache_{field}_overclaim", f"paper.local_cache.{field} must be null while the follow-on PDF is not cached", EXPECTED_FOLLOW_ON_ARXIV_ID))
    return available is True


def _validate_repository(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> bool:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository", "repository must be an object", EXPECTED_REPOSITORY_NAME))
        return False
    expected = {
        "name": EXPECTED_REPOSITORY_NAME,
        "url": EXPECTED_REPOSITORY_URL,
        "git_url": f"{EXPECTED_REPOSITORY_URL}.git",
        "default_branch": "main",
        "snapshot_date": "2026-06-08",
        "live_update_policy": "live_repository_snapshot_required",
        "readme_url": f"{EXPECTED_REPOSITORY_URL}/blob/main/README.md",
        "readme_raw_url": (
            "https://raw.githubusercontent.com/google-deepmind/"
            f"alphaevolve_repository_of_problems/{EXPECTED_REPOSITORY_COMMIT}/README.md"
        ),
        "readme_bytes": EXPECTED_README_BYTES,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_repository_{field}", f"repository.{field} must match the pinned DeepMind problem repository snapshot", EXPECTED_REPOSITORY_NAME))
    commit = value.get("commit")
    if not isinstance(commit, str) or _COMMIT_RE.fullmatch(commit) is None:
        issues.append(_issue("invalid_repository_commit", "repository.commit must be a 40-character commit hash", EXPECTED_REPOSITORY_NAME))
    elif commit != EXPECTED_REPOSITORY_COMMIT:
        issues.append(_issue("repository_commit_drift", "repository.commit must match the verified follow-on source revision", EXPECTED_REPOSITORY_NAME))
    sha256 = value.get("readme_sha256")
    if not isinstance(sha256, str) or _SHA256_RE.fullmatch(sha256) is None:
        issues.append(_issue("invalid_readme_sha256", "repository.readme_sha256 must be a lowercase 64-hex digest", EXPECTED_REPOSITORY_NAME))
    elif sha256 != EXPECTED_README_SHA256:
        issues.append(_issue("readme_sha256_drift", "repository.readme_sha256 must match the pinned README digest", EXPECTED_REPOSITORY_NAME))
    return commit == EXPECTED_REPOSITORY_COMMIT and sha256 == EXPECTED_README_SHA256


def _validate_repository_claims(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repository_claims", "repository_claims must be an object", EXPECTED_REPOSITORY_NAME))
        return
    expected = {
        "declared_problem_count": EXPECTED_DECLARED_PROBLEM_COUNT,
        "problem_pages_declared_complete": True,
        "per_problem_inventory_validated": False,
        "numbered_page_inventory_validated": False,
        "notebook_coverage": "many_not_all",
        "runtime_code_available": False,
        "hosted_problem_page_url_pattern": (
            "https://google-deepmind.github.io/"
            "alphaevolve_repository_of_problems/problems/{n}.html"
        ),
        "status_artifact_inventory_validated": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            code = f"invalid_repository_claims_{field}"
            if field == "runtime_code_available":
                code = "runtime_code_overclaim"
            elif field in {"per_problem_inventory_validated", "numbered_page_inventory_validated"}:
                code = f"{field}_overclaim"
            issues.append(_issue(code, f"repository_claims.{field} must match the scoped follow-on source evidence", EXPECTED_REPOSITORY_NAME))
    if tuple(value.get("notebook_artifact_kinds") or ()) != EXPECTED_ARTIFACT_KINDS:
        issues.append(_issue("invalid_notebook_artifact_kinds", "repository_claims.notebook_artifact_kinds must preserve the README artifact kinds", EXPECTED_REPOSITORY_NAME))


def _validate_source_use(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_source_use", "source_use must be an object", EXPECTED_REPOSITORY_NAME))
        return
    expected = {
        "repository_software_license": "Apache-2.0",
        "repository_materials_license": "CC-BY-4.0",
        "rights_holder": "Google LLC",
        "copyright_year": 2025,
        "citation_required": True,
        "citation_arxiv_id": EXPECTED_FOLLOW_ON_ARXIV_ID,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_source_use_{field}", f"source_use.{field} must match the follow-on repository README source-use boundary", EXPECTED_REPOSITORY_NAME))


def _validate_required_follow_on_work(value: object, issues: list[AlphaEvolveFollowOnMathSourceIssue]) -> None:
    required = {
        "build_per_problem_repository_inventory",
        "reconcile_numbered_problem_pages_with_declared_count",
        "validate_notebook_prompt_verifier_initial_final_artifacts",
        "map_original_appendix_b_claims_to_follow_on_problem_records",
        "attach_rights_attribution_to_generated_artifacts",
    }
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(_issue("invalid_required_follow_on_work", "required_follow_on_work must be a list of remaining work ids"))
        return
    missing = sorted(required - set(value))
    for work_id in missing:
        issues.append(_issue("missing_required_follow_on_work", f"required_follow_on_work is missing {work_id}"))


def _validate_follow_on_source_manifest_source(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
    index: int,
) -> AlphaEvolveFollowOnMathSourceValidation:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_manifest_source", f"follow-on source manifest source {index} must be an object"))
        return AlphaEvolveFollowOnMathSourceValidation(False, 0, False, False, [])
    if value.get("manifest_row_id") != EXPECTED_FOLLOW_ON_ARXIV_ID:
        issues.append(_issue("invalid_manifest_source_row_id", "manifest row id must match the follow-on arXiv id"))
    if value.get("follow_on_source_id") != EXPECTED_FOLLOW_ON_VERSIONED_ID:
        issues.append(_issue("invalid_manifest_follow_on_source_id", "follow-on source id must name the verified arXiv version"))
    source_report = validate_alphaevolve_follow_on_math_source(value.get("source_record"))
    issues.extend(source_report.issues)
    _validate_follow_on_claim_artifact_links(value.get("claim_artifact_links"), issues)
    _validate_follow_on_cache_policy(value.get("cache_policy"), issues)
    _validate_follow_on_manifest_remaining_work(value.get("remaining_work"), issues)
    return source_report


def _validate_follow_on_claim_artifact_links(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_claim_artifact_links", "claim_artifact_links must be an object"))
        return
    expected_surfaces = {
        "README.md",
        "ROADMAP.md",
        "papers/README.md",
        "docs/todo/code.md",
        "docs/todo/papers.md",
        "docs/todo/readme.md",
        "docs/todo/roadmap.md",
    }
    surfaces = value.get("follow_on_source_used_by")
    if not isinstance(surfaces, list) or not all(isinstance(item, str) for item in surfaces):
        issues.append(_issue("invalid_claim_artifact_surfaces", "follow_on_source_used_by must list docs, papers, and active TODO surfaces"))
    elif set(surfaces) != expected_surfaces:
        issues.append(_issue("claim_artifact_surface_mismatch", "follow_on_source_used_by must cover docs, papers, and active TODO evidence"))
    if value.get("policy") != (
        "follow_on_sources_must_not_be_treated_as_original_"
        "alphaevolve_spec_or_cached_pdf"
    ):
        issues.append(_issue("invalid_claim_artifact_policy", "claim artifact policy must preserve original-paper and cached-PDF boundaries"))


def _validate_follow_on_cache_policy(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_cache_policy", "cache_policy must be an object"))
        return
    expected = {
        "paper_cache_manifest_row_required": False,
        "explicit_no_cache_policy_recorded": True,
        "repository_snapshot_required": True,
        "local_cache_status_field": "source_record.paper.local_cache",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_cache_policy_{field}", f"cache_policy.{field} must preserve the follow-on source cache boundary"))
    scope = value.get("scope")
    if not isinstance(scope, str) or "not cached PDF" not in scope or "not" not in scope:
        issues.append(_issue("invalid_cache_policy_scope", "cache_policy.scope must distinguish source provenance from cached PDFs and per-problem inventory"))


def _validate_follow_on_manifest_remaining_work(
    value: object,
    issues: list[AlphaEvolveFollowOnMathSourceIssue],
) -> None:
    expected = {
        "build_per_problem_repository_inventory",
        "reconcile_numbered_problem_pages_with_declared_count",
        "validate_notebook_prompt_verifier_initial_final_artifacts",
        "map_original_appendix_b_claims_to_follow_on_problem_records",
        "attach_rights_attribution_to_generated_artifacts",
    }
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(_issue("invalid_manifest_remaining_work", "remaining_work must list unsatisfied follow-on work ids"))
        return
    actual = set(value)
    if actual != expected:
        issues.append(_issue("manifest_remaining_work_mismatch", "remaining_work must preserve only unsatisfied follow-on inventory, mapping, and rights work"))


def _issue(code: str, message: str, source_id: str | None = None) -> AlphaEvolveFollowOnMathSourceIssue:
    return AlphaEvolveFollowOnMathSourceIssue(code, message, source_id)
