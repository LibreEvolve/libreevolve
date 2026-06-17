from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path

from libreevolve.core.jsonl import StrictJsonlError, iter_quarantine_records

ARTIFACT_SCHEMA_VERSION = 1
RUN_MANIFEST_SCHEMA = "libreevolve.run_manifest.v1"
HISTORY_RECORD_SCHEMA = "libreevolve.history.program.v1"
FAILURE_RECORD_SCHEMA = "libreevolve.failure_history.v1"
EVALUATOR_RESULT_RECORD_SCHEMA = "libreevolve.evaluator_result.v1"
ARCHIVE_EVENT_RECORD_SCHEMA = "libreevolve.archive_event.v1"
LLM_CALL_RECORD_SCHEMA = "libreevolve.llm_call.v1"
LLM_REWARD_RECORD_SCHEMA = "libreevolve.llm_reward.v1"
PROMPT_HISTORY_RECORD_SCHEMA = "libreevolve.prompt_history.v1"
PROMPT_CURRENT_BINDING_TABLE_RECORD_SCHEMA = (
    "libreevolve.prompt_current_binding_table.v1"
)
PROMPT_PRIOR_SCORE_TABLE_RECORD_SCHEMA = (
    "libreevolve.prompt_prior_score_table.v1"
)
CONTROLLER_BUDGET_EVENT_RECORD_SCHEMA = "libreevolve.controller_budget_event.v1"
QUARANTINE_RECORD_SCHEMA = "libreevolve.strict_jsonl_quarantine_diagnostic.v1"
PAPER_ARTIFACT_SUBPATH_SCHEMA = "libreevolve.paper_artifact_subpaths.v1"
LEGACY_RECORD_POLICY = "missing_schema_version_accepted_as_legacy_v0"
RUN_ARTIFACT_NAMES = frozenset(
    {
        "task_specification.json",
        "evaluator_results.jsonl",
        "history.jsonl",
        "history_invalid.jsonl",
        "failure_history.jsonl",
        "failure_history_invalid.jsonl",
        "archive_events.jsonl",
        "archive_events_invalid.jsonl",
        "controller_budget_events.jsonl",
        "controller_budget_events_invalid.jsonl",
        "llm_calls.jsonl",
        "llm_calls_invalid.jsonl",
        "prompt_history.jsonl",
        "prompt_history_invalid.jsonl",
        "prompt_current_binding_table.jsonl",
        "prompt_prior_score_table.jsonl",
        "manifest.json",
        "manifest_invalid.jsonl",
        "best.py",
        "best_workspace",
        "evaluator_artifacts",
        "plugin_artifacts",
        "paper_artifacts",
    }
)

_JSONL_ARTIFACT_OWNERS = {
    "history.jsonl": (
        "ProgramDatabase.log",
        "show inspection, archive restore, lineage reports, and paper validators",
    ),
    "evaluator_results.jsonl": (
        "CascadeEvaluator result logging",
        "runtime reports, evaluator joins, and paper validators",
    ),
    "failure_history.jsonl": (
        "ProgramDatabase failure logging",
        "prompt failure memory, proposal audits, and paper validators",
    ),
    "archive_events.jsonl": (
        "ProgramDatabase archive admission logging",
        "archive replay audits, restore checks, and paper validators",
    ),
    "controller_budget_events.jsonl": (
        "RunBudget controller-event logging",
        "budget restore, controller-state audits, and paper validators",
    ),
    "llm_calls.jsonl": (
        "LLM call logger",
        "budget accounting, provider diagnostics, and paper validators",
    ),
    "prompt_history.jsonl": (
        "PromptDatabase",
        "prompt reports, prompt-table exports, and paper validators",
    ),
    "prompt_current_binding_table.jsonl": (
        "prompt current-binding table finalizer",
        "prompt current-binding reports and cross-run analysis",
    ),
    "prompt_prior_score_table.jsonl": (
        "prompt prior-score table finalizer",
        "prompt prior-score reports and cross-run analysis",
    ),
}

_JSONL_IMPLEMENTATION_ANCHORS = {
    "history.jsonl": {
        "writer": [
            {
                "path": "libreevolve/core/database.py",
                "required_text": 'self._jsonl = run_dir / "history.jsonl"',
            },
            {
                "path": "libreevolve/core/database.py",
                "required_text": "self._jsonl,",
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "for name in sorted(RUN_ARTIFACT_NAMES)",
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/cli.py",
                "required_text": "def _iter_history_records",
            },
            {
                "path": "libreevolve/core/database.py",
                "required_text": "def load_archive_restore_bundle",
            },
        ],
    },
    "evaluator_results.jsonl": {
        "writer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "def _write_evaluator_results",
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_text": 'path = run_dir / "evaluator_results.jsonl"',
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "for name in sorted(RUN_ARTIFACT_NAMES)",
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "candidate_id_to_evaluator_results_jsonl_row",
            }
        ],
    },
    "failure_history.jsonl": {
        "writer": [
            {
                "path": "libreevolve/core/database.py",
                "required_text": 'self._failures = run_dir / "failure_history.jsonl"',
            },
            {
                "path": "libreevolve/core/database.py",
                "required_text": "def log_failure",
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "for name in sorted(RUN_ARTIFACT_NAMES)",
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/core/database.py",
                "required_text": "def load_failure_history_records",
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "failure_history.jsonl",
            },
        ],
    },
    "archive_events.jsonl": {
        "writer": [
            {
                "path": "libreevolve/core/database.py",
                "required_text": 'self._archive_events = run_dir / "archive_events.jsonl"',
            },
            {
                "path": "libreevolve/core/database.py",
                "required_text": "def _log_archive_event",
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "for name in sorted(RUN_ARTIFACT_NAMES)",
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/core/database.py",
                "required_text": "def load_archive_event_records",
            },
            {
                "path": "libreevolve/core/database.py",
                "required_text": "def archive_event_replay_audit",
            },
        ],
    },
    "controller_budget_events.jsonl": {
        "writer": [
            {
                "path": "libreevolve/core/database.py",
                "required_text": (
                    'self._controller_budget_events = run_dir / '
                    '"controller_budget_events.jsonl"'
                ),
            },
            {
                "path": "libreevolve/core/database.py",
                "required_text": "def log_controller_budget_event",
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "for name in sorted(RUN_ARTIFACT_NAMES)",
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "def _load_controller_budget_events_restore_stream",
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "def _process_controller_event_rows_by_kind",
            },
        ],
    },
    "llm_calls.jsonl": {
        "writer": [
            {
                "path": "libreevolve/core/database.py",
                "required_text": 'self._llm_calls = run_dir / "llm_calls.jsonl"',
            },
            {
                "path": "libreevolve/core/database.py",
                "required_text": "def log_llm_call",
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "for name in sorted(RUN_ARTIFACT_NAMES)",
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "def _process_llm_call_rows_by_id",
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "llm_calls_jsonl_row_join_when_provider_ledger_absent",
            },
        ],
    },
    "prompt_history.jsonl": {
        "writer": [
            {
                "path": "libreevolve/core/meta_prompt.py",
                "required_text": 'self._log_path = Path(log_dir) / "prompt_history.jsonl"',
            },
            {
                "path": "libreevolve/core/meta_prompt.py",
                "required_text": "append_strict_jsonl(",
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "for name in sorted(RUN_ARTIFACT_NAMES)",
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/core/meta_prompt.py",
                "required_text": "def load_prompt_history_records",
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "prompt_history_rows_by_event_and_prompt_program_id",
            },
        ],
    },
    "prompt_current_binding_table.jsonl": {
        "writer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "def _write_prompt_current_binding_table",
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_text": 'table_path = run_dir / "prompt_current_binding_table.jsonl"',
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "for name in sorted(RUN_ARTIFACT_NAMES)",
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "def validate_prompt_current_binding_report",
            }
        ],
    },
    "prompt_prior_score_table.jsonl": {
        "writer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "def _write_prompt_prior_score_table",
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_text": 'table_path = run_dir / "prompt_prior_score_table.jsonl"',
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "for name in sorted(RUN_ARTIFACT_NAMES)",
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "def validate_prompt_prior_score_provenance_report",
            }
        ],
    },
}

_QUARANTINE_PATH_ANCHORS = {
    "history_invalid.jsonl": {
        "path": "libreevolve/core/database.py",
        "required_text": 'self._quarantine = run_dir / "history_invalid.jsonl"',
    },
    "failure_history_invalid.jsonl": {
        "path": "libreevolve/core/database.py",
        "required_text": 'self._failure_quarantine = run_dir / "failure_history_invalid.jsonl"',
    },
    "archive_events_invalid.jsonl": {
        "path": "libreevolve/core/database.py",
        "required_text": 'self._archive_event_quarantine = run_dir / "archive_events_invalid.jsonl"',
    },
    "controller_budget_events_invalid.jsonl": {
        "path": "libreevolve/core/database.py",
        "required_text": (
            'run_dir / "controller_budget_events_invalid.jsonl"'
        ),
    },
    "llm_calls_invalid.jsonl": {
        "path": "libreevolve/core/database.py",
        "required_text": 'self._llm_call_quarantine = run_dir / "llm_calls_invalid.jsonl"',
    },
    "prompt_history_invalid.jsonl": {
        "path": "libreevolve/core/meta_prompt.py",
        "required_text": 'self._quarantine_path = Path(log_dir) / "prompt_history_invalid.jsonl"',
    },
    "manifest_invalid.jsonl": {
        "path": "libreevolve/core/database.py",
        "required_text": 'self._manifest_quarantine = run_dir / "manifest_invalid.jsonl"',
    },
}

_QUARANTINE_COMMON_IMPLEMENTATION_ANCHORS = {
    "writer": [
        {
            "path": "libreevolve/core/jsonl.py",
            "required_text": "def append_quarantine_record",
        },
        {
            "path": "libreevolve/core/jsonl.py",
            "required_text": "validate_quarantine_record",
        },
    ],
    "runtime_pointer": [
        {
            "path": "libreevolve/core/loop.py",
            "required_text": "for name in sorted(RUN_ARTIFACT_NAMES)",
        }
    ],
    "show_restore_reader": [
        {
            "path": "libreevolve/core/jsonl.py",
            "required_text": "def iter_quarantine_records",
        },
        {
            "path": "libreevolve/core/artifact_schema.py",
            "required_text": "quarantine_jsonl_records",
        },
    ],
}

_RUN_ARTIFACT_DOCUMENTATION_ANCHORS = {
    "history.jsonl": "`history.jsonl`",
    "history_invalid.jsonl": "`history_invalid.jsonl`",
    "failure_history.jsonl": "`failure_history.jsonl`",
    "failure_history_invalid.jsonl": "`failure_history_invalid.jsonl`",
    "archive_events.jsonl": "`archive_events.jsonl`",
    "archive_events_invalid.jsonl": "`archive_events_invalid.jsonl`",
    "controller_budget_events.jsonl": "`controller_budget_events.jsonl`",
    "controller_budget_events_invalid.jsonl": (
        "`controller_budget_events_invalid.jsonl`"
    ),
    "llm_calls.jsonl": "`llm_calls.jsonl`",
    "llm_calls_invalid.jsonl": "`llm_calls_invalid.jsonl`",
    "prompt_history.jsonl": "`prompt_history.jsonl`",
    "prompt_history_invalid.jsonl": "`prompt_history_invalid.jsonl`",
    "prompt_current_binding_table.jsonl": "`prompt_current_binding_table.jsonl`",
    "prompt_prior_score_table.jsonl": "`prompt_prior_score_table.jsonl`",
    "task_specification.json": "`task_specification.json`",
    "evaluator_results.jsonl": "`evaluator_results.jsonl`",
    "manifest.json": "`manifest.json`",
    "manifest_invalid.jsonl": "`manifest_invalid.jsonl`",
    "best.py": "`best.py`",
    "best_workspace": "`best_workspace/`",
    "evaluator_artifacts": "`evaluator_artifacts/`",
    "plugin_artifacts": "`plugin_artifacts/`",
    "paper_artifacts": "`paper_artifacts/`",
}

_NON_JSONL_RESTORE_SHOW_HANDLING = {
    "manifest.json": "primary show and restore input",
    "task_specification.json": "resolved by task-spec artifact report",
    "best.py": "show summary and best-artifact export",
    "best_workspace": "show summary and best-artifact export",
    "evaluator_artifacts": "runtime artifact summary and evaluator report inspection",
    "plugin_artifacts": "plugin artifact manifest and show inspection",
    "paper_artifacts": "paper-source report validators and docs",
}

_COMMON_BEHAVIOR_TEST_ANCHORS = {
    "inventory_contract": [
        {
            "path": "tests/population/test_database.py",
            "required_text": (
                "def test_generated_run_artifact_inventory_covers_cleanup_"
                "and_schema_surfaces"
            ),
        }
    ],
    "overwrite_cleanup": [
        {
            "path": "tests/population/test_database.py",
            "required_text": (
                "def test_database_overwrite_clears_known_run_artifacts_only"
            ),
        }
    ],
    "show_bundle_behavior": [
        {
            "path": "tests/test_cli.py",
            "required_text": "def test_show_reports_quarantine_stream_summary",
        },
        {
            "path": "tests/test_cli.py",
            "required_text": "def test_show_reports_paper_artifact_lifecycle_summary",
        },
    ],
}

_NON_JSONL_BEHAVIOR_TEST_ANCHORS = {
    "show_policy": [
        {
            "path": "tests/test_cli.py",
            "required_text": (
                "def test_show_rejects_non_jsonl_artifact_policy_drift"
            ),
        }
    ],
    "restore_policy": [
        {
            "path": "tests/test_cli.py",
            "required_text": (
                "def test_run_rejects_non_jsonl_artifact_policy_drift_"
                "before_restore"
            ),
        }
    ],
}

_QUARANTINE_BEHAVIOR_TEST_ANCHORS = {
    "show_diagnostic_behavior": [
        {
            "path": "tests/test_cli.py",
            "required_text": "def test_show_reports_quarantine_stream_summary",
        },
        {
            "path": "tests/test_cli.py",
            "required_text": "def test_show_rejects_malformed_quarantine_stream",
        },
    ],
    "restore_diagnostic_behavior": [
        {
            "path": "tests/test_cli.py",
            "required_text": (
                "def test_run_rejects_quarantine_artifact_drift_before_restore"
            ),
        },
        {
            "path": "tests/core/test_loop.py",
            "required_text": (
                "def test_direct_runtime_restore_loaders_reject_"
                "quarantine_policy_drift"
            ),
        },
        {
            "path": "tests/population/test_database.py",
            "required_text": (
                "def test_direct_archive_restore_loaders_reject_"
                "quarantine_policy_drift"
            ),
        },
    ],
}

_RUN_ARTIFACT_BEHAVIOR_TEST_ANCHORS = {
    "prompt_current_binding_table.jsonl": {
        "emitted_row_behavior": [
            {
                "path": "tests/core/test_loop.py",
                "required_text": (
                    "def test_runtime_history_reports_prompt_current_binding_"
                    "for_diff_mutation"
                ),
            }
        ],
    },
    "prompt_prior_score_table.jsonl": {
        "emitted_row_behavior": [
            {
                "path": "tests/core/test_loop.py",
                "required_text": (
                    "def test_runtime_history_reports_prompt_current_binding_"
                    "for_diff_mutation"
                ),
            }
        ],
    },
    "paper_artifacts": {
        "emitted_path_behavior": [
            {
                "path": "tests/core/test_loop.py",
                "required_text": (
                    "def test_runtime_history_reports_marker_spelling_"
                    "provenance"
                ),
            }
        ],
        "show_behavior": [
            {
                "path": "tests/test_cli.py",
                "required_text": (
                    "def test_show_reports_paper_artifact_lifecycle_summary"
                ),
            },
            {
                "path": "tests/test_cli.py",
                "required_text": (
                    "def test_show_rejects_paper_artifact_lifecycle_drift"
                ),
            },
        ],
        "restore_behavior": [
            {
                "path": "tests/test_cli.py",
                "required_text": (
                    "def test_run_rejects_paper_artifact_lifecycle_drift_"
                    "before_restore"
                ),
            }
        ],
    },
}

_NON_JSONL_IMPLEMENTATION_ANCHORS = {
    "manifest.json": {
        "writer": [
            {
                "path": "libreevolve/core/database.py",
                "required_text": "def _write_manifest",
            },
            {
                "path": "libreevolve/core/database.py",
                "required_text": "strict_json_dump(manifest, self._manifest",
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "def _manifest_artifact_pointer",
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/cli.py",
                "required_text": "def _read_show_manifest",
            },
            {
                "path": "libreevolve/core/database.py",
                "required_text": "def load_archive_restore_bundle",
            },
        ],
    },
    "task_specification.json": {
        "writer": [
            {
                "path": "libreevolve/core/database.py",
                "required_text": (
                    'self._task_specification_artifact = run_dir / '
                    '"task_specification.json"'
                ),
            },
            {
                "path": "libreevolve/core/database.py",
                "required_text": "self._task_specification_artifact,",
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "for name in sorted(RUN_ARTIFACT_NAMES)",
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "def _task_spec_artifact_resolution_report",
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_text": '"standalone_task_specification"',
            },
        ],
    },
    "best.py": {
        "writer": [
            {
                "path": "libreevolve/core/best_artifacts.py",
                "required_text": 'best_py = run_dir / "best.py"',
            },
            {
                "path": "libreevolve/core/best_artifacts.py",
                "required_text": 'artifacts["best.py"] = paths["best.py"]',
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/best_artifacts.py",
                "required_text": '"best.py": _best_artifact_path_record',
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/cli.py",
                "required_text": "--- Best program ---",
            }
        ],
    },
    "best_workspace": {
        "writer": [
            {
                "path": "libreevolve/core/best_artifacts.py",
                "required_text": 'workspace_dir = run_dir / "best_workspace"',
            },
            {
                "path": "libreevolve/core/best_artifacts.py",
                "required_text": (
                    'artifacts["best_workspace"] = paths["best_workspace"]'
                ),
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/best_artifacts.py",
                "required_text": '"best_workspace": _best_artifact_path_record',
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/cli.py",
                "required_text": "--- Best workspace ---",
            }
        ],
    },
    "evaluator_artifacts": {
        "writer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": 'artifact_dir=run_dir / "evaluator_artifacts"',
            }
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "def _runtime_artifact_pointers",
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/cli.py",
                "required_text": "def _validator_boundary_artifact_summary",
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_text": '"evaluator_artifacts": ["evaluator_copy_out"]',
            },
        ],
    },
    "plugin_artifacts": {
        "writer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "def _plugin_artifact_manifest",
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_text": 'runtime["plugin_artifacts"] = plugin_artifacts',
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "def _runtime_artifact_pointers",
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "include_plugin_artifacts",
            }
        ],
    },
    "paper_artifacts": {
        "writer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": 'run_dir / "paper_artifacts" / "marker_spelling"',
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "paper_artifacts/process_exhibit",
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "paper_artifacts/table1_capability_comparison",
            },
        ],
        "runtime_pointer": [
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "def _process_exhibit_artifact_evidence",
            }
        ],
        "show_restore_reader": [
            {
                "path": "libreevolve/tools/paper_manifest.py",
                "required_text": "TASK_SPECIFICATION_BOUNDARY_FILE",
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_text": "validate_alphaevolve_process_exhibit_report",
            },
        ],
    },
}

_PAPER_ARTIFACT_SUBPATH_SCHEMA = {
    "schema": PAPER_ARTIFACT_SUBPATH_SCHEMA,
    "root_artifact": "paper_artifacts",
    "root_schema_pointer": 'artifact_schema.non_jsonl_artifacts["paper_artifacts"]',
    "families": {
        "marker_spelling": {
            "directory": "paper_artifacts/marker_spelling",
            "runtime_report": "runtime.history.marker_spelling_provenance_report",
            "runtime_report_schema": "libreevolve.marker_spelling_provenance_report.v1",
            "source_artifact_schema": "libreevolve.marker_spelling_source_artifacts.v1",
            "writer_anchor": "libreevolve.core.loop._marker_spelling_source_artifacts",
            "path_records": [
                {
                    "path": "paper_artifacts/marker_spelling/alphaevolve_page_4_text.txt",
                    "artifact_kind": "pypdf_page_text_extract",
                    "hash_policy": "sha256_utf8_text_payload",
                },
                {
                    "path": "paper_artifacts/marker_spelling/alphaevolve_page_6_text.txt",
                    "artifact_kind": "pypdf_page_text_extract",
                    "hash_policy": "sha256_utf8_text_payload",
                },
                {
                    "path": (
                        "paper_artifacts/marker_spelling/"
                        "alphaevolve_figure_3a_marker_text.txt"
                    ),
                    "artifact_kind": "pypdf_figure_3a_marker_line_extract",
                    "hash_policy": "sha256_utf8_text_payload",
                },
            ],
        },
        "process_exhibit": {
            "directory": "paper_artifacts/process_exhibit",
            "runtime_report": "runtime.history.alphaevolve_process_exhibit_report",
            "runtime_report_schema": "libreevolve.alphaevolve_process_exhibit_report.v1",
            "writer_anchor": "libreevolve.core.loop._write_process_exhibit_artifact",
            "hash_scope": "generated_process_exhibit_text_artifact",
            "path_records": [
                {
                    "path": "paper_artifacts/process_exhibit/figure_1.mmd",
                    "artifact_kind": "mermaid_source",
                },
                {
                    "path": "paper_artifacts/process_exhibit/figure_1_accessibility.txt",
                    "artifact_kind": "accessibility_text",
                },
                {
                    "path": "paper_artifacts/process_exhibit/figure_2.mmd",
                    "artifact_kind": "mermaid_source",
                },
                {
                    "path": "paper_artifacts/process_exhibit/figure_2_accessibility.txt",
                    "artifact_kind": "accessibility_text",
                },
                {
                    "path": (
                        "paper_artifacts/process_exhibit/"
                        "source_alphaevolve_figure_1_page_3_text.txt"
                    ),
                    "artifact_kind": "source_pdf_page_text_extract",
                    "hash_scope": "source_pdf_page_text_extract",
                },
                {
                    "path": (
                        "paper_artifacts/process_exhibit/"
                        "source_alphaevolve_figure_2_page_4_text.txt"
                    ),
                    "artifact_kind": "source_pdf_page_text_extract",
                    "hash_scope": "source_pdf_page_text_extract",
                },
            ],
        },
        "table1_capability_comparison": {
            "directory": "paper_artifacts/table1_capability_comparison",
            "runtime_report": (
                "runtime.history.alphaevolve_table1_capability_exhibit_report"
            ),
            "runtime_report_schema": (
                "libreevolve.alphaevolve_table1_capability_exhibit_report.v1"
            ),
            "writer_anchor": (
                "libreevolve.core.loop._write_alphaevolve_table1_artifact"
            ),
            "hash_scope": "generated_table1_capability_exhibit_text_artifact",
            "path_records": [
                {
                    "path": (
                        "paper_artifacts/table1_capability_comparison/table_1.md"
                    ),
                    "artifact_kind": "markdown_table",
                },
                {
                    "path": (
                        "paper_artifacts/table1_capability_comparison/"
                        "table_1_accessibility.txt"
                    ),
                    "artifact_kind": "accessibility_text",
                },
            ],
        },
    },
}


def paper_artifact_subpath_schema() -> dict:
    return deepcopy(_PAPER_ARTIFACT_SUBPATH_SCHEMA)


def paper_artifact_subpath_paths() -> set[str]:
    return {
        record["path"]
        for family in _PAPER_ARTIFACT_SUBPATH_SCHEMA["families"].values()
        for record in family["path_records"]
    }


def validate_paper_artifact_lifecycle_manifest(
    manifest: object,
    *,
    run_artifacts_doc_text: str | None = None,
) -> dict:
    """Validate a manifest's paper_artifacts runtime paths against schema.

    This is deliberately a bundle-level check: it joins the manifest artifact
    schema, generated root artifact pointer, and runtime history reports that
    emit paper_artifacts/... subpaths.
    """
    issues: list[dict[str, str]] = []
    schema = "libreevolve.paper_artifact_lifecycle_manifest_validation.v1"
    if not isinstance(manifest, Mapping):
        return {
            "schema": schema,
            "ok": False,
            "issues": [
                {
                    "code": "invalid_manifest",
                    "message": "manifest must be an object",
                }
            ],
        }
    artifact_schema = manifest.get("artifact_schema")
    if not isinstance(artifact_schema, Mapping):
        issues.append(
            {
                "code": "missing_artifact_schema",
                "message": "manifest.artifact_schema must be an object",
            }
        )
        artifact_schema = {}
    if artifact_schema.get("paper_artifact_subpaths") != paper_artifact_subpath_schema():
        issues.append(
            {
                "code": "paper_artifact_subpath_schema_drift",
                "message": "manifest artifact schema must include current paper artifact subpaths",
            }
        )
    inventory = artifact_schema.get("generated_artifact_inventory")
    paper_inventory = (
        inventory.get("paper_artifacts") if isinstance(inventory, Mapping) else None
    )
    if not isinstance(paper_inventory, Mapping):
        issues.append(
            {
                "code": "missing_paper_artifacts_inventory",
                "message": "generated artifact inventory must include paper_artifacts",
            }
        )
    else:
        if paper_inventory.get("subpath_schema_pointer") != (
            "artifact_schema.paper_artifact_subpaths"
        ):
            issues.append(
                {
                    "code": "missing_paper_subpath_schema_pointer",
                    "message": "paper_artifacts inventory must point to subpath schema",
                }
            )
        if paper_inventory.get("cleanup_managed") is not True:
            issues.append(
                {
                    "code": "paper_artifacts_cleanup_not_managed",
                    "message": "paper_artifacts inventory must be cleanup-managed",
                }
            )
    runtime = manifest.get("runtime")
    if not isinstance(runtime, Mapping):
        issues.append(
            {
                "code": "missing_runtime",
                "message": "manifest.runtime must be an object",
            }
        )
        runtime = {}
    artifacts = runtime.get("artifacts")
    paper_pointer = (
        artifacts.get("paper_artifacts") if isinstance(artifacts, Mapping) else None
    )
    if not isinstance(paper_pointer, Mapping):
        issues.append(
            {
                "code": "missing_runtime_paper_artifacts_pointer",
                "message": "runtime.artifacts must include paper_artifacts",
            }
        )
    else:
        if paper_pointer.get("path") != "paper_artifacts":
            issues.append(
                {
                    "code": "invalid_runtime_paper_artifacts_path",
                    "message": "runtime paper_artifacts pointer must use paper_artifacts path",
                }
            )
        if paper_pointer.get("present") is True:
            if paper_pointer.get("kind") != "directory":
                issues.append(
                    {
                        "code": "invalid_runtime_paper_artifacts_kind",
                        "message": "present paper_artifacts pointer must be a directory",
                    }
                )
            if not isinstance(paper_pointer.get("tree_hash"), str):
                issues.append(
                    {
                        "code": "missing_runtime_paper_artifacts_tree_hash",
                        "message": "present paper_artifacts pointer must include tree_hash",
                    }
                )
    history = runtime.get("history")
    if not isinstance(history, Mapping):
        issues.append(
            {
                "code": "missing_runtime_history",
                "message": "runtime.history must be an object",
            }
        )
        history = {}
    expected_paths = paper_artifact_subpath_paths()
    emitted_paths = _paper_artifact_paths_from_runtime_history(history)
    unknown_paths = sorted(emitted_paths - expected_paths)
    missing_paths = sorted(expected_paths - emitted_paths)
    documented_refs: list[str] = []
    missing_doc_paths: list[str] = []
    unknown_doc_refs: list[str] = []
    if run_artifacts_doc_text is not None:
        documented_refs = _paper_artifact_doc_refs(run_artifacts_doc_text)
        documented_exact_paths = {
            ref
            for ref in documented_refs
            if _paper_artifact_doc_ref_kind(ref, expected_paths) == "exact_path"
        }
        missing_doc_paths = sorted(expected_paths - documented_exact_paths)
        unknown_doc_refs = sorted(
            ref
            for ref in documented_refs
            if _paper_artifact_doc_ref_kind(ref, expected_paths) == "unknown"
        )
    if unknown_paths:
        issues.append(
            {
                "code": "unknown_paper_artifact_paths",
                "message": "runtime reports emitted paper_artifacts paths outside schema",
            }
        )
    if missing_paths:
        issues.append(
            {
                "code": "missing_paper_artifact_schema_paths",
                "message": "runtime reports did not emit every schema-declared paper artifact path",
            }
        )
    if missing_doc_paths:
        issues.append(
            {
                "code": "missing_paper_artifact_doc_paths",
                "message": "run-artifacts guide does not document every schema-declared paper artifact path",
            }
        )
    if unknown_doc_refs:
        issues.append(
            {
                "code": "unknown_paper_artifact_doc_refs",
                "message": "run-artifacts guide references paper_artifacts paths outside schema",
            }
        )
    return {
        "schema": schema,
        "ok": not issues,
        "issues": issues,
        "expected_path_count": len(expected_paths),
        "emitted_path_count": len(emitted_paths),
        "expected_paths": sorted(expected_paths),
        "emitted_paths": sorted(emitted_paths),
        "unknown_paths": unknown_paths,
        "missing_paths": missing_paths,
        "documented_refs": documented_refs,
        "missing_doc_paths": missing_doc_paths,
        "unknown_doc_refs": unknown_doc_refs,
    }


def validate_non_jsonl_artifact_policy_manifest(manifest: object) -> dict:
    """Validate runtime non-JSONL artifact pointers against schema policies."""
    schema = "libreevolve.non_jsonl_artifact_policy_manifest_validation.v1"
    issues: list[dict[str, str]] = []
    if not isinstance(manifest, Mapping):
        return {
            "schema": schema,
            "ok": False,
            "issues": [
                {
                    "code": "invalid_manifest",
                    "message": "manifest must be an object",
                }
            ],
        }
    artifact_schema = manifest.get("artifact_schema")
    if not isinstance(artifact_schema, Mapping):
        issues.append(
            {
                "code": "missing_artifact_schema",
                "message": "manifest.artifact_schema must be an object",
            }
        )
        artifact_schema = {}
    non_jsonl_schema = artifact_schema.get("non_jsonl_artifacts")
    expected_schema = run_artifact_schema()["non_jsonl_artifacts"]
    if non_jsonl_schema != expected_schema:
        issues.append(
            {
                "code": "non_jsonl_artifact_schema_drift",
                "message": "manifest non-JSONL artifact schema drifted",
            }
        )
        non_jsonl_schema = expected_schema
    runtime = manifest.get("runtime")
    if not isinstance(runtime, Mapping):
        issues.append(
            {
                "code": "missing_runtime",
                "message": "manifest.runtime must be an object",
            }
        )
        runtime = {}
    runtime_artifacts = runtime.get("artifacts")
    if not isinstance(runtime_artifacts, Mapping):
        issues.append(
            {
                "code": "missing_runtime_artifacts",
                "message": "manifest.runtime.artifacts must be an object",
            }
        )
        runtime_artifacts = {}
    checked_records: list[dict[str, object]] = []
    for name, expected in non_jsonl_schema.items():
        pointer = runtime_artifacts.get(name)
        if not isinstance(pointer, Mapping):
            issues.append(
                {
                    "code": "missing_non_jsonl_runtime_pointer",
                    "message": f"runtime.artifacts missing {name}",
                }
            )
            continue
        checked_records.append(
            {
                "name": name,
                "hash_policy": expected.get("hash_policy"),
                "present": pointer.get("present"),
                "kind": pointer.get("kind"),
            }
        )
        _validate_non_jsonl_pointer_policy(name, expected, pointer, issues)
    return {
        "schema": schema,
        "ok": not issues,
        "issues": issues,
        "checked_artifact_count": len(checked_records),
        "checked_artifacts": checked_records,
    }


def validate_quarantine_artifact_policy_manifest(
    manifest: object,
    *,
    run_dir: str | Path,
) -> dict:
    """Validate manifest-advertised quarantine streams as diagnostics."""
    schema = "libreevolve.quarantine_artifact_policy_manifest_validation.v1"
    issues: list[dict[str, str]] = []
    present_streams: list[str] = []
    record_count = 0
    if not isinstance(manifest, Mapping):
        return {
            "schema": schema,
            "ok": False,
            "issues": [
                {
                    "code": "invalid_manifest",
                    "message": "manifest must be an object",
                }
            ],
            "checked_stream_count": 0,
            "record_count": 0,
            "present_streams": [],
        }
    artifact_schema = manifest.get("artifact_schema")
    if not isinstance(artifact_schema, Mapping):
        return {
            "schema": schema,
            "ok": True,
            "issues": [],
            "checked_stream_count": 0,
            "record_count": 0,
            "present_streams": [],
        }
    quarantine_schema = artifact_schema.get("quarantine_jsonl_records")
    if quarantine_schema is None:
        return {
            "schema": schema,
            "ok": True,
            "issues": [],
            "checked_stream_count": 0,
            "record_count": 0,
            "present_streams": [],
        }
    expected_schema = run_artifact_schema()["quarantine_jsonl_records"]
    if quarantine_schema != expected_schema:
        issues.append(
            {
                "code": "quarantine_artifact_schema_drift",
                "message": "manifest quarantine artifact schema drifted",
            }
        )
        quarantine_schema = expected_schema
    if not isinstance(quarantine_schema, Mapping):
        issues.append(
            {
                "code": "invalid_quarantine_artifact_schema",
                "message": "manifest quarantine artifact schema must be an object",
            }
        )
        quarantine_schema = {}
    root = Path(run_dir)
    for stream_name in sorted(quarantine_schema):
        if not isinstance(stream_name, str) or not stream_name:
            issues.append(
                {
                    "code": "invalid_quarantine_stream_name",
                    "message": "quarantine stream names must be non-empty strings",
                }
            )
            continue
        path = root / stream_name
        if not path.exists():
            continue
        try:
            stream_count = sum(
                1
                for _ in iter_quarantine_records(
                    path,
                    stream_name=stream_name,
                )
            )
        except StrictJsonlError as exc:
            issues.append(
                {
                    "code": "invalid_quarantine_stream_rows",
                    "message": f"{stream_name}: {exc}",
                }
            )
            continue
        present_streams.append(stream_name)
        record_count += stream_count
    return {
        "schema": schema,
        "ok": not issues,
        "issues": issues,
        "checked_stream_count": len(present_streams),
        "record_count": record_count,
        "present_streams": present_streams,
    }


def validate_run_artifact_bundle_report(report: object) -> dict:
    issues: list[dict[str, str]] = []
    if not isinstance(report, Mapping):
        return {
            "schema": "libreevolve.run_artifact_bundle_report_validation.v1",
            "ok": False,
            "issues": [
                {"code": "invalid_report", "message": "report must be an object"}
            ],
        }
    if report.get("schema") != "libreevolve.run_artifact_bundle_report.v1":
        issues.append({"code": "invalid_schema", "message": "invalid report schema"})
    if not isinstance(report.get("accepted_stream_count"), int) or isinstance(
        report.get("accepted_stream_count"), bool
    ):
        issues.append(
            {
                "code": "invalid_accepted_stream_count",
                "message": "accepted stream count must be an integer",
            }
        )
    streams = report.get("accepted_streams")
    if not isinstance(streams, list) or not all(
        isinstance(item, str) and item for item in streams
    ):
        issues.append(
            {
                "code": "invalid_accepted_streams",
                "message": "accepted streams must be a list of names",
            }
        )
        streams = []
    if (
        isinstance(report.get("accepted_stream_count"), int)
        and not isinstance(report.get("accepted_stream_count"), bool)
        and report["accepted_stream_count"] != len(streams)
    ):
        issues.append(
            {
                "code": "accepted_stream_count_mismatch",
                "message": "accepted stream count must match accepted streams",
            }
        )
    for field in (
        "quarantine_stream_count",
        "quarantine_record_count",
        "non_jsonl_checked_artifact_count",
        "paper_artifact_emitted_path_count",
    ):
        value = report.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            issues.append(
                {
                    "code": f"invalid_{field}",
                    "message": f"{field} must be non-negative integer",
                }
            )
    for field in (
        "quarantine_validation_ok",
        "non_jsonl_validation_ok",
        "paper_artifact_lifecycle_checked",
    ):
        if not isinstance(report.get(field), bool):
            issues.append(
                {"code": f"invalid_{field}", "message": f"{field} must be boolean"}
            )
    paper_ok = report.get("paper_artifact_validation_ok")
    if paper_ok not in {None, True, False}:
        issues.append(
            {
                "code": "invalid_paper_artifact_validation_ok",
                "message": "paper artifact validation status must be boolean or null",
            }
        )
    boundary = report.get("accepted_state_boundary")
    if not isinstance(boundary, Mapping):
        issues.append(
            {
                "code": "invalid_accepted_state_boundary",
                "message": "accepted state boundary must be an object",
            }
        )
    else:
        if boundary.get("quarantine_rows_are_diagnostics") is not True:
            issues.append(
                {
                    "code": "quarantine_diagnostic_boundary_missing",
                    "message": "quarantine rows must remain diagnostics",
                }
            )
        for field in (
            "quarantine_rows_replayed_as_state",
            "provider_output_replay",
            "pending_controller_work_replay",
        ):
            if boundary.get(field) is not False:
                issues.append(
                    {
                        "code": f"{field}_overclaim",
                        "message": f"{field} must remain false",
                    }
                )
    if report.get("claim_ready") is not False:
        issues.append(
            {
                "code": "claim_ready_overclaim",
                "message": "bundle report is not full replay certification",
            }
        )
    readiness = report.get("claim_readiness")
    if not isinstance(readiness, Mapping):
        issues.append(
            {
                "code": "invalid_claim_readiness",
                "message": "claim readiness must be an object",
            }
        )
    elif readiness.get("full_restore_replay_certification") is not False:
        issues.append(
            {
                "code": "full_replay_certification_overclaim",
                "message": "full restore replay certification must remain false",
            }
        )
    report_issue_codes = [issue["code"] for issue in issues]
    promotion_gate = report.get("promotion_gate")
    if promotion_gate is not None:
        if not isinstance(promotion_gate, Mapping):
            issues.append(
                {
                    "code": "invalid_promotion_gate",
                    "message": "promotion gate must be an object",
                }
            )
        else:
            if (
                promotion_gate.get("schema")
                != "libreevolve.run_artifact_bundle_promotion_gate.v1"
            ):
                issues.append(
                    {
                        "code": "invalid_promotion_gate_schema",
                        "message": "promotion gate schema changed",
                    }
                )
            status = promotion_gate.get("status")
            if status not in {"passed", "failed"}:
                issues.append(
                    {
                        "code": "invalid_promotion_gate_status",
                        "message": "promotion gate status must be passed or failed",
                    }
                )
            validation_ok = promotion_gate.get("validation_ok")
            if not isinstance(validation_ok, bool):
                issues.append(
                    {
                        "code": "invalid_promotion_gate_validation_ok",
                        "message": "promotion gate validation_ok must be boolean",
                    }
                )
            elif status == "passed" and validation_ok is not True:
                issues.append(
                    {
                        "code": "promotion_gate_passed_without_validation",
                        "message": "passed promotion gate must have validation_ok true",
                    }
                )
            elif status == "failed" and validation_ok is not False:
                issues.append(
                    {
                        "code": "promotion_gate_failed_with_validation",
                        "message": "failed promotion gate must have validation_ok false",
                    }
                )
            if status == "passed" and report_issue_codes:
                issues.append(
                    {
                        "code": "promotion_gate_passed_with_report_issues",
                        "message": "passed promotion gate must not mask report issues",
                    }
                )
            if status == "failed" and not report_issue_codes:
                issues.append(
                    {
                        "code": "promotion_gate_failed_without_report_issues",
                        "message": "failed promotion gate must correspond to report issues",
                    }
                )
            gate_issue_codes = promotion_gate.get("issue_codes")
            if not isinstance(gate_issue_codes, list) or not all(
                isinstance(code, str) and code for code in gate_issue_codes
            ):
                issues.append(
                    {
                        "code": "invalid_promotion_gate_issue_codes",
                        "message": "promotion gate issue_codes must be a list of names",
                    }
                )
            elif status == "passed" and gate_issue_codes:
                issues.append(
                    {
                        "code": "promotion_gate_passed_with_issues",
                        "message": "passed promotion gate must not list issues",
                    }
                )
            elif status == "failed" and set(gate_issue_codes) != set(
                report_issue_codes
            ):
                issues.append(
                    {
                        "code": "promotion_gate_issue_codes_mismatch",
                        "message": "failed promotion gate must list report issue codes",
                    }
                )
            for field in (
                "accepted_state_only",
                "bundle_report_schema_validated",
            ):
                if promotion_gate.get(field) is not True:
                    issues.append(
                        {
                            "code": f"promotion_gate_{field}_missing",
                            "message": f"promotion gate {field} must be true",
                        }
                    )
            for field in (
                "provider_output_replay",
                "pending_controller_work_replay",
                "full_restore_replay_certification",
            ):
                if promotion_gate.get(field) is not False:
                    issues.append(
                        {
                            "code": f"promotion_gate_{field}_overclaim",
                            "message": f"promotion gate {field} must remain false",
                        }
                    )
    return {
        "schema": "libreevolve.run_artifact_bundle_report_validation.v1",
        "ok": not issues,
        "issues": issues,
    }


def _validate_non_jsonl_pointer_policy(
    name: str,
    expected: Mapping,
    pointer: Mapping,
    issues: list[dict[str, str]],
) -> None:
    if pointer.get("path") != expected.get("path"):
        issues.append(
            {
                "code": "non_jsonl_runtime_path_mismatch",
                "message": f"runtime pointer path for {name} does not match schema",
            }
        )
    if pointer.get("present") is not True:
        if expected.get("presence") == "required_startup_manifest_updated_at_runtime":
            issues.append(
                {
                    "code": "required_non_jsonl_artifact_missing",
                    "message": f"required artifact {name} is missing",
                }
            )
        return
    if pointer.get("kind") == "link":
        issues.append(
            {
                "code": "non_jsonl_runtime_pointer_is_link",
                "message": f"runtime pointer for {name} must not be a link",
            }
        )
        return
    policy = expected.get("hash_policy")
    if policy == "self_describing_manifest_not_independently_self_hashed":
        if pointer.get("hash_scope") != "final_manifest_self_reference_deferred":
            issues.append(
                {
                    "code": "invalid_manifest_hash_scope",
                    "message": "manifest pointer must defer final self-reference hash",
                }
            )
        return
    if policy == "file_sha256_when_present":
        if pointer.get("kind") != "file":
            issues.append(
                {
                    "code": "non_jsonl_file_kind_mismatch",
                    "message": f"runtime pointer for {name} must be a file",
                }
            )
        if not _is_sha256_text(pointer.get("sha256")):
            issues.append(
                {
                    "code": "missing_non_jsonl_file_sha256",
                    "message": f"runtime pointer for {name} must include file sha256",
                }
            )
        if pointer.get("hash_scope") not in {None, "file_bytes"}:
            issues.append(
                {
                    "code": "invalid_non_jsonl_file_hash_scope",
                    "message": f"runtime pointer for {name} has invalid file hash scope",
                }
            )
        return
    if policy == "tree_hash_when_present":
        if pointer.get("kind") != "directory":
            issues.append(
                {
                    "code": "non_jsonl_directory_kind_mismatch",
                    "message": f"runtime pointer for {name} must be a directory",
                }
            )
        if pointer.get("tree_hash_status") != "ok":
            issues.append(
                {
                    "code": "invalid_non_jsonl_tree_hash_status",
                    "message": f"runtime pointer for {name} must have ok tree hash",
                }
            )
        if not _is_sha256_text(pointer.get("tree_hash")):
            issues.append(
                {
                    "code": "missing_non_jsonl_tree_hash",
                    "message": f"runtime pointer for {name} must include tree hash",
                }
            )
        if pointer.get("tree_hash_scope") not in {
            "relative_file_paths_and_sha256",
            "best_workspace_file_paths_and_sha256",
        }:
            issues.append(
                {
                    "code": "invalid_non_jsonl_tree_hash_scope",
                    "message": f"runtime pointer for {name} has invalid tree-hash scope",
                }
            )
        return
    issues.append(
        {
            "code": "unknown_non_jsonl_hash_policy",
            "message": f"unknown non-JSONL hash policy for {name}",
        }
    )


def _is_sha256_text(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def _paper_artifact_paths_from_runtime_history(history: Mapping) -> set[str]:
    paths: set[str] = set()
    _collect_paper_artifact_paths(history.get("marker_spelling_provenance_report"), paths)
    _collect_paper_artifact_paths(history.get("alphaevolve_process_exhibit_report"), paths)
    _collect_paper_artifact_paths(
        history.get("alphaevolve_table1_capability_exhibit_report"),
        paths,
    )
    return paths


def _collect_paper_artifact_paths(value: object, paths: set[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in {"path", "artifact_path"} and isinstance(item, str):
                if item.startswith("paper_artifacts/"):
                    paths.add(item)
            _collect_paper_artifact_paths(item, paths)
    elif isinstance(value, list):
        for item in value:
            _collect_paper_artifact_paths(item, paths)


def _paper_artifact_doc_refs(text: str) -> list[str]:
    refs: set[str] = set()
    chunks = text.split("`")
    for index, chunk in enumerate(chunks):
        if index % 2 == 0:
            continue
        if chunk == "paper_artifacts" or chunk.startswith("paper_artifacts/"):
            refs.add(chunk)
    return sorted(refs)


def _paper_artifact_doc_ref_kind(ref: str, expected_paths: set[str]) -> str:
    if ref in {"paper_artifacts", "paper_artifacts/", "paper_artifacts/..."}:
        return "root"
    normalized = ref[:-4] if ref.endswith("/...") else ref
    if normalized.endswith("/"):
        normalized = normalized[:-1]
    if ref in expected_paths:
        return "exact_path"
    if any(path.startswith(f"{normalized}/") for path in expected_paths):
        return "directory"
    return "unknown"


def _quarantine_record(
    source_stream: str,
    source_record_schema: str | dict,
) -> dict:
    return {
        "source_stream": source_stream,
        "source_record_schema": source_record_schema,
        "diagnostic_record_schema": QUARANTINE_RECORD_SCHEMA,
        "diagnostic_fields": {
            "error": "exception class name",
            "message": "bounded redacted serialization or repair diagnostic",
            "record_type": "original record Python type label",
            "record_repr_retention": "redacted|hash_only|off",
            "record_repr": "optional retained rejected-record snapshot",
            "record_repr_truncated": "optional retained snapshot truncation flag",
            "record_repr_error": "optional safe snapshot-construction diagnostic",
        },
        "retention_mode_field": "config.quarantine_snapshot_retention_mode",
        "lifecycle_status": "optional_diagnostic_lifecycle_managed",
    }


def _non_jsonl_artifact(
    *,
    path: str,
    kind: str,
    presence: str,
    writer_owner: str,
    reader_owner: str,
    hash_policy: str,
    runtime_pointer_location: str,
) -> dict:
    return {
        "path": path,
        "kind": kind,
        "presence": presence,
        "writer_owner": writer_owner,
        "reader_owner": reader_owner,
        "hash_policy": hash_policy,
        "lifecycle_status": "known_artifact_collision_checked_and_overwrite_managed",
        "runtime_pointer_location": runtime_pointer_location,
    }


def run_artifact_schema() -> dict:
    schema = _run_artifact_schema_without_inventory()
    return {
        "name": RUN_MANIFEST_SCHEMA,
        "version": ARTIFACT_SCHEMA_VERSION,
        "legacy_record_policy": LEGACY_RECORD_POLICY,
        **schema,
        "paper_artifact_subpaths": paper_artifact_subpath_schema(),
        "generated_artifact_inventory": generated_run_artifact_inventory(),
    }


def generated_run_artifact_inventory() -> dict:
    schema = _run_artifact_schema_without_inventory()
    inventory: dict[str, dict] = {}
    for name, record_schema in schema["jsonl_records"].items():
        writer_owner, reader_owner = _JSONL_ARTIFACT_OWNERS[name]
        inventory[name] = {
            "path": name,
            "artifact_kind": "jsonl_record_stream",
            "schema_pointer": f'artifact_schema.jsonl_records["{name}"]',
            "record_schema": record_schema,
            "writer_owner": writer_owner,
            "reader_owner": reader_owner,
            "lifecycle_status": "known_artifact_collision_checked_and_overwrite_managed",
            "cleanup_managed": True,
            "runtime_pointer_location": f'runtime.artifacts["{name}"]',
            "restore_show_handling": "accepted stream reader or summary report input",
            "implementation_anchors": deepcopy(
                _JSONL_IMPLEMENTATION_ANCHORS[name]
            ),
            "documentation_anchors": _documentation_anchors(name),
            "behavior_test_anchors": _behavior_test_anchors(name),
        }
    for name, record in schema["quarantine_jsonl_records"].items():
        implementation_anchors = deepcopy(_QUARANTINE_COMMON_IMPLEMENTATION_ANCHORS)
        implementation_anchors["writer"].append(_QUARANTINE_PATH_ANCHORS[name])
        inventory[name] = {
            "path": name,
            "artifact_kind": "quarantine_jsonl_record_stream",
            "schema_pointer": f'artifact_schema.quarantine_jsonl_records["{name}"]',
            "record_schema": record["diagnostic_record_schema"],
            "source_stream": record["source_stream"],
            "source_record_schema": record["source_record_schema"],
            "writer_owner": "strict JSONL quarantine writer",
            "reader_owner": "diagnostic inspection and paper validators",
            "lifecycle_status": "known_artifact_collision_checked_and_overwrite_managed",
            "cleanup_managed": True,
            "runtime_pointer_location": f'runtime.artifacts["{name}"]',
            "restore_show_handling": "diagnostic stream, never accepted state input",
            "implementation_anchors": implementation_anchors,
            "documentation_anchors": _documentation_anchors(name),
            "behavior_test_anchors": _behavior_test_anchors(name),
        }
    for name, record in schema["non_jsonl_artifacts"].items():
        inventory[name] = {
            "path": name,
            "artifact_kind": record["kind"],
            "schema_pointer": f'artifact_schema.non_jsonl_artifacts["{name}"]',
            "writer_owner": record["writer_owner"],
            "reader_owner": record["reader_owner"],
            "lifecycle_status": record["lifecycle_status"],
            "cleanup_managed": True,
            "runtime_pointer_location": record["runtime_pointer_location"],
            "restore_show_handling": _NON_JSONL_RESTORE_SHOW_HANDLING[name],
            "implementation_anchors": deepcopy(
                _NON_JSONL_IMPLEMENTATION_ANCHORS[name]
            ),
            "documentation_anchors": _documentation_anchors(name),
            "behavior_test_anchors": _behavior_test_anchors(name),
        }
        if name == "paper_artifacts":
            inventory[name]["subpath_schema_pointer"] = (
                "artifact_schema.paper_artifact_subpaths"
            )
    missing = RUN_ARTIFACT_NAMES - set(inventory)
    extra = set(inventory) - RUN_ARTIFACT_NAMES
    if missing or extra:
        raise RuntimeError(
            "generated artifact inventory drifted from RUN_ARTIFACT_NAMES: "
            f"missing={sorted(missing)} extra={sorted(extra)}"
        )
    return dict(sorted(inventory.items()))


def _documentation_anchors(name: str) -> list[dict]:
    return [
        {
            "path": "docs/run-artifacts.md",
            "required_text": _RUN_ARTIFACT_DOCUMENTATION_ANCHORS[name],
        }
    ]


def _behavior_test_anchors(name: str) -> dict:
    anchors = deepcopy(_COMMON_BEHAVIOR_TEST_ANCHORS)
    if name in _QUARANTINE_PATH_ANCHORS:
        anchors.update(deepcopy(_QUARANTINE_BEHAVIOR_TEST_ANCHORS))
    if name in _NON_JSONL_RESTORE_SHOW_HANDLING:
        anchors.update(deepcopy(_NON_JSONL_BEHAVIOR_TEST_ANCHORS))
    anchors.update(deepcopy(_RUN_ARTIFACT_BEHAVIOR_TEST_ANCHORS.get(name, {})))
    return anchors


def _run_artifact_schema_without_inventory() -> dict:
    return {
        "non_jsonl_artifacts": {
            "manifest.json": _non_jsonl_artifact(
                path="manifest.json",
                kind="json_file",
                presence="required_startup_manifest_updated_at_runtime",
                writer_owner="ProgramDatabase startup manifest and runtime finalization",
                reader_owner="manifest validation, show inspection, and supported restore loaders",
                hash_policy="self_describing_manifest_not_independently_self_hashed",
                runtime_pointer_location="self",
            ),
            "task_specification.json": _non_jsonl_artifact(
                path="task_specification.json",
                kind="json_file",
                presence="generated_when_task_specification_bundle_available",
                writer_owner="ProgramDatabase startup task-specification artifact writer",
                reader_owner="task-specification artifact resolution report and docs/tests",
                hash_policy="file_sha256_when_present",
                runtime_pointer_location=(
                    "runtime.history.task_spec_artifact_resolution_report."
                    "standalone_task_spec_artifact"
                ),
            ),
            "best.py": _non_jsonl_artifact(
                path="best.py",
                kind="file",
                presence="generated_when_best_program_available",
                writer_owner="best artifact export finalization",
                reader_owner="show inspection and archived-best export consumers",
                hash_policy="file_sha256_when_present",
                runtime_pointer_location='runtime.artifacts["best.py"]',
            ),
            "best_workspace": _non_jsonl_artifact(
                path="best_workspace",
                kind="directory",
                presence="generated_when_best_program_available",
                writer_owner="best artifact export finalization",
                reader_owner="show inspection and archived-best export consumers",
                hash_policy="tree_hash_when_present",
                runtime_pointer_location='runtime.artifacts["best_workspace"]',
            ),
            "evaluator_artifacts": _non_jsonl_artifact(
                path="evaluator_artifacts",
                kind="directory",
                presence="generated_when_evaluator_artifact_include_matches",
                writer_owner="cascade evaluator artifact collection",
                reader_owner="runtime reports, show inspection, and documentation tooling",
                hash_policy="tree_hash_when_present",
                runtime_pointer_location='runtime.artifacts["evaluator_artifacts"]',
            ),
            "plugin_artifacts": _non_jsonl_artifact(
                path="plugin_artifacts",
                kind="directory",
                presence="generated_when_plugins_export_artifacts",
                writer_owner="plugin artifact exporters",
                reader_owner="runtime plugin artifact reports and show inspection",
                hash_policy="tree_hash_when_present",
                runtime_pointer_location='runtime.artifacts["plugin_artifacts"]',
            ),
            "paper_artifacts": _non_jsonl_artifact(
                path="paper_artifacts",
                kind="directory",
                presence="generated_when_paper_source_exhibits_enabled",
                writer_owner="paper-facing runtime report artifact writers",
                reader_owner="paper manifests, docs/tests, and report validators",
                hash_policy="tree_hash_when_present",
                runtime_pointer_location=(
                    "runtime.history paper-source reports with per-artifact paths"
                ),
            ),
        },
        "jsonl_records": {
            "history.jsonl": HISTORY_RECORD_SCHEMA,
            "evaluator_results.jsonl": EVALUATOR_RESULT_RECORD_SCHEMA,
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
            "prompt_prior_score_table.jsonl": (
                PROMPT_PRIOR_SCORE_TABLE_RECORD_SCHEMA
            ),
            "controller_budget_events.jsonl": CONTROLLER_BUDGET_EVENT_RECORD_SCHEMA,
        },
        "quarantine_jsonl_records": {
            "history_invalid.jsonl": _quarantine_record(
                "history.jsonl",
                HISTORY_RECORD_SCHEMA,
            ),
            "failure_history_invalid.jsonl": _quarantine_record(
                "failure_history.jsonl",
                FAILURE_RECORD_SCHEMA,
            ),
            "archive_events_invalid.jsonl": _quarantine_record(
                "archive_events.jsonl",
                ARCHIVE_EVENT_RECORD_SCHEMA,
            ),
            "controller_budget_events_invalid.jsonl": _quarantine_record(
                "controller_budget_events.jsonl",
                CONTROLLER_BUDGET_EVENT_RECORD_SCHEMA,
            ),
            "llm_calls_invalid.jsonl": _quarantine_record(
                "llm_calls.jsonl",
                {
                    "call": LLM_CALL_RECORD_SCHEMA,
                    "reward": LLM_REWARD_RECORD_SCHEMA,
                },
            ),
            "prompt_history_invalid.jsonl": _quarantine_record(
                "prompt_history.jsonl",
                PROMPT_HISTORY_RECORD_SCHEMA,
            ),
            "manifest_invalid.jsonl": _quarantine_record(
                "manifest.json",
                RUN_MANIFEST_SCHEMA,
            ),
        },
    }


def versioned_record(record_schema: str, record: dict) -> dict:
    result = deepcopy(record)
    result["schema_version"] = ARTIFACT_SCHEMA_VERSION
    result["record_schema"] = record_schema
    return result
