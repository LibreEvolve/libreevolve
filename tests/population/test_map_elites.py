from libreevolve.population.map_elites import MAPElites
from libreevolve.population.program import Program

def _p(code="x=1", fitness=0.5): return Program(code=code, fitness=fitness)

def _pm(code="x=1", fitness=0.5, selection_score=0.5):
    return Program(code=code, fitness=fitness, metadata={"selection_score": selection_score})

def test_best_none_when_empty():
    assert MAPElites().best() is None

def test_add_and_best():
    a = MAPElites(); event = a.add(_p(fitness=0.7))
    assert a.best().fitness == 0.7
    assert event["admitted"] is True
    assert event["entered_cell"] is True
    assert event["reason"] == "empty_cell"
    assert event["cell"] is not None
    assert set(event["descriptors"]) == {"performance", "complexity", "diversity"}

def test_replacement_only_when_higher():
    a = MAPElites(bins=1)
    first = _p(code="x=1", fitness=0.3)
    a.add(first)
    second = _p(code="x=1", fitness=0.8)
    event = a.add(second)
    assert a._grid[(0, 0, 0)].fitness == 0.8
    assert event["cell_replaced"] is True
    assert event["previous_occupant_id"] == first.id

def test_lower_does_not_replace():
    a = MAPElites(bins=1)
    a.add(_p(code="x=1", fitness=0.8))
    event = a.add(_p(code="x=1", fitness=0.3))
    assert a._grid[(0, 0, 0)].fitness == 0.8
    assert event["entered_cell"] is False
    assert event["reason"] in {"elite_only", "not_improving_cell"}

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

def test_add_reports_elite_displacement():
    a = MAPElites(bins=1, elite_archive_size=1)
    low = _p(code="x=1", fitness=0.1)
    a.add(low)
    event = a.add(_p(code="x=2", fitness=0.9))
    assert event["entered_elite"] is True
    assert event["displaced_elite_ids"] == [low.id]

def test_diversity_no_crash_on_first():
    a = MAPElites()
    a.add(_p(code="def foo(): return 42", fitness=0.5))
    assert a.best() is not None

def test_performance_bounds_affect_cell():
    a = MAPElites(bins=10, perf_bounds=(0.0, 100.0))
    p = _p(fitness=50.0)
    assert a._cell(p)[0] == 5


def test_selection_score_drives_replacement_and_best():
    a = MAPElites(bins=1)
    primary_best = _pm(code="x=1", fitness=0.9, selection_score=0.2)
    a.add(primary_best)

    balanced = _pm(code="x=2", fitness=0.4, selection_score=0.8)
    event = a.add(balanced)

    assert event["cell_replaced"] is True
    assert event["selection_score"] == 0.8
    assert a.best().id == balanced.id
    assert a._grid[(0, 0, 0)].id == balanced.id
