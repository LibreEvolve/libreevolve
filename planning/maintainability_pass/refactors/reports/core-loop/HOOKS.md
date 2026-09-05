# `core/loop.py` Hooks and Feedback Slice

Agent: `01a069ce-b2d8-7f61-97d5-5987112c7bc1`
Status: Wave 1 read-only inventory complete; tests not executed; evidence
`source-derived`, `test-derived` (assertions inspected), `proposed`,
`unverified`.

Stable anchors: `_call_plugin_hook` near 3930, optional dispatch 3959,
failure annotation 3990, `_plugin_artifact_manifest` 47680,
`_build_plugin_context` 46573, and `_apply_plugin_scores` 47774. The ordered
sequential path is parent selection, generation-start hooks, prompt/context,
mutation/critique, evaluation, feedback, program construction, evaluated
hooks, admission, failure/history/rewards, prompt reward, optional meta-prompt
mutation, migration, generation-end hooks, and completion. Async workers do
not execute hooks; grouped drains preserve commit/end-hook order, while a
generation window may prepare later context from stale pre-drain state.

Hook failures are fatal and annotated/persisted; mutation-provider failures
skip `on_evaluated` and create bounded synthetic failure records. Plugin
context, metadata, failures, feedback, prompt text, provider responses, and
retrieval artifacts have independent caps/redaction/retention policies.
Plugin identity is index-sensitive and propagates through manifest, runtime,
candidate metadata, score composition, and plugin artifacts. Prompt-history,
failure-history, and runtime artifact writes are separate streams. The exact
full event trace is not currently asserted across sync, async, and
cross-generation modes.

Proposed seams are dispatch/error annotation, context construction, score
reduction, and artifact collection, in that order. Keep `evolve()` as the
ordering owner; do not move side-effecting plugin hooks into workers or merge
plugin, prompt, feedback, provider, and persistence ownership. Characterize
hook order, mutable side effects, finalization-before/after artifact pointers,
plugin-list reorder identity, and cross-stream joins before movement.
