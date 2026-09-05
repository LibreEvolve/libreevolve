# PR packet — `benchmark-matrix`

- Primary: `libreevolve/problems/benchmarks/matrix_results.py`; proposed branch `refactor/benchmark-matrix`; external PR not opened.
- Allowlist: `libreevolve/problems/benchmarks/matrix_results.py`, `libreevolve/problems/benchmarks/matrix_artifact_identity.py`, `tests/test_matrix_results.py`.
- Scope: deterministic artifact identity and canonical JSON helpers; result schema, rights/publication policy, and runtime evidence remain in the façade.
- Dependency PRs: none. Uniform measurements: 7,534/7,164 → 7,443/7,079 primary physical/nonblank LOC; support 132/119; decision proxy 1,329 → 1,304.
- Evidence: focused `145 passed`; verifier `01a06a07-ad4d-7641-aa55-fe6b0e6690c9` CONDITIONAL for shared-dirty attribution; compile/import checks pass.
- Preserved contract: artifact hashes, canonical serialization, evidence labels, source rights, and publication boundaries. No unrelated paths staged.
- Risks/rollback: remove façade delegation/support module only; clean attribution requires isolated PR verification.
