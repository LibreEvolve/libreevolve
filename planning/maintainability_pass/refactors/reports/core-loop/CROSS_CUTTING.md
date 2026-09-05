# `core/loop.py` Cross-Cutting Slice

Agent: `01a069ce-bd42-7953-bf57-a1bfc3af87e0`
Status: Wave 1 consolidated graph complete; implementation not authorized.

`loop.py` is approximately 49,605 lines with 804 functions; `evolve()` spans
approximately lines 856-2051. Production edges enter through `cli.py` and the
matrix evolution fixture; tests import about 108 loop symbols, including
private helpers, and directly patch roughly 230 loop-module names. Those patch
targets, `artifact_schema.py` writer anchors, phase-local optional imports,
exception attributes, and default signatures are compatibility edges.

## State and ordering graph

```text
preflight/restore -> DB setup -> seed evaluation -> controllers
-> proposal preparation -> evaluation/cache -> feedback/plugin scoring
-> threshold/MAP-Elites admission -> rewards/history/prompt logging
-> migration/generation end -> drain/close -> completed or aborted finalizer
```

The primary mutable owners are the run RNG, `RunBudget`, `ProgramDatabase`,
evaluation cache, `PromptSampler`, `PromptDatabase`, async controllers,
`recent_failures`, `phase`, and LLM/logger state. Config/evaluator/LLM
preflight precedes database setup; the outer `try` starts only after setup.
Async workers may complete out of order, but merge, admission, rewards, and
persistence are submission ordered. Migration/best selection precedes end
hooks; drains precede close and completed persistence; the first relevant
exception remains authoritative during cleanup.

No global/nonlocal declarations, nested functions, or mutable literal defaults
were found. Module-level policy containers remain patchable contract data.
Lazy `pypdf`, benchmark, and Gemini imports must retain optional-dependency and
import-time behavior. `_PLUGIN_FAILURE_ATTR` must remain attached to hook
exceptions if hook code moves.

## Required overlap reviews

Before movement, review lifecycle with sampling, persistence, and reporting;
sampling with evaluation, admission, and hooks; evaluation with admission and
reporting; admission with hooks and persistence; hooks with reporting;
persistence with reporting; and the cross-cutting graph against every slice.
Each review must compare generation numbering, RNG draws, cache/budget
ownership, event/stream order, phase/error attribution, lazy imports, and
monkeypatch compatibility.

## Safe extraction order

1. Add a canonical sequential event trace and admission/budget/mode/restore
   characterization without moving production symbols.
2. Extract pure IDs, cache hashes, metric/mutation policy, and immutable
   request/result records.
3. Extract proposal preparation while preserving prompt-state capture, plugin
   timing, RNG ownership, and patchable LLM names.
4. Extract evaluation/cache/async dispatch and drain with ordered main-thread
   effects.
5. Extract the admission/commit reducer, then terminal report adapters one
   family at a time.
6. Extract generation scheduling and setup/restore; slim `evolve()` last.

The complete event/artifact/order contract has not been executed, so this is
`source-derived`/`proposed` planning evidence only. Native Windows, live
providers, distributed execution, pending-work resume, provider replay,
hostile-code sandboxing, and end-to-end runtime evidence remain unverified.
