import json
import math
import tempfile
from pathlib import Path
import pytest
from libreevolve.core.jsonl import StrictJsonlError
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
    record = json.loads((tmp_path/"grpo_data.jsonl").read_text().splitlines()[0])
    assert record["raw_score"] == 0.7000000000000001
    assert record["reward"] == 0.7000000000000001
    assert record["reward_policy"] == "max(0.0, raw_score)"
    metadata = p.run_artifacts_metadata()
    assert metadata["exported_examples"] == 5
    assert metadata["queued_examples"] == 12
    assert metadata["path"] == str(tmp_path / "grpo_data.jsonl")
    assert metadata["sha256"]
    assert metadata["bytes"] > 0


def test_records_clipped_reward_policy():
    p = TTTRLPlugin()
    p.on_evaluated(_p(), -0.5)
    record = p.get_training_data()[0]
    assert record["raw_score"] == -0.5
    assert record["reward"] == 0.0
    assert record["reward_policy"] == "max(0.0, raw_score)"

def test_rejects_non_finite_jsonl_export(tmp_path):
    p = TTTRLPlugin(train_every=1, log_dir=str(tmp_path))
    p.on_evaluated(_p(), math.inf)
    with pytest.raises(StrictJsonlError):
        p.on_generation_end(1, None)
    record = json.loads((tmp_path/"grpo_data_invalid.jsonl").read_text().splitlines()[0])
    assert "inf" in record["message"]
