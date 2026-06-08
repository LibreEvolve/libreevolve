from __future__ import annotations
import copy
import hashlib
import json
import math
import random
import re
from collections.abc import Mapping
from pathlib import Path
import shutil
from libreevolve.core.artifact_schema import (
    ARCHIVE_EVENT_RECORD_SCHEMA,
    ARTIFACT_SCHEMA_VERSION,
    FAILURE_RECORD_SCHEMA,
    HISTORY_RECORD_SCHEMA,
    LLM_CALL_RECORD_SCHEMA,
    LLM_REWARD_RECORD_SCHEMA,
    run_artifact_schema,
    versioned_record,
)
from libreevolve.core.budget import (
    CONTROLLER_BUDGET_EVENT_SCHEMA,
    validate_controller_budget_event,
)
from libreevolve.core.config import (
    Config,
    MAX_EVALUATOR_STDIN_CHARS,
    _validate_validator_network_policy,
)
from libreevolve.core.candidate import (
    normalize_candidate_path,
    validate_candidate_workspace_limits,
)
from libreevolve.core.jsonl import (
    StrictJsonlError,
    append_quarantine_record,
    append_strict_jsonl,
    iter_strict_jsonl_objects,
    load_strict_json_object,
    strict_json_dump,
    strict_json_text_for_path,
)
from libreevolve.llm.openai_compat import resolve_openai_api_mode
from libreevolve.core.redaction import redact_sensitive_text, redaction_policy_record
from libreevolve.population.map_elites import _selection_score
from libreevolve.population.islands import (
    ISLAND_ARCHIVE_CONTENTS_RESTORE_STATUS,
    ISLAND_MIGRATION_REPLAY_POLICY,
    ISLAND_MIGRATION_REPLAY_SCHEMA,
    ISLAND_MIGRATION_REPLAY_STATUS,
    ISLAND_STATE_ACCEPTED_RESUME_STATUSES,
    IslandModel,
)
from libreevolve.population.program import (
    Program,
    validate_program_evaluation,
    validate_program_identity,
    validate_program_metadata,
    validate_program_metrics,
)
from libreevolve.population.sampling import validate_exclude_ids, validate_sample_count
from libreevolve.problems.loader import _normalize_metric_schema

RUN_ARTIFACT_NAMES = {
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
    "manifest.json",
    "manifest_invalid.jsonl",
    "best.py",
    "best_workspace",
    "evaluator_artifacts",
    "plugin_artifacts",
}
_MAX_CONTEXT_PROVENANCE_STRING_CHARS = 4096
_MAX_CONTEXT_PROVENANCE_ITEMS = 5000
_MAX_CONTEXT_PROVENANCE_DEPTH = 30
_MAX_CONTEXT_PROVENANCE_JSON_CHARS = 200_000
_MAX_SEED_SOURCE_STRING_CHARS = 1024
_MAX_ARCHIVE_EVENT_REASON_CHARS = 128
_MAX_ARCHIVE_REPLAY_MISMATCHES = 25
_MAX_OBJECTIVE_FRONTIER_PROGRAMS = 50
_MAX_OBJECTIVE_METRIC_ARCHIVE_PROGRAMS = 10
_MAX_SCORE_INDEX_PROGRAMS = 50
_MAX_LINEAGE_INDEX_ROOTS = 50
_MAX_LINEAGE_INDEX_PROGRAMS_PER_ROOT = 5
_MAX_DESCRIPTOR_INDEX_PROGRAMS_PER_DESCRIPTOR = 10
_MAX_FEEDBACK_INDEX_PROGRAMS_PER_GRADER = 10
_MAX_FEEDBACK_INDEX_TEXT_CHARS = 200
_MAX_RESURFACING_INDEX_PROGRAMS = 50
_MAX_FAILURE_INDEX_FINGERPRINTS = 50
_MAX_FAILURE_INDEX_RECORDS_PER_FINGERPRINT = 5
_MAX_HYPOTHESIS_INDEX_PROGRAMS = 50
_MAX_HYPOTHESIS_INDEX_TEXT_CHARS = 300
_MAX_ARTIFACT_INDEX_PROGRAMS = 50
_MAX_ARTIFACT_INDEX_FILES_PER_PROGRAM = 10
_MAX_ARTIFACT_INDEX_SKIPPED_PER_PROGRAM = 10
_MAX_ARTIFACT_INDEX_TEXT_CHARS = 300
CANDIDATE_LANGUAGE_POLICY_SCHEMA = "libreevolve.candidate_language_policy.v1"
TASK_SPECIFICATION_BUNDLE_SCHEMA = "libreevolve.alphaevolve_task_specification_bundle.v1"
RESURFACING_INDEX_SCHEMA = "libreevolve.resurfacing_index.v1"
RESURFACING_INDEX_POLICY = (
    "deduplicated_ranked_programs_from_score_metric_frontier_lineage_"
    "descriptor_feedback_hypothesis_artifact_indexes"
)
_RESURFACING_INDEX_LIMITATIONS = (
    "manifest_visible_resurfacing_index_not_persisted_database_table",
    "uses_deterministic_rank_fusion_not_learned_embedding_search",
    "valid_history_programs_only",
    "rebuilt_from_current_history_records_at_runtime_summary_time",
)
_RESURFACING_INDEX_SOURCES = {
    "score",
    "frontier",
    "metric",
    "lineage",
    "descriptor",
    "feedback",
    "hypothesis",
    "artifact",
}
_SEED_SOURCE_ALLOWED_KEYS = {
    "seed_index",
    "seed_source_path",
    "seed_source_kind",
    "primary_file",
    "file_count",
    "files",
    "allowed_reserved_paths",
    "seed_variant_id",
    "seed_idea_origin",
    "seed_idea_label",
    "seed_idea_summary",
    "seed_contribution_roles",
    "seed_prior_technique",
    "seed_background_refs",
}
_SEED_SOURCE_KINDS = {"file", "directory", "inline", "workspace"}
_SEED_IDEA_ORIGINS = {
    "unknown",
    "simple_baseline",
    "random_baseline",
    "researcher_idea",
    "prior_art_derived",
    "collaboration_enhanced",
}
_SEED_CONTRIBUTION_ROLES = {
    "human_seed_author",
    "researcher_idea",
    "background_knowledge",
    "prior_art",
    "collaborator_feedback",
    "automated_baseline_generator",
}
_SEED_IDEA_TEXT_MAX_CHARS = 512
_SEED_IDEA_LABEL_MAX_CHARS = 160
_SEED_BACKGROUND_REF_MAX_CHARS = 160


class ProgramDatabase:
    """Facade: IslandModel + append-only history.jsonl.

    This is a small local log/archive facade, not a GigaEvo-style lifecycle
    database.
    """

    def __init__(
        self,
        config: Config,
        perf_bounds: tuple[float, float] = (0.0, 1.0),
        context_sources: list[dict] | None = None,
        context_policy: dict | None = None,
        objective_schema: dict | None = None,
        evaluator_sources: list[dict] | None = None,
        run_provenance: dict | None = None,
        seed_sources: list[dict] | None = None,
        seed_skipped: list[dict] | None = None,
        seed_policy: dict | None = None,
        retrieval_query_context: Mapping[str, object] | None = None,
        rng: random.Random | None = None,
        archive_state_snapshot: Mapping[str, object] | None = None,
        archive_programs_by_id: Mapping[str, Program] | None = None,
    ):
        config.validate()
        objective_schema = validate_objective_schema(objective_schema)
        self._objective_schema = copy.deepcopy(objective_schema)
        self._objective_metric_order = _metric_order_from_objective_schema(
            objective_schema
        )
        self._islands = IslandModel(
            config,
            perf_bounds=perf_bounds,
            metric_order=self._objective_metric_order,
            rng=rng,
        )
        archive_cursor_restore = _archive_cursor_restore_policy(None)
        if archive_state_snapshot is not None:
            restored_archive_state = validate_archive_state_snapshot(
                archive_state_snapshot
            )
            archive_programs = _archive_program_snapshots_by_id(
                archive_programs_by_id
            )
            if (
                "archive_contents" in restored_archive_state
                and archive_programs is not None
            ):
                restore_result = self._islands.restore_archive_state(
                    restored_archive_state,
                    archive_programs,
                )
            else:
                restore_result = self._islands.restore_cursor_state(
                    restored_archive_state
                )
            archive_cursor_restore = _archive_cursor_restore_policy(restore_result)
        self._interval = config.migration_interval
        log_root = Path(config.log_dir)
        run_dir = log_root / config.problem_name
        validate_run_directory_path(log_root, run_dir)
        foreign_entries = _foreign_run_directory_entries(run_dir)
        manifest_path = run_dir / "manifest.json"
        context_sources = validate_context_sources(context_sources or [])
        context_policy = validate_context_policy(context_policy or {})
        self.retrieval_query_context = validate_retrieval_query_context(
            retrieval_query_context or {}
        )
        seed_sources = validate_seed_sources(seed_sources or [])
        seed_skipped = validate_seed_skipped(seed_skipped or [])
        seed_policy = validate_seed_policy(seed_policy or {})
        startup_manifest = _startup_manifest_payload(
            config,
            context_sources,
            context_policy,
            objective_schema,
            evaluator_sources or [],
            run_provenance or {},
            foreign_entries,
            seed_sources,
            seed_skipped,
            seed_policy,
            archive_cursor_restore,
        )
        strict_json_text_for_path(startup_manifest, manifest_path, indent=2)
        prepare_run_directory(run_dir, config.run_collision_policy)
        run_dir.mkdir(parents=True, exist_ok=True)
        self._jsonl = run_dir / "history.jsonl"
        self._failures = run_dir / "failure_history.jsonl"
        self._archive_events = run_dir / "archive_events.jsonl"
        self._controller_budget_events = run_dir / "controller_budget_events.jsonl"
        self._llm_calls = run_dir / "llm_calls.jsonl"
        self._quarantine = run_dir / "history_invalid.jsonl"
        self._failure_quarantine = run_dir / "failure_history_invalid.jsonl"
        self._archive_event_quarantine = run_dir / "archive_events_invalid.jsonl"
        self._controller_budget_event_quarantine = (
            run_dir / "controller_budget_events_invalid.jsonl"
        )
        self._llm_call_quarantine = run_dir / "llm_calls_invalid.jsonl"
        self._manifest = run_dir / "manifest.json"
        self._manifest_quarantine = run_dir / "manifest_invalid.jsonl"
        self._startup_manifest = startup_manifest
        self._quarantine_snapshot_retention_mode = (
            config.quarantine_snapshot_retention_mode
        )
        self._all: list[Program] = []
        self._ids: set[str] = set()
        self._failed_program_ids: set[str] = set()
        self._failure_records: list[dict] = []
        self.retrieval_failure_context: list[dict] = []
        self.retrieval_hypothesis_context: list[dict] = []
        self._logged_programs_by_id: dict[str, Program] = {}
        self._archive_ids: set[str] = set()
        self._failure_counts: dict[str, int] = {}
        self._controller_budget_event_sequence: int = 0
        self._workspace_limits = _candidate_workspace_limits_from_config(config)
        self._write_manifest(startup_manifest)

    def add(self, program: Program, threshold: float = 0.0) -> dict:
        return self.admit(program, threshold=threshold)

    def objective_schema_snapshot(self) -> dict:
        return copy.deepcopy(self._objective_schema)

    def startup_manifest_snapshot(self) -> dict:
        return copy.deepcopy(self._startup_manifest)

    def log_llm_call(self, record: dict) -> None:
        normalized = {"record_type": "call", **record}
        record_type = normalized.get("record_type")
        record_schema = (
            LLM_REWARD_RECORD_SCHEMA
            if record_type == "reward"
            else LLM_CALL_RECORD_SCHEMA
        )
        append_strict_jsonl(
            self._llm_calls,
            versioned_record(record_schema, normalized),
            quarantine_path=self._llm_call_quarantine,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )

    def log_controller_budget_event(self, event: dict) -> dict:
        normalized = {
            **event,
            "schema": CONTROLLER_BUDGET_EVENT_SCHEMA,
            "sequence": self._controller_budget_event_sequence,
        }
        validated = validate_controller_budget_event(normalized)
        append_strict_jsonl(
            self._controller_budget_events,
            validated,
            quarantine_path=self._controller_budget_event_quarantine,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        self._controller_budget_event_sequence += 1
        return validated

    def _archive_add(self, program: Program) -> tuple[dict, Program]:
        validate_program_identity(program.id, program.parent_id, program.lineage)
        program.metadata = validate_program_metadata(program.metadata)
        program.metrics = validate_program_metrics(program.metrics)
        _validate_unique_archive_program_id(
            program,
            self._archive_ids,
            self._logged_programs_by_id,
        )
        archive_program = _program_snapshot(program)
        event = self._islands.add(archive_program)
        if "archive_sequence" in event:
            program.metadata = dict(program.metadata)
            program.metadata["archive_sequence"] = event["archive_sequence"]
        self._archive_ids.add(program.id)
        return event, archive_program

    def admit(self, program: Program, threshold: float = 0.0) -> dict:
        self._validate_program_workspace_limits(program)
        threshold = _validate_admission_threshold(threshold)
        program.metadata = validate_program_metadata(program.metadata)
        program.evaluation = validate_program_evaluation(program.evaluation)
        evaluation_is_valid = program.evaluation.get("is_valid") is True
        fitness_valid = _is_finite_real(program.fitness)
        validate_history_before_archive = False
        if not evaluation_is_valid:
            event = {
                "program_id": program.id,
                "admitted": False,
                "reason": "invalid_evaluation",
                "threshold": threshold,
                "evaluation_is_valid": evaluation_is_valid,
                "island_id": None,
                "cell": None,
                "descriptors": {},
                "previous_occupant_id": None,
                "cell_replaced": False,
                "entered_cell": False,
                "entered_elite": False,
                "cell_admitted": False,
                "elite_retained": False,
                "search_state_changed": False,
                "sampling_eligible": False,
                "displaced_elite_ids": [],
            }
        elif not fitness_valid:
            event = {
                "program_id": program.id,
                "admitted": False,
                "reason": _fitness_rejection_reason(program.fitness),
                "threshold": threshold,
                "evaluation_is_valid": evaluation_is_valid,
                "island_id": None,
                "cell": None,
                "descriptors": {},
                "previous_occupant_id": None,
                "cell_replaced": False,
                "entered_cell": False,
                "entered_elite": False,
                "cell_admitted": False,
                "elite_retained": False,
                "search_state_changed": False,
                "sampling_eligible": False,
                "displaced_elite_ids": [],
            }
        elif program.fitness < threshold:
            event = {
                "program_id": program.id,
                "admitted": False,
                "reason": "below_threshold",
                "threshold": threshold,
                "evaluation_is_valid": evaluation_is_valid,
                "island_id": None,
                "cell": None,
                "descriptors": {},
                "previous_occupant_id": None,
                "cell_replaced": False,
                "entered_cell": False,
                "entered_elite": False,
                "cell_admitted": False,
                "elite_retained": False,
                "search_state_changed": False,
                "sampling_eligible": False,
                "displaced_elite_ids": [],
            }
        else:
            program.metrics = validate_program_metrics(program.metrics)
            _validate_program_history_record(program, self._jsonl)
            validate_history_before_archive = True
            event, archive_program = self._archive_add(program)
            event["threshold"] = threshold
            event["evaluation_is_valid"] = evaluation_is_valid
        event["selection_score"] = _history_safe_selection_score(program)
        event["objective_vector"] = _history_safe_objective_vector(program)
        metadata = validate_program_metadata(program.metadata)
        metadata["archive_admission"] = event
        if validate_history_before_archive:
            _validate_program_history_record(program, self._jsonl, metadata=metadata)
            archive_program.metadata = metadata
        program.metadata = metadata
        return event

    def log(self, program: Program) -> None:
        self._validate_program_workspace_limits(program)
        program.metadata = validate_program_metadata(program.metadata)
        program.evaluation = validate_program_evaluation(program.evaluation)
        record = _program_history_record(program)
        _validate_history_record_fitness(
            record,
            self._jsonl,
            quarantine_path=self._quarantine,
            jsonl=True,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        _validate_history_record_generation(
            record,
            self._jsonl,
            quarantine_path=self._quarantine,
            jsonl=True,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        _validate_history_record_metrics(
            record,
            self._jsonl,
            quarantine_path=self._quarantine,
            jsonl=True,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        _validate_history_record_identity(
            record,
            self._jsonl,
            quarantine_path=self._quarantine,
            jsonl=True,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        _validate_unique_logged_program_id(
            program.id,
            self._ids,
            self._jsonl,
            record=record,
            quarantine_path=self._quarantine,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        append_strict_jsonl(
            self._jsonl,
            record,
            quarantine_path=self._quarantine,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        self._ids.add(program.id)
        self._logged_programs_by_id[program.id] = program
        self._all.append(_program_snapshot(program))
        self._append_retrieval_hypothesis_context(program)

    def log_failure(
        self,
        program: Program,
        parent: Program,
        mutation_text: object,
        diff_error: str | None,
        admission: dict | None = None,
    ) -> dict:
        program.metadata = validate_program_metadata(program.metadata)
        program.evaluation = validate_program_evaluation(program.evaluation)
        error = program.evaluation.get("error") if program.evaluation else None
        mutation_payload = _failure_mutation_payload(mutation_text)
        changed_files = _changed_files(parent, program)
        file_deltas = _file_deltas(parent, program)
        fingerprint = _failure_fingerprint(
            record_type="generated",
            parent_id=parent.id,
            diff_error=diff_error,
            evaluator_error=error,
            mutation_payload=mutation_payload,
            changed_files=changed_files,
            file_deltas=file_deltas,
        )
        key = fingerprint["sha256"]
        repetition_count = self._failure_counts.get(key, 0) + 1
        normalize_rejected_values = (
            admission is not None and admission.get("admitted") is False
        )
        score, score_diagnostic = _failure_record_number(
            program.fitness, normalize=normalize_rejected_values
        )
        record = {
            "program_id": program.id,
            "parent_id": parent.id,
            "generation": program.generation,
            "score": score,
            "is_valid": program.evaluation.get("is_valid") if program.evaluation else None,
            "error": _failure_optional_text(error, 1000),
            "diff_error": _failure_optional_json_text(diff_error, 1000),
            "changed_files": changed_files,
            "file_deltas": file_deltas,
            "mutation_text": mutation_payload["safe_text"],
            "mutation_truncated": mutation_payload["truncated"],
            "mutation_sha256": mutation_payload["sha256"],
            "mutation_payload_type": mutation_payload["type"],
            "mutation_payload_text": mutation_payload["is_text"],
            "failure_fingerprint": fingerprint,
            "evaluation": _failure_evaluation_summary(
                program, normalize_non_finite=normalize_rejected_values
            ),
            "repetition_count": repetition_count,
        }
        failure_llm = _failure_program_llm_summary(program)
        if failure_llm:
            record["llm"] = failure_llm
        record = versioned_record(FAILURE_RECORD_SCHEMA, record)
        if score_diagnostic is not None:
            record["score_diagnostic"] = score_diagnostic
        if admission is not None:
            record["admission_reason"] = admission.get("reason")
            record["archive_admission"] = admission
        _validate_history_record_identity(
            record,
            self._failures,
            quarantine_path=self._failure_quarantine,
            jsonl=True,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        _validate_history_record_generation(
            record,
            self._failures,
            quarantine_path=self._failure_quarantine,
            jsonl=True,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        _validate_unique_failed_program_id(
            program.id,
            self._failed_program_ids,
            self._failures,
            record=record,
            quarantine_path=self._failure_quarantine,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        append_strict_jsonl(
            self._failures,
            record,
            quarantine_path=self._failure_quarantine,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        self._failed_program_ids.add(program.id)
        self._failure_counts[key] = repetition_count
        self._failure_records.append(copy.deepcopy(record))
        self._append_retrieval_failure_context(record)
        program.metadata = validate_program_metadata(program.metadata)
        program.metadata["failure_record"] = record
        return record

    def log_seed_failure(self, program: Program, admission: dict) -> dict:
        program.metadata = validate_program_metadata(program.metadata)
        program.evaluation = validate_program_evaluation(program.evaluation)
        evaluation = program.evaluation or {}
        error = evaluation.get("error")
        seed_payload = _seed_failure_payload(program)
        changed_files = sorted(program.workspace().files)
        file_deltas = [
            {"path": path, "change": "seed"}
            for path in changed_files
        ]
        fingerprint = _failure_fingerprint(
            record_type="seed",
            parent_id=None,
            diff_error=admission.get("reason"),
            evaluator_error=error,
            mutation_payload=seed_payload,
            changed_files=changed_files,
            file_deltas=file_deltas,
        )
        key = fingerprint["sha256"]
        repetition_count = self._failure_counts.get(key, 0) + 1
        record = {
            "record_type": "seed",
            "program_id": program.id,
            "parent_id": None,
            **_seed_source_metadata(program),
            "generation": program.generation,
            "score": program.fitness,
            "is_valid": evaluation.get("is_valid"),
            "error": _failure_optional_text(error, 1000),
            "diff_error": None,
            "admission_reason": admission.get("reason"),
            "archive_admission": admission,
            "changed_files": changed_files,
            "file_deltas": file_deltas,
            "mutation_text": seed_payload["safe_text"],
            "mutation_truncated": seed_payload["truncated"],
            "mutation_sha256": seed_payload["sha256"],
            "failure_fingerprint": fingerprint,
            "seed_workspace": seed_payload["workspace"],
            "evaluation": _failure_evaluation_summary(program),
            "repetition_count": repetition_count,
        }
        record = versioned_record(FAILURE_RECORD_SCHEMA, record)
        _validate_history_record_generation(
            record,
            self._failures,
            quarantine_path=self._failure_quarantine,
            jsonl=True,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        _validate_history_record_identity(
            record,
            self._failures,
            quarantine_path=self._failure_quarantine,
            jsonl=True,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        _validate_unique_failed_program_id(
            program.id,
            self._failed_program_ids,
            self._failures,
            record=record,
            quarantine_path=self._failure_quarantine,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        append_strict_jsonl(
            self._failures,
            record,
            quarantine_path=self._failure_quarantine,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )
        self._failed_program_ids.add(program.id)
        self._failure_counts[key] = repetition_count
        self._failure_records.append(copy.deepcopy(record))
        self._append_retrieval_failure_context(record)
        program.metadata = validate_program_metadata(program.metadata)
        program.metadata["failure_record"] = record
        return record

    def _append_retrieval_failure_context(self, record: dict) -> None:
        self.retrieval_failure_context.append(_retrieval_failure_context_record(record))
        self.retrieval_failure_context = self.retrieval_failure_context[-5:]

    def _append_retrieval_hypothesis_context(self, program: Program) -> None:
        context_record = _retrieval_hypothesis_context_record(program)
        if context_record:
            self.retrieval_hypothesis_context.append(context_record)
            self.retrieval_hypothesis_context = self.retrieval_hypothesis_context[-5:]

    def sample(self, strategy: str = "exploit") -> Program | None:
        program = self._islands.sample(strategy=strategy)
        return _program_snapshot(program) if program is not None else None

    def last_sample_metadata(self) -> dict:
        return self._islands.last_sample_metadata()

    def sample_diverse(
        self, k: int, exclude_ids: set[str] | None = None, strategy: str = "mixed"
    ) -> list[Program]:
        k = validate_sample_count(k, "database sample count")
        exclude_ids = validate_exclude_ids(exclude_ids, "database exclude_ids")
        return [
            _program_snapshot(program)
            for program in self._islands.sample_diverse(
                k=k, exclude_ids=exclude_ids, strategy=strategy
            )
        ]

    def best(self) -> Program | None:
        program = self._islands.best()
        return _program_snapshot(program) if program is not None else None

    def maybe_migrate(self, gen: int) -> list[dict]:
        if self._interval > 0 and gen > 0 and gen % self._interval == 0:
            events = self._islands.migrate()
            for event in events:
                self._log_archive_event({"event_type": "migration", **event})
            return events
        return []

    def archive_state_snapshot(self) -> dict:
        return self._islands.state_snapshot()

    def all_programs(self) -> list[Program]:
        return [_program_snapshot(program) for program in self._all]

    def objective_frontier_snapshot(self) -> dict:
        return _objective_frontier_snapshot(
            self._all,
            self._objective_metric_order,
            limit=_MAX_OBJECTIVE_FRONTIER_PROGRAMS,
        )

    def objective_metric_leaders_snapshot(self) -> dict:
        return _objective_metric_leaders_snapshot(
            self._all,
            self._objective_metric_order,
        )

    def objective_metric_archives_snapshot(self) -> dict:
        return _objective_metric_archives_snapshot(
            self._all,
            self._objective_metric_order,
            limit=_MAX_OBJECTIVE_METRIC_ARCHIVE_PROGRAMS,
        )

    def score_index_snapshot(self) -> dict:
        return _score_index_snapshot(
            self._all,
            limit=_MAX_SCORE_INDEX_PROGRAMS,
        )

    def lineage_index_snapshot(self) -> dict:
        return _lineage_index_snapshot(
            self._all,
            root_limit=_MAX_LINEAGE_INDEX_ROOTS,
            programs_per_root_limit=_MAX_LINEAGE_INDEX_PROGRAMS_PER_ROOT,
        )

    def descriptor_index_snapshot(self) -> dict:
        return _descriptor_index_snapshot(
            self._all,
            limit=_MAX_DESCRIPTOR_INDEX_PROGRAMS_PER_DESCRIPTOR,
        )

    def feedback_index_snapshot(self) -> dict:
        return _feedback_index_snapshot(
            self._all,
            limit=_MAX_FEEDBACK_INDEX_PROGRAMS_PER_GRADER,
        )

    def resurfacing_index_snapshot(self) -> dict:
        return _resurfacing_index_snapshot(
            self._all,
            self._objective_metric_order,
            limit=_MAX_RESURFACING_INDEX_PROGRAMS,
        )

    def failure_index_snapshot(self) -> dict:
        return _failure_index_snapshot(
            self._failure_records,
            fingerprint_limit=_MAX_FAILURE_INDEX_FINGERPRINTS,
            records_per_fingerprint_limit=_MAX_FAILURE_INDEX_RECORDS_PER_FINGERPRINT,
        )

    def failure_records_snapshot(self) -> list[dict]:
        return copy.deepcopy(self._failure_records)

    def hypothesis_index_snapshot(self) -> dict:
        return _hypothesis_index_snapshot(
            self._all,
            limit=_MAX_HYPOTHESIS_INDEX_PROGRAMS,
        )

    def artifact_index_snapshot(self) -> dict:
        return _artifact_index_snapshot(
            self._all,
            program_limit=_MAX_ARTIFACT_INDEX_PROGRAMS,
            files_per_program_limit=_MAX_ARTIFACT_INDEX_FILES_PER_PROGRAM,
            skipped_per_program_limit=_MAX_ARTIFACT_INDEX_SKIPPED_PER_PROGRAM,
        )

    def resurface_candidates(
        self,
        k: int,
        exclude_ids: set[str] | None = None,
        *,
        target_metric: str | None = None,
    ) -> list[Program]:
        k = validate_sample_count(k, "database resurfacing count")
        exclude_ids = validate_exclude_ids(exclude_ids, "database resurfacing exclude_ids")
        target_metric = _validate_resurfacing_target_metric(
            target_metric,
            self._objective_metric_order,
        )
        if k <= 0:
            return []
        programs_by_id = {program.id: program for program in self._all}
        if target_metric is not None:
            snapshot = _objective_metric_archives_snapshot(
                self._all,
                self._objective_metric_order,
                limit=max(k + len(exclude_ids), _MAX_OBJECTIVE_METRIC_ARCHIVE_PROGRAMS),
            )
            surfaced = []
            for archive in snapshot["archives"]:
                if archive["metric"] != target_metric:
                    continue
                for record in archive["programs"]:
                    program_id = record["program_id"]
                    if program_id in exclude_ids:
                        continue
                    program = programs_by_id.get(program_id)
                    if program is not None:
                        surfaced.append(_program_snapshot(program))
                    if len(surfaced) >= k:
                        return surfaced
                return surfaced
            return []
        snapshot = _resurfacing_index_snapshot(
            self._all,
            self._objective_metric_order,
            limit=max(k + len(exclude_ids), _MAX_RESURFACING_INDEX_PROGRAMS),
        )
        surfaced: list[Program] = []
        for record in snapshot["programs"]:
            program_id = record["program_id"]
            if program_id in exclude_ids:
                continue
            program = programs_by_id.get(program_id)
            if program is not None:
                surfaced.append(_program_snapshot(program))
            if len(surfaced) >= k:
                break
        return surfaced

    def resurface_by_metric(
        self,
        metric: str,
        k: int,
        exclude_ids: set[str] | None = None,
    ) -> list[Program]:
        """Return top retained candidates for one declared normalized metric."""
        return self.resurface_candidates(
            k=k,
            exclude_ids=exclude_ids,
            target_metric=metric,
        )

    def resurface_by_lineage(
        self,
        lineage_root_id: str,
        k: int,
        exclude_ids: set[str] | None = None,
    ) -> list[Program]:
        k = validate_sample_count(k, "database lineage resurfacing count")
        exclude_ids = validate_exclude_ids(
            exclude_ids,
            "database lineage resurfacing exclude_ids",
        )
        lineage_root_id = _validate_database_query_program_id(
            lineage_root_id,
            "database lineage resurfacing lineage_root_id",
        )
        if k <= 0:
            return []
        snapshot = _lineage_index_snapshot(
            self._all,
            root_limit=max(len(self._all), 1),
            programs_per_root_limit=max(k + len(exclude_ids), 1),
        )
        programs_by_id = {program.id: program for program in self._all}
        for lineage in snapshot["lineages"]:
            if lineage["lineage_root_id"] != lineage_root_id:
                continue
            return _ranked_program_snapshots_from_index_records(
                programs_by_id,
                lineage["programs"],
                k=k,
                exclude_ids=exclude_ids,
            )
        return []

    def resurface_by_descriptor(
        self,
        descriptor: str,
        k: int,
        exclude_ids: set[str] | None = None,
    ) -> list[Program]:
        k = validate_sample_count(k, "database descriptor resurfacing count")
        exclude_ids = validate_exclude_ids(
            exclude_ids,
            "database descriptor resurfacing exclude_ids",
        )
        descriptor = _validate_database_query_key(
            descriptor,
            "database descriptor resurfacing descriptor",
        )
        if k <= 0:
            return []
        snapshot = _descriptor_index_snapshot(
            self._all,
            limit=max(k + len(exclude_ids), 1),
        )
        programs_by_id = {program.id: program for program in self._all}
        for descriptor_record in snapshot["descriptors"]:
            if descriptor_record["descriptor"] != descriptor:
                continue
            return _ranked_program_snapshots_from_index_records(
                programs_by_id,
                descriptor_record["programs"],
                k=k,
                exclude_ids=exclude_ids,
            )
        return []

    def resurface_by_novelty(
        self,
        k: int,
        exclude_ids: set[str] | None = None,
        *,
        descriptor: str = "diversity",
    ) -> list[Program]:
        """Return candidates ranked by a novelty-like archive descriptor.

        The default uses the MAP-Elites diversity descriptor; configured
        descriptor axes can be queried by passing their descriptor label.
        """
        return self.resurface_by_descriptor(
            descriptor,
            k=k,
            exclude_ids=exclude_ids,
        )

    def resurface_by_feedback(
        self,
        feedback_name: str,
        k: int,
        exclude_ids: set[str] | None = None,
    ) -> list[Program]:
        k = validate_sample_count(k, "database feedback resurfacing count")
        exclude_ids = validate_exclude_ids(
            exclude_ids,
            "database feedback resurfacing exclude_ids",
        )
        feedback_name = _validate_database_query_key(
            feedback_name,
            "database feedback resurfacing feedback_name",
        )
        if k <= 0:
            return []
        snapshot = _feedback_index_snapshot(
            self._all,
            limit=max(k + len(exclude_ids), 1),
        )
        programs_by_id = {program.id: program for program in self._all}
        for grader in snapshot["graders"]:
            if grader["feedback_name"] != feedback_name:
                continue
            return _ranked_program_snapshots_from_index_records(
                programs_by_id,
                grader["programs"],
                k=k,
                exclude_ids=exclude_ids,
            )
        return []

    def _log_archive_event(self, event: dict) -> None:
        append_strict_jsonl(
            self._archive_events,
            versioned_record(ARCHIVE_EVENT_RECORD_SCHEMA, event),
            quarantine_path=self._archive_event_quarantine,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )

    def _write_manifest(self, manifest: dict) -> None:
        strict_json_dump(manifest, self._manifest, indent=2)

    def update_manifest_runtime(self, runtime: dict) -> None:
        manifest = self._read_current_manifest_or_recover()
        manifest["runtime"] = runtime
        try:
            strict_json_dump(manifest, self._manifest, indent=2)
        except StrictJsonlError as exc:
            append_quarantine_record(
                self._manifest_quarantine,
                {"event": "runtime_update", "runtime": runtime},
                exc,
                retention_mode=self._quarantine_snapshot_retention_mode,
            )
            raise

    def _read_current_manifest_or_recover(self) -> dict:
        try:
            return json.loads(
                self._manifest.read_text(encoding="utf-8"),
                object_pairs_hook=_reject_duplicate_manifest_json_names,
            )
        except _DuplicateManifestJsonNameError as exc:
            append_quarantine_record(
                self._manifest_quarantine,
                {
                    "event": "runtime_update_current_manifest_ambiguous",
                    "manifest_path": "manifest.json",
                    "fallback": None,
                },
                exc,
                retention_mode=self._quarantine_snapshot_retention_mode,
            )
            raise StrictJsonlError(
                f"Could not update runtime for ambiguous manifest.json: {exc}"
            ) from exc
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            append_quarantine_record(
                self._manifest_quarantine,
                {
                    "event": "runtime_update_current_manifest_unreadable",
                    "manifest_path": "manifest.json",
                    "fallback": "startup_manifest",
                },
                exc,
                retention_mode=self._quarantine_snapshot_retention_mode,
            )
            return dict(self._startup_manifest)

    def _validate_program_workspace_limits(self, program: Program) -> dict:
        workspace = program.workspace()
        return validate_candidate_workspace_limits(
            workspace.files,
            static_files=workspace.static_files,
            **self._workspace_limits,
        )


class _DuplicateManifestJsonNameError(ValueError):
    pass


class HistoryRestoreError(ValueError):
    """Raised when accepted history cannot be restored into a safe index."""


class ArchiveStateRestoreError(ValueError):
    """Raised when persisted archive state cannot be validated for restore."""


class ArchiveEventRestoreError(ValueError):
    """Raised when archive_events.jsonl cannot be validated for replay/query."""


class _DuplicateHistoryJsonNameError(ValueError):
    pass


def _reject_duplicate_manifest_json_names(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateManifestJsonNameError(
                f"manifest JSON contains duplicate object name {key!r}"
            )
        result[key] = value
    return result


def load_accepted_history_index(path: str | Path) -> dict[str, dict]:
    """Load history.jsonl into a manifest-safe id index for restore/query code."""
    records = _load_accepted_history_records(Path(path))
    return {record["id"]: copy.deepcopy(record) for record in records}


def load_archive_restore_bundle(
    manifest_path: str | Path,
    history_path: str | Path,
) -> dict:
    """Load manifest archive state plus checked Program snapshots from history."""
    archive_state = load_runtime_archive_state_snapshot(manifest_path)
    history_index = load_accepted_history_index(history_path)
    programs_by_id = {
        program_id: _program_from_history_record(record, line_label=program_id)
        for program_id, record in history_index.items()
    }
    _validate_archive_snapshot_program_references(archive_state, programs_by_id)
    return {
        "archive_state_snapshot": archive_state,
        "archive_programs_by_id": programs_by_id,
    }


def load_failure_history_records(path: str | Path) -> list[dict]:
    """Load failure_history.jsonl records for replay/query code.

    Failure rows store bounded, redacted diagnostics, not exact mutation
    payloads. The reader keeps malformed/non-text payload evidence queryable
    while making the no-reapply policy explicit for resume callers.
    """
    records: list[dict] = []
    seen_ids: dict[str, int] = {}
    try:
        for line_number, record in enumerate(
            iter_strict_jsonl_objects(Path(path), stream_name="failure_history.jsonl"),
            start=1,
        ):
            _validate_restored_record_schema(
                record,
                line_number,
                expected_schema=FAILURE_RECORD_SCHEMA,
                stream_name="failure_history.jsonl",
            )
            _validate_restored_failure_record(record, line_number, seen_ids)
            record["mutation_payload_replay"] = _restored_failure_payload_replay_policy(
                record
            )
            records.append(copy.deepcopy(record))
    except StrictJsonlError as exc:
        raise HistoryRestoreError(str(exc)) from exc
    return records


def load_archive_event_records(path: str | Path) -> list[dict]:
    """Load archive_events.jsonl as a checked migration audit stream."""
    records: list[dict] = []
    previous_sequence = 0
    try:
        for line_number, record in enumerate(
            iter_strict_jsonl_objects(Path(path), stream_name="archive_events.jsonl"),
            start=1,
        ):
            _validate_restored_record_schema(
                record,
                line_number,
                expected_schema=ARCHIVE_EVENT_RECORD_SCHEMA,
                stream_name="archive_events.jsonl",
            )
            previous_sequence = _validate_archive_event_record(
                record,
                line_number,
                previous_sequence,
            )
            records.append(copy.deepcopy(record))
    except StrictJsonlError as exc:
        raise ArchiveEventRestoreError(str(exc)) from exc
    return records


def archive_event_replay_audit(
    path: str | Path,
    archive_state_snapshot: Mapping[str, object],
) -> dict:
    """Replay migration placement events enough to audit final archive contents."""
    event_path = Path(path)
    if not event_path.exists():
        return _archive_event_replay_absent_audit(archive_state_snapshot)
    return audit_archive_event_records(
        load_archive_event_records(event_path),
        archive_state_snapshot,
    )


def audit_archive_event_records(
    records: list[dict],
    archive_state_snapshot: Mapping[str, object],
) -> dict:
    snapshot = validate_archive_state_snapshot(archive_state_snapshot)
    snapshot_cells = _archive_snapshot_cell_map(snapshot)
    if snapshot_cells is None:
        return {
            "schema": "libreevolve.archive_event_replay_audit.v1",
            "status": "archive_contents_missing",
            "audit_only": True,
            "replay_engine_supported": False,
            "event_count": len(records),
            "admitted_event_count": sum(1 for record in records if record["admitted"]),
            "skipped_event_count": sum(1 for record in records if not record["admitted"]),
            "final_replayed_placement_count": 0,
            "matched_placement_count": 0,
            "superseded_or_missing_count": 0,
            "mismatches": [],
            "mismatch_retention_limit": _MAX_ARCHIVE_REPLAY_MISMATCHES,
            "limitations": _archive_event_replay_audit_limitations(),
        }
    final_placements: dict[tuple[int, tuple[int, ...]], dict] = {}
    admitted = 0
    skipped = 0
    for index, record in enumerate(records):
        if not record["admitted"]:
            skipped += 1
            continue
        admitted += 1
        target_island = record["target_island"]
        if target_island >= snapshot["n_islands"]:
            raise ArchiveEventRestoreError(
                "archive event replay target_island exceeds archive state n_islands "
                f"at event index {index}"
            )
        cell = record["cell"]
        if cell is None:
            raise ArchiveEventRestoreError(
                "archive event replay admitted migration row must include cell "
                f"at event index {index}"
            )
        final_placements[(target_island, tuple(cell))] = {
            "program_id": record["program_id"],
            "migration_sequence": record["migration_sequence"],
            "selection_score": record["selection_score"],
        }
    mismatches = []
    matched = 0
    for (island_id, cell), expected in sorted(final_placements.items()):
        actual = snapshot_cells.get((island_id, cell))
        if actual == expected["program_id"]:
            matched += 1
            continue
        if len(mismatches) < _MAX_ARCHIVE_REPLAY_MISMATCHES:
            mismatches.append(
                {
                    "island_id": island_id,
                    "cell": list(cell),
                    "expected_program_id": expected["program_id"],
                    "actual_program_id": actual,
                    "migration_sequence": expected["migration_sequence"],
                    "reason": "migration_placement_not_current_in_archive_contents",
                }
            )
    status = "no_migration_placements"
    if final_placements and not mismatches:
        status = "verified_against_archive_contents"
    elif final_placements:
        status = "superseded_or_missing_migration_placements"
    return {
        "schema": "libreevolve.archive_event_replay_audit.v1",
        "status": status,
        "audit_only": True,
        "replay_engine_supported": False,
        "event_count": len(records),
        "admitted_event_count": admitted,
        "skipped_event_count": skipped,
        "final_replayed_placement_count": len(final_placements),
        "matched_placement_count": matched,
        "superseded_or_missing_count": len(final_placements) - matched,
        "mismatches": mismatches,
        "mismatch_retention_limit": _MAX_ARCHIVE_REPLAY_MISMATCHES,
        "limitations": _archive_event_replay_audit_limitations(),
    }


def validate_archive_event_replay_audit(audit: object) -> dict:
    """Validate archive-event replay audit summaries before manifest use."""
    if not isinstance(audit, dict):
        raise ArchiveEventRestoreError("archive event replay audit must be an object")
    required = {
        "schema",
        "status",
        "audit_only",
        "replay_engine_supported",
        "event_count",
        "admitted_event_count",
        "skipped_event_count",
        "final_replayed_placement_count",
        "matched_placement_count",
        "superseded_or_missing_count",
        "mismatches",
        "mismatch_retention_limit",
        "limitations",
    }
    missing = required - set(audit)
    if missing:
        raise ArchiveEventRestoreError(
            f"archive event replay audit missing fields: {sorted(missing)}"
        )
    unsupported = set(audit) - required
    if unsupported:
        raise ArchiveEventRestoreError(
            f"archive event replay audit has unsupported fields: {sorted(unsupported)}"
        )
    if audit["schema"] != "libreevolve.archive_event_replay_audit.v1":
        raise ArchiveEventRestoreError("archive event replay audit schema is unsupported")
    allowed_statuses = {
        "archive_events_absent",
        "archive_contents_missing",
        "no_migration_placements",
        "verified_against_archive_contents",
        "superseded_or_missing_migration_placements",
    }
    status = audit["status"]
    if status not in allowed_statuses:
        raise ArchiveEventRestoreError("archive event replay audit status is unsupported")
    if audit["audit_only"] is not True:
        raise ArchiveEventRestoreError("archive event replay audit must be audit-only")
    if audit["replay_engine_supported"] is not False:
        raise ArchiveEventRestoreError(
            "archive event replay audit must not claim restore-engine support"
        )
    counts = {
        field: _validate_snapshot_non_negative_int(audit[field], field)
        for field in (
            "event_count",
            "admitted_event_count",
            "skipped_event_count",
            "final_replayed_placement_count",
            "matched_placement_count",
            "superseded_or_missing_count",
            "mismatch_retention_limit",
        )
    }
    if counts["event_count"] != (
        counts["admitted_event_count"] + counts["skipped_event_count"]
    ):
        raise ArchiveEventRestoreError(
            "archive event replay audit event counts are inconsistent"
        )
    if counts["final_replayed_placement_count"] != (
        counts["matched_placement_count"] + counts["superseded_or_missing_count"]
    ):
        raise ArchiveEventRestoreError(
            "archive event replay audit placement counts are inconsistent"
        )
    mismatches = _validate_archive_event_audit_mismatches(
        audit["mismatches"],
        counts["mismatch_retention_limit"],
    )
    if len(mismatches) > counts["superseded_or_missing_count"]:
        raise ArchiveEventRestoreError(
            "archive event replay audit retained mismatches exceed mismatch count"
        )
    if status == "verified_against_archive_contents" and (
        counts["superseded_or_missing_count"] != 0 or mismatches
    ):
        raise ArchiveEventRestoreError(
            "verified archive event replay audits must not retain mismatches"
        )
    if status == "archive_events_absent" and any(
        counts[field] != 0
        for field in (
            "event_count",
            "admitted_event_count",
            "skipped_event_count",
            "final_replayed_placement_count",
            "matched_placement_count",
            "superseded_or_missing_count",
        )
    ):
        raise ArchiveEventRestoreError(
            "absent archive event replay audits must have zero counts"
        )
    limitations = audit["limitations"]
    required_limitations = set(_archive_event_replay_audit_limitations())
    if not isinstance(limitations, list) or not required_limitations <= set(limitations):
        raise ArchiveEventRestoreError(
            "archive event replay audit limitations must state audit boundaries"
        )
    return {
        "schema": audit["schema"],
        "status": status,
        "audit_only": True,
        "replay_engine_supported": False,
        "event_count": counts["event_count"],
        "admitted_event_count": counts["admitted_event_count"],
        "skipped_event_count": counts["skipped_event_count"],
        "final_replayed_placement_count": counts["final_replayed_placement_count"],
        "matched_placement_count": counts["matched_placement_count"],
        "superseded_or_missing_count": counts["superseded_or_missing_count"],
        "mismatches": mismatches,
        "mismatch_retention_limit": counts["mismatch_retention_limit"],
        "limitations": list(limitations),
    }


def _validate_archive_event_audit_mismatches(
    value: object,
    retention_limit: int,
) -> list[dict]:
    if not isinstance(value, list):
        raise ArchiveEventRestoreError(
            "archive event replay audit mismatches must be a list"
        )
    if len(value) > retention_limit:
        raise ArchiveEventRestoreError(
            "archive event replay audit mismatches exceed retention limit"
        )
    restored = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ArchiveEventRestoreError(
                "archive event replay audit mismatches entries must be objects"
            )
        required = {
            "island_id",
            "cell",
            "expected_program_id",
            "actual_program_id",
            "migration_sequence",
            "reason",
        }
        missing = required - set(item)
        if missing:
            raise ArchiveEventRestoreError(
                "archive event replay audit mismatches"
                f"[{index}] missing fields: {sorted(missing)}"
            )
        unsupported = set(item) - required
        if unsupported:
            raise ArchiveEventRestoreError(
                "archive event replay audit mismatches"
                f"[{index}] has unsupported fields: {sorted(unsupported)}"
            )
        island_id = _validate_archive_audit_non_negative_int(
            item["island_id"], f"mismatches[{index}].island_id"
        )
        cell = _validate_archive_audit_mismatch_cell(item["cell"], index)
        try:
            validate_program_identity(item["expected_program_id"])
            actual_program_id = item["actual_program_id"]
            if actual_program_id is not None:
                validate_program_identity(actual_program_id)
        except ValueError as exc:
            raise ArchiveEventRestoreError(
                f"archive event replay audit mismatches[{index}] has invalid program id: {exc}"
            ) from exc
        migration_sequence = _validate_archive_audit_positive_int(
            item["migration_sequence"],
            f"mismatches[{index}].migration_sequence",
        )
        if item["reason"] != "migration_placement_not_current_in_archive_contents":
            raise ArchiveEventRestoreError(
                "archive event replay audit mismatch reason is unsupported"
            )
        restored.append(
            {
                "island_id": island_id,
                "cell": cell,
                "expected_program_id": item["expected_program_id"],
                "actual_program_id": item["actual_program_id"],
                "migration_sequence": migration_sequence,
                "reason": item["reason"],
            }
        )
    return restored


def _validate_archive_audit_mismatch_cell(value: object, index: int) -> list[int]:
    if not isinstance(value, list) or len(value) != 3:
        raise ArchiveEventRestoreError(
            f"archive event replay audit mismatches[{index}].cell must be a 3-item list"
        )
    return [
        _validate_archive_audit_non_negative_int(
            coordinate,
            f"mismatches[{index}].cell[{coordinate_index}]",
        )
        for coordinate_index, coordinate in enumerate(value)
    ]


def _validate_archive_audit_non_negative_int(value: object, field: str) -> int:
    try:
        return _validate_snapshot_non_negative_int(value, field)
    except ArchiveStateRestoreError as exc:
        raise ArchiveEventRestoreError(str(exc)) from exc


def _validate_archive_audit_positive_int(value: object, field: str) -> int:
    try:
        return _validate_snapshot_positive_int(value, field)
    except ArchiveStateRestoreError as exc:
        raise ArchiveEventRestoreError(str(exc)) from exc


def load_runtime_archive_state_snapshot(manifest_path: str | Path) -> dict:
    """Load and validate runtime.history.archive_state from manifest.json."""
    try:
        manifest = load_strict_json_object(Path(manifest_path), source="manifest.json")
    except StrictJsonlError as exc:
        raise ArchiveStateRestoreError(str(exc)) from exc
    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        raise ArchiveStateRestoreError("manifest runtime must be an object")
    history = runtime.get("history")
    if not isinstance(history, dict):
        raise ArchiveStateRestoreError("manifest runtime.history must be an object")
    if "archive_state" not in history:
        raise ArchiveStateRestoreError("manifest runtime.history missing archive_state")
    return validate_archive_state_snapshot(history["archive_state"])


def validate_archive_state_snapshot(snapshot: object) -> dict:
    """Validate compact runtime.history.archive_state before future resume use."""
    if not isinstance(snapshot, dict):
        raise ArchiveStateRestoreError("archive state snapshot must be an object")
    required = {
        "schema",
        "resume_status",
        "cursor_policy",
        "n_islands",
        "next_island_id",
        "archive_sequence",
        "migration_sequence",
        "metric_sample_index",
        "archive_sequence_by_program_id",
        "islands",
    }
    missing = required - set(snapshot)
    if missing:
        raise ArchiveStateRestoreError(
            f"archive state snapshot missing fields: {sorted(missing)}"
        )
    optional = {
        "archive_contents",
        "migration_replay",
        "frontier_sample_index",
        "lineage_sample_index",
    }
    unsupported = set(snapshot) - required - optional
    if unsupported:
        raise ArchiveStateRestoreError(
            f"archive state snapshot has unsupported fields: {sorted(unsupported)}"
        )
    if snapshot["schema"] != "libreevolve.island_state.v1":
        raise ArchiveStateRestoreError("archive state snapshot schema is unsupported")
    if snapshot["resume_status"] not in ISLAND_STATE_ACCEPTED_RESUME_STATUSES:
        raise ArchiveStateRestoreError("archive state snapshot resume status is unsupported")
    if snapshot["cursor_policy"] != "advance_only_on_search_state_changed":
        raise ArchiveStateRestoreError("archive state snapshot cursor policy is unsupported")

    n_islands = _validate_snapshot_positive_int(snapshot["n_islands"], "n_islands")
    next_island_id = _validate_snapshot_non_negative_int(
        snapshot["next_island_id"],
        "next_island_id",
    )
    if next_island_id >= n_islands:
        raise ArchiveStateRestoreError(
            "archive state snapshot next_island_id must be less than n_islands"
        )
    archive_sequence = _validate_snapshot_non_negative_int(
        snapshot["archive_sequence"],
        "archive_sequence",
    )
    migration_sequence = _validate_snapshot_non_negative_int(
        snapshot["migration_sequence"],
        "migration_sequence",
    )
    migration_replay = _validate_archive_migration_replay_policy(
        snapshot.get("migration_replay"),
        migration_sequence,
    )
    metric_sample_index = _validate_snapshot_non_negative_int(
        snapshot["metric_sample_index"],
        "metric_sample_index",
    )
    frontier_sample_index = _validate_snapshot_non_negative_int(
        snapshot.get("frontier_sample_index", 0),
        "frontier_sample_index",
    )
    lineage_sample_index = _validate_snapshot_non_negative_int(
        snapshot.get("lineage_sample_index", 0),
        "lineage_sample_index",
    )
    sequence_by_program = _validate_archive_sequence_by_program(
        snapshot["archive_sequence_by_program_id"],
        archive_sequence,
    )
    islands = _validate_archive_island_summaries(snapshot["islands"], n_islands)
    restored = {
        "schema": snapshot["schema"],
        "resume_status": snapshot["resume_status"],
        "cursor_policy": snapshot["cursor_policy"],
        "n_islands": n_islands,
        "next_island_id": next_island_id,
        "archive_sequence": archive_sequence,
        "migration_sequence": migration_sequence,
        "metric_sample_index": metric_sample_index,
        "frontier_sample_index": frontier_sample_index,
        "lineage_sample_index": lineage_sample_index,
        "migration_replay": migration_replay,
        "archive_sequence_by_program_id": sequence_by_program,
        "islands": islands,
    }
    if "archive_contents" in snapshot:
        restored["archive_contents"] = _validate_archive_contents_snapshot(
            snapshot["archive_contents"],
            n_islands,
        )
    return restored


def _load_accepted_history_records(path: Path) -> list[dict]:
    records: list[dict] = []
    seen_ids: dict[str, int] = {}
    try:
        handle = path.open("rb")
    except OSError as exc:
        raise HistoryRestoreError(f"Failed to read history.jsonl: {exc}") from exc
    with handle:
        for line_number, raw_line in enumerate(handle, start=1):
            try:
                line = raw_line.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise HistoryRestoreError(
                    "Malformed history.jsonl at line "
                    f"{line_number}: invalid UTF-8 ({exc.reason})"
                ) from exc
            if not line.strip():
                continue
            try:
                record = json.loads(
                    line,
                    object_pairs_hook=_reject_duplicate_history_json_names,
                )
            except _DuplicateHistoryJsonNameError as exc:
                raise HistoryRestoreError(
                    f"Malformed history.jsonl at line {line_number}: {exc}"
                ) from exc
            except json.JSONDecodeError as exc:
                raise HistoryRestoreError(
                    f"Malformed history.jsonl at line {line_number}: {exc.msg}"
                ) from exc
            if not isinstance(record, dict):
                raise HistoryRestoreError(
                    f"Malformed history.jsonl at line {line_number}: expected JSON object"
                )
            _validate_restored_record_schema(
                record,
                line_number,
                expected_schema=HISTORY_RECORD_SCHEMA,
                stream_name="history.jsonl",
            )
            _validate_restored_history_fitness(record, line_number)
            _validate_restored_history_identity(record, line_number, seen_ids)
            _validate_restored_history_metrics(record, line_number)
            records.append(record)
    return records


def _validate_snapshot_positive_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ArchiveStateRestoreError(
            f"archive state snapshot {field} must be a positive integer"
        )
    return value


def _validate_snapshot_non_negative_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ArchiveStateRestoreError(
            f"archive state snapshot {field} must be a non-negative integer"
        )
    return value


def _validate_archive_sequence_by_program(
    value: object,
    archive_sequence: int,
) -> dict[str, int]:
    if not isinstance(value, dict):
        raise ArchiveStateRestoreError(
            "archive state snapshot archive_sequence_by_program_id must be an object"
        )
    restored: dict[str, int] = {}
    for program_id, sequence in value.items():
        try:
            validate_program_identity(program_id)
        except ValueError as exc:
            raise ArchiveStateRestoreError(
                f"archive state snapshot archive_sequence_by_program_id invalid id: {exc}"
            ) from exc
        sequence = _validate_snapshot_positive_int(
            sequence,
            f"archive_sequence_by_program_id.{program_id}",
        )
        if sequence > archive_sequence:
            raise ArchiveStateRestoreError(
                "archive state snapshot archive_sequence_by_program_id value "
                "must be <= archive_sequence"
            )
        restored[program_id] = sequence
    return dict(sorted(restored.items()))


def _default_archive_migration_replay_policy(migration_sequence: int) -> dict:
    return {
        "schema": ISLAND_MIGRATION_REPLAY_SCHEMA,
        "status": ISLAND_MIGRATION_REPLAY_STATUS,
        "policy": ISLAND_MIGRATION_REPLAY_POLICY,
        "migration_sequence": migration_sequence,
        "replay_engine_supported": False,
        "archive_contents_restore_covers_current_placements": True,
        "limitations": [
            "migration_event_order_not_applied_as_restore_engine",
            "migration_skip_events_not_reconstructed",
            "controller_pending_work_not_restored",
        ],
    }


def _validate_archive_migration_replay_policy(
    value: object,
    migration_sequence: int,
) -> dict:
    if value is None:
        return _default_archive_migration_replay_policy(migration_sequence)
    if not isinstance(value, dict):
        raise ArchiveStateRestoreError(
            "archive state snapshot migration_replay must be an object"
        )
    required = {
        "schema",
        "status",
        "policy",
        "migration_sequence",
        "replay_engine_supported",
        "archive_contents_restore_covers_current_placements",
        "limitations",
    }
    missing = required - set(value)
    if missing:
        raise ArchiveStateRestoreError(
            f"archive state snapshot migration_replay missing fields: {sorted(missing)}"
        )
    unsupported = set(value) - required
    if unsupported:
        raise ArchiveStateRestoreError(
            "archive state snapshot migration_replay has unsupported fields: "
            f"{sorted(unsupported)}"
        )
    if value["schema"] != ISLAND_MIGRATION_REPLAY_SCHEMA:
        raise ArchiveStateRestoreError(
            "archive state snapshot migration_replay schema is unsupported"
        )
    if value["status"] != ISLAND_MIGRATION_REPLAY_STATUS:
        raise ArchiveStateRestoreError(
            "archive state snapshot migration_replay status is unsupported"
        )
    if value["policy"] != ISLAND_MIGRATION_REPLAY_POLICY:
        raise ArchiveStateRestoreError(
            "archive state snapshot migration_replay policy is unsupported"
        )
    if value["migration_sequence"] != migration_sequence:
        raise ArchiveStateRestoreError(
            "archive state snapshot migration_replay migration_sequence must match snapshot"
        )
    if value["replay_engine_supported"] is not False:
        raise ArchiveStateRestoreError(
            "archive state snapshot migration_replay must not claim replay engine support"
        )
    if value["archive_contents_restore_covers_current_placements"] is not True:
        raise ArchiveStateRestoreError(
            "archive state snapshot migration_replay must preserve archive-content restore coverage"
        )
    limitations = value["limitations"]
    if not isinstance(limitations, list) or not limitations:
        raise ArchiveStateRestoreError(
            "archive state snapshot migration_replay limitations must be a non-empty list"
        )
    for index, limitation in enumerate(limitations):
        if not isinstance(limitation, str) or not limitation.strip():
            raise ArchiveStateRestoreError(
                "archive state snapshot migration_replay limitations"
                f"[{index}] must be non-empty text"
            )
    return {
        "schema": value["schema"],
        "status": value["status"],
        "policy": value["policy"],
        "migration_sequence": value["migration_sequence"],
        "replay_engine_supported": value["replay_engine_supported"],
        "archive_contents_restore_covers_current_placements": value[
            "archive_contents_restore_covers_current_placements"
        ],
        "limitations": list(limitations),
    }


def _validate_archive_island_summaries(value: object, n_islands: int) -> list[dict]:
    if not isinstance(value, list):
        raise ArchiveStateRestoreError("archive state snapshot islands must be a list")
    if len(value) != n_islands:
        raise ArchiveStateRestoreError(
            "archive state snapshot islands length must equal n_islands"
        )
    restored = []
    for index, island in enumerate(value):
        if not isinstance(island, dict):
            raise ArchiveStateRestoreError(
                f"archive state snapshot islands[{index}] must be an object"
            )
        required = {"island_id", "occupied_cell_count", "elite_count"}
        optional = {"pareto_frontier_count", "metric_cell_archive_count"}
        missing = required - set(island)
        if missing:
            raise ArchiveStateRestoreError(
                f"archive state snapshot islands[{index}] missing fields: {sorted(missing)}"
            )
        unsupported = set(island) - required - optional
        if unsupported:
            raise ArchiveStateRestoreError(
                "archive state snapshot islands"
                f"[{index}] has unsupported fields: {sorted(unsupported)}"
            )
        island_id = _validate_snapshot_non_negative_int(
            island["island_id"],
            f"islands[{index}].island_id",
        )
        if island_id != index:
            raise ArchiveStateRestoreError(
                f"archive state snapshot islands[{index}].island_id must equal {index}"
            )
        restored.append(
            {
                "island_id": island_id,
                "occupied_cell_count": _validate_snapshot_non_negative_int(
                    island["occupied_cell_count"],
                    f"islands[{index}].occupied_cell_count",
                ),
                "elite_count": _validate_snapshot_non_negative_int(
                    island["elite_count"],
                    f"islands[{index}].elite_count",
                ),
                "pareto_frontier_count": _validate_snapshot_non_negative_int(
                    island.get("pareto_frontier_count", 0),
                    f"islands[{index}].pareto_frontier_count",
                ),
                "metric_cell_archive_count": _validate_snapshot_non_negative_int(
                    island.get("metric_cell_archive_count", 0),
                    f"islands[{index}].metric_cell_archive_count",
                ),
            }
        )
    return restored


def _validate_archive_contents_snapshot(value: object, n_islands: int) -> dict:
    if not isinstance(value, dict):
        raise ArchiveStateRestoreError(
            "archive state snapshot archive_contents must be an object"
        )
    required = {"schema", "restore_status", "islands"}
    missing = required - set(value)
    if missing:
        raise ArchiveStateRestoreError(
            f"archive state snapshot archive_contents missing fields: {sorted(missing)}"
        )
    unsupported = set(value) - required
    if unsupported:
        raise ArchiveStateRestoreError(
            "archive state snapshot archive_contents has unsupported fields: "
            f"{sorted(unsupported)}"
        )
    if value["schema"] != "libreevolve.island_archive_contents.v1":
        raise ArchiveStateRestoreError(
            "archive state snapshot archive_contents schema is unsupported"
        )
    if value["restore_status"] != ISLAND_ARCHIVE_CONTENTS_RESTORE_STATUS:
        raise ArchiveStateRestoreError(
            "archive state snapshot archive_contents restore status is unsupported"
        )
    islands = value["islands"]
    if not isinstance(islands, list) or len(islands) != n_islands:
        raise ArchiveStateRestoreError(
            "archive state snapshot archive_contents islands length must equal n_islands"
        )
    restored = []
    for index, island in enumerate(islands):
        if not isinstance(island, dict):
            raise ArchiveStateRestoreError(
                "archive state snapshot archive_contents islands"
                f"[{index}] must be an object"
            )
        required_island = {"island_id", "archive"}
        missing_island = required_island - set(island)
        if missing_island:
            raise ArchiveStateRestoreError(
                "archive state snapshot archive_contents islands"
                f"[{index}] missing fields: {sorted(missing_island)}"
            )
        unsupported_island = set(island) - required_island
        if unsupported_island:
            raise ArchiveStateRestoreError(
                "archive state snapshot archive_contents islands"
                f"[{index}] has unsupported fields: {sorted(unsupported_island)}"
            )
        if island["island_id"] != index:
            raise ArchiveStateRestoreError(
                "archive state snapshot archive_contents islands"
                f"[{index}].island_id must equal {index}"
            )
        if not isinstance(island["archive"], dict):
            raise ArchiveStateRestoreError(
                "archive state snapshot archive_contents islands"
                f"[{index}].archive must be an object"
            )
        restored.append(
            {
                "island_id": index,
                "archive": copy.deepcopy(island["archive"]),
            }
        )
    return {
        "schema": value["schema"],
        "restore_status": value["restore_status"],
        "islands": restored,
    }


def _archive_event_replay_absent_audit(
    archive_state_snapshot: Mapping[str, object],
) -> dict:
    validate_archive_state_snapshot(archive_state_snapshot)
    return {
        "schema": "libreevolve.archive_event_replay_audit.v1",
        "status": "archive_events_absent",
        "audit_only": True,
        "replay_engine_supported": False,
        "event_count": 0,
        "admitted_event_count": 0,
        "skipped_event_count": 0,
        "final_replayed_placement_count": 0,
        "matched_placement_count": 0,
        "superseded_or_missing_count": 0,
        "mismatches": [],
        "mismatch_retention_limit": _MAX_ARCHIVE_REPLAY_MISMATCHES,
        "limitations": _archive_event_replay_audit_limitations(),
    }


def _archive_snapshot_cell_map(
    snapshot: dict,
) -> dict[tuple[int, tuple[int, ...]], str] | None:
    contents = snapshot.get("archive_contents")
    if not isinstance(contents, dict):
        return None
    cells: dict[tuple[int, tuple[int, ...]], str] = {}
    for island in contents["islands"]:
        island_id = island["island_id"]
        archive = island["archive"]
        for cell_record in archive.get("cells", []):
            cells[(island_id, tuple(cell_record["cell"]))] = cell_record["program_id"]
    return cells


def _archive_event_replay_audit_limitations() -> list[str]:
    return [
        "audit_replays_migration_rows_only_not_normal_archive_admissions",
        "audit_does_not_restore_controller_pending_work",
        "superseded_non_migration_cell_replacements_report_as_mismatches",
        "archive_contents_snapshot_remains_restore_source",
    ]


def _validate_archive_event_record(
    record: dict,
    line_number: int,
    previous_sequence: int,
) -> int:
    required = {
        "schema_version",
        "record_schema",
        "event_type",
        "migration_sequence",
        "program_id",
        "canonical_program_id",
        "source_island",
        "target_island",
        "identity_policy",
        "clone_id",
        "admitted",
        "reason",
        "cell",
        "selection_score",
    }
    missing = required - set(record)
    if missing:
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            f"missing fields: {sorted(missing)}"
        )
    supported = required | {"objective_vector"}
    unsupported = set(record) - supported
    if unsupported:
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            f"unsupported fields: {sorted(unsupported)}"
        )
    if record["event_type"] != "migration":
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            "event_type must be migration"
        )
    sequence = _validate_archive_event_positive_int(
        record["migration_sequence"],
        line_number,
        "migration_sequence",
    )
    if sequence < previous_sequence:
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            "migration_sequence must be non-decreasing"
        )
    for field in ("program_id", "canonical_program_id"):
        try:
            validate_program_identity(record[field])
        except ValueError as exc:
            raise ArchiveEventRestoreError(
                f"Malformed archive_events.jsonl at line {line_number}: {field}: {exc}"
            ) from exc
    if record["program_id"] != record["canonical_program_id"]:
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            "canonical_program_id must match program_id"
        )
    _validate_archive_event_non_negative_int(
        record["source_island"],
        line_number,
        "source_island",
    )
    _validate_archive_event_non_negative_int(
        record["target_island"],
        line_number,
        "target_island",
    )
    if record["identity_policy"] != "canonical_id_reference":
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            "identity_policy must be canonical_id_reference"
        )
    if record["clone_id"] is not None:
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            "clone_id must be null"
        )
    if not isinstance(record["admitted"], bool):
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            "admitted must be boolean"
        )
    _validate_archive_event_reason(record["reason"], line_number)
    _validate_archive_event_cell(record["cell"], line_number)
    selection_score = record["selection_score"]
    if selection_score is not None and not _is_finite_real(selection_score):
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            "selection_score must be finite or null"
        )
    _validate_archive_event_objective_vector(
        record.get("objective_vector"),
        line_number,
    )
    return sequence


def _validate_archive_event_objective_vector(value: object, line_number: int) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            "objective_vector must be an object or null"
        )
    allowed = {"policy", "normalized_metrics", "selection_policy"}
    unsupported = sorted(set(value) - allowed)
    if unsupported:
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            f"objective_vector has unsupported fields: {unsupported}"
        )
    if value.get("policy") != "normalized_declared_metric_vector_v1":
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            "objective_vector.policy is unsupported"
        )
    metrics = value.get("normalized_metrics")
    if not isinstance(metrics, dict):
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            "objective_vector.normalized_metrics must be an object"
        )
    for metric, score in metrics.items():
        if not isinstance(metric, str):
            raise ArchiveEventRestoreError(
                f"Malformed archive_events.jsonl at line {line_number}: "
                "objective_vector metric names must be strings"
            )
        if not _is_finite_real(score) or not 0.0 <= float(score) <= 1.0:
            raise ArchiveEventRestoreError(
                f"Malformed archive_events.jsonl at line {line_number}: "
                "objective_vector metric values must be finite normalized scores"
            )
    if "selection_policy" in value and not isinstance(value["selection_policy"], dict):
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            "objective_vector.selection_policy must be an object"
        )


def _validate_archive_event_positive_int(
    value: object,
    line_number: int,
    field: str,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            f"{field} must be a positive integer"
        )
    return value


def _validate_archive_event_non_negative_int(
    value: object,
    line_number: int,
    field: str,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            f"{field} must be a non-negative integer"
        )
    return value


def _validate_archive_event_reason(value: object, line_number: int) -> None:
    if not isinstance(value, str) or not value:
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            "reason must be non-empty text"
        )
    if len(value) > _MAX_ARCHIVE_EVENT_REASON_CHARS:
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            f"reason exceeds {_MAX_ARCHIVE_EVENT_REASON_CHARS} chars"
        )
    if redact_sensitive_text(value) != value:
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            "reason must not contain secret-like text"
        )


def _validate_archive_event_cell(value: object, line_number: int) -> None:
    if value is None:
        return
    if not isinstance(value, list) or len(value) != 3:
        raise ArchiveEventRestoreError(
            f"Malformed archive_events.jsonl at line {line_number}: "
            "cell must be null or a 3-item list"
        )
    for index, coordinate in enumerate(value):
        _validate_archive_event_non_negative_int(
            coordinate,
            line_number,
            f"cell[{index}]",
        )


def _reject_duplicate_history_json_names(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateHistoryJsonNameError(
                f"duplicate JSON object name {key!r}"
            )
        result[key] = value
    return result


def _validate_restored_history_fitness(record: dict, line_number: int) -> None:
    if not _is_finite_real(record.get("fitness")):
        raise HistoryRestoreError(
            f"Malformed history.jsonl at line {line_number}: fitness must be a finite number"
        )


def _validate_restored_history_identity(
    record: dict, line_number: int, seen_ids: dict[str, int]
) -> None:
    try:
        validate_program_identity(record.get("id"), record.get("parent_id"), record.get("lineage"))
    except ValueError as exc:
        raise HistoryRestoreError(
            f"Malformed history.jsonl at line {line_number}: {exc}"
        ) from exc
    program_id = record["id"]
    if program_id in seen_ids:
        raise HistoryRestoreError(
            "Malformed history.jsonl at line "
            f"{line_number}: duplicate program id {program_id!r} "
            f"(first seen at line {seen_ids[program_id]})"
        )
    seen_ids[program_id] = line_number


def _validate_restored_history_metrics(record: dict, line_number: int) -> None:
    metrics = record.get("metrics")
    if metrics is None:
        return
    if not isinstance(metrics, dict):
        raise HistoryRestoreError(
            f"Malformed history.jsonl at line {line_number}: metrics must be an object"
        )
    try:
        record["metrics"] = validate_program_metrics(metrics)
    except ValueError as exc:
        raise HistoryRestoreError(
            f"Malformed history.jsonl at line {line_number}: {exc}"
        ) from exc


def _validate_restored_failure_record(
    record: dict, line_number: int, seen_ids: dict[str, int]
) -> None:
    _validate_restored_failure_identity(record, line_number, seen_ids)
    _validate_restored_failure_generation(record, line_number)
    _validate_restored_failure_payload(record, line_number)
    _validate_restored_failure_changed_files(record, line_number)
    _validate_restored_failure_fingerprint(record, line_number)


def _validate_restored_failure_identity(
    record: dict, line_number: int, seen_ids: dict[str, int]
) -> None:
    try:
        validate_program_identity(record.get("program_id"), record.get("parent_id"), None)
    except ValueError as exc:
        raise HistoryRestoreError(
            f"Malformed failure_history.jsonl at line {line_number}: {exc}"
        ) from exc
    program_id = record["program_id"]
    if program_id in seen_ids:
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: duplicate failed program id {program_id!r} "
            f"(first seen at line {seen_ids[program_id]})"
        )
    seen_ids[program_id] = line_number


def _validate_restored_failure_generation(record: dict, line_number: int) -> None:
    generation = record.get("generation")
    if (
        not isinstance(generation, bool)
        and isinstance(generation, int)
        and generation >= 0
    ):
        return
    raise HistoryRestoreError(
        "Malformed failure_history.jsonl at line "
        f"{line_number}: generation must be a non-negative integer"
    )


def _validate_restored_failure_payload(record: dict, line_number: int) -> None:
    mutation_text = record.get("mutation_text")
    if not isinstance(mutation_text, str):
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: mutation_text must be a bounded diagnostic string"
        )
    mutation_truncated = record.get("mutation_truncated")
    if mutation_truncated is not None and not isinstance(mutation_truncated, bool):
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: mutation_truncated must be boolean when present"
        )
    mutation_sha256 = record.get("mutation_sha256")
    if not _is_sha256_hex(mutation_sha256):
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: mutation_sha256 must be a SHA-256 hex digest"
        )
    payload_text = record.get("mutation_payload_text")
    payload_type = record.get("mutation_payload_type")
    if payload_text is None and payload_type is None:
        return
    if not isinstance(payload_text, bool):
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: mutation_payload_text must be boolean when present"
        )
    if not isinstance(payload_type, str) or not payload_type:
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: mutation_payload_type must be a non-empty string when present"
        )
    if payload_text is False and record.get("diff_error") != "non_text_mutation_payload":
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: non-text mutation payloads must use "
            "diff_error='non_text_mutation_payload'"
        )


def _validate_restored_failure_changed_files(record: dict, line_number: int) -> None:
    changed_files = record.get("changed_files")
    if changed_files is None:
        return
    if not isinstance(changed_files, list):
        raise HistoryRestoreError(
            f"Malformed failure_history.jsonl at line {line_number}: changed_files must be a list"
        )
    for path in changed_files:
        try:
            normalize_candidate_path(path)
        except ValueError as exc:
            raise HistoryRestoreError(
                f"Malformed failure_history.jsonl at line {line_number}: {exc}"
            ) from exc
    file_deltas = record.get("file_deltas")
    if file_deltas is None:
        return
    if not isinstance(file_deltas, list):
        raise HistoryRestoreError(
            f"Malformed failure_history.jsonl at line {line_number}: file_deltas must be a list"
        )
    for delta in file_deltas:
        if not isinstance(delta, dict):
            raise HistoryRestoreError(
                "Malformed failure_history.jsonl at line "
                f"{line_number}: file_deltas entries must be objects"
            )
        try:
            normalize_candidate_path(delta.get("path"))
        except ValueError as exc:
            raise HistoryRestoreError(
                f"Malformed failure_history.jsonl at line {line_number}: {exc}"
            ) from exc
        if delta.get("change") not in {"added", "deleted", "modified", "seed"}:
            raise HistoryRestoreError(
                "Malformed failure_history.jsonl at line "
                f"{line_number}: file_deltas change must be added, deleted, modified, or seed"
            )


def _validate_restored_failure_fingerprint(record: dict, line_number: int) -> None:
    fingerprint = record.get("failure_fingerprint")
    if fingerprint is None:
        return
    if not isinstance(fingerprint, dict):
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: failure_fingerprint must be an object"
        )
    if fingerprint.get("schema") != "failure_fingerprint_v1":
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: unsupported failure_fingerprint schema"
        )
    if not _is_sha256_hex(fingerprint.get("sha256")):
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: failure_fingerprint.sha256 must be a SHA-256 hex digest"
        )
    if fingerprint.get("parent_id") != record.get("parent_id"):
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: failure_fingerprint.parent_id must match parent_id"
        )
    if fingerprint.get("mutation_sha256") != record.get("mutation_sha256"):
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: failure_fingerprint.mutation_sha256 must match mutation_sha256"
        )
    payload_text = record.get("mutation_payload_text")
    payload_type = record.get("mutation_payload_type")
    if payload_text is not None and fingerprint.get("mutation_payload_text") != payload_text:
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: failure_fingerprint.mutation_payload_text must match"
        )
    if payload_type is not None and fingerprint.get("mutation_payload_type") != payload_type:
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: failure_fingerprint.mutation_payload_type must match"
        )
    if "changed_files" in fingerprint and fingerprint.get("changed_files") != record.get("changed_files", []):
        raise HistoryRestoreError(
            "Malformed failure_history.jsonl at line "
            f"{line_number}: failure_fingerprint.changed_files must match changed_files"
        )


def _restored_failure_payload_replay_policy(record: dict) -> dict:
    payload_text = record.get("mutation_payload_text")
    if payload_text is False:
        payload_kind = "non_text"
    elif payload_text is True:
        payload_kind = "text"
    else:
        payload_kind = "legacy_or_seed"
    return {
        "policy": "diagnostic_only_do_not_reapply",
        "payload_kind": payload_kind,
        "payload_type": record.get("mutation_payload_type"),
        "mutation_text": "bounded_redacted_diagnostic",
        "mutation_sha256": record.get("mutation_sha256"),
        "queryable": True,
    }


def _is_sha256_hex(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _validate_restored_record_schema(
    record: dict,
    line_number: int,
    *,
    expected_schema: str,
    stream_name: str,
) -> None:
    schema_version = record.get("schema_version")
    record_schema = record.get("record_schema")
    if schema_version is None and record_schema is None:
        return
    if schema_version != ARTIFACT_SCHEMA_VERSION:
        raise HistoryRestoreError(
            f"Malformed {stream_name} at line "
            f"{line_number}: unsupported schema_version {schema_version!r}"
        )
    if record_schema != expected_schema:
        raise HistoryRestoreError(
            f"Malformed {stream_name} at line "
            f"{line_number}: unsupported record_schema {record_schema!r}"
        )


def _candidate_workspace_limits_from_config(config: Config) -> dict:
    return {
        "max_files": config.max_candidate_workspace_files,
        "max_file_chars": config.max_candidate_file_chars,
        "max_total_chars": config.max_candidate_total_chars,
        "max_static_file_bytes": config.max_candidate_static_file_bytes,
        "max_total_static_bytes": config.max_candidate_total_static_bytes,
    }


def validate_objective_schema(schema: object) -> dict:
    if schema is None:
        raise ValueError("objective_schema is required")
    if not isinstance(schema, Mapping):
        raise ValueError("objective_schema must be a mapping")
    unsupported = sorted(set(schema) - {"metrics", "primary_metric", "primary_bounds", "metric_count"})
    if unsupported:
        raise ValueError(f"objective_schema has unsupported fields {unsupported}")
    missing = [
        field
        for field in ("metrics", "primary_metric", "primary_bounds", "metric_count")
        if field not in schema
    ]
    if missing:
        raise ValueError(f"objective_schema missing required fields {missing}")

    metrics, primary_metric, primary_bounds = _normalize_metric_schema(
        schema["metrics"],
        Path("objective_schema"),
        primary_metric=schema["primary_metric"],
    )
    raw_primary_bounds = schema["primary_bounds"]
    if not isinstance(raw_primary_bounds, (list, tuple)) or len(raw_primary_bounds) != 2:
        raise ValueError("objective_schema primary_bounds must be [lo, hi]")
    if isinstance(raw_primary_bounds[0], bool) or isinstance(raw_primary_bounds[1], bool):
        raise ValueError("objective_schema primary_bounds must be numeric [lo, hi]")
    try:
        declared_primary_bounds = (float(raw_primary_bounds[0]), float(raw_primary_bounds[1]))
    except (TypeError, ValueError) as exc:
        raise ValueError("objective_schema primary_bounds must be numeric [lo, hi]") from exc
    if not all(math.isfinite(value) for value in declared_primary_bounds):
        raise ValueError("objective_schema primary_bounds must be finite")
    if declared_primary_bounds != primary_bounds:
        raise ValueError(
            "objective_schema primary_bounds must match the declared primary metric bounds"
        )
    metric_count = schema["metric_count"]
    if isinstance(metric_count, bool) or not isinstance(metric_count, int):
        raise ValueError("objective_schema metric_count must be an integer")
    if metric_count != len(metrics):
        raise ValueError("objective_schema metric_count must match metrics length")
    return {
        "metrics": metrics,
        "primary_metric": primary_metric,
        "primary_bounds": [primary_bounds[0], primary_bounds[1]],
        "metric_count": len(metrics),
    }


def _validate_admission_threshold(threshold: object) -> float:
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise ValueError("archive admission threshold must be a finite number")
    value = float(threshold)
    if not math.isfinite(value):
        raise ValueError("archive admission threshold must be a finite number")
    return value


def _metric_order_from_objective_schema(schema: dict) -> list[str]:
    primary_metric = schema["primary_metric"]
    declared_order = [metric["name"] for metric in schema["metrics"]]
    return [primary_metric] + [name for name in declared_order if name != primary_metric]


def _history_safe_selection_score(program: Program) -> float | None:
    value = _selection_score(program)
    return value if math.isfinite(value) else None


def _history_safe_objective_vector(program: Program) -> dict | None:
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    normalized_metrics = metadata.get("normalized_metrics")
    if not isinstance(normalized_metrics, dict):
        return None
    metrics: dict[str, float] = {}
    for name, value in sorted(normalized_metrics.items()):
        if isinstance(name, str) and _is_finite_real(value):
            numeric = float(value)
            if 0.0 <= numeric <= 1.0:
                metrics[name] = numeric
    if not metrics:
        return None
    record: dict[str, object] = {
        "policy": "normalized_declared_metric_vector_v1",
        "normalized_metrics": metrics,
    }
    selection_policy = metadata.get("selection_policy")
    if isinstance(selection_policy, dict):
        record["selection_policy"] = copy.deepcopy(selection_policy)
    return record


def _objective_frontier_snapshot(
    programs: list[Program],
    metric_order: list[str],
    *,
    limit: int,
) -> dict:
    metric_order = [name for name in metric_order if isinstance(name, str) and name]
    candidates = [
        record
        for program in programs
        if (
            record := _objective_frontier_candidate(program, metric_order)
        )
        is not None
    ]
    frontier = [
        candidate
        for index, candidate in enumerate(candidates)
        if not any(
            other_index != index
            and _objective_frontier_dominates(
                other["normalized_metrics"],
                candidate["normalized_metrics"],
                metric_order,
            )
            for other_index, other in enumerate(candidates)
        )
    ]
    frontier.sort(
        key=lambda record: (
            -(record["selection_score"] if record["selection_score"] is not None else -1.0),
            record["program_id"],
        )
    )
    retained = frontier[:limit]
    return {
        "schema": "libreevolve.objective_frontier.v1",
        "policy": "pareto_frontier_over_complete_declared_normalized_metrics",
        "metric_order": list(metric_order),
        "program_count_considered": len(candidates),
        "frontier_size": len(frontier),
        "retained_frontier_size": len(retained),
        "retention_limit": limit,
        "programs": retained,
        "limitations": [
            "diagnostic_frontier_not_archive_selection_policy",
            "requires_complete_declared_normalized_metric_vectors",
            "plugin_metrics_not_declared_in_objective_schema_are_excluded",
        ],
    }


def _objective_frontier_candidate(
    program: Program,
    metric_order: list[str],
) -> dict | None:
    if program.evaluation.get("is_valid") is not True:
        return None
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    normalized = metadata.get("normalized_metrics")
    if not isinstance(normalized, dict) or not metric_order:
        return None
    metrics: dict[str, float] = {}
    for name in metric_order:
        value = normalized.get(name)
        if not _is_finite_real(value):
            return None
        numeric = float(value)
        if not 0.0 <= numeric <= 1.0:
            return None
        metrics[name] = numeric
    selection_score = _history_safe_selection_score(program)
    return {
        "program_id": program.id,
        "generation": program.generation,
        "selection_score": selection_score,
        "normalized_metrics": metrics,
    }


def _objective_frontier_dominates(
    left: dict[str, float],
    right: dict[str, float],
    metric_order: list[str],
) -> bool:
    return all(left[name] >= right[name] for name in metric_order) and any(
        left[name] > right[name] for name in metric_order
    )


def _objective_metric_leaders_snapshot(
    programs: list[Program],
    metric_order: list[str],
) -> dict:
    metric_order = [name for name in metric_order if isinstance(name, str) and name]
    leaders: list[dict] = []
    for metric in metric_order:
        candidates = [
            record
            for program in programs
            if (
                record := _objective_metric_leader_candidate(program, metric, metric_order)
            )
            is not None
        ]
        if not candidates:
            continue
        candidates.sort(
            key=lambda record: (
                -record["normalized_metric"],
                -(record["selection_score"] if record["selection_score"] is not None else -1.0),
                record["program_id"],
            )
        )
        leaders.append(candidates[0])
    return {
        "schema": "libreevolve.objective_metric_leaders.v1",
        "policy": "best_program_per_declared_normalized_metric",
        "metric_order": list(metric_order),
        "leader_count": len(leaders),
        "leaders": leaders,
        "limitations": [
            "diagnostic_metric_leaders_not_archive_selection_policy",
            "requires_declared_normalized_metric_value",
            "plugin_metrics_not_declared_in_objective_schema_are_excluded",
        ],
    }


def _objective_metric_archives_snapshot(
    programs: list[Program],
    metric_order: list[str],
    *,
    limit: int,
) -> dict:
    metric_order = [name for name in metric_order if isinstance(name, str) and name]
    archives: list[dict] = []
    for metric in metric_order:
        candidates = [
            record
            for program in programs
            if (
                record := _objective_metric_leader_candidate(program, metric, metric_order)
            )
            is not None
        ]
        candidates.sort(
            key=lambda record: (
                -record["normalized_metric"],
                -(record["selection_score"] if record["selection_score"] is not None else -1.0),
                record["program_id"],
            )
        )
        retained = candidates[:limit]
        archives.append(
            {
                "metric": metric,
                "program_count_considered": len(candidates),
                "retained_count": len(retained),
                "retention_limit": limit,
                "programs": retained,
            }
        )
    return {
        "schema": "libreevolve.objective_metric_archives.v1",
        "policy": "top_programs_per_declared_normalized_metric",
        "metric_order": list(metric_order),
        "retention_limit": limit,
        "archive_count": len(archives),
        "archives": archives,
        "limitations": [
            "diagnostic_metric_archives_not_archive_replacement_policy",
            "requires_declared_normalized_metric_value",
            "plugin_metrics_not_declared_in_objective_schema_are_excluded",
        ],
    }


def _objective_metric_leader_candidate(
    program: Program,
    metric: str,
    metric_order: list[str],
) -> dict | None:
    if program.evaluation.get("is_valid") is not True:
        return None
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    normalized = metadata.get("normalized_metrics")
    if not isinstance(normalized, dict):
        return None
    value = normalized.get(metric)
    if not _is_finite_real(value):
        return None
    normalized_metric = float(value)
    if not 0.0 <= normalized_metric <= 1.0:
        return None
    declared_metrics: dict[str, float] = {}
    for name in metric_order:
        candidate_value = normalized.get(name)
        if _is_finite_real(candidate_value):
            numeric = float(candidate_value)
            if 0.0 <= numeric <= 1.0:
                declared_metrics[name] = numeric
    return {
        "metric": metric,
        "program_id": program.id,
        "generation": program.generation,
        "normalized_metric": normalized_metric,
        "selection_score": _history_safe_selection_score(program),
        "normalized_metrics": declared_metrics,
    }


def _score_index_snapshot(
    programs: list[Program],
    *,
    limit: int,
) -> dict:
    candidates = [
        record
        for program in programs
        if (record := _score_index_program(program)) is not None
    ]
    candidates.sort(key=_score_index_sort_key)
    retained = candidates[:limit]
    return {
        "schema": "libreevolve.score_index.v1",
        "policy": "top_valid_programs_by_selection_score_then_fitness",
        "program_count_considered": len(candidates),
        "retained_count": len(retained),
        "retention_limit": limit,
        "programs": retained,
        "limitations": [
            "diagnostic_score_index_not_sampling_replay_engine",
            "valid_history_programs_only",
            "selection_score_uses_current_record_metadata_policy",
            "bounded_top_score_view_not_full_persisted_database_index",
        ],
    }


def _score_index_program(program: Program) -> dict | None:
    if program.evaluation.get("is_valid") is not True:
        return None
    record: dict[str, object] = {
        "program_id": program.id,
        "generation": program.generation,
        "lineage_root_id": _program_lineage_root_id(program),
        "selection_score": _history_safe_selection_score(program),
        "fitness": float(program.fitness),
    }
    admission = _history_safe_archive_admission_summary(program)
    if admission:
        record["archive_admission"] = admission
    objective_vector = _history_safe_objective_vector(program)
    if objective_vector is not None:
        record["objective_vector"] = objective_vector
    return record


def _history_safe_archive_admission_summary(program: Program) -> dict:
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    admission = metadata.get("archive_admission")
    if not isinstance(admission, Mapping):
        return {}
    summary: dict[str, object] = {}
    for field in (
        "admitted",
        "cell_admitted",
        "elite_retained",
        "sampling_eligible",
        "search_state_changed",
    ):
        value = admission.get(field)
        if isinstance(value, bool):
            summary[field] = value
    for field in ("reason",):
        value = admission.get(field)
        if isinstance(value, str) and value:
            summary[field] = value
    for field in ("island_id", "archive_sequence"):
        value = admission.get(field)
        if isinstance(value, int) and not isinstance(value, bool):
            summary[field] = value
    cell = admission.get("cell")
    if isinstance(cell, list) and all(
        isinstance(item, int) and not isinstance(item, bool) for item in cell
    ):
        summary["cell"] = list(cell)
    return summary


def _score_index_sort_key(record: dict) -> tuple:
    selection_score = record.get("selection_score")
    fitness = record.get("fitness")
    generation = record.get("generation")
    program_id = record.get("program_id")
    return (
        -(float(selection_score) if _is_finite_real(selection_score) else float("-inf")),
        -(float(fitness) if _is_finite_real(fitness) else float("-inf")),
        -(int(generation) if isinstance(generation, int) and not isinstance(generation, bool) else -1),
        str(program_id) if isinstance(program_id, str) else "",
    )


def _lineage_index_snapshot(
    programs: list[Program],
    *,
    root_limit: int,
    programs_per_root_limit: int,
) -> dict:
    by_root: dict[str, list[dict]] = {}
    for program in programs:
        if program.evaluation.get("is_valid") is not True:
            continue
        record = _lineage_index_program(program)
        by_root.setdefault(record["lineage_root_id"], []).append(record)

    lineages: list[dict] = []
    for root_id, records in by_root.items():
        records.sort(key=_lineage_index_sort_key)
        retained = records[:programs_per_root_limit]
        best = retained[0] if retained else None
        if best is None:
            continue
        lineages.append(
            {
                "lineage_root_id": root_id,
                "program_count": len(records),
                "retained_count": len(retained),
                "program_retention_limit": programs_per_root_limit,
                "best_program": best,
                "programs": retained,
            }
        )
    lineages.sort(
        key=lambda lineage: (
            _lineage_index_sort_key(lineage["best_program"]),
            lineage["lineage_root_id"],
        )
    )
    retained_lineages = lineages[:root_limit]
    return {
        "schema": "libreevolve.lineage_index.v1",
        "policy": "best_valid_programs_grouped_by_root_lineage",
        "program_count_considered": sum(lineage["program_count"] for lineage in lineages),
        "lineage_count": len(lineages),
        "retained_lineage_count": len(retained_lineages),
        "root_retention_limit": root_limit,
        "program_retention_limit": programs_per_root_limit,
        "lineages": retained_lineages,
        "limitations": [
            "diagnostic_lineage_index_not_sampling_replay_engine",
            "valid_history_programs_only",
            "bounded_best_per_root_view_not_full_persisted_database_index",
        ],
    }


def _lineage_index_program(program: Program) -> dict:
    record: dict[str, object] = {
        "program_id": program.id,
        "lineage_root_id": _program_lineage_root_id(program),
        "parent_id": program.parent_id,
        "generation": program.generation,
        "lineage_depth": len(program.lineage),
        "selection_score": _history_safe_selection_score(program),
        "fitness": float(program.fitness),
    }
    objective_vector = _history_safe_objective_vector(program)
    if objective_vector is not None:
        record["objective_vector"] = objective_vector
    else:
        normalized_metrics = _history_safe_normalized_metrics(program)
        if normalized_metrics:
            record["normalized_metrics"] = normalized_metrics
    return record


def _descriptor_index_snapshot(
    programs: list[Program],
    *,
    limit: int,
) -> dict:
    by_descriptor: dict[str, list[dict]] = {}
    for program in programs:
        if program.evaluation.get("is_valid") is not True:
            continue
        descriptors = _history_safe_archive_descriptors(program)
        for descriptor, value in descriptors.items():
            by_descriptor.setdefault(descriptor, []).append(
                _descriptor_index_program(program, descriptor, value)
            )

    descriptors: list[dict] = []
    for descriptor, records in sorted(by_descriptor.items()):
        records.sort(key=_descriptor_index_sort_key)
        retained = records[:limit]
        descriptors.append(
            {
                "descriptor": descriptor,
                "program_count_considered": len(records),
                "retained_count": len(retained),
                "retention_limit": limit,
                "programs": retained,
            }
        )
    return {
        "schema": "libreevolve.descriptor_index.v1",
        "policy": "top_valid_programs_per_archive_descriptor",
        "descriptor_count": len(descriptors),
        "retention_limit": limit,
        "descriptors": descriptors,
        "limitations": [
            "diagnostic_descriptor_index_not_sampling_replay_engine",
            "valid_history_programs_with_archive_admission_descriptors_only",
            "descriptor_values_are_insertion_time_archive_coordinates",
            "bounded_top_per_descriptor_view_not_full_persisted_database_index",
        ],
    }


def _descriptor_index_program(
    program: Program,
    descriptor: str,
    value: float,
) -> dict:
    record: dict[str, object] = {
        "descriptor": descriptor,
        "program_id": program.id,
        "lineage_root_id": _program_lineage_root_id(program),
        "generation": program.generation,
        "descriptor_value": value,
        "selection_score": _history_safe_selection_score(program),
        "fitness": float(program.fitness),
    }
    objective_vector = _history_safe_objective_vector(program)
    if objective_vector is not None:
        record["objective_vector"] = objective_vector
    else:
        normalized_metrics = _history_safe_normalized_metrics(program)
        if normalized_metrics:
            record["normalized_metrics"] = normalized_metrics
    return record


def _history_safe_archive_descriptors(program: Program) -> dict[str, float]:
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    admission = metadata.get("archive_admission")
    if not isinstance(admission, Mapping):
        return {}
    raw = admission.get("descriptors")
    if not isinstance(raw, Mapping):
        return {}
    descriptors: dict[str, float] = {}
    for name, value in sorted(raw.items()):
        if isinstance(name, str) and name and _is_finite_real(value):
            descriptors[name] = float(value)
    return descriptors


def _descriptor_index_sort_key(record: dict) -> tuple:
    descriptor_value = record.get("descriptor_value")
    selection_score = record.get("selection_score")
    fitness = record.get("fitness")
    generation = record.get("generation")
    program_id = record.get("program_id")
    return (
        -(float(descriptor_value) if _is_finite_real(descriptor_value) else float("-inf")),
        -(float(selection_score) if _is_finite_real(selection_score) else float("-inf")),
        -(float(fitness) if _is_finite_real(fitness) else float("-inf")),
        -(int(generation) if isinstance(generation, int) and not isinstance(generation, bool) else -1),
        str(program_id) if isinstance(program_id, str) else "",
    )


def _feedback_index_snapshot(
    programs: list[Program],
    *,
    limit: int,
) -> dict:
    by_grader: dict[str, list[dict]] = {}
    for program in programs:
        for record in _history_safe_feedback_records(program):
            grader_name = record["feedback_name"]
            by_grader.setdefault(grader_name, []).append(record)

    graders: list[dict] = []
    for grader_name, records in sorted(by_grader.items()):
        records.sort(key=_feedback_index_sort_key)
        retained = records[:limit]
        graders.append(
            {
                "feedback_name": grader_name,
                "record_count": len(records),
                "retained_count": len(retained),
                "retention_limit": limit,
                "programs": retained,
            }
        )
    return {
        "schema": "libreevolve.feedback_index.v1",
        "policy": "top_program_feedback_records_by_grader",
        "feedback_grader_count": len(graders),
        "record_count": sum(grader["record_count"] for grader in graders),
        "retention_limit": limit,
        "graders": graders,
        "limitations": [
            "diagnostic_feedback_index_not_sampling_replay_engine",
            "bounded_feedback_records_grouped_by_grader",
            "raw_feedback_text_retention_follows_feedback_retention_policy",
            "not_a_full_persisted_feedback_embedding_or_ranking_database",
        ],
    }


def _history_safe_feedback_records(program: Program) -> list[dict]:
    evaluation = program.evaluation if isinstance(program.evaluation, dict) else {}
    metadata = evaluation.get("metadata")
    if not isinstance(metadata, Mapping):
        return []
    feedback = metadata.get("llm_feedback")
    if not isinstance(feedback, list):
        return []
    records = []
    for index, item in enumerate(feedback):
        if isinstance(item, Mapping):
            records.append(_feedback_index_record(program, index, item))
    return records


def _feedback_index_record(
    program: Program,
    record_index: int,
    feedback: Mapping,
) -> dict:
    name = feedback.get("name")
    metric = feedback.get("metric")
    error = feedback.get("error")
    record: dict[str, object] = {
        "feedback_name": name if isinstance(name, str) and name else f"feedback_{record_index}",
        "record_index": record_index,
        "program_id": program.id,
        "lineage_root_id": _program_lineage_root_id(program),
        "generation": program.generation,
        "evaluation_is_valid": program.evaluation.get("is_valid") is True,
        "selection_score": _history_safe_selection_score(program),
        "fitness": float(program.fitness),
    }
    if isinstance(metric, str) and metric:
        record["metric"] = metric
    for field in (
        "score",
        "normalized_score",
        "weighted_delta",
        "failure_delta",
    ):
        value = feedback.get(field)
        if _is_finite_real(value):
            record[field] = float(value)
    if isinstance(feedback.get("discard"), bool):
        record["discard"] = feedback["discard"]
    if isinstance(feedback.get("objective_metric"), bool):
        record["objective_metric"] = feedback["objective_metric"]
    if isinstance(error, str) and error:
        record["error"] = error
    feedback_text = feedback.get("feedback")
    if isinstance(feedback_text, str) and feedback_text:
        record["feedback_text"] = _feedback_index_text_summary(feedback_text)
    retention = _feedback_index_retention_summary(feedback)
    if retention:
        record["retention"] = retention
    objective_vector = _history_safe_objective_vector(program)
    if objective_vector is not None:
        record["objective_vector"] = objective_vector
    return record


def _feedback_index_text_summary(value: str) -> dict:
    redacted = redact_sensitive_text(value)
    return {
        "policy": "bounded_redacted_feedback_preview_v1",
        "chars": len(value),
        "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "preview": redacted[:_MAX_FEEDBACK_INDEX_TEXT_CHARS],
        "preview_chars": min(len(redacted), _MAX_FEEDBACK_INDEX_TEXT_CHARS),
        "truncated": len(redacted) > _MAX_FEEDBACK_INDEX_TEXT_CHARS,
        "redacted": redacted != value,
    }


def _feedback_index_retention_summary(feedback: Mapping) -> dict:
    summary = {}
    for field in ("feedback_retention", "raw_response_retention"):
        retention = feedback.get(field)
        if isinstance(retention, Mapping):
            summary[field] = _feedback_index_retention_record(retention)
    return summary


def _feedback_index_retention_record(retention: Mapping) -> dict:
    record: dict[str, object] = {}
    for field in (
        "policy",
        "retention_mode",
        "sha256",
        "chars",
        "stored_chars",
        "max_chars",
        "redacted",
        "truncated",
    ):
        value = retention.get(field)
        if isinstance(value, (str, bool, int)) and not isinstance(value, bool):
            record[field] = value
        elif isinstance(value, bool):
            record[field] = value
    return record


def _feedback_index_sort_key(record: dict) -> tuple:
    normalized_score = record.get("normalized_score")
    score = record.get("score")
    weighted_delta = record.get("weighted_delta")
    selection_score = record.get("selection_score")
    fitness = record.get("fitness")
    program_id = record.get("program_id")
    return (
        -(float(normalized_score) if _is_finite_real(normalized_score) else float("-inf")),
        -(float(score) if _is_finite_real(score) else float("-inf")),
        -(float(weighted_delta) if _is_finite_real(weighted_delta) else float("-inf")),
        -(float(selection_score) if _is_finite_real(selection_score) else float("-inf")),
        -(float(fitness) if _is_finite_real(fitness) else float("-inf")),
        str(program_id) if isinstance(program_id, str) else "",
    )


def _resurfacing_index_snapshot(
    programs: list[Program],
    metric_order: list[str],
    *,
    limit: int,
) -> dict:
    valid_programs = [
        program for program in programs if program.evaluation.get("is_valid") is True
    ]
    by_id = {program.id: program for program in valid_programs}
    records: dict[str, dict] = {}
    source_counts: dict[str, int] = {}

    def add_source(
        source: str,
        source_key: str,
        rank: int,
        source_record: Mapping,
        contribution_weight: float,
    ) -> None:
        program_id = source_record.get("program_id")
        if not isinstance(program_id, str) or program_id not in by_id:
            return
        source_counts[source] = source_counts.get(source, 0) + 1
        record = records.setdefault(
            program_id,
            _resurfacing_program_record(by_id[program_id]),
        )
        contribution = contribution_weight / float(rank + 1)
        record["resurfacing_score"] = float(record["resurfacing_score"]) + contribution
        record["source_count"] = int(record["source_count"]) + 1
        source_entry: dict[str, object] = {
            "source": source,
            "source_key": source_key,
            "rank": rank,
            "contribution": contribution,
        }
        for field in (
            "metric",
            "descriptor",
            "feedback_name",
            "normalized_metric",
            "descriptor_value",
            "normalized_score",
            "score",
            "weighted_delta",
        ):
            value = source_record.get(field)
            if isinstance(value, str) and value:
                source_entry[field] = value
            elif _is_finite_real(value):
                source_entry[field] = float(value)
        record["sources"].append(source_entry)

    score = _score_index_snapshot(programs, limit=limit)
    for rank, record in enumerate(score["programs"]):
        add_source("score", "selection_score", rank, record, 1.0)

    frontier = _objective_frontier_snapshot(
        programs,
        metric_order,
        limit=limit,
    )
    for rank, record in enumerate(frontier["programs"]):
        add_source("frontier", "declared_objective_vector", rank, record, 0.9)

    metric_archives = _objective_metric_archives_snapshot(
        programs,
        metric_order,
        limit=limit,
    )
    for archive in metric_archives["archives"]:
        metric = archive["metric"]
        for rank, record in enumerate(archive["programs"]):
            add_source("metric", str(metric), rank, record, 0.9)

    lineage = _lineage_index_snapshot(
        programs,
        root_limit=limit,
        programs_per_root_limit=1,
    )
    for rank, lineage_record in enumerate(lineage["lineages"]):
        add_source(
            "lineage",
            str(lineage_record["lineage_root_id"]),
            rank,
            lineage_record["best_program"],
            0.7,
        )

    descriptor = _descriptor_index_snapshot(programs, limit=limit)
    for descriptor_record in descriptor["descriptors"]:
        descriptor_name = descriptor_record["descriptor"]
        for rank, record in enumerate(descriptor_record["programs"]):
            add_source("descriptor", str(descriptor_name), rank, record, 0.5)

    feedback = _feedback_index_snapshot(programs, limit=limit)
    for grader in feedback["graders"]:
        grader_name = grader["feedback_name"]
        for rank, record in enumerate(grader["programs"]):
            if record.get("evaluation_is_valid") is True:
                add_source("feedback", str(grader_name), rank, record, 0.6)

    hypothesis = _hypothesis_index_snapshot(programs, limit=limit)
    for rank, record in enumerate(hypothesis["programs"]):
        add_source("hypothesis", "proposal_hypothesis", rank, record, 0.55)

    artifact = _artifact_index_snapshot(
        programs,
        program_limit=limit,
        files_per_program_limit=_MAX_ARTIFACT_INDEX_FILES_PER_PROGRAM,
        skipped_per_program_limit=_MAX_ARTIFACT_INDEX_SKIPPED_PER_PROGRAM,
    )
    for rank, record in enumerate(artifact["programs"]):
        if record.get("evaluation_is_valid") is True:
            add_source("artifact", "evaluator_artifacts", rank, record, 0.45)

    ranked = sorted(records.values(), key=_resurfacing_index_sort_key)
    retained = ranked[:limit]
    return {
        "schema": RESURFACING_INDEX_SCHEMA,
        "policy": RESURFACING_INDEX_POLICY,
        "metric_order": [
            name for name in metric_order if isinstance(name, str) and name
        ],
        "program_count_considered": len(valid_programs),
        "candidate_count": len(ranked),
        "retained_count": len(retained),
        "retention_limit": limit,
        "source_counts": dict(sorted(source_counts.items())),
        "programs": retained,
        "limitations": list(_RESURFACING_INDEX_LIMITATIONS),
    }


def validate_resurfacing_index_summary(index: object) -> dict:
    """Validate a runtime.history.resurfacing_index manifest record."""
    issues: list[dict] = []
    if not isinstance(index, dict):
        return {
            "schema": RESURFACING_INDEX_SCHEMA,
            "ok": False,
            "resurfacing_ready": False,
            "durable_database_ready": False,
            "program_count": 0,
            "issues": [
                {
                    "code": "invalid_shape",
                    "message": "resurfacing index must be an object",
                }
            ],
        }

    _resurfacing_issue_if(
        issues,
        index.get("schema") != RESURFACING_INDEX_SCHEMA,
        "invalid_schema",
        "resurfacing index schema is unsupported",
    )
    _resurfacing_issue_if(
        issues,
        index.get("policy") != RESURFACING_INDEX_POLICY,
        "invalid_policy",
        "resurfacing index policy is unsupported",
    )
    metric_order = _validate_resurfacing_metric_order(
        index.get("metric_order", []),
        issues,
    )
    programs = index.get("programs")
    if not isinstance(programs, list):
        programs = []
        issues.append(
            {
                "code": "invalid_programs",
                "message": "resurfacing index programs must be a list",
            }
        )
    source_counts = index.get("source_counts")
    if not isinstance(source_counts, dict):
        source_counts = {}
        issues.append(
            {
                "code": "invalid_source_counts",
                "message": "resurfacing index source_counts must be an object",
            }
        )
    program_count_considered = _resurfacing_non_negative_int(
        index.get("program_count_considered"),
        "program_count_considered",
        issues,
    )
    candidate_count = _resurfacing_non_negative_int(
        index.get("candidate_count"),
        "candidate_count",
        issues,
    )
    retained_count = _resurfacing_non_negative_int(
        index.get("retained_count"),
        "retained_count",
        issues,
    )
    retention_limit = _resurfacing_non_negative_int(
        index.get("retention_limit"),
        "retention_limit",
        issues,
    )
    _validate_resurfacing_limitations(index.get("limitations"), issues)
    _validate_resurfacing_source_counts(source_counts, issues)

    records: list[dict] = []
    retained_source_counts: dict[str, int] = {}
    seen_ids: set[str] = set()
    for position, record in enumerate(programs):
        if not isinstance(record, dict):
            issues.append(
                {
                    "code": "invalid_program_record",
                    "message": f"programs[{position}] must be an object",
                }
            )
            continue
        normalized = _validate_resurfacing_program_record(
            record,
            position,
            metric_order,
            issues,
        )
        if normalized is None:
            continue
        program_id = normalized["program_id"]
        if program_id in seen_ids:
            issues.append(
                {
                    "code": "duplicate_program_id",
                    "message": "resurfacing index programs must be unique",
                }
            )
        seen_ids.add(program_id)
        for source in normalized["source_names"]:
            retained_source_counts[source] = retained_source_counts.get(source, 0) + 1
        records.append(normalized["record"])

    if retained_count is not None and retained_count != len(programs):
        issues.append(
            {
                "code": "retained_count_mismatch",
                "message": "retained_count must equal programs length",
            }
        )
    if candidate_count is not None and candidate_count < len(programs):
        issues.append(
            {
                "code": "candidate_count_mismatch",
                "message": "candidate_count cannot be smaller than programs length",
            }
        )
    if retention_limit is not None and len(programs) > retention_limit:
        issues.append(
            {
                "code": "retention_limit_exceeded",
                "message": "retained programs exceed retention_limit",
            }
        )
    if (
        program_count_considered is not None
        and candidate_count is not None
        and candidate_count > program_count_considered
    ):
        issues.append(
            {
                "code": "candidate_count_exceeds_program_count",
                "message": "candidate_count cannot exceed program_count_considered",
            }
        )
    for source, retained_count_for_source in retained_source_counts.items():
        count = source_counts.get(source)
        if (
            not isinstance(count, int)
            or isinstance(count, bool)
            or count < retained_count_for_source
        ):
            issues.append(
                {
                    "code": "source_count_below_retained_sources",
                    "message": (
                        "source_counts must cover retained program source entries"
                    ),
                }
            )
            break
    if records and records != sorted(records, key=_resurfacing_index_sort_key):
        issues.append(
            {
                "code": "programs_not_ranked",
                "message": "programs must be sorted by resurfacing ranking policy",
            }
        )
    return {
        "schema": RESURFACING_INDEX_SCHEMA,
        "ok": not issues,
        "resurfacing_ready": not issues,
        "durable_database_ready": False,
        "program_count": len(programs),
        "metric_order": metric_order,
        "issues": issues,
    }


def _validate_resurfacing_target_metric(
    target_metric: object,
    metric_order: list[str],
) -> str | None:
    if target_metric is None:
        return None
    if not isinstance(target_metric, str) or not target_metric:
        raise ValueError("database resurfacing target_metric must be a declared metric")
    try:
        validate_program_metrics({target_metric: 0.0})
    except ValueError as exc:
        raise ValueError(
            "database resurfacing target_metric must be a declared metric"
        ) from exc
    if target_metric not in metric_order:
        raise ValueError("database resurfacing target_metric must be a declared metric")
    return target_metric


def _validate_database_query_program_id(value: object, label: str) -> str:
    try:
        validate_program_identity(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be a manifest-safe identifier") from exc
    assert isinstance(value, str)
    return value


def _validate_database_query_key(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be non-empty text")
    if len(value) > 128:
        raise ValueError(f"{label} must be at most 128 characters")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError(f"{label} must be display-safe text")
    if redact_sensitive_text(value) != value:
        raise ValueError(f"{label} must not contain sensitive-looking text")
    return value


def _ranked_program_snapshots_from_index_records(
    programs_by_id: Mapping[str, Program],
    records: object,
    *,
    k: int,
    exclude_ids: set[str],
) -> list[Program]:
    if not isinstance(records, list):
        return []
    surfaced: list[Program] = []
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, Mapping):
            continue
        program_id = record.get("program_id")
        if (
            not isinstance(program_id, str)
            or program_id in exclude_ids
            or program_id in seen
        ):
            continue
        program = programs_by_id.get(program_id)
        if program is None:
            continue
        seen.add(program_id)
        surfaced.append(_program_snapshot(program))
        if len(surfaced) >= k:
            break
    return surfaced


def _resurfacing_program_record(program: Program) -> dict:
    record: dict[str, object] = {
        "program_id": program.id,
        "lineage_root_id": _program_lineage_root_id(program),
        "generation": program.generation,
        "selection_score": _history_safe_selection_score(program),
        "fitness": float(program.fitness),
        "source_count": 0,
        "resurfacing_score": 0.0,
        "sources": [],
    }
    admission = _history_safe_archive_admission_summary(program)
    if admission:
        record["archive_admission"] = admission
    objective_vector = _history_safe_objective_vector(program)
    if objective_vector is not None:
        record["objective_vector"] = objective_vector
    else:
        normalized_metrics = _history_safe_normalized_metrics(program)
        if normalized_metrics:
            record["normalized_metrics"] = normalized_metrics
    return record


def _resurfacing_index_sort_key(record: dict) -> tuple:
    return (
        -int(record.get("source_count", 0)),
        -(float(record.get("resurfacing_score", 0.0))),
        -(
            float(record["selection_score"])
            if _is_finite_real(record.get("selection_score"))
            else float("-inf")
        ),
        -(
            float(record["fitness"])
            if _is_finite_real(record.get("fitness"))
            else float("-inf")
        ),
        str(record.get("program_id", "")),
    )


def _resurfacing_issue_if(
    issues: list[dict],
    condition: bool,
    code: str,
    message: str,
) -> None:
    if condition:
        issues.append({"code": code, "message": message})


def _resurfacing_non_negative_int(
    value: object,
    field: str,
    issues: list[dict],
) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        issues.append(
            {
                "code": f"invalid_{field}",
                "message": f"{field} must be a non-negative integer",
            }
        )
        return None
    return value


def _validate_resurfacing_metric_order(
    value: object,
    issues: list[dict],
) -> list[str]:
    if not isinstance(value, list):
        issues.append(
            {
                "code": "invalid_metric_order",
                "message": "metric_order must be a list",
            }
        )
        return []
    result: list[str] = []
    seen: set[str] = set()
    for metric in value:
        if not isinstance(metric, str) or not metric:
            issues.append(
                {
                    "code": "invalid_metric_order",
                    "message": "metric_order entries must be non-empty strings",
                }
            )
            continue
        try:
            validate_program_metrics({metric: 0.0})
        except ValueError as exc:
            issues.append(
                {
                    "code": "invalid_metric_order",
                    "message": str(exc),
                }
            )
            continue
        if metric in seen:
            issues.append(
                {
                    "code": "duplicate_metric_order",
                    "message": "metric_order must not contain duplicates",
                }
            )
            continue
        seen.add(metric)
        result.append(metric)
    return result


def _validate_resurfacing_limitations(value: object, issues: list[dict]) -> None:
    if not isinstance(value, list):
        issues.append(
            {
                "code": "invalid_limitations",
                "message": "limitations must be a list",
            }
        )
        return
    missing = [
        item for item in _RESURFACING_INDEX_LIMITATIONS if item not in value
    ]
    if missing:
        issues.append(
            {
                "code": "missing_limitations",
                "message": f"resurfacing index missing limitations: {missing}",
            }
        )


def _validate_resurfacing_source_counts(
    value: Mapping,
    issues: list[dict],
) -> None:
    for source, count in value.items():
        if source not in _RESURFACING_INDEX_SOURCES:
            issues.append(
                {
                    "code": "invalid_source_count_key",
                    "message": "source_counts contains unsupported source",
                }
            )
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            issues.append(
                {
                    "code": "invalid_source_count_value",
                    "message": "source_counts values must be non-negative integers",
                }
            )


def _validate_resurfacing_program_record(
    record: dict,
    position: int,
    metric_order: list[str],
    issues: list[dict],
) -> dict | None:
    required = {
        "program_id",
        "lineage_root_id",
        "generation",
        "fitness",
        "source_count",
        "resurfacing_score",
        "sources",
    }
    missing = required - set(record)
    if missing:
        issues.append(
            {
                "code": "missing_program_fields",
                "message": f"programs[{position}] missing fields: {sorted(missing)}",
            }
        )
        return None
    program_id = record.get("program_id")
    try:
        validate_program_identity(program_id)
    except ValueError as exc:
        issues.append(
            {
                "code": "invalid_program_id",
                "message": str(exc),
            }
        )
        return None
    lineage_root_id = record.get("lineage_root_id")
    try:
        validate_program_identity(lineage_root_id)
    except ValueError as exc:
        issues.append(
            {
                "code": "invalid_lineage_root_id",
                "message": str(exc),
            }
        )
    generation = record.get("generation")
    if isinstance(generation, bool) or not isinstance(generation, int) or generation < 0:
        issues.append(
            {
                "code": "invalid_program_generation",
                "message": "program generation must be a non-negative integer",
            }
        )
    fitness = record.get("fitness")
    if not _is_finite_real(fitness):
        issues.append(
            {
                "code": "invalid_program_fitness",
                "message": "program fitness must be finite",
            }
        )
    selection_score = record.get("selection_score")
    if selection_score is not None and not _is_finite_real(selection_score):
        issues.append(
            {
                "code": "invalid_program_selection_score",
                "message": "program selection_score must be finite or null",
            }
        )
    source_count = record.get("source_count")
    if isinstance(source_count, bool) or not isinstance(source_count, int) or source_count < 0:
        issues.append(
            {
                "code": "invalid_program_source_count",
                "message": "program source_count must be a non-negative integer",
            }
        )
        source_count = None
    resurfacing_score = record.get("resurfacing_score")
    if not _is_finite_real(resurfacing_score) or float(resurfacing_score) < 0.0:
        issues.append(
            {
                "code": "invalid_resurfacing_score",
                "message": "program resurfacing_score must be finite and non-negative",
            }
        )
        resurfacing_score = None
    sources = record.get("sources")
    if not isinstance(sources, list):
        issues.append(
            {
                "code": "invalid_program_sources",
                "message": "program sources must be a list",
            }
        )
        sources = []
    source_names = []
    contribution_sum = 0.0
    for source_position, source in enumerate(sources):
        normalized = _validate_resurfacing_source_entry(
            source,
            position,
            source_position,
            issues,
        )
        if normalized is None:
            continue
        source_names.append(normalized["source"])
        contribution_sum += normalized["contribution"]
    if source_count is not None and source_count != len(sources):
        issues.append(
            {
                "code": "program_source_count_mismatch",
                "message": "program source_count must equal sources length",
            }
        )
    if resurfacing_score is not None and not math.isclose(
        float(resurfacing_score),
        contribution_sum,
        rel_tol=1e-12,
        abs_tol=1e-12,
    ):
        issues.append(
            {
                "code": "resurfacing_score_mismatch",
                "message": "resurfacing_score must equal summed source contributions",
            }
        )
    _validate_resurfacing_optional_objective_fields(
        record,
        metric_order,
        position,
        issues,
    )
    return {"record": record, "program_id": str(program_id), "source_names": source_names}


def _validate_resurfacing_source_entry(
    source: object,
    program_position: int,
    source_position: int,
    issues: list[dict],
) -> dict | None:
    if not isinstance(source, dict):
        issues.append(
            {
                "code": "invalid_source_entry",
                "message": (
                    f"programs[{program_position}].sources[{source_position}] "
                    "must be an object"
                ),
            }
        )
        return None
    source_name = source.get("source")
    if source_name not in _RESURFACING_INDEX_SOURCES:
        issues.append(
            {
                "code": "invalid_source",
                "message": "resurfacing source is unsupported",
            }
        )
    source_key = source.get("source_key")
    if not isinstance(source_key, str) or not source_key:
        issues.append(
            {
                "code": "invalid_source_key",
                "message": "resurfacing source_key must be a non-empty string",
            }
        )
    rank = source.get("rank")
    if isinstance(rank, bool) or not isinstance(rank, int) or rank < 0:
        issues.append(
            {
                "code": "invalid_source_rank",
                "message": "resurfacing source rank must be a non-negative integer",
            }
        )
    contribution = source.get("contribution")
    if not _is_finite_real(contribution) or float(contribution) <= 0.0:
        issues.append(
            {
                "code": "invalid_source_contribution",
                "message": "resurfacing source contribution must be positive and finite",
            }
        )
        return None
    return {"source": str(source_name), "contribution": float(contribution)}


def _validate_resurfacing_optional_objective_fields(
    record: dict,
    metric_order: list[str],
    position: int,
    issues: list[dict],
) -> None:
    if "objective_vector" in record:
        objective = record["objective_vector"]
        if not isinstance(objective, dict):
            issues.append(
                {
                    "code": "invalid_objective_vector",
                    "message": f"programs[{position}].objective_vector must be an object",
                }
            )
            return
        normalized = objective.get("normalized_metrics")
    else:
        normalized = record.get("normalized_metrics")
    if normalized is None:
        return
    if not isinstance(normalized, dict):
        issues.append(
            {
                "code": "invalid_normalized_metrics",
                "message": f"programs[{position}] normalized metrics must be an object",
            }
        )
        return
    for metric, value in normalized.items():
        if metric_order and metric not in metric_order:
            issues.append(
                {
                    "code": "normalized_metric_not_in_metric_order",
                    "message": "normalized metric must be listed in metric_order",
                }
            )
        if not _is_finite_real(value) or not 0.0 <= float(value) <= 1.0:
            issues.append(
                {
                    "code": "invalid_normalized_metric_value",
                    "message": "normalized metric values must be finite in [0, 1]",
                }
            )


def _failure_index_snapshot(
    records: list[dict],
    *,
    fingerprint_limit: int,
    records_per_fingerprint_limit: int,
) -> dict:
    by_fingerprint: dict[str, list[dict]] = {}
    for record in records:
        indexed = _failure_index_record(record)
        if indexed is None:
            continue
        by_fingerprint.setdefault(indexed["fingerprint_sha256"], []).append(indexed)

    fingerprints: list[dict] = []
    for fingerprint_sha256, indexed_records in by_fingerprint.items():
        indexed_records.sort(key=_failure_index_record_sort_key)
        retained = indexed_records[:records_per_fingerprint_limit]
        latest = retained[0]
        fingerprints.append(
            {
                "fingerprint_sha256": fingerprint_sha256,
                "record_type": latest["record_type"],
                "parent_id": latest.get("parent_id"),
                "occurrence_count": len(indexed_records),
                "max_repetition_count": max(
                    record["repetition_count"] for record in indexed_records
                ),
                "retained_count": len(retained),
                "record_retention_limit": records_per_fingerprint_limit,
                "changed_files": latest.get("changed_files", []),
                "latest_record": latest,
                "records": retained,
            }
        )
    fingerprints.sort(key=_failure_index_fingerprint_sort_key)
    retained_fingerprints = fingerprints[:fingerprint_limit]
    return {
        "schema": "libreevolve.failure_index.v1",
        "policy": "failure_records_grouped_by_fingerprint_repetition_and_recency",
        "failure_record_count": len(records),
        "fingerprint_count": len(fingerprints),
        "retained_fingerprint_count": len(retained_fingerprints),
        "fingerprint_retention_limit": fingerprint_limit,
        "record_retention_limit": records_per_fingerprint_limit,
        "fingerprints": retained_fingerprints,
        "limitations": [
            "runtime_manifest_failure_index_not_cross_run_database_table",
            "groups_by_failure_fingerprint_without_semantic_similarity",
            "retains_bounded_records_per_fingerprint",
            "rebuilt_from_current_runtime_failure_records",
        ],
    }


def _failure_index_record(record: Mapping) -> dict | None:
    fingerprint = record.get("failure_fingerprint")
    fingerprint_sha256 = None
    fingerprint_record_type = None
    if isinstance(fingerprint, Mapping):
        raw_sha = fingerprint.get("sha256")
        if _is_sha256_hex(raw_sha):
            fingerprint_sha256 = str(raw_sha)
        if isinstance(fingerprint.get("record_type"), str):
            fingerprint_record_type = fingerprint["record_type"]
    if fingerprint_sha256 is None:
        raw_sha = record.get("mutation_sha256")
        if _is_sha256_hex(raw_sha):
            fingerprint_sha256 = str(raw_sha)
    if fingerprint_sha256 is None:
        return None
    program_id = record.get("program_id")
    try:
        validate_program_identity(program_id)
    except ValueError:
        return None
    indexed: dict[str, object] = {
        "program_id": program_id,
        "fingerprint_sha256": fingerprint_sha256,
        "record_type": (
            fingerprint_record_type
            if isinstance(fingerprint_record_type, str) and fingerprint_record_type
            else record.get("record_type", "generated")
        ),
        "generation": _failure_index_non_negative_int(record.get("generation")),
        "repetition_count": _failure_index_positive_int(
            record.get("repetition_count")
        ),
        "mutation_sha256": record.get("mutation_sha256"),
        "mutation_payload_type": _failure_optional_text(
            record.get("mutation_payload_type"),
            80,
        ),
        "mutation_payload_text": record.get("mutation_payload_text"),
    }
    parent_id = record.get("parent_id")
    if isinstance(parent_id, str) and parent_id:
        indexed["parent_id"] = parent_id
    score = record.get("score")
    if _is_finite_real(score):
        indexed["score"] = float(score)
    is_valid = record.get("is_valid")
    if isinstance(is_valid, bool):
        indexed["is_valid"] = is_valid
    reason = _failure_optional_json_text(
        record.get("admission_reason")
        or record.get("diff_error")
        or record.get("error"),
        300,
    )
    if reason:
        indexed["reason"] = reason
    for field in ("error", "diff_error", "admission_reason"):
        value = _failure_optional_json_text(record.get(field), 300)
        if value:
            indexed[field] = value
    changed_files = record.get("changed_files")
    if isinstance(changed_files, list):
        indexed["changed_files"] = [
            path
            for path in (
                _failure_optional_text(path, 120) for path in changed_files
            )
            if path
        ][:8]
    file_deltas = record.get("file_deltas")
    if isinstance(file_deltas, list):
        indexed["file_deltas"] = _failure_index_file_deltas(file_deltas)
    evaluation = record.get("evaluation")
    if isinstance(evaluation, Mapping):
        summary = _failure_index_evaluation_summary(evaluation)
        if summary:
            indexed["evaluation"] = summary
    return indexed


def _failure_index_file_deltas(file_deltas: list) -> list[dict]:
    restored = []
    for delta in file_deltas[:8]:
        if not isinstance(delta, Mapping):
            continue
        path = _failure_optional_text(delta.get("path"), 120)
        change = delta.get("change")
        if path and change in {"added", "deleted", "modified", "seed"}:
            restored.append({"path": path, "change": change})
    return restored


def _failure_index_evaluation_summary(evaluation: Mapping) -> dict:
    summary: dict[str, object] = {}
    for field in ("error", "stdout", "stderr"):
        value = _failure_optional_text(evaluation.get(field), 200)
        if value:
            summary[field] = value
    stages = evaluation.get("stages")
    if isinstance(stages, list):
        stage_errors = []
        for stage in stages[:3]:
            if isinstance(stage, Mapping):
                error = _failure_optional_text(stage.get("error"), 200)
                if error:
                    stage_errors.append(error)
        if stage_errors:
            summary["stage_errors"] = stage_errors
    return summary


def _failure_index_non_negative_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return 0
    return value


def _failure_index_positive_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        return 1
    return value


def _failure_index_record_sort_key(record: dict) -> tuple:
    return (
        -int(record.get("repetition_count", 1)),
        -int(record.get("generation", 0)),
        str(record.get("program_id", "")),
    )


def _failure_index_fingerprint_sort_key(record: dict) -> tuple:
    return (
        -int(record.get("max_repetition_count", 1)),
        -int(record.get("occurrence_count", 0)),
        str(record.get("fingerprint_sha256", "")),
    )


def _hypothesis_index_snapshot(
    programs: list[Program],
    *,
    limit: int,
) -> dict:
    candidates = [
        record
        for program in programs
        if (record := _hypothesis_index_program(program)) is not None
    ]
    candidates.sort(key=_hypothesis_index_sort_key)
    retained = candidates[:limit]
    return {
        "schema": "libreevolve.hypothesis_index.v1",
        "policy": "top_valid_programs_with_proposal_hypothesis_metadata",
        "program_count_considered": len(candidates),
        "retained_count": len(retained),
        "retention_limit": limit,
        "programs": retained,
        "limitations": [
            "runtime_manifest_hypothesis_index_not_cross_run_database_table",
            "bounded_redacted_text_summaries_not_full_text_search",
            "requires_captured_proposal_metadata",
            "rebuilt_from_current_runtime_history_records",
        ],
    }


def _hypothesis_index_program(program: Program) -> dict | None:
    if program.evaluation.get("is_valid") is not True:
        return None
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    proposal = metadata.get("proposal")
    if not isinstance(proposal, Mapping):
        return None
    text_fields = {}
    for field in ("hypothesis", "idea", "rationale"):
        value = proposal.get(field)
        if isinstance(value, str) and value:
            text_fields[field] = _hypothesis_index_text_summary(value)
    if not text_fields:
        return None
    record: dict[str, object] = {
        "program_id": program.id,
        "lineage_root_id": _program_lineage_root_id(program),
        "generation": program.generation,
        "selection_score": _history_safe_selection_score(program),
        "fitness": float(program.fitness),
        "proposal": text_fields,
    }
    admission = _history_safe_archive_admission_summary(program)
    if admission:
        record["archive_admission"] = admission
    objective_vector = _history_safe_objective_vector(program)
    if objective_vector is not None:
        record["objective_vector"] = objective_vector
    else:
        normalized_metrics = _history_safe_normalized_metrics(program)
        if normalized_metrics:
            record["normalized_metrics"] = normalized_metrics
    return record


def _hypothesis_index_text_summary(value: str) -> dict:
    redacted = redact_sensitive_text(value)
    return {
        "policy": "bounded_redacted_proposal_text_v1",
        "chars": len(value),
        "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "preview": redacted[:_MAX_HYPOTHESIS_INDEX_TEXT_CHARS],
        "preview_chars": min(len(redacted), _MAX_HYPOTHESIS_INDEX_TEXT_CHARS),
        "truncated": len(redacted) > _MAX_HYPOTHESIS_INDEX_TEXT_CHARS,
        "redacted": redacted != value,
    }


def _hypothesis_index_sort_key(record: dict) -> tuple:
    selection_score = record.get("selection_score")
    fitness = record.get("fitness")
    generation = record.get("generation")
    program_id = record.get("program_id")
    return (
        -(float(selection_score) if _is_finite_real(selection_score) else float("-inf")),
        -(float(fitness) if _is_finite_real(fitness) else float("-inf")),
        -(int(generation) if isinstance(generation, int) and not isinstance(generation, bool) else -1),
        str(program_id) if isinstance(program_id, str) else "",
    )


def _artifact_index_snapshot(
    programs: list[Program],
    *,
    program_limit: int,
    files_per_program_limit: int,
    skipped_per_program_limit: int,
) -> dict:
    candidates = [
        record
        for program in programs
        if (
            record := _artifact_index_program(
                program,
                files_per_program_limit=files_per_program_limit,
                skipped_per_program_limit=skipped_per_program_limit,
            )
        )
        is not None
    ]
    candidates.sort(key=_artifact_index_sort_key)
    retained = candidates[:program_limit]
    return {
        "schema": "libreevolve.artifact_index.v1",
        "policy": "top_programs_with_evaluator_artifact_evidence",
        "program_count_considered": len(candidates),
        "retained_count": len(retained),
        "program_retention_limit": program_limit,
        "file_retention_limit": files_per_program_limit,
        "skipped_retention_limit": skipped_per_program_limit,
        "programs": retained,
        "limitations": [
            "runtime_manifest_artifact_index_not_cross_run_database_table",
            "bounded_artifact_metadata_not_full_artifact_content_search",
            "uses_evaluation_metadata_artifacts_only",
            "rebuilt_from_current_runtime_history_records",
        ],
    }


def _artifact_index_program(
    program: Program,
    *,
    files_per_program_limit: int,
    skipped_per_program_limit: int,
) -> dict | None:
    evaluation = program.evaluation if isinstance(program.evaluation, dict) else {}
    metadata = evaluation.get("metadata")
    if not isinstance(metadata, Mapping):
        return None
    artifacts = metadata.get("artifacts")
    if not isinstance(artifacts, Mapping):
        return None
    raw_files = artifacts.get("files")
    if not isinstance(raw_files, list) or not raw_files:
        return None
    files = [
        record
        for item in raw_files[:files_per_program_limit]
        if (record := _artifact_index_file_record(item)) is not None
    ]
    if not files:
        return None
    raw_skipped = artifacts.get("skipped")
    skipped = []
    if isinstance(raw_skipped, list):
        skipped = [
            record
            for item in raw_skipped[:skipped_per_program_limit]
            if (record := _artifact_index_skipped_record(item)) is not None
        ]
    record: dict[str, object] = {
        "program_id": program.id,
        "lineage_root_id": _program_lineage_root_id(program),
        "generation": program.generation,
        "evaluation_is_valid": evaluation.get("is_valid") is True,
        "selection_score": _history_safe_selection_score(program),
        "fitness": float(program.fitness),
        "artifact_count": len(raw_files),
        "retained_file_count": len(files),
        "file_retention_limit": files_per_program_limit,
        "files": files,
    }
    collection_id = artifacts.get("collection_id")
    if isinstance(collection_id, str) and collection_id:
        record["collection_id"] = _artifact_index_string(collection_id)
    artifact_dir_name = artifacts.get("artifact_dir_name")
    if isinstance(artifact_dir_name, str) and artifact_dir_name:
        record["artifact_dir_name"] = _artifact_index_string(artifact_dir_name)
    total_bytes = artifacts.get("total_bytes")
    if _is_non_negative_int(total_bytes):
        record["total_bytes"] = int(total_bytes)
    skipped_count = len(raw_skipped) if isinstance(raw_skipped, list) else 0
    if skipped_count:
        record["skipped_count"] = skipped_count
        record["retained_skipped_count"] = len(skipped)
        record["skipped_retention_limit"] = skipped_per_program_limit
        record["skipped"] = skipped
    stage = _artifact_index_stage_record(artifacts.get("stage"))
    if stage:
        record["stage"] = stage
    admission = _history_safe_archive_admission_summary(program)
    if admission:
        record["archive_admission"] = admission
    objective_vector = _history_safe_objective_vector(program)
    if objective_vector is not None:
        record["objective_vector"] = objective_vector
    else:
        normalized_metrics = _history_safe_normalized_metrics(program)
        if normalized_metrics:
            record["normalized_metrics"] = normalized_metrics
    return record


def _artifact_index_file_record(item: object) -> dict | None:
    if not isinstance(item, Mapping):
        return None
    record: dict[str, object] = {}
    for source, target in (
        ("path", "path"),
        ("artifact_path", "artifact_path"),
        ("artifact_path_root", "artifact_path_root"),
        ("artifact_relative_path", "artifact_relative_path"),
        ("redaction_status", "redaction_status"),
        ("content_excerpt_policy", "content_excerpt_policy"),
        ("content_excerpt_status", "content_excerpt_status"),
        ("stage_name", "stage_name"),
    ):
        value = item.get(source)
        if isinstance(value, str) and value:
            record[target] = _artifact_index_string(value)
    for source, target in (
        ("bytes", "bytes"),
        ("source_bytes", "source_bytes"),
        ("sample_index", "sample_index"),
        ("attempt", "attempt"),
        ("content_excerpt_chars", "content_excerpt_chars"),
        ("content_excerpt_max_chars", "content_excerpt_max_chars"),
    ):
        value = item.get(source)
        if _is_non_negative_int(value):
            record[target] = int(value)
    sha256 = item.get("sha256")
    if _is_sha256_hex(sha256):
        record["sha256"] = sha256
    for field in ("redacted", "content_excerpt_truncated"):
        value = item.get(field)
        if isinstance(value, bool):
            record[field] = value
    excerpt = item.get("content_excerpt")
    if isinstance(excerpt, str) and excerpt:
        record["content_excerpt"] = _artifact_index_text_summary(excerpt)
    return record or None


def _artifact_index_skipped_record(item: object) -> dict | None:
    if not isinstance(item, Mapping):
        return None
    record: dict[str, object] = {}
    for field in ("path", "reason", "message"):
        value = item.get(field)
        if isinstance(value, str) and value:
            record[field] = _artifact_index_string(value)
    for field in ("bytes", "source_bytes"):
        value = item.get(field)
        if _is_non_negative_int(value):
            record[field] = int(value)
    return record or None


def _artifact_index_stage_record(value: object) -> dict:
    if not isinstance(value, Mapping):
        return {}
    record: dict[str, object] = {}
    name = value.get("name")
    if isinstance(name, str) and name:
        record["name"] = _artifact_index_string(name)
    for field in ("sample_index", "attempt"):
        item = value.get(field)
        if _is_non_negative_int(item):
            record[field] = int(item)
    return record


def _artifact_index_text_summary(value: str) -> dict:
    redacted = redact_sensitive_text(value)
    preview = redacted[:_MAX_ARTIFACT_INDEX_TEXT_CHARS]
    return {
        "policy": "bounded_redacted_artifact_excerpt_v1",
        "chars": len(value),
        "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "preview": preview,
        "preview_chars": len(preview),
        "truncated": len(redacted) > _MAX_ARTIFACT_INDEX_TEXT_CHARS,
        "redacted": redacted != value,
    }


def _artifact_index_string(value: str) -> str:
    return redact_sensitive_text(value)[:_MAX_ARTIFACT_INDEX_TEXT_CHARS]


def _artifact_index_sort_key(record: dict) -> tuple:
    artifact_count = record.get("artifact_count")
    selection_score = record.get("selection_score")
    fitness = record.get("fitness")
    generation = record.get("generation")
    program_id = record.get("program_id")
    return (
        -(int(artifact_count) if _is_non_negative_int(artifact_count) else 0),
        -(float(selection_score) if _is_finite_real(selection_score) else float("-inf")),
        -(float(fitness) if _is_finite_real(fitness) else float("-inf")),
        -(int(generation) if isinstance(generation, int) and not isinstance(generation, bool) else -1),
        str(program_id) if isinstance(program_id, str) else "",
    )


def _is_non_negative_int(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, int) and value >= 0


def _program_lineage_root_id(program: Program) -> str:
    if program.lineage:
        return program.lineage[0]
    return program.id


def _lineage_index_sort_key(record: dict) -> tuple:
    selection_score = record.get("selection_score")
    fitness = record.get("fitness")
    generation = record.get("generation")
    program_id = record.get("program_id")
    return (
        -(float(selection_score) if _is_finite_real(selection_score) else float("-inf")),
        -(float(fitness) if _is_finite_real(fitness) else float("-inf")),
        -(int(generation) if isinstance(generation, int) and not isinstance(generation, bool) else -1),
        str(program_id) if isinstance(program_id, str) else "",
    )


def _history_safe_normalized_metrics(program: Program) -> dict[str, float]:
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    raw = metadata.get("normalized_metrics")
    if not isinstance(raw, dict):
        return {}
    metrics: dict[str, float] = {}
    for name, value in sorted(raw.items()):
        if isinstance(name, str) and _is_finite_real(value):
            numeric = float(value)
            if 0.0 <= numeric <= 1.0:
                metrics[name] = numeric
    return metrics


def _is_finite_real(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
    )


def _fitness_rejection_reason(value: object) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "invalid_fitness_type"
    return "non_finite_fitness"


def _program_history_record(
    program: Program, *, metadata: dict | None = None
) -> dict:
    record = {
        "id": program.id,
        "code": program.code,
        "fitness": program.fitness,
        "files": program.files,
        "primary_file": program.primary_file,
        "workspace_path_policy": _workspace_path_policy_record(program),
        "generation": program.generation,
        "parent_id": program.parent_id,
        "lineage": program.lineage,
        "metadata": validate_program_metadata(program.metadata if metadata is None else metadata),
        "metrics": program.metrics,
        "evaluation": program.evaluation,
    }
    if program.static_files:
        record["static_files"] = [dict(item) for item in program.static_files]
    return versioned_record(HISTORY_RECORD_SCHEMA, record)


def _program_snapshot(program: Program) -> Program:
    return Program(
        id=program.id,
        code=program.code,
        fitness=program.fitness,
        generation=program.generation,
        parent_id=program.parent_id,
        lineage=list(program.lineage),
        metadata=copy.deepcopy(validate_program_metadata(program.metadata)),
        metrics=validate_program_metrics(program.metrics),
        evaluation=copy.deepcopy(validate_program_evaluation(program.evaluation)),
        files=dict(program.files),
        primary_file=program.primary_file,
        allowed_reserved_paths=program.allowed_reserved_paths,
        static_files=program.static_files,
    )


def _archive_program_snapshots_by_id(
    value: Mapping[str, Program] | None,
) -> dict[str, Program] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError("archive_programs_by_id must be a mapping")
    restored: dict[str, Program] = {}
    for program_id, program in value.items():
        validate_program_identity(program_id)
        if not isinstance(program, Program):
            raise ValueError("archive_programs_by_id values must be Program instances")
        if program.id != program_id:
            raise ValueError("archive_programs_by_id keys must match Program ids")
        restored[program_id] = _program_snapshot(program)
    return restored


def _program_from_history_record(record: dict, *, line_label: str) -> Program:
    try:
        policy = record.get("workspace_path_policy", {})
        allowed_reserved_paths = ()
        if isinstance(policy, dict):
            allowed_reserved_paths = policy.get("allowed_reserved_paths", ())
        return Program(
            id=record["id"],
            code=record.get("code", ""),
            fitness=record["fitness"],
            generation=record.get("generation", 0),
            parent_id=record.get("parent_id"),
            lineage=list(record.get("lineage", [])),
            metadata=copy.deepcopy(record.get("metadata", {})),
            metrics=copy.deepcopy(record.get("metrics", {})),
            evaluation=copy.deepcopy(record.get("evaluation", {})),
            files=copy.deepcopy(record.get("files", {})),
            primary_file=record.get("primary_file", "main.py"),
            allowed_reserved_paths=frozenset(allowed_reserved_paths),
            static_files=copy.deepcopy(record.get("static_files", ())),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise HistoryRestoreError(
            f"Malformed history.jsonl record {line_label!r} cannot restore Program: {exc}"
        ) from exc


def _validate_archive_snapshot_program_references(
    archive_state: dict,
    programs_by_id: dict[str, Program],
) -> None:
    contents = archive_state.get("archive_contents")
    if contents is None:
        return
    missing: set[str] = set()
    for island in contents["islands"]:
        archive = island["archive"]
        for cell in archive.get("cells", []):
            program_id = cell.get("program_id")
            if isinstance(program_id, str) and program_id not in programs_by_id:
                missing.add(program_id)
        for program_id in archive.get("elite_program_ids", []):
            if isinstance(program_id, str) and program_id not in programs_by_id:
                missing.add(program_id)
        for program_id in archive.get("pareto_frontier_program_ids", []):
            if isinstance(program_id, str) and program_id not in programs_by_id:
                missing.add(program_id)
    if missing:
        raise ArchiveStateRestoreError(
            "archive state snapshot references programs missing from history.jsonl: "
            f"{sorted(missing)}"
        )


def _workspace_path_policy_record(program: Program) -> dict:
    allowed_reserved_paths = sorted(program.allowed_reserved_paths)
    return {
        "policy": "strict_candidate_paths_with_seed_reserved_allowlist",
        "reserved_components": ["dot-prefixed", "__pycache__"],
        "allowed_reserved_paths": allowed_reserved_paths,
    }


def _seed_source_metadata(program: Program) -> dict:
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    return {
        key: metadata[key]
        for key in (
            "seed_index",
            "seed_source_path",
            "seed_source_kind",
            "primary_file",
            "file_count",
            "files",
            "allowed_reserved_paths",
            "seed_variant_id",
            "seed_idea_origin",
            "seed_idea_label",
            "seed_idea_summary",
            "seed_contribution_roles",
            "seed_prior_technique",
            "seed_background_refs",
        )
        if key in metadata
    }


def _validate_program_history_record(
    program: Program, path: Path, *, metadata: dict | None = None
) -> None:
    record = _program_history_record(program, metadata=metadata)
    _validate_history_record_fitness(record, path)
    _validate_history_record_generation(record, path)
    _validate_history_record_metrics(record, path)
    _validate_history_record_identity(record, path)
    strict_json_text_for_path(record, path)


def _validate_history_record_identity(
    record: dict,
    path: Path,
    *,
    quarantine_path: Path | None = None,
    jsonl: bool = False,
    quarantine_snapshot_retention_mode: str = "redacted",
) -> None:
    try:
        if "id" in record:
            validate_program_identity(record.get("id"), record.get("parent_id"), record.get("lineage"))
        elif "program_id" in record:
            validate_program_identity(record.get("program_id"), record.get("parent_id"), None)
        return
    except ValueError as exc:
        if quarantine_path is not None:
            append_quarantine_record(
                quarantine_path,
                record,
                exc,
                retention_mode=quarantine_snapshot_retention_mode,
            )
        kind = "strict JSONL record" if jsonl else "strict JSON"
        raise StrictJsonlError(
            f"Could not serialize {kind} for {path}: {exc}"
        ) from exc


def _validate_unique_logged_program_id(
    program_id: str,
    seen_ids: set[str],
    path: Path,
    *,
    record: dict | None = None,
    quarantine_path: Path | None = None,
    quarantine_snapshot_retention_mode: str = "redacted",
) -> None:
    if program_id not in seen_ids:
        return
    exc = ValueError(f"duplicate program id {program_id!r}")
    if record is not None and quarantine_path is not None:
        append_quarantine_record(
            quarantine_path,
            record,
            exc,
            retention_mode=quarantine_snapshot_retention_mode,
        )
    raise StrictJsonlError(f"Could not serialize strict JSONL record for {path}: {exc}") from exc


def _validate_unique_failed_program_id(
    program_id: str,
    seen_ids: set[str],
    path: Path,
    *,
    record: dict | None = None,
    quarantine_path: Path | None = None,
    quarantine_snapshot_retention_mode: str = "redacted",
) -> None:
    if program_id not in seen_ids:
        return
    exc = ValueError(f"duplicate failed program id {program_id!r}")
    if record is not None and quarantine_path is not None:
        append_quarantine_record(
            quarantine_path,
            record,
            exc,
            retention_mode=quarantine_snapshot_retention_mode,
        )
    raise StrictJsonlError(f"Could not serialize strict JSONL record for {path}: {exc}") from exc


def _validate_unique_archive_program_id(
    program: Program,
    archive_ids: set[str],
    logged_programs_by_id: dict[str, Program],
) -> None:
    if program.id in archive_ids:
        raise ValueError(f"duplicate archive program id {program.id!r}")
    logged = logged_programs_by_id.get(program.id)
    if logged is not None and logged is not program:
        raise ValueError(f"duplicate archive program id {program.id!r}")


def _validate_history_record_fitness(
    record: dict,
    path: Path,
    *,
    quarantine_path: Path | None = None,
    jsonl: bool = False,
    quarantine_snapshot_retention_mode: str = "redacted",
) -> None:
    if _is_finite_real(record.get("fitness")):
        return
    exc = ValueError(
        f"fitness must be a finite non-boolean number, got {record.get('fitness')!r}"
    )
    if quarantine_path is not None:
        append_quarantine_record(
            quarantine_path,
            record,
            exc,
            retention_mode=quarantine_snapshot_retention_mode,
        )
    kind = "strict JSONL record" if jsonl else "strict JSON"
    raise StrictJsonlError(
        f"Could not serialize {kind} for {path}: {exc}"
    ) from exc


def _validate_history_record_generation(
    record: dict,
    path: Path,
    *,
    quarantine_path: Path | None = None,
    jsonl: bool = False,
    quarantine_snapshot_retention_mode: str = "redacted",
) -> None:
    generation = record.get("generation")
    if (
        not isinstance(generation, bool)
        and isinstance(generation, int)
        and generation >= 0
    ):
        return
    exc = ValueError(
        "generation must be a non-negative integer, "
        f"got {generation!r}"
    )
    if quarantine_path is not None:
        append_quarantine_record(
            quarantine_path,
            record,
            exc,
            retention_mode=quarantine_snapshot_retention_mode,
        )
    kind = "strict JSONL record" if jsonl else "strict JSON"
    raise StrictJsonlError(
        f"Could not serialize {kind} for {path}: {exc}"
    ) from exc


def _validate_history_record_metrics(
    record: dict,
    path: Path,
    *,
    quarantine_path: Path | None = None,
    jsonl: bool = False,
    quarantine_snapshot_retention_mode: str = "redacted",
) -> None:
    try:
        record["metrics"] = validate_program_metrics(record.get("metrics"))
        return
    except ValueError as exc:
        if quarantine_path is not None:
            append_quarantine_record(
                quarantine_path,
                record,
                exc,
                retention_mode=quarantine_snapshot_retention_mode,
            )
        kind = "strict JSONL record" if jsonl else "strict JSON"
        raise StrictJsonlError(
            f"Could not serialize {kind} for {path}: {exc}"
        ) from exc


def validate_context_sources(value: object) -> list[dict]:
    if not isinstance(value, list):
        raise StrictJsonlError("context_sources must be a list of mappings")
    sanitized = _validate_context_provenance_value(
        "context_sources",
        value,
        {"count": 0},
        depth=0,
    )
    if not isinstance(sanitized, list) or not all(
        isinstance(item, dict) for item in sanitized
    ):
        raise StrictJsonlError("context_sources must be a list of mappings")
    _validate_context_provenance_json_size("context_sources", sanitized)
    return sanitized


def validate_context_policy(value: object) -> dict:
    if not isinstance(value, dict):
        raise StrictJsonlError("context_policy must be a mapping")
    sanitized = _validate_context_provenance_value(
        "context_policy",
        value,
        {"count": 0},
        depth=0,
    )
    if not isinstance(sanitized, dict):
        raise StrictJsonlError("context_policy must be a mapping")
    _validate_context_provenance_json_size("context_policy", sanitized)
    return sanitized


def validate_retrieval_query_context(value: object) -> dict:
    if not isinstance(value, Mapping):
        raise StrictJsonlError("retrieval_query_context must be a mapping")
    allowed = {"task_description", "context_files", "local_papers"}
    unsupported = sorted(str(key) for key in value if str(key) not in allowed)
    if unsupported:
        raise StrictJsonlError(
            f"retrieval_query_context has unsupported keys {unsupported}"
        )
    task_description = value.get("task_description", "")
    if task_description is None:
        task_description = ""
    if not isinstance(task_description, str):
        raise StrictJsonlError("retrieval_query_context.task_description must be text")
    context_files = value.get("context_files", {})
    if context_files is None:
        context_files = {}
    if not isinstance(context_files, Mapping):
        raise StrictJsonlError("retrieval_query_context.context_files must be a mapping")
    normalized_context_files: dict[str, str] = {}
    for raw_label, raw_text in context_files.items():
        if not isinstance(raw_label, str) or not isinstance(raw_text, str):
            raise StrictJsonlError(
                "retrieval_query_context.context_files must map text labels to text"
            )
        normalized_context_files[redact_sensitive_text(raw_label)] = redact_sensitive_text(
            raw_text
        )
    local_papers = value.get("local_papers", [])
    if local_papers is None:
        local_papers = []
    if not isinstance(local_papers, list):
        raise StrictJsonlError("retrieval_query_context.local_papers must be a list")
    normalized_local_papers: list[dict] = []
    for index, raw_row in enumerate(local_papers):
        if not isinstance(raw_row, Mapping):
            raise StrictJsonlError(
                "retrieval_query_context.local_papers must contain mappings"
            )
        row: dict[str, object] = {}
        for key in ("id", "title", "url", "file", "sha256"):
            raw_value = raw_row.get(key)
            if raw_value is None:
                continue
            if not isinstance(raw_value, str):
                raise StrictJsonlError(
                    f"retrieval_query_context.local_papers[{index}].{key} must be text"
                )
            row[key] = redact_sensitive_text(raw_value)
        raw_ok = raw_row.get("ok")
        if raw_ok is not None:
            if not isinstance(raw_ok, bool):
                raise StrictJsonlError(
                    f"retrieval_query_context.local_papers[{index}].ok must be a boolean"
                )
            row["ok"] = raw_ok
        raw_bytes = raw_row.get("bytes")
        if raw_bytes is not None:
            if (
                isinstance(raw_bytes, bool)
                or not isinstance(raw_bytes, int)
                or raw_bytes < 0
            ):
                raise StrictJsonlError(
                    f"retrieval_query_context.local_papers[{index}].bytes must be a nonnegative integer"
                )
            row["bytes"] = raw_bytes
        if row:
            normalized_local_papers.append(row)
    record = {
        "schema": "libreevolve.retrieval_query_context.v1",
        "task_description": redact_sensitive_text(task_description),
        "context_files": normalized_context_files,
        "local_papers": normalized_local_papers,
    }
    _validate_context_provenance_json_size("retrieval_query_context", record)
    return record


def _retrieval_failure_context_record(record: dict) -> dict:
    evaluation = record.get("evaluation")
    if not isinstance(evaluation, dict):
        evaluation = {}
    stages = evaluation.get("stages")
    stage_errors: list[str] = []
    if isinstance(stages, list):
        for stage in stages[:3]:
            if isinstance(stage, dict) and stage.get("error"):
                stage_errors.append(_failure_optional_text(stage.get("error"), 200) or "")
    return {
        "schema": "libreevolve.retrieval_failure_context.v1",
        "program_id": _failure_optional_text(record.get("program_id"), 128),
        "record_type": record.get("record_type", "generated"),
        "reason": _failure_optional_text(
            record.get("admission_reason") or record.get("diff_error") or record.get("error"),
            300,
        ),
        "error": _failure_optional_text(record.get("error"), 300),
        "diff_error": _failure_optional_json_text(record.get("diff_error"), 300),
        "changed_files": [
            _failure_optional_text(path, 120)
            for path in (record.get("changed_files") if isinstance(record.get("changed_files"), list) else [])
        ][:8],
        "evaluation_error": _failure_optional_text(evaluation.get("error"), 300),
        "stage_errors": [error for error in stage_errors if error],
        "repetition_count": record.get("repetition_count"),
    }


def _retrieval_hypothesis_context_record(program: Program) -> dict:
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    proposal = metadata.get("proposal")
    if not isinstance(proposal, Mapping):
        return {}
    hypothesis = _failure_optional_text(proposal.get("hypothesis"), 300)
    idea = _failure_optional_text(proposal.get("idea"), 200)
    rationale = _failure_optional_text(proposal.get("rationale"), 200)
    if not any((hypothesis, idea, rationale)):
        return {}
    admission = metadata.get("archive_admission")
    if not isinstance(admission, Mapping):
        admission = {}
    return {
        "schema": "libreevolve.retrieval_hypothesis_context.v1",
        "program_id": _failure_optional_text(program.id, 128),
        "generation": program.generation,
        "archive_admitted": admission.get("admitted"),
        "admission_reason": _failure_optional_text(admission.get("reason"), 120),
        "idea": idea,
        "rationale": rationale,
        "hypothesis": hypothesis,
    }


def validate_seed_policy(value: object) -> dict:
    if not isinstance(value, dict):
        raise StrictJsonlError("seed_policy must be a mapping")
    sanitized = _validate_context_provenance_value(
        "seed_policy",
        value,
        {"count": 0},
        depth=0,
    )
    if not isinstance(sanitized, dict):
        raise StrictJsonlError("seed_policy must be a mapping")
    _validate_context_provenance_json_size("seed_policy", sanitized)
    return sanitized


def validate_seed_sources(value: object) -> list[dict]:
    if not isinstance(value, list):
        raise StrictJsonlError("seed_sources must be a list of mappings")
    return [_validate_seed_source_record(index, source) for index, source in enumerate(value)]


def validate_seed_skipped(value: object) -> list[dict]:
    if not isinstance(value, list):
        raise StrictJsonlError("seed_skipped must be a list of mappings")
    sanitized = _validate_context_provenance_value(
        "seed_skipped",
        value,
        {"count": 0},
        depth=0,
    )
    if not isinstance(sanitized, list):
        raise StrictJsonlError("seed_skipped must be a list of mappings")
    for index, record in enumerate(sanitized):
        if not isinstance(record, dict):
            raise StrictJsonlError(f"seed_skipped[{index}] must be a mapping")
    _validate_context_provenance_json_size("seed_skipped", sanitized)
    return sanitized


def validate_seed_source_record(index: int, source: object | None) -> dict:
    return _validate_seed_source_record(index, source)


def _validate_seed_source_record(index: int, source: object | None) -> dict:
    label = f"seed_sources[{index}]"
    if source is None:
        source = {}
    if not isinstance(source, Mapping):
        raise StrictJsonlError(f"{label} must be a mapping")
    if not all(isinstance(key, str) for key in source):
        raise StrictJsonlError(f"{label} keys must be strings")
    unsupported = sorted(redact_sensitive_text(key) for key in set(source) - _SEED_SOURCE_ALLOWED_KEYS)
    if unsupported:
        raise StrictJsonlError(f"{label} has unsupported fields {unsupported}")
    normalized: dict = {}
    if "seed_index" in source:
        seed_index = source["seed_index"]
        if isinstance(seed_index, bool) or not isinstance(seed_index, int) or seed_index < 0:
            raise StrictJsonlError(f"{label}.seed_index must be a non-negative integer")
        if seed_index != index:
            raise StrictJsonlError(f"{label}.seed_index must match seed position {index}")
    normalized["seed_index"] = index
    kind = source.get("seed_source_kind", "workspace")
    if not isinstance(kind, str) or kind not in _SEED_SOURCE_KINDS:
        raise StrictJsonlError(
            f"{label}.seed_source_kind must be one of {sorted(_SEED_SOURCE_KINDS)}"
        )
    normalized["seed_source_kind"] = kind
    allowed_reserved_paths = _normalize_seed_allowed_reserved_paths(
        f"{label}.allowed_reserved_paths",
        source.get("allowed_reserved_paths", []),
    )
    if allowed_reserved_paths:
        normalized["allowed_reserved_paths"] = sorted(allowed_reserved_paths)
    if "seed_source_path" in source:
        normalized["seed_source_path"] = _normalize_seed_source_path(
            f"{label}.seed_source_path",
            source["seed_source_path"],
            allow_reserved=True,
        )
    elif kind in {"file", "directory"}:
        raise StrictJsonlError(f"{label}.seed_source_path is required for {kind} seeds")
    if "primary_file" in source:
        normalized["primary_file"] = _normalize_seed_source_path(
            f"{label}.primary_file",
            source["primary_file"],
            allowed_reserved_paths=allowed_reserved_paths,
        )
    if "files" in source:
        files = source["files"]
        if not isinstance(files, list):
            raise StrictJsonlError(f"{label}.files must be a list of path labels")
        seen_files: set[str] = set()
        normalized_files = []
        for file_index, file_path in enumerate(files):
            path = _normalize_seed_source_path(
                f"{label}.files[{file_index}]",
                file_path,
                allowed_reserved_paths=allowed_reserved_paths,
            )
            if path in seen_files:
                raise StrictJsonlError(f"{label}.files must not contain duplicates")
            seen_files.add(path)
            normalized_files.append(path)
        normalized["files"] = sorted(normalized_files)
    if "file_count" in source:
        file_count = source["file_count"]
        if isinstance(file_count, bool) or not isinstance(file_count, int) or file_count < 0:
            raise StrictJsonlError(f"{label}.file_count must be a non-negative integer")
        if "files" in normalized and file_count != len(normalized["files"]):
            raise StrictJsonlError(f"{label}.file_count must match files length")
        normalized["file_count"] = file_count
    elif "files" in normalized:
        normalized["file_count"] = len(normalized["files"])
    if "primary_file" in normalized and "files" in normalized:
        if normalized["primary_file"] not in normalized["files"]:
            raise StrictJsonlError(f"{label}.primary_file must be present in files")
    _normalize_seed_idea_metadata(label, source, normalized)
    _validate_seed_source_json_size(label, normalized)
    return normalized


def _normalize_seed_idea_metadata(
    label: str,
    source: Mapping[str, object],
    normalized: dict,
) -> None:
    if "seed_variant_id" in source:
        normalized["seed_variant_id"] = _normalize_seed_idea_token(
            f"{label}.seed_variant_id",
            source["seed_variant_id"],
        )
    if "seed_idea_origin" in source:
        origin = source["seed_idea_origin"]
        if not isinstance(origin, str) or origin not in _SEED_IDEA_ORIGINS:
            raise StrictJsonlError(
                f"{label}.seed_idea_origin must be one of {sorted(_SEED_IDEA_ORIGINS)}"
            )
        normalized["seed_idea_origin"] = origin
    if "seed_idea_label" in source:
        normalized["seed_idea_label"] = _normalize_seed_idea_text(
            f"{label}.seed_idea_label",
            source["seed_idea_label"],
            max_chars=_SEED_IDEA_LABEL_MAX_CHARS,
        )
    if "seed_idea_summary" in source:
        normalized["seed_idea_summary"] = _normalize_seed_idea_text(
            f"{label}.seed_idea_summary",
            source["seed_idea_summary"],
            max_chars=_SEED_IDEA_TEXT_MAX_CHARS,
        )
    if "seed_prior_technique" in source:
        normalized["seed_prior_technique"] = _normalize_seed_idea_text(
            f"{label}.seed_prior_technique",
            source["seed_prior_technique"],
            max_chars=_SEED_IDEA_TEXT_MAX_CHARS,
        )
    if "seed_contribution_roles" in source:
        roles = source["seed_contribution_roles"]
        if not isinstance(roles, list) or not roles:
            raise StrictJsonlError(
                f"{label}.seed_contribution_roles must be a non-empty list"
            )
        normalized_roles = []
        for role_index, role in enumerate(roles):
            if not isinstance(role, str) or role not in _SEED_CONTRIBUTION_ROLES:
                raise StrictJsonlError(
                    f"{label}.seed_contribution_roles[{role_index}] must be one of "
                    f"{sorted(_SEED_CONTRIBUTION_ROLES)}"
                )
            if role not in normalized_roles:
                normalized_roles.append(role)
        normalized["seed_contribution_roles"] = normalized_roles
    if "seed_background_refs" in source:
        refs = source["seed_background_refs"]
        if not isinstance(refs, list):
            raise StrictJsonlError(f"{label}.seed_background_refs must be a list")
        normalized_refs = []
        for ref_index, ref in enumerate(refs):
            normalized_ref = _normalize_seed_idea_text(
                f"{label}.seed_background_refs[{ref_index}]",
                ref,
                max_chars=_SEED_BACKGROUND_REF_MAX_CHARS,
            )
            if normalized_ref not in normalized_refs:
                normalized_refs.append(normalized_ref)
        normalized["seed_background_refs"] = normalized_refs


def _normalize_seed_idea_token(label: str, value: object) -> str:
    if not isinstance(value, str) or not value:
        raise StrictJsonlError(f"{label} must be non-empty text")
    if len(value) > _SEED_IDEA_LABEL_MAX_CHARS:
        raise StrictJsonlError(
            f"{label} must be <= {_SEED_IDEA_LABEL_MAX_CHARS} characters"
        )
    if redact_sensitive_text(value) != value:
        raise StrictJsonlError(f"{label} must not contain secret-like text")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", value):
        raise StrictJsonlError(f"{label} must be a safe seed metadata token")
    return value


def _normalize_seed_idea_text(
    label: str,
    value: object,
    *,
    max_chars: int,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StrictJsonlError(f"{label} must be non-empty text")
    if len(value) > max_chars:
        raise StrictJsonlError(f"{label} must be <= {max_chars} characters")
    redacted = redact_sensitive_text(value.strip())
    if redacted != value.strip():
        raise StrictJsonlError(f"{label} must not contain secret-like text")
    if any(ord(char) < 32 or ord(char) == 127 for char in redacted):
        raise StrictJsonlError(f"{label} must not contain control characters")
    return redacted


def _normalize_seed_source_path(
    label: str,
    value: object,
    *,
    allowed_reserved_paths: frozenset[str] = frozenset(),
    allow_reserved: bool = False,
) -> str:
    if not isinstance(value, str) or not value:
        raise StrictJsonlError(f"{label} must be a non-empty path label")
    if len(value) > _MAX_SEED_SOURCE_STRING_CHARS:
        raise StrictJsonlError(
            f"{label} must be <= {_MAX_SEED_SOURCE_STRING_CHARS} characters"
        )
    try:
        effective_allowed = (
            frozenset({value})
            if allow_reserved and _seed_source_path_has_reserved_component(value)
            else allowed_reserved_paths
        )
        return normalize_candidate_path(value, allowed_reserved_paths=effective_allowed)
    except ValueError as exc:
        raise StrictJsonlError(f"{label} must be a safe path label: {exc}") from exc


def _normalize_seed_allowed_reserved_paths(label: str, value: object) -> frozenset[str]:
    if value in (None, ""):
        return frozenset()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise StrictJsonlError(f"{label} must be a list of path labels")
    normalized: set[str] = set()
    for index, raw_path in enumerate(value):
        item_label = f"{label}[{index}]"
        try:
            effective_allowed = (
                {raw_path}
                if _seed_source_path_has_reserved_component(raw_path)
                else ()
            )
            path = normalize_candidate_path(
                raw_path,
                allowed_reserved_paths=effective_allowed,
            )
        except ValueError as exc:
            raise StrictJsonlError(f"{item_label} must be a safe path label: {exc}") from exc
        if not any(part == "__pycache__" or part.startswith(".") for part in path.split("/")):
            raise StrictJsonlError(f"{item_label} must name a reserved path")
        normalized.add(path)
    return frozenset(normalized)


def _seed_source_path_has_reserved_component(path: str) -> bool:
    return any(part == "__pycache__" or part.startswith(".") for part in path.split("/"))


def _validate_seed_source_json_size(label: str, record: dict) -> None:
    try:
        text = json.dumps(record, sort_keys=True, allow_nan=False, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise StrictJsonlError(f"{label} must be strict JSON-safe: {exc}") from exc
    if len(text) > _MAX_CONTEXT_PROVENANCE_STRING_CHARS:
        raise StrictJsonlError(
            f"{label} JSON exceeds {_MAX_CONTEXT_PROVENANCE_STRING_CHARS} chars"
        )


def _validate_context_provenance_value(
    path: str,
    value: object,
    item_counter: dict[str, int],
    *,
    depth: int,
) -> object:
    if depth > _MAX_CONTEXT_PROVENANCE_DEPTH:
        raise StrictJsonlError(
            f"{path} exceeds maximum context provenance nesting depth "
            f"{_MAX_CONTEXT_PROVENANCE_DEPTH}"
        )
    item_counter["count"] += 1
    if item_counter["count"] > _MAX_CONTEXT_PROVENANCE_ITEMS:
        raise StrictJsonlError(
            f"{path} exceeds maximum context provenance item count "
            f"{_MAX_CONTEXT_PROVENANCE_ITEMS}"
        )
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise StrictJsonlError(f"{path} keys must be strings")
            safe_key = redact_sensitive_text(key)
            if len(safe_key) > _MAX_CONTEXT_PROVENANCE_STRING_CHARS:
                raise StrictJsonlError(
                    f"{path}.{safe_key[:80]!r} key exceeds "
                    f"{_MAX_CONTEXT_PROVENANCE_STRING_CHARS} chars"
                )
            sanitized[safe_key] = _validate_context_provenance_value(
                f"{path}.{safe_key}",
                item,
                item_counter,
                depth=depth + 1,
            )
        return sanitized
    if isinstance(value, list):
        return [
            _validate_context_provenance_value(
                f"{path}[{index}]",
                item,
                item_counter,
                depth=depth + 1,
            )
            for index, item in enumerate(value)
        ]
    if isinstance(value, str):
        safe_value = redact_sensitive_text(value)
        if len(safe_value) > _MAX_CONTEXT_PROVENANCE_STRING_CHARS:
            raise StrictJsonlError(
                f"{path} string exceeds {_MAX_CONTEXT_PROVENANCE_STRING_CHARS} chars"
            )
        return safe_value
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise StrictJsonlError(f"{path} must be finite")
        return value
    raise StrictJsonlError(f"{path} must be JSON-safe context provenance")


def _validate_context_provenance_json_size(path: str, value: object) -> None:
    try:
        text = json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise StrictJsonlError(f"{path} must be strict JSON-safe: {exc}") from exc
    if len(text) > _MAX_CONTEXT_PROVENANCE_JSON_CHARS:
        raise StrictJsonlError(
            f"{path} JSON exceeds {_MAX_CONTEXT_PROVENANCE_JSON_CHARS} chars"
        )


def _startup_manifest_payload(
    config: Config,
    context_sources: list[dict],
    context_policy: dict,
    objective_schema: dict,
    evaluator_sources: list[dict],
    run_provenance: dict,
    foreign_entries: list[dict],
    seed_sources: list[dict],
    seed_skipped: list[dict],
    seed_policy: dict,
    archive_cursor_restore: dict,
) -> dict:
    manifest_log_dir = _manifest_log_dir(config.log_dir)
    prompt_variants = _manifest_prompt_text_list(config.prompt_variants)
    prompt_format_options = _manifest_prompt_format_options(
        config.prompt_format_options
    )
    critique_prompt = _manifest_prompt_text(config.critique_prompt)
    llm_feedback = _manifest_llm_feedback(config.llm_feedback)
    llm_prompt_roles = _manifest_prompt_roles(config.llm_prompt_roles)
    evaluator_stdin = _manifest_evaluator_stdin_config(
        config.evaluator_stdin_text,
        config.evaluator_stdin_file,
    )
    manifest = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_schema": run_artifact_schema(),
        "config": {
            "max_generations": config.max_generations,
            "max_evaluations": config.max_evaluations,
            "max_evaluator_seconds": config.max_evaluator_seconds,
            "max_evaluator_subprocess_attempts": (
                config.max_evaluator_subprocess_attempts
            ),
            "max_evaluator_stage_samples": config.max_evaluator_stage_samples,
            "max_evaluator_retry_attempts": config.max_evaluator_retry_attempts,
            "max_evaluator_timeouts": config.max_evaluator_timeouts,
            "max_evaluator_sample_budget_exhaustions": (
                config.max_evaluator_sample_budget_exhaustions
            ),
            "max_evaluator_stage_budget_exhaustions": (
                config.max_evaluator_stage_budget_exhaustions
            ),
            "max_runtime_seconds": config.max_runtime_seconds,
            "proposals_per_generation": config.proposals_per_generation,
            "num_inspirations": config.num_inspirations,
            "eval_timeout_sec": config.eval_timeout_sec,
            "validator_env_allowlist": config.validator_env_allowlist,
            "validator_network_policy": config.validator_network_policy,
            "evaluator_artifact_include": config.evaluator_artifact_include,
            "evaluator_artifact_exclude": config.evaluator_artifact_exclude,
            "evaluator_artifact_max_files": config.evaluator_artifact_max_files,
            "evaluator_artifact_max_bytes": config.evaluator_artifact_max_bytes,
            "evaluator_artifact_redact_secrets": config.evaluator_artifact_redact_secrets,
            "evaluator_data_include": config.evaluator_data_include,
            "evaluator_data_exclude": config.evaluator_data_exclude,
            "evaluator_stdin": evaluator_stdin,
            "explore_ratio": config.explore_ratio,
            "parent_selection_strategy": config.parent_selection_strategy,
            "inspiration_strategy": config.inspiration_strategy,
            "mutation_mode": config.mutation_mode,
            "initial_program_validity_policy": (
                config.initial_program_validity_policy
            ),
            "max_candidate_workspace_files": config.max_candidate_workspace_files,
            "max_candidate_file_chars": config.max_candidate_file_chars,
            "max_candidate_total_chars": config.max_candidate_total_chars,
            "max_candidate_static_file_bytes": config.max_candidate_static_file_bytes,
            "max_candidate_total_static_bytes": config.max_candidate_total_static_bytes,
            "eval_stages": _manifest_eval_stages(config.eval_stages),
            "prompt_variants": prompt_variants["values"],
            "prompt_variant_semantic_policy": config.prompt_variant_semantic_policy,
            "prompt_variants_metadata": prompt_variants["metadata"],
            "prompt_format_options": prompt_format_options["values"],
            "prompt_format_options_metadata": prompt_format_options["metadata"],
            "prompt_max_chars": config.prompt_max_chars,
            "prompt_max_estimated_tokens": config.prompt_max_estimated_tokens,
            "mutation_prompt_retention_mode": config.mutation_prompt_retention_mode,
            "explicit_context_retention_mode": config.explicit_context_retention_mode,
            "meta_prompt_evidence_retention_mode": (
                config.meta_prompt_evidence_retention_mode
            ),
            "quarantine_snapshot_retention_mode": (
                config.quarantine_snapshot_retention_mode
            ),
            "critique_retention_mode": config.critique_retention_mode,
            "feedback_retention_mode": config.feedback_retention_mode,
            "plugin_context_retention_mode": config.plugin_context_retention_mode,
            "meta_prompt_evolution": config.meta_prompt_evolution,
            "meta_prompt_interval": config.meta_prompt_interval,
            "prompt_reward_mode": config.prompt_reward_mode,
            "prompt_reward_bounds": config.prompt_reward_bounds,
            "prompt_explore_coeff": config.prompt_explore_coeff,
            "critique_enabled": config.critique_enabled,
            "critique_prompt": critique_prompt["value"],
            "critique_prompt_metadata": critique_prompt["metadata"],
            "critique_reviewers": config.critique_reviewers,
            "critique_aggregation_policy": config.critique_aggregation_policy,
            "llm_feedback": llm_feedback["values"],
            "llm_feedback_metadata": llm_feedback["metadata"],
            "capture_proposal_metadata": config.capture_proposal_metadata,
            "n_islands": config.n_islands,
            "migration_interval": config.migration_interval,
            "migration_ratio": config.migration_ratio,
            "map_elites_bins": config.map_elites_bins,
            "map_elites_complexity_max_chars": (
                config.map_elites_complexity_max_chars
            ),
            "map_elites_descriptor_axes": list(config.map_elites_descriptor_axes),
            "elite_archive_size": config.elite_archive_size,
            "backends": config.backends,
            "ensemble_explore_coeff": config.ensemble_explore_coeff,
            "ensemble_strategy": config.ensemble_strategy,
            "llm_max_retries": config.llm_max_retries,
            "llm_max_call_attempts": config.llm_max_call_attempts,
            "llm_fallback": config.llm_fallback,
            "llm_max_response_chars": config.llm_max_response_chars,
            "llm_call_history_max": config.llm_call_history_max,
            "provider_response_retention_mode": config.provider_response_retention_mode,
            "provider_error_retention_mode": config.provider_error_retention_mode,
            "max_llm_calls": config.max_llm_calls,
            "max_llm_provider_attempts": config.max_llm_provider_attempts,
            "max_llm_tokens": config.max_llm_tokens,
            "max_llm_cost_microusd": config.max_llm_cost_microusd,
            "max_llm_seconds": config.max_llm_seconds,
            "llm_role_call_limits": dict(config.llm_role_call_limits),
            "llm_role_provider_attempt_limits": dict(
                config.llm_role_provider_attempt_limits
            ),
            "llm_role_token_limits": dict(config.llm_role_token_limits),
            "llm_role_cost_microusd_limits": dict(
                config.llm_role_cost_microusd_limits
            ),
            "llm_role_seconds_limits": dict(config.llm_role_seconds_limits),
            "llm_reward_accounted_roles": list(config.llm_reward_accounted_roles),
            "llm_role_backend_indices": {
                role: list(indices)
                for role, indices in config.llm_role_backend_indices.items()
            },
            "llm_prompt_roles": llm_prompt_roles["values"],
            "llm_prompt_roles_metadata": llm_prompt_roles["metadata"],
            "plugins": config.plugins,
            "log_dir": manifest_log_dir["value"],
            "log_dir_metadata": manifest_log_dir["metadata"],
            "problem_name": config.problem_name,
            "run_id": config.run_id,
            "run_collision_policy": config.run_collision_policy,
            "seed": config.seed,
        },
        "problem": {
            "objective_schema": objective_schema,
            "context_sources": context_sources,
            "context_policy": context_policy,
            "evaluator_sources": evaluator_sources,
            "seed_sources": seed_sources,
            "seed_skipped": seed_skipped,
            "seed_policy": seed_policy,
        },
        "policies": {
            "redaction": redaction_policy_record(),
            "openai_api_mode": _openai_api_mode_manifest_policy(config.backends),
            "provider_capability_lookup": _provider_capability_lookup_policy(
                config.backends
            ),
            "prompt_config_retention": {
                "policy": "redact_and_hash_prompt_bearing_config",
                "fields": [
                    "prompt_variants",
                    "prompt_format_options.*.text",
                    "critique_prompt",
                    "llm_feedback[].prompt",
                    "llm_prompt_roles.*.system",
                    "llm_prompt_roles.*.developer",
                ],
                "default_max_retained_chars": _MANIFEST_PROMPT_CONFIG_MAX_CHARS,
                "hash": "sha256_of_original_text",
            },
            "prompt_data_retention": _prompt_data_retention_policy(config),
            "validator_stdin": _validator_stdin_policy(),
            "validator_execution": _validator_execution_policy(
                config.validator_network_policy
            ),
            "validator_network": _validator_network_policy(
                config.validator_network_policy
            ),
            "candidate_language": _candidate_language_policy(),
            "seed_post_processing": {
                "policy": "raw_evaluator_baseline",
                "llm_feedback": "not_applied",
                "plugin_score_composition": "not_applied",
                "reason": (
                    "Initial seeds are evaluated before mutation LLMs, "
                    "feedback graders, and plugin score-composition hooks."
                ),
            },
            "initial_program_validity": {
                "policy": config.initial_program_validity_policy,
                "permissive_baseline_behavior": (
                    "evaluate_and_log_invalid_generation_zero_seeds"
                ),
                "strict_behavior": (
                    "stop_after_seed_evaluation_when_any_seed_lacks_evaluator_"
                    "validity_or_declared_metrics"
                ),
                "strict_stop_reason": "invalid_initial_programs",
            },
            "candidate_workspace_size": {
                "policy": "reject_oversized_text_and_static_workspace",
                "max_files": config.max_candidate_workspace_files,
                "max_file_chars": config.max_candidate_file_chars,
                "max_total_chars": config.max_candidate_total_chars,
                "max_static_file_bytes": config.max_candidate_static_file_bytes,
                "max_total_static_bytes": config.max_candidate_total_static_bytes,
                "spillover": "not_implemented",
                "summary_only_persistence": "not_used",
            },
            "candidate_artifacts": {
                "policy": "text_workspace_with_typed_static_metadata",
                "candidate_member_types": [
                    "utf8_text_file",
                    "typed_static_metadata",
                    "encoded_static_binary",
                    "verified_source_copy_static_asset",
                    "raw_binary_direct_workspace_record",
                ],
                "binary_candidate_members": (
                    "encoded_static_members_materialized_when_content_b64_present"
                ),
                "raw_binary_direct_workspace_records": (
                    "bytes_values_normalized_to_immutable_binary_static_members"
                ),
                "source_copy_static_assets": (
                    "source_copy_path_materialized_after_size_and_sha256_verification"
                ),
                "static_asset_mutation": (
                    "generated_and_existing_llm_editable_static_members_via_bounded_base64"
                ),
                "seed_workspace_binary_policy": (
                    "encode_bounded_non_utf8_seed_files_as_static_members_when_text_primary_exists_else_skip"
                ),
                "generated_artifact_policy": (
                    "validator_outputs_collected_by_evaluator_artifacts"
                ),
                "hash_scope": "candidate_text_files_and_typed_static_metadata",
                "remaining_gap": None,
            },
            "archive_identity": {
                "program_id_policy": "run_local_unique_canonical_program_id",
                "duplicate_archive_ids": "rejected_before_island_mutation",
                "migration_policy": "canonical_id_reference",
                "migration_clone_ids": "not_created",
                "migration_duplicate_target_policy": "skip_existing_target_id",
                "resume_status": "manifest_archive_state_restore_supported",
                "restore_surfaces": [
                    "round_robin_cursor",
                    "archive_sequence_counters",
                    "map_elites_cells",
                    "elite_archives",
                ],
                "migration_event_replay": "audit_only_not_restore_engine",
            },
            "archive_cursor_restore": archive_cursor_restore,
        },
        "run_directory": {
            "foreign_entry_policy": "preserved_outside_run_contract",
            "foreign_entry_count": len(foreign_entries),
            "foreign_entries": foreign_entries,
        },
        "provenance": run_provenance,
    }
    manifest["task_specification"] = _task_specification_bundle(manifest)
    return manifest


def _task_specification_bundle(manifest: Mapping[str, object]) -> dict:
    config = manifest.get("config") if isinstance(manifest.get("config"), Mapping) else {}
    problem = manifest.get("problem") if isinstance(manifest.get("problem"), Mapping) else {}
    policies = manifest.get("policies") if isinstance(manifest.get("policies"), Mapping) else {}
    seed_sources = _manifest_list(problem.get("seed_sources"))
    seed_skipped = _manifest_list(problem.get("seed_skipped"))
    evaluator_sources = _manifest_list(problem.get("evaluator_sources"))
    context_sources = _manifest_list(problem.get("context_sources"))
    prompt_metadata = _manifest_list(config.get("prompt_variants_metadata"))
    backends = _manifest_list(config.get("backends"))
    candidate_language = (
        policies.get("candidate_language")
        if isinstance(policies.get("candidate_language"), Mapping)
        else {}
    )
    eval_stages = _manifest_list(config.get("eval_stages"))
    embedded_stages = [
        index
        for index, stage in enumerate(eval_stages)
        if isinstance(stage, Mapping) and stage.get("mode") == "embedded_evaluate"
    ]
    bundle = {
        "schema": TASK_SPECIFICATION_BUNDLE_SCHEMA,
        "source": "startup_manifest_cross_reference",
        "status": "partial_alphaevolve_task_specification",
        "fields": {
            "initial_programs": {
                "status": "present" if seed_sources else "missing",
                "manifest_path": "problem.seed_sources",
                "count": len(seed_sources),
                "skipped_count": len(seed_skipped),
                "ids": _seed_source_refs(seed_sources),
            },
            "evaluation_code": {
                "status": "present" if evaluator_sources or embedded_stages else "missing",
                "manifest_path": "problem.evaluator_sources",
                "entrypoint_count": len(evaluator_sources),
                "embedded_stage_indices": embedded_stages,
                "ids": _evaluator_source_refs(evaluator_sources),
                "embedded_candidate_evaluate": bool(embedded_stages),
            },
            "prompt_template_and_config": {
                "status": "present" if prompt_metadata else "missing",
                "manifest_path": "config.prompt_variants_metadata",
                "variant_count": len(prompt_metadata),
                "ids": _prompt_variant_refs(prompt_metadata),
                "prompt_format_option_count": len(
                    config.get("prompt_format_options", {})
                    if isinstance(config.get("prompt_format_options"), Mapping)
                    else {}
                ),
            },
            "llm_ensemble": {
                "status": "present" if backends else "missing",
                "manifest_path": "config.backends",
                "backend_count": len(backends),
                "ids": _backend_refs(backends),
                "role_routing_manifest_path": "config.llm_role_backend_indices",
            },
            "background_knowledge": {
                "status": "present" if context_sources else "omitted",
                "manifest_path": "problem.context_sources",
                "context_source_count": len(context_sources),
                "ids": _context_source_refs(context_sources),
                "context_policy_manifest_path": "problem.context_policy",
            },
            "candidate_representation": {
                "status": "present",
                "manifest_path": "policies.candidate_language",
                "policy": candidate_language.get("policy"),
                "primary_language": candidate_language.get("primary_language"),
                "language_runner_ready": candidate_language.get("language_runner_ready"),
            },
            "objective_metrics": {
                "status": "present"
                if isinstance(problem.get("objective_schema"), Mapping)
                else "missing",
                "manifest_path": "problem.objective_schema",
                "primary_metric": (
                    problem.get("objective_schema", {}).get("primary_metric")
                    if isinstance(problem.get("objective_schema"), Mapping)
                    else None
                ),
                "metric_count": (
                    problem.get("objective_schema", {}).get("metric_count")
                    if isinstance(problem.get("objective_schema"), Mapping)
                    else 0
                ),
            },
        },
        "unsupported_or_incomplete": [
            "unified_task_spec_bundle_is_manifest_evidence_not_standalone_problem_file",
            "embedded_only_problem_definitions_still_require_loader_support",
            "arbitrary_language_build_runner_task_specs_unsupported",
            "problem_defined_candidate_abstraction_hooks_unsupported",
            "skeleton_to_evolved_block_score_linkage_not_yet_reported",
        ],
    }
    bundle["task_spec_id"] = _task_specification_id(bundle)
    bundle["validation"] = validate_task_specification_bundle(bundle)
    return bundle


def validate_task_specification_bundle(bundle: object) -> dict:
    issues: list[dict] = []
    if not isinstance(bundle, Mapping):
        return {
            "schema": TASK_SPECIFICATION_BUNDLE_SCHEMA,
            "ok": False,
            "issues": [
                {
                    "code": "invalid_shape",
                    "message": "task specification bundle must be an object",
                }
            ],
        }
    required = {
        "schema",
        "source",
        "status",
        "fields",
        "unsupported_or_incomplete",
        "task_spec_id",
    }
    missing = required - set(bundle)
    if missing:
        issues.append(
            {
                "code": "missing_fields",
                "message": f"task specification bundle missing fields: {sorted(missing)}",
            }
        )
    unsupported = set(bundle) - (required | {"validation"})
    if unsupported:
        issues.append(
            {
                "code": "unsupported_fields",
                "message": f"task specification bundle has unsupported fields: {sorted(unsupported)}",
            }
        )
    _candidate_policy_issue_if(
        issues,
        bundle.get("schema") != TASK_SPECIFICATION_BUNDLE_SCHEMA,
        "invalid_schema",
        "task specification bundle schema is unsupported",
    )
    _candidate_policy_issue_if(
        issues,
        bundle.get("source") != "startup_manifest_cross_reference",
        "invalid_source",
        "task specification bundle must be derived from startup manifest evidence",
    )
    fields = bundle.get("fields")
    if not isinstance(fields, Mapping):
        issues.append(
            {
                "code": "invalid_fields",
                "message": "task specification fields must be an object",
            }
        )
    else:
        expected_fields = {
            "initial_programs",
            "evaluation_code",
            "prompt_template_and_config",
            "llm_ensemble",
            "background_knowledge",
            "candidate_representation",
            "objective_metrics",
        }
        missing_fields = expected_fields - set(fields)
        if missing_fields:
            issues.append(
                {
                    "code": "missing_task_fields",
                    "message": f"task specification fields missing: {sorted(missing_fields)}",
                }
            )
        for name, field in fields.items():
            if not isinstance(name, str) or not isinstance(field, Mapping):
                issues.append(
                    {
                        "code": "invalid_task_field",
                        "message": "task specification field entries must be named objects",
                    }
                )
                continue
            status = field.get("status")
            if status not in {"present", "missing", "omitted", "unsupported", "partial"}:
                issues.append(
                    {
                        "code": "invalid_field_status",
                        "message": f"task specification field {name!r} has invalid status",
                    }
                )
            manifest_path = field.get("manifest_path")
            if not isinstance(manifest_path, str) or not manifest_path:
                issues.append(
                    {
                        "code": "invalid_manifest_path",
                        "message": f"task specification field {name!r} must link to a manifest path",
                    }
                )
    gaps = bundle.get("unsupported_or_incomplete")
    if not isinstance(gaps, list) or not all(isinstance(item, str) and item for item in gaps):
        issues.append(
            {
                "code": "invalid_gap_list",
                "message": "task specification unsupported_or_incomplete must be a list of labels",
            }
        )
    task_spec_id = bundle.get("task_spec_id")
    expected_id = _task_specification_id(bundle)
    if task_spec_id != expected_id:
        issues.append(
            {
                "code": "invalid_task_spec_id",
                "message": "task specification id must hash the bundle content excluding validation/id",
            }
        )
    return {
        "schema": TASK_SPECIFICATION_BUNDLE_SCHEMA,
        "ok": not issues,
        "issues": issues,
    }


def _task_specification_id(bundle: Mapping[str, object]) -> str:
    payload = {
        key: value
        for key, value in bundle.items()
        if key not in {"task_spec_id", "validation"}
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _manifest_list(value: object) -> list:
    return list(value) if isinstance(value, list) else []


def _seed_source_refs(seed_sources: list) -> list[dict]:
    refs = []
    for index, source in enumerate(seed_sources):
        if not isinstance(source, Mapping):
            continue
        refs.append(
            {
                "seed_index": source.get("seed_index", index),
                "kind": source.get("seed_source_kind"),
                "path": source.get("seed_source_path"),
                "primary_file": source.get("primary_file"),
                "workspace_sha256": source.get("workspace_sha256"),
                "seed_variant_id": source.get("seed_variant_id"),
                "seed_idea_origin": source.get("seed_idea_origin"),
            }
        )
    return refs


def _evaluator_source_refs(evaluator_sources: list) -> list[dict]:
    refs = []
    for index, source in enumerate(evaluator_sources):
        if not isinstance(source, Mapping):
            continue
        refs.append(
            {
                "evaluator_index": index,
                "role": source.get("role"),
                "relative_path": source.get("relative_path"),
                "sha256": source.get("sha256"),
                "source_type": source.get("source_type"),
            }
        )
    return refs


def _prompt_variant_refs(prompt_metadata: list) -> list[dict]:
    refs = []
    for index, metadata in enumerate(prompt_metadata):
        if not isinstance(metadata, Mapping):
            continue
        refs.append(
            {
                "prompt_variant_index": index,
                "sha256": metadata.get("sha256"),
                "chars": metadata.get("chars"),
                "retention": metadata.get("retention"),
            }
        )
    return refs


def _backend_refs(backends: list) -> list[dict]:
    refs = []
    for index, backend in enumerate(backends):
        if not isinstance(backend, Mapping):
            continue
        refs.append(
            {
                "backend_index": index,
                "type": backend.get("type"),
                "model": backend.get("model"),
                "api_mode": backend.get("api_mode"),
            }
        )
    return refs


def _context_source_refs(context_sources: list) -> list[dict]:
    refs = []
    for index, source in enumerate(context_sources):
        if not isinstance(source, Mapping):
            continue
        refs.append(
            {
                "context_source_index": index,
                "path": source.get("path"),
                "sha256": source.get("sha256"),
                "source_type": source.get("source_type"),
            }
        )
    return refs


def _candidate_language_policy() -> dict:
    return {
        "schema": CANDIDATE_LANGUAGE_POLICY_SCHEMA,
        "policy": "python_primary_text_workspace_v1",
        "candidate_representation": (
            "bounded_utf8_text_workspace_with_typed_static_members"
        ),
        "primary_language": "python",
        "primary_file_policy": "python_primary_file_required_for_seed_and_best_py",
        "text_member_policy": {
            "python_files": "evolve_block_markers_supported",
            "non_python_text_files": "allowed_as_unmarked_workspace_members",
            "non_python_marker_like_declarations": "rejected_fail_closed",
        },
        "static_member_policy": {
            "encoded_static_binary": "bounded_base64_metadata",
            "verified_source_copy_static_asset": "copy_only_after_hash_and_size_check",
            "raw_binary_workspace_records": "normalized_to_static_members",
        },
        "runner_policy": {
            "validator_runner": "python_subprocess_entrypoint",
            "validator_entrypoints": "problem_local_python_files_or_packages",
            "arbitrary_language_runners": "unsupported",
            "build_system_runners": "unsupported",
            "problem_defined_solution_abstractions": "unsupported",
        },
        "alphaevolve_divergence": (
            "LibreEvolve currently evolves bounded Python-primary workspace "
            "file sets instead of arbitrary language/codebase solution objects."
        ),
        "language_runner_ready": False,
        "remaining_gap": [
            "language_or_runner_declarations_for_non_python_candidates",
            "language_aware_evolve_block_marker_grammars",
            "problem_defined_candidate_abstraction_hooks",
            "build_system_and_arbitrary_language_runner_contracts",
        ],
    }


def validate_candidate_language_policy(policy: object) -> dict:
    issues: list[dict] = []
    if not isinstance(policy, Mapping):
        return {
            "schema": CANDIDATE_LANGUAGE_POLICY_SCHEMA,
            "ok": False,
            "language_runner_ready": False,
            "issues": [
                {
                    "code": "invalid_shape",
                    "message": "candidate language policy must be an object",
                }
            ],
        }
    required = {
        "schema",
        "policy",
        "candidate_representation",
        "primary_language",
        "primary_file_policy",
        "text_member_policy",
        "static_member_policy",
        "runner_policy",
        "alphaevolve_divergence",
        "language_runner_ready",
        "remaining_gap",
    }
    missing = required - set(policy)
    if missing:
        issues.append(
            {
                "code": "missing_fields",
                "message": f"candidate language policy missing fields: {sorted(missing)}",
            }
        )
    unsupported = set(policy) - required
    if unsupported:
        issues.append(
            {
                "code": "unsupported_fields",
                "message": (
                    "candidate language policy has unsupported fields: "
                    f"{sorted(unsupported)}"
                ),
            }
        )
    _candidate_policy_issue_if(
        issues,
        policy.get("schema") != CANDIDATE_LANGUAGE_POLICY_SCHEMA,
        "invalid_schema",
        "candidate language policy schema is unsupported",
    )
    _candidate_policy_issue_if(
        issues,
        policy.get("policy") != "python_primary_text_workspace_v1",
        "invalid_policy",
        "candidate language policy must declare the Python-primary workspace policy",
    )
    _candidate_policy_issue_if(
        issues,
        policy.get("candidate_representation")
        != "bounded_utf8_text_workspace_with_typed_static_members",
        "invalid_candidate_representation",
        "candidate representation must be the bounded text workspace",
    )
    _candidate_policy_issue_if(
        issues,
        policy.get("primary_language") != "python",
        "invalid_primary_language",
        "primary_language must be python until non-Python runners exist",
    )
    _candidate_policy_issue_if(
        issues,
        policy.get("primary_file_policy")
        != "python_primary_file_required_for_seed_and_best_py",
        "invalid_primary_file_policy",
        "primary file policy must state the Python seed/best.py boundary",
    )
    text_policy = policy.get("text_member_policy")
    if not isinstance(text_policy, Mapping):
        issues.append(
            {
                "code": "invalid_text_member_policy",
                "message": "text_member_policy must be an object",
            }
        )
    else:
        expected_text = {
            "python_files": "evolve_block_markers_supported",
            "non_python_text_files": "allowed_as_unmarked_workspace_members",
            "non_python_marker_like_declarations": "rejected_fail_closed",
        }
        _candidate_policy_expected_mapping(
            issues,
            text_policy,
            expected_text,
            "text_member_policy",
        )
    static_policy = policy.get("static_member_policy")
    if not isinstance(static_policy, Mapping):
        issues.append(
            {
                "code": "invalid_static_member_policy",
                "message": "static_member_policy must be an object",
            }
        )
    else:
        expected_static = {
            "encoded_static_binary": "bounded_base64_metadata",
            "verified_source_copy_static_asset": "copy_only_after_hash_and_size_check",
            "raw_binary_workspace_records": "normalized_to_static_members",
        }
        _candidate_policy_expected_mapping(
            issues,
            static_policy,
            expected_static,
            "static_member_policy",
        )
    runner_policy = policy.get("runner_policy")
    if not isinstance(runner_policy, Mapping):
        issues.append(
            {
                "code": "invalid_runner_policy",
                "message": "runner_policy must be an object",
            }
        )
    else:
        expected_runner = {
            "validator_runner": "python_subprocess_entrypoint",
            "validator_entrypoints": "problem_local_python_files_or_packages",
            "arbitrary_language_runners": "unsupported",
            "build_system_runners": "unsupported",
            "problem_defined_solution_abstractions": "unsupported",
        }
        _candidate_policy_expected_mapping(
            issues,
            runner_policy,
            expected_runner,
            "runner_policy",
        )
        for field in (
            "arbitrary_language_runners",
            "build_system_runners",
            "problem_defined_solution_abstractions",
        ):
            if runner_policy.get(field) != "unsupported":
                issues.append(
                    {
                        "code": f"{field}_overclaim",
                        "message": f"{field} must remain unsupported in this policy",
                    }
                )
    if not isinstance(policy.get("alphaevolve_divergence"), str) or not policy[
        "alphaevolve_divergence"
    ].strip():
        issues.append(
            {
                "code": "invalid_alphaevolve_divergence",
                "message": "policy must describe the AlphaEvolve divergence",
            }
        )
    ready = policy.get("language_runner_ready")
    if ready is not False:
        issues.append(
            {
                "code": "language_runner_ready_overclaim",
                "message": "language_runner_ready must be false for this policy",
            }
        )
    required_gaps = {
        "language_or_runner_declarations_for_non_python_candidates",
        "language_aware_evolve_block_marker_grammars",
        "problem_defined_candidate_abstraction_hooks",
        "build_system_and_arbitrary_language_runner_contracts",
    }
    gaps = policy.get("remaining_gap")
    if not isinstance(gaps, list) or not all(
        isinstance(item, str) and item for item in gaps
    ):
        issues.append(
            {
                "code": "invalid_remaining_gap",
                "message": "remaining_gap must list unsupported language-runner work",
            }
        )
    elif required_gaps - set(gaps):
        issues.append(
            {
                "code": "missing_remaining_gap",
                "message": (
                    "remaining_gap must include all unsupported language-runner "
                    "boundaries"
                ),
            }
        )
    return {
        "schema": CANDIDATE_LANGUAGE_POLICY_SCHEMA,
        "ok": not issues,
        "language_runner_ready": not issues and ready is True,
        "primary_language": (
            policy.get("primary_language")
            if isinstance(policy.get("primary_language"), str)
            else None
        ),
        "issues": issues,
    }


def _candidate_policy_issue_if(
    issues: list[dict],
    condition: bool,
    code: str,
    message: str,
) -> None:
    if condition:
        issues.append({"code": code, "message": message})


def _candidate_policy_expected_mapping(
    issues: list[dict],
    value: Mapping,
    expected: dict[str, str],
    label: str,
) -> None:
    missing = set(expected) - set(value)
    if missing:
        issues.append(
            {
                "code": f"{label}_missing_fields",
                "message": f"{label} missing fields: {sorted(missing)}",
            }
        )
    unsupported = set(value) - set(expected)
    if unsupported:
        issues.append(
            {
                "code": f"{label}_unsupported_fields",
                "message": f"{label} has unsupported fields: {sorted(unsupported)}",
            }
        )
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(
                {
                    "code": f"{label}_{field}_mismatch",
                    "message": f"{label}.{field} must be {expected_value}",
                }
            )


def _validator_stdin_policy() -> dict:
    return {
        "policy": "fixture_only_validator_stdin_v1",
        "default": {
            "policy": "devnull",
            "stdin": "subprocess.DEVNULL",
            "interactive_input": "unsupported",
            "generated_input": "unsupported",
        },
        "configured_text": {
            "supported": True,
            "encoding": "utf-8",
            "max_chars": MAX_EVALUATOR_STDIN_CHARS,
            "raw_text_persisted": False,
            "metadata": [
                "policy",
                "encoding",
                "chars",
                "bytes",
                "sha256",
                "redacted",
                "text_retained",
                "max_chars",
            ],
        },
        "configured_file": {
            "supported": True,
            "scope": "problem_local_file",
            "encoding": "utf-8",
            "max_chars": MAX_EVALUATOR_STDIN_CHARS,
            "raw_path_in_manifest_config": False,
            "raw_text_persisted": False,
            "metadata": [
                "policy",
                "source",
                "path",
                "path_hash",
                "file_bytes",
                "file_sha256",
                "sha256",
                "text_retained",
                "max_chars",
            ],
        },
        "generated_input": {
            "supported": False,
            "policy": "unsupported_until_replayable_source_artifacts_exist",
        },
        "interactive_input": {
            "supported": False,
            "policy": "unsupported_non_interactive_validator_subprocesses",
        },
        "stage_overrides": "configured_stage_stdin_replaces_top_level_fixture",
        "stage_config_persistence": "stdin_text_and_stdin_file_replaced_by_hash_only_metadata",
    }


def _validator_filesystem_capabilities() -> dict:
    return {
        "schema": "libreevolve.validator_filesystem_capabilities.v1",
        "policy": "candidate_root_plus_declared_problem_files",
        "enforcement": "python_runner_problem_local_provenance_checks",
        "cwd": {
            "path": "materialized_candidate_root",
            "read": True,
            "write": True,
            "execute": True,
            "lifetime": "temporary_per_attempt",
        },
        "candidate_workspace": {
            "scope": "materialized_candidate_files",
            "read": True,
            "write": True,
            "execute": True,
            "host_filesystem_sandbox": "unsupported",
        },
        "declared_problem_files": {
            "scope": "entrypoint_companion_data_and_stdin_provenance",
            "read": True,
            "write": False,
            "execute": True,
            "undeclared_problem_local_reads": "python_open_and_import_checks_denied",
        },
        "evaluator_artifacts": {
            "write": "bounded_include_globs",
            "copy_out": "hashed_redacted_optional",
            "symlink_policy": "link_metadata_not_unbounded_follow",
        },
        "host_filesystem": {
            "os_sandbox": "unsupported",
            "ambient_access_possible": True,
            "undeclared_host_paths": "not_capability_enforced",
        },
    }


def _validator_resource_limit_policy() -> dict:
    return {
        "schema": "libreevolve.validator_resource_limit_policy.v1",
        "policy": "wall_clock_timeout_only",
        "enforcement": "local_subprocess_timeout_cleanup",
        "wall_clock_timeout": {
            "supported": True,
            "source": "configured_stage_or_sample_timeout",
            "cleanup": "process_group_or_windows_job_object_plus_tree_kill",
        },
        "cpu": {"supported": False, "quota": "unsupported"},
        "memory": {"supported": False, "quota": "unsupported"},
        "gpu": {"supported": False, "quota": "unsupported"},
        "disk": {"supported": False, "quota": "unsupported"},
        "process_count": {"supported": False, "quota": "unsupported"},
        "container_runtime_limits": "unsupported",
        "remaining_gap": (
            "CPU/memory/GPU/disk/process quotas require an external sandbox "
            "or worker runtime"
        ),
    }


def _validator_network_boundary(configured_network_policy: str) -> dict:
    configured_network_policy = _validate_validator_network_policy(
        configured_network_policy
    )
    if configured_network_policy == "deny":
        return {
            "network_policy": configured_network_policy,
            "network_egress": "python_socket_denied_not_os_sandbox",
            "network_denial": "python_socket_monkeypatch",
        }
    return {
        "network_policy": configured_network_policy,
        "network_egress": "host_inherited_not_sandboxed",
        "network_denial": "unsupported",
    }


def _validator_execution_policy(configured_network_policy: str) -> dict:
    network = _validator_network_boundary(configured_network_policy)
    return {
        "schema": "libreevolve.validator_execution_policy.v1",
        "policy": "local_subprocess_boundary_v1",
        "execution": "temporary_local_subprocess",
        "security_sandbox": "unsupported",
        "container": "unsupported",
        "filesystem_capability_model": (
            "candidate_root_plus_declared_problem_files"
        ),
        "filesystem_scope": {
            "cwd": "materialized_candidate_root",
            "candidate_files": "materialized_under_temporary_candidate_root",
            "problem_local_files": (
                "declared_entrypoint_companion_and_data_provenance_only"
            ),
            "host_filesystem_sandbox": "unsupported",
        },
        "filesystem_capabilities": _validator_filesystem_capabilities(),
        "network_policy": network["network_policy"],
        "network_egress": network["network_egress"],
        "network_denial": network["network_denial"],
        "network_denial_scope": "python_socket_api_only_not_kernel_or_container",
        "resource_limits": {
            "wall_clock_timeout": "configured_stage_or_sample_timeout",
            "cpu": "unsupported",
            "memory": "unsupported",
            "gpu": "unsupported",
            "disk": "unsupported",
            "process_count": "unsupported",
        },
        "resource_limit_policy": _validator_resource_limit_policy(),
        "secret_boundary": "minimal_environment_allowlist_with_redacted_diagnostics",
        "startup_manifest_only": True,
        "per_evaluation_metadata": "evaluation.metadata.validator_boundary",
        "boundary_consistency_validator": (
            "validate_validator_boundary_consistency.v1"
        ),
        "boundary_consistency_fields": [
            "policy",
            "execution",
            "security_sandbox",
            "container",
            "filesystem_capability_model",
            "filesystem_capabilities",
            "network_policy",
            "network_egress",
            "network_denial",
            "network_denial_scope",
            "resource_limits",
            "resource_limit_policy",
            "secret_boundary",
        ],
        "remaining_gap": (
            "configurable sandbox/container enforcement, OS filesystem "
            "capabilities, CPU/memory/GPU/disk/process quotas, and distributed "
            "worker state"
        ),
    }


def _validator_network_policy(configured_policy: str) -> dict:
    configured_policy = _validate_validator_network_policy(configured_policy)
    if configured_policy == "deny":
        network_egress = "python_socket_denied_not_os_sandbox"
        network_denial = "python_socket_monkeypatch"
    else:
        network_egress = "host_inherited_not_sandboxed"
        network_denial = "unsupported"
    return {
        "schema": "libreevolve.validator_network_policy.v1",
        "configured_policy": configured_policy,
        "allowed_policies": ["host", "deny"],
        "network_egress": network_egress,
        "network_denial": network_denial,
        "network_denial_scope": "python_socket_api_only_not_kernel_or_container",
        "applies_to": ["validator_preflight_subprocess", "validator_evaluation_subprocess"],
        "os_container_network_sandbox": "unsupported",
        "native_extension_or_child_process_denial": "unsupported",
        "provider_secret_boundary": (
            "validator_env_allowlist_controls_environment_values; "
            "diagnostics_and_artifacts_use_redaction_policy"
        ),
        "remaining_gap": (
            "OS/container-grade validator network egress isolation and "
            "network-mediated secret-boundary audit"
        ),
    }


def _manifest_eval_stages(stages: list[dict]) -> list[dict]:
    manifest_stages: list[dict] = []
    for stage in stages:
        manifest_stage = copy.deepcopy(stage)
        stdin_text = manifest_stage.pop("stdin_text", None)
        stdin_file = manifest_stage.pop("stdin_file", None)
        if stdin_text is not None or stdin_file is not None:
            manifest_stage["stdin"] = _manifest_evaluator_stdin_config(
                stdin_text,
                stdin_file,
            )
        manifest_stages.append(manifest_stage)
    return manifest_stages


def _manifest_evaluator_stdin_config(
    stdin_text: object,
    stdin_file: object,
) -> dict:
    if stdin_text is not None:
        text = str(stdin_text)
        raw = text.encode("utf-8")
        redacted = redact_sensitive_text(text)
        return {
            "policy": "configured_text",
            "encoding": "utf-8",
            "chars": len(text),
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "redacted": redacted != text,
            "text_retained": False,
            "max_chars": MAX_EVALUATOR_STDIN_CHARS,
        }
    if stdin_file is not None:
        raw_path = str(stdin_file)
        return {
            "policy": "configured_file",
            "source": "problem_local_file",
            "configured_path_sha256": hashlib.sha256(
                raw_path.encode("utf-8", errors="replace")
            ).hexdigest(),
            "path_retained": False,
            "text_retained": False,
            "max_chars": MAX_EVALUATOR_STDIN_CHARS,
        }
    return {
        "policy": "devnull",
        "interactive_input": "unsupported",
        "generated_input": "unsupported",
    }


def _archive_cursor_restore_policy(restore_result: dict | None) -> dict:
    if restore_result is None:
        return {
            "policy": "compact_island_cursor_restore",
            "status": "not_requested",
            "archive_contents_restored": False,
            "full_archive_restore_required": True,
        }
    return {
        "policy": "compact_island_cursor_restore",
        "status": restore_result["status"],
        "archive_contents_restored": restore_result["archive_contents_restored"],
        "full_archive_restore_required": restore_result[
            "full_archive_restore_required"
        ],
        "next_island_id": restore_result["next_island_id"],
        "archive_sequence": restore_result["archive_sequence"],
        "migration_sequence": restore_result["migration_sequence"],
        "metric_sample_index": restore_result["metric_sample_index"],
        "frontier_sample_index": restore_result["frontier_sample_index"],
        "lineage_sample_index": restore_result["lineage_sample_index"],
        "archive_sequence_by_program_id": restore_result[
            "archive_sequence_by_program_id"
        ],
        **(
            {"restored_islands": restore_result["restored_islands"]}
            if "restored_islands" in restore_result
            else {}
        ),
    }


_MANIFEST_PROMPT_CONFIG_MAX_CHARS = 4000


def _prompt_data_retention_policy(config: Config) -> dict:
    return {
        "schema": "libreevolve.prompt_data_retention.v1",
        "policy": "mixed_configurable_and_fixed_bounded_prompt_retention",
        "redaction_policy": "libreevolve.redaction.v2",
        "surfaces": {
            "mutation_prompt": {
                "retention_mode": config.mutation_prompt_retention_mode,
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_original_rendered_prompt_when_policy_allows",
                "default": "redacted",
            },
            "explicit_context_text": {
                "retention_mode": config.explicit_context_retention_mode,
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_original_rendered_context_when_policy_allows",
                "default": "redacted",
                "note": "applies to explicit context spans inside persisted rendered mutation prompts",
            },
            "critique_prompt": {
                "retention_mode": config.critique_retention_mode,
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_original_prompt",
                "max_retained_chars": 6000,
            },
            "critique_mutation_text": {
                "retention_mode": config.critique_retention_mode,
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_original_text",
                "max_retained_chars": 4000,
            },
            "feedback_raw_response": {
                "retention_mode": config.feedback_retention_mode,
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_original_response",
            },
            "feedback_parsed_fields": {
                "retention_mode": config.feedback_retention_mode,
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_original_field_text",
            },
            "failure_memory_llm_feedback": {
                "retention_mode": config.feedback_retention_mode,
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_original_field_text",
                "max_retained_chars": 500,
                "note": (
                    "failure_history evaluation summaries retain selected "
                    "bounded LLM-grader fields for prompt-visible failure memory"
                ),
            },
            "validator_artifact_content": {
                "retention_mode": config.prompt_artifact_content_mode,
                "configurable": True,
                "modes": ["excerpt", "bounded_file", "off"],
                "hash": "sha256_of_stored_artifact_bytes",
                "max_read_bytes": config.prompt_artifact_content_max_bytes,
                "max_rendered_chars": config.prompt_artifact_content_max_chars,
                "path_policy": "run_local_relative_artifact_paths_only",
                "note": (
                    "bounded_file reopens copied UTF-8 evaluator artifacts "
                    "under the run directory for prompt feedback rendering"
                ),
            },
            "llm_call_prompt_text": {
                "retention_mode": "hash_and_char_counts_only",
                "configurable": False,
                "hash": "sha256_of_prompt",
            },
            "llm_call_output_text": {
                "retention_mode": config.provider_response_retention_mode,
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_output_on_success_also_retained_as_call_telemetry",
            },
            "provider_error_text": {
                "retention_mode": config.provider_error_retention_mode,
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_original_error_text_when_policy_allows",
                "max_retained_chars": 500,
            },
            "plugin_context_text": {
                "retention_mode": config.plugin_context_retention_mode,
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_original_rendered_plugin_context_when_policy_allows",
                "max_retained_chars": 4000,
                "note": "mutation_prompt_retention_mode separately controls persisted rendered prompts that may include plugin context",
            },
            "meta_prompt_evidence": {
                "retention_mode": config.meta_prompt_evidence_retention_mode,
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_original_evidence_json_when_policy_allows",
                "max_retained_chars": 1000,
                "note": "provider-visible meta-prompt evidence remains redacted and bounded separately",
            },
            "deep_research_retrieval_bodies": {
                "retention_mode": "plugin_option:retrieval_body_retention_mode",
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_original_retrieval_body_when_policy_allows",
                "default": "redacted",
                "note": "selected mode is recorded in runtime.plugin_state.loaded_specs for DeepResearchPlugin instances",
            },
            "quarantine_record_snapshots": {
                "retention_mode": config.quarantine_snapshot_retention_mode,
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_original_record_repr_or_fragment_when_policy_allows",
                "default": "redacted",
                "max_retained_chars": 4000,
                "note": "applies to framework-owned *_invalid.jsonl record_repr snapshots and torn JSONL fragment previews",
            },
            "prompt_config": {
                "retention_mode": "redacted_bounded",
                "configurable": False,
                "hash": "sha256_of_original_text",
                "max_retained_chars": _MANIFEST_PROMPT_CONFIG_MAX_CHARS,
            },
        },
        "remaining_gap": [
            "replay retention policy for restored historical prompt-bearing artifacts",
        ],
    }


def _manifest_prompt_text(value: object) -> dict:
    if not isinstance(value, str):
        return {
            "value": value,
            "metadata": {
                "retention": "non_text_value",
                "type": type(value).__name__,
            },
        }
    redacted = redact_sensitive_text(value)
    truncated = len(redacted) > _MANIFEST_PROMPT_CONFIG_MAX_CHARS
    retained = (
        redacted[: _MANIFEST_PROMPT_CONFIG_MAX_CHARS - 15] + "...<truncated>"
        if truncated
        else redacted
    )
    return {
        "value": retained,
        "metadata": {
            "retention": "redacted_truncated_with_hash",
            "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
            "chars": len(value),
            "retained_chars": len(retained),
            "redacted": redacted != value,
            "truncated": truncated,
        },
    }


def _manifest_prompt_text_list(values: list[str]) -> dict:
    sanitized = [_manifest_prompt_text(value) for value in values]
    return {
        "values": [item["value"] for item in sanitized],
        "metadata": [item["metadata"] for item in sanitized],
    }


def _manifest_prompt_format_options(options: dict) -> dict:
    sanitized_values: dict = {}
    sanitized_metadata: dict = {}
    for name, alternatives in options.items():
        sanitized_values[name] = []
        sanitized_metadata[name] = []
        for alternative in alternatives:
            if isinstance(alternative, dict):
                sanitized = dict(alternative)
                text = _manifest_prompt_text(sanitized.get("text"))
                sanitized["text"] = text["value"]
                sanitized_values[name].append(sanitized)
                sanitized_metadata[name].append(text["metadata"])
            else:
                text = _manifest_prompt_text(alternative)
                sanitized_values[name].append(text["value"])
                sanitized_metadata[name].append(text["metadata"])
    return {"values": sanitized_values, "metadata": sanitized_metadata}


def _manifest_prompt_roles(roles: dict) -> dict:
    sanitized_values: dict = {}
    sanitized_metadata: dict = {}
    for role, spec in roles.items():
        sanitized_values[role] = {}
        sanitized_metadata[role] = {}
        for field_name, text_value in spec.items():
            text = _manifest_prompt_text(text_value)
            sanitized_values[role][field_name] = text["value"]
            sanitized_metadata[role][field_name] = text["metadata"]
    return {"values": sanitized_values, "metadata": sanitized_metadata}


def _manifest_llm_feedback(graders: list[dict]) -> dict:
    sanitized_values = []
    sanitized_metadata = []
    for grader in graders:
        sanitized = dict(grader)
        metadata = {}
        if "prompt" in sanitized:
            prompt = _manifest_prompt_text(sanitized["prompt"])
            sanitized["prompt"] = prompt["value"]
            metadata["prompt"] = prompt["metadata"]
        sanitized_values.append(sanitized)
        sanitized_metadata.append(metadata)
    return {"values": sanitized_values, "metadata": sanitized_metadata}


def _openai_api_mode_manifest_policy(backends: list[dict]) -> dict:
    records: list[dict] = []
    for index, backend in enumerate(backends):
        if not isinstance(backend, dict) or backend.get("type") != "openai":
            continue
        configured = backend.get("api_mode", "auto")
        reasoning_effort = backend.get("reasoning_effort")
        records.append(
            {
                "backend_index": index,
                "model": backend.get("model"),
                "configured_api_mode": configured,
                "effective_api_mode": resolve_openai_api_mode(
                    configured,
                    reasoning_effort=reasoning_effort,
                    field=f"backends[{index}].api_mode",
                ),
                "reasoning_effort_configured": reasoning_effort is not None,
                "reasoning_effort": reasoning_effort,
                "auto_policy": (
                    "responses_when_reasoning_effort_is_configured_else_chat_completions"
                ),
            }
        )
    return {
        "policy": "explicit_or_auto_openai_api_mode",
        "auto_policy": "responses_when_reasoning_effort_is_configured_else_chat_completions",
        "records": records,
    }


def _provider_capability_lookup_policy(backends: list[dict]) -> dict:
    records: list[dict] = []
    for index, backend in enumerate(backends):
        if not isinstance(backend, dict):
            continue
        provider = backend.get("type")
        record = {
            "backend_index": index,
            "provider": provider,
            "model": backend.get("model"),
            "live_model_registry_lookup": False,
            "provider_service_api_version_lookup": False,
            "provider_account_availability_check": False,
            "offline_compatible": True,
            "local_validation": [
                "backend_type_and_supported_key_schema",
                "manifest_safe_model_identifier",
                "manifest_safe_client_context_fields",
            ],
        }
        if provider == "openai":
            record["local_validation"].extend(
                [
                    "openai_api_mode_enum_and_reasoning_effort_route",
                    "openai_model_family_reasoning_effort_static_compatibility",
                ]
            )
            record["api_mode_policy_ref"] = "policies.openai_api_mode"
        records.append(record)
    records_payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return {
        "schema": "libreevolve.provider_capability_lookup_policy.v1",
        "policy": "local_static_validation_no_live_provider_lookup",
        "live_lookup": "unsupported",
        "offline_operation": "supported",
        "network_calls_before_run": "none_for_capability_discovery",
        "provider_model_registry": "not_queried",
        "provider_service_api_version": "not_queried",
        "provider_account_availability": "not_checked",
        "record_count": len(records),
        "records_sha256": hashlib.sha256(records_payload.encode("utf-8")).hexdigest(),
        "records": records,
        "remaining_gap": (
            "live provider model registry, service API-version, account "
            "availability, and capability evidence"
        ),
    }


def _manifest_log_dir(log_dir: str) -> dict:
    raw = str(log_dir)
    redacted = redact_sensitive_text(raw)
    is_absolute = Path(raw).is_absolute()
    if is_absolute:
        value = "<absolute-log-dir>"
        reason = "absolute_path"
    elif redacted != raw:
        value = redacted
        reason = "sensitive_pattern"
    else:
        value = raw
        reason = "as_configured"
    return {
        "value": value,
        "metadata": {
            "retention_policy": "relative_or_redacted_with_sha256",
            "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "is_absolute": is_absolute,
            "redacted": value != raw,
            "reason": reason,
        },
    }


def prepare_run_directory(run_dir: Path, policy: str) -> None:
    existing = sorted(
        name for name in RUN_ARTIFACT_NAMES if _cleanup_target_exists(run_dir / name)
    )
    if not existing:
        return
    if policy == "overwrite":
        linked = [name for name in existing if _is_link(run_dir / name)]
        if linked:
            raise ValueError(
                "Run directory contains linked run artifacts "
                f"{linked}; {_run_path_display('run_dir', run_dir)}; "
                "replace linked artifacts manually before using overwrite"
            )
        for name in existing:
            path = run_dir / name
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        return
    raise FileExistsError(
        "Run directory already contains run artifacts "
        f"{existing}; {_run_path_display('run_dir', run_dir)}; "
        "use --overwrite or set run_collision_policy: overwrite"
    )


def _cleanup_target_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (is_junction is not None and is_junction())


def _foreign_run_directory_entries(run_dir: Path) -> list[dict]:
    if not run_dir.is_dir():
        return []
    records = []
    try:
        entries = sorted(run_dir.iterdir(), key=lambda p: p.name)
    except OSError as exc:
        return [
            {
                "status": "unreadable",
                "type": "unknown",
                "policy": "preserved_unlisted",
                "error_type": exc.__class__.__name__,
                "error": redact_sensitive_text(str(exc)),
            }
        ]
    for path in entries:
        if path.name in RUN_ARTIFACT_NAMES:
            continue
        records.append(
            {
                "status": "present",
                "name_sha256": hashlib.sha256(path.name.encode("utf-8")).hexdigest(),
                "type": _entry_type(path),
                "policy": "preserved",
            }
        )
    return records


def _entry_type(path: Path) -> str:
    if _is_link(path):
        return "link"
    if path.is_dir():
        return "directory"
    if path.is_file():
        return "file"
    return "other"


def validate_run_directory_path(log_root: Path, run_dir: Path) -> None:
    """Reject run directories that resolve outside the configured log root."""
    resolved_root = Path(log_root).resolve(strict=False)
    resolved_run = Path(run_dir).resolve(strict=False)
    try:
        resolved_run.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(
            "Run directory resolves outside log_dir: "
            f"{_run_path_display('run_dir', run_dir, resolved_root)}; "
            f"{_run_path_display('resolved_run', resolved_run, resolved_root)}; "
            f"{_run_path_display('log_dir', log_root)}"
        ) from exc


def _run_path_display(label: str, path: Path, base: Path | None = None) -> str:
    raw = str(path)
    resolved = Path(path).resolve(strict=False)
    display = _safe_path_label(path, resolved, base)
    digest = hashlib.sha256(str(resolved).encode("utf-8")).hexdigest()[:16]
    redacted = display != raw
    return f"{label}={display} (path_hash={digest}, path_redacted={redacted})"


def _safe_path_label(path: Path, resolved: Path, base: Path | None) -> str:
    if base is not None:
        try:
            return resolved.relative_to(base).as_posix() or "."
        except ValueError:
            pass
    raw = str(path)
    if Path(raw).is_absolute():
        name = redact_sensitive_text(Path(raw).name) or "<unnamed>"
        return f"<absolute>/{name}"
    redacted = redact_sensitive_text(raw)
    return redacted if redacted else "<empty-path>"


def _changed_files(parent: Program, child: Program) -> list[str]:
    parent_files = parent.workspace().files
    child_files = child.workspace().files
    paths = sorted(set(parent_files) | set(child_files))
    return [path for path in paths if parent_files.get(path) != child_files.get(path)]


def _file_deltas(parent: Program, child: Program) -> list[dict]:
    parent_files = parent.workspace().files
    child_files = child.workspace().files
    deltas = []
    for path in sorted(set(parent_files) | set(child_files)):
        if path not in parent_files:
            change = "added"
        elif path not in child_files:
            change = "deleted"
        elif parent_files[path] != child_files[path]:
            change = "modified"
        else:
            continue
        deltas.append({"path": path, "change": change})
    return deltas


def _failure_fingerprint(
    *,
    record_type: str,
    parent_id: str | None,
    diff_error: object,
    evaluator_error: object,
    mutation_payload: dict,
    changed_files: list[str],
    file_deltas: list[dict],
) -> dict:
    components = {
        "schema": "failure_fingerprint_v1",
        "record_type": record_type,
        "parent_id": parent_id,
        "diff_error_sha256": _failure_value_sha256(diff_error),
        "evaluator_error_sha256": _failure_value_sha256(evaluator_error),
        "mutation_sha256": mutation_payload["sha256"],
        "mutation_payload_type": mutation_payload.get("type", record_type),
        "mutation_payload_text": mutation_payload.get("is_text", True),
        "changed_files": list(changed_files),
        "file_deltas_sha256": _failure_value_sha256(file_deltas),
    }
    fingerprint_json = json.dumps(
        components,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    return {
        **components,
        "sha256": hashlib.sha256(fingerprint_json.encode("utf-8")).hexdigest(),
    }


def _failure_value_sha256(value: object) -> str:
    text = _failure_hash_text(value)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _failure_hash_text(value: object) -> str:
    if value is None:
        return "<none>"
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))
    except (TypeError, ValueError):
        return _safe_failure_repr(value)


def _failure_evaluation_summary(
    program: Program, *, normalize_non_finite: bool = False
) -> dict:
    evaluation = program.evaluation or {}
    fitness, fitness_diagnostic = _failure_record_number(
        evaluation.get("fitness", program.fitness),
        normalize=normalize_non_finite,
    )
    summary = {
        "fitness": fitness,
        "is_valid": evaluation.get("is_valid"),
        "error": _failure_optional_text(evaluation.get("error"), 1000),
        "stdout": _failure_text(str(evaluation.get("stdout", "")), 1000),
        "stderr": _failure_text(str(evaluation.get("stderr", "")), 1000),
        "stages": [],
    }
    if fitness_diagnostic is not None:
        summary["fitness_diagnostic"] = fitness_diagnostic
    stages, diagnostic = _failure_stage_summaries(
        evaluation.get("stages", []),
        normalize_non_finite=normalize_non_finite,
    )
    summary["stages"] = stages
    metadata = evaluation.get("metadata")
    llm_feedback = _failure_llm_feedback_summaries(
        metadata.get("llm_feedback") if isinstance(metadata, dict) else None,
        normalize_non_finite=normalize_non_finite,
    )
    if llm_feedback:
        summary["llm_feedback"] = llm_feedback
    if diagnostic is not None:
        summary["stages_diagnostic"] = diagnostic
    return summary


def _failure_llm_feedback_summaries(
    records: object, *, normalize_non_finite: bool = False
) -> list[dict]:
    if not isinstance(records, list):
        return []
    summaries: list[dict] = []
    for record in records[:5]:
        if not isinstance(record, dict):
            continue
        summary: dict = {}
        for field, max_chars in (
            ("name", 120),
            ("metric", 120),
            ("error", 200),
            ("message", 300),
            ("feedback", 500),
            ("raw_response", 500),
        ):
            value = _failure_optional_text(record.get(field), max_chars)
            if value is not None:
                summary[field] = value
        for field in ("score", "normalized_score", "weighted_delta", "failure_delta"):
            value, diagnostic = _failure_record_number(
                record.get(field),
                normalize=normalize_non_finite,
            )
            if value is not None:
                summary[field] = value
            if diagnostic is not None:
                summary[f"{field}_diagnostic"] = diagnostic
        for field in ("discard", "backend_idx", "attempts", "failure_attempts"):
            value = record.get(field)
            if isinstance(value, bool | int):
                summary[field] = value
        retention = _failure_llm_feedback_retention_summary(record)
        if retention:
            summary["retention"] = retention
        llm_call = _failure_llm_call_summary(record.get("llm_call"))
        if llm_call:
            summary["llm_call"] = llm_call
        if summary:
            summaries.append(summary)
    if len(records) > 5:
        summaries.append({"omitted": len(records) - 5})
    return summaries


def _failure_llm_feedback_retention_summary(record: dict) -> dict:
    summary: dict = {}
    for field in ("feedback_retention", "raw_response_retention"):
        retention = record.get(field)
        if not isinstance(retention, dict):
            continue
        value: dict = {}
        for key in ("retention_mode", "sha256", "chars", "stored_chars"):
            retained = retention.get(key)
            if isinstance(retained, str):
                safe = _failure_optional_text(retained, 120)
                if safe is not None:
                    value[key] = safe
            elif isinstance(retained, int) and not isinstance(retained, bool):
                value[key] = retained
        if value:
            summary[field] = value
    return summary


def _failure_llm_call_summary(record: object) -> dict:
    if not isinstance(record, dict):
        return {}
    summary: dict = {}
    for field, max_chars in (
        ("id", 120),
        ("call_id", 120),
        ("role", 80),
        ("backend", 120),
        ("backend_name", 120),
        ("provider", 80),
        ("model", 120),
        ("status", 80),
        ("finish_reason", 80),
        ("error", 200),
        ("provider_failure_category", 80),
    ):
        value = _failure_optional_text(record.get(field), max_chars)
        if value is not None:
            summary[field] = value
    for field in (
        "backend_idx",
        "attempt_index",
        "provider_attempts",
        "prompt_chars",
        "output_chars",
        "total_tokens",
        "cost_microusd",
    ):
        value = record.get(field)
        if isinstance(value, int) and not isinstance(value, bool):
            summary[field] = value
    latency = record.get("latency_sec")
    if isinstance(latency, (int, float)) and not isinstance(latency, bool):
        value, diagnostic = _failure_record_number(latency, normalize=False)
        if value is not None:
            summary["latency_sec"] = value
        if diagnostic is not None:
            summary["latency_sec_diagnostic"] = diagnostic
    return summary


def _failure_program_llm_summary(program: Program) -> dict:
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    summary: dict = {}
    backend_idx = metadata.get("backend_idx")
    if isinstance(backend_idx, int) and not isinstance(backend_idx, bool):
        summary["backend_idx"] = backend_idx
    llm_calls = metadata.get("llm_calls")
    if isinstance(llm_calls, list):
        calls = []
        for call in llm_calls[:5]:
            call_summary = _failure_llm_call_summary(call)
            if call_summary:
                calls.append(call_summary)
        if calls:
            summary["calls"] = calls
            summary["call_count"] = len(llm_calls)
            summary["calls_truncated"] = len(llm_calls) > len(calls)
    llm_failure = metadata.get("llm_failure")
    if isinstance(llm_failure, dict):
        failure_call = _failure_llm_call_summary(llm_failure.get("llm_call"))
        if failure_call:
            summary["failure_call"] = failure_call
    return summary


def _failure_stage_summaries(
    raw_stages: object, *, normalize_non_finite: bool = False
) -> tuple[list[dict], dict | None]:
    if raw_stages is None:
        return [], None
    if not isinstance(raw_stages, list):
        return [], {
            "reason": "malformed_stages",
            "expected": "list",
            "actual_type": type(raw_stages).__name__,
        }
    stages: list[dict] = []
    skipped = 0
    for stage in raw_stages[-3:]:
        if not isinstance(stage, dict):
            skipped += 1
            continue
        score, score_diagnostic = _failure_record_number(
            stage.get("score"),
            normalize=normalize_non_finite,
        )
        stage_summary = {
            "name": stage.get("name"),
            "passed": stage.get("passed"),
            "score": score,
            "error": _failure_optional_text(stage.get("error"), 500),
        }
        if score_diagnostic is not None:
            stage_summary["score_diagnostic"] = score_diagnostic
        stages.append(stage_summary)
    diagnostic = None
    if skipped:
        diagnostic = {
            "reason": "malformed_stage_entries",
            "skipped_count": skipped,
        }
    return stages, diagnostic


def _failure_record_number(
    value: object, *, normalize: bool
) -> tuple[object, dict | None]:
    if _is_finite_real(value) or not normalize:
        return value, None
    return None, {
        "reason": "non_finite_or_invalid_number",
        "value_type": type(value).__name__,
        "value_repr": _failure_optional_text(repr(value), 200),
    }


def _truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    notice = f"\n[truncated {len(text) - max_chars} chars]"
    keep = max(0, max_chars - len(notice))
    return text[:keep] + notice


def _failure_text(text: str, max_chars: int) -> str:
    return _truncate_text(redact_sensitive_text(text), max_chars)


def _seed_failure_payload(program: Program) -> dict:
    workspace = program.workspace()
    sections = [
        "[initial seed workspace]",
        f"primary_file: {workspace.primary_file}",
        f"file_count: {len(workspace.files)}",
    ]
    files = []
    for path in sorted(workspace.files):
        content = workspace.files[path]
        role = "primary" if path == workspace.primary_file else "support"
        sections.extend(
            [
                f"--- {path} ({role}) ---",
                content,
            ]
        )
        files.append(
            {
                "path": path,
                "role": role,
                "bytes": len(content.encode("utf-8")),
                "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "snippet": _failure_text(content, 1000),
                "snippet_truncated": len(content) > 1000,
            }
        )
    text = "\n".join(sections)
    return {
        "text": text,
        "safe_text": _failure_text(text, 4000),
        "truncated": len(text) > 4000,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "workspace": {
            "primary_file": workspace.primary_file,
            "file_count": len(files),
            "files": files,
        },
    }


def _failure_mutation_payload(value: object) -> dict:
    if isinstance(value, str):
        text = value
        payload_type = "str"
        is_text = True
    else:
        text = _safe_failure_repr(value)
        payload_type = type(value).__name__
        is_text = False
    safe_text = _failure_text(text, 4000)
    return {
        "text": text,
        "safe_text": safe_text,
        "truncated": len(text) > 4000,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "type": payload_type,
        "is_text": is_text,
    }


def _safe_failure_repr(value: object) -> str:
    try:
        return repr(value)
    except Exception as exc:  # pragma: no cover - caller-controlled repr failure
        return f"<repr failed: {exc.__class__.__name__}>"


def _failure_optional_text(value: object, max_chars: int) -> str | None:
    if value is None:
        return None
    return _failure_text(str(value), max_chars)


def _failure_optional_json_text(value: object, max_chars: int) -> object:
    if value is None:
        return None
    if isinstance(value, str):
        return _failure_text(value, max_chars)
    return value
