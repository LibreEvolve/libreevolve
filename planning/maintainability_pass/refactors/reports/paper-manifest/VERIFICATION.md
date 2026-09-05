# `paper_manifest.py` verification

Historical verifier: `01a06a28-5194-7bc3-ab5d-abe86f7d267c` (independent,
non-authoring). Historical verdict: `FAIL`; it identified MR-007.

Current fresh verifier: `01a06fa4-c3c2-7d41-bfb0-aba5f355cfa9`
(independent, non-authoring). Scoped verdict: `PASS`; the full module also
passes.

Evidence:

- The current focused selection passes on native Windows Python 3.12.10:
  `9 passed, 708 deselected in 38.35s`; `py_compile` passes.
- The current full source-stable collection contains 717 tests and completed
  `717 passed in 1:18:55` with exit 0. The earlier interrupted run remains
  inconclusive and is not reused.
- The historical verifier reproduced `invalid_pdf_structure` with
  `target_preserved: False` because `os.replace()` occurred before
  `_validate_local_pdf()`, and reproduced matching-invalid-cache acceptance.
- The current fresh verifier confirmed validation of the temporary file before
  replacement and validation of matching existing files before
  `verified_existing`. It also confirmed valid-cache/download compatibility,
  cleanup, redacted diagnostics, compilation, and exact two-file scope.

The paper-lane repair gate is satisfied by the focused fresh review and the
complete module result. The repair is not a maintainability extraction or a
claim of repository-wide readiness; the current full non-integration rerun is
tracked separately as a repository-level gate.
