# `core-budget` implementation record

Primary path: `libreevolve/core/budget.py`.

Support path: `libreevolve/core/budget_contract.py`.

Status: the narrow synchronous budget-contract extraction is present in the
current shared checkout. Independent verifier
`01a06a63-4b58-7661-a978-272442b9961e` found focused behavioral and ownership
compatibility, with a conditional WSL/untracked-file mode qualification. This
record does not claim isolated-patch attribution or full-suite success.

## Exact narrow contract extraction

The implementation moves the data-oriented budget contract kernel out of the
`RunBudget` façade. `budget_contract.py` has no import of `RunBudget`,
`Config`, the loop, evaluators, providers, persistence modules, or async
workers. It contains:

- budget limit and consumed-field declarations, stop reasons, controller-event
  kinds and schema identifiers, and `BudgetSnapshotError`;
- synchronous elapsed-time, evaluator-accounting, numeric, timestamp, role,
  map, snapshot, controller-state, and controller-event validation;
- role-counter copying/increment helpers, role-limit matching, and the
  established first-exhausted-limit precedence;
- `apply_controller_budget_event()`, which validates an event and applies it
  through the small recording-method/attribute surface supplied by the
  façade.

The last operation is intentionally state-mutating on its supplied budget
object; the extraction is pure with respect to external services and owns no
clock, provider, filesystem, or persistence side effect.

`budget.py` remains the compatibility and runtime façade. It retains the
`RunBudget` dataclass and its field order/method signatures, configuration
construction, monotonic and UTC clock acquisition, counter recording,
snapshot assembly, finalization, replay-budget construction and replay
comparison. `_check_limits()` delegates limit ordering to the contract while
passing its existing lazy runtime callback. The public and private constants,
validator names, and exception identity remain available from `budget.py`
through aliases and thin wrappers.

No async reservation, pending-work accounting, provider operation, retry or
cancellation policy, JSONL write, manifest write, or controller scheduler was
moved.

## Changed paths

The implementation seam consists of exactly these production paths:

- `libreevolve/core/budget.py` — replaces inline contract declarations,
  validators, limit checks, and controller-event application with imports,
  compatibility aliases, delegating wrappers, and the retained `RunBudget`
  runtime façade.
- `libreevolve/core/budget_contract.py` — new standard-library-only contract
  module containing the extracted declarations and synchronous helpers.

`tests/core/test_budget.py` is the characterization/evidence path used by the
handoff; its test additions are not part of this production extraction. No
test, registry, matrix, verification report, or other production path is
attributed to this implementation record.

## Shape measurements

The following lightweight measurements were taken from the current checkout
and from `HEAD` before the extraction. Physical LOC is line count; logical LOC
is nonblank, non-comment source lines; functions/classes/methods are AST
counts. The decision proxy counts common branch/loop/exception/comprehension
nodes and boolean expressions. These measurements describe source movement,
not maintainability or runtime quality.

| metric | before `budget.py` | after `budget.py` | new `budget_contract.py` | combined after |
|---|---:|---:|---:|---:|
| physical LOC | 1,497 | 534 | 1,070 | 1,604 |
| logical LOC | 1,385 | 496 | 984 | 1,480 |
| top-level functions | 42 | 8 | 39 | 47 |
| classes | 2 | 1 | 1 | 2 |
| `RunBudget` methods | 18 | 18 | 0 | 18 |
| decision proxy | 213 | 21 | 193 | 214 |

The façade is substantially smaller, but the combined decision proxy is
effectively unchanged and combined source size increases by the explicit
module boundary. No complexity reduction claim is made. The independent
verifier confirmed the public/private signatures, 14 private-name aliases,
exception identity, state transitions, and limit-precedence probes. Its only
qualification is that the untracked support file is observed as mode `100755`
on this WSL-mounted checkout; the repository's `core.filemode=false` and
mounted-file behavior make this a hygiene/attribution observation rather than
a behavioral failure.

## Preserved contracts and ownership

- `RunBudget.from_config()` continues to be the only configuration-to-budget
  construction path and retains its `Config` dependency and effective limit
  mapping.
- `RunBudget.from_restored_snapshot()`, `snapshot()`, `finish()`, and the
  recording methods retain their existing signatures, counter semantics,
  field names, defensive copies, and stop-reason behavior.
- Validation still rejects malformed snapshots, controller states, events,
  counters, role maps, timestamps, accounting, and stop reasons with the
  established `BudgetSnapshotError`/`ValueError` boundary. The façade exports
  the same exception object and compatibility names.
- Limit precedence remains in the extracted helper. Runtime time is checked
  only through the façade's callback and remains lazy, monotonic, and
  non-negative as before.
- Controller-event normalization and application remain synchronous and
  ordered. The façade still owns replay-state orchestration, constructs the
  replay budget, applies events, and compares the replayed snapshot.
- LLM calls, provider attempts, tokens, cost, seconds, role accounting,
  evaluator attempts/samples/retries/timeouts, and generation counters remain
  `RunBudget` state updated by existing callers. No provider call or evaluator
  execution was introduced in the contract module.
- Async sampling/evaluation queues, reservations, worker ownership, merge
  ordering, retry/cancellation behavior, and generation barriers remain in
  their existing loop/async callers. This seam does not make pending work
  resumable or distributed.
- Snapshot/event persistence, JSONL durability and repair, manifest/archive
  writing, and CLI/report assembly remain outside both the contract kernel and
  this extraction's ownership boundary.

## Dependency edges

The inventory identifies `loop.py` and `database.py` as the direct production
consumers of the budget façade; adjacent async/evaluator and reporting paths
consume the façade's accounting and snapshot contracts through their existing
call paths. The intended direction is:

```text
loop/database/adjacent callers -> budget.py façade -> budget_contract.py
                                 |                  \-> standard library
                                 \-> Config, clocks, RunBudget state
```

Only `budget.py` imports the new support module. The support module must not
acquire reverse imports from `Config`, loop scheduling, provider clients,
evaluators, JSONL/storage, or CLI/reporting. Any future move of async
reservation, persistence, or replay orchestration requires a new
characterization and coupling review.

## Rollback

The scoped rollback is to restore the inline declarations, validators, limit
precedence, and controller-event application in `budget.py`, remove its
`budget_contract` imports/aliases/wrappers, and delete only
`libreevolve/core/budget_contract.py`. The façade's public/private compatibility
names and existing callers must remain intact during rollback. Because this is
a shared dirty checkout, rollback must be path-scoped and must not reset,
clean, stash, or alter unrelated user changes.

## Evidence and limitations

- The independent verifier confirmed the Windows Python 3.12 focused run of
  `tests/core/test_budget.py` with **150 passed**, production compilation,
  dataclass/exception compatibility, 14/14 private-name identity aliases,
  contract/state-transition probes, and scoped whitespace checks.
- The characterization covers finalization, invalid-input state preservation,
  zero-limit and precedence behavior, stable snapshots and role maps, UTC and
  monotonic timing, event normalization, and replay-report cases. It does not
  prove every loop/async caller preserves behavior under concurrency or
  cancellation.
- The required full suite,
  `py -3.12 -m pytest tests/ -m "not integration"`, has not been reported as
  passing for this seam. Package/build, CLI, paper, documentation, artifact,
  provider, native-sandbox, distributed, crash-recovery, cross-process resume,
  and end-to-end runtime evidence remain unverified.
- The shared working tree contains other dirty paths and the focused result
  is not an isolated patch attribution. No commit, push, PR, or merge is
  implied by this record.

Accordingly, this is a narrow implementation record with a conditional,
lane-scoped verifier result, not a repository-wide completion report.
