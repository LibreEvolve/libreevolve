# core/best_artifacts.py inventory

Evidence state: measured/read-only Wave 1 report.

Measured shape: 465 physical LOC, 409 logical LOC, 23 top-level functions, one
class, six runtime imports, and complexity proxy 61. The largest symbols are
the rollback path (70 LOC), the transactional writer (66), the workspace tree
record (36), and the path/error records.

The module owns canonical `best.py` and `best_workspace/` export, static-file
sidecars, path/link preflight, byte/tree hashes, structured export errors,
rollback, cleanup, and runtime attachment. `Program`/`CandidateWorkspace` own
primary-file and static-file canonicalization; database owns run collision and
manifest lifecycle; artifact_schema owns schema authority. CLI currently has a
duplicate exporter and needs a separate handoff.

Any future seam must preserve `files`, `primary_file`, `static_files`, reserved
path policy, `best.py` compatibility, complete workspace authority, rollback,
and runtime pointer shapes. Do not reselect a primary file in the exporter.
