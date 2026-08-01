from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ablation_registry import (
    EXPECTED_VARIANT_IDS,
    EXPECTED_VARIANT_IDS_BY_TARGET_FAMILY,
    FIGURE8_TARGET_FAMILIES,
    REPORT_SCHEMA,
)


ABLATION_RESULT_SCHEMA = REPORT_SCHEMA
ABLATION_ARTIFACT_INVENTORY_SCHEMA = "libreevolve.alphaevolve_ablation_artifact_inventory.v1"
REQUIRED_BUDGET_FRACTIONS = (0.0, 0.25, 0.5, 0.75, 1.0)
BUDGET_UNITS = frozenset({"evaluations", "wall_clock_seconds", "llm_calls", "tokens", "cost_usd"})
ARTIFACT_KINDS = frozenset({"variant_report", "curve_summary", "raw_records", "plot"})
METRIC_DIRECTIONS = frozenset({"higher_is_better"})
_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class AblationResultIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AblationResultValidation:
    ok: bool
    equal_budget_ready: bool
    target_count: int
    record_count: int
    issues: list[AblationResultIssue]


def validate_ablation_result_report(report: object | str | Path) -> AblationResultValidation:
    """Validate executed AlphaEvolve-style equal-budget ablation results."""
    data, read_issues = _load_report(report)
    if read_issues:
        return AblationResultValidation(False, False, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[AblationResultIssue] = []
    if data.get("schema") != ABLATION_RESULT_SCHEMA:
        issues.append(AblationResultIssue("invalid_schema", "unsupported ablation result schema"))
    if data.get("budget_axis") != "fraction_of_equal_compute_budget":
        issues.append(AblationResultIssue("invalid_budget_axis", "budget_axis must be fraction_of_equal_compute_budget"))
    targets = data.get("targets")
    target_families_by_id = _validate_targets(targets, issues)
    records = data.get("records")
    record_count, score_groups = _validate_records(
        records,
        target_families_by_id,
        issues,
    )
    _validate_curve_summaries(
        data.get("curve_summaries"),
        score_groups,
        target_families_by_id,
        issues,
    )
    _validate_artifacts(data.get("artifacts"), issues)
    equal_budget_ready = not issues
    return AblationResultValidation(
        ok=not issues,
        equal_budget_ready=equal_budget_ready,
        target_count=len(target_families_by_id),
        record_count=record_count,
        issues=issues,
    )


def render_ablation_result_summary(report: dict[str, Any]) -> str:
    validation = validate_ablation_result_report(report)
    status = "ok" if validation.ok else "invalid"
    ready = "yes" if validation.equal_budget_ready else "no"
    lines = [
        "AlphaEvolve ablation result report",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| equal_budget_ready | {ready} |",
        f"| target_count | {validation.target_count} |",
        f"| record_count | {validation.record_count} |",
        f"| budget_axis | {report.get('budget_axis', '<unknown>')} |",
        f"| curve_summary_count | {len(report.get('curve_summaries', [])) if isinstance(report.get('curve_summaries'), list) else 0} |",
        f"| artifact_count | {len(report.get('artifacts', [])) if isinstance(report.get('artifacts'), list) else 0} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def ablation_result_artifact_inventory(
    report: object | str | Path,
    artifact_root: str | Path,
) -> dict[str, Any]:
    """Verify ablation report artifact references against concrete files."""
    data, read_issues = _load_report(report)
    root = Path(artifact_root)
    records: list[dict[str, Any]] = []
    issues = [
        {"code": issue.code, "message": issue.message}
        for issue in read_issues
    ]
    if data is not None:
        artifacts = data.get("artifacts")
        if isinstance(artifacts, list):
            for artifact in artifacts:
                records.append(_ablation_artifact_inventory_record(artifact, root))
        else:
            issues.append(
                {
                    "code": "invalid_artifacts",
                    "message": "artifacts must be a non-empty list",
                }
            )
    verified_count = sum(1 for record in records if record["status"] == "verified")
    missing_count = sum(1 for record in records if record["status"] == "missing_file")
    mismatch_count = sum(
        1
        for record in records
        if record["status"] in {"hash_mismatch", "bytes_mismatch"}
    )
    invalid_count = sum(
        1
        for record in records
        if record["status"] in {"invalid_artifact", "unsafe_path", "read_error"}
    )
    if not records and data is not None:
        issues.append(
            {
                "code": "empty_artifact_inventory",
                "message": "no artifact records were available to verify",
            }
        )
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return {
        "schema": ABLATION_ARTIFACT_INVENTORY_SCHEMA,
        "report_schema": data.get("schema") if isinstance(data, dict) else None,
        "budget_axis": data.get("budget_axis") if isinstance(data, dict) else None,
        "artifact_root_policy": "safe_relative_report_paths_under_artifact_root",
        "artifact_root_name": root.name,
        "artifact_count": len(records),
        "verified_count": verified_count,
        "missing_count": missing_count,
        "mismatch_count": mismatch_count,
        "invalid_count": invalid_count,
        "records_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "ok": (
            not issues
            and bool(records)
            and verified_count == len(records)
            and missing_count == 0
            and mismatch_count == 0
            and invalid_count == 0
        ),
        "issues": issues,
        "artifacts": records,
    }


def _load_report(report: object | str | Path) -> tuple[dict[str, Any] | None, list[AblationResultIssue]]:
    if isinstance(report, dict):
        return dict(report), []
    if isinstance(report, (str, Path)):
        path = Path(report)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [AblationResultIssue("read_error", f"failed to read ablation result report: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [AblationResultIssue("invalid_json", f"invalid ablation result JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [AblationResultIssue("invalid_shape", "ablation result report must be a JSON object")]


def _ablation_artifact_inventory_record(artifact: object, root: Path) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        return {
            "kind": "unknown",
            "path": "",
            "status": "invalid_artifact",
            "issues": ["invalid_artifact"],
        }
    kind = artifact.get("kind")
    path = artifact.get("path")
    expected_sha = artifact.get("sha256")
    expected_bytes = artifact.get("bytes")
    record: dict[str, Any] = {
        "kind": kind if isinstance(kind, str) else "unknown",
        "path": path if isinstance(path, str) else "",
        "expected_sha256": expected_sha if isinstance(expected_sha, str) else "",
        "expected_bytes": expected_bytes if isinstance(expected_bytes, int) and not isinstance(expected_bytes, bool) else None,
        "status": "verified",
        "issues": [],
    }
    path_obj = Path(path) if isinstance(path, str) else None
    if (
        path_obj is None
        or not path
        or path_obj.is_absolute()
        or path.startswith(("/", "\\"))
        or ".." in path_obj.parts
    ):
        record["status"] = "unsafe_path"
        record["issues"].append("invalid_artifact_path")
        return record
    try:
        resolved_root = root.resolve()
        resolved_path = (resolved_root / path_obj).resolve(strict=False)
    except OSError:
        record["status"] = "unsafe_path"
        record["issues"].append("invalid_artifact_path")
        return record
    if not resolved_path.is_relative_to(resolved_root):
        record["status"] = "unsafe_path"
        record["issues"].append("artifact_path_outside_root")
        return record
    if not resolved_path.exists():
        record["status"] = "missing_file"
        record["issues"].append("missing_artifact_file")
        return record
    if not resolved_path.is_file():
        record["status"] = "unsafe_path"
        record["issues"].append("artifact_path_not_file")
        return record
    try:
        raw = resolved_path.read_bytes()
    except OSError:
        record["status"] = "read_error"
        record["issues"].append("artifact_read_error")
        return record
    actual_sha = hashlib.sha256(raw).hexdigest()
    actual_bytes = len(raw)
    record["actual_sha256"] = actual_sha
    record["actual_bytes"] = actual_bytes
    if not isinstance(expected_sha, str) or _SHA256_RE.fullmatch(expected_sha) is None:
        record["status"] = "hash_mismatch"
        record["issues"].append("invalid_expected_artifact_hash")
    elif actual_sha != expected_sha:
        record["status"] = "hash_mismatch"
        record["issues"].append("artifact_hash_mismatch")
    if isinstance(expected_bytes, bool) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
        if record["status"] == "verified":
            record["status"] = "bytes_mismatch"
        record["issues"].append("invalid_expected_artifact_bytes")
    elif actual_bytes != expected_bytes:
        if record["status"] == "verified":
            record["status"] = "bytes_mismatch"
        record["issues"].append("artifact_bytes_mismatch")
    return record


def _validate_targets(
    value: object,
    issues: list[AblationResultIssue],
) -> dict[str, str]:
    if not isinstance(value, list) or not value:
        issues.append(AblationResultIssue("invalid_targets", "targets must be a non-empty list"))
        return {}
    seen: set[str] = set()
    families: set[str] = set()
    target_families_by_id: dict[str, str] = {}
    for target in value:
        if not isinstance(target, dict):
            issues.append(AblationResultIssue("invalid_target", "target must be an object"))
            continue
        target_id = target.get("target_id")
        if not isinstance(target_id, str) or _ID_RE.fullmatch(target_id) is None:
            issues.append(AblationResultIssue("invalid_target_id", "target_id must be stable"))
            continue
        if target_id in seen:
            issues.append(AblationResultIssue("duplicate_target", "targets must be unique"))
        seen.add(target_id)
        if not isinstance(target.get("description"), str) or not target["description"].strip():
            issues.append(AblationResultIssue("missing_target_description", "target description is required"))
        family = target.get("target_family")
        if family not in FIGURE8_TARGET_FAMILIES:
            issues.append(AblationResultIssue("invalid_target_family", "target_family must match a Figure 8 target family"))
        elif isinstance(family, str):
            families.add(family)
            target_families_by_id[target_id] = family
        _validate_target_metric(target.get("target_metric"), issues)
    for family in sorted(FIGURE8_TARGET_FAMILIES - families):
        issues.append(AblationResultIssue("missing_figure8_target_family", "reports must cover both Figure 8 target families"))
    return target_families_by_id


def _validate_target_metric(value: object, issues: list[AblationResultIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(AblationResultIssue("invalid_target_metric", "target_metric must be an object"))
        return
    if not isinstance(value.get("name"), str) or not value["name"].strip():
        issues.append(AblationResultIssue("missing_target_metric_name", "target_metric.name is required"))
    if value.get("direction") not in METRIC_DIRECTIONS:
        issues.append(AblationResultIssue("invalid_target_metric_direction", "target metric direction must be higher_is_better"))
    if not isinstance(value.get("normalization"), str) or not value["normalization"].strip():
        issues.append(AblationResultIssue("missing_target_metric_normalization", "target_metric.normalization is required"))


def _validate_records(
    value: object,
    target_families_by_id: dict[str, str],
    issues: list[AblationResultIssue],
) -> tuple[int, dict[tuple[str, str, float], list[float]]]:
    if not isinstance(value, list) or not value:
        issues.append(AblationResultIssue("invalid_records", "records must be a non-empty list"))
        return 0, {}
    seen: set[tuple[str, str, int, float]] = set()
    observed: dict[tuple[str, str], set[tuple[int, float]]] = {}
    seed_sets: dict[tuple[str, str], set[int]] = {}
    seed_budget_specs: dict[tuple[str, str, int], tuple[str, float]] = {}
    target_budget_specs: dict[str, tuple[str, float]] = {}
    score_groups: dict[tuple[str, str, float], list[float]] = {}
    for record in value:
        if not isinstance(record, dict):
            issues.append(AblationResultIssue("invalid_record", "record must be an object"))
            continue
        variant_id = record.get("variant_id")
        target_id = record.get("target_id")
        seed = record.get("seed")
        fraction = _budget_fraction(record.get("budget_fraction"), issues)
        if variant_id not in EXPECTED_VARIANT_IDS:
            issues.append(AblationResultIssue("invalid_variant_id", "record variant_id must match AlphaEvolve ablation registry"))
        if not isinstance(target_id, str) or target_id not in target_families_by_id:
            issues.append(AblationResultIssue("invalid_record_target", "record target_id must be declared in targets"))
        pairing_is_valid = _variant_target_pair_is_valid(
            variant_id,
            target_id,
            target_families_by_id,
        )
        if (
            isinstance(variant_id, str)
            and isinstance(target_id, str)
            and target_id in target_families_by_id
            and not pairing_is_valid
        ):
            issues.append(
                AblationResultIssue(
                    "invalid_figure8_variant_target_pair",
                    "record variant_id is not shown for the target's Figure 8 panel",
                )
            )
        if isinstance(seed, bool) or not isinstance(seed, int):
            issues.append(AblationResultIssue("invalid_seed", "seed must be an integer"))
        score = record.get("score")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(float(score)):
            issues.append(AblationResultIssue("invalid_score", "score must be finite"))
        budget_spec = _validate_consumed_budget(record.get("consumed_budget"), fraction, issues)
        _validate_component_assertions(record.get("component_assertions"), issues)
        if (
            pairing_is_valid
            and isinstance(variant_id, str)
            and isinstance(target_id, str)
            and isinstance(seed, int)
            and fraction is not None
        ):
            key = (variant_id, target_id, seed, fraction)
            if key in seen:
                issues.append(AblationResultIssue("duplicate_record", "duplicate variant/target/seed/fraction record"))
            seen.add(key)
            observed.setdefault((variant_id, target_id), set()).add((seed, fraction))
            seed_sets.setdefault((variant_id, target_id), set()).add(seed)
            if isinstance(score, (int, float)) and not isinstance(score, bool) and math.isfinite(float(score)):
                score_groups.setdefault((variant_id, target_id, fraction), []).append(float(score))
            if budget_spec is not None:
                seed_key = (variant_id, target_id, seed)
                if seed_key in seed_budget_specs and seed_budget_specs[seed_key] != budget_spec:
                    issues.append(AblationResultIssue("inconsistent_seed_budget", "variant/target/seed records must use one budget unit and limit"))
                seed_budget_specs.setdefault(seed_key, budget_spec)
                if target_id in target_budget_specs and target_budget_specs[target_id] != budget_spec:
                    issues.append(AblationResultIssue("inconsistent_target_budget", "all paper-applicable variants and seeds for a target must use the same budget unit and limit"))
                target_budget_specs.setdefault(target_id, budget_spec)
    _validate_coverage(
        observed,
        seed_sets,
        target_families_by_id,
        issues,
    )
    return len(value), score_groups


def _budget_fraction(value: object, issues: list[AblationResultIssue]) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        issues.append(AblationResultIssue("invalid_budget_fraction", "budget_fraction must be numeric"))
        return None
    numeric = float(value)
    if not math.isfinite(numeric) or not any(math.isclose(numeric, required, rel_tol=0.0, abs_tol=1e-12) for required in REQUIRED_BUDGET_FRACTIONS):
        issues.append(AblationResultIssue("invalid_budget_fraction", "budget_fraction must match required equal-budget fractions"))
        return None
    return numeric


def _validate_consumed_budget(
    value: object,
    fraction: float | None,
    issues: list[AblationResultIssue],
) -> tuple[str, float] | None:
    if not isinstance(value, dict):
        issues.append(AblationResultIssue("invalid_consumed_budget", "consumed_budget must be an object"))
        return None
    if value.get("unit") not in BUDGET_UNITS:
        issues.append(AblationResultIssue("invalid_budget_unit", "unsupported budget unit"))
    consumed = value.get("consumed")
    limit = value.get("limit")
    if isinstance(consumed, bool) or not isinstance(consumed, (int, float)) or not math.isfinite(float(consumed)) or float(consumed) < 0:
        issues.append(AblationResultIssue("invalid_budget_consumed", "consumed budget must be finite and non-negative"))
        return None
    if isinstance(limit, bool) or not isinstance(limit, (int, float)) or not math.isfinite(float(limit)) or float(limit) <= 0:
        issues.append(AblationResultIssue("invalid_budget_limit", "budget limit must be finite and positive"))
        return None
    if float(consumed) > float(limit):
        issues.append(AblationResultIssue("budget_exceeds_limit", "consumed budget must be <= limit"))
    if fraction is not None and not math.isclose(float(consumed) / float(limit), fraction, rel_tol=0.0, abs_tol=1e-9):
        issues.append(AblationResultIssue("budget_fraction_mismatch", "consumed / limit must equal budget_fraction"))
    unit = value.get("unit")
    if unit in BUDGET_UNITS:
        return unit, float(limit)
    return None


def _validate_component_assertions(value: object, issues: list[AblationResultIssue]) -> None:
    if not isinstance(value, list) or not value:
        issues.append(AblationResultIssue("invalid_component_assertions", "component_assertions must be a non-empty list"))
        return
    for assertion in value:
        if not isinstance(assertion, dict):
            issues.append(AblationResultIssue("invalid_component_assertion", "component assertion must be an object"))
            continue
        if not isinstance(assertion.get("field"), str) or not assertion["field"]:
            issues.append(AblationResultIssue("invalid_component_assertion_field", "component assertion field is required"))
        if assertion.get("passed") is not True:
            issues.append(AblationResultIssue("component_assertion_not_passed", "component assertions must be passed"))


def _validate_coverage(
    observed: dict[tuple[str, str], set[tuple[int, float]]],
    seed_sets: dict[tuple[str, str], set[int]],
    target_families_by_id: dict[str, str],
    issues: list[AblationResultIssue],
) -> None:
    required_fractions = set(REQUIRED_BUDGET_FRACTIONS)
    for target_id, target_family in target_families_by_id.items():
        for variant_id in EXPECTED_VARIANT_IDS_BY_TARGET_FAMILY[target_family]:
            seeds = seed_sets.get((variant_id, target_id), set())
            if len(seeds) != 3:
                issues.append(AblationResultIssue("invalid_seed_coverage", "each variant/target must report exactly three seeds"))
                continue
            for seed in seeds:
                fractions = {fraction for observed_seed, fraction in observed.get((variant_id, target_id), set()) if observed_seed == seed}
                if fractions != required_fractions:
                    issues.append(AblationResultIssue("invalid_budget_fraction_coverage", "each variant/target/seed must report all required budget fractions"))
                    break


def _validate_curve_summaries(
    value: object,
    score_groups: dict[tuple[str, str, float], list[float]],
    target_families_by_id: dict[str, str],
    issues: list[AblationResultIssue],
) -> None:
    if not isinstance(value, list) or not value:
        issues.append(AblationResultIssue("invalid_curve_summaries", "curve_summaries must be a non-empty list"))
        return
    seen: set[tuple[str, str, float]] = set()
    for summary in value:
        if not isinstance(summary, dict):
            issues.append(AblationResultIssue("invalid_curve_summary", "curve summary must be an object"))
            continue
        variant_id = summary.get("variant_id")
        target_id = summary.get("target_id")
        fraction = _budget_fraction(summary.get("budget_fraction"), issues)
        if variant_id not in EXPECTED_VARIANT_IDS:
            issues.append(AblationResultIssue("invalid_curve_variant", "curve summary variant_id must match AlphaEvolve ablation registry"))
        if not isinstance(target_id, str) or target_id not in target_families_by_id:
            issues.append(AblationResultIssue("invalid_curve_target", "curve summary target_id must be declared in targets"))
        pairing_is_valid = _variant_target_pair_is_valid(
            variant_id,
            target_id,
            target_families_by_id,
        )
        if (
            isinstance(variant_id, str)
            and isinstance(target_id, str)
            and target_id in target_families_by_id
            and not pairing_is_valid
        ):
            issues.append(
                AblationResultIssue(
                    "invalid_figure8_curve_variant_target_pair",
                    "curve summary variant_id is not shown for the target's Figure 8 panel",
                )
            )
        if fraction is None or not isinstance(variant_id, str) or not isinstance(target_id, str):
            continue
        if not pairing_is_valid:
            continue
        key = (variant_id, target_id, fraction)
        if key in seen:
            issues.append(AblationResultIssue("duplicate_curve_summary", "duplicate curve summary"))
        seen.add(key)
        scores = score_groups.get(key, [])
        if len(scores) != 3:
            issues.append(AblationResultIssue("invalid_curve_seed_count", "curve summary must be backed by three seed records"))
            continue
        mean = summary.get("mean_score")
        std = summary.get("std_score")
        seed_count = summary.get("seed_count")
        if isinstance(seed_count, bool) or seed_count != 3:
            issues.append(AblationResultIssue("invalid_curve_seed_count", "curve summary seed_count must be three"))
        if isinstance(mean, bool) or not isinstance(mean, (int, float)) or not math.isfinite(float(mean)):
            issues.append(AblationResultIssue("invalid_curve_mean", "curve summary mean_score must be finite"))
        elif not math.isclose(float(mean), sum(scores) / len(scores), rel_tol=0.0, abs_tol=1e-9):
            issues.append(AblationResultIssue("curve_mean_mismatch", "curve summary mean_score must match seed records"))
        expected_std = math.sqrt(sum((score - (sum(scores) / len(scores))) ** 2 for score in scores) / len(scores))
        if isinstance(std, bool) or not isinstance(std, (int, float)) or not math.isfinite(float(std)) or float(std) < 0:
            issues.append(AblationResultIssue("invalid_curve_std", "curve summary std_score must be finite and non-negative"))
        elif not math.isclose(float(std), expected_std, rel_tol=0.0, abs_tol=1e-9):
            issues.append(AblationResultIssue("curve_std_mismatch", "curve summary std_score must match seed records"))
    for target_id, target_family in target_families_by_id.items():
        for variant_id in EXPECTED_VARIANT_IDS_BY_TARGET_FAMILY[target_family]:
            for fraction in REQUIRED_BUDGET_FRACTIONS:
                if (variant_id, target_id, fraction) not in seen:
                    issues.append(AblationResultIssue("missing_curve_summary", "each variant/target/fraction needs a curve summary"))


def _variant_target_pair_is_valid(
    variant_id: object,
    target_id: object,
    target_families_by_id: dict[str, str],
) -> bool:
    if not isinstance(variant_id, str) or variant_id not in EXPECTED_VARIANT_IDS:
        return False
    if not isinstance(target_id, str):
        return False
    target_family = target_families_by_id.get(target_id)
    if target_family is None:
        return False
    return variant_id in EXPECTED_VARIANT_IDS_BY_TARGET_FAMILY[target_family]


def _validate_artifacts(value: object, issues: list[AblationResultIssue]) -> None:
    if not isinstance(value, list) or not value:
        issues.append(AblationResultIssue("invalid_artifacts", "artifacts must be a non-empty list"))
        return
    for artifact in value:
        if not isinstance(artifact, dict):
            issues.append(AblationResultIssue("invalid_artifact", "artifact must be an object"))
            continue
        if artifact.get("kind") not in ARTIFACT_KINDS:
            issues.append(AblationResultIssue("invalid_artifact_kind", "unsupported artifact kind"))
        _validate_file_record(artifact, "artifact", issues)


def _validate_file_record(record: dict[str, Any], prefix: str, issues: list[AblationResultIssue]) -> None:
    path = record.get("path")
    path_obj = Path(path) if isinstance(path, str) else None
    if (
        path_obj is None
        or not path
        or path_obj.is_absolute()
        or path.startswith(("/", "\\"))
        or ".." in path_obj.parts
    ):
        issues.append(AblationResultIssue(f"invalid_{prefix}_path", f"{prefix} path must be safe and relative"))
    sha = record.get("sha256")
    if not isinstance(sha, str) or _SHA256_RE.fullmatch(sha) is None:
        issues.append(AblationResultIssue(f"invalid_{prefix}_hash", f"{prefix} sha256 must be a lowercase SHA-256 hex digest"))
    byte_count = record.get("bytes")
    if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count <= 0:
        issues.append(AblationResultIssue(f"invalid_{prefix}_bytes", f"{prefix} bytes must be a positive integer"))
