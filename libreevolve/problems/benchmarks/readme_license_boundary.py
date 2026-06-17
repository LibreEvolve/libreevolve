from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_LICENSE_BOUNDARY_SCHEMA = "libreevolve.readme_license_boundary.v1"
EXPECTED_BOUNDARY_STATUS = (
    "readme_license_static_consistency_with_rights_surface_map_without_rights_drift_gate"
)
README_PATH = "README.md"
LICENSE_PATH = "LICENSE"
PYPROJECT_PATH = "pyproject.toml"
SOURCE_RIGHTS_PATH = "papers/source_rights.json"
PAPER_SOURCE_RIGHTS_MODULE_PATH = "libreevolve/problems/benchmarks/paper_source_rights.py"
PAPER_SOURCE_RIGHTS_TEST_PATH = "tests/test_paper_source_rights.py"
README_TODO_PATH = "docs/todo/readme.md"
PROJECT_LICENSE_ID = "MIT"

EXPECTED_README_MARKERS = (
    ("license_heading", "## License"),
    ("license_sentence", "MIT. See [LICENSE](LICENSE)."),
)
EXPECTED_EVIDENCE_ANCHORS = (
    ("license_file_title", LICENSE_PATH, "MIT License"),
    ("license_file_permission", LICENSE_PATH, "Permission is hereby granted, free of charge"),
    ("license_file_warranty", LICENSE_PATH, 'THE SOFTWARE IS PROVIDED "AS IS"'),
    ("pyproject_license", PYPROJECT_PATH, 'license = "MIT"'),
    ("source_rights_schema", SOURCE_RIGHTS_PATH, "libreevolve.alphaevolve_source_pdf_rights_manifest.v1"),
    ("source_rights_policy", SOURCE_RIGHTS_PATH, "paper_derived_artifacts_must_carry_source_rights_and_reproduction_policy"),
    ("source_rights_separate_libreevolve", SOURCE_RIGHTS_PATH, "must_separate_from_libreevolve_mit_license"),
    ("source_rights_boundary_scope", SOURCE_RIGHTS_PATH, "not LibreEvolve repository licensing"),
    ("source_rights_module_boundary", PAPER_SOURCE_RIGHTS_MODULE_PATH, "distinct_from_libreevolve_license"),
    ("source_rights_module_artifact_policy", PAPER_SOURCE_RIGHTS_MODULE_PATH, "must_separate_from_libreevolve_mit_license"),
    ("source_rights_test_rejects_mit", PAPER_SOURCE_RIGHTS_TEST_PATH, 'license_identifier"] = "MIT"'),
    ("readme_todo_owner", README_TODO_PATH, "Add README license and third-party rights boundary evidence."),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_license_sentence",
    "license_file_mit_text",
    "pyproject_license_identifier",
    "source_rights_manifest_policy",
    "source_rights_distinct_from_libreevolve_license",
    "paper_source_rights_module_validator",
    "paper_source_rights_tests",
    "active_todo_owner_anchor",
    "packaged_license_file_verification",
    "third_party_rights_semantic_map",
    "license_metadata_drift_gate",
    "paper_rights_policy_drift_gate",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "packaged_license_file_verification": "not_recorded_locally",
    "license_metadata_drift_gate": "not_recorded_locally",
    "paper_rights_policy_drift_gate": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmeLicenseBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeLicenseBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readme_marker_count: int
    missing_readme_marker_count: int
    evidence_anchor_count: int
    missing_evidence_anchor_count: int
    rights_surface_map_count: int
    missing_evidence_count: int
    issues: list[ReadmeLicenseBoundaryIssue]


def readme_license_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the README license and third-party rights static evidence map."""

    root_path = Path(root)
    readme_text = _read_text(root_path / README_PATH)
    texts = {
        path: _read_text(root_path / path)
        for path in (
            LICENSE_PATH,
            PYPROJECT_PATH,
            SOURCE_RIGHTS_PATH,
            PAPER_SOURCE_RIGHTS_MODULE_PATH,
            PAPER_SOURCE_RIGHTS_TEST_PATH,
            README_TODO_PATH,
        )
    }
    readme_marker_records = [
        _marker_record(record_id, README_PATH, readme_text, marker)
        for record_id, marker in EXPECTED_README_MARKERS
    ]
    evidence_anchor_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_EVIDENCE_ANCHORS
    ]
    missing_readme_markers = [
        record for record in readme_marker_records if record["marker_status"] != "marker_present"
    ]
    missing_evidence_anchors = [
        record for record in evidence_anchor_records if record["marker_status"] != "marker_present"
    ]
    pyproject_license = _pyproject_license(root_path / PYPROJECT_PATH)
    source_rights = _source_rights_summary(root_path / SOURCE_RIGHTS_PATH)
    rights_surface_records = _rights_surface_records(source_rights)
    map_present = (
        not missing_readme_markers
        and not missing_evidence_anchors
        and pyproject_license == PROJECT_LICENSE_ID
        and source_rights["source_rights_policy"]
        == "paper_derived_artifacts_must_carry_source_rights_and_reproduction_policy"
        and source_rights["must_separate_from_libreevolve_mit_license"] is True
        and source_rights["publication_ready_without_rights_review"] is False
        and rights_surface_records
        and all(record["map_status"] == "mapped" for record in rights_surface_records)
    )
    return {
        "schema": README_LICENSE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "license_path": LICENSE_PATH,
        "pyproject_path": PYPROJECT_PATH,
        "source_rights_path": SOURCE_RIGHTS_PATH,
        "paper_source_rights_module_path": PAPER_SOURCE_RIGHTS_MODULE_PATH,
        "test_paths": [PAPER_SOURCE_RIGHTS_TEST_PATH],
        "todo_paths": [README_TODO_PATH],
        "readme_marker_count": len(readme_marker_records),
        "missing_readme_marker_count": len(missing_readme_markers),
        "missing_readme_marker_records": missing_readme_markers,
        "readme_marker_records": readme_marker_records,
        "project_license_id": PROJECT_LICENSE_ID,
        "pyproject_license_id": pyproject_license,
        "source_rights_summary": source_rights,
        "rights_surface_map_count": len(rights_surface_records),
        "rights_surface_map_records": rights_surface_records,
        "rights_surface_map_status": (
            "all_source_rights_claim_surfaces_mapped"
            if rights_surface_records
            and all(record["map_status"] == "mapped" for record in rights_surface_records)
            else "source_rights_claim_surface_map_incomplete"
        ),
        "evidence_anchor_count": len(evidence_anchor_records),
        "missing_evidence_anchor_count": len(missing_evidence_anchors),
        "missing_evidence_anchor_records": missing_evidence_anchors,
        "evidence_anchor_records": evidence_anchor_records,
        "readme_license_map_status": (
            "readme_license_static_map_present"
            if map_present
            else "readme_license_static_map_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the README License heading and MIT sentence, "
            "the LICENSE file MIT text markers, pyproject license metadata, "
            "papers/source_rights.json policy markers, paper-source-rights "
            "module validators, paper-source-rights tests, and active TODO "
            "ownership. It also records a bounded third-party source-rights "
            "claim-surface map from papers/source_rights.json. It keeps "
            "third-party paper/source rights separate from LibreEvolve's MIT "
            "repository license. It does not claim packaged license-file "
            "verification, license metadata drift gating, paper-rights policy "
            "drift gating, or owner review signoff."
        ),
    }


def validate_readme_license_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeLicenseBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_license_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeLicenseBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = readme_license_boundary_record(root)
    issues: list[ReadmeLicenseBoundaryIssue] = []
    if data.get("schema") != README_LICENSE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README license boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README license boundary must not claim rights drift gating"))
    for key in (
        "readme_path",
        "license_path",
        "pyproject_path",
        "source_rights_path",
        "paper_source_rights_module_path",
        "test_paths",
        "todo_paths",
        "readme_marker_count",
        "missing_readme_marker_count",
        "missing_readme_marker_records",
        "readme_marker_records",
        "project_license_id",
        "pyproject_license_id",
        "source_rights_summary",
        "rights_surface_map_count",
        "rights_surface_map_records",
        "rights_surface_map_status",
        "evidence_anchor_count",
        "missing_evidence_anchor_count",
        "missing_evidence_anchor_records",
        "evidence_anchor_records",
        "readme_license_map_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current README license inputs"))
    if data.get("missing_readme_marker_count") != 0:
        issues.append(_issue("missing_readme_license_marker", "README license markers are incomplete"))
    if data.get("missing_evidence_anchor_count") != 0:
        issues.append(_issue("missing_readme_license_evidence_anchor", "README license evidence anchors are incomplete"))
    if data.get("pyproject_license_id") != PROJECT_LICENSE_ID:
        issues.append(_issue("invalid_pyproject_license_id", "pyproject license must stay MIT"))
    expected_surface_count = len(expected["source_rights_summary"].get("claim_surfaces", []))
    if data.get("rights_surface_map_count") != expected_surface_count:
        issues.append(_issue("invalid_rights_surface_map_count", "source-rights claim-surface map count changed"))
    if data.get("rights_surface_map_status") != "all_source_rights_claim_surfaces_mapped":
        issues.append(_issue("invalid_rights_surface_map_status", "source-rights claim-surface map is incomplete"))
    if data.get("readme_license_map_status") != "readme_license_static_map_present":
        issues.append(_issue("invalid_readme_license_map_status", "README license static map must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "README License heading and MIT sentence" not in boundary_text
        or "third-party paper/source rights separate" not in boundary_text
        or "bounded third-party source-rights claim-surface map" not in boundary_text
        or "does not claim packaged license-file verification" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate README license consistency from rights drift proof"))
    return ReadmeLicenseBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readme_marker_count=data.get("readme_marker_count") if isinstance(data.get("readme_marker_count"), int) else 0,
        missing_readme_marker_count=data.get("missing_readme_marker_count") if isinstance(data.get("missing_readme_marker_count"), int) else 0,
        evidence_anchor_count=data.get("evidence_anchor_count") if isinstance(data.get("evidence_anchor_count"), int) else 0,
        missing_evidence_anchor_count=data.get("missing_evidence_anchor_count") if isinstance(data.get("missing_evidence_anchor_count"), int) else 0,
        rights_surface_map_count=data.get("rights_surface_map_count") if isinstance(data.get("rights_surface_map_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_license_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_license_boundary(boundary)
    lines = [
        "README license boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| readme_marker_count | {validation.readme_marker_count} |",
        f"| missing_readme_marker_count | {validation.missing_readme_marker_count} |",
        f"| evidence_anchor_count | {validation.evidence_anchor_count} |",
        f"| missing_evidence_anchor_count | {validation.missing_evidence_anchor_count} |",
        f"| rights_surface_map_count | {validation.rights_surface_map_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _pyproject_license(path: Path) -> str | None:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return None
    value = data.get("project", {}).get("license")
    return value if isinstance(value, str) else None


def _source_rights_summary(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {
            "summary_status": "source_rights_unreadable_or_missing",
            "source_rights_policy": None,
            "source_rights_count": None,
            "artifact_classes": [],
            "claim_surfaces": [],
            "reproduction_policy": None,
            "must_separate_from_libreevolve_mit_license": None,
            "publication_ready_without_rights_review": None,
        }
    sources = data.get("sources")
    first_policy = {}
    if isinstance(sources, list) and sources and isinstance(sources[0], dict):
        policy = sources[0].get("paper_derived_artifact_policy")
        if isinstance(policy, dict):
            first_policy = policy
    return {
        "summary_status": "source_rights_summary_recorded",
        "source_rights_policy": data.get("source_rights_policy"),
        "source_rights_count": data.get("source_rights_count"),
        "artifact_classes": first_policy.get("artifact_classes", []),
        "claim_surfaces": first_policy.get("claim_surfaces", []),
        "reproduction_policy": first_policy.get("reproduction_policy"),
        "must_separate_from_libreevolve_mit_license": first_policy.get(
            "must_separate_from_libreevolve_mit_license"
        ),
        "publication_ready_without_rights_review": first_policy.get(
            "publication_ready_without_rights_review"
        ),
    }


def _rights_surface_records(source_rights: dict[str, Any]) -> list[dict[str, Any]]:
    claim_surfaces = source_rights.get("claim_surfaces")
    artifact_classes = source_rights.get("artifact_classes")
    if not isinstance(claim_surfaces, list) or not all(
        isinstance(surface, str) for surface in claim_surfaces
    ):
        return []
    if not isinstance(artifact_classes, list) or not all(
        isinstance(artifact_class, str) for artifact_class in artifact_classes
    ):
        artifact_classes = []
    reproduction_policy = source_rights.get("reproduction_policy")
    must_separate = source_rights.get("must_separate_from_libreevolve_mit_license")
    publication_ready = source_rights.get("publication_ready_without_rights_review")
    records: list[dict[str, Any]] = []
    for surface in claim_surfaces:
        mapped = (
            bool(artifact_classes)
            and reproduction_policy
            == "third_party_paper_source_rights_require_separate_review_before_reproduction"
            and must_separate is True
            and publication_ready is False
        )
        records.append(
            {
                "claim_surface": surface,
                "source_rights_policy": source_rights.get("source_rights_policy"),
                "artifact_classes": list(artifact_classes),
                "reproduction_policy": reproduction_policy,
                "must_separate_from_libreevolve_mit_license": must_separate,
                "publication_ready_without_rights_review": publication_ready,
                "map_status": "mapped" if mapped else "missing_policy_field",
            }
        )
    return records


def _marker_record(record_id: str, path: str, text: str, marker: str) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "path": path,
        "required_marker": marker,
        "marker_status": "marker_present" if marker in text else "marker_missing",
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ReadmeLicenseBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README license boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeLicenseBoundaryIssue],
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
    issues: list[ReadmeLicenseBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeLicenseBoundaryIssue:
    return ReadmeLicenseBoundaryIssue(code, message)
