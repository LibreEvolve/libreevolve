from libreevolve.plugins.causal import CausalPlugin
from libreevolve.population.program import Program

def _p(**kwargs):
    return Program(code="x=1", fitness=0.5, **kwargs)

def _p_with_diff(diff):
    return Program(code="x=1", fitness=0.5, metadata={"diff": diff})

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

# --- Factor detection tests ---

def test_detects_loop_structure():
    diff = "<<<SEARCH\nx = 1\n===\nfor i in range(10): x += i\n>>>REPLACE"
    c = CausalPlugin()
    factors = c._detect_factors(diff)
    assert "loop_structure" in factors

def test_detects_canonical_alphaevolve_diff_fences():
    diff = "<<<<<<< SEARCH\nx = 1\n=======\nfor i in range(10): x += i\n>>>>>>> REPLACE"
    c = CausalPlugin()
    factors = c._detect_factors(diff)
    assert "loop_structure" in factors

def test_detects_mixed_compact_and_canonical_diff_blocks():
    diff = (
        "<<<SEARCH\nreturn 42\n===\nreturn 99\n>>>REPLACE\n"
        "<<<<<<< SEARCH\nx = []\n=======\nx = dict()\n>>>>>>> REPLACE"
    )
    c = CausalPlugin()
    factors = c._detect_factors(diff)
    assert "constants" in factors
    assert "data_types" in factors

def test_detects_constants():
    diff = "<<<SEARCH\nreturn 42\n===\nreturn 99\n>>>REPLACE"
    c = CausalPlugin()
    factors = c._detect_factors(diff)
    assert "constants" in factors

def test_detects_helper_functions():
    diff = "<<<SEARCH\npass\n===\ndef helper(n): return n*2\n>>>REPLACE"
    c = CausalPlugin()
    factors = c._detect_factors(diff)
    assert "helper_functions" in factors

def test_detects_data_types():
    diff = "<<<SEARCH\nx = []\n===\nx = dict()\n>>>REPLACE"
    c = CausalPlugin()
    factors = c._detect_factors(diff)
    assert "data_types" in factors

def test_detects_algorithm_choice():
    diff = "<<<SEARCH\nresult = my_sort(lst)\n===\nresult = sorted(lst)\n>>>REPLACE"
    c = CausalPlugin()
    factors = c._detect_factors(diff)
    assert "algorithm_choice" in factors

def test_fallback_on_empty_diff():
    c = CausalPlugin()
    factors = c._detect_factors("")
    assert factors == ["loop_structure"]

def test_multi_factor_detection():
    diff = "<<<SEARCH\nx = 1\n===\nfor i in range(10): x = float(i)\n>>>REPLACE"
    c = CausalPlugin()
    factors = c._detect_factors(diff)
    assert len(factors) >= 2  # at least loop_structure and data_types

def test_on_evaluated_uses_diff_metadata():
    diff = "<<<SEARCH\nreturn 42\n===\nreturn 99\n>>>REPLACE"
    c = CausalPlugin()
    c.on_evaluated(_p_with_diff(diff), 0.8)
    assert c._history[0]["factors"] == ["constants"]

def test_credit_split_across_factors():
    diff = "<<<SEARCH\nx = 1\n===\nfor i in range(10): x = float(i)\n>>>REPLACE"
    c = CausalPlugin()
    c.on_evaluated(_p_with_diff(diff), 0.8)
    # With delta=0.8, reward should be split across detected factors
    n_factors = len(c._history[0]["factors"])
    total_credit = sum(c._wins[f] for f in c._history[0]["factors"])
    assert abs(total_credit - 0.8) < 1e-9
    assert n_factors >= 2
