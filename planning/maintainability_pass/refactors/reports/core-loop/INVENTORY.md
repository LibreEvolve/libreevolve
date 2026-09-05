# `core/loop.py` Wave 1 Inventory

Primary file: `libreevolve/core/loop.py`
Lane: `core-loop`
Status: complete Wave 1 reconciliation; Wave 2 pure value seam implemented

## Slice reports received

| Slice | Agent | Evidence state | Result |
|---|---|---|---|
| lifecycle | `01a069ce-a5be-7633-846e-54b1fc8c1d1b` | source-derived | completed read-only inventory; two sidecars reconciled |
| persistence | `01a069ce-b62b-7192-9e67-a56caeb84ee2` | source-derived | completed read-only inventory; no tests executed |
| sampling | `01a069ce-a8c8-7513-8649-3b816ad53101` | source-derived | completed read-only inventory |
| evaluation | `01a069ce-ac5e-7b00-956c-9482a9a830ad` | source-derived | completed read-only inventory |
| admission | `01a069ce-af6d-7452-986f-59c9cfc553a9` | source-derived | completed read-only inventory |
| hooks | `01a069ce-b2d8-7f61-97d5-5987112c7bc1` | source-derived | completed read-only inventory |
| reporting | `01a069ce-ba14-7380-811c-c1a3a0db07df` | source-derived | completed read-only inventory |
| cross-cutting | `01a069ce-bd42-7953-bf57-a1bfc3af87e0` | source-derived | completed read-only inventory |

The dedicated file lead reconciled all eight slices and an independent auditor
confirmed 23 stable anchors. The test-only characterization writer added
`tests/core/test_loop_characterization.py`, and the implementation writer then
extracted only the four immutable private value records into
`libreevolve/core/loop_models.py`. Orchestration, side effects, and the public
`evolve()` façade remain in `loop.py`; an independent verifier reviewed the
actual diff.

## Stable lifecycle anchors

- `evolve()` setup and restore inputs: approximately line 856.
- `_initial_run_rng()` / `_initial_run_budget()`: approximately lines 503/518.
- `load_full_resume_bundle()` and validator: approximately lines 5593/5694.
- generation loop, async generation, and generation finalization: approximately
  lines 1125, 2054, and 3312.
- completed and aborted finalizers: approximately lines 3732 and 3790.
- runtime history/report assembly and artifact pointers: approximately lines
  8147 and 7746.

These are stable anchors from the current source snapshot; the file lead must
reconfirm symbols/line positions with AST inventory before editing.

## Observed lifecycle and ownership

`Config` validation occurs during construction, CLI normalization, `evolve()`
setup, and database construction; it mutates canonical fields and must not be
silently duplicated or moved into a lower-level seam. Workspaces are normalized
before seed bootstrap. Seeds are generation 0, receive deterministic IDs and
source metadata, are evaluated/budgeted, and are logged even when admission
rejects them. Restore inputs for RNG, scheduler, archive/cursor, budget, and
full resume are distinct; restored budget precedes seed evaluation, while the
seed block and generation loop still run from their current entry contract.

The loop owns `best`, phase, recent failures, strict seed count, evaluation and
in-flight caches, pending evaluation/finalization lists, and controller
reports. `RunBudget`, `ProgramDatabase`, prompt databases, plugins, LLM
schedulers, and async queues own additional mutable state. Direct callers
include CLI `run`, the matrix evolution fixture, integration tests, and core
tests importing public and private loop helpers.

Normal finalization drains work, closes controllers, exports best artifacts,
assembles runtime reports, updates artifact pointers, and atomically updates
the manifest. Abort finalization closes controllers, records bounded/redacted
failure metadata, attempts manifest persistence, and re-raises the original
exception. Setup failures before the outer `try` boundary can lack an aborted
runtime manifest; this is a characterization requirement, not a license to
change behavior implicitly.

## Persistence and artifact coupling

`ProgramDatabase` writes and/or owns `manifest.json`, `history.jsonl`,
`failure_history.jsonl`, `archive_events.jsonl`,
`controller_budget_events.jsonl`, `llm_calls.jsonl`, prompt streams,
evaluator results, duplicate-work indexes, quarantine streams, and task
specification. `best.py` and `best_workspace/` are output artifacts, not
pending-work resume state. Archive-event replay is an ordered audit stream,
not a restore engine; provider outputs, async queues, validator processes, and
pending work are not replayed.

Source review found several durability boundaries that must be preserved or
explicitly fixed in their owning lane: JSONL writes are locked/flushed/fsynced
but repair plus diagnostic append is not one crash-atomic transaction; archive
memory can advance before an archive-event append succeeds; best artifact pair
installation has rollback but no fsync/crash-atomic pair commit; and some
derived finalization reports use direct `Path.write_text()` rather than the
strict atomic writer. Native-Windows behavior, power-loss durability, and
cross-process sequencing remain unverified.

## Evidence boundary

The slice reports are `source-derived` inventory only. The pure-value
extraction has separate characterization and verifier gates. Native Windows,
provider, distributed, and end-to-end claims remain unverified.
