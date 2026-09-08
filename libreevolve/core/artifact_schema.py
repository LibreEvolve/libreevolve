from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path

from libreevolve.core.jsonl import StrictJsonlError, iter_quarantine_records
from libreevolve.core.artifact_schema_record_contracts import (
    jsonl_record_families,
    quarantine_record_families,
)

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
DUPLICATE_WORK_CACHE_INDEX_RECORD_SCHEMA = (
    "libreevolve.duplicate_work_cache_index.v1"
)
CONTROLLER_BUDGET_EVENT_RECORD_SCHEMA = "libreevolve.controller_budget_event.v1"
QUARANTINE_RECORD_SCHEMA = "libreevolve.strict_jsonl_quarantine_diagnostic.v1"
LEGACY_RECORD_POLICY = "missing_schema_version_accepted_as_legacy_v0"
RUN_ARTIFACT_NAMES = frozenset(
    {
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
        "manifest.json",
        "manifest_invalid.jsonl",
        "best.py",
        "best_workspace",
        "evaluator_artifacts",
    }
)


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
    ):
        if not isinstance(report.get(field), bool):
            issues.append(
                {"code": f"invalid_{field}", "message": f"{field} must be boolean"}
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


def validate_runtime_restore_certification_record(certification: object) -> dict:
    """Validate persisted runtime.restore_certification without upgrading claims."""
    issues = _runtime_restore_certification_issues(certification)
    if issues:
        codes = ",".join(issue["code"] for issue in issues[:5])
        raise ValueError(f"runtime restore certification validation failed: {codes}")
    return deepcopy(dict(certification))  # type: ignore[arg-type]


def _runtime_restore_certification_issues(certification: object) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not isinstance(certification, Mapping):
        return [
            {
                "code": "missing_restore_certification",
                "message": "restore certification must be an object",
            }
        ]
    if certification.get("schema") != "libreevolve.full_resume_restore_certification.v1":
        issues.append(
            {
                "code": "invalid_restore_certification_schema",
                "message": "restore certification schema changed",
            }
        )
    if certification.get("status") != "compatible_surfaces_certified":
        issues.append(
            {
                "code": "invalid_restore_certification_status",
                "message": "restore certification must remain scoped to compatible surfaces",
            }
        )
    if certification.get("scope") != "local_manifest_restore_inputs_only":
        issues.append(
            {
                "code": "invalid_restore_certification_scope",
                "message": "restore certification scope changed",
            }
        )
    expected_surfaces = [
        "runtime_rng_state_snapshot",
        "runtime_llm_scheduler_state_snapshot",
        "runtime_archive_state_snapshot",
        "runtime_archive_programs_by_id",
        "runtime_budget_state_snapshot",
        "controller_budget_event_replay",
        "lineage_provider_boundary",
        "run_artifact_bundle_report",
    ]
    if certification.get("certified_surfaces") != expected_surfaces:
        issues.append(
            {
                "code": "restore_certification_surfaces_mismatch",
                "message": "restore certification surface list changed",
            }
        )
    report = certification.get("run_artifact_bundle_report")
    if not isinstance(report, Mapping):
        issues.append(
            {
                "code": "invalid_restore_certification_bundle_report",
                "message": "restore certification must summarize bundle report validation",
            }
        )
    else:
        if report.get("status") not in {"validated", "absent"}:
            issues.append(
                {
                    "code": "invalid_restore_certification_bundle_report_status",
                    "message": "bundle report status must be validated or absent",
                }
            )
        if report.get("status") == "validated" and report.get("validation_ok") is not True:
            issues.append(
                {
                    "code": "restore_certification_bundle_report_validation_mismatch",
                    "message": "validated bundle report must have validation_ok true",
                }
            )
        if report.get("status") == "absent" and report.get("validation_ok") is not None:
            issues.append(
                {
                    "code": "restore_certification_absent_report_validation_mismatch",
                    "message": "absent bundle report must have null validation status",
                }
            )
    boundary = certification.get("accepted_quarantine_boundary")
    if not isinstance(boundary, Mapping):
        issues.append(
            {
                "code": "invalid_restore_certification_quarantine_boundary",
                "message": "restore certification must record quarantine boundary",
            }
        )
    else:
        if boundary.get("quarantine_rows_replayed_as_state") is not False:
            issues.append(
                {
                    "code": "restore_certification_quarantine_replay_overclaim",
                    "message": "quarantine rows must not be certified as replayed state",
                }
            )
        if boundary.get("quarantine_rows_are_diagnostics") is not True:
            issues.append(
                {
                    "code": "restore_certification_quarantine_diagnostic_missing",
                    "message": "quarantine diagnostic boundary must be explicit",
                }
            )
    for field in (
        "full_replay_ready",
        "provider_output_replay_ready",
        "pending_work_resume_ready",
        "resumed_trace_proof_ready",
    ):
        if certification.get(field) is not False:
            issues.append(
                {
                    "code": f"restore_certification_{field}_overclaim",
                    "message": f"restore certification {field} must remain false",
                }
            )
    if certification.get("compatible_resume_ready") is not True:
        issues.append(
            {
                "code": "restore_certification_compatible_resume_not_ready",
                "message": "restore certification should confirm compatible surfaces",
            }
        )
    return issues


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
    inventory = {}
    for group in ("jsonl_records", "quarantine_jsonl_records", "non_jsonl_artifacts"):
        for name in schema[group]:
            inventory[name] = {
                "path": name,
                "schema_pointer": f"artifact_schema.{group}[{name!r}]",
                "runtime_pointer_location": f"runtime.artifacts[{name!r}]",
                "cleanup_managed": True,
            }
    if set(inventory) != RUN_ARTIFACT_NAMES:
        raise RuntimeError("Generated artifact inventory differs from declared run artifacts")
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
        },
        "jsonl_records": jsonl_record_families(
            history=HISTORY_RECORD_SCHEMA,
            evaluator_result=EVALUATOR_RESULT_RECORD_SCHEMA,
            failure=FAILURE_RECORD_SCHEMA,
            archive_event=ARCHIVE_EVENT_RECORD_SCHEMA,
            llm_call=LLM_CALL_RECORD_SCHEMA,
            llm_reward=LLM_REWARD_RECORD_SCHEMA,
            prompt_history=PROMPT_HISTORY_RECORD_SCHEMA,
            controller_budget_event=CONTROLLER_BUDGET_EVENT_RECORD_SCHEMA,
        ),
        "quarantine_jsonl_records": {
            name: _quarantine_record(
                record["source_stream"],
                record["source_record_schema"],
            )
            for name, record in quarantine_record_families(
                history=HISTORY_RECORD_SCHEMA,
                failure=FAILURE_RECORD_SCHEMA,
                archive_event=ARCHIVE_EVENT_RECORD_SCHEMA,
                controller_budget_event=CONTROLLER_BUDGET_EVENT_RECORD_SCHEMA,
                llm_call=LLM_CALL_RECORD_SCHEMA,
                llm_reward=LLM_REWARD_RECORD_SCHEMA,
                prompt_history=PROMPT_HISTORY_RECORD_SCHEMA,
                manifest=RUN_MANIFEST_SCHEMA,
                diagnostic=QUARANTINE_RECORD_SCHEMA,
            ).items()
        },
    }


def versioned_record(record_schema: str, record: dict) -> dict:
    result = deepcopy(record)
    result["schema_version"] = ARTIFACT_SCHEMA_VERSION
    result["record_schema"] = record_schema
    return result
