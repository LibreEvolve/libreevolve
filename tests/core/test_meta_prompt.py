import json
import hashlib
import math
import tempfile
from pathlib import Path

import pytest

from libreevolve.core.artifact_schema import (
    ARTIFACT_SCHEMA_VERSION,
    PROMPT_HISTORY_RECORD_SCHEMA,
)
from libreevolve.core.jsonl import StrictJsonlError
from libreevolve.core.meta_prompt import (
    PromptDatabase,
    PromptHistoryReplayError,
    PromptProgram,
    load_prompt_history_records,
    parse_prompt_mutation_response,
    validate_prompt_program,
)
from libreevolve.core.prompt import DEFAULT_TEMPLATE, PromptTemplateError, prompt_template_fields


def _program_by_id(db: PromptDatabase, prompt_id: str) -> PromptProgram:
    return next(program for program in db.all() if program.id == prompt_id)


def test_load_prompt_history_records_rejects_duplicate_json_object_names(tmp_path):
    history = tmp_path / "prompt_history.jsonl"
    history.write_text(
        '{"event":"add","program":{"id":"p1","id":"p2"}}\n',
        encoding="utf-8",
    )

    with pytest.raises(
        PromptHistoryReplayError,
        match="Malformed prompt_history.jsonl at line 1: duplicate JSON object name 'id'",
    ):
        load_prompt_history_records(history)


def test_load_prompt_history_records_accepts_current_schema_rows(tmp_path):
    history = tmp_path / "prompt_history.jsonl"
    history.write_text(
        json.dumps(
            {
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "record_schema": PROMPT_HISTORY_RECORD_SCHEMA,
                "event": "add",
                "program": {"id": "p1", "template": "{task}"},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    records = load_prompt_history_records(history)

    assert records[0]["record_schema"] == PROMPT_HISTORY_RECORD_SCHEMA
    records[0]["program"]["id"] = "mutated"
    assert load_prompt_history_records(history)[0]["program"]["id"] == "p1"


def test_prompt_database_strict_seed_policy_rejects_minimal_template(tmp_path):
    with pytest.raises(PromptTemplateError, match="missing AlphaEvolve prompt channels"):
        PromptDatabase(
            tmp_path,
            templates=["Task: {task}"],
            seed_semantic_policy="alphaevolve",
        )


def test_prompt_database_compatibility_seed_policy_accepts_minimal_template(tmp_path):
    db = PromptDatabase(
        tmp_path,
        templates=["Task: {task}"],
        seed_semantic_policy="compatibility",
    )

    assert db.all()[0].template == "Task: {task}"


def test_prompt_database_strict_seed_policy_accepts_default_template(tmp_path):
    db = PromptDatabase(
        tmp_path,
        templates=[DEFAULT_TEMPLATE],
        seed_semantic_policy="alphaevolve",
    )

    assert db.all()[0].template == DEFAULT_TEMPLATE


def test_prompt_database_restores_existing_prompt_history_without_appending_seed(tmp_path):
    db = PromptDatabase(tmp_path, templates=["a {task}"])
    program = db.select()
    db.record_result(program.id, 0.75, metadata={"source": "score"})
    history = tmp_path / "prompt_history.jsonl"
    original_history = history.read_text(encoding="utf-8")

    restored = PromptDatabase(tmp_path, templates=["ignored {task}"])
    restored_program = _program_by_id(restored, program.id)

    assert restored_program.uses == 1
    assert restored_program.reward_sum == 0.75
    assert restored_program.metadata["source"] == "score"
    assert restored.select().id == program.id
    assert history.read_text(encoding="utf-8") == original_history


def test_prompt_database_persists_and_restores_context_policy(tmp_path):
    db = PromptDatabase(tmp_path, templates=["a {task}"])
    parent = db.select()

    child = db.mutate(
        parent.id,
        "b {task}",
        generation=2,
        context_policy={
            "disabled_sections": ["context", "recent_failures"],
            "section_priorities": {"extra_context": 2},
            "mutation_instruction_include_example": False,
            "proposal_metadata_enabled": True,
            "inspiration_strategy": "metric",
            "inspiration_required_metric": "latency",
            "inspiration_excluded_metrics": ["debug_score"],
            "inspiration_fitness_threshold": {"min": 0.25},
            "inspiration_metric_thresholds": {"latency": {"max": 0.5}},
            "inspiration_metric_ranking": {
                "metric": "latency",
                "direction": "minimize",
            },
            "feedback_sections": ["stage_summary"],
            "feedback_section_order": ["llm_grader_feedback", "stage_summary"],
            "feedback_section_max_chars_by_name": {"stage_summary": 120},
            "llm_feedback_fields": ["name", "feedback"],
            "llm_feedback_max_chars_by_field": {"feedback": 100},
            "proposal_fields": ["idea", "hypothesis"],
            "proposal_max_chars_by_field": {"idea": 90},
            "stage_summary_fields": ["name", "score"],
            "stage_summary_max_chars_by_field": {"name": 80},
            "execution_output_fields": ["stderr", "error"],
            "execution_output_max_chars_by_field": {"stderr": 120, "error": 80},
            "sample_retry_fields": ["status", "error"],
            "sample_retry_max_chars_by_field": {"error": 90},
            "program_output_fields": ["source", "sha256"],
            "program_output_max_chars_by_field": {"source": 30},
            "validator_artifact_fields": ["path", "sha256"],
            "validator_artifact_max_chars_by_field": {"path": 80},
            "validator_artifact_content_fields": ["status", "content"],
            "validator_artifact_content_mode": "bounded_file",
            "validator_artifact_content_max_bytes": 512,
            "validator_artifact_content_max_chars": 200,
            "validator_skipped_artifact_fields": ["reason", "sha256"],
            "validator_skipped_artifact_max_chars_by_field": {"reason": 40},
            "validator_diagnostic_groups": ["syntax_errors", "metadata_summary"],
            "validator_metadata_keys": ["score_detail"],
            "validator_metadata_limit": 1,
            "validator_metadata_max_chars_by_key": {"score_detail": 80},
            "evaluator_path_fields": ["validate_path", "validate_path_scope"],
            "evaluator_path_max_chars_by_field": {"validate_path": 80},
            "evaluator_dependency_fields": ["policy", "file_paths"],
            "evaluator_dependency_max_chars_by_field": {"file_paths": 120},
            "evaluator_stage_fields": ["name", "validate_path"],
            "evaluator_stage_max_chars_by_field": {"validate_path": 100},
            "evaluator_workspace_fields": ["primary_file", "file_count"],
            "evaluator_workspace_max_chars_by_field": {"primary_file": 80},
            "syntax_error_fields": ["path", "message"],
            "syntax_error_max_chars_by_field": {"message": 80},
            "metric_bound_fields": ["metric", "value"],
            "metric_bound_max_chars_by_field": {"value": 40},
            "configured_stage_check_fields": ["name", "threshold_passed"],
            "configured_stage_check_max_chars_by_field": {"name": 60},
            "stage_metric_threshold_fields": ["metric", "passed"],
            "stage_metric_threshold_max_chars_by_field": {"metric": 40},
            "artifact_output_check_fields": ["type", "reason"],
            "artifact_output_check_max_chars_by_field": {"reason": 50},
            "malformed_metric_fields": ["reason"],
            "malformed_metric_max_chars_by_field": {"reason": 50},
            "materialization_error_fields": ["message"],
            "materialization_error_max_chars_by_field": {"message": 70},
            "metric_aggregation_fields": ["metric_aggregation"],
            "metric_aggregation_max_chars_by_field": {"metric_aggregation": 90},
            "synthetic_metric_fields": ["policy", "penalty"],
            "synthetic_metric_max_chars_by_field": {"policy": 50},
            "execution_diagnostic_groups": ["stdin", "diagnostic_output"],
            "validator_boundary_fields": ["policy", "resource_limits"],
            "validator_boundary_max_chars_by_field": {"policy": 64},
            "validator_budget_fields": ["policy", "exhausted"],
            "validator_budget_max_chars_by_field": {"policy": 44},
            "validator_env_fields": ["policy", "provided_keys"],
            "validator_env_max_chars_by_field": {"provided_keys": 120},
            "validator_resource_limit_fields": [
                "wall_clock_timeout",
                "process_count",
            ],
            "validator_resource_limit_max_chars_by_field": {"memory": 48},
            "validator_stdin_fields": ["policy", "sha256"],
            "validator_stdin_max_chars_by_field": {"source": 72},
            "diagnostic_output_fields": ["encoding", "redacted"],
            "diagnostic_output_max_chars_by_field": {"encoding": 60},
            "timeout_cleanup_fields": ["method", "status"],
            "timeout_cleanup_max_chars_by_field": {"error": 84},
            "prompt_format_weights": {"tone": [2.0, 1.0]},
            "context_source_paths": ["docs/a.md"],
            "context_source_required_terms": ["matrix"],
            "context_source_excluded_terms": ["debug"],
            "context_source_ranking_terms": ["sorting"],
            "context_source_limit": 1,
            "context_source_max_chars": 400,
            "context_source_truncation": "head_tail",
            "context_source_order_policy": "task_term_ranked",
            "recent_failure_limit": 2,
            "recent_failure_selection_policy": "lowest_score",
            "recent_failure_required_errors": ["syntax_error"],
            "recent_failure_excluded_errors": ["timeout"],
            "recent_failure_required_changed_files": ["main.py"],
            "recent_failure_excluded_changed_files": ["scratch.py"],
            "recent_failure_required_stage_names": ["quick"],
            "recent_failure_excluded_stage_names": ["slow"],
            "recent_failure_required_terms": ["matrix"],
            "recent_failure_excluded_terms": ["debug"],
            "recent_failure_repetition_threshold": {"min": 2},
            "recent_failure_score_threshold": {"max": -0.1},
            "recent_failure_max_chars_by_field": {"mutation": 80},
            "inspiration_limit": 1,
            "inspiration_sample_count": 2,
            "extra_context_max_chars": 1200,
            "plugin_context_excluded_labels": ["BlockedContextPlugin"],
            "plugin_context_required_terms": ["matrix"],
            "plugin_context_excluded_terms": ["debug"],
            "plugin_context_ranking_terms": ["matrix"],
            "plugin_context_limit": 1,
            "plugin_context_max_chars": 256,
        },
    )
    restored = PromptDatabase(tmp_path)
    restored_child = _program_by_id(restored, child.id)

    assert restored_child.context_policy == {
        "schema": "libreevolve.prompt_context_policy.v1",
        "disabled_sections": ["context", "recent_failures"],
        "section_priorities": {"extra_context": 2},
        "mutation_instruction_variant": "default",
        "mutation_instruction_include_example": False,
        "proposal_metadata_enabled": True,
        "parent_code_paths": [],
        "parent_code_required_terms": [],
        "parent_code_excluded_terms": [],
        "parent_code_ranking_terms": [],
        "parent_code_order_policy": "path_order",
        "parent_code_limit": None,
        "parent_code_max_chars_by_path": {},
        "parent_code_max_chars": None,
        "parent_code_truncation": "head",
        "parent_metric_names": None,
        "parent_metrics_max_chars_by_name": {},
        "inspiration_strategy": "metric",
        "inspiration_required_metric": "latency",
        "inspiration_excluded_metrics": ["debug_score"],
        "inspiration_fitness_threshold": {"min": 0.25, "max": None},
        "inspiration_metric_thresholds": {"latency": {"min": None, "max": 0.5}},
        "inspiration_metric_ranking": {
            "metric": "latency",
            "direction": "minimize",
        },
        "feedback_sections": ["stage_summary"],
        "feedback_section_order": [
            "llm_grader_feedback",
            "stage_summary",
            "proposal",
            "execution_output",
            "sample_retry_diagnostics",
            "validator_artifacts",
            "validator_diagnostics",
            "program_outputs",
        ],
        "feedback_section_max_chars_by_name": {"stage_summary": 120},
        "llm_feedback_fields": ["name", "feedback"],
        "llm_feedback_max_chars_by_field": {"feedback": 100},
        "proposal_fields": ["idea", "hypothesis"],
        "proposal_max_chars_by_field": {"idea": 90},
        "stage_summary_fields": ["name", "score"],
        "stage_summary_max_chars_by_field": {"name": 80},
        "execution_output_fields": ["stderr", "error"],
        "execution_output_max_chars_by_field": {"stderr": 120, "error": 80},
        "sample_retry_fields": ["status", "error"],
        "sample_retry_max_chars_by_field": {"error": 90},
        "program_output_fields": ["source", "sha256"],
        "program_output_max_chars_by_field": {"source": 30},
        "validator_artifact_fields": ["path", "sha256"],
        "validator_artifact_max_chars_by_field": {"path": 80},
        "validator_artifact_content_fields": ["status", "content"],
        "validator_artifact_content_mode": "bounded_file",
        "validator_artifact_content_max_bytes": 512,
        "validator_artifact_content_max_chars": 200,
        "validator_skipped_artifact_fields": ["reason", "sha256"],
        "validator_skipped_artifact_max_chars_by_field": {"reason": 40},
        "validator_diagnostic_groups": ["syntax_errors", "metadata_summary"],
        "validator_metadata_keys": ["score_detail"],
        "validator_metadata_limit": 1,
        "validator_metadata_max_chars_by_key": {"score_detail": 80},
        "evaluator_path_fields": ["validate_path", "validate_path_scope"],
        "evaluator_path_max_chars_by_field": {"validate_path": 80},
        "evaluator_dependency_fields": ["policy", "file_paths"],
        "evaluator_dependency_max_chars_by_field": {"file_paths": 120},
        "evaluator_stage_fields": ["name", "validate_path"],
        "evaluator_stage_max_chars_by_field": {"validate_path": 100},
        "evaluator_workspace_fields": ["primary_file", "file_count"],
        "evaluator_workspace_max_chars_by_field": {"primary_file": 80},
        "syntax_error_fields": ["path", "message"],
        "syntax_error_max_chars_by_field": {"message": 80},
        "metric_bound_fields": ["metric", "value"],
        "metric_bound_max_chars_by_field": {"value": 40},
        "configured_stage_check_fields": ["name", "threshold_passed"],
        "configured_stage_check_max_chars_by_field": {"name": 60},
        "stage_metric_threshold_fields": ["metric", "passed"],
        "stage_metric_threshold_max_chars_by_field": {"metric": 40},
        "artifact_output_check_fields": ["type", "reason"],
        "artifact_output_check_max_chars_by_field": {"reason": 50},
        "malformed_metric_fields": ["reason"],
        "malformed_metric_max_chars_by_field": {"reason": 50},
        "materialization_error_fields": ["message"],
        "materialization_error_max_chars_by_field": {"message": 70},
        "metric_aggregation_fields": ["metric_aggregation"],
        "metric_aggregation_max_chars_by_field": {"metric_aggregation": 90},
        "synthetic_metric_fields": ["policy", "penalty"],
        "synthetic_metric_max_chars_by_field": {"policy": 50},
        "execution_diagnostic_groups": ["stdin", "diagnostic_output"],
        "validator_boundary_fields": ["policy", "resource_limits"],
        "validator_boundary_max_chars_by_field": {"policy": 64},
        "validator_budget_fields": ["policy", "exhausted"],
        "validator_budget_max_chars_by_field": {"policy": 44},
        "validator_env_fields": ["policy", "provided_keys"],
        "validator_env_max_chars_by_field": {"provided_keys": 120},
        "validator_resource_limit_fields": [
            "wall_clock_timeout",
            "process_count",
        ],
        "validator_resource_limit_max_chars_by_field": {"memory": 48},
        "validator_stdin_fields": ["policy", "sha256"],
        "validator_stdin_max_chars_by_field": {"source": 72},
        "diagnostic_output_fields": ["encoding", "redacted"],
        "diagnostic_output_max_chars_by_field": {"encoding": 60},
        "timeout_cleanup_fields": ["method", "status"],
        "timeout_cleanup_max_chars_by_field": {"error": 84},
        "prompt_format_weights": {"tone": [2.0, 1.0]},
        "context_source_paths": ["docs/a.md"],
        "context_source_required_terms": ["matrix"],
        "context_source_excluded_terms": ["debug"],
        "context_source_ranking_terms": ["sorting"],
        "context_source_limit": 1,
        "context_source_max_chars": 400,
        "context_source_truncation": "head_tail",
        "context_source_order_policy": "task_term_ranked",
        "recent_failure_limit": 2,
        "recent_failure_selection_policy": "lowest_score",
        "recent_failure_required_errors": ["syntax_error"],
        "recent_failure_excluded_errors": ["timeout"],
        "recent_failure_required_changed_files": ["main.py"],
        "recent_failure_excluded_changed_files": ["scratch.py"],
        "recent_failure_required_stage_names": ["quick"],
        "recent_failure_excluded_stage_names": ["slow"],
        "recent_failure_required_terms": ["matrix"],
        "recent_failure_excluded_terms": ["debug"],
        "recent_failure_repetition_threshold": {"min": 2, "max": None},
        "recent_failure_score_threshold": {"min": None, "max": -0.1},
        "recent_failure_max_chars_by_field": {"mutation": 80},
        "inspiration_limit": 1,
        "inspiration_sample_count": 2,
        "extra_context_max_chars": 1200,
        "plugin_context_enabled": True,
        "plugin_context_allowlist": [],
        "plugin_context_excluded_labels": ["BlockedContextPlugin"],
        "plugin_context_order": [],
        "plugin_context_required_terms": ["matrix"],
        "plugin_context_excluded_terms": ["debug"],
        "plugin_context_ranking_terms": ["matrix"],
        "plugin_context_limit": 1,
        "plugin_context_max_chars": 256,
        "plugin_context_truncation": "head",
        "plugin_context_max_chars_by_label": {},
    }
    child_record = child.to_dict()
    assert child_record["context_policy"] == restored_child.context_policy
    assert len(child_record["context_policy_sha256"]) == 64


def test_parse_prompt_mutation_response_accepts_context_policy_json():
    response = json.dumps(
        {
            "schema": "libreevolve.prompt_mutation_response.v1",
            "template": "Task: {task}",
            "context_policy": {
                "disabled_sections": ["parent_feedback"],
                "section_priorities": {"extra_context": 1},
                "mutation_instruction_variant": "minimal",
                "mutation_instruction_include_example": False,
                "proposal_metadata_enabled": True,
                "inspiration_strategy": "recency",
                "inspiration_required_metric": "latency",
                "inspiration_excluded_metrics": ["debug_score"],
                "inspiration_fitness_threshold": {"max": 0.95},
                "inspiration_metric_thresholds": {
                    "latency": {"max": 0.5},
                    "score": {"min": 0.2},
                },
                "inspiration_metric_ranking": {
                    "metric": "latency",
                    "direction": "minimize",
                },
                "feedback_sections": ["llm_grader_feedback"],
                "feedback_section_order": [
                    "llm_grader_feedback",
                    "stage_summary",
                ],
                "feedback_section_max_chars_by_name": {
                    "llm_grader_feedback": 80,
                },
                "llm_feedback_fields": ["score", "feedback"],
                "llm_feedback_max_chars_by_field": {"feedback": 88},
                "proposal_fields": ["rationale"],
                "proposal_max_chars_by_field": {"rationale": 77},
                "stage_summary_fields": ["status", "error"],
                "stage_summary_max_chars_by_field": {"error": 66},
                "execution_output_fields": ["stdout"],
                "execution_output_max_chars_by_field": {"stdout": 64},
                "sample_retry_fields": ["stage", "attempt"],
                "sample_retry_max_chars_by_field": {"stage": 40},
                "program_output_fields": ["value"],
                "program_output_max_chars_by_field": {"value": 120},
                "validator_artifact_fields": ["content_excerpt"],
                "validator_artifact_max_chars_by_field": {"content_excerpt": 64},
                "validator_artifact_content_fields": ["status"],
                "validator_artifact_content_mode": "off",
                "validator_artifact_content_max_bytes": 128,
                "validator_artifact_content_max_chars": 80,
                "validator_skipped_artifact_fields": ["reason"],
                "validator_skipped_artifact_max_chars_by_field": {"reason": 32},
                "validator_diagnostic_groups": ["metric_bound_diagnostics"],
                "validator_metadata_keys": ["score_detail", "runtime"],
                "validator_metadata_limit": 2,
                "validator_metadata_max_chars_by_key": {"runtime": 72},
                "evaluator_path_fields": ["validate_path", "validate_path_hash"],
                "evaluator_path_max_chars_by_field": {"validate_path": 96},
                "evaluator_dependency_fields": ["file_count", "file_paths"],
                "evaluator_dependency_max_chars_by_field": {"file_paths": 88},
                "evaluator_stage_fields": ["name", "attempt"],
                "evaluator_stage_max_chars_by_field": {"name": 60},
                "evaluator_workspace_fields": ["primary_file", "files"],
                "evaluator_workspace_max_chars_by_field": {"files": 96},
                "syntax_error_fields": ["message"],
                "syntax_error_max_chars_by_field": {"message": 40},
                "metric_bound_fields": ["metric", "value"],
                "metric_bound_max_chars_by_field": {"value": 32},
                "configured_stage_check_fields": ["name", "threshold_passed"],
                "configured_stage_check_max_chars_by_field": {"name": 44},
                "stage_metric_threshold_fields": ["metric", "passed"],
                "stage_metric_threshold_max_chars_by_field": {"metric": 36},
                "artifact_output_check_fields": ["type", "reason"],
                "artifact_output_check_max_chars_by_field": {"reason": 44},
                "malformed_metric_fields": ["reason"],
                "malformed_metric_max_chars_by_field": {"reason": 36},
                "materialization_error_fields": ["message"],
                "materialization_error_max_chars_by_field": {"message": 70},
                "metric_aggregation_fields": ["metric_aggregation"],
                "metric_aggregation_max_chars_by_field": {
                    "metric_aggregation": 64,
                },
                "synthetic_metric_fields": ["policy", "penalty"],
                "synthetic_metric_max_chars_by_field": {"policy": 50},
                "execution_diagnostic_groups": ["stdin"],
                "validator_boundary_fields": ["policy", "resource_limits"],
                "validator_boundary_max_chars_by_field": {"policy": 40},
                "validator_budget_fields": ["policy", "exhausted"],
                "validator_budget_max_chars_by_field": {"policy": 44},
                "validator_env_fields": ["policy", "values_redacted"],
                "validator_env_max_chars_by_field": {"policy": 48},
                "validator_resource_limit_fields": ["wall_clock_timeout"],
                "validator_resource_limit_max_chars_by_field": {"memory": 40},
                "validator_stdin_fields": ["policy", "sha256"],
                "validator_stdin_max_chars_by_field": {"source": 44},
                "diagnostic_output_fields": ["encoding", "redacted"],
                "diagnostic_output_max_chars_by_field": {"encoding": 48},
                "timeout_cleanup_fields": ["method", "status"],
                "timeout_cleanup_max_chars_by_field": {"error": 52},
                "prompt_format_weights": {"tone": [1.0, 3.0]},
                "context_source_paths": ["docs/a.md", "docs/b.md"],
                "context_source_required_terms": ["Matrix"],
                "context_source_excluded_terms": ["debug"],
                "context_source_ranking_terms": ["Sorting"],
                "context_source_limit": 1,
                "context_source_max_chars": 300,
                "context_source_truncation": "head_tail",
                "context_source_order_policy": "task_term_ranked",
                "recent_failure_limit": 1,
                "recent_failure_selection_policy": "highest_repetition",
                "recent_failure_required_errors": ["syntax_error", "missing_search"],
                "recent_failure_excluded_errors": ["timeout"],
                "recent_failure_required_changed_files": ["main.py", "lib/util.py"],
                "recent_failure_excluded_changed_files": ["scratch.py"],
                "recent_failure_required_stage_names": ["quick", "retry"],
                "recent_failure_excluded_stage_names": ["slow"],
                "recent_failure_required_terms": ["Matrix"],
                "recent_failure_excluded_terms": ["debug"],
                "recent_failure_repetition_threshold": {"max": 4},
                "recent_failure_score_threshold": {"min": -0.8},
                "recent_failure_max_chars_by_field": {"error": 64},
                "inspiration_limit": 2,
                "inspiration_sample_count": 3,
                "extra_context_max_chars": 800,
                "plugin_context_excluded_labels": ["BlockedContextPlugin"],
                "plugin_context_required_terms": ["Matrix"],
                "plugin_context_excluded_terms": ["debug"],
                "plugin_context_ranking_terms": ["Matrix"],
                "plugin_context_limit": 1,
                "plugin_context_max_chars": 256,
                "plugin_context_order": ["SecondContextPlugin"],
            },
        }
    )

    template, policy, metadata = parse_prompt_mutation_response(response)

    assert template == "Task: {task}"
    assert policy["disabled_sections"] == ["parent_feedback"]
    assert policy["section_priorities"] == {"extra_context": 1}
    assert policy["mutation_instruction_variant"] == "minimal"
    assert policy["mutation_instruction_include_example"] is False
    assert policy["proposal_metadata_enabled"] is True
    assert policy["inspiration_strategy"] == "recency"
    assert policy["inspiration_required_metric"] == "latency"
    assert policy["inspiration_excluded_metrics"] == ["debug_score"]
    assert policy["inspiration_fitness_threshold"] == {"min": None, "max": 0.95}
    assert policy["inspiration_metric_thresholds"] == {
        "latency": {"min": None, "max": 0.5},
        "score": {"min": 0.2, "max": None},
    }
    assert policy["inspiration_metric_ranking"] == {
        "metric": "latency",
        "direction": "minimize",
    }
    assert policy["feedback_sections"] == ["llm_grader_feedback"]
    assert policy["feedback_section_order"][:2] == [
        "llm_grader_feedback",
        "stage_summary",
    ]
    assert policy["feedback_section_max_chars_by_name"] == {
        "llm_grader_feedback": 80,
    }
    assert policy["llm_feedback_fields"] == ["score", "feedback"]
    assert policy["llm_feedback_max_chars_by_field"] == {"feedback": 88}
    assert policy["proposal_fields"] == ["rationale"]
    assert policy["proposal_max_chars_by_field"] == {"rationale": 77}
    assert policy["stage_summary_fields"] == ["status", "error"]
    assert policy["stage_summary_max_chars_by_field"] == {"error": 66}
    assert policy["execution_output_fields"] == ["stdout"]
    assert policy["execution_output_max_chars_by_field"] == {"stdout": 64}
    assert policy["sample_retry_fields"] == ["stage", "attempt"]
    assert policy["sample_retry_max_chars_by_field"] == {"stage": 40}
    assert policy["program_output_fields"] == ["value"]
    assert policy["program_output_max_chars_by_field"] == {"value": 120}
    assert policy["validator_artifact_fields"] == ["content_excerpt"]
    assert policy["validator_artifact_max_chars_by_field"] == {
        "content_excerpt": 64
    }
    assert policy["validator_artifact_content_fields"] == ["status"]
    assert policy["validator_artifact_content_mode"] == "off"
    assert policy["validator_artifact_content_max_bytes"] == 128
    assert policy["validator_artifact_content_max_chars"] == 80
    assert policy["validator_skipped_artifact_fields"] == ["reason"]
    assert policy["validator_skipped_artifact_max_chars_by_field"] == {"reason": 32}
    assert policy["validator_diagnostic_groups"] == ["metric_bound_diagnostics"]
    assert policy["validator_metadata_keys"] == ["score_detail", "runtime"]
    assert policy["validator_metadata_limit"] == 2
    assert policy["validator_metadata_max_chars_by_key"] == {"runtime": 72}
    assert policy["evaluator_path_fields"] == ["validate_path", "validate_path_hash"]
    assert policy["evaluator_path_max_chars_by_field"] == {"validate_path": 96}
    assert policy["evaluator_dependency_fields"] == ["file_count", "file_paths"]
    assert policy["evaluator_dependency_max_chars_by_field"] == {"file_paths": 88}
    assert policy["evaluator_stage_fields"] == ["name", "attempt"]
    assert policy["evaluator_stage_max_chars_by_field"] == {"name": 60}
    assert policy["evaluator_workspace_fields"] == ["primary_file", "files"]
    assert policy["evaluator_workspace_max_chars_by_field"] == {"files": 96}
    assert policy["syntax_error_fields"] == ["message"]
    assert policy["syntax_error_max_chars_by_field"] == {"message": 40}
    assert policy["metric_bound_fields"] == ["metric", "value"]
    assert policy["metric_bound_max_chars_by_field"] == {"value": 32}
    assert policy["configured_stage_check_fields"] == ["name", "threshold_passed"]
    assert policy["configured_stage_check_max_chars_by_field"] == {"name": 44}
    assert policy["stage_metric_threshold_fields"] == ["metric", "passed"]
    assert policy["stage_metric_threshold_max_chars_by_field"] == {"metric": 36}
    assert policy["artifact_output_check_fields"] == ["type", "reason"]
    assert policy["artifact_output_check_max_chars_by_field"] == {"reason": 44}
    assert policy["malformed_metric_fields"] == ["reason"]
    assert policy["malformed_metric_max_chars_by_field"] == {"reason": 36}
    assert policy["materialization_error_fields"] == ["message"]
    assert policy["materialization_error_max_chars_by_field"] == {"message": 70}
    assert policy["metric_aggregation_fields"] == ["metric_aggregation"]
    assert policy["metric_aggregation_max_chars_by_field"] == {
        "metric_aggregation": 64
    }
    assert policy["synthetic_metric_fields"] == ["policy", "penalty"]
    assert policy["synthetic_metric_max_chars_by_field"] == {"policy": 50}
    assert policy["execution_diagnostic_groups"] == ["stdin"]
    assert policy["validator_boundary_fields"] == ["policy", "resource_limits"]
    assert policy["validator_boundary_max_chars_by_field"] == {"policy": 40}
    assert policy["validator_budget_fields"] == ["policy", "exhausted"]
    assert policy["validator_budget_max_chars_by_field"] == {"policy": 44}
    assert policy["validator_env_fields"] == ["policy", "values_redacted"]
    assert policy["validator_env_max_chars_by_field"] == {"policy": 48}
    assert policy["validator_resource_limit_fields"] == ["wall_clock_timeout"]
    assert policy["validator_resource_limit_max_chars_by_field"] == {"memory": 40}
    assert policy["validator_stdin_fields"] == ["policy", "sha256"]
    assert policy["validator_stdin_max_chars_by_field"] == {"source": 44}
    assert policy["diagnostic_output_fields"] == ["encoding", "redacted"]
    assert policy["diagnostic_output_max_chars_by_field"] == {"encoding": 48}
    assert policy["timeout_cleanup_fields"] == ["method", "status"]
    assert policy["timeout_cleanup_max_chars_by_field"] == {"error": 52}
    assert policy["prompt_format_weights"] == {"tone": [1.0, 3.0]}
    assert policy["context_source_paths"] == ["docs/a.md", "docs/b.md"]
    assert policy["context_source_required_terms"] == ["matrix"]
    assert policy["context_source_excluded_terms"] == ["debug"]
    assert policy["context_source_ranking_terms"] == ["sorting"]
    assert policy["context_source_limit"] == 1
    assert policy["context_source_max_chars"] == 300
    assert policy["context_source_truncation"] == "head_tail"
    assert policy["context_source_order_policy"] == "task_term_ranked"
    assert policy["recent_failure_limit"] == 1
    assert policy["recent_failure_selection_policy"] == "highest_repetition"
    assert policy["recent_failure_required_errors"] == [
        "syntax_error",
        "missing_search",
    ]
    assert policy["recent_failure_excluded_errors"] == ["timeout"]
    assert policy["recent_failure_required_changed_files"] == [
        "main.py",
        "lib/util.py",
    ]
    assert policy["recent_failure_excluded_changed_files"] == ["scratch.py"]
    assert policy["recent_failure_required_stage_names"] == ["quick", "retry"]
    assert policy["recent_failure_excluded_stage_names"] == ["slow"]
    assert policy["recent_failure_required_terms"] == ["matrix"]
    assert policy["recent_failure_excluded_terms"] == ["debug"]
    assert policy["recent_failure_repetition_threshold"] == {"min": None, "max": 4}
    assert policy["recent_failure_score_threshold"] == {"min": -0.8, "max": None}
    assert policy["recent_failure_max_chars_by_field"] == {"error": 64}
    assert policy["inspiration_limit"] == 2
    assert policy["inspiration_sample_count"] == 3
    assert policy["extra_context_max_chars"] == 800
    assert policy["plugin_context_excluded_labels"] == ["BlockedContextPlugin"]
    assert policy["plugin_context_required_terms"] == ["matrix"]
    assert policy["plugin_context_excluded_terms"] == ["debug"]
    assert policy["plugin_context_ranking_terms"] == ["matrix"]
    assert policy["plugin_context_limit"] == 1
    assert policy["plugin_context_max_chars"] == 256
    assert policy["plugin_context_order"] == ["SecondContextPlugin"]
    assert metadata["format"] == "json_object"
    assert metadata["context_policy_source"] == "mutation_response"


def test_prompt_database_restores_invalid_mutation_penalty_state(tmp_path):
    db = PromptDatabase(tmp_path, templates=["a {task}"])
    parent = db.select()

    child = db.mutate(parent.id, "bad {unknown}", generation=2)
    restored = PromptDatabase(tmp_path)
    restored_parent = _program_by_id(restored, parent.id)

    assert child is None
    assert restored_parent.uses == 1
    assert restored_parent.reward_sum == 0.0
    assert restored_parent.metadata["last_prompt_penalty"]["reason"] == "invalid_mutation"
    assert restored_parent.metadata["rejected_prompt_mutations"] == [
        {"generation": 2, "error": "unknown prompt template field 'unknown'"}
    ]


def test_prompt_database_restore_rejects_score_for_unknown_prompt_id(tmp_path):
    history = tmp_path / "prompt_history.jsonl"
    history.write_text(
        json.dumps(
            {
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "record_schema": PROMPT_HISTORY_RECORD_SCHEMA,
                "event": "score",
                "program": PromptProgram(template="a {task}", id="p1", uses=1, reward_sum=1.0).to_dict(),
            }
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(PromptHistoryReplayError, match="unknown prompt program id"):
        PromptDatabase(tmp_path)


def test_prompt_database_restore_rejects_incompatible_reward_policy(tmp_path):
    db = PromptDatabase(
        tmp_path,
        templates=["a {task}"],
        reward_bounds=(-1.0, 1.0),
        reward_mode="improvement",
    )
    program = db.select()
    db.record_result(program.id, 0.0)

    with pytest.raises(PromptHistoryReplayError, match="reward mode is incompatible"):
        PromptDatabase(tmp_path, reward_bounds=(-1.0, 1.0), reward_mode="absolute")
    with pytest.raises(PromptHistoryReplayError, match="reward bounds are incompatible"):
        PromptDatabase(tmp_path, reward_bounds=(0.0, 1.0), reward_mode="improvement")


def test_prompt_database_selects_and_scores_templates():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}", "b {task}"])

    first = db.select()
    db.record_result(first.id, 0.25)
    scored = _program_by_id(db, first.id)

    assert first.uses == 0
    assert scored.uses == 1
    assert scored.mean_reward == 0.25
    assert (Path(tmpdir) / "prompt_history.jsonl").exists()


def test_duplicate_configured_templates_are_independent_arms_with_shared_hash():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=[DEFAULT_TEMPLATE, DEFAULT_TEMPLATE])

    programs = db.all()
    assert len(programs) == 2
    assert {program.template for program in programs} == {DEFAULT_TEMPLATE}
    expected_id_hash = hashlib.sha256(DEFAULT_TEMPLATE.encode("utf-8")).hexdigest()[:16]
    assert [program.id for program in programs] == [
        f"prompt-seed-0-{expected_id_hash}",
        f"prompt-seed-1-{expected_id_hash}",
    ]

    first = db.select()
    db.record_result(first.id, 1.0)
    scored = _program_by_id(db, first.id)
    unscored = [program for program in db.all() if program.id != first.id][0]
    expected_full_hash = hashlib.sha256(DEFAULT_TEMPLATE.encode("utf-8")).hexdigest()

    assert scored.uses == 1
    assert unscored.uses == 0
    add_records = [
        json.loads(line)
        for line in (Path(tmpdir) / "prompt_history.jsonl").read_text().splitlines()
        if json.loads(line)["event"] == "add"
    ]
    assert [record["program"]["template_sha256"] for record in add_records] == [
        expected_full_hash,
        expected_full_hash,
    ]
    assert {record["schema_version"] for record in add_records} == {
        ARTIFACT_SCHEMA_VERSION
    }
    assert {record["record_schema"] for record in add_records} == {
        PROMPT_HISTORY_RECORD_SCHEMA
    }
    assert len({record["program"]["id"] for record in add_records}) == 2


def test_prompt_database_selects_untried_configured_variants_in_config_order():
    first_db = PromptDatabase(
        tempfile.mkdtemp(),
        templates=["first {task}", "second {task}", "third {task}"],
    )
    second_db = PromptDatabase(
        tempfile.mkdtemp(),
        templates=["first {task}", "second {task}", "third {task}"],
    )

    first_selected = first_db.select()
    first_db.record_result(first_selected.id, 0.0)
    second_selected = first_db.select()
    second_db_first_selected = second_db.select()

    assert first_selected.template == "first {task}"
    assert second_selected.template == "second {task}"
    assert second_db_first_selected.template == "first {task}"
    assert first_selected.id == second_db_first_selected.id
    assert first_selected.id.startswith("prompt-seed-0-")


def test_duplicate_mutated_templates_are_independent_children_with_shared_hash():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    parent = db.select()

    first_child = db.mutate(parent.id, "a {task} plus", generation=1)
    second_child = db.mutate(parent.id, "a {task} plus", generation=1)

    assert first_child is not None
    assert second_child is not None
    assert first_child.id.startswith("prompt-mut-1-0-")
    assert second_child.id.startswith("prompt-mut-1-1-")
    assert first_child.id != second_child.id
    assert first_child.template == second_child.template
    expected_hash = hashlib.sha256("a {task} plus".encode("utf-8")).hexdigest()
    add_records = [
        json.loads(line)["program"]
        for line in (Path(tmpdir) / "prompt_history.jsonl").read_text().splitlines()
        if json.loads(line)["event"] == "add"
    ]
    child_records = [
        record for record in add_records if record["parent_id"] == parent.id
    ]

    assert [record["template_sha256"] for record in child_records] == [
        expected_hash,
        expected_hash,
    ]
    assert len({record["id"] for record in child_records}) == 2


def test_prompt_database_normalizes_and_clamps_rewards():
    db = PromptDatabase(
        tempfile.mkdtemp(),
        templates=["a {task}"],
        reward_bounds=(-1.0, 1.0),
        reward_mode="improvement",
    )
    program = db.select()

    db.record_result(program.id, -2.0)
    db.record_result(program.id, 0.0)
    db.record_result(program.id, 2.0)
    scored = _program_by_id(db, program.id)

    assert scored.reward_sum == 1.5
    assert scored.mean_reward == 0.5
    assert scored.metadata["last_prompt_reward"] == {
        "mode": "improvement",
        "raw": 2.0,
        "normalized": 1.0,
        "bounds": [-1.0, 1.0],
    }


def test_prompt_database_selection_uses_configured_exploration_coefficient():
    db = PromptDatabase(
        tempfile.mkdtemp(),
        templates=["a {task}", "b {task}"],
        explore_coeff=0.0,
    )
    first, second = sorted(db.all(), key=lambda p: p.id)
    db.record_result(first.id, 0.2)
    db.record_result(second.id, 0.8)

    assert db.select().id == second.id


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"reward_bounds": [1.0, 1.0]}, "reward_bounds"),
        ({"reward_bounds": [2.0, 1.0]}, "reward_bounds"),
        ({"reward_bounds": [0.0]}, "reward_bounds"),
        ({"reward_bounds": [0.0, math.nan]}, "reward_bounds"),
        ({"reward_bounds": [0.0, True]}, "reward_bounds"),
        ({"explore_coeff": -1.0}, "explore_coeff"),
        ({"explore_coeff": math.nan}, "explore_coeff"),
        ({"explore_coeff": True}, "explore_coeff"),
        ({"explore_coeff": "1.0"}, "explore_coeff"),
        ({"reward_mode": "not-a-mode"}, "reward_mode"),
        ({"reward_mode": 7}, "reward_mode"),
    ],
)
def test_prompt_database_rejects_invalid_direct_reward_policy(kwargs, message):
    with pytest.raises(ValueError, match=message):
        PromptDatabase(tempfile.mkdtemp(), templates=["a {task}"], **kwargs)


def test_prompt_database_mutates_with_lineage():
    db = PromptDatabase(tempfile.mkdtemp(), templates=["a {task}"])
    parent = db.select()
    child = db.mutate(parent.id, "b {task}", generation=3)

    assert child.parent_id == parent.id
    assert child.generation == 3
    assert len(db.all()) == 2


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("id", "", "prompt id"),
        ("id", "bad id", "prompt id"),
        ("id", "api_key=sk-proj_prompt_secret_1234567890", "prompt id"),  # pragma: allowlist secret
        ("parent_id", "bad\nparent", "prompt id"),
        ("generation", -1, "generation"),
        ("generation", True, "generation"),
        ("generation", "1", "generation"),
        ("uses", -1, "uses"),
        ("uses", True, "uses"),
        ("uses", "2", "uses"),
        ("reward_sum", math.nan, "reward_sum"),
        ("reward_sum", True, "reward_sum"),
        ("metadata", {"bad": {1, 2}}, "metadata"),
        ("metadata", ["bad"], "metadata"),
        ("metadata", {"bad\u200dkey": "ok"}, "display-safe metadata label"),
        ("metadata", {"safe": "bad\u200dvalue"}, "display-safe metadata value"),
    ],
)
def test_prompt_program_rejects_invalid_state_at_construction(field, value, message):
    kwargs = {"template": "a {task}", field: value}

    with pytest.raises(ValueError, match=message):
        PromptProgram(**kwargs)


@pytest.mark.parametrize(
    ("template", "message"),
    [
        (123, "template must be a non-empty string"),
        ("Task: {unknown}", "unknown prompt template field"),
        ("Task formatted numeric: {task:.2f}", "format spec"),
    ],
)
def test_prompt_program_rejects_invalid_template_at_construction(template, message):
    with pytest.raises(PromptTemplateError, match=message):
        PromptProgram(template=template)


def test_validate_prompt_program_revalidates_template_after_mutation():
    program = PromptProgram(template="Task: {task}")
    program.template = "Task: {unknown}"

    with pytest.raises(PromptTemplateError, match="unknown prompt template field"):
        validate_prompt_program(program)


def test_prompt_database_revalidates_mutated_prompt_program_before_add():
    db = PromptDatabase(tempfile.mkdtemp(), templates=["a {task}"])
    program = PromptProgram(template="b {task}")
    program.uses = -1

    with pytest.raises(ValueError, match="uses"):
        db.add(program)

    assert len(db.all()) == 1


def test_prompt_database_revalidates_mutated_prompt_program_template_before_add():
    db = PromptDatabase(tempfile.mkdtemp(), templates=["a {task}"])
    program = PromptProgram(template="b {task}")
    program.template = "bad {unknown}"

    with pytest.raises(PromptTemplateError, match="unknown prompt template field"):
        db.add(program)

    assert len(db.all()) == 1


def test_prompt_database_returns_prompt_program_snapshots():
    db = PromptDatabase(tempfile.mkdtemp(), templates=["a {task}"])
    program = PromptProgram(
        template="b {task}",
        metadata={"source": "direct", "nested": {"values": [1]}},
    )
    added = db.add(program)

    program.template = "bad {unknown}"
    program.metadata["nested"]["values"].append(2)
    program.uses = 99
    added.metadata["nested"]["values"].append(3)

    stored = _program_by_id(db, program.id)
    assert stored.template == "b {task}"
    assert stored.uses == 0
    assert stored.metadata["nested"]["values"] == [1]

    listed = _program_by_id(db, program.id)
    listed.template = "bad {missing_from_all}"
    listed.metadata["nested"]["values"].append(4)
    selected = db.select()
    selected.template = "bad {missing_from_select}"
    selected.metadata["source"] = "mutated"

    stored_again = _program_by_id(db, program.id)
    assert stored_again.template == "b {task}"
    assert stored_again.metadata == {"source": "direct", "nested": {"values": [1]}}


def test_prompt_database_sanitizes_metadata_before_prompt_history_persistence():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_prompt_metadata_secret_1234567890"  # pragma: allowlist secret
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    program = PromptProgram(
        template="b {task}",
        metadata={
            "caf\u00e9": "mañana",
            f"api_key={secret}": f"value {secret}",
        },
    )

    added = db.add(program)

    assert added.metadata["caf\u00e9"] == "mañana"
    redacted_key = next(key for key in added.metadata if key.startswith("api_key=[REDACTED]"))
    assert redacted_key.endswith(f"#sha256:{hashlib.sha256(f'api_key={secret}'.encode('utf-8')).hexdigest()[:12]}")
    assert added.metadata[redacted_key] == "value [REDACTED]"
    history_text = (Path(tmpdir) / "prompt_history.jsonl").read_text()
    assert secret not in history_text
    history = [json.loads(line) for line in history_text.splitlines()]
    add_record = history[-1]["program"]["metadata"]
    assert add_record["caf\u00e9"] == "mañana"
    assert add_record[redacted_key] == "value [REDACTED]"


def test_prompt_database_rejects_duplicate_prompt_program_ids_before_logging():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    original = db.select()
    duplicate = PromptProgram(template="b {task}", id=original.id)

    with pytest.raises(StrictJsonlError, match="Duplicate prompt program id"):
        db.add(duplicate)

    events = [
        json.loads(line)["event"]
        for line in (Path(tmpdir) / "prompt_history.jsonl").read_text().splitlines()
    ]
    assert events == ["add"]
    invalid = [
        json.loads(line)
        for line in (Path(tmpdir) / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    assert invalid == [
        {
            "event": "prompt_reference_error",
            "operation": "add",
            "prompt_id": f"'{original.id}'",
            "error": f"duplicate prompt program id: '{original.id}'",
            "generation": "0",
            "template": "b {task}",
            "metadata": "{}",
        }
    ]
    assert [program.id for program in db.all()] == [original.id]


def test_prompt_database_rejects_unknown_parent_prompt_program_id():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    child = PromptProgram(template="b {task}", parent_id="missing_parent")

    with pytest.raises(StrictJsonlError, match="Unknown parent"):
        db.add(child)

    assert len(db.all()) == 1
    invalid = [
        json.loads(line)
        for line in (Path(tmpdir) / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    assert invalid == [
        {
            "event": "prompt_reference_error",
            "operation": "add",
            "prompt_id": f"'{child.id}'",
            "error": "unknown parent prompt program id: 'missing_parent'",
            "generation": "0",
            "parent_id": "'missing_parent'",
            "template": "b {task}",
            "metadata": "{}",
        }
    ]
    assert child.id not in {program.id for program in db.all()}


def test_prompt_database_records_missing_prompt_score_reference():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])

    with pytest.raises(StrictJsonlError, match="Unknown prompt program id"):
        db.record_result("missing-prompt-id", 1.0, metadata={"source": "score"})

    events = [
        json.loads(line)["event"]
        for line in (Path(tmpdir) / "prompt_history.jsonl").read_text().splitlines()
    ]
    assert events == ["add"]
    invalid = [
        json.loads(line)
        for line in (Path(tmpdir) / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    assert invalid == [
        {
            "event": "prompt_reference_error",
            "operation": "score",
            "prompt_id": "'missing-prompt-id'",
            "error": "unknown prompt program id: 'missing-prompt-id'",
            "reward": "1.0",
            "metadata": "{'source': 'score'}",
        }
    ]


def test_prompt_database_records_missing_prompt_mutation_reference():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])

    with pytest.raises(StrictJsonlError, match="Unknown prompt program id"):
        db.mutate(
            "missing-prompt-id",
            "b {task}",
            generation=7,
            metadata={"source": "mutation"},
        )

    invalid = [
        json.loads(line)
        for line in (Path(tmpdir) / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    assert invalid == [
        {
            "event": "prompt_reference_error",
            "operation": "mutate",
            "prompt_id": "'missing-prompt-id'",
            "error": "unknown prompt program id: 'missing-prompt-id'",
            "generation": "7",
            "template": "b {task}",
            "metadata": "{'source': 'mutation'}",
        }
    ]


def test_prompt_database_records_invalid_prompt_reference_without_secret_leak():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    unsafe_id = "api_key=sk-proj_prompt_secret_1234567890"  # pragma: allowlist secret

    with pytest.raises(StrictJsonlError, match="Invalid prompt program id"):
        db.record_result(unsafe_id, 1.0)

    invalid_text = (Path(tmpdir) / "prompt_history_invalid.jsonl").read_text()
    assert "prompt_reference_error" in invalid_text
    assert "sk-proj_prompt_secret" not in invalid_text
    invalid = json.loads(invalid_text.splitlines()[0])
    assert invalid["operation"] == "score"
    assert invalid["prompt_id"] == "'api_key=[REDACTED]'"


def test_prompt_database_mutation_may_add_placeholders_to_minimal_parent():
    db = PromptDatabase(tempfile.mkdtemp(), templates=["a {task}"])
    parent = db.select()
    child = db.mutate(parent.id, "b {task} {parent_code}", generation=3)

    assert child is not None
    assert prompt_template_fields(child.template) == {"task", "parent_code"}


def test_prompt_database_rejects_invalid_configured_template():
    with pytest.raises(PromptTemplateError, match="unknown"):
        PromptDatabase(tempfile.mkdtemp(), templates=["Task: {unknown}"])


def test_prompt_database_rejects_incompatible_configured_format_spec():
    with pytest.raises(PromptTemplateError, match="format spec"):
        PromptDatabase(tempfile.mkdtemp(), templates=["Task: {task:.2f}"])


def test_prompt_database_quarantines_invalid_mutated_template_and_penalizes_parent():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    parent = db.select()

    child = db.mutate(parent.id, "bad {unknown}", generation=3)

    assert child is None
    assert len(db.all()) == 1
    penalized = _program_by_id(db, parent.id)
    assert parent.reward_sum == 0.0
    assert parent.uses == 0
    assert penalized.reward_sum == 0.0
    assert penalized.uses == 1
    assert penalized.mean_reward == 0.0
    assert penalized.metadata["last_prompt_penalty"]["reason"] == "invalid_mutation"
    assert penalized.metadata["last_prompt_penalty"]["raw"] == 0.0
    assert penalized.metadata["last_prompt_penalty"]["normalized"] == 0.0
    assert penalized.metadata["last_prompt_penalty"]["bounds"] == [0.0, 1.0]
    invalid = [
        json.loads(line)
        for line in (Path(tmpdir) / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    assert invalid[0]["event"] == "reject"
    assert invalid[0]["parent_id"] == parent.id
    assert invalid[0]["template"] == "bad {unknown}"
    assert invalid[0]["template_raw_chars"] == len("bad {unknown}")
    assert invalid[0]["template_sha256"] == hashlib.sha256(
        "bad {unknown}".encode("utf-8")
    ).hexdigest()
    assert invalid[0]["template_redacted"] is False
    assert invalid[0]["template_truncated"] is False
    events = [
        json.loads(line)["event"]
        for line in (Path(tmpdir) / "prompt_history.jsonl").read_text().splitlines()
    ]
    assert events == ["add", "penalty"]


def test_prompt_database_redacts_and_bounds_rejected_mutation_template():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    parent = db.select()
    secret = "sk-proj_rejected_template_secret_1234567890"  # pragma: allowlist secret
    template = f"Task: {{unknown}} {secret} " + ("X" * 1200)

    child = db.mutate(parent.id, template, generation=5)

    assert child is None
    invalid_text = (Path(tmpdir) / "prompt_history_invalid.jsonl").read_text()
    assert secret not in invalid_text
    assert "X" * 600 not in invalid_text
    invalid = json.loads(invalid_text.splitlines()[0])
    assert invalid["event"] == "reject"
    assert invalid["template"].startswith("Task: {unknown} [REDACTED]")
    assert invalid["template"].endswith("...<truncated>")
    assert invalid["template_raw_chars"] == len(template)
    assert invalid["template_sha256"] == hashlib.sha256(
        template.encode("utf-8")
    ).hexdigest()
    assert invalid["template_redacted"] is True
    assert invalid["template_truncated"] is True


def test_invalid_mutation_penalty_affects_never_used_parent_selection():
    db = PromptDatabase(
        tempfile.mkdtemp(),
        templates=["a {task}", "b {task}"],
        explore_coeff=0.0,
    )
    parent = db.select()
    other = next(program for program in db.all() if program.id != parent.id)

    child = db.mutate(parent.id, "bad {unknown}", generation=1)

    assert child is None
    penalized = _program_by_id(db, parent.id)
    assert penalized.uses == 1
    assert penalized.mean_reward == 0.0
    assert db.select().id == other.id


def test_invalid_mutation_penalty_updates_used_parent_mean_reward():
    db = PromptDatabase(
        tempfile.mkdtemp(),
        templates=["a {task}"],
        explore_coeff=0.0,
    )
    parent = db.select()
    db.record_result(parent.id, 1.0)

    child = db.mutate(parent.id, "bad {unknown}", generation=2)

    assert child is None
    penalized = _program_by_id(db, parent.id)
    assert penalized.uses == 2
    assert penalized.reward_sum == 1.0
    assert penalized.mean_reward == 0.5


def test_invalid_mutation_penalty_uses_configured_reward_lower_bound():
    db = PromptDatabase(
        tempfile.mkdtemp(),
        templates=["a {task}"],
        reward_bounds=(-2.0, 2.0),
        reward_mode="improvement",
    )
    parent = db.select()

    child = db.mutate(parent.id, "bad {unknown}", generation=2)

    assert child is None
    penalized = _program_by_id(db, parent.id)
    assert penalized.uses == 1
    assert penalized.reward_sum == 0.0
    assert penalized.mean_reward == 0.0
    assert penalized.metadata["last_prompt_penalty"] == {
        "reason": "invalid_mutation",
        "generation": 2,
        "mode": "improvement",
        "raw": -2.0,
        "normalized": 0.0,
        "bounds": [-2.0, 2.0],
        "error": "unknown prompt template field 'unknown'",
    }


def test_invalid_mutation_rejection_metadata_is_checked_before_parent_penalty():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    parent = db.select()

    with pytest.raises(StrictJsonlError):
        db.mutate(parent.id, "bad {unknown}", generation=1, metadata={"bad": {1, 2}})

    unchanged = _program_by_id(db, parent.id)
    assert unchanged.uses == 0
    assert unchanged.reward_sum == 0.0
    assert unchanged.mean_reward == 0.0
    assert "last_prompt_penalty" not in unchanged.metadata
    assert "rejected_prompt_mutations" not in unchanged.metadata
    events = [
        json.loads(line)["event"]
        for line in (Path(tmpdir) / "prompt_history.jsonl").read_text().splitlines()
    ]
    assert events == ["add"]
    invalid = [
        json.loads(line)
        for line in (Path(tmpdir) / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    assert invalid[0]["error"] == "TypeError"
    assert "set" in invalid[0]["message"]


def test_incompatible_mutated_format_spec_is_quarantined_and_penalizes_parent():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    parent = db.select()

    child = db.mutate(parent.id, "bad {task:.2f}", generation=1)

    assert child is None
    penalized = _program_by_id(db, parent.id)
    assert penalized.uses == 1
    assert penalized.mean_reward == 0.0
    assert penalized.metadata["last_prompt_penalty"]["normalized"] == 0.0
    invalid = [
        json.loads(line)
        for line in (Path(tmpdir) / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    assert invalid[0]["event"] == "reject"
    assert "format spec" in invalid[0]["error"]


def test_mutated_template_that_drops_parent_placeholders_is_quarantined():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=[DEFAULT_TEMPLATE])
    parent = db.select()

    child = db.mutate(parent.id, "Task only: {task}", generation=4)

    assert child is None
    assert len(db.all()) == 1
    penalized = _program_by_id(db, parent.id)
    assert penalized.uses == 1
    assert penalized.mean_reward == 0.0
    assert penalized.metadata["last_prompt_penalty"]["normalized"] == 0.0
    invalid = [
        json.loads(line)
        for line in (Path(tmpdir) / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    assert invalid[0]["event"] == "reject"
    assert "dropped parent placeholders" in invalid[0]["error"]
    assert "parent_code" in invalid[0]["error"]
    assert "mutation_instructions" in invalid[0]["error"]


def test_prompt_database_logs_add_and_score_events():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    program = db.select()
    db.record_result(program.id, 1.0)

    events = [
        json.loads(line)["event"]
        for line in (Path(tmpdir) / "prompt_history.jsonl").read_text().splitlines()
    ]
    assert events == ["add", "score"]


def test_prompt_database_rejects_non_finite_score_with_quarantine():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    program = db.select()

    with pytest.raises(StrictJsonlError):
        db.record_result(program.id, math.nan, metadata={"source": "score"})

    assert program.uses == 0
    assert program.reward_sum == 0.0
    stored = _program_by_id(db, program.id)
    assert stored.uses == 0
    assert stored.reward_sum == 0.0
    quarantine = Path(tmpdir) / "prompt_history_invalid.jsonl"
    record = json.loads(quarantine.read_text().splitlines()[0])
    assert "nan" in record["message"]
    assert "'source': 'score'" in record["record_repr"]


def test_prompt_database_rejects_invalid_score_metadata_without_state_change():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}", "b {task}"])
    program = db.select()

    with pytest.raises(StrictJsonlError, match="prompt reward metadata"):
        db.record_result(program.id, 1.0, metadata={"bad": {1, 2}})

    unchanged = _program_by_id(db, program.id)
    assert unchanged.uses == 0
    assert unchanged.reward_sum == 0.0
    assert unchanged.mean_reward == 0.0
    assert unchanged.metadata == {"source": "seed", "seed_index": 0}
    assert db.select().id == program.id
    events = [
        json.loads(line)["event"]
        for line in (Path(tmpdir) / "prompt_history.jsonl").read_text().splitlines()
    ]
    assert events == ["add", "add"]
    invalid = [
        json.loads(line)
        for line in (Path(tmpdir) / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    assert len(invalid) == 1
    assert invalid[0]["error"] == "ValueError"
    assert "prompt reward metadata" in invalid[0]["message"]
    assert "{1, 2}" in invalid[0]["record_repr"]


@pytest.mark.parametrize(
    "metadata",
    [
        {"bad\u200dkey": "ok"},
        {"safe": "bad\u200dvalue"},
    ],
)
def test_prompt_database_rejects_format_control_score_metadata_without_state_change(metadata):
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    program = db.select()

    with pytest.raises(StrictJsonlError, match="prompt reward metadata"):
        db.record_result(program.id, 1.0, metadata=metadata)

    unchanged = _program_by_id(db, program.id)
    assert unchanged.uses == 0
    assert unchanged.reward_sum == 0.0
    invalid = [
        json.loads(line)
        for line in (Path(tmpdir) / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    assert len(invalid) == 1
    assert "display-safe metadata" in invalid[0]["message"]


def test_repeated_invalid_score_metadata_writes_quarantine_without_state_change():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    program = db.select()

    for _ in range(2):
        with pytest.raises(StrictJsonlError, match="prompt reward metadata"):
            db.record_result(program.id, 0.5, metadata={"bad": {1, 2}})

    unchanged = _program_by_id(db, program.id)
    assert unchanged.uses == 0
    assert unchanged.reward_sum == 0.0
    events = [
        json.loads(line)["event"]
        for line in (Path(tmpdir) / "prompt_history.jsonl").read_text().splitlines()
    ]
    assert events == ["add"]
    invalid = [
        json.loads(line)
        for line in (Path(tmpdir) / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    assert len(invalid) == 2
    assert [record["error"] for record in invalid] == ["ValueError", "ValueError"]


def test_prompt_database_redacts_and_bounds_score_metadata_before_persistence():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    program = db.select()
    key_secret = "sk-proj_promptmetakeysecret1234567890"  # pragma: allowlist secret
    value_secret = "sk-proj_promptmetavaluesecret1234567890"  # pragma: allowlist secret
    nested_secret = "ghp_nestedpromptmetasecret1234567890"
    raw_key = f"api_key={key_secret}"
    raw_nested_key = f"token={nested_secret}"
    long_note = "X" * 1500

    db.record_result(
        program.id,
        1.0,
        metadata={
            raw_key: "value",
            "note": f"token={value_secret}",
            "nested": {
                raw_nested_key: "inner",
                "long": long_note,
            },
            "items": [f"secret={value_secret}", {"password": f"secret={value_secret}"}],
        },
    )

    persisted_text = (Path(tmpdir) / "prompt_history.jsonl").read_text()
    assert key_secret not in persisted_text
    assert value_secret not in persisted_text
    assert nested_secret not in persisted_text
    assert long_note not in persisted_text
    record = json.loads(persisted_text.splitlines()[-1])
    metadata = record["program"]["metadata"]
    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:12]
    nested_key_hash = hashlib.sha256(raw_nested_key.encode("utf-8")).hexdigest()[:12]
    safe_key = next(key for key in metadata if key.startswith("api_key=[REDACTED]"))
    assert safe_key.endswith(f"#sha256:{key_hash}")
    safe_nested_key = next(
        key for key in metadata["nested"] if key.startswith("token=[REDACTED]")
    )
    assert safe_nested_key.endswith(f"#sha256:{nested_key_hash}")
    assert metadata[safe_key] == "value"
    assert metadata["note"] == "token=[REDACTED]"
    assert metadata["nested"][safe_nested_key] == "inner"
    assert metadata["nested"]["long"].endswith("...<truncated>")
    assert len(metadata["nested"]["long"]) == 1000
    assert metadata["items"] == [
        "secret=[REDACTED]",
        {"password": "secret=[REDACTED]"},
    ]

    live = _program_by_id(db, program.id)
    assert live.metadata == metadata


def test_prompt_database_honors_quarantine_snapshot_off_retention():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(
        tmpdir,
        templates=["a {task}"],
        quarantine_snapshot_retention_mode="off",
    )
    program = db.select()

    with pytest.raises(StrictJsonlError, match="prompt reward metadata"):
        db.record_result(
            program.id,
            1.0,
            metadata={
                "note": "api_key=sk-proj_prompt_quarantine_secret_123456",
                "bad_tuple": ("not", "json"),
            },
        )

    [record] = [
        json.loads(line)
        for line in (Path(tmpdir) / "prompt_history_invalid.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert "record_repr" not in record
    assert "record_repr_truncated" not in record
    retention = record["record_repr_retention"]
    assert retention["retention_mode"] == "off"
    assert retention["sha256"] is None
    assert retention["chars"] is None
    assert "sk-proj_" not in json.dumps(record)
