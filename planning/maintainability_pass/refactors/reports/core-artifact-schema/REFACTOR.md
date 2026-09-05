# core-artifact-schema implementation record

Evidence state: the narrow implementation seam is present in the current
checkout and has an independent lane-scoped `PASS` from verifier
`01a06a52-8400-7352-beee-81d08ccb012b`. No full-suite, build, or live-runtime
success is claimed here.

## Implemented scope

The implementation extracts only the construction of the versioned record
family declarations from
`libreevolve.core.artifact_schema._run_artifact_schema_without_inventory`.
The façade still owns the canonical schema constants and assembles the complete
run-artifact schema.

The new data-only module,
`libreevolve/core/artifact_schema_record_contracts.py`, provides:

- `jsonl_record_families(...)`, returning the ten accepted JSONL stream
  declarations: history, evaluator results, failure history, archive events,
  the nested LLM call/reward family, prompt history, prompt current bindings,
  prompt prior scores, duplicate-work cache, and controller-budget events.
- `quarantine_record_families(...)`, returning the seven diagnostic stream
  declarations for history, failure history, archive events,
  controller-budget events, LLM calls, prompt history, and the manifest. Each
  declaration retains its source stream, source record schema, and diagnostic
  record schema.

`artifact_schema.py` calls those factories and maps the quarantine declarations
through its existing `_quarantine_record` helper. The extraction is therefore a
record-contract declaration seam, not a validator or storage abstraction. The
new module contains no persistence, JSONL append/repair, validation, redaction,
CLI, or runtime orchestration behavior.

## Changed paths

Implementation paths are:

- `libreevolve/core/artifact_schema.py` — imports the two factories and replaces
  the inline JSONL/quarantine family literals with factory calls.
- `libreevolve/core/artifact_schema_record_contracts.py` — new data-only
  declaration module.

The implementation change to the tracked façade is 32 insertions and 52
deletions. No test, registry, matrix, or other production path was changed by
this implementation record. The report itself is the only planning file being
written for this handoff.

## Shape measurements

Current checkout measurements from the implementation state are:

- `artifact_schema.py`: 2,138 physical lines and 23 top-level definitions by
  the lightweight source count.
- `artifact_schema_record_contracts.py`: 97 physical lines and two top-level
  functions.
- Existing Wave 1 inventory: approximately 2,158 LOC and 23 module functions
  for the façade before this movement.

These are source-shape measurements only. They do not establish reduced
complexity, improved runtime behavior, or lower coupling. An independent
verifier should recompute the before/after measurements using the lane's
standard method.

## Preserved contracts and ownership

The implementation intentionally preserves:

- the canonical schema identifiers, `ARTIFACT_SCHEMA_VERSION`,
  `LEGACY_RECORD_POLICY`, and the façade's existing import/source anchors;
- the exact JSONL and quarantine key sets and nested LLM call/reward shape
  returned by `run_artifact_schema()`;
- `_quarantine_record`'s diagnostic fields, retention-mode pointer,
  `QUARANTINE_RECORD_SCHEMA`, and lifecycle metadata;
- `run_artifact_schema()`, `generated_run_artifact_inventory()`,
  `versioned_record()`, legacy-v0 compatibility, and all existing public and
  private façade call sites;
- strict JSONL error handling and quarantine iteration, including their
  existing error taxonomy and diagnostic boundary;
- redaction, retention modes, bounded diagnostic snapshots, and hashing policy;
- stream writers, readers, locking/order, repair behavior, and artifact-owner
  declarations. No JSONL durability or repair semantics moved into the new
  module.

The helper's `diagnostic_record_schema` input is declarative metadata. The
façade continues to materialize the diagnostic record through
`_quarantine_record`, so the existing façade-owned diagnostic constant and
policy remain authoritative.

## Dependency and coupling edges

`artifact_schema.py` continues to be the public schema boundary for direct
consumers including `core/database.py`, `core/loop.py`, `core/meta_prompt.py`,
`core/run_inspection.py`, `libreevolve/cli.py`, `llm/ensemble.py`, and the
benchmark/documentation boundary modules. Tests also import the façade
directly. The new declaration module has no reverse imports and should remain
free of those consumers.

The record declarations describe streams whose operational owners remain
distributed: database owns history/failure/archive streams, loop owns several
runtime/finalization streams, the evaluator owns evaluator-result logging,
meta-prompt owns prompt history, and strict JSONL owns quarantine writing.
Readers, generated inventory anchors, paper validators, restore handling, and
prompt/report consumers remain coupled to the façade's returned shape. This
seam must not be widened to move any of those behaviors without a new
characterization and coupling review.

## Verification and unverified evidence

The lane characterization report records 24 passing characterization tests and
50 passing tests across the narrow artifact/documentation boundary set. The
independent verifier ran compilation, whitespace, focused JSONL/artifact tests
(`86 passed in 5.49s`), retained-AST checks, public/private identity checks,
schema-output comparisons, and façade-durability ownership checks; all passed.
The verifier classified this as current-checkout, lane-scoped evidence because
the worktree is shared and the support module is untracked.

Still unverified for the repository as a whole are the required full
non-integration suite, package/build gate, CLI/paper/documentation/artifact
gate aggregation, provider/native sandbox/OCI behavior, distributed/resume
behavior, and end-to-end runtime behavior. Those limits do not invalidate the
narrow declaration-seam PASS.

## Rollback and acceptance boundary

Rollback is local and reversible: restore the two inline declaration literals
in `_run_artifact_schema_without_inventory`, remove the import and the new
data-only module, and retain the façade's existing `_quarantine_record`
behavior. No rollback was performed. Because the checkout is shared and dirty,
rollback must be scoped to these exact paths and must not reset or clean
unrelated work.

Acceptance for this lane is satisfied by the independent verifier's exact
schema equality, unchanged ownership and validator/redaction/JSONL behavior,
successful focused tests, and static boundary checks. Repository-level gates
remain a separate root-coordinator responsibility.
