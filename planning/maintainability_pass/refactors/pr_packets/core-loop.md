# PR packet — `core-loop`

- Primary: `libreevolve/core/loop.py`
- Proposed branch: `refactor/core-loop`; external PR: not opened (publication not authorized).
- Allowlist: `libreevolve/core/loop.py`, `libreevolve/core/loop_models.py`, `tests/core/test_loop_characterization.py`.
- Scope: extract frozen value records only; orchestration, queues, persistence, hooks, and RNG ownership stay in the façade.
- Dependency PRs: none. Baseline HEAD: `7983544e28e478eb6a0f5c35e4af5a86b125cea2`.
- Uniform measurements: 49,605/47,918 → 49,548/47,867 primary physical/nonblank LOC; support 77/67; decision proxy 8,315 → 8,315. Full measurements are in the lane report.
- Evidence: characterization and module regression `465 passed, 2 skipped`; Windows Python 3.12 compile/AST and verifier `01a06a0e-41ef-7393-a012-c8da889ab98c` PASS.
- Risks/rollback: preserve private aliases and value identity; remove only the delegation and `loop_models.py` after preserving the dirty-path ledger. No unrelated paths staged.
- Boundaries: focused/static evidence only; provider, live runtime, distributed, and end-to-end behavior unverified.
