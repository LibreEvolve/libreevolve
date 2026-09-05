# Core database slice specialist reviews

Lane: `core-database`
Primary: `libreevolve/core/database.py` (11,841 current physical lines)
Reviews: `01a0705b-5e15-7fa1-8e4b-02b7f1be9f9a` (admission),
`01a0705b-611f-7540-a47d-441eb34b7af8` (persistence/restore), and
`01a07081-b58d-7e61-ae98-f2565549a26f` (archive projection/manifest)

## Admission slice

The façade owns construction, startup validation, archive admission, event
ordering, and sampling/reporting. Relevant current symbols are
`ProgramDatabase.__init__` 446–596, `add` 598–599, `_archive_add` 647–662,
`admit` 664–748, façade sampling/reporting 998–1030, and archive-event
append/sequence ownership 1365–1381.

Callers are `core/loop.py` construction at 865–888, seed admission at
1027–1034, normal admission at 1747–1769, async admission at 3102–3154,
migration/finalization at 1867–1871 and 3255–3263, CLI restore readers at
946–1009, and `deep_research.py`'s `db.best()` use at 327–330.

The contract boundary is:

```text
loop / CLI -> ProgramDatabase façade -> IslandModel -> MAP-Elites -> Program
                         |                    |
                         +-> JSONL/artifact codecs
```

`VALID_THRESHOLD == 0.0` is only the pre-admission gate. `MAPElites.add()`
owns cell replacement; `entered_cell` drives `cell_admitted` and
`sampling_eligible`, while `admitted` reflects any retained search-state
change. `IslandModel.add()` advances archive sequencing for candidates past
database gates but advances the island cursor only when search state changes.

The safest seam is a narrow adapter for admission-result normalization and
archive-event encoding/validation. Keep ordering and mutation in the façade;
do not move cell policy or cursor/sampling policy downward.

## Persistence and restore slice

Relevant symbols include `load_archive_restore_bundle` 1486–1501,
archive-event loading/audit 1534–1749, runtime archive validation 2209–2411,
history/record codecs 2933–3351 and 6161–6270, and derived index builders
4106–6041.

Contracts include `libreevolve.history.program.v1`,
`libreevolve.failure_history.v1`, `libreevolve.archive_event.v1`,
`libreevolve.island_state.v1`, and derived lineage/failure/artifact/output
index schemas. History is strict UTF-8 JSONL with duplicate-key, finite-number,
identity, and duplicate-ID checks. Archive restoration reconstructs Programs
from history and passes them to IslandModel; event replay is audit-only and
quarantine rows are never restore input.

Mutable state includes `_islands`, `_all`, `_ids`, `_archive_ids`, failure
records/counts, bounded retrieval context, sequence counters, startup manifest,
retention policy, objective schema, and admission/failure metadata on live
Programs. The important unresolved transaction boundary is that `admit()` can
mutate the archive and append an archive event before the caller appends the
history record; a characterized failure can leave archive state ahead of its
event stream.

The lowest-risk future extraction is pure record codecs/validators or derived
projections. Archive mutation, history append, event append, manifest updates,
and restore authority should remain in the façade until transaction semantics
are explicitly designed.

Characterization: `110 passed, 277 deselected` for the admission slice;
database module evidence is `292 passed, 3 skipped`, with related JSONL/artifact
characterization `86 passed`. These are local/static checks, not distributed or
live-resume proof. Native Windows junction/locking, complete archive transaction
atomicity, and exact serialized-byte stability remain unresolved.
## Additional projection specialist — Darwin

Agent `01a07081-b58d-7e61-ae98-f2565549a26f` completed a read-only source
review with no tests or edits. The slice covers `_startup_manifest_payload`,
`_write_manifest`, `update_manifest_runtime`, restore/index loaders, objective
and resurfacing projection builders, and their loop/CLI consumers. Archive
authority remains in `IslandModel`; pure projections read `_all` while live
archive state is separate, so an admitted-but-unlogged program can diverge
from runtime projections. Recommended direction is to extract pure codecs and
projections only after preserving admission/event/history ordering. The review
adds the unresolved questions about manifest authority, nine-index recompute
determinism, and MAP-Elites reference validation. It is the fourth database
review required for this large file; it does not authorize a writer.
