# `core/feedback.py` Characterization Gate

Status: `unverified` / not passed.

Existing tests cover scoring, weighted deltas, stages, objective metrics,
retention, invalid schemas/responses, duplicates, provider failures/retries,
discard, context/workspace/diagnostic caps, redaction, telemetry, invalid
candidates, and skipped graders. Before extraction, add or strengthen exact
grader order; repeated metadata behavior; all-feedback-skipped invalid
results; unsupported retention modes; non-string parser input; intent versus
score behavior; duplicate/unsorted context metadata; every cap boundary;
deterministic hashes excluding elapsed time; reward-failure cleanup; and
Windows paths, line endings, Unicode, and encoding.

Keep the public `build_critique_prompt`, `apply_llm_feedback`, and
`parse_feedback_response` contracts. Preserve the distinction between
feedback-adjusted fitness, evaluator validity, stage outputs, scheduler reward,
and retained/redacted text. No production movement is authorized until an
isolated pytest baseline and independent child review exist.
