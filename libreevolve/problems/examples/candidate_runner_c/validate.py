from __future__ import annotations


def evaluate(code: str, workspace: str, stage: dict) -> dict[str, float | bool]:
    del code, workspace
    execution = stage.get("candidate_runner", {})
    runner = execution.get("runner", {})
    toolchain = execution.get("toolchain", {})
    if (
        execution.get("language_runner") != "c"
        or execution.get("build_system") != "c_compiler"
        or runner.get("returncode") != 0
        or runner.get("timed_out") is not False
        or toolchain.get("identity_observed") is not True
        or toolchain.get("dependency_locks_match") is not True
    ):
        return {"score": 0.0, "is_valid": False}
    raw_value = str(runner.get("stdout", "")).strip()
    try:
        value = int(raw_value)
    except ValueError:
        return {"score": 0.0, "is_valid": False}
    return {
        "score": 1.0 / (1.0 + abs(value - 42)),
        "is_valid": True,
    }
