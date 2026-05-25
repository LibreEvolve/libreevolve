import json
import math
import tempfile
from pathlib import Path

import pytest

from libreevolve.core.jsonl import StrictJsonlError
from libreevolve.core.meta_prompt import PromptDatabase


def test_prompt_database_selects_and_scores_templates():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}", "b {task}"])

    first = db.select()
    db.record_result(first.id, 0.25)

    assert first.uses == 1
    assert first.mean_reward == 0.25
    assert (Path(tmpdir) / "prompt_history.jsonl").exists()


def test_prompt_database_mutates_with_lineage():
    db = PromptDatabase(tempfile.mkdtemp(), templates=["a {task}"])
    parent = db.select()
    child = db.mutate(parent.id, "b {task}", generation=3)

    assert child.parent_id == parent.id
    assert child.generation == 3
    assert len(db.all()) == 2


def test_prompt_database_logs_add_and_score_events():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    program = db.select()
    db.record_result(program.id, 1.0)

    events = [
        json.loads(line)["event"]
        for line in (Path(tmpdir) / "prompt_history.jsonl").read_text().splitlines()
    ]
    assert events == ["add", "score"]


def test_prompt_database_rejects_non_finite_score_with_quarantine():
    tmpdir = tempfile.mkdtemp()
    db = PromptDatabase(tmpdir, templates=["a {task}"])
    program = db.select()

    with pytest.raises(StrictJsonlError):
        db.record_result(program.id, math.nan)

    assert program.uses == 0
    assert program.reward_sum == 0.0
    quarantine = Path(tmpdir) / "prompt_history_invalid.jsonl"
    record = json.loads(quarantine.read_text().splitlines()[0])
    assert "nan" in record["message"]
