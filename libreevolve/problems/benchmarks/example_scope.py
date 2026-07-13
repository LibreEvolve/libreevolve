from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.benchmark_hardening import BENCHMARK_LEVELS


EXAMPLE_BENCHMARK_SCOPE_SCHEMA = "libreevolve.example_benchmark_scope.v1"
_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")

_EXAMPLE_BENCHMARK_SCOPE_RECORDS: tuple[dict[str, Any], ...] = (
    {
        "schema": EXAMPLE_BENCHMARK_SCOPE_SCHEMA,
        "problem_id": "hello_world",
        "path": "libreevolve/problems/examples/hello_world",
        "level": "smoke",
        "alphaevolve_comparable": False,
        "current_role": "optimization_pressure_fixture",
        "reason": "Checks local diff/evaluator behavior on an intentionally suboptimal seed, not a paper benchmark.",
        "required_upgrades": [
            "Replace toy string objective with a paper target family.",
            "Emit benchmark reports with repeated seeds and comparable budget accounting.",
        ],
    },
    {
        "schema": EXAMPLE_BENCHMARK_SCOPE_SCHEMA,
        "problem_id": "sorting",
        "path": "libreevolve/problems/examples/sorting",
        "level": "smoke",
        "alphaevolve_comparable": False,
        "current_role": "neutral_plateau_fixture",
        "reason": "Demonstrates plateau/diversity behavior with an already-correct seed rather than target discovery.",
        "required_upgrades": [
            "Define a harder target family with optimization headroom.",
            "Add held-out/generalization checks and benchmark result artifacts.",
        ],
    },
    {
        "schema": EXAMPLE_BENCHMARK_SCOPE_SCHEMA,
        "problem_id": "sorting_network_8",
        "path": "libreevolve/problems/examples/sorting_network_8",
        "level": "benchmark",
        "alphaevolve_comparable": False,
        "current_role": "bounded_rediscovery_benchmark_candidate",
        "reason": "Provides exhaustive zero-one sorting-network validation and a known comparator target, but lacks repeated-run evidence and paper certification.",
        "required_upgrades": [
            "Record repeated-seed runs with fixed evaluator/model/budget conditions.",
            "Emit hardening reports, negative fixtures, and paper-facing certification artifacts.",
        ],
    },
    {
        "schema": EXAMPLE_BENCHMARK_SCOPE_SCHEMA,
        "problem_id": "sorting_network_9",
        "path": "libreevolve/problems/examples/sorting_network_9",
        "level": "benchmark",
        "alphaevolve_comparable": False,
        "current_role": "bounded_rediscovery_benchmark_candidate",
        "reason": "Provides exhaustive zero-one sorting-network validation for 9 inputs and a known 25-comparator target, but lacks repeated-run evidence and paper certification.",
        "required_upgrades": [
            "Record repeated-seed runs with fixed evaluator/model/budget conditions.",
            "Emit hardening reports, negative fixtures, and paper-facing certification artifacts.",
        ],
    },
    {
        "schema": EXAMPLE_BENCHMARK_SCOPE_SCHEMA,
        "problem_id": "workspace_math",
        "path": "libreevolve/problems/examples/workspace_math",
        "level": "smoke",
        "alphaevolve_comparable": False,
        "current_role": "workspace_packaging_fixture",
        "reason": "Exercises multi-file workspace evaluation and artifact handling, not AlphaEvolve-style discovery evidence.",
        "required_upgrades": [
            "Attach a benchmark target family with non-toy scoring.",
            "Record repeated-seed results and independent verification artifacts.",
        ],
    },
    {
        "schema": EXAMPLE_BENCHMARK_SCOPE_SCHEMA,
        "problem_id": "embedded_evaluate_math",
        "path": "libreevolve/problems/examples/embedded_evaluate_math",
        "level": "smoke",
        "alphaevolve_comparable": False,
        "current_role": "embedded_entrypoint_fixture",
        "reason": "Exercises candidate-owned evaluate(eval_inputs) loading without an external validate.py, not a paper benchmark.",
        "required_upgrades": [
            "Attach a non-toy target family with benchmark-scale evaluator inputs.",
            "Record repeated-seed results and path-level score attribution artifacts.",
        ],
    },
    {
        "schema": EXAMPLE_BENCHMARK_SCOPE_SCHEMA,
        "problem_id": "candidate_runner_expression",
        "path": "libreevolve/problems/examples/candidate_runner_expression",
        "level": "smoke",
        "alphaevolve_comparable": False,
        "current_role": "non_python_build_runner_contract_fixture",
        "reason": "Exercises a task-declared non-Python primary file, local build command, local runner command, generated artifact capture, and problem-owned scoring; it is not a real-language or paper benchmark.",
        "required_upgrades": [
            "Replace the expression adapter with real compiled and interpreted language toolchains plus pinned dependency manifests.",
            "Record repeated-seed benchmark results under sandboxed, replayable runner environments.",
        ],
    },
    {
        "schema": EXAMPLE_BENCHMARK_SCOPE_SCHEMA,
        "problem_id": "candidate_runner_c",
        "path": "libreevolve/problems/examples/candidate_runner_c",
        "level": "smoke",
        "alphaevolve_comparable": False,
        "current_role": "real_c_compiler_runner_contract_fixture",
        "reason": "Compiles and runs one toy C program with observed host-toolchain identity and a checked build-contract lock; it is not a codebase-scale or paper benchmark.",
        "required_upgrades": [
            "Provision a portable hermetic compiler image and enforce exact compiler/dependency pins across hosts.",
            "Replace the scalar target with a codebase-scale workload and repeated-seed benchmark evidence.",
        ],
    },
    {
        "schema": EXAMPLE_BENCHMARK_SCOPE_SCHEMA,
        "problem_id": "matrix_multiplication",
        "path": "libreevolve/problems/examples/matrix_multiplication",
        "level": "smoke",
        "alphaevolve_comparable": False,
        "current_role": "operation_counter_smoke_fixture",
        "reason": "Validates a 2x2 Python matmul function and local shortcut probes, not tensor-rank decomposition targets.",
        "required_upgrades": [
            "Connect exact tensor target suites and coefficient-domain certificates.",
            "Emit per-seed rank hit-rate reports and hardening artifacts.",
        ],
    },
    {
        "schema": EXAMPLE_BENCHMARK_SCOPE_SCHEMA,
        "problem_id": "circle_packing",
        "path": "libreevolve/problems/examples/circle_packing",
        "level": "smoke",
        "alphaevolve_comparable": False,
        "current_role": "construction_feasibility_smoke_fixture",
        "reason": "Checks one fixed 26-circle construction objective without repeated seeds, thresholds, or export artifacts.",
        "required_upgrades": [
            "Persist construction JSON/visual artifacts and target/SOTA thresholds.",
            "Run repeated-seed equal-budget comparisons for the paper target family.",
        ],
    },
)


@dataclass(frozen=True)
class ExampleBenchmarkScopeIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ExampleBenchmarkScopeValidation:
    ok: bool
    smoke_only: bool
    comparable_problem_ids: list[str]
    issues: list[ExampleBenchmarkScopeIssue]


def example_benchmark_scope_records() -> list[dict[str, Any]]:
    """Return machine-readable scope records for shipped example problems."""
    return [dict(record) for record in _EXAMPLE_BENCHMARK_SCOPE_RECORDS]


def validate_example_benchmark_scope(records: object) -> ExampleBenchmarkScopeValidation:
    """Validate shipped-example scope records before treating them as benchmark evidence."""
    issues: list[ExampleBenchmarkScopeIssue] = []
    if not isinstance(records, list) or not records:
        return ExampleBenchmarkScopeValidation(
            False,
            False,
            [],
            [ExampleBenchmarkScopeIssue("invalid_records", "scope records must be a non-empty list")],
        )

    seen: set[str] = set()
    comparable: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            issues.append(ExampleBenchmarkScopeIssue("invalid_record", "scope record must be an object"))
            continue
        if record.get("schema") != EXAMPLE_BENCHMARK_SCOPE_SCHEMA:
            issues.append(ExampleBenchmarkScopeIssue("invalid_schema", "unsupported example benchmark scope schema"))
        problem_id = _id_field(record, "problem_id", issues)
        if problem_id is not None:
            if problem_id in seen:
                issues.append(ExampleBenchmarkScopeIssue("duplicate_problem_id", "problem ids must be unique"))
            seen.add(problem_id)
        _validate_relative_path(record.get("path"), issues)
        level = record.get("level")
        if level not in BENCHMARK_LEVELS:
            issues.append(ExampleBenchmarkScopeIssue("invalid_level", "unsupported benchmark level"))
            level = None
        alphaevolve_comparable = record.get("alphaevolve_comparable")
        if not isinstance(alphaevolve_comparable, bool):
            issues.append(ExampleBenchmarkScopeIssue("invalid_comparable_flag", "alphaevolve_comparable must be boolean"))
            alphaevolve_comparable = False
        elif alphaevolve_comparable and problem_id is not None:
            comparable.append(problem_id)
        if level == "smoke" and alphaevolve_comparable:
            issues.append(ExampleBenchmarkScopeIssue("smoke_marked_comparable", "smoke examples cannot be AlphaEvolve-comparable"))
        if level == "paper_claim" and not alphaevolve_comparable:
            issues.append(ExampleBenchmarkScopeIssue("paper_claim_not_comparable", "paper-claim records must be comparable"))
        _validate_nonempty_string(record.get("current_role"), "missing_current_role", "current_role is required", issues)
        _validate_nonempty_string(record.get("reason"), "missing_reason", "reason is required", issues)
        _validate_required_upgrades(record.get("required_upgrades"), issues)

    smoke_only = not comparable and all(isinstance(record, dict) and record.get("level") == "smoke" for record in records)
    return ExampleBenchmarkScopeValidation(
        ok=not issues,
        smoke_only=smoke_only,
        comparable_problem_ids=comparable,
        issues=issues,
    )


def render_example_benchmark_scope_summary(records: list[dict[str, Any]]) -> str:
    validation = validate_example_benchmark_scope(records)
    status = "ok" if validation.ok else "invalid"
    smoke_only = "yes" if validation.smoke_only else "no"
    lines = [
        "Example benchmark scope",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| smoke_only | {smoke_only} |",
        f"| comparable_problem_count | {len(validation.comparable_problem_ids)} |",
        "",
        "| Problem | Level | AlphaEvolve comparable | Role |",
        "|---|---|---|---|",
    ]
    for record in records:
        lines.append(
            "| {problem} | {level} | {comparable} | {role} |".format(
                problem=record.get("problem_id", "<unknown>"),
                level=record.get("level", "<unknown>"),
                comparable="yes" if record.get("alphaevolve_comparable") is True else "no",
                role=record.get("current_role", "<unknown>"),
            )
        )
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _id_field(data: dict[str, Any], field: str, issues: list[ExampleBenchmarkScopeIssue]) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or _ID_RE.fullmatch(value) is None:
        issues.append(ExampleBenchmarkScopeIssue(f"invalid_{field}", f"{field} must be a stable identifier"))
        return None
    return value


def _validate_relative_path(value: object, issues: list[ExampleBenchmarkScopeIssue]) -> None:
    path = Path(value) if isinstance(value, str) else None
    if (
        path is None
        or not value
        or path.is_absolute()
        or value.startswith(("/", "\\"))
        or ".." in path.parts
    ):
        issues.append(ExampleBenchmarkScopeIssue("invalid_path", "path must be safe and relative"))


def _validate_nonempty_string(
    value: object,
    code: str,
    message: str,
    issues: list[ExampleBenchmarkScopeIssue],
) -> None:
    if not isinstance(value, str) or not value.strip():
        issues.append(ExampleBenchmarkScopeIssue(code, message))


def _validate_required_upgrades(value: object, issues: list[ExampleBenchmarkScopeIssue]) -> None:
    if not isinstance(value, list) or not value:
        issues.append(ExampleBenchmarkScopeIssue("invalid_required_upgrades", "required_upgrades must be a non-empty list"))
        return
    for item in value:
        if not isinstance(item, str) or not item.strip():
            issues.append(ExampleBenchmarkScopeIssue("invalid_required_upgrade", "required upgrade entries must be non-empty strings"))
