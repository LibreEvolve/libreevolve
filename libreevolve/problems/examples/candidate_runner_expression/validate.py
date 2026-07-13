from __future__ import annotations

import math


def evaluate(code: str, workspace: str, stage: dict) -> dict[str, float | bool]:
    del code, workspace
    execution = stage.get("candidate_runner", {})
    runner = execution.get("runner", {})
    if (
        execution.get("language_runner") != "expression"
        or execution.get("build_system") != "expression_copy"
        or runner.get("returncode") != 0
        or runner.get("timed_out") is not False
    ):
        return {"score": 0.0, "is_valid": False}
    try:
        value = float(str(runner.get("stdout", "")).strip())
    except ValueError:
        return {"score": 0.0, "is_valid": False}
    if not math.isfinite(value):
        return {"score": 0.0, "is_valid": False}
    return {
        "score": 1.0 / (1.0 + abs(value - 42.0)),
        "is_valid": True,
    }
