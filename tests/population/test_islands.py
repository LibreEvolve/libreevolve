from libreevolve.core.config import Config
from libreevolve.population.islands import IslandModel
from libreevolve.population.program import Program

def _m(n=3): return IslandModel(Config(n_islands=n, migration_interval=5))
def _p(code="x=1", fitness=0.5): return Program(code=code, fitness=fitness)
def _pm(code="x=1", fitness=0.5, selection_score=0.5):
    return Program(code=code, fitness=fitness, metadata={"selection_score": selection_score})

def test_best_returns_highest():
    m = _m(); m.add(_p(fitness=0.3)); m.add(_p(fitness=0.7))
    assert m.best().fitness == 0.7

def test_add_reports_island_id_and_rotates():
    m = IslandModel(Config(n_islands=2, migration_interval=5))
    first = m.add(_p(fitness=0.3))
    second = m.add(_p(fitness=0.7))
    assert first["island_id"] == 0
    assert second["island_id"] == 1

def test_sample_exploit_returns_best():
    m = _m(); m.add(_p(fitness=0.3)); m.add(_p(fitness=0.9))
    assert m.sample("exploit").fitness == 0.9

def test_sample_exploit_uses_selection_score():
    m = _m()
    primary_best = _pm(code="x=1", fitness=0.9, selection_score=0.2)
    balanced = _pm(code="x=2", fitness=0.4, selection_score=0.8)
    m.add(primary_best)
    m.add(balanced)
    assert m.sample("exploit").id == balanced.id
    assert m.best().id == balanced.id

def test_migration_copies_not_moves():
    m = IslandModel(Config(n_islands=2, migration_ratio=1.0, elite_archive_size=10))
    m.islands[0].add(_p(fitness=1.0))
    before = len(m.islands[0].occupied_cells())
    m.migrate()
    assert len(m.islands[0].occupied_cells()) == before
    assert m.islands[1].best() is not None

def test_zero_migration_ratio_selects_no_migrants():
    m = IslandModel(Config(n_islands=2, migration_ratio=0.0, elite_archive_size=10))
    m.islands[0].add(_p(fitness=1.0))
    m.migrate()
    assert m.islands[1].best() is None

def test_sample_diverse_returns_list():
    m = _m()
    for i in range(5): m.add(_p(code=f"x={i}", fitness=i*0.1))
    samples = m.sample_diverse(k=3)
    assert isinstance(samples, list) and len(samples) <= 3

def test_sample_diverse_excludes_program_ids():
    m = _m()
    p = _p(code="x=1", fitness=0.5)
    m.add(p)
    assert m.sample_diverse(k=3, exclude_ids={p.id}) == []

def test_sample_diverse_deduplicates_migrated_program_ids():
    m = IslandModel(Config(n_islands=2, migration_ratio=1.0, elite_archive_size=10))
    p = _p(code="x=1", fitness=1.0)
    m.islands[0].add(p)
    m.migrate()
    samples = m.sample_diverse(k=10)
    assert [sample.id for sample in samples] == [p.id]

def test_ring_topology():
    m = IslandModel(Config(n_islands=3, migration_ratio=1.0, elite_archive_size=10))
    m.islands[0].add(_p(code="i0", fitness=1.0))
    m.migrate()
    assert m.islands[1].best() is not None
    assert m.islands[2].best() is None  # 0 does not reach 2 directly

def test_migration_snapshot_prevents_cascade():
    """With pre-populated islands, island 0 should not reach island 2 in one migrate()."""
    m = IslandModel(Config(n_islands=3, migration_ratio=1.0, elite_archive_size=10))
    m.islands[0].add(_p(code="i0", fitness=1.0))
    m.islands[1].add(_p(code="i1", fitness=0.5))
    m.migrate()
    # Island 2 should get island 1's original program (fitness 0.5), not island 0's (fitness 1.0)
    best2 = m.islands[2].best()
    assert best2 is not None and best2.fitness == 0.5
