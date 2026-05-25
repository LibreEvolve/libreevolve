from libreevolve.population.map_elites import MAPElites
from libreevolve.population.program import Program

def _p(code="x=1", fitness=0.5): return Program(code=code, fitness=fitness)

def test_best_none_when_empty():
    assert MAPElites().best() is None

def test_add_and_best():
    a = MAPElites(); a.add(_p(fitness=0.7))
    assert a.best().fitness == 0.7

def test_replacement_only_when_higher():
    a = MAPElites(bins=1)
    a.add(_p(code="x=1", fitness=0.3))
    a.add(_p(code="x=1", fitness=0.8))
    assert a._grid[(0, 0, 0)].fitness == 0.8

def test_lower_does_not_replace():
    a = MAPElites(bins=1)
    a.add(_p(code="x=1", fitness=0.8))
    a.add(_p(code="x=1", fitness=0.3))
    assert a._grid[(0, 0, 0)].fitness == 0.8

def test_occupied_cells_nonempty():
    a = MAPElites(); a.add(_p())
    assert len(a.occupied_cells()) >= 1

def test_sample_diverse_up_to_k():
    a = MAPElites()
    for i in range(5): a.add(_p(code=f"x={i}", fitness=i*0.1))
    assert 1 <= len(a.sample_diverse(k=3)) <= 3

def test_sample_diverse_excludes_program_ids():
    a = MAPElites()
    p = _p(code="x=1", fitness=0.5)
    a.add(p)
    assert a.sample_diverse(k=3, exclude_ids={p.id}) == []

def test_elite_archive_capped():
    a = MAPElites(elite_archive_size=3)
    for i in range(10): a.add(_p(code=f"x={i}", fitness=i*0.1))
    assert len(a.elite_archive()) <= 3

def test_diversity_no_crash_on_first():
    a = MAPElites()
    a.add(_p(code="def foo(): return 42", fitness=0.5))
    assert a.best() is not None

def test_performance_bounds_affect_cell():
    a = MAPElites(bins=10, perf_bounds=(0.0, 100.0))
    p = _p(fitness=50.0)
    assert a._cell(p)[0] == 5
