# `core-jsonl` implementation record

Primary path: `libreevolve/core/jsonl.py`.

Support path: `libreevolve/core/jsonl_storage.py`.

Status: the narrow raw-storage seam is implemented in the current checkout.
Independent verifier `01a06a52-807e-7a62-879f-7894ec8c55f7` returned
`CONDITIONAL`; the raw operation boundary and focused compatibility checks pass,
while shared-dirty attribution and the pre-existing non-atomic repair sequence
remain qualified. This record does not claim an isolated clean patch or
full-suite success.

## Exact seam

The implementation extracts only the low-level operation that appends one
already-serialized JSONL line:

```text
open(path, "a", encoding="utf-8")
write(line + "\\n")
flush()
fsync(file descriptor)
```

`jsonl_storage.append_serialized_jsonl_line()` owns those raw file operations
and accepts optional `open_fn` and `fsync_fn` callables for platform and fault
injection. The private `_append_serialized_jsonl_line()` wrapper remains in
`jsonl.py` with its existing signature and delegates while explicitly passing
`jsonl.open` and `jsonl.os.fsync`. This preserves the façade's existing
monkeypatch and exception-observation seams.

The inventory's broader proposal (lock ordering, parent preparation, atomic
JSON replacement, and torn-tail inspection/truncation) was not moved in this
implementation. It remains deliberately outside the helper.

## Changed paths

- `libreevolve/core/jsonl.py`: add the private storage import and replace the
  inline append body with the compatibility delegation.
- `libreevolve/core/jsonl_storage.py`: new 39-line raw append module with no
  JSON parser, schema validation, quarantine, redaction, locking, repair, or
  CLI behavior.

No test or other production path is part of this implementation seam.

## Measurements

The inventory measured the façade before this seam at 971 physical LOC and
871 non-comment LOC, with 43 functions, two exception classes, and a decision
proxy of 172. A current source count gives the following implementation
shape; the current counts are measurements of the shared checkout, not an
independent verifier result.

| metric | before façade | after façade | support module | combined after |
|---|---:|---:|---:|---:|
| physical LOC | 971 | 977 | 39 | 1,016 |
| logical non-comment LOC | 871 | 874 | 33 | 907 |
| functions | 43 | 43 | 1 | 44 |
| classes | 2 | 2 | 0 | 2 |
| decision proxy | 172 | pending independent measurement | pending | pending |
| largest symbol | `_retained_quarantine_text`, 66 LOC | pending independent measurement | pending | pending |

The façade retains the original control-policy code; the support module adds
no policy branch. The final complexity and largest-symbol measurements remain
pending independent verification.

## Preserved contracts and ownership

- Strict finite JSON validation, duplicate-object-name rejection, JSONL
  parsing, exception types, and error-message bounding remain in `jsonl.py`.
- Managed append still serializes before touching the stream, prepares parent
  directories in the façade, acquires accepted and quarantine locks in stable
  sorted order, repairs a prior partial tail, and then performs the
  newline-terminated append followed by flush and file `fsync`.
- `_locked_jsonl_paths`, platform-specific lock acquisition/release, reverse
  release order, and release-error precedence remain unchanged in the façade.
- Quarantine diagnostic construction and validation, redaction, retention
  modes (`full`, `redacted`, `hash_only`, and `off`), and quarantine stream
  ownership remain in `jsonl.py`.
- `repair_trailing_partial_jsonl()` still owns torn-tail inspection,
  truncation, repair diagnostics, and the ordering between accepted-stream
  repair and diagnostic append. The existing non-atomic repair/fsync gap
  remains open as finding `MR-009`; this seam does not make repair
  crash-atomic.
- `strict_json_dump()` still owns temporary-file replacement and best-effort
  parent-directory `fsync`; those operations were not moved to the helper.
- `artifact_schema.py` remains the record schema/version authority, while
  `jsonl.py` remains schema-agnostic. `database.py`'s manual history parsing
  and archive-sequence ownership remain outside this lane.

## Dependency edges

The inventory records 18 Python inbound users of `jsonl.py` (11 production
callers and seven test files). The new helper has one direct production
importer: the private compatibility façade. The intended direction is:

```text
callers -> jsonl.py compatibility API -> jsonl_storage.py -> standard library
                                      \-> redaction policy
```

No caller was redirected to the support module. No database, artifact-schema,
feedback, or locking ownership was transferred.

## Rollback

The scoped rollback is to restore the four-line inline body of
`_append_serialized_jsonl_line()` and remove its `_jsonl_storage` import from
`jsonl.py`; then remove only the new `jsonl_storage.py` path. A rollback must
preserve the Wave 0 dirty-worktree ledger and must not reset, clean, or alter
unrelated user changes.

## Evidence and limitations

- A current Windows Python 3.12 run of
  `tests/core/test_jsonl.py` reports **62 passed in 4.07s**. This is focused
  evidence from the combined shared checkout, not proof of an isolated patch
  and not verifier approval.
- The characterization set covers serialization, duplicate names, non-finite
  and cyclic values, quarantine/redaction, retention, repair, locking,
  multi-process writers, and injected write/flush/fsync/truncate/append
  failures. The tests preserve the current post-write failure behavior; they
  do not close `MR-009`.
- The full `tests/ -m "not integration"` suite has not passed as a valid,
  source-stable final gate for this lane,
  and no claim is made for package/build, CLI, paper, provider, distributed,
  crash-recovery, or end-to-end runtime behavior.
- Native cross-platform lock/newline/directory-fsync behavior and genuinely
  crash-atomic repair plus quarantine remain unverified.
- The working tree is shared and `jsonl.py` and `tests/core/test_jsonl.py`
  were already dirty at the Wave 0 baseline. The focused result therefore
  cannot attribute every byte of those files to this implementation.
