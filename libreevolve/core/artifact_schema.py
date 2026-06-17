from __future__ import annotations

from copy import deepcopy

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

_NON_JSONL_RESTORE_SHOW_HANDLING = {
    "manifest.json": "primary show and restore input",
    "task_specification.json": "resolved by task-spec artifact report",
    "best.py": "show summary and best-artifact export",
    "best_workspace": "show summary and best-artifact export",
    "evaluator_artifacts": "runtime artifact summary and evaluator report inspection",
    "plugin_artifacts": "plugin artifact manifest and show inspection",
    "paper_artifacts": "paper-source report validators and docs",
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
        }
    for name, record in schema["quarantine_jsonl_records"].items():
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
        }
    missing = RUN_ARTIFACT_NAMES - set(inventory)
    extra = set(inventory) - RUN_ARTIFACT_NAMES
    if missing or extra:
        raise RuntimeError(
            "generated artifact inventory drifted from RUN_ARTIFACT_NAMES: "
            f"missing={sorted(missing)} extra={sorted(extra)}"
        )
    return dict(sorted(inventory.items()))


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
