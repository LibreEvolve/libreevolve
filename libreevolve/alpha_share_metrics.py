"""Pure, bounded metric admission and comparison for public result records.

No candidate loading, verification, filesystem access or network access occurs
here. Corpus identifiers describe supplied evidence, not authenticated truth.
Record-specific publication approval is a separate outer boundary.
"""

from __future__ import annotations

import math
import re


MAX_COUNT = 2**53 - 1
METRIC_KEYS = frozenset({
    "corpus_id", "corpus_sha256", "split", "case_count", "valid",
    "total_bins", "quality",
})


def admit_metrics(value: object) -> dict | None:
    """Return an allowlisted copy, rejecting malformed rather than coercing data."""
    if value is None:
        return None
    if type(value) is not dict or value.keys() != METRIC_KEYS:
        raise ValueError("metrics require exactly the version-1 metric fields")
    corpus = value["corpus_id"]
    if type(corpus) is not str or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", corpus) is None:
        raise ValueError("corpus_id must be a bounded public identifier, not a path")
    digest = value["corpus_sha256"]
    if type(digest) is not str or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise ValueError("corpus_sha256 must identify the exact corpus bytes")
    if type(value["split"]) is not str or value["split"] not in {"training", "holdout"}:
        raise ValueError("split must be training or holdout")
    valid = value["valid"]
    if valid is not None and type(valid) is not bool:
        raise ValueError("valid must be true, false or null")
    for key in ("case_count", "total_bins"):
        number = value[key]
        if number is not None and (type(number) is not int or not 0 <= number <= MAX_COUNT):
            raise ValueError(f"{key} must be a bounded nonnegative integer or null")
    quality = value["quality"]
    if quality is not None:
        if type(quality) not in (int, float) or not 0 <= quality <= 1 or not math.isfinite(quality):
            raise ValueError("quality must be finite, between zero and one, or null")
    # Explicit construction prevents future internal fields from leaking out.
    return {key: value[key] for key in sorted(METRIC_KEYS)}


def compare_metrics(baseline: object, candidate: object) -> dict:
    """Derive candidate outcome; run completion must remain a separate field.

    A valid candidate after cancellation can still have a measured comparison.
    Invalid placeholders, missing data and incompatible corpora never become
    an improvement. Negative reduction is retained rather than clamped to zero.
    """
    before, after = admit_metrics(baseline), admit_metrics(candidate)

    def result(outcome, reason, reduction=None):
        return {"outcome": outcome, "comparison_reason": reason,
                "bin_reduction_percent": reduction}

    if after is None:
        return result("incomplete", "candidate_missing")
    if after["valid"] is False:
        return result("invalid", "candidate_invalid")
    if after["valid"] is None:
        return result("unknown", "candidate_validity_unknown")
    if before is None:
        return result("unknown", "baseline_missing")
    if before["valid"] is not True:
        return result("unknown", "baseline_not_valid")
    if any(before[key] != after[key] for key in ("corpus_id", "corpus_sha256", "split")):
        return result("unknown", "corpus_or_split_mismatch")
    if before["case_count"] is None or after["case_count"] is None:
        return result("unknown", "case_count_unknown")
    if before["case_count"] != after["case_count"]:
        return result("unknown", "case_count_mismatch")
    if before["case_count"] == 0:
        return result("unknown", "empty_corpus")
    if before["total_bins"] is None or after["total_bins"] is None:
        return result("unknown", "bin_count_unknown")
    if before["total_bins"] == 0:
        return result("unknown", "zero_baseline")
    if after["total_bins"] == 0:
        return result("unknown", "inconsistent_zero_candidate")
    change = before["total_bins"] - after["total_bins"]
    outcome = "improved" if change > 0 else "worse" if change < 0 else "unchanged"
    return result(outcome, "valid_same_corpus", change / before["total_bins"] * 100)
