# PR packet — `core-prompt`

- Primary: `libreevolve/core/prompt.py`; proposed branch `refactor/core-prompt`; external PR not opened.
- Allowlist: `libreevolve/core/prompt.py`, `libreevolve/core/prompt_context_policy.py`, `tests/core/test_prompt_characterization.py`.
- Scope: context-policy validation only; rendering, RNG, feedback/failure rendering, prompt history, and mutable `last_*` side channels remain in `PromptSampler`.
- Dependency PR: `core-loop`. Uniform measurements: 11,952/11,251 → 8,134/7,683 primary physical/nonblank LOC; support 4,260/3,997; decision proxy 1,870 → 1,128.
- Evidence: focused `390 passed`; reload/sentinel/exception identity, path safety, AST/import checks pass; verifier `01a06a72-9795-7fe1-b247-2c60c1fdac70` PASS.
- Preserved contract: deterministic RNG draw order, policy hashes, exception identity, bounded context, and metadata overwrite behavior. No unrelated paths staged.
- Risks/rollback: revert only policy delegation/support module after preserving prompt-history fixtures; provider/live behavior remains unverified.
