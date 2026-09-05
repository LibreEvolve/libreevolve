# `cli.py` verification

Historical verifier: `01a06a0d-1dda-76f0-b1f3-d8519535e035` (independent,
non-authoring). Verdict: `CONDITIONAL` because the shared checkout retains unrelated dirty
paths and exact fresh-diff attribution cannot be established from Git status
alone.

Current fresh verifier: `01a06fcd-6417-7233-9dbf-b28509dd70a2` (independent,
non-authoring). Verdict: `PASS` for the compatibility-anchor correction, with
the same dirty-attribution qualification.

Evidence:

- `tests/test_cli_characterization.py tests/test_cli.py`: `271 passed, 6
  skipped in 49.15s`.
- The generated artifact-inventory anchor test: `1 passed, 294 deselected in
  1.34s`.
- `py_compile` passed for `libreevolve/cli.py` and
  `libreevolve/core/run_inspection.py`.
- README example-runs boundary: `4 passed`; the compatibility anchor at the
  CLI source boundary is behavior-neutral and has zero runtime references.
- Current CLI focused suite remains `271 passed, 6 skipped`; exporter-related
  definitions remain identical after line-ending normalization.
- AST/source ownership checks passed: the new module has no Click dependency,
  write-like filesystem calls, artifact export, or rollback; CLI commands,
  decorators, export/rollback ownership, `_iter_history_records`, and
  `_validator_boundary_artifact_summary` remain available.

The CLI retains pre-existing mixed line endings; `git diff --check` warnings
from those CRLF records were not normalized. Full-suite, provider, distributed,
and end-to-end runtime evidence remain unverified.
