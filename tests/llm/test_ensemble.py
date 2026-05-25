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


def test_generate_records_normalized_call_telemetry():
    ens = LLMEnsemble(
        [_b("b1", "answer")],
        backend_metadata=[{"cost": 2.0, "latency": 3.0, "depth": 4.0, "role": "breadth"}],
    )

    response, idx = ens.generate("prompt text", role="mutation")

    assert response == "answer"
    assert idx == 0
    assert len(ens.call_history) == 1
    record = ens.call_history[0]
    assert record["role"] == "mutation"
    assert record["backend_idx"] == 0
    assert record["backend_name"] == "b1"
    assert record["backend_metadata"]["role"] == "breadth"
    assert record["status"] == "ok"
    assert record["prompt_chars"] == len("prompt text")
    assert record["output_chars"] == len("answer")
    assert len(record["prompt_sha256"]) == 64
    assert len(record["output_sha256"]) == 64
    assert record["usage"] is None
    assert record["counts_before"] == [0]
    assert record["counts_after"] == [1]


def test_generate_records_failed_call_before_reraising():
    backend = _b("b1")
    backend.generate.side_effect = RuntimeError("provider down")
    ens = LLMEnsemble([backend])

    try:
        ens.generate("prompt text", role="mutation")
    except RuntimeError:
        pass

    assert ens.counts[0] == 0
    assert ens.call_history[-1]["status"] == "error"
    assert ens.call_history[-1]["error_type"] == "RuntimeError"
    assert "provider down" in ens.call_history[-1]["error"]


def test_generate_retries_same_backend_before_success():
    backend = _b("b1")
    backend.generate.side_effect = [RuntimeError("rate limit"), "ok"]
    ens = LLMEnsemble([backend], max_retries=1)

    response, idx = ens.generate("prompt text", role="mutation")

    assert response == "ok"
    assert idx == 0
    assert backend.generate.call_count == 2
    assert ens.counts == [1]
    assert ens.call_history[0]["status"] == "error"
    assert ens.call_history[0]["retry_attempt"] == 0
    assert ens.call_history[0]["will_retry"] is True
    assert ens.call_history[1]["status"] == "ok"
    assert ens.call_history[1]["retry_attempt"] == 1


def test_generate_falls_back_to_next_backend_after_failure():
    bad = _b("bad")
    good = _b("good", "fallback")
    bad.generate.side_effect = RuntimeError("provider down")
    ens = LLMEnsemble([bad, good], max_retries=0, fallback=True)

    response, idx = ens.generate("prompt text", role="mutation")

    assert response == "fallback"
    assert idx == 1
    assert ens.counts == [0, 1]
    assert ens.call_history[0]["backend_idx"] == 0
    assert ens.call_history[0]["status"] == "error"
    assert ens.call_history[0]["will_fallback"] is True
    assert ens.call_history[1]["backend_idx"] == 1
    assert ens.call_history[1]["status"] == "ok"
    assert ens.call_history[1]["fallback_attempt"] == 1


def test_generate_can_disable_fallback():
    bad = _b("bad")
    good = _b("good", "fallback")
    bad.generate.side_effect = RuntimeError("provider down")
    ens = LLMEnsemble([bad, good], max_retries=0, fallback=False)

    try:
        ens.generate("prompt text", role="mutation")
    except RuntimeError:
        pass

    assert bad.generate.call_count == 1
    assert good.generate.call_count == 0
    assert ens.call_history[-1]["will_fallback"] is False


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

def test_throughput_depth_strategy_uses_metadata():
    fast = _b("fast")
    deep = _b("deep")
    ens = LLMEnsemble(
        [fast, deep],
        explore_coeff=0.0,
        strategy="throughput_depth",
        backend_metadata=[
            {"cost": 1.0, "latency": 1.0, "depth": 1.0},
            {"cost": 1.0, "latency": 1.0, "depth": 5.0},
        ],
    )

    _, idx = ens.generate("p")

    assert idx == 1
