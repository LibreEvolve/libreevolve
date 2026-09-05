# `tools/paper_manifest.py` refactor

Status: MR-007 behavior-fix prerequisite verified; the later maintainability
extraction remains deferred until a separate seam is authorized.

Primary path: `libreevolve/tools/paper_manifest.py`.

## Current evidence

- The test-only characterization wave added seven cases covering deterministic
  report ordering, timeout and force validation, HTTP/read failure cleanup and
  preservation, claim spans, and case-folded duplicate paths.
- Native Windows Python 3.12.10 reports `7 passed in 73.06s` for those seven
  selected cases (`708 deselected`). AST checks and a small direct harness also
  passed.
- The MR-007 repair adds two regressions for target preservation and structural
  validation of matching existing caches. Native Windows Python 3.12.10
  reports `9 passed in 38.35s` for the selected rehydrate/diagnostic cases;
  `py_compile` passes.
- The complete file contains 717 collected tests. The source-stable Windows
  run completed `717 passed in 1:18:55` with exit 0.
- Historical verifier `01a06a28-5194-7bc3-ab5d-abe86f7d267c` returned FAIL and
  reproduced both defects. Writer `01a06a9b-b505-77d1-a33c-71b8fb56fad1`
  implemented the bounded repair in the two allowed paths. Fresh verifier
  `01a06fa4-c3c2-7d41-bfb0-aba5f355cfa9` reports focused PASS: temporary and
  existing-file validation order, valid-cache/download compatibility,
  cleanup, compile, diff scope, and focused tests. The complete module gate
  independently passes with exit 0.

## Dependencies and authorization gate

The existing lane dependency is `benchmark-matrix`; the paper-manifest lane
must continue to treat benchmark-matrix and rights authorities as separate
handoffs. The immediate dependency was MR-007. The coordinator-approved
contract now specifies that downloaded temporary files are structurally
validated before replacement, matching malformed existing caches are classified
stale and enter the existing redownload path, and failed downloads preserve the
target and clean temporary files. The complete module gate and fresh
independent focused review now pass; the repair is considered verified. The
later extraction remains a separate dependency because it would be a broader
design change.

The proposed data-driven sidecar specification/runner seam remains deferred.
Validator order, public names,
monkeypatch seams, claim inventories, Appendix A handling, and PDF/source
special cases must remain in place for the later writer and verifier.

## Required tests before writer authorization

The approved behavior fix must pass regressions that prove:

1. An invalid downloaded PDF is rejected before `os.replace()` and a valid
   existing target remains byte-for-byte preserved.
2. A structurally invalid existing PDF is not reported as
   `verified_existing`, even when its byte count and SHA match the expected
   metadata.
3. A structurally valid existing PDF retains the intended reuse/status path.
4. A valid replacement still commits successfully, while failed download/read
   paths retain their documented cleanup and diagnostic behavior.

Then complete the active `tests/test_paper_manifest.py` collection on an
isolated clean baseline with native Windows Python 3.12. Repeat AST/compile
checks and the independent direct harness. The fresh verifier confirmed the
repair-focused contract, and the full module result is `717 passed in 1:18:55`
with exit 0.

## No-op rollback

The repair is confined to `libreevolve/tools/paper_manifest.py` and
`tests/test_paper_manifest.py`; no branch, commit, or PR exists. Rollback is
limited to those two MR-007 hunks after preserving the shared dirty-path
ledger. Do not stage or revert unrelated shared-checkout work. If the complete
module gate or fresh review fails, keep the extraction deferred and retain the
diagnostic evidence.
