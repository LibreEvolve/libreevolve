from __future__ import annotations

from copy import deepcopy

ARTIFACT_SCHEMA_VERSION = 1
RUN_MANIFEST_SCHEMA = "libreevolve.run_manifest.v1"
HISTORY_RECORD_SCHEMA = "libreevolve.history.program.v1"
FAILURE_RECORD_SCHEMA = "libreevolve.failure_history.v1"
ARCHIVE_EVENT_RECORD_SCHEMA = "libreevolve.archive_event.v1"
LLM_CALL_RECORD_SCHEMA = "libreevolve.llm_call.v1"
LLM_REWARD_RECORD_SCHEMA = "libreevolve.llm_reward.v1"
PROMPT_HISTORY_RECORD_SCHEMA = "libreevolve.prompt_history.v1"
PROMPT_CURRENT_BINDING_TABLE_RECORD_SCHEMA = (
    "libreevolve.prompt_current_binding_table.v1"
)
CONTROLLER_BUDGET_EVENT_RECORD_SCHEMA = "libreevolve.controller_budget_event.v1"
LEGACY_RECORD_POLICY = "missing_schema_version_accepted_as_legacy_v0"


def run_artifact_schema() -> dict:
    return {
        "name": RUN_MANIFEST_SCHEMA,
        "version": ARTIFACT_SCHEMA_VERSION,
        "legacy_record_policy": LEGACY_RECORD_POLICY,
        "jsonl_records": {
            "history.jsonl": HISTORY_RECORD_SCHEMA,
            "failure_history.jsonl": FAILURE_RECORD_SCHEMA,
            "archive_events.jsonl": ARCHIVE_EVENT_RECORD_SCHEMA,
            "llm_calls.jsonl": {
                "call": LLM_CALL_RECORD_SCHEMA,
                "reward": LLM_REWARD_RECORD_SCHEMA,
            },
            "prompt_history.jsonl": PROMPT_HISTORY_RECORD_SCHEMA,
            "prompt_current_binding_table.jsonl": (
                PROMPT_CURRENT_BINDING_TABLE_RECORD_SCHEMA
            ),
            "controller_budget_events.jsonl": CONTROLLER_BUDGET_EVENT_RECORD_SCHEMA,
        },
    }


def versioned_record(record_schema: str, record: dict) -> dict:
    result = deepcopy(record)
    result["schema_version"] = ARTIFACT_SCHEMA_VERSION
    result["record_schema"] = record_schema
    return result
