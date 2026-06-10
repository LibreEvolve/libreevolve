from __future__ import annotations

import hashlib
import json
import math
import re
import time
from dataclasses import replace

from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.evaluator import EvaluationResult, EvaluationStageResult
from libreevolve.core.jsonl import strict_json_dumps
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.population.program import validate_program_metrics
from libreevolve.problems.loader import Problem

_MAX_FEEDBACK_FILE_CHARS = 4000
_MAX_FEEDBACK_WORKSPACE_CHARS = 12000
_MAX_FEEDBACK_CONTEXT_CHARS = 4000
_MAX_FEEDBACK_CONTEXT_FILE_CHARS = 1500
_MAX_FEEDBACK_DIAGNOSTIC_CHARS = 4000
_MAX_FEEDBACK_ERROR_CHARS = 500
_MAX_FEEDBACK_LLM_CALL_JSON_CHARS = 4000
_MAX_FEEDBACK_LLM_CALL_ITEMS = 20
_MAX_FEEDBACK_LLM_CALL_STRING_CHARS = 500
_MAX_FEEDBACK_RAW_RESPONSE_CHARS = 1000
_MAX_FEEDBACK_STRING_CHARS = 500
_MAX_FEEDBACK_PROMPT_INSTRUCTION_CHARS = 2000
_MAX_CRITIQUE_INSTRUCTION_CHARS = 2000
_MAX_CRITIQUE_BASE_PROMPT_CHARS = 12000
_MAX_CRITIQUE_MUTATION_CHARS = 8000
_MAX_FEEDBACK_FAILURE_RETRIES = 3
_FEEDBACK_RETENTION_POLICY = "redact_bound_hash_v1"
_FEEDBACK_LABEL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
_EXPLICIT_SCORE_RE = re.compile(
    r"(?i)(?:^|[^\w])score\s*[:=]\s*(-?(?:\d+(?:\.\d*)?|\.\d+))(?![\d.])(?!\s*%)"
)
_RESERVED_FEEDBACK_METRICS = {"is_valid", "feedback_adjusted_fitness"}
_FEEDBACK_GRADER_FIELDS = {
    "name",
    "metric",
    "objective_metric",
    "weight",
    "min_score",
    "bounds",
    "direction",
    "prompt",
    "include_invalid",
    "failure_policy",
    "failure_retries",
    "failure_penalty",
    "criterion",
    "criterion_description",
    "evaluator_gap_rationale",
    "rubric",
    "feedback_intent",
    "calibration_report_id",
}
def build_critique_prompt(
    base_prompt: str,
    mutation_text: str,
    critique_prompt: str | None = None,
) -> str:
    base_prompt = _critique_prompt_text(
        base_prompt,
        "base_prompt",
        max_chars=_MAX_CRITIQUE_BASE_PROMPT_CHARS,
    )
    mutation_text = _critique_prompt_text(
        mutation_text,
        "mutation_text",
        max_chars=_MAX_CRITIQUE_MUTATION_CHARS,
    )
    instruction = _critique_instruction_text(critique_prompt) or (
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


def _critique_instruction_text(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("critique_prompt must be a string or None")
    if not value.strip():
        return None
    return _truncate_text(
        _redact_sensitive_text(value),
        _MAX_CRITIQUE_INSTRUCTION_CHARS,
    )


def _critique_prompt_text(value: object, field: str, *, max_chars: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a non-empty string")
    if not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return _truncate_text(_redact_sensitive_text(value), max_chars)


def apply_llm_feedback(
    result: EvaluationResult,
    workspace: CandidateWorkspace,
    problem: Problem,
    graders: list[dict],
    llm,
    *,
    feedback_retention_mode: str = "redacted",
) -> EvaluationResult:
    if not graders:
        return result

    updated = replace(
        result,
        metrics=dict(result.metrics),
        metadata=dict(result.metadata),
        stages=list(result.stages),
    )
    feedback_records = []
    planned_graders = []
    reserved_feedback_metrics: set[str] = set()
    for index, grader in enumerate(graders):
        try:
            normalized = _validate_feedback_grader(
                grader,
                default_name=f"feedback_{index}",
            )
            normalized = _align_feedback_objective_metric(normalized, problem)
            _validate_feedback_metric_available(
                normalized["metric"], updated.metrics, reserved_feedback_metrics
            )
            reserved_feedback_metrics.add(normalized["metric"])
        except Exception as exc:
            record = _invalid_feedback_config_record(index, exc)
            planned_graders.append(("invalid", record))
            continue
        planned_graders.append(("grader", normalized))
    if not planned_graders:
        return result

    fitness = updated.fitness
    is_valid = updated.is_valid
    ran_grader = False
    for kind, item in planned_graders:
        if kind == "invalid":
            record = item
            feedback_records.append(record)
            updated.stages.append(
                _feedback_stage_result(record, record_index=len(feedback_records) - 1)
            )
            continue
        grader = item
        name = grader["name"]
        metric_name = grader["metric"]
        weight = grader["weight"]
        min_score = grader["min_score"]
        bounds = grader["bounds"]
        direction = grader["direction"]
        failure_policy = grader["failure_policy"]
        failure_retries = grader["failure_retries"]
        failure_penalty = grader["failure_penalty"]
        if not is_valid and not grader["include_invalid"]:
            record = {
                "name": name,
                "metric": metric_name,
                "qualitative_policy": grader["qualitative_policy"],
                "error": "llm_feedback_skipped_invalid",
                "message": "candidate is invalid and llm_feedback.include_invalid is false",
                "backend_idx": None,
                "llm_call": None,
                "raw_response": "",
                "skipped": True,
                "include_invalid": False,
            }
            feedback_records.append(record)
            updated.stages.append(
                _feedback_stage_result(record, record_index=len(feedback_records) - 1)
            )
            continue
        ran_grader = True
        response = ""
        backend_idx = None
        started = time.perf_counter()
        prompt = _build_feedback_prompt(grader, workspace, problem, updated)
        attempts: list[dict] = []
        parsed = None
        score = None
        discard = False
        llm_call = None
        failure_exc = None
        feedback_success = False
        for attempt_index in range(failure_retries + 1):
            attempt_started = time.perf_counter()
            response = ""
            backend_idx = None
            try:
                response, backend_idx = llm.generate(prompt, role=f"feedback:{name}")
                llm_call = _last_llm_call(llm)
                parsed = parse_feedback_response(response)
                score = _feedback_score(parsed, bounds=bounds)
                discard = _feedback_discard(parsed)
                feedback_success = True
            except Exception as exc:
                failure_exc = exc
                score = None
                discard = False
                llm_call = _last_llm_call(llm)
                attempts.append(
                    _feedback_failure_attempt_record(
                        attempt_index=attempt_index,
                        exc=exc,
                        backend_idx=backend_idx,
                        llm_call=llm_call,
                        raw_response=response,
                        elapsed_sec=time.perf_counter() - attempt_started,
                        retention_mode=feedback_retention_mode,
                    )
                )
                continue
            break
        if not feedback_success:
            raw_response, raw_response_retention = _retained_feedback_text(
                response,
                max_chars=_MAX_FEEDBACK_RAW_RESPONSE_CHARS,
                mode=feedback_retention_mode,
            )
            policy_record = _apply_feedback_failure_policy(
                failure_policy=failure_policy,
                failure_penalty=failure_penalty,
                fitness=fitness,
                is_valid=is_valid,
            )
            fitness = policy_record["fitness"]
            is_valid = policy_record["is_valid"]
            record = {
                "name": name,
                "metric": metric_name,
                "error": "llm_feedback_failed",
                "exception": failure_exc.__class__.__name__,
                "message": _feedback_exception_text(failure_exc),
                "backend_idx": backend_idx,
                "llm_call": llm_call,
                "raw_response": raw_response,
                "raw_response_retention": raw_response_retention,
                "include_invalid": grader["include_invalid"],
                "qualitative_policy": grader["qualitative_policy"],
                "failure_policy": failure_policy,
                "failure_retries": failure_retries,
                "failure_attempts": attempts,
                "failure_delta": policy_record["failure_delta"],
                "discard": policy_record["discard"],
            }
            feedback_records.append(record)
            updated.stages.append(
                _feedback_stage_result(
                    record,
                    record_index=len(feedback_records) - 1,
                    elapsed_sec=time.perf_counter() - started,
                )
            )
            continue
        feedback_text, feedback_retention = _retained_feedback_text(
            parsed.get("feedback", ""),
            max_chars=_MAX_FEEDBACK_STRING_CHARS,
            mode=feedback_retention_mode,
        )
        raw_response, raw_response_retention = _retained_feedback_text(
            response,
            max_chars=_MAX_FEEDBACK_RAW_RESPONSE_CHARS,
            mode=feedback_retention_mode,
        )
        if attempts:
            retry_count = len(attempts)
        else:
            retry_count = 0
        normalized_score = _normalize_feedback_score(
            score,
            bounds=bounds,
            direction=direction,
        )
        scheduler_reward = _record_feedback_scheduler_reward(
            llm,
            backend_idx=backend_idx,
            llm_call=llm_call,
            reward=normalized_score,
        )
        updated.metrics[metric_name] = score
        weighted_delta = weight * normalized_score
        fitness += weighted_delta
        if min_score is not None and normalized_score < min_score:
            discard = True
        if discard:
            is_valid = False
        record = {
            "name": name,
            "metric": metric_name,
            "qualitative_policy": grader["qualitative_policy"],
            "score": score,
            "normalized_score": normalized_score,
            "score_bounds": list(bounds),
            "score_direction": direction,
            "objective_metric": grader["objective_metric"],
            "objective_metric_schema": grader.get("objective_metric_schema"),
            "weight": weight,
            "weighted_delta": weighted_delta,
            "min_score": min_score,
            "discard": discard,
            "feedback": feedback_text,
            "feedback_retention": feedback_retention,
            "backend_idx": backend_idx,
            "llm_call": llm_call,
            "raw_response": raw_response,
            "raw_response_retention": raw_response_retention,
            "include_invalid": grader["include_invalid"],
            "failure_policy": failure_policy,
            "failure_retries": failure_retries,
            "retry_attempts": retry_count,
            "scheduler_reward": scheduler_reward,
        }
        if attempts:
            record["failure_attempts"] = attempts
        feedback_records.append(record)
        updated.stages.append(
            _feedback_stage_result(
                record,
                record_index=len(feedback_records) - 1,
                elapsed_sec=time.perf_counter() - started,
            )
        )
    if ran_grader:
        updated.fitness = fitness if is_valid else min(fitness, -0.1)
        updated.is_valid = is_valid
        updated.metrics["feedback_adjusted_fitness"] = updated.fitness
        updated.metrics["is_valid"] = is_valid
    updated.metadata["llm_feedback"] = feedback_records
    if not is_valid:
        updated.error = updated.error or "llm_feedback_discard"
    return updated


def _validate_feedback_grader(grader: object, *, default_name: str) -> dict:
    if not isinstance(grader, dict):
        raise ValueError("llm_feedback grader must be a mapping")
    _validate_feedback_grader_schema(grader)
    name = _feedback_label(grader.get("name", default_name), "name")
    metric_name = _feedback_metric_label(grader.get("metric", f"llm_{name}"), "metric")
    objective_metric = grader.get("objective_metric", False)
    if not isinstance(objective_metric, bool):
        raise ValueError("llm_feedback.objective_metric must be boolean")
    weight = _feedback_probability(grader.get("weight", 0.0), "weight")
    min_score = (
        None
        if grader.get("min_score") is None
        else _feedback_probability(grader.get("min_score"), "min_score")
    )
    bounds = _feedback_score_bounds(grader.get("bounds", [0.0, 1.0]), "bounds")
    direction = _feedback_direction(grader.get("direction", "maximize"))
    include_invalid = grader.get("include_invalid", False)
    if not isinstance(include_invalid, bool):
        raise ValueError("llm_feedback.include_invalid must be boolean")
    failure_policy = grader.get("failure_policy", "ignore")
    if failure_policy not in {"ignore", "penalize", "discard"}:
        raise ValueError("llm_feedback.failure_policy must be one of ['discard', 'ignore', 'penalize']")
    failure_retries = grader.get("failure_retries", 0)
    if isinstance(failure_retries, bool) or not isinstance(failure_retries, int):
        raise ValueError("llm_feedback.failure_retries must be an integer >= 0")
    if failure_retries < 0:
        raise ValueError("llm_feedback.failure_retries must be an integer >= 0")
    if failure_retries > _MAX_FEEDBACK_FAILURE_RETRIES:
        raise ValueError(
            f"llm_feedback.failure_retries must be <= {_MAX_FEEDBACK_FAILURE_RETRIES}"
        )
    failure_penalty = (
        weight
        if grader.get("failure_penalty") is None
        else _feedback_probability(grader.get("failure_penalty"), "failure_penalty")
    )
    prompt = _feedback_prompt_instruction(grader.get("prompt"))
    feedback_intent = grader.get("feedback_intent")
    if feedback_intent is None:
        if weight > 0.0 and min_score is not None:
            feedback_intent = "score_and_discard"
        elif min_score is not None:
            feedback_intent = "discard"
        else:
            feedback_intent = "score"
    if feedback_intent not in {"score", "discard", "score_and_discard"}:
        raise ValueError(
            "llm_feedback.feedback_intent must be one of ['score', 'discard', 'score_and_discard']"
        )
    return {
        "name": name,
        "metric": metric_name,
        "objective_metric": objective_metric,
        "weight": weight,
        "min_score": min_score,
        "bounds": bounds,
        "direction": direction,
        "include_invalid": include_invalid,
        "prompt": prompt,
        "failure_policy": failure_policy,
        "failure_retries": failure_retries,
        "failure_penalty": failure_penalty,
        "bounds_configured": "bounds" in grader,
        "direction_configured": "direction" in grader,
        "qualitative_policy": _feedback_qualitative_policy(
            grader,
            name=name,
            metric=metric_name,
            objective_metric=objective_metric,
            prompt=prompt,
            feedback_intent=feedback_intent,
        ),
    }


def _align_feedback_objective_metric(grader: dict, problem: Problem) -> dict:
    if not grader["objective_metric"]:
        return grader
    metric_name = grader["metric"]
    try:
        schema_metric = problem.metric(metric_name)
    except KeyError as exc:
        raise ValueError(
            f"llm_feedback.metric {metric_name!r} must reference a declared metric "
            "when objective_metric is true"
        ) from exc
    if metric_name == problem.primary_metric:
        raise ValueError("llm_feedback.objective_metric cannot target the primary metric")
    if str(schema_metric.get("source", "evaluator")) != "feedback":
        raise ValueError(
            f"llm_feedback.metric {metric_name!r} must use source 'feedback' "
            "when objective_metric is true"
        )
    schema_bounds = problem.metric_bounds(metric_name)
    schema_direction = problem.metric_direction(metric_name)
    if grader["bounds_configured"] and tuple(grader["bounds"]) != schema_bounds:
        raise ValueError(
            f"llm_feedback.metric {metric_name!r} bounds must match problem metric bounds"
        )
    if grader["direction_configured"] and grader["direction"] != schema_direction:
        raise ValueError(
            f"llm_feedback.metric {metric_name!r} direction must match problem metric direction"
        )
    aligned = dict(grader)
    aligned["bounds"] = schema_bounds
    aligned["direction"] = schema_direction
    aligned["objective_metric_schema"] = {
        "name": metric_name,
        "bounds": [schema_bounds[0], schema_bounds[1]],
        "direction": schema_direction,
        "primary": bool(schema_metric.get("primary", False)),
        "metric_source": "feedback",
        "source": "problem_objective_schema",
    }
    return aligned


def _validate_feedback_grader_schema(grader: dict) -> None:
    non_string_keys = [key for key in grader if not isinstance(key, str)]
    if non_string_keys:
        formatted = ", ".join(sorted(repr(key) for key in non_string_keys))
        raise ValueError(f"llm_feedback grader keys must be strings; got {formatted}")
    unsupported = sorted(set(grader) - _FEEDBACK_GRADER_FIELDS)
    if unsupported:
        raise ValueError(f"llm_feedback grader has unsupported fields {unsupported}")


def _feedback_qualitative_policy(
    grader: dict,
    *,
    name: str,
    metric: str,
    objective_metric: bool,
    prompt: str | None,
    feedback_intent: str,
) -> dict:
    criterion = _feedback_label(grader.get("criterion", name), "criterion")
    description = _feedback_optional_policy_text(
        grader.get("criterion_description"),
        "criterion_description",
    )
    rationale = _feedback_optional_policy_text(
        grader.get("evaluator_gap_rationale"),
        "evaluator_gap_rationale",
    )
    rubric = _feedback_optional_policy_text(grader.get("rubric"), "rubric")
    calibration_report_id = grader.get("calibration_report_id")
    if calibration_report_id is not None:
        calibration_report_id = _feedback_label(
            calibration_report_id,
            "calibration_report_id",
        )
    required_present = {
        "criterion_description": bool(description),
        "evaluator_gap_rationale": bool(rationale),
        "rubric": bool(rubric),
        "feedback_intent": True,
        "metric_linkage": bool(metric),
    }
    return {
        "schema": "libreevolve.qualitative_feedback_policy.v1",
        "configured": any(
            key in grader
            for key in (
                "criterion",
                "criterion_description",
                "evaluator_gap_rationale",
                "rubric",
                "feedback_intent",
                "calibration_report_id",
            )
        ),
        "criterion": criterion,
        "criterion_description": description,
        "evaluator_gap_rationale": rationale,
        "rubric_sha256": _feedback_text_sha256(rubric),
        "rubric_chars": len(rubric) if rubric else 0,
        "prompt_sha256": _feedback_text_sha256(prompt),
        "prompt_chars": len(prompt) if prompt else 0,
        "feedback_intent": feedback_intent,
        "metric": metric,
        "objective_metric": objective_metric,
        "calibration_report_id": calibration_report_id,
        "required_fields_present": required_present,
        "complete_for_current_policy": all(required_present.values()),
        "prompt_feedback_linkage": "evaluation.metadata.llm_feedback",
    }


def _feedback_optional_policy_text(value: object, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"llm_feedback.{field} must be a string")
    if not value.strip():
        return None
    return _truncate_text(
        _redact_sensitive_text(value),
        _MAX_FEEDBACK_PROMPT_INSTRUCTION_CHARS,
    )


def _feedback_text_sha256(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _feedback_failure_attempt_record(
    *,
    attempt_index: int,
    exc: Exception,
    backend_idx: int | None,
    llm_call: dict | None,
    raw_response: str,
    elapsed_sec: float,
    retention_mode: str = "redacted",
) -> dict:
    raw_response, raw_response_retention = _retained_feedback_text(
        raw_response,
        max_chars=_MAX_FEEDBACK_RAW_RESPONSE_CHARS,
        mode=retention_mode,
    )
    return {
        "attempt": attempt_index,
        "error": "llm_feedback_failed",
        "exception": exc.__class__.__name__,
        "message": _feedback_exception_text(exc),
        "backend_idx": backend_idx,
        "llm_call": llm_call,
        "raw_response": raw_response,
        "raw_response_retention": raw_response_retention,
        "elapsed_sec": max(float(elapsed_sec), 0.0),
    }


def _apply_feedback_failure_policy(
    *,
    failure_policy: str,
    failure_penalty: float,
    fitness: float,
    is_valid: bool,
) -> dict:
    if failure_policy == "ignore":
        return {
            "fitness": fitness,
            "is_valid": is_valid,
            "failure_delta": 0.0,
            "discard": False,
        }
    if failure_policy == "penalize":
        penalty = float(failure_penalty)
        return {
            "fitness": fitness - penalty,
            "is_valid": is_valid,
            "failure_delta": -penalty,
            "discard": False,
        }
    if failure_policy == "discard":
        return {
            "fitness": fitness,
            "is_valid": False,
            "failure_delta": 0.0,
            "discard": True,
        }
    raise ValueError(f"unsupported llm_feedback.failure_policy {failure_policy!r}")


def _feedback_probability(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"llm_feedback.{field} must be a finite number")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"llm_feedback.{field} must be a finite number")
    if numeric < 0.0 or numeric > 1.0:
        raise ValueError(f"llm_feedback.{field} must be between 0 and 1")
    return numeric


def _feedback_score_bounds(value: object, field: str) -> tuple[float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"llm_feedback.{field} must be [lo, hi]")
    lo = _feedback_finite_number(value[0], f"{field}[0]")
    hi = _feedback_finite_number(value[1], f"{field}[1]")
    if lo >= hi:
        raise ValueError(f"llm_feedback.{field} must be strictly increasing [lo, hi]")
    return (lo, hi)


def _feedback_direction(value: object) -> str:
    if value not in {"maximize", "minimize"}:
        raise ValueError("llm_feedback.direction must be one of ['maximize', 'minimize']")
    return str(value)


def _feedback_finite_number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"llm_feedback.{field} must be a finite number")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"llm_feedback.{field} must be a finite number")
    return numeric


def _invalid_feedback_config_record(index: int, exc: Exception) -> dict:
    return {
        "grader_index": index,
        "error": "invalid_feedback_config",
        "exception": exc.__class__.__name__,
        "message": _feedback_exception_text(exc),
        "backend_idx": None,
        "llm_call": None,
        "raw_response": "",
    }


def _feedback_stage_result(
    record: dict,
    *,
    record_index: int,
    elapsed_sec: float = 0.0,
) -> EvaluationStageResult:
    raw_name = record.get("name")
    name = raw_name if isinstance(raw_name, str) and raw_name else f"feedback_{record_index}"
    raw_metric = record.get("metric")
    metric = raw_metric if isinstance(raw_metric, str) and raw_metric else None
    score = record.get("score")
    numeric_score = (
        float(score)
        if isinstance(score, (int, float)) and not isinstance(score, bool) and math.isfinite(float(score))
        else None
    )
    discard = record.get("discard") is True
    error = record.get("error")
    passed = error is None and not discard
    stage_error = str(error) if error is not None else ("llm_feedback_discard" if discard else None)
    metrics = {metric: numeric_score} if metric and numeric_score is not None else {}
    return EvaluationStageResult(
        name=f"llm_feedback:{name}",
        passed=passed,
        score=numeric_score,
        metrics=metrics,
        error=stage_error,
        elapsed_sec=max(float(elapsed_sec), 0.0),
        metadata={
            "kind": "llm_feedback",
            "record_index": record_index,
            "metric": metric,
            "backend_idx": record.get("backend_idx"),
            "discard": discard,
            "skipped": record.get("skipped") is True,
            "include_invalid": record.get("include_invalid"),
            "min_score": record.get("min_score"),
            "normalized_score": record.get("normalized_score"),
            "score_bounds": record.get("score_bounds"),
            "score_direction": record.get("score_direction"),
            "objective_metric": record.get("objective_metric") is True,
            "objective_metric_schema": record.get("objective_metric_schema"),
            "weight": record.get("weight"),
            "weighted_delta": record.get("weighted_delta"),
            "failure_policy": record.get("failure_policy"),
            "failure_retries": record.get("failure_retries"),
            "retry_attempts": record.get("retry_attempts"),
            "failure_delta": record.get("failure_delta"),
            "failure_attempt_count": len(record.get("failure_attempts") or []),
            "llm_call": record.get("llm_call"),
        },
    )


def _feedback_label(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"llm_feedback.{field} must be a manifest-safe feedback label")
    if redact_sensitive_text(value) != value:
        raise ValueError(f"llm_feedback.{field} must be a manifest-safe feedback label")
    if _FEEDBACK_LABEL_RE.fullmatch(value) is None:
        raise ValueError(f"llm_feedback.{field} must be a manifest-safe feedback label")
    return value


def _last_llm_call(llm) -> dict | None:
    call = getattr(llm, "last_call", None)
    if not isinstance(call, dict):
        return None
    diagnostics = {
        "policy": "redact_bound_strict_json",
        "redacted": False,
        "truncated_strings": 0,
        "stringified_keys": 0,
        "stringified_values": 0,
        "omitted_items": 0,
        "renamed_keys": 0,
        "max_json_chars": _MAX_FEEDBACK_LLM_CALL_JSON_CHARS,
    }
    safe = _safe_llm_call_mapping(call, diagnostics, "$", depth=0)
    json_text = strict_json_dumps(safe, sort_keys=True, separators=(",", ":"))
    if len(json_text) > _MAX_FEEDBACK_LLM_CALL_JSON_CHARS:
        return {
            "telemetry_safety": {
                **diagnostics,
                "omitted": True,
                "json_chars": len(json_text),
            },
            "preview": _truncate_text(json_text, _MAX_FEEDBACK_LLM_CALL_JSON_CHARS),
        }
    if _llm_call_diagnostics_changed(diagnostics):
        safe["telemetry_safety"] = {**diagnostics, "omitted": False, "json_chars": len(json_text)}
    strict_json_dumps(safe, sort_keys=True, separators=(",", ":"))
    return safe


def _record_feedback_scheduler_reward(
    llm: object,
    *,
    backend_idx: int | None,
    llm_call: dict | None,
    reward: float,
) -> dict:
    record = {
        "policy": "successful_feedback_normalized_score_v1",
        "applied": False,
        "reward": reward,
    }
    if (
        not isinstance(backend_idx, int)
        or isinstance(backend_idx, bool)
        or backend_idx < 0
    ):
        record["reason"] = "missing_backend_idx"
        return record
    if not isinstance(llm_call, dict):
        record["reason"] = "missing_llm_call"
        return record
    call_id = llm_call.get("id")
    if not isinstance(call_id, str) or not call_id.strip():
        record["reason"] = "missing_call_id"
        return record
    scheduler_accounting = llm_call.get("scheduler_accounting")
    if scheduler_accounting is None:
        raw_call = getattr(llm, "last_call", None)
        if isinstance(raw_call, dict) and raw_call.get("id") == call_id:
            scheduler_accounting = raw_call.get("scheduler_accounting")
    if scheduler_accounting != "rewarded":
        record["reason"] = "telemetry_only_call"
        return record
    recorder = getattr(llm, "record_reward", None)
    if not callable(recorder):
        record["reason"] = "record_reward_unavailable"
        return record
    try:
        recorder(backend_idx, reward, call_id=call_id)
    except Exception as exc:
        record["reason"] = "record_reward_failed"
        record["error_type"] = exc.__class__.__name__
        record["message"] = _feedback_exception_text(exc)
        return record
    record["applied"] = True
    record["call_id"] = call_id
    record["backend_idx"] = backend_idx
    return record


def _llm_call_diagnostics_changed(diagnostics: dict) -> bool:
    return any(
        diagnostics.get(key)
        for key in (
            "redacted",
            "truncated_strings",
            "stringified_keys",
            "stringified_values",
            "omitted_items",
            "renamed_keys",
        )
    )


def _safe_llm_call_mapping(
    mapping: dict,
    diagnostics: dict,
    path: str,
    *,
    depth: int,
) -> dict:
    rendered: dict[str, object] = {}
    counts: dict[str, int] = {}
    for index, (key, value) in enumerate(mapping.items()):
        if index >= _MAX_FEEDBACK_LLM_CALL_ITEMS:
            diagnostics["omitted_items"] += len(mapping) - index
            break
        rendered_key = _safe_llm_call_key(key, diagnostics)
        count = counts.get(rendered_key, 0)
        counts[rendered_key] = count + 1
        if count:
            diagnostics["renamed_keys"] += 1
            rendered_key = f"{rendered_key}__{count + 1}"
        rendered[rendered_key] = _safe_llm_call_value(
            value, diagnostics, f"{path}.{rendered_key}", depth=depth + 1
        )
    return rendered


def _safe_llm_call_key(key: object, diagnostics: dict) -> str:
    if not isinstance(key, str):
        diagnostics["stringified_keys"] += 1
    raw = str(key)
    redacted = _redact_sensitive_text(raw)
    if redacted != raw:
        diagnostics["redacted"] = True
    text = _truncate_text(redacted, 120)
    if text != redacted:
        diagnostics["truncated_strings"] += 1
    return text or "<empty>"


def _safe_llm_call_value(value: object, diagnostics: dict, path: str, *, depth: int) -> object:
    if depth > 20:
        diagnostics["omitted_items"] += 1
        return {"omitted": True, "reason": "max_depth"}
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        redacted = _redact_sensitive_text(value)
        if redacted != value:
            diagnostics["redacted"] = True
        text = _truncate_text(redacted, _MAX_FEEDBACK_LLM_CALL_STRING_CHARS)
        if text != redacted:
            diagnostics["truncated_strings"] += 1
        return text
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float):
        if math.isfinite(value):
            return value
        label = "nan" if math.isnan(value) else "infinity" if value > 0 else "negative_infinity"
        diagnostics["stringified_values"] += 1
        return {"non_finite": label, "value": None}
    if isinstance(value, dict):
        return _safe_llm_call_mapping(value, diagnostics, path, depth=depth)
    if isinstance(value, (list, tuple)):
        if isinstance(value, tuple):
            diagnostics["stringified_values"] += 1
        items = []
        for index, item in enumerate(value):
            if index >= _MAX_FEEDBACK_LLM_CALL_ITEMS:
                diagnostics["omitted_items"] += len(value) - index
                break
            items.append(
                _safe_llm_call_value(item, diagnostics, f"{path}[{index}]", depth=depth + 1)
            )
        return items
    diagnostics["stringified_values"] += 1
    return {
        "value_type": type(value).__name__,
        "repr": _feedback_text_value(repr(value), _MAX_FEEDBACK_LLM_CALL_STRING_CHARS),
    }


def parse_feedback_response(text: str) -> dict:
    stripped = text.strip()
    try:
        parsed = _loads_feedback_json(stripped)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", stripped, re.DOTALL)
    if match:
        try:
            parsed = _loads_feedback_json(match.group(0))
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    parsed = {"feedback": stripped}
    match = _EXPLICIT_SCORE_RE.search(stripped)
    if match:
        parsed["score"] = float(match.group(1))
    return parsed


def _loads_feedback_json(text: str) -> object:
    return json.loads(text, object_pairs_hook=_reject_duplicate_feedback_json_names)


def _reject_duplicate_feedback_json_names(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"feedback response JSON contains duplicate object name {key!r}")
        result[key] = value
    return result


def _feedback_score(parsed: dict, *, bounds: tuple[float, float]) -> float:
    value = parsed.get("score")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("feedback response score must be numeric")
    score = float(value)
    if not math.isfinite(score):
        raise ValueError("feedback response score must be finite")
    lo, hi = bounds
    if score < lo or score > hi:
        raise ValueError(
            f"feedback response score must be within configured bounds [{lo}, {hi}]"
        )
    return score


def _normalize_feedback_score(
    score: float,
    *,
    bounds: tuple[float, float],
    direction: str,
) -> float:
    lo, hi = bounds
    normalized = (score - lo) / (hi - lo)
    if direction == "minimize":
        normalized = 1.0 - normalized
    return max(0.0, min(1.0, normalized))


def _feedback_discard(parsed: dict) -> bool:
    value = parsed.get("discard", False)
    if not isinstance(value, bool):
        raise ValueError("feedback response discard must be boolean")
    return value


def _feedback_metric_label(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"llm_feedback.{field} must be a manifest-safe metric name")
    try:
        validate_program_metrics({value: 0.0})
    except ValueError as exc:
        raise ValueError(f"llm_feedback.{field} must be a manifest-safe metric name") from exc
    return value


def _validate_feedback_metric_available(
    metric_name: str, existing_metrics: dict, reserved_feedback_metrics: set[str]
) -> None:
    if metric_name in _RESERVED_FEEDBACK_METRICS:
        raise ValueError(f"llm_feedback.metric {metric_name!r} is reserved")
    if metric_name in existing_metrics or metric_name in reserved_feedback_metrics:
        raise ValueError(
            f"llm_feedback.metric {metric_name!r} conflicts with existing evaluation metric"
        )


def _feedback_prompt_instruction(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("llm_feedback.prompt must be a string")
    if not value.strip():
        return None
    return _truncate_text(
        _redact_sensitive_text(value),
        _MAX_FEEDBACK_PROMPT_INSTRUCTION_CHARS,
    )


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
        "[CONTEXT]\n"
        f"{_render_feedback_context(problem)}\n\n"
        "[WORKSPACE]\n"
        f"{_render_feedback_workspace(workspace)}\n\n"
        "[EVALUATION]\n"
        f"{_render_feedback_diagnostics(result)}\n\n"
        "[METRICS]\n"
        f"{_feedback_json_dumps(result.metrics)}"
    )


def _render_feedback_context(problem: Problem) -> str:
    context_files = getattr(problem, "context_files", {})
    if not isinstance(context_files, dict) or not context_files:
        return "(none)"
    sources = {
        source.get("path"): source
        for source in getattr(problem, "context_sources", [])
        if isinstance(source, dict)
    }
    rendered: list[str] = []
    used = 0
    omitted = 0
    for name, content in sorted(context_files.items(), key=lambda item: str(item[0])):
        path = str(name)
        header = _render_feedback_context_header(path, sources.get(path))
        body = _feedback_text_value(content, _MAX_FEEDBACK_CONTEXT_FILE_CHARS) or ""
        section = f"{header}\n{body}"
        projected = used + len(section)
        if projected > _MAX_FEEDBACK_CONTEXT_CHARS:
            remaining = max(0, _MAX_FEEDBACK_CONTEXT_CHARS - used)
            if remaining > 120:
                rendered.append(_truncate_text(section, remaining))
                used += len(rendered[-1])
            omitted += 1
            continue
        rendered.append(section)
        used = projected
    if omitted:
        rendered.append(f"[omitted {omitted} context source(s) due to feedback prompt budget]")
    return "\n\n".join(rendered) if rendered else "(none)"


def _render_feedback_context_header(name: str, source: dict | None) -> str:
    display_name = _feedback_text_value(name, 160) or "context"
    if not source:
        return f"--- CONTEXT SOURCE: {display_name} ---"
    sha = _feedback_text_value(str(source.get("sha256", ""))[:12] or "unknown", 40)
    span = f"{source.get('excerpt_start', 0)}:{source.get('excerpt_end', '?')}"
    status = _feedback_text_value(source.get("extraction_status", "unknown"), 80)
    page_reference = _format_feedback_page_reference(source)
    pages = f", pages={page_reference}" if page_reference else ""
    return (
        f"--- CONTEXT SOURCE: {display_name} "
        f"(sha256={sha}, chars={source.get('chars_original', '?')}, "
        f"excerpt={span}{pages}, status={status}) ---"
    )


def _format_feedback_page_reference(source: dict) -> str:
    span_reference = _format_feedback_page_spans(source.get("excerpt_page_spans"))
    if span_reference:
        return span_reference
    if "excerpt_pages" in source:
        return _format_feedback_page_list(source.get("excerpt_pages"))
    return _format_feedback_page_range(source.get("pages"))


def _format_feedback_page_spans(spans: object) -> str:
    if not isinstance(spans, list) or not spans:
        return ""
    parts: list[str] = []
    for span in spans:
        if not isinstance(span, dict):
            continue
        page = span.get("page")
        start = span.get("page_excerpt_start")
        end = span.get("page_excerpt_end")
        if start is None and end is None:
            start = span.get("excerpt_start")
            end = span.get("excerpt_end")
        if not isinstance(page, int):
            continue
        if isinstance(start, int) and isinstance(end, int):
            parts.append(f"{page}:{start}-{end}")
        else:
            parts.append(str(page))
    return ",".join(parts)


def _format_feedback_page_list(pages: object) -> str:
    if not isinstance(pages, list) or not pages:
        return ""
    numeric_pages = [page for page in pages if isinstance(page, int)]
    if not numeric_pages:
        return ""
    ranges: list[str] = []
    start = previous = numeric_pages[0]
    for page in numeric_pages[1:]:
        if page == previous + 1:
            previous = page
            continue
        ranges.append(_format_feedback_page_range_part(start, previous))
        start = previous = page
    ranges.append(_format_feedback_page_range_part(start, previous))
    return ",".join(ranges)


def _format_feedback_page_range(pages: object) -> str:
    if not isinstance(pages, list) or not pages:
        return ""
    numeric_pages = [page for page in pages if isinstance(page, int)]
    if not numeric_pages:
        return ""
    return _format_feedback_page_range_part(numeric_pages[0], numeric_pages[-1])


def _format_feedback_page_range_part(start: int, end: int) -> str:
    if start == end:
        return str(start)
    return f"{start}-{end}"


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
        "error": _feedback_text_value(result.error, 500),
        "elapsed_sec": result.elapsed_sec,
        "stdout": _feedback_text_value(result.stdout, 1000),
        "stderr": _feedback_text_value(result.stderr, 1000),
        "stages": [
            {
                "name": _feedback_text_value(stage.name, 200),
                "passed": stage.passed,
                "score": stage.score,
                "error": _feedback_text_value(stage.error, 500),
                "stdout": _feedback_text_value(stage.stdout, 500),
                "stderr": _feedback_text_value(stage.stderr, 500),
            }
            for stage in result.stages[-3:]
        ],
    }
    return _truncate_text(
        _feedback_json_dumps(diagnostics, indent=2),
        _MAX_FEEDBACK_DIAGNOSTIC_CHARS,
    )


def _feedback_json_dumps(value: object, **kwargs) -> str:
    return strict_json_dumps(_feedback_json_value(value), sort_keys=True, **kwargs)


def _feedback_json_value(value: object) -> object:
    if isinstance(value, dict):
        rendered: dict[str, object] = {}
        counts: dict[str, int] = {}
        for key, item in value.items():
            rendered_key = _feedback_json_key(key)
            count = counts.get(rendered_key, 0)
            counts[rendered_key] = count + 1
            if count:
                rendered_key = f"{rendered_key}__{count + 1}"
            rendered[rendered_key] = _feedback_json_value(item)
        return rendered
    if isinstance(value, list):
        return [_feedback_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [_feedback_json_value(item) for item in value]
    if isinstance(value, str):
        return _feedback_text_value(value, _MAX_FEEDBACK_STRING_CHARS)
    if isinstance(value, float):
        if math.isfinite(value):
            return value
        if math.isnan(value):
            label = "nan"
        elif value > 0:
            label = "infinity"
        else:
            label = "negative_infinity"
        return {"non_finite": label, "value": None}
    return value


def _feedback_json_key(value: object) -> str:
    return _feedback_text_value(str(value), 120)


def _feedback_text_value(value: object, max_chars: int) -> str | None:
    if value is None:
        return None
    return _truncate_text(_redact_sensitive_text(str(value)), max_chars)


def _retained_feedback_text(
    value: object,
    *,
    max_chars: int,
    mode: str = "redacted",
) -> tuple[str | None, dict]:
    raw = "" if value is None else str(value)
    raw_hash = hashlib.sha256(raw.encode("utf-8", errors="surrogatepass")).hexdigest()
    if mode == "off":
        return None, {
            "policy": "off_no_text_or_hash",
            "retention_mode": mode,
            "sha256": None,
            "chars": None,
            "stored_chars": 0,
            "max_chars": max_chars,
            "redacted": None,
            "truncated": False,
        }
    if mode == "hash_only":
        return None, {
            "policy": "hash_only_with_raw_sha256",
            "retention_mode": mode,
            "sha256": raw_hash,
            "chars": len(raw),
            "stored_chars": 0,
            "max_chars": max_chars,
            "redacted": None,
            "truncated": False,
        }
    redacted = _redact_sensitive_text(raw)
    text = redacted if mode == "full" else _truncate_text(redacted, max_chars)
    return text, {
        "policy": (
            "full_secret_redacted_text_with_raw_sha256"
            if mode == "full"
            else _FEEDBACK_RETENTION_POLICY
        ),
        "retention_mode": mode,
        "sha256": raw_hash,
        "chars": len(raw),
        "stored_chars": len(text),
        "max_chars": max_chars,
        "redacted": redacted != raw,
        "truncated": mode != "full" and text != redacted,
    }


def _truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    notice = f"\n[truncated {len(text) - max_chars} chars]"
    keep = max(0, max_chars - len(notice))
    return text[:keep] + notice


def _redact_sensitive_text(text: str) -> str:
    return redact_sensitive_text(text)


def _feedback_exception_text(exc: Exception) -> str:
    try:
        raw = str(exc)
    except Exception as format_exc:
        raw = (
            f"<exception message unavailable; __str__ raised "
            f"{format_exc.__class__.__name__}>"
        )
    return _truncate_text(_redact_sensitive_text(raw), _MAX_FEEDBACK_ERROR_CHARS)
