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
from libreevolve.core.artifact_schema import ARCHIVE_EVENT_RECORD_SCHEMA, ARTIFACT_SCHEMA_VERSION, FAILURE_RECORD_SCHEMA, HISTORY_RECORD_SCHEMA, LLM_CALL_RECORD_SCHEMA, LLM_REWARD_RECORD_SCHEMA, RUN_ARTIFACT_NAMES, run_artifact_schema, versioned_record
from libreevolve.core.budget import (
    CONTROLLER_BUDGET_EVENT_SCHEMA,
    validate_controller_budget_event,
)
from libreevolve.core.config import Config, MAX_EVALUATOR_STDIN_CHARS, _validate_validator_network_policy
from libreevolve.core.candidate import (
    normalize_candidate_path,
    validate_candidate_workspace_limits,
)
from libreevolve.core.jsonl import StrictJsonlError, append_quarantine_record, append_strict_jsonl, iter_strict_jsonl_objects, strict_json_dump, strict_json_text_for_path
from libreevolve.core.redaction import redact_sensitive_text, redaction_policy_record
from libreevolve.population.map_elites import _selection_score
from libreevolve.population.islands import (
    ISLAND_ARCHIVE_CONTENTS_RESTORE_STATUS,
    ISLAND_MIGRATION_REPLAY_POLICY,
    ISLAND_MIGRATION_REPLAY_SCHEMA,
    ISLAND_MIGRATION_REPLAY_STATUS,
    ISLAND_STATE_ACCEPTED_RESUME_STATUSES,
    IslandModel,
    validate_island_topology_policy,
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

_MAX_CONTEXT_PROVENANCE_STRING_CHARS = 4096
_MAX_CONTEXT_PROVENANCE_ITEMS = 5000
_MAX_CONTEXT_PROVENANCE_DEPTH = 30
_MAX_CONTEXT_PROVENANCE_JSON_CHARS = 200_000
_MAX_SEED_SOURCE_STRING_CHARS = 1024
_MAX_FAILURE_INDEX_FINGERPRINTS = 50
_MAX_FAILURE_INDEX_RECORDS_PER_FINGERPRINT = 5
CANDIDATE_LANGUAGE_POLICY_SCHEMA = "libreevolve.candidate_language_policy.v1"
_SEED_SOURCE_ALLOWED_KEYS = {
    "seed_index",
    "seed_source_path",
    "seed_source_kind",
    "primary_file",
    "file_count",
    "files",
    "static_file_count",
    "static_files",
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
        self._logged_programs_by_id: dict[str, Program] = {}
        self._archive_ids: set[str] = set()
        self._failure_counts: dict[str, int] = {}
        self._controller_budget_event_sequence: int = 0
        self._llm_call_sequence: int = 0
        self._archive_admission_event_sequence: int = 0
        self._workspace_limits = _candidate_workspace_limits_from_config(config)
        self._write_manifest(startup_manifest)

    def add(self, program: Program, threshold: float = 0.0) -> dict:
        return self.admit(program, threshold=threshold)

    def objective_schema_snapshot(self) -> dict:
        return copy.deepcopy(self._objective_schema)


    def log_llm_call(self, record: dict) -> dict:
        normalized = {"record_type": "call", **record}
        record_type = normalized.get("record_type")
        if record_type != "reward":
            producer_sequence = normalized.get("sequence_id")
            next_sequence = self._llm_call_sequence + 1
            normalized["stream_sequence_id"] = next_sequence
            if normalized.get("producer_id") is not None:
                normalized.setdefault("producer_sequence_id", producer_sequence)
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
        if record_type != "reward":
            self._llm_call_sequence += 1
        return copy.deepcopy(normalized)

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
        self._log_archive_admission_event(program, event)
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
        mutation_mode = program.metadata.get("mutation_mode")
        if isinstance(mutation_mode, str) and mutation_mode:
            record["mutation_mode"] = mutation_mode
        mutation_mode_selection = program.metadata.get("mutation_mode_selection")
        if isinstance(mutation_mode_selection, Mapping):
            record["mutation_mode_selection"] = copy.deepcopy(
                dict(mutation_mode_selection)
            )
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
        program.metadata = validate_program_metadata(program.metadata)
        program.metadata["failure_record"] = record
        return record


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


    def failure_index_snapshot(self) -> dict:
        return _failure_index_snapshot(
            self._failure_records,
            fingerprint_limit=_MAX_FAILURE_INDEX_FINGERPRINTS,
            records_per_fingerprint_limit=_MAX_FAILURE_INDEX_RECORDS_PER_FINGERPRINT,
        )


    def _log_archive_event(self, event: dict) -> None:
        append_strict_jsonl(
            self._archive_events,
            versioned_record(ARCHIVE_EVENT_RECORD_SCHEMA, event),
            quarantine_path=self._archive_event_quarantine,
            quarantine_snapshot_retention_mode=self._quarantine_snapshot_retention_mode,
        )

    def _log_archive_admission_event(self, program: Program, event: Mapping[str, object]) -> None:
        self._archive_admission_event_sequence += 1
        self._log_archive_event(
            _archive_admission_event_record(
                program,
                event,
                admission_sequence=self._archive_admission_event_sequence,
            )
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
        "topology_policy",
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
    topology_policy = _validate_archive_topology_policy(
        snapshot.get("topology_policy"),
        n_islands,
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
        "topology_policy": topology_policy,
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


def _validate_archive_topology_policy(value: object, n_islands: int) -> dict:
    try:
        return validate_island_topology_policy(value, n_islands)
    except ValueError as exc:
        raise ArchiveStateRestoreError(
            f"archive state snapshot topology_policy {exc}"
        ) from exc


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


def _archive_admission_event_record(
    program: Program,
    event: Mapping[str, object],
    *,
    admission_sequence: int,
) -> dict:
    record: dict[str, object] = {
        "event_type": "admission",
        "admission_sequence": admission_sequence,
        "program_id": program.id,
        "canonical_program_id": program.id,
        "archive_sequence": event.get("archive_sequence"),
        "island_id": event.get("island_id"),
        "admitted": event.get("admitted"),
        "reason": event.get("reason"),
        "cell": event.get("cell"),
        "selection_score": _history_safe_selection_score(program),
        "threshold": event.get("threshold"),
        "evaluation_is_valid": event.get("evaluation_is_valid"),
        "cell_admitted": event.get("cell_admitted"),
        "elite_retained": event.get("elite_retained"),
        "sampling_eligible": event.get("sampling_eligible"),
        "search_state_changed": event.get("search_state_changed"),
    }
    previous_occupant_id = event.get("previous_occupant_id")
    if previous_occupant_id is None or isinstance(previous_occupant_id, str):
        record["previous_occupant_id"] = previous_occupant_id
    objective_vector = _history_safe_objective_vector(program)
    if objective_vector is not None:
        record["objective_vector"] = objective_vector
    descriptors = event.get("descriptors")
    if isinstance(descriptors, Mapping):
        record["descriptors"] = {
            str(name): float(value)
            for name, value in sorted(descriptors.items())
            if isinstance(name, str) and _is_finite_real(value)
        }
    return record


def _reject_duplicate_history_json_names(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateHistoryJsonNameError(
                f"duplicate JSON object name {key!r}"
            )
        result[key] = value
    return result


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
    if "static_files" in source:
        static_files = source["static_files"]
        if not isinstance(static_files, list):
            raise StrictJsonlError(f"{label}.static_files must be a list of path labels")
        seen_static_files: set[str] = set()
        normalized_static_files = []
        for file_index, file_path in enumerate(static_files):
            path = _normalize_seed_source_path(
                f"{label}.static_files[{file_index}]",
                file_path,
                allowed_reserved_paths=allowed_reserved_paths,
            )
            if path in seen_static_files:
                raise StrictJsonlError(
                    f"{label}.static_files must not contain duplicates"
                )
            seen_static_files.add(path)
            normalized_static_files.append(path)
        normalized["static_files"] = sorted(normalized_static_files)
    if "static_file_count" in source:
        static_file_count = source["static_file_count"]
        if (
            isinstance(static_file_count, bool)
            or not isinstance(static_file_count, int)
            or static_file_count < 0
        ):
            raise StrictJsonlError(
                f"{label}.static_file_count must be a non-negative integer"
            )
        if (
            "static_files" in normalized
            and static_file_count != len(normalized["static_files"])
        ):
            raise StrictJsonlError(
                f"{label}.static_file_count must match static_files length"
            )
        normalized["static_file_count"] = static_file_count
    elif "static_files" in normalized:
        normalized["static_file_count"] = len(normalized["static_files"])
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
    llm_feedback = _manifest_llm_feedback([])
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
            "quarantine_snapshot_retention_mode": (
                config.quarantine_snapshot_retention_mode
            ),
            "prompt_reward_mode": config.prompt_reward_mode,
            "prompt_reward_bounds": config.prompt_reward_bounds,
            "prompt_explore_coeff": config.prompt_explore_coeff,
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
            "llm_role_scheduler_scope": config.llm_role_scheduler_scope,
            "llm_role_backend_indices": {
                role: list(indices)
                for role, indices in config.llm_role_backend_indices.items()
            },
            "llm_prompt_roles": llm_prompt_roles["values"],
            "llm_prompt_roles_metadata": llm_prompt_roles["metadata"],
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
            "candidate_language": _candidate_language_policy(config),
            "seed_post_processing": {
                "policy": "raw_evaluator_baseline",
                "reason": (
                    "Initial seeds are evaluated before mutation LLM calls."
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
    return manifest


def _candidate_language_policy(config: Config) -> dict:
    return {
        "schema": CANDIDATE_LANGUAGE_POLICY_SCHEMA,
        "language": "python",
        "execution": "host_local_validator_subprocess",
        "security_sandbox": False,
        "authority": "problem_owned_python_validator",
    }


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
            "feedback_raw_response": {
                "retention_mode": 'redacted',
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_original_response",
            },
            "feedback_parsed_fields": {
                "retention_mode": 'redacted',
                "configurable": True,
                "modes": ["full", "redacted", "hash_only", "off"],
                "hash": "sha256_of_original_field_text",
            },
            "failure_memory_llm_feedback": {
                "retention_mode": 'redacted',
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
        "capability_readiness": {
            "schema": "libreevolve.provider_capability_lookup_readiness.v1",
            "live_model_registry_lookup": False,
            "provider_service_api_version_lookup": False,
            "provider_account_availability_validation": False,
            "remaining_gap": [
                "live_model_registry_lookup",
                "provider_service_api_version_lookup",
                "provider_account_availability_validation",
            ],
        },
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
    if isinstance(metadata, dict) and isinstance(metadata.get("validator_boundary"), dict):
        summary["metadata"] = {
            "validator_boundary": copy.deepcopy(metadata["validator_boundary"])
        }
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
