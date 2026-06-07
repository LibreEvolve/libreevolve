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
from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.budget import (
    RunBudget,
    apply_controller_budget_event,
    validate_controller_budget_event,
)
from libreevolve.core.config import Config
from libreevolve.core.jsonl import StrictJsonlError, strict_json_dumps
from libreevolve.core.loop import (
    CONTROLLER_STATE_ARTIFACT_INVENTORY_SCHEMA,
    FULL_RESUME_BUNDLE_VALIDATION_SCHEMA,
    RuntimeFullResumeBundleError,
    RuntimeLineageReplayPolicyError,
    RuntimeLLMSchedulerStateError,
    RuntimeRngStateError,
    controller_state_artifact_inventory,
    evolve,
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
    _select_critique_mutation,
)
from libreevolve.core.meta_prompt import PromptDatabase, PromptProgram
from libreevolve.core.prompt import DEFAULT_TEMPLATE, validate_prompt_context_policy
from libreevolve.llm.ensemble import LLMEnsemble, LLM_PROVIDER_DIAGNOSTICS_SCHEMA
from libreevolve.llm.budget_report import (
    LLM_BUDGET_REPORT_SCHEMA,
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
    assert consumed["candidate_evaluations"] == 3
    assert manifest["config"]["proposals_per_generation"] == 3


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
    assert archive_state["islands"][0]["occupied_cell_count"] == 1
    assert archive_state["islands"][1]["occupied_cell_count"] == 0
    assert archive_state["islands"][2]["occupied_cell_count"] == 0
    replay_audit = manifest["runtime"]["history"]["archive_event_replay_audit"]
    assert replay_audit["schema"] == "libreevolve.archive_event_replay_audit.v1"
    assert replay_audit["status"] == "archive_events_absent"
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
    assert accounting["reward_accounting_policy"] == {
        "policy": "configured_reward_accounted_roles_v1",
        "reward_accounted_roles": ["mutation"],
    }
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
    assert budget_report["status"] == "audit_snapshot"
    assert budget_report["policy"] == "runtime_observed_usage_not_budget_enforced"
    assert budget_report["paper_budget_ready"] is False
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

    validation = validate_full_resume_bundle(edited)
    codes = {issue["code"] for issue in validation["issues"]}

    assert validation["schema"] == FULL_RESUME_BUNDLE_VALIDATION_SCHEMA
    assert validation["ok"] is False
    assert validation["compatible_resume_ready"] is False
    assert validation["full_replay_ready"] is False
    assert validation["provider_output_replay_ready"] is False
    assert "invalid_lineage_replay_policy" in codes
    assert "provider_output_replay_overclaim" in codes
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


def test_materialization_collision_is_logged_as_failed_candidate():
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
    assert child["evaluation"]["error"] == "materialization_error"
    assert child["evaluation"]["metadata"]["materialization_error"]["exception_type"] == "ValueError"
    assert child["metadata"]["archive_admission"]["reason"] == "invalid_evaluation"
    failure_records = [
        json.loads(line)
        for line in (run_dir / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failure_records[-1]["evaluation"]["error"] == "materialization_error"
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
    assert state["loaded_specs"][0]["direct_plugin_policy"] == {
        "schema": "libreevolve.direct_plugin_policy.v1",
        "source": "direct_instance",
        "constructor_value_policy": "constructor_values_excluded_signature_shape_only",
        "constructor_values_captured": False,
        "constructor_schema_policy": "not_available_for_direct_instances",
        "constructor_signature_policy": "names_kinds_required_flags_only",
        "instance_attribute_policy": "not_captured",
        "package_scope_policy": (
            "direct_instance_module_identity_file_hash_and_version_only"
        ),
        "paper_scope_policy": "not_available_for_direct_instances",
    }
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
    assert spec["direct_plugin_policy"] == {
        "schema": "libreevolve.direct_plugin_policy.v1",
        "source": "entry_point",
        "constructor_value_policy": (
            "manifest_safe_or_schema_validated_constructor_options_captured"
        ),
        "constructor_values_captured": True,
        "constructor_schema_policy": "entry_point_declared_schema_or_manifest_safe_json",
        "constructor_signature_policy": "names_kinds_required_flags_only",
        "instance_attribute_policy": "not_captured",
        "package_scope_policy": (
            "entry_point_distribution_name_version_record_wheel_metadata"
        ),
        "paper_scope_policy": "configured_entry_point_paper_inspiration_labels",
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
    assert pool["reviewer_count"] == 2
    assert pool["valid_revision_count"] == 2
    assert pool["selected_reviewer"] == "simplicity"
    assert [reviewer["reviewer_role"] for reviewer in pool["reviewers"]] == [
        "critique:correctness",
        "critique:simplicity",
    ]
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
    revised = "preamble\n<<<BLOCK block_0\nx=3\n>>>BLOCK"

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
                    {"name": "simplicity", "metric": "simplicity", "weight": 0.2}
                ],
            ),
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert best.fitness == 1.1
    assert child["metrics"]["simplicity"] == 0.5
    assert child["evaluation"]["metadata"]["llm_feedback"][0]["name"] == "simplicity"


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
