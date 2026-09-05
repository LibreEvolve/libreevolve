# PR packet — `core-database`

- Primary: `libreevolve/core/database.py`; proposed branch `refactor/core-database`; external PR not opened.
- Allowlist: `libreevolve/core/database.py`, `tests/population/test_database.py`.
- Status: characterization/no-op; no implementation writer or support module authorized. Dependency PR: `core-loop`.
- Measurements: 11,841 physical / 11,137 nonblank LOC, 309 functions, 6 classes, 47 methods; no post-refactor measurement because no production change.
- Evidence: Windows Python 3.12 module `292 passed, 3 skipped` and contract subset `4 passed, 291 deselected`, exit 0; verifier `01a06fa4-e0a3-7d43-aaea-9ea8dddc5a9d` accepted the no-op.
- Preserved contract: admission, archive persistence, restore, sampling, migration, and serialized ordering remain together. Residual append-failure atomicity is open.
- Risks/rollback: no production patch to roll back; retain characterization and dirty-path ledger. No unrelated paths staged.
- Boundaries: no implementation/runtime/PR evidence; future writer requires ownership and atomicity design.

