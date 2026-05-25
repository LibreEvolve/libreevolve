import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from libreevolve.core.config import Config
from libreevolve.core.loop import evolve, VALID_THRESHOLD
from libreevolve.problems.loader import Problem

def _problem(src="def evaluate(c): return {'score':1.0,'is_valid':True}"):
    d = Path(tempfile.mkdtemp())
    (d/"validate.py").write_text(src)
    return Problem(name="t", task_description="t",
                   metrics=[{"name":"score","primary":True,"bounds":[0.0,1.0]}],
                   primary_metric="score", primary_bounds=(0.0,1.0),
                   validate_path=d/"validate.py", initial_programs=["x=1"], problem_dir=d)

def _llm(diff="<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"):
    m = MagicMock(); m.generate.return_value = (diff, 0); return m

def test_returns_program():
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        best = evolve(_problem(), Config(max_generations=2,
                                        log_dir=tempfile.mkdtemp(), problem_name="t"))
    assert best is not None and isinstance(best.fitness, float)

def test_threshold_is_zero():
    assert VALID_THRESHOLD == 0.0

def test_invalid_diff_not_archived():
    with patch("libreevolve.core.loop.build_llm", return_value=_llm("no diff here")):
        best = evolve(_problem(), Config(max_generations=1,
                                        log_dir=tempfile.mkdtemp(), problem_name="t"))
    assert best.fitness == 1.0  # seed still best

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
    assert ("start", 0) in calls and ("end", 0) in calls


def test_loop_logs_prompt_program_id_and_prompt_history():
    tmpdir = tempfile.mkdtemp()
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    run_dir = Path(tmpdir) / "t"
    records = [json.loads(l) for l in (run_dir / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert "prompt_program_id" in child["metadata"]
    assert (run_dir / "prompt_history.jsonl").exists()


def test_meta_prompt_evolution_adds_mutated_prompt_template():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        ("[SYSTEM]\n{task}\n{context}\n{parent_score}\n{parent_metrics}\n{parent_feedback}\n{parent_code}\n{inspirations}\n{extra_context}\n{recent_failures}", 0),
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
