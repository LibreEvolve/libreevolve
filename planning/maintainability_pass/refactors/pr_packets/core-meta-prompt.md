# PR packet — `core-meta-prompt`

- Primary: `libreevolve/core/meta_prompt.py`; proposed branch `refactor/core-meta-prompt`; external PR not opened.
- Allowlist: `libreevolve/core/meta_prompt.py`, `tests/core/test_meta_prompt.py`.
- Status: blocked/no-op; no writer authorized. Dependencies: `core-prompt`, `core-loop` lifecycle handoff.
- Measurements: 919 physical / 836 nonblank LOC, 3 classes, 29 top-level functions, 15 methods; no post-refactor value.
- Evidence: Windows focused `94 passed in 1.25s`; verifier `01a06fa4-e97e-7833-a413-f4e8718b7db3` accepts the blocked disposition.
- Preserved contract: prompt identity/selection/scoring, JSONL/quarantine, redaction, rollback, sync/async joins, and exception aliases remain together.
- Risks/rollback: no production patch; future work requires lifecycle and persistence ownership tests. No unrelated paths staged.

