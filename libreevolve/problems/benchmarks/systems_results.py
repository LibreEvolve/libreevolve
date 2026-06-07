from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SYSTEMS_RESULT_SCHEMA = "libreevolve.systems_result_report.v1"
BENCHMARK_DOMAINS = frozenset({"compiler", "hardware", "kernel", "scheduling", "systems"})
GATE_NAMES = frozenset({"optimization", "heldout", "reference_correctness"})
GATE_STATUSES = frozenset({"passed", "failed", "not_checked", "not_applicable"})
ARTIFACT_KINDS = frozenset({"case_set", "metrics", "reference_report", "heldout_report", "summary"})
GATE_ARTIFACT_KINDS = {
    "optimization": "metrics",
    "heldout": "heldout_report",
    "reference_correctness": "reference_report",
}
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
    certification_ready = _validate_certification_reference(data.get("certification"), issues)
    if data.get("alphaevolve_ready") is True and not _gates_are_alphaevolve_ready(gate_statuses):
        issues.append(
            SystemsResultIssue(
                "invalid_alphaevolve_ready",
                "alphaevolve_ready requires passed optimization plus heldout/reference gates passed or documented not_applicable",
            )
        )
    if data.get("alphaevolve_ready") is True:
        _validate_ready_gate_artifacts(gate_statuses, artifact_kinds, issues)
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
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


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
