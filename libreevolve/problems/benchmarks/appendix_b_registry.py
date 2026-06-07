from __future__ import annotations

import json
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
