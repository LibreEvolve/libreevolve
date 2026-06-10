from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REGISTRY_PATH = Path(__file__).with_name("alphaevolve_appendix_b.json")
REGISTRY_SCHEMA = "libreevolve.alphaevolve_appendix_b_registry.v1"
EXPECTED_FAMILY_IDS = (
    "autocorrelation_bounds_k3",
    "autocorrelation_bounds_k4",
    "autocorrelation_bounds_k5",
    "uncertainty_inequality",
    "erdos_minimum_overlap",
    "sums_differences_finite_sets",
    "regular_hexagon_packing",
    "max_min_distance_point_sets",
    "heilbronn_triangle",
    "heilbronn_convex_region",
    "kissing_number_d11",
    "circle_packing_unit_square",
    "circle_packing_perimeter4_rectangle",
)
EXPECTED_AUTOCORRELATION_LABELS = {
    "autocorrelation_bounds_k3": {
        "source_section_id": "B.1",
        "paper_heading": "First autocorrelation inequality",
        "constant_id": "C1",
        "display_label": "B.1. First autocorrelation inequality (C1)",
        "internal_label_policy": "internal_id_only_not_paper_label",
    },
    "autocorrelation_bounds_k4": {
        "source_section_id": "B.2",
        "paper_heading": "Second autocorrelation inequality",
        "constant_id": "C2",
        "display_label": "B.2. Second autocorrelation inequality (C2)",
        "internal_label_policy": "internal_id_only_not_paper_label",
    },
    "autocorrelation_bounds_k5": {
        "source_section_id": "B.3",
        "paper_heading": "Third autocorrelation inequality",
        "constant_id": "C3",
        "display_label": "B.3. Third autocorrelation inequality (C3)",
        "internal_label_policy": "internal_id_only_not_paper_label",
    },
}
EXPECTED_AUTOCORRELATION_STEP_EVIDENCE = {
    "autocorrelation_bounds_k3": {
        "source_section_id": "B.1",
        "constant_id": "C1",
        "domain": "[-1/4, 1/4]",
        "interval_count": 600,
        "interval_spacing": "equally_spaced",
        "function_sign_policy": "non_negative",
        "bound_direction": "upper_bound",
        "previous_bound": 1.5098,
        "previous_bound_source": "[70]",
        "reported_bound": 1.5053,
        "reported_bound_relation": "C1 <= 1.5053",
        "construction_payload_status": "not_recorded_locally",
    },
    "autocorrelation_bounds_k4": {
        "source_section_id": "B.2",
        "constant_id": "C2",
        "domain": "[-1/4, 1/4]",
        "interval_count": 50,
        "interval_spacing": "equally_spaced",
        "function_sign_policy": "non_negative",
        "bound_direction": "lower_bound",
        "previous_bound": 0.88922,
        "previous_bound_source": "[70]",
        "reported_bound": 0.8962,
        "reported_bound_relation": "0.8962 <= C2",
        "construction_payload_status": "not_recorded_locally",
    },
    "autocorrelation_bounds_k5": {
        "source_section_id": "B.3",
        "constant_id": "C3",
        "domain": "[-1/4, 1/4]",
        "interval_count": 400,
        "interval_spacing": "equally_spaced",
        "function_sign_policy": "signed_real",
        "bound_direction": "upper_bound",
        "previous_bound": 1.45810,
        "previous_bound_source": "[104, page 75]",
        "reported_bound": 1.4557,
        "reported_bound_relation": "C3 <= 1.4557",
        "construction_payload_status": "not_recorded_locally",
    },
}
EXPECTED_B8_METRIC_CONVENTIONS = (
    {
        "result_id": "b8_16_points_2d",
        "source_section_id": "B.8",
        "source_figure": "Figure 12 left",
        "point_count": 16,
        "dimension": 2,
        "metric_name": "maximum_distance_over_minimum_distance",
        "reported_value_convention": "squared_max_min_ratio",
        "raw_reported_value": 12.889266112,
        "derived_ratio_transform": "sqrt(raw_reported_value)",
        "derived_ratio": 3.590162407468,
        "prior_best_value": 12.890,
        "prior_best_convention": "squared_max_min_ratio",
        "prior_best_source": "[29]",
        "comparison_unit_policy": "compare_squared_values_before_square_root_display",
        "coordinate_artifact_status": "not_recorded_locally",
    },
    {
        "result_id": "b8_14_points_3d",
        "source_section_id": "B.8",
        "source_figure": "Figure 12 right",
        "point_count": 14,
        "dimension": 3,
        "metric_name": "maximum_distance_over_minimum_distance",
        "reported_value_convention": "squared_max_min_ratio",
        "raw_reported_value": 4.165849767,
        "derived_ratio_transform": "sqrt(raw_reported_value)",
        "derived_ratio": 2.041041343775,
        "prior_best_value": 4.168,
        "prior_best_convention": "squared_max_min_ratio",
        "prior_best_source": "[29]",
        "comparison_unit_policy": "compare_squared_values_before_square_root_display",
        "coordinate_artifact_status": "not_recorded_locally",
    },
)
STATUSES = frozenset({"implemented", "implemented_smoke", "planned", "background_only", "out_of_scope"})
DIRECTIONS = frozenset({"maximize", "minimize", "satisfy", "prove"})
_ID_RE = re.compile(r"[a-z][a-z0-9_]{1,79}")


@dataclass(frozen=True)
class AppendixBRegistryIssue:
    code: str
    message: str
    family_id: str | None = None


@dataclass(frozen=True)
class AppendixBRegistryReport:
    ok: bool
    family_count: int
    implemented_count: int
    planned_count: int
    unsupported_count: int
    issues: list[AppendixBRegistryIssue]


def validate_appendix_b_registry(
    path: str | Path = REGISTRY_PATH,
    *,
    repo_root: str | Path | None = None,
) -> AppendixBRegistryReport:
    registry_path = Path(path)
    root = Path(repo_root) if repo_root is not None else registry_path.parents[3]
    issues: list[AppendixBRegistryIssue] = []
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return AppendixBRegistryReport(False, 0, 0, 0, 0, [
            AppendixBRegistryIssue("read_error", f"failed to read registry: {exc}")
        ])
    except json.JSONDecodeError as exc:
        return AppendixBRegistryReport(False, 0, 0, 0, 0, [
            AppendixBRegistryIssue("invalid_json", f"invalid registry JSON: {exc.msg}")
        ])
    if not isinstance(data, dict):
        return AppendixBRegistryReport(False, 0, 0, 0, 0, [
            AppendixBRegistryIssue("invalid_shape", "registry must be a JSON object")
        ])
    if data.get("schema") != REGISTRY_SCHEMA:
        issues.append(AppendixBRegistryIssue("invalid_schema", "unsupported registry schema"))
    if data.get("source_paper_id") != "2506.13131":
        issues.append(AppendixBRegistryIssue("invalid_source", "source_paper_id must be 2506.13131"))
    families = data.get("families")
    if not isinstance(families, list):
        return AppendixBRegistryReport(False, 0, 0, 0, 0, issues + [
            AppendixBRegistryIssue("invalid_families", "families must be a list")
        ])

    seen: set[str] = set()
    status_counts = {"implemented": 0, "implemented_smoke": 0, "planned": 0, "background_only": 0, "out_of_scope": 0}
    for index, family in enumerate(families):
        family_id = _family_id(family, index)
        if not isinstance(family, dict):
            issues.append(AppendixBRegistryIssue("invalid_family", "family must be an object", family_id))
            continue
        _validate_family(family, family_id, root, issues)
        if family_id in seen:
            issues.append(AppendixBRegistryIssue("duplicate_family", "duplicate family id", family_id))
        seen.add(family_id)
        status = family.get("status")
        if isinstance(status, str) and status in status_counts:
            status_counts[status] += 1
    missing = set(EXPECTED_FAMILY_IDS) - seen
    extra = seen - set(EXPECTED_FAMILY_IDS)
    for family_id in sorted(missing):
        issues.append(AppendixBRegistryIssue("missing_family", "missing Appendix B family", family_id))
    for family_id in sorted(extra):
        issues.append(AppendixBRegistryIssue("extra_family", "unknown Appendix B family", family_id))
    return AppendixBRegistryReport(
        ok=not issues,
        family_count=len(families),
        implemented_count=status_counts["implemented"] + status_counts["implemented_smoke"],
        planned_count=status_counts["planned"],
        unsupported_count=status_counts["background_only"] + status_counts["out_of_scope"],
        issues=issues,
    )


def _validate_family(
    family: dict[str, Any],
    family_id: str,
    repo_root: Path,
    issues: list[AppendixBRegistryIssue],
) -> None:
    if _ID_RE.fullmatch(family_id) is None:
        issues.append(AppendixBRegistryIssue("invalid_family_id", "family id must be snake_case", family_id))
    _require_text(family, "name", family_id, issues)
    _validate_autocorrelation_paper_label(family, family_id, issues)
    _validate_autocorrelation_step_evidence(family, family_id, issues)
    _validate_b8_metric_conventions(family, family_id, issues)
    status = family.get("status")
    if status not in STATUSES:
        issues.append(AppendixBRegistryIssue("invalid_status", "invalid implementation status", family_id))
    objective = family.get("objective")
    if not isinstance(objective, dict):
        issues.append(AppendixBRegistryIssue("invalid_objective", "objective must be an object", family_id))
    else:
        _require_text(objective, "metric", family_id, issues)
        if objective.get("direction") not in DIRECTIONS:
            issues.append(AppendixBRegistryIssue("invalid_direction", "invalid objective direction", family_id))
    target = family.get("target_baseline")
    if not isinstance(target, dict) or not isinstance(target.get("status"), str) or not target["status"]:
        issues.append(AppendixBRegistryIssue("invalid_target_baseline", "target_baseline.status is required", family_id))
    artifact_schema = family.get("artifact_schema")
    if not isinstance(artifact_schema, dict):
        issues.append(AppendixBRegistryIssue("invalid_artifact_schema", "artifact_schema must be an object", family_id))
    else:
        _require_text(artifact_schema, "construction", family_id, issues)
        _require_text(artifact_schema, "certificate", family_id, issues)
    _require_text(family, "certification", family_id, issues)
    _require_text(family, "rationale", family_id, issues)
    citations = family.get("paper_citations")
    if not isinstance(citations, list) or "2506.13131" not in citations:
        issues.append(AppendixBRegistryIssue("missing_alphaevolve_citation", "paper_citations must include 2506.13131", family_id))
    fixture = family.get("fixture")
    if status in {"implemented", "implemented_smoke"}:
        if not isinstance(fixture, str) or not fixture:
            issues.append(AppendixBRegistryIssue("missing_fixture", "implemented family requires fixture", family_id))
        elif not _fixture_exists(repo_root, fixture):
            issues.append(AppendixBRegistryIssue("missing_fixture_path", f"fixture does not exist: {fixture}", family_id))
    elif fixture is not None:
        issues.append(AppendixBRegistryIssue("unexpected_fixture", "non-implemented family must not advertise a fixture", family_id))


def _validate_autocorrelation_paper_label(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    expected = EXPECTED_AUTOCORRELATION_LABELS.get(family_id)
    if expected is None:
        return
    label = family.get("paper_label")
    if not isinstance(label, dict):
        issues.append(AppendixBRegistryIssue("missing_paper_label", "B.1-B.3 autocorrelation rows require paper_label metadata", family_id))
        return
    if label.get("internal_family_id") != family_id:
        issues.append(AppendixBRegistryIssue("invalid_paper_label_internal_id", "paper_label.internal_family_id must match the registry id", family_id))
    for field, expected_value in expected.items():
        if label.get(field) != expected_value:
            issues.append(AppendixBRegistryIssue(f"invalid_paper_label_{field}", f"paper_label.{field} must match the AlphaEvolve Appendix B heading metadata", family_id))
    display_label = label.get("display_label")
    if family.get("name") != display_label:
        issues.append(AppendixBRegistryIssue("paper_label_name_mismatch", "family name must use the paper-facing B.1-B.3 display label", family_id))
    if isinstance(family.get("name"), str) and re.search(r"\bk\s*=", family["name"]):
        issues.append(AppendixBRegistryIssue("paper_label_uses_internal_k_label", "family name must not expose internal k-number labels as paper terminology", family_id))


def _validate_autocorrelation_step_evidence(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    expected = EXPECTED_AUTOCORRELATION_STEP_EVIDENCE.get(family_id)
    if expected is None:
        return
    evidence = family.get("step_function_evidence")
    if not isinstance(evidence, dict):
        issues.append(AppendixBRegistryIssue("missing_step_function_evidence", "B.1-B.3 autocorrelation rows require step_function_evidence metadata", family_id))
        return
    for field, expected_value in expected.items():
        actual = evidence.get(field)
        if isinstance(expected_value, float):
            if isinstance(actual, bool) or not isinstance(actual, (int, float)) or float(actual) != expected_value:
                issues.append(AppendixBRegistryIssue(f"invalid_step_function_{field}", f"step_function_evidence.{field} must match the AlphaEvolve Appendix B value", family_id))
        elif actual != expected_value:
            issues.append(AppendixBRegistryIssue(f"invalid_step_function_{field}", f"step_function_evidence.{field} must match the AlphaEvolve Appendix B value", family_id))
    label = family.get("paper_label")
    if isinstance(label, dict):
        if evidence.get("source_section_id") != label.get("source_section_id"):
            issues.append(AppendixBRegistryIssue("step_function_label_section_mismatch", "step_function_evidence source section must match paper_label", family_id))
        if evidence.get("constant_id") != label.get("constant_id"):
            issues.append(AppendixBRegistryIssue("step_function_label_constant_mismatch", "step_function_evidence constant id must match paper_label", family_id))


def _validate_b8_metric_conventions(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    if family_id != "max_min_distance_point_sets":
        return
    conventions = family.get("metric_convention_evidence")
    if not isinstance(conventions, list):
        issues.append(AppendixBRegistryIssue("missing_b8_metric_convention_evidence", "B.8 requires metric_convention_evidence rows", family_id))
        return
    if len(conventions) != len(EXPECTED_B8_METRIC_CONVENTIONS):
        issues.append(AppendixBRegistryIssue("invalid_b8_metric_convention_count", "B.8 must include exactly the 2D and 3D metric convention rows", family_id))
    by_id = {
        row.get("result_id"): row
        for row in conventions
        if isinstance(row, dict)
    }
    for expected in EXPECTED_B8_METRIC_CONVENTIONS:
        result_id = expected["result_id"]
        row = by_id.get(result_id)
        if not isinstance(row, dict):
            issues.append(AppendixBRegistryIssue("missing_b8_metric_convention_row", "missing B.8 metric convention row", family_id))
            continue
        for field, expected_value in expected.items():
            actual = row.get(field)
            if isinstance(expected_value, float):
                if isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isclose(float(actual), expected_value, rel_tol=0.0, abs_tol=1e-12):
                    issues.append(AppendixBRegistryIssue(f"invalid_b8_{field}", f"B.8 {field} must match the AlphaEvolve metric convention evidence", family_id))
            elif actual != expected_value:
                issues.append(AppendixBRegistryIssue(f"invalid_b8_{field}", f"B.8 {field} must match the AlphaEvolve metric convention evidence", family_id))
        raw = row.get("raw_reported_value")
        derived = row.get("derived_ratio")
        if (
            isinstance(raw, (int, float))
            and not isinstance(raw, bool)
            and isinstance(derived, (int, float))
            and not isinstance(derived, bool)
            and not math.isclose(math.sqrt(float(raw)), float(derived), rel_tol=0.0, abs_tol=1e-12)
        ):
            issues.append(AppendixBRegistryIssue("invalid_b8_derived_ratio_math", "B.8 derived_ratio must equal sqrt(raw_reported_value)", family_id))
        prior = row.get("prior_best_value")
        if (
            isinstance(raw, (int, float))
            and not isinstance(raw, bool)
            and isinstance(prior, (int, float))
            and not isinstance(prior, bool)
            and float(raw) >= float(prior)
        ):
            issues.append(AppendixBRegistryIssue("invalid_b8_improvement_direction", "B.8 raw reported squared value must improve on the prior squared value", family_id))


def _family_id(family: object, index: int) -> str:
    if isinstance(family, dict) and isinstance(family.get("id"), str):
        return family["id"]
    return f"family_{index}"


def _require_text(
    value: dict[str, Any],
    field: str,
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    raw = value.get(field)
    if not isinstance(raw, str) or not raw.strip():
        issues.append(AppendixBRegistryIssue(f"missing_{field}", f"{field} is required", family_id))


def _fixture_exists(repo_root: Path, fixture: str) -> bool:
    if fixture.startswith("/") or "\\" in fixture or ".." in Path(fixture).parts:
        return False
    path = repo_root / fixture
    return (
        path.is_dir()
        and (path / "metrics.yaml").is_file()
        and (path / "validate.py").is_file()
        and (path / "task_description.txt").is_file()
    )
