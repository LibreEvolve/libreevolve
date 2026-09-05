# tools/paper_manifest.py characterization

Evidence state: the MR-007 cache-contract repair is implemented and verified;
the later maintainability extraction remains deferred.

The authorized test-only wave added seven cases to
`tests/test_paper_manifest.py` for deterministic report ordering, timeout and
force validation, HTTP/read failure cleanup and preservation, claim spans, and
case-folded duplicate paths. The MR-007 repair then added two regression cases:
invalid downloaded PDFs are validated before replacement, and matching
structurally invalid existing PDFs are not accepted as `verified_existing`.
The current focused selection reports `9 passed, 708 deselected in 38.35s` on
Windows Python 3.12.10; compilation and diff-scope checks also pass. The
complete current source-stable module run reports `717 passed in 1:18:55` with
exit 0.

The prior independent reviewer reproduced a critical defect: rehydration called
`os.replace()` before structural PDF validation, so an invalid download could
replace an existing target. A matching invalid existing PDF could also be
classified `verified_existing` from byte count/SHA alone. The authorized
behavior-fix writer moved validation before replacement and added existing-cache
validation. A fresh non-authoring verifier reports focused PASS, and the
complete 717-test file now passes.
