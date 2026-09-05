# PR packet — `core-jsonl`

- Primary: `libreevolve/core/jsonl.py`; proposed branch `refactor/core-jsonl`; external PR not opened.
- Allowlist: `libreevolve/core/jsonl.py`, `libreevolve/core/jsonl_storage.py`, `tests/core/test_jsonl.py`.
- Scope: move one already-serialized append/write/flush/fsync primitive; validation, locking, repair, quarantine, and durability policy remain in the façade.
- Dependency PR: `core-loop`. Uniform measurements: 971/871 → 977/877 primary physical/nonblank LOC; support 39/33; decision proxy 128 → 128.
- Evidence: focused `62 passed`, compile/import and AST boundary checks pass; verifier `01a06a52-807e-7a62-879f-7894ec8c55f7` CONDITIONAL.
- Preserved contract: encoding, line bytes, flush/fsync order, schema/redaction and deterministic repair behavior. MR-009 non-crash-atomic repair remains open.
- Risks/rollback: revert only the delegation/support module after preserving dirty status. No unrelated paths staged.
- Boundaries: current-tree attribution conditional; package, live, provider, distributed, and end-to-end evidence unverified.
