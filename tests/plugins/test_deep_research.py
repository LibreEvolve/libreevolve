from unittest.mock import MagicMock
from alphaevolve.plugins.deep_research import DeepResearchPlugin
from alphaevolve.population.program import Program

def _p(): return Program(code="x=1", fitness=0.5)

def test_empty_before_search():
    assert DeepResearchPlugin().build_extra_context(_p(), []) == ""

def test_calls_at_multiples_of_10():
    calls = []
    plugin = DeepResearchPlugin(search_fn=lambda q: (calls.append(q) or "r"))
    db = MagicMock(); db.best.return_value = _p()
    plugin.on_generation_start(0, db)
    plugin.on_generation_start(5, db)
    plugin.on_generation_start(10, db)
    assert len(calls) == 2

def test_context_shows_synthesis():
    plugin = DeepResearchPlugin(search_fn=lambda q: "test synthesis")
    db = MagicMock(); db.best.return_value = _p()
    plugin.on_generation_start(0, db)
    ctx = plugin.build_extra_context(_p(), [])
    assert "DEEP RESEARCH" in ctx and "test synthesis" in ctx

def test_default_search_returns_none():
    assert DeepResearchPlugin()._default_search("q") is None
