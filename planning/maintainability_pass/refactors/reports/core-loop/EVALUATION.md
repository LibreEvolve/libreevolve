# `core/loop.py` Evaluation Coordination Slice

Agent: `01a069ce-ac5e-7b00-956c-9482a9a830ad`
Status: Wave 1 read-only inventory complete; tests not executed; evidence
`source-derived`, `test-derived` (assertions inspected), `proposed`,
`unverified`.

Stable anchors: `evolve()` setup/seed path (856/1027), main barrier (1125),
candidate commit (3034), async dispatch/drain/window (3371/3497/3423),
generation finalization (3312), and final drain/abort handling (1944/2014).
Adjacent controller/evaluator anchors are `AsyncCandidateEvaluationController`
near `async_evaluator.py:54`, `CascadeEvaluator.evaluate()` near
`evaluator.py:528`, and timeout cleanup near `evaluator.py:4010`.

Cascade order is diff error, syntax, contract preflight, configured stages,
then optional/default validation; first failed stage stops the cascade. Seed
evaluation is synchronous. Candidate async work uses a bounded queue and
`to_thread`; cache hits and exact in-flight duplicates do not consume another
evaluation. Completion may be out of order, but drain and commit are in
submission order. Archive/history/budget/plugin/prompt mutations stay on the
loop reducer. `close()` drains and stops workers; it is not evaluator
cancellation. First async errors are re-raised after later accounting is
resolved, before later results commit.

Proposed order-preserving seams are (1) cache/dispatch/coalescing/resolution/
accounting, (2) the existing async controller, and (3) generation-window
coordination separate from candidate commit. Cascade internals and subprocess
cleanup remain evaluator-owned. Characterize detailed evaluator limits,
first-error handling, hung `to_thread` behavior, report fields, and the
`claim_ready: false` local-only boundary before movement. No live, native
Windows, distributed, provider, or end-to-end evidence was collected.
