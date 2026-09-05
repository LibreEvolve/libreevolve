# core/feedback.py verification

## Status

Fresh independent non-authoring verifier: `01a06fa4-e69a-7f23-b4e8-ddd61649f309`.
Verdict: **deferred/no-op accepted for this wave**. Windows focused feedback
tests pass `85 passed`; the prompt/JSONL/artifact/feedback/meta compatibility set
passes `655 passed`. The sync/async mutation, retention, and documentation
handoffs still block a writer.

Evidence state: current focused compatibility pass; production refactor
deferred and no production writer authorized. The prior prompt-import blocker
is superseded by the prompt compatibility repairs and is not a current
feedback-lane blocker.

## Evidence ledger

| Evidence | Result | Classification |
|---|---|---|
| Combined focused compatibility run: `test_prompt.py`, `test_prompt_characterization.py`, `test_jsonl.py`, `test_artifact_schema_characterization.py`, `test_feedback.py`, and `test_meta_prompt.py` | `655 passed` | test-derived, current |
| Prompt compatibility verifier | `PASS` after the prompt compatibility repairs | verification-derived, current focused evidence |
| Coupling review | Identifies a pure future projection seam, but says the lane is not ready for extraction | source-derived design review |

The current combined focused command was:

```text
/mnt/c/Windows/py.exe -3.12 -m pytest tests/core/test_prompt.py tests/core/test_prompt_characterization.py tests/core/test_jsonl.py tests/core/test_artifact_schema_characterization.py tests/core/test_feedback.py tests/core/test_meta_prompt.py --tb=short
655 passed
```

This replaces the earlier isolated `84 passed, 1 failed` result and its
prompt-import diagnosis as current evidence. That earlier result is retained
only in the prior handoff history; it must not be reported as the present
status. The 655-test result is a focused compatibility pass, not evidence that
the full repository suite or a live runtime path has passed.

## Future seam verification requirements

Before authorizing a writer:

1. Retain the current prompt compatibility repair and reproduce the 655-test
   focused result, or an equivalent complete focused run, after any future
   feedback seam change.
2. The retention-policy documentation/source discrepancy must be reconciled
   and recorded by the owning documentation lane.
3. An independent coupling check must confirm that the proposed
   `feedback_boundary.py` is value-only and that `feedback.py` retains metric,
   fitness, validity, provider, retry, failure-policy, plugin, reward, and
   persistence ownership.

After those prerequisites, an independent verifier must confirm:

- both synchronous and asynchronous loop paths call feedback in the same
  order as before;
- evaluator-declared metrics and `Problem.fitness_from_metrics` remain the
  authorities, with feedback/plugin mutation order unchanged;
- provider roles and reward accounting are untouched and absent from the
  boundary module;
- `history.jsonl`, `failure_history.jsonl`, and `prompt_history.jsonl` retain
  their separate owners and compatible records;
- redaction, hashing, truncation, retention modes, cap order, field names,
  Unicode behavior, and duplicate-name failure behavior are unchanged; and
- the boundary has deterministic JSON-safe output and does not mutate
  caller-owned inputs.

The verifier must run the focused compatibility tests plus the applicable
repository static, build, artifact, diff-hygiene, and final non-integration
gates. It must label focused, static, build, runtime, and end-to-end results
separately.

## Ownership and rollback check

No production writer is authorized by this lane at the current evidence
state. The safe disposition is to keep the existing façade and characterization
tests unchanged while the future seam and retention ownership are resolved.
If a future extraction fails verification, remove only that writer's new
helper and façade delegation and rerun the preserved compatibility tests. No
shared-checkout cleanup or broad revert is part of this lane.

## Unverified claims

There is no full non-integration-suite pass, provider-backed run, native
security-sandbox result, OCI parity result, distributed/resume result, or
end-to-end runtime proof in this report. The focused 655-test pass does not
establish any of those broader claims. No production change, PR, merge, or
publication is reported.
