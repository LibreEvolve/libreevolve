from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PAPER_CERTIFICATION_SCHEMA = "libreevolve.paper_result_certification.v1"
CERTIFICATION_LEVELS = frozenset({"local_validator", "independent", "paper_claim"})
VERDICTS = frozenset({"passed", "failed", "not_checked", "not_applicable"})
VERIFIER_KINDS = frozenset(
    {
        "local_evaluator",
        "independent_script",
        "external_human_review",
        "deployment_measurement",
        "simulator_holdout",
        "reference_correctness",
        "exact_certificate",
    }
)
EVIDENCE_KINDS = frozenset(
    {
        "verifier_output",
        "review_record",
        "deployment_measurement",
        "simulator_holdout",
        "reference_correctness",
        "exact_certificate",
    }
)
ARTIFACT_KINDS = frozenset(
    {
        "verifier_log",
        "certificate",
        "review_record",
        "deployment_report",
        "reference_report",
        "reproduction_bundle",
    }
)
EVIDENCE_ARTIFACT_KINDS = {
    "verifier_output": "verifier_log",
    "review_record": "review_record",
    "deployment_measurement": "deployment_report",
    "simulator_holdout": "reproduction_bundle",
    "reference_correctness": "reference_report",
    "exact_certificate": "certificate",
}
_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class CertificationIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CertificationValidation:
    ok: bool
    paper_claim_ready: bool
    claim_id: str | None
    certification_level: str | None
    verdict: str | None
    issues: list[CertificationIssue]


def validate_paper_result_certification(report: object | str | Path) -> CertificationValidation:
    """Validate independent certification metadata for paper-level result claims."""
    data, read_issues = _load_report(report)
    if read_issues:
        return CertificationValidation(False, False, None, None, None, read_issues)
    assert isinstance(data, dict)
    issues: list[CertificationIssue] = []
    if data.get("schema") != PAPER_CERTIFICATION_SCHEMA:
        issues.append(CertificationIssue("invalid_schema", "unsupported certification schema"))
    claim_id = _id_field(data, "claim_id", issues)
    _id_field(data, "benchmark_id", issues)
    _id_field(data, "candidate_id", issues)
    level = data.get("certification_level")
    if level not in CERTIFICATION_LEVELS:
        issues.append(CertificationIssue("invalid_certification_level", "unsupported certification level"))
        level = None
    verdict = data.get("verdict")
    if verdict not in VERDICTS:
        issues.append(CertificationIssue("invalid_verdict", "unsupported certification verdict"))
        verdict = None
    verifier_kind, independent = _validate_verifier(data.get("verifier"), issues)
    _validate_scope(data.get("scope"), issues)
    evidence_passed, passed_evidence_kinds = _validate_evidence(data.get("evidence"), issues)
    artifact_kinds = _validate_artifacts(data.get("artifacts"), issues)
    if level == "paper_claim":
        if verdict != "passed":
            issues.append(CertificationIssue("paper_claim_not_passed", "paper claims require a passed verdict"))
        if verifier_kind == "local_evaluator":
            issues.append(CertificationIssue("paper_claim_local_verifier", "paper claims cannot rely on the local evaluator alone"))
        if independent is not True:
            issues.append(CertificationIssue("paper_claim_not_independent", "paper claims require independent verification"))
        if not evidence_passed:
            issues.append(CertificationIssue("paper_claim_missing_passed_evidence", "paper claims require passed evidence records"))
        missing_artifact_kinds = sorted(
            {
                EVIDENCE_ARTIFACT_KINDS[kind]
                for kind in passed_evidence_kinds
                if kind in EVIDENCE_ARTIFACT_KINDS
                and EVIDENCE_ARTIFACT_KINDS[kind] not in artifact_kinds
            }
        )
        if missing_artifact_kinds:
            issues.append(
                CertificationIssue(
                    "paper_claim_missing_evidence_artifact",
                    "paper claims require artifact kinds matching passed evidence kinds",
                )
            )
    paper_claim_ready = not issues and level == "paper_claim" and verdict == "passed"
    return CertificationValidation(
        ok=not issues,
        paper_claim_ready=paper_claim_ready,
        claim_id=claim_id,
        certification_level=level,
        verdict=verdict,
        issues=issues,
    )


def render_certification_summary(report: dict[str, Any]) -> str:
    validation = validate_paper_result_certification(report)
    status = "ok" if validation.ok else "invalid"
    ready = "yes" if validation.paper_claim_ready else "no"
    verifier = report.get("verifier") if isinstance(report.get("verifier"), dict) else {}
    lines = [
        f"Paper result certification: {report.get('claim_id', '<unknown>')}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| paper_claim_ready | {ready} |",
        f"| benchmark_id | {report.get('benchmark_id', '<unknown>')} |",
        f"| candidate_id | {report.get('candidate_id', '<unknown>')} |",
        f"| certification_level | {report.get('certification_level', '<unknown>')} |",
        f"| verdict | {report.get('verdict', '<unknown>')} |",
        f"| verifier_kind | {verifier.get('kind', '<unknown>')} |",
        f"| independent_from_search | {verifier.get('independent_from_search', '<unknown>')} |",
        f"| evidence_count | {len(report.get('evidence', [])) if isinstance(report.get('evidence'), list) else 0} |",
        f"| artifact_count | {len(report.get('artifacts', [])) if isinstance(report.get('artifacts'), list) else 0} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_report(report: object | str | Path) -> tuple[dict[str, Any] | None, list[CertificationIssue]]:
    if isinstance(report, dict):
        return dict(report), []
    if isinstance(report, (str, Path)):
        path = Path(report)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [CertificationIssue("read_error", f"failed to read certification report: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [CertificationIssue("invalid_json", f"invalid certification JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [CertificationIssue("invalid_shape", "certification report must be a JSON object")]


def _id_field(data: dict[str, Any], field: str, issues: list[CertificationIssue]) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or _ID_RE.fullmatch(value) is None:
        issues.append(CertificationIssue(f"invalid_{field}", f"{field} must be a stable identifier"))
        return None
    return value


def _validate_verifier(value: object, issues: list[CertificationIssue]) -> tuple[str | None, bool | None]:
    if not isinstance(value, dict):
        issues.append(CertificationIssue("invalid_verifier", "verifier must be an object"))
        return None, None
    kind = value.get("kind")
    if kind not in VERIFIER_KINDS:
        issues.append(CertificationIssue("invalid_verifier_kind", "unsupported verifier kind"))
        kind = None
    if not isinstance(value.get("name"), str) or not value["name"].strip():
        issues.append(CertificationIssue("invalid_verifier_name", "verifier name is required"))
    independent = value.get("independent_from_search")
    if not isinstance(independent, bool):
        issues.append(CertificationIssue("invalid_verifier_independence", "independent_from_search must be boolean"))
        independent = None
    return kind, independent


def _validate_scope(value: object, issues: list[CertificationIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(CertificationIssue("invalid_scope", "scope must be an object"))
        return
    for field in ("claim", "pass_fail_scope"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            issues.append(CertificationIssue(f"invalid_scope_{field}", f"scope.{field} is required"))
    limitations = value.get("limitations", [])
    if not isinstance(limitations, list) or any(not isinstance(item, str) for item in limitations):
        issues.append(CertificationIssue("invalid_scope_limitations", "scope.limitations must be a list of strings"))


def _validate_evidence(
    value: object,
    issues: list[CertificationIssue],
) -> tuple[bool, set[str]]:
    if not isinstance(value, list) or not value:
        issues.append(CertificationIssue("invalid_evidence", "evidence must be a non-empty list"))
        return False, set()
    passed = False
    passed_kinds: set[str] = set()
    for record in value:
        if not isinstance(record, dict):
            issues.append(CertificationIssue("invalid_evidence_record", "evidence record must be an object"))
            continue
        if record.get("kind") not in EVIDENCE_KINDS:
            issues.append(CertificationIssue("invalid_evidence_kind", "unsupported evidence kind"))
        status = record.get("status")
        if status not in VERDICTS:
            issues.append(CertificationIssue("invalid_evidence_status", "unsupported evidence status"))
        elif status == "passed":
            passed = True
            kind = record.get("kind")
            if kind in EVIDENCE_KINDS:
                passed_kinds.add(kind)
        _validate_file_record(record, "evidence", issues)
    return passed, passed_kinds


def _validate_artifacts(value: object, issues: list[CertificationIssue]) -> set[str]:
    kinds: set[str] = set()
    if not isinstance(value, list) or not value:
        issues.append(CertificationIssue("invalid_artifacts", "artifacts must be a non-empty list"))
        return kinds
    for record in value:
        if not isinstance(record, dict):
            issues.append(CertificationIssue("invalid_artifact_record", "artifact record must be an object"))
            continue
        if record.get("kind") not in ARTIFACT_KINDS:
            issues.append(CertificationIssue("invalid_artifact_kind", "unsupported artifact kind"))
        else:
            kinds.add(record["kind"])
        _validate_file_record(record, "artifact", issues)
    return kinds


def _validate_file_record(record: dict[str, Any], prefix: str, issues: list[CertificationIssue]) -> None:
    path = record.get("path")
    path_obj = Path(path) if isinstance(path, str) else None
    if (
        path_obj is None
        or not path
        or path_obj.is_absolute()
        or path.startswith(("/", "\\"))
        or ".." in path_obj.parts
    ):
        issues.append(CertificationIssue(f"invalid_{prefix}_path", f"{prefix} path must be safe and relative"))
    sha = record.get("sha256")
    if not isinstance(sha, str) or _SHA256_RE.fullmatch(sha) is None:
        issues.append(CertificationIssue(f"invalid_{prefix}_hash", f"{prefix} sha256 must be a lowercase SHA-256 hex digest"))
    byte_count = record.get("bytes")
    if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count <= 0:
        issues.append(CertificationIssue(f"invalid_{prefix}_bytes", f"{prefix} bytes must be a positive integer"))
