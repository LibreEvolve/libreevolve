from libreevolve.plugins.causal import CausalPlugin
from libreevolve.population.program import Program
import math
import pytest

def _p(**kwargs):
    return Program(code="x=1", fitness=0.5, **kwargs)

def _p_with_diff(diff):
    return Program(code="x=1", fitness=0.5, metadata={"diff": diff})

def _p_with_diff_and_baseline(diff, *, parent_id="parent", parent_score=0.0):
    return Program(
        code="x=1",
        fitness=0.5,
        parent_id=parent_id,
        metadata={
            "diff": diff,
            "causal_reward_baseline": {
                "source": "parent_program",
                "parent_id": parent_id,
                "score": parent_score,
            },
        },
    )

def _p_with_full_payload(payload):
    return Program(
        code=payload,
        fitness=0.5,
        metadata={"diff": payload, "mutation_mode": "full"},
    )

def test_empty_context_before_history():
    assert CausalPlugin().build_extra_context(_p(), []) == ""

def test_score_passthrough():
    assert CausalPlugin().on_evaluated(_p(), 0.7) == 0.7

@pytest.mark.parametrize("score", [math.nan, math.inf, -math.inf, "1.0", True])
def test_rejects_non_finite_or_malformed_scores(score):
    c = CausalPlugin()

    with pytest.raises(ValueError, match="finite number"):
        c.on_evaluated(_p(), score)

    assert c._history == []
    assert c._total == 0
    assert not c._wins
    assert not c._counts

@pytest.mark.parametrize("history_limit", [0, -1, 1.5, True])
def test_rejects_invalid_history_limit(history_limit):
    with pytest.raises(ValueError, match="history_limit"):
        CausalPlugin(history_limit=history_limit)

def test_non_empty_context_after_history():
    p = CausalPlugin(); p.on_evaluated(_p(), 0.5)
    assert "CAUSAL" in p.build_extra_context(_p(), [])

def test_history_accumulates():
    p = CausalPlugin()
    for i in range(5): p.on_evaluated(_p(), i*0.1)
    assert len(p._history) == 5

def test_history_retention_is_bounded_and_reported():
    p = CausalPlugin(history_limit=3)
    for i in range(8):
        p.on_evaluated(_p(), i * 0.1)

    assert len(p._history) == 3
    assert [entry["score"] for entry in p._history] == pytest.approx([0.5, 0.6, 0.7])
    metadata = p.run_artifacts_metadata()
    assert metadata["history_limit"] == 3
    assert metadata["retained_history_entries"] == 3
    assert metadata["dropped_history_entries"] == 5
    assert metadata["total_evaluations"] == 8

def test_build_context_quarantines_malformed_restored_history():
    c = CausalPlugin()
    c._history = [
        {"factors": ["constants"], "delta": math.nan, "score": math.nan},
        {"factors": ["loop_structure"], "delta": 0.5, "score": 0.5},
        {"factors": "bad", "delta": 1.0, "score": 1.0},
    ]

    context = c.build_extra_context(_p(), [])

    assert "delta=+nan" not in context
    assert "Skipped malformed causal history entries: 2" in context
    assert c._history == [{"factors": ["loop_structure"], "delta": 0.5, "score": 0.5}]

def test_on_evaluated_ignores_malformed_restored_history_before_delta():
    c = CausalPlugin()
    c._history = [{"factors": ["constants"], "delta": math.inf, "score": math.inf}]

    c.on_evaluated(_p(), 0.4)

    assert c._history[-1]["delta"] == 0.4
    assert c._quarantined_history_entries == 1

def test_ucb1_returns_valid_factor():
    assert CausalPlugin()._ucb1_factor() in CausalPlugin.FACTORS

def test_factor_selector_uses_stable_pull_once_initialization():
    c = CausalPlugin()

    assert c._ucb1_factor() == "loop_structure"
    c._counts["loop_structure"] = 1
    assert c._ucb1_factor() == "data_types"
    c._counts["data_types"] = 1
    assert c._ucb1_factor() == "algorithm_choice"

def test_factor_selector_does_not_repeat_positive_reward_before_untried_factors():
    c = CausalPlugin()
    diff = "<<<SEARCH\nreturn 42\n===\nreturn 99\n>>>REPLACE"

    c.on_evaluated(_p_with_diff(diff), 0.8)
    context = c.build_extra_context(_p(), [])

    assert c._counts["constants"] == 1
    assert "Most promising dimension: loop_structure" in context

def test_factor_selector_uses_ucb_like_score_after_all_factors_tried():
    c = CausalPlugin()
    for factor in CausalPlugin.FACTORS:
        c._counts[factor] = 1
        c._wins[factor] = 0.0
    c._wins["algorithm_choice"] = 2.0
    c._total = len(CausalPlugin.FACTORS)

    assert c._ucb1_factor() == "algorithm_choice"

def test_factor_selection_policy_is_reported_in_artifact_metadata():
    metadata = CausalPlugin().run_artifacts_metadata()

    assert metadata["factor_selection_policy"] == "pull_once_then_ucb1_like"

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
    assert c._history[0]["baseline_source"] == "legacy_zero_initial_baseline"
    assert c._history[0]["mutation_evidence_status"] == "text"
    assert c._history[0]["mutation_mode"] == "diff"

def test_factor_credit_uses_parent_baseline_not_previous_evaluation_order():
    c = CausalPlugin()
    constants = "<<<SEARCH\nreturn 42\n===\nreturn 99\n>>>REPLACE"
    loop = "<<<SEARCH\nx = 1\n===\nfor i in range(10): x += i\n>>>REPLACE"

    c.on_evaluated(_p_with_diff_and_baseline(constants, parent_id="a", parent_score=0.0), 0.9)
    wins_before = dict(c._wins)
    c.on_evaluated(_p_with_diff_and_baseline(loop, parent_id="b", parent_score=0.3), 0.8)

    assert c._history[0]["delta"] == pytest.approx(0.9)
    assert c._history[0]["baseline_parent_id"] == "a"
    assert c._history[1]["delta"] == pytest.approx(0.5)
    assert c._history[1]["baseline_parent_id"] == "b"
    loop_factors = c._history[1]["factors"]
    assert "loop_structure" in loop_factors
    incremental_reward = sum(
        c._wins[factor] - wins_before.get(factor, 0.0) for factor in loop_factors
    )
    assert incremental_reward == pytest.approx(0.5)

def test_parent_regression_records_negative_delta_without_positive_factor_reward():
    c = CausalPlugin()
    diff = "<<<SEARCH\nreturn 42\n===\nreturn 99\n>>>REPLACE"

    c.on_evaluated(_p_with_diff_and_baseline(diff, parent_score=0.9), 0.4)

    assert c._history[0]["delta"] == pytest.approx(-0.5)
    assert c._history[0]["baseline_score"] == pytest.approx(0.9)
    assert c._wins["constants"] == 0.0
    assert c._counts["constants"] == 1

def test_metadata_parent_score_baseline_is_supported_for_direct_plugin_use():
    c = CausalPlugin()
    diff = "<<<SEARCH\nreturn 42\n===\nreturn 99\n>>>REPLACE"
    program = Program(
        code="x=1",
        fitness=0.5,
        parent_id="parent",
        metadata={"diff": diff, "parent_score": 0.25},
    )

    c.on_evaluated(program, 0.75)

    assert c._history[0]["delta"] == pytest.approx(0.5)
    assert c._history[0]["baseline_source"] == "metadata_parent_score"

def test_on_evaluated_detects_full_mode_algorithm_factor():
    c = CausalPlugin()

    c.on_evaluated(_p_with_full_payload("def solve(xs):\n    return sorted(xs)\n"), 0.8)

    assert "algorithm_choice" in c._history[0]["factors"]
    assert c._history[0]["mutation_evidence_status"] == "text"
    assert c._history[0]["mutation_mode"] == "full"

def test_detects_full_mode_helper_function_factor():
    c = CausalPlugin()

    factors = c._detect_factors(
        "def helper(x):\n    return x + 1\n",
        mutation_mode="full",
    )

    assert "helper_functions" in factors

@pytest.mark.parametrize("diff", [None, 7, {"patch": "bad"}, ["bad"]])
def test_on_evaluated_tolerates_non_text_mutation_evidence(diff):
    c = CausalPlugin()

    assert c.on_evaluated(_p_with_diff(diff), 0.4) == 0.4

    assert c._history[0]["factors"] == ["loop_structure"]
    assert c._history[0]["mutation_evidence_status"] == "non_text"
    assert c._history[0]["mutation_mode"] == "diff"
    assert c._malformed_mutation_evidence_entries == 1
    metadata = c.run_artifacts_metadata()
    assert metadata["malformed_mutation_evidence_entries"] == 1
    assert metadata["mutation_evidence_policy"] == "diff_parser_or_full_text_factor_scan"

def test_on_evaluated_records_missing_mutation_evidence_without_malformed_count():
    c = CausalPlugin()

    c.on_evaluated(_p(), 0.4)

    assert c._history[0]["factors"] == ["loop_structure"]
    assert c._history[0]["mutation_evidence_status"] == "missing"
    assert c.run_artifacts_metadata()["malformed_mutation_evidence_entries"] == 0

def test_credit_split_across_factors():
    diff = "<<<SEARCH\nx = 1\n===\nfor i in range(10): x = float(i)\n>>>REPLACE"
    c = CausalPlugin()
    c.on_evaluated(_p_with_diff(diff), 0.8)
    # With delta=0.8, reward should be split across detected factors
    n_factors = len(c._history[0]["factors"])
    total_credit = sum(c._wins[f] for f in c._history[0]["factors"])
    assert abs(total_credit - 0.8) < 1e-9
    assert n_factors >= 2
