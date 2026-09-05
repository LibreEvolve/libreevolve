# PR packet — `problem-loader`

- Primary: `libreevolve/problems/loader.py`; proposed branch `refactor/problem-loader`; external PR not opened.
- Allowlist: `libreevolve/problems/loader.py`, `libreevolve/problems/context_loader.py`, `tests/core/test_loader.py`.
- Scope: context ingestion, manifest diagnostics, excerpts, hashing, and lazy PDF normalization; problem/validator/metric/seed/workspace/path policy remains in the façade.
- Dependency PRs: `core-config`, `core-yaml-utils`. Uniform measurements: 3,005/2,802 → 1,418/1,305 primary physical/nonblank LOC; support 1,658/1,550; decision proxy 533 → 318.
- Evidence: loader/boundary focused `279 passed, 8 skipped`; verifier `01a069f4-5cec-7bc2-bb61-dc6d2204337a` PASS; compile/import and path-policy checks pass.
- Preserved contract: falsey non-mapping rejection, manifest schema, error provenance, path safety, lazy PDF behavior, and primary-file selection. No unrelated paths staged.
- Risks/rollback: remove context-loader delegation/support module only; full repository/provider/live evidence remains separate.
