# `core/loop.py` Characterization Gate

Status: `pure value extraction characterized`; independent verifier passed the
implementation seam.

## Existing test surfaces to execute and classify

- `tests/core/test_loop.py`: setup/no-write failures, deterministic IDs and
  proposal batches, async evaluation/LLM ordering, seed validity, restore,
  completion/abort/redaction/hooks/artifacts, and generation-start parent
  stability.
- `tests/core/test_jsonl.py`, `tests/population/test_database.py`,
  `tests/test_cli.py`, and the restore/durability boundary tests for adjacent
  serialized contracts.

Source inspection identified these ranges in `tests/core/test_loop.py` as
particularly relevant: approximately 919-940, 1079-1234, 1338, 1392-1934,
4030-5108, 11716-12109, 13826-14578, and 16655-16703. These ranges are
navigation hints, not proof that the tests pass.

The reconciled isolated lead report recorded 13 dedicated characterization
passes, 19 selected loop-contract passes, 8 async-evaluator passes, 12
async-sampler passes, 140 budget passes, 40 JSONL passes, and 13 database
contract passes. Its full loop run was intentionally interrupted after 453
passes and one skip at 92%, so it is incomplete evidence. A shared test-only
writer re-established the focused coverage in the root checkout. The pure
value seam writer subsequently moved four frozen private dataclasses from
`loop.py` to `loop_models.py` without moving orchestration or side effects.

Root Windows evidence after the extraction:

- `tests/core/test_loop_characterization.py`: `11 passed`.
- `tests/core/test_loop.py`: `465 passed, 2 skipped in 799.84s`.
- The independent verifier reports 8 selected sync/async contract passes,
  plus AST, compile, import-cycle, alias-identity, signature, field/default,
  repr, equality, and whitespace checks.

## Required cases before movement

1. Snapshot `Config` and `Problem` around direct `evolve()` and prove intended
   validation/idempotent mutation; compare CLI and direct effective plans.
2. Preserve no-write behavior for evaluator, LLM, plugin, malformed-seed,
   containment, symlink, and overwrite failures.
3. Lock seed ordering, primary-file policy, source metadata, deterministic IDs,
   generation 0, strict/permissive invalidity, and restored-budget-before-seed.
4. Trace zero, one, and multiple proposals: parent selection,
   generation-start hooks, migration, generation-end hooks, budget events, and
   phase labels.
5. Compare synchronous, async-evaluation, async-LLM, and generation-window
   paths for submission/completion/admission order, cache accounting,
   stale-state behavior, and worker failures.
6. Inject controller-close, best-export, plugin-artifact, runtime-summary, and
   strict-manifest failures; preserve original exception precedence and abort
   persistence semantics.
7. Round-trip runtime artifacts and preserve negative boundaries: no provider
   replay, no pending-work resume, no archive-event restore engine, and no
   distributed-execution claim.

8. Add a canonical event trace covering parent selection, prompt/context,
   provider role, evaluation/cache, feedback, plugin scoring/hooks, admission,
   rewards, history/failure/prompt streams, migration, and finalization.
9. Preserve public/private imports, monkeypatch targets, lazy optional imports,
   exception annotations, exact default arguments, and run-owned RNG state.

## Proposed seam order

Keep `evolve()` as the compatibility facade. After characterization, extract
explicit `RunPlan`, `RestoreState`, and mutable `RunState`; then preparation/
restore selection; seed bootstrap; a generation-boundary coordinator shared by
sync and async paths; and completion/abort finalization. Keep `Config.validate()`
and `ProgramDatabase` policy authority in their owning files. Each extraction
must have a separate lane dependency edge, before/after metrics, focused tests,
and an independent verifier.

The cross-cutting overlap review confirms that no implementation writer is
authorized while any of the eight loop slice reports, the event trace, or the
admission/mode/restore characterization remains missing.
