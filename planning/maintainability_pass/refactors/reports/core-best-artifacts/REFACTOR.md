# `core/best_artifacts.py` refactor disposition

Primary path: `libreevolve/core/best_artifacts.py`.

Related paths inspected: `libreevolve/cli.py`,
`libreevolve/core/artifact_schema.py`, `libreevolve/core/jsonl.py`, and the
`Program`/`CandidateWorkspace` workspace materialization code.

Disposition: intentional no-op for this wave. No production writer is
authorized and this documentation lane made no production or test changes.
No PR was opened.

## Static/source-derived evidence

The existing inventory measures `best_artifacts.py` at 465 physical LOC and
409 logical LOC, with 23 top-level functions and one class. It is a cohesive
but failure-sensitive export boundary. It currently owns:

- materialization of the canonical `best.py` and `best_workspace/` pair;
- static-file sidecar generation and source-copy handling;
- run-relative path and link/junction preflight;
- file bytes/SHA-256 and workspace tree records;
- structured success/failure records and bounded redaction;
- replacement staging, rollback, backup preservation, and cleanup; and
- attachment of export records to runtime artifact pointers.

Source inspection also finds a second implementation in `cli.py`. Its private
`_write_best_artifacts`, static-sidecar, preflight, path-record, tree-hash,
error, rollback, cleanup, and manifest-update helpers duplicate the core
implementation. The CLI imports names from `best_artifacts.py` but later
defines same-named helpers, so moving only one group would leave ambiguous
ownership and creates a compatibility risk for callers and source-anchor
checks. The CLI must first become a thin Click/error-translation adapter that
delegates to one canonical exporter.

The artifact-schema dependency is also not a cosmetic import boundary.
`artifact_schema.py` owns `RUN_ARTIFACT_NAMES`, generated run-artifact
inventory, non-JSONL artifact policy, schema pointers, and validation of the
manifest/runtime contract. `best.py` and `best_workspace` are explicit entries
in that inventory, with writer, runtime-pointer, and show/restore anchors.
Extracting record builders or path metadata before that contract handoff is
settled could create a second schema authority, change pointer shapes, or make
the exporter and CLI validate different versions. The current artifact-schema
lane is itself reconciling a narrow record-contract seam, so this lane treats
that contract as unstable rather than assuming the in-progress seam is an API.

`Program`/`CandidateWorkspace` remain responsible for primary-file selection,
workspace canonicalization, and static-file metadata. The exporter must not
reselect a primary file. `jsonl.py` remains responsible for strict JSON
loading/dumping and storage semantics; those responsibilities should not be
silently absorbed by an artifact-export helper.

## Why a writer is unsafe now

1. **Duplicate CLI ownership.** There is no single writer owner. A partial
   extraction could make `run` use the CLI implementation while direct core
   callers use the core implementation, preserving behavior only by accident.
   The two implementations already differ in manifest-read/error handling and
   helper provenance, so a mechanical move cannot be treated as behaviorally
   neutral.

2. **Schema authority is upstream.** The export record, runtime pointers,
   artifact inventory, and non-JSONL validation must agree. Until the
   artifact-schema lane publishes a stable contract and compatibility anchors,
   moving record construction would cross the ownership boundary and could
   invalidate `show`, restore validation, paper validators, or generated
   inventory checks.

3. **The transaction is a coupled unit.** Staging `best_workspace` and
   `best.py`, replacing existing targets, handling links/junctions, preserving
   backups, and cleaning temporary paths are one rollback protocol. Splitting
   these helpers without crash/fault-injection evidence could leave a mixed
   pair or discard the only recoverable backup.

4. **The characterization boundary is incomplete.** The existing focused
   tests do not establish native junction/locking behavior, crash recovery,
   concurrent exports, cross-device rename behavior, aborted-run handling, or
   parity of all hash scopes and runtime consumers. Those are required before
   changing the shared export transaction.

## Future seam boundary

The next implementation should be one explicitly coordinated handoff, with a
single writer and a separate verifier:

| Owner | Boundary to preserve |
|---|---|
| `Program` / `CandidateWorkspace` | Primary-file choice, canonical workspace files, static-file metadata, and source-copy validation. |
| `core/best_artifacts.py` | One canonical export engine for pair materialization, sidecar creation, path/link safety, hashes, structured records, rollback, cleanup, and runtime attachment. |
| `core/artifact_schema.py` | Versioned record/inventory/policy authority and the expected runtime/show/restore pointers; it must not be redefined in the exporter. |
| `core/jsonl.py` | Strict JSON serialization and file durability behavior used by manifest updates. |
| `cli.py` | Click options, terminal formatting, user-facing error translation, and delegation to the canonical exporter; no duplicate physical writer or rollback helpers. |

A future writer may introduce a small pure support module for an agreed,
versioned record-contract or path-inspection seam, but only after the schema
owner and CLI owner sign off on the exact API and compatibility re-exports.
The writer must preserve `files`, `primary_file`, `static_files`, reserved-path
policy, `best.py` compatibility, complete workspace authority, rollback
records, and runtime pointer shapes.

## Open findings and follow-up

The lane has no new `FINDINGS.jsonl` row because this report-only change is
within the existing finding set. Relevant open coordination findings are:

- `MP-011`: oversized modules require measured seam extraction with focused
  and module-level evidence;
- `MR-002`: every lane needs an explicit writer, support-path allowlist,
  verifier, and dependency handoff; and
- the characterization report's open platform/transaction cases listed above.

Before implementation, resolve the duplicate CLI owner, freeze the
artifact-schema contract, add the missing transaction/platform cases, and
rerun both direct exporter and CLI characterization on the resulting
compatibility surface. An independent verifier must inspect ownership and
source anchors in addition to running tests.

## Rollback / no-op disposition

The safe rollback for this wave is to retain the existing implementations and
make no production move. That is the selected disposition: there is no new
support module, no changed import surface, no changed runtime artifact shape,
and no rollback operation required. A later failed extraction must be reverted
as one allowlisted change across the canonical exporter and CLI delegation
boundary; the old CLI implementation must not be deleted until the replacement
passes the compatibility and fault-injection gates.
