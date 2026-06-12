from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SYSTEMS_RESULT_SCHEMA = "libreevolve.systems_result_report.v1"
SYSTEMS_ARTIFACT_INVENTORY_SCHEMA = "libreevolve.systems_result_artifact_inventory.v1"
SYSTEMS_EVIDENCE_BUNDLE_SCHEMA = "libreevolve.systems_evidence_bundle.v1"
BENCHMARK_DOMAINS = frozenset({"compiler", "hardware", "kernel", "scheduling", "systems"})
GATE_NAMES = frozenset({"optimization", "heldout", "reference_correctness"})
GATE_STATUSES = frozenset({"passed", "failed", "not_checked", "not_applicable"})
ARTIFACT_KINDS = frozenset({"case_set", "metrics", "reference_report", "heldout_report", "summary"})
GATE_ARTIFACT_KINDS = {
    "optimization": "metrics",
    "heldout": "heldout_report",
    "reference_correctness": "reference_report",
}
DOMAIN_READY_GATE_REQUIREMENTS = {
    "scheduling": {"heldout": "passed"},
    "kernel": {"heldout": "passed"},
    "compiler": {"reference_correctness": "passed"},
    "hardware": {"reference_correctness": "passed"},
    "systems": {"heldout": "passed", "reference_correctness": "passed"},
}
APPLICATION_PROVENANCE_ROLES = frozenset(
    {
        "application_colead",
        "domain_advisor",
        "domain_reviewer",
        "validation_infrastructure_owner",
        "workload_data_steward",
        "production_approver",
    }
)
APPLICATION_APPROVAL_STATES = frozenset(
    {"pending", "reviewed", "approved", "deployed", "not_applicable"}
)
COMPILER_IR_ABSTRACTION_LEVELS = frozenset(
    {"kernel_ir", "preprocessing_ir", "postprocessing_ir"}
)
CLAIM_CALIBRATION_KINDS = frozenset(
    {
        "scheduling_resource_recovery",
        "kernel_speedup",
        "training_time_reduction",
        "hardware_power_area",
        "compiler_kernel_speedup",
        "compiler_prepost_speedup",
        "engineering_effort_turnaround",
    }
)
_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class SystemsResultIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SystemsResultValidation:
    ok: bool
    alphaevolve_ready: bool
    benchmark_id: str | None
    domain: str | None
    issues: list[SystemsResultIssue]


@dataclass(frozen=True)
class SystemsEvidenceBundleValidation:
    ok: bool
    benchmark_id: str | None
    report_ok: bool
    inventory_ok: bool
    alphaevolve_ready: bool
    issues: list[SystemsResultIssue]


def validate_systems_result_report(report: object | str | Path) -> SystemsResultValidation:
    """Validate held-out and reference-correctness gates for systems benchmarks."""
    data, read_issues = _load_report(report)
    if read_issues:
        return SystemsResultValidation(False, False, None, None, read_issues)
    assert isinstance(data, dict)
    issues: list[SystemsResultIssue] = []
    if data.get("schema") != SYSTEMS_RESULT_SCHEMA:
        issues.append(SystemsResultIssue("invalid_schema", "unsupported systems result schema"))
    benchmark_id = _id_field(data, "benchmark_id", issues)
    _id_field(data, "candidate_id", issues)
    domain = data.get("domain")
    if domain not in BENCHMARK_DOMAINS:
        issues.append(SystemsResultIssue("invalid_domain", "unsupported systems benchmark domain"))
        domain = None
    gate_statuses = _validate_gates(data.get("gates"), issues)
    artifact_kinds = _validate_artifacts(data.get("artifacts"), issues)
    scheduling_formulation_ready = _validate_scheduling_formulation(
        data.get("scheduling_formulation"),
        data,
        domain,
        data.get("alphaevolve_ready") is True,
        issues,
    )
    scheduling_safety_ready = _validate_scheduling_safety(
        data.get("scheduling_safety"),
        data,
        domain,
        data.get("alphaevolve_ready") is True,
        issues,
    )
    scheduling_deployment_ready = _validate_scheduling_deployment_readiness(
        data.get("scheduling_deployment_readiness"),
        data,
        domain,
        data.get("alphaevolve_ready") is True,
        issues,
    )
    claim_calibration_ready = _validate_claim_calibration(
        data.get("claim_calibration"),
        data,
        domain,
        data.get("alphaevolve_ready") is True,
        issues,
    )
    application_ready = _validate_application_provenance(
        data.get("application_provenance"),
        data,
        domain,
        data.get("alphaevolve_ready") is True,
        issues,
    )
    compiler_ir_ready = _validate_compiler_ir_provenance(
        data.get("compiler_ir_provenance"),
        data,
        domain,
        data.get("alphaevolve_ready") is True,
        issues,
    )
    certification_ready = _validate_certification_reference(data.get("certification"), issues)
    if data.get("alphaevolve_ready") is True and not _gates_are_alphaevolve_ready(gate_statuses):
        issues.append(
            SystemsResultIssue(
                "invalid_alphaevolve_ready",
                "alphaevolve_ready requires passed optimization plus heldout/reference gates passed or documented not_applicable",
            )
        )
    if data.get("alphaevolve_ready") is True:
        _validate_domain_ready_gate_requirements(domain, gate_statuses, issues)
        _validate_ready_gate_artifacts(gate_statuses, artifact_kinds, issues)
        if not claim_calibration_ready:
            issues.append(
                SystemsResultIssue(
                    "invalid_ready_claim_calibration",
                    "alphaevolve_ready systems reports require claim-calibrated metric records",
                )
            )
        if domain == "scheduling" and not scheduling_safety_ready:
            issues.append(
                SystemsResultIssue(
                    "invalid_ready_scheduling_safety",
                    "alphaevolve_ready scheduling reports require ranking-only safety provenance",
                )
            )
        if domain == "scheduling" and not scheduling_formulation_ready:
            issues.append(
                SystemsResultIssue(
                    "invalid_ready_scheduling_formulation",
                    "alphaevolve_ready scheduling reports require vector-bin-packing formulation provenance",
                )
            )
        if domain == "scheduling" and not scheduling_deployment_ready:
            issues.append(
                SystemsResultIssue(
                    "invalid_ready_scheduling_deployment_readiness",
                    "alphaevolve_ready scheduling reports require mission-critical deployment-readiness provenance",
                )
            )
        if not application_ready:
            issues.append(
                SystemsResultIssue(
                    "invalid_ready_application_provenance",
                    "alphaevolve_ready systems reports require application owner/reviewer provenance",
                )
            )
        if domain == "compiler" and not compiler_ir_ready:
            issues.append(
                SystemsResultIssue(
                    "invalid_ready_compiler_ir_provenance",
                    "alphaevolve_ready compiler reports require compiler-IR provenance",
                )
            )
        if certification_ready is False:
            issues.append(
                SystemsResultIssue(
                    "invalid_ready_certification",
                    "alphaevolve_ready reports cannot reference a certification that is not paper_claim_ready",
                )
            )
    alphaevolve_ready = not issues and data.get("alphaevolve_ready") is True
    return SystemsResultValidation(
        ok=not issues,
        alphaevolve_ready=alphaevolve_ready,
        benchmark_id=benchmark_id,
        domain=domain,
        issues=issues,
    )


def validate_systems_evidence_bundle(
    report: object | str | Path,
    inventory: object,
) -> SystemsEvidenceBundleValidation:
    """Validate a systems result report together with its artifact inventory."""
    data, read_issues = _load_report(report)
    if read_issues:
        return SystemsEvidenceBundleValidation(
            ok=False,
            benchmark_id=None,
            report_ok=False,
            inventory_ok=False,
            alphaevolve_ready=False,
            issues=read_issues,
        )
    assert isinstance(data, dict)
    issues: list[SystemsResultIssue] = []
    report_validation = validate_systems_result_report(data)
    issues.extend(report_validation.issues)
    inventory_ok = _validate_systems_inventory(
        inventory,
        data,
        report_validation.benchmark_id,
        issues,
    )
    return SystemsEvidenceBundleValidation(
        ok=not issues,
        benchmark_id=report_validation.benchmark_id,
        report_ok=report_validation.ok,
        inventory_ok=inventory_ok,
        alphaevolve_ready=report_validation.alphaevolve_ready and inventory_ok and not issues,
        issues=issues,
    )


def validate_systems_evidence_bundle_record(
    bundle: object | str | Path,
) -> SystemsEvidenceBundleValidation:
    """Validate a portable systems evidence bundle record."""
    data, read_issues = _load_bundle(bundle)
    if read_issues:
        return SystemsEvidenceBundleValidation(
            ok=False,
            benchmark_id=None,
            report_ok=False,
            inventory_ok=False,
            alphaevolve_ready=False,
            issues=read_issues,
        )
    assert isinstance(data, dict)
    issues: list[SystemsResultIssue] = []
    if data.get("schema") != SYSTEMS_EVIDENCE_BUNDLE_SCHEMA:
        issues.append(
            SystemsResultIssue(
                "invalid_bundle_schema",
                "unsupported systems evidence bundle schema",
            )
        )
    report = data.get("report")
    inventory = data.get("inventory")
    if not isinstance(report, dict):
        issues.append(
            SystemsResultIssue("invalid_bundle_report", "bundle report must be an object")
        )
        report = {}
    if not isinstance(inventory, dict):
        issues.append(
            SystemsResultIssue(
                "invalid_bundle_inventory",
                "bundle inventory must be an object",
            )
        )
        inventory = {}
    embedded_validation = validate_systems_evidence_bundle(report, inventory)
    issues.extend(embedded_validation.issues)
    benchmark_id = embedded_validation.benchmark_id
    _validate_bundle_identity(data, report, inventory, issues)
    _validate_bundle_hashes(data, report, inventory, issues)
    alphaevolve_ready = (
        embedded_validation.alphaevolve_ready
        and data.get("alphaevolve_ready") is True
        and not issues
    )
    if data.get("alphaevolve_ready") is not embedded_validation.alphaevolve_ready:
        issues.append(
            SystemsResultIssue(
                "bundle_ready_mismatch",
                "bundle alphaevolve_ready must match embedded report/inventory readiness",
            )
        )
        alphaevolve_ready = False
    return SystemsEvidenceBundleValidation(
        ok=not issues,
        benchmark_id=benchmark_id,
        report_ok=embedded_validation.report_ok,
        inventory_ok=embedded_validation.inventory_ok,
        alphaevolve_ready=alphaevolve_ready and not issues,
        issues=issues,
    )


def render_systems_result_summary(report: dict[str, Any]) -> str:
    validation = validate_systems_result_report(report)
    status = "ok" if validation.ok else "invalid"
    ready = "yes" if validation.alphaevolve_ready else "no"
    gate_rows = []
    gates = report.get("gates")
    if isinstance(gates, list):
        for gate in gates:
            if isinstance(gate, dict):
                gate_rows.append(f"{gate.get('name', '<unknown>')}={gate.get('status', '<unknown>')}")
    claim_records = report.get("claim_calibration", {}).get("records")
    application_records = report.get("application_provenance", {}).get("records")
    scheduling_formulation = report.get("scheduling_formulation")
    scheduling_safety = report.get("scheduling_safety")
    scheduling_deployment = report.get("scheduling_deployment_readiness")
    lines = [
        f"Systems result report: {report.get('benchmark_id', '<unknown>')}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| alphaevolve_ready | {ready} |",
        f"| domain | {report.get('domain', '<unknown>')} |",
        f"| candidate_id | {report.get('candidate_id', '<unknown>')} |",
        f"| gates | {', '.join(gate_rows) if gate_rows else '<none>'} |",
        f"| artifact_count | {len(report.get('artifacts', [])) if isinstance(report.get('artifacts'), list) else 0} |",
        f"| claim_calibration_records | {len(claim_records) if isinstance(claim_records, list) else 0} |",
        f"| application_provenance_records | {len(application_records) if isinstance(application_records, list) else 0} |",
        f"| scheduling_formulation | {'present' if isinstance(scheduling_formulation, dict) else 'absent'} |",
        f"| scheduling_safety | {'present' if isinstance(scheduling_safety, dict) else 'absent'} |",
        f"| scheduling_deployment_readiness | {'present' if isinstance(scheduling_deployment, dict) else 'absent'} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def systems_result_artifact_inventory(
    report: object | str | Path,
    artifact_root: str | Path,
) -> dict[str, Any]:
    """Verify systems report artifact references against concrete files."""
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
                records.append(_systems_artifact_inventory_record(artifact, root))
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
        "schema": SYSTEMS_ARTIFACT_INVENTORY_SCHEMA,
        "report_schema": data.get("schema") if isinstance(data, dict) else None,
        "benchmark_id": data.get("benchmark_id") if isinstance(data, dict) else None,
        "candidate_id": data.get("candidate_id") if isinstance(data, dict) else None,
        "domain": data.get("domain") if isinstance(data, dict) else None,
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


def _load_report(report: object | str | Path) -> tuple[dict[str, Any] | None, list[SystemsResultIssue]]:
    if isinstance(report, dict):
        return dict(report), []
    if isinstance(report, (str, Path)):
        path = Path(report)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [SystemsResultIssue("read_error", f"failed to read systems result report: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [SystemsResultIssue("invalid_json", f"invalid systems result JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [SystemsResultIssue("invalid_shape", "systems result report must be a JSON object")]


def _load_bundle(bundle: object | str | Path) -> tuple[dict[str, Any] | None, list[SystemsResultIssue]]:
    if isinstance(bundle, dict):
        return dict(bundle), []
    if isinstance(bundle, (str, Path)):
        path = Path(bundle)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [
                SystemsResultIssue(
                    "read_error",
                    f"failed to read systems evidence bundle: {exc}",
                )
            ]
        except json.JSONDecodeError as exc:
            return None, [
                SystemsResultIssue(
                    "invalid_json",
                    f"invalid systems evidence bundle JSON: {exc.msg}",
                )
            ]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [
        SystemsResultIssue(
            "invalid_shape",
            "systems evidence bundle must be a JSON object",
        )
    ]


def _validate_bundle_identity(
    bundle: dict[str, Any],
    report: dict[str, Any],
    inventory: dict[str, Any],
    issues: list[SystemsResultIssue],
) -> None:
    for field in ("benchmark_id", "candidate_id", "domain"):
        expected = report.get(field)
        if isinstance(expected, str) and bundle.get(field) != expected:
            issues.append(
                SystemsResultIssue(
                    f"bundle_{field}_mismatch",
                    f"bundle {field} must match embedded systems report",
                )
            )
        if isinstance(expected, str) and inventory.get(field) != expected:
            issues.append(
                SystemsResultIssue(
                    f"bundle_inventory_{field}_mismatch",
                    f"embedded inventory {field} must match systems report",
                )
            )


def _validate_bundle_hashes(
    bundle: dict[str, Any],
    report: dict[str, Any],
    inventory: dict[str, Any],
    issues: list[SystemsResultIssue],
) -> None:
    _validate_embedded_hash(
        bundle,
        "report_sha256",
        report,
        "bundle_report_hash_mismatch",
        "bundle report_sha256 must match embedded report",
        issues,
    )
    _validate_embedded_hash(
        bundle,
        "inventory_sha256",
        inventory,
        "bundle_inventory_hash_mismatch",
        "bundle inventory_sha256 must match embedded inventory",
        issues,
    )
    if bundle.get("inventory_records_sha256") != inventory.get("records_sha256"):
        issues.append(
            SystemsResultIssue(
                "bundle_inventory_records_hash_mismatch",
                "bundle inventory_records_sha256 must match embedded inventory records_sha256",
            )
        )


def _validate_embedded_hash(
    bundle: dict[str, Any],
    field: str,
    value: dict[str, Any],
    mismatch_code: str,
    message: str,
    issues: list[SystemsResultIssue],
) -> None:
    expected = bundle.get(field)
    if not isinstance(expected, str) or _SHA256_RE.fullmatch(expected) is None:
        issues.append(
            SystemsResultIssue(
                f"invalid_{field}",
                f"bundle {field} must be a lowercase SHA-256 hex digest",
            )
        )
        return
    actual = hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if expected != actual:
        issues.append(SystemsResultIssue(mismatch_code, message))


def _validate_systems_inventory(
    inventory: object,
    report: dict[str, Any],
    benchmark_id: str | None,
    issues: list[SystemsResultIssue],
) -> bool:
    if not isinstance(inventory, dict):
        issues.append(SystemsResultIssue("invalid_inventory", "inventory must be an object"))
        return False
    issue_count = len(issues)
    if inventory.get("schema") != SYSTEMS_ARTIFACT_INVENTORY_SCHEMA:
        issues.append(SystemsResultIssue("invalid_inventory_schema", "unsupported systems inventory schema"))
    if inventory.get("ok") is not True:
        issues.append(SystemsResultIssue("inventory_not_ok", "systems inventory must verify every artifact"))
    if inventory.get("report_schema") != report.get("schema"):
        issues.append(SystemsResultIssue("inventory_report_schema_mismatch", "inventory report_schema must match systems report"))
    if benchmark_id is not None and inventory.get("benchmark_id") != benchmark_id:
        issues.append(SystemsResultIssue("inventory_benchmark_id_mismatch", "inventory benchmark_id must match systems report"))
    for field in ("candidate_id", "domain"):
        expected = report.get(field)
        if isinstance(expected, str) and inventory.get(field) != expected:
            issues.append(
                SystemsResultIssue(
                    f"inventory_{field}_mismatch",
                    f"inventory {field} must match systems report",
                )
            )
    records = inventory.get("artifacts")
    if not isinstance(records, list) or not records:
        issues.append(SystemsResultIssue("invalid_inventory_artifacts", "inventory artifacts must be a non-empty list"))
        records = []
    records_payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    records_sha = inventory.get("records_sha256")
    if not isinstance(records_sha, str) or _SHA256_RE.fullmatch(records_sha) is None:
        issues.append(
            SystemsResultIssue(
                "invalid_inventory_records_hash",
                "inventory records_sha256 must be a lowercase SHA-256 hex digest",
            )
        )
    elif hashlib.sha256(records_payload.encode("utf-8")).hexdigest() != records_sha:
        issues.append(
            SystemsResultIssue(
                "inventory_records_hash_mismatch",
                "inventory records_sha256 must match inventory artifacts",
            )
        )
    expected_counts = {
        "artifact_count": len(records),
        "verified_count": sum(
            1
            for record in records
            if isinstance(record, dict) and record.get("status") == "verified"
        ),
        "missing_count": sum(
            1
            for record in records
            if isinstance(record, dict) and record.get("status") == "missing_file"
        ),
        "mismatch_count": sum(
            1
            for record in records
            if isinstance(record, dict)
            and record.get("status") in {"hash_mismatch", "bytes_mismatch"}
        ),
        "invalid_count": sum(
            1
            for record in records
            if isinstance(record, dict)
            and record.get("status")
            in {"invalid_artifact", "unsafe_path", "read_error"}
        ),
    }
    for field, expected in expected_counts.items():
        value = inventory.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            issues.append(
                SystemsResultIssue(
                    f"invalid_inventory_{field}",
                    f"inventory {field} must be a non-negative integer",
                )
            )
        elif value != expected:
            issues.append(
                SystemsResultIssue(
                    f"inventory_{field}_mismatch",
                    f"inventory {field} must match inventory artifacts",
                )
            )
    if inventory.get("verified_count") != inventory.get("artifact_count"):
        issues.append(
            SystemsResultIssue(
                "inventory_verified_count_mismatch",
                "inventory verified_count must equal artifact_count",
            )
        )
    for field in ("missing_count", "mismatch_count", "invalid_count"):
        if inventory.get(field) != 0:
            issues.append(
                SystemsResultIssue(
                    f"inventory_{field}_nonzero",
                    f"inventory {field} must be zero for systems evidence",
                )
            )
    if inventory.get("issues"):
        issues.append(SystemsResultIssue("inventory_has_issues", "inventory issues must be empty"))
    return len(issues) == issue_count


def _systems_artifact_inventory_record(artifact: object, root: Path) -> dict[str, Any]:
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


def _id_field(data: dict[str, Any], field: str, issues: list[SystemsResultIssue]) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or _ID_RE.fullmatch(value) is None:
        issues.append(SystemsResultIssue(f"invalid_{field}", f"{field} must be a stable identifier"))
        return None
    return value


def _validate_gates(value: object, issues: list[SystemsResultIssue]) -> dict[str, str]:
    if not isinstance(value, list) or not value:
        issues.append(SystemsResultIssue("invalid_gates", "gates must be a non-empty list"))
        return {}
    statuses: dict[str, str] = {}
    seen: set[str] = set()
    for gate in value:
        if not isinstance(gate, dict):
            issues.append(SystemsResultIssue("invalid_gate", "gate must be an object"))
            continue
        name = gate.get("name")
        if name not in GATE_NAMES:
            issues.append(SystemsResultIssue("invalid_gate_name", "unsupported gate name"))
            continue
        if name in seen:
            issues.append(SystemsResultIssue("duplicate_gate", "gate names must be unique"))
        seen.add(name)
        status = gate.get("status")
        if status not in GATE_STATUSES:
            issues.append(SystemsResultIssue("invalid_gate_status", "unsupported gate status"))
            continue
        statuses[name] = status
        _validate_gate_detail(gate, name, status, issues)
    for required in GATE_NAMES:
        if required not in seen:
            issues.append(SystemsResultIssue("missing_gate", f"{required} gate is required"))
    return statuses


def _validate_gate_detail(
    gate: dict[str, Any],
    name: str,
    status: str,
    issues: list[SystemsResultIssue],
) -> None:
    case_set_id = gate.get("case_set_id")
    if not isinstance(case_set_id, str) or _ID_RE.fullmatch(case_set_id) is None:
        issues.append(SystemsResultIssue(f"invalid_{name}_case_set_id", "gate case_set_id must be stable"))
    if status == "not_applicable":
        if not isinstance(gate.get("rationale"), str) or not gate["rationale"].strip():
            issues.append(SystemsResultIssue(f"missing_{name}_rationale", "not_applicable gates require rationale"))
        return
    sample_count = gate.get("sample_count")
    if isinstance(sample_count, bool) or not isinstance(sample_count, int) or sample_count <= 0:
        issues.append(SystemsResultIssue(f"invalid_{name}_sample_count", "gate sample_count must be a positive integer"))
    _validate_sha(gate.get("case_set_sha256"), f"invalid_{name}_case_set_hash", "gate case_set_sha256", issues)
    seeds = gate.get("seeds", [])
    if not isinstance(seeds, list) or any(isinstance(seed, bool) or not isinstance(seed, int) for seed in seeds):
        issues.append(SystemsResultIssue(f"invalid_{name}_seeds", "gate seeds must be a list of integers"))
    metrics = gate.get("metrics")
    if not isinstance(metrics, dict) or not metrics:
        issues.append(SystemsResultIssue(f"invalid_{name}_metrics", "gate metrics must be a non-empty object"))
    elif not all(isinstance(key, str) and isinstance(value, (int, float)) and math.isfinite(float(value)) for key, value in metrics.items()):
        issues.append(SystemsResultIssue(f"invalid_{name}_metrics", "gate metrics must be finite numeric values"))


def _gates_are_alphaevolve_ready(statuses: dict[str, str]) -> bool:
    return (
        statuses.get("optimization") == "passed"
        and statuses.get("heldout") in {"passed", "not_applicable"}
        and statuses.get("reference_correctness") in {"passed", "not_applicable"}
    )


def _validate_domain_ready_gate_requirements(
    domain: str | None,
    gate_statuses: dict[str, str],
    issues: list[SystemsResultIssue],
) -> None:
    if domain is None:
        return
    for gate_name, required_status in DOMAIN_READY_GATE_REQUIREMENTS.get(
        domain, {}
    ).items():
        if gate_statuses.get(gate_name) != required_status:
            issues.append(
                SystemsResultIssue(
                    f"invalid_ready_domain_{gate_name}_gate",
                    (
                        f"alphaevolve_ready {domain} reports require "
                        f"{gate_name} gate status {required_status}"
                    ),
                )
            )


def _validate_ready_gate_artifacts(
    gate_statuses: dict[str, str],
    artifact_kinds: set[str],
    issues: list[SystemsResultIssue],
) -> None:
    missing = sorted(
        required_kind
        for gate_name, required_kind in GATE_ARTIFACT_KINDS.items()
        if gate_statuses.get(gate_name) == "passed"
        and required_kind not in artifact_kinds
    )
    if missing:
        issues.append(
            SystemsResultIssue(
                "missing_ready_gate_artifact",
                "alphaevolve_ready passed gates require matching artifact kinds",
            )
        )


def _validate_scheduling_formulation(
    value: object,
    report: dict[str, Any],
    domain: str | None,
    require_ready: bool,
    issues: list[SystemsResultIssue],
) -> bool:
    if domain != "scheduling":
        if value is not None:
            issues.append(
                SystemsResultIssue(
                    "unexpected_scheduling_formulation",
                    "scheduling_formulation is only valid for scheduling reports",
                )
            )
        return domain != "scheduling"
    if value is None:
        if require_ready:
            issues.append(
                SystemsResultIssue(
                    "missing_scheduling_formulation",
                    "alphaevolve_ready scheduling reports require scheduling_formulation",
                )
            )
        return False
    if not isinstance(value, dict):
        issues.append(
            SystemsResultIssue(
                "invalid_scheduling_formulation",
                "scheduling_formulation must be an object",
            )
        )
        return False
    artifact_paths = {
        artifact.get("path")
        for artifact in report.get("artifacts", [])
        if isinstance(artifact, dict) and isinstance(artifact.get("path"), str)
    }
    ok = True
    expected_text = {
        "problem_class": "online_vector_bin_packing",
        "machine_role": "bin",
        "job_role": "item",
        "objective": "stranded_resource_minimization",
    }
    for field, expected in expected_text.items():
        if value.get(field) != expected:
            issues.append(
                SystemsResultIssue(
                    f"invalid_scheduling_{field}",
                    f"scheduling_formulation.{field} must be {expected}",
                )
            )
            ok = False
    resource_dimensions = value.get("resource_dimensions")
    if not isinstance(resource_dimensions, list) or not resource_dimensions:
        issues.append(
            SystemsResultIssue(
                "invalid_scheduling_resource_dimensions",
                "scheduling_formulation.resource_dimensions must be a non-empty list",
            )
        )
        ok = False
    else:
        seen_dimensions: set[str] = set()
        for index, dimension in enumerate(resource_dimensions):
            if not isinstance(dimension, dict):
                issues.append(
                    SystemsResultIssue(
                        "invalid_scheduling_resource_dimension",
                        "resource dimension records must be objects",
                    )
                )
                ok = False
                continue
            name = dimension.get("name")
            if name not in {"cpu", "memory"}:
                issues.append(
                    SystemsResultIssue(
                        "invalid_scheduling_resource_name",
                        f"resource_dimensions[{index}].name must be cpu or memory",
                    )
                )
                ok = False
            else:
                seen_dimensions.add(name)
            for field in ("unit", "capacity_field", "required_field", "free_field"):
                text = dimension.get(field)
                if not isinstance(text, str) or not text.strip():
                    issues.append(
                        SystemsResultIssue(
                            f"invalid_scheduling_resource_{field}",
                            f"resource_dimensions[{index}].{field} must be non-empty text",
                        )
                    )
                    ok = False
        if seen_dimensions != {"cpu", "memory"}:
            issues.append(
                SystemsResultIssue(
                    "missing_scheduling_resource_dimension",
                    "scheduling formulation must include cpu and memory dimensions",
                )
            )
            ok = False
    snapshots = value.get("snapshot_provenance")
    if not isinstance(snapshots, list) or not snapshots:
        issues.append(
            SystemsResultIssue(
                "invalid_scheduling_snapshot_provenance",
                "scheduling_formulation.snapshot_provenance must be a non-empty list",
            )
        )
        ok = False
    else:
        for index, snapshot in enumerate(snapshots):
            if not isinstance(snapshot, dict):
                issues.append(
                    SystemsResultIssue(
                        "invalid_scheduling_snapshot_record",
                        "snapshot provenance records must be objects",
                    )
                )
                ok = False
                continue
            snapshot_id = snapshot.get("snapshot_id")
            if not isinstance(snapshot_id, str) or _ID_RE.fullmatch(snapshot_id) is None:
                issues.append(
                    SystemsResultIssue(
                        "invalid_scheduling_snapshot_id",
                        f"snapshot_provenance[{index}].snapshot_id must be stable",
                    )
                )
                ok = False
            for field in ("workload_source", "capacity_source"):
                text = snapshot.get(field)
                if not isinstance(text, str) or not text.strip():
                    issues.append(
                        SystemsResultIssue(
                            f"invalid_scheduling_{field}",
                            f"snapshot_provenance[{index}].{field} must be non-empty text",
                        )
                    )
                    ok = False
            _validate_sha(
                snapshot.get("simulator_input_sha256"),
                "invalid_scheduling_simulator_input_hash",
                "scheduling simulator_input_sha256",
                issues,
            )
            if not isinstance(snapshot.get("simulator_input_sha256"), str) or _SHA256_RE.fullmatch(snapshot.get("simulator_input_sha256")) is None:
                ok = False
    for field in (
        "stranded_resource_definition",
        "feature_mapping",
    ):
        text = value.get(field)
        if not isinstance(text, str) or not text.strip():
            issues.append(
                SystemsResultIssue(
                    f"invalid_scheduling_{field}",
                    f"scheduling_formulation.{field} must be non-empty text",
                )
            )
            ok = False
    _validate_application_reference_list(
        value.get("artifact_refs"),
        artifact_paths,
        "artifact_refs",
        "invalid_scheduling_formulation_artifact_ref",
        "scheduling_formulation",
        issues,
    )
    if not isinstance(value.get("artifact_refs"), list) or not value["artifact_refs"]:
        ok = False
    elif any(item not in artifact_paths for item in value["artifact_refs"]):
        ok = False
    return ok


def _validate_scheduling_safety(
    value: object,
    report: dict[str, Any],
    domain: str | None,
    require_ready: bool,
    issues: list[SystemsResultIssue],
) -> bool:
    if domain != "scheduling":
        if value is not None:
            issues.append(
                SystemsResultIssue(
                    "unexpected_scheduling_safety",
                    "scheduling_safety is only valid for scheduling reports",
                )
            )
        return domain != "scheduling"
    if value is None:
        if require_ready:
            issues.append(
                SystemsResultIssue(
                    "missing_scheduling_safety",
                    "alphaevolve_ready scheduling reports require scheduling_safety",
                )
            )
        return False
    if not isinstance(value, dict):
        issues.append(
            SystemsResultIssue(
                "invalid_scheduling_safety",
                "scheduling_safety must be an object",
            )
        )
        return False
    artifact_paths = {
        artifact.get("path")
        for artifact in report.get("artifacts", [])
        if isinstance(artifact, dict) and isinstance(artifact.get("path"), str)
    }
    ok = True
    for field in (
        "feasibility_filter_id",
        "candidate_set_source",
        "simulator_boundary",
        "admission_boundary",
        "placement_boundary",
        "ranking_function_scope",
    ):
        text = value.get(field)
        if not isinstance(text, str) or not text.strip():
            issues.append(
                SystemsResultIssue(
                    f"invalid_scheduling_{field}",
                    f"scheduling_safety.{field} must be non-empty text",
                )
            )
            ok = False
    if value.get("ranking_only") is not True:
        issues.append(
            SystemsResultIssue(
                "invalid_scheduling_ranking_only",
                "scheduling_safety.ranking_only must be true",
            )
        )
        ok = False
    if value.get("can_admit_jobs") is not False:
        issues.append(
            SystemsResultIssue(
                "invalid_scheduling_admission_authority",
                "scheduling heuristics must not admit jobs directly",
            )
        )
        ok = False
    if value.get("can_reject_jobs") is not False:
        issues.append(
            SystemsResultIssue(
                "invalid_scheduling_rejection_authority",
                "scheduling heuristics must not reject jobs directly",
            )
        )
        ok = False
    if value.get("can_place_jobs") is not False:
        issues.append(
            SystemsResultIssue(
                "invalid_scheduling_placement_authority",
                "scheduling heuristics must not place jobs directly",
            )
        )
        ok = False
    invariants = value.get("resource_invariants")
    if not isinstance(invariants, list) or not invariants:
        issues.append(
            SystemsResultIssue(
                "invalid_scheduling_resource_invariants",
                "scheduling_safety.resource_invariants must be a non-empty list",
            )
        )
        ok = False
    elif not all(isinstance(item, str) and item.strip() for item in invariants):
        issues.append(
            SystemsResultIssue(
                "invalid_scheduling_resource_invariants",
                "scheduling resource invariants must be non-empty text",
            )
        )
        ok = False
    _validate_application_reference_list(
        value.get("artifact_refs"),
        artifact_paths,
        "artifact_refs",
        "invalid_scheduling_artifact_ref",
        "scheduling_safety",
        issues,
    )
    if not isinstance(value.get("artifact_refs"), list) or not value["artifact_refs"]:
        ok = False
    elif any(item not in artifact_paths for item in value["artifact_refs"]):
        ok = False
    return ok


def _validate_scheduling_deployment_readiness(
    value: object,
    report: dict[str, Any],
    domain: str | None,
    require_ready: bool,
    issues: list[SystemsResultIssue],
) -> bool:
    if domain != "scheduling":
        if value is not None:
            issues.append(
                SystemsResultIssue(
                    "unexpected_scheduling_deployment_readiness",
                    "scheduling_deployment_readiness is only valid for scheduling reports",
                )
            )
        return domain != "scheduling"
    if value is None:
        if require_ready:
            issues.append(
                SystemsResultIssue(
                    "missing_scheduling_deployment_readiness",
                    "alphaevolve_ready scheduling reports require scheduling_deployment_readiness",
                )
            )
        return False
    if not isinstance(value, dict):
        issues.append(
            SystemsResultIssue(
                "invalid_scheduling_deployment_readiness",
                "scheduling_deployment_readiness must be an object",
            )
        )
        return False
    artifact_paths = {
        artifact.get("path")
        for artifact in report.get("artifacts", [])
        if isinstance(artifact, dict) and isinstance(artifact.get("path"), str)
    }
    ok = True
    for field in (
        "heuristic_structure",
        "operator_review",
        "debuggability_notes",
        "deployment_ergonomics",
        "rollout_risk_controls",
        "learned_policy_comparison",
    ):
        text = value.get(field)
        if not isinstance(text, str) or not text.strip():
            issues.append(
                SystemsResultIssue(
                    f"invalid_scheduling_deployment_{field}",
                    f"scheduling_deployment_readiness.{field} must be non-empty text",
                )
            )
            ok = False
    checks = value.get("predictability_checks")
    if not isinstance(checks, list) or not checks:
        issues.append(
            SystemsResultIssue(
                "invalid_scheduling_predictability_checks",
                "scheduling_deployment_readiness.predictability_checks must be a non-empty list",
            )
        )
        ok = False
    elif not all(isinstance(item, str) and item.strip() for item in checks):
        issues.append(
            SystemsResultIssue(
                "invalid_scheduling_predictability_checks",
                "scheduling predictability checks must be non-empty text",
            )
        )
        ok = False
    for flag in (
        "human_reviewed",
        "black_box_baseline_compared",
        "rollout_risk_reviewed",
    ):
        if value.get(flag) is not True:
            issues.append(
                SystemsResultIssue(
                    f"invalid_scheduling_{flag}",
                    f"scheduling_deployment_readiness.{flag} must be true",
                )
            )
            ok = False
    _validate_application_reference_list(
        value.get("artifact_refs"),
        artifact_paths,
        "artifact_refs",
        "invalid_scheduling_deployment_artifact_ref",
        "scheduling_deployment_readiness",
        issues,
    )
    if not isinstance(value.get("artifact_refs"), list) or not value["artifact_refs"]:
        ok = False
    elif any(item not in artifact_paths for item in value["artifact_refs"]):
        ok = False
    return ok


def _validate_claim_calibration(
    value: object,
    report: dict[str, Any],
    domain: str | None,
    require_ready: bool,
    issues: list[SystemsResultIssue],
) -> bool:
    if value is None:
        if require_ready:
            issues.append(
                SystemsResultIssue(
                    "missing_claim_calibration",
                    "alphaevolve_ready systems reports require claim_calibration",
                )
            )
        return False
    if not isinstance(value, dict):
        issues.append(
            SystemsResultIssue(
                "invalid_claim_calibration",
                "claim_calibration must be an object",
            )
        )
        return False
    boundary = value.get("boundary_statement")
    if not isinstance(boundary, str) or not boundary.strip():
        issues.append(
            SystemsResultIssue(
                "missing_claim_calibration_boundary",
                "claim_calibration requires a non-empty boundary_statement",
            )
        )
    records = value.get("records")
    if not isinstance(records, list) or not records:
        issues.append(
            SystemsResultIssue(
                "invalid_claim_calibration_records",
                "claim_calibration.records must be a non-empty list",
            )
        )
        return False
    artifact_paths = {
        artifact.get("path")
        for artifact in report.get("artifacts", [])
        if isinstance(artifact, dict) and isinstance(artifact.get("path"), str)
    }
    gate_names = {
        gate.get("name")
        for gate in report.get("gates", [])
        if isinstance(gate, dict) and isinstance(gate.get("name"), str)
    }
    metric_names = _report_metric_names(report)
    claim_ids: set[str] = set()
    valid_records = 0
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append(
                SystemsResultIssue(
                    "invalid_claim_calibration_record",
                    "claim calibration records must be objects",
                )
            )
            continue
        prefix = f"claim_calibration.records[{index}]"
        before_issues = len(issues)
        claim_id = record.get("claim_id")
        if not isinstance(claim_id, str) or _ID_RE.fullmatch(claim_id) is None:
            issues.append(
                SystemsResultIssue(
                    "invalid_claim_id",
                    f"{prefix}.claim_id must be stable",
                )
            )
        elif claim_id in claim_ids:
            issues.append(
                SystemsResultIssue(
                    "duplicate_claim_calibration",
                    "claim_calibration claim_id values must be unique",
                )
            )
        else:
            claim_ids.add(claim_id)
        if domain is not None and record.get("domain") != domain:
            issues.append(
                SystemsResultIssue(
                    "claim_calibration_domain_mismatch",
                    f"{prefix}.domain must match the systems report domain",
                )
            )
        if record.get("claim_kind") not in CLAIM_CALIBRATION_KINDS:
            issues.append(
                SystemsResultIssue(
                    "invalid_claim_kind",
                    f"{prefix}.claim_kind is unsupported",
                )
            )
        gate_name = record.get("gate_name")
        if not isinstance(gate_name, str) or gate_name not in gate_names:
            issues.append(
                SystemsResultIssue(
                    "invalid_claim_gate",
                    f"{prefix}.gate_name must reference a declared gate",
                )
            )
        metric_name = record.get("metric_name")
        if not isinstance(metric_name, str) or metric_name not in metric_names:
            issues.append(
                SystemsResultIssue(
                    "invalid_claim_metric",
                    f"{prefix}.metric_name must reference a declared gate metric",
                )
            )
        value_number = record.get("reported_value")
        if (
            isinstance(value_number, bool)
            or not isinstance(value_number, (int, float))
            or not math.isfinite(float(value_number))
        ):
            issues.append(
                SystemsResultIssue(
                    "invalid_claim_reported_value",
                    f"{prefix}.reported_value must be finite numeric",
                )
            )
        for field in (
            "unit",
            "baseline_label",
            "denominator",
            "comparison_window",
            "aggregation_method",
            "runtime_context",
            "claim_scope",
            "source_ref",
        ):
            text = record.get(field)
            if not isinstance(text, str) or not text.strip():
                issues.append(
                    SystemsResultIssue(
                        f"invalid_claim_{field}",
                        f"{prefix}.{field} must be non-empty text",
                    )
                )
        _validate_application_reference_list(
            record.get("artifact_refs"),
            artifact_paths,
            "artifact_refs",
            "invalid_claim_artifact_ref",
            prefix,
            issues,
        )
        if len(issues) == before_issues:
            valid_records += 1
    return valid_records == len(records)


def _validate_compiler_ir_provenance(
    value: object,
    report: dict[str, Any],
    domain: str | None,
    require_ready: bool,
    issues: list[SystemsResultIssue],
) -> bool:
    if value is None:
        if require_ready and domain == "compiler":
            issues.append(
                SystemsResultIssue(
                    "missing_compiler_ir_provenance",
                    "alphaevolve_ready compiler reports require compiler_ir_provenance",
                )
            )
        return False
    if domain not in {"compiler", "kernel"}:
        issues.append(
            SystemsResultIssue(
                "invalid_compiler_ir_domain",
                "compiler_ir_provenance is only valid for compiler or kernel domains",
            )
        )
        return False
    if not isinstance(value, dict):
        issues.append(
            SystemsResultIssue(
                "invalid_compiler_ir_provenance",
                "compiler_ir_provenance must be an object",
            )
        )
        return False
    artifact_paths = {
        artifact.get("path")
        for artifact in report.get("artifacts", [])
        if isinstance(artifact, dict) and isinstance(artifact.get("path"), str)
    }
    for field in (
        "boundary_statement",
        "ir_origin",
        "editability_boundary",
        "baseline_provenance",
        "numerical_tolerance_policy",
        "final_expert_confirmation_scope",
    ):
        text = value.get(field)
        if not isinstance(text, str) or not text.strip():
            issues.append(
                SystemsResultIssue(
                    f"invalid_compiler_ir_{field}",
                    f"compiler_ir_provenance.{field} must be non-empty text",
                )
            )
    _validate_sha(
        value.get("reference_implementation_sha256"),
        "invalid_compiler_ir_reference_hash",
        "compiler_ir_provenance.reference_implementation_sha256",
        issues,
    )
    input_generator_id = value.get("randomized_input_generator_id")
    if (
        not isinstance(input_generator_id, str)
        or _ID_RE.fullmatch(input_generator_id) is None
    ):
        issues.append(
            SystemsResultIssue(
                "invalid_compiler_ir_input_generator_id",
                "compiler_ir_provenance.randomized_input_generator_id must be stable",
            )
        )
    _validate_sha(
        value.get("randomized_input_generator_sha256"),
        "invalid_compiler_ir_input_generator_hash",
        "compiler_ir_provenance.randomized_input_generator_sha256",
        issues,
    )
    records = value.get("edit_records")
    if not isinstance(records, list) or not records:
        issues.append(
            SystemsResultIssue(
                "invalid_compiler_ir_edit_records",
                "compiler_ir_provenance.edit_records must be a non-empty list",
            )
        )
        return False
    record_ids: set[str] = set()
    valid_records = 0
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append(
                SystemsResultIssue(
                    "invalid_compiler_ir_edit_record",
                    "compiler IR edit records must be objects",
                )
            )
            continue
        prefix = f"compiler_ir_provenance.edit_records[{index}]"
        before_issues = len(issues)
        edit_id = record.get("edit_id")
        if not isinstance(edit_id, str) or _ID_RE.fullmatch(edit_id) is None:
            issues.append(
                SystemsResultIssue(
                    "invalid_compiler_ir_edit_id",
                    f"{prefix}.edit_id must be stable",
                )
            )
        elif edit_id in record_ids:
            issues.append(
                SystemsResultIssue(
                    "duplicate_compiler_ir_edit_id",
                    "compiler IR edit_id values must be unique",
                )
            )
        else:
            record_ids.add(edit_id)
        if record.get("abstraction_level") not in COMPILER_IR_ABSTRACTION_LEVELS:
            issues.append(
                SystemsResultIssue(
                    "invalid_compiler_ir_abstraction_level",
                    f"{prefix}.abstraction_level is unsupported",
                )
            )
        seed_count = record.get("randomized_seed_count")
        if (
            isinstance(seed_count, bool)
            or not isinstance(seed_count, int)
            or seed_count <= 0
        ):
            issues.append(
                SystemsResultIssue(
                    "invalid_compiler_ir_randomized_seed_count",
                    f"{prefix}.randomized_seed_count must be positive",
                )
            )
        if record.get("reference_check_passed") is not True:
            issues.append(
                SystemsResultIssue(
                    "invalid_compiler_ir_reference_check",
                    f"{prefix}.reference_check_passed must be true",
                )
            )
        _validate_application_reference_list(
            record.get("artifact_refs"),
            artifact_paths,
            "artifact_refs",
            "invalid_compiler_ir_artifact_ref",
            prefix,
            issues,
        )
        if len(issues) == before_issues:
            valid_records += 1
    return valid_records == len(records)


def _validate_application_provenance(
    value: object,
    report: dict[str, Any],
    domain: str | None,
    require_ready: bool,
    issues: list[SystemsResultIssue],
) -> bool:
    if value is None:
        if require_ready:
            issues.append(
                SystemsResultIssue(
                    "missing_application_provenance",
                    "alphaevolve_ready systems reports require application_provenance",
                )
            )
        return False
    if not isinstance(value, dict):
        issues.append(
            SystemsResultIssue(
                "invalid_application_provenance",
                "application_provenance must be an object",
            )
        )
        return False
    boundary = value.get("boundary_statement")
    if not isinstance(boundary, str) or not boundary.strip():
        issues.append(
            SystemsResultIssue(
                "missing_application_boundary",
                "application_provenance requires a non-empty boundary_statement",
            )
        )
    records = value.get("records")
    if not isinstance(records, list) or not records:
        issues.append(
            SystemsResultIssue(
                "invalid_application_records",
                "application_provenance.records must be a non-empty list",
            )
        )
        return False
    artifact_paths = {
        artifact.get("path")
        for artifact in report.get("artifacts", [])
        if isinstance(artifact, dict) and isinstance(artifact.get("path"), str)
    }
    claim_ids = _report_claim_ids(report)
    role_counts: dict[str, int] = {}
    approved_or_deployed = False
    record_ids: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append(
                SystemsResultIssue(
                    "invalid_application_record",
                    "application provenance records must be objects",
                )
            )
            continue
        prefix = f"application_provenance.records[{index}]"
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or _ID_RE.fullmatch(record_id) is None:
            issues.append(
                SystemsResultIssue(
                    "invalid_application_record_id",
                    f"{prefix}.record_id must be stable",
                )
            )
        elif record_id in record_ids:
            issues.append(
                SystemsResultIssue(
                    "duplicate_application_record",
                    "application provenance record_id values must be unique",
                )
            )
        else:
            record_ids.add(record_id)
        role = record.get("role")
        if role not in APPLICATION_PROVENANCE_ROLES:
            issues.append(
                SystemsResultIssue(
                    "invalid_application_role",
                    f"{prefix}.role is unsupported",
                )
            )
        else:
            role_counts[role] = role_counts.get(role, 0) + 1
        if domain is not None and record.get("domain") != domain:
            issues.append(
                SystemsResultIssue(
                    "application_domain_mismatch",
                    f"{prefix}.domain must match the systems report domain",
                )
            )
        for field in (
            "responsible_label",
            "review_scope",
            "ownership_scope",
        ):
            text = record.get(field)
            if not isinstance(text, str) or not text.strip():
                issues.append(
                    SystemsResultIssue(
                        f"invalid_application_{field}",
                        f"{prefix}.{field} must be non-empty text",
                    )
                )
        approval_state = record.get("approval_state")
        if approval_state not in APPLICATION_APPROVAL_STATES:
            issues.append(
                SystemsResultIssue(
                    "invalid_application_approval_state",
                    f"{prefix}.approval_state is unsupported",
                )
            )
        elif approval_state in {"approved", "deployed"}:
            approved_or_deployed = True
        _validate_application_reference_list(
            record.get("claim_links"),
            claim_ids,
            "claim_links",
            "invalid_application_claim_link",
            prefix,
            issues,
        )
        _validate_application_reference_list(
            record.get("artifact_refs"),
            artifact_paths,
            "artifact_refs",
            "invalid_application_artifact_ref",
            prefix,
            issues,
        )
    required_role_sets = [
        {"application_colead", "domain_advisor"},
        {"domain_reviewer"},
        {"validation_infrastructure_owner", "workload_data_steward"},
        {"production_approver"},
    ]
    missing_groups = [
        sorted(group)
        for group in required_role_sets
        if not any(role_counts.get(role, 0) > 0 for role in group)
    ]
    if missing_groups:
        issues.append(
            SystemsResultIssue(
                "missing_application_role_coverage",
                "application provenance must include owner/advisor, reviewer, validation/data, and approval roles",
            )
        )
    if not approved_or_deployed:
        issues.append(
            SystemsResultIssue(
                "missing_application_approval",
                "application provenance requires an approved or deployed record",
            )
        )
    return not missing_groups and approved_or_deployed


def _report_claim_ids(report: dict[str, Any]) -> set[str]:
    claim_ids = {report["benchmark_id"]} if isinstance(report.get("benchmark_id"), str) else set()
    certification = report.get("certification")
    if isinstance(certification, dict) and isinstance(certification.get("claim_id"), str):
        claim_ids.add(certification["claim_id"])
    calibration = report.get("claim_calibration")
    records = calibration.get("records") if isinstance(calibration, dict) else None
    if isinstance(records, list):
        for record in records:
            if isinstance(record, dict) and isinstance(record.get("claim_id"), str):
                claim_ids.add(record["claim_id"])
    return claim_ids


def _report_metric_names(report: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    gates = report.get("gates")
    if not isinstance(gates, list):
        return names
    for gate in gates:
        if not isinstance(gate, dict):
            continue
        metrics = gate.get("metrics")
        if isinstance(metrics, dict):
            names.update(key for key in metrics if isinstance(key, str))
    return names


def _validate_application_reference_list(
    value: object,
    allowed: set[str],
    field: str,
    code: str,
    prefix: str,
    issues: list[SystemsResultIssue],
) -> None:
    if not isinstance(value, list) or not value:
        issues.append(
            SystemsResultIssue(
                code,
                f"{prefix}.{field} must be a non-empty list",
            )
        )
        return
    for item in value:
        if not isinstance(item, str) or item not in allowed:
            issues.append(
                SystemsResultIssue(
                    code,
                    f"{prefix}.{field} must reference declared report evidence",
                )
            )


def _validate_artifacts(value: object, issues: list[SystemsResultIssue]) -> set[str]:
    kinds: set[str] = set()
    if not isinstance(value, list) or not value:
        issues.append(SystemsResultIssue("invalid_artifacts", "artifacts must be a non-empty list"))
        return kinds
    for artifact in value:
        if not isinstance(artifact, dict):
            issues.append(SystemsResultIssue("invalid_artifact", "artifact must be an object"))
            continue
        if artifact.get("kind") not in ARTIFACT_KINDS:
            issues.append(SystemsResultIssue("invalid_artifact_kind", "unsupported artifact kind"))
        else:
            kinds.add(artifact["kind"])
        _validate_file_record(artifact, "artifact", issues)
    return kinds


def _validate_certification_reference(value: object, issues: list[SystemsResultIssue]) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        issues.append(SystemsResultIssue("invalid_certification", "certification must be an object when present"))
        return None
    if value.get("schema") != "libreevolve.paper_result_certification.v1":
        issues.append(SystemsResultIssue("invalid_certification_schema", "certification schema must reference paper result certification v1"))
    if not isinstance(value.get("claim_id"), str) or _ID_RE.fullmatch(value["claim_id"]) is None:
        issues.append(SystemsResultIssue("invalid_certification_claim_id", "certification claim_id must be stable"))
    paper_claim_ready = value.get("paper_claim_ready")
    if not isinstance(paper_claim_ready, bool):
        issues.append(SystemsResultIssue("invalid_certification_ready", "certification paper_claim_ready must be boolean"))
        return None
    return paper_claim_ready


def _validate_file_record(record: dict[str, Any], prefix: str, issues: list[SystemsResultIssue]) -> None:
    path = record.get("path")
    path_obj = Path(path) if isinstance(path, str) else None
    if (
        path_obj is None
        or not path
        or path_obj.is_absolute()
        or path.startswith(("/", "\\"))
        or ".." in path_obj.parts
    ):
        issues.append(SystemsResultIssue(f"invalid_{prefix}_path", f"{prefix} path must be safe and relative"))
    _validate_sha(record.get("sha256"), f"invalid_{prefix}_hash", f"{prefix} sha256", issues)
    byte_count = record.get("bytes")
    if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count <= 0:
        issues.append(SystemsResultIssue(f"invalid_{prefix}_bytes", f"{prefix} bytes must be a positive integer"))


def _validate_sha(value: object, code: str, label: str, issues: list[SystemsResultIssue]) -> None:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        issues.append(SystemsResultIssue(code, f"{label} must be a lowercase SHA-256 hex digest"))
