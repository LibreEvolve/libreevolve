# Real-model validation protocol

Status: pending implementation completion and explicit aggregate spending cap.
No live requests have been made for this goal.

Use the installed candidate wheel on Windows Python 3.12. Select a currently
available OpenAI model using account evidence and record the official pricing
source and observation date. Do not use a placeholder model for live evidence.

Before starting, record the authorized aggregate dollar cap, allocated per-run
estimates, maximum attempts and tokens, timeout, model, and candidate wheel hash.
The local cost estimate uses configured pricing and reported tokens. A running
request can exceed a threshold, usage may be missing on failed requests, and
provider billing can differ. Use provider-side limits where available and keep
headroom; do not describe the local estimate as a hard spending guarantee.

Run three independently initialized experiments with framework seeds 17, 29,
and 43 and fresh run directories. Framework seeds do not promise deterministic
provider responses. Fix the evaluation corpus, config, model, output limit,
and proposal budget across all three. Retain a row for every initiated run,
including setup errors, provider errors, invalid proposals, and no improvement.

Independently reevaluate each exported candidate and the fixed baseline on the
same training and held-out corpora in fresh subprocesses. Do not feed held-out
results back into these three searches or tune the corpus after seeing outcomes.
Record code/evaluator hashes, correctness, bins/quality, provider usage, estimated
spend, duration, termination state, and every failed attempt. A calibration
control is clearly labelled and is never counted as model discovery.

Summarize all three results, improvement frequency, score range and individual
costs. Three trials are early evidence, not a broad statistical performance claim.
If none improves, investigate the example, evaluator or prompt and retain the
failed cohort before starting another authorized cohort.
