from unittest.mock import MagicMock
from libreevolve.llm.ensemble import LLMEnsemble

def _b(name="b", resp="<<<SEARCH\nfoo\n===\nbar\n>>>REPLACE"):
    m = MagicMock(); m.name = name; m.generate.return_value = resp; return m

def test_returns_tuple():
    diff, idx = LLMEnsemble([_b()]).generate("p")
    assert isinstance(diff, str) and idx == 0

def test_single_backend_always_idx0():
    b = _b(); ens = LLMEnsemble([b])
    assert all(ens.generate("p")[1] == 0 for _ in range(3))

def test_ucb1_explores_both_first():
    b1, b2 = _b("b1"), _b("b2")
    ens = LLMEnsemble([b1, b2])
    _, i1 = ens.generate("p"); _, i2 = ens.generate("p")
    assert {i1, i2} == {0, 1}

def test_record_reward_updates_wins():
    ens = LLMEnsemble([_b()]); ens.generate("p")
    ens.record_reward(0, 2.5)
    assert ens.wins[0] == 2.5

def test_ensemble_does_not_clamp():
    ens = LLMEnsemble([_b()]); ens.generate("p")
    ens.record_reward(0, -1.0)
    assert ens.wins[0] == -1.0

def test_counts_increment():
    ens = LLMEnsemble([_b()])
    assert ens.counts[0] == 0; ens.generate("p"); assert ens.counts[0] == 1

def test_high_reward_preferred_at_zero_explore():
    b1, b2 = _b("b1"), _b("b2")
    ens = LLMEnsemble([b1, b2], explore_coeff=0.0)
    ens.generate("p"); ens.generate("p")
    ens.record_reward(0, 10.0); ens.record_reward(1, 0.0)
    _, idx = ens.generate("p")
    assert idx == 0

def test_ucb1_converges_on_superior_arm():
    """After many rounds with arm 0 winning, arm 0 should be selected next."""
    b1, b2 = _b("b1"), _b("b2")
    ens = LLMEnsemble([b1, b2])
    # Warm up: explore both arms first
    ens.generate("p"); ens.generate("p")
    # Give arm 0 consistently high reward, arm 1 zero
    for _ in range(20):
        ens.record_reward(0, 1.0)
        ens.record_reward(1, 0.0)
    _, idx = ens.generate("p")
    assert idx == 0
