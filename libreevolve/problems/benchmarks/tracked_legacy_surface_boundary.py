from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TRACKED_LEGACY_SURFACE_BOUNDARY_SCHEMA = (
    "libreevolve.tracked_legacy_surface_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "tracked_legacy_surface_inventory_without_owner_review_signoff"
)
LEGACY_ROOT = "old"
WORKFLOW_PATH = ".github/workflows/tests.yml"
README_PATH = "README.md"
DOCS_README_PATH = "docs/README.md"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "tracked_old_markdown_inventory",
    "archival_classification",
    "self_classification_banner",
    "obsolete_package_path_detection",
    "legacy_plan_checkbox_detection",
    "readme_repository_layout_routing",
    "docs_readme_boundary_routing",
    "ci_path_filter_policy",
    "paper_manifest_validation",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class TrackedLegacySurfaceBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class TrackedLegacySurfaceBoundaryValidation:
    ok: bool
    boundary_status: str | None
    legacy_surface_count: int
    archival_surface_count: int
    missing_route_count: int
    missing_evidence_count: int
    issues: list[TrackedLegacySurfaceBoundaryIssue]


def tracked_legacy_surface_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the tracked legacy planning surface classification boundary."""

    root_path = Path(root)
    legacy_paths = _tracked_legacy_markdown_paths(root_path)
    readme_text = _read_text(root_path / README_PATH)
    docs_readme_text = _read_text(root_path / DOCS_README_PATH)
    workflow_text = _read_text(root_path / WORKFLOW_PATH)
    records = [
        _legacy_surface_record(root_path, path, readme_text, docs_readme_text, workflow_text)
        for path in legacy_paths
    ]
    missing_route_records = [
        record
        for record in records
        if record["routing_status"] != "legacy_surface_routed_as_archival"
        or record["ci_path_filter_status"] != "legacy_path_filter_present"
        or record["self_classification_status"] != "self_classified_archival"
    ]
    archival_surface_count = sum(
        1 for record in records if record["classification"] == "archival_non_authoritative"
    )
    return {
        "schema": TRACKED_LEGACY_SURFACE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "legacy_root": LEGACY_ROOT,
        "workflow_path": WORKFLOW_PATH,
        "readme_path": README_PATH,
        "docs_readme_path": DOCS_README_PATH,
        "legacy_surface_count": len(records),
        "archival_surface_count": archival_surface_count,
        "missing_route_count": len(missing_route_records),
        "missing_route_records": missing_route_records,
        "legacy_surface_records": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records tracked old/** Markdown planning surfaces, "
            "their archival non-authoritative classification, self-classification "
            "banners, obsolete alphaevolve/* package-path signals, legacy checkbox "
            "plan signals, README/docs routing, and old/** GitHub Actions path "
            "filter coverage. It does not claim owner review signoff or that "
            "archival plans are implementation evidence."
        ),
    }


def validate_tracked_legacy_surface_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> TrackedLegacySurfaceBoundaryValidation:
    data, read_issues = _load_boundary(
        tracked_legacy_surface_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return TrackedLegacySurfaceBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = tracked_legacy_surface_boundary_record(root)
    issues: list[TrackedLegacySurfaceBoundaryIssue] = []
    if data.get("schema") != TRACKED_LEGACY_SURFACE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported tracked legacy surface boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "legacy surface boundary must not claim owner-reviewed implementation evidence"))
    for key in (
        "legacy_root",
        "workflow_path",
        "readme_path",
        "docs_readme_path",
        "legacy_surface_count",
        "archival_surface_count",
        "missing_route_count",
        "missing_route_records",
        "legacy_surface_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current tracked legacy surface inputs"))
    if data.get("legacy_surface_count") != data.get("archival_surface_count"):
        issues.append(_issue("unclassified_legacy_surface", "all tracked legacy surfaces must be classified archival_non_authoritative"))
    if data.get("missing_route_count") != 0:
        issues.append(_issue("missing_legacy_route", "tracked legacy surfaces must have README/docs routing, self-classification, and CI path-filter coverage"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "tracked old/** Markdown planning surfaces" not in boundary_text
        or "archival non-authoritative classification" not in boundary_text
        or "old/** GitHub Actions path filter" not in boundary_text
        or "does not claim owner review signoff" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate archival classification from owner-reviewed evidence"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return TrackedLegacySurfaceBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        legacy_surface_count=data.get("legacy_surface_count") if isinstance(data.get("legacy_surface_count"), int) else 0,
        archival_surface_count=data.get("archival_surface_count") if isinstance(data.get("archival_surface_count"), int) else 0,
        missing_route_count=data.get("missing_route_count") if isinstance(data.get("missing_route_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_tracked_legacy_surface_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_tracked_legacy_surface_boundary(boundary)
    lines = [
        "Tracked legacy surface boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| legacy_surface_count | {validation.legacy_surface_count} |",
        f"| archival_surface_count | {validation.archival_surface_count} |",
        f"| missing_route_count | {validation.missing_route_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _legacy_surface_record(
    root: Path,
    path: str,
    readme_text: str,
    docs_readme_text: str,
    workflow_text: str,
) -> dict[str, Any]:
    full_path = root / path
    text = _read_text(full_path)
    heading = _first_heading(text)
    normalized_text = " ".join(text.split())
    self_classified = (
        "Historical archive" in normalized_text
        and "non-authoritative" in normalized_text
        and "not current" in normalized_text
        and "LibreEvolve implementation evidence" in normalized_text
    )
    readme_routed = "`old/`" in readme_text and "archival" in readme_text and "non-authoritative" in readme_text
    docs_routed = "`old/`" in docs_readme_text and "archival" in docs_readme_text and "non-authoritative" in docs_readme_text
    workflow_routed = '"old/**"' in workflow_text or "- old/**" in workflow_text
    return {
        "path": path,
        "exists": full_path.exists(),
        "classification": "archival_non_authoritative",
        "classification_reason": (
            "tracked historical implementation plan with obsolete alphaevolve/* "
            "paths and checkbox task steps; retained for context, not current evidence"
        ),
        "first_heading": heading,
        "byte_count": len(text.encode("utf-8")),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "obsolete_alphaevolve_path_count": text.count("alphaevolve/"),
        "legacy_checkbox_count": text.count("- [ ]"),
        "self_classification_status": (
            "self_classified_archival" if self_classified else "self_classification_missing"
        ),
        "readme_route_status": "archival_route_present" if readme_routed else "archival_route_missing",
        "docs_readme_route_status": "archival_route_present" if docs_routed else "archival_route_missing",
        "routing_status": (
            "legacy_surface_routed_as_archival"
            if readme_routed and docs_routed
            else "legacy_surface_routing_incomplete"
        ),
        "ci_path_filter_status": (
            "legacy_path_filter_present" if workflow_routed else "legacy_path_filter_missing"
        ),
        "implementation_evidence_status": "not_current_implementation_evidence",
    }


def _tracked_legacy_markdown_paths(root: Path) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "ls-files", LEGACY_ROOT],
            check=False,
            capture_output=True,
            encoding="utf-8",
        )
    except OSError:
        completed = None
    if completed is not None and completed.returncode == 0:
        paths = [
            line.strip().replace("\\", "/")
            for line in completed.stdout.splitlines()
            if line.strip().replace("\\", "/").endswith(".md")
        ]
        return sorted(paths)
    return sorted(
        path.relative_to(root).as_posix()
        for path in (root / LEGACY_ROOT).rglob("*.md")
        if path.is_file()
    )


def _first_heading(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[TrackedLegacySurfaceBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "tracked legacy surface boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[TrackedLegacySurfaceBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_required_evidence_field", f"missing required evidence fields: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_required_evidence_field", f"unknown required evidence fields: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[TrackedLegacySurfaceBoundaryIssue],
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


def _issue(code: str, message: str) -> TrackedLegacySurfaceBoundaryIssue:
    return TrackedLegacySurfaceBoundaryIssue(code, message)
