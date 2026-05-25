import json, tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from libreevolve.cli import cli
from libreevolve.population.program import Program
import yaml

def _make_problem(tmp_path):
    (tmp_path/"task_description.txt").write_text("t")
    (tmp_path/"metrics.yaml").write_text(yaml.dump({"metrics": [
        {"name":"score","primary":True,"direction":"maximize","bounds":[0.0,1.0]}]}))
    (tmp_path/"validate.py").write_text("def evaluate(c): return {'score':1.0,'is_valid':True}")
    s = tmp_path/"initial_programs"; s.mkdir(); (s/"seed.py").write_text("x=1")

def test_help(): assert "run" in CliRunner().invoke(cli, ["--help"]).output
def test_run_help(): assert "PROBLEM_DIR" in CliRunner().invoke(cli, ["run", "--help"]).output
def test_show_help(): assert CliRunner().invoke(cli, ["show", "--help"]).exit_code == 0

def test_run_calls_evolve(tmp_path):
    _make_problem(tmp_path)
    mock_best = MagicMock(); mock_best.fitness = 0.99; mock_best.code = "x=2"
    with patch("libreevolve.cli.evolve", return_value=mock_best) as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--max-generations", "1"])
    assert r.exit_code == 0 and mock.called

def test_run_writes_complete_best_workspace(tmp_path):
    _make_problem(tmp_path)
    log_dir = tmp_path / "runs"
    (tmp_path / "config.yaml").write_text(f"log_dir: {log_dir.as_posix()}\n")
    best = Program(
        files={
            "main.py": "from pkg.helper import value\n",
            "pkg/helper.py": "value = 2\n",
        },
        primary_file="main.py",
        fitness=0.99,
    )
    with patch("libreevolve.cli.evolve", return_value=best):
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--max-generations", "1"])

    run_dir = log_dir / tmp_path.name
    assert r.exit_code == 0
    assert (run_dir / "best.py").read_text(encoding="utf-8") == best.code
    assert (run_dir / "best_workspace" / "main.py").read_text(encoding="utf-8") == best.code
    assert (
        run_dir / "best_workspace" / "pkg" / "helper.py"
    ).read_text(encoding="utf-8") == "value = 2\n"
    assert "Best workspace saved to:" in r.output

def test_show_prints_best(tmp_path):
    (tmp_path/"history.jsonl").write_text(json.dumps(
        {"id":"a","code":"x=2","fitness":0.9,"generation":1,
         "parent_id":None,"lineage":[],"metadata":{}}))
    r = CliRunner().invoke(cli, ["show", str(tmp_path)])
    assert r.exit_code == 0 and "0.9" in r.output and "x=2" in r.output

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

def test_run_rejects_bad_cli_backend_spec(tmp_path):
    _make_problem(tmp_path)
    r = CliRunner().invoke(cli, ["run", str(tmp_path), "--backends", "openai:"])
    assert r.exit_code != 0
    assert "model" in r.output

def test_run_rejects_invalid_config_mutation_mode(tmp_path):
    _make_problem(tmp_path)
    (tmp_path/"config.yaml").write_text("mutation_mode: typo\n")
    r = CliRunner().invoke(cli, ["run", str(tmp_path)])
    assert r.exit_code != 0
    assert "mutation_mode" in r.output
