# `core/loop.py` Reporting and Observability Slice

Agent: `01a069ce-ba14-7380-811c-c1a3a0db07df`
Status: Wave 1 read-only inventory complete; tests not executed; evidence
`source-derived`, `test-derived` (assertions inspected), `proposed`,
`unverified`.

Stable anchors: `evolve()` near 856, outer `try` near 956, seed path near
1027, completed/aborted finalizers near 1997/2014,
`_runtime_history_summary()` near 8147, `_attach_runtime_summaries()` near
4034, and artifact pointers/bundle validation near 7746/7758.

`ProgramDatabase` owns durable streams. Completed and aborted finalization
both assemble runtime projections from in-memory database/budget/controller
state, write derived evaluator/prompt/duplicate reports, attach provider,
plugin, cascade, archive, async-controller, and topology summaries, compute
artifact pointers, and update `manifest.json`. `claim_ready: false`, provider
output non-replay, pending-work non-resume, and diagnostic quarantine
boundaries must remain explicit. `history_partially_written` is an existence
indicator, not a corruption verdict.

Normal termination is `completed`, including nonfatal mutation/evaluation
rejections and many best-export failures. Fatal hook/evaluator/controller
errors inside the `try` become `aborted` and re-raise the original exception;
setup failures before that boundary may have no final runtime status. Reporting
has side effects and cannot be extracted as a pure projection without
preserving ordering and error precedence. LLM spans, failure history, prompt
history, artifact writers, and manifest updates are separate persistence
streams.

Proposed decomposition is `LifecycleReporter`, pure-ish
`RuntimeSummaryBuilder` over explicit inputs, `TelemetryReporter`,
`ArtifactBundleReporter`, and `ManifestFinalizer`, while keeping stream writes
and policy ownership in their current modules. First characterize normal,
budget-stopped, mutation-failed, invalid, async, and aborted runs, including
runtime key/stream snapshots, redaction/bounds, finalization failure paths,
and artifact pointer/report ordering. Native-Windows, power-loss, provider,
and end-to-end evidence remain unverified.
