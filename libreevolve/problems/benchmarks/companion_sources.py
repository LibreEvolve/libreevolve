from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_COMPANION_COLAB_SCHEMA = "libreevolve.alphaevolve_companion_colab_source.v1"
ALPHAEVOLVE_COMPANION_SOURCE_MANIFEST_SCHEMA = (
    "libreevolve.alphaevolve_companion_source_manifest.v1"
)
ALPHAEVOLVE_COMPANION_SELECTION_SCOPE_SCHEMA = (
    "libreevolve.alphaevolve_companion_selection_scope.v1"
)
EXPECTED_COMPANION_SOURCE_MANIFEST_FILE = "papers/companion_sources.json"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_REPOSITORY_URL = "https://github.com/google-deepmind/alphaevolve_results"
EXPECTED_REPOSITORY_COMMIT = "".join(
    ["4226", "acbf", "237f", "f9ad", "10ba", "7673", "a2af", "127a", "2d8a", "5971"]
)
EXPECTED_NOTEBOOK_PATH = "mathematical_results.ipynb"
EXPECTED_NOTEBOOK_SHA256 = "".join(
    [
        "2cce",
        "2543",
        "e48c",
        "89aa",
        "3e91",
        "6142",
        "72a6",
        "98a0",
        "147d",
        "d254",
        "8ea1",
        "1cf9",
        "2f12",
        "92b7",
        "435d",
        "38ff",
    ]
)
EXPECTED_NOTEBOOK_BYTES = 1311048
EXPECTED_NOTEBOOK_CELL_COUNT = 128
EXPECTED_NOTEBOOK_NBFORMAT = 4
EXPECTED_CLAIM_IDS = frozenset(
    {
        "appendix_a_matrix_improved_decompositions",
        "appendix_b_constructive_math_improved_results",
    }
)
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_COMMIT_RE = re.compile(r"[0-9a-f]{40}")
COMPANION_NOTEBOOK_COVERAGE_STATUSES = frozenset(
    {"included", "intentionally_absent"}
)
PAPER_RESULT_RELATIONS = frozenset(
    {"improved_over_sota", "matched_not_outperformed"}
)
ABSENCE_REASONS = frozenset(
    {"matched_but_not_outperformed_excluded_to_avoid_clutter"}
)


@dataclass(frozen=True)
class AlphaEvolveCompanionColabIssue:
    code: str
    message: str
    claim_id: str | None = None


@dataclass(frozen=True)
class AlphaEvolveCompanionColabValidation:
    ok: bool
    artifact_count: int
    claim_mapping_count: int
    local_cache_available: bool
    issues: list[AlphaEvolveCompanionColabIssue]


def alphaevolve_companion_colab_source_record() -> dict[str, Any]:
    raw_url = (
        f"{EXPECTED_REPOSITORY_URL.replace('github.com', 'raw.githubusercontent.com')}/"
        f"{EXPECTED_REPOSITORY_COMMIT}/{EXPECTED_NOTEBOOK_PATH}"
    )
    return {
        "schema": ALPHAEVOLVE_COMPANION_COLAB_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_name": "google-deepmind/alphaevolve_results",
        "artifact_id": "alphaevolve_results_mathematical_results_colab",
        "artifact_role": "external_alphaevolve_source_evidence",
        "retrieval_policy": "external_source_pinned_commit_no_local_copy_required",
        "repository": {
            "url": EXPECTED_REPOSITORY_URL,
            "commit": EXPECTED_REPOSITORY_COMMIT,
            "branch": "main",
            "readme_url": f"{EXPECTED_REPOSITORY_URL}/blob/main/README.md",
        },
        "notebook": {
            "path": EXPECTED_NOTEBOOK_PATH,
            "raw_url": raw_url,
            "colab_url": (
                "https://colab.research.google.com/github/google-deepmind/"
                "alphaevolve_results/blob/master/mathematical_results.ipynb"
            ),
            "sha256": EXPECTED_NOTEBOOK_SHA256,
            "bytes": EXPECTED_NOTEBOOK_BYTES,
            "nbformat": EXPECTED_NOTEBOOK_NBFORMAT,
            "cell_count": EXPECTED_NOTEBOOK_CELL_COUNT,
            "readability_check": "valid_ipynb_json",
            "local_cache": {
                "available": False,
                "path": None,
                "sha256": None,
            },
        },
        "selection_policy": {
            "inclusion_rule": "outperformed_sota_only",
            "excluded_result_policy": "matched_but_not_outperformed_results_excluded_to_avoid_clutter",
            "runtime_code_available": False,
            "readme_source_phrase": (
                "contains only the instances where the results from AlphaEvolve "
                "outperforms the state-of-the-art"
            ),
            "readme_exclusion_phrase": "matched but did not outperform are excluded to avoid clutter",
            "runtime_absence_phrase": "does not contain the code to run AlphaEvolve",
        },
        "rights": {
            "rights_holder": "Google LLC",
            "copyright_year": 2025,
            "software_license": "Apache-2.0",
            "materials_license": "CC-BY-4.0",
            "as_is_disclaimer": True,
            "official_product": False,
            "official_google_product": False,
            "source_phrase": "distributed on an AS IS basis and is not an official Google product",
            "artifact_license_mapping": {
                "notebook_code": "Apache-2.0",
                "verification_code": "Apache-2.0",
                "construction_data": "CC-BY-4.0",
                "readme_text": "CC-BY-4.0",
            },
        },
        "claim_mappings": [
            {
                "claim_id": "appendix_a_matrix_improved_decompositions",
                "paper_scope": "Section 3.1 and Table 2 improved matrix decompositions",
                "coverage_status": "covered_improved_results_only",
                "notebook_section": "Tensor decompositions (algorithms for matrix multiplication)",
                "cell_markers": [
                    "Tensor decompositions (algorithms for matrix multiplication)",
                    "Verification function",
                    "Rank-48 decomposition of <4,4,4>",
                ],
                "source_artifact_ref": EXPECTED_NOTEBOOK_PATH,
                "local_reproduction_artifact_ref": None,
                "local_export_equivalent": False,
            },
            {
                "claim_id": "appendix_b_constructive_math_improved_results",
                "paper_scope": "Section 3.2 and Appendix B improved constructive mathematics results",
                "coverage_status": "covered_improved_results_only",
                "notebook_section": "mathematical discoveries of AlphaEvolve outlined in Section 3",
                "cell_markers": [
                    "mathematical discoveries of AlphaEvolve",
                    "correctness-verification code",
                ],
                "source_artifact_ref": EXPECTED_NOTEBOOK_PATH,
                "local_reproduction_artifact_ref": None,
                "local_export_equivalent": False,
            },
        ],
    }


def alphaevolve_companion_source_manifest_record() -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_COMPANION_SOURCE_MANIFEST_SCHEMA,
        "companion_source_count": 1,
        "sources": [
            {
                "manifest_row_id": EXPECTED_SOURCE_PAPER_ID,
                "companion_source_id": "alphaevolve_results_mathematical_results_colab",
                "source_record": alphaevolve_companion_colab_source_record(),
                "claim_artifact_links": {
                    "companion_source_used_by": [
                        "README.md",
                        "ROADMAP.md",
                        "papers/README.md",
                        "docs/todo/code.md",
                        "docs/todo/papers.md",
                        "docs/todo/readme.md",
                        "docs/todo/roadmap.md",
                    ],
                    "policy": (
                        "paper_claim_audits_must_distinguish_external_companion_source_"
                        "from_local_generated_exports"
                    ),
                },
                "local_cache_policy": {
                    "cache_required_for_manifest_validation": False,
                    "validated_when_present": True,
                    "local_cache_status_field": "source_record.notebook.local_cache",
                    "scope": (
                        "committed external source provenance, not local reproduced "
                        "notebook/export evidence"
                    ),
                },
            }
        ],
    }


def alphaevolve_companion_selection_scope_record(
    claim_id: str,
    *,
    paper_result_relation: str = "improved_over_sota",
    companion_notebook_coverage: str = "included",
    absence_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "schema": ALPHAEVOLVE_COMPANION_SELECTION_SCOPE_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_manifest": EXPECTED_COMPANION_SOURCE_MANIFEST_FILE,
        "companion_source_id": "alphaevolve_results_mathematical_results_colab",
        "claim_id": claim_id,
        "source_artifact_ref": EXPECTED_NOTEBOOK_PATH,
        "paper_result_relation": paper_result_relation,
        "companion_notebook_coverage": companion_notebook_coverage,
        "absence_reason": absence_reason,
        "coverage_status": "covered_improved_results_only",
        "verifier_code_available": True,
        "alphaevolve_runtime_code_available": False,
        "selection_policy": {
            "inclusion_rule": "outperformed_sota_only",
            "excluded_result_policy": "matched_but_not_outperformed_results_excluded_to_avoid_clutter",
            "runtime_absence_policy": "companion_repository_does_not_contain_alphaevolve_runtime_code",
        },
    }


def validate_alphaevolve_companion_colab_source(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveCompanionColabValidation:
    data, read_issues = _load_recordset(recordset)
    if read_issues:
        return AlphaEvolveCompanionColabValidation(False, 0, 0, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveCompanionColabIssue] = []
    if data.get("schema") != ALPHAEVOLVE_COMPANION_COLAB_SCHEMA:
        issues.append(AlphaEvolveCompanionColabIssue("invalid_schema", "unsupported AlphaEvolve companion Colab source schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_source_paper_id",
                "source_paper_id must be 2506.13131",
            )
        )
    if data.get("source_name") != "google-deepmind/alphaevolve_results":
        issues.append(AlphaEvolveCompanionColabIssue("invalid_source_name", "source_name must identify google-deepmind/alphaevolve_results"))
    if data.get("artifact_role") != "external_alphaevolve_source_evidence":
        issues.append(AlphaEvolveCompanionColabIssue("invalid_artifact_role", "artifact_role must identify external AlphaEvolve source evidence"))
    if data.get("retrieval_policy") != "external_source_pinned_commit_no_local_copy_required":
        issues.append(AlphaEvolveCompanionColabIssue("invalid_retrieval_policy", "retrieval_policy must keep the companion source external and pinned"))
    _validate_repository(data.get("repository"), issues)
    local_cache_available = _validate_notebook(data.get("notebook"), issues)
    _validate_selection_policy(data.get("selection_policy"), issues)
    _validate_rights(data.get("rights"), issues)
    claim_count = _validate_claim_mappings(data.get("claim_mappings"), issues)
    return AlphaEvolveCompanionColabValidation(
        ok=not issues,
        artifact_count=1 if isinstance(data.get("notebook"), dict) else 0,
        claim_mapping_count=claim_count,
        local_cache_available=local_cache_available,
        issues=issues,
    )


def validate_alphaevolve_companion_selection_scope(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveCompanionColabValidation:
    data, read_issues = _load_selection_recordset(recordset)
    if read_issues:
        return AlphaEvolveCompanionColabValidation(False, 0, 0, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveCompanionColabIssue] = []
    if data.get("schema") != ALPHAEVOLVE_COMPANION_SELECTION_SCOPE_SCHEMA:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_selection_scope_schema",
                "unsupported AlphaEvolve companion selection-scope schema",
            )
        )
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(AlphaEvolveCompanionColabIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_manifest") != EXPECTED_COMPANION_SOURCE_MANIFEST_FILE:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_source_manifest",
                "source_manifest must point to papers/companion_sources.json",
            )
        )
    if data.get("companion_source_id") != "alphaevolve_results_mathematical_results_colab":
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_companion_source_id",
                "companion_source_id must identify the official mathematical_results Colab",
            )
        )
    claim_id = data.get("claim_id")
    safe_claim_id = claim_id if isinstance(claim_id, str) else None
    if safe_claim_id not in EXPECTED_CLAIM_IDS:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "unknown_claim_id",
                "claim_id must be a required companion source mapping",
                safe_claim_id,
            )
        )
    if data.get("source_artifact_ref") != EXPECTED_NOTEBOOK_PATH:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_source_artifact_ref",
                "source_artifact_ref must point to mathematical_results.ipynb",
            )
        )
    relation = data.get("paper_result_relation")
    coverage = data.get("companion_notebook_coverage")
    absence = data.get("absence_reason")
    if relation not in PAPER_RESULT_RELATIONS:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_paper_result_relation",
                "paper_result_relation must distinguish improved from matched-only results",
                safe_claim_id,
            )
        )
    if coverage not in COMPANION_NOTEBOOK_COVERAGE_STATUSES:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_companion_notebook_coverage",
                "companion_notebook_coverage must be included or intentionally_absent",
                safe_claim_id,
            )
        )
    if relation == "improved_over_sota":
        if coverage != "included":
            issues.append(
                AlphaEvolveCompanionColabIssue(
                    "invalid_improved_result_coverage",
                    "improved-over-SOTA results must be included in the companion notebook",
                    safe_claim_id,
                )
            )
        if absence is not None:
            issues.append(
                AlphaEvolveCompanionColabIssue(
                    "unexpected_absence_reason",
                    "included improved results must not carry an absence reason",
                    safe_claim_id,
                )
            )
    elif relation == "matched_not_outperformed":
        if coverage != "intentionally_absent":
            issues.append(
                AlphaEvolveCompanionColabIssue(
                    "invalid_matched_result_coverage",
                    "matched-only results must be marked intentionally absent from the companion notebook",
                    safe_claim_id,
                )
            )
        if absence not in ABSENCE_REASONS:
            issues.append(
                AlphaEvolveCompanionColabIssue(
                    "invalid_absence_reason",
                    "matched-only absences must preserve the README exclusion reason",
                    safe_claim_id,
                )
            )
    if data.get("coverage_status") != "covered_improved_results_only":
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_coverage_status",
                "coverage_status must preserve improved-results-only scope",
                safe_claim_id,
            )
        )
    if data.get("verifier_code_available") is not True:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_verifier_code_available",
                "selection scope must state verifier code is available for covered companion results",
                safe_claim_id,
            )
        )
    if data.get("alphaevolve_runtime_code_available") is not False:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "runtime_code_overclaim",
                "selection scope must preserve AlphaEvolve runtime-code absence",
                safe_claim_id,
            )
        )
    _validate_selection_scope_policy(data.get("selection_policy"), issues, safe_claim_id)
    return AlphaEvolveCompanionColabValidation(
        ok=not issues,
        artifact_count=1 if data.get("source_artifact_ref") == EXPECTED_NOTEBOOK_PATH else 0,
        claim_mapping_count=1 if safe_claim_id in EXPECTED_CLAIM_IDS else 0,
        local_cache_available=False,
        issues=issues,
    )


def validate_alphaevolve_companion_source_manifest(
    recordset: object | str | Path | None = None,
) -> AlphaEvolveCompanionColabValidation:
    data, read_issues = _load_manifest_recordset(recordset)
    if read_issues:
        return AlphaEvolveCompanionColabValidation(False, 0, 0, False, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveCompanionColabIssue] = []
    if data.get("schema") != ALPHAEVOLVE_COMPANION_SOURCE_MANIFEST_SCHEMA:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_manifest_schema",
                "unsupported AlphaEvolve companion-source manifest schema",
            )
        )
    sources = data.get("sources")
    if not isinstance(sources, list):
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_manifest_sources",
                "companion-source manifest sources must be a list",
            )
        )
        sources = []
    source_count = len(sources)
    if data.get("companion_source_count") != source_count:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_manifest_companion_source_count",
                "companion_source_count must equal the number of companion-source records",
            )
        )
    if source_count != 1:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_manifest_source_count",
                "companion-source manifest must contain the AlphaEvolve companion notebook row",
            )
        )
    artifact_count = 0
    claim_mapping_count = 0
    local_cache_available = False
    for index, source in enumerate(sources):
        source_validation = _validate_companion_source_manifest_source(source, issues, index)
        artifact_count += source_validation.artifact_count
        claim_mapping_count += source_validation.claim_mapping_count
        local_cache_available = local_cache_available or source_validation.local_cache_available
    return AlphaEvolveCompanionColabValidation(
        ok=not issues,
        artifact_count=artifact_count,
        claim_mapping_count=claim_mapping_count,
        local_cache_available=local_cache_available,
        issues=issues,
    )


def render_alphaevolve_companion_colab_source_summary(recordset: dict[str, Any]) -> str:
    validation = validate_alphaevolve_companion_colab_source(recordset)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve companion Colab source evidence",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| artifact_count | {validation.artifact_count} |",
        f"| claim_mapping_count | {validation.claim_mapping_count} |",
        f"| local_cache_available | {validation.local_cache_available} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(
            f"- {issue.code}: {issue.message}"
            + (f" ({issue.claim_id})" if issue.claim_id else "")
            for issue in validation.issues
        )
    return "\n".join(lines)


def _load_manifest_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveCompanionColabIssue]]:
    if recordset is None:
        return alphaevolve_companion_source_manifest_record(), []
    return _load_recordset(recordset)


def _load_selection_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveCompanionColabIssue]]:
    if recordset is None:
        return alphaevolve_companion_selection_scope_record(
            "appendix_a_matrix_improved_decompositions"
        ), []
    return _load_recordset(recordset)


def _load_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveCompanionColabIssue]]:
    if recordset is None:
        return alphaevolve_companion_colab_source_record(), []
    if isinstance(recordset, dict):
        return dict(recordset), []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [AlphaEvolveCompanionColabIssue("read_error", f"failed to read companion source record: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [AlphaEvolveCompanionColabIssue("invalid_json", f"invalid companion source JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [AlphaEvolveCompanionColabIssue("invalid_shape", "companion source record must be a JSON object")]


def _validate_companion_source_manifest_source(
    value: object,
    issues: list[AlphaEvolveCompanionColabIssue],
    index: int,
) -> AlphaEvolveCompanionColabValidation:
    if not isinstance(value, dict):
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_manifest_source",
                f"companion-source manifest source {index} must be an object",
            )
        )
        return AlphaEvolveCompanionColabValidation(False, 0, 0, False, [])
    if value.get("manifest_row_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_manifest_source_row_id",
                "companion-source manifest row id must match the cached AlphaEvolve row",
            )
        )
    if value.get("companion_source_id") != "alphaevolve_results_mathematical_results_colab":
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_manifest_companion_source_id",
                "companion-source manifest must name the official mathematical_results Colab",
            )
        )
    source_report = validate_alphaevolve_companion_colab_source(value.get("source_record"))
    issues.extend(source_report.issues)
    _validate_claim_artifact_links(value.get("claim_artifact_links"), issues)
    _validate_local_cache_policy(value.get("local_cache_policy"), issues)
    return source_report


def _validate_claim_artifact_links(
    value: object,
    issues: list[AlphaEvolveCompanionColabIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_claim_artifact_links",
                "claim_artifact_links must be an object",
            )
        )
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
    surfaces = value.get("companion_source_used_by")
    if not isinstance(surfaces, list) or not all(isinstance(item, str) for item in surfaces):
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_claim_artifact_surfaces",
                "companion_source_used_by must list paper-claim artifact surfaces",
            )
        )
    elif set(surfaces) != expected_surfaces:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "claim_artifact_surface_mismatch",
                "companion_source_used_by must cover docs, papers, and active TODO evidence",
            )
        )
    if value.get("policy") != (
        "paper_claim_audits_must_distinguish_external_companion_source_"
        "from_local_generated_exports"
    ):
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_claim_artifact_policy",
                "claim artifact policy must distinguish external companion source evidence from local exports",
            )
        )


def _validate_local_cache_policy(
    value: object,
    issues: list[AlphaEvolveCompanionColabIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_local_cache_policy",
                "local_cache_policy must be an object",
            )
        )
        return
    expected = {
        "cache_required_for_manifest_validation": False,
        "validated_when_present": True,
        "local_cache_status_field": "source_record.notebook.local_cache",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(
                AlphaEvolveCompanionColabIssue(
                    f"invalid_local_cache_policy_{field}",
                    f"local_cache_policy.{field} must preserve the companion-source cache boundary",
                )
            )
    scope = value.get("scope")
    if not isinstance(scope, str) or "not local reproduced notebook/export evidence" not in scope:
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_local_cache_policy_scope",
                "local_cache_policy.scope must distinguish source provenance from local exports",
            )
        )


def _validate_selection_scope_policy(
    value: object,
    issues: list[AlphaEvolveCompanionColabIssue],
    claim_id: str | None,
) -> None:
    if not isinstance(value, dict):
        issues.append(
            AlphaEvolveCompanionColabIssue(
                "invalid_selection_policy",
                "selection_policy must be an object",
                claim_id,
            )
        )
        return
    expected = {
        "inclusion_rule": "outperformed_sota_only",
        "excluded_result_policy": "matched_but_not_outperformed_results_excluded_to_avoid_clutter",
        "runtime_absence_policy": "companion_repository_does_not_contain_alphaevolve_runtime_code",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(
                AlphaEvolveCompanionColabIssue(
                    f"invalid_selection_policy_{field}",
                    f"selection_policy.{field} must preserve the companion README scope",
                    claim_id,
                )
            )


def _validate_repository(value: object, issues: list[AlphaEvolveCompanionColabIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AlphaEvolveCompanionColabIssue("invalid_repository", "repository must be an object"))
        return
    if value.get("url") != EXPECTED_REPOSITORY_URL:
        issues.append(AlphaEvolveCompanionColabIssue("invalid_repository_url", "repository.url must be the official alphaevolve_results GitHub repository"))
    commit = value.get("commit")
    if not isinstance(commit, str) or _COMMIT_RE.fullmatch(commit) is None:
        issues.append(AlphaEvolveCompanionColabIssue("invalid_repository_commit", "repository.commit must be a 40-character commit hash"))
    elif commit != EXPECTED_REPOSITORY_COMMIT:
        issues.append(AlphaEvolveCompanionColabIssue("repository_commit_drift", "repository.commit must match the verified source revision"))
    if value.get("branch") != "main":
        issues.append(AlphaEvolveCompanionColabIssue("invalid_repository_branch", "repository.branch must be main"))
    readme_url = value.get("readme_url")
    if not isinstance(readme_url, str) or "google-deepmind/alphaevolve_results" not in readme_url or "README.md" not in readme_url:
        issues.append(AlphaEvolveCompanionColabIssue("invalid_readme_url", "repository.readme_url must link the official README"))


def _validate_notebook(value: object, issues: list[AlphaEvolveCompanionColabIssue]) -> bool:
    if not isinstance(value, dict):
        issues.append(AlphaEvolveCompanionColabIssue("invalid_notebook", "notebook must be an object"))
        return False
    if value.get("path") != EXPECTED_NOTEBOOK_PATH:
        issues.append(AlphaEvolveCompanionColabIssue("invalid_notebook_path", "notebook.path must be mathematical_results.ipynb"))
    raw_url = value.get("raw_url")
    if not isinstance(raw_url, str) or EXPECTED_REPOSITORY_COMMIT not in raw_url or EXPECTED_NOTEBOOK_PATH not in raw_url:
        issues.append(AlphaEvolveCompanionColabIssue("invalid_raw_url", "notebook.raw_url must pin the verified commit and notebook path"))
    colab_url = value.get("colab_url")
    if not isinstance(colab_url, str) or "colab.research.google.com" not in colab_url or EXPECTED_NOTEBOOK_PATH not in colab_url:
        issues.append(AlphaEvolveCompanionColabIssue("invalid_colab_url", "notebook.colab_url must link the README Colab notebook"))
    if value.get("sha256") != EXPECTED_NOTEBOOK_SHA256:
        issues.append(AlphaEvolveCompanionColabIssue("invalid_notebook_sha256", "notebook sha256 must match the verified raw notebook digest"))
    if value.get("bytes") != EXPECTED_NOTEBOOK_BYTES:
        issues.append(AlphaEvolveCompanionColabIssue("invalid_notebook_bytes", "notebook bytes must match the verified raw notebook length"))
    if value.get("nbformat") != EXPECTED_NOTEBOOK_NBFORMAT:
        issues.append(AlphaEvolveCompanionColabIssue("invalid_nbformat", "notebook nbformat must be 4"))
    if value.get("cell_count") != EXPECTED_NOTEBOOK_CELL_COUNT:
        issues.append(AlphaEvolveCompanionColabIssue("invalid_cell_count", "notebook cell_count must match the verified notebook"))
    if value.get("readability_check") != "valid_ipynb_json":
        issues.append(AlphaEvolveCompanionColabIssue("invalid_readability_check", "readability_check must record valid_ipynb_json"))
    cache = value.get("local_cache")
    if not isinstance(cache, dict):
        issues.append(AlphaEvolveCompanionColabIssue("invalid_local_cache", "notebook.local_cache must be an object"))
        return False
    available = cache.get("available")
    if not isinstance(available, bool):
        issues.append(AlphaEvolveCompanionColabIssue("invalid_local_cache_available", "local_cache.available must be boolean"))
        return False
    if available:
        if not isinstance(cache.get("path"), str) or not cache["path"].strip():
            issues.append(AlphaEvolveCompanionColabIssue("missing_local_cache_path", "available local cache must include a path"))
        if cache.get("sha256") != EXPECTED_NOTEBOOK_SHA256:
            issues.append(AlphaEvolveCompanionColabIssue("local_cache_hash_mismatch", "available local cache sha256 must match the notebook digest"))
    elif cache.get("path") is not None or cache.get("sha256") is not None:
        issues.append(AlphaEvolveCompanionColabIssue("local_cache_overclaim", "unavailable local cache must not include path or sha256"))
    return available


def _validate_selection_policy(value: object, issues: list[AlphaEvolveCompanionColabIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AlphaEvolveCompanionColabIssue("invalid_selection_policy", "selection_policy must be an object"))
        return
    if value.get("inclusion_rule") != "outperformed_sota_only":
        issues.append(AlphaEvolveCompanionColabIssue("invalid_inclusion_rule", "selection policy must record outperformed_sota_only"))
    if value.get("excluded_result_policy") != "matched_but_not_outperformed_results_excluded_to_avoid_clutter":
        issues.append(AlphaEvolveCompanionColabIssue("invalid_excluded_result_policy", "selection policy must preserve matched-result exclusion"))
    if value.get("runtime_code_available") is not False:
        issues.append(AlphaEvolveCompanionColabIssue("runtime_code_overclaim", "companion repository must not claim AlphaEvolve runtime code availability"))
    source_phrase = value.get("readme_source_phrase")
    if not isinstance(source_phrase, str) or "outperforms the state-of-the-art" not in source_phrase:
        issues.append(AlphaEvolveCompanionColabIssue("missing_selection_source_phrase", "selection policy must preserve outperformed-SOTA README wording"))
    exclusion_phrase = value.get("readme_exclusion_phrase")
    if not isinstance(exclusion_phrase, str) or "matched but did not outperform" not in exclusion_phrase:
        issues.append(AlphaEvolveCompanionColabIssue("missing_exclusion_source_phrase", "selection policy must preserve matched-result exclusion wording"))
    absence_phrase = value.get("runtime_absence_phrase")
    if not isinstance(absence_phrase, str) or "does not contain the code to run AlphaEvolve" not in absence_phrase:
        issues.append(AlphaEvolveCompanionColabIssue("missing_runtime_absence_phrase", "selection policy must preserve runtime-code absence wording"))


def _validate_rights(value: object, issues: list[AlphaEvolveCompanionColabIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AlphaEvolveCompanionColabIssue("invalid_rights", "rights must be an object"))
        return
    expected = {
        "rights_holder": "Google LLC",
        "copyright_year": 2025,
        "software_license": "Apache-2.0",
        "materials_license": "CC-BY-4.0",
        "as_is_disclaimer": True,
        "official_product": False,
        "official_google_product": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(AlphaEvolveCompanionColabIssue(f"invalid_rights_{field}", f"rights.{field} must match the companion repository README"))
    mapping = value.get("artifact_license_mapping")
    if not isinstance(mapping, dict):
        issues.append(AlphaEvolveCompanionColabIssue("invalid_artifact_license_mapping", "artifact_license_mapping must be an object"))
        return
    expected_mapping = {
        "notebook_code": "Apache-2.0",
        "verification_code": "Apache-2.0",
        "construction_data": "CC-BY-4.0",
        "readme_text": "CC-BY-4.0",
    }
    if mapping != expected_mapping:
        issues.append(AlphaEvolveCompanionColabIssue("artifact_license_mapping_mismatch", "artifact license mapping must distinguish software from other materials"))
    source_phrase = value.get("source_phrase")
    if not isinstance(source_phrase, str) or "AS IS" not in source_phrase or "not an official Google product" not in source_phrase:
        issues.append(AlphaEvolveCompanionColabIssue("missing_rights_source_phrase", "rights.source_phrase must preserve disclaimer and official-product boundary"))


def _validate_claim_mappings(value: object, issues: list[AlphaEvolveCompanionColabIssue]) -> int:
    if not isinstance(value, list) or not value:
        issues.append(AlphaEvolveCompanionColabIssue("invalid_claim_mappings", "claim_mappings must be a non-empty list"))
        return 0
    seen: set[str] = set()
    for mapping in value:
        if not isinstance(mapping, dict):
            issues.append(AlphaEvolveCompanionColabIssue("invalid_claim_mapping", "claim mappings must be objects"))
            continue
        claim_id = mapping.get("claim_id")
        safe_id = claim_id if isinstance(claim_id, str) else None
        if safe_id not in EXPECTED_CLAIM_IDS:
            issues.append(AlphaEvolveCompanionColabIssue("unknown_claim_id", "claim_id must be a required companion source mapping", safe_id))
            continue
        if safe_id in seen:
            issues.append(AlphaEvolveCompanionColabIssue("duplicate_claim_id", "claim mapping ids must be unique", safe_id))
        seen.add(safe_id)
        _validate_claim_mapping(mapping, safe_id, issues)
    for claim_id in sorted(EXPECTED_CLAIM_IDS - seen):
        issues.append(AlphaEvolveCompanionColabIssue("missing_claim_mapping", "required companion source mapping is missing", claim_id))
    return len(value)


def _validate_claim_mapping(
    mapping: dict[str, Any],
    claim_id: str,
    issues: list[AlphaEvolveCompanionColabIssue],
) -> None:
    if not isinstance(mapping.get("paper_scope"), str) or not mapping["paper_scope"].strip():
        issues.append(AlphaEvolveCompanionColabIssue("missing_paper_scope", "claim mapping must include paper_scope", claim_id))
    if mapping.get("coverage_status") != "covered_improved_results_only":
        issues.append(AlphaEvolveCompanionColabIssue("invalid_coverage_status", "claim mapping must record improved-results-only coverage", claim_id))
    if not isinstance(mapping.get("notebook_section"), str) or not mapping["notebook_section"].strip():
        issues.append(AlphaEvolveCompanionColabIssue("missing_notebook_section", "claim mapping must name a notebook section", claim_id))
    markers = mapping.get("cell_markers")
    if not isinstance(markers, list) or not markers or not all(isinstance(marker, str) and marker.strip() for marker in markers):
        issues.append(AlphaEvolveCompanionColabIssue("invalid_cell_markers", "claim mapping must include non-empty cell markers", claim_id))
    if mapping.get("source_artifact_ref") != EXPECTED_NOTEBOOK_PATH:
        issues.append(AlphaEvolveCompanionColabIssue("invalid_source_artifact_ref", "claim mapping must point to mathematical_results.ipynb", claim_id))
    if mapping.get("local_reproduction_artifact_ref") is not None:
        issues.append(AlphaEvolveCompanionColabIssue("local_reproduction_overclaim", "external companion mappings must not claim local reproduction artifacts"))
    if mapping.get("local_export_equivalent") is not False:
        issues.append(AlphaEvolveCompanionColabIssue("local_export_overclaim", "external companion mappings must not claim local Colab-equivalent exports"))
