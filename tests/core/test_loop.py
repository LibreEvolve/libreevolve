import tempfile
import base64
import copy
import hashlib
import json
import math
import os
import random
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
import yaml
from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.budget import (
    RunBudget,
    apply_controller_budget_event,
    validate_controller_budget_event,
)
from libreevolve.core.config import Config
from libreevolve.core.database import validate_task_specification_bundle
from libreevolve.core.jsonl import StrictJsonlError, strict_json_dumps
from libreevolve.core.loop import (
    CONTROLLER_STATE_ARTIFACT_INVENTORY_SCHEMA,
    CONTROLLER_STATE_VALIDATION_SCHEMA,
    FULL_RESUME_BUNDLE_VALIDATION_SCHEMA,
    PROMPT_CONTEXT_POLICY_COVERAGE_SCHEMA,
    PROMPT_CONTEXT_POLICY_COVERAGE_VALIDATION_SCHEMA,
    META_PROMPT_CONTEXT_POLICY_CAPABILITY_SUMMARY_VALIDATION_SCHEMA,
    PROMPT_SECTION_PACKING_COVERAGE_SCHEMA,
    PROMPT_SECTION_PACKING_COVERAGE_VALIDATION_SCHEMA,
    RETRIEVAL_EVIDENCE_COVERAGE_SCHEMA,
    RETRIEVAL_EVIDENCE_COVERAGE_VALIDATION_SCHEMA,
    RuntimeFullResumeBundleError,
    RuntimeLineageReplayPolicyError,
    RuntimeLLMSchedulerStateError,
    RuntimeRngStateError,
    controller_state_artifact_inventory,
    evolve,
    validate_direct_plugin_policy,
    validate_prompt_context_policy_coverage,
    validate_prompt_section_packing_coverage,
    validate_retrieval_evidence_coverage,
    validate_acknowledgement_role_provenance_report,
    validate_controller_state_snapshot,
    validate_evaluation_cascade_report,
    validate_cascade_hypothesis_test_policy_report,
    validate_evaluator_workload_report,
    validate_parallel_evaluation_readiness_report,
    validate_distributed_pipeline_topology_report,
    validate_alphaevolve_process_exhibit_report,
    validate_alphaevolve_table1_capability_exhibit_report,
    validate_codebase_scale_benchmark_report,
    validate_candidate_abstraction_choice_report,
    validate_candidate_language_runner_contract_report,
    validate_collaborator_feedback_provenance_report,
    validate_initial_program_idea_provenance_report,
    validate_initial_program_validity_report,
    validate_initial_pool_divergence_report,
    validate_benchmark_fixture_readiness_report,
    validate_problem_formulation_provenance_report,
    validate_existing_codebase_integration_report,
    validate_explicit_context_source_role_report,
    validate_marker_spelling_provenance_report,
    validate_task_spec_artifact_resolution_report,
    validate_evaluator_oracle_registry,
    validate_embedded_evaluator_entrypoint_report,
    validate_automated_evaluator_scope_report,
    validate_whole_run_source_workspace_integrity_report,
    validate_qualitative_feedback_policy_report,
    validate_qualitative_feedback_prompt_history_audit_report,
    validate_paper_evaluator_metric_contract,
    validate_paper_author_metadata_report,
    validate_paper_metric_table_export,
    paper_metric_cross_run_report,
    validate_paper_metric_cross_run_report,
    validate_system_contribution_provenance_report,
    validate_title_page_affiliation_report,
    validate_metric_diverse_inspiration_report,
    validate_duplicate_work_policy_report,
    validate_sampling_balance_report,
    validate_programmatic_representation_boundary_report,
    validate_mutation_operator_boundary_report,
    validate_mutation_consistency_report,
    validate_prompt_example_copy_report,
    validate_prompt_current_binding_report,
    validate_primary_prompt_instruction_report,
    validate_stochastic_prompt_format_distribution_report,
    validate_prompt_prior_score_provenance_report,
    validate_natural_language_preamble_report,
    validate_proposal_diversity_report,
    validate_proposal_score_report,
    validate_proposal_lifecycle_report,
    validate_incorrect_suggestion_audit_report,
    validate_sample_efficiency_report,
    validate_repeated_sampling_baseline_report,
    validate_gemini_provider_parity_report,
    validate_hypothesis_branch_report,
    validate_controller_backtracking_report,
    VALID_THRESHOLD,
    META_PROMPT_CONTEXT_POLICY_CAPABILITIES_SCHEMA,
    _build_meta_prompt_mutation_request,
    _META_PROMPT_CONTEXT_POLICY_CAPABILITIES,
    _meta_prompt_metrics,
    _meta_prompt_safe_value,
    load_runtime_budget_state_snapshot,
    load_runtime_lineage_replay_policy_snapshot,
    load_runtime_rng_state_snapshot,
    restore_runtime_rng_state_snapshot,
    _runtime_artifact_pointers,
    _runtime_llm_scheduler_state,
    _runtime_provider_cancellation_policy,
    _runtime_rng_state,
    _workspace_sha256,
    _generate_with_budget,
    load_full_resume_bundle,
    load_runtime_llm_scheduler_state_snapshot,
    validate_full_resume_bundle,
    validate_runtime_rng_state_snapshot,
    validate_runtime_lineage_replay_policy,
    validate_runtime_llm_scheduler_state_snapshot,
    validate_meta_prompt_context_policy_capabilities,
    validate_meta_prompt_context_policy_capability_summary,
    _select_critique_mutation,
)
from libreevolve.core.meta_prompt import PromptDatabase, PromptProgram
from libreevolve.core.prompt import DEFAULT_TEMPLATE, validate_prompt_context_policy
from libreevolve.llm.ensemble import LLMEnsemble, LLM_PROVIDER_DIAGNOSTICS_SCHEMA
from libreevolve.llm.budget_report import (
    LLM_BUDGET_REPORT_POLICY,
    LLM_BUDGET_REPORT_SCHEMA,
    LLM_BUDGET_REPORT_STATUS,
    validate_llm_budget_report,
)
from libreevolve.llm.cancellation_policy import validate_provider_cancellation_policy
from libreevolve.population.program import Program
from libreevolve.plugins.causal import CausalPlugin
from libreevolve.plugins.deep_research import DeepResearchPlugin
from libreevolve.plugins.base import PluginBase
from libreevolve.plugins.modular import ModularPlugin
from libreevolve.plugins.ttt_rl import TTTRLPlugin
from libreevolve.problems.loader import Problem, load_problem


class _EntryPointPlugin(PluginBase):
    def __init__(self, mode: str = "default", limit: int = 1):
        self.mode = mode
        self.limit = limit

    def run_artifacts_metadata(self):
        return {"entry_point": True, "mode": self.mode, "limit": self.limit}


def test_workspace_sha256_includes_static_file_metadata():
    base = CandidateWorkspace(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        static_files=[
            {"path": "fixture.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 1}
        ],
    )
    changed_static = CandidateWorkspace(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        static_files=[
            {"path": "fixture.bin", "kind": "binary", "sha256": "b" * 64, "bytes": 1}
        ],
    )

    assert _workspace_sha256(base) != _workspace_sha256(changed_static)


class _SchemaEntryPointPlugin(PluginBase):
    libreevolve_constructor_option_schema = {
        "mode": {"type": "enum", "values": ["audit", "dry_run"]},
        "limit": {"type": "positive_int"},
    }

    def __init__(self, mode: str = "audit", limit: int = 1):
        self.mode = mode
        self.limit = limit

    def run_artifacts_metadata(self):
        return {"entry_point": True, "mode": self.mode, "limit": self.limit}


class _FakeDistribution:
    version = "1.2.3"
    metadata = {"Name": "libreevolve-test-plugin"}

    def read_text(self, name: str):
        if name == "RECORD":
            return (
                "tests/fake.py,sha256=abc,123\n"
                "libreevolve_test_plugin-1.2.3.dist-info/METADATA,,456\n"
            )
        if name == "WHEEL":
            return (
                "Wheel-Version: 1.0\n"
                "Generator: test-wheel\n"
                "Root-Is-Purelib: true\n"
                "Tag: py3-none-any\n"
                "Tag: py3-none-win_amd64\n"
            )
        raise FileNotFoundError(name)


class _FakeEntryPoint:
    name = "sample"
    group = "libreevolve.plugins"
    value = "tests.fake:EntryPointPlugin"
    dist = _FakeDistribution()

    def load(self):
        return _EntryPointPlugin


class _FakeSchemaEntryPoint(_FakeEntryPoint):
    name = "schema_sample"
    value = "tests.fake:SchemaEntryPointPlugin"

    def load(self):
        return _SchemaEntryPointPlugin


class _FakeEntryPoints(list):
    def select(self, *, group: str, name: str):
        return [
            entry_point
            for entry_point in self
            if entry_point.group == group and entry_point.name == name
        ]

def _problem(src="def evaluate(c): return {'score':1.0,'is_valid':True}"):
    d = Path(tempfile.mkdtemp())
    (d/"validate.py").write_text(src)
    return Problem(name="t", task_description="t",
                   metrics=[{"name":"score","primary":True,"bounds":[0.0,1.0]}],
                   primary_metric="score", primary_bounds=(0.0,1.0),
                   validate_path=d/"validate.py", initial_programs=["x=1"], problem_dir=d)


def _parse_utc_timestamp(value: str) -> datetime:
    assert value.endswith("Z")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def test_evolve_rejects_inline_seed_over_candidate_workspace_budget(tmp_path):
    problem = _problem()
    problem.initial_programs = ["x = 1\n"]

    with pytest.raises(ValueError, match="max_candidate_file_chars"):
        evolve(
            problem,
            Config(
                max_generations=0,
                log_dir=str(tmp_path),
                problem_name="t",
                max_candidate_file_chars=5,
            ),
        )


def test_evolve_rejects_direct_workspace_over_file_count_budget(tmp_path):
    problem = _problem()
    problem.initial_programs = []
    problem.initial_workspaces = [
        {"primary_file": "main.py", "files": {"main.py": "x=1", "helper.py": "y=2"}}
    ]

    with pytest.raises(ValueError, match="max_candidate_workspace_files"):
        evolve(
            problem,
            Config(
                max_generations=0,
                log_dir=str(tmp_path),
                problem_name="t",
                max_candidate_workspace_files=1,
            ),
        )


def test_evolve_rejects_direct_workspace_over_static_byte_budget(tmp_path):
    problem = _problem()
    problem.initial_programs = []
    problem.initial_workspaces = [
        {
            "primary_file": "main.py",
            "files": {"main.py": "x=1"},
            "static_files": [
                {
                    "path": "fixture.bin",
                    "kind": "binary",
                    "sha256": "a" * 64,
                    "bytes": 4,
                }
            ],
        }
    ]

    with pytest.raises(ValueError, match="max_candidate_static_file_bytes"):
        evolve(
            problem,
            Config(
                max_generations=0,
                log_dir=str(tmp_path),
                problem_name="t",
                max_candidate_static_file_bytes=3,
            ),
        )


def test_evolve_passes_configured_evaluator_stdin_text_to_seed_validator(tmp_path):
    problem = _problem(
        "import sys\n"
        "def evaluate(c):\n"
        "    data = sys.stdin.read()\n"
        "    return {'score': 1.0 if data == 'seed-input' else 0.0, 'is_valid': data == 'seed-input'}\n"
    )

    best = evolve(
        problem,
        Config(
            max_generations=0,
            log_dir=str(tmp_path),
            problem_name="t",
            evaluator_stdin_text="seed-input",
        ),
    )

    record = json.loads((tmp_path / "t" / "history.jsonl").read_text().splitlines()[0])
    stdin = record["evaluation"]["metadata"]["stdin"]
    assert best.fitness == 1.0
    assert stdin["policy"] == "configured_text"
    assert stdin["sha256"] == hashlib.sha256(b"seed-input").hexdigest()
    assert "seed-input" not in json.dumps(record)


def test_evolve_passes_configured_evaluator_stdin_file_to_seed_validator(tmp_path):
    problem = _problem(
        "import sys\n"
        "def evaluate(c):\n"
        "    data = sys.stdin.read()\n"
        "    return {'score': 1.0 if data == 'file-seed-input' else 0.0, 'is_valid': data == 'file-seed-input'}\n"
    )
    (problem.problem_dir / "stdin.txt").write_bytes(b"file-seed-input")

    best = evolve(
        problem,
        Config(
            max_generations=0,
            log_dir=str(tmp_path),
            problem_name="t",
            evaluator_stdin_file="stdin.txt",
        ),
    )

    record = json.loads((tmp_path / "t" / "history.jsonl").read_text().splitlines()[0])
    stdin = record["evaluation"]["metadata"]["stdin"]
    assert best.fitness == 1.0
    assert stdin["policy"] == "configured_file"
    assert stdin["path"] == "stdin.txt"
    assert stdin["file_sha256"] == hashlib.sha256(b"file-seed-input").hexdigest()
    assert "file-seed-input" not in json.dumps(record)


def _llm(diff="<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"):
    m = MagicMock(); m.generate.return_value = (diff, 0); return m


class _TelemetryLLM:
    def __init__(self, diff="<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"):
        self.diff = diff
        self.last_call = None
        self.calls = []

    def generate(self, prompt, role="mutation"):
        self.last_call = {
            "id": f"call-{len(self.calls)}",
            "role": role,
            "backend_idx": 0,
            "backend_name": "fake/model",
            "prompt": prompt,
            "prompt_chars": len(prompt),
            "output_chars": len(self.diff),
            "status": "ok",
        }
        self.calls.append(self.last_call)
        return self.diff, 0

    def record_reward(self, idx, reward, call_id=None):
        pass


class _RewardLLM:
    def __init__(
        self,
        diff="<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE",
        feedback='{"score": 0.0, "feedback": "reject", "discard": true}',
    ):
        self.diff = diff
        self.feedback = feedback
        self.rewards = []
        self.last_call = None
        self.calls = []

    def generate(self, prompt, role="mutation"):
        self.last_call = {
            "id": f"reward-call-{len(self.calls)}",
            "role": role,
            "backend_idx": 0,
            "backend_name": "fake/model",
            "status": "ok",
        }
        self.calls.append(self.last_call)
        if role.startswith("feedback:"):
            return self.feedback, 0
        return self.diff, 0

    def record_reward(self, idx, reward, call_id=None):
        self.rewards.append((idx, reward, call_id))


class _FailingLLM:
    def __init__(self, message="provider down"):
        self.message = message

    def generate(self, prompt, role="mutation"):
        raise RuntimeError(self.message)

    def record_reward(self, idx, reward, call_id=None):
        pass


def test_evolve_preflights_validator_contract_before_database_cleanup():
    problem = _problem("BROKEN = True\n")
    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "t"
        run_dir.mkdir()
        old_history = "old history\n"
        (run_dir / "history.jsonl").write_text(old_history, encoding="utf-8")

        with pytest.raises(ValueError, match="missing callable evaluate"):
            evolve(
                problem,
                Config(
                    max_generations=0,
                    log_dir=tmpdir,
                    problem_name="t",
                    run_collision_policy="overwrite",
                ),
            )

        assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == old_history
        assert not (run_dir / "manifest.json").exists()


def test_evolve_does_not_mutate_process_global_random_state():
    with tempfile.TemporaryDirectory() as tmpdir:
        random.seed(999)
        expected_after_evolve = random.Random(999).random()

        evolve(
            _problem(),
            Config(
                max_generations=0,
                log_dir=tmpdir,
                problem_name="t",
                run_collision_policy="overwrite",
                seed=42,
            ),
        )

        assert random.random() == expected_after_evolve


def test_runtime_rng_state_snapshot_restores_next_random_values():
    rng = random.Random(123)
    for _ in range(5):
        rng.random()

    snapshot = _runtime_rng_state(rng, 123)
    expected_next_values = [rng.random() for _ in range(3)]

    restored = restore_runtime_rng_state_snapshot(snapshot)

    assert snapshot["status"] == "snapshot"
    assert snapshot["schema"] == "python.random.mt19937.v1"
    assert snapshot["engine"] == "python.random.Random"
    assert snapshot["restore_entrypoint"] == "random.Random.setstate"
    assert snapshot["resume_status"] == "snapshot_persisted_restore_supported"
    assert len(snapshot["state_sha256"]) == 64
    assert snapshot["replay_boundary"] == {
        "schema": "libreevolve.runtime_rng_replay_boundary.v1",
        "owned_rng": "framework_run_random",
        "restored_by_runtime_rng_snapshot": True,
        "owned_surfaces": [
            "loop_parent_explore_exploit_choice",
            "prompt_template_sampling",
            "program_database_sampling",
            "island_sampling",
            "map_elites_sampling",
        ],
        "external_surfaces": [
            {
                "surface": "llm_provider_outputs",
                "restored_by_runtime_rng": False,
                "boundary": "remote_or_sdk_provider_nondeterminism",
            },
            {
                "surface": "plugin_internal_randomness",
                "restored_by_runtime_rng": False,
                "boundary": "plugins_do_not_receive_runtime_rng_automatically",
            },
            {
                "surface": "validator_subprocess_randomness",
                "restored_by_runtime_rng": False,
                "boundary": "stage_rng_seeds_are_recorded_per_evaluation",
            },
        ],
        "provider_rng_policy": "provider_outputs_not_replayed_by_framework_rng",
        "plugin_rng_policy": "plugin_internal_randomness_not_replayed_by_framework_rng",
    }
    assert [restored.random() for _ in range(3)] == expected_next_values


def test_runtime_rng_state_snapshot_validation_returns_defensive_copy():
    rng = random.Random(456)
    snapshot = _runtime_rng_state(rng, 456)

    validated = validate_runtime_rng_state_snapshot(snapshot)
    validated["state"]["internal_state"][0] = 0

    restored = restore_runtime_rng_state_snapshot(snapshot)

    assert validated != snapshot
    assert isinstance(restored.random(), float)


def test_runtime_rng_state_snapshot_validation_accepts_legacy_boundaryless_snapshot():
    snapshot = _runtime_rng_state(random.Random(456), 456)
    snapshot.pop("replay_boundary")

    validated = validate_runtime_rng_state_snapshot(snapshot)

    assert validated["replay_boundary"]["schema"] == (
        "libreevolve.runtime_rng_replay_boundary.v1"
    )
    assert validated["replay_boundary"]["external_surfaces"][0] == {
        "surface": "llm_provider_outputs",
        "restored_by_runtime_rng": False,
        "boundary": "remote_or_sdk_provider_nondeterminism",
    }


def test_runtime_rng_state_snapshot_rejects_overclaimed_external_boundary():
    snapshot = _runtime_rng_state(random.Random(456), 456)
    snapshot["replay_boundary"]["external_surfaces"][0][
        "restored_by_runtime_rng"
    ] = True

    with pytest.raises(RuntimeRngStateError, match="external surfaces"):
        validate_runtime_rng_state_snapshot(snapshot)


def test_runtime_rng_state_snapshot_rejects_hash_mismatch():
    rng = random.Random(789)
    snapshot = _runtime_rng_state(rng, 789)
    snapshot["state"]["internal_state"][0] += 1

    with pytest.raises(RuntimeRngStateError, match="hash mismatch"):
        validate_runtime_rng_state_snapshot(snapshot)


@pytest.mark.parametrize(
    ("task_description", "initial_programs", "message"),
    [
        (None, ["x=1"], "task_description"),
        ("  \n\t", ["x=1"], "task_description"),
        (
            "Use api_key=sk-proj_task_secret_1234567890",  # pragma: allowlist secret
            ["x=1"],
            "task_description",
        ),
        ("A" * 20001, ["x=1"], "task_description"),
        ("valid task", "x=1", "initial_programs"),
        ("valid task", [123], r"initial_programs\[0\]"),
        ("valid task", ["bad\ud800seed"], r"initial_programs\[0\]"),
        ("valid task", ["# EVOLVE-BLOCK-END\nx = 1"], r"initial_programs\[0\]"),
        ("valid task", ["# EVOLVE-BLOCK-START core\nx = 1\n"], r"initial_programs\[0\]"),
        ("valid task", ["x = 1\n" + ("A" * 1_000_001)], r"initial_programs\[0\]"),
        ("valid task", [], "initial program"),
    ],
)
def test_evolve_rejects_incomplete_direct_problem_before_database_writes(
    task_description,
    initial_programs,
    message,
):
    problem = _problem()
    problem.task_description = task_description
    problem.initial_programs = initial_programs
    problem.initial_workspaces = []
    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "t"
        run_dir.mkdir()
        old_history = "old history\n"
        (run_dir / "history.jsonl").write_text(old_history, encoding="utf-8")

        with pytest.raises(ValueError, match=message):
            evolve(
                problem,
                Config(
                    max_generations=0,
                    log_dir=tmpdir,
                    problem_name="t",
                    run_collision_policy="overwrite",
                ),
            )

        assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == old_history
        assert not (run_dir / "manifest.json").exists()


def test_evolve_accepts_valid_direct_inline_seed_after_preflight():
    with tempfile.TemporaryDirectory() as tmpdir:
        best = evolve(
            _problem("def evaluate(c): return {'score': 0.5, 'is_valid': True}"),
            Config(
                max_generations=0,
                log_dir=tmpdir,
                problem_name="t",
                run_collision_policy="overwrite",
            ),
        )

        run_dir = Path(tmpdir) / "t"
        records = [
            json.loads(line)
            for line in (run_dir / "history.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))

        assert best is not None
        assert records[0]["metadata"]["candidate_type"] == "seed"
        assert manifest["problem"]["seed_sources"] == [
            {"seed_index": 0, "seed_source_kind": "inline"}
        ]


@pytest.mark.parametrize(
    "initial_workspaces",
    [
        "bad-workspace",
        ["bad-workspace"],
        [{"files": {"main.py": 1}, "primary_file": "main.py"}],
        [{"files": {"helper.py": "x=1"}, "primary_file": "missing.py"}],
        [{"files": {"main.py": "# EVOLVE-BLOCK-END\nx=1"}, "primary_file": "main.py"}],
    ],
)
def test_evolve_rejects_invalid_direct_initial_workspaces_before_database_writes(
    initial_workspaces,
):
    problem = _problem()
    problem.initial_programs = []
    problem.initial_workspaces = initial_workspaces
    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "t"
        run_dir.mkdir()
        old_history = "old history\n"
        (run_dir / "history.jsonl").write_text(old_history, encoding="utf-8")

        with pytest.raises(ValueError, match="initial_workspaces"):
            evolve(
                problem,
                Config(
                    max_generations=0,
                    log_dir=tmpdir,
                    problem_name="t",
                    run_collision_policy="overwrite",
                ),
            )

        assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == old_history
        assert not (run_dir / "manifest.json").exists()


def test_evolve_revalidates_mutated_direct_initial_workspace_before_database_writes():
    problem = _problem()
    workspace = CandidateWorkspace.from_code("x=1", "main.py")
    workspace.files["main.py"] = "bad\ud800seed"
    problem.initial_programs = []
    problem.initial_workspaces = [workspace]
    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "t"
        run_dir.mkdir()
        old_history = "old history\n"
        (run_dir / "history.jsonl").write_text(old_history, encoding="utf-8")

        with pytest.raises(ValueError, match="initial_workspaces\\[0\\]"):
            evolve(
                problem,
                Config(
                    max_generations=0,
                    log_dir=tmpdir,
                    problem_name="t",
                    run_collision_policy="overwrite",
                ),
            )

        assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == old_history
        assert not (run_dir / "manifest.json").exists()


def test_evolve_accepts_direct_initial_workspace_record_after_preflight():
    with tempfile.TemporaryDirectory() as tmpdir:
        problem = _problem("def evaluate(c): return {'score': 0.5, 'is_valid': True}")
        problem.initial_programs = []
        problem.initial_workspaces = [
            {
                "primary_file": "main.py",
                "files": {"main.py": "x=1\n", "helper.py": "value = 1\n"},
            }
        ]

        best = evolve(
            problem,
            Config(
                max_generations=0,
                log_dir=tmpdir,
                problem_name="t",
                run_collision_policy="overwrite",
            ),
        )

        run_dir = Path(tmpdir) / "t"
        records = [
            json.loads(line)
            for line in (run_dir / "history.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))

        assert best is not None
        assert isinstance(problem.initial_workspaces[0], CandidateWorkspace)
        assert records[0]["metadata"]["candidate_type"] == "seed"
        assert records[0]["files"]["helper.py"] == "value = 1\n"
        assert manifest["problem"]["seed_sources"] == [
            {"seed_index": 0, "seed_source_kind": "workspace"}
        ]


def test_evolve_accepts_direct_initial_workspace_raw_binary_member_after_preflight():
    payload = b"\xff\x00fixture"
    with tempfile.TemporaryDirectory() as tmpdir:
        problem = _problem("def evaluate(c): return {'score': 0.5, 'is_valid': True}")
        problem.initial_programs = []
        problem.initial_workspaces = [
            {
                "primary_file": "main.py",
                "files": {"main.py": "x=1\n", "fixture.bin": payload},
            }
        ]

        best = evolve(
            problem,
            Config(
                max_generations=0,
                log_dir=tmpdir,
                problem_name="t",
                run_collision_policy="overwrite",
            ),
        )

        run_dir = Path(tmpdir) / "t"
        records = [
            json.loads(line)
            for line in (run_dir / "history.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))

        assert best is not None
        assert isinstance(problem.initial_workspaces[0], CandidateWorkspace)
        assert records[0]["files"] == {"main.py": "x=1\n"}
        assert records[0]["static_files"] == [
            {
                "path": "fixture.bin",
                "kind": "binary",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "source_kind": "direct_workspace_record",
                "mutation_policy": "immutable",
                "content_b64": base64.b64encode(payload).decode("ascii"),
            }
        ]
        assert manifest["problem"]["seed_sources"] == [
            {"seed_index": 0, "seed_source_kind": "workspace"}
        ]


def test_evolve_persists_reserved_seed_workspace_policy():
    with tempfile.TemporaryDirectory() as tmpdir:
        problem = _problem("def evaluate(c): return {'score': 0.5, 'is_valid': True}")
        problem.initial_programs = []
        problem.initial_workspaces = [
            CandidateWorkspace(
                files={"main.py": "x=1\n", ".config.py": "value = 1\n"},
                primary_file="main.py",
                allowed_reserved_paths=frozenset({".config.py"}),
            )
        ]
        problem.initial_workspace_sources = [
            {
                "seed_index": 0,
                "seed_source_kind": "directory",
                "seed_source_path": "initial_programs/seed_a",
                "primary_file": "main.py",
                "file_count": 2,
                "files": [".config.py", "main.py"],
                "allowed_reserved_paths": [".config.py"],
            }
        ]
        problem.initial_workspace_policy = {
            "policy": "skip_reserved_seed_paths_by_default",
            "reserved_components": ["dot-prefixed", "__pycache__"],
            "source": "seed_policy.yaml",
            "include": ["seed_a/.config.py"],
            "exclude": [],
            "exclude_precedence": True,
        }

        evolve(
            problem,
            Config(
                max_generations=0,
                log_dir=tmpdir,
                problem_name="t",
                run_collision_policy="overwrite",
            ),
        )

        run_dir = Path(tmpdir) / "t"
        records = [
            json.loads(line)
            for line in (run_dir / "history.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))

        assert manifest["problem"]["seed_policy"]["source"] == "seed_policy.yaml"
        assert manifest["problem"]["seed_sources"][0]["allowed_reserved_paths"] == [".config.py"]
        assert records[0]["workspace_path_policy"]["allowed_reserved_paths"] == [".config.py"]
        assert records[0]["files"][".config.py"] == "value = 1\n"


def test_evolve_rejects_invalid_direct_context_before_database_writes():
    problem = _problem()
    problem.context_files = {"../secret.md": "text"}
    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "t"
        run_dir.mkdir()
        old_history = "old history\n"
        (run_dir / "history.jsonl").write_text(old_history, encoding="utf-8")

        with pytest.raises(ValueError, match="context_files"):
            evolve(
                problem,
                Config(
                    max_generations=0,
                    log_dir=tmpdir,
                    problem_name="t",
                    run_collision_policy="overwrite",
                ),
            )

        assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == old_history
        assert not (run_dir / "manifest.json").exists()


def test_returns_program():
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        best = evolve(_problem(), Config(max_generations=2,
                                        log_dir=tempfile.mkdtemp(), problem_name="t"))
    assert best is not None and isinstance(best.fitness, float)


def test_loop_logs_llm_call_telemetry_on_candidate():
    tmpdir = tempfile.mkdtemp()
    llm = _TelemetryLLM()

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[1]
    assert records[0]["metadata"]["candidate_type"] == "seed"
    assert records[0]["generation"] == 0
    assert "prompt_program_id" not in records[0]["metadata"]
    assert child["metadata"]["candidate_type"] == "generated"
    assert child["generation"] == 1
    assert child["metadata"]["loop_generation_index"] == 0
    assert "prompt_program_id" in child["metadata"]
    assert child["metadata"]["llm_calls"][0]["role"] == "mutation"
    assert child["metadata"]["llm_calls"][0]["backend_name"] == "fake/model"


def test_loop_uses_deterministic_seed_and_generated_candidate_ids():
    def run_once():
        tmpdir = tempfile.mkdtemp()
        with patch("libreevolve.core.loop.build_llm", return_value=_TelemetryLLM()):
            evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))
        return [
            json.loads(line)
            for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
        ]

    first = run_once()
    second = run_once()

    assert [record["id"] for record in first] == [record["id"] for record in second]
    assert first[0]["id"].startswith("candidate-seed-0-")
    assert first[1]["id"].startswith("candidate-gen-1-0-p0-")
    assert first[1]["parent_id"] == first[0]["id"]
    assert second[1]["parent_id"] == second[0]["id"]


def test_loop_evaluates_configured_proposal_batch_in_one_generation():
    tmpdir = tempfile.mkdtemp()
    llm = _TelemetryLLM("x=2")

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                proposals_per_generation=3,
                mutation_mode="full",
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    run_dir = Path(tmpdir) / "t"
    records = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    generated = records[1:]
    assert len(generated) == 3
    assert [record["generation"] for record in generated] == [1, 1, 1]
    assert [record["metadata"]["proposal_batch"]["proposal_index"] for record in generated] == [0, 1, 2]
    assert all(
        record["metadata"]["proposal_batch"]["proposals_per_generation"] == 3
        for record in generated
    )
    assert [record["metadata"]["proposal_batch"]["loop_proposal_index"] for record in generated] == [0, 1, 2]
    assert generated[0]["id"].startswith("candidate-gen-1-0-p0-")
    assert generated[1]["id"].startswith("candidate-gen-1-0-p1-")
    assert generated[2]["id"].startswith("candidate-gen-1-0-p2-")
    assert [call["role"] for call in llm.calls] == ["mutation", "mutation", "mutation"]

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    consumed = manifest["runtime"]["consumed"]
    assert consumed["generations_started"] == 1
    assert consumed["generations_completed"] == 1
    assert consumed["candidate_evaluations"] == 2
    duplicate_report = manifest["runtime"]["history"]["duplicate_work_policy_report"]
    assert duplicate_report["evaluation_cache_hit_count"] == 1
    assert manifest["config"]["proposals_per_generation"] == 3


def test_runtime_history_reports_exact_proposal_diversity_counts():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        (
            "IDEA: Set x to the accepted value.\n"
            "RATIONALE: The validator expects x=2.\n"
            "HYPOTHESIS: Direct assignment should validate.\n"
            "x=2",
            0,
        ),
        (
            "IDEA: Use a plain constant assignment.\n"
            "RATIONALE: Keeping the solution minimal should pass.\n"
            "HYPOTHESIS: The evaluator accepts the exact value.\n"
            "x=2",
            0,
        ),
        (
            "IDEA: Set x to the accepted value.\n"
            "RATIONALE: The duplicate idea should be counted exactly.\n"
            "HYPOTHESIS: Duplicate proposal text is observable.\n"
            "x=2",
            0,
        ),
    ]

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                proposals_per_generation=3,
                mutation_mode="full",
                capture_proposal_metadata=True,
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    report = manifest["runtime"]["history"]["proposal_diversity_report"]

    assert report["schema"] == "libreevolve.proposal_diversity_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_proposal_diversity_report(report)["ok"] is True
    assert report["generated_candidate_count"] == 3
    assert report["proposal_metadata_count"] == 3
    assert report["idea_record_count"] == 3
    assert report["unique_idea_hash_count"] == 2
    assert report["duplicate_exact_idea_count"] == 1
    assert report["unique_proposal_signature_count"] == 3
    assert report["duplicate_exact_proposal_count"] == 0
    assert report["analysis_policy"]["exact_text_hashes"] is True
    assert report["analysis_policy"]["near_duplicate_detection"] is False
    assert report["analysis_policy"]["semantic_novelty_scoring"] is False
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["exact_duplicate_detection"] is True
    assert report["claim_readiness"]["semantic_proposal_diversity"] is False
    assert report["claim_readiness"]["model_quality_effect"] is False

    generation = report["generation_records"][0]
    assert generation["generation"] == 1
    assert generation["candidate_count"] == 3
    assert generation["proposal_metadata_count"] == 3
    assert generation["unique_idea_hash_count"] == 2
    assert generation["duplicate_exact_idea_count"] == 1

    batch = report["batch_records"][0]
    assert batch["loop_generation_index"] == 0
    assert batch["proposals_per_generation"] == 3
    assert batch["candidate_count"] == 3
    assert batch["unique_idea_hash_count"] == 2
    assert batch["duplicate_exact_idea_count"] == 1
    assert {record["idea_preview"] for record in report["sample_records"]} == {
        "Set x to the accepted value.",
        "Use a plain constant assignment.",
    }


def test_runtime_history_reports_proposal_scores_without_semantic_index_claim():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code):\n"
        "    if 'x=2' in code:\n"
        "        return {'score': 1.0, 'is_valid': True}\n"
        "    if 'x=1' in code:\n"
        "        return {'score': 0.5, 'is_valid': True}\n"
        "    return {'score': -0.1, 'is_valid': False}\n"
    )
    llm = MagicMock()
    llm.generate.side_effect = [
        (
            "IDEA: Set x to the accepted value.\n"
            "RATIONALE: The validator expects x=2.\n"
            "HYPOTHESIS: Direct assignment should validate.\n"
            "x=2",
            0,
        ),
        (
            "IDEA: Try an unaccepted value.\n"
            "RATIONALE: This tests rejection scoring.\n"
            "HYPOTHESIS: The evaluator should reject x=3.\n"
            "x=3",
            0,
        ),
        (
            "IDEA: Set x to the accepted value.\n"
            "RATIONALE: The validator expects x=2.\n"
            "HYPOTHESIS: Direct assignment should validate.\n"
            "x=2",
            0,
        ),
    ]

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(
                max_generations=1,
                proposals_per_generation=3,
                mutation_mode="full",
                capture_proposal_metadata=True,
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    report = manifest["runtime"]["history"]["proposal_score_report"]

    assert report["schema"] == "libreevolve.proposal_score_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_proposal_score_report(report)["ok"] is True
    assert report["generated_candidate_count"] == 3
    assert report["proposal_metadata_count"] == 3
    assert report["scored_proposal_count"] == 3
    assert report["unique_proposal_signature_count"] == 2
    assert report["duplicate_exact_signature_count"] == 1
    assert report["accepted_scored_count"] == 2
    assert report["rejected_scored_count"] == 1
    assert report["scoring_policy"]["semantic_similarity"] is False
    assert report["scoring_policy"]["embedding_index"] is False
    assert report["scoring_policy"]["calibrated_quality_model"] is False
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["versioned_proposal_score_records"] is True
    assert report["claim_readiness"]["semantic_proposal_index"] is False
    assert report["claim_readiness"]["prompt_or_archive_selection_uses_scores"] is False

    top = report["top_records"][0]
    assert top["idea_preview"] == "Set x to the accepted value."
    assert top["outcome_quality_score"] == 1.0
    assert top["exact_text_novelty_score"] == 1.0
    assert top["proposal_score"] == 1.0
    duplicate = [
        record
        for record in report["top_records"]
        if record["idea_preview"] == "Set x to the accepted value."
        and record["exact_signature_duplicate"] is True
    ][0]
    assert duplicate["outcome_quality_score"] == 1.0
    assert duplicate["exact_text_novelty_score"] == 0.0
    assert duplicate["proposal_score"] == 0.7
    rejected = [
        record
        for record in report["top_records"]
        if record["idea_preview"] == "Try an unaccepted value."
    ][0]
    assert rejected["outcome_quality_score"] == 0.0
    assert rejected["proposal_score"] == 0.3


def test_runtime_history_reports_initial_pool_divergence_boundary():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c):\n"
        "    if 'x=3' in c:\n"
        "        return {'score': 0.9, 'is_valid': True}\n"
        "    if 'x=2' in c:\n"
        "        return {'score': 0.4, 'is_valid': True}\n"
        "    return {'score': 0.1, 'is_valid': True}\n"
    )
    problem = Problem(
        name="t",
        task_description="t",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["x=1", "x=2"],
        problem_dir=d,
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm("x=3")):
        evolve(
            problem,
            Config(
                max_generations=1,
                mutation_mode="full",
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    report = manifest["runtime"]["history"]["initial_pool_divergence_report"]

    assert report["schema"] == "libreevolve.initial_pool_divergence_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_initial_pool_divergence_report(report)["ok"] is True
    assert report["seed_program_count"] == 2
    assert report["generated_candidate_count"] == 1
    assert len(report["seed_records"]) == 2
    assert report["exact_seed_workspace_match_count"] == 0
    assert report["non_seed_workspace_count"] == 1
    assert report["max_primary_text_distance"] > 0.0
    assert report["max_numeric_metric_l1_distance"] > 0.0
    assert report["distance_policy"]["workspace_identity"] == (
        "canonical_workspace_sha256"
    )
    assert report["distance_policy"]["functional_distance_artifacts"] is False
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["syntactic_distance_reported"] is True
    assert report["claim_readiness"]["metric_distance_reported"] is True
    assert report["claim_readiness"]["functional_distance_reported"] is False
    assert report["claim_readiness"]["substantially_different_claim_ready"] is False

    candidate = report["candidate_records"][0]
    assert candidate["generation"] == 1
    assert candidate["exact_seed_workspace_match"] is False
    assert candidate["seed_comparison_count"] == 2
    closest = candidate["closest_seed"]
    assert closest["exact_workspace_match"] is False
    assert closest["primary_text_distance"] > 0.0
    assert closest["numeric_metric_l1_distance"] > 0.0
    assert closest["shared_metric_names"] == ["score"]
    assert closest["changed_components"]["modified_file_count"] == 1
    assert closest["changed_components"]["modified_files"] == ["main.py"]


def test_runtime_history_records_whole_run_source_workspace_integrity():
    tmpdir = tempfile.mkdtemp()
    problem = _problem("def evaluate(c): return {'score': 0.5, 'is_valid': True}")
    problem.initial_programs = ["x = 1\n", "x = 2\n"]

    evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"][
        "whole_run_source_workspace_integrity_report"
    ]

    assert report["schema"] == (
        "libreevolve.whole_run_source_workspace_integrity_report.v1"
    )
    assert report["validation"]["ok"] is True
    assert validate_whole_run_source_workspace_integrity_report(report)["ok"] is True
    assert report["program_count"] == 2
    assert report["workspace_hash_count"] == 2
    assert report["primary_file_present_count"] == 2
    assert report["program_records_truncated"] is False
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["all_retained_program_workspaces_hashed"] is True
    assert report["claim_readiness"]["primary_file_coherence_checked"] is True
    assert report["claim_readiness"]["whole_run_cli_query_surface"] is False
    assert report["claim_readiness"]["full_source_payload_replay"] is False

    program_records = report["program_records"]
    assert [record["candidate_type"] for record in program_records] == ["seed", "seed"]
    assert all(record["primary_file_present"] is True for record in program_records)
    assert all(len(record["workspace_sha256"]) == 64 for record in program_records)
    assert len({record["workspace_sha256"] for record in program_records}) == 2
    assert report["runtime_artifact_count"] >= 9
    artifact_names = {record["name"] for record in report["runtime_artifacts"]}
    assert {"history.jsonl", "best.py", "best_workspace"}.issubset(artifact_names)
    assert report["runtime_artifact_hash_count"] >= 2

    overclaimed = copy.deepcopy(report)
    overclaimed["integrity_scope"]["raw_source_payload_replay"] = True
    overclaimed["claim_readiness"]["whole_run_cli_query_surface"] = True
    validation = validate_whole_run_source_workspace_integrity_report(overclaimed)
    assert validation["ok"] is False
    assert {
        "raw_source_replay_overclaim",
        "whole_run_cli_query_surface_overclaim",
    }.issubset({issue["code"] for issue in validation["issues"]})


def test_completed_runtime_records_no_llm_scheduler_for_zero_generation_run():
    tmpdir = tempfile.mkdtemp()

    evolve(_problem(), Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["runtime"]["llm_scheduler"] == {
        "status": "not_initialized",
        "reason": "no_mutation_llm_was_constructed",
    }
    assert manifest["runtime"]["llm_accounting"] == {
        "status": "not_initialized",
        "schema": "libreevolve.llm_accounting.v1",
        "policy": "audit_summary_not_budget_enforced",
        "reason": "no_mutation_llm_was_constructed",
    }
    assert manifest["runtime"]["llm_provider_diagnostics"] == {
        "schema": LLM_PROVIDER_DIAGNOSTICS_SCHEMA,
        "status": "not_initialized",
        "reason": "no_mutation_llm_was_constructed",
    }


def test_runtime_history_records_gemini_provider_parity_boundary():
    tmpdir = tempfile.mkdtemp()
    backends = [
        {"type": "openai", "model": "gpt-5", "role": "general"},
        {
            "type": "custom",
            "model": "gemini-2.0-flash",
            "class_path": "example.backends:GeminiFlashBackend",
            "role": "breadth",
        },
        {
            "type": "custom",
            "model": "gemini-2.0-pro",
            "class_path": "example.backends:GeminiProBackend",
            "role": "depth",
        },
    ]

    evolve(
        _problem(),
        Config(
            max_generations=0,
            log_dir=tmpdir,
            problem_name="t",
            backends=backends,
        ),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["gemini_provider_parity_report"]

    assert report["schema"] == "libreevolve.gemini_provider_parity_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_gemini_provider_parity_report(report)["ok"] is True
    assert report["built_in_backend_types"] == ["anthropic", "ollama", "openai"]
    assert report["gemini_builtin_available"] is False
    assert report["configured_backend_count"] == 3
    assert report["configured_custom_backend_count"] == 2
    assert report["configured_gemini_like_backend_count"] == 2
    assert report["configured_flash_lane_count"] == 1
    assert report["configured_pro_lane_count"] == 1
    assert report["provider_parity_status"] == "missing_first_class_gemini_backend"
    assert report["substitution_status"] == (
        "custom_gemini_like_backend_configured_without_first_class_parity"
    )
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["credential_preflight"] is False
    assert report["claim_readiness"]["provider_native_usage_telemetry"] is False
    assert report["claim_readiness"]["substitution_contract"] is False
    assert report["configured_backends"][1]["provider_family"] == "gemini"
    assert report["configured_backends"][1]["lane"] == "flash"
    assert report["configured_backends"][1]["first_class_provider"] is False


def test_completed_runtime_records_valid_provider_cancellation_policy():
    tmpdir = tempfile.mkdtemp()

    evolve(
        _problem(),
        Config(
            max_generations=0,
            log_dir=tmpdir,
            problem_name="t",
            llm_call_timeout_sec=0.25,
            max_runtime_seconds=10.0,
        ),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    record = manifest["runtime"]["provider_cancellation_policy"]
    policy = record["policy"]
    validation = validate_provider_cancellation_policy(policy)

    assert record["status"] == "valid"
    assert record["validation"]["ok"] is True
    assert validation.ok is True
    assert validation.hard_cancel_ready is False
    assert policy["hard_cancel_ready"] is False
    assert policy["configured_limits"]["llm_call_timeout_sec"] == 0.25
    assert policy["configured_limits"]["max_runtime_seconds"] == 10.0
    assert policy["configured_limits"]["llm_role_failure_quarantine_after"] == {}
    assert record["observations"] == {
        "schema": "libreevolve.provider_cancellation_observations.v1",
        "source": "runtime.llm_scheduler",
        "status": "not_initialized",
        "reason": "no_mutation_llm_was_constructed",
    }
    assert policy["role_scope"] == {
        "policy": "libreevolve.llm_timeout_role_scope.v1",
        "roles": ["mutation", "critique", "feedback:*", "meta_prompt"],
        "source": "loop_llm_generate_roles",
    }
    assert policy["runtime_readiness"] == {
        "schema": "libreevolve.provider_cancellation_runtime_readiness.v1",
        "live_provider_sdk_cancellation": False,
        "timeout_driven_stop_enforcement": False,
        "cross_run_provider_quarantine_resume": False,
        "remaining_gap": [
            "live_provider_sdk_cancellation",
            "timeout_driven_stop_enforcement",
            "cross_run_provider_quarantine_resume",
        ],
    }
    timeout_rules = policy["rules"][:-1]
    runtime_rule = policy["rules"][-1]
    assert len(timeout_rules) == 8
    assert record["validation"]["rule_count"] == 9
    assert {
        (rule["kind"], rule["role"])
        for rule in timeout_rules
    } == {
        ("provider_request_timeout", "mutation"),
        ("provider_request_timeout", "critique"),
        ("provider_request_timeout", "feedback:*"),
        ("provider_request_timeout", "meta_prompt"),
        ("ensemble_wait_deadline", "mutation"),
        ("ensemble_wait_deadline", "critique"),
        ("ensemble_wait_deadline", "feedback:*"),
        ("ensemble_wait_deadline", "meta_prompt"),
    }
    assert all(rule["budget_actions"] == ["retry", "fallback"] for rule in timeout_rules)
    assert all(rule["artifact_kinds"] == ["timeout_log"] for rule in timeout_rules)
    assert runtime_rule["kind"] == "runtime_deadline"
    assert runtime_rule["budget_actions"] == ["stop_run"]
    assert runtime_rule["artifact_kinds"] == ["budget_stop_record"]
    assert all(rule["artifact_required"] is True for rule in policy["rules"])
    assert {artifact["kind"] for artifact in policy["artifacts"]} == {
        "timeout_log",
        "quarantine_record",
        "budget_stop_record",
    }

    forged = copy.deepcopy(policy)
    forged["runtime_readiness"]["live_provider_sdk_cancellation"] = True
    forged["runtime_readiness"]["timeout_driven_stop_enforcement"] = True
    forged["runtime_readiness"]["cross_run_provider_quarantine_resume"] = True
    forged_validation = validate_provider_cancellation_policy(forged)
    forged_codes = {issue.code for issue in forged_validation.issues}

    assert forged_validation.ok is False
    assert "live_provider_sdk_cancellation_overclaim" in forged_codes
    assert "timeout_driven_stop_enforcement_overclaim" in forged_codes
    assert "cross_run_provider_quarantine_resume_overclaim" in forged_codes


def test_provider_cancellation_policy_records_configured_timeout_quarantine():
    tmpdir = tempfile.mkdtemp()

    evolve(
        _problem(),
        Config(
            max_generations=0,
            log_dir=tmpdir,
            problem_name="t",
            llm_call_timeout_sec=0.25,
            llm_role_failure_quarantine_after={
                "feedback:grader": 2,
                "mutation": 1,
            },
        ),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    record = manifest["runtime"]["provider_cancellation_policy"]
    policy = record["policy"]

    assert record["status"] == "valid"
    assert validate_provider_cancellation_policy(policy).ok is True
    assert policy["configured_limits"]["llm_role_failure_quarantine_after"] == {
        "feedback:grader": 2,
        "mutation": 1,
    }
    timeout_rules = {
        (rule["kind"], rule["role"]): rule
        for rule in policy["rules"]
        if rule["kind"] in {"provider_request_timeout", "ensemble_wait_deadline"}
    }
    for kind in ("provider_request_timeout", "ensemble_wait_deadline"):
        mutation_rule = timeout_rules[(kind, "mutation")]
        feedback_rule = timeout_rules[(kind, "feedback:*")]
        critique_rule = timeout_rules[(kind, "critique")]
        assert mutation_rule["budget_actions"] == ["retry", "fallback", "quarantine"]
        assert mutation_rule["artifact_kinds"] == [
            "timeout_log",
            "quarantine_record",
        ]
        assert feedback_rule["budget_actions"] == ["retry", "fallback", "quarantine"]
        assert feedback_rule["artifact_kinds"] == [
            "timeout_log",
            "quarantine_record",
        ]
        assert critique_rule["budget_actions"] == ["retry", "fallback"]
        assert critique_rule["artifact_kinds"] == ["timeout_log"]
    assert {artifact["kind"] for artifact in policy["artifacts"]} == {
        "timeout_log",
        "quarantine_record",
        "budget_stop_record",
    }


def test_provider_cancellation_policy_observes_timeout_quarantine_state():
    class TimeoutBackend:
        name = "timeout/model"
        api_mode = "chat"

        def generate(self, prompt, **kwargs):
            raise TimeoutError("provider timeout")

    llm = LLMEnsemble(
        [TimeoutBackend()],
        fallback=False,
        role_failure_quarantine_after={"mutation": 1},
    )
    with pytest.raises(TimeoutError):
        llm.generate("prompt", role="mutation")

    scheduler = _runtime_llm_scheduler_state(llm)
    record = _runtime_provider_cancellation_policy(
        Config(
            llm_call_timeout_sec=0.25,
            llm_role_failure_quarantine_after={"mutation": 1},
        ),
        scheduler,
    )

    observations = record["observations"]
    assert record["status"] == "valid"
    assert observations == {
        "schema": "libreevolve.provider_cancellation_observations.v1",
        "source": "runtime.llm_scheduler",
        "status": "snapshot",
        "timeout_failures_total": 1,
        "timeout_failures_by_role": {"mutation": 1},
        "quarantine_thresholds": {"mutation": 1},
        "quarantined_backend_count": 1,
        "quarantined_backends_by_role": {"mutation": 1},
        "hard_cancel_runtime_enforcement": "unsupported",
        "timeout_stop_runtime_enforcement": "unsupported",
        "remaining_gap": (
            "timeout observations are audit evidence only; SDK hard "
            "cancellation handles and timeout-driven stop policies remain open"
        ),
    }


def test_completed_runtime_records_lineage_replay_policy():
    tmpdir = tempfile.mkdtemp()

    evolve(_problem(), Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    policy = manifest["runtime"]["lineage_replay_policy"]

    assert policy["schema"] == "libreevolve.lineage_replay_policy.v1"
    assert (
        policy["policy"]
        == "deterministic_loop_ids_with_explicit_external_boundaries"
    )
    assert policy["loop_created_program_ids"] == {
        "seed_candidates": "deterministic_seed_index_workspace_hash",
        "generated_candidates": (
            "deterministic_generation_loop_index_proposal_parent_prompt_"
            "mutation_workspace_hash"
        ),
        "direct_program_default": "uuid4_excluded_from_replay_contract",
    }
    assert policy["prompt_program_ids"][
        "direct_prompt_program_default"
    ] == "uuid4_excluded_from_replay_contract"
    assert policy["provider_boundary"] == {
        "provider_outputs_replayed": False,
        "provider_nondeterminism": "remote_or_sdk_outputs_not_replayed",
        "call_ids_do_not_prove_same_provider_output": True,
    }
    assert policy["llm_call_ids"]["provider_output_replay"] == "not_supported"
    assert "runtime_rng_snapshot" in policy["covered_restore_surfaces"]
    assert "provider/model outputs" in policy["excluded_surfaces"]
    assert policy["full_replay_ready"] is False


def test_runtime_lineage_replay_policy_manifest_loading():
    tmpdir = tempfile.mkdtemp()

    evolve(_problem(), Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest_path = Path(tmpdir) / "t" / "manifest.json"
    loaded = load_runtime_lineage_replay_policy_snapshot(manifest_path)

    assert loaded["schema"] == "libreevolve.lineage_replay_policy.v1"
    assert loaded["provider_boundary"]["provider_outputs_replayed"] is False
    assert loaded["llm_call_ids"]["provider_output_replay"] == "not_supported"
    assert loaded["full_replay_ready"] is False


def test_lineage_replay_policy_rejects_provider_output_overclaim():
    tmpdir = tempfile.mkdtemp()

    evolve(_problem(), Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    policy = manifest["runtime"]["lineage_replay_policy"]
    policy["provider_boundary"]["provider_outputs_replayed"] = True

    with pytest.raises(RuntimeLineageReplayPolicyError, match="overclaims"):
        validate_runtime_lineage_replay_policy(policy)


def test_completed_runtime_persists_archive_state_cursor_snapshot():
    tmpdir = tempfile.mkdtemp()

    evolve(
        _problem(),
        Config(max_generations=0, log_dir=tmpdir, problem_name="t", n_islands=3),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    archive_state = manifest["runtime"]["history"]["archive_state"]
    assert archive_state["schema"] == "libreevolve.island_state.v1"
    assert archive_state["resume_status"] == (
        "snapshot_persisted_cursor_and_full_archive_restore_supported"
    )
    assert archive_state["cursor_policy"] == "advance_only_on_search_state_changed"
    assert archive_state["n_islands"] == 3
    assert archive_state["next_island_id"] == 1
    assert archive_state["archive_sequence"] == 1
    assert archive_state["migration_sequence"] == 0
    assert archive_state["metric_sample_index"] == 0
    assert archive_state["frontier_sample_index"] == 0
    assert archive_state["lineage_sample_index"] == 0
    assert len(archive_state["archive_sequence_by_program_id"]) == 1
    assert archive_state["topology_policy"] == {
        "schema": "libreevolve.island_topology_policy.v1",
        "status": "configured_synchronous_ring_topology",
        "policy": "config_n_islands_controls_local_synchronous_ring_migration_default_five",
        "configured_n_islands": 3,
        "default_n_islands": 5,
        "island_count_configurable": True,
        "migration_topology": "ring",
        "migration_execution": "synchronous_local_generation_boundary",
        "adaptive_island_count_supported": False,
        "non_ring_topologies_supported": False,
        "alphaevolve_policy_ready": False,
        "limitations": [
            "no_adaptive_island_count_policy",
            "no_non_ring_migration_topology",
            "no_topology_specific_ablation_evidence",
            "not_claimed_as_alphaevolve_identical_policy",
        ],
    }
    assert archive_state["islands"][0]["occupied_cell_count"] == 1
    assert archive_state["islands"][1]["occupied_cell_count"] == 0
    assert archive_state["islands"][2]["occupied_cell_count"] == 0
    replay_audit = manifest["runtime"]["history"]["archive_event_replay_audit"]
    assert replay_audit["schema"] == "libreevolve.archive_event_replay_audit.v1"
    assert replay_audit["status"] == "no_migration_placements"
    assert replay_audit["audit_only"] is True
    assert replay_audit["replay_engine_supported"] is False
    assert replay_audit["event_count"] == 0
    controller_state = manifest["runtime"]["history"]["controller_state"]
    assert controller_state["schema"] == "libreevolve.controller_state.v1"
    assert controller_state["status"] == "terminal_synchronous_controller_drained"
    assert controller_state["controller_model"] == "single_process_serial_loop"
    assert controller_state["resume_scope"] == "terminal_drained_state_only"
    assert controller_state["pending_work"] == {
        "queued_proposals": 0,
        "running_proposals": 0,
        "queued_evaluations": 0,
        "running_evaluations": 0,
        "in_flight_llm_calls": 0,
        "pending_archive_admissions": 0,
        "partially_completed_generation": False,
    }
    assert controller_state["terminal"]["stop_reason"] == "max_generations"
    assert controller_state["event_stream"] == {
        "path": "controller_budget_events.jsonl",
        "status": "present",
        "event_count": 2,
        "last_sequence": 1,
        "last_kind": "stop",
        "replay_scope": "budget_counters_only",
    }
    validation = controller_state["validation"]
    assert validation["schema"] == CONTROLLER_STATE_VALIDATION_SCHEMA
    assert validation["controller_state_schema"] == "libreevolve.controller_state.v1"
    assert validation["ok"] is True
    assert validation["status"] == "verified"
    assert validation["terminal_drained"] is True
    assert validation["pending_work_count"] == 0
    assert validation["overclaim_count"] == 0
    assert validation["invalid_count"] == 0
    assert len(validation["records_sha256"]) == 64
    assert validation["issues"] == []
    assert validation["record"]["event_stream_status"] == "present"
    assert validation["record"]["event_count"] == 2
    topology = manifest["runtime"]["history"]["distributed_pipeline_topology_report"]
    assert topology["schema"] == "libreevolve.distributed_pipeline_topology_report.v1"
    assert topology["validation"]["ok"] is True
    assert validate_distributed_pipeline_topology_report(topology)["ok"] is True
    assert topology["queue_count"] == 0
    assert topology["queues"] == []
    assert topology["dispatch_policy"]["asyncio_pipeline"] is False
    assert topology["pending_work_checkpoint"]["supported"] is False
    assert topology["claim_ready"] is False
    assert topology["claim_readiness"]["controller_sampler_evaluator_roles_named"] is True
    assert topology["claim_readiness"]["alphaevolve_async_pipeline_topology"] is False
    assert {node["role"] for node in topology["nodes"]} >= {
        "controller",
        "program_database",
        "llm_sampler",
        "evaluation_node",
    }
    assert all(edge["blocking"] is True for edge in topology["blocking_edges"])
    assert all(edge["queue"] is None for edge in topology["blocking_edges"])

    edited = copy.deepcopy(topology)
    edited["dispatch_policy"]["asyncio_pipeline"] = True
    edited["pending_work_checkpoint"]["supported"] = True
    edited["nodes"][0]["async_worker"] = True
    edited["claim_ready"] = True
    edited["claim_readiness"]["alphaevolve_async_pipeline_topology"] = True
    topology_validation = validate_distributed_pipeline_topology_report(edited)
    assert topology_validation["ok"] is False
    assert {
        "async_worker_overclaim",
        "async_pipeline_overclaim",
        "pending_checkpoint_overclaim",
        "claim_ready_overclaim",
        "async_topology_overclaim",
    }.issubset({issue["code"] for issue in topology_validation["issues"]})


def test_pipeline_topology_records_configured_evaluator_sample_workers(tmp_path):
    problem = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    return {'score': (stage['sample_index'] + 1) / 3, 'is_valid': True}\n",
    )

    evolve(
        problem,
        Config(
            max_generations=0,
            log_dir=str(tmp_path),
            problem_name="sample_workers",
            eval_stages=[
                {
                    "name": "sampled",
                    "samples": 2,
                    "sample_workers": 2,
                }
            ],
        ),
    )

    manifest = json.loads(
        (tmp_path / "sample_workers" / "manifest.json").read_text(encoding="utf-8")
    )
    topology = manifest["runtime"]["history"]["distributed_pipeline_topology_report"]

    assert topology["validation"]["ok"] is True
    assert topology["dispatch_policy"]["evaluation_dispatch"] == (
        "blocking_stage_sample_thread_pool_local_subprocess"
    )
    assert topology["dispatch_policy"]["evaluator_sample_workers"]["configured"] is True
    assert topology["dispatch_policy"]["evaluator_sample_workers"]["max_effective_workers"] == 2
    assert topology["throughput_budget_linkage"]["worker_fanout_accounted"] is True
    assert topology["throughput_budget_linkage"]["worker_fanout_accounting_scope"] == (
        "configured_stage_sample_workers"
    )
    assert topology["throughput_budget_linkage"]["evaluator_stage_samples"] == 2
    assert topology["claim_readiness"]["worker_identity_and_fanout"] is True
    evaluator_nodes = [
        node for node in topology["nodes"] if node["role"] == "evaluation_node"
    ]
    assert evaluator_nodes[0]["worker_identity"] == (
        "process_main_thread_spawns_subprocess_thread_pool"
    )
    assert evaluator_nodes[0]["sample_workers"] == {
        "requested_workers": 2,
        "effective_workers": 2,
        "samples": 2,
        "dispatch": "thread_pool",
    }
    process_report = manifest["runtime"]["history"]["alphaevolve_process_exhibit_report"]
    assert process_report["validation"]["ok"] is True
    evaluator_pool = process_report["evaluator_pool_parallelism_record"]
    assert evaluator_pool["evaluation_dispatch"] == (
        "blocking_stage_sample_thread_pool_local_subprocess"
    )
    assert evaluator_pool["parallel_evaluator_workers"] is True
    assert evaluator_pool["parallelism_scope"] == "configured_stage_sample_workers"
    assert evaluator_pool["independent_evaluator_pool_parallelism"] is False
    assert evaluator_pool["compute_hour_wall_clock_compression"] is True
    compression = evaluator_pool["wall_clock_compression"]
    assert compression["wall_clock_compression_observed"] is True
    assert compression["observed_record_count"] >= 1
    assert compression["max_wall_clock_compression_ratio"] > 1.0
    assert compression["claim_scope"] == (
        "local_configured_stage_sample_worker_wall_clock_compression"
    )


def test_runtime_history_records_parallel_evaluation_readiness_boundary(tmp_path):
    problem = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    import time\n"
        "    time.sleep(0.05)\n"
        "    return {'score': (stage['sample_index'] + 1) / 3, 'is_valid': True}\n",
    )

    evolve(
        problem,
        Config(
            max_generations=0,
            log_dir=str(tmp_path),
            problem_name="parallel_readiness",
            eval_stages=[
                {
                    "name": "sampled",
                    "samples": 3,
                    "sample_workers": 3,
                    "timeout_sec": 1.0,
                    "seeds": [101, 102, 103],
                }
            ],
        ),
    )

    manifest = json.loads(
        (tmp_path / "parallel_readiness" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    report = manifest["runtime"]["history"]["parallel_evaluation_readiness_report"]

    assert report["schema"] == "libreevolve.parallel_evaluation_readiness_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_parallel_evaluation_readiness_report(report)["ok"] is True
    assert report["configured_stage_count"] == 1
    assert report["configured_sample_worker_stage_count"] == 1
    assert report["configured_stage_sample_count"] == 3
    assert report["configured_max_effective_workers"] == 3
    assert report["observed_evaluated_candidate_count"] == 1
    assert report["observed_configured_stage_candidate_count"] == 1
    assert report["observed_sample_execution_record_count"] == 1
    assert report["observed_parallel_sample_worker_record_count"] == 1
    assert report["observed_wall_clock_compression_record_count"] == 1
    assert report["observed_max_wall_clock_compression_ratio"] > 1.0
    assert report["compute_hour_budget"] == {
        "per_candidate_compute_hour_budget_declared": False,
        "local_timeout_budget_seconds_available": True,
        "local_timeout_budget_scope": "stage_sample_wall_clock_timeout_not_compute_hours",
        "observed_sample_elapsed_sec_sum": report["observed_sample_elapsed_sec_sum"],
        "observed_wall_clock_elapsed_sec_sum": report["observed_wall_clock_elapsed_sec_sum"],
    }
    assert report["async_pipeline_state"] == {
        "candidate_level_evaluation_queue": False,
        "distributed_evaluator_nodes": False,
        "pending_work_resume": False,
        "mutation_chain_depth_preserved_under_slow_feedback": False,
    }
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["local_stage_sample_worker_fanout"] is True
    assert report["claim_readiness"]["wall_clock_compression_observed"] is True
    assert report["claim_readiness"]["candidate_level_async_evaluation"] is False
    assert report["candidate_records"][0]["sample_execution_records"][0]["mode"] == (
        "thread_pool"
    )

    overclaimed = copy.deepcopy(report)
    overclaimed["compute_hour_budget"]["per_candidate_compute_hour_budget_declared"] = True
    overclaimed["async_pipeline_state"]["distributed_evaluator_nodes"] = True
    validation = validate_parallel_evaluation_readiness_report(overclaimed)
    assert validation["ok"] is False
    assert {
        "compute_hour_budget_overclaim",
        "distributed_evaluator_nodes_overclaim",
    }.issubset({issue["code"] for issue in validation["issues"]})


def test_validate_controller_state_snapshot_reports_overclaims_and_pending_work():
    controller_state = {
        "schema": "libreevolve.controller_state.v1",
        "status": "terminal_synchronous_controller_drained",
        "controller_model": "single_process_serial_loop",
        "resume_scope": "terminal_drained_state_only",
        "pending_work": {
            "queued_proposals": 1,
            "running_proposals": 0,
            "queued_evaluations": 0,
            "running_evaluations": 0,
            "in_flight_llm_calls": 0,
            "pending_archive_admissions": 0,
            "partially_completed_generation": False,
        },
        "terminal": {
            "stop_reason": "max_generations",
            "generations_completed": 1,
            "evaluations": 2,
        },
        "event_stream": {
            "path": "controller_budget_events.jsonl",
            "status": "present",
            "event_count": 2,
            "last_sequence": 1,
            "last_kind": "stop",
            "replay_scope": "full_controller_replay",
        },
        "async_resume_ready": True,
        "pending_work_resume_ready": False,
        "full_replay_ready": True,
        "provider_output_replay_ready": False,
        "limitations": [
            "synchronous_terminal_snapshot_not_async_queue_checkpoint",
            "no_mid_generation_resume_boundary",
            "provider_outputs_not_replayed",
        ],
    }

    validation = validate_controller_state_snapshot(controller_state)

    assert validation["schema"] == CONTROLLER_STATE_VALIDATION_SCHEMA
    assert validation["ok"] is False
    assert validation["status"] == "overclaim"
    assert validation["terminal_drained"] is False
    assert validation["pending_work_count"] == 1
    assert validation["overclaim_count"] == 1
    assert validation["invalid_count"] == 0
    assert "controller_pending_work_not_drained" in validation["issues"]
    assert "async_resume_ready_overclaimed" in validation["issues"]
    assert "full_replay_ready_overclaimed" in validation["issues"]
    assert "event_stream_replay_scope_overclaimed" in validation["issues"]

    invalid = validate_controller_state_snapshot("bad")

    assert invalid["ok"] is False
    assert invalid["status"] == "invalid_record"
    assert invalid["invalid_count"] == 1
    assert invalid["issues"] == ["invalid_controller_state"]


def test_controller_state_artifact_inventory_verifies_event_stream(tmp_path):
    backend = MagicMock()
    backend.name = "controller/model"
    backend.api_mode = None
    backend.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    with patch("libreevolve.core.loop.build_llm", return_value=LLMEnsemble([backend])):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=str(tmp_path), problem_name="source"),
        )

    run_dir = tmp_path / "source"
    manifest_path = run_dir / "manifest.json"

    inventory = controller_state_artifact_inventory(manifest_path, run_dir)

    assert inventory["schema"] == CONTROLLER_STATE_ARTIFACT_INVENTORY_SCHEMA
    assert inventory["controller_state_schema"] == "libreevolve.controller_state.v1"
    assert inventory["artifact_root_policy"] == (
        "safe_relative_controller_artifact_paths_under_artifact_root"
    )
    assert inventory["ok"] is True
    assert inventory["artifact_count"] == 1
    assert inventory["verified_count"] == 1
    assert inventory["missing_count"] == 0
    assert inventory["mismatch_count"] == 0
    assert inventory["invalid_count"] == 0
    assert len(inventory["records_sha256"]) == 64
    [record] = inventory["artifacts"]
    assert record["path"] == "controller_budget_events.jsonl"
    assert record["status"] == "verified"
    assert record["actual_event_count"] == 6
    assert record["actual_last_kind"] == "stop"


def test_controller_state_artifact_inventory_reports_bad_references(tmp_path):
    backend = MagicMock()
    backend.name = "controller/model"
    backend.api_mode = None
    backend.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    with patch("libreevolve.core.loop.build_llm", return_value=LLMEnsemble([backend])):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=str(tmp_path), problem_name="source"),
        )

    run_dir = tmp_path / "source"
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    state = manifest["runtime"]["history"]["controller_state"]
    state["event_stream"]["event_count"] = 999
    state["event_stream"]["last_kind"] = "candidate_evaluation"
    artifact = manifest["runtime"]["artifacts"]["controller_budget_events.jsonl"]
    artifact["sha256"] = "0" * 64
    artifact["bytes"] = 999

    inventory = controller_state_artifact_inventory(manifest, run_dir)

    assert inventory["ok"] is False
    assert inventory["mismatch_count"] == 1
    [record] = inventory["artifacts"]
    assert record["status"] == "hash_mismatch"
    assert "controller_event_artifact_hash_mismatch" in record["issues"]
    assert "controller_event_artifact_bytes_mismatch" in record["issues"]
    assert "controller_event_count_mismatch" in record["issues"]
    assert "controller_last_kind_mismatch" in record["issues"]

    state["event_stream"]["path"] = "../escape.jsonl"
    unsafe = controller_state_artifact_inventory(manifest, run_dir)
    assert unsafe["ok"] is False
    assert unsafe["invalid_count"] == 1
    assert unsafe["artifacts"][0]["status"] == "unsafe_path"

    state["event_stream"]["path"] = "missing-controller-events.jsonl"
    missing = controller_state_artifact_inventory(manifest, run_dir)
    assert missing["ok"] is False
    assert missing["missing_count"] == 1
    assert missing["artifacts"][0]["status"] == "missing_file"


def test_completed_runtime_persists_llm_scheduler_state_snapshot():
    tmpdir = tempfile.mkdtemp()
    backend = MagicMock()
    backend.name = "scheduler/model"
    backend.api_mode = None
    backend.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    llm = LLMEnsemble([backend])

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    scheduler = manifest["runtime"]["llm_scheduler"]
    assert scheduler["status"] == "snapshot"
    assert scheduler["schema"] == "libreevolve.llm_scheduler_state.v1"
    assert scheduler["restore_entrypoint"] == "LLMEnsemble.restore_scheduler_state"
    assert scheduler["resume_status"] == "snapshot_persisted_restore_supported"
    assert scheduler["state"]["counts"] == [1]
    assert scheduler["state"]["wins"] == [0.0]
    assert scheduler["state"]["total"] == 1
    assert scheduler["state"]["unrewarded_success_call_ids"] == [[]]
    assert len(scheduler["state"]["rewarded_call_ids"]) == 1
    assert scheduler["state"]["call_history_retention"]["total_records"] == 1
    assert scheduler["state"]["reward_accounting_policy"] == {
        "policy": "configured_reward_accounted_roles_v1",
        "reward_accounted_roles": ["mutation"],
    }
    assert scheduler["state"]["role_scheduler_scope"] == "shared"
    assert scheduler["state"]["role_call_limits"] == {
        "policy": "logical_generate_call_limits_by_role_v1",
        "max_calls_by_role": {},
        "logical_calls_by_role": {"mutation": 1},
    }
    assert scheduler["state"]["role_scheduler_state"]["mutation"]["counts"] == [1]
    assert scheduler["state"]["role_scheduler_state"]["mutation"]["wins"] == [0.0]
    assert scheduler["state"]["role_scheduler_state"]["mutation"]["total"] == 1
    assert scheduler["state"]["role_scheduler_state"]["mutation"][
        "rewarded_call_ids"
    ] == scheduler["state"]["rewarded_call_ids"]
    accounting = manifest["runtime"]["llm_accounting"]
    assert accounting["status"] == "snapshot"
    assert accounting["schema"] == "libreevolve.llm_accounting.v1"
    assert accounting["policy"] == "audit_summary_not_budget_enforced"
    assert accounting["source"] == (
        "llm_scheduler_state.role_accounting_and_role_scheduler_state"
    )
    assert accounting["limits"]["max_llm_calls"] is None
    assert accounting["limits"]["max_llm_provider_attempts"] is None
    assert accounting["limits"]["max_llm_tokens"] is None
    assert accounting["limits"]["max_llm_cost_microusd"] is None
    assert accounting["limits"]["max_llm_seconds"] is None
    assert accounting["limits"]["llm_role_call_limits"] == {}
    assert accounting["limits"]["llm_role_provider_attempt_limits"] == {}
    assert accounting["limits"]["llm_role_token_limits"] == {}
    assert accounting["limits"]["llm_role_cost_microusd_limits"] == {}
    assert accounting["limits"]["llm_role_seconds_limits"] == {}
    assert accounting["limits"]["llm_max_retries"] == 0
    assert accounting["limits"]["llm_max_call_attempts"] == 32
    assert accounting["limits"]["llm_fallback"] is True
    assert accounting["limits"]["prompt_max_chars"] is None
    assert accounting["limits"]["llm_reward_accounted_roles"] == ["mutation"]
    assert accounting["limits"]["llm_role_scheduler_scope"] == "shared"
    assert accounting["reward_accounting_policy"] == {
        "policy": "configured_reward_accounted_roles_v1",
        "reward_accounted_roles": ["mutation"],
    }
    assert accounting["role_scheduler_scope"] == "shared"
    assert accounting["role_accounting"]["mutation"]["calls"] == 1
    assert accounting["role_accounting"]["mutation"]["reward_accounted_calls"] == 1
    assert accounting["role_accounting"]["mutation"]["provider_internal_attempts"] == 0
    assert accounting["totals"]["calls"] == 1
    assert accounting["totals"]["reward_accounted_calls"] == 1
    assert accounting["totals"]["provider_internal_attempts"] == 0
    assert accounting["role_scheduler_state"]["mutation"]["counts"] == [1]
    assert accounting["role_scheduler_state"]["mutation"]["wins"] == [0.0]
    assert accounting["role_call_limits"] == {
        "policy": "logical_generate_call_limits_by_role_v1",
        "max_calls_by_role": {},
        "logical_calls_by_role": {"mutation": 1},
    }
    assert accounting["scheduler_totals"] == {
        "counts": [1],
        "wins": [0.0],
        "total": 1,
        "unrewarded_success_call_count": 0,
        "rewarded_call_count": 1,
    }
    budget_report = manifest["runtime"]["llm_budget_report"]
    budget_validation = validate_llm_budget_report(budget_report)
    assert budget_report["schema"] == LLM_BUDGET_REPORT_SCHEMA
    assert budget_report["status"] == LLM_BUDGET_REPORT_STATUS
    assert budget_report["policy"] == LLM_BUDGET_REPORT_POLICY
    assert budget_report["paper_budget_ready"] is False
    assert budget_report["role_scheduler_scope"] == "shared"
    assert budget_report["validation"]["ok"] is True
    assert budget_report["validation"]["paper_budget_ready"] is False
    assert budget_validation.ok is True
    assert budget_validation.paper_budget_ready is False
    assert budget_report["role_budgets"] == [
        {
            "role": "mutation",
            "logical_call_limit": 1,
            "retry_attempt_limit": 31,
            "adapter_attempt_limit": 0,
            "configured_adapter_attempt_limit": None,
            "configured_token_limit": None,
            "configured_cost_limit_usd": None,
            "configured_wall_clock_limit_seconds": None,
            "limit_source": {
                "logical_call_limit": "observed_role_calls",
                "retry_attempt_limit": (
                    "config.llm_max_call_attempts_times_observed_role_calls"
                ),
                "adapter_attempt_limit": "observed_provider_internal_attempts",
                "token_limit": "not_configured",
                "cost_limit_usd": "not_configured",
                "wall_clock_limit_seconds": "not_configured",
            },
        }
    ]
    role_usage = budget_report["role_usage"]
    assert len(role_usage) == 1
    assert role_usage[0].pop("wall_clock_seconds") >= 0.0
    assert role_usage == [
        {
            "role": "mutation",
            "logical_calls": 1,
            "retry_attempts": 0,
            "adapter_attempt_count": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "adapter_attempts": [],
            "adapter_attempt_policy": (
                "aggregate_only_provider_attempt_details_not_retained"
            ),
            "retained_adapter_attempt_count": 0,
        }
    ]
    assert budget_report["resume_state"]["persisted"] is True
    assert budget_report["resume_state"]["restored"] is False
    assert len(budget_report["resume_state"]["state_sha256"]) == 64


def test_runtime_persists_role_scoped_llm_scheduler_scope():
    tmpdir = tempfile.mkdtemp()
    backend = MagicMock()
    backend.name = "scheduler/model"
    backend.api_mode = None
    backend.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    llm = LLMEnsemble([backend], role_scheduler_scope="role_scoped")

    config = Config(
        max_generations=1,
        log_dir=tmpdir,
        problem_name="t",
        llm_role_scheduler_scope="role_scoped",
    )
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), config)

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["config"]["llm_role_scheduler_scope"] == "role_scoped"
    scheduler = manifest["runtime"]["llm_scheduler"]
    assert scheduler["state"]["role_scheduler_scope"] == "role_scoped"
    assert scheduler["state"]["role_scheduler_state"]["mutation"][
        "selection_policy"
    ] == "role_owned_bandit_selection_state"
    accounting = manifest["runtime"]["llm_accounting"]
    assert accounting["limits"]["llm_role_scheduler_scope"] == "role_scoped"
    assert accounting["role_scheduler_scope"] == "role_scoped"
    budget_report = manifest["runtime"]["llm_budget_report"]
    assert budget_report["role_scheduler_scope"] == "role_scoped"
    assert budget_report["validation"]["ok"] is True


def test_runtime_llm_budget_report_retains_provider_retry_attempts_by_role():
    tmpdir = tempfile.mkdtemp()

    class RetryingBackend:
        name = "retrying/model"
        api_mode = None
        provider_response_metadata = {
            "adapter_retry": {
                "policy": "bounded_provider_internal_retries",
                "max_retries": 2,
                "attempts": 3,
                "failed_attempts": 2,
                "failures": [
                    {"attempt": 0, "error_type": "TimeoutError"},
                    {"attempt": 1, "error_type": "RateLimitError"},
                ],
            },
        }

        def generate(self, prompt, **kwargs):
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    llm = LLMEnsemble([RetryingBackend()])

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["llm_budget_report"]
    usage = report["role_usage"][0]
    attempt = usage["adapter_attempts"][0]

    assert validate_llm_budget_report(report).ok is True
    assert usage["role"] == "mutation"
    assert usage["adapter_attempt_count"] == 3
    assert usage["retained_adapter_attempt_count"] == 3
    assert usage["adapter_attempt_policy"] == (
        "retained_call_history_provider_retry_details"
    )
    assert attempt["backend"] == "retrying/model"
    assert attempt["provider_max_retries"] == 2
    assert attempt["attempts"] == 3
    assert attempt["failed_attempts"] == 2
    assert attempt["status"] == "ok"
    assert attempt["failures"] == [
        {"attempt": 0, "error_type": "TimeoutError"},
        {"attempt": 1, "error_type": "RateLimitError"},
    ]


def test_runtime_llm_budget_report_uses_configured_provider_attempt_limit():
    tmpdir = tempfile.mkdtemp()

    class RetryingBackend:
        name = "retrying/model"
        api_mode = None
        provider_response_metadata = {
            "adapter_retry": {
                "policy": "bounded_provider_internal_retries",
                "max_retries": 2,
                "attempts": 3,
                "failed_attempts": 2,
                "failures": [
                    {"attempt": 0, "error_type": "TimeoutError"},
                    {"attempt": 1, "error_type": "RateLimitError"},
                ],
            },
        }

        def generate(self, prompt, **kwargs):
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    llm = LLMEnsemble([RetryingBackend()])

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                max_llm_provider_attempts=3,
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    runtime_budget = manifest["runtime"]
    report = manifest["runtime"]["llm_budget_report"]
    role_budget = report["role_budgets"][0]
    usage = report["role_usage"][0]

    assert manifest["config"]["max_llm_provider_attempts"] == 3
    assert manifest["runtime"]["llm_accounting"]["limits"][
        "max_llm_provider_attempts"
    ] == 3
    assert runtime_budget["limits"]["max_llm_provider_attempts"] == 3
    assert runtime_budget["consumed"]["llm_provider_attempts"] == 3
    assert runtime_budget["stop_reason"] == "max_llm_provider_attempts"
    assert validate_llm_budget_report(report).ok is True
    assert role_budget["adapter_attempt_limit"] == 3
    assert role_budget["configured_adapter_attempt_limit"] == 3
    assert role_budget["limit_source"]["adapter_attempt_limit"] == (
        "config.max_llm_provider_attempts_or_observed_inflight_overshoot"
    )
    assert usage["adapter_attempt_count"] == 3


def test_runtime_llm_budget_report_uses_configured_provider_cost_rate():
    tmpdir = tempfile.mkdtemp()

    class UsageBackend:
        name = "usage/model"
        api_mode = None
        provider_response_metadata = {
            "usage": {
                "input_tokens": 400,
                "output_tokens": 1600,
                "total_tokens": 2000,
            },
        }

        def generate(self, prompt, **kwargs):
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    llm = LLMEnsemble(
        [UsageBackend()],
        backend_metadata=[{"cost_usd_per_million_tokens": 5.0}],
    )

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    accounting = manifest["runtime"]["llm_accounting"]
    usage = manifest["runtime"]["llm_budget_report"]["role_usage"][0]

    assert accounting["role_accounting"]["mutation"]["total_tokens"] == 2000
    assert accounting["role_accounting"]["mutation"]["cost_microusd"] == 10000
    assert usage["total_tokens"] == 2000
    assert usage["cost_usd"] == 0.01
    llm_rows = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "llm_calls.jsonl").read_text().splitlines()
    ]
    llm_call = next(row for row in llm_rows if row["record_type"] == "call")
    cost_estimate = llm_call["cost_estimate"]
    cost_estimate_status = llm_call["cost_estimate_status"]
    assert cost_estimate["pricing_source"] == "configured_backend_metadata"
    assert (
        cost_estimate["pricing_status"]
        == "configured_estimate_not_live_provider_pricing"
    )
    assert (
        cost_estimate["token_count_source"]
        == "provider_response_metadata.usage.total_tokens"
    )
    assert cost_estimate_status["status"] == "estimated"
    assert (
        cost_estimate_status["reason"]
        == "estimated_from_configured_rate_and_provider_total_tokens"
    )
    assert cost_estimate_status["live_pricing_status"] == "not_fetched"
    diagnostics = manifest["runtime"]["llm_provider_diagnostics"]
    assert diagnostics["pricing_readiness"] == {
        "schema": "libreevolve.llm_provider_pricing_readiness.v1",
        "live_provider_pricing": False,
        "provider_default_rate_capture": False,
        "account_model_specific_pricing": False,
        "remaining_gap": [
            "live_provider_pricing",
            "provider_default_rate_capture",
            "account_model_specific_pricing",
        ],
    }


def test_loop_persists_replayable_controller_llm_budget_events():
    tmpdir = tempfile.mkdtemp()

    class UsageBackend:
        name = "usage/model"
        api_mode = None
        provider_response_metadata = {
            "usage": {
                "input_tokens": 400,
                "output_tokens": 1600,
                "total_tokens": 2000,
            },
            "adapter_retry": {
                "policy": "bounded_provider_internal_retries",
                "max_retries": 2,
                "attempts": 3,
                "failed_attempts": 2,
                "failures": [
                    {"attempt": 0, "error_type": "TimeoutError"},
                    {"attempt": 1, "error_type": "RateLimitError"},
                ],
            },
        }

        def generate(self, prompt, **kwargs):
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    llm = LLMEnsemble(
        [UsageBackend()],
        backend_metadata=[{"cost_usd_per_million_tokens": 5.0}],
    )
    config = Config(max_generations=1, log_dir=tmpdir, problem_name="t")

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), config)

    run_dir = Path(tmpdir) / "t"
    events = [
        json.loads(line)
        for line in (run_dir / "controller_budget_events.jsonl").read_text().splitlines()
    ]
    validated_events = [validate_controller_budget_event(event) for event in events]
    assert [event["sequence"] for event in validated_events] == list(
        range(len(validated_events))
    )
    assert [event["kind"] for event in validated_events] == [
        "seed_evaluation",
        "generation_started",
        "llm_call",
        "candidate_evaluation",
        "generation_completed",
        "stop",
    ]
    llm_event = validated_events[2]
    assert llm_event["schema"] == "libreevolve.controller_budget_event.v1"
    assert llm_event["role"] == "mutation"
    assert llm_event["provider_attempts"] == 3
    assert llm_event["tokens"] == 2000
    assert llm_event["cost_microusd"] == 10000
    assert llm_event["seconds"] > 0
    assert validated_events[-1]["stop_reason"] == "max_generations"

    replay_budget = RunBudget.from_config(config)
    for event in validated_events:
        apply_controller_budget_event(replay_budget, event)
    replay_consumed = replay_budget.snapshot()["consumed"]
    manifest = json.loads((run_dir / "manifest.json").read_text())
    consumed = manifest["runtime"]["consumed"]
    assert replay_budget.stop_reason == manifest["runtime"]["stop_reason"]
    assert replay_consumed["evaluations"] == consumed["evaluations"]
    assert replay_consumed["seed_evaluations"] == consumed["seed_evaluations"]
    assert replay_consumed["candidate_evaluations"] == consumed["candidate_evaluations"]
    assert replay_consumed["generations_started"] == consumed["generations_started"]
    assert replay_consumed["generations_completed"] == consumed["generations_completed"]
    assert replay_consumed["llm_calls"] == consumed["llm_calls"]
    assert replay_consumed["llm_provider_attempts"] == consumed["llm_provider_attempts"]
    assert replay_consumed["llm_tokens"] == consumed["llm_tokens"]
    assert replay_consumed["llm_cost_microusd"] == consumed["llm_cost_microusd"]
    assert replay_consumed["llm_provider_attempts_by_role"] == {
        "mutation": consumed["llm_provider_attempts"]
    }
    assert manifest["runtime"]["artifacts"]["controller_budget_events.jsonl"][
        "exists"
    ] is True
    assert manifest["runtime"]["artifacts"]["controller_budget_events.jsonl"]["sha256"]


def test_load_full_resume_bundle_composes_checked_runtime_restore_surfaces(tmp_path):
    class UsageBackend:
        name = "usage/model"
        api_mode = None
        provider_response_metadata = {
            "usage": {
                "input_tokens": 1,
                "output_tokens": 2,
                "total_tokens": 3,
            },
        }

        def generate(self, prompt, **kwargs):
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    with patch("libreevolve.core.loop.build_llm", return_value=LLMEnsemble([UsageBackend()])):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=str(tmp_path),
                problem_name="source",
                seed=99,
            ),
        )

    manifest_path = tmp_path / "source" / "manifest.json"
    bundle = load_full_resume_bundle(manifest_path)
    kwargs = bundle["evolve_kwargs"]

    assert bundle["schema"] == "libreevolve.full_resume_bundle.v1"
    assert bundle["restore_entrypoint"] == "evolve"
    assert bundle["manifest_name"] == "manifest.json"
    assert bundle["history_name"] == "history.jsonl"
    assert bundle["controller_budget_events_name"] == "controller_budget_events.jsonl"
    assert bundle["bundle_validation"]["schema"] == (
        FULL_RESUME_BUNDLE_VALIDATION_SCHEMA
    )
    assert bundle["bundle_validation"]["ok"] is True
    assert bundle["bundle_validation"]["compatible_resume_ready"] is True
    assert bundle["bundle_validation"]["full_replay_ready"] is False
    assert bundle["bundle_validation"]["provider_output_replay_ready"] is False
    assert bundle["bundle_validation"]["pending_work_resume_ready"] is False
    assert bundle["bundle_validation"]["resumed_trace_proof_ready"] is False
    assert bundle["resumed_trace_proof_ready"] is False
    assert bundle["bundle_validation"]["controller_event_count"] == 6
    assert kwargs["runtime_rng_state_snapshot"]["seed"] == 99
    assert kwargs["runtime_llm_scheduler_state_snapshot"]["state"]["total"] == 1
    assert kwargs["runtime_budget_state_snapshot"]["consumed"]["generations_completed"] == 1
    programs_by_id = kwargs["runtime_archive_programs_by_id"]
    assert programs_by_id
    assert all(isinstance(program, Program) for program in programs_by_id.values())
    assert kwargs["runtime_archive_state_snapshot"]["archive_contents"][
        "restore_status"
    ] == "snapshot_persisted_full_archive_restore_supported"
    controller_state = bundle["controller_budget_state"]
    assert controller_state["schema"] == "libreevolve.controller_budget_state.v1"
    assert [event["sequence"] for event in controller_state["events"]] == list(
        range(len(controller_state["events"]))
    )
    assert [event["kind"] for event in controller_state["events"]] == [
        "seed_evaluation",
        "generation_started",
        "llm_call",
        "candidate_evaluation",
        "generation_completed",
        "stop",
    ]
    assert bundle["controller_budget_replay"] == {
        "status": "replayed_and_applied_to_evolve_budget_snapshot",
        "event_count": 6,
        "replay_entrypoint": "apply_controller_budget_event",
        "runtime_seconds_policy": "manifest_snapshot_authoritative",
    }
    assert bundle["runtime_rng_replay_boundary"]["schema"] == (
        "libreevolve.runtime_rng_replay_boundary.v1"
    )
    assert bundle["runtime_rng_replay_boundary"]["external_surfaces"][0] == {
        "surface": "llm_provider_outputs",
        "restored_by_runtime_rng": False,
        "boundary": "remote_or_sdk_provider_nondeterminism",
    }
    assert bundle["lineage_replay_policy"]["provider_boundary"] == {
        "provider_outputs_replayed": False,
        "provider_nondeterminism": "remote_or_sdk_outputs_not_replayed",
        "call_ids_do_not_prove_same_provider_output": True,
    }
    assert bundle["lineage_replay_policy"]["full_replay_ready"] is False
    assert "provider_outputs" in bundle["unsupported_surfaces"]
    assert "end_to_end_resumed_trace_proof" in bundle["unsupported_surfaces"]


def test_full_resume_bundle_validation_rejects_replay_overclaims(tmp_path):
    class UsageBackend:
        name = "usage/model"
        api_mode = None

        def generate(self, prompt, **kwargs):
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    with patch("libreevolve.core.loop.build_llm", return_value=LLMEnsemble([UsageBackend()])):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=str(tmp_path),
                problem_name="source",
                seed=99,
            ),
        )

    bundle = load_full_resume_bundle(tmp_path / "source" / "manifest.json")
    edited = copy.deepcopy(bundle)
    edited["lineage_replay_policy"]["provider_boundary"][
        "provider_outputs_replayed"
    ] = True
    edited["unsupported_surfaces"] = ["controller_pending_work"]
    edited["controller_budget_replay"]["event_count"] = 999
    edited["resumed_trace_proof_ready"] = True

    validation = validate_full_resume_bundle(edited)
    codes = {issue["code"] for issue in validation["issues"]}

    assert validation["schema"] == FULL_RESUME_BUNDLE_VALIDATION_SCHEMA
    assert validation["ok"] is False
    assert validation["compatible_resume_ready"] is False
    assert validation["full_replay_ready"] is False
    assert validation["provider_output_replay_ready"] is False
    assert validation["resumed_trace_proof_ready"] is False
    assert "invalid_lineage_replay_policy" in codes
    assert "provider_output_replay_overclaim" in codes
    assert "resumed_trace_proof_overclaim" in codes
    assert "unsupported_surfaces_mismatch" in codes
    assert "controller_budget_replay_event_count_mismatch" in codes


def test_load_full_resume_bundle_rejects_budget_event_manifest_mismatch(tmp_path):
    class UsageBackend:
        name = "usage/model"
        api_mode = None
        provider_response_metadata = {
            "usage": {
                "input_tokens": 1,
                "output_tokens": 2,
                "total_tokens": 3,
            },
        }

        def generate(self, prompt, **kwargs):
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    with patch("libreevolve.core.loop.build_llm", return_value=LLMEnsemble([UsageBackend()])):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=str(tmp_path),
                problem_name="source",
                seed=99,
            ),
        )

    run_dir = tmp_path / "source"
    events_path = run_dir / "controller_budget_events.jsonl"
    events = events_path.read_text(encoding="utf-8").splitlines()
    events_path.write_text("\n".join(events[:-1]) + "\n", encoding="utf-8")

    with pytest.raises(RuntimeFullResumeBundleError, match="does not match"):
        load_full_resume_bundle(run_dir / "manifest.json")


def test_runtime_llm_budget_report_uses_configured_token_and_cost_limits():
    tmpdir = tempfile.mkdtemp()

    class UsageBackend:
        name = "usage/model"
        api_mode = None
        provider_response_metadata = {
            "usage": {
                "input_tokens": 400,
                "output_tokens": 1600,
                "total_tokens": 2000,
            },
        }

        def generate(self, prompt, **kwargs):
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    llm = LLMEnsemble(
        [UsageBackend()],
        backend_metadata=[{"cost_usd_per_million_tokens": 5.0}],
    )

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                max_llm_tokens=2000,
                max_llm_cost_microusd=10000,
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    runtime_budget = manifest["runtime"]
    report = manifest["runtime"]["llm_budget_report"]
    role_budget = report["role_budgets"][0]
    usage = report["role_usage"][0]

    assert manifest["config"]["max_llm_tokens"] == 2000
    assert manifest["config"]["max_llm_cost_microusd"] == 10000
    assert manifest["runtime"]["llm_accounting"]["limits"]["max_llm_tokens"] == 2000
    assert manifest["runtime"]["llm_accounting"]["limits"][
        "max_llm_cost_microusd"
    ] == 10000
    assert runtime_budget["limits"]["max_llm_tokens"] == 2000
    assert runtime_budget["limits"]["max_llm_cost_microusd"] == 10000
    assert runtime_budget["consumed"]["llm_tokens"] == 2000
    assert runtime_budget["consumed"]["llm_cost_microusd"] == 10000
    assert runtime_budget["stop_reason"] == "max_llm_tokens"
    assert validate_llm_budget_report(report).ok is True
    assert role_budget["token_limit"] == 2000
    assert role_budget["cost_limit_usd"] == 0.01
    assert role_budget["configured_token_limit"] == 2000
    assert role_budget["configured_cost_limit_usd"] == 0.01
    assert usage["total_tokens"] == 2000
    assert usage["cost_usd"] == 0.01


def test_runtime_llm_budget_report_uses_configured_seconds_limits():
    tmpdir = tempfile.mkdtemp()

    class TimedBackend:
        name = "timed/model"
        api_mode = None

        def generate(self, prompt, **kwargs):
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    llm = LLMEnsemble([TimedBackend()])

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                max_llm_seconds=0.000000001,
                llm_role_seconds_limits={"mutation": 0.000000001},
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    runtime_budget = manifest["runtime"]
    report = manifest["runtime"]["llm_budget_report"]
    role_budget = report["role_budgets"][0]
    usage = report["role_usage"][0]

    assert manifest["config"]["max_llm_seconds"] == 0.000000001
    assert manifest["config"]["llm_role_seconds_limits"] == {
        "mutation": 0.000000001
    }
    assert runtime_budget["limits"]["max_llm_seconds"] == 0.000000001
    assert runtime_budget["limits"]["llm_role_seconds_limits"] == {
        "mutation": 0.000000001
    }
    assert runtime_budget["consumed"]["llm_seconds"] > 0.0
    assert runtime_budget["consumed"]["llm_seconds_by_role"]["mutation"] > 0.0
    assert runtime_budget["stop_reason"] == "max_llm_seconds"
    assert validate_llm_budget_report(report).ok is True
    assert role_budget["wall_clock_limit_seconds"] >= usage["wall_clock_seconds"]
    assert role_budget["configured_wall_clock_limit_seconds"] == 0.000000001
    assert role_budget["limit_source"]["wall_clock_limit_seconds"] == (
        "config.llm_role_seconds_limits_or_observed_inflight_overshoot"
    )
    assert usage["wall_clock_seconds"] > 0.0


def test_runtime_llm_budget_report_uses_configured_role_usage_limits():
    tmpdir = tempfile.mkdtemp()

    class UsageBackend:
        name = "usage/model"
        api_mode = None
        provider_response_metadata = {
            "adapter_retry": {
                "policy": "bounded_provider_internal_retries",
                "max_retries": 1,
                "attempts": 2,
                "failed_attempts": 1,
                "failures": [{"attempt": 0, "error_type": "TimeoutError"}],
            },
            "usage": {
                "input_tokens": 400,
                "output_tokens": 1600,
                "total_tokens": 2000,
            },
        }

        def generate(self, prompt, **kwargs):
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    llm = LLMEnsemble(
        [UsageBackend()],
        backend_metadata=[{"cost_usd_per_million_tokens": 5.0}],
    )

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                llm_role_provider_attempt_limits={"mutation": 2},
                llm_role_token_limits={"mutation": 2000},
                llm_role_cost_microusd_limits={"mutation": 10000},
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    runtime_budget = manifest["runtime"]
    report = manifest["runtime"]["llm_budget_report"]
    role_budget = report["role_budgets"][0]

    assert manifest["config"]["llm_role_provider_attempt_limits"] == {"mutation": 2}
    assert manifest["config"]["llm_role_token_limits"] == {"mutation": 2000}
    assert manifest["config"]["llm_role_cost_microusd_limits"] == {"mutation": 10000}
    assert runtime_budget["limits"]["llm_role_provider_attempt_limits"] == {
        "mutation": 2
    }
    assert runtime_budget["limits"]["llm_role_token_limits"] == {"mutation": 2000}
    assert runtime_budget["limits"]["llm_role_cost_microusd_limits"] == {
        "mutation": 10000
    }
    assert runtime_budget["consumed"]["llm_provider_attempts_by_role"] == {
        "mutation": 2
    }
    assert runtime_budget["consumed"]["llm_tokens_by_role"] == {"mutation": 2000}
    assert runtime_budget["consumed"]["llm_cost_microusd_by_role"] == {
        "mutation": 10000
    }
    assert role_budget["adapter_attempt_limit"] == 2
    assert role_budget["token_limit"] == 2000
    assert role_budget["cost_limit_usd"] == 0.01
    assert role_budget["limit_source"]["adapter_attempt_limit"] == (
        "config.llm_role_provider_attempt_limits_or_observed_inflight_overshoot"
    )
    assert role_budget["limit_source"]["token_limit"] == (
        "config.llm_role_token_limits_or_observed_inflight_overshoot"
    )
    assert role_budget["limit_source"]["cost_limit_usd"] == (
        "config.llm_role_cost_microusd_limits_or_observed_inflight_overshoot"
    )
    assert validate_llm_budget_report(report).ok is True


def test_runtime_llm_budget_report_uses_configured_role_call_limit():
    tmpdir = tempfile.mkdtemp()
    backend = MagicMock()
    backend.name = "scheduler/model"
    backend.api_mode = None
    backend.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    llm = LLMEnsemble([backend], max_calls_by_role={"mutation": 3})

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                llm_role_call_limits={"mutation": 3},
            ),
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["config"]["llm_role_call_limits"] == {"mutation": 3}
    assert manifest["runtime"]["llm_accounting"]["limits"]["llm_role_call_limits"] == {
        "mutation": 3
    }
    assert manifest["runtime"]["llm_scheduler"]["state"]["role_call_limits"] == {
        "policy": "logical_generate_call_limits_by_role_v1",
        "max_calls_by_role": {"mutation": 3},
        "logical_calls_by_role": {"mutation": 1},
    }
    role_budget = manifest["runtime"]["llm_budget_report"]["role_budgets"][0]
    assert role_budget["logical_call_limit"] == 3
    assert role_budget["limit_source"]["logical_call_limit"] == (
        "config.llm_role_call_limits"
    )


def test_runtime_llm_budget_report_applies_wildcard_feedback_role_limits():
    class FeedbackUsageBackend:
        name = "usage/model"
        api_mode = None
        provider_response_metadata = {
            "adapter_retry": {
                "policy": "bounded_provider_internal_retries",
                "max_retries": 1,
                "attempts": 2,
                "failed_attempts": 1,
                "failures": [{"attempt": 0, "error_type": "TimeoutError"}],
            },
            "usage": {
                "input_tokens": 400,
                "output_tokens": 1600,
                "total_tokens": 2000,
            },
        }

        def generate(self, prompt, **kwargs):
            if kwargs.get("role") == "feedback:review":
                return '{"score": 1.0, "feedback": "ok"}'
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    tmpdir = tempfile.mkdtemp()
    llm = LLMEnsemble(
        [FeedbackUsageBackend()],
        backend_metadata=[{"cost_usd_per_million_tokens": 5.0}],
        max_calls_by_role={"feedback:*": 1},
    )

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                llm_feedback=[{"name": "review", "weight": 0.0}],
                llm_role_call_limits={"feedback:*": 1},
                llm_role_provider_attempt_limits={"feedback:*": 2},
                llm_role_token_limits={"feedback:*": 2000},
                llm_role_cost_microusd_limits={"feedback:*": 10000},
                llm_role_seconds_limits={"feedback:*": 10.0},
            ),
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["config"]["llm_role_call_limits"] == {"feedback:*": 1}
    assert manifest["runtime"]["llm_scheduler"]["state"]["role_call_limits"] == {
        "policy": "logical_generate_call_limits_by_role_v1",
        "max_calls_by_role": {"feedback:*": 1},
        "logical_calls_by_role": {"feedback:review": 1, "mutation": 1},
    }
    report = manifest["runtime"]["llm_budget_report"]
    feedback_budget = next(
        row for row in report["role_budgets"] if row["role"] == "feedback:review"
    )
    assert feedback_budget["logical_call_limit"] == 1
    assert feedback_budget["adapter_attempt_limit"] == 2
    assert feedback_budget["token_limit"] == 2000
    assert feedback_budget["cost_limit_usd"] == 0.01
    assert feedback_budget["wall_clock_limit_seconds"] == 10.0
    assert validate_llm_budget_report(report).ok is True


def test_runtime_llm_scheduler_state_snapshot_validation_and_manifest_loading(tmp_path):
    backend = MagicMock()
    backend.name = "scheduler/model"
    backend.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    llm = LLMEnsemble([backend])
    llm.generate("Task: mutate", role="mutation")
    snapshot = _runtime_llm_scheduler_state(llm)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"runtime": {"llm_scheduler": snapshot}}),
        encoding="utf-8",
    )

    loaded = load_runtime_llm_scheduler_state_snapshot(manifest)
    validated = validate_runtime_llm_scheduler_state_snapshot(
        snapshot,
        backend_count=1,
    )

    assert loaded == validated
    assert loaded["state"] == snapshot["state"]
    loaded["state"]["counts"][0] = 999
    assert snapshot["state"]["counts"][0] == 1


def test_runtime_budget_state_snapshot_manifest_loading(tmp_path):
    budget = RunBudget.from_config(Config(max_generations=3, max_llm_tokens=2000))
    budget.record_llm_call()
    budget.record_llm_tokens(750, role="mutation")
    snapshot = budget.snapshot()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "runtime": {
                    **snapshot,
                    "history": {"candidate_count": 0},
                }
            }
        ),
        encoding="utf-8",
    )

    loaded = load_runtime_budget_state_snapshot(manifest)

    assert loaded == {
        "wall_clock": snapshot["wall_clock"],
        "limits": snapshot["limits"],
        "consumed": snapshot["consumed"],
        "stop_reason": snapshot["stop_reason"],
    }
    loaded["consumed"]["llm_tokens"] = 999
    assert snapshot["consumed"]["llm_tokens"] == 750


def test_evolve_applies_restored_budget_snapshot_before_seed_work(tmp_path):
    config = Config(
        max_generations=0,
        max_evaluations=1,
        log_dir=str(tmp_path / "runs"),
        problem_name="t",
        run_collision_policy="overwrite",
    )
    previous = RunBudget.from_config(config)
    previous.record_evaluation(0.1, seed=True)

    best = evolve(
        _problem(),
        config,
        runtime_budget_state_snapshot=previous.snapshot(),
    )

    manifest = json.loads((tmp_path / "runs" / "t" / "manifest.json").read_text())
    assert best is None
    assert manifest["runtime"]["stop_reason"] == "max_evaluations"
    assert manifest["runtime"]["consumed"]["evaluations"] == 1
    assert manifest["runtime"]["history"]["programs_logged"] == 0
    assert manifest["runtime"]["wall_clock"]["resume_segments"][1]["kind"] == (
        "resumed_process"
    )


def test_evolve_can_restore_llm_scheduler_snapshot_into_new_run(tmp_path):
    snapshot = {
        "status": "snapshot",
        "schema": "libreevolve.llm_scheduler_state.v1",
        "state": {"counts": [3, 2], "wins": [1.5, 0.5], "total": 5},
        "restore_entrypoint": "LLMEnsemble.restore_scheduler_state",
        "resume_status": "snapshot_persisted_restore_supported",
    }
    first = MagicMock()
    first.name = "first/model"
    first.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    second = MagicMock()
    second.name = "second/model"
    second.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    llm = LLMEnsemble([first, second])

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=str(tmp_path),
                problem_name="t",
                backends=[
                    {"type": "openai", "model": "gpt-4o-mini"},
                    {"type": "openai", "model": "gpt-4o-mini"},
                ],
            ),
            runtime_llm_scheduler_state_snapshot=snapshot,
        )

    manifest = json.loads((tmp_path / "t" / "manifest.json").read_text())
    scheduler = manifest["runtime"]["llm_scheduler"]

    assert scheduler["resume_status"] == "snapshot_restored_into_evolve"
    assert scheduler["state"]["total"] == 6
    assert sum(scheduler["state"]["counts"]) == 6
    assert scheduler["state"]["wins"][0] == 1.5
    assert scheduler["state"]["wins"][1] == 0.5


def test_evolve_rejects_llm_scheduler_snapshot_backend_count_mismatch(tmp_path):
    snapshot = {
        "status": "snapshot",
        "schema": "libreevolve.llm_scheduler_state.v1",
        "state": {"counts": [1, 0], "wins": [0.0, 0.0], "total": 1},
        "restore_entrypoint": "LLMEnsemble.restore_scheduler_state",
        "resume_status": "snapshot_persisted_restore_supported",
    }
    backend = MagicMock()
    backend.name = "scheduler/model"
    backend.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    llm = LLMEnsemble([backend])

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        with pytest.raises(RuntimeLLMSchedulerStateError, match="one integer per backend"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=str(tmp_path), problem_name="t"),
                runtime_llm_scheduler_state_snapshot=snapshot,
            )

    assert not (tmp_path / "t" / "manifest.json").exists()


def test_completed_runtime_persists_run_rng_state_snapshot():
    tmpdir = tempfile.mkdtemp()

    evolve(
        _problem(),
        Config(max_generations=0, log_dir=tmpdir, problem_name="t", seed=77),
    )

    manifest_path = Path(tmpdir) / "t" / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    rng_state = load_runtime_rng_state_snapshot(manifest_path)
    restored = restore_runtime_rng_state_snapshot(rng_state)

    assert rng_state["status"] == "snapshot"
    assert rng_state["schema"] == "python.random.mt19937.v1"
    assert rng_state["engine"] == "python.random.Random"
    assert rng_state["seed"] == 77
    assert rng_state["resume_status"] == "snapshot_persisted_restore_supported"
    assert len(rng_state["state"]["internal_state"]) == 625
    assert len(rng_state["state_sha256"]) == 64
    assert isinstance(restored.random(), float)


def test_evolve_can_restore_runtime_rng_snapshot_into_new_run():
    source_rng = random.Random(91)
    for _ in range(4):
        source_rng.random()
    snapshot = _runtime_rng_state(source_rng, 91)
    expected_state_hash = snapshot["state_sha256"]
    tmpdir = tempfile.mkdtemp()

    evolve(
        _problem(),
        Config(max_generations=0, log_dir=tmpdir, problem_name="t", seed=91),
        runtime_rng_state_snapshot=snapshot,
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    rng_state = manifest["runtime"]["rng"]
    assert rng_state["resume_status"] == "snapshot_restored_into_evolve"
    assert rng_state["state_sha256"] == expected_state_hash


def test_evolve_can_restore_archive_cursor_snapshot_into_new_run():
    snapshot = {
        "schema": "libreevolve.island_state.v1",
        "resume_status": (
            "snapshot_persisted_cursor_restore_available_full_archive_restore_not_implemented"
        ),
        "cursor_policy": "advance_only_on_search_state_changed",
        "n_islands": 2,
        "next_island_id": 1,
        "archive_sequence": 3,
        "migration_sequence": 1,
        "metric_sample_index": 2,
        "archive_sequence_by_program_id": {"p1": 1, "p2": 3},
        "islands": [
            {"island_id": 0, "occupied_cell_count": 1, "elite_count": 1},
            {"island_id": 1, "occupied_cell_count": 1, "elite_count": 1},
        ],
    }
    tmpdir = tempfile.mkdtemp()

    evolve(
        _problem(),
        Config(max_generations=0, log_dir=tmpdir, problem_name="t", n_islands=2),
        runtime_archive_state_snapshot=snapshot,
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    restore = manifest["policies"]["archive_cursor_restore"]
    archive_state = manifest["runtime"]["history"]["archive_state"]
    assert restore["status"] == "cursor_state_restored"
    assert restore["archive_contents_restored"] is False
    assert restore["full_archive_restore_required"] is True
    assert archive_state["archive_sequence"] == 4
    assert archive_state["migration_sequence"] == 1
    assert archive_state["metric_sample_index"] == 2
    assert archive_state["lineage_sample_index"] == 0
    assert archive_state["next_island_id"] == 0
    assert archive_state["archive_sequence_by_program_id"]["p1"] == 1
    assert archive_state["archive_sequence_by_program_id"]["p2"] == 3
    assert 4 in archive_state["archive_sequence_by_program_id"].values()
    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    assert records[0]["metadata"]["archive_admission"]["island_id"] == 1
    assert records[0]["metadata"]["archive_sequence"] == 4


def test_evolve_rejects_runtime_rng_snapshot_with_mismatched_seed(tmp_path):
    snapshot = _runtime_rng_state(random.Random(12), 12)

    with pytest.raises(ValueError, match="snapshot seed must match"):
        evolve(
            _problem(),
            Config(max_generations=0, log_dir=str(tmp_path), problem_name="t", seed=13),
            runtime_rng_state_snapshot=snapshot,
        )

    assert not (tmp_path / "t" / "manifest.json").exists()


def test_load_runtime_rng_state_snapshot_rejects_manifest_without_runtime_rng(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"runtime": {"status": "completed"}}', encoding="utf-8")

    with pytest.raises(RuntimeRngStateError, match="missing rng snapshot"):
        load_runtime_rng_state_snapshot(manifest)


def test_completed_mutation_failure_runtime_persists_run_rng_state_snapshot():
    tmpdir = tempfile.mkdtemp()

    with patch("libreevolve.core.loop.build_llm", return_value=_FailingLLM()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t", seed=88),
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    rng_state = manifest["runtime"]["rng"]
    restored = restore_runtime_rng_state_snapshot(rng_state)

    assert manifest["runtime"]["status"] == "completed"
    assert manifest["runtime"]["stop_reason"] == "completed"
    assert manifest["runtime"]["artifacts"]["failure_history.jsonl"]["exists"] is True
    assert rng_state["status"] == "snapshot"
    assert rng_state["schema"] == "python.random.mt19937.v1"
    assert rng_state["seed"] == 88
    assert rng_state["resume_status"] == "snapshot_persisted_restore_supported"
    assert len(rng_state["state_sha256"]) == 64
    assert isinstance(restored.random(), float)


def test_runtime_llm_scheduler_state_records_unavailable_custom_llm():
    class CustomLLM:
        pass

    scheduler = _runtime_llm_scheduler_state(CustomLLM())

    assert scheduler == {
        "status": "unavailable",
        "reason": "llm_does_not_expose_scheduler_state",
        "llm_type": "CustomLLM",
    }


def test_runtime_llm_scheduler_state_records_invalid_non_finite_state():
    class InvalidStateLLM:
        scheduler_state = {"counts": [float("nan")]}

    scheduler = _runtime_llm_scheduler_state(InvalidStateLLM())

    assert scheduler == {
        "status": "invalid",
        "reason": "scheduler_state_not_finite_json",
        "error_type": "ValueError",
        "llm_type": "InvalidStateLLM",
    }


def test_runtime_llm_scheduler_state_rejects_unvalidated_custom_dict_state():
    class CustomStateLLM:
        scheduler_state = {"counts": [0], "wins": [0.0], "total": 0}

    scheduler = _runtime_llm_scheduler_state(CustomStateLLM())

    assert scheduler == {
        "status": "invalid",
        "reason": "scheduler_state_not_validated_by_llm_ensemble",
        "llm_type": "CustomStateLLM",
    }


def test_runtime_llm_scheduler_state_rejects_malformed_ensemble_state():
    backend = MagicMock()
    backend.name = "broken/model"
    backend.api_mode = None
    llm = LLMEnsemble([backend])
    llm._counts = []

    scheduler = _runtime_llm_scheduler_state(llm)

    assert scheduler["status"] == "invalid"
    assert scheduler["reason"] == "scheduler_state_validation_failed"
    assert scheduler["error_type"] == "ValueError"
    assert scheduler["error"] == "scheduler counts must contain one integer per backend"
    assert scheduler["llm_type"] == "LLMEnsemble"


def test_loop_persists_parent_selection_metric_target_on_candidate():
    tmpdir = tempfile.mkdtemp()
    llm = _TelemetryLLM()

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                parent_selection_strategy="metric",
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    parent_selection = records[1]["metadata"]["parent_selection"]
    assert parent_selection["strategy"] == "metric"
    assert parent_selection["target_metric"] == "score"
    assert parent_selection["selected_program_id"] == records[1]["parent_id"]


def test_loop_records_llm_call_span_after_bounded_history_eviction():
    tmpdir = tempfile.mkdtemp()
    backend = MagicMock()
    backend.name = "bounded/model"
    backend.api_mode = None
    backend.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    llm = LLMEnsemble([backend], max_call_history=1)
    llm.generate("prefill prompt", role="mutation")
    prefill_id = llm.last_call["id"]

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    calls = records[1]["metadata"]["llm_calls"]
    assert len(calls) == 1
    assert calls[0]["backend_name"] == "bounded/model"
    assert calls[0]["id"] != prefill_id
    assert llm.call_history_retention["dropped_records"] >= 1
    call_records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "llm_calls.jsonl").read_text().splitlines()
    ]
    assert [record["record_type"] for record in call_records] == ["call", "reward"]
    assert call_records[0]["id"] == calls[0]["id"]
    assert call_records[0]["record_type"] == "call"
    assert call_records[0]["sequence_id"] == 2
    assert call_records[0]["prompt_sha256"] == calls[0]["prompt_sha256"]
    assert call_records[0]["backend_name"] == "bounded/model"
    assert call_records[1]["call_id"] == calls[0]["id"]
    assert call_records[1]["backend_idx"] == calls[0]["backend_idx"]
    assert call_records[1]["rewarded"] is True


def test_loop_persists_sanitized_backend_object_telemetry_on_candidate():
    tmpdir = tempfile.mkdtemp()
    raw_secret = "sk-proj_history_backend_name_secret_1234567890"  # pragma: allowlist secret

    class UnsafeTelemetryBackend:
        name = f"api_key={raw_secret}"
        api_mode = object()

        def generate(self, prompt, **kwargs):
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    llm = LLMEnsemble([UnsafeTelemetryBackend()])

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[1]
    call = child["metadata"]["llm_calls"][0]
    assert call["backend_name"] == "UnsafeTelemetryBackend"
    assert call["api_mode"] is None
    assert {
        "field": "backend_name",
        "reason": "unsafe_or_non_string",
        "value_type": "str",
    } in call["backend_telemetry_diagnostics"]
    assert {
        "field": "api_mode",
        "reason": "unsafe_or_non_string",
        "value_type": "object",
    } in call["backend_telemetry_diagnostics"]
    assert raw_secret not in json.dumps(child)


def test_loop_records_proposal_metadata_when_enabled():
    tmpdir = tempfile.mkdtemp()
    response = """IDEA: Change x to the accepted value.
RATIONALE: The validator expects x=2.
HYPOTHESIS: The candidate should remain valid.
<<<SEARCH
x=1
===
x=2
>>>REPLACE"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                capture_proposal_metadata=True,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    assert child["metadata"]["proposal"]["idea"] == "Change x to the accepted value."
    assert child["metadata"]["proposal"]["rationale"] == "The validator expects x=2."
    assert child["metadata"]["proposal"]["hypothesis"] == "The candidate should remain valid."
    assert "IDEA:" in child["metadata"]["prompt"]


def test_runtime_history_reports_programmatic_representation_boundary():
    tmpdir = tempfile.mkdtemp()
    response = """IDEA: Change x to the accepted value.
RATIONALE: The validator expects x=2.
HYPOTHESIS: The candidate should remain valid.
<<<SEARCH
x=1
===
x=2
>>>REPLACE"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                capture_proposal_metadata=True,
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"][
        "programmatic_representation_boundary_report"
    ]

    assert report["schema"] == (
        "libreevolve.programmatic_representation_boundary_report.v1"
    )
    assert report["validation"]["ok"] is True
    assert validate_programmatic_representation_boundary_report(report)["ok"] is True
    assert report["candidate_representation"]["kind"] == "executable_code_workspace"
    assert report["candidate_representation"]["natural_language_candidate"] is False
    assert report["candidate_representation"]["generated_candidate_count"] == 1
    assert report["candidate_representation"]["executable_generated_count"] == 1
    assert report["natural_language_artifacts"]["capture_configured"] is True
    assert report["natural_language_artifacts"]["proposal_record_count"] == 1
    assert report["natural_language_artifacts"]["proposal_field_counts"] == {
        "idea": 1,
        "rationale": 1,
        "hypothesis": 1,
    }
    assert report["natural_language_artifacts"][
        "candidate_code_contains_proposal_preamble"
    ] is False
    assert report["programmatic_evaluation_criteria"]["metric_names"] == ["score"]
    assert report["programmatic_evaluation_criteria"]["evaluated_generated_count"] == 1
    assert report["programmatic_evaluation_criteria"]["valid_generated_count"] == 1
    assert report["feedback_boundary"]["llm_feedback_primary_validity_gate"] is False
    assert report["runtime_step_scope"]["max_generation_observed"] == 1
    assert report["runtime_step_scope"]["long_horizon_evidence"] is False
    assert report["boundary_policy"]["natural_language_hypothesis_role"] == (
        "context_metadata_only"
    )
    assert report["boundary_policy"]["transition_from_hypothesis_to_code_required"] is True
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["hallucination_resistance_measured"] is False
    assert report["claim_readiness"]["long_horizon_evolution_measured"] is False
    assert report["claim_readiness"]["ai_coscientist_bridge_contract"] is False
    sample = report["sample_records"][0]
    assert sample["candidate_representation"] == "executable_code_workspace"
    assert sample["proposal_fields_present"] == ["idea", "rationale", "hypothesis"]
    assert sample["natural_language_hypothesis_is_candidate"] is False
    assert sample["evaluation_criteria_source"] == "programmatic_evaluator_metrics"


def test_runtime_history_reports_mutation_operator_boundary():
    tmpdir = tempfile.mkdtemp()
    response = """IDEA: Try a direct constant update.
RATIONALE: The parser applies a fixed diff payload.
HYPOTHESIS: The generated candidate should validate.
<<<SEARCH
x=1
===
x=2
>>>REPLACE"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                capture_proposal_metadata=True,
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["mutation_operator_boundary_report"]

    assert report["schema"] == "libreevolve.mutation_operator_boundary_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_mutation_operator_boundary_report(report)["ok"] is True
    assert report["configured_mutation_mode"] == "diff"
    assert report["generated_candidate_count"] == 1
    assert report["mutation_mode_counts"] == {"diff": 1}
    assert report["payload_surface_counts"] == {"search_replace_diff": 1}
    assert report["proposal_operator_family_counts"] == {
        "proposal_text_unclassified": 1
    }
    policy = report["edit_grammar_policy"]
    assert policy["run_wide_mutation_mode"] is True
    assert policy["adaptive_diff_full_selection"] is False
    assert policy["llm_constructed_operator_families"] is False
    assert policy["operator_family_scoring"] is False
    assert "search_replace_diff" in policy["fixed_local_parser_surfaces"]
    assert report["strategy_boundary"][
        "task_or_failure_aware_operator_construction"
    ] is False
    assert report["strategy_boundary"]["benchmark_operator_telemetry"] is False
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["edit_payload_grammar_reported"] is True
    assert report["claim_readiness"][
        "llm_constructed_operator_family_reported"
    ] is False
    assert report["claim_readiness"]["adaptive_operator_selection_reported"] is False
    sample = report["sample_records"][0]
    assert sample["mutation_mode"] == "diff"
    assert sample["payload_surfaces"] == ["search_replace_diff"]
    assert sample["operator_family_source"] == "not_declared"
    assert sample["operator_family"] == "proposal_text_unclassified"
    assert sample["llm_constructed_operator_family"] is False
    assert sample["adaptive_operator_selection"] is False
    assert sample["proposal_fields_present"] == ["idea", "rationale", "hypothesis"]


def test_runtime_history_reports_mutation_consistency_diagnostics():
    tmpdir = tempfile.mkdtemp()
    problem = _problem()
    problem.initial_programs = ["x=1\ny=1"]
    response = """<<<SEARCH
x=1
===
x=helper
>>>REPLACE
<<<SEARCH
y=1
===
y=helper + 1
>>>REPLACE"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            problem,
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["mutation_consistency_report"]

    assert report["schema"] == "libreevolve.mutation_consistency_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_mutation_consistency_report(report)["ok"] is True
    assert report["generated_candidate_count"] == 1
    assert report["multi_edit_candidate_count"] == 1
    assert report["python_symbol_scan_candidate_count"] == 1
    assert report["unresolved_reference_candidate_count"] == 1
    assert report["candidate_status_counts"] == {"accepted_history": 1}
    assert report["mutation_mode_counts"] == {"diff": 1}
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["python_symbol_reference_scan"] is True
    assert report["claim_readiness"]["semantic_consistency_proven"] is False
    assert report["claim_readiness"]["hard_acceptance_gate"] is False

    record = report["records"][0]
    edit_summary = record["edit_summary"]
    assert edit_summary["search_replace_block_count"] == 2
    assert edit_summary["edit_unit_count"] == 2
    assert edit_summary["multi_edit"] is True
    assert edit_summary["changed_files"] == ["main.py"]
    assert record["cochange_links"] == []
    symbols = record["symbol_summary"]
    assert symbols["schema"] == "libreevolve.python_symbol_consistency_scan.v1"
    assert symbols["scanned_files"] == ["main.py"]
    assert "helper" in symbols["referenced_symbols"]
    assert symbols["unresolved_references"] == ["helper"]
    assert symbols["unresolved_reference_count"] == 1
    assert record["failure_taxonomy"]["category"] == "symbol_consistency_diagnostic"
    assert record["admission"]["admitted"] is True
    assert record["evaluation"]["is_valid"] is True


def test_runtime_history_reports_prompt_example_copy_diagnostics():
    tmpdir = tempfile.mkdtemp()
    copied_example_payload = """<<<SEARCH
def foo():
    return 1
===
def foo():
    return 2
>>>REPLACE"""

    with patch(
        "libreevolve.core.loop.build_llm",
        return_value=_llm(copied_example_payload),
    ):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["prompt_example_copy_report"]

    assert report["schema"] == "libreevolve.prompt_example_copy_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_prompt_example_copy_report(report)["ok"] is True
    assert report["inventory"]["schema"] == "libreevolve.prompt_example_inventory.v1"
    assert report["inventory"]["example_id"] == "default_diff_format_example:v1"
    assert report["generated_candidate_count"] == 1
    assert report["prompt_example_enabled_count"] == 1
    assert report["copied_example_candidate_count"] == 1
    assert report["candidate_status_counts"] == {"rejected_history": 1}
    assert report["copied_candidate_status_counts"] == {"rejected_history": 1}
    assert report["mutation_mode_counts"] == {"diff": 1}
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["prompt_example_inventory_versioned"] is True
    assert report["claim_readiness"]["copied_sentinel_detection"] is True
    assert report["claim_readiness"]["hard_acceptance_gate"] is False
    assert report["claim_readiness"]["semantic_example_copy_detection"] is False

    record = report["records"][0]
    assert record["prompt_example_enabled"] is True
    assert record["copied_example_sentinel_count"] == 3
    labels = {item["label"] for item in record["copied_example_sentinels"]}
    assert labels == {
        "example_function_signature",
        "example_search_return",
        "example_replace_return",
    }
    assert record["admission"]["admitted"] is False


def test_runtime_history_reports_normalized_prompt_example_copy_diagnostics():
    tmpdir = tempfile.mkdtemp()
    copied_example_payload = """<<<FILE helper.py
def foo( ):
    return    1

def foo( ):
    return    2
>>>FILE"""

    with patch(
        "libreevolve.core.loop.build_llm",
        return_value=_llm(copied_example_payload),
    ):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_mode="full",
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["prompt_example_copy_report"]

    assert report["validation"]["ok"] is True
    assert validate_prompt_example_copy_report(report)["ok"] is True
    assert report["copied_example_candidate_count"] == 1
    assert report["normalized_copy_signal_count"] >= 3
    assert report["format_skeleton_signal_count"] == 1
    assert report["claim_readiness"]["normalized_region_detection"] is True
    assert report["claim_readiness"]["format_skeleton_detection"] is True
    assert report["claim_readiness"]["semantic_example_copy_detection"] is False

    record = report["records"][0]
    assert record["copied_example_sentinel_count"] == 0
    assert record["normalized_copy_signal_count"] >= 3
    assert record["format_skeleton_signal_count"] == 1
    assert record["copy_signal_count"] == (
        record["normalized_copy_signal_count"]
        + record["format_skeleton_signal_count"]
    )
    assert {signal["region"] for signal in record["normalized_copy_signals"]} == {
        "file_section:0"
    }
    assert record["format_skeleton_signals"][0]["surface"] == "file_section_body"
    assert record["format_skeleton_signals"][0]["section_header"] == "helper.py"


def test_runtime_history_reports_prompt_example_disabled_policy():
    tmpdir = tempfile.mkdtemp()
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompt_db",
        templates=["{task}\n{parent_code}\n{mutation_instructions}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={"mutation_instruction_include_example": False},
    )
    prompt_db.record_result(parent_prompt.id, 0.0)

    with (
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
        patch("libreevolve.core.loop.build_llm", return_value=_llm()),
    ):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["prompt_example_copy_report"]

    assert report["validation"]["ok"] is True
    assert validate_prompt_example_copy_report(report)["ok"] is True
    assert report["generated_candidate_count"] == 1
    assert report["prompt_example_enabled_count"] == 0
    assert report["copied_example_candidate_count"] == 0
    assert report["records"] == []


def test_runtime_history_reports_prompt_current_binding_for_diff_mutation():
    tmpdir = tempfile.mkdtemp()
    response = """IDEA: Change x to the accepted value.
RATIONALE: The validator expects x=2.
HYPOTHESIS: The candidate should remain valid.
<<<SEARCH
x=1
===
x=2
>>>REPLACE"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                capture_proposal_metadata=True,
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["prompt_current_binding_report"]

    assert report["schema"] == "libreevolve.prompt_current_binding_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_prompt_current_binding_report(report)["ok"] is True
    assert report["generated_candidate_count"] == 1
    assert report["binding_record_count"] == 1
    assert report["mutation_mode_counts"] == {"diff": 1}
    assert report["candidate_status_counts"] == {"accepted_history": 1}
    assert report["exact_diff_binding_count"] == 1
    assert report["history_join_count"] == 1
    assert report["prompt_history_score_join_count"] == 1
    assert report["cross_run_binding_table_record_count"] == 1
    assert report["cross_run_binding_table"]["exists"] is True
    assert report["cross_run_binding_table"]["record_count"] == 1
    assert report["cross_run_binding_table"]["path"] == (
        "prompt_current_binding_table.jsonl"
    )
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["prompt_current_hashes_recorded"] is True
    assert report["claim_readiness"]["parent_workspace_hash_recorded"] is True
    assert report["claim_readiness"]["diff_exact_match_spans_recorded"] is True
    assert report["claim_readiness"]["prompt_history_row_join"] is True
    assert report["claim_readiness"]["cross_run_binding_table"] is True
    assert report["claim_readiness"]["remaining_gap"] == []
    assert (
        report["claim_readiness"]["full_alphaevolve_current_program_provenance"]
        is False
    )

    table_path = run_dir / "prompt_current_binding_table.jsonl"
    table_lines = table_path.read_text(encoding="utf-8").splitlines()
    assert len(table_lines) == 1
    table_row = json.loads(table_lines[0])
    assert table_row["record_schema"] == "libreevolve.prompt_current_binding_table.v1"
    assert table_row["run_id"] == manifest["config"]["run_id"]
    assert table_row["problem_name"] == "t"
    assert table_row["candidate_id"] == report["records"][0]["candidate_id"]
    assert table_row["prompt_program_id"] == report["records"][0]["prompt_program_id"]
    assert table_row["history_join"]["candidate_history_line_number"] == 2
    assert table_row["history_join"]["prompt_history_score_line_number"] == 2
    assert table_row["binding"]["mode_policy"] == "diff_primary_file_exact_search_match"
    assert table_row["binding"]["diff_match_count"] == 1
    assert manifest["runtime"]["artifacts"]["prompt_current_binding_table.jsonl"][
        "exists"
    ] is True

    record = report["records"][0]
    assert record["prompt_program_id"]
    history_join = record["history_join"]
    assert history_join["schema"] == "libreevolve.prompt_current_history_join.v1"
    assert history_join["candidate_history_joined"] is True
    assert history_join["prompt_history_add_joined"] is True
    assert history_join["prompt_history_score_joined"] is True
    assert history_join["candidate_history"]["stream"] == "history.jsonl"
    assert history_join["candidate_history"]["line_number"] == 2
    assert history_join["candidate_failure_history"] is None
    assert history_join["prompt_history"]["stream"] == "prompt_history.jsonl"
    assert history_join["prompt_history"]["add_line_number"] == 1
    assert history_join["prompt_history"]["score_line_number"] == 2
    assert history_join["prompt_history"]["score_line_numbers"] == [2]
    assert record["prompt_sha256_scope"] == "rendered_prompt"
    assert record["parent_id"]
    assert record["parent_workspace_sha256"]
    assert record["candidate_workspace_sha256"]
    current = record["prompt_current_program"]
    assert current["policy_schema"] == "libreevolve.parent_code_policy.v1"
    assert current["path_policy_schema"] == "libreevolve.parent_code_paths.v1"
    assert current["primary_file"] == "main.py"
    assert current["rendered_paths"] == ["main.py"]
    assert current["rendered_parent_file_hashes"][0]["path"] == "main.py"
    binding = record["mutation_binding"]
    assert binding["mode_policy"] == "diff_primary_file_exact_search_match"
    assert binding["target_path"] == "main.py"
    assert binding["search_block_count"] == 1
    assert binding["all_search_blocks_match_once"] is True
    assert binding["match_records"][0]["match_count"] == 1
    assert binding["match_records"][0]["normalized_span"] is not None
    assert record["evaluation_link"]["is_valid"] is True
    assert record["admission_link"]["admitted"] is True

    score_report = manifest["runtime"]["history"][
        "prompt_prior_score_provenance_report"
    ]
    assert score_report["schema"] == (
        "libreevolve.prompt_prior_score_provenance_report.v1"
    )
    assert score_report["validation"]["ok"] is True
    assert validate_prompt_prior_score_provenance_report(score_report)["ok"] is True
    assert score_report["generated_candidate_count"] == 1
    assert score_report["prompt_record_count"] == 1
    assert score_report["score_record_count"] == 1
    assert score_report["target_score_record_count"] == 1
    assert score_report["inspiration_score_record_count"] == 0
    assert score_report["history_join_count"] == 1
    assert score_report["evaluator_result_join_count"] == 1
    assert score_report["omitted_or_truncated_score_record_count"] == 0
    assert score_report["score_field_record_count"] == 3
    assert score_report["omitted_or_truncated_score_field_count"] == 0
    assert score_report["cross_run_prompt_score_table_record_count"] == 1
    assert score_report["cross_run_prompt_score_table"]["exists"] is True
    assert score_report["cross_run_prompt_score_table"]["record_count"] == 1
    assert score_report["cross_run_prompt_score_table"]["path"] == (
        "prompt_prior_score_table.jsonl"
    )
    assert score_report["claim_ready"] is False
    assert score_report["claim_readiness"]["target_scores_joined"] is True
    assert score_report["claim_readiness"]["history_rows_joined"] is True
    assert score_report["claim_readiness"]["evaluator_rows_joined"] is True
    assert score_report["claim_readiness"]["prompt_visible_score_rows"] is True
    assert (
        score_report["claim_readiness"]["score_omission_and_truncation_policy"]
        is True
    )
    assert score_report["claim_readiness"]["average_score_formula_parity"] is True
    assert score_report["claim_readiness"]["cross_run_prompt_score_table"] is True
    assert (
        score_report["claim_readiness"][
            "full_alphaevolve_rendered_evaluation_result_provenance"
        ]
        is False
    )
    score_prompt = score_report["records"][0]
    assert score_prompt["candidate_id"] == record["candidate_id"]
    assert score_prompt["prompt_program_id"] == record["prompt_program_id"]
    assert score_prompt["prompt_sha256"] == record["prompt_sha256"]
    score_row = score_prompt["score_records"][0]
    assert score_row["role"] == "target"
    assert score_row["program_id"] == record["parent_id"]
    assert score_row["prompt_visible"] is True
    assert score_row["displayed_aggregate_formula"] == "program.fitness"
    assert score_row["displayed_aggregate_score"] == 1.0
    assert score_row["displayed_average_score_formula"] == "program.fitness"
    assert score_row["displayed_average_score"] == 1.0
    assert score_row["displayed_average_score_text"] == "average_score=1.0000"
    assert score_row["raw_metrics"]["score"] == 1.0
    assert score_row["metric_names"] == ["score"]
    display_fields = {
        field["field_id"]: field for field in score_row["score_display"]["fields"]
    }
    assert display_fields["average_score"]["prompt_visible"] is True
    assert display_fields["average_score"]["display_text"] == (
        score_row["displayed_average_score_text"]
    )
    assert display_fields["aggregate_score"]["prompt_visible"] is True
    assert display_fields["metric:score"]["prompt_visible"] is True
    assert display_fields["metric:score"]["display_text"] == "score=1"
    assert score_row["history_joined"] is True
    assert score_row["history_row"]["stream"] == "history.jsonl"
    assert score_row["history_row"]["line_number"] == 1
    assert score_row["evaluator_result_joined"] is True
    assert score_row["evaluator_result"]["stream"] == "evaluator_results.jsonl"
    assert score_row["evaluator_result"]["line_number"] == 1
    score_table_path = run_dir / "prompt_prior_score_table.jsonl"
    score_table_lines = score_table_path.read_text(encoding="utf-8").splitlines()
    assert len(score_table_lines) == 1
    score_table_row = json.loads(score_table_lines[0])
    assert score_table_row["record_schema"] == (
        "libreevolve.prompt_prior_score_table.v1"
    )
    assert score_table_row["run_id"] == manifest["config"]["run_id"]
    assert score_table_row["problem_name"] == "t"
    assert score_table_row["candidate_id"] == record["candidate_id"]
    assert score_table_row["prompt_program_id"] == record["prompt_program_id"]
    assert score_table_row["score_role"] == "target"
    assert score_table_row["score_program_id"] == record["parent_id"]
    assert score_table_row["displayed_aggregate_formula"] == "program.fitness"
    assert score_table_row["displayed_average_score_formula"] == "program.fitness"
    assert score_table_row["displayed_average_score_text"] == (
        "average_score=1.0000"
    )
    assert score_table_row["score_display"]["visible_fields"] == [
        "average_score",
        "aggregate_score",
        "metric:score",
    ]
    assert score_table_row["history_join"]["line_number"] == 1
    assert score_table_row["evaluator_result"]["line_number"] == 1
    assert manifest["runtime"]["artifacts"]["prompt_prior_score_table.jsonl"][
        "exists"
    ] is True

    edited_score_report = copy.deepcopy(score_report)
    edited_score_report["records"][0]["score_records"][0][
        "displayed_aggregate_formula"
    ] = "claimed_average_score"
    validation = validate_prompt_prior_score_provenance_report(edited_score_report)
    assert validation["ok"] is False
    assert "invalid_score_formula" in {
        issue["code"] for issue in validation["issues"]
    }

    edited_score_report = copy.deepcopy(score_report)
    edited_score_report["records"][0]["score_records"][0][
        "displayed_average_score_formula"
    ] = "claimed_average_score"
    validation = validate_prompt_prior_score_provenance_report(edited_score_report)
    assert validation["ok"] is False
    assert "invalid_average_score_formula" in {
        issue["code"] for issue in validation["issues"]
    }


def test_runtime_history_reports_prompt_prior_execution_output_display():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "print('parent stdout visible')\n"
        "def evaluate(c): return {'score':1.0,'is_valid':True}"
    )
    problem.context_policy = {
        "feedback_sections": ["execution_output"],
        "execution_output_fields": ["stdout", "stderr", "error"],
        "execution_output_max_chars_by_field": {"stdout": 80},
    }
    response = """<<<SEARCH
x=1
===
x=2
>>>REPLACE"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"][
        "prompt_prior_score_provenance_report"
    ]

    assert report["validation"]["ok"] is True
    assert validate_prompt_prior_score_provenance_report(report)["ok"] is True
    assert report["execution_result_record_count"] == 1
    assert report["prompt_visible_execution_result_record_count"] == 1
    assert report["execution_result_evaluator_join_count"] == 1
    assert report["cross_run_prompt_score_table_record_count"] == 1
    assert (
        report["claim_readiness"]["execution_result_text_display_attribution"]
        is True
    )
    assert "execution_result_text_display_attribution" not in (
        report["claim_readiness"]["remaining_gap"]
    )

    score_row = report["records"][0]["score_records"][0]
    display = score_row["execution_result_display"]
    assert display["schema"] == (
        "libreevolve.prompt_prior_execution_result_display.v1"
    )
    assert display["role"] == "target"
    assert display["prompt_visible"] is True
    assert display["has_source_execution_result"] is True
    assert display["source_fields"] == ["stdout"]
    assert display["prompt_visible_fields"] == ["stdout"]
    assert display["evaluator_result"]["stream"] == "evaluator_results.jsonl"
    assert display["evaluator_result"]["execution_output"]["present_fields"] == [
        "stdout"
    ]
    stdout = display["field_records"][0]
    assert stdout["field"] == "stdout"
    assert stdout["prompt_visible"] is True
    assert stdout["display_text"] == "parent stdout visible"
    assert stdout["raw_sha256"] == hashlib.sha256(
        b"parent stdout visible"
    ).hexdigest()
    table_row = json.loads(
        (run_dir / "prompt_prior_score_table.jsonl").read_text(encoding="utf-8")
    )
    assert table_row["execution_result"]["prompt_visible"] is True
    assert table_row["execution_result"]["prompt_visible_fields"] == ["stdout"]
    assert table_row["execution_result"]["visible_field_display_sha256"] == {
        "stdout": stdout["display_sha256"]
    }

    edited_report = copy.deepcopy(report)
    edited_report["records"][0]["score_records"][0]["execution_result_display"][
        "field_records"
    ][0]["display_text"] = None
    validation = validate_prompt_prior_score_provenance_report(edited_report)
    assert validation["ok"] is False
    assert "missing_execution_result_display_text" in {
        issue["code"] for issue in validation["issues"]
    }


def test_runtime_history_reports_prompt_prior_score_display_omission_policy():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(c):\n"
        "    return {'score': 1.0, 'latency': 123.456, 'size': 7.0, 'is_valid': True}\n"
    )
    problem.metrics = [
        {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
        {"name": "latency", "primary": False, "bounds": [0.0, 200.0]},
        {"name": "size", "primary": False, "bounds": [0.0, 10.0]},
    ]
    prompt_db = PromptDatabase(Path(tmpdir) / "prompts", templates=[DEFAULT_TEMPLATE])
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={
            "parent_metric_names": ["score", "latency", "size"],
            "parent_metrics_max_chars_by_name": {"latency": 8, "size": 0},
        },
    )
    prompt_db.record_result(parent_prompt.id, 0.0)
    problem.context_policy = {
        "parent_metric_names": ["score", "latency", "size"],
        "parent_metrics_max_chars_by_name": {"latency": 8, "size": 0},
    }
    response = """<<<SEARCH
x=1
===
x=2
>>>REPLACE"""

    with (
        patch("libreevolve.core.loop.build_llm", return_value=_llm(response)),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            problem,
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"][
        "prompt_prior_score_provenance_report"
    ]

    assert report["validation"]["ok"] is True
    assert validate_prompt_prior_score_provenance_report(report)["ok"] is True
    assert report["score_field_record_count"] == 5
    assert report["omitted_or_truncated_score_field_count"] == 2
    assert (
        report["claim_readiness"]["score_omission_and_truncation_policy"]
        is True
    )
    assert "score_omission_and_truncation_policy" not in (
        report["claim_readiness"]["remaining_gap"]
    )

    score_row = report["records"][0]["score_records"][0]
    fields = {
        field["field_id"]: field for field in score_row["score_display"]["fields"]
    }
    assert fields["average_score"]["prompt_visible"] is True
    assert fields["aggregate_score"]["prompt_visible"] is True
    assert fields["metric:score"]["prompt_visible"] is True
    assert fields["metric:latency"]["prompt_visible"] is True
    assert fields["metric:latency"]["truncated"] is True
    assert fields["metric:size"]["prompt_visible"] is False
    assert fields["metric:size"]["omission_reason"] == (
        "metric_suppressed_by_parent_metrics_cap"
    )

    table_row = json.loads(
        (run_dir / "prompt_prior_score_table.jsonl").read_text(encoding="utf-8")
    )
    assert "metric:latency" in table_row["score_display"]["truncated_fields"]
    assert table_row["score_display"]["omitted_fields"] == [
        {
            "field_id": "metric:size",
            "omission_reason": "metric_suppressed_by_parent_metrics_cap",
        }
    ]

    edited_report = copy.deepcopy(report)
    edited_report["records"][0]["score_records"][0]["score_display"]["fields"][0][
        "display_text"
    ] = None
    validation = validate_prompt_prior_score_provenance_report(edited_report)
    assert validation["ok"] is False
    assert "missing_score_display_text" in {
        issue["code"] for issue in validation["issues"]
    }


def test_runtime_history_reports_prompt_prior_stage_summary_io_display():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "print('stage stdout visible')\n"
        "def evaluate(c): return {'score':1.0,'is_valid':True}"
    )
    problem.context_policy = {
        "feedback_sections": ["stage_summary"],
        "stage_summary_fields": ["name", "io"],
        "execution_output_fields": ["stdout"],
        "execution_output_max_chars_by_field": {"stdout": 80},
    }
    response = """<<<SEARCH
x=1
===
x=2
>>>REPLACE"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"][
        "prompt_prior_score_provenance_report"
    ]

    assert report["validation"]["ok"] is True
    assert validate_prompt_prior_score_provenance_report(report)["ok"] is True
    assert report["stage_summary_io_record_count"] == 1
    assert report["prompt_visible_stage_summary_io_record_count"] == 1
    assert report["stage_summary_io_evaluator_join_count"] == 1
    assert report["claim_readiness"]["stage_summary_io_display_attribution"] is True
    assert "stage_summary_io_display_attribution" not in (
        report["claim_readiness"]["remaining_gap"]
    )

    score_row = report["records"][0]["score_records"][0]
    display = score_row["stage_summary_io_display"]
    assert display["schema"] == (
        "libreevolve.prompt_prior_stage_summary_io_display.v1"
    )
    assert display["prompt_visible"] is True
    assert display["has_source_stage_io"] is True
    assert display["visible_stage_count"] == 1
    assert display["evaluator_result"]["stream"] == "evaluator_results.jsonl"
    assert display["evaluator_result"]["stage_summary_io"]["stage_record_count"] >= 1
    stage = next(
        stage for stage in display["stage_records"] if stage["prompt_visible"] is True
    )
    assert stage["prompt_visible"] is True
    assert stage["prompt_visible_fields"] == ["stdout"]
    assert "stage stdout visible" in stage["stage_io_display_text"]
    assert stage["stage_io_display_sha256"]

    table_row = json.loads(
        (run_dir / "prompt_prior_score_table.jsonl").read_text(encoding="utf-8")
    )
    assert table_row["stage_summary_io"]["prompt_visible"] is True
    assert table_row["stage_summary_io"]["visible_stage_count"] == 1
    visible_table_stage = next(
        stage
        for stage in table_row["stage_summary_io"]["stage_records"]
        if stage["prompt_visible"] is True
    )
    assert visible_table_stage[
        "stage_io_display_sha256"
    ] == stage["stage_io_display_sha256"]

    edited_report = copy.deepcopy(report)
    edited_stages = edited_report["records"][0]["score_records"][0][
        "stage_summary_io_display"
    ]["stage_records"]
    next(stage for stage in edited_stages if stage["prompt_visible"] is True)[
        "stage_io_display_text"
    ] = None
    validation = validate_prompt_prior_score_provenance_report(edited_report)
    assert validation["ok"] is False
    assert "missing_stage_summary_io_display_text" in {
        issue["code"] for issue in validation["issues"]
    }


def test_runtime_history_reports_prompt_prior_feedback_section_policy():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "print('feedback stdout source')\n"
        "def evaluate(c): return {'score':1.0,'is_valid':True}"
    )
    prompt_db = PromptDatabase(Path(tmpdir) / "prompts", templates=[DEFAULT_TEMPLATE])
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={
            "feedback_sections": ["execution_output", "stage_summary"],
            "feedback_section_order": ["stage_summary", "execution_output"],
            "feedback_section_max_chars_by_name": {"execution_output": 0},
            "stage_summary_fields": ["name", "score"],
        },
    )
    prompt_db.record_result(parent_prompt.id, 0.0)
    response = """<<<SEARCH
x=1
===
x=2
>>>REPLACE"""

    with (
        patch("libreevolve.core.loop.build_llm", return_value=_llm(response)),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"][
        "prompt_prior_score_provenance_report"
    ]

    assert report["validation"]["ok"] is True
    assert validate_prompt_prior_score_provenance_report(report)["ok"] is True
    assert report["feedback_section_policy_record_count"] == 1
    assert report["feedback_section_global_policy_record_count"] == 1
    assert (
        report["claim_readiness"]["feedback_section_global_truncation_policy"]
        is True
    )
    assert "feedback_section_global_truncation_policy" not in (
        report["claim_readiness"]["remaining_gap"]
    )

    score_row = report["records"][0]["score_records"][0]
    display = score_row["feedback_section_display"]
    assert display["schema"] == (
        "libreevolve.prompt_prior_feedback_section_display.v1"
    )
    assert display["global_cap_chars"] == 1800
    assert display["global_cap_policy"] == (
        "fixed_prompt_feedback_text_chars_after_section_caps"
    )
    assert display["selected_sections"] == ["execution_output", "stage_summary"]
    assert display["section_order"][:2] == ["stage_summary", "execution_output"]
    assert display["section_caps"] == {"execution_output": 0}
    sections = {section["name"]: section for section in display["section_records"]}
    assert sections["stage_summary"]["prompt_visible"] is True
    assert sections["execution_output"]["has_source"] is True
    assert sections["execution_output"]["prompt_visible"] is False
    assert sections["execution_output"]["omission_reason"] == (
        "feedback_section_suppressed_by_prompt_context_policy_cap"
    )

    table_row = json.loads(
        (run_dir / "prompt_prior_score_table.jsonl").read_text(encoding="utf-8")
    )
    assert table_row["feedback_section_display"]["global_cap_chars"] == 1800
    assert "stage_summary" in table_row["feedback_section_display"]["visible_sections"]
    assert table_row["feedback_section_display"]["suppressed_sections"][0] == {
        "name": "execution_output",
        "omission_reason": "feedback_section_suppressed_by_prompt_context_policy_cap",
    }

    edited_report = copy.deepcopy(report)
    edited_report["records"][0]["score_records"][0]["feedback_section_display"][
        "global_cap_chars"
    ] = 1799
    validation = validate_prompt_prior_score_provenance_report(edited_report)
    assert validation["ok"] is False
    assert "invalid_feedback_section_global_cap" in {
        issue["code"] for issue in validation["issues"]
    }


def test_runtime_history_reports_prompt_current_binding_for_evolve_block_span():
    tmpdir = tempfile.mkdtemp()
    problem = _problem()
    problem.initial_programs = [
        "# EVOLVE-BLOCK-START solve\nx=1\n# EVOLVE-BLOCK-END\n"
    ]
    response = """<<<SEARCH
x=1
===
x=2
>>>REPLACE"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            problem,
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["prompt_current_binding_report"]

    assert report["validation"]["ok"] is True
    assert validate_prompt_current_binding_report(report)["ok"] is True
    assert report["exact_diff_binding_count"] == 1
    assert report["evolve_block_match_count"] == 1
    assert report["claim_readiness"]["evolve_block_inner_span_mapping"] is True

    match = report["records"][0]["mutation_binding"]["match_records"][0]
    assert match["match_count"] == 1
    assert match["normalized_span"] is not None
    scope = match["evolve_block_scope"]
    assert scope["scope"] == "evolve_block"
    assert scope["target_path"] == "main.py"
    assert scope["block_name"] == "solve"
    assert scope["block_index"] == 0
    assert scope["search_span_in_block"] == [0, 3]
    assert scope["block_content_span"][0] <= match["normalized_span"][0]
    assert scope["block_content_span"][1] >= match["normalized_span"][1]


def test_runtime_history_reports_prompt_current_binding_for_full_mutation_policy():
    tmpdir = tempfile.mkdtemp()

    with patch("libreevolve.core.loop.build_llm", return_value=_llm("x=2")):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_mode="full",
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["prompt_current_binding_report"]

    assert report["validation"]["ok"] is True
    assert validate_prompt_current_binding_report(report)["ok"] is True
    assert report["mutation_mode_counts"] == {"full": 1}
    assert report["exact_diff_binding_count"] == 0
    assert report["full_mode_target_record_count"] == 1
    assert report["claim_readiness"]["full_mode_target_spans_or_block_ids"] is True
    assert "full_mode_target_span_or_block_policy" not in (
        report["claim_readiness"]["remaining_gap"]
    )
    record = report["records"][0]
    binding = record["mutation_binding"]
    assert binding["mode_policy"] == "full_mode_target_span_records"
    assert binding["target_path"] == "main.py"
    assert binding["search_block_count"] == 0
    assert binding["all_search_blocks_match_once"] is False
    assert binding["full_mode_target_count"] == 1
    target = binding["full_mode_target_records"][0]
    assert target["target_scope"] == "whole_file"
    assert target["target_path"] == "main.py"
    assert target["target_span_policy"] == "whole_primary_file_replacement"
    assert target["parent_file"]["normalized_full_file_span"] == [0, 3]
    assert target["candidate_file"]["normalized_full_file_span"] == [0, 3]
    assert report["claim_ready"] is False


def test_runtime_history_reports_prompt_current_binding_for_full_block_target():
    tmpdir = tempfile.mkdtemp()
    problem = _problem()
    problem.initial_programs = [
        "keep = 1\n# EVOLVE-BLOCK-START solve\nx=1\n# EVOLVE-BLOCK-END\n"
    ]

    with patch("libreevolve.core.loop.build_llm", return_value=_llm("x=2")):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_mode="full",
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["prompt_current_binding_report"]

    assert report["validation"]["ok"] is True
    assert validate_prompt_current_binding_report(report)["ok"] is True
    assert report["full_mode_target_record_count"] == 1
    binding = report["records"][0]["mutation_binding"]
    target = binding["full_mode_target_records"][0]
    assert target["target_scope"] == "evolve_block"
    assert target["block_name"] == "solve"
    assert target["target_span_policy"] == "single_parent_evolve_block_content_span"
    assert target["parent_block"]["exists"] is True
    assert target["parent_block"]["block_name"] == "solve"
    assert target["parent_block"]["content_span"] is not None
    assert target["candidate_block"]["exists"] is True
    assert target["candidate_block"]["block_name"] == "solve"
    assert target["parent_block"]["content_sha256"] != (
        target["candidate_block"]["content_sha256"]
    )


def test_runtime_history_reports_prompt_current_binding_for_file_section_spans():
    tmpdir = tempfile.mkdtemp()
    response = """<<<FILE main.py
x=2
>>>FILE"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_mode="full",
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["prompt_current_binding_report"]

    assert report["validation"]["ok"] is True
    assert validate_prompt_current_binding_report(report)["ok"] is True
    assert report["file_section_record_count"] == 1
    assert report["claim_readiness"]["workspace_file_section_span_records"] is True

    binding = report["records"][0]["mutation_binding"]
    assert binding["mode_policy"] == "workspace_file_section_payload_span_records"
    assert binding["file_section_count"] == 1
    section = binding["file_section_records"][0]
    assert section["operation"] == "edit"
    assert section["target_path"] == "main.py"
    assert section["target_span_policy"] == "full_file_replacement_section"
    assert section["body_chars"] == 4
    assert section["parent_file"]["exists"] is True
    assert section["parent_file"]["normalized_full_file_span"] == [0, 3]
    assert section["candidate_file"]["exists"] is True
    assert section["candidate_file"]["normalized_full_file_span"] == [0, 4]
    assert section["parent_file"]["sha256"] != section["candidate_file"]["sha256"]


def test_runtime_history_reports_primary_prompt_instruction_provenance():
    tmpdir = tempfile.mkdtemp()
    problem = _problem()
    problem.initial_programs = ["x=1", "x=0"]
    llm = _TelemetryLLM("x=2")

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_mode="full",
                num_inspirations=1,
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["primary_prompt_instruction_report"]

    assert report["schema"] == "libreevolve.primary_prompt_instruction_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_primary_prompt_instruction_report(report)["ok"] is True
    assert report["generated_candidate_count"] == 1
    assert report["prompt_record_count"] == 1
    assert report["target_solution_link_count"] == 1
    assert report["instruction_hash_count"] == 1
    assert report["inspiration_context_record_count"] == 1
    assert report["telemetry_join_count"] == 1
    assert report["claim_ready"] is True
    assert report["claim_readiness"]["target_solution_hashes_recorded"] is True
    assert report["claim_readiness"]["instruction_hashes_recorded"] is True
    assert report["claim_readiness"]["supporting_inspiration_roles_observed"] is True
    assert report["claim_readiness"]["provider_message_role_placement_recorded"] is True
    assert report["claim_readiness"]["role_separated_provider_messages_supported"] is False
    assert report["claim_readiness"]["full_alphaevolve_primary_prompt_parity"] is False
    assert report["claim_readiness"]["remaining_gap"] == []

    record = report["records"][0]
    assert record["prompt_program_id"].startswith("prompt-seed-")
    assert len(record["prompt_sha256"]) == 64
    target = record["target_solution"]
    assert target["role"] == "target"
    assert target["prompt_visible"] is True
    assert len(target["workspace_sha256"]) == 64
    sampled_roles = {item["role"] for item in record["sampled_prior_solutions"]}
    assert sampled_roles == {"target", "inspiration"}
    assert record["sampled_prior_solution_count"] == 2
    assert len(record["selected_inspiration_ids"]) == 1
    instruction = record["instruction_block"]
    assert instruction["instruction_policy_id"] == (
        "PromptSampler._render_mutation_instructions"
    )
    assert instruction["mutation_instruction_variant"] == "default"
    assert instruction["mutation_instruction_include_example"] is True
    assert len(instruction["instruction_text_sha256"]) == 64
    assert instruction["instruction_text_retention"] == "hash_only_section_budget"
    placement = record["provider_message_role_placement"]
    assert placement["mutation_call_joined"] is True
    assert placement["mutation_call_ids"] == ["call-0"]
    assert placement["scheduler_role"] == "mutation"
    assert placement["provider_payload_shape"] == "serialized_single_prompt_string"
    assert placement["role_separated_messages_supported"] is False
    channels = {item["name"]: item for item in record["required_channel_records"]}
    assert channels["task"]["present"] is True
    assert channels["parent_code"]["present"] is True
    assert channels["mutation_instructions"]["present"] is True
    assert record["required_channels_present"] is True

    edited = copy.deepcopy(report)
    edited["records"][0]["provider_message_role_placement"][
        "role_separated_messages_supported"
    ] = True
    edited["claim_readiness"]["full_alphaevolve_primary_prompt_parity"] = True
    validation = validate_primary_prompt_instruction_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "role_separated_messages_overclaim",
        "full_primary_prompt_parity_overclaim",
    }


def test_runtime_history_reports_natural_language_preamble_metadata():
    tmpdir = tempfile.mkdtemp()
    response = """IDEA: Change x to the accepted value.

This explains the edit before the structured SEARCH/REPLACE payload.
<<<SEARCH
x=1
===
x=2
>>>REPLACE"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                capture_proposal_metadata=True,
            ),
        )

    run_dir = Path(tmpdir) / "t"
    records = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    preamble = child["metadata"]["explanatory_preamble"]
    assert preamble["schema"] == "libreevolve.explanatory_preamble.v1"
    assert preamble["source"] == "freeform_text_before_first_mutation_marker"
    assert preamble["structured_proposal_preamble_present"] is True
    assert "This explains the edit" in preamble["preview"]
    assert "IDEA:" not in preamble["preview"]

    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["natural_language_preamble_report"]

    assert report["schema"] == "libreevolve.natural_language_preamble_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_natural_language_preamble_report(report)["ok"] is True
    assert report["generated_candidate_count"] == 1
    assert report["preamble_record_count"] == 1
    assert report["structured_proposal_plus_preamble_count"] == 1
    assert report["candidate_status_counts"] == {"accepted_history": 1}
    assert report["mutation_mode_counts"] == {"diff": 1}
    assert report["claim_ready"] is False
    assert (
        report["claim_readiness"]["arbitrary_unparsed_rationale_accepted"]
        is False
    )
    record = report["records"][0]
    assert record["preamble"]["sha256"] == preamble["sha256"]
    assert record["structured_proposal_fields"] == ["idea"]
    assert record["admission"]["admitted"] is True
    assert record["evaluation"]["is_valid"] is True


def test_prompt_context_policy_can_enable_proposal_metadata_capture():
    tmpdir = tempfile.mkdtemp()
    response = """IDEA: Use the prompt arm override.
RATIONALE: The policy enabled proposal metadata for this arm.
HYPOTHESIS: The candidate should still validate.
<<<SEARCH
x=1
===
x=2
>>>REPLACE"""
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompt_db",
        templates=["{task}\n{parent_code}\n{mutation_instructions}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={"proposal_metadata_enabled": True},
    )
    prompt_db.record_result(parent_prompt.id, 0.0)

    with (
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
        patch("libreevolve.core.loop.build_llm", return_value=_llm(response)),
    ):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                capture_proposal_metadata=False,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    assert child["metadata"]["proposal"] == {
        "idea": "Use the prompt arm override.",
        "rationale": "The policy enabled proposal metadata for this arm.",
        "hypothesis": "The candidate should still validate.",
    }
    assert child["metadata"]["prompt_diagnostics"]["prompt_context_policy"][
        "proposal_metadata_enabled"
    ] is True
    assert "IDEA:" in child["metadata"]["prompt"]
    assert "IDEA: Use the prompt arm override" not in child["code"]


def test_loop_strips_proposal_metadata_before_full_replacement():
    tmpdir = tempfile.mkdtemp()
    response = """IDEA: Replace the whole primary file.
RATIONALE: Full mode should apply code only.
HYPOTHESIS: The stored candidate code should omit metadata.
note = '''IDEA: this is candidate data'''
x=2
"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_mode="full",
                capture_proposal_metadata=True,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    assert child["code"] == "note = '''IDEA: this is candidate data'''\nx=2\n"
    assert child["metadata"]["diff"] == response
    assert child["metadata"]["proposal"]["idea"] == "Replace the whole primary file."


def test_loop_records_multiline_proposal_metadata_when_enabled():
    tmpdir = tempfile.mkdtemp()
    response = """[IDEA]
Replace the whole primary file.
Keep a second idea line.
[/IDEA]
[RATIONALE]
Full mode should apply code only.
[/RATIONALE]
x=2
"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_mode="full",
                capture_proposal_metadata=True,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    assert child["code"] == "x=2\n"
    assert child["metadata"]["proposal"]["idea"] == (
        "Replace the whole primary file.\nKeep a second idea line."
    )
    assert child["metadata"]["proposal"]["rationale"] == "Full mode should apply code only."


def test_loop_rejects_wrapped_proposal_metadata_before_full_replacement():
    tmpdir = tempfile.mkdtemp()
    response = """IDEA: Replace the whole primary file.
This wrapped idea line is not code.
RATIONALE: Full mode should not apply ambiguous metadata.
x=2
"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_mode="full",
                capture_proposal_metadata=True,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    admission = child["metadata"]["archive_admission"]
    diff_error = child["evaluation"]["metadata"]["diff_error"]
    assert child["code"] == "x=1"
    assert admission["admitted"] is False
    assert admission["reason"] == "invalid_evaluation"
    assert diff_error["reason"] == "malformed_proposal_metadata:multiline_continuation"
    assert diff_error["known"] is True


def test_loop_records_normalized_metrics_and_selection_score():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c): return {'accuracy': 0.8, 'latency': 20.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    problem = Problem(
        name="t",
        task_description="balance metrics",
        metrics=[
            {"name": "accuracy", "primary": True, "bounds": [0.0, 1.0]},
            {"name": "latency", "direction": "minimize", "bounds": [0.0, 100.0]},
        ],
        primary_metric="accuracy",
        primary_bounds=(0.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["x=1"],
        problem_dir=d,
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()) as build:
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))
    build.assert_not_called()

    record = json.loads((Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()[0])
    assert record["metadata"]["normalized_metrics"] == {"accuracy": 0.8, "latency": 0.8}
    assert record["metadata"]["selection_score"] == 0.8
    assert record["metadata"]["selection_policy"]["type"] == "mean_normalized_declared_metrics"
    assert record["metadata"]["archive_admission"]["selection_score"] == 0.8
    assert record["metadata"]["archive_admission"]["objective_vector"] == {
        "policy": "normalized_declared_metric_vector_v1",
        "normalized_metrics": {"accuracy": 0.8, "latency": 0.8},
        "selection_policy": {
            "type": "mean_normalized_declared_metrics",
            "primary_metric": "accuracy",
            "metrics": ["accuracy", "latency"],
        },
    }
    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    frontier = manifest["runtime"]["history"]["objective_frontier"]
    assert frontier["schema"] == "libreevolve.objective_frontier.v1"
    assert frontier["policy"] == "pareto_frontier_over_complete_declared_normalized_metrics"
    assert frontier["metric_order"] == ["accuracy", "latency"]
    assert frontier["program_count_considered"] == 1
    assert frontier["programs"][0]["normalized_metrics"] == {
        "accuracy": 0.8,
        "latency": 0.8,
    }
    metric_leaders = manifest["runtime"]["history"]["objective_metric_leaders"]
    assert metric_leaders["schema"] == "libreevolve.objective_metric_leaders.v1"
    assert metric_leaders["policy"] == "best_program_per_declared_normalized_metric"
    assert metric_leaders["metric_order"] == ["accuracy", "latency"]
    assert metric_leaders["leaders"] == [
        {
            "metric": "accuracy",
            "program_id": record["id"],
            "generation": 0,
            "normalized_metric": 0.8,
            "selection_score": 0.8,
            "normalized_metrics": {"accuracy": 0.8, "latency": 0.8},
        },
        {
            "metric": "latency",
            "program_id": record["id"],
            "generation": 0,
            "normalized_metric": 0.8,
            "selection_score": 0.8,
            "normalized_metrics": {"accuracy": 0.8, "latency": 0.8},
        },
    ]
    metric_archives = manifest["runtime"]["history"]["objective_metric_archives"]
    assert metric_archives["schema"] == "libreevolve.objective_metric_archives.v1"
    assert metric_archives["policy"] == "top_programs_per_declared_normalized_metric"
    assert metric_archives["metric_order"] == ["accuracy", "latency"]
    assert metric_archives["archives"] == [
        {
            "metric": "accuracy",
            "program_count_considered": 1,
            "retained_count": 1,
            "retention_limit": 10,
            "programs": [
                {
                    "metric": "accuracy",
                    "program_id": record["id"],
                    "generation": 0,
                    "normalized_metric": 0.8,
                    "selection_score": 0.8,
                    "normalized_metrics": {"accuracy": 0.8, "latency": 0.8},
                }
            ],
        },
        {
            "metric": "latency",
            "program_count_considered": 1,
            "retained_count": 1,
            "retention_limit": 10,
            "programs": [
                {
                    "metric": "latency",
                    "program_id": record["id"],
                    "generation": 0,
                    "normalized_metric": 0.8,
                    "selection_score": 0.8,
                    "normalized_metrics": {"accuracy": 0.8, "latency": 0.8},
                }
            ],
        },
    ]
    score_index = manifest["runtime"]["history"]["score_index"]
    assert score_index["schema"] == "libreevolve.score_index.v1"
    assert score_index["policy"] == "top_valid_programs_by_selection_score_then_fitness"
    assert score_index["program_count_considered"] == 1
    assert score_index["programs"][0]["program_id"] == record["id"]
    assert score_index["programs"][0]["selection_score"] == 0.8
    assert score_index["programs"][0]["objective_vector"] == {
        "policy": "normalized_declared_metric_vector_v1",
        "normalized_metrics": {"accuracy": 0.8, "latency": 0.8},
        "selection_policy": {
            "type": "mean_normalized_declared_metrics",
            "primary_metric": "accuracy",
            "metrics": ["accuracy", "latency"],
        },
    }
    lineage_index = manifest["runtime"]["history"]["lineage_index"]
    assert lineage_index["schema"] == "libreevolve.lineage_index.v1"
    assert lineage_index["policy"] == "best_valid_programs_grouped_by_root_lineage"
    assert lineage_index["program_count_considered"] == 1
    assert lineage_index["lineage_count"] == 1
    assert lineage_index["lineages"] == [
        {
            "lineage_root_id": record["id"],
            "program_count": 1,
            "retained_count": 1,
            "program_retention_limit": 5,
            "best_program": {
                "program_id": record["id"],
                "lineage_root_id": record["id"],
                "parent_id": None,
                "generation": 0,
                "lineage_depth": 0,
                "selection_score": 0.8,
                "fitness": 0.8,
                "objective_vector": {
                    "policy": "normalized_declared_metric_vector_v1",
                    "normalized_metrics": {"accuracy": 0.8, "latency": 0.8},
                    "selection_policy": {
                        "type": "mean_normalized_declared_metrics",
                        "primary_metric": "accuracy",
                        "metrics": ["accuracy", "latency"],
                    },
                },
            },
            "programs": [
                {
                    "program_id": record["id"],
                    "lineage_root_id": record["id"],
                    "parent_id": None,
                    "generation": 0,
                    "lineage_depth": 0,
                    "selection_score": 0.8,
                    "fitness": 0.8,
                    "objective_vector": {
                        "policy": "normalized_declared_metric_vector_v1",
                        "normalized_metrics": {"accuracy": 0.8, "latency": 0.8},
                        "selection_policy": {
                            "type": "mean_normalized_declared_metrics",
                            "primary_metric": "accuracy",
                            "metrics": ["accuracy", "latency"],
                        },
                    },
                }
            ],
        }
    ]
    descriptor_index = manifest["runtime"]["history"]["descriptor_index"]
    assert descriptor_index["schema"] == "libreevolve.descriptor_index.v1"
    assert descriptor_index["policy"] == "top_valid_programs_per_archive_descriptor"
    assert {
        descriptor["descriptor"] for descriptor in descriptor_index["descriptors"]
    } == {"performance", "complexity", "diversity"}
    performance = next(
        descriptor
        for descriptor in descriptor_index["descriptors"]
        if descriptor["descriptor"] == "performance"
    )
    assert performance["programs"][0]["program_id"] == record["id"]
    assert performance["programs"][0]["descriptor_value"] == 0.8
    resurfacing_index = manifest["runtime"]["history"]["resurfacing_index"]
    assert resurfacing_index["schema"] == "libreevolve.resurfacing_index.v1"
    assert resurfacing_index["metric_order"] == ["accuracy", "latency"]
    assert resurfacing_index["program_count_considered"] == 1
    assert resurfacing_index["programs"][0]["program_id"] == record["id"]
    assert {
        source["source"] for source in resurfacing_index["programs"][0]["sources"]
    } >= {"score", "frontier", "metric", "lineage", "descriptor"}
    failure_index = manifest["runtime"]["history"]["failure_index"]
    assert failure_index["schema"] == "libreevolve.failure_index.v1"
    assert failure_index["failure_record_count"] == 0
    assert failure_index["fingerprints"] == []
    hypothesis_index = manifest["runtime"]["history"]["hypothesis_index"]
    assert hypothesis_index["schema"] == "libreevolve.hypothesis_index.v1"
    assert hypothesis_index["program_count_considered"] == 0
    assert hypothesis_index["programs"] == []
    artifact_index = manifest["runtime"]["history"]["artifact_index"]
    assert artifact_index["schema"] == "libreevolve.artifact_index.v1"
    assert artifact_index["program_count_considered"] == 0
    assert artifact_index["programs"] == []


def test_loop_uses_configured_metric_weights_for_selection_score():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c): return {'accuracy': 0.2, 'latency': 20.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    problem = Problem(
        name="t",
        task_description="weight metrics",
        metrics=[
            {"name": "accuracy", "primary": True, "bounds": [0.0, 1.0], "weight": 3.0},
            {
                "name": "latency",
                "direction": "minimize",
                "bounds": [0.0, 100.0],
                "weight": 1.0,
            },
        ],
        primary_metric="accuracy",
        primary_bounds=(0.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["x=1"],
        problem_dir=d,
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()) as build:
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))
    build.assert_not_called()

    record = json.loads((Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()[0])
    assert record["metadata"]["normalized_metrics"] == {"accuracy": 0.2, "latency": 0.8}
    assert record["metadata"]["selection_score"] == pytest.approx(0.35)
    assert record["metadata"]["selection_policy"] == {
        "type": "weighted_normalized_declared_metrics",
        "metrics": ["accuracy", "latency"],
        "primary_metric": "accuracy",
        "weights": {"accuracy": 3.0, "latency": 1.0},
    }
    assert record["metadata"]["archive_admission"]["objective_vector"][
        "selection_policy"
    ] == record["metadata"]["selection_policy"]


def test_loop_includes_plugin_emitted_declared_objective_metric_in_selection_score():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    problem = Problem(
        name="t",
        task_description="plugin metrics",
        metrics=[
            {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
            {
                "name": "plugin_quality",
                "bounds": [0.0, 10.0],
                "source": "plugin",
            },
        ],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["x=1"],
        problem_dir=d,
    )

    class PluginMetric:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            program.metrics["plugin_quality"] = 2.5
            return score

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            problem,
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[PluginMetric()],
        )

    run_dir = Path(tmpdir) / "t"
    records = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]

    assert child["metrics"]["plugin_quality"] == 2.5
    assert child["metadata"]["score_composition"]["plugins"][0]["metrics_added"] == [
        "plugin_quality"
    ]
    assert child["metadata"]["normalized_metrics"] == {
        "plugin_quality": 0.25,
        "score": 1.0,
    }
    assert child["metadata"]["selection_score"] == pytest.approx(0.625)
    assert child["metadata"]["selection_policy"] == {
        "type": "mean_normalized_declared_metrics",
        "metrics": ["score", "plugin_quality"],
        "primary_metric": "score",
    }
    assert child["metadata"]["archive_admission"]["objective_vector"] == {
        "policy": "normalized_declared_metric_vector_v1",
        "normalized_metrics": {"plugin_quality": 0.25, "score": 1.0},
        "selection_policy": child["metadata"]["selection_policy"],
    }

    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["problem"]["objective_schema"]["metrics"][1]["source"] == "plugin"
    metric_archives = manifest["runtime"]["history"]["objective_metric_archives"]
    plugin_archive = next(
        archive
        for archive in metric_archives["archives"]
        if archive["metric"] == "plugin_quality"
    )
    assert plugin_archive["program_count_considered"] == 1
    assert plugin_archive["programs"][0]["program_id"] == child["id"]
    assert plugin_archive["programs"][0]["normalized_metric"] == 0.25


def test_loop_includes_final_fitness_sourced_objective_metric_after_plugins():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    problem = Problem(
        name="t",
        task_description="final score objective",
        metrics=[
            {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
            {
                "name": "final_quality",
                "bounds": [0.0, 1.0],
                "source": "final_fitness",
            },
        ],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["x=1"],
        problem_dir=d,
    )

    class PenalizeFinalFitness:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            return 0.4

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            problem,
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[PenalizeFinalFitness()],
        )

    run_dir = Path(tmpdir) / "t"
    records = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]

    assert child["fitness"] == 0.4
    assert child["metrics"]["final_quality"] == 0.4
    assert child["metadata"]["score_composition"]["final_fitness"] == 0.4
    assert child["metadata"]["normalized_metrics"] == {
        "final_quality": 0.4,
        "score": 1.0,
    }
    assert child["metadata"]["selection_score"] == pytest.approx(0.7)
    assert child["metadata"]["archive_admission"]["objective_vector"] == {
        "policy": "normalized_declared_metric_vector_v1",
        "normalized_metrics": {"final_quality": 0.4, "score": 1.0},
        "selection_policy": {
            "type": "mean_normalized_declared_metrics",
            "metrics": ["score", "final_quality"],
            "primary_metric": "score",
        },
    }

    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["problem"]["objective_schema"]["metrics"][1]["source"] == (
        "final_fitness"
    )
    metric_archives = manifest["runtime"]["history"]["objective_metric_archives"]
    final_archive = next(
        archive
        for archive in metric_archives["archives"]
        if archive["metric"] == "final_quality"
    )
    assert final_archive["programs"][0]["program_id"] == records[0]["id"]
    assert final_archive["programs"][1]["program_id"] == child["id"]
    assert final_archive["programs"][1]["normalized_metric"] == 0.4


def test_loop_includes_feedback_filled_objective_metric_in_selection_score():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c): return {'score': 0.4, 'is_valid': True}\n",
        encoding="utf-8",
    )
    problem = Problem(
        name="t",
        task_description="balance evaluator and feedback metrics",
        metrics=[
            {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
            {
                "name": "review_latency_ms",
                "direction": "minimize",
                "bounds": [0.0, 100.0],
                "source": "feedback",
            },
        ],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["x=1"],
        problem_dir=d,
    )
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        ('{"score": 25, "feedback": "lower is better"}', 0),
    ]

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                llm_feedback=[
                    {
                        "name": "latency_review",
                        "metric": "review_latency_ms",
                        "objective_metric": True,
                        "weight": 0.0,
                    }
                ],
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    assert child["metrics"]["review_latency_ms"] == 25.0
    assert child["metadata"]["normalized_metrics"] == {
        "score": 0.4,
        "review_latency_ms": 0.75,
    }
    assert child["metadata"]["selection_score"] == pytest.approx(0.575)
    assert child["metadata"]["archive_admission"]["selection_score"] == pytest.approx(0.575)
    assert child["metadata"]["archive_admission"]["objective_vector"] == {
        "policy": "normalized_declared_metric_vector_v1",
        "normalized_metrics": {
            "review_latency_ms": 0.75,
            "score": 0.4,
        },
        "selection_policy": {
            "type": "mean_normalized_declared_metrics",
            "primary_metric": "score",
            "metrics": ["score", "review_latency_ms"],
        },
    }
    feedback = child["evaluation"]["metadata"]["llm_feedback"][0]
    assert feedback["objective_metric"] is True
    assert feedback["objective_metric_schema"]["source"] == "problem_objective_schema"
    feedback_index = (
        json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"][
            "history"
        ]["feedback_index"]
    )
    assert feedback_index["schema"] == "libreevolve.feedback_index.v1"
    assert feedback_index["policy"] == "top_program_feedback_records_by_grader"
    assert feedback_index["graders"][0]["feedback_name"] == "latency_review"
    assert feedback_index["graders"][0]["programs"][0]["program_id"] == child["id"]
    assert feedback_index["graders"][0]["programs"][0]["normalized_score"] == 0.75
    assert feedback_index["graders"][0]["programs"][0]["objective_metric"] is True
    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    contract = manifest["runtime"]["history"]["paper_evaluator_metric_contract"]
    assert contract["schema"] == "libreevolve.paper_evaluator_metric_contract.v1"
    assert contract["validation"]["ok"] is True
    assert validate_paper_evaluator_metric_contract(contract)["ok"] is True
    assert contract["claim_ready"] is True
    assert contract["declared_metric_names"] == ["score", "review_latency_ms"]
    assert contract["paper_metric_names"] == ["score"]
    assert contract["paper_metric_count"] == 1
    assert contract["excluded_declared_metrics"] == [
        {
            "name": "review_latency_ms",
            "source": "feedback",
            "reason": "declared_metric_source_feedback_not_evaluator",
        }
    ]
    assert contract["validity_gate"]["field"] == "is_valid"
    assert contract["validity_gate"]["scored_metric"] is False
    assert contract["validity_gate"]["valid_true_count"] == 2
    assert "is_valid" in {
        field["field"] for field in contract["excluded_reserved_fields"]
    }
    assert "program_output" in {
        field["field"] for field in contract["excluded_reserved_fields"]
    }
    score_metric, feedback_metric = contract["metrics"]
    assert score_metric["paper_metric"] is True
    assert score_metric["source"] == "evaluator"
    assert score_metric["maximize_transform"] == "raw_value"
    assert score_metric["observed_values"][-1]["raw_value"] == 0.4
    assert score_metric["observed_values"][-1]["normalized_value"] == 0.4
    assert feedback_metric["paper_metric"] is False
    assert feedback_metric["source"] == "feedback"
    assert feedback_metric["maximize_transform"] == "upper_bound_minus_raw_value"
    assert feedback_metric["observed_values"][-1]["raw_value"] == 25.0
    assert feedback_metric["observed_values"][-1]["normalized_value"] == 0.75
    table = manifest["runtime"]["history"]["paper_metric_table_export"]
    assert table["schema"] == "libreevolve.paper_metric_table_export.v1"
    assert table["validation"]["ok"] is True
    assert validate_paper_metric_table_export(table)["ok"] is True
    assert table["source"] == "runtime.history.paper_evaluator_metric_contract"
    assert table["paper_metric_names"] == ["score"]
    assert table["columns"] == [
        "metric_name",
        "program_id",
        "is_valid",
        "primary",
        "direction",
        "raw_value",
        "raw_display",
        "maximized_value",
        "maximized_display",
        "normalized_value",
        "normalized_display",
    ]
    assert table["row_count"] == 2
    assert table["rows_truncated"] is False
    assert len(table["table_sha256"]) == 64
    assert table["display_policy"]["raw_value_significant_digits"] == 12
    assert table["display_policy"]["normalized_value_decimal_places"] == 6
    assert table["claim_ready"] is True
    assert table["claim_readiness"]["single_run_paper_metric_table"] is True
    assert table["claim_readiness"]["cross_run_metric_contract_diff"] is False
    assert table["claim_readiness"]["remaining_gap"] == [
        "cross_run_metric_contract_diff_report"
    ]
    assert table["excluded_declared_metrics"] == contract["excluded_declared_metrics"]
    assert [row["metric_name"] for row in table["rows"]] == ["score", "score"]
    assert [row["program_id"] for row in table["rows"]] == [
        records[0]["id"],
        child["id"],
    ]
    assert table["rows"][-1]["raw_value"] == 0.4
    assert table["rows"][-1]["raw_display"] == "0.4"
    assert table["rows"][-1]["maximized_value"] == 0.4
    assert table["rows"][-1]["maximized_display"] == "0.4"
    assert table["rows"][-1]["normalized_value"] == 0.4
    assert table["rows"][-1]["normalized_display"] == "0.400000"

    oracle_registry = manifest["runtime"]["history"]["evaluator_oracle_registry"]
    assert oracle_registry["schema"] == "libreevolve.evaluator_oracle_registry.v1"
    assert oracle_registry["validation"]["ok"] is True
    assert validate_evaluator_oracle_registry(oracle_registry)["ok"] is True
    assert oracle_registry["oracle_count"] == 2
    assert oracle_registry["claim_ready"] is False
    assert "independent_cross_oracle_disagreement_outcome_evidence" in (
        oracle_registry["claim_readiness"]["remaining_gap"]
    )
    default_oracle, feedback_oracle = oracle_registry["oracles"]
    assert default_oracle["oracle_id"] == "evaluator:default"
    assert default_oracle["oracle_type"] == "deterministic_validator"
    assert default_oracle["authority"] == "candidate_validity_and_metric_gate"
    assert default_oracle["metric_ownership"] == ["score"]
    assert default_oracle["source"]["role"] == "default"


    assert feedback_oracle["oracle_id"] == "llm_feedback:latency_review"
    assert feedback_oracle["oracle_type"] == "llm_judge"
    assert feedback_oracle["metric_ownership"] == ["review_latency_ms"]
    assert oracle_registry["metric_ownership"] == [
        {
            "metric": "score",
            "source": "evaluator",
            "primary": True,
            "oracle_id": "evaluator:default",
            "paper_evaluator_metric": True,
        },
        {
            "metric": "review_latency_ms",
            "source": "feedback",
            "primary": False,
            "oracle_id": "llm_feedback:latency_review",
            "paper_evaluator_metric": False,
        },
    ]
    assert oracle_registry["merge_policy"]["evaluator_policy"] == "single_default_validator"
    assert oracle_registry["merge_policy"]["llm_feedback_policy"] == (
        "synchronous_post_evaluator_feedback_graders"
    )
    arbitration = oracle_registry["arbitration_policy"]
    assert arbitration["schema"] == "libreevolve.evaluator_oracle_arbitration_policy.v1"
    assert arbitration["conflict_resolution"]["validity_owner"] == (
        "deterministic_evaluator_cascade"
    )
    assert arbitration["conflict_resolution"]["feedback_can_override_validity"] is False
    assert arbitration["claim_readiness"]["independent_evaluator_oracle_arbitration"] is False
    assert arbitration["claim_readiness"]["independent_oracle_count"] == 0
    assert arbitration["claim_readiness"]["reference_or_statistical_oracle_count"] == 0
    assert [record["oracle_id"] for record in arbitration["authority_matrix"]] == [
        "evaluator:default",
        "llm_feedback:latency_review",
    ]
    assert arbitration["authority_matrix"][0]["benchmark_sufficiency"] == (
        "local_validator_gate_not_independent_benchmark_sufficient"
    )
    assert arbitration["authority_matrix"][0]["conflict_role"] == (
        "primary_local_validity_gate"
    )
    assert arbitration["authority_matrix"][1]["benchmark_sufficiency"] == (
        "feedback_only_not_validity_sufficient"
    )
    assert arbitration["authority_matrix"][1]["conflict_role"] == (
        "post_hoc_feedback_no_validity_override"
    )
    assert oracle_registry["runtime_summary"]["evaluated_program_count"] == 2
    assert oracle_registry["runtime_summary"]["llm_feedback_record_count"] == 1
    outcomes = oracle_registry["disagreement_outcomes"]
    assert outcomes["schema"] == "libreevolve.evaluator_oracle_disagreement_outcomes.v1"
    assert outcomes["candidate_with_feedback_count"] == 1
    assert outcomes["outcome_count"] == 1
    assert outcomes["disagreement_count"] == 0
    assert outcomes["feedback_discard_after_evaluator_pass_count"] == 0
    assert outcomes["records"][0]["outcome"] == "feedback_accept_after_evaluator_pass"
    assert outcomes["records"][0]["disagreement_observed"] is False
    assert outcomes["claim_readiness"][
        "independent_cross_oracle_disagreement_outcomes"
    ] is False

    scope = manifest["runtime"]["history"]["automated_evaluator_scope_report"]
    assert scope["schema"] == "libreevolve.automated_evaluator_scope_report.v1"
    assert scope["validation"]["ok"] is True
    assert validate_automated_evaluator_scope_report(scope)["ok"] is True
    assert scope["automated_evaluator_available"] is True
    assert scope["evaluator_record_count"] == 1
    assert scope["evaluator_records"][0]["evaluator_id"] == "evaluator:default"
    assert scope["evaluator_records"][0]["automated"] is True
    assert scope["evaluator_records"][0]["manual_experiment"] is False
    assert scope["configured_llm_feedback_count"] == 1
    assert scope["runtime_summary"]["evaluated_program_count"] == 2
    assert scope["runtime_summary"]["generated_evaluated_count"] == 1
    assert scope["runtime_summary"]["llm_feedback_record_count"] == 1
    assert scope["runtime_summary"]["manual_feedback_record_count"] == 0
    assert scope["machine_feedback_policy"]["manual_experiment_candidate_feedback"] is False
    assert scope["machine_feedback_policy"]["llm_only_idea_review_candidate_feedback"] is False
    assert scope["machine_feedback_policy"]["transition_to_executable_code_required"] is True
    assert scope["manual_experiment_boundary"]["status"] == (
        "excluded_from_current_candidate_evaluation_scope"
    )
    assert scope["llm_only_idea_feedback_boundary"]["status"] == (
        "post_evaluator_feedback_only"
    )
    assert scope["llm_only_idea_feedback_boundary"]["primary_validity_gate"] is False
    assert scope["claim_ready"] is False


def test_paper_metric_cross_run_report_compares_metric_tables():
    tmpdir = tempfile.mkdtemp()
    evolve(
        _problem("def evaluate(c): return {'score': 0.2, 'is_valid': True}"),
        Config(max_generations=0, log_dir=tmpdir, problem_name="metric_a"),
    )
    evolve(
        _problem("def evaluate(c): return {'score': 0.8, 'is_valid': True}"),
        Config(max_generations=0, log_dir=tmpdir, problem_name="metric_b"),
    )
    manifest_a = json.loads((Path(tmpdir) / "metric_a" / "manifest.json").read_text())
    manifest_b = json.loads((Path(tmpdir) / "metric_b" / "manifest.json").read_text())

    report = paper_metric_cross_run_report(
        [manifest_a, manifest_b],
        run_labels=["seed_low", "seed_high"],
    )

    assert report["schema"] == "libreevolve.paper_metric_cross_run_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_paper_metric_cross_run_report(report)["ok"] is True
    assert report["run_count"] == 2
    assert report["metric_names"] == ["score"]
    assert report["table_record_count"] == 2
    assert report["drift_count"] == 0
    assert report["claim_ready"] is True
    assert report["claim_readiness"]["cross_run_metric_contract_diff"] is True
    assert report["claim_readiness"]["remaining_gap"] == []
    assert [record["run_id"] for record in report["table_records"]] == [
        "seed_low",
        "seed_high",
    ]
    assert all(len(record["table_sha256"]) == 64 for record in report["table_records"])

    drifted_manifest = copy.deepcopy(manifest_b)
    drifted_manifest["runtime"]["history"]["paper_metric_table_export"][
        "paper_metric_names"
    ] = ["score", "latency"]
    drifted = paper_metric_cross_run_report(
        [manifest_a, drifted_manifest],
        run_labels=["seed_low", "schema_drift"],
    )
    assert drifted["validation"]["ok"] is True
    assert validate_paper_metric_cross_run_report(drifted)["ok"] is True
    assert drifted["claim_ready"] is False
    assert drifted["claim_readiness"]["remaining_gap"] == [
        "metric_contract_or_display_policy_drift"
    ]
    assert drifted["drift_records"][0]["drift_type"] == "metric_contract"
    assert drifted["drift_records"][0]["field"] == "paper_metric_names"

    edited = copy.deepcopy(report)
    edited["drift_count"] = 99
    validation = validate_paper_metric_cross_run_report(edited)
    assert validation["ok"] is False
    assert "drift_count_mismatch" in {
        issue["code"] for issue in validation["issues"]
    }


def test_evaluator_oracle_registry_validation_rejects_malformed_arbitration_policy():
    report = {
        "schema": "libreevolve.evaluator_oracle_registry.v1",
        "source": "startup_manifest_and_runtime_history",
        "oracle_count": 1,
        "oracles": [
            {
                "oracle_id": "evaluator:default",
                "oracle_type": "deterministic_validator",
                "role": "default_problem_validator",
                "authority": "candidate_validity_and_metric_gate",
                "input_schema": "evaluate(code)",
                "output_schema": "declared_metrics_plus_boolean_is_valid",
                "metric_ownership": ["score"],
                "failure_policy": "invalid_evaluation_blocks_database_admission",
                "prompt_feedback_linkage": "evaluation_summary",
            }
        ],
        "metric_ownership": [
            {
                "metric": "score",
                "source": "evaluator",
                "primary": True,
                "oracle_id": "evaluator:default",
                "paper_evaluator_metric": True,
            }
        ],
        "merge_policy": {"schema": "libreevolve.evaluator_oracle_merge_policy.v1"},
        "arbitration_policy": {
            "schema": "libreevolve.evaluator_oracle_arbitration_policy.v1",
            "authority_matrix": [],
            "conflict_resolution": {},
            "failure_handling": {},
            "claim_readiness": {
                "independent_evaluator_oracle_arbitration": True
            },
        },
        "runtime_summary": {},
        "disagreement_outcomes": {
            "schema": "libreevolve.evaluator_oracle_disagreement_outcomes.v1",
            "source": "history_evaluation_stages_and_metadata_llm_feedback",
            "records_limit": 100,
            "records_truncated": False,
            "candidate_with_feedback_count": 0,
            "outcome_count": 0,
            "disagreement_count": 0,
            "feedback_discard_after_evaluator_pass_count": 0,
            "evaluator_invalid_feedback_skipped_count": 0,
            "records": [],
            "policy": {
                "validity_owner": "deterministic_evaluator_cascade",
                "feedback_disagreement_policy": "post_hoc_feedback",
                "independent_reference_or_statistical_oracle": False,
            },
            "claim_readiness": {
                "observed_post_hoc_feedback_disagreement_outcomes": False,
                "independent_cross_oracle_disagreement_outcomes": False,
                "remaining_gap": [
                    "independent_reference_checker_or_statistical_test_oracles",
                    "per_benchmark_oracle_sufficiency_evidence",
                    "independent_cross_oracle_disagreement_outcome_records",
                ],
            },
        },
        "prompt_feedback_linkage": {},
        "claim_ready": False,
        "claim_readiness": {},
    }

    validation = validate_evaluator_oracle_registry(report)
    codes = {issue["code"] for issue in validation["issues"]}

    assert validation["ok"] is False
    assert "invalid_authority_matrix_count" in codes
    assert "invalid_authority_matrix_oracles" in codes
    assert "arbitration_overclaim" in codes


def test_evaluation_budget_stops_before_llm_mutation():
    tmpdir = tempfile.mkdtemp()
    llm = _llm()

    with patch("libreevolve.core.loop.build_llm", return_value=llm) as build:
        best = evolve(
            _problem(),
            Config(
                max_generations=5,
                max_evaluations=1,
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    assert best is not None
    build.assert_not_called()
    llm.generate.assert_not_called()
    run_dir = Path(tmpdir) / "t"
    records = [json.loads(line) for line in (run_dir / "history.jsonl").read_text().splitlines()]
    assert len(records) == 1
    assert records[0]["metadata"]["budget"]["consumed"]["evaluations"] == 1
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["config"]["max_evaluations"] == 1
    runtime = manifest["runtime"]
    assert runtime["stop_reason"] == "max_evaluations"
    assert runtime["status"] == "completed"
    wall_clock = runtime["wall_clock"]
    assert wall_clock["schema"] == "utc_run_timestamps_v1"
    assert wall_clock["final_status"] == "completed"
    assert wall_clock["completed_at"] == wall_clock["finished_at"]
    assert wall_clock["runtime_seconds_source"] == "consumed.runtime_seconds"
    assert wall_clock["resume_segments"][0]["kind"] == "initial_process"
    _parse_utc_timestamp(wall_clock["started_at"])
    _parse_utc_timestamp(wall_clock["completed_at"])
    assert runtime["consumed"]["evaluations"] == 1
    assert runtime["consumed"]["seed_evaluations"] == 1
    assert runtime["consumed"]["candidate_evaluations"] == 0
    assert runtime["history"]["programs_logged"] == 1
    assert runtime["history"]["history_partially_written"] is True
    assert runtime["artifacts"]["history.jsonl"]["exists"] is True
    assert runtime["artifacts"]["history.jsonl"]["bytes"] > 0
    export = runtime["best_artifact_export"]
    assert export["status"] == "completed"
    assert runtime["artifacts"]["best.py"]["exists"] is True
    assert len(runtime["artifacts"]["best.py"]["sha256"]) == 64
    assert runtime["artifacts"]["best_workspace"]["exists"] is True
    assert runtime["artifacts"]["best_workspace"]["tree_hash_status"] == "ok"
    assert (run_dir / "best.py").read_text(encoding="utf-8") == "x=1"
    assert (run_dir / "best_workspace" / "main.py").read_text(encoding="utf-8") == "x=1"


def test_zero_llm_call_budget_stops_before_llm_mutation():
    tmpdir = tempfile.mkdtemp()
    llm = _llm()

    with patch("libreevolve.core.loop.build_llm", return_value=llm) as build:
        best = evolve(
            _problem(),
            Config(
                max_generations=5,
                max_llm_calls=0,
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    assert best is not None
    build.assert_not_called()
    llm.generate.assert_not_called()
    run_dir = Path(tmpdir) / "t"
    records = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    assert len(records) == 1
    assert records[0]["metadata"]["budget"]["consumed"]["llm_calls"] == 0
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["config"]["max_llm_calls"] == 0
    assert manifest["runtime"]["stop_reason"] == "max_llm_calls"
    assert manifest["runtime"]["consumed"]["llm_calls"] == 0


@pytest.mark.parametrize(
    ("field", "stop_reason"),
    [
        ("max_llm_provider_attempts", "max_llm_provider_attempts"),
        ("max_llm_tokens", "max_llm_tokens"),
        ("max_llm_cost_microusd", "max_llm_cost_microusd"),
        ("max_llm_seconds", "max_llm_seconds"),
        ("llm_role_provider_attempt_limits", "llm_role_provider_attempt_limits"),
        ("llm_role_token_limits", "llm_role_token_limits"),
        ("llm_role_cost_microusd_limits", "llm_role_cost_microusd_limits"),
        ("llm_role_seconds_limits", "llm_role_seconds_limits"),
    ],
)
def test_zero_llm_usage_budget_stops_before_provider_construction(field, stop_reason):
    tmpdir = tempfile.mkdtemp()
    llm = _llm()

    with patch("libreevolve.core.loop.build_llm", return_value=llm) as build:
        best = evolve(
            _problem(),
            Config(
                max_generations=5,
                log_dir=tmpdir,
                problem_name="t",
                **{
                    field: {"mutation": 0}
                    if field.startswith("llm_role_")
                    else 0
                },
            ),
        )

    assert best is not None
    build.assert_not_called()
    llm.generate.assert_not_called()
    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["config"][field] == (
        {"mutation": 0} if field.startswith("llm_role_") else 0
    )
    assert manifest["runtime"]["stop_reason"] == stop_reason
    assert manifest["runtime"]["consumed"]["llm_calls"] == 0


def test_llm_call_budget_counts_mutation_and_skips_optional_llm_roles():
    tmpdir = tempfile.mkdtemp()
    llm = _RewardLLM(diff="x=2", feedback='{"score": 0.5, "feedback": "ok"}')

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                mutation_mode="full",
                critique_enabled=True,
                llm_feedback=[
                    {"name": "simplicity", "metric": "simplicity", "weight": 0.2}
                ],
                max_llm_calls=1,
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    assert [call["role"] for call in llm.calls] == ["mutation"]
    run_dir = Path(tmpdir) / "t"
    records = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    assert child["metadata"]["budget"]["stop_reason"] == "max_llm_calls"
    assert child["metadata"]["budget"]["consumed"]["llm_calls"] == 1
    assert child["metadata"]["critique"]["status"] == "skipped"
    assert child["metadata"]["critique"]["role"] == "critique"
    feedback = child["evaluation"]["metadata"]["llm_feedback"][0]
    assert feedback["error"] == "llm_feedback_failed"
    assert "LLM call budget exhausted before feedback:simplicity" in feedback["message"]
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["runtime"]["stop_reason"] == "max_llm_calls"
    assert manifest["runtime"]["consumed"]["llm_calls"] == 1


def test_run_budget_persists_evaluator_attempt_and_sample_accounting():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    ok = stage['attempt'] == 1\n"
        "    return {'score': 1.0 if ok else 0.0, 'is_valid': ok}\n"
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()) as build:
        evolve(
            problem,
            Config(
                max_generations=0,
                log_dir=tmpdir,
                problem_name="t",
                eval_stages=[{"name": "accounted", "samples": 2, "retries": 1}],
            ),
        )

    build.assert_not_called()
    run_dir = Path(tmpdir) / "t"
    record = json.loads((run_dir / "history.jsonl").read_text().splitlines()[0])
    evaluation_accounting = record["evaluation"]["accounting"]
    consumed = record["metadata"]["budget"]["consumed"]
    assert evaluation_accounting["subprocess_attempts"] == 4
    assert evaluation_accounting["configured_stage_samples"] == 2
    assert evaluation_accounting["retry_attempts"] == 2
    assert consumed["evaluator_subprocess_attempts"] == 4
    assert consumed["evaluator_stage_samples"] == 2
    assert consumed["evaluator_retry_attempts"] == 2
    manifest = json.loads((run_dir / "manifest.json").read_text())
    runtime_consumed = manifest["runtime"]["consumed"]
    assert runtime_consumed["evaluator_subprocess_attempts"] == 4
    assert runtime_consumed["evaluator_stage_samples"] == 2
    assert runtime_consumed["evaluator_retry_attempts"] == 2


def test_runtime_history_reports_configured_stage_promotion_and_attrition():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    name = stage['name']\n"
        "    seed = 'x=1' in code\n"
        "    if name == 'smoke':\n"
        "        score = 1.0 if seed else 0.2\n"
        "    else:\n"
        "        score = 1.0 if seed else 0.9\n"
        "    return {'score': score, 'is_valid': True}\n"
    )
    llm = _TelemetryLLM("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE")

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                eval_stages=[
                    {
                        "name": "smoke",
                        "role": "small_scale_filter",
                        "min_score": 0.5,
                    },
                    {"name": "main", "role": "main_test", "min_score": 0.5},
                ],
            ),
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["evaluation_cascade_report"]

    assert report["schema"] == "libreevolve.evaluation_cascade_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_evaluation_cascade_report(report)["ok"] is True
    assert report["configured_candidate_count"] == 2
    assert report["stage_count"] == 2
    assert report["main_test_exposure_count"] == 1
    assert report["early_prune_count"] == 1
    assert report["claim_ready"] is False
    assert report["candidate_stage_record_count"] == 3
    assert report["candidate_stage_records_truncated"] is False
    assert len(report["candidate_stage_records"]) == 3
    assert report["denominator_policy"]["paper_claim_ready"] is False
    assert report["denominator_policy"]["main_test_exposure_denominator"] == (
        "candidates_whose_final_configured_stage_record_passed"
    )
    assert "stage_difficulty_or_scale_labels" in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "benchmark_seed_sample_denominator_policy" in (
        report["claim_readiness"]["remaining_gap"]
    )

    smoke, main = report["stages"]
    assert smoke["name"] == "smoke"
    assert smoke["stage_id"] == "0:smoke"
    assert smoke["difficulty_or_scale"] == {"status": "not_declared"}
    assert isinstance(smoke["source"], dict)
    assert smoke["candidate_count"] == 2
    assert smoke["passed"] == 1
    assert smoke["failed"] == 1
    assert smoke["threshold_failed"] == 1
    assert smoke["promotion_rate"] == 0.5
    assert smoke["sample_count"] == 2
    assert smoke["failure_reasons"] == {"stage_threshold_not_met": 1}
    assert main["name"] == "main"
    assert main["candidate_count"] == 1
    assert main["passed"] == 1
    assert main["failed"] == 0

    stage_records = report["candidate_stage_records"]
    assert [record["history_path"] for record in stage_records] == [
        "history.jsonl",
        "history.jsonl",
        "history.jsonl",
    ]
    assert [record["metadata_path"] for record in stage_records].count(
        "evaluation.metadata.configured_stage_results[0]"
    ) == 2
    assert [record["metadata_path"] for record in stage_records].count(
        "evaluation.metadata.configured_stage_results[1]"
    ) == 1
    assert [record["stage_name"] for record in stage_records].count("smoke") == 2
    assert [record["stage_name"] for record in stage_records].count("main") == 1
    assert all(isinstance(record["source"], dict) for record in stage_records)
    assert all(
        record["accounting"]["configured_stage_samples"] == 1
        for record in stage_records
    )

    overclaimed = copy.deepcopy(report)
    overclaimed["denominator_policy"]["paper_claim_ready"] = True
    validation = validate_evaluation_cascade_report(overclaimed)
    assert validation["ok"] is False
    assert any(
        issue["code"] == "cascade_denominator_overclaim"
        for issue in validation["issues"]
    )

    hypothesis_policy = manifest["runtime"]["history"][
        "cascade_hypothesis_test_policy_report"
    ]
    assert (
        hypothesis_policy["schema"]
        == "libreevolve.cascade_hypothesis_test_policy_report.v1"
    )
    assert hypothesis_policy["validation"]["ok"] is True
    assert validate_cascade_hypothesis_test_policy_report(hypothesis_policy)[
        "ok"
    ] is True
    assert hypothesis_policy["configured_stage_policy_count"] == 2
    assert hypothesis_policy["observed_stage_count"] == 2
    assert hypothesis_policy["current_policy"] == {
        "schema": "libreevolve.cascade_promotion_policy_boundary.v1",
        "promotion_mechanism": "deterministic_threshold_and_artifact_checks",
        "statistical_hypothesis_tests_supported": False,
        "confidence_intervals_supported": False,
        "p_values_supported": False,
        "sequential_stopping_supported": False,
        "false_promotion_budget_supported": False,
        "false_rejection_budget_supported": False,
        "per_sample_observation_retention": (
            "stage_accounting_and_candidate_stage_summary_only"
        ),
        "paper_claim_ready": False,
    }
    assert hypothesis_policy["claim_ready"] is False
    assert (
        hypothesis_policy["claim_readiness"][
            "alphaevolve_section_2_4_hypothesis_testing"
        ]
        is False
    )
    assert "confidence_interval_or_p_value_records" in (
        hypothesis_policy["claim_readiness"]["remaining_gap"]
    )
    smoke_policy, main_policy = hypothesis_policy["stage_policies"]
    assert smoke_policy["stage_id"] == "0:smoke"
    assert smoke_policy["stage_role"] == "small_scale_filter"
    assert smoke_policy["configured_role"] == "small_scale_filter"
    assert smoke_policy["inferred_role"] == "small_scale_filter"
    assert smoke_policy["role_source"] == "configured"
    assert smoke_policy["promotion_decision_source"] == (
        "fixed_threshold_and_artifact_checks"
    )
    assert smoke_policy["sample_design"] == {
        "configured_samples": 1,
        "configured_seed_count": 0,
        "explicit_seeds_configured": False,
        "repeated_sample_or_seed_design": False,
    }
    assert smoke_policy["observed"]["entered"] == 2
    assert smoke_policy["observed"]["passed"] == 1
    assert smoke_policy["observed"]["failed"] == 1
    assert smoke_policy["observed"]["promotion_rate"] == 0.5
    assert smoke_policy["statistical_test"] == {
        "configured": False,
        "test_name": None,
        "metric": None,
        "min": None,
        "min_success_rate": None,
        "success_threshold": None,
        "confidence": None,
        "min_samples": None,
        "test_count": 0,
        "passed": 0,
        "failed": 0,
        "confidence_interval_count": 0,
        "p_value_count": 0,
        "sequential_stopping": False,
        "sequential_stop_count": 0,
        "error_budget_configured": False,
        "error_budget_passed": 0,
        "error_budget_failed": 0,
        "false_promotion_budget": None,
        "false_rejection_budget": None,
    }
    assert main_policy["stage_id"] == "1:main"
    assert main_policy["stage_role"] == "main_test"
    assert main_policy["configured_role"] == "main_test"
    assert main_policy["inferred_role"] == "main_test"
    assert main_policy["role_source"] == "configured"
    assert (
        hypothesis_policy["claim_readiness"]["explicit_stage_roles_configured"]
        is True
    )

    overclaimed_policy = copy.deepcopy(hypothesis_policy)
    overclaimed_policy["claim_ready"] = True
    overclaimed_policy["current_policy"]["statistical_hypothesis_tests_supported"] = True
    overclaimed_policy["current_policy"]["p_values_supported"] = True
    overclaimed_policy["current_policy"]["paper_claim_ready"] = True
    overclaimed_policy["claim_readiness"][
        "alphaevolve_section_2_4_hypothesis_testing"
    ] = True
    overclaimed_policy["stage_policies"][0]["promotion_decision_source"] = (
        "welch_t_test"
    )
    overclaimed_policy["stage_policies"][0]["statistical_test"][
        "sequential_stopping"
    ] = True
    policy_validation = validate_cascade_hypothesis_test_policy_report(
        overclaimed_policy
    )
    assert policy_validation["ok"] is False
    assert {
        "claim_ready_overclaim",
        "policy_statistical_hypothesis_tests_supported_mismatch",
        "policy_p_values_supported_mismatch",
        "policy_paper_claim_ready_overclaim",
        "alphaevolve_hypothesis_testing_overclaim",
        "promotion_source_overclaim",
        "policy_sequential_stopping_supported_mismatch",
    }.issubset({issue["code"] for issue in policy_validation["issues"]})


def test_runtime_history_reports_configured_cascade_hypothesis_test_gate():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    return {'score': stage['seed'], 'is_valid': True}\n"
    )

    evolve(
        problem,
        Config(
            max_generations=0,
            log_dir=tmpdir,
            problem_name="t",
            eval_stages=[
                {
                    "name": "stat_gate",
                    "role": "small_scale_filter",
                    "samples": 3,
                    "seeds": [0.8, 0.85, 0.9],
                    "min_score": 0.7,
                    "hypothesis_test": {
                        "type": "one_sided_lower_confidence_bound",
                        "metric": "score",
                        "min": 0.7,
                        "confidence": 0.8,
                        "min_samples": 3,
                        "error_budget": {
                            "max_false_promotion_rate": 0.25,
                            "max_false_rejection_rate": 0.05,
                            "min_effect_size": 0.2,
                        },
                    },
                },
            ],
        ),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    cascade = manifest["runtime"]["history"]["evaluation_cascade_report"]
    stage = cascade["stages"][0]
    assert stage["hypothesis_test"] == {
        "configured": True,
        "test_count": 1,
        "passed": 1,
        "failed": 0,
        "confidence_interval_count": 1,
        "p_value_count": 1,
        "sequential_stopping_configured": False,
        "sequential_stop_count": 0,
        "error_budget_configured": True,
        "error_budget_passed": 1,
        "error_budget_failed": 0,
        "false_promotion_budget_count": 1,
        "false_rejection_budget_count": 1,
    }
    stage_record = cascade["candidate_stage_records"][0]
    hypothesis_result = stage_record["hypothesis_test_result"]
    assert hypothesis_result["configured"] is True
    assert hypothesis_result["passed"] is True
    assert hypothesis_result["sample_count"] == 3
    assert hypothesis_result["lower_bound"] >= 0.7
    assert hypothesis_result["error_budget"]["passed"] is True
    assert hypothesis_result["error_budget"]["false_promotion"]["estimated_rate"] == pytest.approx(0.2)
    assert hypothesis_result["error_budget"]["false_rejection"]["passed"] is True

    report = manifest["runtime"]["history"]["cascade_hypothesis_test_policy_report"]
    assert report["validation"]["ok"] is True
    assert validate_cascade_hypothesis_test_policy_report(report)["ok"] is True
    assert report["current_policy"]["promotion_mechanism"] == (
        "configured_statistical_gate_after_threshold_checks"
    )
    assert report["current_policy"]["statistical_hypothesis_tests_supported"] is True
    assert report["current_policy"]["confidence_intervals_supported"] is True
    assert report["current_policy"]["p_values_supported"] is True
    assert report["current_policy"]["false_promotion_budget_supported"] is True
    assert report["current_policy"]["false_rejection_budget_supported"] is True
    assert report["current_policy"]["paper_claim_ready"] is False
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["statistical_test_configuration"] is True
    assert report["claim_readiness"]["confidence_or_p_value_records"] is True
    assert (
        report["claim_readiness"]["false_promotion_false_rejection_budgets"]
        is True
    )

    policy = report["stage_policies"][0]
    assert policy["stage_role"] == "small_scale_filter"
    assert policy["configured_role"] == "small_scale_filter"
    assert policy["role_source"] == "configured"
    assert policy["promotion_decision_source"] == "statistical_hypothesis_test"
    assert policy["statistical_test"]["configured"] is True
    assert policy["statistical_test"]["test_name"] == (
        "one_sided_lower_confidence_bound"
    )
    assert policy["statistical_test"]["test_count"] == 1
    assert policy["statistical_test"]["passed"] == 1
    assert policy["statistical_test"]["p_value_count"] == 1
    assert policy["statistical_test"]["error_budget_configured"] is True
    assert policy["statistical_test"]["error_budget_passed"] == 1
    assert policy["statistical_test"]["error_budget_failed"] == 0
    assert policy["statistical_test"]["false_promotion_budget"] == {
        "max_rate": 0.25,
        "observed_count": 1,
        "calibration_method": "one_sided_confidence_level",
    }
    assert policy["statistical_test"]["false_rejection_budget"] == {
        "max_rate": 0.05,
        "min_effect_size": 0.2,
        "observed_count": 1,
        "calibration_method": "normal_approximation_min_effect_size",
    }


def test_runtime_history_reports_hypothesis_test_sequential_stopping():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    return {'score': stage['seed'], 'is_valid': True}\n"
    )

    evolve(
        problem,
        Config(
            max_generations=0,
            log_dir=tmpdir,
            problem_name="t",
            eval_stages=[
                {
                    "name": "stat_gate",
                    "role": "small_scale_filter",
                    "samples": 5,
                    "seeds": [0.9, 0.92, 0.94, 0.1, 0.1],
                    "hypothesis_test": {
                        "type": "one_sided_lower_confidence_bound",
                        "metric": "score",
                        "min": 0.8,
                        "confidence": 0.8,
                        "min_samples": 3,
                        "sequential_stopping": True,
                    },
                },
            ],
        ),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    cascade = manifest["runtime"]["history"]["evaluation_cascade_report"]
    stage = cascade["stages"][0]
    assert stage["sample_count"] == 3
    assert stage["hypothesis_test"]["sequential_stopping_configured"] is True
    assert stage["hypothesis_test"]["sequential_stop_count"] == 1
    stage_record = cascade["candidate_stage_records"][0]
    assert stage_record["accounting"]["configured_stage_samples"] == 3
    assert stage_record["hypothesis_test_result"]["sequential_stop"] == {
        "enabled": True,
        "stopped_early": True,
        "stop_reason": "hypothesis_test_passed_after_min_samples",
        "evaluated_samples": 3,
        "planned_samples": 5,
    }

    report = manifest["runtime"]["history"]["cascade_hypothesis_test_policy_report"]
    assert report["validation"]["ok"] is True
    assert report["current_policy"]["sequential_stopping_supported"] is True
    assert report["claim_readiness"]["sequential_stopping_diagnostics"] is True
    policy = report["stage_policies"][0]
    assert policy["statistical_test"]["sequential_stopping"] is True
    assert policy["statistical_test"]["sequential_stop_count"] == 1


def test_runtime_history_reports_binomial_hypothesis_test_gate():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    return {'score': stage['seed'], 'is_valid': True}\n"
    )

    evolve(
        problem,
        Config(
            max_generations=0,
            log_dir=tmpdir,
            problem_name="t",
            eval_stages=[
                {
                    "name": "success_gate",
                    "role": "small_scale_filter",
                    "samples": 5,
                    "seeds": [1.0, 1.0, 1.0, 1.0, 0.0],
                    "hypothesis_test": {
                        "type": "binomial_success_rate",
                        "metric": "score",
                        "success_threshold": 0.5,
                        "min_success_rate": 0.5,
                        "confidence": 0.8,
                        "min_samples": 5,
                        "error_budget": {
                            "max_false_promotion_rate": 0.25,
                            "max_false_rejection_rate": 0.1,
                            "min_effect_size": 0.4,
                        },
                    },
                },
            ],
        ),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    cascade = manifest["runtime"]["history"]["evaluation_cascade_report"]
    stage = cascade["stages"][0]
    assert stage["hypothesis_test"] == {
        "configured": True,
        "test_count": 1,
        "passed": 1,
        "failed": 0,
        "confidence_interval_count": 1,
        "p_value_count": 1,
        "sequential_stopping_configured": False,
        "sequential_stop_count": 0,
        "error_budget_configured": True,
        "error_budget_passed": 1,
        "error_budget_failed": 0,
        "false_promotion_budget_count": 1,
        "false_rejection_budget_count": 1,
    }
    stage_record = cascade["candidate_stage_records"][0]
    hypothesis_result = stage_record["hypothesis_test_result"]
    assert hypothesis_result["test_name"] == "binomial_success_rate"
    assert hypothesis_result["success_count"] == 4
    assert hypothesis_result["failure_count"] == 1
    assert hypothesis_result["confidence_interval"]["kind"] == "one_sided_wilson_lower"
    assert hypothesis_result["error_budget"]["calibration_method"] == (
        "binomial_wilson_success_rate"
    )

    report = manifest["runtime"]["history"]["cascade_hypothesis_test_policy_report"]
    assert report["validation"]["ok"] is True
    assert validate_cascade_hypothesis_test_policy_report(report)["ok"] is True
    policy = report["stage_policies"][0]
    assert policy["statistical_test"]["test_name"] == "binomial_success_rate"
    assert policy["statistical_test"]["min_success_rate"] == 0.5
    assert policy["statistical_test"]["success_threshold"] == 0.5
    assert policy["statistical_test"]["false_promotion_budget"] == {
        "max_rate": 0.25,
        "observed_count": 1,
        "calibration_method": "one_sided_wilson_confidence_level",
    }
    assert policy["statistical_test"]["false_rejection_budget"] == {
        "max_rate": 0.1,
        "min_effect_size": 0.4,
        "observed_count": 1,
        "calibration_method": "exact_binomial_min_effect_size",
    }


def test_runtime_history_reports_alphaevolve_process_exhibit_mapping():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code):\n"
        "    return {'score': 1.0 if 'x=2' in code else 0.1, 'is_valid': True}\n"
    )

    class ProcessExhibitBackend:
        name = "process-exhibit/model"

        def generate(self, prompt, **kwargs):
            return "<<<<<<< SEARCH\nx=1\n=======\nx=2\n>>>>>>> REPLACE"

    llm = LLMEnsemble([ProcessExhibitBackend()])

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["alphaevolve_process_exhibit_report"]

    assert report["schema"] == "libreevolve.alphaevolve_process_exhibit_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_alphaevolve_process_exhibit_report(report)["ok"] is True
    assert report["figure_count"] == 2
    assert report["pseudocode_step_count"] == 6
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["stable_figure_ids"] is True
    assert report["claim_readiness"]["step_artifact_stream_validation_records"] is True
    assert report["claim_readiness"]["step_stream_row_summaries"] is True
    assert report["claim_readiness"]["component_todo_links"] is True
    assert report["claim_readiness"]["source_diagram_text_record"] is True
    assert report["claim_readiness"]["async_topology_record"] is True
    assert report["claim_readiness"]["alphaevolve_async_pipeline_topology"] is False
    assert report["claim_readiness"]["evaluator_pool_parallelism_record"] is True
    assert report["claim_readiness"]["independent_evaluator_pool_parallelism"] is False
    assert report["claim_readiness"]["rendered_diagram_artifacts"] is True
    assert report["claim_readiness"]["accessibility_exports"] is True
    assert report["claim_readiness"]["exact_diagram_text_reproduction"] is False
    assert report["claim_readiness"]["durable_every_stream_candidate_join"] is True
    assert "exact_source_diagram_layout_reproduction" in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "exact_source_diagram_text_reproduction" not in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "alphaevolve_async_pipeline_topology_implementation" in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "independent_evaluator_pool_parallelism_implementation" in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "async_controller_sampler_evaluator_topology" not in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "independent_evaluator_pool_parallelism" not in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "durable_llm_stream_candidate_joins" not in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "semantic_candidate_level_step_stream_join_against_each_stream" not in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "row_level_step_stream_validation_against_each_stream" not in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "artifact_level_step_validation_against_each_stream" not in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "rendered_process_diagram_artifacts_and_hashes" not in (
        report["claim_readiness"]["remaining_gap"]
    )

    figures = {figure["figure_id"]: figure for figure in report["figures"]}
    assert set(figures) == {"alphaevolve_figure_1", "alphaevolve_figure_2"}
    assert figures["alphaevolve_figure_1"]["local_pdf_page"] == 3
    assert figures["alphaevolve_figure_2"]["local_pdf_page"] == 4
    assert report["rendered_artifact_count"] == 2
    assert report["accessibility_export_count"] == 2
    figure_1_artifact = figures["alphaevolve_figure_1"]["rendered_artifact"]
    assert figure_1_artifact["status"] == "generated"
    assert figure_1_artifact["artifact_kind"] == "mermaid_source"
    assert figure_1_artifact["path"] == "paper_artifacts/process_exhibit/figure_1.mmd"
    figure_1_mermaid = Path(tmpdir) / "t" / figure_1_artifact["path"]
    assert figure_1_mermaid.exists()
    assert "flowchart LR" in figure_1_mermaid.read_text(encoding="utf-8")
    assert len(figure_1_artifact["sha256"]) == 64
    figure_2_accessibility = figures["alphaevolve_figure_2"]["accessibility_export"]
    assert figure_2_accessibility["artifact_kind"] == "accessibility_text"
    assert figure_2_accessibility["path"] == (
        "paper_artifacts/process_exhibit/figure_2_accessibility.txt"
    )
    assert "database.sample()" in (
        Path(tmpdir) / "t" / figure_2_accessibility["path"]
    ).read_text(encoding="utf-8")

    figure_2_steps = figures["alphaevolve_figure_2"]["pseudocode_steps"]
    assert [step["displayed_call"] for step in figure_2_steps] == [
        "database.sample()",
        "prompt_sampler.build(...)",
        "llm.generate(...)",
        "apply_diff(...)",
        "evaluator.execute(...)",
        "database.add(...)",
    ]
    assert figure_2_steps[0]["local_component"].startswith("ProgramDatabase")
    assert figure_2_steps[2]["evidence_paths"] == [
        "llm_calls.jsonl",
        "controller_budget_events.jsonl",
    ]
    assert report["step_stream_validation_count"] == 6
    assert report["stream_row_evidence_count"] == 7
    stream_rows_by_path = {
        evidence["path"]: evidence for evidence in report["stream_row_evidence"]
    }
    assert stream_rows_by_path["history.jsonl"]["status"] == "rows_recorded"
    assert stream_rows_by_path["history.jsonl"]["line_numbers"] == [1, 2]
    assert stream_rows_by_path["history.jsonl"]["row_identifiers"][0]["id"].startswith(
        "candidate-"
    )
    assert stream_rows_by_path["prompt_history.jsonl"]["row_count"] >= 1
    assert stream_rows_by_path["controller_budget_events.jsonl"]["row_count"] >= 1
    assert stream_rows_by_path["llm_calls.jsonl"]["status"] == "rows_recorded"
    step_validation_by_id = {
        validation["step_id"]: validation
        for validation in report["step_stream_validations"]
    }
    generate_validation = step_validation_by_id["fig2.step_3_generate"]
    assert generate_validation["all_artifact_records_resolved"] is True
    assert generate_validation["artifact_paths"] == [
        "llm_calls.jsonl",
        "controller_budget_events.jsonl",
    ]
    assert generate_validation["stream_records"][0]["artifact_record_present"] is True
    assert generate_validation["stream_records"][0]["row_summary_recorded"] is True
    assert generate_validation["stream_records"][0]["row_level_join"] is False
    assert generate_validation["stream_records"][1]["row_summary_recorded"] is True
    assert generate_validation["stream_records"][1]["row_line_numbers"]
    evaluator_validation = step_validation_by_id["fig2.step_5_execute_evaluator"]
    assert "evaluator_artifacts" in evaluator_validation["artifact_paths"]
    assert evaluator_validation["all_artifact_records_resolved"] is True
    assert evaluator_validation["row_summary_record_count"] >= 1
    assert report["component_todo_link_count"] == 3
    source_text = report["source_diagram_text_record"]
    assert source_text["schema"] == (
        "libreevolve.process_exhibit_source_diagram_text_record.v1"
    )
    assert source_text["record_status"] == "attached"
    assert source_text["source_paper"] == "papers/2506.13131__AlphaEvolve.pdf"
    assert source_text["source_figure_ids"] == ["Figure 1", "Figure 2"]
    assert source_text["extraction_tool"] == "pypdf.extract_text"
    assert source_text["extraction_scope"] == (
        "source_page_text_extract_not_visual_diagram_layout"
    )
    assert source_text["exact_diagram_text_reproduction"] is False
    assert source_text["exact_diagram_layout_reproduction"] is False
    assert source_text["figure_record_count"] == 2
    assert source_text["attached_figure_record_count"] == 2
    assert source_text["remaining_gap"] == ["exact_visual_diagram_layout_reproduction"]
    source_records = {
        record["figure_id"]: record for record in source_text["figure_records"]
    }
    assert source_records["alphaevolve_figure_1"]["local_pdf_page"] == 3
    assert source_records["alphaevolve_figure_1"]["source_figure_label_present"] is True
    assert source_records["alphaevolve_figure_1"]["artifact"]["path"] == (
        "paper_artifacts/process_exhibit/source_alphaevolve_figure_1_page_3_text.txt"
    )
    assert source_records["alphaevolve_figure_2"]["local_pdf_page"] == 4
    assert source_records["alphaevolve_figure_2"]["source_figure_label_present"] is True
    assert source_records["alphaevolve_figure_2"]["artifact"]["hash_scope"] == (
        "source_pdf_page_text_extract"
    )
    topology = report["async_topology_record"]
    assert topology["schema"] == "libreevolve.process_exhibit_async_topology_record.v1"
    assert topology["record_status"] == "recorded"
    assert topology["source_report_ref"] == (
        "runtime.history.distributed_pipeline_topology_report"
    )
    assert topology["source_report_validation_ok"] is True
    assert topology["controller_model"] == "single_process_serial_loop"
    assert topology["queue_count"] == 0
    assert topology["asyncio_pipeline"] is False
    assert topology["pending_work_checkpoint_supported"] is False
    assert topology["alphaevolve_async_pipeline_topology"] is False
    assert set(topology["roles"]) == {
        "controller",
        "evaluation_node",
        "llm_sampler",
        "program_database",
    }
    evaluator_pool = report["evaluator_pool_parallelism_record"]
    assert evaluator_pool["schema"] == (
        "libreevolve.process_exhibit_evaluator_pool_parallelism_record.v1"
    )
    assert evaluator_pool["record_status"] == "recorded"
    assert evaluator_pool["source_report_ref"] == (
        "runtime.history.distributed_pipeline_topology_report"
    )
    assert evaluator_pool["source_report_validation_ok"] is True
    assert evaluator_pool["figure_node_id"] == "fig1.evaluator_pool"
    assert evaluator_pool["figure_step_id"] == "fig2.step_5_execute_evaluator"
    assert evaluator_pool["evaluator_node_count"] == 1
    assert evaluator_pool["evaluator_node_ids"] == [
        "evaluation_node:default_validator"
    ]
    assert evaluator_pool["queue_count"] == 0
    assert evaluator_pool["evaluation_dispatch"] == "inline_blocking_local_subprocess"
    assert evaluator_pool["parallel_evaluator_workers"] is False
    assert evaluator_pool["parallelism_scope"] == "none"
    assert evaluator_pool["independent_evaluator_pool_parallelism"] is False
    assert evaluator_pool["compute_hour_wall_clock_compression"] is False
    assert evaluator_pool["wall_clock_compression"]["record_count"] == 0
    assert evaluator_pool["wall_clock_compression"]["wall_clock_compression_observed"] is False
    assert report["candidate_semantic_trace_count"] == 1
    assert report["durable_candidate_stream_join_count"] == 1
    assert report["claim_readiness"]["candidate_semantic_trace_records"] is True
    assert report["claim_readiness"]["durable_every_stream_candidate_join"] is True
    [trace] = report["candidate_semantic_traces"]
    assert trace["candidate_type"] == "generated"
    assert trace["semantic_trace_ready"] is True
    assert trace["durable_every_stream_join"] is True
    assert trace["remaining_gap"] == []
    assert trace["step_join_count"] == 6
    trace_steps = {step["step_id"]: step for step in trace["step_joins"]}
    assert trace_steps["fig2.step_2_build_prompt"][
        "prompt_history_add_line_number"
    ] == 1
    assert trace_steps["fig2.step_2_build_prompt"][
        "prompt_history_score_line_number"
    ] == 2
    assert len(trace_steps["fig2.step_3_generate"]["llm_call_ids"]) == 1
    llm_call_id = trace_steps["fig2.step_3_generate"]["llm_call_ids"][0]
    assert llm_call_id.startswith("llm-call-")
    assert trace_steps["fig2.step_3_generate"]["llm_call_stream_joined"] is True
    assert trace_steps["fig2.step_3_generate"]["llm_call_stream_rows"][0][
        "call_id"
    ] == llm_call_id
    assert trace_steps["fig2.step_3_generate"][
        "controller_llm_call_event_rows"
    ][0]["kind"] == "llm_call"
    assert trace_steps["fig2.step_5_execute_evaluator"][
        "evaluator_result_line_number"
    ] == 2
    assert trace_steps["fig2.step_6_add_database"]["archive_admitted"] is True
    assert trace_steps["fig2.step_6_add_database"][
        "archive_event_stream_joined"
    ] is True
    assert trace_steps["fig2.step_6_add_database"]["archive_event_stream_rows"][0][
        "event_type"
    ] == "admission"
    todo_links_by_gap = {
        link["gap_id"]: link for link in report["component_todo_links"]
    }
    assert "alphaevolve_figure_1" in todo_links_by_gap[
        "exact_source_diagram_layout_reproduction"
    ]["component_ids"]
    assert "fig2.step_5_execute_evaluator" in todo_links_by_gap[
        "independent_evaluator_pool_parallelism_implementation"
    ]["component_ids"]
    assert "fig2.step_3_generate" in todo_links_by_gap[
        "alphaevolve_async_pipeline_topology_implementation"
    ]["component_ids"]
    assert "durable_llm_stream_candidate_joins" not in todo_links_by_gap
    artifact_by_path = {
        artifact["path"]: artifact for artifact in report["artifact_evidence"]
    }
    assert artifact_by_path["history.jsonl"]["present"] is True
    assert artifact_by_path["prompt_history.jsonl"]["present"] is True
    assert "llm_generation_calls" in artifact_by_path["llm_calls.jsonl"]["roles"]
    assert artifact_by_path["controller_budget_events.jsonl"]["present"] is True
    assert artifact_by_path["paper_artifacts/process_exhibit/figure_1.mmd"][
        "present"
    ] is True
    assert artifact_by_path[
        "paper_artifacts/process_exhibit/source_alphaevolve_figure_1_page_3_text.txt"
    ]["present"] is True
    assert "source_pdf_page_text_extract" in artifact_by_path[
        "paper_artifacts/process_exhibit/source_alphaevolve_figure_2_page_4_text.txt"
    ]["roles"]
    assert artifact_by_path[
        "paper_artifacts/process_exhibit/figure_2_accessibility.txt"
    ]["present"] is True
    assert artifact_by_path["manifest.json"]["hash_scope"] == (
        "final_manifest_self_reference_deferred"
    )
    assert report["artifact_evidence_paths"] == list(artifact_by_path)

    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["claim_readiness"]["full_alphaevolve_process_parity"] = True
    validation = validate_alphaevolve_process_exhibit_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_overclaim",
        "process_parity_overclaim",
    }

    edited = copy.deepcopy(report)
    edited["figures"][0]["rendered_artifact"]["sha256"] = "nothex"
    validation = validate_alphaevolve_process_exhibit_report(edited)
    assert validation["ok"] is False
    assert "invalid_rendered_artifact_hash" in {
        issue["code"] for issue in validation["issues"]
    }

    edited = copy.deepcopy(report)
    edited["source_diagram_text_record"]["exact_diagram_text_reproduction"] = True
    validation = validate_alphaevolve_process_exhibit_report(edited)
    assert validation["ok"] is False
    assert "source_diagram_text_overclaim" in {
        issue["code"] for issue in validation["issues"]
    }

    edited = copy.deepcopy(report)
    edited["claim_readiness"]["alphaevolve_async_pipeline_topology"] = True
    validation = validate_alphaevolve_process_exhibit_report(edited)
    assert validation["ok"] is False
    assert "async_topology_overclaim" in {
        issue["code"] for issue in validation["issues"]
    }

    edited = copy.deepcopy(report)
    edited["async_topology_record"]["asyncio_pipeline"] = True
    validation = validate_alphaevolve_process_exhibit_report(edited)
    assert validation["ok"] is False
    assert "async_topology_pipeline_overclaim" in {
        issue["code"] for issue in validation["issues"]
    }

    edited = copy.deepcopy(report)
    edited["claim_readiness"]["independent_evaluator_pool_parallelism"] = True
    validation = validate_alphaevolve_process_exhibit_report(edited)
    assert validation["ok"] is False
    assert "evaluator_pool_parallelism_overclaim" in {
        issue["code"] for issue in validation["issues"]
    }

    edited = copy.deepcopy(report)
    edited["evaluator_pool_parallelism_record"]["parallel_evaluator_workers"] = True
    validation = validate_alphaevolve_process_exhibit_report(edited)
    assert validation["ok"] is False
    assert "parallel_evaluator_workers_mismatch" in {
        issue["code"] for issue in validation["issues"]
    }

    edited = copy.deepcopy(report)
    edited["step_stream_validations"][2]["stream_records"][0]["path"] = "missing.jsonl"
    validation = validate_alphaevolve_process_exhibit_report(edited)
    assert validation["ok"] is False
    assert "step_stream_path_mismatch" in {
        issue["code"] for issue in validation["issues"]
    }


def test_runtime_history_reports_alphaevolve_table1_capability_exhibit():
    tmpdir = tempfile.mkdtemp()
    problem = _problem("def evaluate(c): return {'score': 0.5, 'is_valid': True}")

    evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"][
        "alphaevolve_table1_capability_exhibit_report"
    ]

    assert report["schema"] == (
        "libreevolve.alphaevolve_table1_capability_exhibit_report.v1"
    )
    assert report["validation"]["ok"] is True
    assert validate_alphaevolve_table1_capability_exhibit_report(report)["ok"] is True
    assert report["table_id"] == "alphaevolve_table_1_capability_comparison"
    assert report["source_paper"] == "papers/2506.13131__AlphaEvolve.pdf"
    assert report["local_pdf_page"] == 2
    assert report["row_count"] == 8
    assert report["rendered_artifact_count"] == 2
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["stable_table_id"] is True
    assert report["claim_readiness"]["stable_row_ids"] is True
    assert report["claim_readiness"]["table_exhibit_record_ready"] is True
    assert report["claim_readiness"]["individual_capability_rows_satisfied"] is False
    assert report["claim_readiness"]["full_table1_parity"] is False

    rows = report["rows"]
    assert [row["row_id"] for row in rows] == [
        "table1.function_vs_file_scope",
        "table1.code_length_scale",
        "table1.programming_language_scope",
        "table1.evaluator_workload_scope",
        "table1.llm_sample_efficiency",
        "table1.model_scale_effect",
        "table1.prompt_context_feedback",
        "table1.metric_optimization_scope",
    ]
    assert rows[0]["funsearch_cell"] == "evolves single function"
    assert rows[0]["alphaevolve_cell"] == "evolves entire code file"
    assert all(row["capability_claim_ready"] is False for row in rows)
    assert all(row["evidence_refs"] for row in rows)
    assert all(row["remaining_gap"] for row in rows)

    artifact_by_kind = {
        artifact["artifact_kind"]: artifact for artifact in report["rendered_artifacts"]
    }
    markdown = artifact_by_kind["markdown_table"]
    assert markdown["path"] == "paper_artifacts/table1_capability_comparison/table_1.md"
    assert len(markdown["sha256"]) == 64
    markdown_path = Path(tmpdir) / "t" / markdown["path"]
    assert markdown_path.exists()
    assert "AlphaEvolve Table 1 Capability Comparison" in markdown_path.read_text(
        encoding="utf-8"
    )
    accessibility = artifact_by_kind["accessibility_text"]
    assert accessibility["path"] == (
        "paper_artifacts/table1_capability_comparison/table_1_accessibility.txt"
    )
    assert Path(tmpdir, "t", accessibility["path"]).exists()

    overclaimed = copy.deepcopy(report)
    overclaimed["claim_ready"] = True
    overclaimed["claim_readiness"]["full_table1_parity"] = True
    overclaimed["rows"][0]["capability_claim_ready"] = True
    validation = validate_alphaevolve_table1_capability_exhibit_report(overclaimed)
    assert validation["ok"] is False
    assert {
        "claim_ready_overclaim",
        "full_table1_parity_overclaim",
        "row_capability_overclaim",
    }.issubset({issue["code"] for issue in validation["issues"]})

    bad_artifact = copy.deepcopy(report)
    bad_artifact["rendered_artifacts"][0]["sha256"] = "nothex"
    validation = validate_alphaevolve_table1_capability_exhibit_report(bad_artifact)
    assert validation["ok"] is False
    assert "invalid_artifact_hash" in {
        issue["code"] for issue in validation["issues"]
    }


def test_runtime_history_reports_codebase_scale_benchmark_boundary():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code, workspace):\n"
        "    score = 2.0 if 'VALUE = 2' in code else 1.0\n"
        "    return {'score': score, 'is_valid': True}\n"
    )
    long_helper = "\n".join(f"def helper_{index}(): return {index}" for index in range(60))
    problem.initial_programs = []
    problem.initial_workspaces = [
        {
            "primary_file": "main.py",
            "files": {
                "main.py": "from pkg.helpers import helper_1\nVALUE = 1\n",
                "pkg/helpers.py": long_helper + "\n",
                "pkg/config.py": "SETTING = 'seed'\n",
            },
        }
    ]

    class CodebaseScaleBackend:
        name = "codebase-scale/model"

        def generate(self, prompt, **kwargs):
            return "<<<<<<< SEARCH\nVALUE = 1\n=======\nVALUE = 2\n>>>>>>> REPLACE"

    with patch(
        "libreevolve.core.loop.build_llm",
        return_value=LLMEnsemble([CodebaseScaleBackend()]),
    ):
        evolve(problem, Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["codebase_scale_benchmark_report"]

    assert report["schema"] == "libreevolve.codebase_scale_benchmark_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_codebase_scale_benchmark_report(report)["ok"] is True
    assert report["program_count"] == 2
    assert report["generated_program_count"] == 1
    assert report["multi_file_program_count"] == 2
    assert report["max_file_count"] == 3
    assert report["max_total_text_lines"] >= 62
    assert report["max_changed_file_count_vs_parent"] == 1
    assert report["max_changed_line_count_vs_parent"] == 1
    assert report["threshold_evidence"]["any_three_file_program"] is True
    assert report["threshold_evidence"]["any_multi_file_generated_program"] is True
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["workspace_file_line_scale_measured"] is True
    assert report["claim_readiness"]["generated_change_scale_measured"] is True
    assert report["claim_readiness"]["multi_component_workspace_observed"] is True
    assert report["claim_readiness"]["realistic_codebase_benchmark_fixture"] is False
    assert report["claim_readiness"]["arbitrary_language_runner_scope"] is False
    assert report["claim_readiness"]["build_runner_scope"] is False
    assert report["claim_readiness"]["table1_code_scale_parity"] is False

    generated = [
        record
        for record in report["program_records"]
        if record["candidate_type"] == "generated"
    ][0]
    assert generated["parent_present"] is True
    assert generated["file_count"] == 3
    assert generated["changed_files_vs_parent"] == ["main.py"]
    assert generated["cross_file_change_vs_parent"] is False

    overclaimed = copy.deepcopy(report)
    overclaimed["claim_ready"] = True
    overclaimed["claim_readiness"]["table1_code_scale_parity"] = True
    overclaimed["claim_readiness"]["arbitrary_language_runner_scope"] = True
    validation = validate_codebase_scale_benchmark_report(overclaimed)
    assert validation["ok"] is False
    assert {
        "claim_ready_overclaim",
        "table1_code_scale_parity_overclaim",
        "arbitrary_language_runner_scope_overclaim",
    }.issubset({issue["code"] for issue in validation["issues"]})


def test_runtime_history_reports_existing_codebase_marker_inventory():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code, workspace):\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    problem.initial_programs = []
    problem.initial_workspaces = [
        {
            "primary_file": "main.py",
            "files": {
                "main.py": (
                    "from pkg.helpers import helper\n"
                    "# EVOLVE-BLOCK-START solve\n"
                    "def solve():\n"
                    "    return helper()\n"
                    "# EVOLVE-BLOCK-END\n"
                ),
                "pkg/helpers.py": (
                    "def keep():\n"
                    "    return 1\n"
                    "# EVOLVE-BLOCK-START helper\n"
                    "def helper():\n"
                    "    return keep()\n"
                    "# EVOLVE-BLOCK-END\n"
                ),
                "README.md": "fixture notes\n",
            },
        }
    ]

    evolve(
        problem,
        Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["existing_codebase_integration_report"]

    assert report["schema"] == "libreevolve.existing_codebase_integration_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_existing_codebase_integration_report(report)["ok"] is True
    assert report["program_count"] == 1
    assert report["workspace_program_count"] == 1
    assert report["marked_python_file_count"] == 2
    assert report["evolved_block_count"] == 2
    assert report["unmarked_file_count"] == 1
    assert report["marker_contract"]["start_marker"] == "# EVOLVE-BLOCK-START"
    assert report["integration_boundary"]["original_codebase_identity"] == (
        "not_recorded"
    )
    assert report["source_setup_metadata"]["status"] == "not_provided"
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["marker_span_inventory"] is True
    assert report["claim_readiness"]["source_setup_metadata_recorded"] is False
    assert report["claim_readiness"]["marker_only_setup_diff"] is False
    assert "pre_marker_source_hashes" in report["claim_readiness"]["remaining_gap"]

    record = report["program_records"][0]
    assert record["primary_file"] == "main.py"
    assert len(record["workspace_sha256"]) == 64
    files = {item["path"]: item for item in record["marked_files"]}
    assert set(files) == {"main.py", "pkg/helpers.py"}
    main = files["main.py"]
    assert main["block_count"] == 1
    assert len(main["skeleton_sha256"]) == 64
    block = main["blocks"][0]
    assert block["name"] == "solve"
    assert len(block["span_id"]) == 24
    assert block["score_linked"] is False
    assert record["unmarked_files"][0]["path"] == "README.md"

    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["claim_readiness"]["paper_faithful_existing_codebase_integration"] = True
    validation = validate_existing_codebase_integration_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_overclaim",
        "integration_parity_overclaim",
    }


def test_existing_codebase_setup_metadata_reaches_manifest_and_report():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code, workspace):\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    problem.initial_programs = []
    problem.initial_workspaces = [
        {
            "primary_file": "src/main.py",
            "files": {
                "src/main.py": (
                    "# EVOLVE-BLOCK-START solve\n"
                    "def solve():\n"
                    "    return 1\n"
                    "# EVOLVE-BLOCK-END\n"
                ),
                "data/config.json": '{"mode": "fixture"}\n',
            },
        }
    ]
    problem.codebase_integration_metadata = {
        "original_codebase_id": "fixture-lib-1",
        "upstream_release_artifact": {
            "id": "fixture-lib-v1",
            "version": "1.0.0",
            "source": "local_fixture",
        },
        "pre_marker_source_sha256": [
            {"path": "src/main.py", "sha256": "a" * 64},
        ],
        "marker_added_setup_diff": {
            "summary": "Added one evolve block marker pair.",
            "files_changed": 1,
            "markers_added": 2,
            "non_marker_lines_changed": 0,
        },
        "setup_change_counts": {
            "files_changed": 1,
            "markers_added": 2,
            "non_marker_lines_changed": 0,
        },
        "evaluator_call_path_before_marker_insertion": [
            "validate.py",
            "src/main.py:solve",
        ],
        "evaluator_call_path_after_marker_insertion": [
            "validate.py",
            "src/main.py:solve",
        ],
        "copied_static_asset_source_identity": [
            {
                "path": "data/config.json",
                "source_root": "fixture-lib-v1",
                "sha256": "b" * 64,
            }
        ],
        "codebase_scale_fixture": {
            "status": "smoke",
            "file_count": 3,
            "component_count": 1,
            "upstream_identity_present": True,
        },
        "review": {
            "status": "self_reviewed",
            "notes": "Fixture metadata only.",
        },
    }

    evolve(
        problem,
        Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    metadata = manifest["problem"]["codebase_integration_metadata"]
    report = manifest["runtime"]["history"]["existing_codebase_integration_report"]

    assert metadata["schema"] == "libreevolve.existing_codebase_setup_metadata.v1"
    assert metadata["status"] == "provided"
    assert metadata["metadata_complete"] is True
    assert metadata["original_codebase_id"] == "fixture-lib-1"
    assert report["validation"]["ok"] is True
    assert validate_existing_codebase_integration_report(report)["ok"] is True
    assert report["source_setup_metadata"]["status"] == "provided"
    assert report["source_setup_metadata"]["metadata_complete"] is True
    assert report["integration_boundary"]["original_codebase_identity"] == "fixture-lib-1"
    assert report["integration_boundary"]["upstream_release_artifact_identity"] == (
        "fixture-lib-v1"
    )
    assert report["integration_boundary"]["pre_marker_source_hash_count"] == 1
    assert report["integration_boundary"]["evaluator_entrypoint_continuity"] == (
        "declared_before_and_after_marker_insertion"
    )
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["source_setup_metadata_recorded"] is True
    assert report["claim_readiness"]["source_setup_metadata_complete"] is True
    assert report["claim_readiness"]["marker_only_setup_diff"] is True
    assert report["claim_readiness"]["paper_faithful_existing_codebase_integration"] is False
    assert "paper_faithful_existing_codebase_claim_gate" in report["claim_readiness"]["remaining_gap"]

    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["claim_readiness"]["paper_faithful_existing_codebase_integration"] = True
    validation = validate_existing_codebase_integration_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_overclaim",
        "integration_parity_overclaim",
    }


def test_codebase_setup_metadata_rejects_secret_like_text(tmp_path):
    problem = _problem()
    problem.codebase_integration_metadata = {
        "original_codebase_id": "api_key=sk-proj_secret1234567890",
    }

    with pytest.raises(StrictJsonlError, match="secret-like text"):
        evolve(
            problem,
            Config(max_generations=0, log_dir=str(tmp_path), problem_name="t"),
        )


def test_runtime_history_reports_marker_spelling_provenance():
    tmpdir = tempfile.mkdtemp()

    evolve(
        _problem(),
        Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["marker_spelling_provenance_report"]

    assert report["schema"] == "libreevolve.marker_spelling_provenance_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_marker_spelling_provenance_report(report)["ok"] is True
    assert report["canonical_start_marker"] == "# EVOLVE-BLOCK-START"
    assert report["canonical_end_marker"] == "# EVOLVE-BLOCK-END"
    assert report["compatibility_decision"] == {
        "policy": "canonical_hyphenated_markers_only",
        "space_variant_supported": False,
        "space_variant_probe_error": "orphan_end",
        "compatibility_mode": "not_configured",
        "documentation_policy": (
            "document Figure 3 space spelling as source variant or extraction "
            "uncertainty, not as supported parser syntax"
        ),
    }
    records = {record["record_id"]: record for record in report["records"]}
    canonical = records["alphaevolve_section_2_1_page_4_start"]
    assert canonical["marker_text"] == "# EVOLVE-BLOCK-START"
    assert canonical["local_parser_probe"]["accepted"] is True
    assert canonical["local_parser_probe"]["block_names"] == ["solve"]
    space_variant = records["alphaevolve_figure_3a_page_6_space_start"]
    assert space_variant["marker_text"] == "# EVOLVE-BLOCK START"
    assert space_variant["local_support"] == "unsupported_current_parser"
    assert space_variant["local_parser_probe"]["accepted"] is False
    assert space_variant["local_parser_probe"]["error"] == "orphan_end"
    assert space_variant["source_artifact"]["status"] == "attached"
    assert len(space_variant["source_artifact"]["sha256"]) == 64
    assert space_variant["source_artifact"]["marker_text_found"] is True
    assert space_variant["source_artifact"]["marker_token_found"] is True
    assert space_variant["final_classification"] == (
        "pdf_text_extraction_uncertainty_not_supported_parser_syntax"
    )
    source_artifacts = report["source_artifacts"]
    assert source_artifacts["schema"] == (
        "libreevolve.marker_spelling_source_artifacts.v1"
    )
    assert len(source_artifacts["paper_sha256"]) == 64
    assert source_artifacts["page_artifacts"]["4"]["status"] == "attached"
    figure_3_artifact = source_artifacts["figure_3_marker_text_artifact"]
    assert figure_3_artifact["status"] == "attached"
    assert figure_3_artifact["artifact_path"].endswith(
        "alphaevolve_figure_3a_marker_text.txt"
    )
    assert (Path(tmpdir) / "t" / figure_3_artifact["artifact_path"]).exists()
    assert report["variant_classification"]["classification"] == (
        "pdf_text_extraction_uncertainty_not_supported_parser_syntax"
    )
    assert report["variant_classification"]["parser_compatibility_changed"] is False
    assert report["claim_ready"] is True
    assert report["claim_readiness"]["source_locations_recorded"] is True
    assert report["claim_readiness"]["source_artifact_hashes_attached"] is True
    assert report["claim_readiness"]["exact_figure_3_text_artifact"] is True
    assert report["claim_readiness"]["final_variant_classification"] is True
    assert report["claim_readiness"]["remaining_gap"] == []

    edited = copy.deepcopy(report)
    edited["compatibility_decision"]["space_variant_supported"] = True
    edited["variant_classification"]["parser_compatibility_changed"] = True
    validation = validate_marker_spelling_provenance_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "space_variant_support_overclaim",
        "variant_compatibility_overclaim",
    }


def test_runtime_history_reports_candidate_abstraction_choice():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code, workspace):\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    problem.initial_programs = []
    problem.initial_workspaces = [
        {
            "primary_file": "main.py",
            "files": {
                "main.py": "x = 1\n",
                "notes.txt": "fixture context\n",
            },
            "static_files": [
                {
                    "path": "fixture.bin",
                    "kind": "binary",
                    "sha256": "a" * 64,
                    "bytes": 3,
                }
            ],
        }
    ]

    evolve(
        problem,
        Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["candidate_abstraction_choice_report"]

    assert report["schema"] == "libreevolve.candidate_abstraction_choice_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_candidate_abstraction_choice_report(report)["ok"] is True
    assert report["selected_abstraction"] == "code_file_set"
    assert report["selected_representation"]["manifest_path"] == (
        "policies.candidate_language"
    )
    assert report["selected_representation"]["policy"] == (
        "python_primary_text_workspace_v1"
    )
    assert report["selected_representation"]["candidate_representation"] == (
        "bounded_utf8_text_workspace_with_typed_static_members"
    )
    assert report["selected_representation"]["language_runner_ready"] is False
    assert report["selected_representation"]["policy_validation"]["ok"] is True
    assert report["serializer_runner_linkage"]["validator_runner"] == (
        "python_subprocess_entrypoint"
    )
    assert report["serializer_runner_linkage"]["problem_defined_serializer_hooks"] == (
        "unsupported"
    )
    assert report["runtime_candidate_shape"]["program_count"] == 1
    assert report["runtime_candidate_shape"]["workspace_program_count"] == 1
    assert report["runtime_candidate_shape"]["python_file_count"] == 1
    assert report["runtime_candidate_shape"]["non_python_text_file_count"] == 1
    assert report["runtime_candidate_shape"]["static_member_count"] == 1
    record = report["runtime_candidate_shape"]["program_records"][0]
    assert record["primary_file"] == "main.py"
    assert record["representational_role"] == "direct_solution_code_workspace"
    assert len(record["workspace_sha256"]) == 64

    options = {item["option"]: item for item in report["abstraction_options"]}
    assert set(options) == {
        "direct_solution",
        "constructor_function",
        "bespoke_search_algorithm",
        "coevolved_solution_and_search",
    }
    assert options["direct_solution"]["selection_status"] == "selected_current_default"
    assert options["constructor_function"]["local_status"] == (
        "not_distinguished_from_python_workspace"
    )
    assert options["coevolved_solution_and_search"]["local_status"] == "unsupported"
    assert report["abstraction_rationale"]["status"] == "not_recorded"
    assert report["bias_assessment"]["symmetry_structure_assumptions_recorded"] is False
    assert report["bias_assessment"]["equal_budget_comparison_ready"] is False
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["selected_abstraction_recorded"] is True
    assert report["claim_readiness"]["alphaevolve_abstraction_selection_fidelity"] is False
    assert "equal_budget_direct_constructor_search_comparisons" in (
        report["claim_readiness"]["remaining_gap"]
    )

    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["claim_readiness"]["alphaevolve_abstraction_selection_fidelity"] = True
    edited["bias_assessment"]["equal_budget_comparison_ready"] = True
    validation = validate_candidate_abstraction_choice_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_overclaim",
        "abstraction_selection_fidelity_overclaim",
        "equal_budget_comparison_ready_overclaim",
    }


def test_runtime_history_reports_candidate_language_runner_contracts():
    tmpdir = tempfile.mkdtemp()

    evolve(_problem(), Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"][
        "candidate_language_runner_contract_report"
    ]

    assert report["schema"] == (
        "libreevolve.candidate_language_runner_contract_report.v1"
    )
    assert report["validation"]["ok"] is True
    assert validate_candidate_language_runner_contract_report(report)["ok"] is True
    assert report["selected_policy"]["manifest_path"] == "policies.candidate_language"
    assert report["selected_policy"]["policy"] == "python_primary_text_workspace_v1"
    assert report["selected_policy"]["primary_language"] == "python"
    assert report["selected_policy"]["language_runner_ready"] is False
    assert report["selected_policy"]["policy_validation"]["ok"] is True

    runners = {item["language"]: item for item in report["configured_language_runners"]}
    assert set(runners) == {"python", "non_python_text", "arbitrary_language"}
    assert runners["python"]["status"] == "supported_current_primary"
    assert runners["python"]["marker_grammar"] == "python_hash_evolve_block_markers"
    assert runners["python"]["runner_contract"] == (
        "python_subprocess_validator_entrypoint"
    )
    assert runners["non_python_text"]["status"] == "workspace_member_only_no_runner"
    assert runners["non_python_text"]["marker_grammar"] == (
        "unsupported_fail_closed_marker_like_declarations"
    )
    assert runners["non_python_text"]["runner_contract"] == "unsupported"
    assert runners["arbitrary_language"]["runner_contract"] == "unsupported"
    assert runners["arbitrary_language"]["build_contract"] == "unsupported"

    build_contracts = report["build_system_runner_contracts"]
    assert build_contracts["status"] == "unsupported"
    assert build_contracts["declared_build_files"] == []
    assert build_contracts["build_runner"] == "unsupported"
    assert build_contracts["package_install_runner"] == "unsupported"
    assert build_contracts["compiled_artifact_capture"] == "unsupported"
    assert report["declared_language_runner_records"] == []
    assert report["declared_build_system_records"] == []

    hooks = report["task_candidate_abstraction_hooks"]
    assert hooks["status"] == "unsupported"
    assert hooks["serializer_hook"] == "unsupported"
    assert hooks["materializer_hook"] == "unsupported"
    assert hooks["runner_hook"] == "unsupported"
    assert hooks["scorer_output_adapter"] == "python_validator_json_metrics_only"

    assert report["claim_ready"] is False
    assert report["claim_readiness"]["python_runner_contract_recorded"] is True
    assert report["claim_readiness"]["metadata_runner_declarations_recorded"] is False
    assert report["claim_readiness"]["non_python_language_runners_configured"] is False
    assert report["claim_readiness"]["language_aware_marker_grammars_configured"] is False
    assert report["claim_readiness"]["build_system_runner_contracts_configured"] is False
    assert report["claim_readiness"]["task_candidate_abstraction_hooks_configured"] is False
    assert report["claim_readiness"]["alphaevolve_language_runner_parity"] is False
    assert report["alphaevolve_contract_gap"]["required_before_parity_claim"] == (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "configured_non_python_language_runners" in (
        report["claim_readiness"]["remaining_gap"]
    )

    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["selected_policy"]["language_runner_ready"] = True
    edited["configured_language_runners"][1]["runner_contract"] = "supported"
    edited["configured_language_runners"][2]["build_contract"] = "supported"
    edited["build_system_runner_contracts"]["build_runner"] = "supported"
    edited["declared_language_runner_records"] = [
        {"language": "rust", "execution_status": "supported"}
    ]
    edited["declared_build_system_records"] = [
        {"name": "cargo", "execution_status": "supported"}
    ]
    edited["task_candidate_abstraction_hooks"]["serializer_hook"] = "supported"
    edited["claim_readiness"]["alphaevolve_language_runner_parity"] = True
    validation = validate_candidate_language_runner_contract_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_overclaim",
        "language_runner_ready_overclaim",
        "non_python_text_runner_overclaim",
        "arbitrary_language_build_overclaim",
        "build_runner_overclaim",
        "declared_language_runner_execution_overclaim",
        "declared_build_system_execution_overclaim",
        "serializer_hook_overclaim",
        "alphaevolve_language_runner_parity_overclaim",
    }


def test_runtime_history_reports_declared_candidate_language_runner_metadata():
    tmpdir = tempfile.mkdtemp()

    evolve(
        _problem(),
        Config(
            max_generations=0,
            log_dir=tmpdir,
            problem_name="t",
            candidate_language_runners=[
                {
                    "language": "rust",
                    "file_patterns": ["src/*.rs"],
                    "marker_grammar": "custom_declared_unsupported",
                    "runner_command": ["cargo", "test"],
                }
            ],
            candidate_build_systems=[
                {
                    "name": "cargo",
                    "build_files": ["Cargo.toml"],
                    "build_command": ["cargo", "build"],
                    "artifact_patterns": ["target/debug/*"],
                }
            ],
        ),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"][
        "candidate_language_runner_contract_report"
    ]

    assert report["validation"]["ok"] is True
    assert validate_candidate_language_runner_contract_report(report)["ok"] is True
    assert report["declared_language_runner_records"][0]["language"] == "rust"
    assert report["declared_language_runner_records"][0]["runner_command"] == [
        "cargo",
        "test",
    ]
    assert report["declared_build_system_records"][0]["name"] == "cargo"
    assert report["build_system_runner_contracts"]["declared_build_files"] == [
        "Cargo.toml"
    ]
    assert report["claim_readiness"]["metadata_runner_declarations_recorded"] is True
    assert report["claim_readiness"]["non_python_language_runners_configured"] is False
    assert report["claim_readiness"]["build_system_runner_contracts_configured"] is False
    assert "execution_for_declared_non_python_language_or_build_runners" in (
        report["claim_readiness"]["remaining_gap"]
    )


def test_runtime_history_reports_initial_program_idea_provenance():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code, workspace):\n"
        "    return {'score': 0.8, 'is_valid': True}\n"
    )
    problem.initial_programs = []
    problem.initial_workspaces = [CandidateWorkspace.from_code("x = 1\n", "main.py")]
    problem.initial_workspace_sources = [
        {
            "seed_index": 0,
            "seed_source_kind": "workspace",
            "primary_file": "main.py",
            "file_count": 1,
            "files": ["main.py"],
            "seed_variant_id": "seed.simple:v1",
            "seed_idea_origin": "researcher_idea",
            "seed_idea_label": "stochastic baseline idea",
            "seed_idea_summary": "Use a researcher-proposed stochastic baseline.",
            "seed_contribution_roles": [
                "human_seed_author",
                "researcher_idea",
            ],
            "seed_prior_technique": "stochastic evaluation",
            "seed_background_refs": ["context/matrix.md"],
        }
    ]

    evolve(
        problem,
        Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
    )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["initial_program_idea_provenance_report"]

    assert report["schema"] == "libreevolve.initial_program_idea_provenance_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_initial_program_idea_provenance_report(report)["ok"] is True
    assert report["seed_source_count"] == 1
    assert report["seed_program_count"] == 1
    assert report["annotated_seed_count"] == 1
    assert report["unknown_origin_count"] == 0
    assert report["origin_counts"] == {"researcher_idea": 1}
    assert report["metadata_contract"]["manifest_path"] == "problem.seed_sources"
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["idea_origin_metadata_present"] is True
    assert report["claim_readiness"]["evaluator_metric_linkage"] is True
    assert report["claim_readiness"]["equal_budget_seed_variant_results"] is False
    assert report["claim_readiness"]["alphaevolve_human_seeded_benchmark_parity"] is False
    assert "equal_budget_simple_random_researcher_seed_comparison" in (
        report["claim_readiness"]["remaining_gap"]
    )

    record = report["records"][0]
    assert record["seed_variant_id"] == "seed.simple:v1"
    assert record["seed_idea_origin"] == "researcher_idea"
    assert record["seed_contribution_roles"] == [
        "human_seed_author",
        "researcher_idea",
    ]
    assert record["seed_background_refs"] == ["context/matrix.md"]
    assert record["runtime"]["history_linked"] is True
    assert record["runtime"]["metric_names"] == ["score"]
    assert len(record["runtime"]["workspace_sha256"]) == 64
    assert record["equal_budget_variant_evidence"] == "not_recorded"

    history = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    assert history[0]["metadata"]["seed_idea_origin"] == "researcher_idea"
    assert history[0]["metadata"]["seed_variant_id"] == "seed.simple:v1"

    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["claim_readiness"]["alphaevolve_human_seeded_benchmark_parity"] = True
    edited["records"][0]["equal_budget_variant_evidence"] = "claimed"
    validation = validate_initial_program_idea_provenance_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_overclaim",
        "human_seeded_parity_overclaim",
        "equal_budget_variant_overclaim",
    }


def test_runtime_history_reports_evaluator_workload_provenance():
    tmpdir = tempfile.mkdtemp()
    digest = "b" * 64
    problem = _problem(
        "import json\n"
        "from pathlib import Path\n"
        "def evaluate(code, workspace, stage):\n"
        "    workload = stage['workload']\n"
        "    ok = workload['type'] == 'inner_search'\n"
        "    Path('search_trace.json').write_text(json.dumps({'ok': ok}))\n"
        "    return {'score': 1.0 if ok else 0.0, 'is_valid': ok}\n"
    )

    evolve(
        problem,
        Config(
            max_generations=0,
            log_dir=tmpdir,
            problem_name="t",
            eval_stages=[
                {
                    "name": "search_stage",
                    "artifact_include": ["search_trace.json"],
                    "workload": {
                        "type": "inner_search",
                        "datasets": [
                            {
                                "id": "packing_train",
                                "split": "train",
                                "sha256": digest,
                                "rows": 8,
                            }
                        ],
                        "budget": {"max_trials": 25, "max_seconds": 2.0},
                        "checkpoint_policy": "retained_artifacts",
                        "score_fields": ["score"],
                        "artifact_policy": "candidate_construct_json",
                    },
                }
            ],
        ),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["config"]["eval_stages"][0]["workload"]["type"] == "inner_search"
    report = manifest["runtime"]["history"]["evaluator_workload_report"]

    assert report["schema"] == "libreevolve.evaluator_workload_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_evaluator_workload_report(report)["ok"] is True
    assert report["configured_candidate_count"] == 1
    assert report["stage_count"] == 1
    assert report["declared_workload_stage_count"] == 1
    assert report["workload_type_counts"] == {"inner_search": 1}
    assert report["workload_protocol_policy"]["paper_claim_ready"] is False
    assert report["protocol_readiness"] == {
        "declared_protocol_stage_count": 1,
        "dataset_digest_complete_stage_count": 1,
        "score_field_linked_stage_count": 1,
        "artifact_evidence_stage_count": 1,
        "managed_runner_stage_count": 0,
        "claim_ready": False,
    }
    assert report["claim_ready"] is False

    stage = report["stages"][0]
    assert stage["name"] == "search_stage"
    assert stage["workload_type"] == "inner_search"
    assert stage["declared"] is True
    assert stage["candidate_count"] == 1
    assert stage["passed"] == 1
    assert stage["datasets"][0]["sha256"] == digest
    assert stage["budget"]["max_trials"] == 25
    assert stage["checkpoint_policy"] == "retained_artifacts"
    assert stage["score_fields"] == ["score"]
    assert stage["dataset_digest_evidence"] == {
        "required_for_protocol_claim": True,
        "dataset_count": 1,
        "sha256_count": 1,
        "missing_sha256_dataset_ids": [],
        "missing_sha256_dataset_ids_truncated": False,
        "complete": True,
    }
    assert stage["score_field_linkage"]["complete"] is True
    assert stage["score_field_linkage"]["declared_score_fields"] == ["score"]
    assert stage["score_field_linkage"]["observed_metric_names"] == [
        "is_valid",
        "score",
    ]
    assert stage["artifact_evidence"]["file_count"] == 1
    assert stage["artifact_evidence"]["sha256_count"] == 1
    assert stage["artifact_evidence"]["sample_paths"] == ["search_trace.json"]
    assert stage["artifact_evidence"]["completeness_status"] == "observed"
    assert stage["protocol_execution"] == {
        "managed_runner": False,
        "execution_owner": "problem_local_validator",
        "validator_workload_context": True,
        "claim_ready": False,
    }

    overclaimed = copy.deepcopy(report)
    overclaimed["workload_protocol_policy"]["paper_claim_ready"] = True
    overclaimed["protocol_readiness"]["claim_ready"] = True
    validation = validate_evaluator_workload_report(overclaimed)
    assert validation["ok"] is False
    assert any(
        issue["code"] == "workload_protocol_overclaim"
        for issue in validation["issues"]
    )


def test_runtime_history_reports_embedded_evaluator_entrypoint():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code):\n"
        "    return {'score': 0.0, 'is_valid': False}\n"
    )
    problem.initial_programs = [
        "def transform(value):\n"
        "    # EVOLVE-BLOCK-START scoring_rule\n"
        "    return value\n"
        "    # EVOLVE-BLOCK-END\n\n"
        "def evaluate(eval_inputs):\n"
        "    return {'score': transform(eval_inputs['score']), 'is_valid': True}\n"
    ]

    evolve(
        problem,
        Config(
            max_generations=0,
            log_dir=tmpdir,
            problem_name="t",
            eval_stages=[
                {
                    "name": "candidate_eval",
                    "mode": "embedded_evaluate",
                    "eval_inputs": {"score": 0.7},
                }
            ],
        ),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["embedded_evaluator_entrypoint_report"]

    assert report["schema"] == "libreevolve.embedded_evaluator_entrypoint_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_embedded_evaluator_entrypoint_report(report)["ok"] is True
    assert report["embedded_candidate_count"] == 1
    assert report["external_validator_candidate_count"] == 0
    assert report["embedded_entrypoint_count"] == 1
    assert report["entrypoint_contract"]["signature"] == "evaluate(eval_inputs)"
    assert report["entrypoint_contract"]["dependency_policy"] == (
        "candidate_primary_module_embedded_evaluate_v1"
    )
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["candidate_owned_evaluate_entrypoint"] is True
    assert report["claim_readiness"]["embedded_only_problem_definition"] is True
    assert report["claim_readiness"]["evolved_block_to_score_path_mapping"] is True
    assert report["claim_readiness"][
        "skeleton_to_evolved_block_invocation_trace"
    ] is True
    assert report["claim_readiness"][
        "score_field_to_evolved_code_path_causal_attribution"
    ] is True
    assert "skeleton_to_evolved_block_invocation_trace" not in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "load_problem_without_external_validate_py" not in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "score_field_to_evolved_code_path_causal_attribution" not in (
        report["claim_readiness"]["remaining_gap"]
    )

    record = report["records"][0]
    assert record["stage_name"] == "candidate_eval"
    assert record["evaluator_mode"] == "embedded_evaluate"
    assert record["entrypoint"] == "main.py"
    assert record["callable"] == "evaluate"
    assert record["signature"] == "evaluate(eval_inputs)"
    assert record["eval_inputs"]["retained"] is False
    assert len(record["eval_inputs"]["sha256"]) == 64
    assert record["dependency_policy"]["allowed_scope"] == (
        "materialized_candidate_workspace"
    )
    assert record["raw_eval_inputs_retained"] is False
    assert record["metric_names"] == ["score"]
    assert len(record["invocation_traces"]) == 1
    invocation_trace = record["invocation_traces"][0]
    assert invocation_trace["schema"] == (
        "libreevolve.embedded_evaluator_invocation_trace.v1"
    )
    assert invocation_trace["method"] == (
        "static_ast_evaluate_call_graph_to_evolved_blocks"
    )
    assert invocation_trace["trace_policy"] == (
        "candidate_primary_file_direct_name_calls_only"
    )
    assert invocation_trace["called_function_count"] == 1
    assert invocation_trace["called_functions"][0]["name"] == "transform"
    assert invocation_trace["called_functions"][0]["depth"] == 1
    assert invocation_trace["called_functions"][0][
        "evolved_block_dependency_count"
    ] == 1
    assert invocation_trace["evolved_block_dependency_count"] == 1
    assert len(record["score_field_links"]) == 1
    score_link = record["score_field_links"][0]
    assert score_link["metric_name"] == "score"
    assert score_link["link_policy"] == (
        "static_ast_evaluate_return_dependency_to_evolved_block"
    )
    assert score_link["candidate_primary_file"] == "main.py"
    assert len(score_link["candidate_primary_file_sha256"]) == 64
    assert score_link["causal_attribution_claimed"] is True
    assert score_link["evolved_block_candidate_count"] == 1
    block_link = score_link["evolved_block_candidates"][0]
    assert block_link["path"] == "main.py"
    assert block_link["name"] == "scoring_rule"
    assert len(block_link["span_id"]) == 24
    assert len(block_link["content_sha256"]) == 64
    assert invocation_trace["evolved_block_dependencies"][0]["span_id"] == (
        block_link["span_id"]
    )
    attribution = score_link["causal_attribution"]
    assert attribution["schema"] == "libreevolve.score_field_causal_attribution.v1"
    assert attribution["method"] == "static_ast_evaluate_return_metric_dependency_trace"
    assert attribution["dependency_policy"] == "local_ast_function_calls_to_evolve_blocks_only"
    assert attribution["dependency_functions"] == ["transform"]
    assert attribution["evolved_block_dependency_count"] == 1
    assert attribution["evolved_block_dependencies"][0]["span_id"] == block_link["span_id"]
    assert len(attribution["metric_return"]["expression_sha256"]) == 64

    edited = copy.deepcopy(report)
    edited["records"][0]["score_field_links"][0]["causal_attribution"][
        "dependency_policy"
    ] = "overclaim"
    validation = validate_embedded_evaluator_entrypoint_report(edited)
    assert validation["ok"] is False
    assert "invalid_score_field_causal_dependency_policy" in {
        issue["code"] for issue in validation["issues"]
    }

    edited = copy.deepcopy(report)
    edited["records"][0]["invocation_traces"][0]["method"] = "dynamic_probe"
    validation = validate_embedded_evaluator_entrypoint_report(edited)
    assert validation["ok"] is False
    assert "invalid_invocation_trace_method" in {
        issue["code"] for issue in validation["issues"]
    }


def test_runtime_history_reports_execution_filtered_proposal_lifecycle():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code):\n"
        "    ok = 'x=2' not in code\n"
        "    return {'score': 1.0 if ok else 0.0, 'is_valid': ok}\n"
    )
    llm = _TelemetryLLM("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE")

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
        )

    run_dir = Path(tmpdir) / "t"
    records = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    failures = [
        json.loads(line)
        for line in (run_dir / "failure_history.jsonl").read_text().splitlines()
    ]
    assert len(records) == 2
    assert len(failures) == 1
    assert failures[0]["admission_reason"] == "invalid_evaluation"
    assert failures[0]["llm"]["backend_idx"] == 0
    assert failures[0]["llm"]["calls"][0]["backend_name"] == "fake/model"

    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["proposal_lifecycle_report"]
    assert report["schema"] == "libreevolve.proposal_lifecycle_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_proposal_lifecycle_report(report)["ok"] is True
    assert report["generated_candidate_count"] == 1
    assert report["accepted_generated_count"] == 0
    assert report["rejected_generated_count"] == 1
    assert report["execution_filtered_count"] == 1
    assert report["invalid_evaluation_count"] == 1
    assert report["archive_rejected_count"] == 1
    assert report["accepted_invalid_count"] == 0
    assert report["feedback_reuse"]["generated_failure_record_count"] == 1
    assert report["feedback_reuse"]["failure_memory_context_count"] == 1
    assert report["claim_ready"] is False
    assert "audited_false_acceptance_and_false_rejection_rates" in (
        report["claim_readiness"]["remaining_gap"]
    )

    lifecycle = report["records"][0]
    assert lifecycle["lifecycle_status"] == "rejected_history"
    assert lifecycle["evaluator_is_valid"] is False
    assert lifecycle["execution_filtered"] is True
    assert lifecycle["rejection_reason"] == "invalid_evaluation"
    assert lifecycle["failure_record_linked"] is True
    assert lifecycle["admission"]["admitted"] is False
    assert lifecycle["admission"]["reason"] == "invalid_evaluation"
    assert lifecycle["llm"]["calls"][0]["backend_name"] == "fake/model"
    assert lifecycle["mutation"]["sha256"] == failures[0]["mutation_sha256"]

    audit = manifest["runtime"]["history"]["incorrect_suggestion_audit_report"]
    assert audit["schema"] == "libreevolve.incorrect_suggestion_audit_report.v1"
    assert audit["validation"]["ok"] is True
    assert validate_incorrect_suggestion_audit_report(audit)["ok"] is True
    assert audit["generated_candidate_count"] == 1
    assert audit["accepted_generated_count"] == 0
    assert audit["rejected_generated_count"] == 1
    assert audit["execution_filtered_count"] == 1
    assert audit["invalid_evaluation_count"] == 1
    assert audit["accepted_invalid_count"] == 0
    assert audit["local_filter_rate"] == 1.0
    assert audit["accepted_invalid_rate"] is None
    assert audit["audit_scope"]["local_execution_grounding"] is True
    assert audit["audit_scope"]["independent_rejudge"] is False
    assert audit["audit_scope"]["reference_or_statistical_oracle"] is False
    assert audit["claim_ready"] is False
    assert audit["claim_readiness"]["local_execution_grounding_counts"] is True
    assert audit["claim_readiness"]["independent_rejudge_of_rejected_candidates"] is False
    assert audit["claim_readiness"]["audited_false_acceptance_rate"] is False
    assert audit["claim_readiness"]["audited_false_rejection_rate"] is False
    assert audit["claim_readiness"][
        "publication_strength_incorrect_suggestion_filtering"
    ] is False
    audit_record = audit["audit_records"][0]
    assert audit_record["proposal_id"] == lifecycle["proposal_id"]
    assert audit_record["execution_filtered"] is True
    assert audit_record["independent_rejudge_status"] == "not_run"
    assert audit_record["false_acceptance_audited"] is False
    assert audit_record["false_rejection_audited"] is False

    overclaimed = copy.deepcopy(audit)
    overclaimed["claim_ready"] = True
    overclaimed["audit_scope"]["independent_rejudge"] = True
    overclaimed["claim_readiness"]["audited_false_rejection_rate"] = True
    overclaimed["audit_records"][0]["independent_rejudge_status"] = "passed"
    validation = validate_incorrect_suggestion_audit_report(overclaimed)
    assert validation["ok"] is False
    assert {
        "claim_ready_overclaim",
        "independent_rejudge_overclaim",
        "audited_false_rejection_rate_overclaim",
        "independent_rejudge_status_overclaim",
    }.issubset({issue["code"] for issue in validation["issues"]})

    sample_efficiency = manifest["runtime"]["history"]["sample_efficiency_report"]
    assert sample_efficiency["schema"] == "libreevolve.sample_efficiency_report.v1"
    assert sample_efficiency["validation"]["ok"] is True
    assert validate_sample_efficiency_report(sample_efficiency)["ok"] is True
    assert sample_efficiency["generated_proposal_count"] == 1
    assert sample_efficiency["evaluated_candidate_count"] == 1
    assert sample_efficiency["valid_candidate_count"] == 0
    assert sample_efficiency["archive_admitted_candidate_count"] == 0
    assert sample_efficiency["retained_elite_count"] == 0
    assert sample_efficiency["logical_llm_sample_count"] == 1
    assert sample_efficiency["target_policy"]["status"] == "not_configured"
    assert sample_efficiency["claim_ready"] is False
    assert "cross_run_sample_budget_curves" in (
        sample_efficiency["claim_readiness"]["remaining_gap"]
    )
    assert sample_efficiency["cumulative_curve"] == [
        {
            "sample_index": 1,
            "proposal_id": lifecycle["proposal_id"],
            "logical_llm_sample_count": 1,
            "evaluated_candidate_count": 1,
            "valid_candidate_count": 0,
            "archive_admitted_candidate_count": 0,
            "retained_elite_count": 0,
            "search_state_changed_count": 0,
            "sampling_eligible_count": 0,
            "best_score_so_far": -0.1,
            "target_hit_count": 0,
        }
    ]

    repeated_sampling = manifest["runtime"]["history"][
        "repeated_sampling_baseline_report"
    ]
    assert repeated_sampling["schema"] == (
        "libreevolve.repeated_sampling_baseline_report.v1"
    )
    assert repeated_sampling["validation"]["ok"] is True
    assert validate_repeated_sampling_baseline_report(repeated_sampling)["ok"] is True
    assert repeated_sampling["status"] == "not_configured"
    assert repeated_sampling["paper_variant"] == "No evolution"
    assert repeated_sampling["observed_sample_counts"] == {
        "generated_proposal_count": 1,
        "accepted_generated_count": 0,
        "rejected_generated_count": 1,
        "execution_filtered_count": 1,
    }
    assert repeated_sampling["budget_parity"]["status"] == "not_checked"
    assert repeated_sampling["claim_ready"] is False
    assert repeated_sampling["claim_readiness"][
        "controlled_repeated_sampling_run"
    ] is False
    assert "disabled_parent_selection" in (
        repeated_sampling["required_comparator_controls"]
    )


def test_runtime_history_reports_duplicate_work_policy_with_run_local_cache():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code):\n"
        "    ok = 'x=1' in code\n"
        "    return {'score': 1.0 if ok else -0.1, 'is_valid': ok}\n"
    )
    llm = _TelemetryLLM("x=2")

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(
                max_generations=1,
                proposals_per_generation=2,
                mutation_mode="full",
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    run_dir = Path(tmpdir) / "t"
    history = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    events = [
        json.loads(line)
        for line in (run_dir / "controller_budget_events.jsonl").read_text().splitlines()
    ]
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["duplicate_work_policy_report"]

    assert report["schema"] == "libreevolve.duplicate_work_policy_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_duplicate_work_policy_report(report)["ok"] is True
    assert report["program_count"] == 3
    assert report["generated_candidate_count"] == 2
    assert report["unique_workspace_count"] == 2
    assert report["duplicate_workspace_group_count"] == 1
    assert report["duplicate_generated_candidate_count"] == 1
    assert report["evaluation_cache_store_count"] == 2
    assert report["evaluation_cache_hit_count"] == 1
    assert report["evaluation_cache_policy"]["pre_evaluation_duplicate_skip"] is True
    assert report["evaluation_cache_policy"]["evaluation_result_reuse"] is True
    assert report["evaluation_cache_policy"]["cache_storage"] == "run_local_memory"
    assert report["claim_ready"] is False

    group = report["duplicate_workspace_groups"][0]
    assert group["program_count"] == 2
    assert group["generated_program_count"] == 2
    assert group["generated_duplicate_program_ids"] == (
        report["duplicate_generated_program_ids"]
    )
    assert group["evaluated_again"] is False
    assert group["cache_hit_program_ids"] == report["evaluation_cache_hit_program_ids"]
    assert {record["candidate_type"] for record in group["records"]} == {"generated"}

    generated = [record for record in history if record["metadata"]["candidate_type"] == "generated"]
    assert generated[0]["metadata"]["evaluation_cache"]["status"] == "stored"
    assert generated[1]["metadata"]["evaluation_cache"]["status"] == "hit"
    assert generated[1]["evaluation"]["metadata"]["evaluation_cache"]["cache_hit"] is True
    assert manifest["runtime"]["consumed"]["candidate_evaluations"] == 1
    assert [event["kind"] for event in events].count("candidate_evaluation") == 1
    assert [event["kind"] for event in events].count(
        "candidate_evaluation_cache_hit"
    ) == 1


def test_runtime_history_reports_sampling_balance_counts():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c):\n"
        "    if 'x=2' in c:\n"
        "        return {'score': 0.8, 'latency': 0.2, 'is_valid': True}\n"
        "    return {'score': 0.9, 'latency': 0.1, 'is_valid': True}\n"
    )
    problem = Problem(
        name="t",
        task_description="t",
        metrics=[
            {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
            {"name": "latency", "bounds": [0.0, 1.0]},
        ],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["x=1", "x=2"],
        problem_dir=d,
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                parent_selection_strategy="mixed",
                explore_ratio=1.0,
                inspiration_strategy="metric",
                num_inspirations=1,
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["sampling_balance_report"]

    assert report["schema"] == "libreevolve.sampling_balance_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_sampling_balance_report(report)["ok"] is True
    assert report["configured_parent_selection_strategy"] == "mixed"
    assert report["configured_explore_ratio"] == 1.0
    assert report["configured_inspiration_strategy"] == "metric"
    assert report["generated_candidate_count"] == 1
    assert report["parent_strategy_counts"] == {"explore": 1}
    assert report["mixed_parent_decision_count"] == 1
    assert report["mixed_parent_explore_count"] == 1
    assert report["mixed_parent_exploit_count"] == 0
    assert report["inspiration_strategy_counts"] == {"metric": 1}
    assert report["inspiration_strategy_source_counts"] == {"config": 1}
    assert report["inspiration_requested_total"] == 1
    assert report["inspiration_selected_total"] == 1
    assert set(report["metric_target_counts"]) == {"score", "latency"}
    assert report["generation_records"][0]["candidate_count"] == 1
    sample = report["sample_records"][0]
    assert sample["parent_strategy"] == "explore"
    assert sample["inspiration_strategy"] == "metric"
    assert sample["inspiration_selected_count"] == 1
    assert report["claim_ready"] is False


def test_runtime_history_reports_abandoned_hypothesis_branch_evidence():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code):\n"
        "    ok = 'x=1' in code\n"
        "    return {'score': 1.0 if ok else 0.0, 'is_valid': ok}\n"
    )
    llm = MagicMock()
    llm.generate.side_effect = [
        (
            "IDEA: Try the risky branch.\n"
            "RATIONALE: It may improve the candidate.\n"
            "HYPOTHESIS: Risky branch remains valid.\n"
            "<<<<<<< SEARCH\nx=1\n=======\nx=2\n>>>>>>> REPLACE",
            0,
        ),
        (
            "IDEA: Try the risky branch.\n"
            "RATIONALE: It may improve the candidate.\n"
            "HYPOTHESIS: Risky branch remains valid.\n"
            "<<<<<<< SEARCH\nx=1\n=======\nx=3\n>>>>>>> REPLACE",
            0,
        ),
    ]

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(
                max_generations=2,
                log_dir=tmpdir,
                problem_name="t",
                capture_proposal_metadata=True,
            ),
        )

    run_dir = Path(tmpdir) / "t"
    failures = [
        json.loads(line)
        for line in (run_dir / "failure_history.jsonl").read_text().splitlines()
    ]
    assert len(failures) == 2
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["hypothesis_branch_report"]

    assert report["schema"] == "libreevolve.hypothesis_branch_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_hypothesis_branch_report(report)["ok"] is True
    assert report["branch_count"] == 1
    assert report["abandoned_branch_count"] == 1
    assert report["active_or_validated_branch_count"] == 0
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["branch_level_abandonment_evidence"] is True
    assert report["claim_readiness"]["controller_backtracking_decision"] is False
    assert report["backtracking_policy"]["controller_suppression"] == "not_configured"
    assert report["failure_memory_linkage"]["failure_record_count"] == 2
    assert report["failure_memory_linkage"]["failure_memory_context_count"] == 2

    branch = report["branches"][0]
    assert branch["branch_status"] == "abandoned_evidence"
    assert branch["abandonment_reason"] == (
        "all_observed_candidates_rejected_or_execution_filtered"
    )
    assert branch["candidate_count"] == 2
    assert branch["accepted_count"] == 0
    assert branch["rejected_count"] == 2
    assert branch["execution_filtered_count"] == 2
    assert branch["rejection_reasons"] == {"invalid_evaluation": 2}
    assert branch["proposal_fields"]["hypothesis"]["preview"] == (
        "Risky branch remains valid."
    )
    assert branch["fallback_target"]["type"] == "parent_program"
    assert len(branch["fallback_target"]["candidate_ids"]) == 1
    assert branch["suppression_policy"] == "not_configured"
    assert branch["resumed_search_outcome"]["status"] == "not_causally_tracked"


def test_runtime_history_reports_observed_controller_redirect_boundary():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code):\n"
        "    if 'x=4' in code:\n"
        "        return {'score': 2.0, 'is_valid': True}\n"
        "    if 'x=1' in code:\n"
        "        return {'score': 1.0, 'is_valid': True}\n"
        "    return {'score': 0.0, 'is_valid': False}\n"
    )
    llm = MagicMock()
    llm.generate.side_effect = [
        (
            "IDEA: Try the risky branch.\n"
            "RATIONALE: It may improve the candidate.\n"
            "HYPOTHESIS: Risky branch remains valid.\n"
            "<<<<<<< SEARCH\nx=1\n=======\nx=2\n>>>>>>> REPLACE",
            0,
        ),
        (
            "IDEA: Return to a safer parent.\n"
            "RATIONALE: Use the last valid parent for a different edit.\n"
            "HYPOTHESIS: Fallback parent can produce a valid improvement.\n"
            "<<<<<<< SEARCH\nx=1\n=======\nx=4\n>>>>>>> REPLACE",
            0,
        ),
    ]

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(
                max_generations=2,
                log_dir=tmpdir,
                problem_name="t",
                capture_proposal_metadata=True,
            ),
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["controller_backtracking_report"]

    assert report["schema"] == "libreevolve.controller_backtracking_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_controller_backtracking_report(report)["ok"] is True
    assert report["generated_candidate_count"] == 2
    assert report["visible_branch_count"] == 2
    assert report["visible_abandoned_branch_count"] == 1
    assert report["redirect_event_count"] == 1
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["branch_state_transitions"] is True
    assert report["claim_readiness"]["observed_redirect_events"] is True
    assert (
        report["claim_readiness"]["explicit_controller_backtracking_decision"]
        is False
    )
    assert report["policies"]["controller_suppression"] == "not_configured"

    event = report["redirect_events"][0]
    assert event["redirect_kind"] == "fallback_parent_sampled_for_alternative_branch"
    assert event["causal_proof"] is False
    assert event["source_branch_id"] != event["selected_branch_id"]
    transitions = report["branch_state_transitions"]
    assert any(
        transition["event_type"] == "abandoned_evidence"
        for transition in transitions
    )
    assert any(
        transition["event_type"] == "candidate_accepted"
        for transition in transitions
    )


def test_evolve_records_best_artifact_export_failure_without_failing_search():
    tmpdir = tempfile.mkdtemp()
    secret = "api_key=sk-proj_core_export_secret_1234567890"  # pragma: allowlist secret

    with patch(
        "libreevolve.core.best_artifacts._write_best_artifacts",
        side_effect=OSError(f"export failed {secret}"),
    ):
        best = evolve(
            _problem(),
            Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
        )

    assert best is not None
    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    runtime = manifest["runtime"]
    export = runtime["best_artifact_export"]
    rendered = json.dumps(export, sort_keys=True)
    assert runtime["status"] == "completed"
    assert export["status"] == "failed"
    assert export["error_type"] == "OSError"
    assert secret not in rendered
    assert export["paths"]["best.py"]["exists"] is False
    assert runtime["artifacts"]["best.py"]["exists"] is False


def test_detailed_evaluator_attempt_budget_stops_before_llm_mutation():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    ok = stage['attempt'] == 1\n"
        "    return {'score': 1.0 if ok else 0.0, 'is_valid': ok}\n"
    )
    llm = _llm()

    with patch("libreevolve.core.loop.build_llm", return_value=llm) as build:
        evolve(
            problem,
            Config(
                max_generations=5,
                max_evaluator_subprocess_attempts=4,
                log_dir=tmpdir,
                problem_name="t",
                eval_stages=[{"name": "accounted", "samples": 2, "retries": 1}],
            ),
        )

    build.assert_called_once()
    llm.generate.assert_not_called()
    run_dir = Path(tmpdir) / "t"
    records = [json.loads(line) for line in (run_dir / "history.jsonl").read_text().splitlines()]
    assert len(records) == 1
    assert records[0]["metadata"]["budget"]["consumed"]["evaluator_subprocess_attempts"] == 4
    assert records[0]["metadata"]["budget"]["stop_reason"] == "max_evaluator_subprocess_attempts"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["config"]["max_evaluator_subprocess_attempts"] == 4
    runtime = manifest["runtime"]
    assert runtime["stop_reason"] == "max_evaluator_subprocess_attempts"
    assert runtime["consumed"]["evaluator_subprocess_attempts"] == 4
    assert runtime["consumed"]["generations_started"] == 0


def test_terminal_generated_candidate_records_budget_stop_reason():
    tmpdir = tempfile.mkdtemp()

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(
                max_generations=5,
                max_evaluations=2,
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    run_dir = Path(tmpdir) / "t"
    records = [json.loads(line) for line in (run_dir / "history.jsonl").read_text().splitlines()]
    assert len(records) == 2
    seed, child = records
    assert seed["metadata"]["budget"]["stop_reason"] is None
    assert child["metadata"]["candidate_type"] == "generated"
    assert child["metadata"]["budget"]["consumed"]["evaluations"] == 2
    assert child["metadata"]["budget"]["stop_reason"] == "max_evaluations"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["runtime"]["stop_reason"] == "max_evaluations"
    assert manifest["runtime"]["consumed"]["evaluations"] == 2


def test_zero_evaluation_budget_manifest_declares_no_candidate_history():
    tmpdir = tempfile.mkdtemp()
    llm = _llm()

    with patch("libreevolve.core.loop.build_llm", return_value=llm) as build:
        best = evolve(
            _problem(),
            Config(
                max_generations=3,
                max_evaluations=0,
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    assert best is None
    build.assert_not_called()
    llm.generate.assert_not_called()
    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    assert runtime["status"] == "completed"
    assert runtime["stop_reason"] == "max_evaluations"
    assert runtime["consumed"]["evaluations"] == 0
    assert runtime["consumed"]["seed_evaluations"] == 0
    assert runtime["consumed"]["candidate_evaluations"] == 0
    assert runtime["history"]["programs_logged"] == 0
    assert runtime["history"]["history_partially_written"] is False
    assert runtime["history"]["no_candidates_evaluated"] is True
    assert (
        runtime["history"]["candidate_absence_reason"]
        == "max_evaluations_before_seed_evaluation"
    )
    assert (
        runtime["history"]["history_absent_reason"]
        == "max_evaluations_before_seed_evaluation"
    )
    assert runtime["artifacts"]["history.jsonl"]["exists"] is False


def test_direct_evolve_preflights_llm_before_overwrite_cleanup(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    run_dir = Path(tmpdir) / "t"
    run_dir.mkdir(parents=True)
    old_history = "old history\n"
    (run_dir / "history.jsonl").write_text(old_history, encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="LLM backend preflight failed"):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                run_collision_policy="overwrite",
                backends=[{"type": "openai", "model": "gpt-4o-mini"}],
            ),
        )

    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == old_history
    assert not (run_dir / "manifest.json").exists()


@pytest.mark.parametrize("budget_field", ["max_evaluator_seconds", "max_runtime_seconds"])
def test_zero_second_budget_limits_are_rejected_before_run_artifacts(tmp_path, budget_field):
    kwargs = {budget_field: 0.0}

    with pytest.raises(Exception, match=f"{budget_field} must be > 0"):
        Config(
            max_generations=3,
            log_dir=str(tmp_path),
            problem_name="t",
            **kwargs,
        )

    assert not (tmp_path / "t" / "manifest.json").exists()


def test_llm_call_timeout_is_clamped_to_remaining_runtime_budget():
    backend = MagicMock()
    backend.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    llm = LLMEnsemble([backend], call_timeout_sec=None)
    budget = RunBudget(
        max_generations=1,
        max_evaluations=None,
        max_evaluator_seconds=None,
        max_runtime_seconds=10.0,
        started_at=time.monotonic() - 9.0,
        started_at_utc="2000-01-01T00:00:00.000Z",
    )

    response, idx = _generate_with_budget(llm, budget, "prompt", role="mutation")

    assert (response, idx) == ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0)
    assert llm.call_timeout_sec is None
    assert 0.0 < llm.last_call["call_timeout_sec"] <= 1.0
    assert budget.llm_calls == 1


def test_llm_call_budget_counts_retry_fallback_attempts():
    bad = MagicMock()
    bad.name = "bad/model"
    bad.api_mode = None
    bad.generate.side_effect = RuntimeError("provider down")
    good = MagicMock()
    good.name = "good/model"
    good.api_mode = None
    good.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    llm = LLMEnsemble([bad, good], fallback=True)
    budget = RunBudget(
        max_generations=1,
        max_evaluations=None,
        max_evaluator_seconds=None,
        max_runtime_seconds=None,
        started_at=time.monotonic(),
        started_at_utc="2000-01-01T00:00:00.000Z",
        max_llm_calls=2,
    )

    response, idx = _generate_with_budget(llm, budget, "prompt", role="mutation")

    assert (response, idx) == ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 1)
    assert budget.llm_calls == 2
    assert [record["status"] for record in llm.call_history] == ["error", "ok"]
    assert [record["fallback_attempt"] for record in llm.call_history] == [0, 1]


def test_llm_call_budget_clamps_ensemble_fallback_attempts():
    bad = MagicMock()
    bad.name = "bad/model"
    bad.api_mode = None
    bad.generate.side_effect = RuntimeError("provider down")
    good = MagicMock()
    good.name = "good/model"
    good.api_mode = None
    good.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    llm = LLMEnsemble([bad, good], fallback=True, max_call_attempts=32)
    budget = RunBudget(
        max_generations=1,
        max_evaluations=None,
        max_evaluator_seconds=None,
        max_runtime_seconds=None,
        started_at=time.monotonic(),
        started_at_utc="2000-01-01T00:00:00.000Z",
        max_llm_calls=1,
    )

    with pytest.raises(RuntimeError, match="provider down"):
        _generate_with_budget(llm, budget, "prompt", role="mutation")

    assert budget.llm_calls == 1
    assert llm.max_call_attempts == 32
    good.generate.assert_not_called()
    [record] = llm.call_history
    assert record["status"] == "error"
    assert record["max_call_attempts"] == 1
    assert record["will_fallback"] is False


def test_llm_provider_attempt_budget_stops_before_next_llm_call():
    class RetryingBackend:
        name = "retrying/model"
        api_mode = None
        provider_response_metadata = {
            "adapter_retry": {
                "policy": "bounded_provider_internal_retries",
                "max_retries": 2,
                "attempts": 3,
                "failed_attempts": 2,
                "failures": [
                    {"attempt": 0, "error_type": "TimeoutError"},
                    {"attempt": 1, "error_type": "RateLimitError"},
                ],
            },
        }

        def __init__(self):
            self.calls = 0

        def generate(self, prompt, **kwargs):
            self.calls += 1
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    backend = RetryingBackend()
    llm = LLMEnsemble([backend])
    budget = RunBudget(
        max_generations=2,
        max_evaluations=None,
        max_evaluator_seconds=None,
        max_runtime_seconds=None,
        started_at=time.monotonic(),
        started_at_utc="2000-01-01T00:00:00.000Z",
        max_llm_provider_attempts=3,
    )

    response, idx = _generate_with_budget(llm, budget, "prompt", role="mutation")

    assert (response, idx) == ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0)
    assert backend.calls == 1
    assert budget.llm_calls == 1
    assert budget.llm_provider_attempts == 3
    with pytest.raises(RuntimeError, match="max_llm_provider_attempts"):
        _generate_with_budget(llm, budget, "prompt", role="mutation")
    assert backend.calls == 1


def test_llm_token_budget_stops_before_next_llm_call():
    class UsageBackend:
        name = "usage/model"
        api_mode = None
        provider_response_metadata = {
            "usage": {
                "input_tokens": 400,
                "output_tokens": 1600,
                "total_tokens": 2000,
            },
        }

        def __init__(self):
            self.calls = 0

        def generate(self, prompt, **kwargs):
            self.calls += 1
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    backend = UsageBackend()
    llm = LLMEnsemble([backend])
    budget = RunBudget(
        max_generations=2,
        max_evaluations=None,
        max_evaluator_seconds=None,
        max_runtime_seconds=None,
        started_at=time.monotonic(),
        started_at_utc="2000-01-01T00:00:00.000Z",
        max_llm_tokens=2000,
    )

    _generate_with_budget(llm, budget, "prompt", role="mutation")

    assert backend.calls == 1
    assert budget.llm_calls == 1
    assert budget.llm_tokens == 2000
    with pytest.raises(RuntimeError, match="max_llm_tokens"):
        _generate_with_budget(llm, budget, "prompt", role="mutation")
    assert backend.calls == 1


def test_llm_cost_budget_stops_before_next_llm_call():
    class UsageBackend:
        name = "usage/model"
        api_mode = None
        provider_response_metadata = {
            "usage": {
                "input_tokens": 400,
                "output_tokens": 1600,
                "total_tokens": 2000,
            },
        }

        def __init__(self):
            self.calls = 0

        def generate(self, prompt, **kwargs):
            self.calls += 1
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    backend = UsageBackend()
    llm = LLMEnsemble(
        [backend],
        backend_metadata=[{"cost_usd_per_million_tokens": 5.0}],
    )
    budget = RunBudget(
        max_generations=2,
        max_evaluations=None,
        max_evaluator_seconds=None,
        max_runtime_seconds=None,
        started_at=time.monotonic(),
        started_at_utc="2000-01-01T00:00:00.000Z",
        max_llm_cost_microusd=10000,
    )

    _generate_with_budget(llm, budget, "prompt", role="mutation")

    assert backend.calls == 1
    assert budget.llm_calls == 1
    assert budget.llm_cost_microusd == 10000
    with pytest.raises(RuntimeError, match="max_llm_cost_microusd"):
        _generate_with_budget(llm, budget, "prompt", role="mutation")
    assert backend.calls == 1


def test_llm_seconds_budget_stops_before_next_llm_call():
    class TimedBackend:
        name = "timed/model"
        api_mode = None

        def __init__(self):
            self.calls = 0

        def generate(self, prompt, **kwargs):
            self.calls += 1
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    backend = TimedBackend()
    llm = LLMEnsemble([backend])
    budget = RunBudget(
        max_generations=2,
        max_evaluations=None,
        max_evaluator_seconds=None,
        max_runtime_seconds=None,
        started_at=time.monotonic(),
        started_at_utc="2000-01-01T00:00:00.000Z",
        max_llm_seconds=0.000000001,
    )

    _generate_with_budget(llm, budget, "prompt", role="mutation")

    assert backend.calls == 1
    assert budget.llm_calls == 1
    assert budget.llm_seconds > 0.0
    with pytest.raises(RuntimeError, match="max_llm_seconds"):
        _generate_with_budget(llm, budget, "prompt", role="mutation")
    assert backend.calls == 1


def test_llm_role_seconds_budget_stops_matching_role_before_next_call():
    class TimedBackend:
        name = "timed/model"
        api_mode = None

        def __init__(self):
            self.calls = 0

        def generate(self, prompt, **kwargs):
            self.calls += 1
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    backend = TimedBackend()
    llm = LLMEnsemble([backend])
    budget = RunBudget(
        max_generations=2,
        max_evaluations=None,
        max_evaluator_seconds=None,
        max_runtime_seconds=None,
        started_at=time.monotonic(),
        started_at_utc="2000-01-01T00:00:00.000Z",
        llm_role_seconds_limits={"critique": 0.000000001},
    )

    _generate_with_budget(llm, budget, "prompt", role="mutation")
    assert budget.check_before_llm_call(role="mutation") is None
    _generate_with_budget(llm, budget, "prompt", role="critique")

    assert budget.llm_seconds_by_role["critique"] > 0.0
    with pytest.raises(RuntimeError, match="llm_role_seconds_limits"):
        _generate_with_budget(llm, budget, "prompt", role="critique")
    assert backend.calls == 2


def test_llm_wildcard_role_usage_budgets_stop_matching_feedback_roles():
    class UsageBackend:
        name = "usage/model"
        api_mode = None
        provider_response_metadata = {
            "adapter_retry": {
                "policy": "bounded_provider_internal_retries",
                "max_retries": 1,
                "attempts": 2,
                "failed_attempts": 1,
                "failures": [{"attempt": 0, "error_type": "TimeoutError"}],
            },
            "usage": {
                "input_tokens": 400,
                "output_tokens": 1600,
                "total_tokens": 2000,
            },
        }

        def __init__(self):
            self.calls = 0

        def generate(self, prompt, **kwargs):
            self.calls += 1
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    backend = UsageBackend()
    llm = LLMEnsemble(
        [backend],
        backend_metadata=[{"cost_usd_per_million_tokens": 5.0}],
    )
    budget = RunBudget(
        max_generations=2,
        max_evaluations=None,
        max_evaluator_seconds=None,
        max_runtime_seconds=None,
        started_at=time.monotonic(),
        started_at_utc="2000-01-01T00:00:00.000Z",
        llm_role_provider_attempt_limits={"feedback:*": 2},
        llm_role_token_limits={"feedback:*": 2000},
        llm_role_cost_microusd_limits={"feedback:*": 10000},
        llm_role_seconds_limits={"feedback:*": 0.000000001},
    )

    _generate_with_budget(llm, budget, "prompt", role="feedback:quality")

    assert backend.calls == 1
    assert budget.llm_provider_attempts_by_role == {"feedback:quality": 2}
    assert budget.llm_tokens_by_role == {"feedback:quality": 2000}
    assert budget.llm_cost_microusd_by_role == {"feedback:quality": 10000}
    assert budget.llm_seconds_by_role["feedback:quality"] > 0.0
    with pytest.raises(RuntimeError, match="llm_role_provider_attempt_limits"):
        _generate_with_budget(llm, budget, "prompt", role="feedback:safety")
    assert backend.calls == 1


def test_configured_llm_call_timeout_wins_when_shorter_than_runtime_budget():
    backend = MagicMock()
    backend.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    llm = LLMEnsemble([backend], call_timeout_sec=0.25)
    budget = RunBudget(
        max_generations=1,
        max_evaluations=None,
        max_evaluator_seconds=None,
        max_runtime_seconds=10.0,
        started_at=time.monotonic(),
        started_at_utc="2000-01-01T00:00:00.000Z",
    )

    _generate_with_budget(llm, budget, "prompt", role="mutation")

    assert llm.call_timeout_sec == 0.25
    assert llm.last_call["call_timeout_sec"] == 0.25


def test_all_invalid_seeds_stop_without_starting_generation_or_mutation_call():
    tmpdir = tempfile.mkdtemp()
    llm = _llm()

    with patch("libreevolve.core.loop.build_llm", return_value=llm) as build:
        best = evolve(
            _problem("def evaluate(c): return {'score': -1.0, 'is_valid': False}"),
            Config(max_generations=3, log_dir=tmpdir, problem_name="t"),
        )

    assert best is None
    build.assert_called_once()
    llm.generate.assert_not_called()
    run_dir = Path(tmpdir) / "t"
    records = [json.loads(line) for line in (run_dir / "history.jsonl").read_text().splitlines()]
    assert len(records) == 1
    assert records[0]["metadata"]["archive_admission"]["admitted"] is False
    assert records[0]["metadata"]["archive_admission"]["reason"] == "invalid_evaluation"
    assert records[0]["metadata"]["candidate_type"] == "seed"
    assert records[0]["metadata"]["post_processing"] == {
        "policy": "raw_evaluator_baseline",
        "llm_feedback": "not_applied",
        "plugin_score_composition": "not_applied",
    }
    assert records[0]["metadata"]["failure_record"]["record_type"] == "seed"
    assert records[0]["metadata"]["failure_record"]["admission_reason"] == "invalid_evaluation"
    failures = [
        json.loads(line)
        for line in (run_dir / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failures[0]["record_type"] == "seed"
    assert failures[0]["parent_id"] is None
    assert failures[0]["admission_reason"] == "invalid_evaluation"
    assert failures[0]["evaluation"]["error"] == "domain_invalid"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["runtime"]["status"] == "completed"
    assert manifest["runtime"]["stop_reason"] == "no_valid_programs"
    assert manifest["runtime"]["consumed"]["seed_evaluations"] == 1
    assert manifest["runtime"]["consumed"]["candidate_evaluations"] == 0
    assert manifest["runtime"]["consumed"]["generations_started"] == 0
    assert manifest["runtime"]["consumed"]["generations_completed"] == 0
    assert manifest["runtime"]["history"]["programs_logged"] == 1
    assert manifest["runtime"]["artifacts"]["history.jsonl"]["exists"] is True
    assert manifest["runtime"]["artifacts"]["failure_history.jsonl"]["exists"] is True


def test_zero_generation_all_invalid_seeds_report_no_valid_programs():
    tmpdir = tempfile.mkdtemp()
    llm = _llm()

    with patch("libreevolve.core.loop.build_llm", return_value=llm) as build:
        best = evolve(
            _problem("def evaluate(c): return {'score': -1.0, 'is_valid': False}"),
            Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
        )

    assert best is None
    build.assert_not_called()
    llm.generate.assert_not_called()
    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    runtime = manifest["runtime"]
    assert runtime["status"] == "completed"
    assert runtime["stop_reason"] == "no_valid_programs"
    assert runtime["consumed"]["seed_evaluations"] == 1
    assert runtime["consumed"]["candidate_evaluations"] == 0
    assert runtime["consumed"]["generations_started"] == 0
    assert runtime["consumed"]["generations_completed"] == 0
    assert runtime["history"]["programs_logged"] == 1
    assert runtime["history"]["history_partially_written"] is True
    assert runtime["history"]["no_candidates_evaluated"] is False
    assert runtime["artifacts"]["history.jsonl"]["exists"] is True
    assert runtime["artifacts"]["failure_history.jsonl"]["exists"] is True
    assert runtime["artifacts"]["best.py"]["exists"] is False
    assert runtime["artifacts"]["best_workspace"]["exists"] is False
    failures = [
        json.loads(line)
        for line in (run_dir / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failures[0]["record_type"] == "seed"
    assert failures[0]["admission_reason"] == "invalid_evaluation"


def test_initial_program_validity_report_marks_permissive_invalid_seed_boundary():
    tmpdir = tempfile.mkdtemp()

    evolve(
        _problem("def evaluate(c): return {'score': -1.0, 'is_valid': False}"),
        Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["initial_program_validity_report"]

    assert report["schema"] == "libreevolve.initial_program_validity_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_initial_program_validity_report(report)["ok"] is True
    assert report["policy"]["value"] == "permissive_baseline"
    assert report["strict_policy_enabled"] is False
    assert report["seed_program_count"] == 1
    assert report["evaluator_valid_seed_count"] == 0
    assert report["declared_metric_complete_seed_count"] == 1
    assert report["strict_valid_seed_count"] == 0
    assert report["strict_invalid_seed_count"] == 1
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["alphaevolve_complete_initial_program_parity"] is False
    assert "enable_alphaevolve_strict_initial_program_policy" in (
        report["claim_readiness"]["remaining_gap"]
    )
    record = report["records"][0]
    assert record["evaluator_is_valid"] is False
    assert record["missing_declared_metrics"] == []
    assert record["strict_initial_program_valid"] is False
    assert record["archive_admission_reason"] == "invalid_evaluation"

    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["claim_readiness"]["alphaevolve_complete_initial_program_parity"] = True
    validation = validate_initial_program_validity_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_mismatch",
        "initial_program_parity_overclaim",
    }


def test_alphaevolve_strict_initial_program_policy_stops_before_mutation():
    tmpdir = tempfile.mkdtemp()
    llm = _llm()

    with patch("libreevolve.core.loop.build_llm", return_value=llm) as build:
        best = evolve(
            _problem("def evaluate(c): return {'score': -1.0, 'is_valid': False}"),
            Config(
                max_generations=3,
                log_dir=tmpdir,
                problem_name="t",
                initial_program_validity_policy="alphaevolve_strict",
            ),
        )

    assert best is None
    build.assert_called_once()
    llm.generate.assert_not_called()
    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    runtime = manifest["runtime"]
    assert runtime["stop_reason"] == "invalid_initial_programs"
    assert runtime["consumed"]["seed_evaluations"] == 1
    assert runtime["consumed"]["candidate_evaluations"] == 0
    assert runtime["consumed"]["generations_started"] == 0
    assert manifest["config"]["initial_program_validity_policy"] == (
        "alphaevolve_strict"
    )
    assert manifest["policies"]["initial_program_validity"]["policy"] == (
        "alphaevolve_strict"
    )
    report = runtime["history"]["initial_program_validity_report"]
    assert report["strict_policy_enabled"] is True
    assert report["strict_invalid_seed_count"] == 1
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["strict_stop_on_invalid_seed"] is True
    assert validate_initial_program_validity_report(report)["ok"] is True


def test_alphaevolve_strict_initial_program_validity_report_claim_ready():
    tmpdir = tempfile.mkdtemp()

    evolve(
        _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}"),
        Config(
            max_generations=0,
            log_dir=tmpdir,
            problem_name="t",
            initial_program_validity_policy="alphaevolve_strict",
        ),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["initial_program_validity_report"]

    assert report["strict_policy_enabled"] is True
    assert report["evaluator_valid_seed_count"] == 1
    assert report["declared_metric_complete_seed_count"] == 1
    assert report["strict_valid_seed_count"] == 1
    assert report["strict_invalid_seed_count"] == 0
    assert report["claim_ready"] is True
    assert report["claim_readiness"]["alphaevolve_complete_initial_program_parity"] is True
    assert report["claim_readiness"]["remaining_gap"] == []
    assert validate_initial_program_validity_report(report)["ok"] is True


def test_zero_generation_mixed_seeds_keep_best_and_generation_limit_reason():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c):\n"
        "    valid = 'good_seed' in c\n"
        "    return {'score': 1.0 if valid else -1.0, 'is_valid': valid}\n",
        encoding="utf-8",
    )
    problem = Problem(
        name="t",
        task_description="mixed seeds",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["bad_seed = 1", "good_seed = 1"],
        problem_dir=d,
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()) as build:
        best = evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    assert best is not None
    assert best.code == "good_seed = 1"
    build.assert_not_called()
    run_dir = Path(tmpdir) / "t"
    records = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    assert len(records) == 2
    assert [record["metadata"]["archive_admission"]["admitted"] for record in records] == [
        False,
        True,
    ]
    failures = [
        json.loads(line)
        for line in (run_dir / "failure_history.jsonl").read_text().splitlines()
    ]
    assert len(failures) == 1
    runtime = json.loads((run_dir / "manifest.json").read_text())["runtime"]
    assert runtime["status"] == "completed"
    assert runtime["stop_reason"] == "max_generations"
    assert runtime["consumed"]["seed_evaluations"] == 2
    assert runtime["consumed"]["candidate_evaluations"] == 0


def test_loaded_seed_history_manifest_records_source_artifacts_for_duplicate_directories():
    problem_dir = Path(tempfile.mkdtemp())
    (problem_dir / "task_description.txt").write_text("trace seeds", encoding="utf-8")
    (problem_dir / "metrics.yaml").write_text(
        "metrics:\n"
        "  - name: score\n"
        "    primary: true\n"
        "    bounds: [0.0, 1.0]\n",
        encoding="utf-8",
    )
    (problem_dir / "validate.py").write_text(
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    seed_root = problem_dir / "initial_programs"
    seed_root.mkdir()
    for name in ("seed_a", "seed_b"):
        seed = seed_root / name
        seed.mkdir()
        (seed / "main.py").write_text("from helper import value\n", encoding="utf-8")
        (seed / "helper.py").write_text("value = 1\n", encoding="utf-8")
    problem = load_problem(problem_dir)
    tmpdir = tempfile.mkdtemp()

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()) as build:
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    build.assert_not_called()
    run_dir = Path(tmpdir) / "t"
    records = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [record["metadata"]["seed_source_path"] for record in records] == [
        "initial_programs/seed_a",
        "initial_programs/seed_b",
    ]
    assert [record["metadata"]["seed_index"] for record in records] == [0, 1]
    assert {record["metadata"]["seed_source_kind"] for record in records} == {"directory"}
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert [source["seed_source_path"] for source in manifest["problem"]["seed_sources"]] == [
        "initial_programs/seed_a",
        "initial_programs/seed_b",
    ]


def test_loaded_seed_manifest_records_skipped_seed_entries():
    problem_dir = Path(tempfile.mkdtemp())
    (problem_dir / "task_description.txt").write_text("trace skipped seeds", encoding="utf-8")
    (problem_dir / "metrics.yaml").write_text(
        "metrics:\n"
        "  - name: score\n"
        "    primary: true\n"
        "    bounds: [0.0, 1.0]\n",
        encoding="utf-8",
    )
    (problem_dir / "validate.py").write_text(
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    seed_root = problem_dir / "initial_programs"
    seed_root.mkdir()
    (seed_root / "seed.py").write_text("x = 1\n", encoding="utf-8")
    (seed_root / ".hidden.py").write_text("secret = True\n", encoding="utf-8")
    (seed_root / "notes.txt").write_text("not a seed\n", encoding="utf-8")
    problem = load_problem(problem_dir)
    tmpdir = tempfile.mkdtemp()

    evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    skipped = {
        record["seed_source_path"]: record
        for record in manifest["problem"]["seed_skipped"]
    }
    assert skipped["initial_programs/.hidden.py"]["reason"] == (
        "top_level_hidden_seed_entry"
    )
    assert skipped["initial_programs/notes.txt"]["reason"] == (
        "unsupported_top_level_seed_file"
    )


def test_loaded_invalid_seed_failure_records_source_artifact():
    problem_dir = Path(tempfile.mkdtemp())
    (problem_dir / "task_description.txt").write_text("trace bad seed", encoding="utf-8")
    (problem_dir / "metrics.yaml").write_text(
        "metrics:\n"
        "  - name: score\n"
        "    primary: true\n"
        "    bounds: [0.0, 1.0]\n",
        encoding="utf-8",
    )
    (problem_dir / "validate.py").write_text(
        "def evaluate(c):\n"
        "    ok = 'bad_seed' not in c\n"
        "    return {'score': 1.0 if ok else -1.0, 'is_valid': ok}\n",
        encoding="utf-8",
    )
    seed_root = problem_dir / "initial_programs"
    seed_root.mkdir()
    (seed_root / "bad.py").write_text("bad_seed = True\n", encoding="utf-8")
    (seed_root / "good.py").write_text("good_seed = True\n", encoding="utf-8")
    problem = load_problem(problem_dir)
    tmpdir = tempfile.mkdtemp()

    evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    run_dir = Path(tmpdir) / "t"
    failures = [
        json.loads(line)
        for line in (run_dir / "failure_history.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert failures[0]["seed_source_path"] == "initial_programs/bad.py"
    assert failures[0]["seed_source_kind"] == "file"
    assert failures[0]["seed_index"] == 0
    records = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert records[0]["metadata"]["failure_record"]["seed_source_path"] == (
        "initial_programs/bad.py"
    )


def test_direct_seed_source_records_are_validated_before_manifest_write():
    problem = _problem()
    problem.initial_programs = []
    problem.initial_workspaces = [CandidateWorkspace.from_code("x=1", "main.py")]
    problem.initial_workspace_sources = ["bad-source-record"]
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(StrictJsonlError, match="seed_sources\\[0\\] must be a mapping"):
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_direct_seed_source_records_reject_non_json_values_before_manifest_write():
    problem = _problem()
    problem.initial_programs = []
    problem.initial_workspaces = [CandidateWorkspace.from_code("x=1", "main.py")]
    problem.initial_workspace_sources = [
        {"seed_source_kind": "workspace", "files": {"not-json-safe"}}
    ]
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(StrictJsonlError, match="seed_sources\\[0\\]\\.files must be a list"):
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_seed_rows_declare_raw_baseline_policy_with_feedback_and_plugins_configured():
    tmpdir = tempfile.mkdtemp()
    llm = _RewardLLM()

    class BoostPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            return score + 1.0

    with patch("libreevolve.core.loop.build_llm", return_value=llm) as build:
        best = evolve(
            _problem("def evaluate(c): return {'score': 0.2, 'is_valid': True}"),
            Config(
                max_generations=0,
                log_dir=tmpdir,
                problem_name="t",
                llm_feedback=[{"name": "review", "weight": 0.5}],
            ),
            plugins=[BoostPlugin()],
        )

    build.assert_not_called()
    assert best.fitness == 0.2
    run_dir = Path(tmpdir) / "t"
    seed = json.loads((run_dir / "history.jsonl").read_text().splitlines()[0])
    assert seed["fitness"] == 0.2
    assert seed["metadata"]["candidate_type"] == "seed"
    assert seed["metadata"]["post_processing"] == {
        "policy": "raw_evaluator_baseline",
        "llm_feedback": "not_applied",
        "plugin_score_composition": "not_applied",
    }
    assert "score_composition" not in seed["metadata"]
    assert "llm_feedback" not in seed["evaluation"].get("metadata", {})
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["policies"]["seed_post_processing"]["policy"] == "raw_evaluator_baseline"


def test_loop_writes_problem_context_policy_to_manifest():
    tmpdir = tempfile.mkdtemp()
    problem = _problem()
    problem.context_policy = {
        "present": True,
        "manifest": {"path": "context.yaml", "sha256": "a" * 64, "bytes": 12},
        "include": ["*.md"],
        "exclude": ["skip.md"],
        "selected_count": 1,
        "skipped_count": 1,
        "skipped": [{"path": "skip.md", "reason": "excluded", "sha256": "b" * 64}],
    }

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()) as build:
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    build.assert_not_called()
    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["problem"]["context_policy"] == problem.context_policy


def test_loop_rejects_malformed_direct_problem_context_policy_before_manifest():
    tmpdir = tempfile.mkdtemp()
    problem = _problem()
    problem.context_policy = {
        "present": True,
        "skipped": [{"path": "notes.md", "reason": {"bad"}}],
    }

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()) as build:
        with pytest.raises(
            StrictJsonlError,
            match=r"context_policy\.skipped\[0\]\.reason must be JSON-safe",
        ):
            evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    build.assert_not_called()
    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_loop_persists_loader_context_limit_policy_to_manifest():
    tmpdir = tempfile.mkdtemp()
    problem_dir = Path(tempfile.mkdtemp())
    (problem_dir / "task_description.txt").write_text("context manifest test", encoding="utf-8")
    (problem_dir / "metrics.yaml").write_text(
        "metrics:\n"
        "  - name: score\n"
        "    direction: maximize\n"
        "    primary: true\n"
        "    bounds: [0.0, 1.0]\n",
        encoding="utf-8",
    )
    (problem_dir / "validate.py").write_text(
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    seeds = problem_dir / "initial_programs"
    seeds.mkdir()
    (seeds / "seed.py").write_text("x = 1\n", encoding="utf-8")
    context = problem_dir / "context"
    context.mkdir()
    (context / "keep.md").write_text("keep", encoding="utf-8")
    (context / "drop-a.bin").write_bytes(b"a")
    (context / "drop-b.bin").write_bytes(b"b")
    (context / "context.yaml").write_text(
        "max_context_entries: 3\n"
        "max_context_depth: 2\n"
        "max_skipped_diagnostics: 1\n"
        "max_context_provenance_chars: 200000\n",
        encoding="utf-8",
    )
    problem = load_problem(problem_dir)

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()) as build:
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="ctx"))

    build.assert_not_called()
    manifest = json.loads((Path(tmpdir) / "ctx" / "manifest.json").read_text())
    policy = manifest["problem"]["context_policy"]
    assert policy["max_context_entries"] == 3
    assert policy["max_context_depth"] == 2
    assert policy["max_skipped_diagnostics"] == 1
    assert policy["max_context_provenance_chars"] == 200000
    assert policy["skipped_count"] == 2
    assert policy["skipped_record_count"] == 1
    assert policy["skipped_records_truncated"] is True
    assert policy["skipped_records_omitted"] == 1


def test_runtime_history_reports_explicit_context_source_roles():
    tmpdir = tempfile.mkdtemp()
    problem_dir = Path(tempfile.mkdtemp())
    (problem_dir / "task_description.txt").write_text(
        "optimize a formula with local instructions",
        encoding="utf-8",
    )
    (problem_dir / "metrics.yaml").write_text(
        "metrics:\n"
        "  - name: score\n"
        "    direction: maximize\n"
        "    primary: true\n"
        "    bounds: [0.0, 1.0]\n",
        encoding="utf-8",
    )
    (problem_dir / "validate.py").write_text(
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    seeds = problem_dir / "initial_programs"
    seeds.mkdir()
    (seeds / "seed.py").write_text("x = 1\n", encoding="utf-8")
    context = problem_dir / "context"
    context.mkdir()
    (context / "instructions.md").write_text("always keep x positive", encoding="utf-8")
    (context / "formula.md").write_text("score = x * 2", encoding="utf-8")
    (context / "context.yaml").write_text(
        yaml.dump(
            {
                "source_roles": {
                    "instructions.md": {
                        "role": "human_instruction",
                        "topic": "search constraints",
                        "section": "operator notes",
                    },
                    "formula.md": {
                        "role": "equation",
                        "topic": "objective formula",
                        "span": "full file",
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    problem = load_problem(problem_dir)

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()) as build:
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="ctx"))

    build.assert_not_called()
    manifest = json.loads((Path(tmpdir) / "ctx" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["explicit_context_source_role_report"]

    assert report["schema"] == "libreevolve.explicit_context_source_role_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_explicit_context_source_role_report(report)["ok"] is True
    assert report["classified_count"] == 2
    assert report["unclassified_count"] == 0
    assert report["included_record_count"] == 2
    assert report["included_classified_count"] == 2
    assert report["claim_ready"] is True
    records = {record["path"]: record for record in report["records"]}
    assert records["instructions.md"]["source_role"]["role"] == "human_instruction"
    assert records["instructions.md"]["problem_linkage"]["topic"] == "search constraints"
    assert records["instructions.md"]["source_location"]["section"] == "operator notes"
    assert records["formula.md"]["source_role"]["role"] == "equation"
    assert records["formula.md"]["source_location"]["span"] == "full file"
    assert records["formula.md"]["prompt_inclusion_decision"] == (
        "included_in_startup_prompt_context"
    )
    assert report["hash_policy"]["retained_source_text"] is False

    edited = copy.deepcopy(report)
    edited["records"][0]["source_role"]["role"] = "retrieval_blob"
    validation = validate_explicit_context_source_role_report(edited)
    assert validation["ok"] is False
    assert "invalid_source_role_name" in {
        issue["code"] for issue in validation["issues"]
    }


def test_loop_writes_objective_schema_to_manifest():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c): return {'score': 0.9, 'runtime': 2.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    problem = Problem(
        name="t",
        task_description="track schema",
        metrics=[
            {"name": "score", "direction": "maximize", "bounds": [0.0, 1.0]},
            {"name": "runtime", "direction": "minimize", "bounds": [0.0, 10.0]},
        ],
        primary_metric="runtime",
        primary_bounds=(0.0, 10.0),
        validate_path=d / "validate.py",
        initial_programs=["x=1"],
        problem_dir=d,
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()) as build:
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    build.assert_not_called()
    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["problem"]["objective_schema"] == {
        "metrics": [
            {
                "name": "score",
                "direction": "maximize",
                "bounds": [0.0, 1.0],
                "source": "evaluator",
                "weight": 1.0,
                "primary": False,
            },
            {
                "name": "runtime",
                "direction": "minimize",
                "bounds": [0.0, 10.0],
                "source": "evaluator",
                "weight": 1.0,
                "primary": True,
            },
        ],
        "primary_metric": "runtime",
        "primary_bounds": [0.0, 10.0],
        "metric_count": 2,
    }


def test_loop_writes_unified_task_specification_bundle_to_manifest():
    tmpdir = tempfile.mkdtemp()
    problem = _problem()
    problem.context_sources = [
        {"path": "context/notes.md", "sha256": "a" * 64, "source_type": "text"}
    ]

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()) as build:
        evolve(
            problem,
            Config(
                max_generations=0,
                log_dir=tmpdir,
                problem_name="t",
                prompt_variants=[DEFAULT_TEMPLATE],
                backends=[{"type": "openai", "model": "gpt-4o-mini"}],
            ),
        )

    build.assert_not_called()
    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    task_spec = manifest["task_specification"]
    standalone_task_spec = json.loads(
        (run_dir / "task_specification.json").read_text(encoding="utf-8")
    )

    assert task_spec["schema"] == "libreevolve.alphaevolve_task_specification_bundle.v1"
    assert standalone_task_spec == task_spec
    assert task_spec["status"] == "partial_alphaevolve_task_specification"
    assert task_spec["validation"]["ok"] is True
    assert validate_task_specification_bundle(task_spec)["ok"] is True
    assert len(task_spec["task_spec_id"]) == 64

    fields = task_spec["fields"]
    assert fields["initial_programs"]["status"] == "present"
    assert fields["initial_programs"]["manifest_path"] == "problem.seed_sources"
    assert fields["initial_programs"]["count"] == len(manifest["problem"]["seed_sources"])
    assert fields["evaluation_code"]["status"] == "present"
    assert fields["evaluation_code"]["ids"][0]["relative_path"] == "validate.py"
    assert fields["prompt_template_and_config"]["variant_count"] == 1
    assert fields["prompt_template_and_config"]["ids"][0]["sha256"] == (
        manifest["config"]["prompt_variants_metadata"][0]["sha256"]
    )
    assert fields["llm_ensemble"]["backend_count"] == 1
    assert fields["llm_ensemble"]["ids"][0] == {
        "backend_index": 0,
        "type": "openai",
        "model": "gpt-4o-mini",
        "api_mode": None,
    }
    assert fields["background_knowledge"]["status"] == "present"
    assert fields["background_knowledge"]["context_source_count"] == 1
    assert fields["human_problem_formulation"]["status"] == "omitted"
    assert fields["human_problem_formulation"]["manifest_path"] == (
        "problem.formulation_metadata"
    )
    assert fields["candidate_representation"]["manifest_path"] == (
        "policies.candidate_language"
    )
    assert fields["objective_metrics"]["primary_metric"] == "score"
    assert "startup_task_spec_needs_runtime_score_path_causal_attribution" in (
        task_spec["unsupported_or_incomplete"]
    )

    tampered = copy.deepcopy(task_spec)
    tampered["fields"]["llm_ensemble"]["backend_count"] = 99
    validation = validate_task_specification_bundle(tampered)
    assert validation["ok"] is False
    assert validation["issues"][0]["code"] == "invalid_task_spec_id"


def test_runtime_history_reports_task_spec_artifact_resolution():
    tmpdir = tempfile.mkdtemp()
    problem = _problem()
    problem.context_sources = [
        {"path": "context/notes.md", "sha256": "a" * 64, "source_type": "text"}
    ]
    llm = _TelemetryLLM("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE")

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                prompt_variants=[DEFAULT_TEMPLATE],
                backends=[{"type": "openai", "model": "gpt-4o-mini"}],
            ),
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["task_spec_artifact_resolution_report"]
    task_spec = manifest["task_specification"]

    assert report["schema"] == "libreevolve.task_spec_artifact_resolution_report.v1"
    assert report["task_spec_id"] == task_spec["task_spec_id"]
    assert report["task_spec_validation_ok"] is True
    assert report["standalone_task_spec_artifact"]["path"] == "task_specification.json"
    assert report["standalone_task_spec_artifact"]["role"] == (
        "standalone_task_specification"
    )
    assert report["standalone_task_spec_artifact"]["present"] is True
    assert len(report["standalone_task_spec_artifact"]["sha256"]) == 64
    deep_id = report["deep_id_resolution"]
    assert deep_id["schema"] == "libreevolve.task_spec_deep_id_resolution.v1"
    assert deep_id["program_count"] == 2
    assert deep_id["record_count"] == 2
    assert deep_id["candidate_history_join_count"] == 2
    assert deep_id["generated_prompt_record_count"] == 1
    assert deep_id["prompt_history_add_join_count"] == 1
    assert deep_id["prompt_history_score_join_count"] == 1
    assert deep_id["evaluator_result_join_count"] == 2
    assert deep_id["claim_readiness"]["candidate_history_rows_joined"] is True
    assert deep_id["claim_readiness"]["prompt_history_rows_joined"] is True
    assert deep_id["claim_readiness"]["evaluator_row_ids_resolved"] is True
    assert report["validation"]["ok"] is True
    assert validate_task_spec_artifact_resolution_report(report)["ok"] is True
    assert report["field_count"] == 8
    assert report["manifest_path_count"] == report["manifest_path_resolved_count"]
    assert report["artifact_link_count"] > 0
    assert report["program_count"] == 2
    assert report["seed_program_count"] == 1
    assert report["generated_program_count"] == 1
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["startup_bundle_validated"] is True
    assert report["claim_readiness"]["manifest_paths_resolved"] is True
    assert report["claim_readiness"]["standalone_task_spec_artifact"] is True
    assert report["claim_readiness"]["candidate_history_rows_joined"] is True
    assert report["claim_readiness"]["prompt_history_rows_joined"] is True
    assert report["claim_readiness"]["evaluator_row_ids_resolved"] is True
    assert report["claim_readiness"]["evolvable_component_span_ids"] is False
    assert report["claim_readiness"]["full_alphaevolve_task_spec_parity"] is False
    assert "deep_id_resolution_into_prompt_evaluator_candidate_history" not in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "deep_evaluator_score_causality_resolution" in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "standalone_task_spec_report_examples" not in (
        report["claim_readiness"]["remaining_gap"]
    )

    by_field = {record["field"]: record for record in report["field_resolutions"]}
    assert set(by_field) == {
        "initial_programs",
        "evaluation_code",
        "prompt_template_and_config",
        "llm_ensemble",
        "background_knowledge",
        "human_problem_formulation",
        "candidate_representation",
        "objective_metrics",
    }
    initial = by_field["initial_programs"]
    assert initial["manifest_path_resolutions"] == [
        {
            "path": "problem.seed_sources",
            "resolved": True,
            "value_type": "list",
            "value_count": 1,
        }
    ]
    assert len(initial["reference_summary"]["seed_program_ids"]) == 1
    assert initial["reference_summary"]["seed_program_ids"][0].startswith(
        "candidate-seed-0-"
    )
    assert initial["reference_summary"]["evolvable_component_span_count"] == 0
    assert "evolvable_component_span_ids" in initial["unresolved_gap"]
    evaluator = by_field["evaluation_code"]
    assert evaluator["reference_summary"]["entrypoint_count"] == 1
    assert evaluator["reference_summary"]["evaluated_program_count"] == 2
    prompt_artifacts = {
        artifact["path"]: artifact
        for artifact in by_field["prompt_template_and_config"][
            "runtime_artifact_resolutions"
        ]
    }
    assert prompt_artifacts["prompt_history.jsonl"]["present"] is True
    llm_artifacts = {
        artifact["path"]: artifact
        for artifact in by_field["llm_ensemble"]["runtime_artifact_resolutions"]
    }
    assert "llm_ensemble:llm_calls.jsonl" == llm_artifacts["llm_calls.jsonl"]["role"]
    objective = by_field["objective_metrics"]["reference_summary"]
    assert objective["primary_metric"] == "score"
    assert objective["paper_metric_names"] == ["score"]
    assert "score_field_to_evolved_block_mapping" in (
        by_field["objective_metrics"]["unresolved_gap"]
    )
    formulation = by_field["human_problem_formulation"]
    assert formulation["reference_summary"]["review_status"] == "not_reviewed"
    assert formulation["manifest_path_resolutions"] == [
        {
            "path": "problem.formulation_metadata",
            "resolved": True,
            "value_type": "object",
            "value_count": 10,
        }
    ]
    generated_deep_record = [
        record
        for record in deep_id["records"]
        if record["candidate_type"] == "generated"
    ][0]
    assert generated_deep_record["history_join"]["candidate_history"]["stream"] == (
        "history.jsonl"
    )
    assert generated_deep_record["history_join"]["prompt_history"]["add_line_number"] == 1
    assert generated_deep_record["history_join"]["prompt_history"]["score_line_number"] == 2
    assert generated_deep_record["evaluation_link"]["evaluator_result_joined"] is True
    assert generated_deep_record["evaluation_link"]["evaluator_result"]["stream"] == (
        "evaluator_results.jsonl"
    )
    assert len(generated_deep_record["evaluation_link"]["evaluator_result"]["row_id"]) == 24
    assert generated_deep_record["evaluation_link"]["row_policy"] == (
        "candidate_id_to_evaluator_results_jsonl_row"
    )
    evaluator_rows = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "evaluator_results.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert [row["record_schema"] for row in evaluator_rows] == [
        "libreevolve.evaluator_result.v1",
        "libreevolve.evaluator_result.v1",
    ]
    assert manifest["runtime"]["artifacts"]["evaluator_results.jsonl"]["exists"] is True
    assert manifest["runtime"]["history"]["evaluator_result_export"]["record_count"] == 2

    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["claim_readiness"]["full_alphaevolve_task_spec_parity"] = True
    edited["standalone_task_spec_artifact"]["present"] = False
    edited["claim_readiness"]["standalone_task_spec_artifact"] = False
    edited["deep_id_resolution"]["claim_ready"] = True
    edited["deep_id_resolution"]["claim_readiness"][
        "full_alphaevolve_task_spec_id_resolution"
    ] = True
    validation = validate_task_spec_artifact_resolution_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_overclaim",
        "missing_standalone_task_spec_artifact",
        "standalone_task_spec_artifact_not_ready",
        "task_spec_deep_id_claim_overclaim",
        "task_spec_deep_id_parity_overclaim",
        "task_spec_parity_overclaim",
    }


def test_task_spec_artifact_resolution_links_embedded_score_fields():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(code):\n"
        "    return {'score': 0.0, 'is_valid': False}\n"
    )
    problem.initial_programs = [
        "def transform(value):\n"
        "    # EVOLVE-BLOCK-START scoring_rule\n"
        "    return value\n"
        "    # EVOLVE-BLOCK-END\n\n"
        "def evaluate(eval_inputs):\n"
        "    return {'score': transform(eval_inputs['score']), 'is_valid': True}\n"
    ]

    evolve(
        problem,
        Config(
            max_generations=0,
            log_dir=tmpdir,
            problem_name="t",
            eval_stages=[
                {
                    "name": "candidate_eval",
                    "mode": "embedded_evaluate",
                    "eval_inputs": {"score": 0.7},
                }
            ],
        ),
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["task_spec_artifact_resolution_report"]

    assert report["validation"]["ok"] is True
    assert validate_task_spec_artifact_resolution_report(report)["ok"] is True
    assert report["claim_readiness"]["evolvable_component_span_ids"] is True
    assert report["claim_readiness"]["score_field_to_candidate_path_links"] is True
    assert report["claim_readiness"][
        "score_field_to_evolved_block_causal_attribution"
    ] is True
    assert report["claim_readiness"]["embedded_only_problem_definition"] is True
    assert "score_field_to_candidate_path_links" not in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "embedded_only_problem_definitions" not in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "evolvable_component_span_ids" not in (
        report["claim_readiness"]["remaining_gap"]
    )

    by_field = {record["field"]: record for record in report["field_resolutions"]}
    initial = by_field["initial_programs"]
    assert "evolvable_component_span_ids" not in initial["unresolved_gap"]
    initial_summary = initial["reference_summary"]
    assert initial_summary["evolvable_component_span_count"] == 1
    assert initial_summary["evolvable_component_spans_truncated"] is False
    span = initial_summary["evolvable_component_spans"][0]
    assert span["path"] == "main.py"
    assert span["name"] == "scoring_rule"
    assert span["span_role"] == "initial_program_evolvable_component"
    assert len(span["span_id"]) == 24
    assert len(span["content_sha256"]) == 64
    objective = by_field["objective_metrics"]
    assert "score_field_to_evolved_block_mapping" not in objective["unresolved_gap"]
    assert "deep_evaluator_score_causality_resolution" not in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "score_field_to_evolved_block_causal_attribution" not in (
        objective["unresolved_gap"]
    )
    summary = objective["reference_summary"]
    assert summary["score_field_link_count"] == 1
    assert summary["score_field_causal_attribution_count"] == 1
    assert summary["score_field_links_truncated"] is False
    assert len(summary["score_field_links"]) == 1
    link = summary["score_field_links"][0]
    assert link["metric_name"] == "score"
    assert link["candidate_primary_file"] == "main.py"
    assert link["causal_attribution_claimed"] is True
    assert link["link_policy"] == "static_ast_evaluate_return_dependency_to_evolved_block"
    assert link["evolved_block_candidate_count"] == 1
    assert link["evolved_block_candidates"][0]["name"] == "scoring_rule"
    assert link["causal_attribution"]["dependency_functions"] == ["transform"]

    edited = copy.deepcopy(report)
    edited_initial = next(
        record
        for record in edited["field_resolutions"]
        if record["field"] == "initial_programs"
    )
    edited_initial["reference_summary"]["evolvable_component_spans"][0][
        "span_role"
    ] = "overclaim"
    edited_objective = next(
        record
        for record in edited["field_resolutions"]
        if record["field"] == "objective_metrics"
    )
    edited_objective["reference_summary"]["score_field_links"][0]["link_policy"] = (
        "candidate_path_candidates_not_causal_attribution"
    )
    validation = validate_task_spec_artifact_resolution_report(edited)
    assert validation["ok"] is False
    issue_codes = {issue["code"] for issue in validation["issues"]}
    assert "invalid_score_field_causal_policy" in issue_codes
    assert "invalid_task_spec_evolvable_component_span_role" in issue_codes


def test_loaded_problem_formulation_metadata_reaches_manifest_and_report():
    problem_dir = Path(tempfile.mkdtemp())
    (problem_dir / "task_description.txt").write_text("formulated task", encoding="utf-8")
    (problem_dir / "metrics.yaml").write_text(
        "metrics:\n"
        "  - name: score\n"
        "    primary: true\n"
        "    bounds: [0.0, 1.0]\n",
        encoding="utf-8",
    )
    (problem_dir / "validate.py").write_text(
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    seed_dir = problem_dir / "initial_programs"
    seed_dir.mkdir()
    (seed_dir / "seed.py").write_text("x = 1\n", encoding="utf-8")
    (problem_dir / "formulation.yaml").write_text(
        "problem_origin: expert_suggested\n"
        "contributors:\n"
        "  - role: formulation_advisor\n"
        "    label: geometry advisor\n"
        "formulation_notes: Advisor suggested the compact benchmark framing.\n"
        "objective_rationale: Maximize score because it is the published target.\n"
        "evaluator_rationale: The validator measures the exact objective output.\n"
        "parameter_scope:\n"
        "  - name: instance_size\n"
        "    value: small deterministic fixture\n"
        "    rationale: Keeps local tests bounded.\n"
        "background_knowledge_refs:\n"
        "  - papers/alphaevolve.pdf section 3.2\n"
        "review:\n"
        "  status: expert_reviewed\n"
        "  reviewer_labels:\n"
        "    - geometry advisor\n",
        encoding="utf-8",
    )
    problem = load_problem(problem_dir)
    tmpdir = tempfile.mkdtemp()

    evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    formulation = manifest["problem"]["formulation_metadata"]
    assert formulation["schema"] == "libreevolve.problem_formulation_metadata.v1"
    assert formulation["status"] == "provided"
    assert formulation["problem_origin"] == "expert_suggested"
    assert formulation["contributors"][0]["role"] == "formulation_advisor"
    assert manifest["task_specification"]["fields"]["human_problem_formulation"][
        "status"
    ] == "present"
    report = manifest["runtime"]["history"]["problem_formulation_provenance_report"]
    assert report["schema"] == "libreevolve.problem_formulation_provenance_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_problem_formulation_provenance_report(report)["ok"] is True
    assert report["claim_ready"] is True
    assert report["claim_readiness"][
        "alphaevolve_expert_guided_formulation_parity"
    ] is True
    assert report["review_status"] == "expert_reviewed"


def test_benchmark_fixture_readiness_report_keeps_smoke_scope_unready():
    problem_dir = Path(tempfile.mkdtemp())
    (problem_dir / "task_description.txt").write_text(
        "matrix smoke fixture", encoding="utf-8"
    )
    (problem_dir / "metrics.yaml").write_text(
        "metrics:\n"
        "  - name: score\n"
        "    primary: true\n"
        "    bounds: [0.0, 1.0]\n",
        encoding="utf-8",
    )
    (problem_dir / "validate.py").write_text(
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    seed_dir = problem_dir / "initial_programs"
    seed_dir.mkdir()
    (seed_dir / "seed.py").write_text("x = 1\n", encoding="utf-8")
    (problem_dir / "formulation.yaml").write_text(
        "problem_origin: benchmark_fixture\n"
        "contributors:\n"
        "  - role: formulation_advisor\n"
        "    label: matrix advisor\n"
        "formulation_notes: Reviewed as a bounded matrix smoke fixture.\n"
        "objective_rationale: Maximize score for the declared smoke metric.\n"
        "evaluator_rationale: The validator returns the declared primary score.\n"
        "parameter_scope:\n"
        "  - name: matrix_size\n"
        "    value: 2x2 smoke case\n"
        "    rationale: Keeps regression runs bounded.\n"
        "background_knowledge_refs:\n"
        "  - papers/2506.13131__AlphaEvolve.pdf pages 21-22\n"
        "review:\n"
        "  status: domain_owner_signed_off\n"
        "  reviewer_labels:\n"
        "    - matrix advisor\n",
        encoding="utf-8",
    )
    problem = load_problem(problem_dir)
    tmpdir = tempfile.mkdtemp()

    evolve(
        problem,
        Config(
            max_generations=0,
            log_dir=tmpdir,
            problem_name="matrix_multiplication",
        ),
    )

    manifest = json.loads(
        (Path(tmpdir) / "matrix_multiplication" / "manifest.json").read_text()
    )
    report = manifest["runtime"]["history"]["benchmark_fixture_readiness_report"]
    assert report["schema"] == "libreevolve.benchmark_fixture_readiness_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_benchmark_fixture_readiness_report(report)["ok"] is True
    assert report["problem_name"] == "matrix_multiplication"
    assert report["example_scope_registry"]["validation_ok"] is True
    assert report["example_scope_registry"]["smoke_only"] is True
    assert report["scope_level"] == "smoke"
    assert report["alphaevolve_comparable"] is False
    assert report["matching_example_scope"]["problem_id"] == "matrix_multiplication"
    evidence = report["readiness_evidence"]
    assert evidence["example_scope_record_present"] is True
    assert evidence["scope_registry_valid"] is True
    assert evidence["not_smoke_only_claim"] is False
    assert evidence["alphaevolve_comparable_scope"] is False
    assert evidence["reviewed_formulation_metadata"] is True
    assert evidence["background_knowledge_refs"] is True
    assert evidence["task_spec_target_identity"] is True
    assert evidence["benchmark_hardening_refs"] is True
    assert evidence["repeated_seed_protocol"] is False
    assert evidence["sota_or_target_baseline_values"] is False
    assert evidence["fixture_emitted_result_artifacts"] is False
    assert evidence["anti_gaming_negative_fixtures_passed"] is False
    assert report["hardening_ref_count"] == 1
    assert report["claim_ready"] is False
    assert report["claim_readiness"]["benchmark_fixture_readiness"] is False
    assert report["claim_readiness"]["alphaevolve_paper_claim_fixture"] is False
    assert "non_smoke_benchmark_scope_record" in (
        report["claim_readiness"]["remaining_gap"]
    )
    assert "alphaevolve_comparable_scope_record" in (
        report["claim_readiness"]["remaining_gap"]
    )

    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["alphaevolve_comparable"] = True
    edited["readiness_evidence"]["repeated_seed_protocol"] = True
    edited["claim_readiness"]["benchmark_fixture_readiness"] = True
    validation = validate_benchmark_fixture_readiness_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_overclaim",
        "benchmark_fixture_readiness_overclaim",
        "repeated_seed_protocol_overclaim",
        "smoke_scope_comparable_overclaim",
    }


def test_problem_formulation_report_marks_missing_metadata_boundary():
    tmpdir = tempfile.mkdtemp()

    evolve(_problem(), Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["problem_formulation_provenance_report"]
    assert report["metadata_status"] == "not_provided"
    assert report["claim_ready"] is False
    assert report["claim_readiness"][
        "alphaevolve_expert_guided_formulation_parity"
    ] is False
    assert "formulation_yaml_in_problem_fixture" in (
        report["claim_readiness"]["remaining_gap"]
    )
    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["claim_readiness"]["alphaevolve_expert_guided_formulation_parity"] = True
    validation = validate_problem_formulation_provenance_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_mismatch",
        "formulation_parity_mismatch",
    }


def test_direct_problem_formulation_metadata_rejects_secret_like_text_before_manifest():
    problem = _problem()
    problem.formulation_metadata = {
        "problem_origin": "expert_suggested",
        "formulation_notes": (
            "OPENAI_API_KEY=sk-123456789012345678901234567890123456789012345678"
        ),
    }
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(
        StrictJsonlError,
        match="formulation_metadata\\.formulation_notes must not contain secret-like text",
    ):
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_loaded_collaborator_feedback_metadata_reaches_manifest_and_report():
    problem_dir = Path(tempfile.mkdtemp())
    (problem_dir / "task_description.txt").write_text("feedback shaped task", encoding="utf-8")
    (problem_dir / "metrics.yaml").write_text(
        "metrics:\n"
        "  - name: score\n"
        "    primary: true\n"
        "    bounds: [0.0, 1.0]\n",
        encoding="utf-8",
    )
    (problem_dir / "validate.py").write_text(
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    seed_dir = problem_dir / "initial_programs"
    seed_dir.mkdir()
    (seed_dir / "seed.py").write_text("x = 1\n", encoding="utf-8")
    (problem_dir / "collaborator_feedback.yaml").write_text(
        "cohorts:\n"
        "  - cohort_id: workflow-users\n"
        "    role: early_user\n"
        "    label: workflow users\n"
        "    use_case_area: prompt workflow\n"
        "  - cohort_id: benchmark-partners\n"
        "    role: collaborator\n"
        "    label: benchmark partners\n"
        "    use_case_area: benchmark operations\n"
        "feedback_events:\n"
        "  - feedback_id: fb-workflow-1\n"
        "    cohort_id: workflow-users\n"
        "    status: validated\n"
        "    summary: Users reported unclear prompt artifact traceability.\n"
        "    affected_workflow_areas:\n"
        "      - prompt history review\n"
        "    change_artifact_links:\n"
        "      - docs/run-artifacts.md prompt history section\n"
        "    validation_outcomes:\n"
        "      - focused tests validate artifact summary fields\n"
        "    claim_links:\n"
        "      - robustness\n"
        "  - feedback_id: fb-benchmark-1\n"
        "    cohort_id: benchmark-partners\n"
        "    status: validated\n"
        "    summary: Partners needed clearer benchmark result boundaries.\n"
        "    affected_workflow_areas:\n"
        "      - benchmark report review\n"
        "    change_artifact_links:\n"
        "      - papers/README.md AlphaEvolve table row\n"
        "    validation_outcomes:\n"
        "      - paper manifest tests validate status wording\n"
        "    claim_links:\n"
        "      - versatility\n"
        "privacy_policy:\n"
        "  retention: redacted_labels_only\n"
        "  redaction: anonymous_labels\n"
        "review:\n"
        "  status: collaborator_reviewed\n"
        "  reviewer_labels:\n"
        "    - workflow users\n",
        encoding="utf-8",
    )
    problem = load_problem(problem_dir)
    tmpdir = tempfile.mkdtemp()

    evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    metadata = manifest["problem"]["collaborator_feedback_metadata"]
    assert metadata["schema"] == "libreevolve.collaborator_feedback_metadata.v1"
    assert metadata["status"] == "provided"
    assert metadata["cohorts"][0]["cohort_id"] == "workflow-users"
    assert metadata["feedback_events"][0]["claim_links"] == ["robustness"]
    report = manifest["runtime"]["history"]["collaborator_feedback_provenance_report"]
    assert report["schema"] == "libreevolve.collaborator_feedback_provenance_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_collaborator_feedback_provenance_report(report)["ok"] is True
    assert report["claim_ready"] is True
    assert report["use_case_area_count"] == 2
    assert report["events_with_change_artifact_links"] == 2
    assert report["events_with_validation_outcomes"] == 2
    assert report["claim_readiness"][
        "alphaevolve_collaborator_feedback_parity"
    ] is True


def test_collaborator_feedback_report_marks_missing_metadata_boundary():
    tmpdir = tempfile.mkdtemp()

    evolve(_problem(), Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["collaborator_feedback_provenance_report"]
    assert report["metadata_status"] == "not_provided"
    assert report["claim_ready"] is False
    assert report["validation"]["ok"] is True
    assert report["claim_readiness"][
        "alphaevolve_collaborator_feedback_parity"
    ] is False
    assert "collaborator_feedback_yaml_in_problem_fixture" in (
        report["claim_readiness"]["remaining_gap"]
    )
    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["claim_readiness"]["alphaevolve_collaborator_feedback_parity"] = True
    validation = validate_collaborator_feedback_provenance_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_mismatch",
        "collaborator_feedback_parity_mismatch",
    }


def test_direct_collaborator_feedback_metadata_rejects_secret_like_text_before_manifest():
    problem = _problem()
    problem.collaborator_feedback_metadata = {
        "cohorts": [
            {
                "cohort_id": "users",
                "role": "early_user",
                "label": "users",
                "use_case_area": "OPENAI_API_KEY=sk-123456789012345678901234567890123456789012345678",
            }
        ]
    }
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(
        StrictJsonlError,
        match=(
            "collaborator_feedback_metadata\\.cohorts\\[0\\]\\.use_case_area "
            "must not contain secret-like text"
        ),
    ):
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_loaded_acknowledgement_metadata_reaches_manifest_and_report():
    problem_dir = Path(tempfile.mkdtemp())
    (problem_dir / "task_description.txt").write_text("acknowledged task", encoding="utf-8")
    (problem_dir / "metrics.yaml").write_text(
        "metrics:\n"
        "  - name: score\n"
        "    primary: true\n"
        "    bounds: [0.0, 1.0]\n",
        encoding="utf-8",
    )
    (problem_dir / "validate.py").write_text(
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    seed_dir = problem_dir / "initial_programs"
    seed_dir.mkdir()
    (seed_dir / "seed.py").write_text("x = 1\n", encoding="utf-8")
    records = [
        ("ack-white-paper", "white_paper_review", "white_paper", "AlphaEvolve paper", 21),
        ("ack-explore", "early_exploration", "general_system", "early system work", 21),
        ("ack-support", "support_advice", "general_system", "system support", 21),
        (
            "ack-management",
            "practical_application_management_advice",
            "practical_application",
            "application management",
            22,
        ),
        ("ack-app-review", "application_review", "application_specific_work", "application review", 22),
        (
            "ack-app-advice",
            "application_specific_advice",
            "application_specific_work",
            "application advice",
            22,
        ),
    ]
    yaml_lines = ["records:"]
    for record_id, role, scope_type, scope_label, page in records:
        yaml_lines.extend(
            [
                f"  - record_id: {record_id}",
                f"    contributor_label: {record_id} contributor",
                f"    role_category: {role}",
                f"    scope_type: {scope_type}",
                f"    scope_label: {scope_label}",
                f"    source_page: {page}",
                "    source_section: AlphaEvolve acknowledgements",
            ]
        )
    yaml_lines.extend(
        [
            "privacy_policy:",
            "  retention: redacted_labels_only",
            "  redaction: anonymous_labels",
            "review:",
            "  status: paper_process_reviewed",
            "  reviewer_labels:",
            "    - paper process reviewer",
        ]
    )
    (problem_dir / "acknowledgements.yaml").write_text(
        "\n".join(yaml_lines) + "\n",
        encoding="utf-8",
    )
    problem = load_problem(problem_dir)
    tmpdir = tempfile.mkdtemp()

    evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    metadata = manifest["problem"]["acknowledgement_metadata"]
    assert metadata["schema"] == "libreevolve.acknowledgement_metadata.v1"
    assert metadata["status"] == "provided"
    assert metadata["records"][0]["role_category"] == "white_paper_review"
    report = manifest["runtime"]["history"]["acknowledgement_role_provenance_report"]
    assert report["schema"] == "libreevolve.acknowledgement_role_provenance_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_acknowledgement_role_provenance_report(report)["ok"] is True
    assert report["claim_ready"] is True
    assert report["record_count"] == 6
    assert report["source_pages"] == [21, 22]
    assert report["claim_readiness"][
        "alphaevolve_acknowledgement_role_parity"
    ] is True


def test_matrix_example_acknowledgement_fixture_is_claim_ready():
    repo_root = Path(__file__).resolve().parents[2]
    problem = load_problem(
        repo_root
        / "libreevolve"
        / "problems"
        / "examples"
        / "matrix_multiplication"
    )
    tmpdir = tempfile.mkdtemp()

    evolve(
        problem,
        Config(
            max_generations=0,
            log_dir=tmpdir,
            problem_name="matrix_acknowledgements",
        ),
    )

    manifest = json.loads(
        (Path(tmpdir) / "matrix_acknowledgements" / "manifest.json").read_text()
    )
    metadata = manifest["problem"]["acknowledgement_metadata"]
    assert metadata["schema"] == "libreevolve.acknowledgement_metadata.v1"
    assert metadata["status"] == "provided"
    assert len(metadata["records"]) == 6

    report = manifest["runtime"]["history"]["acknowledgement_role_provenance_report"]
    assert validate_acknowledgement_role_provenance_report(report)["ok"] is True
    assert report["claim_ready"] is True
    assert report["record_count"] == 6
    assert report["source_pages"] == [21, 22]
    assert report["records_with_source_locator"] == 6
    assert report["claim_readiness"][
        "alphaevolve_acknowledgement_role_parity"
    ] is True


def test_acknowledgement_report_marks_missing_metadata_boundary():
    tmpdir = tempfile.mkdtemp()

    evolve(_problem(), Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["acknowledgement_role_provenance_report"]
    assert report["metadata_status"] == "not_provided"
    assert report["claim_ready"] is False
    assert report["validation"]["ok"] is True
    assert report["claim_readiness"][
        "alphaevolve_acknowledgement_role_parity"
    ] is False
    assert "acknowledgements_yaml_in_problem_fixture" in (
        report["claim_readiness"]["remaining_gap"]
    )
    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["claim_readiness"]["alphaevolve_acknowledgement_role_parity"] = True
    validation = validate_acknowledgement_role_provenance_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_mismatch",
        "acknowledgement_role_parity_mismatch",
    }


def test_direct_acknowledgement_metadata_rejects_secret_like_text_before_manifest():
    problem = _problem()
    problem.acknowledgement_metadata = {
        "records": [
            {
                "record_id": "ack-secret",
                "contributor_label": (
                    "OPENAI_API_KEY=sk-123456789012345678901234567890123456789012345678"
                ),
                "role_category": "white_paper_review",
                "scope_type": "white_paper",
                "scope_label": "paper",
                "source_page": 21,
                "source_section": "Acknowledgements",
            }
        ]
    }
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(
        StrictJsonlError,
        match=(
            "acknowledgement_metadata\\.records\\[0\\]\\.contributor_label "
            "must not contain secret-like text"
        ),
    ):
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_loaded_paper_author_metadata_reaches_manifest_and_report():
    problem_dir = Path(tempfile.mkdtemp())
    (problem_dir / "task_description.txt").write_text("author metadata task", encoding="utf-8")
    (problem_dir / "metrics.yaml").write_text(
        "metrics:\n"
        "  - name: score\n"
        "    primary: true\n"
        "    bounds: [0.0, 1.0]\n",
        encoding="utf-8",
    )
    (problem_dir / "validate.py").write_text(
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    seed_dir = problem_dir / "initial_programs"
    seed_dir.mkdir()
    (seed_dir / "seed.py").write_text("x = 1\n", encoding="utf-8")
    (problem_dir / "paper_authors.yaml").write_text(
        "records:\n"
        "  - record_id: author-equal\n"
        "    contributor_label: equal contributor group\n"
        "    role_category: equal_contributor\n"
        "    scope_type: publication\n"
        "    scope_label: title page equal contributor marker\n"
        "    source_page: 1\n"
        "    source_section: AlphaEvolve title page\n"
        "    title_page_marker: star\n"
        "    contact_policy: no_contact_recorded\n"
        "  - record_id: author-writer\n"
        "    contributor_label: manuscript writer group\n"
        "    role_category: manuscript_writer\n"
        "    scope_type: manuscript\n"
        "    scope_label: Contributions section manuscript writing\n"
        "    source_page: 22\n"
        "    source_section: Contributions\n"
        "    contact_policy: no_contact_recorded\n"
        "  - record_id: author-input\n"
        "    contributor_label: paper input group\n"
        "    role_category: paper_input\n"
        "    scope_type: paper_input\n"
        "    scope_label: Contributions section paper input\n"
        "    source_page: 22\n"
        "    source_section: Contributions\n"
        "    contact_policy: no_contact_recorded\n"
        "  - record_id: author-corresponding\n"
        "    contributor_label: corresponding author group\n"
        "    role_category: corresponding_author\n"
        "    scope_type: correspondence\n"
        "    scope_label: Author information contact list\n"
        "    source_page: 23\n"
        "    source_section: Author information\n"
        "    contact_policy: public_contact_available_in_source\n"
        "privacy_policy:\n"
        "  contact: redacted_contact\n"
        "review:\n"
        "  status: publication_metadata_reviewed\n"
        "  reviewer_labels:\n"
        "    - publication metadata reviewer\n",
        encoding="utf-8",
    )
    problem = load_problem(problem_dir)
    tmpdir = tempfile.mkdtemp()

    evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    metadata = manifest["problem"]["paper_author_metadata"]
    assert metadata["schema"] == "libreevolve.paper_author_metadata.v1"
    assert metadata["status"] == "provided"
    assert metadata["records"][0]["title_page_marker"] == "star"
    report = manifest["runtime"]["history"]["paper_author_metadata_report"]
    assert report["schema"] == "libreevolve.paper_author_metadata_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_paper_author_metadata_report(report)["ok"] is True
    assert report["claim_ready"] is True
    assert report["record_count"] == 4
    assert report["source_pages"] == [1, 22, 23]
    assert report["claim_readiness"][
        "alphaevolve_publication_author_metadata_parity"
    ] is True


def test_matrix_example_paper_author_fixture_is_claim_ready():
    repo_root = Path(__file__).resolve().parents[2]
    problem = load_problem(
        repo_root
        / "libreevolve"
        / "problems"
        / "examples"
        / "matrix_multiplication"
    )
    tmpdir = tempfile.mkdtemp()

    evolve(
        problem,
        Config(max_generations=0, log_dir=tmpdir, problem_name="matrix_fixture"),
    )

    manifest = json.loads(
        (Path(tmpdir) / "matrix_fixture" / "manifest.json").read_text()
    )
    metadata = manifest["problem"]["paper_author_metadata"]
    assert metadata["schema"] == "libreevolve.paper_author_metadata.v1"
    assert metadata["status"] == "provided"
    assert {record["role_category"] for record in metadata["records"]} == {
        "equal_contributor",
        "manuscript_writer",
        "paper_input",
        "corresponding_author",
    }

    report = manifest["runtime"]["history"]["paper_author_metadata_report"]
    assert validate_paper_author_metadata_report(report)["ok"] is True
    assert report["claim_ready"] is True
    assert report["claim_readiness"][
        "alphaevolve_publication_author_metadata_parity"
    ] is True
    assert report["source_pages"] == [22, 23]
    assert report["records_with_contact_policy"] == 4


def test_paper_author_metadata_report_marks_missing_metadata_boundary():
    tmpdir = tempfile.mkdtemp()

    evolve(_problem(), Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["paper_author_metadata_report"]
    assert report["metadata_status"] == "not_provided"
    assert report["claim_ready"] is False
    assert report["validation"]["ok"] is True
    assert report["claim_readiness"][
        "alphaevolve_publication_author_metadata_parity"
    ] is False
    assert "paper_authors_yaml_in_problem_fixture" in (
        report["claim_readiness"]["remaining_gap"]
    )
    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["claim_readiness"]["alphaevolve_publication_author_metadata_parity"] = True
    validation = validate_paper_author_metadata_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_mismatch",
        "publication_author_parity_mismatch",
    }


def test_direct_paper_author_metadata_rejects_secret_like_text_before_manifest():
    problem = _problem()
    problem.paper_author_metadata = {
        "records": [
            {
                "record_id": "author-secret",
                "contributor_label": (
                    "OPENAI_API_KEY=sk-123456789012345678901234567890123456789012345678"
                ),
                "role_category": "equal_contributor",
                "scope_type": "publication",
                "scope_label": "title page",
                "source_page": 1,
                "source_section": "Title page",
            }
        ]
    }
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(
        StrictJsonlError,
        match=(
            "paper_author_metadata\\.records\\[0\\]\\.contributor_label "
            "must not contain secret-like text"
        ),
    ):
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_loaded_title_page_metadata_reaches_manifest_and_report():
    problem_dir = Path(tempfile.mkdtemp())
    (problem_dir / "task_description.txt").write_text("title page task", encoding="utf-8")
    (problem_dir / "metrics.yaml").write_text(
        "metrics:\n"
        "  - name: score\n"
        "    primary: true\n"
        "    bounds: [0.0, 1.0]\n",
        encoding="utf-8",
    )
    (problem_dir / "validate.py").write_text(
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    seed_dir = problem_dir / "initial_programs"
    seed_dir.mkdir()
    (seed_dir / "seed.py").write_text("x = 1\n", encoding="utf-8")
    (problem_dir / "title_page.yaml").write_text(
        "affiliation:\n"
        "  organization: Google DeepMind\n"
        "  marker_id: affiliation-1\n"
        "  source_page: 1\n"
        "  source_section: AlphaEvolve title page\n"
        "footnotes:\n"
        "  - marker_id: affiliation-1\n"
        "    kind: affiliation\n"
        "    text: See Acknowledgments and Author information section.\n"
        "    source_page: 1\n"
        "    source_section: Title page footnotes\n"
        "  - marker_id: star\n"
        "    kind: equal_contribution\n"
        "    text: Equal contributions.\n"
        "    source_page: 1\n"
        "    source_section: Title page footnotes\n"
        "author_markers:\n"
        "  - author_label: equal contributor group\n"
        "    marker_id: star\n"
        "    source_page: 1\n"
        "rights_linkage:\n"
        "  status: source_rights_record_referenced\n"
        "  record_id: alphaevolve-2025-rights\n"
        "  source_page: 1\n"
        "privacy_policy:\n"
        "  redaction: public_source_text\n"
        "review:\n"
        "  status: title_page_metadata_reviewed\n"
        "  reviewer_labels:\n"
        "    - title page reviewer\n",
        encoding="utf-8",
    )
    problem = load_problem(problem_dir)
    tmpdir = tempfile.mkdtemp()

    evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    metadata = manifest["problem"]["title_page_metadata"]
    assert metadata["schema"] == "libreevolve.title_page_metadata.v1"
    assert metadata["status"] == "provided"
    assert metadata["affiliation"]["organization"] == "Google DeepMind"
    report = manifest["runtime"]["history"]["title_page_affiliation_report"]
    assert report["schema"] == "libreevolve.title_page_affiliation_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_title_page_affiliation_report(report)["ok"] is True
    assert report["claim_ready"] is True
    assert report["affiliation_organization"] == "Google DeepMind"
    assert report["footnote_kind_counts"] == {
        "affiliation": 1,
        "equal_contribution": 1,
    }
    assert report["claim_readiness"][
        "alphaevolve_title_page_affiliation_parity"
    ] is True


def test_matrix_example_title_page_fixture_is_claim_ready():
    repo_root = Path(__file__).resolve().parents[2]
    problem = load_problem(
        repo_root
        / "libreevolve"
        / "problems"
        / "examples"
        / "matrix_multiplication"
    )
    tmpdir = tempfile.mkdtemp()

    evolve(
        problem,
        Config(max_generations=0, log_dir=tmpdir, problem_name="matrix_title_page"),
    )

    manifest = json.loads(
        (Path(tmpdir) / "matrix_title_page" / "manifest.json").read_text()
    )
    metadata = manifest["problem"]["title_page_metadata"]
    assert metadata["schema"] == "libreevolve.title_page_metadata.v1"
    assert metadata["status"] == "provided"
    assert metadata["affiliation"]["organization"] == "Google DeepMind"
    assert metadata["rights_linkage"]["record_id"] == "2506.13131"

    report = manifest["runtime"]["history"]["title_page_affiliation_report"]
    assert validate_title_page_affiliation_report(report)["ok"] is True
    assert report["claim_ready"] is True
    assert report["affiliation_organization"] == "Google DeepMind"
    assert report["footnote_kind_counts"] == {
        "affiliation": 1,
        "equal_contribution": 1,
    }
    assert report["author_marker_mapping_count"] == 1
    assert report["rights_linkage_status"] == "source_rights_record_referenced"
    assert report["source_pages"] == [1]
    assert report["claim_readiness"][
        "alphaevolve_title_page_affiliation_parity"
    ] is True


def test_title_page_affiliation_report_marks_missing_metadata_boundary():
    tmpdir = tempfile.mkdtemp()

    evolve(_problem(), Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["title_page_affiliation_report"]
    assert report["metadata_status"] == "not_provided"
    assert report["claim_ready"] is False
    assert report["validation"]["ok"] is True
    assert report["claim_readiness"][
        "alphaevolve_title_page_affiliation_parity"
    ] is False
    assert "title_page_yaml_in_problem_fixture" in (
        report["claim_readiness"]["remaining_gap"]
    )
    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["claim_readiness"]["alphaevolve_title_page_affiliation_parity"] = True
    validation = validate_title_page_affiliation_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_mismatch",
        "title_page_affiliation_parity_mismatch",
    }


def test_direct_title_page_metadata_rejects_secret_like_text_before_manifest():
    problem = _problem()
    problem.title_page_metadata = {
        "affiliation": {
            "organization": (
                "OPENAI_API_KEY=sk-123456789012345678901234567890123456789012345678"
            ),
            "marker_id": "affiliation-1",
            "source_page": 1,
            "source_section": "Title page",
        }
    }
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(
        StrictJsonlError,
        match=(
            "title_page_metadata\\.affiliation\\.organization "
            "must not contain secret-like text"
        ),
    ):
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_loaded_system_contribution_metadata_reaches_manifest_and_report():
    problem_dir = Path(tempfile.mkdtemp())
    (problem_dir / "task_description.txt").write_text(
        "system contribution task",
        encoding="utf-8",
    )
    (problem_dir / "metrics.yaml").write_text(
        "metrics:\n"
        "  - name: score\n"
        "    primary: true\n"
        "    bounds: [0.0, 1.0]\n",
        encoding="utf-8",
    )
    (problem_dir / "validate.py").write_text(
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    seed_dir = problem_dir / "initial_programs"
    seed_dir.mkdir()
    (seed_dir / "seed.py").write_text("x = 1\n", encoding="utf-8")
    records = []
    phases = [
        ("initial-design", "initial_design", 22),
        ("vision-scoping", "project_vision_scoping", 22),
        ("first-benchmark", "first_benchmark_iteration", 22),
        ("final-system", "final_system", 22),
        ("infrastructure", "infrastructure", 22),
        ("code-review", "code_review", 23),
        ("coordination", "team_coordination", 23),
        ("supervision", "supervision", 23),
    ]
    for record_id, phase, page in phases:
        records.append(
            "  - record_id: " + record_id + "\n"
            "    contributor_label: source contribution group " + record_id + "\n"
            "    phase: " + phase + "\n"
            "    role_label: AlphaEvolve " + phase.replace("_", " ") + "\n"
            "    artifacts:\n"
            "      - contribution artifact " + record_id + "\n"
            "    source_page: " + str(page) + "\n"
            "    source_section: AlphaEvolve Contributions\n"
            "    review_scope: Contribution role and source locator reviewed.\n"
        )
    (problem_dir / "system_contributions.yaml").write_text(
        "records:\n"
        + "".join(records)
        + "privacy_policy:\n"
        + "  retention: public_names_allowed\n"
        + "review:\n"
        + "  status: contribution_roles_reviewed\n"
        + "  reviewer_labels:\n"
        + "    - contribution reviewer\n",
        encoding="utf-8",
    )
    problem = load_problem(problem_dir)
    tmpdir = tempfile.mkdtemp()

    evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    metadata = manifest["problem"]["system_contribution_metadata"]
    assert metadata["schema"] == "libreevolve.system_contribution_metadata.v1"
    assert metadata["status"] == "provided"
    assert len(metadata["records"]) == 8
    report = manifest["runtime"]["history"][
        "system_contribution_provenance_report"
    ]
    assert report["schema"] == (
        "libreevolve.system_contribution_provenance_report.v1"
    )
    assert report["validation"]["ok"] is True
    assert validate_system_contribution_provenance_report(report)["ok"] is True
    assert report["claim_ready"] is True
    assert report["source_pages"] == [22, 23]
    assert report["missing_phases"] == []
    assert report["claim_readiness"][
        "alphaevolve_system_contribution_parity"
    ] is True


def test_matrix_example_system_contribution_fixture_is_claim_ready():
    repo_root = Path(__file__).resolve().parents[2]
    problem = load_problem(
        repo_root
        / "libreevolve"
        / "problems"
        / "examples"
        / "matrix_multiplication"
    )
    tmpdir = tempfile.mkdtemp()

    evolve(
        problem,
        Config(max_generations=0, log_dir=tmpdir, problem_name="matrix_system_roles"),
    )

    manifest = json.loads(
        (Path(tmpdir) / "matrix_system_roles" / "manifest.json").read_text()
    )
    metadata = manifest["problem"]["system_contribution_metadata"]
    assert metadata["schema"] == "libreevolve.system_contribution_metadata.v1"
    assert metadata["status"] == "provided"
    assert len(metadata["records"]) == 8

    report = manifest["runtime"]["history"][
        "system_contribution_provenance_report"
    ]
    assert validate_system_contribution_provenance_report(report)["ok"] is True
    assert report["claim_ready"] is True
    assert report["missing_phases"] == []
    assert report["source_pages"] == [22, 23]
    assert report["artifact_link_count"] == 8
    assert report["review_scope_count"] == 8
    assert report["claim_readiness"][
        "alphaevolve_system_contribution_parity"
    ] is True


def test_system_contribution_report_marks_missing_metadata_boundary():
    tmpdir = tempfile.mkdtemp()

    evolve(_problem(), Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"][
        "system_contribution_provenance_report"
    ]
    assert report["metadata_status"] == "not_provided"
    assert report["claim_ready"] is False
    assert report["validation"]["ok"] is True
    assert "system_contributions_yaml_in_problem_fixture" in (
        report["claim_readiness"]["remaining_gap"]
    )
    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["claim_readiness"]["alphaevolve_system_contribution_parity"] = True
    validation = validate_system_contribution_provenance_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "claim_ready_mismatch",
        "system_contribution_parity_mismatch",
    }


def test_direct_system_contribution_metadata_rejects_secret_like_text_before_manifest():
    problem = _problem()
    problem.system_contribution_metadata = {
        "records": [
            {
                "record_id": "initial-design",
                "contributor_label": (
                    "OPENAI_API_KEY=sk-123456789012345678901234567890123456789012345678"
                ),
                "phase": "initial_design",
                "role_label": "Initial system design",
                "artifacts": ["core system"],
                "source_page": 22,
                "source_section": "Contributions",
                "review_scope": "Contribution role reviewed.",
            }
        ]
    }
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(
        StrictJsonlError,
        match=(
            "system_contribution_metadata\\.records\\[0\\]\\.contributor_label "
            "must not contain secret-like text"
        ),
    ):
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_invalid_seed_failure_memory_is_rendered_for_first_mutation_prompt():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c):\n"
        "    return {'score': 1.0 if 'valid_seed' in c or 'x=2' in c else -1.0,"
        " 'is_valid': ('valid_seed' in c or 'x=2' in c)}\n",
        encoding="utf-8",
    )
    problem = Problem(
        name="t",
        task_description="avoid bad seeds",
        metrics=[{"name": "score", "primary": True, "bounds": [-1.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(-1.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["bad_seed = True", "valid_seed = True\nx=1"],
        problem_dir=d,
    )
    llm = _llm("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE")

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(problem, Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    first_prompt = llm.generate.call_args_list[0].args[0]
    assert "RECENTLY FAILED" in first_prompt
    assert "error=domain_invalid" in first_prompt
    assert "changed_files=main.py" in first_prompt
    failures = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failures[0]["record_type"] == "seed"
    assert failures[0]["admission_reason"] == "invalid_evaluation"


def test_exhausted_mutation_call_writes_completed_runtime_manifest_and_failure_history():
    tmpdir = tempfile.mkdtemp()

    with patch("libreevolve.core.loop.build_llm", return_value=_FailingLLM()):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    runtime = manifest["runtime"]
    assert runtime["status"] == "completed"
    assert runtime["stop_reason"] == "completed"
    wall_clock = runtime["wall_clock"]
    assert wall_clock["final_status"] == "completed"
    assert wall_clock["runtime_seconds_source"] == "consumed.runtime_seconds"
    assert wall_clock["resume_segments"][0]["finished_at"] == wall_clock["finished_at"]
    _parse_utc_timestamp(wall_clock["started_at"])
    _parse_utc_timestamp(wall_clock["finished_at"])
    assert "abort" not in runtime
    assert runtime["history"]["programs_logged"] == 1
    assert runtime["history"]["history_partially_written"] is True
    assert runtime["artifacts"]["history.jsonl"]["exists"] is True
    assert runtime["artifacts"]["failure_history.jsonl"]["exists"] is True
    assert runtime["consumed"]["seed_evaluations"] == 1
    assert runtime["consumed"]["candidate_evaluations"] == 0
    assert runtime["consumed"]["llm_calls"] == 1

    failures = [
        json.loads(line)
        for line in (run_dir / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failures[0]["error"] == "llm_mutation_failed"
    assert failures[0]["diff_error"] == "llm_mutation_failed"
    assert "provider down" in failures[0]["mutation_text"]


def test_aborted_plugin_hook_writes_runtime_manifest_before_reraising():
    tmpdir = tempfile.mkdtemp()

    class FailingPlugin:
        def on_generation_start(self, g, db):
            raise RuntimeError("plugin broke")
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score): return score

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(RuntimeError, match="plugin broke"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
                plugins=[FailingPlugin()],
            )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    assert runtime["status"] == "aborted"
    assert runtime["abort"]["phase"] == "generation:0:plugin_on_generation_start"
    assert runtime["abort"]["role"] == "plugin"
    plugin_failure = runtime["abort"]["plugin_failure"]
    assert plugin_failure["plugin"] == "FailingPlugin"
    assert plugin_failure["module"] == FailingPlugin.__module__
    assert plugin_failure["index"] == 0
    assert plugin_failure["hook"] == "on_generation_start"
    assert plugin_failure["policy"] == "fatal_run_abort"
    assert plugin_failure["continued"] is False
    assert plugin_failure["exception_type"] == "RuntimeError"
    assert plugin_failure["message"] == "plugin broke"
    assert plugin_failure["generation"] == 1
    assert plugin_failure["phase"] == "generation:0:plugin_on_generation_start"
    assert "parent_id" in plugin_failure
    assert runtime["plugin_failures"] == [plugin_failure]
    assert runtime["history"]["programs_logged"] == 1
    assert runtime["consumed"]["generations_started"] == 1
    assert runtime["consumed"]["generations_completed"] == 0


def test_aborted_provider_message_is_redacted_in_manifest():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj-providerSecret1234567890"

    with patch(
        "libreevolve.core.loop.build_llm",
        return_value=_FailingLLM(f"provider Authorization: Bearer {secret}"),
    ):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    run_dir = Path(tmpdir) / "t"
    manifest_text = (run_dir / "manifest.json").read_text()
    failure_text = (run_dir / "failure_history.jsonl").read_text()
    runtime = json.loads(manifest_text)["runtime"]
    assert runtime["status"] == "completed"
    assert secret not in manifest_text
    assert secret not in failure_text
    assert "Bearer [REDACTED]" in failure_text
    assert "llm_mutation_failed" in failure_text


def test_aborted_plugin_message_is_redacted_and_bounded_in_manifest():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj-pluginSecret1234567890"

    class FailingPlugin:
        def on_generation_start(self, g, db):
            raise RuntimeError("plugin api_key=" + secret + " " + ("x" * 3000))
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score): return score

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(RuntimeError):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
                plugins=[FailingPlugin()],
            )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    abort = runtime["abort"]
    assert secret not in abort["message"]
    assert "api_key=[REDACTED]" in abort["message"]
    assert abort["message_truncated"] is True
    assert abort["message"].endswith("...<truncated>")
    assert len(abort["message"]) <= 2048
    assert abort["message_chars"] > len(abort["message"])
    assert abort["role"] == "plugin"
    plugin_failure = abort["plugin_failure"]
    assert secret not in plugin_failure["message"]
    assert "api_key=[REDACTED]" in plugin_failure["message"]
    assert plugin_failure["message_truncated"] is True
    assert plugin_failure["message"].endswith("...<truncated>")
    assert plugin_failure["hook"] == "on_generation_start"
    assert plugin_failure["continued"] is False


def test_aborted_plugin_context_hook_records_plugin_failure_metadata():
    tmpdir = tempfile.mkdtemp()

    class ContextFailingPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations):
            raise RuntimeError("plugin context failed")
        def on_evaluated(self, program, score): return score

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(RuntimeError, match="plugin context failed"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
                plugins=[ContextFailingPlugin()],
            )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    plugin_failure = runtime["abort"]["plugin_failure"]
    assert runtime["abort"]["phase"] == "generation:0:plugin_context"
    assert runtime["abort"]["role"] == "plugin"
    assert plugin_failure["plugin"] == "ContextFailingPlugin"
    assert plugin_failure["hook"] == "build_extra_context"
    assert plugin_failure["exception_type"] == "RuntimeError"
    assert plugin_failure["message"] == "plugin context failed"
    assert plugin_failure["generation"] == 1
    assert "parent_id" in plugin_failure
    assert "candidate_id" not in plugin_failure
    assert runtime["consumed"]["candidate_evaluations"] == 0


def test_aborted_prompt_context_metadata_hook_records_plugin_failure_metadata():
    tmpdir = tempfile.mkdtemp()

    class MetadataFailingPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def prompt_context_metadata(self):
            raise RuntimeError("metadata failed")
        def on_evaluated(self, program, score): return score

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(RuntimeError, match="metadata failed"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
                plugins=[MetadataFailingPlugin()],
            )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    plugin_failure = runtime["abort"]["plugin_failure"]
    assert plugin_failure["hook"] == "prompt_context_metadata"
    assert plugin_failure["plugin"] == "MetadataFailingPlugin"
    assert plugin_failure["message"] == "metadata failed"
    assert plugin_failure["phase"] == "generation:0:plugin_context"


def test_aborted_on_evaluated_hook_records_plugin_failure_metadata():
    tmpdir = tempfile.mkdtemp()

    class EvaluatedFailingPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            raise RuntimeError("score hook failed")

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(RuntimeError, match="score hook failed"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
                plugins=[EvaluatedFailingPlugin()],
            )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    plugin_failure = runtime["abort"]["plugin_failure"]
    assert runtime["abort"]["phase"] == "generation:0:plugin_on_evaluated"
    assert plugin_failure["hook"] == "on_evaluated"
    assert plugin_failure["plugin"] == "EvaluatedFailingPlugin"
    assert plugin_failure["message"] == "score hook failed"
    assert plugin_failure["generation"] == 1
    assert "parent_id" in plugin_failure
    assert "candidate_id" in plugin_failure
    assert runtime["consumed"]["candidate_evaluations"] == 1


def test_aborted_generation_end_hook_records_plugin_failure_metadata():
    tmpdir = tempfile.mkdtemp()

    class EndFailingPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b):
            raise RuntimeError("end hook failed")
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score): return score

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(RuntimeError, match="end hook failed"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
                plugins=[EndFailingPlugin()],
            )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    plugin_failure = runtime["abort"]["plugin_failure"]
    assert runtime["abort"]["phase"] == "generation:0:plugin_on_generation_end"
    assert plugin_failure["hook"] == "on_generation_end"
    assert plugin_failure["plugin"] == "EndFailingPlugin"
    assert plugin_failure["generation"] == 1
    assert plugin_failure["continued"] is False
    assert runtime["consumed"]["generations_completed"] == 0


def test_aborted_evaluator_message_is_redacted_in_manifest():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj-evaluatorSecret1234567890"

    with patch(
        "libreevolve.core.loop.CascadeEvaluator.evaluate",
        side_effect=RuntimeError(f"validator token={secret}"),
    ):
        with pytest.raises(RuntimeError):
            evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    abort = runtime["abort"]
    assert secret not in abort["message"]
    assert "token=[REDACTED]" in abort["message"]
    assert abort["phase"] == "seed_evaluation"
    assert abort["role"] == "evaluation"


def test_unstringifiable_abort_exception_still_writes_strict_manifest():
    tmpdir = tempfile.mkdtemp()

    class BrokenStrError(Exception):
        def __str__(self):
            raise RuntimeError("format failure")

    class FailingPlugin:
        def on_generation_start(self, g, db):
            raise BrokenStrError()
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score): return score

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(BrokenStrError):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
                plugins=[FailingPlugin()],
            )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    abort = runtime["abort"]
    assert abort["message"] == "<exception message unavailable; __str__ raised RuntimeError>"
    assert abort["message_unavailable"] is True
    assert abort["message_truncated"] is False
    assert abort["role"] == "plugin"


def test_runtime_artifact_pointer_reports_regular_file_without_following_links(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    history = run_dir / "history.jsonl"
    history.write_text("{}\n", encoding="utf-8")

    record = _runtime_artifact_pointers(run_dir)["history.jsonl"]

    assert record["exists"] is True
    assert record["present"] is True
    assert record["is_symlink"] is False
    assert record["is_junction"] is False
    assert record["broken_link"] is False
    assert record["kind"] == "file"
    assert record["bytes"] == history.stat().st_size
    assert record["sha256"] == hashlib.sha256(history.read_bytes()).hexdigest()
    assert record["hash_scope"] == "file_bytes"


def test_runtime_artifact_pointer_reports_directory_tree_hash(tmp_path):
    run_dir = tmp_path / "run"
    artifacts = run_dir / "plugin_artifacts"
    nested = artifacts / "plugin"
    nested.mkdir(parents=True)
    (nested / "data.jsonl").write_text('{"value": 1}\n', encoding="utf-8")

    record = _runtime_artifact_pointers(run_dir)["plugin_artifacts"]

    assert record["exists"] is True
    assert record["present"] is True
    assert record["is_symlink"] is False
    assert record["is_junction"] is False
    assert record["kind"] == "directory"
    assert record["tree_hash_status"] == "ok"
    assert len(record["tree_hash"]) == 64
    assert record["tree_hash_scope"] == "relative_file_paths_and_sha256"
    assert record["file_count"] == 1
    assert record["skipped_link_count"] == 0


def test_runtime_artifact_pointer_reports_file_symlink_without_target_size(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    outside = tmp_path / "outside-history.jsonl"
    outside.write_text("outside\n", encoding="utf-8")
    link = run_dir / "history.jsonl"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"file symlink creation is unavailable: {exc}")

    record = _runtime_artifact_pointers(run_dir)["history.jsonl"]

    assert record["exists"] is True
    assert record["present"] is True
    assert record["is_symlink"] is True
    assert record["broken_link"] is False
    assert record["kind"] == "link"
    assert "bytes" not in record
    assert record["target_within_run_dir"] is False
    assert record["target_scope"] == "outside_run_dir"
    assert record["target_path_redacted"] is True
    assert record["target_resolved_hash"]
    assert record["link_target_hash"]


def test_runtime_artifact_pointer_reports_broken_symlink(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    link = run_dir / "history.jsonl"
    try:
        link.symlink_to(tmp_path / "missing-history.jsonl")
    except OSError as exc:
        pytest.skip(f"file symlink creation is unavailable: {exc}")

    record = _runtime_artifact_pointers(run_dir)["history.jsonl"]

    assert record["exists"] is False
    assert record["present"] is True
    assert record["is_symlink"] is True
    assert record["broken_link"] is True
    assert record["kind"] == "link"
    assert record["target_scope"] == "unresolved"
    assert record["target_within_run_dir"] is None
    assert any(error["operation"] == "resolve" for error in record["inspection_errors"])


def test_runtime_artifact_pointer_reports_windows_junction_without_directory_kind(tmp_path):
    if os.name != "nt":
        pytest.skip("Windows junction test")
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    outside = tmp_path / "outside-plugin-artifacts"
    outside.mkdir()
    junction = run_dir / "plugin_artifacts"
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(f"junction creation is unavailable: {result.stderr or result.stdout}")

    record = _runtime_artifact_pointers(run_dir)["plugin_artifacts"]

    assert record["exists"] is True
    assert record["present"] is True
    assert record["is_junction"] is True
    assert record["kind"] == "link"
    assert record["target_scope"] == "outside_run_dir"
    assert record["target_within_run_dir"] is False
    assert "bytes" not in record


@pytest.mark.parametrize(
    "artifact_name",
    [
        "history.jsonl",
        "archive_events.jsonl",
        "failure_history_invalid.jsonl",
        "evaluator_artifacts",
        "plugin_artifacts",
    ],
)
def test_runtime_artifact_pointer_stat_failures_are_redacted(monkeypatch, tmp_path, artifact_name):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    artifact = run_dir / artifact_name
    if artifact_name.endswith(".jsonl"):
        artifact.write_text("{}\n", encoding="utf-8")
    else:
        artifact.mkdir()
    secret = "sk-proj_runtimeartifact_secret_1234567890"
    path_type = type(run_dir)
    original_lstat = path_type.lstat

    def fake_lstat(self):
        if self == artifact:
            raise PermissionError(f"cannot stat api_key={secret}")
        return original_lstat(self)

    monkeypatch.setattr(path_type, "lstat", fake_lstat)

    record = _runtime_artifact_pointers(run_dir)[artifact_name]

    encoded = json.dumps(record)
    assert secret not in encoded
    assert "api_key=[REDACTED]" in encoded
    assert record["exists"] is None
    assert record["present"] is None
    assert record["inspection_errors"][0]["operation"] == "lstat"


def test_invalid_plugin_artifact_metadata_value_aborts_before_manifest_write():
    tmpdir = tempfile.mkdtemp()

    class BadArtifactPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score): return score
        def run_artifacts_metadata(self):
            return {"bad": object()}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(ValueError, match="metadata value must be JSON-safe"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
                plugins=[BadArtifactPlugin()],
            )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    runtime = manifest["runtime"]
    assert runtime["status"] == "aborted"
    assert runtime["abort"]["phase"] == "normal_finalization"
    assert runtime["abort"]["role"] == "manifest"
    assert runtime["abort"]["exception_type"] == "ValueError"
    plugin_failure = runtime["abort"]["plugin_failure"]
    assert plugin_failure["plugin"] == "BadArtifactPlugin"
    assert plugin_failure["hook"] == "run_artifacts_metadata"
    assert plugin_failure["policy"] == "fatal_run_abort"
    assert plugin_failure["continued"] is False
    assert plugin_failure["exception_type"] == "ValueError"
    assert "metadata value must be JSON-safe" in plugin_failure["message"]
    assert runtime["plugin_failures"] == [plugin_failure]
    assert not (run_dir / "manifest_invalid.jsonl").exists()


def test_rejects_plugin_artifact_metadata_with_unsafe_label():
    tmpdir = tempfile.mkdtemp()

    class BadArtifactLabelPlugin:
        def run_artifacts_metadata(self):
            return {"safe": [{"bad\u202e": "value"}]}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(ValueError, match="display-safe metadata label"):
            evolve(
                _problem(),
                Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
                plugins=[BadArtifactLabelPlugin()],
            )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    assert runtime["status"] == "aborted"
    assert runtime["abort"]["phase"] == "normal_finalization"
    assert runtime["abort"]["role"] == "manifest"
    assert runtime["abort"]["exception_type"] == "ValueError"


def test_rejects_plugin_artifact_metadata_with_non_string_key():
    tmpdir = tempfile.mkdtemp()

    class BadArtifactKeyPlugin:
        def run_artifacts_metadata(self):
            return {1: "value"}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(ValueError, match="keys must be strings"):
            evolve(
                _problem(),
                Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
                plugins=[BadArtifactKeyPlugin()],
            )


def test_rejects_plugin_artifact_metadata_with_unsafe_value():
    tmpdir = tempfile.mkdtemp()

    class BadArtifactValuePlugin:
        def run_artifacts_metadata(self):
            return {"safe": ["value\u200d"]}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(ValueError, match="display-safe metadata value"):
            evolve(
                _problem(),
                Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
                plugins=[BadArtifactValuePlugin()],
            )


def test_rejects_plugin_artifact_metadata_with_oversized_aggregate_json():
    tmpdir = tempfile.mkdtemp()

    class OversizedArtifactMetadataPlugin:
        def run_artifacts_metadata(self):
            return {"items": ["x" * 4000] * 30}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(ValueError, match="metadata JSON exceeds"):
            evolve(
                _problem(),
                Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
                plugins=[OversizedArtifactMetadataPlugin()],
            )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    assert runtime["status"] == "aborted"
    assert runtime["abort"]["phase"] == "normal_finalization"
    assert runtime["abort"]["plugin_failure"]["hook"] == "run_artifacts_metadata"


def test_plugin_artifact_metadata_redacts_secret_values():
    tmpdir = tempfile.mkdtemp()

    class SecretArtifactValuePlugin:
        def run_artifacts_metadata(self):
            return {"note": "api_key=sk-proj_secretvalue1234567890"}  # pragma: allowlist secret

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
            plugins=[SecretArtifactValuePlugin()],
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["runtime"]["plugin_artifacts"] == [
        {
            "plugin": "SecretArtifactValuePlugin",
            "module": SecretArtifactValuePlugin.__module__,
            "class": f"{SecretArtifactValuePlugin.__module__}.{SecretArtifactValuePlugin.__qualname__}",
            "index": 0,
            "instance_id": f"plugin:0:{SecretArtifactValuePlugin.__module__}.{SecretArtifactValuePlugin.__qualname__}",
            "version": {"status": "missing"},
            "metadata": {"note": "api_key=[REDACTED]"},
        }
    ]


def test_accepts_plugin_artifact_metadata_with_ordinary_unicode_label():
    tmpdir = tempfile.mkdtemp()

    class UnicodeArtifactLabelPlugin:
        def run_artifacts_metadata(self):
            return {"caf\u00e9": "ok"}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
            plugins=[UnicodeArtifactLabelPlugin()],
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["runtime"]["plugin_artifacts"] == [
        {
            "plugin": "UnicodeArtifactLabelPlugin",
            "module": UnicodeArtifactLabelPlugin.__module__,
            "class": f"{UnicodeArtifactLabelPlugin.__module__}.{UnicodeArtifactLabelPlugin.__qualname__}",
            "index": 0,
            "instance_id": f"plugin:0:{UnicodeArtifactLabelPlugin.__module__}.{UnicodeArtifactLabelPlugin.__qualname__}",
            "version": {"status": "missing"},
            "metadata": {"caf\u00e9": "ok"},
        }
    ]


def test_plugin_artifact_metadata_uses_runtime_plugin_identity_not_spoofed_metadata():
    tmpdir = tempfile.mkdtemp()

    class SpoofArtifactPlugin:
        def run_artifacts_metadata(self):
            return {"plugin": "TrustedPlugin", "path": "external.jsonl", "count": 1}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
            plugins=[SpoofArtifactPlugin()],
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    artifact = manifest["runtime"]["plugin_artifacts"][0]
    assert artifact["plugin"] == "SpoofArtifactPlugin"
    assert artifact["module"] == SpoofArtifactPlugin.__module__
    assert artifact["class"] == f"{SpoofArtifactPlugin.__module__}.{SpoofArtifactPlugin.__qualname__}"
    assert artifact["index"] == 0
    assert artifact["instance_id"] == f"plugin:0:{SpoofArtifactPlugin.__module__}.{SpoofArtifactPlugin.__qualname__}"
    assert artifact["metadata"]["plugin"] == "TrustedPlugin"
    assert artifact["metadata"]["path"] == "external.jsonl"


@pytest.mark.parametrize("metadata", [[{"path": "x"}], "artifact", 1, True])
def test_rejects_non_mapping_plugin_artifact_metadata_returns(metadata):
    tmpdir = tempfile.mkdtemp()

    class BadShapeArtifactPlugin:
        def run_artifacts_metadata(self):
            return metadata

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(ValueError, match="run_artifacts_metadata must return a mapping"):
            evolve(
                _problem(),
                Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
                plugins=[BadShapeArtifactPlugin()],
            )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    assert runtime["status"] == "aborted"
    assert runtime["abort"]["role"] == "manifest"
    assert runtime["abort"]["plugin_failure"]["hook"] == "run_artifacts_metadata"
    assert runtime["abort"]["plugin_failure"]["plugin"] == "BadShapeArtifactPlugin"
    assert runtime["plugin_artifact_failures"][0]["plugin"] == "BadShapeArtifactPlugin"
    assert "run_artifacts_metadata must return a mapping" in runtime[
        "plugin_artifact_failures"
    ][0]["message"]


@pytest.mark.parametrize("metadata", [None, {}])
def test_empty_plugin_artifact_metadata_returns_are_accepted(metadata):
    tmpdir = tempfile.mkdtemp()

    class EmptyArtifactPlugin:
        def run_artifacts_metadata(self):
            return metadata

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=0, log_dir=tmpdir, problem_name="t"),
            plugins=[EmptyArtifactPlugin()],
        )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    assert runtime["status"] == "completed"
    assert "plugin_artifacts" not in runtime
    assert "plugin_artifact_failures" not in runtime


def test_aborted_run_preserves_valid_plugin_artifact_metadata_after_hook_failure(tmp_path):
    artifact_root = tmp_path / "t" / "plugin_artifacts" / "proof"

    class ArtifactThenFailPlugin:
        def on_generation_start(self, g, db):
            artifact_root.mkdir(parents=True)
            (artifact_root / "proof.txt").write_text("proof", encoding="utf-8")
            raise RuntimeError("plugin abort after artifact")
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score): return score
        def run_artifacts_metadata(self):
            return {"path": str(artifact_root / "proof.txt"), "count": 1}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(RuntimeError, match="plugin abort after artifact"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=str(tmp_path), problem_name="t"),
                plugins=[ArtifactThenFailPlugin()],
            )

    runtime = json.loads((tmp_path / "t" / "manifest.json").read_text())["runtime"]
    artifact = runtime["plugin_artifacts"][0]
    assert runtime["status"] == "aborted"
    assert runtime["abort"]["plugin_failure"]["hook"] == "on_generation_start"
    assert artifact["plugin"] == "ArtifactThenFailPlugin"
    assert artifact["metadata"]["count"] == 1
    assert artifact["metadata"]["path"].endswith("proof.txt")
    assert runtime["artifacts"]["plugin_artifacts"]["exists"] is True
    assert "plugin_artifact_failures" not in runtime


def test_aborted_run_records_plugin_artifact_summary_failure_without_hiding_abort(tmp_path):
    class BadArtifactAfterAbortPlugin:
        def on_generation_start(self, g, db):
            raise RuntimeError("original abort")
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score): return score
        def run_artifacts_metadata(self):
            return [{"path": "bad"}]

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(RuntimeError, match="original abort"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=str(tmp_path), problem_name="t"),
                plugins=[BadArtifactAfterAbortPlugin()],
            )

    runtime = json.loads((tmp_path / "t" / "manifest.json").read_text())["runtime"]
    assert runtime["abort"]["message"] == "original abort"
    assert runtime["abort"]["plugin_failure"]["hook"] == "on_generation_start"
    failure = runtime["plugin_artifact_failures"][0]
    assert failure["plugin"] == "BadArtifactAfterAbortPlugin"
    assert failure["hook"] == "run_artifacts_metadata"
    assert failure["policy"] == "recorded_during_abort_finalization"
    assert "run_artifacts_metadata must return a mapping" in failure["message"]


def test_threshold_is_zero():
    assert VALID_THRESHOLD == 0.0

def test_invalid_diff_not_archived():
    tmpdir = tempfile.mkdtemp()
    with patch("libreevolve.core.loop.build_llm", return_value=_llm("no diff here")):
        best = evolve(_problem(), Config(max_generations=1,
                                        log_dir=tmpdir, problem_name="t"))
    assert best.fitness == 1.0  # seed still best
    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    assert child["metadata"]["archive_admission"]["admitted"] is False
    assert child["metadata"]["archive_admission"]["reason"] == "invalid_evaluation"
    failure_records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failure_records[-1]["diff_error"] == "no_diff_blocks"
    assert failure_records[-1]["admission_reason"] == "invalid_evaluation"
    assert failure_records[-1]["archive_admission"]["reason"] == "invalid_evaluation"
    assert child["metadata"]["failure_record"]["admission_reason"] == "invalid_evaluation"
    assert child["metadata"]["failure_record"]["diff_error"] == "no_diff_blocks"
    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    assert runtime["status"] == "completed"
    assert runtime["history"]["programs_logged"] == 2
    assert runtime["artifacts"]["history.jsonl"]["exists"] is True
    assert runtime["artifacts"]["failure_history.jsonl"]["exists"] is True
    assert runtime["best_artifact_export"]["status"] == "completed"
    assert runtime["artifacts"]["best.py"]["exists"] is True


def test_non_text_mutation_payload_is_logged_as_failed_candidate():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        (7, 0),
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        best = evolve(_problem(), Config(max_generations=2, log_dir=tmpdir, problem_name="t"))

    assert best.fitness == 1.0
    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[1]
    assert child["evaluation"]["error"] == "non_text_mutation_payload"
    failure_records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failure_records[-1]["diff_error"] == "non_text_mutation_payload"
    assert failure_records[-1]["mutation_text"] == "7"
    assert failure_records[-1]["mutation_payload_type"] == "int"
    assert failure_records[-1]["mutation_payload_text"] is False
    second_prompt = llm.generate.call_args_list[1].args[0]
    assert "diff_error=non_text_mutation_payload" in second_prompt
    assert "mutation=7" in second_prompt


def test_blank_mutation_payload_is_logged_as_failed_candidate():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("   \n\t", 0),
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        best = evolve(_problem(), Config(max_generations=2, log_dir=tmpdir, problem_name="t"))

    assert best.fitness == 1.0
    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[1]
    assert child["evaluation"]["error"] == "blank_mutation_payload"
    failure_records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failure_records[-1]["diff_error"] == "blank_mutation_payload"
    second_prompt = llm.generate.call_args_list[1].args[0]
    assert "diff_error=blank_mutation_payload" in second_prompt


def test_oversized_mutation_payload_is_logged_as_failed_candidate(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("x" * 9, 0),
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
    ]
    monkeypatch.setattr(
        "libreevolve.core.candidate.DEFAULT_MAX_MUTATION_PAYLOAD_CHARS", 8
    )
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        best = evolve(_problem(), Config(max_generations=2, log_dir=tmpdir, problem_name="t"))

    assert best.fitness == 1.0
    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[1]
    assert child["evaluation"]["error"] == "oversized_mutation_payload"
    failure_records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failure_records[-1]["diff_error"] == "oversized_mutation_payload"
    second_prompt = llm.generate.call_args_list[1].args[0]
    assert "diff_error=oversized_mutation_payload" in second_prompt


def test_workspace_host_path_collision_is_logged_as_failed_candidate():
    tmpdir = tempfile.mkdtemp()
    response = (
        "<<<FILE README.md\nupper\n>>>FILE\n"
        "<<<FILE readme.md\nlower\n>>>FILE"
    )
    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        best = evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_mode="full",
            ),
        )

    assert best.fitness == 1.0
    run_dir = Path(tmpdir) / "t"
    records = [json.loads(line) for line in (run_dir / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert child["evaluation"]["error"] == "unknown_diff_error"
    diff_error = child["evaluation"]["metadata"]["diff_error"]
    assert diff_error["reason"] == "unknown_diff_error"
    assert diff_error["detail"] == "readme.md:host_path_collision"
    assert child["metadata"]["archive_admission"]["reason"] == "invalid_evaluation"
    failure_records = [
        json.loads(line)
        for line in (run_dir / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failure_records[-1]["diff_error"] == "readme.md:host_path_collision"
    assert failure_records[-1]["evaluation"]["error"] == "unknown_diff_error"
    assert failure_records[-1]["admission_reason"] == "invalid_evaluation"
    runtime = json.loads((run_dir / "manifest.json").read_text())["runtime"]
    assert runtime["status"] == "completed"
    assert runtime["artifacts"]["failure_history.jsonl"]["exists"] is True
    assert runtime["best_artifact_export"]["status"] == "completed"
    assert runtime["artifacts"]["best_workspace"]["exists"] is True
    assert not (run_dir / "README.md").exists()
    assert not (run_dir / "readme.md").exists()


def test_failed_mutation_memory_is_rendered_in_next_prompt():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("no diff here", 0),
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(max_generations=2, log_dir=tmpdir, problem_name="t"))

    second_prompt = llm.generate.call_args_list[1].args[0]
    assert "RECENTLY FAILED" in second_prompt
    assert "diff_error=no_diff_blocks" in second_prompt


def test_loop_logs_non_primary_workspace_failure():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "from pathlib import Path\n"
        "def evaluate(code, workspace_path):\n"
        "    helper = Path(workspace_path, 'helper.py').read_text()\n"
        "    return {'score': 1.0 if 'value = 1' in helper else -1.0, "
        "'is_valid': 'value = 1' in helper}\n"
    )
    problem = Problem(
        name="t",
        task_description="keep helper valid",
        metrics=[{"name": "score", "primary": True, "bounds": [-1.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(-1.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["from helper import value\n"],
        problem_dir=d,
        initial_workspaces=[
            CandidateWorkspace(
                files={"main.py": "from helper import value\n", "helper.py": "value = 1\n"},
                primary_file="main.py",
            )
        ],
    )
    llm = _llm("<<<FILE helper.py\nvalue = 0\n>>>FILE")

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(max_generations=1, log_dir=tmpdir, problem_name="t", mutation_mode="full"),
        )

    failure_records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failure_records[-1]["changed_files"] == ["helper.py"]
    assert failure_records[-1]["score"] == -0.1

def test_plugins_called():
    from libreevolve.plugins.base import PluginBase
    calls = []
    class T(PluginBase):
        def on_generation_start(self, g, db): calls.append(("start", g))
        def on_generation_end(self, g, b): calls.append(("end", g))
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(_problem(), Config(max_generations=2,
                                  log_dir=tempfile.mkdtemp(), problem_name="t"),
               plugins=[T()])
    assert ("start", 1) in calls and ("end", 1) in calls


@pytest.mark.parametrize("max_generations", [0, 1])
def test_invalid_direct_plugin_object_is_rejected_before_run_setup(max_generations, tmp_path):
    run_dir = tmp_path / "t"
    run_dir.mkdir()
    history = run_dir / "history.jsonl"
    history.write_text("sentinel\n", encoding="utf-8")
    manifest = run_dir / "manifest.json"
    manifest.write_text('{"sentinel": true}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid plugin instance"):
        evolve(
            _problem(),
            Config(
                max_generations=max_generations,
                log_dir=str(tmp_path),
                problem_name="t",
                run_collision_policy="overwrite",
            ),
            plugins=[object()],
        )

    assert history.read_text(encoding="utf-8") == "sentinel\n"
    assert manifest.read_text(encoding="utf-8") == '{"sentinel": true}\n'


def test_direct_artifact_only_plugin_protocol_is_valid_for_zero_generation_runs(tmp_path):
    class ArtifactOnlyPlugin:
        def run_artifacts_metadata(self):
            return {"status": "ok"}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=0, log_dir=str(tmp_path), problem_name="t"),
            plugins=[ArtifactOnlyPlugin()],
        )

    manifest = json.loads((tmp_path / "t" / "manifest.json").read_text())
    artifact = manifest["runtime"]["plugin_artifacts"][0]
    assert artifact["plugin"] == "ArtifactOnlyPlugin"
    assert artifact["metadata"] == {"status": "ok"}


def test_runtime_plugin_state_resolves_configured_plugins_in_core(tmp_path):
    evolve(
        _problem(),
        Config(
            max_generations=0,
            log_dir=str(tmp_path),
            problem_name="t",
            plugins=["causal"],
        ),
    )

    manifest = json.loads((tmp_path / "t" / "manifest.json").read_text())
    state = manifest["runtime"]["plugin_state"]
    assert manifest["config"]["plugins"] == ["causal"]
    assert manifest["provenance"]["plugins"][0]["plugin"] == "CausalPlugin"
    assert state["configured"] == ["causal"]
    assert state["configured_count"] == 1
    assert state["loaded"][0]["plugin"] == "CausalPlugin"
    assert state["loaded_count"] == 1
    assert state["loaded_specs"][0]["configured_label"] == "causal"
    assert state["loaded_specs"][0]["parameters"]["history_limit"] == 500
    assert state["configured_without_loaded_instances"] == []
    assert state["loaded_without_configured_labels"] == []
    assert state["resolution"] == "configured_and_loaded"
    assert state["core_resolves_config_plugins"] is True


def test_runtime_plugin_state_resolves_configured_plugin_options(tmp_path):
    evolve(
        _problem(),
        Config(
            max_generations=0,
            log_dir=str(tmp_path),
            problem_name="t",
            plugins=[{"name": "causal", "options": {"history_limit": 7}}],
        ),
    )

    manifest = json.loads((tmp_path / "t" / "manifest.json").read_text())
    state = manifest["runtime"]["plugin_state"]
    [spec] = state["loaded_specs"]

    assert manifest["config"]["plugins"] == [
        {"name": "causal", "options": {"history_limit": 7}}
    ]
    assert state["configured"] == ["causal"]
    assert state["core_resolves_config_plugins"] is True
    assert spec["configured_label"] == "causal"
    assert spec["parameters"]["history_limit"] == 7


def test_runtime_plugin_state_reports_direct_loaded_plugins_without_config_labels(tmp_path):
    class ArtifactOnlyPlugin:
        def run_artifacts_metadata(self):
            return {"ok": True}

    evolve(
        _problem(),
        Config(max_generations=0, log_dir=str(tmp_path), problem_name="t"),
        plugins=[ArtifactOnlyPlugin()],
    )

    manifest = json.loads((tmp_path / "t" / "manifest.json").read_text())
    state = manifest["runtime"]["plugin_state"]
    assert manifest["config"]["plugins"] == []
    assert state["configured"] == []
    assert state["loaded_count"] == 1
    assert state["loaded"][0]["class"].endswith("ArtifactOnlyPlugin")
    assert state["configured_without_loaded_instances"] == []
    assert state["loaded_without_configured_labels"] == state["loaded"]
    assert state["resolution"] == "loaded_without_configured_labels"
    assert state["loaded_specs"][0]["status"] == "custom_plugin_signature_recorded"
    assert state["loaded_specs"][0]["schema"] == "libreevolve.plugin_spec.v1"
    assert (
        state["loaded_specs"][0]["parameter_policy"]
        == "custom_constructor_signature_only_no_parameter_values"
    )
    direct_policy = state["loaded_specs"][0]["direct_plugin_policy"]
    assert direct_policy["schema"] == "libreevolve.direct_plugin_policy.v1"
    assert direct_policy["source"] == "direct_instance"
    assert direct_policy["constructor_value_policy"] == (
        "constructor_values_excluded_signature_shape_only"
    )
    assert direct_policy["constructor_values_captured"] is False
    assert direct_policy["constructor_schema_policy"] == (
        "not_available_for_direct_instances"
    )
    assert direct_policy["constructor_signature_policy"] == (
        "names_kinds_required_flags_only"
    )
    assert direct_policy["instance_attribute_policy"] == "not_captured"
    assert direct_policy["package_scope_policy"] == (
        "direct_instance_module_identity_file_hash_and_version_only"
    )
    assert direct_policy["paper_scope_policy"] == "not_available_for_direct_instances"
    assert direct_policy["direct_instance_readiness"] == {
        "schema": "libreevolve.direct_plugin_policy_readiness.v1",
        "direct_instance_constructor_values": False,
        "direct_instance_constructor_schema": False,
        "direct_custom_plugin_registry": False,
        "arbitrary_instance_state_capture": False,
        "remaining_gap": [
            "direct_instance_constructor_values",
            "direct_instance_constructor_schema",
            "direct_custom_plugin_registry",
            "arbitrary_instance_state_capture",
        ],
    }
    assert direct_policy["validation"] == {
        "schema": "libreevolve.direct_plugin_policy_validation.v1",
        "ok": True,
        "issues": [],
    }
    forged_policy = copy.deepcopy(direct_policy)
    forged_policy["direct_instance_readiness"][
        "direct_instance_constructor_values"
    ] = True
    forged_policy["direct_instance_readiness"][
        "direct_instance_constructor_schema"
    ] = True
    forged_policy["direct_instance_readiness"]["direct_custom_plugin_registry"] = True
    forged_validation = validate_direct_plugin_policy(forged_policy)
    forged_codes = {issue["code"] for issue in forged_validation["issues"]}

    assert forged_validation["ok"] is False
    assert "direct_instance_constructor_values_overclaim" in forged_codes
    assert "direct_instance_constructor_schema_overclaim" in forged_codes
    assert "direct_custom_plugin_registry_overclaim" in forged_codes
    signature = state["loaded_specs"][0]["constructor_signature"]
    assert signature == {
        "status": "available",
        "parameter_policy": "names_kinds_required_flags_only",
        "parameter_values_captured": False,
        "parameter_count": 0,
        "parameters": [],
    }
    assert manifest["runtime"]["plugin_artifacts"][0]["metadata"] == {"ok": True}


def test_runtime_plugin_state_records_custom_constructor_signature_without_values(tmp_path):
    secret = "sk-proj_custom_plugin_constructor_secret_1234567890"  # pragma: allowlist secret

    class CustomPlugin:
        def __init__(self, api_key: str, *, mode: str = "default_mode", limit: int = 3):
            self.api_key = api_key
            self.mode = mode
            self.limit = limit

        def run_artifacts_metadata(self):
            return {"ok": True}

    evolve(
        _problem(),
        Config(max_generations=0, log_dir=str(tmp_path), problem_name="t"),
        plugins=[CustomPlugin(secret, mode="secret-mode")],
    )

    manifest_text = (tmp_path / "t" / "manifest.json").read_text()
    assert secret not in manifest_text
    assert "secret-mode" not in manifest_text
    assert "default_mode" not in manifest_text

    manifest = json.loads(manifest_text)
    [spec] = manifest["runtime"]["plugin_state"]["loaded_specs"]
    assert spec["status"] == "custom_plugin_signature_recorded"
    assert spec["parameter_policy"] == (
        "custom_constructor_signature_only_no_parameter_values"
    )
    assert spec["direct_plugin_policy"]["constructor_values_captured"] is False
    assert (
        spec["direct_plugin_policy"]["constructor_value_policy"]
        == "constructor_values_excluded_signature_shape_only"
    )
    assert (
        spec["direct_plugin_policy"]["package_scope_policy"]
        == "direct_instance_module_identity_file_hash_and_version_only"
    )
    assert spec["direct_plugin_policy"]["direct_instance_readiness"][
        "direct_instance_constructor_values"
    ] is False
    assert spec["direct_plugin_policy"]["direct_instance_readiness"][
        "direct_instance_constructor_schema"
    ] is False
    assert spec["direct_plugin_policy"]["direct_instance_readiness"][
        "direct_custom_plugin_registry"
    ] is False
    assert spec["direct_plugin_policy"]["validation"]["ok"] is True
    signature = spec["constructor_signature"]
    assert signature["parameter_values_captured"] is False
    assert signature["parameter_count"] == 3
    assert signature["parameters"] == [
        {
            "name": "api_key",
            "kind": "POSITIONAL_OR_KEYWORD",
            "required": True,
            "default_present": False,
            "annotation_present": True,
        },
        {
            "name": "mode",
            "kind": "KEYWORD_ONLY",
            "required": False,
            "default_present": True,
            "annotation_present": True,
        },
        {
            "name": "limit",
            "kind": "KEYWORD_ONLY",
            "required": False,
            "default_present": True,
            "annotation_present": True,
        },
    ]


def test_runtime_plugin_state_records_entry_point_plugin_provenance(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "libreevolve.plugins.registry.metadata.entry_points",
        lambda: _FakeEntryPoints([_FakeEntryPoint()]),
    )

    evolve(
        _problem(),
        Config(
            max_generations=0,
            log_dir=str(tmp_path),
            problem_name="t",
            plugins=[
                {
                    "name": "entry_point",
                    "options": {
                        "group": "libreevolve.plugins",
                        "name": "sample",
                        "paper_inspiration": "AlphaEvolveExtension",
                        "constructor_options": {
                            "mode": "audit",
                            "limit": 7,
                        },
                    },
                }
            ],
        ),
    )

    manifest = json.loads((tmp_path / "t" / "manifest.json").read_text())
    [spec] = manifest["runtime"]["plugin_state"]["loaded_specs"]

    assert spec["status"] == "entry_point_plugin_signature_recorded"
    assert spec["source"] == "entry_point"
    assert spec["configured_label"] == "entry_point"
    assert spec["parameter_policy"] == (
        "entry_point_constructor_options_from_manifest_safe_config"
    )
    entry_policy = spec["direct_plugin_policy"]
    assert entry_policy["schema"] == "libreevolve.direct_plugin_policy.v1"
    assert entry_policy["source"] == "entry_point"
    assert entry_policy["constructor_value_policy"] == (
        "manifest_safe_or_schema_validated_constructor_options_captured"
    )
    assert entry_policy["constructor_values_captured"] is True
    assert entry_policy["constructor_schema_policy"] == (
        "entry_point_declared_schema_or_manifest_safe_json"
    )
    assert entry_policy["constructor_signature_policy"] == (
        "names_kinds_required_flags_only"
    )
    assert entry_policy["instance_attribute_policy"] == "not_captured"
    assert entry_policy["package_scope_policy"] == (
        "entry_point_distribution_name_version_record_wheel_metadata"
    )
    assert entry_policy["paper_scope_policy"] == (
        "configured_entry_point_paper_inspiration_labels"
    )
    assert entry_policy["direct_instance_readiness"] == {
        "schema": "libreevolve.direct_plugin_policy_readiness.v1",
        "direct_instance_constructor_values": False,
        "direct_instance_constructor_schema": False,
        "direct_custom_plugin_registry": False,
        "arbitrary_instance_state_capture": False,
        "remaining_gap": [
            "direct_instance_constructor_values",
            "direct_instance_constructor_schema",
            "direct_custom_plugin_registry",
            "arbitrary_instance_state_capture",
        ],
    }
    assert entry_policy["validation"] == {
        "schema": "libreevolve.direct_plugin_policy_validation.v1",
        "ok": True,
        "issues": [],
    }
    assert spec["entry_point"] == {
        "schema": "libreevolve.plugin_entry_point.v1",
        "group": "libreevolve.plugins",
        "name": "sample",
        "value": "tests.fake:EntryPointPlugin",
        "paper_inspiration": "AlphaEvolveExtension",
        "constructor_options_captured": True,
        "constructor_option_policy": "manifest_safe_json_values",
        "constructor_options": {
            "mode": "audit",
            "limit": 7,
        },
        "distribution": {
            "status": "available",
            "policy": "entry_point_distribution_name_version_hash_v1",
            "name": "libreevolve-test-plugin",
            "name_sha256": hashlib.sha256(
                b"libreevolve-test-plugin"
            ).hexdigest(),
            "version": "1.2.3",
            "version_sha256": hashlib.sha256(b"1.2.3").hexdigest(),
            "record_metadata": {
                "status": "available",
                "policy": "distribution_record_hash_only_v1",
                "record_sha256": hashlib.sha256(
                    (
                        "tests/fake.py,sha256=abc,123\n"
                        "libreevolve_test_plugin-1.2.3.dist-info/METADATA,,456\n"
                    ).encode("utf-8")
                ).hexdigest(),
                "line_count": 2,
                "bytes": 83,
            },
            "wheel_metadata": {
                "status": "available",
                "policy": "distribution_wheel_bounded_metadata_v1",
                "wheel_sha256": hashlib.sha256(
                    (
                        "Wheel-Version: 1.0\n"
                        "Generator: test-wheel\n"
                        "Root-Is-Purelib: true\n"
                        "Tag: py3-none-any\n"
                        "Tag: py3-none-win_amd64\n"
                    ).encode("utf-8")
                ).hexdigest(),
                "bytes": 105,
                "tag_count": 2,
                "max_retained_tags": 8,
                "retained_tags": [
                    {
                        "value": "py3-none-any",
                        "sha256": hashlib.sha256(
                            b"py3-none-any"
                        ).hexdigest(),
                    },
                    {
                        "value": "py3-none-win_amd64",
                        "sha256": hashlib.sha256(
                            b"py3-none-win_amd64"
                        ).hexdigest(),
                    },
                ],
                "omitted_tag_count": 0,
                "wheel_version_present": True,
                "generator_present": True,
                "root_is_purelib_present": True,
                "wheel_version": {
                    "value": "1.0",
                    "sha256": hashlib.sha256(b"1.0").hexdigest(),
                },
                "generator": {
                    "value": "test-wheel",
                    "sha256": hashlib.sha256(b"test-wheel").hexdigest(),
                },
                "root_is_purelib": {
                    "value": "true",
                    "sha256": hashlib.sha256(b"true").hexdigest(),
                },
            },
        },
        "loaded": True,
    }
    assert spec["constructor_signature"]["parameter_values_captured"] is False
    assert manifest["runtime"]["plugin_artifacts"][0]["metadata"] == {
        "entry_point": True,
        "mode": "audit",
        "limit": 7,
    }


def test_runtime_plugin_state_records_entry_point_constructor_schema(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "libreevolve.plugins.registry.metadata.entry_points",
        lambda: _FakeEntryPoints([_FakeSchemaEntryPoint()]),
    )

    evolve(
        _problem(),
        Config(
            max_generations=0,
            log_dir=str(tmp_path),
            problem_name="t",
            plugins=[
                {
                    "name": "entry_point",
                    "options": {
                        "group": "libreevolve.plugins",
                        "name": "schema_sample",
                        "constructor_options": {
                            "mode": "dry_run",
                            "limit": 2,
                        },
                    },
                }
            ],
        ),
    )

    manifest = json.loads((tmp_path / "t" / "manifest.json").read_text())
    [spec] = manifest["runtime"]["plugin_state"]["loaded_specs"]
    entry_point = spec["entry_point"]

    assert entry_point["constructor_option_policy"] == (
        "declared_constructor_option_schema_v1"
    )
    assert entry_point["constructor_option_schema"] == {
        "mode": {"type": "enum", "values": ["audit", "dry_run"]},
        "limit": {"type": "positive_int"},
    }
    assert entry_point["constructor_options"] == {
        "mode": "dry_run",
        "limit": 2,
    }


def test_runtime_plugin_state_records_builtin_plugin_constructor_specs(tmp_path):
    plugin = TTTRLPlugin(
        train_every=3,
        log_dir=str(tmp_path / "t" / "plugin_artifacts" / "ttt_rl"),
        max_retained_examples=17,
        max_payload_field_chars=101,
        max_payload_total_chars=202,
    )

    evolve(
        _problem(),
        Config(max_generations=0, log_dir=str(tmp_path), problem_name="t"),
        plugins=[plugin],
    )

    manifest = json.loads((tmp_path / "t" / "manifest.json").read_text())
    [spec] = manifest["runtime"]["plugin_state"]["loaded_specs"]

    assert spec["status"] == "ok"
    assert spec["schema"] == "libreevolve.plugin_spec.v1"
    assert spec["plugin"] == "TTTRLPlugin"
    assert spec["module"] == "libreevolve.plugins.ttt_rl"
    assert spec["configured_label"] is None
    assert spec["parameter_policy"] == "validated_builtin_constructor_parameters"
    assert spec["parameters"]["train_every"] == 3
    assert spec["parameters"]["max_retained_examples"] == 17
    assert spec["parameters"]["max_payload_field_chars"] == 101
    assert spec["parameters"]["max_payload_total_chars"] == 202
    assert spec["parameters"]["log_dir"]["path"] == "plugin_artifacts/ttt_rl"
    assert spec["parameters"]["log_dir"]["scope"] == "within_run_dir"
    assert spec["parameters"]["log_dir"]["path_redacted"] is True
    assert len(spec["parameters"]["log_dir"]["path_hash"]) == 64
    assert len(spec["parameters"]["log_dir"]["resolved_path_hash"]) == 64


def test_runtime_plugin_state_records_deep_research_constructor_specs(tmp_path):
    plugin = DeepResearchPlugin(
        search_fn=lambda query: "",
        search_every=4,
        max_events=12,
        cache_dir=tmp_path / "t" / "plugin_artifacts" / "deep_research",
        cache_mode="offline",
        retrieval_body_retention_mode="hash_only",
        source_ranking_policy="query_overlap_score_desc_v1",
    )

    evolve(
        _problem(),
        Config(
            max_generations=0,
            log_dir=str(tmp_path),
            problem_name="t",
            plugins=["deep_research"],
        ),
        plugins=[plugin],
    )

    manifest = json.loads((tmp_path / "t" / "manifest.json").read_text())
    [spec] = manifest["runtime"]["plugin_state"]["loaded_specs"]

    assert spec["status"] == "ok"
    assert spec["plugin"] == "DeepResearchPlugin"
    assert spec["configured_label"] == "deep_research"
    assert spec["parameters"]["provider"] == "custom"
    assert spec["parameters"]["search_every"] == 4
    assert spec["parameters"]["max_events"] == 12
    assert spec["parameters"]["cache_mode"] == "offline"
    assert spec["parameters"]["retrieval_body_retention_mode"] == "hash_only"
    assert spec["parameters"]["source_ranking_policy"] == "query_overlap_score_desc_v1"
    assert spec["parameters"]["cache_dir"]["path"] == "plugin_artifacts/deep_research"
    assert spec["parameters"]["cache_dir"]["scope"] == "within_run_dir"


def test_direct_artifact_only_plugin_protocol_is_rejected_for_mutation_runs(tmp_path):
    class ArtifactOnlyPlugin:
        def run_artifacts_metadata(self):
            return {"status": "ok"}

    with pytest.raises(ValueError, match="missing .*build_extra_context"):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=str(tmp_path), problem_name="t"),
            plugins=[ArtifactOnlyPlugin()],
        )

    assert not (tmp_path / "t").exists()


def test_plugin_score_composition_is_logged_for_multiple_plugins():
    tmpdir = tempfile.mkdtemp()

    class AddMetricPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            program.metrics["plugin_metric"] = 1
            return score + 0.1

    class PenalizePlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            return score - 0.2

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[AddMetricPlugin(), PenalizePlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    composition = child["metadata"]["score_composition"]
    assert composition["initial_fitness"] == 1.0
    assert composition["final_fitness"] == pytest.approx(0.9)
    assert composition["diverged_from_evaluation"] is True
    assert [p["plugin"] for p in composition["plugins"]] == ["AddMetricPlugin", "PenalizePlugin"]
    assert composition["plugins"][0]["metrics_added"] == ["plugin_metric"]
    assert child["fitness"] == pytest.approx(0.9)
    assert child["metadata"]["selection_score"] == pytest.approx(1.0)
    assert child["metadata"]["archive_admission"]["selection_score"] == pytest.approx(1.0)


def test_repeated_plugin_instances_have_stable_runtime_instance_ids():
    tmpdir = tempfile.mkdtemp()

    class DeltaPlugin:
        def __init__(self, delta):
            self.delta = delta
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations):
            return f"delta={self.delta}"
        def prompt_context_metadata(self):
            return {"delta": self.delta}
        def on_evaluated(self, program, score):
            return score + self.delta
        def run_artifacts_metadata(self):
            return {"delta": self.delta}

    plugins = [DeltaPlugin(0.1), DeltaPlugin(-0.2)]
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=plugins,
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    records = [json.loads(line) for line in (run_dir / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    provenance = manifest["provenance"]["plugins"]
    contexts = child["metadata"]["plugin_context"]
    score_plugins = child["metadata"]["score_composition"]["plugins"]
    artifacts = manifest["runtime"]["plugin_artifacts"]

    expected_ids = [
        f"plugin:0:{DeltaPlugin.__module__}.{DeltaPlugin.__qualname__}",
        f"plugin:1:{DeltaPlugin.__module__}.{DeltaPlugin.__qualname__}",
    ]
    assert [record["instance_id"] for record in provenance] == expected_ids
    assert [record["index"] for record in provenance] == [0, 1]
    assert [record["instance_id"] for record in contexts] == expected_ids
    assert [record["instance_id"] for record in score_plugins] == expected_ids
    assert [record["instance_id"] for record in artifacts] == expected_ids
    assert [record["metadata"]["delta"] for record in contexts] == [0.1, -0.2]
    assert [record["metadata"]["delta"] for record in artifacts] == [0.1, -0.2]
    assert [record["delta"] for record in score_plugins] == [pytest.approx(0.1), pytest.approx(-0.2)]


def test_secret_like_plugin_identity_is_redacted_in_manifest_and_candidate_history():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_pluginctx_secret_1234567890"  # pragma: allowlist secret

    def on_generation_start(self, g, db):
        pass

    def on_generation_end(self, g, b):
        pass

    def build_extra_context(self, parent, inspirations):
        return "prefer the simple branch"

    def prompt_context_metadata(self):
        return {"safe": "metadata"}

    def on_evaluated(self, program, score):
        return score

    def run_artifacts_metadata(self):
        return {"safe": "artifact"}

    SecretPlugin = type(
        f"api_key={secret}",
        (),
        {
            "__module__": f"api_key={secret}",
            "on_generation_start": on_generation_start,
            "on_generation_end": on_generation_end,
            "build_extra_context": build_extra_context,
            "prompt_context_metadata": prompt_context_metadata,
            "on_evaluated": on_evaluated,
            "run_artifacts_metadata": run_artifacts_metadata,
        },
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[SecretPlugin()],
        )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text())
    records = [json.loads(line) for line in (run_dir / "history.jsonl").read_text().splitlines()]
    context_record = records[-1]["metadata"]["plugin_context"][0]
    artifact_record = manifest["runtime"]["plugin_artifacts"][0]
    provenance_record = manifest["provenance"]["plugins"][0]
    rendered = json.dumps(
        {
            "context": context_record,
            "artifact": artifact_record,
            "provenance": provenance_record,
        },
        sort_keys=True,
    )

    assert secret not in rendered
    assert context_record["plugin"] == "api_key=[REDACTED]"
    assert context_record["module"] == "api_key=[REDACTED]"
    assert context_record["plugin_secret_redacted"] is True
    assert context_record["module_secret_redacted"] is True
    assert context_record["class_secret_redacted"] is True
    assert context_record["instance_id_redacted"] is True
    assert "Plugin: api_key=[REDACTED]" in context_record["context"]
    assert "Module: api_key=[REDACTED]" in context_record["context"]
    assert provenance_record["instance_id"] == context_record["instance_id"]
    assert artifact_record["instance_id"] == context_record["instance_id"]
    assert len(context_record["class_hash"]) == 64


def test_plugin_unsafe_metric_side_effect_is_reverted_and_logged():
    tmpdir = tempfile.mkdtemp()

    class BadMetricPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            program.metrics["api_key=sk-proj_plugin_metric_secret_1234567890"] = 0.2
            return score + 0.1

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[BadMetricPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    plugin_record = child["metadata"]["score_composition"]["plugins"][0]
    assert plugin_record["error"] == "invalid_plugin_metrics"
    assert plugin_record["accepted"] is False
    assert plugin_record["after"] == 1.0
    assert "sk-proj_plugin_metric_secret" not in json.dumps(child)
    assert child["fitness"] == 1.0


def test_plugin_valid_metadata_side_effect_is_persisted_and_logged():
    tmpdir = tempfile.mkdtemp()

    class MetadataPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            program.metadata["plugin_note"] = {
                "status": "ok",
                "value": 1,
                "secret": "api_key=sk-proj_plugin_metadata_secret_1234567890",
            }
            return score + 0.1

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[MetadataPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    plugin_record = child["metadata"]["score_composition"]["plugins"][0]
    assert child["metadata"]["plugin_note"] == {
        "status": "ok",
        "value": 1,
        "secret": "api_key=[REDACTED]",
    }
    assert plugin_record["accepted"] is True
    assert plugin_record["metadata_added"] == ["plugin_note"]
    assert plugin_record["error"] is None


@pytest.mark.parametrize(
    "metadata_value,error_text",
    [
        ({"bad": {"not", "json"}}, "JSON-safe metadata"),
        ({"bad": float("inf")}, "must be finite"),
    ],
)
def test_plugin_invalid_metadata_side_effect_is_reverted_and_logged(metadata_value, error_text):
    tmpdir = tempfile.mkdtemp()

    class BadMetadataPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            program.metadata["plugin_bad"] = metadata_value["bad"]
            return score + 0.1

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[BadMetadataPlugin()],
        )

    run_dir = Path(tmpdir) / "t"
    records = [json.loads(line) for line in (run_dir / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    plugin_record = child["metadata"]["score_composition"]["plugins"][0]
    assert "plugin_bad" not in child["metadata"]
    assert child["fitness"] == 1.0
    assert plugin_record["accepted"] is False
    assert plugin_record["after"] == 1.0
    assert plugin_record["error"] == "invalid_plugin_metadata"
    assert error_text in plugin_record["message"]
    assert plugin_record["metadata_added"] == []
    assert not (run_dir / "history_invalid.jsonl").exists()


def test_persisted_mutation_prompt_filters_plugin_metrics_but_keeps_feedback_metrics():
    tmpdir = tempfile.mkdtemp()

    class AddUnsafeMetricPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            program.metrics["plugin_metric"] = 1
            program.metrics["api_key=sk-proj_prompt_metric_secret_1234567890"] = 0.5
            return score + 0.1

    llm = _RewardLLM(feedback='{"score": 0.8, "feedback": "ok", "discard": false}')
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=2,
                log_dir=tmpdir,
                problem_name="t",
                parent_selection_strategy="exploit",
                num_inspirations=1,
                inspiration_strategy="selection",
                llm_feedback=[{"name": "review", "metric": "llm_review", "weight": 0.1}],
            ),
            plugins=[AddUnsafeMetricPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    prompt = records[-1]["metadata"]["prompt"]
    assert "llm_review=0.8" in prompt
    assert "plugin_metric" not in prompt
    assert "sk-proj_prompt_metric_secret" not in prompt


def test_invalid_plugin_score_is_rejected_and_logged():
    tmpdir = tempfile.mkdtemp()

    class BadScorePlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            return float("inf")

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[BadScorePlugin()],
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    plugin_record = child["metadata"]["score_composition"]["plugins"][0]
    assert child["fitness"] == 1.0
    assert plugin_record["accepted"] is False
    assert plugin_record["error"] == "non_finite_plugin_score"


def test_plugin_boosted_invalid_candidate_is_not_archived():
    tmpdir = tempfile.mkdtemp()
    llm = _llm("no diff here")

    class BoostPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            return 1.0

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        best = evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[BoostPlugin()],
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert best.id == records[0]["id"]
    assert child["fitness"] == 1.0
    assert child["evaluation"]["is_valid"] is False
    assert child["metadata"]["archive_admission"]["admitted"] is False
    assert child["metadata"]["archive_admission"]["reason"] == "invalid_evaluation"
    assert child["metadata"]["backend_reward"]["eligible"] is False
    assert child["metadata"]["backend_reward"]["reward"] == 0.0
    assert child["metadata"]["backend_reward"]["reason"] == "invalid_evaluation"
    llm.record_reward.assert_called_once_with(0, 0.0, call_id=None)


def test_admitted_valid_candidate_rewards_backend_improvement():
    tmpdir = tempfile.mkdtemp()
    llm = _RewardLLM()

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem("def evaluate(c): return {'score': 1.0 if 'x=2' in c else 0.25, 'is_valid': True}"),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert child["metadata"]["archive_admission"]["admitted"] is True
    assert child["metadata"]["backend_reward"]["eligible"] is True
    assert child["metadata"]["backend_reward"]["reward"] == 0.75
    assert llm.rewards == [(0, 0.75, "reward-call-0")]


def test_successful_candidate_persists_recovered_llm_fallback_span():
    tmpdir = tempfile.mkdtemp()
    bad = MagicMock()
    bad.name = "bad/model"
    bad.api_mode = None
    bad.generate.side_effect = RuntimeError("provider down")
    good = MagicMock()
    good.name = "good/model"
    good.api_mode = None
    good.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    llm = LLMEnsemble([bad, good], fallback=True)

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem("def evaluate(c): return {'score': 1.0 if 'x=2' in c else 0.25, 'is_valid': True}"),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    calls = child["metadata"]["llm_calls"]

    assert [call["backend_idx"] for call in calls] == [0, 1]
    assert [call["status"] for call in calls] == ["error", "ok"]
    assert calls[0]["error_type"] == "RuntimeError"
    assert "provider down" in calls[0]["error"]
    assert calls[0]["will_fallback"] is True
    assert calls[1]["rewarded"] is True
    assert calls[1]["reward"] == 0.75
    assert child["metadata"]["backend_reward"]["reward"] == 0.75


def test_mutation_provider_failure_logs_failure_and_continues_run():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_mutation_failure_secret_1234567890"  # pragma: allowlist secret

    class FlakyBackend:
        name = "flaky/model"
        api_mode = None

        def __init__(self):
            self.calls = 0

        def generate(self, prompt, **kwargs):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError(f"mutation provider failed token={secret}")
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    llm = LLMEnsemble([FlakyBackend()], fallback=False)

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        best = evolve(
            _problem(
                "def evaluate(c): return {'score': 1.0 if 'x=2' in c else 0.25, "
                "'is_valid': True}"
            ),
            Config(max_generations=2, log_dir=tmpdir, problem_name="t"),
        )

    run_dir = Path(tmpdir) / "t"
    records = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    failures = [
        json.loads(line)
        for line in (run_dir / "failure_history.jsonl").read_text().splitlines()
    ]
    manifest = json.loads((run_dir / "manifest.json").read_text())
    failure = failures[0]
    failure_text = json.dumps(failure)

    assert best.code == "x=2"
    assert records[-1]["code"] == "x=2"
    assert manifest["runtime"]["status"] == "completed"
    assert manifest["runtime"]["artifacts"]["failure_history.jsonl"]["exists"] is True
    assert failure["error"] == "llm_mutation_failed"
    assert failure["diff_error"] == "llm_mutation_failed"
    assert failure["changed_files"] == []
    assert "llm_mutation_failed" in failure["mutation_text"]
    assert "RuntimeError" in failure["mutation_text"]
    assert secret not in failure_text
    assert "[REDACTED]" in failure_text
    assert llm.scheduler_state["role_accounting"]["mutation"]["failures"] == 1
    assert llm.scheduler_state["role_accounting"]["mutation"]["successes"] == 1


def test_mutation_timeout_logs_failure_artifact_and_continues_run():
    tmpdir = tempfile.mkdtemp()

    class FirstSlowThenFastBackend:
        name = "slow-then-fast/model"
        api_mode = None

        def __init__(self):
            self.calls = 0

        def generate(self, prompt, **kwargs):
            self.calls += 1
            if self.calls == 1:
                time.sleep(0.05)
            return "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    llm = LLMEnsemble(
        [FirstSlowThenFastBackend()],
        fallback=False,
        call_timeout_sec=0.001,
    )

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        best = evolve(
            _problem(
                "def evaluate(c): return {'score': 1.0 if 'x=2' in c else 0.25, "
                "'is_valid': True}"
            ),
            Config(max_generations=2, log_dir=tmpdir, problem_name="t"),
        )

    run_dir = Path(tmpdir) / "t"
    records = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    failures = [
        json.loads(line)
        for line in (run_dir / "failure_history.jsonl").read_text().splitlines()
    ]
    manifest = json.loads((run_dir / "manifest.json").read_text())
    failure = failures[0]

    assert best.code == "x=2"
    assert records[-1]["code"] == "x=2"
    assert manifest["runtime"]["status"] == "completed"
    assert manifest["runtime"]["artifacts"]["failure_history.jsonl"]["exists"] is True
    assert manifest["runtime"]["artifacts"]["llm_calls.jsonl"]["exists"] is True
    assert failure["error"] == "llm_mutation_failed"
    assert failure["diff_error"] == "llm_mutation_failed"
    assert "ProviderCallTimeoutError" in failure["mutation_text"]
    assert "provider_failure_category" in failure["mutation_text"]
    assert "timeout" in failure["mutation_text"]
    accounting = llm.scheduler_state["role_accounting"]["mutation"]
    assert accounting["timeout_failures"] == 1
    assert accounting["successes"] == 1


def test_llm_feedback_discarded_candidate_does_not_reward_backend():
    tmpdir = tempfile.mkdtemp()
    llm = _RewardLLM()

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem("def evaluate(c): return {'score': 1.0 if 'x=2' in c else 0.25, 'is_valid': True}"),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                llm_feedback=[{"name": "review", "min_score": 0.5}],
            ),
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert child["evaluation"]["is_valid"] is False
    assert child["metadata"]["archive_admission"]["admitted"] is False
    assert child["metadata"]["archive_admission"]["reason"] == "invalid_evaluation"
    assert child["metadata"]["backend_reward"]["eligible"] is False
    assert child["metadata"]["backend_reward"]["reward"] == 0.0
    assert llm.rewards == [(0, 0.0, "reward-call-0")]
    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    registry = manifest["runtime"]["history"]["evaluator_oracle_registry"]
    outcomes = registry["disagreement_outcomes"]
    assert registry["validation"]["ok"] is True
    assert validate_evaluator_oracle_registry(registry)["ok"] is True
    assert outcomes["candidate_with_feedback_count"] == 1
    assert outcomes["outcome_count"] == 1
    assert outcomes["disagreement_count"] == 1
    assert outcomes["feedback_discard_after_evaluator_pass_count"] == 1
    outcome = outcomes["records"][0]
    assert outcome["program_id"] == child["id"]
    assert outcome["feedback_oracle_id"] == "llm_feedback:review"
    assert outcome["evaluator_valid_before_feedback"] is True
    assert outcome["feedback_discard"] is True
    assert outcome["final_is_valid"] is False
    assert outcome["outcome"] == "feedback_discard_after_evaluator_pass"
    assert outcome["final_effect"] == "post_hoc_feedback_invalidated_candidate"
    assert outcome["disagreement_observed"] is True
    assert outcome["authority_boundary"] == (
        "post_evaluator_feedback_not_independent_reference_or_statistical_oracle"
    )
    assert outcomes["policy"]["independent_reference_or_statistical_oracle"] is False
    assert outcomes["claim_readiness"][
        "observed_post_hoc_feedback_disagreement_outcomes"
    ] is True
    assert outcomes["claim_readiness"][
        "independent_cross_oracle_disagreement_outcomes"
    ] is False


def test_plugin_corrupted_validity_metadata_is_not_archived():
    tmpdir = tempfile.mkdtemp()

    class CorruptValidityPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            program.evaluation["is_valid"] = "false"
            return 1.0

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        best = evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[CorruptValidityPlugin()],
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert best.id == records[0]["id"]
    assert child["evaluation"]["is_valid"] == "false"
    assert child["metadata"]["archive_admission"]["admitted"] is False
    assert child["metadata"]["archive_admission"]["reason"] == "invalid_evaluation"
    failures = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failures[-1]["admission_reason"] == "invalid_evaluation"
    assert failures[-1]["archive_admission"]["reason"] == "invalid_evaluation"


def test_plugin_penalized_valid_candidate_below_threshold_not_archived():
    tmpdir = tempfile.mkdtemp()

    class PenalizePlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            return -0.5

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[PenalizePlugin()],
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert child["evaluation"]["is_valid"] is True
    assert child["metadata"]["archive_admission"]["admitted"] is False
    assert child["metadata"]["archive_admission"]["reason"] == "below_threshold"
    failures = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failures[-1]["admission_reason"] == "below_threshold"
    assert failures[-1]["archive_admission"]["threshold"] == 0.0


def test_loop_logs_prompt_program_id_and_prompt_history():
    tmpdir = tempfile.mkdtemp()
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    run_dir = Path(tmpdir) / "t"
    records = [json.loads(l) for l in (run_dir / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert "prompt_program_id" in child["metadata"]
    assert (run_dir / "prompt_history.jsonl").exists()


def test_loop_applies_prompt_budget_before_llm_and_logs_diagnostics():
    tmpdir = tempfile.mkdtemp()
    problem = _problem()
    problem.task_description = "Expand the implementation. " + ("A" * 4000)
    llm = _TelemetryLLM()

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                prompt_max_chars=700,
            ),
        )

    run_dir = Path(tmpdir) / "t"
    records = [json.loads(l) for l in (run_dir / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    prompt = child["metadata"]["prompt"]
    diagnostics = child["metadata"]["prompt_diagnostics"]

    assert len(prompt) <= 700
    assert llm.calls[0]["prompt_chars"] <= 700
    assert diagnostics["max_chars"] == 700
    assert diagnostics["original_chars"] > 700
    assert diagnostics["rendered_chars"] == len(prompt)
    assert diagnostics["truncated"] is True
    assert diagnostics["strategy"] == "middle_truncate_preserve_task"
    assert diagnostics["prompt_sha256"]
    assert len(diagnostics["prompt_sha256"]) == 64
    assert diagnostics["prompt_sha256_scope"] == "rendered_prompt"
    assert diagnostics["context_order_policy"] == "path_sort"
    assert diagnostics["section_budget"]["schema"] == (
        "libreevolve.prompt_section_budget.v1"
    )
    assert diagnostics["section_budget"]["max_chars"] == 700
    assert diagnostics["section_budget"]["rendered_chars_before_cap"] == (
        diagnostics["original_chars"]
    )
    assert diagnostics["section_budget"]["required_sections_fit"] is False
    assert (
        diagnostics["section_budget"]["required_section_chars"]
        + diagnostics["section_budget"]["template_overhead_chars"]
        > 700
    )
    assert any(
        section["name"] == "task"
        for section in diagnostics["section_budget"]["sections"]
    )
    assert "Mutation mode: diff" in prompt
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["config"]["prompt_max_chars"] == 700


def test_loop_applies_prompt_estimated_token_budget_before_llm_and_logs_diagnostics():
    tmpdir = tempfile.mkdtemp()
    problem = _problem()
    problem.task_description = "Expand the implementation. " + ("A" * 4000)
    llm = _TelemetryLLM()

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                prompt_max_estimated_tokens=175,
            ),
        )

    run_dir = Path(tmpdir) / "t"
    records = [json.loads(l) for l in (run_dir / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    prompt = child["metadata"]["prompt"]
    diagnostics = child["metadata"]["prompt_diagnostics"]

    assert len(prompt) <= 700
    assert math.ceil(len(prompt) / 4) <= 175
    assert llm.calls[0]["prompt_chars"] <= 700
    assert diagnostics["estimated_tokens"] <= 175
    assert diagnostics["section_budget"]["max_chars"] == 700
    assert diagnostics["section_budget"]["configured_max_chars"] is None
    assert diagnostics["section_budget"]["max_estimated_tokens"] == 175
    assert diagnostics["section_budget"]["max_estimated_tokens_source"] == (
        "config.prompt_max_estimated_tokens"
    )
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["config"]["prompt_max_estimated_tokens"] == 175


def test_loop_wires_discovered_provider_token_counter_into_prompt_diagnostics():
    tmpdir = tempfile.mkdtemp()
    problem = _problem()
    problem.context_files = {
        "notes.txt": " ".join(f"context{i}" for i in range(40)),
    }
    llm = _TelemetryLLM()
    capability = {
        "schema": "libreevolve.prompt_token_counter_capability.v1",
        "policy": "eligible_backend_common_provider_counter_optional_dependency_v1",
        "role": "mutation",
        "status": "ready",
        "reason": "common_provider_counter_available",
        "counter_name": "fixture:wordpiece",
        "eligible_backend_indices": [0],
        "selection_scope": "backend_metadata_role_match_when_available",
        "backends": [
            {
                "backend_idx": 0,
                "type": "openai",
                "model": "gpt-4o-mini",
                "status": "ready",
                "source": "fixture",
                "counter_name": "fixture:wordpiece",
                "reason": "available",
            }
        ],
    }

    with (
        patch("libreevolve.core.loop.build_llm", return_value=llm),
        patch(
            "libreevolve.core.loop.discover_prompt_token_counter",
            return_value=(lambda text: len(text.split()), capability),
        ),
    ):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                prompt_max_estimated_tokens=40,
                backends=[{"type": "openai", "model": "gpt-4o-mini"}],
            ),
        )

    run_dir = Path(tmpdir) / "t"
    records = [json.loads(l) for l in (run_dir / "history.jsonl").read_text().splitlines()]
    diagnostics = records[-1]["metadata"]["prompt_diagnostics"]
    section_budget = diagnostics["section_budget"]

    assert diagnostics["prompt_token_counter_capability"] == capability
    assert diagnostics["provider_token_counter"] == "fixture:wordpiece"
    assert diagnostics["provider_tokens"] == len(llm.calls[0]["prompt"].split())
    assert section_budget["token_count_policy"] == "provider_token_counter"
    assert section_budget["provider_token_counter"] == "fixture:wordpiece"
    assert section_budget["provider_tokens_limit"] == 40


def test_runtime_prompt_section_packing_coverage_scopes_non_mutation_roles():
    tmpdir = tempfile.mkdtemp()
    problem = _problem()
    problem.context_files = {
        "notes.txt": " ".join(f"context{i}" for i in range(20)),
    }
    llm = _TelemetryLLM()

    def discover_counter(backends, *, role="mutation", role_backend_indices=None):
        capability = {
            "schema": "libreevolve.prompt_token_counter_capability.v1",
            "policy": "eligible_backend_common_provider_counter_optional_dependency_v1",
            "role": role,
            "status": "ready",
            "reason": "common_provider_counter_available",
            "counter_name": "fixture:wordpiece",
            "eligible_backend_indices": [0],
            "selection_scope": "backend_metadata_role_match_when_available",
            "backends": [
                {
                    "backend_idx": 0,
                    "type": "openai",
                    "model": "gpt-4o-mini",
                    "status": "ready",
                    "source": "fixture",
                    "counter_name": "fixture:wordpiece",
                    "reason": "available",
                }
            ],
        }
        return (lambda text: len(text.split())), capability

    with (
        patch("libreevolve.core.loop.build_llm", return_value=llm),
        patch(
            "libreevolve.core.loop.discover_prompt_token_counter",
            side_effect=discover_counter,
        ),
    ):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                prompt_max_estimated_tokens=80,
                backends=[{"type": "openai", "model": "gpt-4o-mini"}],
            ),
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    coverage = manifest["runtime"]["prompt_section_packing"]

    assert coverage["schema"] == PROMPT_SECTION_PACKING_COVERAGE_SCHEMA
    assert coverage["section_packing_roles"] == ["mutation"]
    assert coverage["provider_token_section_packing_ready_roles"] == ["mutation"]
    assert coverage["provider_token_section_packing_missing_roles"] == [
        "critique",
        "feedback:*",
        "meta_prompt",
    ]
    assert coverage["automatic_provider_token_section_packing_complete"] is False
    role_status = {
        role["role"]: role["section_packing_status"]
        for role in coverage["roles"]
    }
    assert role_status == {
        "mutation": "supported",
        "critique": "unsupported",
        "feedback:*": "unsupported",
        "meta_prompt": "unsupported",
    }
    validation = coverage["validation"]
    assert validation["schema"] == PROMPT_SECTION_PACKING_COVERAGE_VALIDATION_SCHEMA
    assert validation["coverage_schema"] == PROMPT_SECTION_PACKING_COVERAGE_SCHEMA
    assert validation["ok"] is True
    assert validation["section_packing_role_count"] == 1
    assert validation["ready_role_count"] == 1
    assert validation["missing_role_count"] == 3
    assert coverage["exact_non_openai_provider_counters_ready"] is False
    assert coverage["registry_custom_role_section_packing_ready"] is False
    assert (
        coverage["retrieval_context_plugin_failure_memory_section_packing_ready"]
        is False
    )

    overclaim = copy.deepcopy(coverage)
    overclaim["automatic_provider_token_section_packing_complete"] = True
    overclaim.pop("validation")

    invalid = validate_prompt_section_packing_coverage(overclaim)

    assert invalid["ok"] is False
    assert any(
        issue["code"] == "section_packing_overclaim"
        for issue in invalid["issues"]
    )
    surface_overclaim = copy.deepcopy(coverage)
    surface_overclaim["exact_non_openai_provider_counters_ready"] = True
    surface_overclaim["registry_custom_role_section_packing_ready"] = True
    surface_overclaim[
        "retrieval_context_plugin_failure_memory_section_packing_ready"
    ] = True
    surface_overclaim.pop("validation")

    invalid_surface = validate_prompt_section_packing_coverage(surface_overclaim)

    assert invalid_surface["ok"] is False
    surface_codes = {issue["code"] for issue in invalid_surface["issues"]}
    assert "exact_non_openai_provider_counters_overclaim" in surface_codes
    assert "registry_custom_role_section_packing_overclaim" in surface_codes
    assert (
        "retrieval_context_plugin_failure_memory_section_packing_overclaim"
        in surface_codes
    )

    role_overclaim = copy.deepcopy(coverage)
    role_overclaim.pop("validation")
    role_overclaim["roles"][1]["section_packing_status"] = "supported"
    role_overclaim["roles"][1]["section_packing_boundary"] = (
        "pre_llm_promptsampler_optional_section_packing"
    )
    role_overclaim["roles"][1]["provider_token_section_packing_ready"] = True
    role_overclaim["section_packing_roles"] = ["mutation", "critique"]
    role_overclaim["provider_token_section_packing_ready_roles"] = [
        "mutation",
        "critique",
    ]
    role_overclaim["provider_token_section_packing_missing_roles"] = [
        "feedback:*",
        "meta_prompt",
    ]

    invalid_role = validate_prompt_section_packing_coverage(role_overclaim)

    assert invalid_role["ok"] is False
    assert any(
        issue["code"] == "non_mutation_section_packing_overclaim"
        for issue in invalid_role["issues"]
    )


def test_loop_logs_stochastic_prompt_format_selection_metadata():
    tmpdir = tempfile.mkdtemp()
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                num_inspirations=0,
                parent_selection_strategy="exploit",
                log_dir=tmpdir,
                problem_name="t",
                seed=0,
                prompt_variants=[DEFAULT_TEMPLATE + "\n[[prompt:tone]]"],
                prompt_format_options={
                    "tone": [
                        {"text": "Be concise.", "weight": 1.0},
                        {"text": "Explain tradeoffs.", "weight": 1.0},
                    ]
                },
            ),
        )

    run_dir = Path(tmpdir) / "t"
    records = [json.loads(l) for l in (run_dir / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    diagnostics = child["metadata"]["prompt_diagnostics"]["stochastic_formatting"]
    manifest = json.loads((run_dir / "manifest.json").read_text())

    assert "Explain tradeoffs." in child["metadata"]["prompt"]
    assert diagnostics["marker_syntax"] == "[[prompt:name]]"
    assert diagnostics["selections"][0]["name"] == "tone"
    assert diagnostics["selections"][0]["choice_index"] == 1
    assert diagnostics["selections"][0]["occurrences"] == 1
    assert len(diagnostics["selections"][0]["text_sha256"]) == 64
    assert manifest["config"]["prompt_format_options"]["tone"][0]["weight"] == 1.0
    report = manifest["runtime"]["history"][
        "stochastic_prompt_format_distribution_report"
    ]
    assert report["schema"] == (
        "libreevolve.stochastic_prompt_format_distribution_report.v1"
    )
    assert report["validation"]["ok"] is True
    assert validate_stochastic_prompt_format_distribution_report(report)["ok"] is True
    assert report["formatted_prompt_record_count"] == 1
    assert report["option_set_count"] == 1
    assert report["option_set_names"] == ["tone"]
    assert report["marker_names"] == ["tone"]
    assert report["selected_hash_match_count"] == 1
    assert report["prompt_call_link_count"] == 1
    assert report["claim_ready"] is True
    assert report["claim_readiness"]["option_distributions_recorded"] is True
    assert report["claim_readiness"]["selected_alternative_hashes_joined"] is True
    assert report["claim_readiness"]["prompt_call_linkage_recorded"] is True
    assert report["claim_readiness"]["rng_boundary_recorded"] is True
    assert report["claim_readiness"]["separate_config_file_source_recorded"] is False
    assert report["claim_readiness"]["human_authored_alternatives_certified"] is False
    assert (
        report["claim_readiness"]["full_alphaevolve_stochastic_formatting_parity"]
        is False
    )
    record = report["records"][0]
    assert record["candidate_id"] == child["id"]
    assert record["prompt_program_id"] == child["metadata"]["prompt_program_id"]
    assert record["marker_name"] == "tone"
    assert record["option_set_id"] == "prompt_format_options.tone"
    assert record["source_kind"] == "inline_or_effective_config"
    assert len(record["distribution_sha256"]) == 64
    assert record["choice_index"] == 1
    assert record["selected_text_sha256"] == diagnostics["selections"][0]["text_sha256"]
    assert record["selected_alternative"]["index"] == 1
    assert record["selected_alternative"]["text_sha256"] == record["selected_text_sha256"]
    assert record["weight_source"] == "prompt_format_options"
    assert record["weight_override_source"] == "prompt_format_options"
    assert record["rng_boundary"] == "run_local_framework_random"
    assert record["prompt_linkage"]["prompt_program_id"] == record["prompt_program_id"]
    assert len(record["alternatives"]) == 2
    assert [alternative["index"] for alternative in record["alternatives"]] == [0, 1]
    assert [alternative["weight"] for alternative in record["alternatives"]] == [
        1.0,
        1.0,
    ]
    assert sum(alternative["probability"] for alternative in record["alternatives"]) == 1.0

    edited = copy.deepcopy(report)
    edited["records"][0]["selected_alternative"]["text_sha256"] = "a" * 64
    edited["claim_readiness"]["full_alphaevolve_stochastic_formatting_parity"] = True
    validation = validate_stochastic_prompt_format_distribution_report(edited)
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "selected_hash_mismatch",
        "stochastic_formatting_parity_overclaim",
    }


def test_loop_logs_normalized_prompt_reward_policy_metadata():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(c): return {'score': 1.0 if 'x=2' in c else 0.5,"
        "'is_valid': True}"
    )
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                prompt_reward_mode="improvement",
                prompt_reward_bounds=[-1.0, 1.0],
                prompt_explore_coeff=0.0,
            ),
        )

    run_dir = Path(tmpdir) / "t"
    events = [
        json.loads(line)
        for line in (run_dir / "prompt_history.jsonl").read_text().splitlines()
    ]
    score_event = next(event for event in events if event["event"] == "score")
    reward = score_event["program"]["metadata"]["last_prompt_reward"]
    assert reward["mode"] == "improvement"
    assert reward["raw"] == 0.5
    assert reward["normalized"] == 0.75
    assert reward["bounds"] == [-1.0, 1.0]
    assert score_event["program"]["metadata"]["last_candidate_score"] == 1.0
    assert score_event["program"]["metadata"]["last_parent_score"] == 0.5
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["config"]["prompt_reward_mode"] == "improvement"
    assert manifest["config"]["prompt_reward_bounds"] == [-1.0, 1.0]
    assert manifest["config"]["prompt_explore_coeff"] == 0.0
    evaluator_source = manifest["problem"]["evaluator_sources"][0]
    assert evaluator_source["relative_path"] == "validate.py"
    expected_hash = hashlib.sha256((problem.problem_dir / "validate.py").read_bytes()).hexdigest()
    assert evaluator_source["sha256"] == expected_hash
    assert manifest["provenance"]["problem"]["tree_hash"]
    assert manifest["provenance"]["source"]["tree_hash"]
    assert manifest["provenance"]["environment"]["python"]["version"]
    assert manifest["provenance"]["environment"]["package"]["pyproject"]["path"] == "pyproject.toml"
    assert any(
        dep["name"] == "click"
        for dep in manifest["provenance"]["environment"]["dependencies"]
    )
    assert "git" in manifest["provenance"]


def test_loop_records_cli_dotenv_source_in_manifest():
    tmpdir = tempfile.mkdtemp()
    problem = _problem()
    problem.dotenv_source = {
        "path": ".env",
        "status": "loaded",
        "override": True,
        "load_phase": "cli_run_command",
        "scope": "run_command_provider_setup",
        "keys": ["LIBREEVOLVE_DOTENV_PROBE"],
    }

    evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["provenance"]["dotenv"] == problem.dotenv_source


def test_loop_records_declared_evaluator_data_in_manifest(tmp_path):
    problem = _problem()
    data_dir = problem.problem_dir / "data"
    data_dir.mkdir()
    data_file = data_dir / "input.json"
    data_file.write_text('{"target": 1}\n', encoding="utf-8")

    evolve(
        problem,
        Config(
            max_generations=0,
            log_dir=str(tmp_path),
            problem_name="t",
            evaluator_data_include=["data/*.json"],
        ),
    )

    manifest = json.loads((tmp_path / "t" / "manifest.json").read_text())
    evaluator_source = manifest["problem"]["evaluator_sources"][0]
    declared = evaluator_source["declared_data_sources"]

    assert manifest["config"]["evaluator_data_include"] == ["data/*.json"]
    assert manifest["config"]["evaluator_data_exclude"] == []
    assert declared["enabled"] is True
    assert declared["file_count"] == 1
    assert declared["files"][0]["data_path"] == "data/input.json"
    assert declared["files"][0]["sha256"] == hashlib.sha256(
        data_file.read_bytes()
    ).hexdigest()


def test_evolve_git_provenance_uses_hashed_source_root(tmp_path, monkeypatch):
    problem = _problem()
    outside_cwd = tmp_path / "outside"
    outside_cwd.mkdir()
    monkeypatch.chdir(outside_cwd)
    import libreevolve.core.loop as loop_module

    expected_source_root = Path(loop_module.__file__).resolve().parents[1]
    captured_git_paths = []

    def fake_git_state(cwd=None):
        captured_git_paths.append(Path(cwd).resolve())
        return {
            "available": True,
            "root": "<git-root>",
            "root_scope": "local_root_label",
            "root_hash": "0" * 64,
            "root_redacted": True,
            "head": "test-head",
            "dirty": False,
            "status_entries": [],
        }

    with patch("libreevolve.core.loop.git_state", side_effect=fake_git_state):
        evolve(
            problem,
            Config(
                max_generations=0,
                log_dir=str(tmp_path / "runs"),
                problem_name="t",
            ),
        )

    manifest = json.loads((tmp_path / "runs" / "t" / "manifest.json").read_text())
    source_provenance = manifest["provenance"]["source"]
    git_provenance = manifest["provenance"]["git"]
    assert captured_git_paths == [expected_source_root]
    assert expected_source_root != outside_cwd.resolve()
    assert source_provenance["root"] == "<libreevolve-root>"
    assert source_provenance["root_redacted"] is True
    assert len(source_provenance["root_hash"]) == 64
    assert git_provenance["root"] == "<git-root>"
    assert git_provenance["root_redacted"] is True
    assert len(git_provenance["root_hash"]) == 64


def test_prompt_reward_uses_plugin_adjusted_score_with_multiple_metrics():
    tmpdir = tempfile.mkdtemp()

    class BoostPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            program.metrics["plugin_bonus"] = 0.25
            return score + 0.25

    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c): return {'score': 0.4, 'aux': 0.2, 'is_valid': True}"
    )
    problem = Problem(
        name="t",
        task_description="t",
        metrics=[
            {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
            {"name": "aux", "bounds": [0.0, 1.0]},
        ],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["x=1"],
        problem_dir=d,
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            problem,
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[BoostPlugin()],
        )

    events = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "prompt_history.jsonl").read_text().splitlines()
    ]
    score_event = next(event for event in events if event["event"] == "score")
    reward = score_event["program"]["metadata"]["last_prompt_reward"]
    assert reward["raw"] == 0.65
    assert reward["normalized"] == 0.65
    assert score_event["program"]["metadata"]["last_candidate_score"] == 0.65


def test_loop_logs_mutation_backend_index():
    tmpdir = tempfile.mkdtemp()
    llm = _llm()
    llm.generate.return_value = ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 2)
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert child["metadata"]["backend_idx"] == 2


def test_loop_logs_archive_admission_for_seed_and_child():
    tmpdir = tempfile.mkdtemp()
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    seed_admission = records[0]["metadata"]["archive_admission"]
    child_admission = records[-1]["metadata"]["archive_admission"]
    assert seed_admission["admitted"] is True
    assert seed_admission["island_id"] == 0
    assert seed_admission["cell"] is not None
    assert child_admission["admitted"] is True
    assert child_admission["program_id"] == records[-1]["id"]


def test_loop_excludes_selected_parent_from_inspirations():
    tmpdir = tempfile.mkdtemp()
    seen = []

    class CapturePlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            seen.append((parent.id, [program.id for program in inspirations]))
            return ""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[CapturePlugin()],
        )

    assert seen
    parent_id, inspiration_ids = seen[0]
    assert parent_id not in inspiration_ids


def test_generation_start_hook_mutations_do_not_replace_selected_parent():
    tmpdir = tempfile.mkdtemp()
    seen = []
    injected_ids = []

    class InjectBestPlugin:
        def on_generation_start(self, g, db):
            program = Program(
                code="x=999",
                fitness=999.0,
                generation=g,
                metrics={"score": 999.0},
                evaluation={"score": 999.0, "is_valid": True},
                metadata={"source": "generation_start_plugin"},
            )
            admission = db.admit(program, threshold=VALID_THRESHOLD)
            assert admission["admitted"] is True
            injected_ids.append(program.id)

        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score

        def build_extra_context(self, parent, inspirations):
            seen.append((parent.id, [program.id for program in inspirations]))
            return ""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                parent_selection_strategy="exploit",
                inspiration_strategy="selection",
                num_inspirations=1,
            ),
            plugins=[InjectBestPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    seed, child = records[0], records[-1]
    assert injected_ids
    assert seen == [(seed["id"], injected_ids)]
    assert child["parent_id"] == seed["id"]
    assert child["parent_id"] != injected_ids[0]


def test_loop_records_metric_targeted_inspiration_selection_metadata():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c):\n"
        "    if 'x=10' in c:\n"
        "        return {'score': 0.1, 'latency': 0.9, 'is_valid': True}\n"
        "    if 'x=2' in c:\n"
        "        return {'score': 0.8, 'latency': 0.2, 'is_valid': True}\n"
        "    return {'score': 0.9, 'latency': 0.1, 'is_valid': True}\n"
    )
    problem = Problem(
        name="t",
        task_description="t",
        metrics=[
            {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
            {"name": "latency", "bounds": [0.0, 1.0]},
        ],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["x=1", "x=10"],
        problem_dir=d,
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                parent_selection_strategy="exploit",
                inspiration_strategy="metric",
                num_inspirations=1,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    seed_ids = {record["id"] for record in records[:-1]}
    inspiration = child["metadata"]["inspiration_selection"]

    assert inspiration["strategy"] == "metric"
    assert inspiration["sample_kind"] == "diverse"
    assert inspiration["requested_count"] == 1
    assert inspiration["selected_count"] == 1
    assert inspiration["excluded_count"] == 1
    assert set(inspiration["selected_program_ids"]).issubset(seed_ids)
    assert child["parent_id"] not in inspiration["selected_program_ids"]
    assert inspiration["target_metrics"] == [
        {"metric": "score", "program_id": inspiration["selected_program_ids"][0]},
        {"metric": "latency", "program_id": inspiration["selected_program_ids"][0]},
    ]


def test_loop_records_prompt_visible_metric_diverse_inspiration_evidence():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c):\n"
        "    if 'x=10' in c:\n"
        "        return {'score': 0.1, 'latency': 0.95, 'is_valid': True}\n"
        "    if 'x=2' in c:\n"
        "        return {'score': 0.8, 'latency': 0.2, 'is_valid': True}\n"
        "    return {'score': 0.9, 'latency': 0.1, 'is_valid': True}\n"
    )
    problem = Problem(
        name="t",
        task_description="t",
        metrics=[
            {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
            {"name": "latency", "bounds": [0.0, 1.0]},
        ],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["x=1", "x=10", "x=2"],
        problem_dir=d,
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                parent_selection_strategy="exploit",
                inspiration_strategy="metric",
                num_inspirations=2,
            ),
        )

    run_dir = Path(tmpdir) / "t"
    records = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    diversity = child["metadata"]["inspiration_selection"]["metric_diversity"]

    assert diversity["schema"] == "libreevolve.metric_diverse_inspiration.v1"
    assert diversity["visible_count"] == 2
    assert diversity["visible_program_ids"] == diversity["selected_program_ids"]
    assert diversity["distinct_metric_count"] == 2
    assert diversity["distinct_metric_niches"] == ["score", "latency"]
    assert diversity["metric_diverse_prompt_visible"] is True
    assert diversity["claim_ready"] is False
    assert diversity["benchmark_policy"] == {
        "schema": "libreevolve.metric_diverse_prompt_benchmark_boundary.v1",
        "benchmark_required_metric_diverse_prompt_policy": False,
        "cross_run_metric_diverse_prompt_fixture": False,
        "scalar_and_single_metric_comparison": False,
        "alphaevolve_section_2_4_claim_ready": False,
    }
    assert diversity["benchmark_comparison_readiness"] == {
        "schema": "libreevolve.metric_diverse_benchmark_comparison_readiness.v1",
        "prompt_visible_metric_diversity_evidence": True,
        "benchmark_prompt_policy_enforced": False,
        "cross_run_metric_diverse_fixture": False,
        "scalar_only_baseline_comparison": False,
        "single_metric_target_baseline_comparison": False,
        "equal_budget_comparison_report": False,
        "alphaevolve_section_2_4_claim_ready": False,
        "remaining_gap": [
            "benchmark_prompt_policy_enforced",
            "cross_run_metric_diverse_fixture",
            "scalar_only_baseline_comparison",
            "single_metric_target_baseline_comparison",
            "equal_budget_comparison_report",
        ],
    }
    assert diversity["records"][0]["metric_niche"] == "score"
    assert diversity["records"][0]["metric_niche_source"] == (
        "selection_metadata.target_metrics"
    )
    assert diversity["records"][1]["metric_niche"] == "latency"
    assert child["metadata"]["prompt_diagnostics"]["metric_diverse_inspiration"][
        "metric_diverse_prompt_visible"
    ] is True

    manifest = json.loads((run_dir / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["metric_diverse_inspiration_report"]
    assert report["schema"] == "libreevolve.metric_diverse_inspiration_report.v1"
    assert report["candidate_count"] == 1
    assert report["metric_diverse_prompt_count"] == 1
    assert report["claim_ready"] is False
    assert report["claim_readiness"][
        "prompt_visible_metric_diversity_evidence"
    ] is True
    assert report["claim_readiness"][
        "benchmark_required_metric_diverse_prompt_policy"
    ] is False
    assert report["benchmark_policy"]["alphaevolve_section_2_4_claim_ready"] is False
    assert report["benchmark_comparison_readiness"][
        "prompt_visible_metric_diversity_evidence"
    ] is True
    assert report["benchmark_comparison_readiness"][
        "benchmark_prompt_policy_enforced"
    ] is False
    assert report["benchmark_comparison_readiness"][
        "scalar_only_baseline_comparison"
    ] is False
    assert report["benchmark_comparison_readiness"][
        "single_metric_target_baseline_comparison"
    ] is False
    assert report["benchmark_comparison_readiness"][
        "equal_budget_comparison_report"
    ] is False
    assert "scalar_and_single_metric_comparison" in (
        report["benchmark_policy"]["remaining_required_evidence"]
    )
    assert report["validation"]["ok"] is True
    assert validate_metric_diverse_inspiration_report(report)["ok"] is True

    edited = copy.deepcopy(report)
    edited["claim_ready"] = True
    edited["benchmark_policy"]["alphaevolve_section_2_4_claim_ready"] = True
    edited["benchmark_comparison_readiness"]["equal_budget_comparison_report"] = True
    edited["claim_readiness"]["benchmark_required_metric_diverse_prompt_policy"] = True
    validation = validate_metric_diverse_inspiration_report(edited)
    assert validation["ok"] is False
    assert {
        "invalid_claim_ready",
        "invalid_benchmark_policy",
        "invalid_benchmark_comparison_readiness",
        "benchmark_claim_overclaim",
    }.issubset({issue["code"] for issue in validation["issues"]})


def test_prompt_context_policy_overrides_upstream_inspiration_strategy():
    tmpdir = tempfile.mkdtemp()
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_feedback}\n{parent_code}\n{inspirations}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={"inspiration_strategy": "recency"},
    )
    prompt_db.record_result(parent_prompt.id, 0.0)

    with (
        patch("libreevolve.core.loop.build_llm", return_value=_llm()),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                inspiration_strategy="metric",
                num_inspirations=1,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    inspiration = records[-1]["metadata"]["inspiration_selection"]
    assert inspiration["strategy"] == "recency"
    assert inspiration["strategy_source"] == "prompt_context_policy"
    assert inspiration["configured_strategy"] == "metric"


def test_prompt_context_policy_overrides_upstream_inspiration_sample_count():
    tmpdir = tempfile.mkdtemp()
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_feedback}\n{parent_code}\n{inspirations}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={"inspiration_sample_count": 0},
    )
    prompt_db.record_result(parent_prompt.id, 0.0)

    with (
        patch("libreevolve.core.loop.build_llm", return_value=_llm()),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                num_inspirations=3,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    inspiration = records[-1]["metadata"]["inspiration_selection"]
    assert inspiration["requested_count"] == 0
    assert inspiration["selected_count"] == 0
    assert inspiration["requested_count_source"] == "prompt_context_policy"
    assert inspiration["configured_count"] == 3


def test_prompt_context_policy_filters_upstream_inspirations_by_required_metric():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(c):\n"
        "    if 'x=4' in c:\n"
        "        return {'score': 0.95, 'is_valid': True}\n"
        "    return {'score': 0.5, 'is_valid': True}\n"
    )
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_feedback}\n{parent_code}\n{inspirations}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={"inspiration_required_metric": "latency"},
    )
    prompt_db.record_result(parent_prompt.id, 0.0)
    seen_inspirations = []
    injected_ids = []

    class CaptureInspirationsPlugin(PluginBase):
        def on_generation_start(self, g, db):
            candidates = [
                Program(
                    code="x=3",
                    fitness=0.9,
                    metrics={"score": 0.9, "is_valid": True},
                    evaluation={"score": 0.9, "is_valid": True},
                ),
                Program(
                    code="x=2",
                    fitness=0.8,
                    metrics={"score": 0.8, "latency": 0.2, "is_valid": True},
                    evaluation={"score": 0.8, "latency": 0.2, "is_valid": True},
                ),
            ]
            for program in candidates:
                admission = db.admit(program, threshold=VALID_THRESHOLD)
                assert admission["admitted"] is True
                injected_ids.append(program.id)

        def build_extra_context(self, parent, inspirations):
            seen_inspirations.append(
                [(program.id, dict(program.metrics)) for program in inspirations]
            )
            return ""

    with (
        patch(
            "libreevolve.core.loop.build_llm",
            return_value=_llm("<<<SEARCH\nx=1\n===\nx=4\n>>>REPLACE"),
        ),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                parent_selection_strategy="exploit",
                inspiration_strategy="selection",
                num_inspirations=1,
            ),
            plugins=[CaptureInspirationsPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    inspiration = child["metadata"]["inspiration_selection"]

    assert len(injected_ids) == 2
    assert len(seen_inspirations) == 1
    assert len(seen_inspirations[0]) == 1
    assert "latency" in seen_inspirations[0][0][1]
    assert inspiration["requested_count"] == 1
    assert inspiration["selected_count"] == 1
    assert inspiration["inspiration_required_metric"] == "latency"
    assert inspiration["required_metric_source"] == "prompt_context_policy"
    assert inspiration["inspiration_required_metric_policy"] == "metric_present_filter_v1"
    assert inspiration["pre_filter_selected_count"] == 2
    assert inspiration["pool_requested_count"] == 20
    assert inspiration["required_metric_matching_count"] == 1
    assert inspiration["inspiration_filter_filtered_count"] == 1
    assert inspiration["selected_program_ids"] == [seen_inspirations[0][0][0]]


def test_prompt_context_policy_excludes_upstream_inspirations_by_metric():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(c):\n"
        "    if 'x=4' in c:\n"
        "        return {'score': 0.95, 'is_valid': True}\n"
        "    return {'score': 0.5, 'is_valid': True}\n"
    )
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_feedback}\n{parent_code}\n{inspirations}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={"inspiration_excluded_metrics": ["debug_score"]},
    )
    prompt_db.record_result(parent_prompt.id, 0.0)
    seen_inspirations = []
    injected_ids = []

    class CaptureInspirationsPlugin(PluginBase):
        def on_generation_start(self, g, db):
            candidates = [
                Program(
                    code="x=3",
                    fitness=0.9,
                    metrics={
                        "score": 0.9,
                        "debug_score": 1.0,
                        "is_valid": True,
                    },
                    evaluation={
                        "score": 0.9,
                        "debug_score": 1.0,
                        "is_valid": True,
                    },
                ),
                Program(
                    code="x=2",
                    fitness=0.8,
                    metrics={"score": 0.8, "is_valid": True},
                    evaluation={"score": 0.8, "is_valid": True},
                ),
            ]
            for program in candidates:
                admission = db.admit(program, threshold=VALID_THRESHOLD)
                assert admission["admitted"] is True
                injected_ids.append(program.id)

        def build_extra_context(self, parent, inspirations):
            seen_inspirations.append(
                [(program.id, dict(program.metrics)) for program in inspirations]
            )
            return ""

    with (
        patch(
            "libreevolve.core.loop.build_llm",
            return_value=_llm("<<<SEARCH\nx=1\n===\nx=4\n>>>REPLACE"),
        ),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                parent_selection_strategy="exploit",
                inspiration_strategy="selection",
                num_inspirations=1,
            ),
            plugins=[CaptureInspirationsPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    inspiration = records[-1]["metadata"]["inspiration_selection"]

    assert len(injected_ids) == 2
    assert len(seen_inspirations) == 1
    assert len(seen_inspirations[0]) == 1
    assert "debug_score" not in seen_inspirations[0][0][1]
    assert inspiration["selected_count"] == 1
    assert inspiration["excluded_metrics_source"] == "prompt_context_policy"
    assert inspiration["inspiration_excluded_metrics"] == ["debug_score"]
    assert inspiration["inspiration_excluded_metrics_policy"] == (
        "metric_absence_filter_v1"
    )
    assert inspiration["pre_filter_selected_count"] == 2
    assert inspiration["excluded_metric_matching_count"] == 1
    assert inspiration["inspiration_filter_filtered_count"] == 1
    assert inspiration["selected_program_ids"] == [seen_inspirations[0][0][0]]


def test_prompt_context_policy_filters_upstream_inspirations_by_fitness():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(c):\n"
        "    if 'x=4' in c:\n"
        "        return {'score': 0.95, 'is_valid': True}\n"
        "    return {'score': 0.5, 'is_valid': True}\n"
    )
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_feedback}\n{parent_code}\n{inspirations}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={"inspiration_fitness_threshold": {"min": 0.75}},
    )
    prompt_db.record_result(parent_prompt.id, 0.0)
    seen_inspirations = []

    class CaptureInspirationsPlugin(PluginBase):
        def on_generation_start(self, g, db):
            for program in [
                Program(
                    code="x=3",
                    fitness=0.2,
                    metrics={"score": 0.2, "is_valid": True},
                    evaluation={"score": 0.2, "is_valid": True},
                ),
                Program(
                    code="x=2",
                    fitness=0.8,
                    metrics={"score": 0.8, "is_valid": True},
                    evaluation={"score": 0.8, "is_valid": True},
                ),
            ]:
                admission = db.admit(program, threshold=VALID_THRESHOLD)
                assert admission["admitted"] is True

        def build_extra_context(self, parent, inspirations):
            seen_inspirations.append(
                [(program.id, program.fitness) for program in inspirations]
            )
            return ""

    with (
        patch(
            "libreevolve.core.loop.build_llm",
            return_value=_llm("<<<SEARCH\nx=1\n===\nx=4\n>>>REPLACE"),
        ),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                parent_selection_strategy="exploit",
                inspiration_strategy="selection",
                num_inspirations=1,
            ),
            plugins=[CaptureInspirationsPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    inspiration = records[-1]["metadata"]["inspiration_selection"]

    assert len(seen_inspirations) == 1
    assert len(seen_inspirations[0]) == 1
    assert seen_inspirations[0][0][1] == 0.8
    assert inspiration["selected_count"] == 1
    assert inspiration["fitness_threshold_source"] == "prompt_context_policy"
    assert inspiration["inspiration_fitness_threshold"] == {
        "min": 0.75,
        "max": None,
    }
    assert inspiration["inspiration_fitness_threshold_policy"] == (
        "fitness_value_threshold_filter_v1"
    )
    assert inspiration["pre_filter_selected_count"] == 2
    assert inspiration["fitness_threshold_matching_count"] == 1
    assert inspiration["inspiration_filter_filtered_count"] == 1
    assert inspiration["selected_program_ids"] == [seen_inspirations[0][0][0]]


def test_prompt_context_policy_filters_upstream_inspirations_by_metric_thresholds():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(c):\n"
        "    if 'x=4' in c:\n"
        "        return {'score': 0.95, 'is_valid': True}\n"
        "    return {'score': 0.5, 'is_valid': True}\n"
    )
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_feedback}\n{parent_code}\n{inspirations}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={
            "inspiration_metric_thresholds": {
                "latency": {"max": 0.3},
                "score": {"min": 0.7},
            }
        },
    )
    prompt_db.record_result(parent_prompt.id, 0.0)
    seen_inspirations = []

    class CaptureInspirationsPlugin(PluginBase):
        def on_generation_start(self, g, db):
            for program in [
                Program(
                    code="x=3",
                    fitness=0.9,
                    metrics={"score": 0.9, "latency": 0.8, "is_valid": True},
                    evaluation={"score": 0.9, "latency": 0.8, "is_valid": True},
                ),
                Program(
                    code="x=2",
                    fitness=0.8,
                    metrics={"score": 0.8, "latency": 0.2, "is_valid": True},
                    evaluation={"score": 0.8, "latency": 0.2, "is_valid": True},
                ),
            ]:
                admission = db.admit(program, threshold=VALID_THRESHOLD)
                assert admission["admitted"] is True

        def build_extra_context(self, parent, inspirations):
            seen_inspirations.append(
                [(program.id, dict(program.metrics)) for program in inspirations]
            )
            return ""

    with (
        patch(
            "libreevolve.core.loop.build_llm",
            return_value=_llm("<<<SEARCH\nx=1\n===\nx=4\n>>>REPLACE"),
        ),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                parent_selection_strategy="exploit",
                inspiration_strategy="selection",
                num_inspirations=1,
            ),
            plugins=[CaptureInspirationsPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    inspiration = records[-1]["metadata"]["inspiration_selection"]

    assert len(seen_inspirations) == 1
    assert len(seen_inspirations[0]) == 1
    assert seen_inspirations[0][0][1]["latency"] == 0.2
    assert inspiration["selected_count"] == 1
    assert inspiration["inspiration_metric_thresholds"] == {
        "latency": {"min": None, "max": 0.3},
        "score": {"min": 0.7, "max": None},
    }
    assert inspiration["metric_thresholds_source"] == "prompt_context_policy"
    assert inspiration["inspiration_metric_threshold_policy"] == (
        "metric_value_threshold_filter_v1"
    )
    assert inspiration["pre_filter_selected_count"] == 2
    assert inspiration["metric_threshold_matching_count"] == 1
    assert inspiration["inspiration_filter_filtered_count"] == 1
    assert inspiration["selected_program_ids"] == [seen_inspirations[0][0][0]]


def test_prompt_context_policy_ranks_upstream_inspirations_by_metric():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(c):\n"
        "    if 'x=4' in c:\n"
        "        return {'score': 0.95, 'is_valid': True}\n"
        "    return {'score': 0.5, 'is_valid': True}\n"
    )
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_feedback}\n{parent_code}\n{inspirations}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={
            "inspiration_metric_ranking": {
                "metric": "latency",
                "direction": "minimize",
            }
        },
    )
    prompt_db.record_result(parent_prompt.id, 0.0)
    seen_inspirations = []

    class CaptureInspirationsPlugin(PluginBase):
        def on_generation_start(self, g, db):
            for program in [
                Program(
                    code="x=3",
                    fitness=0.9,
                    metrics={"score": 0.9, "latency": 0.8, "is_valid": True},
                    evaluation={"score": 0.9, "latency": 0.8, "is_valid": True},
                ),
                Program(
                    code="x=2",
                    fitness=0.8,
                    metrics={"score": 0.8, "latency": 0.2, "is_valid": True},
                    evaluation={"score": 0.8, "latency": 0.2, "is_valid": True},
                ),
            ]:
                admission = db.admit(program, threshold=VALID_THRESHOLD)
                assert admission["admitted"] is True

        def build_extra_context(self, parent, inspirations):
            seen_inspirations.append(
                [(program.id, dict(program.metrics)) for program in inspirations]
            )
            return ""

    with (
        patch(
            "libreevolve.core.loop.build_llm",
            return_value=_llm("<<<SEARCH\nx=1\n===\nx=4\n>>>REPLACE"),
        ),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                parent_selection_strategy="exploit",
                inspiration_strategy="selection",
                num_inspirations=1,
            ),
            plugins=[CaptureInspirationsPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    inspiration = records[-1]["metadata"]["inspiration_selection"]

    assert len(seen_inspirations) == 1
    assert len(seen_inspirations[0]) == 1
    assert seen_inspirations[0][0][1]["latency"] == 0.2
    assert inspiration["selected_count"] == 1
    assert inspiration["inspiration_metric_ranking"] == {
        "metric": "latency",
        "direction": "minimize",
    }
    assert inspiration["metric_ranking_source"] == "prompt_context_policy"
    assert inspiration["inspiration_metric_ranking_policy"] == "metric_value_sort_v1"
    assert inspiration["metric_ranking_candidate_count"] == 2
    assert inspiration["pre_filter_selected_count"] == 2
    assert inspiration["inspiration_filter_filtered_count"] == 1
    assert inspiration["selected_program_ids"] == [seen_inspirations[0][0][0]]


def test_prompt_context_policy_disables_plugin_context_generation():
    tmpdir = tempfile.mkdtemp()
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_code}\n{extra_context}\n{mutation_instructions}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={"plugin_context_enabled": False},
    )
    prompt_db.record_result(parent_prompt.id, 0.0)

    class DisabledContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            raise AssertionError("build_extra_context should not be called")
        def prompt_context_metadata(self):
            raise AssertionError("prompt_context_metadata should not be called")

    with (
        patch("libreevolve.core.loop.build_llm", return_value=_llm()),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[DisabledContextPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    plugin_context = child["metadata"]["plugin_context"]
    prompt_policy = child["metadata"]["prompt_diagnostics"]["prompt_context_policy"]

    assert "[PLUGIN CONTEXT]" not in child["metadata"]["prompt"]
    assert prompt_policy["plugin_context_enabled"] is False
    assert plugin_context[0]["emitted"] is False
    assert plugin_context[0]["context_visibility"] == "disabled_by_prompt_context_policy"
    assert plugin_context[0]["prompt_context_policy"] == {
        "schema": "libreevolve.plugin_context_policy.v1",
        "plugin_context_enabled": False,
        "source": "prompt_context_policy",
    }


def test_prompt_context_policy_allowlists_plugin_context_generation():
    tmpdir = tempfile.mkdtemp()
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_code}\n{extra_context}\n{mutation_instructions}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={"plugin_context_allowlist": ["AllowedContextPlugin"]},
    )
    prompt_db.record_result(parent_prompt.id, 0.0)

    class AllowedContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "allowed plugin guidance"
        def prompt_context_metadata(self):
            return {"channel": "allowed"}

    class BlockedContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            raise AssertionError("blocked plugin context hook should not run")
        def prompt_context_metadata(self):
            raise AssertionError("blocked plugin metadata hook should not run")

    with (
        patch("libreevolve.core.loop.build_llm", return_value=_llm()),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[AllowedContextPlugin(), BlockedContextPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    plugin_context = child["metadata"]["plugin_context"]
    prompt_policy = child["metadata"]["prompt_diagnostics"]["prompt_context_policy"]

    assert "allowed plugin guidance" in child["metadata"]["prompt"]
    assert "blocked plugin" not in child["metadata"]["prompt"]
    assert prompt_policy["plugin_context_allowlist"] == ["AllowedContextPlugin"]
    assert plugin_context[0]["plugin"] == "AllowedContextPlugin"
    assert plugin_context[0]["emitted"] is True
    assert plugin_context[0]["metadata"] == {"channel": "allowed"}
    assert plugin_context[1]["plugin"] == "BlockedContextPlugin"
    assert plugin_context[1]["emitted"] is False
    assert (
        plugin_context[1]["context_visibility"]
        == "not_selected_by_prompt_context_allowlist"
    )
    assert plugin_context[1]["prompt_context_policy"] == {
        "schema": "libreevolve.plugin_context_policy.v1",
        "plugin_context_enabled": True,
        "source": "prompt_context_policy",
        "plugin_context_allowlist": ["AllowedContextPlugin"],
        "selected": False,
    }


def test_prompt_context_policy_excludes_plugin_context_by_label():
    tmpdir = tempfile.mkdtemp()
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_code}\n{extra_context}\n{mutation_instructions}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={"plugin_context_excluded_labels": ["BlockedContextPlugin"]},
    )
    prompt_db.record_result(parent_prompt.id, 0.0)

    class AllowedContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "allowed plugin guidance"

    class BlockedContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            raise AssertionError("excluded plugin context hook should not run")
        def prompt_context_metadata(self):
            raise AssertionError("excluded plugin metadata hook should not run")

    with (
        patch("libreevolve.core.loop.build_llm", return_value=_llm()),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[AllowedContextPlugin(), BlockedContextPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    plugin_context = child["metadata"]["plugin_context"]
    prompt_policy = child["metadata"]["prompt_diagnostics"]["prompt_context_policy"]

    assert "allowed plugin guidance" in child["metadata"]["prompt"]
    assert "blocked plugin" not in child["metadata"]["prompt"]
    assert prompt_policy["plugin_context_excluded_labels"] == [
        "BlockedContextPlugin"
    ]
    assert plugin_context[0]["plugin"] == "AllowedContextPlugin"
    assert plugin_context[0]["emitted"] is True
    assert plugin_context[1]["plugin"] == "BlockedContextPlugin"
    assert plugin_context[1]["emitted"] is False
    assert plugin_context[1]["context_visibility"] == (
        "excluded_by_prompt_context_labels"
    )
    assert plugin_context[1]["prompt_context_policy"] == {
        "schema": "libreevolve.plugin_context_policy.v1",
        "plugin_context_enabled": True,
        "source": "prompt_context_policy",
        "plugin_context_excluded_labels": ["BlockedContextPlugin"],
        "selected": False,
    }


def test_prompt_context_policy_orders_plugin_context_generation():
    tmpdir = tempfile.mkdtemp()
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_code}\n{extra_context}\n{mutation_instructions}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={"plugin_context_order": ["SecondContextPlugin"]},
    )
    prompt_db.record_result(parent_prompt.id, 0.0)

    class FirstContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "first plugin guidance"

    class SecondContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "second plugin guidance"

    with (
        patch("libreevolve.core.loop.build_llm", return_value=_llm()),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[FirstContextPlugin(), SecondContextPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    prompt = child["metadata"]["prompt"]
    plugin_context = child["metadata"]["plugin_context"]
    prompt_policy = child["metadata"]["prompt_diagnostics"]["prompt_context_policy"]

    assert prompt.index("second plugin guidance") < prompt.index("first plugin guidance")
    assert prompt_policy["plugin_context_order"] == ["SecondContextPlugin"]
    assert plugin_context[0]["plugin"] == "FirstContextPlugin"
    assert plugin_context[0]["prompt_context_order"] == {
        "policy": "plugin_context_order_v1",
        "source": "config_plugin_order_append",
        "position": None,
        "configured_order": ["SecondContextPlugin"],
    }
    assert plugin_context[1]["plugin"] == "SecondContextPlugin"
    assert plugin_context[1]["prompt_context_order"] == {
        "policy": "plugin_context_order_v1",
        "source": "prompt_context_policy",
        "position": 0,
        "configured_order": ["SecondContextPlugin"],
    }


def test_prompt_context_policy_caps_plugin_context_by_label():
    tmpdir = tempfile.mkdtemp()
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_code}\n{extra_context}\n{mutation_instructions}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={"plugin_context_max_chars_by_label": {"CappedContextPlugin": 12}},
    )
    prompt_db.record_result(parent_prompt.id, 0.0)

    class CappedContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "abcdefghijklmnopqrstuvwxyz"
        def prompt_context_metadata(self):
            return {"channel": "capped"}

    with (
        patch("libreevolve.core.loop.build_llm", return_value=_llm()),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[CappedContextPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    context_record = child["metadata"]["plugin_context"][0]
    prompt_policy = child["metadata"]["prompt_diagnostics"]["prompt_context_policy"]

    assert "abcdefghijklmnopqrstuvwxyz" not in child["metadata"]["prompt"]
    assert '"abcdefghijkl"' in child["metadata"]["prompt"]
    assert prompt_policy["plugin_context_max_chars_by_label"] == {
        "CappedContextPlugin": 12
    }
    assert context_record["policy_max_chars"] == 12
    assert context_record["max_chars"] == 12
    assert context_record["default_max_chars"] == 4000
    assert context_record["original_chars"] == 26
    assert context_record["prompt_context_truncated"] is True
    assert context_record["metadata"] == {"channel": "capped"}


def test_prompt_context_policy_uses_head_tail_plugin_context_truncation():
    tmpdir = tempfile.mkdtemp()
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_code}\n{extra_context}\n{mutation_instructions}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={
            "plugin_context_max_chars": 12,
            "plugin_context_truncation": "head_tail",
        },
    )
    prompt_db.record_result(parent_prompt.id, 0.0)

    class HeadTailContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "abcdefghij0123456789"

    with (
        patch("libreevolve.core.loop.build_llm", return_value=_llm()),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[HeadTailContextPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    prompt = child["metadata"]["prompt"]
    context_record = child["metadata"]["plugin_context"][0]
    prompt_policy = child["metadata"]["prompt_diagnostics"]["prompt_context_policy"]

    assert '"abcdef456789"' in prompt
    assert "ghij0123" not in prompt
    assert prompt_policy["plugin_context_truncation"] == "head_tail"
    assert context_record["policy_truncation"] == "head_tail"
    assert context_record["prompt_context_truncated"] is True
    assert context_record["prompt_context_content_policy"] == {
        "schema": "libreevolve.plugin_context_content_policy.v1",
        "max_chars": 12,
        "truncation": "head_tail",
        "selection_policy": "head_tail_chars_after_redaction",
    }


def test_prompt_context_policy_caps_plugin_context_globally():
    tmpdir = tempfile.mkdtemp()
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_code}\n{extra_context}\n{mutation_instructions}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={"plugin_context_max_chars": 8},
    )
    prompt_db.record_result(parent_prompt.id, 0.0)

    class GloballyCappedContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "abcdefghijklmnopqrstuvwxyz"
        def prompt_context_metadata(self):
            return {"channel": "global"}

    with (
        patch("libreevolve.core.loop.build_llm", return_value=_llm()),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[GloballyCappedContextPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    context_record = child["metadata"]["plugin_context"][0]
    prompt_policy = child["metadata"]["prompt_diagnostics"]["prompt_context_policy"]

    assert "abcdefghijklmnopqrstuvwxyz" not in child["metadata"]["prompt"]
    assert '"abcdefgh"' in child["metadata"]["prompt"]
    assert prompt_policy["plugin_context_max_chars"] == 8
    assert context_record["policy_global_max_chars"] == 8
    assert context_record["policy_max_chars"] is None
    assert context_record["max_chars"] == 8
    assert context_record["default_max_chars"] == 4000
    assert context_record["original_chars"] == 26
    assert context_record["prompt_context_truncated"] is True
    assert context_record["metadata"] == {"channel": "global"}


def test_prompt_context_policy_limits_ordered_plugin_context_generation():
    tmpdir = tempfile.mkdtemp()
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_code}\n{extra_context}\n{mutation_instructions}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={
            "plugin_context_order": ["SecondContextPlugin"],
            "plugin_context_limit": 1,
        },
    )
    prompt_db.record_result(parent_prompt.id, 0.0)

    class FirstContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "first plugin guidance"
        def prompt_context_metadata(self):
            return {"channel": "first"}

    class SecondContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "second plugin guidance"
        def prompt_context_metadata(self):
            return {"channel": "second"}

    with (
        patch("libreevolve.core.loop.build_llm", return_value=_llm()),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[FirstContextPlugin(), SecondContextPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    prompt = child["metadata"]["prompt"]
    plugin_context = child["metadata"]["plugin_context"]
    prompt_policy = child["metadata"]["prompt_diagnostics"]["prompt_context_policy"]

    assert "second plugin guidance" in prompt
    assert "first plugin guidance" not in prompt
    assert prompt_policy["plugin_context_limit"] == 1
    assert plugin_context[0]["plugin"] == "FirstContextPlugin"
    assert plugin_context[0]["emitted"] is False
    assert (
        plugin_context[0]["context_visibility"]
        == "not_selected_by_prompt_context_limit"
    )
    assert plugin_context[0]["metadata_visibility"] == "provenance_only"
    assert plugin_context[0]["pre_limit_prompt_context_chars"] > 0
    assert plugin_context[0]["prompt_context_chars"] == 0
    assert plugin_context[0]["prompt_context_limit_policy"] == {
        "schema": "libreevolve.plugin_context_limit_policy.v1",
        "source_limit": 1,
        "pre_limit_selected_count": 2,
        "selected_count": 1,
        "omitted_count": 1,
        "selected": False,
        "rank": 2,
        "selection_sha256": plugin_context[0]["prompt_context_limit_policy"][
            "selection_sha256"
        ],
    }
    assert len(
        plugin_context[0]["prompt_context_limit_policy"]["selection_sha256"]
    ) == 64
    assert plugin_context[1]["plugin"] == "SecondContextPlugin"
    assert plugin_context[1]["emitted"] is True
    assert plugin_context[1]["context_visibility"] == "prompt_visible"
    assert plugin_context[1]["prompt_context_limit_policy"]["selected"] is True
    assert plugin_context[1]["prompt_context_limit_policy"]["rank"] == 1
    assert (
        plugin_context[1]["prompt_context_limit_policy"]["selection_sha256"]
        == plugin_context[0]["prompt_context_limit_policy"]["selection_sha256"]
    )


def test_prompt_context_policy_ranks_plugin_context_by_terms_before_limit():
    tmpdir = tempfile.mkdtemp()
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_code}\n{extra_context}\n{mutation_instructions}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={
            "plugin_context_ranking_terms": ["matrix"],
            "plugin_context_limit": 1,
        },
    )
    prompt_db.record_result(parent_prompt.id, 0.0)

    class GenericContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "sorting guidance"

    class MatrixContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "matrix optimization guidance"

    with (
        patch("libreevolve.core.loop.build_llm", return_value=_llm()),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[GenericContextPlugin(), MatrixContextPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    prompt = child["metadata"]["prompt"]
    plugin_context = child["metadata"]["plugin_context"]
    prompt_policy = child["metadata"]["prompt_diagnostics"]["prompt_context_policy"]

    assert "matrix optimization guidance" in prompt
    assert "sorting guidance" not in prompt
    assert prompt_policy["plugin_context_ranking_terms"] == ["matrix"]
    assert plugin_context[0]["plugin"] == "GenericContextPlugin"
    assert plugin_context[0]["emitted"] is False
    assert plugin_context[0]["context_visibility"] == (
        "not_selected_by_prompt_context_limit"
    )
    assert plugin_context[0]["prompt_context_ranking_policy"]["score"] == 0
    assert plugin_context[0]["prompt_context_ranking_policy"]["rank"] == 2
    assert plugin_context[0]["prompt_context_ranking_policy"]["previous_rank"] == 1
    assert plugin_context[1]["plugin"] == "MatrixContextPlugin"
    assert plugin_context[1]["emitted"] is True
    ranking_policy = plugin_context[1]["prompt_context_ranking_policy"]
    assert ranking_policy["schema"] == "libreevolve.plugin_context_ranking_policy.v1"
    assert ranking_policy["ranking_terms"] == ["matrix"]
    assert ranking_policy["ranking_term_count"] == 1
    assert ranking_policy["candidate_count"] == 2
    assert ranking_policy["score"] == 1
    assert ranking_policy["rank"] == 1
    assert ranking_policy["previous_rank"] == 2
    assert len(ranking_policy["ranking_terms_sha256"]) == 64
    assert len(ranking_policy["ranking_sha256"]) == 64
    assert (
        plugin_context[1]["prompt_context_limit_policy"]["selected"] is True
    )


def test_prompt_context_policy_filters_plugin_context_by_terms():
    tmpdir = tempfile.mkdtemp()
    prompt_db = PromptDatabase(
        Path(tmpdir) / "prompts",
        templates=["{task}\n{parent_code}\n{extra_context}\n{mutation_instructions}"],
    )
    parent_prompt = prompt_db.select()
    prompt_db.mutate(
        parent_prompt.id,
        parent_prompt.template,
        generation=1,
        context_policy={
            "plugin_context_required_terms": ["matrix"],
            "plugin_context_excluded_terms": ["debug"],
        },
    )
    prompt_db.record_result(parent_prompt.id, 0.0)

    class MatrixContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "matrix optimization guidance"
        def prompt_context_metadata(self):
            return {"channel": "matrix"}

    class DebugContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "matrix debug scratch guidance"
        def prompt_context_metadata(self):
            return {"channel": "debug"}

    with (
        patch("libreevolve.core.loop.build_llm", return_value=_llm()),
        patch("libreevolve.core.loop.PromptDatabase", return_value=prompt_db),
    ):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[MatrixContextPlugin(), DebugContextPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    prompt = child["metadata"]["prompt"]
    plugin_context = child["metadata"]["plugin_context"]
    prompt_policy = child["metadata"]["prompt_diagnostics"]["prompt_context_policy"]

    assert "matrix optimization guidance" in prompt
    assert "matrix debug scratch guidance" not in prompt
    assert prompt_policy["plugin_context_required_terms"] == ["matrix"]
    assert prompt_policy["plugin_context_excluded_terms"] == ["debug"]
    assert plugin_context[0]["emitted"] is True
    assert plugin_context[0]["context_visibility"] == "prompt_visible"
    assert plugin_context[0]["prompt_context_term_policy"]["selected"] is True
    assert plugin_context[1]["emitted"] is False
    assert (
        plugin_context[1]["context_visibility"]
        == "not_selected_by_prompt_context_terms"
    )
    assert plugin_context[1]["metadata"] == {"channel": "debug"}
    term_policy = plugin_context[1]["prompt_context_term_policy"]
    assert term_policy["required_terms"] == ["matrix"]
    assert term_policy["excluded_terms"] == ["debug"]
    assert term_policy["matched_required_count"] == 1
    assert term_policy["matched_excluded_terms"] == ["debug"]
    assert term_policy["selected"] is False
    assert len(term_policy["selection_sha256"]) == 64


def test_loop_records_per_plugin_prompt_context():
    tmpdir = tempfile.mkdtemp()

    class ContextPlugin:
        __version__ = "0.3.0"

        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "[PLUGIN CONTEXT]\nPrefer the simple branch.\n"
        def prompt_context_metadata(self):
            return {"strategy": "static_guidance"}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[ContextPlugin()],
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    child = records[-1]
    plugin_context = child["metadata"]["plugin_context"]

    assert "[PLUGIN CONTEXT]" in child["metadata"]["prompt"]
    assert '"[PLUGIN CONTEXT]\\nPrefer the simple branch.\\n"' in child["metadata"]["prompt"]
    assert plugin_context[0]["plugin"] == "ContextPlugin"
    assert plugin_context[0]["module"] == __name__
    assert plugin_context[0]["version"] == {
        "status": "present",
        "source": "class",
        "value": "0.3.0",
    }
    assert manifest["runtime"]["plugin_state"]["loaded"][0]["version"] == {
        "status": "present",
        "source": "class",
        "value": "0.3.0",
    }
    assert plugin_context[0]["parent_id"] == child["parent_id"]
    assert plugin_context[0]["context"].startswith("[PLUGIN CONTEXT]\nPlugin: ContextPlugin")
    assert "Content-JSON:" in plugin_context[0]["context"]
    assert '"[PLUGIN CONTEXT]\\nPrefer the simple branch.\\n"' in plugin_context[0]["context"]
    assert plugin_context[0]["chars"] == len(plugin_context[0]["context"])
    assert plugin_context[0]["prompt_context_chars"] == len(plugin_context[0]["context"])
    assert plugin_context[0]["sha256"] == hashlib.sha256(
        plugin_context[0]["context"].encode("utf-8")
    ).hexdigest()
    assert plugin_context[0]["context_retention"]["retention_mode"] == "redacted"
    assert plugin_context[0]["context_retention"]["stored_chars"] == len(
        plugin_context[0]["context"]
    )
    assert plugin_context[0]["emitted"] is True
    assert plugin_context[0]["context_visibility"] == "prompt_visible"
    assert plugin_context[0]["metadata_visibility"] == "prompt_visible_context"
    assert plugin_context[0]["original_chars"] == len("[PLUGIN CONTEXT]\nPrefer the simple branch.\n")
    assert plugin_context[0]["context_redacted"] is False
    assert plugin_context[0]["context_truncated"] is False
    assert plugin_context[0]["metadata"] == {"strategy": "static_guidance"}
    assert plugin_context[0]["plugin_spec"]["status"] == "custom_plugin_signature_recorded"
    assert plugin_context[0]["plugin_spec"]["constructor_signature"]["parameter_count"] == 0
    assert plugin_context[0]["plugin_spec"]["parameter_policy"] == (
        "custom_constructor_signature_only_no_parameter_values"
    )


def test_loop_records_modular_plugin_static_strategy_metadata():
    tmpdir = tempfile.mkdtemp()

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                plugins=["modular"],
            ),
            plugins=[ModularPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    context_record = records[-1]["metadata"]["plugin_context"][0]
    metadata = context_record["metadata"]

    assert metadata["paper_inspiration"] == "ImprovEvolve"
    assert metadata["strategy_policy"] == "static_prompt_only"
    assert metadata["operation_selected"] == "static_modular_guidance"
    assert metadata["operation_executed"] is False
    assert metadata["interface_enforced"] is False
    assert metadata["described_operations"] == [
        "generate_config",
        "improve",
        "perturb",
    ]
    assert context_record["plugin_spec"] == {
        "plugin": "ModularPlugin",
        "module": "libreevolve.plugins.modular",
        "class": "libreevolve.plugins.modular.ModularPlugin",
        "index": 0,
        "instance_id": "plugin:0:libreevolve.plugins.modular.ModularPlugin",
        "version": {"status": "missing"},
        "configured_label": "modular",
        "source": "loaded_instance",
        "status": "ok",
        "schema": "libreevolve.plugin_spec.v1",
        "parameter_policy": "validated_builtin_constructor_parameters",
        "parameters": {},
    }


def test_plugin_prompt_context_metadata_can_be_provenance_only_without_prompt_text():
    tmpdir = tempfile.mkdtemp()

    class MetadataOnlyPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations): return ""
        def prompt_context_metadata(self):
            return {"state": "updated_without_prompt_text"}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[MetadataOnlyPlugin()],
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    context_record = child["metadata"]["plugin_context"][0]

    assert "metadata" in context_record
    assert context_record["metadata"] == {"state": "updated_without_prompt_text"}
    assert context_record["emitted"] is False
    assert context_record["context_visibility"] == "not_prompt_visible"
    assert context_record["metadata_visibility"] == "provenance_only"
    assert "context" not in context_record
    assert "updated_without_prompt_text" not in child["metadata"]["prompt"]


def test_retrieval_metadata_without_prompt_text_is_summarized_as_provenance_only():
    tmpdir = tempfile.mkdtemp()

    class RetrievalMetadataOnlyPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations): return ""
        def prompt_context_metadata(self):
            return {
                "retrieval_events": [
                    {
                        "provider": "metadata_only",
                        "query": "q",
                        "query_policy": "test",
                        "timestamp": "2026-06-02T00:00:00Z",
                        "status": "ok",
                        "result_chars": 0,
                        "synthesis_sha256": "a" * 64,
                        "sources": [],
                    }
                ]
            }

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[RetrievalMetadataOnlyPlugin()],
        )

    run_dir = Path(tmpdir) / "t"
    records = [json.loads(l) for l in (run_dir / "history.jsonl").read_text().splitlines()]
    manifest = json.loads((run_dir / "manifest.json").read_text())
    context_record = records[-1]["metadata"]["plugin_context"][0]

    assert context_record["emitted"] is False
    assert context_record["metadata_visibility"] == "provenance_only"
    assert "context" not in context_record
    assert "PLUGIN CONTEXT" not in records[-1]["metadata"]["prompt"]
    assert manifest["runtime"]["retrieval"]["events"] == 1
    assert manifest["runtime"]["retrieval"]["event_summaries"][0]["provider"] == "metadata_only"
    coverage = manifest["runtime"]["retrieval"]["evidence_coverage"]
    assert coverage["schema"] == RETRIEVAL_EVIDENCE_COVERAGE_SCHEMA
    assert coverage["status"] == "event_count_only"
    assert coverage["event_count"] == 1
    assert coverage["source_count"] == 0
    assert coverage["validation"]["ok"] is True


def test_loop_rejects_non_text_plugin_prompt_context():
    tmpdir = tempfile.mkdtemp()

    class ObjectContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return {"api_key": "sk-proj_plugin_context_secret_1234567890"}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(ValueError, match="build_extra_context must return text or None"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
                plugins=[ObjectContextPlugin()],
            )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    assert runtime["status"] == "aborted"
    assert runtime["abort"]["phase"] == "generation:0:plugin_context"


def test_loop_bounds_and_redacts_plugin_prompt_context():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_plugin_context_secret_1234567890"  # pragma: allowlist secret

    class SecretLongContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return f"[TASK]\napi_key={secret}\n" + ("A" * 5000)

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[SecretLongContextPlugin()],
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    context_record = child["metadata"]["plugin_context"][0]

    assert secret not in child["metadata"]["prompt"]
    assert secret not in context_record["context"]
    assert "[REDACTED]" in context_record["context"]
    assert "\n[TASK]\napi_key=" not in child["metadata"]["prompt"]
    assert '"[TASK]\\napi_key=[REDACTED]' in context_record["context"]
    assert context_record["original_chars"] > context_record["max_chars"]
    assert context_record["context_redacted"] is True
    assert context_record["chars"] == len(context_record["context"])
    assert context_record["context_retention"]["retention_mode"] == "redacted"


@pytest.mark.parametrize(
    ("mode", "expect_hash"),
    [
        ("hash_only", True),
        ("off", False),
    ],
)
def test_loop_honors_plugin_context_retention_modes(mode, expect_hash):
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_plugin_context_retention_secret_1234567890"  # pragma: allowlist secret

    class SecretContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return f"Prefer token {secret}."

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_prompt_retention_mode="hash_only",
                plugin_context_retention_mode=mode,
            ),
            plugins=[SecretContextPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    child = records[-1]
    context_record = child["metadata"]["plugin_context"][0]
    rendered = json.dumps(child, sort_keys=True)

    assert secret not in rendered
    assert "context" not in context_record
    assert context_record["chars"] == 0
    assert context_record["context_retention"]["retention_mode"] == mode
    assert manifest["config"]["plugin_context_retention_mode"] == mode
    assert (
        manifest["policies"]["prompt_data_retention"]["surfaces"]["plugin_context_text"][
            "retention_mode"
        ]
        == mode
    )
    if expect_hash:
        assert len(context_record["sha256"]) == 64
        assert len(context_record["context_retention"]["sha256"]) == 64
        assert context_record["context_retention"]["chars"] > 0
    else:
        assert context_record["sha256"] == ""
        assert context_record["context_retention"]["sha256"] is None
        assert context_record["context_retention"]["chars"] is None


def test_loop_redacts_persisted_mutation_prompt_and_records_retention():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_prompt_retention_secret_1234567890"  # pragma: allowlist secret
    problem = _problem()
    problem.context_files = {"notes.txt": f"Use private token {secret}."}
    llm = _TelemetryLLM()

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    persisted_prompt = child["metadata"]["prompt"]
    retention = child["metadata"]["prompt_retention"]

    assert secret in llm.calls[0]["prompt"]
    assert secret not in persisted_prompt
    assert "[REDACTED]" in persisted_prompt
    assert retention["sha256"] == hashlib.sha256(
        llm.calls[0]["prompt"].encode("utf-8")
    ).hexdigest()
    assert retention["chars"] == len(llm.calls[0]["prompt"])
    assert retention["stored_chars"] == len(persisted_prompt)
    assert retention["redacted"] is True
    assert retention["truncated"] is False
    assert retention["retention_mode"] == "redacted"
    assert retention["retention_policy"] == "redact_only_with_raw_sha256"


@pytest.mark.parametrize(
    ("mode", "expect_text", "expect_hash"),
    [
        ("full", True, True),
        ("hash_only", False, True),
        ("off", False, False),
    ],
)
def test_loop_honors_mutation_prompt_retention_modes(mode, expect_text, expect_hash):
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_prompt_mode_secret_1234567890"  # pragma: allowlist secret
    problem = _problem()
    problem.context_files = {"notes.txt": f"Use private token {secret}."}
    llm = _TelemetryLLM()

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_prompt_retention_mode=mode,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    persisted_prompt = child["metadata"]["prompt"]
    retention = child["metadata"]["prompt_retention"]

    assert secret in llm.calls[0]["prompt"]
    assert retention["retention_mode"] == mode
    assert retention["stored_chars"] == (len(persisted_prompt) if expect_text else 0)
    if expect_text:
        assert secret not in persisted_prompt
        assert "[REDACTED]" in persisted_prompt
        assert retention["chars"] == len(llm.calls[0]["prompt"])
    else:
        assert persisted_prompt is None
        assert secret not in json.dumps(child["metadata"])
    if expect_hash:
        assert retention["sha256"] == hashlib.sha256(
            llm.calls[0]["prompt"].encode("utf-8")
        ).hexdigest()
        assert retention["chars"] == len(llm.calls[0]["prompt"])
    else:
        assert retention["sha256"] is None
        assert retention["chars"] is None


@pytest.mark.parametrize(
    ("mode", "replacement", "expect_hash"),
    [
        ("hash_only", "[EXPLICIT_CONTEXT_RETAINED_AS_HASH]", True),
        ("off", "[EXPLICIT_CONTEXT_OMITTED_BY_RETENTION_POLICY]", False),
    ],
)
def test_loop_honors_explicit_context_retention_inside_persisted_prompts(
    mode,
    replacement,
    expect_hash,
):
    tmpdir = tempfile.mkdtemp()
    context_body = "private scheduler note for prompt only"
    problem = _problem()
    problem.context_files = {"notes.txt": context_body}
    llm = _TelemetryLLM()

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_prompt_retention_mode="redacted",
                explicit_context_retention_mode=mode,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    persisted_prompt = child["metadata"]["prompt"]
    retention = child["metadata"]["prompt_retention"]["explicit_context_retention"]

    assert context_body in llm.calls[0]["prompt"]
    assert context_body not in persisted_prompt
    assert replacement in persisted_prompt
    assert retention["retention_mode"] == mode
    assert retention["replacement_count"] == 1
    if expect_hash:
        assert retention["sha256"] == hashlib.sha256(
            prompt_sampler_context_for_test("notes.txt", context_body).encode("utf-8")
        ).hexdigest()
        assert retention["chars"] > 0
    else:
        assert retention["sha256"] is None
        assert retention["chars"] is None


def prompt_sampler_context_for_test(path: str, body: str) -> str:
    return "\n".join(
        [
            f"--- CONTEXT SOURCE: {path} ---",
            f"Content-Characters: {len(body)}",
            f"Original-Content-Characters: {len(body)}",
            "Content-JSON:",
            json.dumps(body),
        ]
    )


def test_loop_truncates_oversized_plugin_prompt_context():
    tmpdir = tempfile.mkdtemp()

    class LongContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "A" * 5000

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[LongContextPlugin()],
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    context_record = records[-1]["metadata"]["plugin_context"][0]

    assert context_record["original_chars"] == 5000
    assert context_record["max_chars"] == 4000
    assert context_record["context_truncated"] is True
    assert context_record["context_redacted"] is False
    assert context_record["chars"] == len(context_record["context"])
    assert "...<truncated>" in context_record["context"]


def test_rejects_plugin_prompt_context_metadata_with_unsafe_label():
    tmpdir = tempfile.mkdtemp()

    class BadContextLabelPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations): return ""
        def prompt_context_metadata(self):
            return {"safe": [{"bad\u200d": "value"}]}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(ValueError, match="display-safe metadata label"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
                plugins=[BadContextLabelPlugin()],
            )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    assert runtime["status"] == "aborted"
    assert runtime["abort"]["phase"] == "generation:0:plugin_context"
    assert runtime["abort"]["role"] == "plugin"
    assert runtime["abort"]["plugin_failure"]["hook"] == "prompt_context_metadata"
    assert runtime["abort"]["plugin_failure"]["plugin"] == "BadContextLabelPlugin"


def test_rejects_plugin_prompt_context_metadata_with_unsafe_value():
    tmpdir = tempfile.mkdtemp()

    class BadContextValuePlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations): return ""
        def prompt_context_metadata(self):
            return {"safe": [{"value": "bad\u202e"}]}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(ValueError, match="display-safe metadata value"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
                plugins=[BadContextValuePlugin()],
            )


def test_rejects_plugin_prompt_context_metadata_with_too_many_items():
    tmpdir = tempfile.mkdtemp()

    class ManyItemsContextMetadataPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations): return ""
        def prompt_context_metadata(self):
            return {"items": list(range(1001))}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(ValueError, match="metadata item count exceeds"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
                plugins=[ManyItemsContextMetadataPlugin()],
            )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    assert runtime["status"] == "aborted"
    assert runtime["abort"]["phase"] == "generation:0:plugin_context"
    assert runtime["abort"]["plugin_failure"]["hook"] == "prompt_context_metadata"


def test_rejects_plugin_prompt_context_metadata_with_excessive_nesting():
    tmpdir = tempfile.mkdtemp()
    nested: object = "ok"
    for _ in range(22):
        nested = {"nested": nested}

    class DeepContextMetadataPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations): return ""
        def prompt_context_metadata(self):
            return {"root": nested}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(ValueError, match="metadata nesting exceeds"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
                plugins=[DeepContextMetadataPlugin()],
            )


@pytest.mark.parametrize("metadata", [[{"status": "ok"}], "metadata", 1, True])
def test_rejects_non_mapping_plugin_prompt_context_metadata_returns(metadata):
    tmpdir = tempfile.mkdtemp()

    class BadContextShapePlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations): return ""
        def prompt_context_metadata(self):
            return metadata

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        with pytest.raises(ValueError, match="prompt_context_metadata must return a mapping"):
            evolve(
                _problem(),
                Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
                plugins=[BadContextShapePlugin()],
            )

    runtime = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())["runtime"]
    failure = runtime["abort"]["plugin_failure"]
    assert runtime["abort"]["phase"] == "generation:0:plugin_context"
    assert failure["plugin"] == "BadContextShapePlugin"
    assert failure["hook"] == "prompt_context_metadata"
    assert "prompt_context_metadata must return a mapping" in failure["message"]
    assert runtime["consumed"]["candidate_evaluations"] == 0


@pytest.mark.parametrize("metadata", [None, {}])
def test_empty_plugin_prompt_context_metadata_returns_are_accepted(metadata):
    tmpdir = tempfile.mkdtemp()

    class EmptyContextMetadataPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations): return ""
        def prompt_context_metadata(self):
            return metadata

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[EmptyContextMetadataPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    context_record = records[-1]["metadata"]["plugin_context"][0]
    assert context_record["plugin"] == "EmptyContextMetadataPlugin"
    assert context_record["emitted"] is False
    assert "metadata" not in context_record


def test_plugin_prompt_context_metadata_redacts_secret_values():
    tmpdir = tempfile.mkdtemp()

    class SecretContextValuePlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations): return ""
        def prompt_context_metadata(self):
            return {"note": "token: sk-proj_contextsecret1234567890"}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[SecretContextValuePlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    assert records[-1]["metadata"]["plugin_context"][0]["metadata"] == {
        "note": "token: [REDACTED]"
    }


def test_plugin_metadata_redacts_secret_keys_in_history_and_manifest():
    tmpdir = tempfile.mkdtemp()
    context_secret = "sk-proj_pluginmetakey_secret_1234567890"  # pragma: allowlist secret
    artifact_secret = "ghp_pluginartifactkey_secret_1234567890"  # pragma: allowlist secret
    nested_secret = "sk-proj_pluginnestedkey_secret_1234567890"  # pragma: allowlist secret
    long_key = "plugin_" + ("X" * 240)

    class SecretKeyMetadataPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations): return ""
        def prompt_context_metadata(self):
            return {
                f"api_key={context_secret}": "context",
                f"token={artifact_secret}": "context-second",
                "nested": {f"token={nested_secret}": "inner"},
                long_key: "large",
            }
        def run_artifacts_metadata(self):
            return {
                f"token={artifact_secret}": "artifact",
                "nested": {f"api_key={nested_secret}": "inner"},
            }

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[SecretKeyMetadataPlugin()],
        )

    run_dir = Path(tmpdir) / "t"
    records = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    context_metadata = records[-1]["metadata"]["plugin_context"][0]["metadata"]
    manifest = json.loads((run_dir / "manifest.json").read_text())
    artifact_metadata = manifest["runtime"]["plugin_artifacts"][0]["metadata"]
    serialized = json.dumps(
        {"history": context_metadata, "manifest": artifact_metadata},
        sort_keys=True,
    )

    assert context_secret not in serialized
    assert artifact_secret not in serialized
    assert nested_secret not in serialized
    context_key = next(
        key for key in context_metadata if key.startswith("redacted_metadata_key")
    )
    context_second_key = next(
        key
        for key in context_metadata
        if key.endswith(
            "#sha256:"
            + hashlib.sha256(f"token={artifact_secret}".encode("utf-8")).hexdigest()[:12]
        )
    )
    artifact_key = next(
        key for key in artifact_metadata if key.startswith("redacted_metadata_key")
    )
    context_nested_key = next(
        key
        for key in context_metadata["nested"]
        if key.startswith("redacted_metadata_key")
    )
    artifact_nested_key = next(
        key
        for key in artifact_metadata["nested"]
        if key.startswith("redacted_metadata_key")
    )
    long_safe_key = next(key for key in context_metadata if key.startswith("plugin_"))
    assert context_key.endswith(
        "#sha256:"
        + hashlib.sha256(f"api_key={context_secret}".encode("utf-8")).hexdigest()[:12]
    )
    assert artifact_key.endswith(
        "#sha256:"
        + hashlib.sha256(f"token={artifact_secret}".encode("utf-8")).hexdigest()[:12]
    )
    assert context_second_key != context_key
    assert context_metadata[context_second_key] == "context-second"
    assert context_nested_key.endswith(
        "#sha256:"
        + hashlib.sha256(f"token={nested_secret}".encode("utf-8")).hexdigest()[:12]
    )
    assert artifact_nested_key.endswith(
        "#sha256:"
        + hashlib.sha256(f"api_key={nested_secret}".encode("utf-8")).hexdigest()[:12]
    )
    assert long_safe_key.endswith(
        "#sha256:" + hashlib.sha256(long_key.encode("utf-8")).hexdigest()[:12]
    )
    assert len(long_safe_key) == 160
    assert context_metadata[context_key] == "context"
    assert artifact_metadata[artifact_key] == "artifact"


def test_accepts_plugin_prompt_context_metadata_with_ordinary_unicode_label():
    tmpdir = tempfile.mkdtemp()

    class UnicodeContextLabelPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations): return ""
        def prompt_context_metadata(self):
            return {"caf\u00e9": "ok"}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[UnicodeContextLabelPlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    assert records[-1]["metadata"]["plugin_context"][0]["metadata"] == {"caf\u00e9": "ok"}


def test_manifest_summarizes_retrieval_events():
    tmpdir = tempfile.mkdtemp()
    run_dir = Path(tmpdir) / "t"
    plugin = DeepResearchPlugin(
        search_fn=lambda q: {
            "status": "ok",
            "synthesis": "retrieved context",
            "sources": [{"id": "paper-1"}, {"id": "paper-2"}],
            "transport": {
                "authenticated_transport": True,
                "status_code": 200,
                "payload_bytes": 123,
                "payload_observed_bytes": 123,
                "payload_limit_bytes": 1000,
                "payload_truncated": False,
                "oversized_response": False,
                "payload_sha256": "a" * 64,
                "request": {"scheme": "https", "host": "example.test"},
                "final": {"scheme": "https", "host": "example.test"},
                "redirected": False,
            },
        },
        cache_dir=run_dir / "plugin_artifacts" / "deep_research",
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[plugin],
        )

    manifest = json.loads((run_dir / "manifest.json").read_text())
    retrieval = manifest["runtime"]["retrieval"]
    assert retrieval["events"] == 1
    assert retrieval["by_plugin"]["DeepResearchPlugin"] == {
        "events": 1,
        "ok": 1,
        "empty": 0,
        "error": 0,
        "sources": 2,
    }
    summary = retrieval["event_summaries"][0]
    assert summary["plugin"] == "DeepResearchPlugin"
    assert summary["provider"] == "custom"
    assert summary["status"] == "ok"
    assert summary["query_policy"] == "best_program_code_metrics_v1"
    assert summary["query_inputs"]["policy"] == "best_program_code_metrics_v1"
    assert summary["query_inputs"]["fitness"] == 1.0
    assert summary["query_inputs"]["metric_names"] == ["score"]
    assert isinstance(summary["query_inputs"]["code_terms"], list)
    assert summary["source_count"] == 2
    assert summary["source_metadata"] == {
        "provided": True,
        "input_count": 2,
        "retained_count": 2,
        "dropped_count": 0,
        "truncated": False,
        "redacted": False,
        "max_sources": 5,
        "max_field_chars": 300,
        "content_snapshot_count": 0,
        "max_content_snapshot_chars": 1200,
    }
    assert summary["synthesis_sha256"]
    assert summary["trust_policy"] == "untrusted_evidence_v1"
    assert summary["prompt_boundary"] == "begin_end_untrusted_retrieval_evidence"
    assert summary["authoritative"] is False
    assert summary["cache"]["mode"] == "cached"
    assert summary["cache"]["hit"] is False
    assert len(summary["cache"]["key"]) == 64
    assert len(summary["cache"]["snapshot_sha256"]) == 64
    assert summary["transport"] == {
        "authenticated_transport": True,
        "status_code": 200,
        "payload_bytes": 123,
        "payload_observed_bytes": 123,
        "payload_limit_bytes": 1000,
        "payload_truncated": False,
        "oversized_response": False,
        "payload_sha256": "a" * 64,
        "request_scheme": "https",
        "request_host": "example.test",
        "final_scheme": "https",
        "final_host": "example.test",
        "redirected": False,
    }
    coverage = retrieval["evidence_coverage"]
    assert coverage["schema"] == RETRIEVAL_EVIDENCE_COVERAGE_SCHEMA
    assert coverage["status"] == "bounded_metadata_or_snapshot_evidence"
    assert coverage["event_count"] == 1
    assert coverage["ok_event_count"] == 1
    assert coverage["source_count"] == 2
    assert coverage["transport_policy_count"] == 1
    assert coverage["payload_artifact_policy_count"] == 1
    assert coverage["source_grounding_policy_count"] == 1
    assert coverage["source_content_trust_policy_count"] == 1
    assert coverage["source_ranking_provenance_count"] == 1
    assert coverage["evidence_boundary_policy_count"] == 1
    assert coverage["context_audit_policy_count"] == 1
    assert coverage["raw_provider_payload_retained"] is False
    assert coverage["raw_source_payload_retained"] is False
    assert coverage["semantic_source_verification_ready"] is False
    assert coverage["semantic_source_ranking_ready"] is False
    assert coverage["learned_ranking_ready"] is False
    assert coverage["external_source_scoring_ready"] is False
    assert coverage["tls_decision_replay_ready"] is False
    assert coverage["full_retrieval_replay_ready"] is False
    assert coverage["validation"]["schema"] == (
        RETRIEVAL_EVIDENCE_COVERAGE_VALIDATION_SCHEMA
    )
    assert coverage["validation"]["ok"] is True
    overclaim = copy.deepcopy(coverage)
    overclaim["semantic_source_verification_ready"] = True
    overclaim.pop("validation")
    invalid = validate_retrieval_evidence_coverage(overclaim)
    assert invalid["ok"] is False
    assert any(
        issue["code"] == "semantic_source_verification_overclaim"
        for issue in invalid["issues"]
    )
    ranking_overclaim = copy.deepcopy(coverage)
    ranking_overclaim["semantic_source_ranking_ready"] = True
    ranking_overclaim["learned_ranking_ready"] = True
    ranking_overclaim["external_source_scoring_ready"] = True
    ranking_overclaim["limitations"].remove("query_overlap_not_external_source_scoring")
    ranking_overclaim.pop("validation")
    invalid_ranking = validate_retrieval_evidence_coverage(ranking_overclaim)
    assert invalid_ranking["ok"] is False
    ranking_issue_codes = {issue["code"] for issue in invalid_ranking["issues"]}
    assert "semantic_source_ranking_overclaim" in ranking_issue_codes
    assert "learned_ranking_overclaim" in ranking_issue_codes
    assert "external_source_scoring_overclaim" in ranking_issue_codes
    assert "missing_limitation" in ranking_issue_codes
    [artifact] = manifest["runtime"]["plugin_artifacts"]
    metadata = artifact["metadata"]
    assert artifact["plugin"] == "DeepResearchPlugin"
    assert metadata["artifact_kind"] == "deep_research_cache_snapshots"
    assert metadata["status"] == "ok"
    assert metadata["schema"] == "deep_research_cache_v1"
    assert metadata["cache_mode"] == "cached"
    assert metadata["snapshot_count"] == 1
    assert metadata["retained_snapshot_count"] == 1
    assert metadata["provider_result_snapshot_count"] == 1
    assert len(metadata["provider_result_snapshots_sha256"]) == 64
    assert metadata["aggregate_sha256"]
    assert len(metadata["snapshots"]) == 1
    assert metadata["snapshots"][0]["file"].endswith(".json")
    assert metadata["snapshots"][0]["sha256"]


def test_manifest_summarizes_retrieval_error_types():
    tmpdir = tempfile.mkdtemp()
    plugin = DeepResearchPlugin(
        search_fn=lambda q: {
            "status": "error",
            "error_type": "network_error",
            "error": "offline",
        }
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[plugin],
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    summary = manifest["runtime"]["retrieval"]["event_summaries"][0]
    assert summary["status"] == "error"
    assert summary["error_type"] == "network_error"
    assert summary["error"] == "offline"


def test_retrieval_query_url_is_not_persisted_raw_in_history_or_manifest():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_queryurl_loop_secret_1234567890"  # pragma: allowlist secret
    plugin = DeepResearchPlugin(
        search_fn=lambda q: {
            "status": "ok",
            "query_url": f"https://example.test/search?api_key={secret}&q=private",
            "synthesis": "retrieved context",
            "sources": [
                {
                    "title": "source",
                    "summary": f"source summary token={secret}",
                }
            ],
        }
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[plugin],
        )

    run_dir = Path(tmpdir) / "t"
    history_text = (run_dir / "history.jsonl").read_text(encoding="utf-8")
    manifest_text = (run_dir / "manifest.json").read_text(encoding="utf-8")
    child = json.loads(history_text.splitlines()[1])
    plugin_metadata = child["metadata"]["plugin_context"][0]["metadata"]
    event = plugin_metadata["retrieval_events"][0]
    active_context = plugin_metadata["active_context"]

    assert "query_url" not in event
    assert event["request_url"]["sanitized_url"] == "https://example.test/search"
    assert event["request_url"]["query_param_count"] == 2
    assert len(event["request_url"]["raw_url_sha256"]) == 64
    assert active_context["schema"] == "libreevolve.deep_research_active_context.v1"
    assert active_context["event_index"] == event["event_index"]
    assert active_context["synthesis_sha256"] == event["synthesis_sha256"]
    assert active_context["raw_result_sha256"] == event["raw_result_sha256"]
    assert active_context["result_source_kind"] == "dict"
    assert len(active_context["query_sha256"]) == 64
    assert "query" not in active_context
    assert "request_url" not in active_context
    ranking = active_context["source_ranking"]
    assert ranking["relevance_policy"] == "query_term_overlap_audit_v1"
    assert len(ranking["query_relevance_scores_sha256"]) == 64
    assert ranking["retained_source_count"] == 1
    snapshot = event["sources"][0]["content_snapshot"]
    assert snapshot["schema"] == "libreevolve.retrieval_source_content_snapshot.v1"
    assert snapshot["field"] == "summary"
    assert "[REDACTED]" in snapshot["text"]
    assert secret not in snapshot["text"]
    assert len(snapshot["raw_sha256"]) == 64
    assert len(snapshot["stored_sha256"]) == 64
    relevance = event["sources"][0]["query_relevance"]
    assert relevance["policy"] == "query_term_overlap_audit_v1"
    assert relevance["audit_only"] is True
    assert relevance["affects_order"] is False
    assert 0.0 <= relevance["score"] <= 1.0
    assert secret not in history_text
    assert "private" not in history_text
    assert secret not in manifest_text
    assert "api_key" not in manifest_text


def test_deep_research_query_uses_problem_task_and_context_in_evolve():
    tmpdir = tempfile.mkdtemp()
    calls = []
    problem = _problem()
    problem.task_description = "Optimize scheduling fairness for latency sensitive kernels."
    problem.context_files = {
        "notes.md": "Beam priority queues guide scheduler design."
    }
    plugin = DeepResearchPlugin(search_fn=lambda q: calls.append(q) or "retrieved context")

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            problem,
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[plugin],
        )

    run_dir = Path(tmpdir) / "t"
    child = json.loads((run_dir / "history.jsonl").read_text().splitlines()[1])
    event = child["metadata"]["plugin_context"][0]["metadata"]["retrieval_events"][0]

    assert "task optimize scheduling fairness latency sensitive kernels" in calls[0]
    assert "context notes beam priority queues guide scheduler design" in calls[0]
    assert event["query_inputs"]["query_context_policy"] == (
        "task_and_context_term_overlap_v1"
    )
    assert event["query_inputs"]["task_terms"] == [
        "optimize",
        "scheduling",
        "fairness",
        "latency",
        "sensitive",
        "kernels",
    ]
    assert event["query_inputs"]["context_terms"] == [
        "notes",
        "beam",
        "priority",
        "queues",
        "guide",
        "scheduler",
        "design",
    ]
    assert len(event["query_inputs"]["context_sha256"]) == 64


def test_deep_research_query_uses_local_paper_context_in_evolve():
    tmpdir = tempfile.mkdtemp()
    calls = []
    problem = _problem()
    problem.local_papers = [
        {
            "id": "1504.04909",
            "title": "MAP_Elites",
            "url": "https://arxiv.org/pdf/1504.04909.pdf",
            "file": "papers/1504.04909__MAP_Elites.pdf",
            "sha256": "0" * 64,
            "ok": True,
            "bytes": 123,
        }
    ]
    problem.initial_programs = ["x=1\ndef map_elites_archive():\n    return 1\n"]
    plugin = DeepResearchPlugin(search_fn=lambda q: calls.append(q) or "retrieved context")

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            problem,
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[plugin],
        )

    run_dir = Path(tmpdir) / "t"
    child = json.loads((run_dir / "history.jsonl").read_text().splitlines()[1])
    event = child["metadata"]["plugin_context"][0]["metadata"]["retrieval_events"][0]

    assert "papers map elites" in calls[0]
    assert event["query_inputs"]["local_paper_policy"] == "manifest_title_overlap_v1"
    assert event["query_inputs"]["local_paper_terms"][:2] == ["map", "elites"]
    assert event["query_inputs"]["local_paper_count"] == 1
    assert event["query_inputs"]["local_paper_selected_count"] == 1
    assert len(event["query_inputs"]["local_paper_corpus_sha256"]) == 64


def test_deep_research_query_uses_recent_hypothesis_context_in_evolve():
    tmpdir = tempfile.mkdtemp()
    calls = []
    problem = _problem()
    plugin = DeepResearchPlugin(
        search_fn=lambda q: calls.append(q) or "retrieved context",
        search_every=1,
    )
    llm = _llm()
    llm.generate.side_effect = [
        (
            "IDEA: Add a tile cache.\n"
            "RATIONALE: Reduce duplicate matrix products.\n"
            "HYPOTHESIS: Tile cache improves matrix rank search.\n"
            "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE",
            0,
        ),
        ("<<<SEARCH\nx=2\n===\nx=3\n>>>REPLACE", 0),
    ]

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(
                max_generations=2,
                log_dir=tmpdir,
                problem_name="t",
                capture_proposal_metadata=True,
            ),
            plugins=[plugin],
        )

    run_dir = Path(tmpdir) / "t"
    history_rows = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    second_child = history_rows[2]
    event = second_child["metadata"]["plugin_context"][0]["metadata"]["retrieval_events"][-1]

    assert len(calls) == 2
    assert "hypotheses tile cache improves matrix rank search" in calls[1]
    assert event["query_inputs"]["hypothesis_context_policy"] == (
        "recent_proposal_hypothesis_terms_v1"
    )
    assert event["query_inputs"]["hypothesis_terms"][:6] == [
        "tile",
        "cache",
        "improves",
        "matrix",
        "rank",
        "search",
    ]
    assert event["query_inputs"]["hypothesis_count"] == 1
    assert len(event["query_inputs"]["hypothesis_context_sha256"]) == 64


def test_deep_research_query_uses_recent_failure_context_in_evolve():
    tmpdir = tempfile.mkdtemp()
    calls = []
    problem = _problem(
        """
def evaluate(c):
    if "x=2" in c:
        return {
            "score": 0.5,
            "is_valid": False,
            "error": "validator timeout branch bound",
        }
    return {"score": 1.0, "is_valid": True}
"""
    )
    plugin = DeepResearchPlugin(
        search_fn=lambda q: calls.append(q) or "retrieved context",
        search_every=1,
    )
    llm = _llm()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        ("<<<SEARCH\nx=1\n===\nx=3\n>>>REPLACE", 0),
    ]

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(max_generations=2, log_dir=tmpdir, problem_name="t"),
            plugins=[plugin],
        )

    run_dir = Path(tmpdir) / "t"
    history_rows = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    second_child = history_rows[2]
    event = second_child["metadata"]["plugin_context"][0]["metadata"]["retrieval_events"][-1]

    assert len(calls) == 2
    assert "failures invalid evaluation malformed metrics" in calls[1]
    assert event["query_inputs"]["failure_context_policy"] == "recent_failure_terms_v1"
    assert event["query_inputs"]["failure_terms"][:4] == [
        "invalid",
        "evaluation",
        "malformed",
        "metrics",
    ]
    assert event["query_inputs"]["failure_count"] == 1
    assert len(event["query_inputs"]["failure_context_sha256"]) == 64


def test_manifest_summarizes_plugin_artifacts_after_first_completed_generation(tmp_path):
    plugin = TTTRLPlugin(train_every=1, log_dir=str(tmp_path / "run" / "plugin_artifacts" / "ttt_rl"))
    backend = MagicMock()
    backend.name = "artifact/model"
    backend.api_mode = None
    backend.generate.return_value = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    llm = LLMEnsemble([backend])

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=str(tmp_path), problem_name="run"),
            plugins=[plugin],
        )

    manifest = json.loads((tmp_path / "run" / "manifest.json").read_text())
    artifact = manifest["runtime"]["plugin_artifacts"][0]
    assert artifact["plugin"] == "TTTRLPlugin"
    assert artifact["module"] == "libreevolve.plugins.ttt_rl"
    assert artifact["index"] == 0
    metadata = artifact["metadata"]
    assert metadata["reward_policy"] == "max(0.0, raw_score)"
    assert metadata["exported_examples"] >= 1
    assert metadata["path"].endswith("plugin_artifacts\\ttt_rl\\grpo_data.jsonl") or metadata[
        "path"
    ].endswith("plugin_artifacts/ttt_rl/grpo_data.jsonl")
    assert metadata["sha256"]
    assert metadata["bytes"] > 0
    runtime_artifacts = manifest["runtime"]["artifacts"]
    assert manifest["runtime"]["history"]["programs_logged"] == 2
    assert runtime_artifacts["history.jsonl"]["exists"] is True
    assert runtime_artifacts["history.jsonl"]["sha256"]
    assert runtime_artifacts["history.jsonl"]["hash_scope"] == "file_bytes"
    assert runtime_artifacts["llm_calls.jsonl"]["exists"] is True
    assert runtime_artifacts["llm_calls.jsonl"]["sha256"]
    assert runtime_artifacts["plugin_artifacts"]["exists"] is True
    assert runtime_artifacts["plugin_artifacts"]["kind"] == "directory"
    assert runtime_artifacts["plugin_artifacts"]["tree_hash_status"] == "ok"
    assert runtime_artifacts["plugin_artifacts"]["tree_hash"]


def test_ttt_rl_loop_export_cadence_and_final_manifest_flush(tmp_path):
    short_plugin = TTTRLPlugin(
        train_every=2,
        log_dir=str(tmp_path / "short" / "plugin_artifacts" / "ttt_rl"),
    )
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=str(tmp_path), problem_name="short"),
            plugins=[short_plugin],
        )

    short_manifest = json.loads((tmp_path / "short" / "manifest.json").read_text())
    short_artifact = short_manifest["runtime"]["plugin_artifacts"][0]["metadata"]
    assert short_artifact["queued_examples"] == 1
    assert short_artifact["pending_examples"] == 0
    assert short_artifact["exported_examples"] == 1
    assert short_artifact["finalization_policy"] == "flush_pending_examples_before_artifact_metadata"
    assert short_artifact["path"].endswith("grpo_data.jsonl")

    full_plugin = TTTRLPlugin(
        train_every=2,
        log_dir=str(tmp_path / "full" / "plugin_artifacts" / "ttt_rl"),
    )
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=2, log_dir=str(tmp_path), problem_name="full"),
            plugins=[full_plugin],
        )

    full_manifest = json.loads((tmp_path / "full" / "manifest.json").read_text())
    full_artifact = full_manifest["runtime"]["plugin_artifacts"][0]["metadata"]
    assert full_artifact["queued_examples"] == 2
    assert full_artifact["pending_examples"] == 0
    assert full_artifact["exported_examples"] == 2
    assert full_artifact["path"].endswith("grpo_data.jsonl")


def test_loop_renders_full_mode_prompt_instructions():
    tmpdir = tempfile.mkdtemp()
    llm = _llm("x=2")
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_mode="full",
            ),
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert child["metadata"]["mutation_mode"] == "full"
    assert "Mutation mode: full" in child["metadata"]["prompt"]
    assert "Return full replacement code, not SEARCH/REPLACE diffs." in child["metadata"]["prompt"]


def test_meta_prompt_evolution_adds_mutated_prompt_template():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        (
            "[SYSTEM]\n{task}\n{context}\n{parent_score}\n{parent_metrics}\n"
            "{parent_feedback}\n{parent_code}\n{inspirations}\n{extra_context}\n"
            "{recent_failures}\n{mutation_mode}\n{mutation_instructions}",
            0,
        ),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(
            max_generations=1,
            log_dir=tmpdir,
            problem_name="t",
            meta_prompt_evolution=True,
            meta_prompt_interval=1,
        ))

    events = [
        json.loads(l)["event"]
        for l in (Path(tmpdir) / "t" / "prompt_history.jsonl").read_text().splitlines()
    ]
    assert events.count("add") == 2


def test_meta_prompt_evolution_accepts_context_policy_json_response():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    mutated_template = (
        "[SYSTEM]\n{task}\n{context}\n{parent_score}\n{parent_metrics}\n"
        "{parent_feedback}\n{parent_code}\n{inspirations}\n{extra_context}\n"
        "{recent_failures}\n{mutation_mode}\n{mutation_instructions}"
    )
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        (
            json.dumps(
                {
                    "schema": "libreevolve.prompt_mutation_response.v1",
                    "template": mutated_template,
                    "context_policy": {
                        "disabled_sections": ["recent_failures"],
                        "section_priorities": {"extra_context": 1},
                        "mutation_instruction_variant": "exploratory",
                        "mutation_instruction_include_example": False,
                        "proposal_metadata_enabled": True,
                        "parent_code_paths": ["main.py"],
                        "parent_code_required_terms": ["solver"],
                        "parent_code_excluded_terms": ["debug"],
                        "parent_code_ranking_terms": ["matrix"],
                        "parent_code_order_policy": "task_term_ranked",
                        "parent_code_limit": 2,
                        "parent_code_max_chars_by_path": {"main.py": 120},
                        "parent_code_max_chars": 240,
                        "parent_code_truncation": "head_tail",
                        "inspiration_strategy": "recency",
                        "inspiration_required_metric": "latency",
                        "inspiration_excluded_metrics": ["debug_score"],
                        "inspiration_fitness_threshold": {"min": 0.25},
                        "inspiration_metric_thresholds": {
                            "latency": {"max": 0.5},
                        },
                        "inspiration_metric_ranking": {
                            "metric": "latency",
                            "direction": "minimize",
                        },
                        "feedback_sections": ["stage_summary", "llm_grader_feedback"],
                        "feedback_section_order": [
                            "llm_grader_feedback",
                            "stage_summary",
                        ],
                        "feedback_section_max_chars_by_name": {
                            "llm_grader_feedback": 80,
                        },
                        "llm_feedback_fields": ["score", "feedback"],
                        "llm_feedback_max_chars_by_field": {"feedback": 100},
                        "proposal_fields": ["idea", "rationale"],
                        "proposal_max_chars_by_field": {"idea": 90},
                        "stage_summary_fields": ["name", "status"],
                        "stage_summary_max_chars_by_field": {"name": 80},
                        "execution_output_fields": ["stderr", "error"],
                        "execution_output_max_chars_by_field": {"stderr": 100},
                        "sample_retry_fields": ["status", "error"],
                        "sample_retry_max_chars_by_field": {"error": 80},
                        "program_output_fields": ["source", "sha256"],
                        "program_output_max_chars_by_field": {"source": 40},
                        "validator_artifact_fields": ["path", "sha256"],
                        "validator_artifact_max_chars_by_field": {"path": 80},
                        "validator_artifact_content_fields": ["status", "content"],
                        "validator_artifact_content_mode": "bounded_file",
                        "validator_artifact_content_max_bytes": 512,
                        "validator_artifact_content_max_chars": 200,
                        "validator_skipped_artifact_fields": ["reason", "sha256"],
                        "validator_skipped_artifact_max_chars_by_field": {
                            "reason": 40,
                        },
                        "validator_diagnostic_groups": ["syntax_errors"],
                        "validator_metadata_keys": ["score_detail"],
                        "validator_metadata_limit": 1,
                        "validator_metadata_max_chars_by_key": {
                            "score_detail": 80,
                        },
                        "evaluator_path_fields": [
                            "validate_path",
                            "validate_path_scope",
                        ],
                        "evaluator_path_max_chars_by_field": {
                            "validate_path": 80,
                        },
                        "evaluator_dependency_fields": ["policy", "file_paths"],
                        "evaluator_dependency_max_chars_by_field": {
                            "file_paths": 120,
                        },
                        "evaluator_stage_fields": ["name", "validate_path"],
                        "evaluator_stage_max_chars_by_field": {
                            "validate_path": 100,
                        },
                        "evaluator_workspace_fields": [
                            "primary_file",
                            "file_count",
                        ],
                        "evaluator_workspace_max_chars_by_field": {
                            "primary_file": 80,
                        },
                        "syntax_error_fields": ["path", "message"],
                        "syntax_error_max_chars_by_field": {"message": 80},
                        "metric_bound_fields": ["metric", "value"],
                        "metric_bound_max_chars_by_field": {"value": 40},
                        "configured_stage_check_fields": [
                            "name",
                            "threshold_passed",
                        ],
                        "configured_stage_check_max_chars_by_field": {
                            "name": 60,
                        },
                        "stage_metric_threshold_fields": ["metric", "passed"],
                        "stage_metric_threshold_max_chars_by_field": {
                            "metric": 40,
                        },
                        "artifact_output_check_fields": ["type", "reason"],
                        "artifact_output_check_max_chars_by_field": {
                            "reason": 50,
                        },
                        "malformed_metric_fields": ["reason"],
                        "malformed_metric_max_chars_by_field": {"reason": 50},
                        "materialization_error_fields": ["message"],
                        "materialization_error_max_chars_by_field": {"message": 70},
                        "metric_aggregation_fields": ["metric_aggregation"],
                        "metric_aggregation_max_chars_by_field": {
                            "metric_aggregation": 90,
                        },
                        "synthetic_metric_fields": ["policy", "penalty"],
                        "synthetic_metric_max_chars_by_field": {"policy": 50},
                        "execution_diagnostic_groups": ["stdin"],
                        "validator_boundary_fields": [
                            "policy",
                            "resource_limits",
                        ],
                        "validator_boundary_max_chars_by_field": {
                            "policy": 64,
                        },
                        "validator_budget_fields": ["policy", "exhausted"],
                        "validator_budget_max_chars_by_field": {"policy": 44},
                        "validator_env_fields": ["policy", "provided_keys"],
                        "validator_env_max_chars_by_field": {
                            "provided_keys": 120,
                        },
                        "validator_resource_limit_fields": [
                            "wall_clock_timeout",
                            "process_count",
                        ],
                        "validator_resource_limit_max_chars_by_field": {
                            "memory": 48,
                        },
                        "validator_stdin_fields": ["policy", "sha256"],
                        "validator_stdin_max_chars_by_field": {"source": 72},
                        "diagnostic_output_fields": ["encoding", "redacted"],
                        "diagnostic_output_max_chars_by_field": {
                            "encoding": 60,
                        },
                        "timeout_cleanup_fields": ["method", "status"],
                        "timeout_cleanup_max_chars_by_field": {"error": 84},
                        "prompt_format_weights": {"tone": [1.0, 2.0]},
                        "context_source_paths": ["docs/a.md"],
                        "context_source_required_terms": ["matrix"],
                        "context_source_excluded_terms": ["debug"],
                        "context_source_ranking_terms": ["sorting"],
                        "context_source_limit": 1,
                        "context_source_max_chars": 256,
                        "context_source_truncation": "head_tail",
                        "context_source_order_policy": "task_term_ranked",
                        "recent_failure_limit": 1,
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
                        "recent_failure_max_chars_by_field": {"error": 64},
                        "inspiration_limit": 2,
                        "inspiration_sample_count": 3,
                        "extra_context_max_chars": 500,
                        "plugin_context_enabled": False,
                        "plugin_context_excluded_labels": ["BlockedContextPlugin"],
                        "plugin_context_required_terms": ["matrix"],
                        "plugin_context_excluded_terms": ["debug"],
                        "plugin_context_ranking_terms": ["matrix"],
                        "plugin_context_limit": 1,
                        "plugin_context_max_chars": 256,
                        "plugin_context_order": ["SecondContextPlugin"],
                    },
                }
            ),
            0,
        ),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                meta_prompt_evolution=True,
                meta_prompt_interval=1,
            ),
        )

    events = [
        json.loads(l)
        for l in (Path(tmpdir) / "t" / "prompt_history.jsonl").read_text().splitlines()
    ]
    mutated_add = [event for event in events if event["event"] == "add"][-1]
    assert mutated_add["program"]["template"] == mutated_template
    assert mutated_add["program"]["context_policy"] == {
        "schema": "libreevolve.prompt_context_policy.v1",
        "disabled_sections": ["recent_failures"],
        "section_priorities": {"extra_context": 1},
        "mutation_instruction_variant": "exploratory",
        "mutation_instruction_include_example": False,
        "proposal_metadata_enabled": True,
        "parent_metric_names": None,
        "parent_metrics_max_chars_by_name": {},
        "parent_code_paths": ["main.py"],
        "parent_code_required_terms": ["solver"],
        "parent_code_excluded_terms": ["debug"],
        "parent_code_ranking_terms": ["matrix"],
        "parent_code_order_policy": "task_term_ranked",
        "parent_code_limit": 2,
        "parent_code_max_chars_by_path": {"main.py": 120},
        "parent_code_max_chars": 240,
        "parent_code_truncation": "head_tail",
        "inspiration_strategy": "recency",
        "inspiration_required_metric": "latency",
        "inspiration_excluded_metrics": ["debug_score"],
        "inspiration_fitness_threshold": {"min": 0.25, "max": None},
        "inspiration_metric_thresholds": {"latency": {"min": None, "max": 0.5}},
        "inspiration_metric_ranking": {
            "metric": "latency",
            "direction": "minimize",
        },
        "feedback_sections": ["stage_summary", "llm_grader_feedback"],
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
        "feedback_section_max_chars_by_name": {"llm_grader_feedback": 80},
        "llm_feedback_fields": ["score", "feedback"],
        "llm_feedback_max_chars_by_field": {"feedback": 100},
        "proposal_fields": ["idea", "rationale"],
        "proposal_max_chars_by_field": {"idea": 90},
        "stage_summary_fields": ["name", "status"],
        "stage_summary_max_chars_by_field": {"name": 80},
        "execution_output_fields": ["stderr", "error"],
        "execution_output_max_chars_by_field": {"stderr": 100},
        "sample_retry_fields": ["status", "error"],
        "sample_retry_max_chars_by_field": {"error": 80},
        "program_output_fields": ["source", "sha256"],
        "program_output_max_chars_by_field": {"source": 40},
        "validator_artifact_fields": ["path", "sha256"],
        "validator_artifact_max_chars_by_field": {"path": 80},
        "validator_artifact_content_fields": ["status", "content"],
        "validator_artifact_content_mode": "bounded_file",
        "validator_artifact_content_max_bytes": 512,
        "validator_artifact_content_max_chars": 200,
        "validator_skipped_artifact_fields": ["reason", "sha256"],
        "validator_skipped_artifact_max_chars_by_field": {"reason": 40},
        "validator_diagnostic_groups": ["syntax_errors"],
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
        "execution_diagnostic_groups": ["stdin"],
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
        "prompt_format_weights": {"tone": [1.0, 2.0]},
        "context_source_paths": ["docs/a.md"],
        "context_source_required_terms": ["matrix"],
        "context_source_excluded_terms": ["debug"],
        "context_source_ranking_terms": ["sorting"],
        "context_source_limit": 1,
        "context_source_max_chars": 256,
        "context_source_truncation": "head_tail",
        "context_source_order_policy": "task_term_ranked",
        "recent_failure_limit": 1,
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
        "recent_failure_max_chars_by_field": {"error": 64},
        "inspiration_limit": 2,
        "inspiration_sample_count": 3,
        "extra_context_max_chars": 500,
        "plugin_context_enabled": False,
        "plugin_context_allowlist": [],
        "plugin_context_excluded_labels": ["BlockedContextPlugin"],
        "plugin_context_order": ["SecondContextPlugin"],
        "plugin_context_required_terms": ["matrix"],
        "plugin_context_excluded_terms": ["debug"],
        "plugin_context_ranking_terms": ["matrix"],
        "plugin_context_limit": 1,
        "plugin_context_max_chars": 256,
        "plugin_context_truncation": "head",
        "plugin_context_max_chars_by_label": {},
    }
    assert len(mutated_add["program"]["context_policy_sha256"]) == 64
    response = mutated_add["program"]["metadata"]["mutation_response"]
    assert response["format"] == "json_object"
    assert response["context_policy_source"] == "mutation_response"


def test_meta_prompt_evolution_conditions_mutation_on_performance_evidence():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_meta_prompt_secret_1234567890"  # pragma: allowlist secret
    llm = MagicMock()
    llm.generate.side_effect = [
        (f"<<<SEARCH\napi_key={secret}\n===\nx=2\n>>>REPLACE", 0),
        (
            "[SYSTEM]\n{task}\n{context}\n{parent_score}\n{parent_metrics}\n"
            "{parent_feedback}\n{parent_code}\n{inspirations}\n{extra_context}\n"
            "{recent_failures}\n{mutation_mode}\n{mutation_instructions}",
            0,
        ),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(
            max_generations=1,
            log_dir=tmpdir,
            problem_name="t",
            meta_prompt_evolution=True,
            meta_prompt_interval=1,
        ))

    meta_prompt = next(
        call.args[0]
        for call in llm.generate.call_args_list
        if "[Prompt Performance Evidence]" in call.args[0]
    )
    assert "[Prompt Performance Evidence]" in meta_prompt
    assert '"reward_policy"' in meta_prompt
    assert '"selected_prompt"' in meta_prompt
    assert '"prompt_reward"' in meta_prompt
    assert '"context_policy_capabilities"' in meta_prompt
    assert '"context_policy_preview"' in meta_prompt
    assert '"latest_candidate"' in meta_prompt
    assert '"prompt_program_summaries"' in meta_prompt
    assert '"recent_failures"' in meta_prompt
    assert secret not in meta_prompt

    events = [
        json.loads(l)
        for l in (Path(tmpdir) / "t" / "prompt_history.jsonl").read_text().splitlines()
    ]
    mutated_add = [event for event in events if event["event"] == "add"][-1]
    context = mutated_add["program"]["metadata"]["mutation_context"]
    assert context["schema"] == "meta_prompt_mutation_context_v1"
    assert len(context["sha256"]) == 64
    assert context["chars"] > 0
    assert "evidence" not in context
    assert context["evidence_retention"]["retention_mode"] == "hash_only"
    assert context["evidence_retention"]["stored_chars"] == 0
    assert len(context["evidence_retention"]["sha256"]) == 64
    assert context["sections"] == [
        "reward_policy",
        "latest_candidate",
        "selected_prompt",
        "context_policy_capabilities",
        "prompt_program_summaries",
        "recent_failures",
    ]
    capability_summary = context["context_policy_capability_summary"]
    assert capability_summary["schema"] == (
        "libreevolve.meta_prompt_context_policy_capability_summary.v1"
    )
    assert capability_summary["capabilities_schema"] == (
        META_PROMPT_CONTEXT_POLICY_CAPABILITIES_SCHEMA
    )
    assert capability_summary["context_policy_schema"] == (
        "libreevolve.prompt_context_policy.v1"
    )
    assert capability_summary["field_count"] == (
        len(validate_prompt_context_policy({})) - 1
    )
    assert len(capability_summary["fields_sha256"]) == 64
    assert len(capability_summary["sections"]) == 3
    assert capability_summary["validation"]["schema"] == (
        META_PROMPT_CONTEXT_POLICY_CAPABILITY_SUMMARY_VALIDATION_SCHEMA
    )
    assert capability_summary["validation"]["ok"] is True


def test_meta_prompt_context_policy_capabilities_validate_current_policy_schema():
    capabilities = validate_meta_prompt_context_policy_capabilities(
        _META_PROMPT_CONTEXT_POLICY_CAPABILITIES
    )

    assert capabilities["schema"] == META_PROMPT_CONTEXT_POLICY_CAPABILITIES_SCHEMA
    advertised = set()
    for section in (
        "channel_controls",
        "feedback_selection",
        "sampling_and_context",
    ):
        fields = capabilities[section].split(",")
        assert fields == sorted(fields, key=fields.index)
        advertised.update(fields)
    assert advertised == set(validate_prompt_context_policy({})) - {"schema"}


def test_meta_prompt_context_policy_capability_summary_rejects_overclaims():
    _, context = _build_meta_prompt_mutation_request(
        PromptProgram(template=DEFAULT_TEMPLATE),
        PromptDatabase(tempfile.mkdtemp(), templates=[DEFAULT_TEMPLATE]),
        Program(code="x=2", fitness=0.4),
        Program(code="x=1", fitness=0.3),
        0.1,
        [],
        Config(),
    )
    summary = copy.deepcopy(context["context_policy_capability_summary"])
    summary["field_count"] += 1
    summary["fields_sha256"] = "0" * 64
    summary["sections"][0]["field_count"] += 1
    summary["unsupported"] = True
    summary.pop("validation")

    validation = validate_meta_prompt_context_policy_capability_summary(summary)

    assert validation["schema"] == (
        META_PROMPT_CONTEXT_POLICY_CAPABILITY_SUMMARY_VALIDATION_SCHEMA
    )
    assert validation["ok"] is False
    codes = {issue["code"] for issue in validation["issues"]}
    assert "field_count_mismatch" in codes
    assert "fields_sha256_mismatch" in codes
    assert "sections_mismatch" in codes
    assert "unsupported_field" in codes


def test_runtime_prompt_context_policy_coverage_scopes_alphaevolve_completeness():
    tmpdir = tempfile.mkdtemp()

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    coverage = manifest["runtime"]["prompt_context_policy_coverage"]

    assert coverage["schema"] == PROMPT_CONTEXT_POLICY_COVERAGE_SCHEMA
    assert coverage["capabilities_schema"] == META_PROMPT_CONTEXT_POLICY_CAPABILITIES_SCHEMA
    assert coverage["context_policy_schema"] == (
        "libreevolve.prompt_context_policy.v1"
    )
    assert coverage["tunable_field_count"] == (
        len(validate_prompt_context_policy({})) - 1
    )
    assert len(coverage["tunable_fields_sha256"]) == 64
    assert coverage["meta_prompt_mutation_accepts_context_policy"] is True
    assert coverage["prompt_history_replay_validates_context_policy_hash"] is True
    assert coverage["alphaevolve_context_policy_complete"] is False
    assert coverage["retrieval_summarization_policy_tunable"] is False
    assert coverage["semantic_source_selection_policy_tunable"] is False
    assert coverage["non_promptsampler_role_policy_tunable"] is False
    assert coverage["deep_retrieval_debug_refinement_policy_tunable"] is False
    assert "retrieval_summarization_policy" in coverage["unsupported_surfaces"]
    assert "semantic_source_selection_policy" in coverage["unsupported_surfaces"]

    validation = coverage["validation"]
    assert validation["schema"] == PROMPT_CONTEXT_POLICY_COVERAGE_VALIDATION_SCHEMA
    assert validation["coverage_schema"] == PROMPT_CONTEXT_POLICY_COVERAGE_SCHEMA
    assert validation["ok"] is True
    assert validation["alphaevolve_context_policy_complete"] is False
    assert validation["tunable_field_count"] == coverage["tunable_field_count"]
    assert validation["unsupported_surface_count"] == len(
        coverage["unsupported_surfaces"]
    )

    overclaim = copy.deepcopy(coverage)
    overclaim["alphaevolve_context_policy_complete"] = True
    overclaim.pop("validation")

    invalid = validate_prompt_context_policy_coverage(overclaim)

    assert invalid["ok"] is False
    assert any(
        issue["code"] == "context_policy_completion_overclaim"
        for issue in invalid["issues"]
    )
    surface_overclaim = copy.deepcopy(coverage)
    surface_overclaim["retrieval_summarization_policy_tunable"] = True
    surface_overclaim["semantic_source_selection_policy_tunable"] = True
    surface_overclaim["non_promptsampler_role_policy_tunable"] = True
    surface_overclaim["deep_retrieval_debug_refinement_policy_tunable"] = True
    surface_overclaim.pop("validation")

    invalid_surface = validate_prompt_context_policy_coverage(surface_overclaim)

    assert invalid_surface["ok"] is False
    surface_codes = {issue["code"] for issue in invalid_surface["issues"]}
    assert "retrieval_summarization_policy_overclaim" in surface_codes
    assert "semantic_source_selection_policy_overclaim" in surface_codes
    assert "non_promptsampler_role_policy_overclaim" in surface_codes
    assert "deep_retrieval_debug_refinement_policy_overclaim" in surface_codes


def test_meta_prompt_context_policy_capabilities_reject_missing_policy_field():
    capabilities = json.loads(json.dumps(_META_PROMPT_CONTEXT_POLICY_CAPABILITIES))
    capabilities["channel_controls"] = capabilities["channel_controls"].replace(
        "disabled_sections,",
        "",
    )

    with pytest.raises(ValueError, match="omit prompt policy fields"):
        validate_meta_prompt_context_policy_capabilities(capabilities)


def test_meta_prompt_context_policy_capabilities_reject_unsupported_policy_field():
    capabilities = json.loads(json.dumps(_META_PROMPT_CONTEXT_POLICY_CAPABILITIES))
    capabilities["sampling_and_context"] += ",unsupported_field"

    with pytest.raises(ValueError, match="unsupported fields"):
        validate_meta_prompt_context_policy_capabilities(capabilities)


def test_meta_prompt_context_policy_capabilities_reject_duplicate_field():
    capabilities = json.loads(json.dumps(_META_PROMPT_CONTEXT_POLICY_CAPABILITIES))
    capabilities["sampling_and_context"] += ",disabled_sections"

    with pytest.raises(ValueError, match="duplicate fields"):
        validate_meta_prompt_context_policy_capabilities(capabilities)


def test_meta_prompt_context_policy_capabilities_reject_malformed_section():
    capabilities = json.loads(json.dumps(_META_PROMPT_CONTEXT_POLICY_CAPABILITIES))
    capabilities["feedback_selection"] = "feedback_sections, bad"

    with pytest.raises(ValueError, match="malformed field"):
        validate_meta_prompt_context_policy_capabilities(capabilities)


def test_meta_prompt_mutation_request_redacts_and_bounds_current_template():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_template_secret_1234567890"  # pragma: allowlist secret
    template = f"Task: {{task}}\napi_key={secret}\n" + ("X" * 2500)
    prompt_program = PromptProgram(template=template)
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(
        code="x=1",
        fitness=0.25,
        metrics={"score": 0.25, "is_valid": True},
    )
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5, "is_valid": True},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert "[Current Template Placeholders]\n[\"task\"]" in mutation_prompt
    assert secret not in mutation_prompt
    assert "[REDACTED]" in mutation_prompt
    assert "X" * 1500 not in mutation_prompt
    assert mutation_prompt.endswith("...<truncated>")
    current_template = context["current_template"]
    assert current_template == {
        "sha256": hashlib.sha256(template.encode("utf-8")).hexdigest(),
        "raw_chars": len(template),
        "prompt_chars": 1200,
        "redacted": True,
        "truncated": True,
        "limit_chars": 1200,
    }
    context_json = json.dumps(context, sort_keys=True)
    assert secret not in context_json
    assert "X" * 100 not in context_json
    assert context["evidence_retention"]["retention_mode"] == "hash_only"


def test_meta_prompt_mutation_request_exposes_context_policy_values():
    tmpdir = tempfile.mkdtemp()
    context_policy = {
        "disabled_sections": ["recent_failures"],
        "mutation_instruction_variant": "exploratory",
        "mutation_instruction_include_example": False,
        "proposal_metadata_enabled": True,
        "feedback_sections": ["proposal", "validator_diagnostics"],
        "llm_feedback_max_chars_by_field": {"feedback": 80},
        "proposal_max_chars_by_field": {"idea": 80},
        "stage_summary_max_chars_by_field": {"error": 80},
        "execution_output_max_chars_by_field": {"stdout": 80},
        "sample_retry_max_chars_by_field": {"error": 80},
        "program_output_max_chars_by_field": {"value": 120},
        "validator_artifact_max_chars_by_field": {"content_excerpt": 80},
        "validator_skipped_artifact_max_chars_by_field": {"reason": 40},
        "syntax_error_max_chars_by_field": {"message": 80},
        "metric_bound_max_chars_by_field": {"value": 80},
        "malformed_metric_max_chars_by_field": {"reason": 80},
        "metric_aggregation_max_chars_by_field": {"metric_aggregation": 80},
        "configured_stage_check_max_chars_by_field": {"name": 80},
        "stage_metric_threshold_max_chars_by_field": {"metric": 80},
        "artifact_output_check_max_chars_by_field": {"reason": 80},
        "validator_boundary_max_chars_by_field": {"policy": 80},
        "validator_resource_limit_max_chars_by_field": {"memory": 80},
        "validator_stdin_max_chars_by_field": {"source": 80},
        "diagnostic_output_max_chars_by_field": {"encoding": 80},
        "timeout_cleanup_max_chars_by_field": {"error": 80},
        "validator_metadata_limit": 1,
        "validator_metadata_max_chars_by_key": {"score_detail": 80},
        "context_source_max_chars": 256,
        "context_source_truncation": "head_tail",
        "context_source_order_policy": "task_term_ranked",
        "inspiration_strategy": "novelty",
        "inspiration_required_metric": "latency",
        "inspiration_excluded_metrics": ["debug_score"],
        "inspiration_fitness_threshold": {"min": 0.25},
        "inspiration_metric_thresholds": {"latency": {"max": 0.5}},
        "inspiration_metric_ranking": {
            "metric": "latency",
            "direction": "minimize",
        },
        "plugin_context_enabled": False,
        "plugin_context_order": ["SecondContextPlugin"],
    }
    prompt_program = PromptProgram(
        template="Task: {task}\n{context}\n{mutation_instructions}",
        context_policy=context_policy,
    )
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(
        code="x=1",
        fitness=0.25,
        metrics={"score": 0.25, "is_valid": True},
    )
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5, "is_valid": True},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert '"context_policy_preview"' in mutation_prompt
    assert '"non_default_fields"' in mutation_prompt
    assert '"mutation_instruction_variant": "exploratory"' in mutation_prompt
    assert '"mutation_instruction_include_example": false' in mutation_prompt
    assert '"proposal_metadata_enabled": true' in mutation_prompt
    assert '"inspiration_required_metric": "latency"' in mutation_prompt
    assert '"inspiration_excluded_metrics": [' in mutation_prompt
    assert '"inspiration_fitness_threshold": {' in mutation_prompt
    assert '"inspiration_metric_thresholds": {' in mutation_prompt
    assert '"inspiration_metric_ranking": {' in mutation_prompt
    assert '"llm_feedback_max_chars_by_field": {' in mutation_prompt
    assert '"proposal_max_chars_by_field": {' in mutation_prompt
    assert '"stage_summary_max_chars_by_field": {' in mutation_prompt
    assert '"execution_output_max_chars_by_field": {' in mutation_prompt
    assert '"sample_retry_max_chars_by_field": {' in mutation_prompt
    assert '"disabled_sections": [' in mutation_prompt
    assert '"recent_failures"' in mutation_prompt
    assert "context_policy_capabilities" in context["sections"]
    assert context["sections"] == [
        "reward_policy",
        "latest_candidate",
        "selected_prompt",
        "context_policy_capabilities",
        "prompt_program_summaries",
        "recent_failures",
    ]


def test_meta_prompt_mutation_request_exposes_context_source_limit():
    tmpdir = tempfile.mkdtemp()
    prompt_program = PromptProgram(
        template="Task: {task}\n{context}\n{mutation_instructions}",
        context_policy={"context_source_limit": 1},
    )
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(code="x=1", fitness=0.4, metrics={"score": 0.4})
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert '"context_source_limit": 1' in mutation_prompt
    assert "context_policy_capabilities" in context["sections"]


def test_meta_prompt_mutation_request_exposes_validator_budget_fields():
    tmpdir = tempfile.mkdtemp()
    prompt_program = PromptProgram(
        template="Task: {task}\n{parent_feedback}\n{mutation_instructions}",
        context_policy={
            "feedback_sections": ["validator_diagnostics"],
            "validator_diagnostic_groups": ["execution_diagnostics"],
            "execution_diagnostic_groups": ["validator_budget"],
            "validator_budget_fields": ["policy", "exhausted"],
            "validator_budget_max_chars_by_field": {"policy": 44},
        },
    )
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(code="x=1", fitness=0.4, metrics={"score": 0.4})
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert '"validator_budget_fields": [' in mutation_prompt
    assert '"validator_budget_max_chars_by_field": {' in mutation_prompt
    assert '"validator_budget"' in mutation_prompt
    assert '"exhausted"' in mutation_prompt
    assert "validator_budget_fields" in mutation_prompt
    assert "validator_budget_max_chars_by_field" in mutation_prompt
    assert "context_policy_capabilities" in context["sections"]


def test_meta_prompt_mutation_request_exposes_validator_env_fields():
    tmpdir = tempfile.mkdtemp()
    prompt_program = PromptProgram(
        template="Task: {task}\n{parent_feedback}\n{mutation_instructions}",
        context_policy={
            "feedback_sections": ["validator_diagnostics"],
            "validator_diagnostic_groups": ["execution_diagnostics"],
            "execution_diagnostic_groups": ["validator_env"],
            "validator_env_fields": ["policy", "values_redacted"],
            "validator_env_max_chars_by_field": {"policy": 48},
        },
    )
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(code="x=1", fitness=0.4, metrics={"score": 0.4})
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert '"validator_env_fields": [' in mutation_prompt
    assert '"validator_env_max_chars_by_field": {' in mutation_prompt
    assert '"validator_env"' in mutation_prompt
    assert '"values_redacted"' in mutation_prompt
    assert "validator_env_fields" in mutation_prompt
    assert "validator_env_max_chars_by_field" in mutation_prompt
    assert "context_policy_capabilities" in context["sections"]


def test_meta_prompt_mutation_request_exposes_evaluator_path_fields():
    tmpdir = tempfile.mkdtemp()
    prompt_program = PromptProgram(
        template="Task: {task}\n{parent_feedback}\n{mutation_instructions}",
        context_policy={
            "feedback_sections": ["validator_diagnostics"],
            "validator_diagnostic_groups": ["evaluator_path"],
            "evaluator_path_fields": ["validate_path", "validate_path_hash"],
            "evaluator_path_max_chars_by_field": {"validate_path": 96},
        },
    )
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(code="x=1", fitness=0.4, metrics={"score": 0.4})
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert '"evaluator_path_fields": [' in mutation_prompt
    assert '"evaluator_path_max_chars_by_field": {' in mutation_prompt
    assert '"evaluator_path"' in mutation_prompt
    assert '"validate_path_hash"' in mutation_prompt
    assert "evaluator_path_fields" in mutation_prompt
    assert "evaluator_path_max_chars_by_field" in mutation_prompt
    assert "context_policy_capabilities" in context["sections"]


def test_meta_prompt_mutation_request_exposes_evaluator_dependency_fields():
    tmpdir = tempfile.mkdtemp()
    prompt_program = PromptProgram(
        template="Task: {task}\n{parent_feedback}\n{mutation_instructions}",
        context_policy={
            "feedback_sections": ["validator_diagnostics"],
            "validator_diagnostic_groups": ["evaluator_dependency"],
            "evaluator_dependency_fields": ["policy", "file_paths"],
            "evaluator_dependency_max_chars_by_field": {"file_paths": 88},
        },
    )
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(code="x=1", fitness=0.4, metrics={"score": 0.4})
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert '"evaluator_dependency_fields": [' in mutation_prompt
    assert '"evaluator_dependency_max_chars_by_field": {' in mutation_prompt
    assert '"evaluator_dependency"' in mutation_prompt
    assert '"file_paths"' in mutation_prompt
    assert "evaluator_dependency_fields" in mutation_prompt
    assert "evaluator_dependency_max_chars_by_field" in mutation_prompt
    assert "context_policy_capabilities" in context["sections"]


def test_meta_prompt_mutation_request_exposes_evaluator_stage_fields():
    tmpdir = tempfile.mkdtemp()
    prompt_program = PromptProgram(
        template="Task: {task}\n{parent_feedback}\n{mutation_instructions}",
        context_policy={
            "feedback_sections": ["validator_diagnostics"],
            "validator_diagnostic_groups": ["evaluator_stage"],
            "evaluator_stage_fields": ["name", "validate_path"],
            "evaluator_stage_max_chars_by_field": {"validate_path": 100},
        },
    )
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(code="x=1", fitness=0.4, metrics={"score": 0.4})
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert '"evaluator_stage_fields": [' in mutation_prompt
    assert '"evaluator_stage_max_chars_by_field": {' in mutation_prompt
    assert '"evaluator_stage"' in mutation_prompt
    assert '"validate_path"' in mutation_prompt
    assert "evaluator_stage_fields" in mutation_prompt
    assert "evaluator_stage_max_chars_by_field" in mutation_prompt
    assert "context_policy_capabilities" in context["sections"]


def test_meta_prompt_mutation_request_exposes_evaluator_workspace_fields():
    tmpdir = tempfile.mkdtemp()
    prompt_program = PromptProgram(
        template="Task: {task}\n{parent_feedback}\n{mutation_instructions}",
        context_policy={
            "feedback_sections": ["validator_diagnostics"],
            "validator_diagnostic_groups": ["evaluator_workspace"],
            "evaluator_workspace_fields": ["primary_file", "files"],
            "evaluator_workspace_max_chars_by_field": {"files": 96},
        },
    )
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(code="x=1", fitness=0.4, metrics={"score": 0.4})
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert '"evaluator_workspace_fields": [' in mutation_prompt
    assert '"evaluator_workspace_max_chars_by_field": {' in mutation_prompt
    assert '"evaluator_workspace"' in mutation_prompt
    assert '"primary_file"' in mutation_prompt
    assert "evaluator_workspace_fields" in mutation_prompt
    assert "evaluator_workspace_max_chars_by_field" in mutation_prompt
    assert "context_policy_capabilities" in context["sections"]


def test_meta_prompt_mutation_request_exposes_synthetic_metric_fields():
    tmpdir = tempfile.mkdtemp()
    prompt_program = PromptProgram(
        template="Task: {task}\n{parent_feedback}\n{mutation_instructions}",
        context_policy={
            "feedback_sections": ["validator_diagnostics"],
            "validator_diagnostic_groups": ["synthetic_metrics"],
            "synthetic_metric_fields": ["policy", "penalty"],
            "synthetic_metric_max_chars_by_field": {"policy": 50},
        },
    )
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(code="x=1", fitness=0.4, metrics={"score": 0.4})
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert '"synthetic_metric_fields": [' in mutation_prompt
    assert '"synthetic_metric_max_chars_by_field": {' in mutation_prompt
    assert '"synthetic_metrics"' in mutation_prompt
    assert '"penalty"' in mutation_prompt
    assert "synthetic_metric_fields" in mutation_prompt
    assert "synthetic_metric_max_chars_by_field" in mutation_prompt
    assert "context_policy_capabilities" in context["sections"]


def test_meta_prompt_mutation_request_exposes_materialization_error_fields():
    tmpdir = tempfile.mkdtemp()
    prompt_program = PromptProgram(
        template="Task: {task}\n{parent_feedback}\n{mutation_instructions}",
        context_policy={
            "feedback_sections": ["validator_diagnostics"],
            "validator_diagnostic_groups": ["materialization_error"],
            "materialization_error_fields": ["message"],
            "materialization_error_max_chars_by_field": {"message": 70},
        },
    )
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(code="x=1", fitness=0.4, metrics={"score": 0.4})
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert '"materialization_error_fields": [' in mutation_prompt
    assert '"materialization_error_max_chars_by_field": {' in mutation_prompt
    assert '"materialization_error"' in mutation_prompt
    assert '"message"' in mutation_prompt
    assert "materialization_error_fields" in mutation_prompt
    assert "materialization_error_max_chars_by_field" in mutation_prompt
    assert "context_policy_capabilities" in context["sections"]


def test_meta_prompt_mutation_request_exposes_context_source_term_filters():
    tmpdir = tempfile.mkdtemp()
    prompt_program = PromptProgram(
        template="Task: {task}\n{context}\n{mutation_instructions}",
        context_policy={
            "context_source_required_terms": ["matrix"],
            "context_source_excluded_terms": ["debug"],
        },
    )
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(code="x=1", fitness=0.4, metrics={"score": 0.4})
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert '"context_source_required_terms": [' in mutation_prompt
    assert '"matrix"' in mutation_prompt
    assert '"context_source_excluded_terms": [' in mutation_prompt
    assert '"debug"' in mutation_prompt
    assert "context_policy_capabilities" in context["sections"]


def test_meta_prompt_mutation_request_exposes_recent_failure_term_filters():
    tmpdir = tempfile.mkdtemp()
    prompt_program = PromptProgram(
        template="Task: {task}\n{recent_failures}\n{mutation_instructions}",
        context_policy={
            "recent_failure_required_terms": ["matrix"],
            "recent_failure_excluded_terms": ["debug"],
        },
    )
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(code="x=1", fitness=0.4, metrics={"score": 0.4})
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert '"recent_failure_required_terms": [' in mutation_prompt
    assert '"recent_failure_excluded_terms": [' in mutation_prompt
    assert '"matrix"' in mutation_prompt
    assert '"debug"' in mutation_prompt
    assert "recent_failure_required_terms" in mutation_prompt
    assert "recent_failure_excluded_terms" in mutation_prompt
    assert "context_policy_capabilities" in context["sections"]


def test_meta_prompt_mutation_request_exposes_context_source_ranking_terms():
    tmpdir = tempfile.mkdtemp()
    prompt_program = PromptProgram(
        template="Task: {task}\n{context}\n{mutation_instructions}",
        context_policy={
            "context_source_order_policy": "task_term_ranked",
            "context_source_ranking_terms": ["sorting"],
        },
    )
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(code="x=1", fitness=0.4, metrics={"score": 0.4})
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert '"context_source_ranking_terms": [' in mutation_prompt
    assert '"sorting"' in mutation_prompt
    assert "context_source_ranking_terms" in mutation_prompt
    assert "context_policy_capabilities" in context["sections"]


def test_meta_prompt_mutation_request_exposes_plugin_context_term_filters():
    tmpdir = tempfile.mkdtemp()
    prompt_program = PromptProgram(
        template="Task: {task}\n{extra_context}\n{mutation_instructions}",
        context_policy={
            "plugin_context_excluded_labels": ["BlockedContextPlugin"],
            "plugin_context_required_terms": ["matrix"],
            "plugin_context_excluded_terms": ["debug"],
            "plugin_context_ranking_terms": ["matrix"],
            "plugin_context_limit": 1,
            "plugin_context_max_chars": 256,
            "plugin_context_truncation": "head_tail",
        },
    )
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(code="x=1", fitness=0.4, metrics={"score": 0.4})
    program = Program(
        code="x=2",
        fitness=0.5,
        parent_id=parent.id,
        metrics={"score": 0.5},
        evaluation={"score": 0.5, "is_valid": True},
    )

    mutation_prompt, context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.5,
        recent_failures=[],
        config=Config(),
    )

    assert '"plugin_context_required_terms": [' in mutation_prompt
    assert '"plugin_context_excluded_labels": [' in mutation_prompt
    assert '"plugin_context_excluded_terms": [' in mutation_prompt
    assert '"plugin_context_ranking_terms": [' in mutation_prompt
    assert '"plugin_context_limit": 1' in mutation_prompt
    assert '"plugin_context_max_chars": 256' in mutation_prompt
    assert '"plugin_context_truncation": "head_tail"' in mutation_prompt
    assert '"matrix"' in mutation_prompt
    assert '"debug"' in mutation_prompt
    assert '"BlockedContextPlugin"' in mutation_prompt
    assert "plugin_context_excluded_labels" in mutation_prompt
    assert "plugin_context_required_terms" in mutation_prompt
    assert "plugin_context_excluded_terms" in mutation_prompt
    assert "plugin_context_ranking_terms" in mutation_prompt
    assert "plugin_context_limit" in mutation_prompt
    assert "plugin_context_max_chars" in mutation_prompt
    assert "plugin_context_truncation" in mutation_prompt
    assert "context_policy_capabilities" in context["sections"]


def test_meta_prompt_evidence_retention_modes_control_persisted_context():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_meta_evidence_secret_1234567890"  # pragma: allowlist secret
    prompt_program = PromptProgram(template="Task: {task}")
    prompt_db = PromptDatabase(tmpdir, templates=["Task: {task}"])
    prompt_db.add(prompt_program)
    parent = Program(code="x=1", fitness=0.1, metrics={"score": 0.1})
    program = Program(
        code="x=2",
        fitness=0.2,
        parent_id=parent.id,
        metrics={"score": 0.2},
        evaluation={"error": secret, "is_valid": False},
    )

    _, redacted_context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.1,
        recent_failures=[{"error": secret}],
        config=Config(meta_prompt_evidence_retention_mode="redacted"),
    )
    assert redacted_context["evidence_retention"]["retention_mode"] == "redacted"
    assert redacted_context["evidence_retention"]["stored_chars"] > 0
    assert redacted_context["evidence_retention"]["max_retained_chars"] == 1000
    assert "evidence" in redacted_context
    assert secret not in redacted_context["evidence"]
    assert "[REDACTED]" in redacted_context["evidence"]

    _, off_context = _build_meta_prompt_mutation_request(
        prompt_program,
        prompt_db,
        program,
        parent,
        0.1,
        recent_failures=[{"error": secret}],
        config=Config(meta_prompt_evidence_retention_mode="off"),
    )
    assert "evidence" not in off_context
    assert off_context["sha256"] is None
    assert off_context["chars"] is None
    assert off_context["evidence_retention"] == {
        "sha256": None,
        "chars": None,
        "stored_chars": 0,
        "redacted": None,
        "truncated": False,
        "prompt_sha256": None,
        "prompt_chars": None,
        "prompt_truncated": False,
        "max_retained_chars": 1000,
        "retention_mode": "off",
        "retention_policy": "off_no_evidence_or_hash",
    }


def test_meta_prompt_evidence_redacts_and_hashes_mapping_keys():
    key_secret = "sk-proj_metakey_secret_1234567890"  # pragma: allowlist secret
    nested_secret = "ghp_nested_secret_1234567890"  # pragma: allowlist secret
    long_key = "metric_" + ("X" * 240)

    safe = _meta_prompt_safe_value(
        {
            f"api_key={key_secret}": "safe",
            "nested": {f"token={nested_secret}": "inner"},
            long_key: "large",
            7: "non-string",
        }
    )

    serialized = json.dumps(safe, sort_keys=True)
    assert key_secret not in serialized
    assert nested_secret not in serialized
    secret_key = next(key for key in safe if key.startswith("api_key=[REDACTED]"))
    nested_key = next(
        key for key in safe["nested"] if key.startswith("token=[REDACTED]")
    )
    long_safe_key = next(key for key in safe if key.startswith("metric_"))
    assert secret_key.endswith(
        "#sha256:"
        + hashlib.sha256(f"api_key={key_secret}".encode("utf-8")).hexdigest()[:12]
    )
    assert nested_key.endswith(
        "#sha256:"
        + hashlib.sha256(f"token={nested_secret}".encode("utf-8")).hexdigest()[:12]
    )
    assert long_safe_key.endswith(
        "#sha256:" + hashlib.sha256(long_key.encode("utf-8")).hexdigest()[:12]
    )
    assert len(long_safe_key) == 160
    assert safe["7"] == "non-string"


def test_meta_prompt_metrics_redacts_keys_and_sorts_non_string_keys():
    key_secret = "sk-proj_metric_key_secret_1234567890"  # pragma: allowlist secret

    safe = _meta_prompt_metrics(
        {
            2: 0.2,
            f"api_key={key_secret}": 0.9,
            "accuracy": 1.0,
        }
    )

    serialized = json.dumps(safe, sort_keys=True)
    assert key_secret not in serialized
    safe_secret_key = next(key for key in safe if key.startswith("api_key=[REDACTED]"))
    assert safe_secret_key.endswith(
        "#sha256:"
        + hashlib.sha256(f"api_key={key_secret}".encode("utf-8")).hexdigest()[:12]
    )
    assert safe["2"] == 0.2
    assert safe["accuracy"] == 1.0


def test_meta_prompt_evolution_rejects_invalid_mutated_prompt_template():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        (json.dumps({"template": "[SYSTEM]\n{unknown}"}), 0),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(
            max_generations=1,
            log_dir=tmpdir,
            problem_name="t",
            meta_prompt_evolution=True,
            meta_prompt_interval=1,
        ))

    run_dir = Path(tmpdir) / "t"
    events = [
        json.loads(l)["event"]
        for l in (run_dir / "prompt_history.jsonl").read_text().splitlines()
    ]
    invalid = [
        json.loads(l)
        for l in (run_dir / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    assert events == ["add", "score", "penalty"]
    assert invalid[0]["event"] == "reject"
    assert "unknown" in invalid[0]["metadata"]["mutation_response"]["error"]


def test_meta_prompt_evolution_rejects_template_that_drops_parent_placeholders():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        ("Task only: {task}", 0),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(
            max_generations=1,
            log_dir=tmpdir,
            problem_name="t",
            meta_prompt_evolution=True,
            meta_prompt_interval=1,
        ))

    run_dir = Path(tmpdir) / "t"
    events = [
        json.loads(l)["event"]
        for l in (run_dir / "prompt_history.jsonl").read_text().splitlines()
    ]
    invalid = [
        json.loads(l)
        for l in (run_dir / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    assert events == ["add", "score", "penalty"]
    assert invalid[0]["event"] == "reject"
    assert "dropped parent placeholders" in invalid[0]["error"]
    assert "parent_code" in invalid[0]["error"]
    assert "mutation_instructions" in invalid[0]["error"]


def test_meta_prompt_provider_failure_records_rejected_prompt_without_aborting_candidate():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_meta_prompt_failure_secret_1234567890"
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        RuntimeError(f"meta prompt provider failed token={secret}"),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        best = evolve(
            _problem(
                "def evaluate(c): return {'score': 1.0 if 'x=2' in c else 0.5,"
                "'is_valid':True}"
            ),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                meta_prompt_evolution=True,
                meta_prompt_interval=1,
            ),
        )

    run_dir = Path(tmpdir) / "t"
    history = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text().splitlines()
    ]
    prompt_events = [
        json.loads(line)["event"]
        for line in (run_dir / "prompt_history.jsonl").read_text().splitlines()
    ]
    invalid = [
        json.loads(line)
        for line in (run_dir / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    failure_metadata = invalid[0]["metadata"]
    serialized = json.dumps(failure_metadata)

    assert best.code == "x=2"
    assert history[-1]["code"] == "x=2"
    assert prompt_events == ["add", "score", "penalty"]
    assert invalid[0]["event"] == "reject"
    assert invalid[0]["error"] == "prompt template must be a non-empty string"
    assert failure_metadata["status"] == "failed"
    assert failure_metadata["error"] == "llm_meta_prompt_failed"
    assert failure_metadata["exception"] == "RuntimeError"
    assert secret not in serialized
    assert "[REDACTED]" in failure_metadata["message"]


def test_critique_revises_mutation_before_evaluation():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=0\n>>>REPLACE", 0),
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        problem = _problem(
            "def evaluate(c): return {'score': 1.0 if 'x=2' in c else 0.5,"
            "'is_valid':True}"
        )
        best = evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                critique_enabled=True,
            ),
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert best.code == "x=2"
    assert child["metadata"]["critique"]["original_diff"].endswith("x=0\n>>>REPLACE")
    assert child["metadata"]["critique"]["accepted_revision"] is True
    assert child["metadata"]["critique"]["selected_diff"] == "revised"


def test_critique_reviewer_pool_aggregates_valid_revisions_without_backend_corruption():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=0\n>>>REPLACE", 0),
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 1),
        ("<<<SEARCH\nx=1\n===\nx=3\n>>>REPLACE", 2),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        problem = _problem(
            "def evaluate(c): return {'score': 1.0 if 'x=3' in c else 0.5,"
            "'is_valid':True}"
        )
        best = evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                critique_enabled=True,
                critique_reviewers=[
                    {
                        "name": "correctness",
                        "prompt": "Check correctness.",
                        "role": "critique:correctness",
                    },
                    {
                        "name": "simplicity",
                        "prompt": "Prefer the simplest valid revision.",
                        "role": "critique:simplicity",
                    },
                ],
                critique_aggregation_policy="last_valid",
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    critique = child["metadata"]["critique"]
    pool = critique["reviewer_pool"]

    assert best.code == "x=3"
    assert child["metadata"]["backend_idx"] == 0
    assert critique["reviewer_name"] == "simplicity"
    assert critique["reviewer_role"] == "critique:simplicity"
    assert critique["backend_idx"] == 2
    assert critique["accepted_revision"] is True
    assert pool["schema"] == "libreevolve.critique_reviewer_pool.v1"
    assert pool["aggregation_policy"] == "last_valid"
    assert pool["execution_model"] == "synchronous_sequential"
    assert pool["reviewer_count"] == 2
    assert pool["completed_review_count"] == 2
    assert pool["valid_revision_count"] == 2
    assert pool["failed_review_count"] == 0
    assert pool["budget_skipped_review_count"] == 0
    assert pool["pool_elapsed_sec"] >= 0.0
    assert pool["reviewer_elapsed_sec_sum"] >= 0.0
    assert pool["selected_reviewer"] == "simplicity"
    assert [reviewer["reviewer_role"] for reviewer in pool["reviewers"]] == [
        "critique:correctness",
        "critique:simplicity",
    ]
    assert [reviewer["reviewer_outcome"] for reviewer in pool["reviewers"]] == [
        "accepted_revision",
        "accepted_revision",
    ]
    assert all(
        reviewer["reviewer_elapsed_sec"] >= 0.0
        for reviewer in pool["reviewers"]
    )
    assert all(
        reviewer["reviewer_runtime_artifact_policy"]
        == "inline_timing_and_status_no_external_artifact"
        for reviewer in pool["reviewers"]
    )
    assert [call.kwargs["role"] for call in llm.generate.call_args_list] == [
        "mutation",
        "critique:correctness",
        "critique:simplicity",
    ]


def test_critique_provider_failure_falls_back_to_original_mutation():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_critique_failure_secret_1234567890"
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        RuntimeError(f"critique provider failed token={secret}"),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        problem = _problem(
            "def evaluate(c): return {'score': 1.0 if 'x=2' in c else 0.0,"
            "'is_valid':True}"
        )
        best = evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                critique_enabled=True,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    critique = child["metadata"]["critique"]
    serialized = json.dumps(critique)

    assert best.code == "x=2"
    assert child["metadata"]["diff"].endswith("x=2\n>>>REPLACE")
    assert critique["status"] == "failed"
    assert critique["error"] == "llm_critique_failed"
    assert critique["exception"] == "RuntimeError"
    assert critique["accepted_revision"] is False
    assert critique["selected_diff"] == "original"
    assert critique["fallback_reason"] == "critique_provider_failure_original_mutation"
    pool = critique["reviewer_pool"]
    assert pool["execution_model"] == "synchronous_sequential"
    assert pool["failed_review_count"] == 1
    assert pool["budget_skipped_review_count"] == 0
    assert pool["reviewers"][0]["reviewer_outcome"] == "provider_failure"
    assert pool["reviewers"][0]["reviewer_elapsed_sec"] >= 0.0
    assert secret not in serialized
    assert "[REDACTED]" in critique["message"]


def test_critique_revised_mutation_updates_selected_proposal_metadata():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        (
            "IDEA: original idea\n"
            "RATIONALE: original rationale\n"
            "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE",
            0,
        ),
        (
            "IDEA: revised idea\n"
            "RATIONALE: revised rationale\n"
            "<<<SEARCH\nx=1\n===\nx=3\n>>>REPLACE",
            0,
        ),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        problem = _problem(
            "def evaluate(c): return {'score': 1.0 if 'x=3' in c else 0.5,"
            "'is_valid':True}"
        )
        best = evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                capture_proposal_metadata=True,
                critique_enabled=True,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    assert best.code == "x=3"
    assert child["metadata"]["proposal"] == {
        "idea": "revised idea",
        "rationale": "revised rationale",
    }
    critique = child["metadata"]["critique"]
    assert critique["selected_diff"] == "revised"
    assert critique["proposal_source"] == "revised"
    assert critique["original_proposal"] == {
        "idea": "original idea",
        "rationale": "original rationale",
    }
    assert critique["revised_proposal"] == {
        "idea": "revised idea",
        "rationale": "revised rationale",
    }


def test_invalid_critique_revision_falls_back_to_original_mutation():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        ("this is not a mutation", 0),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        problem = _problem(
            "def evaluate(c): return {'score': 1.0 if 'x=2' in c else 0.0,"
            "'is_valid':True}"
        )
        best = evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                critique_enabled=True,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    critique = child["metadata"]["critique"]
    assert best.code == "x=2"
    assert child["metadata"]["diff"].endswith("x=2\n>>>REPLACE")
    assert critique["accepted_revision"] is False
    assert critique["selected_diff"] == "original"
    assert critique["revised_diff_error"] == "no_diff_blocks"
    assert critique["original_diff_error"] is None
    assert critique["fallback_reason"] == "invalid_revised_diff"


def test_critique_metadata_retains_bounded_redacted_prompt_and_mutations():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_critique_history_secret_1234567890"
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        (f"api_key={secret}\n" + ("bad mutation " * 1000), 0),
    ]
    problem = _problem(
        "def evaluate(c): return {'score': 1.0 if 'x=2' in c else 0.0,"
        "'is_valid':True}"
    )
    problem.task_description = "Improve solve(). " + ("A" * 19_000)

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                critique_enabled=True,
                critique_prompt=f"Review without leaking token={secret}",
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    critique = records[-1]["metadata"]["critique"]
    serialized = json.dumps(critique)

    assert secret not in serialized
    assert critique["prompt_truncated"] is True
    assert critique["prompt_retained_chars"] <= 6000 + len("\n[truncated 00000 chars]")
    assert len(critique["prompt_sha256"]) == 64
    assert critique["revised_diff_truncated"] is True
    assert critique["revised_diff_retained_chars"] <= 4000 + len("\n[truncated 00000 chars]")
    assert len(critique["revised_diff_sha256"]) == 64
    assert critique["original_diff_truncated"] is False
    assert critique["retention_policy"] == "redact_then_prefix_truncate_with_sha256"
    assert critique["selected_diff"] == "original"
    assert critique["fallback_reason"] == "invalid_revised_diff"


@pytest.mark.parametrize(
    ("mode", "expect_hash"),
    [
        ("hash_only", True),
        ("off", False),
    ],
)
def test_loop_honors_critique_retention_modes(mode, expect_hash):
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_critique_retention_secret_1234567890"  # pragma: allowlist secret
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        f"<<<SEARCH\nx=2\n===\nx=3\n>>>REPLACE\n# {secret}",
    ]
    problem = _problem(
        "def evaluate(c): return {'score': 1.0 if 'x=3' in c else 0.0,"
        "'is_valid':True}"
    )
    try:
        with patch("libreevolve.core.loop.build_llm", return_value=llm):
            evolve(
                problem,
                Config(
                    max_generations=1,
                    log_dir=tmpdir,
                    problem_name="t",
                    critique_enabled=True,
                    critique_prompt=f"Review token={secret}",
                    critique_retention_mode=mode,
                ),
            )

        run_dir = Path(tmpdir) / "t"
        records = [
            json.loads(line)
            for line in (run_dir / "history.jsonl").read_text().splitlines()
        ]
        critique = records[-1]["metadata"]["critique"]
        serialized = json.dumps(critique)
        manifest = json.loads((run_dir / "manifest.json").read_text())
        surfaces = manifest["policies"]["prompt_data_retention"]["surfaces"]

        assert secret not in serialized
        assert critique["retention_mode"] == mode
        assert critique["prompt"] is None
        assert critique["original_diff"] is None
        assert critique["revised_diff"] is None
        assert bool(critique["prompt_sha256"]) is expect_hash
        assert bool(critique["original_diff_sha256"]) is expect_hash
        assert bool(critique["revised_diff_sha256"]) is expect_hash
        assert surfaces["critique_prompt"]["retention_mode"] == mode
        assert surfaces["critique_prompt"]["configurable"] is True
        assert surfaces["critique_mutation_text"]["retention_mode"] == mode
        assert manifest["config"]["critique_retention_mode"] == mode
    finally:
        shutil.rmtree(tmpdir)


def test_non_text_critique_revision_falls_back_to_original_mutation():
    workspace = CandidateWorkspace.from_code("x=1")
    original = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    selected, status = _select_critique_mutation(
        workspace, original, ["bad"], mutation_mode="diff"
    )

    assert selected == original
    assert status["accepted_revision"] is False
    assert status["selected_diff"] == "original"
    assert status["revised_diff_error"] == "non_text_mutation_payload"
    assert status["original_diff_error"] is None
    assert status["fallback_reason"] == "invalid_revised_diff"


def test_blank_critique_revision_falls_back_to_original_mutation():
    workspace = CandidateWorkspace.from_code("x=1")
    original = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"

    selected, status = _select_critique_mutation(
        workspace, original, "   \n\t", mutation_mode="diff"
    )

    assert selected == original
    assert status["accepted_revision"] is False
    assert status["selected_diff"] == "original"
    assert status["revised_diff_error"] == "blank_mutation_payload"
    assert status["original_diff_error"] is None
    assert status["fallback_reason"] == "invalid_revised_diff"


def test_oversized_critique_revision_falls_back_to_original_mutation(monkeypatch):
    workspace = CandidateWorkspace.from_code("x=1")
    original = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"
    max_payload_chars = len(original) + 1
    monkeypatch.setattr(
        "libreevolve.core.candidate.DEFAULT_MAX_MUTATION_PAYLOAD_CHARS",
        max_payload_chars,
    )

    selected, status = _select_critique_mutation(
        workspace, original, "x" * (max_payload_chars + 1), mutation_mode="diff"
    )

    assert selected == original
    assert status["accepted_revision"] is False
    assert status["selected_diff"] == "original"
    assert status["revised_diff_error"] == "oversized_mutation_payload"
    assert status["original_diff_error"] is None
    assert status["fallback_reason"] == "invalid_revised_diff"


def test_critique_selection_preserves_original_when_no_diff_candidate_is_valid():
    workspace = CandidateWorkspace.from_code("x=1")
    original = "<<<SEARCH\nmissing\n===\nx=2\n>>>REPLACE"
    revised = "this is not a mutation"

    selected, status = _select_critique_mutation(
        workspace, original, revised, mutation_mode="diff"
    )

    assert selected == original
    assert status["accepted_revision"] is False
    assert status["selected_diff"] == "original"
    assert status["revised_diff_error"] == "no_diff_blocks"
    assert status["original_diff_error"] == "search_not_found"
    assert status["fallback_reason"] == "no_valid_mutation"


def test_critique_selection_preserves_original_when_no_full_candidate_is_valid():
    workspace = CandidateWorkspace.from_code(
        "# EVOLVE-BLOCK-START\nx=1\n# EVOLVE-BLOCK-END\n"
    )
    original = "<<<BLOCK unknown\nx=2\n>>>BLOCK"
    revised = "<<<BLOCK block_0\nx=3\n>>>BLOCK\npreamble"

    selected, status = _select_critique_mutation(
        workspace, original, revised, mutation_mode="full"
    )

    assert selected == original
    assert status["accepted_revision"] is False
    assert status["selected_diff"] == "original"
    assert status["revised_diff_error"] == "malformed_block_sections:unconsumed_text"
    assert status["original_diff_error"] == "malformed_block_sections:unknown_name"
    assert status["fallback_reason"] == "no_valid_mutation"


def test_loop_applies_llm_feedback_to_candidate_score():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        ('{"score": 0.5, "feedback": "simple"}', 1),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        best = evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                llm_feedback=[
                    {
                        "name": "simplicity",
                        "metric": "simplicity",
                        "weight": 0.2,
                        "criterion": "simplicity",
                        "criterion_description": "Candidate should stay concise.",
                        "evaluator_gap_rationale": (
                            "The deterministic evaluator measures correctness, "
                            "not readability."
                        ),
                        "rubric": "Prefer fewer moving parts and clear names.",
                        "feedback_intent": "score",
                        "calibration_report_id": "simplicity_calibration_v1",
                    }
                ],
            ),
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    report = manifest["runtime"]["history"]["qualitative_feedback_policy_report"]
    audit = manifest["runtime"]["history"][
        "qualitative_feedback_prompt_history_audit_report"
    ]
    assert best.fitness == 1.1
    assert child["metrics"]["simplicity"] == 0.5
    feedback = child["evaluation"]["metadata"]["llm_feedback"][0]
    assert feedback["name"] == "simplicity"
    assert feedback["qualitative_policy"]["criterion"] == "simplicity"
    assert feedback["qualitative_policy"]["feedback_intent"] == "score"
    assert feedback["qualitative_policy"]["complete_for_current_policy"] is True

    assert report["schema"] == "libreevolve.qualitative_feedback_policy_report.v1"
    assert report["validation"]["ok"] is True
    assert validate_qualitative_feedback_policy_report(report)["ok"] is True
    assert report["configured_llm_feedback_count"] == 1
    assert report["configured_qualitative_policy_count"] == 1
    assert report["complete_policy_count"] == 1
    assert report["observed_feedback_record_count"] == 1
    assert report["claim_ready"] is False
    policy_record = report["records"][0]
    assert policy_record["feedback_id"] == "llm_feedback:simplicity"
    assert policy_record["criterion_description_present"] is True
    assert policy_record["evaluator_gap_rationale_present"] is True
    assert len(policy_record["rubric_sha256"]) == 64
    assert policy_record["calibration_report_id"] == "simplicity_calibration_v1"
    assert policy_record["runtime_record_count"] == 1

    assert audit["schema"] == (
        "libreevolve.qualitative_feedback_prompt_history_audit_report.v1"
    )
    assert audit["validation"]["ok"] is True
    assert (
        validate_qualitative_feedback_prompt_history_audit_report(audit)["ok"]
        is True
    )
    assert audit["configured_llm_feedback_count"] == 1
    assert audit["candidate_with_feedback_count"] == 1
    assert audit["observed_feedback_record_count"] == 1
    assert audit["prompt_history_add_join_count"] == 1
    assert audit["prompt_history_score_join_count"] == 1
    assert audit["claim_ready"] is False
    assert audit["claim_readiness"]["feedback_records_observed"] is True
    assert audit["claim_readiness"]["prompt_history_score_rows_joined"] is True
    assert audit["claim_readiness"]["calibration_or_task_suite_linkage"] is False
    assert audit["claim_readiness"]["criterion_quality_ablation"] is False
    audit_record = audit["records"][0]
    assert audit_record["candidate_id"] == child["id"]
    assert audit_record["feedback_names"] == ["simplicity"]
    assert audit_record["prompt_history_add_joined"] is True
    assert audit_record["prompt_history_score_joined"] is True
    assert audit_record["prompt_history"]["score_line_number"] == 2

    overclaimed = copy.deepcopy(report)
    overclaimed["policy"]["paper_claim_ready"] = True
    overclaimed["claim_ready"] = True
    validation = validate_qualitative_feedback_policy_report(overclaimed)
    assert validation["ok"] is False
    assert {
        issue["code"] for issue in validation["issues"]
    } >= {"qualitative_feedback_overclaim", "claim_ready_overclaim"}

    overclaimed_audit = copy.deepcopy(audit)
    overclaimed_audit["audit_policy"]["paper_claim_ready"] = True
    overclaimed_audit["claim_ready"] = True
    overclaimed_audit["claim_readiness"]["alphaevolve_qualitative_feedback_audit"] = True
    validation = validate_qualitative_feedback_prompt_history_audit_report(
        overclaimed_audit
    )
    assert validation["ok"] is False
    assert {issue["code"] for issue in validation["issues"]} >= {
        "qualitative_feedback_audit_overclaim",
        "claim_ready_overclaim",
        "alphaevolve_qualitative_feedback_audit_overclaim",
    }


def test_loop_honors_feedback_retention_mode_in_history_and_manifest():
    tmpdir = tempfile.mkdtemp()
    secret = "sk-proj_loop_feedback_retention_secret_1234567890"  # pragma: allowlist secret
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        (json.dumps({"score": 0.5, "feedback": f"retain? {secret}"}), 1),
    ]
    try:
        with patch("libreevolve.core.loop.build_llm", return_value=llm):
            evolve(
                _problem(),
                Config(
                    max_generations=1,
                    log_dir=tmpdir,
                    problem_name="t",
                    llm_feedback=[
                        {"name": "simplicity", "metric": "simplicity", "weight": 0.2}
                    ],
                    feedback_retention_mode="hash_only",
                ),
            )

        run_dir = Path(tmpdir) / "t"
        records = [
            json.loads(line)
            for line in (run_dir / "history.jsonl").read_text().splitlines()
        ]
        child = records[-1]
        feedback = child["evaluation"]["metadata"]["llm_feedback"][0]
        manifest = json.loads((run_dir / "manifest.json").read_text())
        surfaces = manifest["policies"]["prompt_data_retention"]["surfaces"]

        assert secret not in strict_json_dumps(feedback)
        assert feedback["feedback"] is None
        assert feedback["raw_response"] is None
        assert feedback["feedback_retention"]["retention_mode"] == "hash_only"
        assert feedback["raw_response_retention"]["retention_mode"] == "hash_only"
        assert len(feedback["feedback_retention"]["sha256"]) == 64
        assert len(feedback["raw_response_retention"]["sha256"]) == 64
        assert manifest["config"]["feedback_retention_mode"] == "hash_only"
        assert surfaces["feedback_raw_response"]["retention_mode"] == "hash_only"
        assert surfaces["feedback_raw_response"]["configurable"] is True
        assert surfaces["feedback_parsed_fields"]["retention_mode"] == "hash_only"
    finally:
        shutil.rmtree(tmpdir)


def test_evolve_passes_parent_baseline_to_causal_plugin():
    validator = (
        "def evaluate(c):\n"
        "    return {'score': 1.0 if 'x=2' in c else 0.2, 'is_valid': True}\n"
    )
    plugin = CausalPlugin()
    tmpdir = tempfile.mkdtemp()

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(validator),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[plugin],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    assert child["metadata"]["causal_reward_baseline"] == {
        "source": "parent_program",
        "parent_id": records[0]["id"],
        "score": 0.2,
    }
    assert plugin._history[0]["baseline_source"] == "parent_program"
    assert plugin._history[0]["baseline_parent_id"] == records[0]["id"]
    assert plugin._history[0]["delta"] == pytest.approx(0.8)
