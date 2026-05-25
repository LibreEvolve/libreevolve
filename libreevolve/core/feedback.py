from __future__ import annotations

import json
import math
import re
from dataclasses import replace

from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.evaluator import EvaluationResult
from libreevolve.problems.loader import Problem

_MAX_FEEDBACK_FILE_CHARS = 4000
_MAX_FEEDBACK_WORKSPACE_CHARS = 12000
_MAX_FEEDBACK_DIAGNOSTIC_CHARS = 4000
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)(api[_-]?key|token|secret|password)(\s*[:=]\s*)(['\"]?)[^\s,'\"]+"
)
_SECRET_TOKEN = re.compile(r"\b(?:sk|sk-proj|ghp|gho|github_pat)_[A-Za-z0-9_\-]{12,}\b")


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
        metric_name = str(grader.get("metric", f"llm_{name}"))
        response = ""
        backend_idx = None
        try:
            prompt = _build_feedback_prompt(grader, workspace, problem, updated)
            response, backend_idx = llm.generate(prompt, role=f"feedback:{name}")
            llm_call = _last_llm_call(llm)
            parsed = parse_feedback_response(response)
            score = _feedback_score(parsed)
            discard = _feedback_discard(parsed)
        except Exception as exc:
            llm_call = _last_llm_call(llm)
            feedback_records.append(
                {
                    "name": name,
                    "metric": metric_name,
                    "error": "llm_feedback_failed",
                    "exception": exc.__class__.__name__,
                    "message": str(exc),
                    "backend_idx": backend_idx,
                    "llm_call": llm_call,
                    "raw_response": response,
                }
            )
            continue
        updated.metrics[metric_name] = score
        weight = float(grader.get("weight", 0.0))
        fitness += weight * score
        min_score = grader.get("min_score")
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
                "llm_call": llm_call,
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


def _last_llm_call(llm) -> dict | None:
    call = getattr(llm, "last_call", None)
    return dict(call) if isinstance(call, dict) else None


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
    parsed = {"feedback": stripped}
    if number:
        parsed["score"] = float(number.group(0))
    return parsed


def _feedback_score(parsed: dict) -> float:
    value = parsed.get("score")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("feedback response score must be numeric")
    score = float(value)
    if not math.isfinite(score):
        raise ValueError("feedback response score must be finite")
    return score


def _feedback_discard(parsed: dict) -> bool:
    value = parsed.get("discard", False)
    if not isinstance(value, bool):
        raise ValueError("feedback response discard must be boolean")
    return value


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
        "[WORKSPACE]\n"
        f"{_render_feedback_workspace(workspace)}\n\n"
        "[EVALUATION]\n"
        f"{_render_feedback_diagnostics(result)}\n\n"
        "[METRICS]\n"
        f"{json.dumps(result.metrics, sort_keys=True)}"
    )


def _render_feedback_workspace(workspace: CandidateWorkspace) -> str:
    rendered: list[str] = [f"Primary file: {workspace.primary_file}"]
    used = sum(len(item) for item in rendered)
    omitted = 0
    for path, content in sorted(workspace.files.items()):
        redacted = _redact_sensitive_text(content)
        body = _truncate_text(redacted, _MAX_FEEDBACK_FILE_CHARS)
        primary = " (primary)" if path == workspace.primary_file else ""
        fence = "python" if path.endswith(".py") else ""
        section = f"--- FILE {path}{primary} ---\n```{fence}\n{body}\n```"
        projected = used + len(section)
        if projected > _MAX_FEEDBACK_WORKSPACE_CHARS:
            remaining = max(0, _MAX_FEEDBACK_WORKSPACE_CHARS - used)
            if remaining > 120:
                rendered.append(_truncate_text(section, remaining))
                used += len(rendered[-1])
            omitted += 1
            continue
        rendered.append(section)
        used = projected
    if omitted:
        rendered.append(f"[omitted {omitted} file section(s) due to feedback prompt budget]")
    return "\n\n".join(rendered)


def _render_feedback_diagnostics(result: EvaluationResult) -> str:
    diagnostics = {
        "fitness": result.fitness,
        "is_valid": result.is_valid,
        "error": result.error,
        "elapsed_sec": result.elapsed_sec,
        "stdout": _truncate_text(result.stdout, 1000),
        "stderr": _truncate_text(result.stderr, 1000),
        "stages": [
            {
                "name": stage.name,
                "passed": stage.passed,
                "score": stage.score,
                "error": stage.error,
                "stdout": _truncate_text(stage.stdout, 500),
                "stderr": _truncate_text(stage.stderr, 500),
            }
            for stage in result.stages[-3:]
        ],
    }
    return _truncate_text(
        json.dumps(diagnostics, sort_keys=True, indent=2),
        _MAX_FEEDBACK_DIAGNOSTIC_CHARS,
    )


def _truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    notice = f"\n[truncated {len(text) - max_chars} chars]"
    keep = max(0, max_chars - len(notice))
    return text[:keep] + notice


def _redact_sensitive_text(text: str) -> str:
    text = _SECRET_ASSIGNMENT.sub(r"\1\2\3[REDACTED]", text)
    return _SECRET_TOKEN.sub("[REDACTED]", text)
