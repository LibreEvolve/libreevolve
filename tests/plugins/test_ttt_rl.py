import tempfile
from pathlib import Path
from libreevolve.plugins.ttt_rl import TTTRLPlugin
from libreevolve.population.program import Program

def _p(prompt="p", diff="d"):
    return Program(code="x=1", fitness=0.5, metadata={"prompt": prompt, "diff": diff})

def test_passthrough(): assert TTTRLPlugin().on_evaluated(_p(), 0.75) == 0.75

def test_skips_without_metadata():
    p = TTTRLPlugin(); p.on_evaluated(Program(), 0.5)
    assert len(p.get_training_data()) == 0

def test_accumulates():
    p = TTTRLPlugin()
    for i in range(5): p.on_evaluated(_p(), i*0.1)
    assert len(p.get_training_data()) == 5

def test_writes_jsonl(tmp_path):
    p = TTTRLPlugin(train_every=5, log_dir=str(tmp_path))
    for i in range(12): p.on_evaluated(_p(f"p{i}", f"d{i}"), i*0.1)
    p.on_generation_end(5, None)
    assert (tmp_path/"grpo_data.jsonl").exists()
