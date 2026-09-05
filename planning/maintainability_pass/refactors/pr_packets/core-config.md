# PR packet — `core-config`

- Primary: `libreevolve/core/config.py`; proposed branch `refactor/core-config`; external PR not opened.
- Allowlist: `libreevolve/core/config.py`, `tests/core/test_config.py`.
- Status: no-op; no writer authorized. Dependencies: `core-yaml-utils`, `problem-loader`.
- Measurements: 2,776 physical / 2,592 nonblank LOC, 86 functions; no post-refactor value because no semantic seam was authorized.
- Evidence: Windows focused `639 passed in 2.79s`; verifier `01a06fa4-ec39-7cb2-b357-a0fd6b25f14d` accepts the no-op; no semantic config diff, five pre-existing mixed-EOL warnings.
- Preserved contract: validation mutation order, evaluator/candidate-runner/prompt/backend/plugin/runtime policy, normalized fields, and manifest serialization remain together.
- Risks/rollback: no production patch; future work requires caller-by-caller ownership and comparable measurements. No unrelated paths staged.

