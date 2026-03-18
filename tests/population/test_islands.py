from alphaevolve.core.config import Config
from alphaevolve.population.islands import IslandModel
from alphaevolve.population.program import Program

def _m(n=3): return IslandModel(Config(n_islands=n, migration_interval=5))
def _p(code="x=1", fitness=0.5): return Program(code=code, fitness=fitness)

def test_best_returns_highest():
    m = _m(); m.add(_p(fitness=0.3)); m.add(_p(fitness=0.7))
    assert m.best().fitness == 0.7

def test_sample_exploit_returns_best():
    m = _m(); m.add(_p(fitness=0.3)); m.add(_p(fitness=0.9))
    assert m.sample("exploit").fitness == 0.9

def test_migration_copies_not_moves():
    m = IslandModel(Config(n_islands=2, migration_ratio=1.0, elite_archive_size=10))
    m.islands[0].add(_p(fitness=1.0))
    before = len(m.islands[0].occupied_cells())
    m.migrate()
    assert len(m.islands[0].occupied_cells()) == before
    assert m.islands[1].best() is not None

def test_sample_diverse_returns_list():
    m = _m()
    for i in range(5): m.add(_p(code=f"x={i}", fitness=i*0.1))
    samples = m.sample_diverse(k=3)
    assert isinstance(samples, list) and len(samples) <= 3

def test_ring_topology():
    m = IslandModel(Config(n_islands=3, migration_ratio=1.0, elite_archive_size=10))
    m.islands[0].add(_p(code="i0", fitness=1.0))
    m.migrate()
    assert m.islands[1].best() is not None
    assert m.islands[2].best() is None  # 0 does not reach 2 directly
