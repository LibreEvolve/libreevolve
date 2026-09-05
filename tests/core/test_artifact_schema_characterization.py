"""Characterization tests for the run-artifact schema boundary.

These tests exercise schema assembly and the readers which consume the schema.
They deliberately do not test JSONL append, fsync, locking, or torn-write
repair; those durability concerns belong to ``tests/core/test_jsonl.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
import pytest

from libreevolve.cli import cli
from libreevolve.core.artifact_schema import (
    ARCHIVE_EVENT_RECORD_SCHEMA,
    ARTIFACT_SCHEMA_VERSION,
    CONTROLLER_BUDGET_EVENT_RECORD_SCHEMA,
    DUPLICATE_WORK_CACHE_INDEX_RECORD_SCHEMA,
    EVALUATOR_RESULT_RECORD_SCHEMA,
    FAILURE_RECORD_SCHEMA,
    HISTORY_RECORD_SCHEMA,
    LEGACY_RECORD_POLICY,
    LLM_CALL_RECORD_SCHEMA,
    LLM_REWARD_RECORD_SCHEMA,
    PAPER_ARTIFACT_SUBPATH_SCHEMA,
    PROMPT_CURRENT_BINDING_TABLE_RECORD_SCHEMA,
    PROMPT_HISTORY_RECORD_SCHEMA,
    PROMPT_PRIOR_SCORE_TABLE_RECORD_SCHEMA,
    QUARANTINE_RECORD_SCHEMA,
    RUN_ARTIFACT_NAMES,
    RUN_MANIFEST_SCHEMA,
    generated_run_artifact_inventory,
    paper_artifact_subpath_paths,
    paper_artifact_subpath_schema,
    run_artifact_schema,
    validate_non_jsonl_artifact_policy_manifest,
    validate_quarantine_artifact_policy_manifest,
    validate_run_artifact_bundle_report,
    versioned_record,
)
from libreevolve.core.database import HistoryRestoreError, load_accepted_history_index
from libreevolve.core.meta_prompt import (
    PromptDatabase,
    PromptHistoryReplayError,
    PromptTemplateError,
    load_prompt_history_records,
    parse_prompt_mutation_response,
)


_VERSIONED_JSONL_FAMILIES = {
    "history.jsonl": HISTORY_RECORD_SCHEMA,
    "evaluator_results.jsonl": EVALUATOR_RESULT_RECORD_SCHEMA,
    "failure_history.jsonl": FAILURE_RECORD_SCHEMA,
    "archive_events.jsonl": ARCHIVE_EVENT_RECORD_SCHEMA,
    "llm_calls.jsonl": {
        "call": LLM_CALL_RECORD_SCHEMA,
        "reward": LLM_REWARD_RECORD_SCHEMA,
    },
    "prompt_history.jsonl": PROMPT_HISTORY_RECORD_SCHEMA,
    "prompt_current_binding_table.jsonl": PROMPT_CURRENT_BINDING_TABLE_RECORD_SCHEMA,
    "prompt_prior_score_table.jsonl": PROMPT_PRIOR_SCORE_TABLE_RECORD_SCHEMA,
    "duplicate_work_cache_index.jsonl": DUPLICATE_WORK_CACHE_INDEX_RECORD_SCHEMA,
    "controller_budget_events.jsonl": CONTROLLER_BUDGET_EVENT_RECORD_SCHEMA,
}


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _legacy_history_row(program_id: str = "legacy") -> dict:
    return {
        "id": program_id,
        "code": "x = 1\n",
        "fitness": 0.75,
        "generation": 0,
        "future_record_field": {"kept": [1, 2]},
    }


def _prompt_add_row(prompt_id: str = "legacy-prompt") -> dict:
    return {
        "event": "add",
        "program": {
            "id": prompt_id,
            "template": "Task: {task}",
            "future_program_field": {"kept": True},
        },
    }


def _valid_bundle_report() -> dict:
    return {
        "schema": "libreevolve.run_artifact_bundle_report.v1",
        "accepted_stream_count": 0,
        "accepted_streams": [],
        "quarantine_stream_count": 0,
        "quarantine_record_count": 0,
        "non_jsonl_checked_artifact_count": 0,
        "paper_artifact_emitted_path_count": 0,
        "quarantine_validation_ok": True,
        "non_jsonl_validation_ok": True,
        "paper_artifact_lifecycle_checked": False,
        "paper_artifact_validation_ok": None,
        "accepted_state_boundary": {
            "quarantine_rows_are_diagnostics": True,
            "quarantine_rows_replayed_as_state": False,
            "provider_output_replay": False,
            "pending_controller_work_replay": False,
        },
        "claim_ready": False,
        "claim_readiness": {"full_restore_replay_certification": False},
    }


def _quarantine_row(retention_mode: str) -> dict:
    retention_policy = {
        "full": "full_secret_redacted_text_with_raw_sha256",
        "redacted": "redact_then_prefix_truncate_with_sha256",
        "hash_only": "hash_only_with_raw_sha256",
        "off": "off_no_text_or_hash",
    }[retention_mode]
    retention = {
        "retention_mode": retention_mode,
        "retention_policy": retention_policy,
        "sha256": None if retention_mode == "off" else "a" * 64,
        "chars": None if retention_mode == "off" else 32,
        "stored_chars": 0 if retention_mode in {"hash_only", "off"} else 16,
        "redacted": (
            None
            if retention_mode in {"hash_only", "off"}
            else True
        ),
        "truncated": retention_mode == "redacted",
        "max_chars": 4000,
    }
    row = {
        "error": "ValueError",
        "message": "bad input [REDACTED]",
        "record_type": "dict",
        "record_repr_retention": retention,
    }
    if retention_mode in {"full", "redacted"}:
        row["record_repr"] = (
            "safe redacted snapshot...<truncated>"
            if retention_mode == "redacted"
            else "safe redacted snapshot"
        )
        row["record_repr_truncated"] = retention["truncated"]
    return row


def test_run_artifact_schema_declares_all_versioned_record_families():
    schema = run_artifact_schema()

    assert schema["name"] == RUN_MANIFEST_SCHEMA
    assert schema["version"] == ARTIFACT_SCHEMA_VERSION
    assert schema["legacy_record_policy"] == LEGACY_RECORD_POLICY
    assert schema["jsonl_records"] == _VERSIONED_JSONL_FAMILIES

    quarantine = schema["quarantine_jsonl_records"]
    assert set(quarantine) == {
        "history_invalid.jsonl",
        "failure_history_invalid.jsonl",
        "archive_events_invalid.jsonl",
        "controller_budget_events_invalid.jsonl",
        "llm_calls_invalid.jsonl",
        "prompt_history_invalid.jsonl",
        "manifest_invalid.jsonl",
    }
    for stream_name, record in quarantine.items():
        assert record["diagnostic_record_schema"] == QUARANTINE_RECORD_SCHEMA
        assert record["retention_mode_field"] == (
            "config.quarantine_snapshot_retention_mode"
        )
        assert record["source_stream"] == (
            "manifest.json"
            if stream_name == "manifest_invalid.jsonl"
            else stream_name.removesuffix("_invalid.jsonl") + ".jsonl"
        )
        assert set(record["diagnostic_fields"]) == {
            "error",
            "message",
            "record_type",
            "record_repr_retention",
            "record_repr",
            "record_repr_truncated",
            "record_repr_error",
        }

    non_jsonl = schema["non_jsonl_artifacts"]
    assert set(non_jsonl) == {
        "manifest.json",
        "task_specification.json",
        "best.py",
        "best_workspace",
        "evaluator_artifacts",
        "plugin_artifacts",
        "paper_artifacts",
    }
    assert set(_VERSIONED_JSONL_FAMILIES) | set(quarantine) | set(non_jsonl) == (
        RUN_ARTIFACT_NAMES
    )


def test_schema_factories_and_versioned_records_are_defensive():
    schema = run_artifact_schema()
    inventory = generated_run_artifact_inventory()
    paper_schema = paper_artifact_subpath_schema()
    paper_paths = paper_artifact_subpath_paths()

    schema["jsonl_records"]["history.jsonl"] = "changed"
    schema["non_jsonl_artifacts"].clear()
    inventory.clear()
    paper_schema["families"].clear()
    paper_paths.clear()

    assert run_artifact_schema()["jsonl_records"]["history.jsonl"] == (
        HISTORY_RECORD_SCHEMA
    )
    assert generated_run_artifact_inventory()
    assert paper_artifact_subpath_schema()["schema"] == PAPER_ARTIFACT_SUBPATH_SCHEMA
    assert paper_artifact_subpath_paths()

    payload = {
        "id": "candidate",
        "future_field": {"nested": [1]},
        "schema_version": 0,
        "record_schema": "legacy.v0",
    }
    record = versioned_record(HISTORY_RECORD_SCHEMA, payload)

    assert record["schema_version"] == ARTIFACT_SCHEMA_VERSION
    assert record["record_schema"] == HISTORY_RECORD_SCHEMA
    assert record["future_field"] == {"nested": [1]}
    assert record is not payload
    record["future_field"]["nested"].append(2)
    assert payload["future_field"] == {"nested": [1]}
    assert payload["schema_version"] == 0
    assert payload["record_schema"] == "legacy.v0"


def test_legacy_v0_history_restore_accepts_missing_schema_markers(tmp_path):
    history = tmp_path / "history.jsonl"
    row = _legacy_history_row()
    _write_jsonl(history, [row])

    restored = load_accepted_history_index(history)

    assert restored["legacy"]["id"] == "legacy"
    assert restored["legacy"]["future_record_field"] == {"kept": [1, 2]}
    assert "schema_version" not in restored["legacy"]
    assert "record_schema" not in restored["legacy"]
    restored["legacy"]["future_record_field"]["kept"].append(3)
    assert row["future_record_field"] == {"kept": [1, 2]}


def test_legacy_v0_prompt_artifact_restores_without_markers(tmp_path):
    history = tmp_path / "prompt_history.jsonl"
    row = _prompt_add_row()
    _write_jsonl(history, [row])

    records = load_prompt_history_records(history)
    database = PromptDatabase(tmp_path, templates=["ignored {task}"])

    assert records[0]["event"] == "add"
    assert records[0]["program"]["future_program_field"] == {"kept": True}
    assert "schema_version" not in records[0]
    assert "record_schema" not in records[0]
    [program] = database.all()
    assert program.id == "legacy-prompt"
    assert program.template == "Task: {task}"


@pytest.mark.parametrize(
    ("markers", "expected_fragment"),
    [
        (
            {"schema_version": 99, "record_schema": HISTORY_RECORD_SCHEMA},
            "unsupported schema_version 99",
        ),
        (
            {"schema_version": ARTIFACT_SCHEMA_VERSION, "record_schema": "future.v1"},
            "unsupported record_schema 'future.v1'",
        ),
        (
            {"schema_version": ARTIFACT_SCHEMA_VERSION},
            "unsupported record_schema None",
        ),
        (
            {"record_schema": HISTORY_RECORD_SCHEMA},
            "unsupported schema_version None",
        ),
    ],
)
def test_history_restore_reports_malformed_marker_taxonomy(
    tmp_path,
    markers,
    expected_fragment,
):
    history = tmp_path / "history.jsonl"
    row = _legacy_history_row()
    row.update(markers)
    _write_jsonl(history, [row])

    with pytest.raises(HistoryRestoreError) as raised:
        load_accepted_history_index(history)

    message = str(raised.value)
    assert "Malformed history.jsonl at line 1" in message
    assert expected_fragment in message


@pytest.mark.parametrize(
    ("markers", "expected_fragment"),
    [
        (
            {"schema_version": 99, "record_schema": PROMPT_HISTORY_RECORD_SCHEMA},
            "unsupported schema_version 99",
        ),
        (
            {"schema_version": ARTIFACT_SCHEMA_VERSION, "record_schema": "future.v1"},
            "unsupported record_schema 'future.v1'",
        ),
        (
            {"schema_version": ARTIFACT_SCHEMA_VERSION},
            "unsupported record_schema None",
        ),
        (
            {"record_schema": PROMPT_HISTORY_RECORD_SCHEMA},
            "unsupported schema_version None",
        ),
    ],
)
def test_prompt_restore_reports_malformed_marker_taxonomy(
    tmp_path,
    markers,
    expected_fragment,
):
    history = tmp_path / "prompt_history.jsonl"
    row = _prompt_add_row()
    row.update(markers)
    _write_jsonl(history, [row])

    with pytest.raises(PromptHistoryReplayError) as raised:
        load_prompt_history_records(history)

    message = str(raised.value)
    assert "Malformed prompt_history.jsonl at line 1" in message
    assert expected_fragment in message


def test_bundle_schema_validator_has_stable_malformed_marker_error_codes():
    report = _valid_bundle_report()
    report.update(
        {
            "schema": "future.bundle.v2",
            "accepted_stream_count": "zero",
            "claim_ready": True,
        }
    )
    report["accepted_state_boundary"]["provider_output_replay"] = True
    report["claim_readiness"]["full_restore_replay_certification"] = True

    validation = validate_run_artifact_bundle_report(report)
    codes = {issue["code"] for issue in validation["issues"]}

    assert validation["ok"] is False
    assert {
        "invalid_schema",
        "invalid_accepted_stream_count",
        "provider_output_replay_overclaim",
        "claim_ready_overclaim",
        "full_replay_certification_overclaim",
    } <= codes


def test_unknown_fields_are_forward_compatible_for_bundle_records():
    report = _valid_bundle_report()
    report["future_field"] = {"schema": "future.v2", "value": [1, 2, 3]}

    validation = validate_run_artifact_bundle_report(report)

    assert validation == {
        "schema": "libreevolve.run_artifact_bundle_report_validation.v1",
        "ok": True,
        "issues": [],
    }


def test_unknown_declared_non_jsonl_artifacts_are_schema_drift():
    schema = run_artifact_schema()
    schema["non_jsonl_artifacts"]["future-artifact.bin"] = {
        "path": "future-artifact.bin",
        "kind": "file",
    }
    manifest = {"artifact_schema": schema, "runtime": {"artifacts": {}}}

    validation = validate_non_jsonl_artifact_policy_manifest(manifest)
    codes = {issue["code"] for issue in validation["issues"]}

    assert validation["ok"] is False
    assert "non_jsonl_artifact_schema_drift" in codes


def test_quarantine_schema_declares_redacted_diagnostic_error_contract():
    schema = run_artifact_schema()["quarantine_jsonl_records"]

    for record in schema.values():
        assert record["diagnostic_record_schema"] == QUARANTINE_RECORD_SCHEMA
        assert record["diagnostic_fields"]["error"] == "exception class name"
        assert record["diagnostic_fields"]["message"] == (
            "bounded redacted serialization or repair diagnostic"
        )
        assert record["diagnostic_fields"]["record_repr_retention"] == (
            "redacted|hash_only|off"
        )
        assert record["lifecycle_status"] == "optional_diagnostic_lifecycle_managed"


@pytest.mark.parametrize("retention_mode", ["full", "redacted", "hash_only", "off"])
def test_quarantine_schema_validator_accepts_each_retention_shape(
    tmp_path,
    retention_mode,
):
    stream = tmp_path / "history_invalid.jsonl"
    _write_jsonl(stream, [_quarantine_row(retention_mode)])
    manifest = {"artifact_schema": run_artifact_schema()}

    validation = validate_quarantine_artifact_policy_manifest(
        manifest,
        run_dir=tmp_path,
    )

    assert validation["ok"] is True
    assert validation["checked_stream_count"] == 1
    assert validation["record_count"] == 1
    assert validation["present_streams"] == ["history_invalid.jsonl"]


def test_quarantine_schema_validator_classifies_malformed_retention_rows(tmp_path):
    stream = tmp_path / "history_invalid.jsonl"
    malformed = _quarantine_row("hash_only")
    malformed["record_repr"] = "must not be retained"
    _write_jsonl(stream, [malformed])

    validation = validate_quarantine_artifact_policy_manifest(
        {"artifact_schema": run_artifact_schema()},
        run_dir=tmp_path,
    )

    assert validation["ok"] is False
    assert validation["issues"][0]["code"] == "invalid_quarantine_stream_rows"
    assert "record_repr is not allowed" in validation["issues"][0]["message"]


def test_cli_show_round_trips_a_versioned_history_artifact(tmp_path):
    row = versioned_record(
        HISTORY_RECORD_SCHEMA,
        {
            "id": "current",
            "code": "answer = 2\n",
            "fitness": 0.9,
            "generation": 1,
            "metadata": {
                "archive_admission": {
                    "admitted": True,
                    "selection_score": 0.9,
                }
            },
            "metrics": {"score": 0.9, "is_valid": True},
            "evaluation": {"is_valid": True},
        },
    )
    _write_jsonl(tmp_path / "history.jsonl", [row])

    result = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert "Selection:      archive-retained valid" in result.output
    assert "answer = 2" in result.output


def test_meta_prompt_round_trip_preserves_v1_artifact_and_restore_state(tmp_path):
    database = PromptDatabase(tmp_path, templates=["Task: {task}"])
    selected = database.select()
    database.record_result(selected.id, 0.75, metadata={"source": "characterization"})

    history_path = tmp_path / "prompt_history.jsonl"
    rows = [json.loads(line) for line in history_path.read_text().splitlines()]
    restored_rows = load_prompt_history_records(history_path)
    restored = PromptDatabase(tmp_path, templates=["ignored {task}"])
    [program] = restored.all()

    assert all(row["schema_version"] == ARTIFACT_SCHEMA_VERSION for row in rows)
    assert all(row["record_schema"] == PROMPT_HISTORY_RECORD_SCHEMA for row in rows)
    assert restored_rows == rows
    assert program.id == selected.id
    assert program.uses == 1
    assert program.reward_sum == pytest.approx(0.75)
    assert program.metadata["source"] == "characterization"


def test_meta_prompt_mutation_artifact_rejects_unknown_json_fields():
    response = json.dumps(
        {
            "schema": "libreevolve.prompt_mutation_response.v1",
            "template": "Task: {task}",
            "future_field": "not part of v1",
        }
    )

    with pytest.raises(PromptTemplateError, match="unsupported fields"):
        parse_prompt_mutation_response(response)
