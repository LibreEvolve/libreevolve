from math import inf
from alphaevolve.population.program import Program

def test_default_fitness_is_neg_inf():
    assert Program().fitness == -inf

def test_unique_ids():
    assert Program().id != Program().id

def test_fields_set():
    p = Program(code="x = 1", fitness=0.5)
    assert p.code == "x = 1" and p.fitness == 0.5

def test_lineage_defaults_empty():
    assert Program().lineage == []

def test_metadata_defaults_empty():
    assert Program().metadata == {}
