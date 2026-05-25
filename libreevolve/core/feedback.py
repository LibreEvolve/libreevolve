from __future__ import annotations

import json
import re
from dataclasses import replace

from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.evaluator import EvaluationResult
from libreevolve.problems.loader import Problem


def build_critique_prompt(
    base_prompt: str,
    mutation_text: str,
    critique_prompt: str | None = None,
) -> str:
    instruction = critique_prompt or (
        "Review the proposed mutation for correctness, simplicity, and fit to "
        "the task. If it should be improved, return the complete revised "
        "mutation in the same format. If it is already good, return it exactly."
    )
    return (
        f"{instruction}\n\n"
        "[ORIGINAL PROMPT]\n"
        f"{base_prompt}\n\n"
        "[PROPOSED MUTATION]\n"
        f"{mutation_text}"
    )


def apply_llm_feedback(
    result: EvaluationResult,
    workspace: CandidateWorkspace,
    problem: Problem,
    graders: list[dict],
    llm,
) -> EvaluationResult:
    if not graders:
        return result
    active_graders = (
        graders
        if result.is_valid
        else [grader for grader in graders if bool(grader.get("include_invalid", False))]
    )
    if not active_graders:
        return result

    updated = replace(
        result,
        metrics=dict(result.metrics),
        metadata=dict(result.metadata),
    )
    feedback_records = []
    fitness = updated.fitness
    is_valid = updated.is_valid
    for grader in active_graders:
        name = str(grader.get("name", f"feedback_{len(feedback_records)}"))
        prompt = _build_feedback_prompt(grader, workspace, problem, updated)
        response, backend_idx = llm.generate(prompt)
        parsed = parse_feedback_response(response)
        score = float(parsed.get("score", 0.0))
        metric_name = str(grader.get("metric", f"llm_{name}"))
        updated.metrics[metric_name] = score
        weight = float(grader.get("weight", 0.0))
        fitness += weight * score
        min_score = grader.get("min_score")
        discard = bool(parsed.get("discard", False))
        if min_score is not None and score < float(min_score):
            discard = True
        if discard:
            is_valid = False
        feedback_records.append(
            {
                "name": name,
                "metric": metric_name,
                "score": score,
                "weight": weight,
                "min_score": min_score,
                "discard": discard,
                "feedback": parsed.get("feedback", ""),
                "backend_idx": backend_idx,
                "raw_response": response,
            }
        )
    updated.fitness = fitness if is_valid else min(fitness, -0.1)
    updated.is_valid = is_valid
    updated.metrics["feedback_adjusted_fitness"] = updated.fitness
    updated.metrics["is_valid"] = is_valid
    updated.metadata["llm_feedback"] = feedback_records
    if not is_valid:
        updated.error = updated.error or "llm_feedback_discard"
    return updated


def parse_feedback_response(text: str) -> dict:
    stripped = text.strip()
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", stripped, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    number = re.search(r"-?\d+(?:\.\d+)?", stripped)
    return {
        "score": float(number.group(0)) if number else 0.0,
        "feedback": stripped,
    }


def _build_feedback_prompt(
    grader: dict,
    workspace: CandidateWorkspace,
    problem: Problem,
    result: EvaluationResult,
) -> str:
    instruction = grader.get("prompt") or (
        "Grade this candidate. Return JSON with keys: score, feedback, discard."
    )
    return (
        f"{instruction}\n\n"
        "[TASK]\n"
        f"{problem.task_description}\n\n"
        "[PRIMARY FILE]\n"
        f"{workspace.primary_file}\n\n"
        "[CODE]\n"
        f"{workspace.code}\n\n"
        "[METRICS]\n"
        f"{json.dumps(result.metrics, sort_keys=True)}"
    )
