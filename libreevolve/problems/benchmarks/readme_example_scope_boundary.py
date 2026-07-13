from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.example_scope import (
    example_benchmark_scope_records,
    validate_example_benchmark_scope,
)


README_EXAMPLE_SCOPE_BOUNDARY_SCHEMA = "libreevolve.readme_example_scope_boundary.v1"
EXPECTED_BOUNDARY_STATUS = (
    "readme_example_scope_structural_map_without_benchmark_certification"
)
README_PATH = "README.md"
README_TODO_PATH = "docs/todo/readme.md"
EXAMPLE_SCOPE_MODULE_PATH = "libreevolve/problems/benchmarks/example_scope.py"
EXAMPLE_SCOPE_JSON_PATH = "papers/example_benchmark_scope.json"
EXAMPLE_SCOPE_TEST_PATH = "tests/test_example_benchmark_scope.py"
BENCHMARK_HARDENING_TEST_PATH = "tests/test_benchmark_hardening.py"
EXAMPLES_TEST_PATH = "tests/test_examples.py"
SORTING_NETWORK_BOUNDARY_PATH = "papers/sorting_network_rediscovery_boundary.json"
BENCHMARK_FIXTURE_READINESS_PATH = "papers/benchmark_fixture_readiness_boundary.json"
ROADMAP_PORTFOLIO_BOUNDARY_PATH = (
    "papers/roadmap_representative_benchmark_portfolio_boundary.json"
)
PAPERS_README_PATH = "papers/README.md"
STATUS_PATH = "docs/status.md"

EXPECTED_README_MARKERS = (
    ("heading", "## Example Scope"),
    ("intro", "The bundled examples are intentionally small:"),
    ("optimization_pressure", "Optimization-pressure seeds"),
    ("neutral_plateau", "Neutral plateau/diversity fixtures"),
    ("candidate_runner_scope", "`candidate_runner_expression` is a non-comparable contract smoke fixture."),
    ("candidate_runner_c_scope", "`candidate_runner_c` is a non-comparable real-compiler contract smoke fixture."),
    ("sorting_network_pair", "`sorting_network_8` and `sorting_network_9`"),
    ("bounded_candidates", "bounded benchmark candidates"),
    ("zero_one_validation", "exhaustive zero-one validation"),
    ("known_targets", "known comparator targets"),
    ("not_paper_comparable", "not paper-comparable evidence until repeated runs"),
    ("hardening_bundle", "hardening bundle helper emits generic"),
    ("not_certified_rediscovery", "not a certified rediscovery result"),
    ("sorting_boundary_link", "`papers/sorting_network_rediscovery_boundary.json`"),
    (
        "benchmark_only_when_sidecar_says_so",
        "Treat an example as benchmark evidence only when its own docs or paper sidecar",
    ),
)
EXPECTED_EVIDENCE_ANCHORS = (
    ("example_scope_schema", EXAMPLE_SCOPE_MODULE_PATH, "EXAMPLE_BENCHMARK_SCOPE_SCHEMA"),
    ("example_scope_records", EXAMPLE_SCOPE_MODULE_PATH, "def example_benchmark_scope_records"),
    ("example_scope_validation", EXAMPLE_SCOPE_MODULE_PATH, "def validate_example_benchmark_scope"),
    ("example_scope_render", EXAMPLE_SCOPE_MODULE_PATH, "def render_example_benchmark_scope_summary"),
    ("scope_json_schema", EXAMPLE_SCOPE_JSON_PATH, "libreevolve.example_benchmark_scope.v1"),
    ("scope_json_sorting_8", EXAMPLE_SCOPE_JSON_PATH, "\"problem_id\": \"sorting_network_8\""),
    ("scope_json_sorting_9", EXAMPLE_SCOPE_JSON_PATH, "\"problem_id\": \"sorting_network_9\""),
    ("scope_json_candidate_runner", EXAMPLE_SCOPE_JSON_PATH, "\"problem_id\": \"candidate_runner_expression\""),
    ("scope_json_candidate_runner_c", EXAMPLE_SCOPE_JSON_PATH, "\"problem_id\": \"candidate_runner_c\""),
    ("scope_json_no_comparable", EXAMPLE_SCOPE_JSON_PATH, "\"alphaevolve_comparable\": false"),
    ("scope_test_non_comparable", EXAMPLE_SCOPE_TEST_PATH, "test_example_scope_records_keep_shipped_examples_non_comparable"),
    ("scope_test_reject_smoke", EXAMPLE_SCOPE_TEST_PATH, "test_example_scope_rejects_smoke_record_marked_alphaevolve_comparable"),
    ("scope_test_paper_claim", EXAMPLE_SCOPE_TEST_PATH, "test_example_scope_requires_paper_claims_to_be_comparable"),
    ("hardening_test_sorting_8", BENCHMARK_HARDENING_TEST_PATH, "test_sorting_network_8_hardening_bundle_writes_benchmark_evidence"),
    ("hardening_test_sorting_9", BENCHMARK_HARDENING_TEST_PATH, "test_sorting_network_9_hardening_bundle_writes_benchmark_evidence"),
    ("examples_test_sorting_8", EXAMPLES_TEST_PATH, "test_sorting_network_8_known_19_comparator_target_is_valid"),
    ("examples_test_sorting_9", EXAMPLES_TEST_PATH, "test_sorting_network_9_known_25_comparator_target_is_valid"),
    ("examples_test_candidate_runner", EXAMPLES_TEST_PATH, "test_candidate_runner_expression_example_loads_builds_and_scores"),
    ("examples_test_candidate_runner_c", EXAMPLES_TEST_PATH, "test_candidate_runner_c_example_loads_compiles_and_scores"),
    ("sorting_boundary", SORTING_NETWORK_BOUNDARY_PATH, "bounded_sorting_network_fixtures_available"),
    (
        "benchmark_fixture_boundary",
        BENCHMARK_FIXTURE_READINESS_PATH,
        "smoke_scope_with_deterministic_matrix_calibration_only",
    ),
    ("roadmap_portfolio_boundary", ROADMAP_PORTFOLIO_BOUNDARY_PATH, "smoke_fixture_guardrail"),
    ("papers_readme_scope_catalog", PAPERS_README_PATH, "shipped-example scope"),
    ("status_sorting_scope", STATUS_PATH, "non-comparable benchmark candidates"),
    ("readme_todo_owner", README_TODO_PATH, "Add README example-scope drift and benchmark-claim evidence."),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_example_scope_markers",
    "example_scope_registry_records",
    "example_scope_sidecar_records",
    "example_path_existence_records",
    "smoke_fixture_classification_records",
    "benchmark_candidate_classification_records",
    "sorting_network_boundary_anchor",
    "benchmark_fixture_readiness_anchor",
    "benchmark_hardening_test_anchor",
    "example_validator_test_anchor",
    "status_and_papers_index_anchors",
    "active_todo_owner_anchor",
    "semantic_scope_claim_verifier",
    "runtime_scope_metadata_comparison",
    "paper_comparable_certification_gate",
    "new_example_surface_detector",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "semantic_scope_claim_verifier": "not_recorded_locally",
    "runtime_scope_metadata_comparison": "not_recorded_locally",
    "paper_comparable_certification_gate": "not_recorded_locally",
    "new_example_surface_detector": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmeExampleScopeBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeExampleScopeBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readme_marker_count: int
    missing_readme_marker_count: int
    evidence_anchor_count: int
    missing_evidence_anchor_count: int
    scope_record_count: int
    comparable_problem_count: int
    missing_evidence_count: int
    issues: list[ReadmeExampleScopeBoundaryIssue]


def readme_example_scope_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the README Example Scope structural evidence map."""

    root_path = Path(root)
    paths = {
        README_PATH,
        README_TODO_PATH,
        EXAMPLE_SCOPE_MODULE_PATH,
        EXAMPLE_SCOPE_JSON_PATH,
        EXAMPLE_SCOPE_TEST_PATH,
        BENCHMARK_HARDENING_TEST_PATH,
        EXAMPLES_TEST_PATH,
        SORTING_NETWORK_BOUNDARY_PATH,
        BENCHMARK_FIXTURE_READINESS_PATH,
        ROADMAP_PORTFOLIO_BOUNDARY_PATH,
        PAPERS_README_PATH,
        STATUS_PATH,
    }
    texts = {path: _read_text(root_path / path) for path in paths}
    readme_marker_records = [
        _marker_record(record_id, README_PATH, texts[README_PATH], marker)
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
    scope_records = example_benchmark_scope_records()
    scope_validation = validate_example_benchmark_scope(scope_records)
    example_path_records = [
        {
            "problem_id": record.get("problem_id"),
            "path": record.get("path"),
            "level": record.get("level"),
            "alphaevolve_comparable": record.get("alphaevolve_comparable"),
            "path_status": (
                "path_present"
                if isinstance(record.get("path"), str)
                and (root_path / record["path"]).exists()
                else "path_missing"
            ),
        }
        for record in scope_records
    ]
    benchmark_problem_ids = [
        record["problem_id"]
        for record in scope_records
        if record.get("level") == "benchmark"
        and isinstance(record.get("problem_id"), str)
    ]
    smoke_problem_ids = [
        record["problem_id"]
        for record in scope_records
        if record.get("level") == "smoke"
        and isinstance(record.get("problem_id"), str)
    ]
    comparable_problem_ids = list(scope_validation.comparable_problem_ids)
    missing_example_paths = [
        record["path"]
        for record in example_path_records
        if record["path_status"] != "path_present"
        and isinstance(record.get("path"), str)
    ]
    return {
        "schema": README_EXAMPLE_SCOPE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "example_scope_registry_path": EXAMPLE_SCOPE_MODULE_PATH,
        "example_scope_sidecar_path": EXAMPLE_SCOPE_JSON_PATH,
        "source_paths": [EXAMPLE_SCOPE_MODULE_PATH],
        "test_paths": [EXAMPLE_SCOPE_TEST_PATH, BENCHMARK_HARDENING_TEST_PATH, EXAMPLES_TEST_PATH],
        "sidecar_paths": [
            EXAMPLE_SCOPE_JSON_PATH,
            SORTING_NETWORK_BOUNDARY_PATH,
            BENCHMARK_FIXTURE_READINESS_PATH,
            ROADMAP_PORTFOLIO_BOUNDARY_PATH,
        ],
        "todo_paths": [README_TODO_PATH],
        "readme_marker_count": len(readme_marker_records),
        "missing_readme_marker_count": len(missing_readme_markers),
        "missing_readme_marker_records": missing_readme_markers,
        "readme_marker_records": readme_marker_records,
        "evidence_anchor_count": len(evidence_anchor_records),
        "missing_evidence_anchor_count": len(missing_evidence_anchors),
        "missing_evidence_anchor_records": missing_evidence_anchors,
        "evidence_anchor_records": evidence_anchor_records,
        "scope_record_count": len(scope_records),
        "scope_registry_validation_status": (
            "scope_registry_valid" if scope_validation.ok else "scope_registry_invalid"
        ),
        "smoke_problem_ids": smoke_problem_ids,
        "benchmark_problem_ids": benchmark_problem_ids,
        "comparable_problem_ids": comparable_problem_ids,
        "comparable_problem_count": len(comparable_problem_ids),
        "example_path_records": example_path_records,
        "missing_example_paths": missing_example_paths,
        "example_path_status": (
            "all_example_scope_paths_present"
            if not missing_example_paths
            else "missing_example_scope_paths"
        ),
        "readme_example_scope_map_status": (
            "readme_example_scope_structural_map_present"
            if not missing_readme_markers
            and not missing_evidence_anchors
            and scope_validation.ok
            and not missing_example_paths
            and not comparable_problem_ids
            else "readme_example_scope_structural_map_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the README Example Scope markers, shipped "
            "example-scope registry records, the committed example-scope JSON "
            "sidecar, example path existence, smoke and benchmark-candidate "
            "classification, sorting-network boundary anchors, benchmark "
            "fixture-readiness anchors, hardening and validator test anchors, "
            "status/papers index anchors, and active TODO ownership. It does "
            "not claim semantic scope-claim verification, runtime metadata "
            "comparison, paper-comparable certification gates, new example "
            "surface detection, or owner review signoff."
        ),
    }


def validate_readme_example_scope_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeExampleScopeBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_example_scope_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeExampleScopeBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = readme_example_scope_boundary_record(root)
    issues: list[ReadmeExampleScopeBoundaryIssue] = []
    if data.get("schema") != README_EXAMPLE_SCOPE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README example-scope boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README example-scope boundary must not claim benchmark certification"))
    for key in (
        "readme_path",
        "example_scope_registry_path",
        "example_scope_sidecar_path",
        "source_paths",
        "test_paths",
        "sidecar_paths",
        "todo_paths",
        "readme_marker_count",
        "missing_readme_marker_count",
        "missing_readme_marker_records",
        "readme_marker_records",
        "evidence_anchor_count",
        "missing_evidence_anchor_count",
        "missing_evidence_anchor_records",
        "evidence_anchor_records",
        "scope_record_count",
        "scope_registry_validation_status",
        "smoke_problem_ids",
        "benchmark_problem_ids",
        "comparable_problem_ids",
        "comparable_problem_count",
        "example_path_records",
        "missing_example_paths",
        "example_path_status",
        "readme_example_scope_map_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current README example-scope inputs"))
    if data.get("missing_readme_marker_count") != 0:
        issues.append(_issue("missing_readme_example_scope_marker", "README example-scope markers are incomplete"))
    if data.get("missing_evidence_anchor_count") != 0:
        issues.append(_issue("missing_readme_example_scope_evidence_anchor", "README example-scope evidence anchors are incomplete"))
    if data.get("scope_registry_validation_status") != "scope_registry_valid":
        issues.append(_issue("invalid_scope_registry_validation_status", "example scope registry must validate"))
    if data.get("comparable_problem_count") != 0:
        issues.append(_issue("paper_comparable_overclaim", "shipped examples must not be paper-comparable without certification"))
    if data.get("example_path_status") != "all_example_scope_paths_present":
        issues.append(_issue("missing_example_scope_path", "example scope paths must exist"))
    if data.get("readme_example_scope_map_status") != "readme_example_scope_structural_map_present":
        issues.append(_issue("invalid_readme_example_scope_map_status", "README example-scope structural map must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "README Example Scope markers" not in boundary_text
        or "paper-comparable certification gates" not in boundary_text
        or "does not claim semantic scope-claim verification" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate structural scope evidence from certification"))
    return ReadmeExampleScopeBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readme_marker_count=data.get("readme_marker_count") if isinstance(data.get("readme_marker_count"), int) else 0,
        missing_readme_marker_count=data.get("missing_readme_marker_count") if isinstance(data.get("missing_readme_marker_count"), int) else 0,
        evidence_anchor_count=data.get("evidence_anchor_count") if isinstance(data.get("evidence_anchor_count"), int) else 0,
        missing_evidence_anchor_count=data.get("missing_evidence_anchor_count") if isinstance(data.get("missing_evidence_anchor_count"), int) else 0,
        scope_record_count=data.get("scope_record_count") if isinstance(data.get("scope_record_count"), int) else 0,
        comparable_problem_count=data.get("comparable_problem_count") if isinstance(data.get("comparable_problem_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_example_scope_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_example_scope_boundary(boundary)
    lines = [
        "README Example Scope boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| readme_marker_count | {validation.readme_marker_count} |",
        f"| missing_readme_marker_count | {validation.missing_readme_marker_count} |",
        f"| evidence_anchor_count | {validation.evidence_anchor_count} |",
        f"| missing_evidence_anchor_count | {validation.missing_evidence_anchor_count} |",
        f"| scope_record_count | {validation.scope_record_count} |",
        f"| comparable_problem_count | {validation.comparable_problem_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


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
) -> tuple[dict[str, Any] | None, list[ReadmeExampleScopeBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README example-scope boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeExampleScopeBoundaryIssue],
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
    issues: list[ReadmeExampleScopeBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeExampleScopeBoundaryIssue:
    return ReadmeExampleScopeBoundaryIssue(code, message)
