from __future__ import annotations
import math, re
from collections import defaultdict
from libreevolve.core.diff import parse_diff_blocks
from libreevolve.plugins.base import PluginBase

# Heuristic patterns for classifying which code dimension a diff changed.
# Checked against tokens that differ between SEARCH and REPLACE blocks.
_FACTOR_PATTERNS: dict[str, re.Pattern] = {
    "loop_structure":   re.compile(r'\b(for|while|break|continue|range|enumerate)\b'),
    "data_types":       re.compile(r'\b(int|float|str|list|dict|set|tuple|bool|bytes|array)\b'
                                   r'|\.astype\b'),
    "constants":        re.compile(r'\b\d+\.?\d*\b|["\'][^"\']*["\']'),
    "helper_functions": re.compile(r'\bdef\s+\w+|\bclass\s+\w+|\blambda\b'),
    "algorithm_choice": re.compile(r'\b(import|sorted|\.sort\(|heapq|bisect|itertools'
                                   r'|collections|functools|math\.|numpy|np\.)\b'),
}


class CausalPlugin(PluginBase):
    """CausalEvolve-inspired MAB outcome-factor guidance.

    This is not the CausalEvolve causal scratchpad from the paper.
    Source: arXiv 2603.14575. Hooks: build_extra_context, on_evaluated.
    """
    FACTORS = ["loop_structure", "data_types", "algorithm_choice",
               "constants", "helper_functions"]

    def __init__(self, history_limit: int = 500):
        if isinstance(history_limit, bool) or not isinstance(history_limit, int) or history_limit <= 0:
            raise ValueError("history_limit must be a positive integer")
        self._history_limit = history_limit
        self._wins:   dict[str, float] = defaultdict(float)
        self._counts: dict[str, int]   = defaultdict(int)
        self._total = 0
        self._history: list[dict] = []
        self._quarantined_history_entries = 0
        self._dropped_history_entries = 0
        self._malformed_mutation_evidence_entries = 0

    def build_extra_context(self, parent, inspirations) -> str:
        self._quarantine_malformed_history()
        self._prune_history()
        if not self._history: return ""
        f = self._ucb1_factor()
        lines = "\n".join(f"  - Changed {h['factors']}: delta={h['delta']:+.4f}"
                         for h in self._history[-5:])
        if self._quarantined_history_entries:
            lines += (
                "\n  - Skipped malformed causal history entries: "
                f"{self._quarantined_history_entries}"
            )
        if self._malformed_mutation_evidence_entries:
            lines += (
                "\n  - Skipped malformed mutation evidence records: "
                f"{self._malformed_mutation_evidence_entries}"
            )
        return f"[CAUSAL GUIDANCE]\nMost promising dimension: {f}\nRecent outcomes:\n{lines}\n"

    def on_evaluated(self, program, score: float) -> float:
        score = self._validate_score(score)
        self._quarantine_malformed_history()
        baseline = self._baseline_score(program)
        delta = score - baseline["score"]
        diff_text, evidence_status = self._mutation_evidence(program)
        if evidence_status == "non_text":
            self._malformed_mutation_evidence_entries += 1
        mutation_mode = self._mutation_mode(program)
        factors = self._detect_factors(diff_text, mutation_mode=mutation_mode)
        reward = max(0.0, delta) / len(factors)
        for factor in factors:
            self._wins[factor] += reward
            self._counts[factor] += 1
        self._total += 1
        self._history.append(
            {
                "factors": factors,
                "delta": delta,
                "score": score,
                "baseline_score": baseline["score"],
                "baseline_source": baseline["source"],
                "baseline_parent_id": baseline.get("parent_id"),
                "mutation_evidence_status": evidence_status,
                "mutation_mode": mutation_mode,
            }
        )
        self._prune_history()
        return score

    def run_artifacts_metadata(self) -> dict:
        return {
            "plugin": self.__class__.__name__,
            "history_limit": self._history_limit,
            "retained_history_entries": len(self._history),
            "dropped_history_entries": self._dropped_history_entries,
            "quarantined_history_entries": self._quarantined_history_entries,
            "malformed_mutation_evidence_entries": self._malformed_mutation_evidence_entries,
            "total_evaluations": self._total,
            "retention_policy": "most_recent_history_entries",
            "mutation_evidence_policy": "diff_parser_or_full_text_factor_scan",
            "factor_reward_baseline_policy": (
                "parent_program_baseline_when_available_else_legacy_previous_history"
            ),
            "factor_selection_policy": "pull_once_then_ucb1_like",
        }

    def _baseline_score(self, program) -> dict:
        metadata = getattr(program, "metadata", {})
        if isinstance(metadata, dict):
            baseline = metadata.get("causal_reward_baseline")
            if isinstance(baseline, dict):
                value = baseline.get("score")
                if _finite_number(value):
                    source = baseline.get("source")
                    parent_id = baseline.get("parent_id")
                    return {
                        "score": float(value),
                        "source": source
                        if isinstance(source, str) and source
                        else "metadata_baseline",
                        "parent_id": parent_id if isinstance(parent_id, str) else None,
                    }
            parent_score = metadata.get("parent_score")
            if _finite_number(parent_score):
                return {
                    "score": float(parent_score),
                    "source": "metadata_parent_score",
                    "parent_id": getattr(program, "parent_id", None),
                }
        if self._history:
            return {
                "score": float(self._history[-1]["score"]),
                "source": "legacy_previous_history_score",
                "parent_id": None,
            }
        return {"score": 0.0, "source": "legacy_zero_initial_baseline", "parent_id": None}

    def _mutation_evidence(self, program) -> tuple[str, str]:
        metadata = getattr(program, "metadata", {})
        if not isinstance(metadata, dict) or "diff" not in metadata:
            return "", "missing"
        diff_text = metadata.get("diff")
        if isinstance(diff_text, str):
            return diff_text, "text"
        return "", "non_text"

    def _mutation_mode(self, program) -> str:
        metadata = getattr(program, "metadata", {})
        if isinstance(metadata, dict) and metadata.get("mutation_mode") == "full":
            return "full"
        return "diff"

    def _validate_score(self, score: object) -> float:
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise ValueError("CausalPlugin score must be a finite number")
        score_value = float(score)
        if not math.isfinite(score_value):
            raise ValueError("CausalPlugin score must be a finite number")
        return score_value

    def _quarantine_malformed_history(self) -> None:
        valid: list[dict] = []
        removed = 0
        for entry in self._history:
            if self._valid_history_entry(entry):
                valid.append(entry)
            else:
                removed += 1
        if removed:
            self._history = valid
            self._quarantined_history_entries += removed
            self._prune_history()

    def _prune_history(self) -> None:
        excess = len(self._history) - self._history_limit
        if excess <= 0:
            return
        del self._history[:excess]
        self._dropped_history_entries += excess

    def _valid_history_entry(self, entry: object) -> bool:
        if not isinstance(entry, dict):
            return False
        score = entry.get("score")
        delta = entry.get("delta")
        baseline_score = entry.get("baseline_score", 0.0)
        if (
            isinstance(score, bool)
            or isinstance(delta, bool)
            or isinstance(baseline_score, bool)
            or not isinstance(score, (int, float))
            or not isinstance(delta, (int, float))
            or not isinstance(baseline_score, (int, float))
            or not math.isfinite(float(score))
            or not math.isfinite(float(delta))
            or not math.isfinite(float(baseline_score))
        ):
            return False
        factors = entry.get("factors")
        return isinstance(factors, list) and all(
            isinstance(factor, str) for factor in factors
        )

    def _detect_factors(self, diff_text: str, mutation_mode: str = "diff") -> list[str]:
        """Classify which code dimensions a mutation changed.

        Diff-mode evidence compares tokens that differ between SEARCH and
        REPLACE blocks. Full-mode evidence scans the replacement payload
        directly because there is no old/new block boundary.
        """
        if mutation_mode == "full":
            return self._detect_factors_in_text(diff_text)
        blocks = parse_diff_blocks(diff_text)
        if not blocks:
            return [self.FACTORS[0]]
        factors: set[str] = set()
        for search, replace in blocks:
            old_tokens = re.findall(r'\S+', search)
            new_tokens = re.findall(r'\S+', replace)
            old_token_set = set(old_tokens)
            new_token_set = set(new_tokens)
            # Preserve token order so multi-token patterns like "def helper"
            # remain matchable after diff extraction.
            changed_tokens = [tok for tok in new_tokens if tok not in old_token_set]
            changed_tokens.extend(tok for tok in old_tokens if tok not in new_token_set)
            changed = " ".join(changed_tokens)
            for factor, pattern in _FACTOR_PATTERNS.items():
                if pattern.search(changed):
                    factors.add(factor)
        return sorted(factors) if factors else [self.FACTORS[0]]

    def _detect_factors_in_text(self, text: str) -> list[str]:
        factors = [
            factor for factor, pattern in _FACTOR_PATTERNS.items() if pattern.search(text)
        ]
        return sorted(factors) if factors else [self.FACTORS[0]]

    def _ucb1_factor(self) -> str:
        for factor in self.FACTORS:
            if self._counts[factor] == 0:
                return factor
        scores = [(self._wins[f]/max(self._counts[f],1)
                   + math.sqrt(math.log(max(self._total,1))/max(self._counts[f],1)), f)
                  for f in self.FACTORS]
        return max(scores)[1]


def _finite_number(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
    )
