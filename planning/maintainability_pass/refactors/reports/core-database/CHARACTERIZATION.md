# core/database.py characterization

Evidence state: requested characterization cases green; production lane remains
closed because no database implementation writer is authorized.

The population database suite collected 295 cases and now reports `292 passed,
3 skipped` on the Windows Python 3.12 environment. The previously failing
artifact-inventory source-anchor case was corrected by restoring thin CLI
compatibility seams; it now passes. These are focused reports, not a full
repository pass.

Existing coverage spans admission, invalid evaluations, sampling exclusion,
local RNG, cursor/full restore, JSONL and archive-event schemas, UTF-8 and
duplicate-name rejection, sequence/cell/restore errors, manifest recovery,
cleanup, links, and migration. Required additions remain: the full admission
flag matrix, restore equivalence/next-admission sequencing, stable serialized
bytes, missing archive references, and append-failure atomicity. Native
Windows junction/locking behavior remains unverified.

The initial two-child review was rejected by the thread limit. A retry completed
both children. Child A added four test-only cases and the targeted run reports
`4 passed, 291 deselected`; Child B independently confirmed the archive seam and
its append-atomicity/restore ownership risks. The full focused run is now
`292 passed, 3 skipped`; the artifact-inventory anchor passes after the CLI
compatibility wrappers were restored. No implementation writer is authorized.
