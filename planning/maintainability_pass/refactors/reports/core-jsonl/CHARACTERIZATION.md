# core/jsonl.py characterization

Evidence state: characterization complete; implementation barrier remains
conditional on the explicit durability seam and independent contract review.

Existing focused tests cover normal serialization/append, duplicate names,
non-finite and cyclic values, quarantine/redaction, repair, cleanup, and
multi-process writers. The focused JSONL test module has 38 tests, but the WSL
Python environment has no pytest. A standard-library smoke check observed
normal rows, fail-closed rejection of an unterminated tail, opt-in repair, and
one quarantine diagnostic; this is not a pytest pass.

The test-only specialist added 472 lines covering fault injection for write,
flush/fsync, replace, truncate, and lock failures; exact prior-content
preservation; invalid UTF-8; retention cutoffs; and repair/quarantine ordering.
The focused Windows Python 3.12 run first reported `58 passed in 4.68s`; a
supplemental specialist then added four edge cases for quarantine-append,
accepted-append, partial-write, and body/release failure precedence. The
current focused run reports `62 passed in 4.46s`, and the test module compiles
cleanly. The cases confirm current post-write failure behavior and retain the
known non-atomic repair-fsync gap as an open finding.

Native Windows lock/newline/directory-fsync behavior, crash-atomic repair plus
quarantine, and provider/distributed/end-to-end evidence remain unverified.

The lane is not ready for an implementation writer until the coupling review
selects a minimal seam that does not silently change the durability boundary.
