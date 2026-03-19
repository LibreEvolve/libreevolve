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
