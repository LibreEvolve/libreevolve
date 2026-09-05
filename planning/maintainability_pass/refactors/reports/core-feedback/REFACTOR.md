# core/feedback.py refactor decision

## Decision

Evidence state: focused compatibility evidence is current; no production
writer is authorized for this lane.

The lane has a completed characterization report and coupling review. The
safe future direction remains a narrow, pure `feedback_boundary.py` projection
for bounded and redacted diagnostic/context records, but that seam is deferred
until the retention-policy documentation mismatch is reconciled and a future
writer receives an explicit boundary handoff. The prompt-import blocker was
repaired in the owning prompt lane; this lane makes no production change.

## Scope and current evidence

The primary module is approximately 1,312 lines with 52 functions. The
`apply_llm_feedback` path is approximately 238 lines with a branch/decision
complexity proxy of 221. These are source-derived measurements from
`INVENTORY.md`, not a claim that a line-count reduction alone would improve
correctness.

The module currently combines feedback parsing and normalization, diagnostic
rendering, truncation and redaction, evaluator-facing context, grader/provider
calls, retry and failure policy, metric/fitness mutation, and compatibility
handling. The characterization specialist added focused cases for ordering,
partial evaluator/plugin diagnostics, Unicode truncation, retention modes,
malformed payloads, and local history/failure JSONL round trips.

Current focused compatibility evidence, test-derived and run with Windows
Python 3.12, is:

```text
 /mnt/c/Windows/py.exe -3.12 -m pytest \
  tests/core/test_prompt.py tests/core/test_prompt_characterization.py \
  tests/core/test_jsonl.py tests/core/test_artifact_schema_characterization.py \
  tests/core/test_feedback.py tests/core/test_meta_prompt.py --tb=short
655 passed
```

This combined run replaces the earlier isolated `84 passed, 1 failed` result
and its prompt-import diagnosis as current evidence. The earlier failure is
retained only as repair history. The 655-test result is focused compatibility
evidence, not evidence that the full repository suite or a live runtime path
has passed.

## Safe future seam

After the blocker is repaired and the focused baseline is green, a future
writer may evaluate a pure `feedback_boundary.py` module that projects
bounded, redacted values and diagnostics. Candidate responsibilities are:

- deterministic bounded/redacted feedback context records;
- safe JSON-compatible diagnostic normalization;
- telemetry normalization, hashing, and truncation; and
- value-only rendering helpers whose inputs and outputs are explicit records.

The seam must remain side-effect free and must not own evaluator execution,
prompt assembly, LLM/provider calls, persistence, plugin hooks, scheduler
rewards, or candidate admission. It must not become a second source of
metric authority or a second retention-policy implementation.

## Contracts that must not move

The following ownership and ordering rules are source-derived from the
coupling review and are acceptance constraints for any future writer:

- Evaluator metric validation remains authoritative in
  `evaluator.py:_validate_metrics`; raw fitness remains owned by
  `Problem.fitness_from_metrics` in `problems/loader.py`. Feedback may apply
  its existing mutation of metrics, fitness, and validity only at the existing
  point, before plugin scoring.
- Synchronous and asynchronous loop commit paths must both retain the same
  feedback call and ordering. A boundary helper must not run feedback in a
  worker or alter the ordering relative to evaluator completion, admission,
  or plugin hooks.
- Grader/provider calls, including the `feedback:<grader>` role, retry and
  failure policy, and scheduler `record_reward` accounting remain in
  `feedback.py` and their current owners. The value-only seam cannot call an
  LLM or consume provider credentials.
- Plugin score application remains index-ordered and receives the same
  feedback-adjusted values. Causal, TTT-RL, and DeepResearch hooks retain
  their state and artifact/provider ownership.
- `history.jsonl`, `failure_history.jsonl`, and `prompt_history.jsonl` retain
  separate artifact owners. Failure summaries must continue to project
  `evaluation.metadata.llm_feedback` at the same point and with the same
  field names.
- Retention semantics remain exact: raw feedback is hashed before redaction
  where the current policy does so; prompt rendering keeps its independent
  redaction/truncation caps; and `off`, `hash_only`, `redacted`, and `full`
  modes preserve their current meaning and cap order. The current policy
  identifier is `redact_bound_hash_v1`.
- Duplicate JSON names continue to raise `ValueError` and become failed
  feedback without a score side effect. Parser fallback behavior must not be
  broadened by a boundary extraction.

## Required acceptance tests for a future writer

No writer may start until the focused compatibility baseline remains green. A
future implementation must then run, with the
Windows Python 3.12 command used by this project:

- `tests/core/test_feedback.py`, including duplicate-name rejection,
  malformed payloads, evaluator failure and partial diagnostics, exact
  Unicode truncation, retention modes, and feedback ordering;
- prompt, evaluator, loop synchronous and asynchronous, plugin, database,
  CLI, and JSONL compatibility tests covering both feedback call sites and
  persisted prompt/failure records;
- direct tests for the pure boundary's deterministic JSON-safe projection,
  redaction/hash/cap ordering, field-name compatibility, no mutation of
  caller-owned values, and duplicate-name/error behavior;
- AST/import checks proving that the new module contains no provider,
  persistence, evaluator-authority, plugin-state, or scheduler-reward
  ownership; and
- the required repository non-integration, artifact, diff-hygiene, and paper
  gates after all lanes are assembled. A focused pass or a compile check must
  not be reported as full-suite or runtime evidence.

The acceptance record must distinguish test-derived results from
source-derived ownership checks and must identify any collection or
environment blocker explicitly.

## Rollback and no-op disposition

The present decision is a no-op for production code: retain `feedback.py` as
the sole implementation and retain the characterization evidence. A future
failed extraction is recoverable by removing the new helper and its façade
delegation, then rerunning the preserved focused compatibility tests. Do not
reset, clean, stash, or broadly revert the shared checkout; any rollback must
be limited to the future writer's explicitly owned paths.

## Unverified boundaries

The current evidence does not establish a green full non-integration suite,
provider-backed behavior, native security-sandbox behavior, OCI/runtime
parity, distributed execution, resumability, or end-to-end coordinator to
provider behavior. It also does not resolve the source/documentation mismatch
about whether feedback is retained verbatim. Those claims remain
unverified, and no PR, merge, or external publication is implied.
