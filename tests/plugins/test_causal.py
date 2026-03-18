from alphaevolve.plugins.causal import CausalPlugin
from alphaevolve.population.program import Program

def _p(): return Program(code="x=1", fitness=0.5)

def test_empty_context_before_history():
    assert CausalPlugin().build_extra_context(_p(), []) == ""

def test_score_passthrough():
    assert CausalPlugin().on_evaluated(_p(), 0.7) == 0.7

def test_non_empty_context_after_history():
    p = CausalPlugin(); p.on_evaluated(_p(), 0.5)
    assert "CAUSAL" in p.build_extra_context(_p(), [])

def test_history_accumulates():
    p = CausalPlugin()
    for i in range(5): p.on_evaluated(_p(), i*0.1)
    assert len(p._history) == 5

def test_ucb1_returns_valid_factor():
    assert CausalPlugin()._ucb1_factor() in CausalPlugin.FACTORS
