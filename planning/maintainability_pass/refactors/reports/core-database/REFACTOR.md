# core-database refactor decision

Evidence state: characterized; no production writer authorized.

## Decision

Do not perform a production extraction in this wave. `ProgramDatabase` is a
compatibility façade over admission, archive/history persistence, restore,
manifest assembly, cleanup, and sampling-facing state. Those responsibilities
cross several existing authorities, so a mechanical move would make ownership
ambiguous and could change externally visible sequencing or serialized data.

The narrow seam identified for a future design review is an
`archive_boundary.py` adapter/codecs layer. It could normalize admission
results, immutable archive snapshots, archive events, and archive-state restore
validation while leaving the façade and the existing population owners in
control. This is a proposal only; no such module or production patch is
authorized by this record.

## Measured shape

The existing inventory measured `libreevolve/core/database.py` at 11,841
physical LOC and 11,137 logical/nonblank LOC, with 309 module functions, six
classes, and 47 methods. `ProgramDatabase` is approximately 1,008 LOC. The
largest reported hotspots are candidate-runner declaration validation (389
LOC), startup manifest assembly (319 LOC), language-policy validation (266
LOC), and archive/restore summary validators.

The module has 11 direct importers and 115 distinct `config.<attribute>`
references across 154 uses. These measurements are source/inventory evidence;
they are not a claim that a split would reduce total complexity.

## Ownership and dependency edges

- `ProgramDatabase` remains the compatibility façade and currently spans
  admission, persistence, restore, manifests, and cleanup.
- `libreevolve/population/islands.py` owns cursors, migration, and sampling.
- `libreevolve/population/map_elites.py` owns cell identity, replacement, and
  eligibility.
- `libreevolve/population/program.py` owns identity, lineage, and workspace
  normalization.
- The lane is adjacent to the loop, JSONL, and artifact-schema lanes. The
  orchestration plan records `core-loop` as the current dependency; any future
  archive seam must also account for JSONL durability and artifact-schema
  contracts without creating a circular ownership boundary.
- The database has 11 direct production importers, so every proposed public or
  private symbol move requires a caller and compatibility-anchor audit.

## Contracts that must remain in the façade boundary

Any future implementation must preserve, with tests and an independent review:

- `VALID_THRESHOLD = 0.0` as a pre-admission eligibility gate only;
- the distinct `cell_admitted`, `elite_retained`, `search_state_changed`, and
  `sampling_eligible` outcomes;
- cursor advancement only after a search-state change;
- canonical migration identifiers;
- archive replay as audit-only rather than a second source of admission truth;
- existing identity, lineage, workspace-normalization, serialization, restore,
  manifest, cleanup, and failure behavior;
- ordering and failure semantics for JSONL/archive writes, including the
  append-failure atomicity boundary.

## Acceptance criteria before authorizing a writer

The following must be resolved before a production writer is assigned:

1. Produce a caller/ownership map that identifies every moved symbol and keeps
   island, MAP-Elites, and program semantics in their current owners.
2. Add executable characterization for the complete admission-flag matrix,
   restore equivalence and next-admission sequencing, stable serialized bytes,
   missing archive references, and append-failure atomicity.
3. Define whether stable bytes are a compatibility contract; if they are,
   compare exact bytes before and after the seam.
4. Run the focused database suite and relevant JSONL, artifact-schema, loop,
   and CLI boundary tests after any implementation, followed by the required
   repository non-integration suite.
5. Obtain an independent verifier that checks AST/import ownership, public and
   private compatibility anchors, serialization/restore behavior, and the
   dirty-path attribution before reporting a pass.

## Rollback and no-op disposition

The safe action for this wave is a no-op: retain `database.py` unchanged and
record the seam as unimplemented. There is no database production patch to
roll back. If the seam is later authorized, isolate its changes, stage only the
database seam and explicitly approved support/tests, and make rollback consist
of removing the new adapter/codecs module and reverting only that lane while
preserving unrelated dirty work.

## Unverified gates

The focused characterization result does not establish any of the following:

- full repository non-integration or integration-suite success;
- package/build, CLI, paper, documentation, artifact, or diff-hygiene gates;
- native Windows junction and locking behavior;
- the complete admission-flag matrix, restore equivalence/next-admission
  sequencing, stable serialized bytes, missing-reference behavior, or
  append-failure atomicity;
- runtime, end-to-end, provider, distributed, or hostile-code sandbox
  behavior.

No refactor, full-suite pass, or runtime claim is made by this report.
