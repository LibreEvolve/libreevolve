# `core/best_artifacts.py` verification

Fresh independent non-authoring verifier: `01a06fa4-e367-7830-877a-fdc499cb07cf`.
Verdict: **no-op accepted / not ready for writer**. Windows focused tests pass
`5 passed, 2 skipped`; compilation passes. Runtime/source review confirms the
CLI and core exporters remain distinct, so the duplicate-owner handoff is still
required.

Verdict: `NO-OP / NOT READY FOR WRITER`.

This report records documentation and verification evidence only. No
production code, tests, matrix row, registry entry, or external PR was changed
by this lane.

## Test-derived evidence

- Current direct Windows Python 3.12 run:
  `py -3.12 -m pytest tests/core/test_best_artifacts.py --tb=short` — **5
  passed, 2 skipped** in 0.22s.
- The two skips are the parameterized linked-target cases; symlink creation
  was unavailable on the host. Their behavior is characterized in the test
  source but is not a passed platform proof.
- The existing characterization run for
  `tests/test_cli_characterization.py tests/test_cli.py` reported **271
  passed, 6 skipped**. This is prior green evidence for the duplicate CLI
  consumer, not evidence that the duplicate ownership is safe to refactor.
- A fresh combined rerun in this checkout did not collect the CLI tests: the
  unrelated in-progress `core/prompt` seam currently raises an
  `IndentationError` in `libreevolve/core/prompt_context_policy.py` during
  import. Therefore the prior CLI result remains historical/test-derived
  evidence, and current end-to-end CLI verification is unverified until that
  separate lane is repaired.

The direct tests cover canonical pair records, repeated-export determinism and
sorted tree-hash input, runtime pointer attachment, static source-copy
sidecars, source-copy failure cleanup, and the linked-target rejection path
(skipped on this host). They do not prove the unexecuted platform and failure
cases listed below.

## Static/source-derived evidence

- `best_artifacts.py` contains the canonical-looking export API and the full
  staging/replace/rollback/cleanup protocol.
- `cli.py` independently contains same-purpose writer, sidecar, preflight,
  record, error, rollback, cleanup, and manifest-update helpers. Its imports
  from the core module do not remove the later same-named definitions, so a
  partial move would leave two possible owners.
- `artifact_schema.py` lists `best.py` and `best_workspace` in
  `RUN_ARTIFACT_NAMES`, generates their non-JSONL artifact contracts, and
  records writer/runtime/show-restore anchors. That module is the schema and
  inventory authority; the export lane must consume a settled contract.
- The inventory reports 465 physical LOC, 409 logical LOC, 23 top-level
  functions, and one class. These are measurements of the current source, not
  a claimed post-refactor improvement.

## Unverified gates and open risks

The following remain unverified and block a writer:

- native junction and file-lock behavior;
- crash/fault-injection behavior across the two-artifact replacement;
- concurrent export and cross-device rename behavior;
- aborted-run and backup-preservation behavior;
- complete hash-scope parity across runtime, CLI, and schema consumers;
- a single-owner CLI delegation test after duplicate helpers are removed; and
- a stable artifact-schema contract with compatibility/source-anchor checks.

Full non-integration suite, package/build checks, and runtime/end-to-end
provider evidence are outside this report's green focused-test result and are
not claimed here.

## Acceptance for a future writer

The next writer must first obtain an explicit CLI/schema handoff, limit its
support paths to the agreed allowlist, preserve compatibility exports and
runtime pointer shapes, and add characterization for the missing transaction
cases. An independent non-authoring verifier must then run the direct exporter
and CLI suites, compile/import and ownership checks, generated artifact
inventory/schema checks, and the relevant module suite. Until those gates are
green, the no-op disposition is the rollback state.
