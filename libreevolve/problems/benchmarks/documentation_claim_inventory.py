from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DOCUMENTATION_CLAIM_INVENTORY_SCHEMA = (
    "libreevolve.documentation_claim_inventory.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_INVENTORY_STATUS = (
    "top_level_readme_roadmap_papers_claim_inventory_without_semantic_verifier"
)
EXPECTED_MISSING_EVIDENCE = {
    "complete_readme_claim_inventory": "not_recorded_locally",
    "complete_roadmap_claim_inventory": "not_recorded_locally",
    "complete_paper_index_status_row_inventory": "not_recorded_locally",
    "semantic_claim_verifier": "not_recorded_locally",
    "stale_completed_entry_detection": "not_recorded_locally",
    "generated_alignment_report": "not_recorded_locally",
    "full_alphaevolve_claim_truth_proof": "not_recorded_locally",
}
EXPECTED_CLAIMS = (
    {
        "claim_id": "readme_current_status_scope",
        "document_path": "README.md",
        "document_section": "Current Status",
        "claim_kind": "status_scope",
        "claim_summary": (
            "LibreEvolve is alpha-stage, local, Python-first research code and "
            "not a production optimizer or full AlphaEvolve reproduction."
        ),
        "evidence_refs": [
            "README.md#current-status",
            "docs/status.md",
            "papers/documentation_truthfulness_boundary.json",
            "docs/todo/readme.md",
        ],
        "source_anchor_text": "## Current Status",
        "verification_scope": "top_level_claim_anchor_only",
    },
    {
        "claim_id": "readme_runnable_today_scope",
        "document_path": "README.md",
        "document_section": "Current Status / Runnable today",
        "claim_kind": "feature_scope",
        "claim_summary": (
            "README runnable-today bullets describe Python-primary workspaces, "
            "SEARCH/REPLACE mutations, configured provider backends, local "
            "MAP-Elites/island archives, local evaluation, hooks, and runs/ "
            "artifacts."
        ),
        "evidence_refs": [
            "README.md#current-status",
            "libreevolve/cli.py",
            "libreevolve/core/loop.py",
            "libreevolve/core/diff.py",
            "libreevolve/llm/",
            "libreevolve/population/",
            "docs/status.md",
        ],
        "source_anchor_text": "## Current Status",
        "verification_scope": "top_level_claim_anchor_only",
    },
    {
        "claim_id": "readme_important_limits_scope",
        "document_path": "README.md",
        "document_section": "Current Status / Important limits",
        "claim_kind": "limitation_scope",
        "claim_summary": (
            "README important limits keep AlphaEvolve-scale benchmarks, "
            "Google/Gemini parity, distributed async topology, arbitrary "
            "language runners, hardened sandboxing, and paper-cache claims "
            "scoped as missing or non-proof evidence."
        ),
        "evidence_refs": [
            "README.md#current-status",
            "papers/README.md",
            "papers/documentation_truthfulness_boundary.json",
            "docs/todo/code.md",
            "docs/todo/papers.md",
        ],
        "source_anchor_text": "## Current Status",
        "verification_scope": "top_level_claim_anchor_only",
    },
    {
        "claim_id": "roadmap_current_state_scope",
        "document_path": "ROADMAP.md",
        "document_section": "Current State",
        "claim_kind": "planning_scope",
        "claim_summary": (
            "ROADMAP current-state bullets are maintained planning summaries "
            "whose authoritative evidence remains code, tests, runtime "
            "artifacts, paper sidecars, and TODO ledgers."
        ),
        "evidence_refs": [
            "ROADMAP.md#current-state",
            "docs/status.md",
            "papers/README.md",
            "docs/todo/roadmap.md",
        ],
        "source_anchor_text": "## Current State",
        "verification_scope": "top_level_claim_anchor_only",
    },
    {
        "claim_id": "roadmap_documentation_truthfulness_scope",
        "document_path": "ROADMAP.md",
        "document_section": "Documentation truthfulness",
        "claim_kind": "documentation_boundary",
        "claim_summary": (
            "ROADMAP documentation-truthfulness status records path, manifest, "
            "TODO-coverage, and sidecar-registry guards while leaving semantic "
            "claim-by-claim proof open."
        ),
        "evidence_refs": [
            "ROADMAP.md#documentation-truthfulness",
            "papers/documentation_truthfulness_boundary.json",
            "papers/documentation_claim_inventory.json",
            "docs/todo/readme.md",
            "docs/todo/roadmap.md",
            "docs/todo/papers.md",
        ],
        "source_anchor_text": "### 5. Documentation truthfulness",
        "verification_scope": "top_level_claim_anchor_only",
    },
    {
        "claim_id": "roadmap_alphaevolve_gap_scope",
        "document_path": "ROADMAP.md",
        "document_section": "Remaining AlphaEvolve gaps",
        "claim_kind": "gap_scope",
        "claim_summary": (
            "ROADMAP missing-work sections preserve AlphaEvolve parity gaps "
            "instead of treating local validators, sidecars, or fixtures as "
            "full paper-result reproduction."
        ),
        "evidence_refs": [
            "ROADMAP.md",
            "papers/2506.13131__AlphaEvolve.pdf",
            "papers/README.md",
            "docs/todo/code.md",
            "docs/todo/papers.md",
        ],
        "source_anchor_text": "# Roadmap",
        "verification_scope": "top_level_claim_anchor_only",
    },
    {
        "claim_id": "papers_cache_manifest_scope",
        "document_path": "papers/README.md",
        "document_section": "Local Paper Cache",
        "claim_kind": "paper_cache_scope",
        "claim_summary": (
            "The papers README describes the local cache manifests, ignored "
            "PDF policy, retained AlphaEvolve source-artifact exception, "
            "rehydration command, and manifest validation boundaries."
        ),
        "evidence_refs": [
            "papers/README.md#local-paper-cache",
            "papers/download_manifest.json",
            "papers/download_manifest.csv",
            "libreevolve/tools/paper_manifest.py",
            "tests/test_paper_manifest.py",
        ],
        "source_anchor_text": "# Local Paper Cache",
        "verification_scope": "top_level_claim_anchor_only",
    },
    {
        "claim_id": "papers_implementation_status_scope",
        "document_path": "papers/README.md",
        "document_section": "Implementation status",
        "claim_kind": "paper_status_scope",
        "claim_summary": (
            "The papers README implementation-status table is a maintained "
            "public claim surface with structural validation and TODO linkage, "
            "but not a semantic proof ledger for every long status phrase."
        ),
        "evidence_refs": [
            "papers/README.md#implementation-status",
            "docs/todo/papers.md",
            "papers/implementation_evidence_map_boundary.json",
            "papers/documentation_truthfulness_boundary.json",
            "libreevolve/tools/paper_manifest.py",
        ],
        "source_anchor_text": "## Implementation status",
        "verification_scope": "top_level_claim_anchor_only",
    },
)


@dataclass(frozen=True)
class DocumentationClaimInventoryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class DocumentationClaimInventoryValidation:
    ok: bool
    inventory_status: str | None
    claim_count: int
    readme_claim_count: int
    roadmap_claim_count: int
    papers_claim_count: int
    missing_evidence_count: int
    issues: list[DocumentationClaimInventoryIssue]


def documentation_claim_inventory_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the current top-level documentation claim inventory boundary."""

    root_path = Path(root)
    claims = []
    for claim in EXPECTED_CLAIMS:
        claim_record = dict(claim)
        claim_record["source_span"] = _source_anchor_span(
            root_path,
            claim_record["document_path"],
            claim_record["source_anchor_text"],
        )
        claim_record["source_anchor_status"] = (
            "source_anchor_recorded"
            if claim_record["source_span"]["found"]
            else "source_anchor_missing"
        )
        claim_record["evidence_ref_records"] = [
            _evidence_ref_record(root_path, ref)
            for ref in claim_record["evidence_refs"]
        ]
        claim_record["missing_evidence_refs"] = [
            record["ref"]
            for record in claim_record["evidence_ref_records"]
            if not record["exists"]
        ]
        claim_record["evidence_ref_status"] = (
            "all_local_evidence_refs_present"
            if not claim_record["missing_evidence_refs"]
            else "missing_local_evidence_refs"
        )
        claims.append(claim_record)
    source_anchor_missing_claim_ids = [
        claim["claim_id"]
        for claim in claims
        if claim["source_anchor_status"] != "source_anchor_recorded"
    ]
    missing_evidence_ref_records = [
        {
            "claim_id": claim["claim_id"],
            "ref": ref,
        }
        for claim in claims
        for ref in claim["missing_evidence_refs"]
    ]
    return {
        "schema": DOCUMENTATION_CLAIM_INVENTORY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "inventory_status": EXPECTED_INVENTORY_STATUS,
        "claim_ready": False,
        "coverage_scope": (
            "Top-level README, ROADMAP, and papers index claim anchors only. "
            "This is not a complete semantic verifier for every documentation "
            "sentence."
        ),
        "source_anchor_status": (
            "all_claim_source_anchors_recorded"
            if not source_anchor_missing_claim_ids
            else "missing_claim_source_anchors"
        ),
        "source_anchor_missing_claim_ids": source_anchor_missing_claim_ids,
        "evidence_ref_status": (
            "all_local_evidence_refs_present"
            if not missing_evidence_ref_records
            else "missing_local_evidence_refs"
        ),
        "evidence_ref_record_count": sum(
            len(claim["evidence_ref_records"]) for claim in claims
        ),
        "missing_evidence_ref_records": missing_evidence_ref_records,
        "claims": claims,
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This inventory gives stable ids and evidence anchors for the "
            "top-level README, ROADMAP, and papers index AlphaEvolve-facing "
            "status claims, including source-anchor file offsets for those "
            "top-level claim surfaces and local evidence-ref existence records. "
            "It does not claim complete README coverage, "
            "complete ROADMAP coverage, complete papers index coverage, "
            "semantic claim verification, stale completed-entry detection, "
            "generated alignment reports, or full proof that every documentation "
            "claim is current."
        ),
    }


def validate_documentation_claim_inventory(
    inventory: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> DocumentationClaimInventoryValidation:
    data, read_issues = _load_inventory(
        documentation_claim_inventory_record(root) if inventory is None else inventory
    )
    if read_issues:
        return DocumentationClaimInventoryValidation(False, None, 0, 0, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[DocumentationClaimInventoryIssue] = []
    if data.get("schema") != DOCUMENTATION_CLAIM_INVENTORY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported documentation claim inventory schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    status = data.get("inventory_status")
    if status != EXPECTED_INVENTORY_STATUS:
        issues.append(_issue("invalid_inventory_status", f"inventory_status must be {EXPECTED_INVENTORY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "documentation claim inventory must not claim complete semantic proof"))
    scope = data.get("coverage_scope")
    if not isinstance(scope, str) or "Top-level README, ROADMAP, and papers index" not in scope:
        issues.append(_issue("invalid_coverage_scope", "coverage_scope must identify top-level README, ROADMAP, and papers index scope"))
    source_anchor_status = data.get("source_anchor_status")
    if source_anchor_status not in {
        "all_claim_source_anchors_recorded",
        "missing_claim_source_anchors",
    }:
        issues.append(_issue("invalid_source_anchor_status", "source_anchor_status must report recorded or missing claim anchors"))
    source_anchor_missing_claim_ids = data.get("source_anchor_missing_claim_ids")
    if not isinstance(source_anchor_missing_claim_ids, list) or any(
        not isinstance(item, str) for item in source_anchor_missing_claim_ids
    ):
        issues.append(_issue("invalid_source_anchor_missing_claim_ids", "source_anchor_missing_claim_ids must be a list of strings"))
    expected_missing_claim_ids = [
        claim["claim_id"]
        for claim in _expected_claims_with_spans(Path(root))
        if claim["source_anchor_status"] != "source_anchor_recorded"
    ]
    expected_source_anchor_status = (
        "all_claim_source_anchors_recorded"
        if not expected_missing_claim_ids
        else "missing_claim_source_anchors"
    )
    if source_anchor_status != expected_source_anchor_status:
        issues.append(_issue("invalid_source_anchor_status", "source_anchor_status drifted from current claim anchors"))
    if source_anchor_missing_claim_ids != expected_missing_claim_ids:
        issues.append(_issue("invalid_source_anchor_missing_claim_ids", "source anchor missing ids drifted"))
    expected_claims = _expected_claims_with_spans(Path(root))
    expected_missing_evidence_ref_records = [
        {
            "claim_id": claim["claim_id"],
            "ref": ref,
        }
        for claim in expected_claims
        for ref in claim["missing_evidence_refs"]
    ]
    expected_evidence_ref_status = (
        "all_local_evidence_refs_present"
        if not expected_missing_evidence_ref_records
        else "missing_local_evidence_refs"
    )
    if data.get("evidence_ref_status") != expected_evidence_ref_status:
        issues.append(_issue("invalid_evidence_ref_status", "evidence_ref_status drifted from current files"))
    expected_evidence_ref_record_count = sum(
        len(claim["evidence_ref_records"]) for claim in expected_claims
    )
    if data.get("evidence_ref_record_count") != expected_evidence_ref_record_count:
        issues.append(_issue("invalid_evidence_ref_record_count", "evidence_ref_record_count drifted from current claims"))
    if data.get("missing_evidence_ref_records") != expected_missing_evidence_ref_records:
        issues.append(_issue("invalid_missing_evidence_ref_records", "missing evidence-ref records drifted"))
    claim_count, readme_count, roadmap_count, papers_count = _validate_claims(
        data.get("claims"),
        issues,
        Path(root),
    )
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim complete README coverage" not in boundary_text
        or "complete papers index coverage" not in boundary_text
        or "semantic claim verification" not in boundary_text
        or "full proof that every documentation claim is current" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate top-level anchors from semantic proof"))
    return DocumentationClaimInventoryValidation(
        ok=not issues,
        inventory_status=status if isinstance(status, str) else None,
        claim_count=claim_count,
        readme_claim_count=readme_count,
        roadmap_claim_count=roadmap_count,
        papers_claim_count=papers_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_documentation_claim_inventory_summary(inventory: dict[str, Any]) -> str:
    validation = validate_documentation_claim_inventory(inventory)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Documentation claim inventory",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| inventory_status | {validation.inventory_status or '<unknown>'} |",
        f"| claim_count | {validation.claim_count} |",
        f"| readme_claim_count | {validation.readme_claim_count} |",
        f"| roadmap_claim_count | {validation.roadmap_claim_count} |",
        f"| papers_claim_count | {validation.papers_claim_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_inventory(
    inventory: object | str | Path,
) -> tuple[dict[str, Any] | None, list[DocumentationClaimInventoryIssue]]:
    if isinstance(inventory, dict):
        return dict(inventory), []
    if isinstance(inventory, str) and inventory.strip().startswith("{"):
        try:
            data = json.loads(inventory)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"inventory JSON is invalid: {exc}")]
    else:
        try:
            data = json.loads(Path(inventory).read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_inventory", f"inventory could not be loaded: {exc}")]
    if isinstance(data, dict):
        return data, []
    return None, [_issue("invalid_shape", "documentation claim inventory must be a JSON object")]


def _validate_claims(
    value: object,
    issues: list[DocumentationClaimInventoryIssue],
    root: Path,
) -> tuple[int, int, int, int]:
    if not isinstance(value, list):
        issues.append(_issue("invalid_claims", "claims must be a list"))
        return 0, 0, 0, 0
    claims = [claim for claim in value if isinstance(claim, dict)]
    if len(claims) != len(value):
        issues.append(_issue("invalid_claim", "each claim must be an object"))
    expected_by_id = {claim["claim_id"]: claim for claim in _expected_claims_with_spans(root)}
    actual_by_id = {
        claim.get("claim_id"): claim
        for claim in claims
        if isinstance(claim.get("claim_id"), str)
    }
    missing = sorted(set(expected_by_id) - set(actual_by_id))
    extra = sorted(set(actual_by_id) - set(expected_by_id))
    if missing:
        issues.append(_issue("missing_claim_id", f"missing claim ids: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_claim_id", f"unknown claim ids: {', '.join(extra)}"))
    for claim_id, expected in expected_by_id.items():
        actual = actual_by_id.get(claim_id)
        if not actual:
            continue
        for key, expected_value in expected.items():
            if actual.get(key) != expected_value:
                issues.append(_issue(f"invalid_{claim_id}_{key}", f"{claim_id}.{key} does not match the expected inventory anchor"))
    readme_count = sum(
        1 for claim in claims if claim.get("document_path") == "README.md"
    )
    roadmap_count = sum(
        1 for claim in claims if claim.get("document_path") == "ROADMAP.md"
    )
    papers_count = sum(
        1 for claim in claims if claim.get("document_path") == "papers/README.md"
    )
    return len(claims), readme_count, roadmap_count, papers_count


def _validate_missing_evidence(
    value: object,
    issues: list[DocumentationClaimInventoryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_missing_evidence_key", f"missing_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_missing_evidence_key", f"missing_evidence has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _expected_claims_with_spans(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for claim in EXPECTED_CLAIMS:
        record = dict(claim)
        record["source_span"] = _source_anchor_span(
            root,
            record["document_path"],
            record["source_anchor_text"],
        )
        record["source_anchor_status"] = (
            "source_anchor_recorded"
            if record["source_span"]["found"]
            else "source_anchor_missing"
        )
        record["evidence_ref_records"] = [
            _evidence_ref_record(root, ref)
            for ref in record["evidence_refs"]
        ]
        record["missing_evidence_refs"] = [
            item["ref"]
            for item in record["evidence_ref_records"]
            if not item["exists"]
        ]
        record["evidence_ref_status"] = (
            "all_local_evidence_refs_present"
            if not record["missing_evidence_refs"]
            else "missing_local_evidence_refs"
        )
        records.append(record)
    return records


def _evidence_ref_record(root: Path, ref: str) -> dict[str, Any]:
    path_text, separator, fragment = ref.partition("#")
    path = root / path_text
    try:
        exists = path.exists()
        if exists and path.is_file():
            kind = "file"
        elif exists and path.is_dir():
            kind = "directory"
        elif exists:
            kind = "other"
        else:
            kind = "missing"
    except OSError:
        exists = True
        kind = "inaccessible"
    if not exists:
        kind = "missing"
    return {
        "ref": ref,
        "path": path_text,
        "fragment": fragment if separator else None,
        "exists": exists,
        "kind": kind,
    }


def _source_anchor_span(root: Path, document_path: str, anchor_text: str) -> dict[str, Any]:
    path = root / document_path
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {
            "path": document_path,
            "anchor_text": anchor_text,
            "found": False,
            "file_text_char_start": None,
            "file_text_char_end": None,
            "line_start": None,
            "line_end": None,
        }
    start = text.find(anchor_text)
    if start < 0:
        return {
            "path": document_path,
            "anchor_text": anchor_text,
            "found": False,
            "file_text_char_start": None,
            "file_text_char_end": None,
            "line_start": None,
            "line_end": None,
        }
    end = start + len(anchor_text)
    return {
        "path": document_path,
        "anchor_text": anchor_text,
        "found": True,
        "file_text_char_start": start,
        "file_text_char_end": end,
        "line_start": text.count("\n", 0, start) + 1,
        "line_end": text.count("\n", 0, end) + 1,
    }


def _issue(code: str, message: str) -> DocumentationClaimInventoryIssue:
    return DocumentationClaimInventoryIssue(code, message)
