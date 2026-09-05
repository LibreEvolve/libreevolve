# Core prompt lane verification

Verdict: PASS

This is an independent verification of the final current shared-checkout
state. The requested compile, focused tests, import-order/reload checks,
exception and sentinel identity checks, path-safety checks, and AST/import
dependency checks pass. The support module's WSL file-mode observation is
reported separately and is not a semantic failure.

## Scope and evidence boundary

Inspected the current diff and these lane records:

- `libreevolve/core/prompt.py`
- `libreevolve/core/prompt_context_policy.py`
- `INVENTORY.md`, `CHARACTERIZATION.md`, `REFACTOR.md`, and the prior
  `VERIFICATION.md` under this report directory

The current tracked diff is a narrow façade extraction (`6 insertions,
3,824 deletions` in `prompt.py`); the support module is currently untracked
in the shared checkout. This verifier changed only this `VERIFICATION.md`.
No production files, tests, coordination files, Git staging state, commits,
branches, or PRs were changed.

Evidence here is static inspection, compilation, and focused Python-process
behavior. It is not provider, OCI, security-sandbox, distributed, package
publication, or end-to-end host/provider evidence.

## Required commands and results

- `/mnt/c/Windows/py.exe -3.12 -m py_compile libreevolve/core/prompt.py libreevolve/core/prompt_context_policy.py` — PASS.
- `/mnt/c/Windows/py.exe -3.12 -m pytest tests/core/test_prompt.py tests/core/test_prompt_characterization.py --tb=short` — PASS: `390 passed in 0.57s` on Windows Python 3.12.10.
- `git diff --check -- libreevolve/core/prompt.py` — PASS, exit `0`.
- `git diff --no-index --check -- /dev/null libreevolve/core/prompt_context_policy.py` — no diagnostics; exit `1` is the expected status for an untracked-file comparison.

## Import, reload, identity, and path checks

A fresh-process Python harness run with
`/mnt/c/Windows/py.exe -3.12 - <<'PY' ... PY` produced:

- `support-first: PASS`: importing `prompt_context_policy` does not import
  `prompt`; reloading the support module preserves `PromptTemplateError`, the
  `_VALIDATED_CONTEXT_POLICY_PATHS_UNSET` sentinel, and the validator's
  keyword-default identity.
- `facade-first/reload: PASS`: façade and support share the same
  `PromptTemplateError`; support reload preserves that identity, the sentinel
  identity, and the already-imported façade validator's defaults. The unsafe
  traversal call after reload produces the expected message:
  `prompt context_policy.context_source_paths[0] must be a safe
  problem-relative context path: problem.context_files path must be a safe
  problem-relative label: '../escape.py'`.
- `path safety/messages/dedup: PASS`: direct support labels and the façade's
  `validate_direct_context_files` rejected traversal, dot-segment, absolute,
  drive-qualified, backslash, and repeated-separator cases; policy traversal
  and required-file traversal produced their expected error messages; safe
  duplicate `src/main.py` entries were deduplicated.
- `AST/import safety and exception ownership: PASS`: neither module contains
  `_configure_prompt_context_dependencies` or
  `_configure_prompt_template_error`; the support module does not import the
  façade; the support module has exactly one `PromptTemplateError` class
  definition and the façade has none.

These checks specifically cover both support-first and façade-first imports,
support reload after façade import, exception identity, sentinel identity,
direct-path/traversal safety, error-message compatibility, and removal of the
former callback/configurator dependencies.

## WSL file-mode observation

`stat` reports the untracked support file as mode `777`, and
`git diff --no-index --summary -- /dev/null
libreevolve/core/prompt_context_policy.py` reports create mode `100755`.
The same WSL-mounted-workspace behavior applies to other newly created
support files, while the repository has `core.filemode=false`. The support
file has no whitespace diagnostics, and this observation does not alter the
semantic PASS above. Tracked-mode normalization remains a checkout/staging
hygiene task outside this verifier's authorization.

## Limitations

The focused suite does not establish full-suite, clean-checkout, native-only,
provider, OCI, security-sandbox, distributed, package-build, or end-to-end
runtime behavior. Dirty-checkout attribution and final integration gates are
also outside this lane report. No commit, branch, external PR, or merge was
created.
