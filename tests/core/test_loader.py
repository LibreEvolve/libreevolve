import tempfile
from pathlib import Path
import pytest, yaml
from libreevolve.problems.loader import load_problem, Problem

def _make(tmp):
    d = Path(tmp)
    (d / "task_description.txt").write_text("test task")
    (d / "metrics.yaml").write_text(yaml.dump({"metrics": [
        {"name": "score", "direction": "maximize", "primary": True, "bounds": [0.0, 1.0]}]}))
    (d / "validate.py").write_text("def evaluate(c): return {'score': 1.0, 'is_valid': True}")
    (d / "initial_programs").mkdir()
    (d / "initial_programs" / "seed.py").write_text("x = 1")
    return d

def test_returns_problem():
    with tempfile.TemporaryDirectory() as t:
        assert isinstance(load_problem(_make(t)), Problem)

def test_reads_task_description():
    with tempfile.TemporaryDirectory() as t:
        assert load_problem(_make(t)).task_description == "test task"

def test_reads_primary_metric():
    with tempfile.TemporaryDirectory() as t:
        assert load_problem(_make(t)).primary_metric == "score"

def test_reads_seeds():
    with tempfile.TemporaryDirectory() as t:
        p = load_problem(_make(t))
        assert len(p.initial_programs) == 1 and "x = 1" in p.initial_programs[0]
        assert p.initial_workspaces[0].primary_file == "seed.py"

def test_raises_on_missing_dir():
    with pytest.raises(FileNotFoundError):
        load_problem("/nonexistent/problem")

def test_raises_on_no_seeds():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        for f in (d / "initial_programs").glob("*.py"): f.unlink()
        with pytest.raises(ValueError, match="No seed programs"):
            load_problem(d)

def test_hello_world_example_loads():
    examples = Path(__file__).parent.parent.parent / "libreevolve/problems/examples/hello_world"
    if not examples.exists():
        pytest.skip("hello_world example not present")
    p = load_problem(examples)
    assert p.name == "hello_world" and len(p.initial_programs) >= 1

def test_primary_bounds_default_when_missing():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(yaml.dump({"metrics": [
            {"name": "score", "direction": "maximize", "primary": True}
        ]}))
        p = load_problem(d)
        assert p.primary_bounds == (0.0, 1.0)

def test_raises_on_malformed_metrics_yaml():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text("not_metrics: true")
        with pytest.raises(ValueError, match="metrics"):
            load_problem(d)


def test_reads_context_files():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "context").mkdir()
        (d / "context" / "notes.md").write_text("important context")
        p = load_problem(d)
        assert p.context_files["notes.md"] == "important context"


def test_reads_pdf_context_files():
    from pypdf import PdfWriter

    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "context").mkdir()
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with open(d / "context" / "paper.pdf", "wb") as f:
            writer.write(f)
        p = load_problem(d)
        assert p.context_files["paper.pdf"] == "(no extractable text)"


def test_truncates_long_context_files():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "context").mkdir()
        (d / "context" / "long.txt").write_text("x" * 7000)
        p = load_problem(d)
        assert "showing first 6000 of 7000 characters" in p.context_files["long.txt"]
        assert len(p.context_files["long.txt"]) < 6100


def test_normalizes_minimize_metric():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(yaml.dump({"metrics": [
            {"name": "loss", "direction": "minimize", "primary": True, "bounds": [0.0, 10.0]}
        ]}))
        p = load_problem(d)
        assert p.fitness_from_metrics({"loss": 2.0}) == 0.8


def test_reads_seed_directory_as_workspace():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        for f in (d / "initial_programs").glob("*.py"):
            f.unlink()
        seed = d / "initial_programs" / "seed_a"
        seed.mkdir()
        (seed / "main.py").write_text("from helper import value\n")
        (seed / "helper.py").write_text("value = 1\n")
        p = load_problem(d)
        assert p.initial_workspaces[0].primary_file == "main.py"
        assert sorted(p.initial_workspaces[0].files) == ["helper.py", "main.py"]
