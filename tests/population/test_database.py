import json, tempfile
from pathlib import Path
from alphaevolve.core.config import Config
from alphaevolve.core.database import ProgramDatabase
from alphaevolve.population.program import Program

def _db(): return ProgramDatabase(Config(log_dir=tempfile.mkdtemp(), problem_name="t"))
def _p(code="x=1", fitness=0.5): return Program(code=code, fitness=fitness)

def test_log_always_appends():
    db = _db(); db.log(_p(fitness=-0.4))
    assert len(db.all_programs()) == 1

def test_add_updates_best():
    db = _db(); p = _p(fitness=0.8); db.log(p); db.add(p)
    assert db.best().fitness == 0.8

def test_log_without_add_not_in_archive():
    db = _db(); db.log(_p(fitness=-0.3))
    assert db.best() is None

def test_sample_exploit():
    db = _db()
    for f in (0.3, 0.7):
        p = _p(fitness=f); db.log(p); db.add(p)
    assert db.sample("exploit").fitness == 0.7

def test_log_writes_jsonl():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(_p(fitness=0.5))
    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert records[0]["fitness"] == 0.5

def test_maybe_migrate_no_crash():
    db = ProgramDatabase(Config(migration_interval=5, n_islands=2,
                                log_dir=tempfile.mkdtemp(), problem_name="t"))
    p = _p(); db.log(p); db.add(p)
    db.maybe_migrate(4); db.maybe_migrate(5)
