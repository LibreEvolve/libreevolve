# PR packet — `core-budget`

- Primary: `libreevolve/core/budget.py`; proposed branch `refactor/core-budget`; external PR not opened.
- Allowlist: `libreevolve/core/budget.py`, `libreevolve/core/budget_contract.py`, `tests/core/test_budget.py`.
- Scope: pure declarations, validation, limit precedence, and controller-event application; clocks, replay, persistence, async reservation, provider/evaluator accounting stay in the façade.
- Dependency PR: `core-loop`. Uniform measurements: 1,497/1,385 → 548/510 primary physical/nonblank LOC; support 1,070/984; decision proxy 220 → 21.
- Evidence: focused `150 passed`; compatibility/signature/identity checks pass; verifier `01a06a63-4b58-7661-a978-272442b9961e` CONDITIONAL only for WSL/untracked mode 100755.
- Preserved contract: public/private aliases, event order, budget precedence, and RNG/accounting ownership. No unrelated paths staged.
- Risks/rollback: revert only the budget delegation/support module; normalize file mode only through an authorized scoped staging operation.
