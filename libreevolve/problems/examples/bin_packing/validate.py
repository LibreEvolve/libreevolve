"""Deterministic packing checks, executed in the engine's local subprocess.

Direct calls execute candidate code in the caller. Neither path is a
hostile-code security sandbox. Holdout is an explicit reporting-only API.
"""

from collections import Counter
from random import Random


def training_cases() -> tuple:
    """Immutable (items, capacity) cases; no global random state changes."""
    cases = [
        ((), 10), ((1,), 1), ((10,), 10), ((1,) * 25, 10),
        ((6, 6, 4, 4) * 8, 10), ((2, 5, 4, 7, 1, 3, 8), 10),
        ((7,) * 17, 10), ((5,) * 19, 10),
        (tuple(range(1, 21)), 20), (tuple(range(20, 0, -1)), 20),
    ]
    rng = Random(1729)
    for capacity in (10, 31, 100):
        for size in (16, 48, 96):
            uniform = [rng.randint(1, capacity) for _ in range(size)]
            small = [rng.randint(1, max(1, capacity // 4)) for _ in range(size)]
            pairs = [rng.randint(1, capacity - 1) for _ in range(size // 2)]
            paired = pairs + [capacity - x for x in pairs]
            rng.shuffle(paired)
            cases.extend((tuple(values), capacity) for values in
                         (uniform, sorted(uniform), sorted(uniform, reverse=True),
                          small, paired))
    return tuple(cases)


def holdout_cases() -> tuple:
    """Distinct seeds, capacities and distributions; never called by evaluate."""
    cases = [((), 17), ((17,) * 9, 17), ((9, 9, 8, 8) * 11, 17)]
    rng = Random(8675309)
    for capacity in (17, 53, 127):
        for size in (23, 61, 113):
            # Bimodal, near-half, and discrete repeated-size workloads.
            bimodal = [rng.choice((rng.randint(1, capacity // 5),
                                   rng.randint(4 * capacity // 5, capacity)))
                       for _ in range(size)]
            near_half = [capacity // 2 + rng.choice((-1, 0, 1, 2))
                         for _ in range(size)]
            repeated = [rng.choice((1, capacity // 3, capacity // 2, capacity))
                        for _ in range(size)]
            cases.extend((tuple(values), capacity)
                         for values in (bimodal, near_half, repeated))
    return tuple(cases)


def _valid_packing(result, original, capacity):
    if type(result) is not list:
        return False
    observed = Counter()
    for bin_items in result:
        if type(bin_items) is not list or not bin_items:
            return False
        if any(type(item) is not int or item <= 0 or item > capacity
               for item in bin_items):
            return False
        if sum(bin_items) > capacity:
            return False
        observed.update(bin_items)
    return observed == Counter(original)


def _evaluate(code, cases):
    invalid = {"quality": 0.0, "is_valid": False, "total_bins": 0,
               "lower_bound_bins": 0, "case_count": 0}
    namespace = {}
    try:
        exec(compile(code, "<candidate>", "exec"), namespace)  # noqa: S102
        pack = namespace.get("pack")
        if not callable(pack):
            return invalid
        total_bins = 0
        lower_bound = 0
        for original, capacity in cases:
            # Never derive the expected items from the candidate's mutable input.
            result = pack(list(original), capacity)
            if not _valid_packing(result, original, capacity):
                return invalid
            total_bins += len(result)
            lower_bound += (sum(original) + capacity - 1) // capacity
    except BaseException:
        # Includes candidate SystemExit; external engine timeout bounds hangs.
        return invalid
    return {"quality": lower_bound / total_bins if total_bins else 1.0,
            "is_valid": True, "total_bins": total_bins,
            "lower_bound_bins": lower_bound, "case_count": len(cases)}


def evaluate(code: str) -> dict:
    """Search entry point: training only, with no holdout metrics."""
    return _evaluate(code, training_cases())


def evaluate_holdout(code: str) -> dict:
    """Explicit post-search reporting on a frozen candidate; never search fitness."""
    return _evaluate(code, holdout_cases())
