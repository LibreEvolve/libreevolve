from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

OBJECTIVE_FRONTIER_SCHEMA = "libreevolve.objective_frontier.v1"
OBJECTIVE_METRIC_LEADERS_SCHEMA = "libreevolve.objective_metric_leaders.v1"
OBJECTIVE_METRIC_ARCHIVES_SCHEMA = "libreevolve.objective_metric_archives.v1"
OBJECTIVE_HISTORY_POLICY = "diagnostic_declared_normalized_metric_history"
_METRIC_NAME_RE = re.compile(
    r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*){0,7}"
)
_PROGRAM_ID_RE = re.compile(r"[A-Za-z0-9_.:-]{1,128}")
_FRONTIER_REQUIRED_LIMITATIONS = {
    "diagnostic_frontier_not_archive_selection_policy",
    "requires_complete_declared_normalized_metric_vectors",
    "plugin_metrics_not_declared_in_objective_schema_are_excluded",
}
_LEADERS_REQUIRED_LIMITATIONS = {
    "diagnostic_metric_leaders_not_archive_selection_policy",
    "requires_declared_normalized_metric_value",
    "plugin_metrics_not_declared_in_objective_schema_are_excluded",
}
_ARCHIVES_REQUIRED_LIMITATIONS = {
    "diagnostic_metric_archives_not_archive_replacement_policy",
    "requires_declared_normalized_metric_value",
    "plugin_metrics_not_declared_in_objective_schema_are_excluded",
}


@dataclass(frozen=True)
class ObjectiveHistoryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ObjectiveHistoryValidation:
    ok: bool
    diagnostic_ready: bool
    primary_archive_policy_ready: bool
    metric_order: list[str]
    frontier_program_count: int
    leader_count: int
    archive_count: int
    issues: list[ObjectiveHistoryIssue]


def validate_objective_history_summary(
    history: object | str | Path,
) -> ObjectiveHistoryValidation:
    """Validate runtime multi-objective diagnostic history snapshots."""
    data, read_issues = _load_history(history)
    if read_issues:
        return ObjectiveHistoryValidation(
            False, False, False, [], 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[ObjectiveHistoryIssue] = []
    frontier = _required_mapping(data, "objective_frontier", issues)
    leaders = _required_mapping(data, "objective_metric_leaders", issues)
    archives = _required_mapping(data, "objective_metric_archives", issues)
    frontier_metrics = (
        _validate_frontier(frontier, issues) if frontier is not None else []
    )
    leader_metrics = _validate_leaders(leaders, issues) if leaders is not None else []
    archive_metrics = (
        _validate_archives(archives, issues) if archives is not None else []
    )
    metric_order = frontier_metrics or leader_metrics or archive_metrics
    for label, order in (
        ("objective_metric_leaders", leader_metrics),
        ("objective_metric_archives", archive_metrics),
    ):
        if order and metric_order and order != metric_order:
            issues.append(
                ObjectiveHistoryIssue(
                    f"{label}_metric_order_mismatch",
                    f"{label}.metric_order must match objective_frontier.metric_order",
                )
            )
    frontier_count = _list_count(frontier, "programs")
    leader_count = _list_count(leaders, "leaders")
    archive_count = _list_count(archives, "archives")
    return ObjectiveHistoryValidation(
        ok=not issues,
        diagnostic_ready=not issues,
        primary_archive_policy_ready=False,
        metric_order=list(metric_order),
        frontier_program_count=frontier_count,
        leader_count=leader_count,
        archive_count=archive_count,
        issues=issues,
    )


def _load_history(
    history: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ObjectiveHistoryIssue]]:
    if isinstance(history, dict):
        if all(
            key in history
            for key in (
                "objective_frontier",
                "objective_metric_leaders",
                "objective_metric_archives",
            )
        ):
            return dict(history), []
        runtime = history.get("runtime") if isinstance(history.get("runtime"), dict) else None
        runtime_history = (
            runtime.get("history")
            if isinstance(runtime, dict) and isinstance(runtime.get("history"), dict)
            else None
        )
        if runtime_history is not None:
            return dict(runtime_history), []
    if isinstance(history, (str, Path)):
        path = Path(history)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [
                ObjectiveHistoryIssue(
                    "read_error",
                    f"failed to read objective history summary: {exc}",
                )
            ]
        except json.JSONDecodeError as exc:
            return None, [
                ObjectiveHistoryIssue(
                    "invalid_json",
                    f"invalid objective history summary JSON: {exc.msg}",
                )
            ]
        return _load_history(loaded)
    return None, [
        ObjectiveHistoryIssue(
            "invalid_shape",
            "objective history summary must be a history object or manifest object",
        )
    ]


def _required_mapping(
    data: dict[str, Any],
    field: str,
    issues: list[ObjectiveHistoryIssue],
) -> dict[str, Any] | None:
    value = data.get(field)
    if not isinstance(value, dict):
        issues.append(
            ObjectiveHistoryIssue(
                f"invalid_{field}",
                f"{field} must be an object",
            )
        )
        return None
    return value


def _validate_frontier(
    frontier: dict[str, Any],
    issues: list[ObjectiveHistoryIssue],
) -> list[str]:
    _expect(
        frontier,
        "schema",
        OBJECTIVE_FRONTIER_SCHEMA,
        "objective_frontier",
        issues,
    )
    _expect(
        frontier,
        "policy",
        "pareto_frontier_over_complete_declared_normalized_metrics",
        "objective_frontier",
        issues,
    )
    metric_order = _validate_metric_order(
        frontier.get("metric_order"),
        "objective_frontier.metric_order",
        issues,
    )
    _require_limitations(
        frontier.get("limitations"),
        _FRONTIER_REQUIRED_LIMITATIONS,
        "objective_frontier",
        issues,
    )
    for field in (
        "program_count_considered",
        "frontier_size",
        "retained_frontier_size",
        "retention_limit",
    ):
        _non_negative_int(frontier.get(field), f"objective_frontier.{field}", issues)
    programs = _validate_frontier_programs(
        frontier.get("programs"), metric_order, issues
    )
    if isinstance(frontier.get("retained_frontier_size"), int) and (
        frontier["retained_frontier_size"] != len(programs)
    ):
        issues.append(
            ObjectiveHistoryIssue(
                "objective_frontier_retained_count_mismatch",
                "retained_frontier_size must equal retained program count",
            )
        )
    if isinstance(frontier.get("frontier_size"), int) and (
        frontier["frontier_size"] < len(programs)
    ):
        issues.append(
            ObjectiveHistoryIssue(
                "objective_frontier_size_mismatch",
                "frontier_size cannot be smaller than retained program count",
            )
        )
    if isinstance(frontier.get("retention_limit"), int) and (
        len(programs) > frontier["retention_limit"]
    ):
        issues.append(
            ObjectiveHistoryIssue(
                "objective_frontier_retention_limit_exceeded",
                "retained objective frontier exceeds retention_limit",
            )
        )
    _validate_non_dominated_frontier(programs, metric_order, issues)
    return metric_order


def _validate_leaders(
    leaders: dict[str, Any],
    issues: list[ObjectiveHistoryIssue],
) -> list[str]:
    _expect(
        leaders,
        "schema",
        OBJECTIVE_METRIC_LEADERS_SCHEMA,
        "objective_metric_leaders",
        issues,
    )
    _expect(
        leaders,
        "policy",
        "best_program_per_declared_normalized_metric",
        "objective_metric_leaders",
        issues,
    )
    metric_order = _validate_metric_order(
        leaders.get("metric_order"),
        "objective_metric_leaders.metric_order",
        issues,
    )
    _require_limitations(
        leaders.get("limitations"),
        _LEADERS_REQUIRED_LIMITATIONS,
        "objective_metric_leaders",
        issues,
    )
    _non_negative_int(leaders.get("leader_count"), "objective_metric_leaders.leader_count", issues)
    records = _validate_metric_records(
        leaders.get("leaders"),
        metric_order,
        "objective_metric_leaders.leaders",
        issues,
    )
    if isinstance(leaders.get("leader_count"), int) and leaders["leader_count"] != len(records):
        issues.append(
            ObjectiveHistoryIssue(
                "objective_metric_leaders_count_mismatch",
                "leader_count must equal leader record count",
            )
        )
    seen_metrics: set[str] = set()
    for record in records:
        metric = record["metric"]
        if metric in seen_metrics:
            issues.append(
                ObjectiveHistoryIssue(
                    "objective_metric_leaders_duplicate_metric",
                    "leaders must contain at most one record per metric",
                )
            )
        seen_metrics.add(metric)
    return metric_order


def _validate_archives(
    archives: dict[str, Any],
    issues: list[ObjectiveHistoryIssue],
) -> list[str]:
    _expect(
        archives,
        "schema",
        OBJECTIVE_METRIC_ARCHIVES_SCHEMA,
        "objective_metric_archives",
        issues,
    )
    _expect(
        archives,
        "policy",
        "top_programs_per_declared_normalized_metric",
        "objective_metric_archives",
        issues,
    )
    metric_order = _validate_metric_order(
        archives.get("metric_order"),
        "objective_metric_archives.metric_order",
        issues,
    )
    _require_limitations(
        archives.get("limitations"),
        _ARCHIVES_REQUIRED_LIMITATIONS,
        "objective_metric_archives",
        issues,
    )
    _non_negative_int(
        archives.get("retention_limit"),
        "objective_metric_archives.retention_limit",
        issues,
    )
    _non_negative_int(
        archives.get("archive_count"),
        "objective_metric_archives.archive_count",
        issues,
    )
    archive_records = archives.get("archives")
    if not isinstance(archive_records, list):
        issues.append(
            ObjectiveHistoryIssue(
                "invalid_objective_metric_archives_archives",
                "objective_metric_archives.archives must be a list",
            )
        )
        return metric_order
    if isinstance(archives.get("archive_count"), int) and archives["archive_count"] != len(archive_records):
        issues.append(
            ObjectiveHistoryIssue(
                "objective_metric_archives_count_mismatch",
                "archive_count must equal archive record count",
            )
        )
    seen_metrics: set[str] = set()
    for index, archive in enumerate(archive_records):
        if not isinstance(archive, dict):
            issues.append(
                ObjectiveHistoryIssue(
                    "invalid_objective_metric_archive",
                    "objective metric archive records must be objects",
                )
            )
            continue
        scope = f"objective_metric_archives.archives[{index}]"
        metric = archive.get("metric")
        if not _valid_metric_name(metric) or metric not in metric_order:
            issues.append(
                ObjectiveHistoryIssue(
                    "invalid_objective_metric_archive_metric",
                    f"{scope}.metric must be in metric_order",
                )
            )
        elif metric in seen_metrics:
            issues.append(
                ObjectiveHistoryIssue(
                    "duplicate_objective_metric_archive_metric",
                    "archives must contain at most one record per metric",
                )
            )
        else:
            seen_metrics.add(metric)
        for field in (
            "program_count_considered",
            "retained_count",
            "retention_limit",
        ):
            _non_negative_int(archive.get(field), f"{scope}.{field}", issues)
        records = _validate_metric_records(
            archive.get("programs"),
            metric_order,
            f"{scope}.programs",
            issues,
        )
        if isinstance(archive.get("retained_count"), int) and archive["retained_count"] != len(records):
            issues.append(
                ObjectiveHistoryIssue(
                    "objective_metric_archive_retained_count_mismatch",
                    f"{scope}.retained_count must equal program count",
                )
            )
        if isinstance(archive.get("program_count_considered"), int) and archive[
            "program_count_considered"
        ] < len(records):
            issues.append(
                ObjectiveHistoryIssue(
                    "objective_metric_archive_considered_count_mismatch",
                    f"{scope}.program_count_considered cannot be smaller than retained programs",
                )
            )
        retention_limit = archive.get("retention_limit")
        if isinstance(retention_limit, int) and len(records) > retention_limit:
            issues.append(
                ObjectiveHistoryIssue(
                    "objective_metric_archive_retention_limit_exceeded",
                    f"{scope}.programs exceeds retention_limit",
                )
            )
    if seen_metrics and seen_metrics != set(metric_order):
        issues.append(
            ObjectiveHistoryIssue(
                "objective_metric_archives_metric_coverage_mismatch",
                "archives must contain exactly one archive per metric_order entry",
            )
        )
    return metric_order


def _validate_frontier_programs(
    value: object,
    metric_order: list[str],
    issues: list[ObjectiveHistoryIssue],
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        issues.append(
            ObjectiveHistoryIssue(
                "invalid_objective_frontier_programs",
                "objective_frontier.programs must be a list",
            )
        )
        return []
    records: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            issues.append(
                ObjectiveHistoryIssue(
                    "invalid_objective_frontier_program",
                    "objective frontier program records must be objects",
                )
            )
            continue
        _validate_program_common(
            item,
            metric_order,
            f"objective_frontier.programs[{index}]",
            issues,
            require_complete_vector=True,
        )
        records.append(item)
    return records


def _validate_metric_records(
    value: object,
    metric_order: list[str],
    scope: str,
    issues: list[ObjectiveHistoryIssue],
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        issues.append(
            ObjectiveHistoryIssue(
                f"invalid_{_code_scope(scope)}",
                f"{scope} must be a list",
            )
        )
        return []
    records: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            issues.append(
                ObjectiveHistoryIssue(
                    f"invalid_{_code_scope(scope)}_record",
                    f"{scope} records must be objects",
                )
            )
            continue
        record_scope = f"{scope}[{index}]"
        metric = item.get("metric")
        if not _valid_metric_name(metric) or metric not in metric_order:
            issues.append(
                ObjectiveHistoryIssue(
                    f"invalid_{_code_scope(record_scope)}_metric",
                    f"{record_scope}.metric must be in metric_order",
                )
            )
        metric_value = item.get("normalized_metric")
        if not _normalized_number(metric_value):
            issues.append(
                ObjectiveHistoryIssue(
                    f"invalid_{_code_scope(record_scope)}_normalized_metric",
                    f"{record_scope}.normalized_metric must be finite in [0, 1]",
                )
            )
        elif isinstance(metric, str):
            normalized_metrics = item.get("normalized_metrics")
            if isinstance(normalized_metrics, dict) and metric in normalized_metrics:
                metric_in_vector = normalized_metrics[metric]
                if _normalized_number(metric_in_vector) and float(metric_in_vector) != float(metric_value):
                    issues.append(
                        ObjectiveHistoryIssue(
                            f"{_code_scope(record_scope)}_metric_value_mismatch",
                            f"{record_scope}.normalized_metric must match normalized_metrics[metric]",
                        )
                    )
        _validate_program_common(
            item,
            metric_order,
            record_scope,
            issues,
            require_complete_vector=False,
        )
        records.append(item)
    return records


def _validate_program_common(
    record: dict[str, Any],
    metric_order: list[str],
    scope: str,
    issues: list[ObjectiveHistoryIssue],
    *,
    require_complete_vector: bool,
) -> None:
    program_id = record.get("program_id")
    if not isinstance(program_id, str) or _PROGRAM_ID_RE.fullmatch(program_id) is None:
        issues.append(
            ObjectiveHistoryIssue(
                f"invalid_{_code_scope(scope)}_program_id",
                f"{scope}.program_id must be a manifest-safe id",
            )
        )
    generation = record.get("generation")
    if isinstance(generation, bool) or not isinstance(generation, int) or generation < 0:
        issues.append(
            ObjectiveHistoryIssue(
                f"invalid_{_code_scope(scope)}_generation",
                f"{scope}.generation must be a non-negative integer",
            )
        )
    selection_score = record.get("selection_score")
    if selection_score is not None and not _normalized_number(selection_score):
        issues.append(
            ObjectiveHistoryIssue(
                f"invalid_{_code_scope(scope)}_selection_score",
                f"{scope}.selection_score must be null or finite in [0, 1]",
            )
        )
    metrics = record.get("normalized_metrics")
    if not isinstance(metrics, dict):
        issues.append(
            ObjectiveHistoryIssue(
                f"invalid_{_code_scope(scope)}_normalized_metrics",
                f"{scope}.normalized_metrics must be an object",
            )
        )
        return
    expected = set(metric_order)
    actual = set(metrics)
    if require_complete_vector and actual != expected:
        issues.append(
            ObjectiveHistoryIssue(
                f"{_code_scope(scope)}_metric_coverage_mismatch",
                f"{scope}.normalized_metrics must contain all declared metrics",
            )
        )
    elif actual - expected:
        issues.append(
            ObjectiveHistoryIssue(
                f"{_code_scope(scope)}_unknown_metric",
                f"{scope}.normalized_metrics contains metrics outside metric_order",
            )
        )
    for metric, value in metrics.items():
        if not _valid_metric_name(metric):
            issues.append(
                ObjectiveHistoryIssue(
                    f"invalid_{_code_scope(scope)}_metric_name",
                    f"{scope}.normalized_metrics keys must be safe metric names",
                )
            )
        if not _normalized_number(value):
            issues.append(
                ObjectiveHistoryIssue(
                    f"invalid_{_code_scope(scope)}_metric_value",
                    f"{scope}.normalized_metrics values must be finite in [0, 1]",
                )
            )


def _validate_non_dominated_frontier(
    programs: list[dict[str, Any]],
    metric_order: list[str],
    issues: list[ObjectiveHistoryIssue],
) -> None:
    if not metric_order:
        return
    for index, candidate in enumerate(programs):
        metrics = candidate.get("normalized_metrics")
        if not isinstance(metrics, dict):
            continue
        for other_index, other in enumerate(programs):
            if index == other_index:
                continue
            other_metrics = other.get("normalized_metrics")
            if not isinstance(other_metrics, dict):
                continue
            if _dominates(other_metrics, metrics, metric_order):
                issues.append(
                    ObjectiveHistoryIssue(
                        "objective_frontier_contains_dominated_program",
                        "objective frontier retained programs must be non-dominated",
                    )
                )
                return


def _dominates(left: dict[str, Any], right: dict[str, Any], metric_order: list[str]) -> bool:
    if not all(_normalized_number(left.get(name)) and _normalized_number(right.get(name)) for name in metric_order):
        return False
    return all(float(left[name]) >= float(right[name]) for name in metric_order) and any(
        float(left[name]) > float(right[name]) for name in metric_order
    )


def _validate_metric_order(
    value: object,
    scope: str,
    issues: list[ObjectiveHistoryIssue],
) -> list[str]:
    if not isinstance(value, list):
        issues.append(ObjectiveHistoryIssue(f"invalid_{_code_scope(scope)}", f"{scope} must be a list"))
        return []
    order: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not _valid_metric_name(item):
            issues.append(
                ObjectiveHistoryIssue(
                    f"invalid_{_code_scope(scope)}_entry",
                    f"{scope} entries must be manifest-safe metric names",
                )
            )
            continue
        assert isinstance(item, str)
        if item in seen:
            issues.append(
                ObjectiveHistoryIssue(
                    f"duplicate_{_code_scope(scope)}_entry",
                    f"{scope} entries must be unique",
                )
            )
        seen.add(item)
        order.append(item)
    return order


def _require_limitations(
    value: object,
    required: set[str],
    scope: str,
    issues: list[ObjectiveHistoryIssue],
) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        issues.append(
            ObjectiveHistoryIssue(
                f"invalid_{scope}_limitations",
                f"{scope}.limitations must be a non-empty string list",
            )
        )
        return
    if not required <= set(value):
        issues.append(
            ObjectiveHistoryIssue(
                f"missing_{scope}_limitations",
                f"{scope}.limitations must state diagnostic archive limits",
            )
        )


def _expect(
    data: dict[str, Any],
    field: str,
    expected: object,
    scope: str,
    issues: list[ObjectiveHistoryIssue],
) -> None:
    if data.get(field) != expected:
        issues.append(
            ObjectiveHistoryIssue(
                f"invalid_{scope}_{field}",
                f"{scope}.{field} must be {expected!r}",
            )
        )


def _non_negative_int(
    value: object,
    scope: str,
    issues: list[ObjectiveHistoryIssue],
) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        issues.append(
            ObjectiveHistoryIssue(
                f"invalid_{_code_scope(scope)}",
                f"{scope} must be a non-negative integer",
            )
        )


def _normalized_number(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
        and 0.0 <= float(value) <= 1.0
    )


def _valid_metric_name(value: object) -> bool:
    return isinstance(value, str) and _METRIC_NAME_RE.fullmatch(value) is not None


def _list_count(value: dict[str, Any] | None, field: str) -> int:
    if not isinstance(value, dict) or not isinstance(value.get(field), list):
        return 0
    return len(value[field])


def _code_scope(scope: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", scope).strip("_")
