# README Todo: Incorrect or Unsupported Claims

This list tracks README statements that are inaccurate, misleading, or too
strong after comparing the current code, `papers/`, and AlphaEvolve sources.

## AlphaEvolve Comparison Table

## Research References and Bundled Papers

## Feature Claims

- [ ] Keep README LLM budget/replay claims scoped to current synchronous
  restore boundaries.
  - Spec evidence: AlphaEvolve-scale reproduction needs compute-budgeted model
    scheduling, replayable run accounting, and enough provider evidence to
    distinguish resumed controller state from replayed provider outputs.
  - Current evidence: README now documents live synchronous
    provider-attempt/token/configured-cost/latency stops, restorable runtime
    budget snapshots, `controller_budget_events.jsonl` replay, and
    full-runtime restore validation, while still marking live provider pricing,
    provider-output replay, and async/pending-work budget composition as open.
  - Required result: once provider-output replay, async/pending-work budget
    composition, or live pricing/default capture land, update the README and
    matching code/paper TODO entries together so the README neither underclaims
    current synchronous budget replay nor overclaims full AlphaEvolve-style
    replay.

## Architecture Description
