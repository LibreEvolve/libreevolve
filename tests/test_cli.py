import base64
import hashlib, json, random, tempfile
import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
from click.testing import CliRunner
import libreevolve.core.loop as loop_module
import libreevolve.core.best_artifacts as best_artifacts_module
from libreevolve.cli import (
    cli,
    _load_best_artifact_export_record,
    _load_plugins,
)
from libreevolve.core.best_artifacts import BestArtifactExportError, _write_best_artifacts
from libreevolve.core.config import Config
from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.database import ProgramDatabase, _validator_execution_policy
from libreevolve.core.evaluator import _validator_boundary_metadata
from libreevolve.core.artifact_schema import (
    paper_artifact_subpath_schema,
    run_artifact_schema,
)
from libreevolve.core.loop import _runtime_llm_scheduler_state, _runtime_rng_state
from libreevolve.llm.ensemble import LLMEnsemble
from libreevolve.plugins.base import PluginBase
from libreevolve.plugins.deep_research import DeepResearchPlugin
from libreevolve.plugins.ttt_rl import TTTRLPlugin
from libreevolve.population.program import Program
from libreevolve.problems.loader import load_problem
import pytest
import yaml

def _objective_schema():
    return {
        "metrics": [
            {
                "name": "score",
                "direction": "maximize",
                "primary": True,
                "bounds": [0.0, 1.0],
            }
        ],
        "primary_metric": "score",
        "primary_bounds": [0.0, 1.0],
        "metric_count": 1,
    }


class _EntryPointPlugin(PluginBase):
    def __init__(self, mode: str = "default", limit: int = 1):
        self.mode = mode
        self.limit = limit

    def run_artifacts_metadata(self):
        return {"entry_point": True}


class _SchemaEntryPointPlugin(PluginBase):
    libreevolve_constructor_option_schema = {
        "mode": {"type": "enum", "values": ["audit", "dry_run"]},
        "limit": {"type": "positive_int"},
    }

    def __init__(self, mode: str = "audit", limit: int = 1):
        self.mode = mode
        self.limit = limit


class _FakeDistribution:
    version = "1.2.3"
    metadata = {"Name": "libreevolve-test-plugin"}


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

def _make_problem(tmp_path):
    os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
    os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
    (tmp_path/"task_description.txt").write_text("t")
    (tmp_path/"metrics.yaml").write_text(yaml.dump({"metrics": [
        {"name":"score","primary":True,"direction":"maximize","bounds":[0.0,1.0]}]}))
    (tmp_path/"validate.py").write_text("def evaluate(c): return {'score':1.0,'is_valid':True}")
    s = tmp_path/"initial_programs"; s.mkdir(); (s/"seed.py").write_text("x=1")


def _show_current_row(program_id: str, fitness: float, generation: int, code: str) -> dict:
    return {
        "id": program_id,
        "code": code,
        "fitness": fitness,
        "generation": generation,
        "metadata": {
            "archive_admission": {
                "admitted": True,
                "selection_score": fitness,
            }
        },
        "metrics": {"score": fitness, "is_valid": True},
        "evaluation": {
            "is_valid": True,
            "metadata": {"validator_boundary": _validator_boundary_metadata("host")},
        },
    }


def _write_show_history(run_dir: Path, rows: list[dict]) -> None:
    (run_dir / "history.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def _write_show_manifest(
    run_dir: Path,
    *,
    status: str = "completed",
    stop_reason: str = "max_generations",
    programs_logged: int = 1,
    config: dict | None = None,
) -> None:
    manifest = {
        "runtime": {
            "status": status,
            "stop_reason": stop_reason,
            "history": {"programs_logged": programs_logged},
        },
        "policies": {"validator_execution": _validator_execution_policy("host")},
    }
    if config is not None:
        manifest["config"] = config
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def _write_show_paper_artifact_manifest(run_dir: Path) -> dict:
    schema = paper_artifact_subpath_schema()
    artifact_schema = run_artifact_schema()
    paths_by_family = {
        family_name: [
            record["path"] for record in family["path_records"]
        ]
        for family_name, family in schema["families"].items()
    }
    runtime_artifacts = {
        name: {
            "path": artifact["path"],
            "exists": False,
            "present": False,
        }
        for name, artifact in artifact_schema["non_jsonl_artifacts"].items()
    }
    runtime_artifacts["manifest.json"] = {
        "path": "manifest.json",
        "exists": True,
        "present": True,
        "kind": "file",
        "hash_scope": "final_manifest_self_reference_deferred",
    }
    runtime_artifacts["paper_artifacts"] = {
        "path": "paper_artifacts",
        "exists": False,
        "present": False,
    }
    manifest = {
        "artifact_schema": artifact_schema,
        "runtime": {
            "status": "completed",
            "stop_reason": "max_generations",
            "history": {
                "programs_logged": 1,
                "marker_spelling_provenance_report": {
                    "source_artifacts": {
                        "page_artifacts": {
                            "4": {
                                "artifact_path": paths_by_family[
                                    "marker_spelling"
                                ][0]
                            },
                            "6": {
                                "artifact_path": paths_by_family[
                                    "marker_spelling"
                                ][1]
                            },
                        },
                        "figure_3_marker_text_artifact": {
                            "artifact_path": paths_by_family["marker_spelling"][2]
                        },
                    }
                },
                "alphaevolve_process_exhibit_report": {
                    "artifact_evidence": [
                        {"path": path}
                        for path in paths_by_family["process_exhibit"]
                    ]
                },
                "alphaevolve_table1_capability_exhibit_report": {
                    "rendered_artifacts": [
                        {"path": path}
                        for path in paths_by_family[
                            "table1_capability_comparison"
                        ]
                    ]
                },
            },
            "artifacts": runtime_artifacts,
        },
        "policies": {"validator_execution": _validator_execution_policy("host")},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


def _run_artifact_bundle_report_overclaim() -> dict:
    return {
        "schema": "libreevolve.run_artifact_bundle_report.v1",
        "source": "runtime_artifact_schema_pointers_and_quarantine_diagnostics",
        "accepted_stream_count": 0,
        "accepted_streams": [],
        "quarantine_stream_count": 0,
        "quarantine_record_count": 0,
        "quarantine_streams": [],
        "quarantine_validation_ok": True,
        "non_jsonl_checked_artifact_count": 0,
        "non_jsonl_validation_ok": True,
        "paper_artifact_lifecycle_checked": False,
        "paper_artifact_emitted_path_count": 0,
        "paper_artifact_validation_ok": None,
        "issue_codes": [],
        "accepted_state_boundary": {
            "quarantine_rows_are_diagnostics": True,
            "quarantine_rows_replayed_as_state": False,
            "non_jsonl_artifacts_are_policy_checked": True,
            "provider_output_replay": True,
            "pending_controller_work_replay": False,
        },
        "claim_ready": False,
        "claim_readiness": {
            "accepted_streams_counted": True,
            "quarantine_diagnostics_validated": True,
            "non_jsonl_policy_validated": True,
            "paper_artifact_lifecycle_validated": False,
            "persisted_manifest_report": True,
            "full_restore_replay_certification": False,
            "remaining_gap": [],
        },
    }


def _restore_certification_overclaim() -> dict:
    return {
        "schema": "libreevolve.full_resume_restore_certification.v1",
        "status": "compatible_surfaces_certified",
        "scope": "local_manifest_restore_inputs_only",
        "certified_surfaces": [
            "runtime_rng_state_snapshot",
            "runtime_llm_scheduler_state_snapshot",
            "runtime_archive_state_snapshot",
            "runtime_archive_programs_by_id",
            "runtime_budget_state_snapshot",
            "controller_budget_event_replay",
            "lineage_provider_boundary",
            "run_artifact_bundle_report",
        ],
        "run_artifact_bundle_report": {
            "status": "absent",
            "validation_ok": None,
            "promotion_gate_status": None,
        },
        "accepted_quarantine_boundary": {
            "quarantine_rows_replayed_as_state": False,
            "quarantine_rows_are_diagnostics": True,
        },
        "compatible_resume_ready": True,
        "full_replay_ready": False,
        "provider_output_replay_ready": True,
        "pending_work_resume_ready": False,
        "resumed_trace_proof_ready": False,
        "remaining_gap": [
            "provider_output_replay_or_exclusion_in_resumed_trace",
            "pending_controller_work_resume",
            "migration_event_replay_engine",
            "end_to_end_resumed_trace_proof",
        ],
    }


def test_help(): assert "run" in CliRunner().invoke(cli, ["--help"]).output
def test_run_help(): assert "PROBLEM_DIR" in CliRunner().invoke(cli, ["run", "--help"]).output
def test_show_help(): assert CliRunner().invoke(cli, ["show", "--help"]).exit_code == 0


def test_importing_cli_does_not_load_dotenv_from_cwd(tmp_path):
    (tmp_path / ".env").write_text(
        "LIBREEVOLVE_DOTENV_PROBE=from_dotenv\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["LIBREEVOLVE_DOTENV_PROBE"] = "from_parent"
    repo_root = Path(__file__).resolve().parents[1]
    env["PYTHONPATH"] = (
        str(repo_root)
        if not env.get("PYTHONPATH")
        else str(repo_root) + os.pathsep + env["PYTHONPATH"]
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import os, libreevolve.cli; print(os.environ['LIBREEVOLVE_DOTENV_PROBE'])",
        ],
        cwd=tmp_path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == "from_parent"


def test_show_does_not_load_dotenv_from_cwd(tmp_path, monkeypatch):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_show_history(run_dir, [_show_current_row("p1", 1.0, 0, "x=1")])
    _write_show_manifest(run_dir)
    (tmp_path / ".env").write_text(
        "LIBREEVOLVE_DOTENV_PROBE=from_dotenv\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LIBREEVOLVE_DOTENV_PROBE", "from_parent")

    r = CliRunner().invoke(cli, ["show", str(run_dir)])

    assert r.exit_code == 0
    assert os.environ["LIBREEVOLVE_DOTENV_PROBE"] == "from_parent"


def test_show_rejects_run_artifact_bundle_report_overclaim(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_show_history(run_dir, [_show_current_row("p1", 1.0, 0, "x=1")])
    _write_show_manifest(run_dir)
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["runtime"]["run_artifact_bundle_report"] = (
        _run_artifact_bundle_report_overclaim()
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(run_dir)])

    assert r.exit_code != 0
    assert "run artifact bundle report validation failed" in r.output
    assert "provider_output_replay_overclaim" in r.output


def test_show_rejects_restore_certification_overclaim(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_show_history(run_dir, [_show_current_row("p1", 1.0, 0, "x=1")])
    _write_show_manifest(run_dir)
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["runtime"]["restore_certification"] = _restore_certification_overclaim()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(run_dir)])

    assert r.exit_code != 0
    assert "Restore certification validation failed" in r.output
    assert "restore_certification_provider_output_replay_ready_overclaim" in r.output


def test_module_help_uses_documented_windows_launcher():
    result = subprocess.run(
        [sys.executable, "-m", "libreevolve", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Usage: py -3.12 -m libreevolve [OPTIONS] COMMAND [ARGS]..." in result.stdout
    assert "Usage: python -m libreevolve" not in result.stdout


def test_module_run_help_uses_documented_windows_launcher():
    result = subprocess.run(
        [sys.executable, "-m", "libreevolve", "run", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Usage: py -3.12 -m libreevolve run [OPTIONS] PROBLEM_DIR" in result.stdout
    assert "Usage: python -m libreevolve run" not in result.stdout


def test_run_calls_evolve(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(f"log_dir: {(tmp_path / 'runs').as_posix()}\n")
    mock_best = Program(code="x=2", fitness=0.99)
    with patch("libreevolve.cli.evolve", return_value=mock_best) as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--max-generations", "1"])
    assert r.exit_code == 0 and mock.called


def test_run_records_strict_initial_program_report_for_embedded_fixture(tmp_path):
    source = (
        Path(__file__).resolve().parents[1]
        / "libreevolve"
        / "problems"
        / "examples"
        / "embedded_evaluate_math"
    )
    problem_dir = tmp_path / "embedded_evaluate_math"
    shutil.copytree(source, problem_dir)
    config_path = problem_dir / "config.yaml"
    config_path.write_text(
        config_path.read_text(encoding="utf-8")
        + f"\nlog_dir: {(tmp_path / 'runs').as_posix()}\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        cli,
        [
            "run",
            str(problem_dir),
            "--max-generations",
            "0",
            "--run-name",
            "strict_embedded",
        ],
    )

    assert result.exit_code == 0, result.output
    manifest_path = tmp_path / "runs" / "strict_embedded" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report = manifest["runtime"]["history"]["initial_program_validity_report"]
    assert manifest["runtime"]["status"] == "completed"
    assert manifest["config"]["initial_program_validity_policy"] == "alphaevolve_strict"
    assert (
        manifest["policies"]["initial_program_validity"]["policy"]
        == "alphaevolve_strict"
    )
    assert report["strict_policy_enabled"] is True
    assert report["claim_ready"] is True
    assert report["strict_invalid_seed_count"] == 0
    assert report["strict_valid_seed_count"] == 1
    assert report["claim_readiness"]["alphaevolve_complete_initial_program_parity"] is True
    assert (
        manifest["runtime"]["history"]["embedded_evaluator_entrypoint_report"][
            "embedded_entrypoint_count"
        ]
        == 1
    )


def test_run_budget_cli_options_override_config(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(f"log_dir: {(tmp_path / 'runs').as_posix()}\n")
    mock_best = Program(code="x=2", fitness=0.99)

    with patch("libreevolve.cli.evolve", return_value=mock_best) as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--max-generations",
                "3",
                "--max-evaluations",
                "7",
                "--max-evaluator-seconds",
                "11.5",
                "--max-runtime-seconds",
                "30",
                "--max-llm-calls",
                "9",
                "--max-llm-provider-attempts",
                "12",
                "--max-llm-tokens",
                "2000",
                "--max-llm-cost-microusd",
                "5000",
                "--max-llm-seconds",
                "13.5",
            ],
        )

    assert r.exit_code == 0
    config = mock.call_args.args[1]
    assert config.max_generations == 3
    assert config.max_evaluations == 7
    assert config.max_evaluator_seconds == 11.5
    assert config.max_runtime_seconds == 30.0
    assert config.max_llm_calls == 9
    assert config.max_llm_provider_attempts == 12
    assert config.max_llm_tokens == 2000
    assert config.max_llm_cost_microusd == 5000
    assert config.max_llm_seconds == 13.5


def test_run_rejects_invalid_config_switches_before_evolve(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "critique_enabled": "false",
            }
        )
    )

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code == 1
    assert "critique_enabled" in r.output
    assert not mock.called


def test_run_rejects_unsafe_config_log_dir_before_evolve(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text('log_dir: "runs/line\\nbreak"\n', encoding="utf-8")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code == 1
    assert "log_dir must be a path-safe log directory" in r.output
    assert "WinError" not in r.output
    assert not mock.called


def test_run_rejects_unsafe_run_name_before_evolve(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(f"log_dir: {(tmp_path / 'runs').as_posix()}\n")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--run-name", "../escape"])

    assert r.exit_code == 1
    assert "problem_name" in r.output
    assert not mock.called


def test_run_rejects_del_control_run_name_before_evolve(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(f"log_dir: {(tmp_path / 'runs').as_posix()}\n")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--run-name", "bad\x7fname"])

    assert r.exit_code == 1
    assert "problem_name" in r.output
    assert not mock.called


def test_run_rejects_unicode_format_control_run_name_before_evolve(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(f"log_dir: {(tmp_path / 'runs').as_posix()}\n")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--run-name", "rtl\u202egnp"])

    assert r.exit_code == 1
    assert "problem_name" in r.output
    assert not mock.called


def test_run_rejects_reserved_run_name_before_evolve(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(f"log_dir: {(tmp_path / 'runs').as_posix()}\n")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--run-name", "CON"])

    assert r.exit_code == 1
    assert "problem_name" in r.output
    assert not mock.called


def test_run_rejects_secret_like_run_name_before_evolve(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(f"log_dir: {(tmp_path / 'runs').as_posix()}\n")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--run-name",
                "api_key=sk-proj_runname_secret_1234567890",
            ],
        )

    assert r.exit_code == 1
    assert "secret-safe run-name component" in r.output
    assert "sk-proj_runname_secret_1234567890" not in r.output
    assert not mock.called


def test_run_rejects_problem_name_in_config_yaml_before_evolve(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "problem_name": "ignored-name",
            }
        ),
        encoding="utf-8",
    )

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code == 1
    assert "config.yaml problem_name is not used by the CLI" in r.output
    assert "--run-name" in r.output
    assert not mock.called


def test_run_name_cli_override_is_manifest_effective_problem_name(tmp_path):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    (tmp_path / "config.yaml").write_text(
        f"log_dir: {log_dir.as_posix()}\n",
        encoding="utf-8",
    )

    r = CliRunner().invoke(
        cli,
        [
            "run",
            str(tmp_path),
            "--max-generations",
            "0",
            "--run-name",
            "explicit-run",
        ],
    )

    run_dir = log_dir / "explicit-run"
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert r.exit_code == 0
    assert manifest["config"]["problem_name"] == "explicit-run"
    assert "Running 0 generations on 'explicit-run'" in r.output
    assert not (log_dir / tmp_path.name).exists()


def test_run_sampling_cli_options_override_config(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "parent_selection_strategy": "exploit",
                "inspiration_strategy": "selection",
            }
        )
    )
    mock_best = Program(code="x=2", fitness=0.99)

    with patch("libreevolve.cli.evolve", return_value=mock_best) as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--parent-selection-strategy",
                "lineage",
                "--inspiration-strategy",
                "lineage",
                "--prompt-max-chars",
                "2048",
                "--prompt-max-estimated-tokens",
                "512",
            ],
        )

    assert r.exit_code == 0
    config = mock.call_args.args[1]
    assert config.parent_selection_strategy == "lineage"
    assert config.inspiration_strategy == "lineage"
    assert config.prompt_max_chars == 2048
    assert config.prompt_max_estimated_tokens == 512


def test_run_can_restore_runtime_rng_snapshot_from_manifest(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "seed": 123,
            }
        ),
        encoding="utf-8",
    )
    snapshot = _runtime_rng_state(random.Random(123), 123)
    previous_manifest = tmp_path / "previous-manifest.json"
    previous_manifest.write_text(
        json.dumps({"runtime": {"rng": snapshot}}),
        encoding="utf-8",
    )
    mock_best = Program(code="x=2", fitness=0.99)

    with patch("libreevolve.cli.evolve", return_value=mock_best) as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--max-generations",
                "0",
                "--restore-rng-from-manifest",
                str(previous_manifest),
            ],
        )

    assert r.exit_code == 0
    assert mock.call_args.kwargs["runtime_rng_state_snapshot"] == snapshot


def test_run_rejects_paper_artifact_lifecycle_drift_before_restore(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "seed": 123,
            }
        ),
        encoding="utf-8",
    )
    previous_dir = tmp_path / "previous"
    previous_dir.mkdir()
    manifest = _write_show_paper_artifact_manifest(previous_dir)
    manifest["runtime"]["rng"] = _runtime_rng_state(random.Random(123), 123)
    manifest["runtime"]["history"]["alphaevolve_table1_capability_exhibit_report"][
        "rendered_artifacts"
    ][0]["path"] = "paper_artifacts/table1_capability_comparison/unregistered.md"
    previous_manifest = previous_dir / "manifest.json"
    previous_manifest.write_text(json.dumps(manifest), encoding="utf-8")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--max-generations",
                "0",
                "--restore-rng-from-manifest",
                str(previous_manifest),
            ],
        )

    assert r.exit_code != 0
    assert "Runtime RNG manifest restore failed" in r.output
    assert "paper artifact lifecycle validation failed" in r.output
    assert "unknown_paper_artifact_paths" in r.output
    assert not mock.called


@pytest.mark.parametrize(
    ("restore_flag", "error_prefix"),
    [
        ("--restore-rng-from-manifest", "Runtime RNG manifest restore failed"),
        (
            "--restore-llm-scheduler-from-manifest",
            "LLM scheduler manifest restore failed",
        ),
        ("--restore-budget-from-manifest", "Runtime budget manifest restore failed"),
        (
            "--restore-archive-cursor-from-manifest",
            "Archive cursor manifest restore failed",
        ),
        ("--restore-archive-from-manifest", "Archive manifest restore failed"),
        ("--restore-runtime-from-manifest", "Runtime manifest restore failed"),
    ],
)
def test_run_rejects_non_jsonl_artifact_policy_drift_before_restore(
    tmp_path,
    restore_flag,
    error_prefix,
):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "seed": 123,
            }
        ),
        encoding="utf-8",
    )
    previous_dir = tmp_path / "previous"
    previous_dir.mkdir()
    manifest = _write_show_paper_artifact_manifest(previous_dir)
    manifest["runtime"]["rng"] = _runtime_rng_state(random.Random(123), 123)
    manifest["runtime"]["artifacts"]["task_specification.json"] = {
        "path": "task_specification.json",
        "exists": True,
        "present": True,
        "kind": "file",
        "hash_scope": "file_bytes",
    }
    previous_manifest = previous_dir / "manifest.json"
    previous_manifest.write_text(json.dumps(manifest), encoding="utf-8")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--max-generations",
                "0",
                restore_flag,
                str(previous_manifest),
            ],
        )

    assert r.exit_code != 0
    assert error_prefix in r.output
    assert "non-JSONL artifact policy validation failed" in r.output
    assert "missing_non_jsonl_file_sha256" in r.output
    assert not mock.called


@pytest.mark.parametrize(
    ("restore_flag", "error_prefix"),
    [
        ("--restore-rng-from-manifest", "Runtime RNG manifest restore failed"),
        (
            "--restore-llm-scheduler-from-manifest",
            "LLM scheduler manifest restore failed",
        ),
        ("--restore-budget-from-manifest", "Runtime budget manifest restore failed"),
        (
            "--restore-archive-cursor-from-manifest",
            "Archive cursor manifest restore failed",
        ),
        ("--restore-archive-from-manifest", "Archive manifest restore failed"),
        ("--restore-runtime-from-manifest", "Runtime manifest restore failed"),
    ],
)
def test_run_rejects_quarantine_artifact_drift_before_restore(
    tmp_path,
    restore_flag,
    error_prefix,
):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "seed": 123,
            }
        ),
        encoding="utf-8",
    )
    previous_dir = tmp_path / "previous"
    previous_dir.mkdir()
    previous_manifest = previous_dir / "manifest.json"
    previous_manifest.write_text(
        json.dumps(
            {
                "artifact_schema": {
                    "quarantine_jsonl_records": run_artifact_schema()[
                        "quarantine_jsonl_records"
                    ],
                },
                "runtime": {},
            }
        ),
        encoding="utf-8",
    )
    (previous_dir / "history_invalid.jsonl").write_text(
        json.dumps({"error": "ValueError"}) + "\n",
        encoding="utf-8",
    )

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--max-generations",
                "0",
                restore_flag,
                str(previous_manifest),
            ],
        )

    assert r.exit_code != 0
    assert error_prefix in r.output
    assert "quarantine artifact validation failed" in r.output
    assert "invalid_quarantine_stream_rows" in r.output
    assert "history_invalid.jsonl" in r.output
    assert not mock.called


@pytest.mark.parametrize(
    ("restore_flag", "error_prefix"),
    [
        ("--restore-rng-from-manifest", "Runtime RNG manifest restore failed"),
        (
            "--restore-llm-scheduler-from-manifest",
            "LLM scheduler manifest restore failed",
        ),
        ("--restore-budget-from-manifest", "Runtime budget manifest restore failed"),
        (
            "--restore-archive-cursor-from-manifest",
            "Archive cursor manifest restore failed",
        ),
        ("--restore-archive-from-manifest", "Archive manifest restore failed"),
        ("--restore-runtime-from-manifest", "Runtime manifest restore failed"),
    ],
)
def test_run_rejects_run_artifact_bundle_report_overclaim_before_restore(
    tmp_path,
    restore_flag,
    error_prefix,
):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "seed": 123,
            }
        ),
        encoding="utf-8",
    )
    previous_manifest = tmp_path / "previous-manifest.json"
    previous_manifest.write_text(
        json.dumps(
            {
                "runtime": {
                    "run_artifact_bundle_report": (
                        _run_artifact_bundle_report_overclaim()
                    )
                }
            }
        ),
        encoding="utf-8",
    )

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--max-generations",
                "0",
                restore_flag,
                str(previous_manifest),
            ],
        )

    assert r.exit_code != 0
    assert error_prefix in r.output
    assert "run artifact bundle report validation failed" in r.output
    assert "provider_output_replay_overclaim" in r.output
    assert not mock.called


@pytest.mark.parametrize(
    ("restore_flag", "error_prefix"),
    [
        ("--restore-rng-from-manifest", "Runtime RNG manifest restore failed"),
        (
            "--restore-llm-scheduler-from-manifest",
            "LLM scheduler manifest restore failed",
        ),
        ("--restore-budget-from-manifest", "Runtime budget manifest restore failed"),
        (
            "--restore-archive-cursor-from-manifest",
            "Archive cursor manifest restore failed",
        ),
        ("--restore-archive-from-manifest", "Archive manifest restore failed"),
        ("--restore-runtime-from-manifest", "Runtime manifest restore failed"),
    ],
)
def test_run_rejects_restore_certification_overclaim_before_restore(
    tmp_path,
    restore_flag,
    error_prefix,
):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "seed": 123,
            }
        ),
        encoding="utf-8",
    )
    previous_manifest = tmp_path / "previous-manifest.json"
    previous_manifest.write_text(
        json.dumps(
            {
                "runtime": {
                    "restore_certification": _restore_certification_overclaim()
                }
            }
        ),
        encoding="utf-8",
    )

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--max-generations",
                "0",
                restore_flag,
                str(previous_manifest),
            ],
        )

    assert r.exit_code != 0
    assert error_prefix in r.output
    assert "runtime restore certification validation failed" in r.output
    assert "restore_certification_provider_output_replay_ready_overclaim" in r.output
    assert not mock.called


def test_run_can_restore_llm_scheduler_snapshot_from_manifest(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "backends": [
                    {"type": "openai", "model": "gpt-4o-mini"},
                    {"type": "openai", "model": "gpt-4o-mini"},
                ],
            }
        ),
        encoding="utf-8",
    )
    backend_one = type(
        "BackendOne",
        (),
        {"name": "one", "generate": lambda self, prompt, role="mutation": "ok"},
    )()
    backend_two = type(
        "BackendTwo",
        (),
        {"name": "two", "generate": lambda self, prompt, role="mutation": "ok"},
    )()
    llm = LLMEnsemble([backend_one, backend_two])
    llm.restore_scheduler_state({"counts": [2, 1], "wins": [1.0, 0.0], "total": 3})
    snapshot = _runtime_llm_scheduler_state(llm)
    previous_manifest = tmp_path / "previous-manifest.json"
    previous_manifest.write_text(
        json.dumps({"runtime": {"llm_scheduler": snapshot}}),
        encoding="utf-8",
    )
    mock_best = Program(code="x=2", fitness=0.99)

    with patch("libreevolve.cli.evolve", return_value=mock_best) as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--restore-llm-scheduler-from-manifest",
                str(previous_manifest),
            ],
        )

    assert r.exit_code == 0
    assert mock.call_args.kwargs["runtime_llm_scheduler_state_snapshot"] == snapshot


def test_run_can_restore_archive_cursor_snapshot_from_manifest(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "n_islands": 2,
            }
        ),
        encoding="utf-8",
    )
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
        "frontier_sample_index": 0,
        "lineage_sample_index": 0,
        "archive_sequence_by_program_id": {"p1": 1, "p2": 3},
        "islands": [
            {"island_id": 0, "occupied_cell_count": 1, "elite_count": 1},
            {"island_id": 1, "occupied_cell_count": 1, "elite_count": 1},
        ],
    }
    previous_manifest = tmp_path / "previous-manifest.json"
    previous_manifest.write_text(
        json.dumps({"runtime": {"history": {"archive_state": snapshot}}}),
        encoding="utf-8",
    )
    mock_best = Program(code="x=2", fitness=0.99)

    with patch("libreevolve.cli.evolve", return_value=mock_best) as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--max-generations",
                "0",
                "--restore-archive-cursor-from-manifest",
                str(previous_manifest),
            ],
        )

    assert r.exit_code == 0
    expected_snapshot = {
        **snapshot,
        "islands": [
            {
                "island_id": 0,
                "occupied_cell_count": 1,
                "elite_count": 1,
                "pareto_frontier_count": 0,
                "metric_cell_archive_count": 0,
            },
            {
                "island_id": 1,
                "occupied_cell_count": 1,
                "elite_count": 1,
                "pareto_frontier_count": 0,
                "metric_cell_archive_count": 0,
            },
        ],
        "migration_replay": {
            "schema": "libreevolve.island_migration_replay_policy.v1",
            "status": "not_applied_as_restore_engine",
            "policy": (
                "archive_contents_snapshot_restores_current_placements_without_"
                "replaying_migration_events"
            ),
            "migration_sequence": 1,
            "replay_engine_supported": False,
            "archive_contents_restore_covers_current_placements": True,
            "limitations": [
                "migration_event_order_not_applied_as_restore_engine",
                "migration_skip_events_not_reconstructed",
                "controller_pending_work_not_restored",
            ],
        },
        "topology_policy": {
            "schema": "libreevolve.island_topology_policy.v1",
            "status": "configured_synchronous_ring_topology",
            "policy": (
                "config_n_islands_controls_local_synchronous_ring_migration_default_five"
            ),
            "configured_n_islands": 2,
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
        },
    }
    assert mock.call_args.kwargs["runtime_archive_state_snapshot"] == expected_snapshot
    assert mock.call_args.kwargs["runtime_archive_programs_by_id"] is None


def test_run_can_restore_full_archive_snapshot_from_manifest_history_bundle(tmp_path):
    source_root = tmp_path / "source-runs"
    source = ProgramDatabase(
        Config(
            log_dir=str(source_root),
            problem_name="previous",
            n_islands=2,
            map_elites_bins=1,
        ),
        objective_schema=_objective_schema(),
    )
    first = Program(
        id="p1",
        code="x=1",
        fitness=0.9,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.9},
    )
    second = Program(
        id="p2",
        code="x=2",
        fitness=0.8,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.8},
    )
    source.admit(first)
    source.log(first)
    source.admit(second)
    source.log(second)
    archive_state = source.archive_state_snapshot()
    source.update_manifest_runtime(
        {
            "history": {"archive_state": archive_state},
            "artifacts": loop_module._runtime_artifact_pointers(source_root / "previous"),
        }
    )
    previous_manifest = source_root / "previous" / "manifest.json"

    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "n_islands": 2,
                "map_elites_bins": 1,
            }
        ),
        encoding="utf-8",
    )
    mock_best = Program(code="x=2", fitness=0.99)

    with patch("libreevolve.cli.evolve", return_value=mock_best) as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--max-generations",
                "0",
                "--restore-archive-from-manifest",
                str(previous_manifest),
            ],
        )

    assert r.exit_code == 0
    assert mock.call_args.kwargs["runtime_archive_state_snapshot"] == archive_state
    programs = mock.call_args.kwargs["runtime_archive_programs_by_id"]
    assert sorted(programs) == ["p1", "p2"]
    assert programs["p1"].code == "x=1"
    assert archive_state["archive_contents"]["restore_status"] == (
        "snapshot_persisted_full_archive_restore_supported"
    )


def test_run_can_restore_composed_runtime_bundle_from_manifest(tmp_path):
    _make_problem(tmp_path)
    problem = load_problem(tmp_path)

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

    with patch(
        "libreevolve.core.loop.build_llm",
        return_value=LLMEnsemble([UsageBackend()]),
    ):
        loop_module.evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=str(tmp_path / "source-runs"),
                problem_name="previous",
                seed=456,
            ),
        )

    previous_manifest = tmp_path / "source-runs" / "previous" / "manifest.json"
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "seed": 456,
            }
        ),
        encoding="utf-8",
    )
    mock_best = Program(code="x=2", fitness=0.99)

    with patch("libreevolve.cli.evolve", return_value=mock_best) as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--max-generations",
                "0",
                "--restore-runtime-from-manifest",
                str(previous_manifest),
            ],
        )

    assert r.exit_code == 0
    kwargs = mock.call_args.kwargs
    assert kwargs["runtime_rng_state_snapshot"]["seed"] == 456
    assert kwargs["runtime_llm_scheduler_state_snapshot"]["state"]["total"] == 1
    assert kwargs["runtime_budget_state_snapshot"]["consumed"][
        "generations_completed"
    ] == 1
    assert kwargs["runtime_archive_state_snapshot"]["archive_contents"][
        "restore_status"
    ] == "snapshot_persisted_full_archive_restore_supported"
    assert kwargs["runtime_archive_programs_by_id"]
    assert kwargs["runtime_restore_certification"]["schema"] == (
        "libreevolve.full_resume_restore_certification.v1"
    )
    assert kwargs["runtime_restore_certification"]["status"] == (
        "compatible_surfaces_certified"
    )
    assert kwargs["runtime_restore_certification"]["provider_output_replay_ready"] is False


def test_run_rejects_composed_runtime_restore_with_individual_restore_flags(tmp_path):
    _make_problem(tmp_path)
    manifest = tmp_path / "previous-manifest.json"
    manifest.write_text("{}", encoding="utf-8")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--max-generations",
                "0",
                "--restore-runtime-from-manifest",
                str(manifest),
                "--restore-budget-from-manifest",
                str(manifest),
            ],
        )

    assert r.exit_code == 1
    assert "--restore-runtime-from-manifest cannot be combined" in r.output
    assert "--restore-budget-from-manifest" in r.output
    assert mock.call_count == 0


def test_run_rejects_archive_cursor_and_full_restore_flags_together(tmp_path):
    _make_problem(tmp_path)
    manifest = tmp_path / "previous-manifest.json"
    manifest.write_text("{}", encoding="utf-8")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--max-generations",
                "0",
                "--restore-archive-cursor-from-manifest",
                str(manifest),
                "--restore-archive-from-manifest",
                str(manifest),
            ],
        )

    assert r.exit_code == 1
    assert "Use either --restore-archive-cursor-from-manifest" in r.output
    assert mock.call_count == 0


def test_run_rejects_runtime_rng_snapshot_seed_mismatch_before_evolve(tmp_path):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    (tmp_path / "config.yaml").write_text(
        yaml.dump({"log_dir": log_dir.as_posix(), "seed": 123}),
        encoding="utf-8",
    )
    snapshot = _runtime_rng_state(random.Random(456), 456)
    previous_manifest = tmp_path / "previous-manifest.json"
    previous_manifest.write_text(
        json.dumps({"runtime": {"rng": snapshot}}),
        encoding="utf-8",
    )

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--restore-rng-from-manifest",
                str(previous_manifest),
            ],
        )

    assert r.exit_code == 1
    assert "snapshot seed 456 does not match configured seed 123" in r.output
    assert not mock.called
    assert not (log_dir / tmp_path.name).exists()


def test_run_llm_failure_policy_cli_options_override_config(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "llm_max_retries": 0,
                "llm_max_call_attempts": 10,
                "llm_fallback": True,
                "llm_max_response_chars": 100,
                "llm_call_history_max": 50,
                "llm_call_timeout_sec": 10.0,
            }
        )
    )
    mock_best = Program(code="x=2", fitness=0.99)

    with patch("libreevolve.cli.evolve", return_value=mock_best) as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--llm-max-retries",
                "2",
                "--llm-max-call-attempts",
                "6",
                "--no-llm-fallback",
                "--llm-max-response-chars",
                "64",
                "--llm-call-history-max",
                "8",
                "--llm-call-timeout-sec",
                "0.5",
            ],
        )

    assert r.exit_code == 0
    config = mock.call_args.args[1]
    assert config.llm_max_retries == 2
    assert config.llm_max_call_attempts == 6
    assert config.llm_fallback is False
    assert config.llm_max_response_chars == 64
    assert config.llm_call_history_max == 8
    assert config.llm_call_timeout_sec == 0.5


def test_run_rejects_over_cap_llm_retries_before_evolve(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(f"log_dir: {(tmp_path / 'runs').as_posix()}\n")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--llm-max-retries", "11"])

    assert r.exit_code == 1
    assert "llm_max_retries" in r.output
    assert not mock.called


def test_run_rejects_over_cap_llm_call_attempts_before_evolve(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(f"log_dir: {(tmp_path / 'runs').as_posix()}\n")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            ["run", str(tmp_path), "--llm-max-call-attempts", "33"],
        )

    assert r.exit_code == 1
    assert "llm_max_call_attempts" in r.output
    assert not mock.called


def test_run_writes_complete_best_workspace(tmp_path):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n")
    payload = b"\xff\x00fixture"
    best = Program(
        code='x = "legacy"\n',
        files={
            "main.py": "from pkg.helper import value\n",
            "pkg/helper.py": "value = 2\n",
        },
        primary_file="main.py",
        fitness=0.99,
        static_files=[
            {
                "path": "fixture.bin",
                "kind": "binary",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "source_kind": "unknown",
                "mutation_policy": "immutable",
                "content_b64": base64.b64encode(payload).decode("ascii"),
            }
        ],
    )
    with patch("libreevolve.cli.evolve", return_value=best):
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--max-generations", "1"])

    run_dir = log_dir / tmp_path.name
    assert r.exit_code == 0
    assert (run_dir / "best.py").read_text(encoding="utf-8") == best.code
    assert (run_dir / "best_workspace" / "main.py").read_text(encoding="utf-8") == best.code
    assert 'x = "legacy"' not in (run_dir / "best.py").read_text(encoding="utf-8")
    assert (
        run_dir / "best_workspace" / "pkg" / "helper.py"
    ).read_text(encoding="utf-8") == "value = 2\n"
    static_manifest = json.loads(
        (run_dir / "best_workspace" / ".libreevolve_static_files.json").read_text(
            encoding="utf-8"
        )
    )
    assert (run_dir / "best_workspace" / "fixture.bin").read_bytes() == payload
    assert static_manifest["schema"] == "libreevolve.static_workspace_files.v1"
    assert static_manifest["static_files"] == [
        {
            "path": "fixture.bin",
            "kind": "binary",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            "source_kind": "unknown",
            "mutation_policy": "immutable",
        }
    ]
    assert "Best workspace saved to:" in r.output


def test_run_records_best_artifact_export_success_in_manifest(tmp_path):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n")

    r = CliRunner().invoke(
        cli, ["run", str(tmp_path), "--max-generations", "0"]
    )

    run_dir = log_dir / tmp_path.name
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    export = manifest["runtime"]["best_artifact_export"]
    assert r.exit_code == 0
    assert export["status"] == "completed"
    assert export["paths"]["best.py"]["exists"] is True
    assert len(export["paths"]["best.py"]["sha256"]) == 64
    assert export["paths"]["best_workspace"]["kind"] == "directory"
    assert export["paths"]["best_workspace"]["tree_hash_status"] == "ok"
    assert len(export["paths"]["best_workspace"]["tree_hash"]) == 64
    assert manifest["runtime"]["artifacts"]["best.py"]["exists"] is True
    assert manifest["runtime"]["artifacts"]["best.py"]["sha256"] == export["paths"]["best.py"]["sha256"]
    assert manifest["runtime"]["artifacts"]["best_workspace"]["exists"] is True


def test_candidate_runner_example_runs_and_show_accepts_validator_boundary(tmp_path):
    source = (
        Path(__file__).resolve().parents[1]
        / "libreevolve"
        / "problems"
        / "examples"
        / "candidate_runner_expression"
    )
    problem_dir = tmp_path / "candidate_runner_expression"
    shutil.copytree(source, problem_dir)
    log_dir = tmp_path / "runs"
    with (problem_dir / "config.yaml").open("a", encoding="utf-8") as handle:
        handle.write(f"\nlog_dir: {log_dir.as_posix()}\n")

    run_result = CliRunner().invoke(
        cli,
        [
            "run",
            str(problem_dir),
            "--run-name",
            "candidate_runner_cli",
            "--max-generations",
            "0",
            "--overwrite",
        ],
    )

    run_dir = log_dir / "candidate_runner_cli"
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    report = manifest["runtime"]["history"][
        "candidate_language_runner_contract_report"
    ]
    assert run_result.exit_code == 0, run_result.output
    assert manifest["policies"]["candidate_language"]["language_runner_ready"] is True
    assert report["execution_summary"]["record_count"] == 1
    assert report["execution_summary"]["successful_record_count"] == 1
    assert report["execution_summary"]["generated_build_artifact_count"] == 1
    assert (run_dir / "best_workspace" / "solution.expr").read_text(
        encoding="utf-8"
    ) == "6 * 6\n"

    show_result = CliRunner().invoke(cli, ["show", str(run_dir)])

    assert show_result.exit_code == 0, show_result.output
    assert "Validator boundary" in show_result.output
    assert "checked_attempts=1" in show_result.output


def test_run_records_best_artifact_export_failure_in_manifest(tmp_path):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n")
    secret = "api_key=sk-proj_best_export_secret_1234567890"

    with patch(
        "libreevolve.core.best_artifacts._write_best_artifacts",
        side_effect=OSError(f"export failed {secret}"),
    ):
        r = CliRunner().invoke(
            cli, ["run", str(tmp_path), "--max-generations", "0"]
        )

    run_dir = log_dir / tmp_path.name
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    export = manifest["runtime"]["best_artifact_export"]
    assert r.exit_code == 1
    assert "Best artifact export failed" in r.output
    assert secret not in r.output
    assert manifest["runtime"]["status"] == "completed"
    assert export["status"] == "failed"
    assert export["error_type"] == "OSError"
    assert secret not in json.dumps(export, sort_keys=True)
    assert export["paths"]["best.py"]["exists"] is False
    assert manifest["runtime"]["artifacts"]["best.py"]["exists"] is False


def test_load_best_artifact_export_record_rejects_duplicate_manifest_keys(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "manifest.json").write_text(
        '{"runtime":{"best_artifact_export":{"status":"completed","status":"failed"}}}',
        encoding="utf-8",
    )

    export = _load_best_artifact_export_record(run_dir)

    assert export["status"] == "failed"
    assert "duplicate JSON object name 'status'" in export["error"]


def test_run_records_structured_best_artifact_export_recovery_errors(tmp_path):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n")
    original_secret = "api_key=sk-proj_install_secret_1234567890"  # pragma: allowlist secret
    rollback_secret = "api_key=sk-proj_rollback_secret_1234567890"  # pragma: allowlist secret
    cleanup_secret = "api_key=sk-proj_cleanup_secret_1234567890"  # pragma: allowlist secret
    failure = BestArtifactExportError(
        OSError(original_secret),
        rollback_errors=[
            {
                "stage": "restore_best.py",
                "path": ".best-old.py.bak",
                "exception": OSError(rollback_secret),
            }
        ],
        cleanup_errors=[
            {
                "stage": "cleanup",
                "path": ".best-old.tmp",
                "exception": OSError(cleanup_secret),
            }
        ],
        preserved_paths=(".best-old.py.bak",),
    )
    with patch("libreevolve.core.best_artifacts._write_best_artifacts", side_effect=failure):
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--max-generations", "0"])

    run_dir = log_dir / tmp_path.name
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    export = manifest["runtime"]["best_artifact_export"]
    rendered = json.dumps(export, sort_keys=True)
    assert r.exit_code == 1
    assert "Best artifact export failed" in r.output
    assert original_secret not in r.output
    assert rollback_secret not in r.output
    assert cleanup_secret not in r.output
    assert original_secret not in rendered
    assert rollback_secret not in rendered
    assert cleanup_secret not in rendered
    assert export["error_type"] == "BestArtifactExportError"
    assert export["original_error_type"] == "OSError"
    assert export["rollback_errors"][0]["stage"] == "restore_best.py"
    assert export["cleanup_errors"][0]["stage"] == "cleanup"
    assert export["preserved_backups"] == [".best-old.py.bak"]
    assert manifest["runtime"]["status"] == "completed"


def test_write_best_artifacts_preserves_previous_export_on_materialize_failure(
    tmp_path, monkeypatch
):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "best.py").write_text("old best\n", encoding="utf-8")
    old_workspace = run_dir / "best_workspace"
    old_workspace.mkdir()
    (old_workspace / "old.py").write_text("old workspace\n", encoding="utf-8")
    best = Program(
        files={
            "main.py": "new best\n",
            "helper.py": "new helper\n",
        },
        primary_file="main.py",
        fitness=0.99,
    )

    def fail_materialize(self, root):
        root.mkdir(parents=True, exist_ok=True)
        (root / "main.py").write_text(self.code, encoding="utf-8")
        raise OSError("workspace could not be materialized")

    monkeypatch.setattr(CandidateWorkspace, "materialize", fail_materialize)

    with pytest.raises(OSError, match="workspace could not be materialized"):
        _write_best_artifacts(best, run_dir)

    assert (run_dir / "best.py").read_text(encoding="utf-8") == "old best\n"
    assert (old_workspace / "old.py").read_text(encoding="utf-8") == "old workspace\n"
    assert not (old_workspace / "main.py").exists()
    assert not list(run_dir.glob(".best*"))


def test_write_best_artifacts_preserves_previous_export_on_install_failure(
    tmp_path, monkeypatch
):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "best.py").write_text("old best\n", encoding="utf-8")
    old_workspace = run_dir / "best_workspace"
    old_workspace.mkdir()
    (old_workspace / "old.py").write_text("old workspace\n", encoding="utf-8")
    best = Program(files={"main.py": "new best\n"}, primary_file="main.py", fitness=0.99)
    install_secret = "api_key=sk-proj_install_secret_1234567890"  # pragma: allowlist secret
    path_type = type(run_dir)
    original_replace = path_type.replace

    def fail_workspace_install(self, target):
        if self.name.endswith(".tmp") and Path(target).name == "best_workspace":
            raise OSError(install_secret)
        return original_replace(self, target)

    monkeypatch.setattr(path_type, "replace", fail_workspace_install)

    with pytest.raises(BestArtifactExportError) as excinfo:
        _write_best_artifacts(best, run_dir)

    err = excinfo.value
    assert err.original_error_type == "OSError"
    assert install_secret not in str(err)
    assert not err.rollback_errors
    assert not err.cleanup_errors
    assert (run_dir / "best.py").read_text(encoding="utf-8") == "old best\n"
    assert (old_workspace / "old.py").read_text(encoding="utf-8") == "old workspace\n"
    assert not (old_workspace / "main.py").exists()
    assert not list(run_dir.glob(".best*"))


def test_write_best_artifacts_preserves_backup_and_original_error_when_rollback_fails(
    tmp_path, monkeypatch
):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "best.py").write_text("old best\n", encoding="utf-8")
    old_workspace = run_dir / "best_workspace"
    old_workspace.mkdir()
    (old_workspace / "old.py").write_text("old workspace\n", encoding="utf-8")
    best = Program(files={"main.py": "new best\n"}, primary_file="main.py", fitness=0.99)
    install_secret = "api_key=sk-proj_install_secret_1234567890"  # pragma: allowlist secret
    rollback_secret = "api_key=sk-proj_rollback_secret_1234567890"  # pragma: allowlist secret
    path_type = type(run_dir)
    original_replace = path_type.replace

    def fail_workspace_install_and_py_restore(self, target):
        target_path = Path(target)
        if self.name.endswith(".tmp") and target_path.name == "best_workspace":
            raise OSError(install_secret)
        if self.name.endswith(".py.bak") and target_path.name == "best.py":
            raise OSError(rollback_secret)
        return original_replace(self, target)

    monkeypatch.setattr(path_type, "replace", fail_workspace_install_and_py_restore)

    with pytest.raises(BestArtifactExportError) as excinfo:
        _write_best_artifacts(best, run_dir)

    err = excinfo.value
    manifest_record = err.to_manifest_record()
    rendered = json.dumps(manifest_record, sort_keys=True)
    assert install_secret not in str(err)
    assert rollback_secret not in str(err)
    assert install_secret not in rendered
    assert rollback_secret not in rendered
    assert err.original_error_type == "OSError"
    assert err.rollback_errors[0]["stage"] == "restore_best.py"
    assert err.preserved_paths
    backup_py = next(run_dir.glob(".best-*.py.bak"))
    assert backup_py.read_text(encoding="utf-8") == "old best\n"
    assert not (run_dir / "best.py").exists()
    assert (old_workspace / "old.py").read_text(encoding="utf-8") == "old workspace\n"
    assert not list(run_dir.glob("*.tmp"))


def test_write_best_artifacts_reports_cleanup_failure_after_success(
    tmp_path, monkeypatch
):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    best = Program(files={"main.py": "new best\n"}, primary_file="main.py", fitness=0.99)
    cleanup_secret = "api_key=sk-proj_cleanup_secret_1234567890"  # pragma: allowlist secret
    original_remove = best_artifacts_module._remove_best_artifact_temp

    def fail_tmp_py_cleanup(path):
        if path.name.endswith(".py.tmp"):
            raise OSError(cleanup_secret)
        original_remove(path)

    monkeypatch.setattr(
        best_artifacts_module, "_remove_best_artifact_temp", fail_tmp_py_cleanup
    )

    with pytest.raises(BestArtifactExportError) as excinfo:
        _write_best_artifacts(best, run_dir)

    err = excinfo.value
    rendered = json.dumps(err.to_manifest_record(), sort_keys=True)
    assert cleanup_secret not in str(err)
    assert cleanup_secret not in rendered
    assert err.cleanup_errors[0]["stage"] == "cleanup"
    assert (run_dir / "best.py").read_text(encoding="utf-8") == "new best\n"
    assert (run_dir / "best_workspace" / "main.py").read_text(
        encoding="utf-8"
    ) == "new best\n"


def test_write_best_artifacts_replaces_previous_export_as_a_pair(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "best.py").write_text("old best\n", encoding="utf-8")
    old_workspace = run_dir / "best_workspace"
    old_workspace.mkdir()
    (old_workspace / "old.py").write_text("old workspace\n", encoding="utf-8")
    best = Program(
        files={
            "main.py": "new best\n",
            "pkg/helper.py": "new helper\n",
        },
        primary_file="main.py",
        fitness=0.99,
    )

    best_py, best_workspace = _write_best_artifacts(best, run_dir)

    assert best_py == run_dir / "best.py"
    assert best_workspace == run_dir / "best_workspace"
    assert best_py.read_text(encoding="utf-8") == "new best\n"
    assert (best_workspace / "main.py").read_text(encoding="utf-8") == "new best\n"
    assert (
        best_workspace / "pkg" / "helper.py"
    ).read_text(encoding="utf-8") == "new helper\n"
    assert not (best_workspace / "old.py").exists()
    assert not list(run_dir.glob(".best*"))


def test_write_best_artifacts_exports_static_workspace_manifest(tmp_path):
    run_dir = tmp_path / "run"
    payload = b"\xff\x00fixture"
    best = Program(
        files={"main.py": "new best\n"},
        primary_file="main.py",
        fitness=0.99,
        static_files=[
            {
                "path": "fixture.bin",
                "kind": "binary",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "source_kind": "unknown",
                "mutation_policy": "immutable",
                "content_b64": base64.b64encode(payload).decode("ascii"),
            }
        ],
    )

    _best_py, best_workspace = _write_best_artifacts(best, run_dir)

    static_manifest = json.loads(
        (best_workspace / ".libreevolve_static_files.json").read_text(encoding="utf-8")
    )
    assert (best_workspace / "fixture.bin").read_bytes() == payload
    assert static_manifest["schema"] == "libreevolve.static_workspace_files.v1"
    assert static_manifest["static_files"] == [
        {
            "path": "fixture.bin",
            "kind": "binary",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            "source_kind": "unknown",
            "mutation_policy": "immutable",
        }
    ]


def test_write_best_artifacts_rejects_linked_best_py_before_export(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("outside\n", encoding="utf-8")
    link = run_dir / "best.py"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")
    best = Program(code="new best\n", fitness=0.99)

    with pytest.raises(OSError, match="linked best artifact path"):
        _write_best_artifacts(best, run_dir)

    assert link.is_symlink()
    assert outside.read_text(encoding="utf-8") == "outside\n"
    assert not (run_dir / "best_workspace").exists()


def test_write_best_artifacts_rejects_linked_best_workspace_before_export(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    outside = tmp_path / "outside_workspace"
    outside.mkdir()
    (outside / "old.py").write_text("outside\n", encoding="utf-8")
    link = run_dir / "best_workspace"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlink creation is unavailable: {exc}")
    best = Program(code="new best\n", fitness=0.99)

    with pytest.raises(OSError, match="linked best artifact path"):
        _write_best_artifacts(best, run_dir)

    assert link.is_symlink()
    assert (outside / "old.py").read_text(encoding="utf-8") == "outside\n"
    assert not (run_dir / "best.py").exists()


def test_write_best_artifacts_rejects_junction_best_workspace_before_export(tmp_path):
    if os.name != "nt":
        pytest.skip("Windows junctions are only available on Windows")
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    outside = tmp_path / "outside_workspace"
    outside.mkdir()
    (outside / "old.py").write_text("outside\n", encoding="utf-8")
    junction = run_dir / "best_workspace"
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        pytest.skip(f"junction creation is unavailable: {result.stderr or result.stdout}")
    best = Program(code="new best\n", fitness=0.99)

    with pytest.raises(OSError, match="linked best artifact path"):
        _write_best_artifacts(best, run_dir)

    assert junction.exists()
    assert (outside / "old.py").read_text(encoding="utf-8") == "outside\n"
    assert not (run_dir / "best.py").exists()


def test_run_fails_when_target_run_artifacts_exist(tmp_path):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n")
    run_dir = log_dir / tmp_path.name
    run_dir.mkdir(parents=True)
    (run_dir / "history.jsonl").write_text("{}\n", encoding="utf-8")
    best = Program(code="x=2", fitness=0.99)

    with patch("libreevolve.cli.evolve", return_value=best) as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--max-generations", "1"])

    assert r.exit_code != 0
    assert "already contains run artifacts" in r.output
    assert not mock.called


def test_run_existing_artifact_error_uses_safe_run_path_context(tmp_path):
    _make_problem(tmp_path)
    log_dir = tmp_path / "api_key=sk-proj_rundir_secret_1234567890"  # pragma: allowlist secret
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n")
    run_dir = log_dir / tmp_path.name
    run_dir.mkdir(parents=True)
    (run_dir / "history.jsonl").write_text("{}\n", encoding="utf-8")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--max-generations", "1"])

    assert r.exit_code != 0
    assert "already contains run artifacts" in r.output
    assert "path_hash=" in r.output
    assert "path_redacted=True" in r.output
    assert "sk-proj_rundir_secret" not in r.output
    assert str(log_dir) not in r.output
    assert not mock.called


def test_run_overwrite_clears_target_artifacts(tmp_path):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n")
    run_dir = log_dir / tmp_path.name
    run_dir.mkdir(parents=True)
    (run_dir / "history.jsonl").write_text("{}\n", encoding="utf-8")
    (run_dir / "best_workspace").mkdir()
    (run_dir / "best_workspace" / "old.py").write_text("old", encoding="utf-8")

    r = CliRunner().invoke(
        cli,
        ["run", str(tmp_path), "--max-generations", "0", "--overwrite"],
    )

    assert r.exit_code == 0
    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") != "{}\n"
    assert not (run_dir / "best_workspace" / "old.py").exists()
    assert (run_dir / "best.py").read_text(encoding="utf-8") == "x=1"
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["config"]["run_collision_policy"] == "overwrite"
    assert manifest["runtime"]["best_artifact_export"]["status"] == "completed"


def test_load_plugins_scopes_ttt_rl_to_run_artifacts(tmp_path):
    plugins = _load_plugins(["ttt_rl"], run_dir=tmp_path / "runs" / "demo")

    assert isinstance(plugins[0], TTTRLPlugin)
    assert plugins[0]._log_dir == tmp_path / "runs" / "demo" / "plugin_artifacts" / "ttt_rl"


def test_load_plugins_accepts_configured_plugin_options(tmp_path):
    plugins = _load_plugins(
        [
            {
                "name": "deep_research",
                "options": {"search_every": 2, "max_events": 9, "cache_mode": "offline"},
            }
        ],
        run_dir=tmp_path / "runs" / "demo",
    )

    assert isinstance(plugins[0], DeepResearchPlugin)
    assert plugins[0]._search_every == 2
    assert plugins[0]._max_events == 9
    assert plugins[0]._cache_mode == "offline"
    assert plugins[0]._cache_dir == tmp_path / "runs" / "demo" / "plugin_artifacts" / "deep_research"


def test_load_plugins_accepts_entry_point_plugin_specs(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "libreevolve.plugins.registry.metadata.entry_points",
        lambda: _FakeEntryPoints([_FakeEntryPoint()]),
    )

    plugins = _load_plugins(
        [
            {
                "name": "entry_point",
                "options": {
                    "group": "libreevolve.plugins",
                    "name": "sample",
                    "paper_inspiration": "AlphaEvolveExtension",
                },
            }
        ],
        run_dir=tmp_path / "runs" / "demo",
    )

    assert len(plugins) == 1
    assert isinstance(plugins[0], _EntryPointPlugin)


def test_load_plugins_passes_entry_point_constructor_options(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "libreevolve.plugins.registry.metadata.entry_points",
        lambda: _FakeEntryPoints([_FakeEntryPoint()]),
    )

    plugins = _load_plugins(
        [
            {
                "name": "entry_point",
                "options": {
                    "group": "libreevolve.plugins",
                    "name": "sample",
                    "paper_inspiration": "AlphaEvolveExtension",
                    "constructor_options": {
                        "mode": "audit",
                        "limit": 5,
                    },
                },
            }
        ],
        run_dir=tmp_path / "runs" / "demo",
    )

    assert isinstance(plugins[0], _EntryPointPlugin)
    assert plugins[0].mode == "audit"
    assert plugins[0].limit == 5


def test_load_plugins_validates_entry_point_constructor_schema(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "libreevolve.plugins.registry.metadata.entry_points",
        lambda: _FakeEntryPoints([_FakeSchemaEntryPoint()]),
    )

    plugins = _load_plugins(
        [
            {
                "name": "entry_point",
                "options": {
                    "group": "libreevolve.plugins",
                    "name": "schema_sample",
                    "constructor_options": {
                        "mode": "dry_run",
                        "limit": 3,
                    },
                },
            }
        ],
        run_dir=tmp_path / "runs" / "demo",
    )

    assert isinstance(plugins[0], _SchemaEntryPointPlugin)
    assert plugins[0].mode == "dry_run"
    assert plugins[0].limit == 3


def test_load_plugins_rejects_entry_point_constructor_schema_violation(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "libreevolve.plugins.registry.metadata.entry_points",
        lambda: _FakeEntryPoints([_FakeSchemaEntryPoint()]),
    )

    with pytest.raises(ValueError, match="positive integer"):
        _load_plugins(
            [
                {
                    "name": "entry_point",
                    "options": {
                        "group": "libreevolve.plugins",
                        "name": "schema_sample",
                        "constructor_options": {
                            "mode": "audit",
                            "limit": 0,
                        },
                    },
                }
            ],
            run_dir=tmp_path / "runs" / "demo",
        )


def test_show_prints_best(tmp_path):
    (tmp_path/"history.jsonl").write_text(json.dumps(
        {"id":"a","code":"x=2","fitness":0.9,"generation":1,
         "parent_id":None,"lineage":[],"metadata":{}}))
    r = CliRunner().invoke(cli, ["show", str(tmp_path)])
    assert r.exit_code == 0 and "0.9" in r.output and "x=2" in r.output
    assert "legacy highest-fitness" in r.output
    assert "Run status:     legacy history-only (manifest.json missing)" in r.output


def test_show_accepts_history_workspace_with_reserved_path_allowlist(tmp_path):
    _write_show_history(
        tmp_path,
        [
            {
                **_show_current_row("a", 0.9, 1, "x=2"),
                "files": {"main.py": "x=2", ".config.py": "value = 1\n"},
                "primary_file": "main.py",
                "workspace_path_policy": {
                    "policy": "strict_candidate_paths_with_seed_reserved_allowlist",
                    "reserved_components": ["dot-prefixed", "__pycache__"],
                    "allowed_reserved_paths": [".config.py"],
                },
            }
        ],
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "x=2" in r.output


def test_show_reports_completed_manifest_runtime_status(tmp_path):
    _write_show_history(tmp_path, [_show_current_row("a", 0.9, 1, "x=2")])
    _write_show_manifest(
        tmp_path,
        status="completed",
        stop_reason="max_generations",
        programs_logged=1,
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "Run status:     completed (stop_reason: max_generations)" in r.output
    assert "Selection:      archive-retained valid" in r.output
    assert "Validator boundary: checked_attempts=1; streams=history.jsonl" in r.output


def test_show_reports_quarantine_stream_summary(tmp_path):
    _write_show_history(tmp_path, [_show_current_row("a", 0.9, 1, "x=2")])
    _write_show_manifest(tmp_path)
    manifest_path = tmp_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifact_schema"] = {
        "quarantine_jsonl_records": run_artifact_schema()[
            "quarantine_jsonl_records"
        ],
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "history_invalid.jsonl").write_text(
        json.dumps(
            {
                "error": "ValueError",
                "message": "generation must be an integer",
                "record_type": "dict",
                "record_repr_retention": {
                    "retention_mode": "hash_only",
                    "retention_policy": "hash_only_with_raw_sha256",
                    "sha256": "0" * 64,
                    "chars": 42,
                    "stored_chars": 0,
                    "redacted": None,
                    "truncated": False,
                    "max_chars": 4000,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert (
        "Quarantine streams: checked=1; records=1; "
        "streams=history_invalid.jsonl"
    ) in r.output
    assert (
        "Run artifact bundle: accepted_streams=0; quarantine_streams=1; "
        "quarantine_records=1; non_jsonl_checked=0; paper_paths=0"
    ) in r.output


def test_show_rejects_malformed_quarantine_stream(tmp_path):
    _write_show_history(tmp_path, [_show_current_row("a", 0.9, 1, "x=2")])
    _write_show_manifest(tmp_path)
    manifest_path = tmp_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifact_schema"] = {
        "quarantine_jsonl_records": run_artifact_schema()[
            "quarantine_jsonl_records"
        ],
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "history_invalid.jsonl").write_text(
        json.dumps({"error": "ValueError"}) + "\n",
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Quarantine stream validation failed" in r.output
    assert "history_invalid.jsonl" in r.output
    assert "message must be a non-empty string" in r.output


def test_show_reports_paper_artifact_lifecycle_summary(tmp_path):
    _write_show_history(tmp_path, [_show_current_row("a", 0.9, 1, "x=2")])
    _write_show_paper_artifact_manifest(tmp_path)

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert (
        "Run artifact bundle: accepted_streams=1; quarantine_streams=0; "
        "quarantine_records=0; non_jsonl_checked=7; paper_paths=11"
    ) in r.output
    assert "Non-JSONL artifacts: checked=7" in r.output
    assert "Paper artifacts: checked_paths=11" in r.output
    assert "docs_refs=" in r.output


def test_show_rejects_non_jsonl_artifact_policy_drift(tmp_path):
    _write_show_history(tmp_path, [_show_current_row("a", 0.9, 1, "x=2")])
    manifest = _write_show_paper_artifact_manifest(tmp_path)
    manifest["runtime"]["artifacts"]["task_specification.json"] = {
        "path": "task_specification.json",
        "exists": True,
        "present": True,
        "kind": "file",
        "hash_scope": "file_bytes",
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Non-JSONL artifact policy validation failed" in r.output
    assert "missing_non_jsonl_file_sha256" in r.output


def test_show_rejects_paper_artifact_lifecycle_drift(tmp_path):
    _write_show_history(tmp_path, [_show_current_row("a", 0.9, 1, "x=2")])
    manifest = _write_show_paper_artifact_manifest(tmp_path)
    manifest["runtime"]["history"]["alphaevolve_table1_capability_exhibit_report"][
        "rendered_artifacts"
    ][0]["path"] = "paper_artifacts/table1_capability_comparison/unregistered.md"
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Paper artifact lifecycle validation failed" in r.output
    assert "unknown_paper_artifact_paths" in r.output


def test_show_rejects_manifest_backed_row_without_validator_boundary(tmp_path):
    row = _show_current_row("a", 0.9, 1, "x=2")
    row["evaluation"] = {"is_valid": True, "metadata": {}}
    _write_show_history(tmp_path, [row])
    _write_show_manifest(tmp_path)

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Validator boundary artifact validation failed" in r.output
    assert "history.jsonl line 1" in r.output
    assert "missing_validator_boundary" in r.output


def test_show_rejects_manifest_backed_failure_boundary_mismatch(tmp_path):
    _write_show_history(tmp_path, [_show_current_row("a", 0.9, 1, "x=2")])
    _write_show_manifest(
        tmp_path,
        status="completed",
        stop_reason="max_generations",
        programs_logged=1,
    )
    mutation = "bad mutation"
    (tmp_path / "failure_history.jsonl").write_text(
        json.dumps(
            {
                "program_id": "failed",
                "parent_id": "a",
                "generation": 2,
                "mutation_text": mutation,
                "mutation_sha256": hashlib.sha256(mutation.encode("utf-8")).hexdigest(),
                "evaluation": {
                    "metadata": {
                        "validator_boundary": _validator_boundary_metadata("deny")
                    }
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "failure_history.jsonl line 1" in r.output
    assert "boundary_network_policy_mismatch" in r.output


def test_show_reports_aborted_after_seed_as_best_so_far(tmp_path):
    _write_show_history(tmp_path, [_show_current_row("seed", 0.4, 0, "x=1")])
    _write_show_manifest(
        tmp_path,
        status="aborted",
        stop_reason="aborted",
        programs_logged=1,
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "Run status:     aborted best-so-far (stop_reason: aborted)" in r.output
    assert "Best fitness:   0.400000 (generation 0)" in r.output


def test_show_reports_aborted_after_candidate_as_best_so_far(tmp_path):
    _write_show_history(
        tmp_path,
        [
            _show_current_row("seed", 0.4, 0, "x=1"),
            _show_current_row("child", 0.8, 1, "x=2"),
        ],
    )
    _write_show_manifest(
        tmp_path,
        status="aborted",
        stop_reason="aborted",
        programs_logged=2,
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "Total programs: 2" in r.output
    assert "Run status:     aborted best-so-far (stop_reason: aborted)" in r.output
    assert "Best fitness:   0.800000 (generation 1)" in r.output
    assert "x=2" in r.output


def test_show_reports_partial_status_when_manifest_runtime_missing(tmp_path):
    _write_show_history(tmp_path, [_show_current_row("a", 0.9, 1, "x=2")])
    (tmp_path / "manifest.json").write_text(json.dumps({"config": {}}), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "Run status:     partial best-so-far (manifest runtime missing)" in r.output


def test_show_rejects_manifest_history_count_mismatch(tmp_path):
    _write_show_history(tmp_path, [_show_current_row("a", 0.9, 1, "x=2")])
    _write_show_manifest(
        tmp_path,
        status="completed",
        stop_reason="max_generations",
        programs_logged=2,
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Inconsistent manifest.json/runtime history" in r.output
    assert "programs_logged=2 but history.jsonl has 1 row(s)" in r.output


def test_show_does_not_render_runtime_pyproject_diagnostics(tmp_path):
    secret = "sk-proj_pyprojectread_secret_1234567890"  # pragma: allowlist secret
    (tmp_path / "history.jsonl").write_text(
        json.dumps(
            {
                "id": "a",
                "code": "x=2",
                "fitness": 0.9,
                "generation": 1,
                "parent_id": None,
                "lineage": [],
                "metadata": {},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "provenance": {
                    "runtime": {
                        "package": {
                            "pyproject": {
                                "status": "unreadable",
                                "error": f"api_key={secret}",
                            }
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert secret not in r.output
    assert "pyproject" not in r.output


def test_show_uses_workspace_primary_code_from_logged_program(tmp_path):
    db = ProgramDatabase(
        Config(log_dir=tmp_path, problem_name="demo"),
        objective_schema=_objective_schema(),
    )
    db.log(
        Program(
            code='x = "legacy"\n',
            files={"main.py": 'x = "workspace"\n'},
            primary_file="main.py",
            fitness=0.9,
            evaluation={
                "is_valid": True,
                "metadata": {"validator_boundary": _validator_boundary_metadata("host")},
            },
        )
    )
    _write_show_manifest(tmp_path / "demo")

    r = CliRunner().invoke(cli, ["show", str(tmp_path / "demo")])

    assert r.exit_code == 0
    assert 'x = "workspace"' in r.output
    assert 'x = "legacy"' not in r.output


def test_show_prints_full_workspace_files_from_logged_program(tmp_path):
    db = ProgramDatabase(
        Config(log_dir=tmp_path, problem_name="demo"),
        objective_schema=_objective_schema(),
    )
    db.log(
        Program(
            files={
                "main.py": "from helper import value\n",
                "helper.py": "value = 42\n",
            },
            primary_file="main.py",
            fitness=0.9,
            evaluation={
                "is_valid": True,
                "metadata": {"validator_boundary": _validator_boundary_metadata("host")},
            },
        )
    )
    _write_show_manifest(tmp_path / "demo")

    r = CliRunner().invoke(cli, ["show", str(tmp_path / "demo")])

    assert r.exit_code == 0
    assert "--- Best workspace ---" in r.output
    assert "Primary file:   main.py" in r.output
    assert "Files:          main.py, helper.py" in r.output
    assert "--- main.py (primary) ---" in r.output
    assert "--- helper.py ---" in r.output
    assert "from helper import value" in r.output
    assert "value = 42" in r.output


def test_show_handles_canonical_empty_program_records(tmp_path):
    db = ProgramDatabase(
        Config(log_dir=tmp_path, problem_name="demo"),
        objective_schema=_objective_schema(),
    )
    db.log(
        Program(
            fitness=0.1,
            evaluation={
                "is_valid": True,
                "metadata": {"validator_boundary": _validator_boundary_metadata("host")},
            },
        )
    )
    _write_show_manifest(tmp_path / "demo")

    r = CliRunner().invoke(cli, ["show", str(tmp_path / "demo")])

    assert r.exit_code == 0
    assert "Best fitness:   0.100000" in r.output


def test_show_reports_malformed_history_line(tmp_path):
    (tmp_path / "history.jsonl").write_text(
        json.dumps({"id": "a", "code": "x=1", "fitness": 0.1, "generation": 0})
        + "\nnot-json\n",
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output


def test_show_reports_non_object_history_line(tmp_path):
    (tmp_path / "history.jsonl").write_text("[]\n", encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "expected JSON object" in r.output


@pytest.mark.parametrize(
    ("history_text", "duplicate_name"),
    [
        (
            '{"id": "a", "id": "b", "code": "x=1", "fitness": 0.1, "generation": 0}\n',
            "id",
        ),
        (
            '{"id": "a", "code": "x=1", "fitness": 0.1, "generation": 0, '
            '"metrics": {"score": 0.1, "score": 0.9}}\n',
            "score",
        ),
        (
            '{"id": "a", "code": "x=1", "fitness": 0.1, "generation": 0, '
            '"metadata": {"archive_admission": {"selection_score": 0.1, '
            '"selection_score": 0.9}}, "evaluation": {"is_valid": true}}\n',
            "selection_score",
        ),
    ],
)
def test_show_rejects_duplicate_json_object_names(tmp_path, history_text, duplicate_name):
    (tmp_path / "history.jsonl").write_text(history_text, encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert f"duplicate JSON object name '{duplicate_name}'" in r.output
    assert "Total programs:" not in r.output


def test_show_reports_non_finite_history_fitness(tmp_path):
    (tmp_path / "history.jsonl").write_text(
        '{"id": "a", "code": "x=1", "fitness": NaN, "generation": 0}\n',
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert "fitness must be a finite number" in r.output


@pytest.mark.parametrize(
    ("row", "message"),
    [
        (
            {"code": "x=1", "fitness": 1.0, "generation": 0},
            "Program id must be a manifest-safe identifier",
        ),
        (
            {"id": "a", "code": "x=1", "fitness": 1.0, "generation": "bad"},
            "generation must be a non-negative integer",
        ),
        (
            {"id": "a", "fitness": 1.0, "generation": 0},
            "code must be a string",
        ),
        (
            {"id": "a", "code": ["not", "text"], "fitness": 1.0, "generation": 0},
            "code must be a string",
        ),
        (
            {"id": "a", "code": "x=1", "fitness": 1.0, "generation": 0, "metrics": []},
            "metrics must be an object",
        ),
        (
            {
                "id": "a",
                "fitness": 1.0,
                "generation": 0,
                "files": {"main.py": "x=1"},
                "primary_file": "other.py",
            },
            "primary_file missing from files",
        ),
        (
            {
                "id": "a",
                "fitness": 1.0,
                "generation": 0,
                "files": {"main.py": ["not", "text"]},
            },
            "files must map strings to strings",
        ),
        (
            {
                "id": "a",
                "code": "x=1",
                "fitness": 1.0,
                "generation": 0,
                "metadata": {"archive_admission": {"admitted": True, "selection_score": "bad"}},
                "evaluation": {"is_valid": True},
            },
            "archive_admission.selection_score must be a finite number",
        ),
        (
            {
                "id": "a",
                "code": "x=1",
                "fitness": 1.0,
                "generation": 0,
                "metadata": {
                    "archive_admission": {
                        "admitted": True,
                        "selection_score": 1.0,
                        "cell": [0, "bad"],
                    }
                },
                "evaluation": {"is_valid": True},
            },
            "archive_admission.cell must be a list of three non-negative integers",
        ),
        (
            {
                "id": "a",
                "code": "x=1",
                "fitness": 1.0,
                "generation": 0,
                "metadata": {
                    "archive_admission": {
                        "admitted": True,
                        "selection_score": 1.0,
                        "descriptors": {"performance": "bad"},
                    }
                },
                "evaluation": {"is_valid": True},
            },
            "archive_admission.descriptors must map strings to finite numbers",
        ),
        (
            {
                "id": "a",
                "code": "x=1",
                "fitness": 1.0,
                "generation": 0,
                "metadata": {
                    "archive_admission": {
                        "admitted": True,
                        "selection_score": 1.0,
                        "cell_admitted": "yes",
                    }
                },
                "evaluation": {"is_valid": True},
            },
            "archive_admission.cell_admitted must be a boolean",
        ),
    ],
)
def test_show_reports_malformed_selected_display_fields(tmp_path, row, message):
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert message in r.output


def test_show_rejects_secret_like_generation_before_printing(tmp_path):
    secret_generation = "api_key=sk-proj_secret_show_1234567890"
    (tmp_path / "history.jsonl").write_text(
        json.dumps(
            {
                "id": "a",
                "fitness": 1.0,
                "generation": secret_generation,
                "metadata": {"archive_admission": {"admitted": True}},
                "evaluation": {"is_valid": True},
            }
        ),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "generation must be a non-negative integer" in r.output
    assert secret_generation not in r.output


def test_show_reports_empty_history(tmp_path):
    (tmp_path / "history.jsonl").write_text("\n", encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "history.jsonl is empty" in r.output


def test_show_uses_archive_admitted_valid_best_for_modern_history(tmp_path):
    rows = [
        {
            "id": "seed",
            "code": "x=1",
            "fitness": 0.5,
            "generation": 0,
            "metadata": {"archive_admission": {"admitted": True}},
            "metrics": {"score": 0.5, "is_valid": True},
            "evaluation": {"is_valid": True},
        },
        {
            "id": "invalid",
            "code": "x=999",
            "fitness": 2.0,
            "generation": 1,
            "metadata": {"archive_admission": {"admitted": False}},
            "metrics": {"score": 2.0, "is_valid": False},
            "evaluation": {"is_valid": False},
        },
        {
            "id": "below",
            "code": "x=500",
            "fitness": 1.5,
            "generation": 2,
            "metadata": {"archive_admission": {"admitted": False}},
            "metrics": {"score": 1.5, "is_valid": True},
            "evaluation": {"is_valid": True},
        },
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "archive-retained valid" in r.output
    assert "0.500000" in r.output
    assert "x=1" in r.output
    assert "x=999" not in r.output
    assert "x=500" not in r.output


def test_show_accepts_matching_archive_admission_program_id(tmp_path):
    row = {
        "id": "row-program",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {
            "archive_admission": {
                "program_id": "row-program",
                "admitted": True,
                "selection_score": 1.0,
            }
        },
        "evaluation": {
            "is_valid": True,
            "metadata": {"validator_boundary": _validator_boundary_metadata("host")},
        },
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "archive-retained valid" in r.output
    assert "x=1" in r.output


def test_show_allows_current_history_without_archive_admission_program_id(tmp_path):
    row = {
        "id": "compat-row",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {"archive_admission": {"admitted": True, "selection_score": 1.0}},
        "evaluation": {
            "is_valid": True,
            "metadata": {"validator_boundary": _validator_boundary_metadata("host")},
        },
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "archive-retained valid" in r.output


def test_show_rejects_selected_archive_admission_program_id_mismatch(tmp_path):
    row = {
        "id": "row-program",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {
            "archive_admission": {
                "program_id": "different-program",
                "admitted": True,
                "selection_score": 1.0,
            }
        },
        "evaluation": {"is_valid": True},
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert "archive_admission.program_id must match history row id" in r.output
    assert "archive-retained valid" not in r.output


def test_show_rejects_unselected_archive_admission_program_id_mismatch(tmp_path):
    rows = [
        {
            "id": "selected",
            "code": "x=1",
            "fitness": 1.0,
            "generation": 0,
            "metadata": {
                "archive_admission": {
                    "program_id": "selected",
                    "admitted": True,
                    "selection_score": 1.0,
                }
            },
            "evaluation": {"is_valid": True},
        },
        {
            "id": "unselected",
            "code": "x=2",
            "fitness": 0.5,
            "generation": 1,
            "metadata": {
                "archive_admission": {
                    "program_id": "other",
                    "admitted": False,
                    "selection_score": 0.5,
                }
            },
            "evaluation": {"is_valid": True},
        },
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output
    assert "archive_admission.program_id must match history row id" in r.output
    assert "archive-retained valid" not in r.output


def test_show_rejects_unsafe_archive_admission_program_id_before_printing(tmp_path):
    secret_program_id = "api_key=sk-proj_archive_program_secret_1234567890"
    row = {
        "id": "row-program",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {
            "archive_admission": {
                "program_id": secret_program_id,
                "admitted": True,
                "selection_score": 1.0,
            }
        },
        "evaluation": {"is_valid": True},
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "archive_admission.program_id must be a manifest-safe identifier" in r.output
    assert secret_program_id not in r.output


def test_show_requires_explicit_boolean_validity_for_modern_history(tmp_path):
    rows = [
        {
            "id": "missing-evaluation",
            "code": "x=999",
            "fitness": 2.0,
            "generation": 1,
            "metadata": {"archive_admission": {"admitted": True, "selection_score": 1.0}},
        },
        {
            "id": "missing-validity",
            "code": "x=500",
            "fitness": 1.5,
            "generation": 2,
            "metadata": {"archive_admission": {"admitted": True, "selection_score": 0.9}},
            "evaluation": {},
        },
        {
            "id": "valid",
            "code": "x=1",
            "fitness": 0.5,
            "generation": 0,
            "metadata": {"archive_admission": {"admitted": True, "selection_score": 0.1}},
            "evaluation": {"is_valid": True},
        },
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "x=1" in r.output
    assert "x=999" not in r.output
    assert "x=500" not in r.output


@pytest.mark.parametrize("evaluation", [["not", "object"], {"is_valid": "false"}])
def test_show_rejects_malformed_current_history_evaluation_payloads(tmp_path, evaluation):
    row = {
        "id": "malformed-evaluation",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {
            "archive_admission": {
                "admitted": True,
                "selection_score": 1.0,
            }
        },
        "evaluation": evaluation,
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert (
        "evaluation must be an object" in r.output
        or "evaluation.is_valid must be a boolean" in r.output
    )
    assert "No archive-retained valid programs" not in r.output


def test_show_allows_current_history_missing_validity_as_non_retained(tmp_path):
    rows = [
        {
            "id": "missing-evaluation",
            "code": "x=1",
            "fitness": 1.0,
            "generation": 0,
            "metadata": {"archive_admission": {"admitted": True}},
        },
        {
            "id": "missing-is-valid",
            "code": "x=2",
            "fitness": 0.5,
            "generation": 1,
            "metadata": {"archive_admission": {"admitted": True}},
            "evaluation": {},
        },
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "No archive-retained valid programs" in r.output
    assert "Malformed history.jsonl" not in r.output


@pytest.mark.parametrize(
    "cell",
    [
        [0, "bad", 1],
        [-1, 0, 1],
        [0, 1],
        [0, 1, 2, 3],
    ],
)
def test_show_rejects_malformed_archive_cell_coordinates(tmp_path, cell):
    row = {
        "id": "bad-cell",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {
            "archive_admission": {
                "admitted": True,
                "selection_score": 1.0,
                "cell_admitted": True,
                "search_state_changed": True,
                "sampling_eligible": True,
                "cell": cell,
            }
        },
        "evaluation": {"is_valid": True},
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert "archive_admission.cell must be a list of three non-negative integers" in r.output


def test_show_rejects_archive_cell_coordinates_outside_manifest_bins(tmp_path):
    row = {
        "id": "bad-cell-bound",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {
            "archive_admission": {
                "admitted": True,
                "selection_score": 1.0,
                "cell_admitted": True,
                "search_state_changed": True,
                "sampling_eligible": True,
                "cell": [0, 2, 1],
            }
        },
        "evaluation": {"is_valid": True},
    }
    _write_show_history(tmp_path, [row])
    _write_show_manifest(
        tmp_path,
        programs_logged=1,
        config={"map_elites_bins": 2},
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert (
        "archive_admission.cell values must be less than "
        "manifest config.map_elites_bins (2)"
    ) in r.output
    assert "Best fitness:" not in r.output


def test_show_allows_archive_cell_coordinates_when_manifest_bins_absent(tmp_path):
    row = {
        "id": "legacy-cell-bound",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {
            "archive_admission": {
                "admitted": True,
                "selection_score": 1.0,
                "cell_admitted": True,
                "search_state_changed": True,
                "sampling_eligible": True,
                "cell": [0, 999, 1],
            }
        },
        "evaluation": {
            "is_valid": True,
            "metadata": {"validator_boundary": _validator_boundary_metadata("host")},
        },
    }
    _write_show_history(tmp_path, [row])
    _write_show_manifest(tmp_path, programs_logged=1)

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "cell=[0, 999, 1]" in r.output


@pytest.mark.parametrize("map_elites_bins", [0, -1, True, "10"])
def test_show_rejects_malformed_manifest_map_elites_bins(tmp_path, map_elites_bins):
    row = {
        "id": "bad-manifest-bin",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {"archive_admission": {"admitted": True}},
        "evaluation": {"is_valid": True},
    }
    _write_show_history(tmp_path, [row])
    _write_show_manifest(
        tmp_path,
        programs_logged=1,
        config={"map_elites_bins": map_elites_bins},
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed manifest.json" in r.output
    assert "config.map_elites_bins must be a positive integer" in r.output


@pytest.mark.parametrize(
    "descriptor_name",
    [
        "bad name",
        "api_key=sk-proj_archivedesc_secret_1234567890",  # pragma: allowlist secret
        "score\u202e",
        "is_valid",
    ],
)
def test_show_rejects_unsafe_archive_descriptor_labels_before_printing(
    tmp_path, descriptor_name
):
    row = {
        "id": "bad-descriptor",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {
            "archive_admission": {
                "admitted": True,
                "selection_score": 1.0,
                "cell_admitted": True,
                "search_state_changed": True,
                "sampling_eligible": True,
                "descriptors": {descriptor_name: 1.0},
            }
        },
        "evaluation": {"is_valid": True},
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert "archive_admission.descriptor names must be manifest-safe metric names" in r.output
    assert "Best fitness:" not in r.output
    assert "sk-proj_archivedesc_secret" not in r.output


def test_show_rejects_unsafe_unselected_archive_descriptor_labels(tmp_path):
    secret_descriptor = "api_key=sk-proj_archivedesc_secret_1234567890"  # pragma: allowlist secret
    rows = [
        {
            "id": "best",
            "code": "x=1",
            "fitness": 1.0,
            "generation": 0,
            "metadata": {
                "archive_admission": {
                    "admitted": True,
                    "selection_score": 1.0,
                    "cell_admitted": True,
                    "search_state_changed": True,
                    "sampling_eligible": True,
                    "descriptors": {"performance": 1.0},
                }
            },
            "evaluation": {"is_valid": True},
        },
        {
            "id": "bad-lower",
            "code": "x=2",
            "fitness": 0.5,
            "generation": 1,
            "metadata": {
                "archive_admission": {
                    "admitted": True,
                    "selection_score": 0.1,
                    "cell_admitted": True,
                    "search_state_changed": True,
                    "sampling_eligible": True,
                    "descriptors": {secret_descriptor: 0.2},
                }
            },
            "evaluation": {"is_valid": True},
        },
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output
    assert "archive_admission.descriptor names must be manifest-safe metric names" in r.output
    assert "Best fitness:" not in r.output
    assert "sk-proj_archivedesc_secret" not in r.output


def test_show_summarizes_large_archive_descriptor_maps(tmp_path):
    descriptors = {f"metric_{i:03d}": i / 1000 for i in range(500)}
    row = {
        "id": "many-descriptors",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {
            "archive_admission": {
                "admitted": True,
                "selection_score": 1.0,
                "cell_admitted": True,
                "search_state_changed": True,
                "sampling_eligible": True,
                "descriptors": descriptors,
            }
        },
        "evaluation": {"is_valid": True},
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "descriptors_count=500" in r.output
    assert "descriptors_omitted=492" in r.output
    assert "descriptors_sha256=" in r.output
    assert "descriptors_preview=" in r.output
    assert '"metric_000": 0.0' in r.output
    assert '"metric_499"' not in r.output
    assert len(r.output) < 2500


def test_show_summarizes_long_archive_descriptor_labels(tmp_path):
    long_label = "descriptor_" + ("a" * 120)
    row = {
        "id": "long-descriptor",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {
            "archive_admission": {
                "admitted": True,
                "selection_score": 1.0,
                "cell_admitted": True,
                "search_state_changed": True,
                "sampling_eligible": True,
                "descriptors": {long_label: 0.2},
            }
        },
        "evaluation": {"is_valid": True},
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "descriptors_count=1" in r.output
    assert "descriptors_omitted=0" in r.output
    assert "descriptors_sha256=" in r.output
    assert "descriptor_" in r.output
    assert "..." in r.output
    assert long_label not in r.output


def test_show_rejects_malformed_unselected_current_archive_diagnostics(tmp_path):
    rows = [
        {
            "id": "best",
            "code": "x=1",
            "fitness": 1.0,
            "generation": 0,
            "metadata": {
                "archive_admission": {
                    "admitted": True,
                    "selection_score": 1.0,
                    "cell_admitted": True,
                    "search_state_changed": True,
                    "sampling_eligible": True,
                    "cell": [0, 0, 0],
                }
            },
            "evaluation": {"is_valid": True},
        },
        {
            "id": "bad-lower",
            "code": "x=2",
            "fitness": 0.5,
            "generation": 1,
            "metadata": {
                "archive_admission": {
                    "admitted": True,
                    "selection_score": 0.1,
                    "cell_admitted": True,
                    "search_state_changed": True,
                    "sampling_eligible": True,
                    "cell": [0, "bad", 0],
                }
            },
            "evaluation": {"is_valid": True},
        },
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output
    assert "archive_admission.cell must be a list of three non-negative integers" in r.output
    assert "Best fitness:" not in r.output


def test_show_uses_archive_selection_score_and_prints_cell_diagnostics(tmp_path):
    rows = [
        {
            "id": "primary",
            "code": "x=1",
            "fitness": 0.95,
            "generation": 1,
            "metadata": {
                "archive_admission": {
                    "admitted": True,
                    "selection_score": 0.2,
                    "cell_admitted": True,
                    "elite_retained": True,
                    "search_state_changed": True,
                    "sampling_eligible": True,
                    "island_id": 0,
                    "cell": [2, 0, 0],
                    "descriptors": {"performance": 0.2},
                }
            },
            "evaluation": {"is_valid": True},
        },
        {
            "id": "balanced",
            "code": "x=2",
            "fitness": 0.8,
            "generation": 2,
            "metadata": {
                "archive_admission": {
                    "admitted": True,
                    "selection_score": 0.9,
                    "cell_admitted": True,
                    "elite_retained": True,
                    "search_state_changed": True,
                    "sampling_eligible": True,
                    "island_id": 1,
                    "cell": [9, 3, 4],
                    "descriptors": {
                        "performance": 0.9,
                        "diversity": 0.4,
                        "behavior.custom_metric": 0.6,
                    },
                }
            },
            "evaluation": {"is_valid": True},
        },
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "x=2" in r.output
    assert "x=1" not in r.output
    assert "selection_score=0.900000" in r.output
    assert "cell_admitted=True" in r.output
    assert "elite_retained=True" in r.output
    assert "search_state_changed=True" in r.output
    assert "sampling_eligible=True" in r.output
    assert "island=1" in r.output
    assert "cell=[9, 3, 4]" in r.output
    assert '"behavior.custom_metric": 0.6' in r.output
    assert '"diversity": 0.4' in r.output


def test_show_prints_archive_objective_vector(tmp_path):
    row = {
        "id": "balanced",
        "code": "x=2",
        "fitness": 0.8,
        "generation": 2,
        "metadata": {
            "archive_admission": {
                "admitted": True,
                "selection_score": 0.9,
                "objective_vector": {
                    "policy": "normalized_declared_metric_vector_v1",
                    "normalized_metrics": {"accuracy": 0.8, "latency": 0.7},
                    "selection_policy": {
                        "type": "mean_normalized_declared_metrics",
                        "metrics": ["accuracy", "latency"],
                    },
                },
            }
        },
        "evaluation": {"is_valid": True},
    }
    _write_show_history(tmp_path, [row])

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert 'objective_metrics={"accuracy": 0.8, "latency": 0.7}' in r.output
    assert "objective_policy=mean_normalized_declared_metrics" in r.output


def test_show_summarizes_large_archive_objective_vectors(tmp_path):
    metrics = {f"metric_{index}": index / 20 for index in range(12)}
    row = {
        "id": "balanced",
        "code": "x=2",
        "fitness": 0.8,
        "generation": 2,
        "metadata": {
            "archive_admission": {
                "admitted": True,
                "selection_score": 0.9,
                "objective_vector": {
                    "policy": "normalized_declared_metric_vector_v1",
                    "normalized_metrics": metrics,
                },
            }
        },
        "evaluation": {"is_valid": True},
    }
    _write_show_history(tmp_path, [row])

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "objective_metrics_count=12" in r.output
    assert "objective_metrics_preview=" in r.output
    assert "objective_metrics_omitted=4" in r.output
    assert "objective_metrics_sha256=" in r.output


def test_show_rejects_malformed_unselected_archive_objective_vector(tmp_path):
    rows = [
        {
            "id": "selected",
            "code": "x=2",
            "fitness": 0.8,
            "generation": 2,
            "metadata": {
                "archive_admission": {
                    "admitted": True,
                    "selection_score": 0.9,
                }
            },
            "evaluation": {"is_valid": True},
        },
        {
            "id": "malformed",
            "code": "x=1",
            "fitness": 0.1,
            "generation": 1,
            "metadata": {
                "archive_admission": {
                    "admitted": False,
                    "selection_score": 0.1,
                    "objective_vector": {
                        "policy": "normalized_declared_metric_vector_v1",
                        "normalized_metrics": {"accuracy": 1.5},
                    },
                }
            },
            "evaluation": {"is_valid": True},
        },
    ]
    _write_show_history(tmp_path, rows)

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output
    assert "archive_admission.objective_vector metric values" in r.output
    assert "Best fitness:" not in r.output


def test_show_prints_selected_diagnostics_and_failure_statistics(tmp_path):
    db = ProgramDatabase(
        Config(log_dir=tmp_path, problem_name="diagnostics"),
        objective_schema=_objective_schema(),
    )
    run_dir = tmp_path / "diagnostics"
    parent = Program(
        id="parent",
        code="x=1",
        fitness=0.4,
        generation=0,
        metrics={"score": 0.4, "is_valid": True},
        evaluation={"is_valid": True},
    )
    failed = Program(
        id="failed-child",
        code="x=bad",
        fitness=0.0,
        generation=1,
        parent_id="parent",
        lineage=["parent"],
        metrics={"score": 0.0, "is_valid": False},
        evaluation={
            "fitness": 0.0,
            "metrics": {"score": 0.0},
            "is_valid": False,
            "error": "stage_threshold_not_met",
            "stages": [
                {
                    "name": "hard",
                    "passed": False,
                    "score": 0.1,
                    "error": "stage_threshold_not_met",
                    }
                ],
                "metadata": {
                    "validator_boundary": _validator_boundary_metadata("host")
                },
            },
        )
    db.log_failure(
        failed,
        parent,
        "<<<SEARCH\nx=1\n===\nx=bad\n>>>REPLACE",
        "stage_threshold_not_met",
        admission={"admitted": False, "reason": "invalid_evaluation"},
    )
    _write_show_history(
        run_dir,
        [
            {
                "id": "selected",
                "code": "x=2",
                "fitness": 0.9,
                "generation": 2,
                "parent_id": "parent",
                "lineage": ["root", "parent"],
                "metadata": {
                    "archive_admission": {
                        "admitted": True,
                        "selection_score": 0.9,
                    },
                    "prompt_program_id": "prompt-1",
                    "parent_selection": {
                        "strategy": "metric",
                        "selected_program_id": "parent",
                        "target_metric": "score",
                    },
                },
                "metrics": {"score": 0.9, "is_valid": True},
                "evaluation": {
                    "is_valid": True,
                    "stages": [
                        {"name": "syntax", "passed": True, "score": None},
                        {"name": "validate", "passed": True, "score": 1.0},
                        {
                            "name": "hard",
                            "passed": False,
                            "score": 0.4,
                            "error": "stage_threshold_not_met",
                        },
                    ],
                    "accounting": {
                        "configured_stage_samples": 1,
                        "subprocess_attempts": 3,
                        "retry_attempts": 1,
                        "timeout_count": 0,
                        "sample_budget_exhaustions": 0,
                        "stage_budget_exhaustions": 0,
                    },
                    "metadata": {
                        "validator_boundary": _validator_boundary_metadata("host"),
                        "llm_feedback": [
                            {
                                "name": "simplicity",
                                "score": 0.5,
                                "weighted_delta": 0.1,
                            },
                            {
                                "name": "style",
                                "error": "llm_feedback_failed",
                            },
                        ]
                    },
                },
            }
        ],
    )
    _write_show_manifest(run_dir, programs_logged=1)

    r = CliRunner().invoke(cli, ["show", str(run_dir)])

    assert r.exit_code == 0
    assert "Lineage:       parent=parent; lineage_depth=2; lineage_tail=root->parent" in r.output
    assert "Prompt:        prompt_program_id=prompt-1; parent_strategy=metric" in r.output
    assert "selected_parent=parent" in r.output
    assert "target_metric=score" in r.output
    assert "Evaluation:    is_valid=True; stages=3; failed=1" in r.output
    assert "failed_stages=hard:stage_threshold_not_met" in r.output
    assert "subprocess_attempts=3" in r.output
    assert "retry_attempts=1" in r.output
    assert "Feedback:      llm_feedback=2; applied=simplicity; failed=style:llm_feedback_failed" in r.output
    assert "weighted_delta=0.100000" in r.output
    assert "Failures:      total=1" in r.output
    assert "admission_reasons=invalid_evaluation:1" in r.output
    assert "errors=stage_threshold_not_met:1" in r.output
    assert "<<<SEARCH" not in r.output


def test_show_reports_elite_only_retention_distinct_from_cell_admission(tmp_path):
    row = {
        "id": "elite-only",
        "code": "x=2",
        "fitness": 0.8,
        "generation": 2,
        "metadata": {
            "archive_admission": {
                "admitted": True,
                "selection_score": 0.8,
                "reason": "elite_only",
                "cell_admitted": False,
                "elite_retained": True,
                "search_state_changed": True,
                "sampling_eligible": False,
                "island_id": 0,
                "cell": [0, 0, 0],
                "descriptors": {"performance": 0.8},
            }
        },
        "evaluation": {"is_valid": True},
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "archive-retained valid" in r.output
    assert "cell_admitted=False" in r.output
    assert "elite_retained=True" in r.output
    assert "search_state_changed=True" in r.output
    assert "sampling_eligible=False" in r.output


@pytest.mark.parametrize("archive_admission", ["bad", [], None])
def test_show_rejects_malformed_archive_admission_payloads(tmp_path, archive_admission):
    row = {
        "id": "row",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {"archive_admission": archive_admission},
        "evaluation": {"is_valid": True},
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert "archive_admission must be an object" in r.output
    assert "No archive-retained valid programs" not in r.output


def test_show_rejects_contradictory_admitted_archive_flags(tmp_path):
    row = {
        "id": "contradictory",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {
            "archive_admission": {
                "admitted": True,
                "selection_score": 1.0,
                "cell_admitted": False,
                "elite_retained": False,
                "search_state_changed": False,
                "sampling_eligible": False,
            }
        },
        "evaluation": {"is_valid": True},
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert "admitted is true but no retention/search-state flag is true" in r.output
    assert "archive-retained valid" not in r.output


def test_show_allows_non_admitted_current_rows_with_false_archive_flags(tmp_path):
    row = {
        "id": "not-admitted",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {
            "archive_admission": {
                "admitted": False,
                "cell_admitted": False,
                "elite_retained": False,
                "search_state_changed": False,
                "sampling_eligible": False,
            }
        },
        "evaluation": {"is_valid": True},
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "No archive-retained valid programs" in r.output
    assert "Malformed history.jsonl" not in r.output


def test_show_streams_large_legacy_history(tmp_path):
    rows = []
    for index in range(1000):
        rows.append(
            json.dumps(
                {
                    "id": str(index),
                    "code": f"x={index}",
                    "fitness": index / 1000,
                    "generation": index,
                    "metadata": {},
                }
            )
        )
    (tmp_path / "history.jsonl").write_text("\n".join(rows), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "Total programs: 1000" in r.output
    assert "x=999" in r.output


def test_show_reports_invalid_history_utf8_on_first_line(tmp_path):
    (tmp_path / "history.jsonl").write_bytes(b"\xff\n")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert "invalid UTF-8" in r.output
    assert not isinstance(r.exception, UnicodeDecodeError)


def test_show_reports_invalid_history_utf8_after_valid_rows(tmp_path):
    row = {
        "id": "ok",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metadata": {},
    }
    payload = json.dumps(row).encode("utf-8") + b"\n" + b'{"id": "\xff"}\n'
    (tmp_path / "history.jsonl").write_bytes(payload)

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output
    assert "invalid UTF-8" in r.output
    assert not isinstance(r.exception, UnicodeDecodeError)


def test_show_rejects_duplicate_legacy_history_ids(tmp_path):
    rows = [
        {"id": "same", "code": "x=1", "fitness": 0.1, "generation": 0},
        {"id": "same", "code": "x=2", "fitness": 0.9, "generation": 1},
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output
    assert "duplicate program id 'same'" in r.output
    assert "first seen at line 1" in r.output
    assert "Total programs:" not in r.output


def test_show_rejects_duplicate_current_history_ids_before_selection(tmp_path):
    rows = [
        {
            "id": "same",
            "code": "x=1",
            "fitness": 0.1,
            "generation": 0,
            "metadata": {
                "archive_admission": {
                    "admitted": True,
                    "selection_score": 0.1,
                }
            },
            "evaluation": {"is_valid": True},
        },
        {
            "id": "same",
            "code": "x=2",
            "fitness": 0.9,
            "generation": 1,
            "metadata": {
                "archive_admission": {
                    "admitted": True,
                    "selection_score": 0.9,
                }
            },
            "evaluation": {"is_valid": True},
        },
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output
    assert "duplicate program id 'same'" in r.output
    assert "Best fitness:" not in r.output


@pytest.mark.parametrize(
    "program_id",
    [
        "line\nbreak",
        "api_key=sk-proj_1234567890abcdef",
        "bad\u202egnp",
    ],
)
def test_show_rejects_unselected_history_rows_with_unsafe_ids(tmp_path, program_id):
    rows = [
        {
            "id": "best",
            "code": "x=1",
            "fitness": 1.0,
            "generation": 0,
            "metadata": {
                "archive_admission": {
                    "admitted": True,
                    "selection_score": 1.0,
                }
            },
            "evaluation": {"is_valid": True},
        },
        {
            "id": program_id,
            "code": "x=2",
            "fitness": 0.0,
            "generation": 1,
            "metadata": {"archive_admission": {"admitted": False}},
            "evaluation": {"is_valid": False},
        },
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output
    assert "Program id must be a manifest-safe identifier" in r.output
    assert "Best fitness:" not in r.output


def test_show_rejects_unselected_history_rows_with_incoherent_lineage(tmp_path):
    rows = [
        {
            "id": "best",
            "code": "x=1",
            "fitness": 1.0,
            "generation": 0,
            "metadata": {
                "archive_admission": {
                    "admitted": True,
                    "selection_score": 1.0,
                }
            },
            "evaluation": {"is_valid": True},
        },
        {
            "id": "child",
            "parent_id": "parent",
            "lineage": ["root", "other"],
            "code": "x=2",
            "fitness": 0.0,
            "generation": 1,
            "metadata": {"archive_admission": {"admitted": False}},
            "evaluation": {"is_valid": False},
        },
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output
    assert "Program lineage tail must match parent_id" in r.output
    assert "Best fitness:" not in r.output


@pytest.mark.parametrize(
    ("unselected_payload", "message"),
    [
        ({"code": ["not", "text"]}, "code must be a string"),
        (
            {
                "files": {"main.py": "x=1"},
                "primary_file": "other.py",
            },
            "primary_file missing from files",
        ),
        (
            {
                "files": {"../escape.py": "x=1"},
                "primary_file": "../escape.py",
            },
            "Unsafe candidate path",
        ),
    ],
)
def test_show_rejects_unselected_current_source_payloads(
    tmp_path, unselected_payload, message
):
    rows = [
        {
            "id": "best",
            "code": "x=1",
            "fitness": 1.0,
            "generation": 0,
            "metadata": {
                "archive_admission": {
                    "admitted": True,
                    "selection_score": 1.0,
                }
            },
            "evaluation": {"is_valid": True},
        },
        {
            "id": "bad-source",
            "fitness": 0.0,
            "generation": 1,
            "metadata": {"archive_admission": {"admitted": False}},
            "evaluation": {"is_valid": False},
            **unselected_payload,
        },
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output
    assert message in r.output
    assert "Best fitness:" not in r.output


def test_show_rejects_unselected_legacy_source_payloads(tmp_path):
    rows = [
        {
            "id": "best",
            "code": "x=1",
            "fitness": 1.0,
            "generation": 0,
            "metadata": {},
        },
        {
            "id": "bad-legacy-source",
            "code": {"not": "text"},
            "fitness": 0.0,
            "generation": 1,
            "metadata": {},
        },
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output
    assert "code must be a string" in r.output
    assert "Best fitness:" not in r.output


@pytest.mark.parametrize(
    "metrics_json",
    [
        '{"score": NaN}',
        '{"score": Infinity}',
        '{"score": true}',
    ],
)
def test_show_rejects_legacy_history_with_invalid_metric_values(tmp_path, metrics_json):
    (tmp_path / "history.jsonl").write_text(
        '{"id":"row","code":"x=1","fitness":1.0,"generation":0,'
        f'"metrics":{metrics_json}}}\n',
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert "Program metric values must be JSON-native finite numbers" in r.output
    assert "Metrics:" not in r.output


def test_show_rejects_current_history_with_invalid_metric_values(tmp_path):
    row = {
        "id": "current",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metrics": {"score": float("nan"), "latency": float("inf")},
        "metadata": {
            "archive_admission": {
                "admitted": True,
                "selection_score": 1.0,
            }
        },
        "evaluation": {"is_valid": True},
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert "Program metric values must be JSON-native finite numbers" in r.output


@pytest.mark.parametrize(
    "metrics",
    [
        {"bad name": 1.0},
        {"api_key=sk-proj_metricsecret1234567890": 1.0},
    ],
)
def test_show_rejects_history_with_bad_metric_keys(tmp_path, metrics):
    row = {
        "id": "row",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metrics": metrics,
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert "Program metric names must be manifest-safe metric names" in r.output


def test_show_rejects_unselected_history_rows_with_invalid_metrics(tmp_path):
    rows = [
        {
            "id": "best",
            "code": "x=1",
            "fitness": 1.0,
            "generation": 0,
            "metrics": {"score": 1.0, "is_valid": True},
            "metadata": {
                "archive_admission": {
                    "admitted": True,
                    "selection_score": 1.0,
                }
            },
            "evaluation": {"is_valid": True},
        },
        {
            "id": "bad-metrics",
            "code": "x=2",
            "fitness": 0.0,
            "generation": 1,
            "metrics": {"score": float("nan")},
            "metadata": {"archive_admission": {"admitted": False}},
            "evaluation": {"is_valid": False},
        },
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output
    assert "Program metric values must be JSON-native finite numbers" in r.output
    assert "Best fitness:" not in r.output


def test_show_prints_valid_metrics_as_strict_json(tmp_path):
    row = {
        "id": "row",
        "code": "x=1",
        "fitness": 1.0,
        "generation": 0,
        "metrics": {"score": 1.0, "latency": 2, "is_valid": True},
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert 'Metrics:        {"is_valid": true, "latency": 2, "score": 1.0}' in r.output
    assert "NaN" not in r.output
    assert "Infinity" not in r.output


@pytest.mark.parametrize(
    "path",
    [
        "../outside.py",
        "/absolute.py",
        ".hidden.py",
        "bad\u202egnp.py",
        ("a" * 256) + ".py",
    ],
)
def test_show_rejects_history_workspace_unsafe_paths(tmp_path, path):
    row = {
        "id": "row",
        "fitness": 1.0,
        "generation": 0,
        "files": {path: "x=1"},
        "primary_file": path,
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert "Unsafe candidate path" in r.output
    assert "--- Best workspace ---" not in r.output


def test_show_rejects_history_workspace_duplicate_normalized_paths(tmp_path):
    row = {
        "id": "row",
        "fitness": 1.0,
        "generation": 0,
        "files": {"e\u0301.py": "x=1", "é.py": "x=2"},
        "primary_file": "é.py",
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert "Duplicate candidate path after normalization" in r.output


def test_show_normalizes_history_workspace_paths_before_display(tmp_path):
    row = {
        "id": "row",
        "fitness": 1.0,
        "generation": 0,
        "files": {"nested/e\u0301.py": "x=1", "helper.py": "y=2"},
        "primary_file": "nested/e\u0301.py",
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "Primary file:   nested/é.py" in r.output
    assert "Files:          nested/é.py, helper.py" in r.output
    assert "--- nested/é.py (primary) ---" in r.output
    assert "--- helper.py ---" in r.output


def test_show_rejects_history_workspace_compatibility_confusable_paths(tmp_path):
    row = {
        "id": "row",
        "fitness": 1.0,
        "generation": 0,
        "files": {"main.py": "x=1", "Ａ.py": "y=2"},
        "primary_file": "main.py",
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 1" in r.output
    assert "compatibility-normalized" in r.output


def test_show_truncates_large_legacy_source_output(tmp_path):
    end_sentinel = "END_SENTINEL_SHOULD_NOT_PRINT"
    code = ("A" * 50000) + end_sentinel
    row = {
        "id": "large-source",
        "code": code,
        "fitness": 1.0,
        "generation": 0,
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "--- Best program ---" in r.output
    assert "source_truncated=True" in r.output
    assert "source_chars=50029" in r.output
    assert "displayed_chars=4096" in r.output
    assert "omitted_chars=45933" in r.output
    assert "source_sha256=" in r.output
    assert "full_source=history.jsonl" in r.output
    assert end_sentinel not in r.output
    assert len(r.output) < 6000


def test_show_uses_configured_source_display_character_budget(tmp_path):
    code = ("A" * 120) + "TAIL_SHOULD_NOT_PRINT"
    row = {
        "id": "custom-limit",
        "code": code,
        "fitness": 1.0,
        "generation": 0,
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(
        cli,
        ["show", str(tmp_path), "--source-display-chars", "40"],
    )

    assert r.exit_code == 0
    assert "displayed_chars=40" in r.output
    assert "rendered_chars=141" in r.output
    assert "omitted_chars=101" in r.output
    assert "TAIL_SHOULD_NOT_PRINT" not in r.output


def test_show_full_source_mode_prints_complete_legacy_source(tmp_path):
    end_sentinel = "END_SENTINEL_SHOULD_PRINT"
    code = ("A" * 6000) + end_sentinel
    row = {
        "id": "full-source",
        "code": code,
        "fitness": 1.0,
        "generation": 0,
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path), "--full-source"])

    assert r.exit_code == 0
    assert end_sentinel in r.output
    assert "source_truncated=True" not in r.output
    assert "displayed_chars=" not in r.output


def test_show_source_display_budget_counts_multibyte_characters(tmp_path):
    code = ("界" * 30) + "TAIL_SHOULD_NOT_PRINT"
    row = {
        "id": "multibyte-source",
        "code": code,
        "fitness": 1.0,
        "generation": 0,
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(
        cli,
        ["show", str(tmp_path), "--source-display-chars", "10"],
    )

    assert r.exit_code == 0
    assert "界" * 10 in r.output
    assert "界" * 11 not in r.output
    assert "source_chars=51" in r.output
    assert "rendered_chars=51" in r.output
    assert "displayed_chars=10" in r.output
    assert "omitted_chars=41" in r.output
    assert "TAIL_SHOULD_NOT_PRINT" not in r.output


def test_show_redacts_source_before_display_budget_accounting(tmp_path):
    token = "sk-proj_showredactsource1234567890"
    code = f"token = {token}\n" + ("x" * 80)
    row = {
        "id": "redacted-source",
        "code": code,
        "fitness": 1.0,
        "generation": 0,
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(
        cli,
        ["show", str(tmp_path), "--redact-source", "--source-display-chars", "35"],
    )

    assert r.exit_code == 0
    assert token not in r.output
    assert "[REDACTED]" in r.output
    assert "source_redacted=True" in r.output
    assert "rendered_chars=" in r.output
    assert "source_sha256=" in r.output


def test_show_truncates_large_workspace_file_outputs(tmp_path):
    primary_sentinel = "PRIMARY_TAIL_SHOULD_NOT_PRINT"
    helper_sentinel = "HELPER_TAIL_SHOULD_NOT_PRINT"
    primary = ("P" * 6000) + primary_sentinel
    helper = ("H" * 7000) + helper_sentinel
    row = {
        "id": "large-workspace",
        "fitness": 1.0,
        "generation": 0,
        "files": {
            "main.py": primary,
            "helper.py": helper,
        },
        "primary_file": "main.py",
        "metadata": {"archive_admission": {"admitted": True}},
        "evaluation": {"is_valid": True},
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code == 0
    assert "--- Best workspace ---" in r.output
    assert "source_truncated=True for main.py" in r.output
    assert "source_truncated=True for helper.py" in r.output
    assert "source_chars=6029" in r.output
    assert "source_chars=7028" in r.output
    assert "displayed_chars=4096" in r.output
    assert "full_source=history.jsonl" in r.output
    assert primary_sentinel not in r.output
    assert helper_sentinel not in r.output
    assert len(r.output) < 10000


def test_show_full_source_mode_prints_complete_workspace_files(tmp_path):
    primary_sentinel = "PRIMARY_TAIL_SHOULD_PRINT"
    helper_sentinel = "HELPER_TAIL_SHOULD_PRINT"
    row = {
        "id": "full-workspace",
        "fitness": 1.0,
        "generation": 0,
        "files": {
            "main.py": ("P" * 6000) + primary_sentinel,
            "very_long_but_safe_helper_name.py": ("H" * 7000) + helper_sentinel,
        },
        "primary_file": "main.py",
        "metadata": {"archive_admission": {"admitted": True}},
        "evaluation": {"is_valid": True},
    }
    (tmp_path / "history.jsonl").write_text(json.dumps(row), encoding="utf-8")

    r = CliRunner().invoke(cli, ["show", str(tmp_path), "--full-source"])

    assert r.exit_code == 0
    assert primary_sentinel in r.output
    assert helper_sentinel in r.output
    assert "very_long_but_safe_helper_name.py" in r.output
    assert "source_truncated=True" not in r.output


def test_show_errors_when_modern_history_has_no_admitted_valid_program(tmp_path):
    (tmp_path / "history.jsonl").write_text(
        json.dumps(
            {
                "id": "invalid",
                "code": "x=999",
                "fitness": 2.0,
                "generation": 1,
                "metadata": {"archive_admission": {"admitted": False}},
                "evaluation": {"is_valid": False},
            }
        ),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "No archive-retained valid programs" in r.output


def test_show_rejects_legacy_then_current_mixed_history_schema(tmp_path):
    rows = [
        {"id": "legacy", "code": "x=1", "fitness": 1.0, "generation": 0},
        {
            "id": "current",
            "code": "x=2",
            "fitness": 0.0,
            "generation": 1,
            "metadata": {"archive_admission": {"admitted": False}},
            "evaluation": {"is_valid": False},
        },
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output
    assert "mixed legacy/current history schemas" in r.output
    assert "first legacy row line 1" in r.output
    assert "first archive_admission row line 2" in r.output
    assert "No archive-retained valid programs" not in r.output


def test_show_rejects_current_then_legacy_mixed_history_schema(tmp_path):
    rows = [
        {
            "id": "current",
            "code": "x=2",
            "fitness": 0.5,
            "generation": 1,
            "metadata": {"archive_admission": {"admitted": True}},
            "evaluation": {"is_valid": True},
        },
        {"id": "legacy", "code": "x=1", "fitness": 1.0, "generation": 0},
    ]
    (tmp_path / "history.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["show", str(tmp_path)])

    assert r.exit_code != 0
    assert "Malformed history.jsonl at line 2" in r.output
    assert "mixed legacy/current history schemas" in r.output
    assert "first legacy row line 2" in r.output
    assert "first archive_admission row line 1" in r.output


def test_run_none_best(tmp_path):
    _make_problem(tmp_path)
    with patch("libreevolve.cli.evolve", return_value=None):
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--max-generations", "1"])
    assert r.exit_code != 0

def test_run_rejects_unknown_config_key(tmp_path):
    _make_problem(tmp_path)
    (tmp_path/"config.yaml").write_text("max_generationz: 5\n")
    r = CliRunner().invoke(cli, ["run", str(tmp_path)])
    assert r.exit_code != 0
    assert "Unknown config keys" in r.output

def test_run_rejects_non_string_config_key(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text("1: bad\n", encoding="utf-8")
    r = CliRunner().invoke(cli, ["run", str(tmp_path)])
    assert r.exit_code != 0
    assert "top-level config keys must be strings" in r.output
    assert "1" in r.output

def test_run_rejects_mixed_unknown_and_non_string_config_keys(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        "1: bad\nunknown_config_key: bad\n",
        encoding="utf-8",
    )
    r = CliRunner().invoke(cli, ["run", str(tmp_path)])
    assert r.exit_code != 0
    assert "top-level config keys must be strings" in r.output
    assert r.exception is None or isinstance(r.exception, SystemExit)

def test_run_rejects_non_mapping_config_file(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text("- max_generations\n", encoding="utf-8")
    r = CliRunner().invoke(cli, ["run", str(tmp_path)])
    assert r.exit_code != 0
    assert "config.yaml must contain a YAML mapping" in r.output

def test_run_reports_malformed_config_yaml_path(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text("max_generations: [1\n", encoding="utf-8")
    r = CliRunner().invoke(cli, ["run", str(tmp_path)])
    assert r.exit_code != 0
    assert "Failed to parse" in r.output
    assert "config.yaml" in r.output


def test_run_reports_invalid_config_encoding_path(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_bytes(b"log_dir: \xff\n")
    r = CliRunner().invoke(cli, ["run", str(tmp_path)])
    assert r.exit_code != 0
    assert "Failed to read" in r.output
    assert "config.yaml" in r.output
    assert "UTF-8" in r.output


def test_run_rejects_duplicate_config_keys_with_path(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        "max_generations: 1\nmax_generations: 2\n",
        encoding="utf-8",
    )
    r = CliRunner().invoke(cli, ["run", str(tmp_path)])
    assert r.exit_code != 0
    assert "Failed to parse" in r.output
    assert "config.yaml" in r.output
    assert "duplicate key" in r.output


@pytest.mark.parametrize(
    ("yaml_text", "message"),
    [
        ("backends: &backends ['openai:gpt-4o-mini']\n", "YAML anchors are not supported"),
        ("*missing_anchor\n", "YAML aliases are not supported"),
    ],
)
def test_run_rejects_config_yaml_anchors_and_aliases(tmp_path, yaml_text, message):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(yaml_text, encoding="utf-8")

    r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code != 0
    assert "Failed to parse config.yaml" in r.output
    assert message in r.output


@pytest.mark.parametrize(
    ("config_bytes", "expected"),
    [
        (b"max_generations: [1\n", "Failed to parse config.yaml"),
        (b"log_dir: \xff\n", "Failed to read config.yaml as UTF-8"),
    ],
)
def test_run_redacts_secret_like_config_root_in_parse_diagnostics(
    tmp_path, config_bytes, expected
):
    secret_root = tmp_path / "api_key=sk-proj_configroot_secret_1234567890"
    secret_root.mkdir()
    _make_problem(secret_root)
    (secret_root / "config.yaml").write_bytes(config_bytes)

    r = CliRunner().invoke(cli, ["run", str(secret_root)])

    assert r.exit_code != 0
    assert expected in r.output
    assert str(secret_root) not in r.output
    assert "sk-proj_configroot_secret_1234567890" not in r.output


def test_run_redacts_secret_like_duplicate_config_key(tmp_path):
    _make_problem(tmp_path)
    secret_key = "api_key=sk-proj_yamldiagsecret1234567890"
    (tmp_path / "config.yaml").write_text(
        f"{secret_key}: 1\n{secret_key}: 2\n",
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code != 0
    assert "Failed to parse config.yaml" in r.output
    assert "duplicate key" in r.output
    assert secret_key not in r.output
    assert "api_key=[REDACTED]" in r.output


def test_run_redacts_secret_like_unknown_config_key(tmp_path):
    _make_problem(tmp_path)
    secret_key = "api_key=sk-proj_unknownconfigsecret1234567890"
    (tmp_path / "config.yaml").write_text(f"{secret_key}: 1\n", encoding="utf-8")

    r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code != 0
    assert "Unknown config keys in config.yaml" in r.output
    assert secret_key not in r.output
    assert "api_key=[REDACTED]" in r.output


def test_run_rejects_config_yaml_directory_with_click_diagnostic(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").mkdir()

    r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code != 0
    assert "config.yaml must be a regular file" in r.output
    assert r.exception is None or isinstance(r.exception, SystemExit)


def test_run_rejects_config_yaml_symlink_with_click_diagnostic(tmp_path):
    _make_problem(tmp_path)
    target = tmp_path / "outside-config.yaml"
    target.write_text("max_generations: 0\n", encoding="utf-8")
    config_path = tmp_path / "config.yaml"
    try:
        config_path.symlink_to(target)
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")

    r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code != 0
    assert "config.yaml links are not supported" in r.output
    assert str(target) not in r.output
    assert r.exception is None or isinstance(r.exception, SystemExit)


def test_run_records_absent_config_source_before_evolve(tmp_path):
    _make_problem(tmp_path)
    mock_best = Program(code="x=2", fitness=0.99)

    with (
        patch("libreevolve.cli._prepare_run_dir_for_cli"),
        patch("libreevolve.cli.evolve", return_value=mock_best) as mock,
    ):
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--max-generations", "0"])

    assert r.exit_code == 0
    problem = mock.call_args.args[0]
    assert problem.config_source == {"path": "config.yaml", "status": "absent"}


def test_run_loads_dotenv_and_records_non_secret_source_before_evolve(
    tmp_path, monkeypatch
):
    _make_problem(tmp_path)
    dotenv_text = "LIBREEVOLVE_DOTENV_PROBE=from_dotenv\n"
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(dotenv_text, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LIBREEVOLVE_DOTENV_PROBE", "from_parent")
    mock_best = Program(code="x=2", fitness=0.99)

    with (
        patch("libreevolve.cli._prepare_run_dir_for_cli"),
        patch("libreevolve.cli.evolve", return_value=mock_best) as mock,
    ):
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--max-generations", "0"])

    assert r.exit_code == 0
    assert os.environ["LIBREEVOLVE_DOTENV_PROBE"] == "from_dotenv"
    problem = mock.call_args.args[0]
    source = problem.dotenv_source
    assert source["path"] == ".env"
    assert source["status"] == "loaded"
    assert source["override"] is True
    assert source["load_phase"] == "cli_run_command"
    assert source["scope"] == "run_command_provider_setup"
    dotenv_bytes = dotenv_path.read_bytes()
    assert source["bytes"] == len(dotenv_bytes)
    assert source["sha256"] == hashlib.sha256(dotenv_bytes).hexdigest()
    assert source["keys"] == ["LIBREEVOLVE_DOTENV_PROBE"]
    assert "from_dotenv" not in json.dumps(source)


def test_run_manifest_records_config_file_provenance(tmp_path):
    _make_problem(tmp_path)
    config_text = (
        f"log_dir: {(tmp_path / 'runs').as_posix()}\n"
        "max_generations: 0\n"
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(config_text, encoding="utf-8")

    r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code == 0
    manifest = json.loads(
        (tmp_path / "runs" / tmp_path.name / "manifest.json").read_text(encoding="utf-8")
    )
    source = manifest["provenance"]["config"]
    config_bytes = config_path.read_bytes()
    assert source["path"] == "config.yaml"
    assert source["status"] == "ok"
    assert source["bytes"] == len(config_bytes)
    assert source["sha256"] == hashlib.sha256(config_bytes).hexdigest()


def test_run_accepts_embedded_only_problem_without_validate_py(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "validate.py").unlink()
    (tmp_path / "initial_programs" / "seed.py").write_text(
        "def evaluate(eval_inputs):\n"
        "    return {'score': eval_inputs['score'], 'is_valid': True}\n",
        encoding="utf-8",
    )
    config_text = (
        f"log_dir: {(tmp_path / 'runs').as_posix()}\n"
        "max_generations: 0\n"
        "eval_stages:\n"
        "  - name: candidate_eval\n"
        "    mode: embedded_evaluate\n"
        "    eval_inputs:\n"
        "      score: 0.75\n"
    )
    (tmp_path / "config.yaml").write_text(config_text, encoding="utf-8")

    r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code == 0
    manifest = json.loads(
        (tmp_path / "runs" / tmp_path.name / "manifest.json").read_text(encoding="utf-8")
    )
    report = manifest["runtime"]["history"]["embedded_evaluator_entrypoint_report"]
    assert report["validation"]["ok"] is True
    assert report["embedded_entrypoint_count"] == 1
    record = report["records"][0]
    assert record["evaluator_mode"] == "embedded_evaluate"
    assert record["signature"] == "evaluate(eval_inputs)"


def test_run_zero_generation_all_invalid_seed_manifest_matches_cli_no_best(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "validate.py").write_text(
        "def evaluate(c): return {'score': -1.0, 'is_valid': False}\n",
        encoding="utf-8",
    )
    config_text = (
        f"log_dir: {(tmp_path / 'runs').as_posix()}\n"
        "max_generations: 0\n"
    )
    (tmp_path / "config.yaml").write_text(config_text, encoding="utf-8")

    r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code != 0
    assert "Evolution produced no valid programs." in r.output
    run_dir = tmp_path / "runs" / tmp_path.name
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    runtime = manifest["runtime"]
    assert runtime["status"] == "completed"
    assert runtime["stop_reason"] == "no_valid_programs"
    assert runtime["consumed"]["seed_evaluations"] == 1
    assert runtime["consumed"]["candidate_evaluations"] == 0
    assert runtime["artifacts"]["history.jsonl"]["exists"] is True
    assert runtime["artifacts"]["failure_history.jsonl"]["exists"] is True
    assert runtime["artifacts"]["best.py"]["exists"] is False
    assert runtime["artifacts"]["best_workspace"]["exists"] is False
    assert not (run_dir / "best.py").exists()
    assert not (run_dir / "best_workspace").exists()


@pytest.mark.parametrize(
    "run_id",
    [
        "mutated\nrun",
        "sk-proj_runidsecret_1234567890abcdef",
    ],
)
def test_run_rejects_unsafe_configured_run_id_before_evolve(tmp_path, run_id):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        f"run_id: {run_id!r}\n",
        encoding="utf-8",
    )

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code != 0
    assert "run_id must be a manifest-safe identifier" in r.output
    mock.assert_not_called()


def test_cli_overrides_invalid_config_before_validation(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        "max_generations: -1\n"
        "backends: []\n"
        f"log_dir: {(tmp_path / 'runs').as_posix()}\n",
        encoding="utf-8",
    )
    best = Program(code="x=2", fitness=0.99)

    with patch("libreevolve.cli.evolve", return_value=best) as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--max-generations",
                "0",
                "--backends",
                "ollama:llama3",
            ],
        )

    assert r.exit_code == 0
    config = mock.call_args.args[1]
    assert config.max_generations == 0
    assert config.backends == [{"type": "ollama", "model": "llama3"}]


@pytest.mark.parametrize(
    ("yaml_text", "message"),
    [
        ("eval_stages:\n  - 1: bad\n    unknown: bad\n", "eval_stages[0] keys must be strings"),
        ("llm_feedback:\n  - 1: bad\n    unknown: bad\n", "llm_feedback[0] keys must be strings"),
        (
            "backends:\n  - type: openai\n    model: m\n    1: bad\n    unknown: bad\n",
            "backends[0] keys must be strings",
        ),
    ],
)
def test_run_rejects_non_string_nested_config_keys_with_config_error(tmp_path, yaml_text, message):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(yaml_text, encoding="utf-8")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code != 0
    assert message in r.output
    mock.assert_not_called()


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda d: (d / "metrics.yaml").write_text("not_metrics: true\n"), "metrics.yaml"),
        (
            lambda d: (d / "metrics.yaml").write_text(
                "metrics:\n"
                "  - name: score\n"
                "    direction: maximize\n"
                "    primary: true\n"
                "    bounds: [0, 1]\n"
                "metricz: []\n",
                encoding="utf-8",
            ),
            "unsupported top-level metrics.yaml fields",
        ),
        (
            lambda d: (d / "metrics.yaml").write_text(
                "metrics:\n"
                "  - name: score\n"
                "    1: bad\n"
                "    unknown: bad\n",
                encoding="utf-8",
            ),
            "metric #1 keys must be strings",
        ),
        (lambda d: (d / "metrics.yaml").write_text("metrics: [\n", encoding="utf-8"), "metrics.yaml"),
        (lambda d: (d / "metrics.yaml").write_bytes(b"metrics: \xff\n"), "metrics.yaml"),
        (
            lambda d: ((d / "metrics.yaml").unlink(), (d / "metrics.yaml").mkdir()),
            "regular file",
        ),
        (lambda d: (d / "validate.py").unlink(), "validate.py"),
        (
            lambda d: ((d / "validate.py").unlink(), (d / "validate.py").mkdir()),
            "regular file",
        ),
        (lambda d: (d / "task_description.txt").write_text("  \n\t"), "task_description.txt"),
        (lambda d: (d / "task_description.txt").write_bytes(b"task \xff\n"), "task_description.txt"),
        (
            lambda d: (
                (d / "task_description.txt").unlink(),
                (d / "task_description.txt").mkdir(),
            ),
            "regular file",
        ),
        (lambda d: (d / "initial_programs" / "seed.py").write_bytes(b"x = \xff\n"), "seed.py"),
        (lambda d: (d / "initial_programs" / "seed.py").unlink(), "No seed programs"),
        (
            lambda d: (
                (d / "context").mkdir(),
                (d / "context" / "context.yaml").mkdir(),
            ),
            "regular file",
        ),
        (
            lambda d: (
                (d / "context").mkdir(),
                (d / "context" / "context.yaml").write_text("includes: ['*.md']\n"),
            ),
            "unsupported context manifest fields",
        ),
        (
            lambda d: (
                (d / "context").mkdir(),
                (d / "context" / "context.yaml").write_text("1: bad\nunknown: bad\n"),
            ),
            "context manifest keys must be strings",
        ),
    ],
)
def test_run_normalizes_problem_load_failures(tmp_path, mutate, message):
    _make_problem(tmp_path)
    mutate(tmp_path)

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code == 1
    assert message in r.output
    assert r.exception is not None
    assert mock.call_count == 0


def test_run_rejects_symlinked_problem_root_before_evolve(tmp_path):
    target = tmp_path / "target_problem"
    target.mkdir()
    _make_problem(target)
    link = tmp_path / "linked_problem"
    try:
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(link)])

    assert r.exit_code == 1
    assert "Problem directory links are not supported" in r.output
    mock.assert_not_called()


def test_run_rejects_junction_problem_root_before_evolve(tmp_path):
    if os.name != "nt":
        pytest.skip("Windows junctions are only available on Windows")
    target = tmp_path / "target_problem"
    target.mkdir()
    _make_problem(target)
    link = tmp_path / "linked_problem"
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"junction creation is unavailable: {result.stderr or result.stdout}")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(link)])

    assert r.exit_code == 1
    assert "Problem directory links are not supported" in r.output
    mock.assert_not_called()


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: (d / "metrics.yaml").write_text(
            "api_key=sk-proj_yamldiagsecret1234567890: 1\n"
            "api_key=sk-proj_yamldiagsecret1234567890: 2\n",
            encoding="utf-8",
        ),
        lambda d: (
            (d / "context").mkdir(),
            (d / "context" / "context.yaml").write_text(
                "api_key=sk-proj_yamldiagsecret1234567890: 1\n"
                "api_key=sk-proj_yamldiagsecret1234567890: 2\n",
                encoding="utf-8",
            ),
        ),
    ],
)
def test_run_redacts_secret_like_setup_yaml_duplicate_keys(tmp_path, mutate):
    _make_problem(tmp_path)
    secret_key = "api_key=sk-proj_yamldiagsecret1234567890"
    mutate(tmp_path)

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path)])

    assert r.exit_code == 1
    assert "duplicate key" in r.output
    assert secret_key not in r.output
    assert "api_key=[REDACTED]" in r.output
    mock.assert_not_called()


def test_run_preflights_validator_contract_before_overwrite(tmp_path):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    run_dir = log_dir / "preflight_probe"
    run_dir.mkdir(parents=True)
    old_history = "old history\n"
    (run_dir / "history.jsonl").write_text(old_history, encoding="utf-8")
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n", encoding="utf-8")
    (tmp_path / "validate.py").write_text("BROKEN = True\n", encoding="utf-8")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--run-name",
                "preflight_probe",
                "--overwrite",
                "--max-generations",
                "1",
            ],
        )

    assert r.exit_code == 1
    assert "missing callable evaluate" in r.output
    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == old_history
    assert not (run_dir / "manifest.json").exists()
    assert mock.call_count == 0


def test_run_preflight_failure_redacts_secret_like_problem_root(tmp_path):
    secret_dir = tmp_path / "api_key=sk-proj_preflightpath_secret_1234567890"  # pragma: allowlist secret
    secret_dir.mkdir()
    _make_problem(secret_dir)
    (secret_dir / "validate.py").write_text("BROKEN = True\n", encoding="utf-8")
    raw_secret_path = str(secret_dir)

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(secret_dir),
                "--max-generations",
                "1",
                "--run-name",
                "preflight_root_redaction",
            ],
        )

    assert r.exit_code == 1
    assert "Evaluator preflight failed for validate.py" in r.output
    assert "path_scope=problem_relative" in r.output
    assert "path_hash=" in r.output
    assert "missing callable evaluate" in r.output
    assert raw_secret_path not in r.output
    assert "sk-proj_preflightpath_secret" not in r.output
    assert mock.call_count == 0


@pytest.mark.parametrize(
    ("source", "message"),
    [
        (
            "async def evaluate(code):\n"
            "    return {'score': 1.0, 'is_valid': True}\n",
            "async evaluate functions are unsupported",
        ),
        (
            "def evaluate(code):\n"
            "    yield {'score': 1.0, 'is_valid': True}\n",
            "generator evaluate functions are unsupported",
        ),
    ],
)
def test_run_rejects_unsupported_validator_callables_before_overwrite(
    tmp_path,
    source,
    message,
):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    run_dir = log_dir / "preflight_callable_probe"
    run_dir.mkdir(parents=True)
    old_history = "old history\n"
    (run_dir / "history.jsonl").write_text(old_history, encoding="utf-8")
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n", encoding="utf-8")
    (tmp_path / "validate.py").write_text(source, encoding="utf-8")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--run-name",
                "preflight_callable_probe",
                "--overwrite",
                "--max-generations",
                "1",
            ],
        )

    assert r.exit_code == 1
    assert message in r.output
    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == old_history
    assert not (run_dir / "manifest.json").exists()
    assert mock.call_count == 0


def test_run_preflights_plugin_names_before_overwrite(tmp_path):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    run_dir = log_dir / "plugin_probe"
    run_dir.mkdir(parents=True)
    old_history = "old history\n"
    (run_dir / "history.jsonl").write_text(old_history, encoding="utf-8")
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n", encoding="utf-8")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--run-name",
                "plugin_probe",
                "--plugins",
                "missing",
                "--overwrite",
                "--max-generations",
                "1",
            ],
        )

    assert r.exit_code == 1
    assert "Unknown plugin: 'missing'" in r.output
    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == old_history
    assert not (run_dir / "manifest.json").exists()
    assert mock.call_count == 0


def test_run_preflights_plugin_options_before_overwrite(tmp_path):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    run_dir = log_dir / "plugin_probe"
    run_dir.mkdir(parents=True)
    old_history = "old history\n"
    (run_dir / "history.jsonl").write_text(old_history, encoding="utf-8")
    (tmp_path / "config.yaml").write_text(
        "plugins:\n"
        "  - name: deep_research\n"
        "    options:\n"
        "      search_every: 0\n"
        f"log_dir: {log_dir.as_posix()}\n",
        encoding="utf-8",
    )

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--run-name",
                "plugin_probe",
                "--overwrite",
                "--max-generations",
                "1",
            ],
        )

    assert r.exit_code == 1
    assert "Plugin 'deep_research' option 'search_every' must be a positive integer" in r.output
    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == old_history
    assert not (run_dir / "manifest.json").exists()
    assert mock.call_count == 0


def test_unknown_plugin_is_rejected_before_validator_import_preflight(tmp_path):
    _make_problem(tmp_path)
    marker = tmp_path / "validator_imported.txt"
    (tmp_path / "validate.py").write_text(
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('imported', encoding='utf-8')\n"
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )

    r = CliRunner().invoke(
        cli,
        [
            "run",
            str(tmp_path),
            "--plugins",
            "missing",
            "--max-generations",
            "0",
        ],
    )

    assert r.exit_code == 1
    assert "Unknown plugin: 'missing'" in r.output
    assert not marker.exists()


def test_unsafe_plugin_label_is_rejected_before_validator_import_preflight(tmp_path):
    _make_problem(tmp_path)
    marker = tmp_path / "validator_imported.txt"
    (tmp_path / "config.yaml").write_text(
        "plugins:\n"
        "  - ' causal '\n",
        encoding="utf-8",
    )
    (tmp_path / "validate.py").write_text(
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('imported', encoding='utf-8')\n"
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )

    r = CliRunner().invoke(
        cli,
        [
            "run",
            str(tmp_path),
            "--max-generations",
            "0",
        ],
    )

    assert r.exit_code == 1
    assert "plugins[0] must be a manifest-safe plugin label" in r.output
    assert not marker.exists()


def test_zero_generation_run_does_not_require_provider_credentials(tmp_path, monkeypatch):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    r = CliRunner().invoke(
        cli,
        [
            "run",
            str(tmp_path),
            "--max-generations",
            "0",
            "--backends",
            "openai:gpt-4o-mini",
        ],
    )

    assert r.exit_code == 0
    assert "Best fitness: 1.000000" in r.output
    run_dir = log_dir / tmp_path.name
    assert (run_dir / "history.jsonl").exists()
    assert (run_dir / "manifest.json").exists()


def test_run_preflights_llm_credentials_before_overwrite(tmp_path, monkeypatch):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    run_dir = log_dir / "provider_probe"
    run_dir.mkdir(parents=True)
    old_history = "old history\n"
    (run_dir / "history.jsonl").write_text(old_history, encoding="utf-8")
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--run-name",
                "provider_probe",
                "--backends",
                "openai:gpt-4o-mini",
                "--overwrite",
                "--max-generations",
                "1",
            ],
        )

    assert r.exit_code == 1
    assert "LLM backend preflight failed" in r.output
    assert "OPENAI_API_KEY" in r.output
    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == old_history
    assert not (run_dir / "manifest.json").exists()
    assert mock.call_count == 0


def test_run_preflights_gemini_credentials_before_overwrite(tmp_path, monkeypatch):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    run_dir = log_dir / "gemini_provider_probe"
    run_dir.mkdir(parents=True)
    old_history = "old history\n"
    (run_dir / "history.jsonl").write_text(old_history, encoding="utf-8")
    (tmp_path / "config.yaml").write_text(
        f"log_dir: {log_dir.as_posix()}\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with patch("libreevolve.cli.evolve") as mock:
        result = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--run-name",
                "gemini_provider_probe",
                "--backends",
                "gemini:gemini-2.0-flash",
                "--overwrite",
                "--max-generations",
                "1",
            ],
        )

    assert result.exit_code == 1
    assert "LLM backend preflight failed" in result.output
    assert "GOOGLE_API_KEY or GEMINI_API_KEY" in result.output
    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == old_history
    assert not (run_dir / "manifest.json").exists()
    assert mock.call_count == 0


def test_mutation_run_preflights_provider_before_all_invalid_seed_diagnostics(
    tmp_path,
    monkeypatch,
):
    _make_problem(tmp_path)
    (tmp_path / "validate.py").write_text(
        "def evaluate(c): return {'score': -1.0, 'is_valid': False}",
        encoding="utf-8",
    )
    log_dir = tmp_path / "runs"
    run_dir = log_dir / "invalid_seed_provider_probe"
    run_dir.mkdir(parents=True)
    old_history = "old history\n"
    (run_dir / "history.jsonl").write_text(old_history, encoding="utf-8")
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--run-name",
                "invalid_seed_provider_probe",
                "--backends",
                "openai:gpt-4o-mini",
                "--overwrite",
                "--max-generations",
                "3",
            ],
        )

    assert r.exit_code == 1
    assert "LLM backend preflight failed" in r.output
    assert "OPENAI_API_KEY" in r.output
    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == old_history
    assert not (run_dir / "manifest.json").exists()
    assert mock.call_count == 0


@pytest.mark.parametrize(
    ("backend", "env_name"),
    [
        ("openai:gpt-4o-mini", "OPENAI_API_KEY"),
        ("anthropic:claude-sonnet-4-6", "ANTHROPIC_API_KEY"),
    ],
)
def test_run_rejects_blank_llm_credentials_before_overwrite(
    tmp_path,
    monkeypatch,
    backend,
    env_name,
):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    run_dir = log_dir / "blank_provider_probe"
    run_dir.mkdir(parents=True)
    old_history = "old history\n"
    (run_dir / "history.jsonl").write_text(old_history, encoding="utf-8")
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n", encoding="utf-8")
    monkeypatch.setenv(env_name, " \t ")

    with patch("libreevolve.cli.evolve") as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--run-name",
                "blank_provider_probe",
                "--backends",
                backend,
                "--overwrite",
                "--max-generations",
                "1",
            ],
        )

    assert r.exit_code == 1
    assert "LLM backend preflight failed" in r.output
    assert env_name in r.output
    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == old_history
    assert not (run_dir / "manifest.json").exists()
    assert mock.call_count == 0


def test_run_rejects_bad_cli_backend_spec(tmp_path):
    _make_problem(tmp_path)
    r = CliRunner().invoke(cli, ["run", str(tmp_path), "--backends", "openai:"])
    assert r.exit_code != 0
    assert "model" in r.output


def test_run_rejects_unsafe_backend_model_before_validator_import_preflight(tmp_path):
    _make_problem(tmp_path)
    marker = tmp_path / "validator_imported.txt"
    (tmp_path / "config.yaml").write_text(
        "backends:\n"
        "  - type: openai\n"
        "    model: \"gpt-4o-mini\\napi_key=sk-proj_secret_1234567890\"\n",  # pragma: allowlist secret
        encoding="utf-8",
    )
    (tmp_path / "validate.py").write_text(
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('imported', encoding='utf-8')\n"
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )

    r = CliRunner().invoke(cli, ["run", str(tmp_path), "--max-generations", "0"])

    assert r.exit_code == 1
    assert "backends[0].model must be a manifest-safe model identifier" in r.output
    assert not marker.exists()


def test_run_rejects_invalid_config_mutation_mode(tmp_path):
    _make_problem(tmp_path)
    (tmp_path/"config.yaml").write_text("mutation_mode: typo\n")
    r = CliRunner().invoke(cli, ["run", str(tmp_path)])
    assert r.exit_code != 0
    assert "mutation_mode" in r.output


def test_run_accepts_adaptive_mutation_mode_override(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump({"log_dir": (tmp_path / "runs").as_posix()}),
        encoding="utf-8",
    )
    mock_best = Program(code="x=1", fitness=1.0)

    with patch("libreevolve.cli.evolve", return_value=mock_best) as mock:
        result = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--max-generations",
                "0",
                "--mutation-mode",
                "adaptive",
            ],
        )

    assert result.exit_code == 0
    assert mock.call_args.args[1].mutation_mode == "adaptive"


def test_reasoning_effort_overrides_configured_openai_backend(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(
        yaml.dump(
            {
                "log_dir": (tmp_path / "runs").as_posix(),
                "backends": [
                    {"type": "openai", "model": "gpt-5.4-mini"},
                    {"type": "anthropic", "model": "claude-sonnet-4-6"},
                ]
            }
        )
    )
    best = Program(code="x=2", fitness=0.99)
    with patch("libreevolve.cli.evolve", return_value=best) as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--reasoning-effort", "high"])

    assert r.exit_code == 0
    config = mock.call_args.args[1]
    assert config.backends[0]["reasoning_effort"] == "high"
    assert "reasoning_effort" not in config.backends[1]


def test_reasoning_effort_still_applies_to_cli_backends(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(f"log_dir: {(tmp_path / 'runs').as_posix()}\n")
    best = Program(code="x=2", fitness=0.99)
    with patch("libreevolve.cli.evolve", return_value=best) as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--backends",
                "openai:gpt-5.4-mini",
                "--reasoning-effort",
                "medium",
            ],
        )

    assert r.exit_code == 0
    config = mock.call_args.args[1]
    assert config.backends == [
        {"type": "openai", "model": "gpt-5.4-mini", "reasoning_effort": "medium"}
    ]


def test_reasoning_effort_does_not_attach_to_non_openai_cli_backends(tmp_path):
    _make_problem(tmp_path)
    (tmp_path / "config.yaml").write_text(f"log_dir: {(tmp_path / 'runs').as_posix()}\n")
    best = Program(code="x=2", fitness=0.99)
    with patch("libreevolve.cli.evolve", return_value=best) as mock:
        r = CliRunner().invoke(
            cli,
            [
                "run",
                str(tmp_path),
                "--backends",
                "anthropic:claude-sonnet-4-6",
                "--reasoning-effort",
                "medium",
            ],
        )

    assert r.exit_code == 0
    config = mock.call_args.args[1]
    assert config.backends == [{"type": "anthropic", "model": "claude-sonnet-4-6"}]
