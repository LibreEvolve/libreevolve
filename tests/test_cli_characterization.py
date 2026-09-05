"""Focused characterization tests for the public LibreEvolve CLI contracts."""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

import libreevolve.cli as cli_module
from libreevolve.cli import cli
from libreevolve.core.database import _validator_execution_policy
from libreevolve.core.evaluator import _validator_boundary_metadata
from libreevolve.population.program import Program


def _make_problem(root: Path) -> Path:
    problem = root / "problem"
    seed_dir = problem / "initial_programs"
    seed_dir.mkdir(parents=True)
    (problem / "task_description.txt").write_text("return the score", encoding="utf-8")
    (problem / "metrics.yaml").write_text(
        "metrics:\n"
        "  - name: score\n"
        "    primary: true\n"
        "    direction: maximize\n"
        "    bounds: [0.0, 1.0]\n",
        encoding="utf-8",
    )
    (problem / "validate.py").write_text(
        "def evaluate(code):\n"
        "    return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    (seed_dir / "seed.py").write_text("value = 1\n", encoding="utf-8")
    (problem / "config.yaml").write_text(
        f"log_dir: {(root / 'runs').as_posix()}\n",
        encoding="utf-8",
    )
    return problem


def _show_record(program_id: str, fitness: float, generation: int, code: str) -> dict:
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


def _write_history(run_dir: Path, records: list[dict]) -> None:
    (run_dir / "history.jsonl").write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )


def _write_manifest(run_dir: Path, *, programs_logged: int = 1) -> None:
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "runtime": {
                    "status": "completed",
                    "stop_reason": "max_generations",
                    "history": {"programs_logged": programs_logged},
                },
                "policies": {"validator_execution": _validator_execution_policy("host")},
            }
        ),
        encoding="utf-8",
    )


def _disable_dotenv_loading(monkeypatch) -> None:
    monkeypatch.setattr(cli_module, "_load_cli_dotenv", lambda: {})


def test_characterization_help_and_command_help_contract():
    runner = CliRunner()

    root = runner.invoke(cli, ["--help"])
    run = runner.invoke(cli, ["run", "--help"])
    show = runner.invoke(cli, ["show", "--help"])

    assert root.exit_code == 0
    assert "run" in root.output
    assert run.exit_code == 0
    assert "PROBLEM_DIR" in run.output
    assert show.exit_code == 0
    assert "RUN_DIR" in show.output


def test_characterization_run_and_show_output_contract(tmp_path, monkeypatch):
    _disable_dotenv_loading(monkeypatch)
    problem = _make_problem(tmp_path)

    run_result = CliRunner().invoke(
        cli,
        [
            "run",
            str(problem),
            "--max-generations",
            "0",
            "--run-name",
            "characterization",
        ],
    )

    assert run_result.exit_code == 0, run_result.output
    assert "Running 0 generations on 'characterization'" in run_result.output
    assert "Best fitness: 1.000000" in run_result.output
    assert "best.py" in run_result.output
    assert "best_workspace" in run_result.output

    run_dir = tmp_path / "runs" / "characterization"
    show_result = CliRunner().invoke(cli, ["show", str(run_dir)])

    assert show_result.exit_code == 0, show_result.output
    assert "Run status:" in show_result.output
    assert "Best fitness:" in show_result.output
    assert "value = 1" in show_result.output


def test_characterization_config_failure_precedes_overwrite(tmp_path, monkeypatch):
    _disable_dotenv_loading(monkeypatch)
    problem = _make_problem(tmp_path)
    (problem / "config.yaml").write_text(
        f"log_dir: {(tmp_path / 'runs').as_posix()}\n"
        "unexpected_key: true\n",
        encoding="utf-8",
    )
    run_dir = tmp_path / "runs" / "config_guard"
    run_dir.mkdir(parents=True)
    sentinel = run_dir / "history.jsonl"
    sentinel.write_text("pre-existing history\n", encoding="utf-8")

    result = CliRunner().invoke(
        cli,
        [
            "run",
            str(problem),
            "--run-name",
            "config_guard",
            "--overwrite",
            "--max-generations",
            "0",
        ],
    )

    assert result.exit_code == 1
    assert "unexpected_key" in result.output
    assert sentinel.read_text(encoding="utf-8") == "pre-existing history\n"
    assert not (run_dir / "manifest.json").exists()


def test_characterization_restore_archive_flags_are_mutually_exclusive(
    tmp_path, monkeypatch
):
    _disable_dotenv_loading(monkeypatch)
    problem = _make_problem(tmp_path)
    manifest = tmp_path / "restore.json"
    manifest.write_text("{}", encoding="utf-8")

    result = CliRunner().invoke(
        cli,
        [
            "run",
            str(problem),
            "--max-generations",
            "0",
            "--restore-archive-cursor-from-manifest",
            str(manifest),
            "--restore-archive-from-manifest",
            str(manifest),
        ],
    )

    assert result.exit_code == 1
    assert "Use either --restore-archive-cursor-from-manifest or" in result.output


def test_characterization_show_malformed_history_has_nonzero_diagnostic(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "history.jsonl").write_text("not-json\n", encoding="utf-8")

    result = CliRunner().invoke(cli, ["show", str(run_dir)])

    assert result.exit_code == 1
    assert "Malformed history.jsonl" in result.output
    assert "line 1" in result.output


def test_characterization_show_is_bounded_and_repeatable(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_history(
        run_dir,
        [_show_record("best", 0.9, 2, "value = 1\n" + ("x" * 512))],
    )
    _write_manifest(run_dir)

    first = CliRunner().invoke(
        cli, ["show", str(run_dir), "--source-display-chars", "32"]
    )
    second = CliRunner().invoke(
        cli, ["show", str(run_dir), "--source-display-chars", "32"]
    )

    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    assert first.output == second.output
    assert "source_truncated=True" in first.output
    assert "displayed_chars=32" in first.output
    assert "full_source=history.jsonl" in first.output


def test_characterization_show_selects_best_record_deterministically(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_history(
        run_dir,
        [
            _show_record("lower", 0.2, 0, "lower = True"),
            _show_record("higher", 0.8, 1, "higher = True"),
        ],
    )
    _write_manifest(run_dir, programs_logged=2)

    result = CliRunner().invoke(cli, ["show", str(run_dir)])

    assert result.exit_code == 0, result.output
    assert "Best fitness:   0.800000 (generation 1)" in result.output
    assert "higher = True" in result.output
    assert "lower = True" not in result.output


def test_characterization_overwrite_preserves_unknown_artifacts(tmp_path, monkeypatch):
    _disable_dotenv_loading(monkeypatch)
    problem = _make_problem(tmp_path)
    run_dir = tmp_path / "runs" / "overwrite_guard"
    run_dir.mkdir(parents=True)
    (run_dir / "history.jsonl").write_text("old history\n", encoding="utf-8")
    preserved = run_dir / "operator-note.txt"
    preserved.write_text("preserve me\n", encoding="utf-8")

    result = CliRunner().invoke(
        cli,
        [
            "run",
            str(problem),
            "--run-name",
            "overwrite_guard",
            "--overwrite",
            "--max-generations",
            "0",
        ],
    )

    assert result.exit_code == 0, result.output
    assert preserved.read_text(encoding="utf-8") == "preserve me\n"
    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") != "old history\n"


def test_characterization_artifact_export_failure_is_bounded_cli_error(
    tmp_path, monkeypatch
):
    _disable_dotenv_loading(monkeypatch)
    problem = _make_problem(tmp_path)
    best = Program(code="value = 2\n", fitness=1.0)

    with patch.object(cli_module, "evolve", return_value=best), patch.object(
        cli_module,
        "_write_best_artifacts",
        side_effect=OSError("synthetic export failure"),
    ):
        result = CliRunner().invoke(
            cli,
            [
                "run",
                str(problem),
                "--run-name",
                "export_failure",
                "--max-generations",
                "0",
            ],
        )

    assert result.exit_code == 1
    assert "Best artifact export failed: synthetic export failure" in result.output


@pytest.mark.skipif(
    os.name == "nt",
    reason="POSIX symlink characterization is not native-Windows evidence",
)
def test_characterization_artifact_path_rejects_symlink_before_write(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("outside = True\n", encoding="utf-8")
    linked_best = run_dir / "best.py"
    linked_best.symlink_to(outside)

    with pytest.raises(OSError, match="refusing to replace linked best artifact path"):
        cli_module._preflight_best_artifact_export_paths(
            run_dir=run_dir,
            paths=(linked_best,),
        )


@pytest.mark.skipif(
    os.name == "nt",
    reason="Native-Windows junction fixture is unavailable in this POSIX/WSL lane",
)
def test_characterization_native_windows_junction_behavior_is_unverified():
    pytest.skip("native-Windows junction behavior requires a native-Windows run")
