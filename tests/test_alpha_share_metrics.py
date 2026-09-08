"""Synthetic metric fixtures: never presented as real optimization results."""

from copy import deepcopy

import pytest

from libreevolve.alpha_share_metrics import MAX_COUNT, admit_metrics, compare_metrics


def metric(**changes):
    value = dict(corpus_id="synthetic-corpus", corpus_sha256="a" * 64,
                 split="training", case_count=4, valid=True, total_bins=10, quality=0.8)
    return dict(value, **changes)


@pytest.mark.parametrize("bins,outcome,reduction", [(8, "improved", 20), (10, "unchanged", 0), (12, "worse", -20)])
def test_valid_comparisons(bins, outcome, reduction):
    result = compare_metrics(metric(), metric(total_bins=bins))
    assert result == dict(outcome=outcome, comparison_reason="valid_same_corpus", bin_reduction_percent=reduction)


@pytest.mark.parametrize("before,after,reason,outcome", [
    (metric(), None, "candidate_missing", "incomplete"),
    (metric(), metric(valid=False, total_bins=0), "candidate_invalid", "invalid"),
    (metric(), metric(valid=None), "candidate_validity_unknown", "unknown"),
    (None, metric(), "baseline_missing", "unknown"),
    (metric(valid=False), metric(), "baseline_not_valid", "unknown"),
    (metric(), metric(split="holdout"), "corpus_or_split_mismatch", "unknown"),
    (metric(), metric(corpus_sha256="b" * 64), "corpus_or_split_mismatch", "unknown"),
    (metric(), metric(corpus_id="different"), "corpus_or_split_mismatch", "unknown"),
    (metric(case_count=None), metric(), "case_count_unknown", "unknown"),
    (metric(), metric(case_count=3), "case_count_mismatch", "unknown"),
    (metric(case_count=0), metric(case_count=0), "empty_corpus", "unknown"),
    (metric(), metric(total_bins=None), "bin_count_unknown", "unknown"),
    (metric(total_bins=0), metric(), "zero_baseline", "unknown"),
    (metric(), metric(total_bins=0), "inconsistent_zero_candidate", "unknown"),
])
def test_noncomparisons_never_invent_a_percentage(before, after, reason, outcome):
    assert compare_metrics(before, after) == dict(outcome=outcome, comparison_reason=reason, bin_reduction_percent=None)


@pytest.mark.parametrize("field,value", [
    ("valid", 1), ("valid", "true"), ("split", []), ("split", "test"),
    ("case_count", True), ("case_count", -1), ("case_count", 1.2),
    ("total_bins", False), ("total_bins", MAX_COUNT + 1),
    ("quality", float("nan")), ("quality", float("inf")),
    ("quality", True), ("quality", -0.1), ("quality", 2),
    ("quality", 10**500), ("corpus_id", "../private"),
    ("corpus_id", "<script>"), ("corpus_id", "x" * 81),
    ("corpus_sha256", "not-a-hash"),
])
def test_malformed_fields_are_rejected(field, value):
    with pytest.raises(ValueError):
        admit_metrics(metric(**{field: value}))


def test_allowlist_and_copy():
    value = metric()
    original = deepcopy(value)
    assert admit_metrics(value) == original
    assert admit_metrics(value) is not value
    assert value == original
    with pytest.raises(ValueError):
        admit_metrics(dict(value, source="private code"))
    del value["valid"]
    with pytest.raises(ValueError):
        admit_metrics(value)
