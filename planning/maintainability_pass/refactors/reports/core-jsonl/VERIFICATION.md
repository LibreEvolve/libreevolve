# core-jsonl verification

## Verdict

**CONDITIONAL**

The narrow storage extraction is behaviorally compatible on the current
Windows Python 3.12 environment and keeps the JSONL policy in `jsonl.py`. The
verdict remains conditional because `jsonl.py` and the focused test module
were already dirty at the Wave 0 baseline, the new storage file is untracked,
and the existing repair sequence is not crash-atomic.

## Scope and diff inspection

Verification was performed against `HEAD`
`7983544e28e478eb6a0f5c35e4af5a86b125cea2` in the shared checkout. The scoped
tracked diff for `libreevolve/core/jsonl.py` is 10 insertions and 4 deletions:
it adds the `_jsonl_storage` import and changes only
`_append_serialized_jsonl_line` to delegate while passing `jsonl.open` and
`jsonl.os.fsync` as injectable callables. Its private façade signature is
unchanged.

`libreevolve/core/jsonl_storage.py` is a new 39-line untracked module. Its
only production operation is `append_serialized_jsonl_line`: open in append
mode with `encoding="utf-8"`, write the supplied serialized line plus one
newline, flush, and call `fsync` on the file descriptor. AST inspection found
no schema, JSON parser, redaction, quarantine, locking, repair, or CLI
implementation in that module; its only non-future imports are `os`,
`collections.abc`, `pathlib`, and `typing`.

The façade still owns and visibly retains:

- strict finite-value and duplicate-object-name validation, including
  `StrictJsonlError` and its message/exception policy;
- quarantine record construction/validation, retention modes, and redaction;
- `_locked_jsonl_paths`, platform lock acquisition/release, sorted lock
  ordering, and release-error precedence; and
- `repair_trailing_partial_jsonl`, including truncation, repair diagnostics,
  and quarantine ordering.

The append wrapper preserves the existing monkeypatch seams by explicitly
passing the façade’s `open` and `os.fsync` objects into the raw primitive.

## Executed evidence

All commands below were run in the current checkout with
`/mnt/c/Windows/py.exe -3.12`:

- `py_compile` for both production files: **PASS** (exit 0).
- `git diff --check -- libreevolve/core/jsonl.py libreevolve/core/jsonl_storage.py`:
  **PASS** for the tracked diff. Because Git does not include an untracked
  file in `git diff`, a separate trailing-whitespace audit of
  `jsonl_storage.py` also passed.
- `-m pytest tests/core/test_jsonl.py --tb=short`: **62 passed in 4.18s**;
  collection ran on `platform win32`.
- Raw-storage AST/import boundary smoke: **PASS**. The function’s operations
  are limited to the injected open, write, flush, `fileno`, and injected
  fsync calls.
- Injected open/write/flush/fileno/fsync ordering smoke: **PASS**; the
  serialized value was passed through unchanged except for the one newline,
  and failures remain caller-visible.
- Path/encoding/reference compatibility smoke: **PASS**. A `Path` call
  through the façade produced byte-for-byte the same result as the original
  inline implementation for UTF-8 `é`; a string path also worked through the
  raw helper. On Windows both preserve the original platform newline
  translation (`os.linesep`, currently `\r\n`).
- Focused artifact-schema import smoke: **PASS**; the schema module imported,
  its canonical manifest constant remained intact, and its JSONL family
  declaration remained callable.

The focused test file includes the write, partial-write, flush, fsync,
truncate, quarantine-append, accepted-append, lock-acquire, lock-release,
ordering, invalid-UTF-8, retention, and repair fault-injection cases. No
tests or production files were edited by this verifier.

## Dirty-worktree attribution

The Wave 0 ledger records `libreevolve/core/jsonl.py` and
`tests/core/test_jsonl.py` as pre-existing dirty paths. The baseline also
records an empty normalized semantic diff, but that does not make a shared
dirty file independently attributable to this verifier. The current scoped
`jsonl.py` patch contains only the expected delegation change; the new
`jsonl_storage.py` is an untracked current-worktree addition. The 62-test
result therefore verifies the current combined checkout, not an isolated
commit or clean-HEAD patch. No reset, cleanup, staging, commit, or unrelated
path modification was performed.

## Risks and unverified boundaries

- `jsonl_storage.py` intentionally provides file flush/fsync only. It does
  not fsync the parent directory, validate that `line` is JSON, enforce a
  newline-free input, acquire locks, or provide crash-atomic repair.
- The pre-existing repair sequence truncates and fsyncs the accepted stream
  before appending its quarantine diagnostic. A later diagnostic append or a
  crash between those operations can leave repair state and its diagnostic
  out of sync. The extraction leaves this known non-atomic behavior
  unchanged; it must not be reported as crash-atomic durability.
- The tests exercise the current Windows host and injected failure paths.
  They do not establish crash recovery, all-platform lock/newline behavior,
  provider, distributed, or end-to-end runtime evidence.

The narrow raw-storage seam is suitable for the current refactor boundary,
subject to the attribution and durability qualifications above.
