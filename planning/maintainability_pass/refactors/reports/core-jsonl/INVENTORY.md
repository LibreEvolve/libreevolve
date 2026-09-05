# core/jsonl.py inventory

Evidence state: source-derived, read-only Wave 1 report. No production changes are authorized by this report.

## Measured shape

- 971 physical LOC; 871 logical LOC.
- 43 functions, two exception classes, no class methods.
- Aggregate branch/control proxy 172; maximum per-function proxy 14.
- Nine standard-library dependencies plus `libreevolve.core.redaction`.
- Inbound fan-in: 18 Python files (11 production callers and seven test files).

The largest symbols are `_retained_quarantine_text` (66 LOC),
`_validate_quarantine_retention_metadata` (60),
`repair_trailing_partial_jsonl` (60), `_non_finite_details` (53), and
`_validate_strict_json_value` (51).

## Contract anchors

The module is a de facto public compatibility API for finite strict JSON,
duplicate-name rejection, JSONL iteration, managed append, torn-tail repair,
quarantine records, locking, and redacted diagnostics. Managed append currently
serializes before touching the stream, creates parents, acquires accepted and
quarantine locks in sorted order, repairs a prior partial tail, writes a
newline-terminated record, flushes, and fsyncs.

`artifact_schema.py` owns record schema/version validation; `jsonl.py` does not
enforce those markers. `database.py` still manually parses `history.jsonl`, and
archive sequence ownership remains a database concern.

## Proposed seam and boundaries

Extract only durable storage mechanics to a future `jsonl_storage.py`: lock
ordering/platform locks, parent preparation, append/fsync, atomic JSON replace,
and torn-tail inspection/truncation. Keep strict value validation, duplicate
name parsing, quarantine schema, redaction, retention policy, and compatibility
wrappers in `jsonl.py`.

The proposed dependency direction is callers -> `jsonl.py` compatibility API ->
`jsonl_storage.py` -> standard library. Any database or artifact-schema handoff
must be separately authorized.
