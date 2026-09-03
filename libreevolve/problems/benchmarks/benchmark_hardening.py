from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._path_policy import safe_relative_path


BENCHMARK_HARDENING_SCHEMA = "libreevolve.benchmark_hardening.v1"
BENCHMARK_HARDENING_ARTIFACT_INVENTORY_SCHEMA = "libreevolve.benchmark_hardening_artifact_inventory.v1"
BENCHMARK_EVIDENCE_SCOPE_SCHEMA = "libreevolve.benchmark_evidence_scope.v1"
BENCHMARK_HARDENING_BUNDLE_SCHEMA = "libreevolve.benchmark_hardening_bundle.v1"
BENCHMARK_LEVELS = frozenset({"smoke", "benchmark", "paper_claim"})
SHORTCUT_CATEGORIES = frozenset(
    {
        "hardcoded_cases",
        "library_delegation",
        "dead_code_counter",
        "external_io",
        "stateful_cache",
        "prompt_or_metadata_leakage",
        "invalid_artifact",
        "reference_oracle_access",
    }
)
DETECTOR_KINDS = frozenset({"static_ast", "runtime_probe", "randomized_cases", "exhaustive_cases", "artifact_validator"})
FIXTURE_STATUSES = frozenset({"passed", "failed", "not_run"})
PROTECTED_SIGNAL_KINDS = frozenset({"operation_count", "rank", "correctness", "construction_artifact", "score"})
ARTIFACT_KINDS = frozenset({"hardening_report", "negative_fixture", "detector_log", "artifact_schema"})
_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class BenchmarkHardeningIssue:
    code: str
    message: str


@dataclass(frozen=True)
class BenchmarkHardeningValidation:
    ok: bool
    benchmark_ready: bool
    benchmark_id: str | None
    level: str | None
    issues: list[BenchmarkHardeningIssue]


@dataclass(frozen=True)
class BenchmarkEvidenceScopeValidation:
    ok: bool
    benchmark_id: str | None
    hardening_ok: bool
    inventory_ok: bool
    scope_level: str | None
    hardening_level: str | None
    alphaevolve_comparable: bool
    issues: list[BenchmarkHardeningIssue]


def validate_benchmark_hardening_report(report: object | str | Path) -> BenchmarkHardeningValidation:
    """Validate anti-gaming coverage metadata for advertised benchmarks."""
    data, read_issues = _load_report(report)
    if read_issues:
        return BenchmarkHardeningValidation(False, False, None, None, read_issues)
    assert isinstance(data, dict)
    issues: list[BenchmarkHardeningIssue] = []
    if data.get("schema") != BENCHMARK_HARDENING_SCHEMA:
        issues.append(BenchmarkHardeningIssue("invalid_schema", "unsupported benchmark hardening schema"))
    benchmark_id = _id_field(data, "benchmark_id", issues)
    level = data.get("level")
    if level not in BENCHMARK_LEVELS:
        issues.append(BenchmarkHardeningIssue("invalid_level", "unsupported benchmark level"))
        level = None
    protected_signal_ids = _validate_protected_signals(data.get("protected_signals"), issues)
    categories = _validate_shortcuts(
        data.get("shortcut_threats"),
        protected_signal_ids,
        issues,
    )
    fixture_categories = _validate_negative_fixtures(data.get("negative_fixtures"), issues)
    _validate_artifacts(data.get("artifacts"), issues)
    if level in {"benchmark", "paper_claim"}:
        missing_fixtures = categories - fixture_categories
        if missing_fixtures:
            issues.append(
                BenchmarkHardeningIssue(
                    "missing_negative_fixture",
                    "benchmark-level hardening requires a passed negative fixture for every shortcut threat",
                )
            )
    benchmark_ready = not issues and level in {"benchmark", "paper_claim"}
    return BenchmarkHardeningValidation(
        ok=not issues,
        benchmark_ready=benchmark_ready,
        benchmark_id=benchmark_id,
        level=level,
        issues=issues,
    )


def validate_benchmark_evidence_scope(
    hardening_report: object | str | Path,
    scope_record: dict[str, Any],
    inventory: dict[str, Any] | None = None,
) -> BenchmarkEvidenceScopeValidation:
    """Validate benchmark hardening evidence against its declared scope."""
    hardening_data, read_issues = _load_report(hardening_report)
    issues = list(read_issues)
    if hardening_data is None:
        return BenchmarkEvidenceScopeValidation(
            ok=False,
            benchmark_id=None,
            hardening_ok=False,
            inventory_ok=False,
            scope_level=None,
            hardening_level=None,
            alphaevolve_comparable=False,
            issues=issues,
        )

    hardening_validation = validate_benchmark_hardening_report(hardening_data)
    issues.extend(hardening_validation.issues)
    benchmark_id = hardening_validation.benchmark_id
    hardening_level = hardening_validation.level
    scope_level, alphaevolve_comparable = _validate_scope_record(
        scope_record,
        benchmark_id,
        hardening_level,
        issues,
    )
    inventory_ok = True
    if inventory is not None:
        inventory_ok = _validate_hardening_inventory(
            inventory,
            hardening_data,
            benchmark_id,
            hardening_level,
            issues,
        )

    return BenchmarkEvidenceScopeValidation(
        ok=not issues,
        benchmark_id=benchmark_id,
        hardening_ok=hardening_validation.ok,
        inventory_ok=inventory_ok,
        scope_level=scope_level,
        hardening_level=hardening_level,
        alphaevolve_comparable=alphaevolve_comparable,
        issues=issues,
    )


def render_benchmark_hardening_summary(report: dict[str, Any]) -> str:
    validation = validate_benchmark_hardening_report(report)
    status = "ok" if validation.ok else "invalid"
    ready = "yes" if validation.benchmark_ready else "no"
    lines = [
        f"Benchmark hardening report: {report.get('benchmark_id', '<unknown>')}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| benchmark_ready | {ready} |",
        f"| level | {report.get('level', '<unknown>')} |",
        f"| protected_signal_count | {len(report.get('protected_signals', [])) if isinstance(report.get('protected_signals'), list) else 0} |",
        f"| shortcut_threat_count | {len(report.get('shortcut_threats', [])) if isinstance(report.get('shortcut_threats'), list) else 0} |",
        f"| negative_fixture_count | {len(report.get('negative_fixtures', [])) if isinstance(report.get('negative_fixtures'), list) else 0} |",
        f"| artifact_count | {len(report.get('artifacts', [])) if isinstance(report.get('artifacts'), list) else 0} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def write_matrix_smoke_hardening_bundle(artifact_root: str | Path) -> dict[str, Any]:
    """Emit checked hardening evidence for the shipped matrix smoke fixture."""
    root = Path(artifact_root)
    bundle_dir = root / "hardening" / "matrix_multiplication_smoke"
    fixture_dir = bundle_dir / "negative_fixtures"
    detector_log = {
        "schema": "libreevolve.matrix_smoke_detector_log.v1",
        "benchmark_id": "matrix_multiplication_smoke",
        "scope": "smoke_only_not_alphaevolve_tensor_rank_benchmark",
        "detectors": [
            {
                "category": "hardcoded_cases",
                "kind": "randomized_cases",
                "description": "Validator uses deterministic integer cases beyond the seed examples and rejects fixed-case lookup shortcuts.",
            },
            {
                "category": "library_delegation",
                "kind": "static_ast",
                "description": "Validator rejects numpy/import and library delegation paths for matmul2.",
            },
            {
                "category": "dead_code_counter",
                "kind": "static_ast",
                "description": "Validator counts multiplication operators inside matmul2 and rejects module-level dead-code counters.",
            },
        ],
    }
    fixture_payloads = {
        "hardcoded_cases": {
            "schema": "libreevolve.matrix_smoke_negative_fixture.v1",
            "category": "hardcoded_cases",
            "candidate_summary": "fixed-three-case lookup table for validator examples",
            "expected_detector": "randomized_cases",
            "expected_status": "rejected",
        },
        "library_delegation": {
            "schema": "libreevolve.matrix_smoke_negative_fixture.v1",
            "category": "library_delegation",
            "candidate_summary": "delegates multiplication to numpy or imported helpers",
            "expected_detector": "static_ast",
            "expected_status": "rejected",
        },
        "dead_code_counter": {
            "schema": "libreevolve.matrix_smoke_negative_fixture.v1",
            "category": "dead_code_counter",
            "candidate_summary": "declares fake multiplication counter outside matmul2",
            "expected_detector": "static_ast",
            "expected_status": "rejected",
        },
    }
    fixture_records = []
    for category, payload in fixture_payloads.items():
        path = fixture_dir / f"reject_{category}.json"
        info = _write_json_artifact(path, payload)
        fixture_records.append(
            {
                "id": f"reject_{category}",
                "category": category,
                "status": "passed",
                "path": _relative_artifact_path(root, path),
                "sha256": info["sha256"],
                "bytes": info["bytes"],
            }
        )
    detector_info = _write_json_artifact(bundle_dir / "detector_log.json", detector_log)
    report = {
        "schema": BENCHMARK_HARDENING_SCHEMA,
        "benchmark_id": "matrix_multiplication_smoke",
        "level": "smoke",
        "protected_signals": [
            {
                "id": "matmul_operation_count",
                "kind": "operation_count",
                "description": "Counts scalar multiplication operators in the candidate matmul2 body.",
            },
            {
                "id": "matmul_correctness",
                "kind": "correctness",
                "description": "Requires exact 2x2 matrix multiplication on validator cases.",
            },
        ],
        "shortcut_threats": [
            {
                "category": "hardcoded_cases",
                "protected_signal_ids": ["matmul_correctness"],
                "detector": {
                    "kind": "randomized_cases",
                    "description": "Use non-seed integer cases and reject fixed lookup tables.",
                },
            },
            {
                "category": "library_delegation",
                "protected_signal_ids": ["matmul_operation_count", "matmul_correctness"],
                "detector": {
                    "kind": "static_ast",
                    "description": "Reject imports and library calls that bypass candidate scalar-operation accounting.",
                },
            },
            {
                "category": "dead_code_counter",
                "protected_signal_ids": ["matmul_operation_count"],
                "detector": {
                    "kind": "static_ast",
                    "description": "Restrict multiplication counting to the matmul2 function body.",
                },
            },
        ],
        "negative_fixtures": fixture_records,
        "artifacts": [
            {
                "kind": "detector_log",
                "path": _relative_artifact_path(root, bundle_dir / "detector_log.json"),
                "sha256": detector_info["sha256"],
                "bytes": detector_info["bytes"],
            }
        ],
    }
    report_info = _write_json_artifact(bundle_dir / "report.json", report)
    inventory = benchmark_hardening_artifact_inventory(report, root)
    inventory_info = _write_json_artifact(bundle_dir / "inventory.json", inventory)
    summary = render_benchmark_hardening_summary(report)
    summary_path = bundle_dir / "summary.md"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(summary, encoding="utf-8")
    summary_raw = summary_path.read_bytes()
    scope_record = _matrix_scope_record()
    scope_validation = validate_benchmark_evidence_scope(
        report,
        scope_record,
        inventory,
    )
    scope_payload = _scope_validation_payload(scope_validation)
    scope_info = _write_json_artifact(bundle_dir / "scope_validation.json", scope_payload)
    return {
        "schema": BENCHMARK_HARDENING_BUNDLE_SCHEMA,
        "benchmark_id": "matrix_multiplication_smoke",
        "level": "smoke",
        "alphaevolve_comparable": False,
        "scope_policy": "shipped_matrix_multiplication_example_remains_smoke_only",
        "report_path": _relative_artifact_path(root, bundle_dir / "report.json"),
        "report_sha256": report_info["sha256"],
        "report_bytes": report_info["bytes"],
        "inventory_path": _relative_artifact_path(root, bundle_dir / "inventory.json"),
        "inventory_sha256": inventory_info["sha256"],
        "summary_path": _relative_artifact_path(root, summary_path),
        "summary_sha256": hashlib.sha256(summary_raw).hexdigest(),
        "scope_validation_path": _relative_artifact_path(
            root,
            bundle_dir / "scope_validation.json",
        ),
        "scope_validation_sha256": scope_info["sha256"],
        "report": report,
        "inventory": inventory,
        "scope_validation": scope_payload,
    }


def write_sorting_network_hardening_bundle(
    artifact_root: str | Path,
    problem_id: str,
) -> dict[str, Any]:
    """Emit checked hardening evidence for sorting-network benchmark candidates."""

    specs = {
        "sorting_network_8": {
            "wire_count": 8,
            "target_comparators": 19,
            "seed_comparators": 28,
        },
        "sorting_network_9": {
            "wire_count": 9,
            "target_comparators": 25,
            "seed_comparators": 36,
        },
    }
    if problem_id not in specs:
        raise ValueError("problem_id must be sorting_network_8 or sorting_network_9")
    spec = specs[problem_id]
    root = Path(artifact_root)
    bundle_dir = root / "hardening" / problem_id
    fixture_dir = bundle_dir / "negative_fixtures"
    benchmark_id = f"{problem_id}_benchmark"
    detector_log = {
        "schema": "libreevolve.sorting_network_detector_log.v1",
        "benchmark_id": benchmark_id,
        "problem_id": problem_id,
        "wire_count": spec["wire_count"],
        "zero_one_input_count": 2 ** int(spec["wire_count"]),
        "target_comparators": spec["target_comparators"],
        "detectors": [
            {
                "category": "hardcoded_cases",
                "kind": "exhaustive_cases",
                "description": "Validator checks every Boolean input, so a network that only sorts a few examples cannot pass correctness.",
            },
            {
                "category": "library_delegation",
                "kind": "static_ast",
                "description": "Validator rejects imports and direct dynamic-code helpers before running network().",
            },
            {
                "category": "invalid_artifact",
                "kind": "artifact_validator",
                "description": "Validator requires a plain list of two-integer comparator pairs with distinct in-range wires.",
            },
        ],
    }
    fixture_payloads = {
        "hardcoded_cases": {
            "schema": "libreevolve.sorting_network_negative_fixture.v1",
            "category": "hardcoded_cases",
            "candidate_summary": "network intended to satisfy selected examples but not exhaustive zero-one inputs",
            "expected_detector": "exhaustive_cases",
            "expected_status": "rejected",
        },
        "library_delegation": {
            "schema": "libreevolve.sorting_network_negative_fixture.v1",
            "category": "library_delegation",
            "candidate_summary": "candidate attempts import or dynamic helper access instead of returning a static comparator network",
            "expected_detector": "static_ast",
            "expected_status": "rejected",
        },
        "invalid_artifact": {
            "schema": "libreevolve.sorting_network_negative_fixture.v1",
            "category": "invalid_artifact",
            "candidate_summary": "candidate returns out-of-range, self-comparing, or non-integer comparator entries",
            "expected_detector": "artifact_validator",
            "expected_status": "rejected",
        },
    }
    fixture_records = []
    for category, payload in fixture_payloads.items():
        path = fixture_dir / f"reject_{category}.json"
        info = _write_json_artifact(path, payload)
        fixture_records.append(
            {
                "id": f"reject_{category}",
                "category": category,
                "status": "passed",
                "path": _relative_artifact_path(root, path),
                "sha256": info["sha256"],
                "bytes": info["bytes"],
            }
        )
    detector_info = _write_json_artifact(bundle_dir / "detector_log.json", detector_log)
    report = {
        "schema": BENCHMARK_HARDENING_SCHEMA,
        "benchmark_id": benchmark_id,
        "level": "benchmark",
        "protected_signals": [
            {
                "id": "sorting_network_correctness",
                "kind": "correctness",
                "description": "Requires the returned comparator network to sort every Boolean input under the zero-one principle.",
            },
            {
                "id": "sorting_network_comparator_count",
                "kind": "operation_count",
                "description": "Counts comparator pairs and compares them to the known target threshold.",
            },
            {
                "id": "sorting_network_candidate_artifact",
                "kind": "construction_artifact",
                "description": "Requires a safe static comparator-list artifact rather than an executable oracle or malformed payload.",
            },
        ],
        "shortcut_threats": [
            {
                "category": "hardcoded_cases",
                "protected_signal_ids": ["sorting_network_correctness"],
                "detector": {
                    "kind": "exhaustive_cases",
                    "description": "Reject partial-example networks by evaluating all Boolean inputs.",
                },
            },
            {
                "category": "library_delegation",
                "protected_signal_ids": [
                    "sorting_network_correctness",
                    "sorting_network_comparator_count",
                ],
                "detector": {
                    "kind": "static_ast",
                    "description": "Reject imports and dynamic execution helpers before calling network().",
                },
            },
            {
                "category": "invalid_artifact",
                "protected_signal_ids": ["sorting_network_candidate_artifact"],
                "detector": {
                    "kind": "artifact_validator",
                    "description": "Reject malformed comparator artifacts before scoring.",
                },
            },
        ],
        "negative_fixtures": fixture_records,
        "artifacts": [
            {
                "kind": "detector_log",
                "path": _relative_artifact_path(root, bundle_dir / "detector_log.json"),
                "sha256": detector_info["sha256"],
                "bytes": detector_info["bytes"],
            }
        ],
    }
    report_info = _write_json_artifact(bundle_dir / "report.json", report)
    inventory = benchmark_hardening_artifact_inventory(report, root)
    inventory_info = _write_json_artifact(bundle_dir / "inventory.json", inventory)
    summary = render_benchmark_hardening_summary(report)
    summary_path = bundle_dir / "summary.md"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(summary, encoding="utf-8")
    summary_raw = summary_path.read_bytes()
    scope_record = _example_scope_record(problem_id)
    scope_validation = validate_benchmark_evidence_scope(
        report,
        scope_record,
        inventory,
    )
    scope_payload = _scope_validation_payload(scope_validation)
    scope_info = _write_json_artifact(bundle_dir / "scope_validation.json", scope_payload)
    return {
        "schema": BENCHMARK_HARDENING_BUNDLE_SCHEMA,
        "benchmark_id": benchmark_id,
        "problem_id": problem_id,
        "level": "benchmark",
        "alphaevolve_comparable": False,
        "scope_policy": "sorting_network_benchmark_candidate_not_paper_comparable",
        "wire_count": spec["wire_count"],
        "target_comparators": spec["target_comparators"],
        "seed_comparators": spec["seed_comparators"],
        "report_path": _relative_artifact_path(root, bundle_dir / "report.json"),
        "report_sha256": report_info["sha256"],
        "report_bytes": report_info["bytes"],
        "inventory_path": _relative_artifact_path(root, bundle_dir / "inventory.json"),
        "inventory_sha256": inventory_info["sha256"],
        "summary_path": _relative_artifact_path(root, summary_path),
        "summary_sha256": hashlib.sha256(summary_raw).hexdigest(),
        "scope_validation_path": _relative_artifact_path(
            root,
            bundle_dir / "scope_validation.json",
        ),
        "scope_validation_sha256": scope_info["sha256"],
        "report": report,
        "inventory": inventory,
        "scope_validation": scope_payload,
    }


def benchmark_hardening_artifact_inventory(
    report: object | str | Path,
    artifact_root: str | Path,
) -> dict[str, Any]:
    """Verify negative-fixture and hardening artifact references under a root."""
    data, read_issues = _load_report(report)
    root = Path(artifact_root)
    records: list[dict[str, Any]] = []
    issues = [
        {"code": issue.code, "message": issue.message}
        for issue in read_issues
    ]
    if data is not None:
        for field in ("negative_fixtures", "artifacts"):
            values = data.get(field)
            if isinstance(values, list):
                for index, record in enumerate(values):
                    records.append(_hardening_inventory_record(record, root, field, index))
            else:
                issues.append(
                    {
                        "code": f"invalid_{field}",
                        "message": f"{field} must be a non-empty list",
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
        if record["status"] in {"invalid_record", "unsafe_path", "read_error"}
    )
    if not records and data is not None:
        issues.append(
            {
                "code": "empty_artifact_inventory",
                "message": "no negative fixture or artifact records were available to verify",
            }
        )
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return {
        "schema": BENCHMARK_HARDENING_ARTIFACT_INVENTORY_SCHEMA,
        "report_schema": data.get("schema") if isinstance(data, dict) else None,
        "benchmark_id": data.get("benchmark_id") if isinstance(data, dict) else None,
        "level": data.get("level") if isinstance(data, dict) else None,
        "artifact_root_policy": "safe_relative_report_paths_under_artifact_root",
        "artifact_root_name": root.name,
        "record_count": len(records),
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
        "records": records,
    }


def _write_json_artifact(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(payload, sort_keys=True, indent=2).encode("utf-8")
    path.write_bytes(raw)
    return {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def _relative_artifact_path(root: Path, path: Path) -> str:
    return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()


def _matrix_scope_record() -> dict[str, Any]:
    return _example_scope_record("matrix_multiplication")


def _example_scope_record(problem_id: str) -> dict[str, Any]:
    from libreevolve.problems.benchmarks.example_scope import (
        example_benchmark_scope_records,
    )

    return next(
        record
        for record in example_benchmark_scope_records()
        if record["problem_id"] == problem_id
    )


def _scope_validation_payload(
    validation: BenchmarkEvidenceScopeValidation,
) -> dict[str, Any]:
    return {
        "schema": BENCHMARK_EVIDENCE_SCOPE_SCHEMA,
        "ok": validation.ok,
        "benchmark_id": validation.benchmark_id,
        "hardening_ok": validation.hardening_ok,
        "inventory_ok": validation.inventory_ok,
        "scope_level": validation.scope_level,
        "hardening_level": validation.hardening_level,
        "alphaevolve_comparable": validation.alphaevolve_comparable,
        "issues": [
            {"code": issue.code, "message": issue.message}
            for issue in validation.issues
        ],
    }


def _load_report(report: object | str | Path) -> tuple[dict[str, Any] | None, list[BenchmarkHardeningIssue]]:
    if isinstance(report, dict):
        return dict(report), []
    if isinstance(report, (str, Path)):
        path = Path(report)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [BenchmarkHardeningIssue("read_error", f"failed to read hardening report: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [BenchmarkHardeningIssue("invalid_json", f"invalid hardening JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [BenchmarkHardeningIssue("invalid_shape", "benchmark hardening report must be a JSON object")]


def _validate_scope_record(
    scope_record: dict[str, Any],
    benchmark_id: str | None,
    hardening_level: str | None,
    issues: list[BenchmarkHardeningIssue],
) -> tuple[str | None, bool]:
    if not isinstance(scope_record, dict):
        issues.append(BenchmarkHardeningIssue("invalid_scope_record", "scope record must be an object"))
        return None, False
    if scope_record.get("schema") != "libreevolve.example_benchmark_scope.v1":
        issues.append(BenchmarkHardeningIssue("invalid_scope_schema", "unsupported benchmark scope schema"))
    scope_id = scope_record.get("problem_id")
    if not isinstance(scope_id, str) or _ID_RE.fullmatch(scope_id) is None:
        issues.append(BenchmarkHardeningIssue("invalid_scope_problem_id", "scope problem_id must be stable"))
    elif benchmark_id is not None and not benchmark_id.startswith(scope_id):
        issues.append(
            BenchmarkHardeningIssue(
                "scope_benchmark_id_mismatch",
                "hardening benchmark_id must be tied to scope problem_id",
            )
        )
    scope_level = scope_record.get("level")
    if scope_level not in BENCHMARK_LEVELS:
        issues.append(BenchmarkHardeningIssue("invalid_scope_level", "unsupported benchmark scope level"))
        scope_level = None
    alphaevolve_comparable = scope_record.get("alphaevolve_comparable")
    if not isinstance(alphaevolve_comparable, bool):
        issues.append(BenchmarkHardeningIssue("invalid_scope_comparable_flag", "scope alphaevolve_comparable must be boolean"))
        alphaevolve_comparable = False
    if scope_level == "smoke" and hardening_level in {"benchmark", "paper_claim"}:
        issues.append(
            BenchmarkHardeningIssue(
                "smoke_scope_promoted",
                "smoke-only examples cannot be promoted by hardening evidence",
            )
        )
    if hardening_level == "paper_claim" and not alphaevolve_comparable:
        issues.append(
            BenchmarkHardeningIssue(
                "paper_claim_scope_not_comparable",
                "paper-claim hardening evidence requires comparable scope",
            )
        )
    return scope_level, alphaevolve_comparable


def _validate_hardening_inventory(
    inventory: dict[str, Any],
    hardening_data: dict[str, Any],
    benchmark_id: str | None,
    hardening_level: str | None,
    issues: list[BenchmarkHardeningIssue],
) -> bool:
    if not isinstance(inventory, dict):
        issues.append(BenchmarkHardeningIssue("invalid_inventory", "inventory must be an object"))
        return False
    issue_count = len(issues)
    if inventory.get("schema") != BENCHMARK_HARDENING_ARTIFACT_INVENTORY_SCHEMA:
        issues.append(BenchmarkHardeningIssue("invalid_inventory_schema", "unsupported hardening inventory schema"))
    if inventory.get("ok") is not True:
        issues.append(BenchmarkHardeningIssue("inventory_not_ok", "hardening inventory must verify every record"))
    if benchmark_id is not None and inventory.get("benchmark_id") != benchmark_id:
        issues.append(BenchmarkHardeningIssue("inventory_benchmark_id_mismatch", "inventory benchmark_id must match hardening report"))
    if hardening_level is not None and inventory.get("level") != hardening_level:
        issues.append(BenchmarkHardeningIssue("inventory_level_mismatch", "inventory level must match hardening report"))
    if inventory.get("report_schema") != hardening_data.get("schema"):
        issues.append(BenchmarkHardeningIssue("inventory_report_schema_mismatch", "inventory report_schema must match hardening report"))
    records = inventory.get("records")
    if not isinstance(records, list) or not records:
        issues.append(BenchmarkHardeningIssue("invalid_inventory_records", "inventory records must be a non-empty list"))
        records = []
    records_payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    records_sha = inventory.get("records_sha256")
    if not isinstance(records_sha, str) or _SHA256_RE.fullmatch(records_sha) is None:
        issues.append(
            BenchmarkHardeningIssue(
                "invalid_inventory_records_hash",
                "inventory records_sha256 must be a lowercase SHA-256 hex digest",
            )
        )
    elif hashlib.sha256(records_payload.encode("utf-8")).hexdigest() != records_sha:
        issues.append(
            BenchmarkHardeningIssue(
                "inventory_records_hash_mismatch",
                "inventory records_sha256 must match inventory records",
            )
        )
    expected_counts = {
        "record_count": len(records),
        "verified_count": sum(1 for record in records if isinstance(record, dict) and record.get("status") == "verified"),
        "missing_count": sum(1 for record in records if isinstance(record, dict) and record.get("status") == "missing_file"),
        "mismatch_count": sum(
            1
            for record in records
            if isinstance(record, dict) and record.get("status") in {"hash_mismatch", "bytes_mismatch"}
        ),
        "invalid_count": sum(
            1
            for record in records
            if isinstance(record, dict) and record.get("status") in {"invalid_record", "unsafe_path", "read_error"}
        ),
    }
    for field, expected in expected_counts.items():
        value = inventory.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            issues.append(
                BenchmarkHardeningIssue(
                    f"invalid_inventory_{field}",
                    f"inventory {field} must be a non-negative integer",
                )
            )
        elif value != expected:
            issues.append(
                BenchmarkHardeningIssue(
                    f"inventory_{field}_mismatch",
                    f"inventory {field} must match inventory records",
                )
            )
    if inventory.get("verified_count") != inventory.get("record_count"):
        issues.append(
            BenchmarkHardeningIssue(
                "inventory_verified_count_mismatch",
                "inventory verified_count must equal record_count",
            )
        )
    for field in ("missing_count", "mismatch_count", "invalid_count"):
        if inventory.get(field) != 0:
            issues.append(
                BenchmarkHardeningIssue(
                    f"inventory_{field}_nonzero",
                    f"inventory {field} must be zero for benchmark evidence scope",
                )
            )
    if inventory.get("issues"):
        issues.append(BenchmarkHardeningIssue("inventory_has_issues", "inventory issues must be empty"))
    return len(issues) == issue_count


def _hardening_inventory_record(
    record: object,
    root: Path,
    section: str,
    index: int,
) -> dict[str, Any]:
    if not isinstance(record, dict):
        return {
            "section": section,
            "index": index,
            "kind": "unknown",
            "path": "",
            "status": "invalid_record",
            "issues": ["invalid_record"],
        }
    kind = record.get("kind")
    if section == "negative_fixtures":
        kind = record.get("category")
    path = record.get("path")
    expected_sha = record.get("sha256")
    expected_bytes = record.get("bytes")
    inventory: dict[str, Any] = {
        "section": section,
        "index": index,
        "kind": kind if isinstance(kind, str) else "unknown",
        "path": path if isinstance(path, str) else "",
        "expected_sha256": expected_sha if isinstance(expected_sha, str) else "",
        "expected_bytes": expected_bytes if isinstance(expected_bytes, int) and not isinstance(expected_bytes, bool) else None,
        "status": "verified",
        "issues": [],
    }
    path_obj = safe_relative_path(path)
    if path_obj is None:
        inventory["status"] = "unsafe_path"
        inventory["issues"].append("invalid_record_path")
        return inventory
    try:
        resolved_root = root.resolve()
        resolved_path = (resolved_root / path_obj).resolve(strict=False)
    except OSError:
        inventory["status"] = "unsafe_path"
        inventory["issues"].append("invalid_record_path")
        return inventory
    if not resolved_path.is_relative_to(resolved_root):
        inventory["status"] = "unsafe_path"
        inventory["issues"].append("record_path_outside_root")
        return inventory
    if not resolved_path.exists():
        inventory["status"] = "missing_file"
        inventory["issues"].append("missing_record_file")
        return inventory
    if not resolved_path.is_file():
        inventory["status"] = "unsafe_path"
        inventory["issues"].append("record_path_not_file")
        return inventory
    try:
        raw = resolved_path.read_bytes()
    except OSError:
        inventory["status"] = "read_error"
        inventory["issues"].append("record_read_error")
        return inventory
    actual_sha = hashlib.sha256(raw).hexdigest()
    actual_bytes = len(raw)
    inventory["actual_sha256"] = actual_sha
    inventory["actual_bytes"] = actual_bytes
    if not isinstance(expected_sha, str) or _SHA256_RE.fullmatch(expected_sha) is None:
        inventory["status"] = "hash_mismatch"
        inventory["issues"].append("invalid_expected_record_hash")
    elif actual_sha != expected_sha:
        inventory["status"] = "hash_mismatch"
        inventory["issues"].append("record_hash_mismatch")
    if isinstance(expected_bytes, bool) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
        if inventory["status"] == "verified":
            inventory["status"] = "bytes_mismatch"
        inventory["issues"].append("invalid_expected_record_bytes")
    elif actual_bytes != expected_bytes:
        if inventory["status"] == "verified":
            inventory["status"] = "bytes_mismatch"
        inventory["issues"].append("record_bytes_mismatch")
    return inventory


def _id_field(data: dict[str, Any], field: str, issues: list[BenchmarkHardeningIssue]) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or _ID_RE.fullmatch(value) is None:
        issues.append(BenchmarkHardeningIssue(f"invalid_{field}", f"{field} must be a stable identifier"))
        return None
    return value


def _validate_protected_signals(value: object, issues: list[BenchmarkHardeningIssue]) -> set[str]:
    signal_ids: set[str] = set()
    if not isinstance(value, list) or not value:
        issues.append(BenchmarkHardeningIssue("invalid_protected_signals", "protected_signals must be a non-empty list"))
        return signal_ids
    seen: set[str] = set()
    for signal in value:
        if not isinstance(signal, dict):
            issues.append(BenchmarkHardeningIssue("invalid_protected_signal", "protected signal must be an object"))
            continue
        signal_id = signal.get("id")
        if not isinstance(signal_id, str) or _ID_RE.fullmatch(signal_id) is None:
            issues.append(BenchmarkHardeningIssue("invalid_protected_signal_id", "protected signal id must be stable"))
        elif signal_id in seen:
            issues.append(BenchmarkHardeningIssue("duplicate_protected_signal", "protected signal ids must be unique"))
        else:
            seen.add(signal_id)
            signal_ids.add(signal_id)
        if signal.get("kind") not in PROTECTED_SIGNAL_KINDS:
            issues.append(BenchmarkHardeningIssue("invalid_protected_signal_kind", "unsupported protected signal kind"))
        if not isinstance(signal.get("description"), str) or not signal["description"].strip():
            issues.append(BenchmarkHardeningIssue("missing_protected_signal_description", "protected signal description is required"))
    return signal_ids


def _validate_shortcuts(
    value: object,
    protected_signal_ids: set[str],
    issues: list[BenchmarkHardeningIssue],
) -> set[str]:
    if not isinstance(value, list) or not value:
        issues.append(BenchmarkHardeningIssue("invalid_shortcut_threats", "shortcut_threats must be a non-empty list"))
        return set()
    categories: set[str] = set()
    for threat in value:
        if not isinstance(threat, dict):
            issues.append(BenchmarkHardeningIssue("invalid_shortcut_threat", "shortcut threat must be an object"))
            continue
        category = threat.get("category")
        if category not in SHORTCUT_CATEGORIES:
            issues.append(BenchmarkHardeningIssue("invalid_shortcut_category", "unsupported shortcut category"))
            continue
        categories.add(category)
        detector = threat.get("detector")
        if not isinstance(detector, dict):
            issues.append(BenchmarkHardeningIssue("invalid_shortcut_detector", "shortcut detector must be an object"))
            continue
        if detector.get("kind") not in DETECTOR_KINDS:
            issues.append(BenchmarkHardeningIssue("invalid_detector_kind", "unsupported shortcut detector kind"))
        if not isinstance(detector.get("description"), str) or not detector["description"].strip():
            issues.append(BenchmarkHardeningIssue("missing_detector_description", "shortcut detector description is required"))
        linked_signals = threat.get("protected_signal_ids")
        if not isinstance(linked_signals, list) or not linked_signals:
            issues.append(BenchmarkHardeningIssue("invalid_shortcut_protected_signals", "shortcut threat must list protected_signal_ids"))
        else:
            seen_signals: set[str] = set()
            for signal_id in linked_signals:
                if not isinstance(signal_id, str) or _ID_RE.fullmatch(signal_id) is None:
                    issues.append(BenchmarkHardeningIssue("invalid_shortcut_protected_signal_id", "shortcut protected signal id must be stable"))
                elif signal_id in seen_signals:
                    issues.append(BenchmarkHardeningIssue("duplicate_shortcut_protected_signal_id", "shortcut protected_signal_ids must be unique"))
                elif signal_id not in protected_signal_ids:
                    issues.append(BenchmarkHardeningIssue("unknown_shortcut_protected_signal", "shortcut protected_signal_ids must reference protected_signals"))
                else:
                    seen_signals.add(signal_id)
    return categories


def _validate_negative_fixtures(value: object, issues: list[BenchmarkHardeningIssue]) -> set[str]:
    if not isinstance(value, list) or not value:
        issues.append(BenchmarkHardeningIssue("invalid_negative_fixtures", "negative_fixtures must be a non-empty list"))
        return set()
    covered: set[str] = set()
    seen: set[str] = set()
    for fixture in value:
        if not isinstance(fixture, dict):
            issues.append(BenchmarkHardeningIssue("invalid_negative_fixture", "negative fixture must be an object"))
            continue
        fixture_id = fixture.get("id")
        if not isinstance(fixture_id, str) or _ID_RE.fullmatch(fixture_id) is None:
            issues.append(BenchmarkHardeningIssue("invalid_negative_fixture_id", "negative fixture id must be stable"))
        elif fixture_id in seen:
            issues.append(BenchmarkHardeningIssue("duplicate_negative_fixture", "negative fixture ids must be unique"))
        else:
            seen.add(fixture_id)
        category = fixture.get("category")
        if category not in SHORTCUT_CATEGORIES:
            issues.append(BenchmarkHardeningIssue("invalid_negative_fixture_category", "unsupported negative fixture category"))
        status = fixture.get("status")
        if status not in FIXTURE_STATUSES:
            issues.append(BenchmarkHardeningIssue("invalid_negative_fixture_status", "unsupported negative fixture status"))
        elif status == "passed" and category in SHORTCUT_CATEGORIES:
            covered.add(category)
        _validate_file_record(fixture, "negative_fixture", issues)
    return covered


def _validate_artifacts(value: object, issues: list[BenchmarkHardeningIssue]) -> None:
    if not isinstance(value, list) or not value:
        issues.append(BenchmarkHardeningIssue("invalid_artifacts", "artifacts must be a non-empty list"))
        return
    for artifact in value:
        if not isinstance(artifact, dict):
            issues.append(BenchmarkHardeningIssue("invalid_artifact", "artifact must be an object"))
            continue
        if artifact.get("kind") not in ARTIFACT_KINDS:
            issues.append(BenchmarkHardeningIssue("invalid_artifact_kind", "unsupported artifact kind"))
        _validate_file_record(artifact, "artifact", issues)


def _validate_file_record(record: dict[str, Any], prefix: str, issues: list[BenchmarkHardeningIssue]) -> None:
    path = record.get("path")
    path_obj = safe_relative_path(path)
    if path_obj is None:
        issues.append(BenchmarkHardeningIssue(f"invalid_{prefix}_path", f"{prefix} path must be safe and relative"))
    sha = record.get("sha256")
    if not isinstance(sha, str) or _SHA256_RE.fullmatch(sha) is None:
        issues.append(BenchmarkHardeningIssue(f"invalid_{prefix}_hash", f"{prefix} sha256 must be a lowercase SHA-256 hex digest"))
    byte_count = record.get("bytes")
    if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count <= 0:
        issues.append(BenchmarkHardeningIssue(f"invalid_{prefix}_bytes", f"{prefix} bytes must be a positive integer"))
