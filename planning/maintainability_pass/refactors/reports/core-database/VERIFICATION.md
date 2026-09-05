# core-database verification

Fresh independent non-authoring verifier: `01a06fa4-e0a3-7d43-aaea-9ea8dddc5a9d`.
Verdict: **no-op accepted for this wave**. Focused target: `292 passed, 3
skipped` from 295 collected; the four-case contract subset passed `4 passed,
291 deselected`; Windows `py_compile`/scoped source review passed. This confirms
the disposition only, not an implementation or runtime pass.

Evidence state: characterization-only; no production refactor to verify.

## Scope and verdict

This report verifies the narrow-seam decision for
`libreevolve/core/database.py`. It does not verify an implementation: no
database writer was authorized, no database support module was added, and no
database production diff is being asserted. Verdict: **no-op accepted for this
wave; future production work remains unverified and gated**.

## Exact evidence already run

- Focused database target: `tests/population/test_database.py` on the Windows
  Python 3.12 environment — `292 passed, 3 skipped` from 295 collected cases.
- Characterization subset in that same target, containing the four added
  contract cases — `4 passed, 291 deselected`.
- The focused cases cover admission, invalid evaluations, sampling exclusion,
  local RNG, cursor/full restore, JSONL and archive-event schemas, UTF-8 and
  duplicate-name rejection, sequence/cell/restore errors, manifest recovery,
  cleanup, links, and migration.

These are current-tree focused results. The checkout is shared and contains
other scoped dirty work, including characterization and compatibility changes;
the results therefore do not attribute every passing test exclusively to this
lane. The artifact-inventory source-anchor failure was resolved by restoring
thin CLI compatibility wrappers, not by a database refactor.

## Contract and ownership checks

Source/inventory review confirms the following boundary that a future writer
must preserve:

- `ProgramDatabase` is the compatibility façade for admission, persistence,
  restore, manifests, and cleanup.
- Islands retain cursor, migration, and sampling ownership; MAP-Elites retains
  cell identity, replacement, and eligibility; programs retain identity,
  lineage, and workspace normalization.
- `VALID_THRESHOLD = 0.0` is pre-admission only, and admission, cell
  replacement, search-state mutation, and sampling eligibility remain distinct
  outcomes.
- Cursor advancement is conditional on search-state change; migration IDs are
  canonical; archive replay is audit-only.
- The measured module shape is 11,841 physical LOC, 11,137 logical LOC, 309
  functions, six classes, and 47 methods, with 11 direct importers and 115
  distinct configuration attributes across 154 references.

These are source-derived and characterization evidence, not proof of a
successful extraction.

## Required future verification

Before any future implementation can receive a pass, an independent verifier
must check the caller map and import ownership, public/private compatibility
anchors, exact admission flags, cursor sequencing, archive-event and JSONL
ordering, restore equivalence, serialized bytes, missing-reference behavior,
and append-failure atomicity. The verifier must rerun the focused database and
adjacent boundary tests, then the required repository non-integration suite.

## Gate status

| Gate | Status | Evidence |
| --- | --- | --- |
| Inventory and ownership review | PASS, source-derived | Existing `INVENTORY.md` and `CHARACTERIZATION.md` |
| Focused database characterization | PASS | `292 passed, 3 skipped` |
| Four added characterization cases | PASS | `4 passed, 291 deselected` |
| Production seam implementation | NOT RUN | No writer authorized; no patch exists |
| Independent implementation verifier | NOT RUN | No implementation to verify |
| Full repository non-integration suite | UNVERIFIED | Not run for this lane decision |
| Build/CLI/paper/docs/artifact/diff gates | UNVERIFIED | Outside the focused result |
| Native Windows junction/locking behavior | UNVERIFIED | Not covered by the reported run |
| Runtime/end-to-end/provider/distributed behavior | UNVERIFIED | Not claimed |

## Rollback and evidence boundary

There is no production database change, so rollback is the no-op disposition:
retain the current façade and the existing working-tree attribution. A future
authorized seam must be isolated and independently verified; rollback must
remove only that seam and its approved support/tests. This report makes no
claim of a full suite pass, runtime proof, or completed refactor.
