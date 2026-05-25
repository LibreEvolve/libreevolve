import json, math, tempfile
from pathlib import Path
import pytest
from libreevolve.core.config import Config
from libreevolve.core.database import ProgramDatabase
from libreevolve.core.jsonl import StrictJsonlError
from libreevolve.population.program import Program

def _db(): return ProgramDatabase(Config(log_dir=tempfile.mkdtemp(), problem_name="t"))
def _p(code="x=1", fitness=0.5): return Program(code=code, fitness=fitness)

def test_log_always_appends():
    db = _db(); db.log(_p(fitness=-0.4))
    assert len(db.all_programs()) == 1

def test_add_updates_best():
    db = _db(); p = _p(fitness=0.8); db.log(p); db.add(p)
    assert db.best().fitness == 0.8

def test_admit_records_archive_event_on_program_metadata():
    db = _db()
    p = _p(fitness=0.8)
    event = db.admit(p, threshold=0.0)
    assert event["admitted"] is True
    assert p.metadata["archive_admission"]["program_id"] == p.id
    assert p.metadata["archive_admission"]["island_id"] == 0
    assert p.metadata["archive_admission"]["threshold"] == 0.0

def test_admit_below_threshold_does_not_archive():
    db = _db()
    p = _p(fitness=-0.1)
    event = db.admit(p, threshold=0.0)
    assert event["admitted"] is False
    assert event["reason"] == "below_threshold"
    assert event["island_id"] is None
    assert db.best() is None

def test_log_without_add_not_in_archive():
    db = _db(); db.log(_p(fitness=-0.3))
    assert db.best() is None

def test_sample_exploit():
    db = _db()
    for f in (0.3, 0.7):
        p = _p(fitness=f); db.log(p); db.add(p)
    assert db.sample("exploit").fitness == 0.7

def test_sample_diverse_excludes_program_ids():
    db = _db()
    p = _p(fitness=0.7); db.log(p); db.add(p)
    assert db.sample_diverse(k=3, exclude_ids={p.id}) == []

def test_log_writes_jsonl():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(_p(fitness=0.5))
    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert records[0]["fitness"] == 0.5

def test_log_writes_metrics_and_evaluation():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(_p(fitness=0.5))
    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert "metrics" in records[0]
    assert "evaluation" in records[0]

def test_log_writes_candidate_files():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(Program(
        files={"main.py": "x=1", "helper.py": "y=2"},
        primary_file="main.py",
        fitness=0.0,
    ))
    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert records[0]["primary_file"] == "main.py"
    assert records[0]["files"]["helper.py"] == "y=2"

def test_log_rejects_non_finite_records_with_quarantine():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    with pytest.raises(StrictJsonlError):
        db.log(_p(fitness=math.inf))
    assert db.all_programs() == []
    assert not (Path(tmpdir)/"t"/"history.jsonl").exists()
    quarantine = Path(tmpdir)/"t"/"history_invalid.jsonl"
    record = json.loads(quarantine.read_text().splitlines()[0])
    assert "inf" in record["message"]

def test_manifest_written():
    tmpdir = tempfile.mkdtemp()
    ProgramDatabase(Config(log_dir=tmpdir, problem_name="t", mutation_mode="full"))
    manifest = json.loads((Path(tmpdir)/"t"/"manifest.json").read_text())
    assert manifest["config"]["mutation_mode"] == "full"

def test_maybe_migrate_triggers_on_interval():
    db = ProgramDatabase(Config(migration_interval=5, n_islands=2,
                                log_dir=tempfile.mkdtemp(), problem_name="t"))
    p = _p(); db.log(p); db.add(p)
    # Before interval: island 1 has nothing
    assert db._islands.islands[1].best() is None
    db.maybe_migrate(4)  # not a multiple of 5 — no migration
    assert db._islands.islands[1].best() is None
    db.maybe_migrate(5)  # multiple of 5 — migration fires
    assert db._islands.islands[1].best() is not None
