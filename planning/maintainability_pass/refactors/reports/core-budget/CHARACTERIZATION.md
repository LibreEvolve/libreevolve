# core/budget.py characterization

Evidence state: test additions present in the shared checkout, but this lane
is not yet implementation-ready.

The authorized characterization wave added normal finalization, invalid-input
state preservation, zero-limit/limit precedence, stable snapshots and role
maps, UTC/monotonic timing, event normalization, and replay-report cases to
`tests/core/test_budget.py`. The root-side Windows run recorded 150 passed;
the earlier WSL report could not collect pytest. The focused test additions are
test evidence only; no production budget code has changed.

Before a writer, independently confirm the focused baseline and preserve the
boundary with async queue accounting, retry/cancellation, persistence, and
report assembly. Native platform and full-suite claims remain open.
