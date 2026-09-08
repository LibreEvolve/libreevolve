"""Data-only record-family declarations for the artifact-schema façade.

This module deliberately contains no validation, persistence, redaction, or
CLI behavior.  The façade supplies the canonical schema identifiers so that
their existing import and source anchors remain owned by ``artifact_schema``.
"""

from __future__ import annotations


def jsonl_record_families(
    *,
    history: str,
    evaluator_result: str,
    failure: str,
    archive_event: str,
    llm_call: str,
    llm_reward: str,
    prompt_history: str,
    controller_budget_event: str,
) -> dict[str, str | dict[str, str]]:
    """Return the versioned JSONL record-family contract."""

    return {
        "history.jsonl": history,
        "evaluator_results.jsonl": evaluator_result,
        "failure_history.jsonl": failure,
        "archive_events.jsonl": archive_event,
        "llm_calls.jsonl": {
            "call": llm_call,
            "reward": llm_reward,
        },
        "prompt_history.jsonl": prompt_history,
        "controller_budget_events.jsonl": controller_budget_event,
    }


def quarantine_record_families(
    *,
    history: str,
    failure: str,
    archive_event: str,
    controller_budget_event: str,
    llm_call: str,
    llm_reward: str,
    prompt_history: str,
    manifest: str,
    diagnostic: str,
) -> dict[str, dict[str, str | dict[str, str]]]:
    """Return the diagnostic stream contract for malformed records."""

    return {
        "history_invalid.jsonl": {
            "source_stream": "history.jsonl",
            "source_record_schema": history,
            "diagnostic_record_schema": diagnostic,
        },
        "failure_history_invalid.jsonl": {
            "source_stream": "failure_history.jsonl",
            "source_record_schema": failure,
            "diagnostic_record_schema": diagnostic,
        },
        "archive_events_invalid.jsonl": {
            "source_stream": "archive_events.jsonl",
            "source_record_schema": archive_event,
            "diagnostic_record_schema": diagnostic,
        },
        "controller_budget_events_invalid.jsonl": {
            "source_stream": "controller_budget_events.jsonl",
            "source_record_schema": controller_budget_event,
            "diagnostic_record_schema": diagnostic,
        },
        "llm_calls_invalid.jsonl": {
            "source_stream": "llm_calls.jsonl",
            "source_record_schema": {
                "call": llm_call,
                "reward": llm_reward,
            },
            "diagnostic_record_schema": diagnostic,
        },
        "prompt_history_invalid.jsonl": {
            "source_stream": "prompt_history.jsonl",
            "source_record_schema": prompt_history,
            "diagnostic_record_schema": diagnostic,
        },
        "manifest_invalid.jsonl": {
            "source_stream": "manifest.json",
            "source_record_schema": manifest,
            "diagnostic_record_schema": diagnostic,
        },
    }
