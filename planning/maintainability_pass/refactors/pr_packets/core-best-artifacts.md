# PR packet — `core-best-artifacts`

- Primary: `libreevolve/core/best_artifacts.py`; proposed branch `refactor/core-best-artifacts`; external PR not opened.
- Allowlist: `libreevolve/core/best_artifacts.py`, `tests/core/test_best_artifacts.py`.
- Status: no-op/dependency handoff; no writer authorized. Dependencies: `core-loop`, `core-artifact-schema`, and an authorized CLI duplicate-owner handoff.
- Measurements: 465 physical LOC; no post-refactor value because no production change.
- Evidence: Windows focused `5 passed, 2 skipped`, compile pass; fresh verifier `01a06fa4-e367-7830-877a-fdc499cb07cf` confirms distinct CLI/core exporters and accepts the no-op.
- Preserved contract: coupled `best_workspace`/`best.py` replacement, rollback, cleanup, primary-file selection, runtime pointers, and schema parity remain untouched.
- Risks/rollback: no production patch; future work needs fault-injection, junction/locking, concurrency, and parity tests. No unrelated paths staged.

