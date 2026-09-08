"""Deterministic calibration, not evidence of evolved heuristic discovery."""

import importlib.util
from pathlib import Path
import random

import pytest


EXAMPLE = Path(__file__).resolve().parents[1] / "libreevolve/problems/examples/bin_packing"
SPEC = importlib.util.spec_from_file_location("alpha_bin_packing", EXAMPLE / "validate.py")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
BASELINE = (EXAMPLE / "initial_programs/seed.py").read_text(encoding="utf-8")
INVALID = {"quality": 0.0, "is_valid": False, "total_bins": 0,
           "lower_bound_bins": 0, "case_count": 0}
FFD = '''
def pack(items, capacity):
    items.sort(reverse=True)
    bins, loads = [], []
    for item in items:
        for i, load in enumerate(loads):
            if load + item <= capacity:
                bins[i].append(item)
                loads[i] += item
                break
        else:
            bins.append([item])
            loads.append(item)
    return bins
'''


@pytest.mark.parametrize("evaluate,count", [(validator.evaluate, 55),
                                            (validator.evaluate_holdout, 30)])
def test_baseline_and_decreasing_calibration(evaluate, count):
    baseline = evaluate(BASELINE)
    improved = evaluate(FFD)
    assert baseline["is_valid"] and improved["is_valid"]
    assert 0 < baseline["quality"] < improved["quality"] <= 1
    assert improved["total_bins"] < baseline["total_bins"]
    assert baseline["case_count"] == count
    assert baseline["quality"] == baseline["lower_bound_bins"] / baseline["total_bins"]
    assert baseline == evaluate(BASELINE)
    assert improved == evaluate(FFD)


@pytest.mark.parametrize("body", [
    "return []",  # Dropped items.
    "items.clear(); return []",  # Mutation cannot erase expected multiplicities.
    "return [items] if items else []",  # Capacity overflow.
    "return [[x] for x in set(items)]",  # Deduplicated items.
    "return [[x] for x in items + items]",  # Duplicated items.
    "return [[float(x)] for x in items]",
    "return [[True] for x in items]",
    "return tuple([x] for x in items)",
    "return [(x,) for x in items]",
    "return ([x] for x in items)",
    "return [[]] + [[x] for x in items]",
    "return [[0]] + [[x] for x in items]",
    "return [[-1]] + [[x] for x in items]",
    "return [[capacity + 1]]",
    "raise RuntimeError('bad candidate')",
    "raise SystemExit(0)",
])
@pytest.mark.parametrize("evaluate", [validator.evaluate, validator.evaluate_holdout])
def test_invalid_outputs_fail(body, evaluate):
    assert evaluate("def pack(items, capacity):\n    " + body) == INVALID


@pytest.mark.parametrize("code", ["not python!", "pack = 7", "", "raise SystemExit(0)"])
def test_invalid_module_fails(code):
    assert validator.evaluate(code) == INVALID


def test_consuming_input_is_allowed():
    code = '''
def pack(items, capacity):
    bins = []
    while items:
        bins.append([items.pop()])
    return bins
'''
    assert validator.evaluate(code)["is_valid"]
    assert validator.evaluate_holdout(code)["is_valid"]


def test_holdout_is_separate(monkeypatch):
    def forbidden():
        pytest.fail("search touched holdout")
    monkeypatch.setattr(validator, "holdout_cases", forbidden)
    assert validator.evaluate(BASELINE)["is_valid"]


def test_holdout_does_not_evaluate_training(monkeypatch):
    def forbidden():
        pytest.fail("holdout touched training")
    monkeypatch.setattr(validator, "training_cases", forbidden)
    assert validator.evaluate_holdout(BASELINE)["is_valid"]


def test_corpus_determinism_and_input_contract():
    state = random.getstate()
    training, heldout = validator.training_cases(), validator.holdout_cases()
    assert training == validator.training_cases()
    assert heldout == validator.holdout_cases()
    assert random.getstate() == state
    assert not set(training).intersection(heldout)
    for items, capacity in training + heldout:
        assert type(items) is tuple
        assert type(capacity) is int and capacity > 0
        assert all(type(x) is int and 0 < x <= capacity for x in items)
    assert {p.name for p in (EXAMPLE / "initial_programs").glob("*.py")} == {"seed.py"}


def test_exact_multiplicity_and_type_validation():
    assert validator._valid_packing([[2, 2], [3]], (2, 2, 3), 4)
    assert not validator._valid_packing([[2], [3, 3]], (2, 2, 3), 6)
    assert not validator._valid_packing([[True]], (1,), 1)
    assert not validator._valid_packing([[1.0]], (1,), 1)
    assert validator._valid_packing([], (), 1)
    assert not validator._valid_packing([[]], (), 1)


def test_example_loads_with_quality_metric():
    from libreevolve.problems.loader import load_problem

    problem = load_problem(EXAMPLE)
    assert problem.primary_metric == "quality"
    assert problem.primary_bounds == (0.0, 1.0)


def test_real_evaluator_pipeline_baseline_and_calibration():
    from libreevolve.core.evaluator import CascadeEvaluator
    from libreevolve.problems.loader import load_problem

    evaluator = CascadeEvaluator(load_problem(EXAMPLE))
    baseline = evaluator.evaluate(BASELINE, diff_error=None)
    assert baseline.is_valid, (baseline.error, baseline.metadata, baseline.stderr)
    assert baseline.error is None
    assert baseline.metrics == validator.evaluate(BASELINE)
    assert baseline.fitness == pytest.approx(baseline.metrics["quality"])
    assert baseline.fitness > 0
    improved = evaluator.evaluate(FFD, diff_error=None)
    assert improved.is_valid, (improved.error, improved.metadata, improved.stderr)
    assert improved.fitness > baseline.fitness
    invalid = evaluator.evaluate("def pack(items, capacity): return []", diff_error=None)
    assert not invalid.is_valid
    assert invalid.error == "domain_invalid"
    assert "malformed_metrics" not in invalid.metadata
    assert invalid.metrics == INVALID
