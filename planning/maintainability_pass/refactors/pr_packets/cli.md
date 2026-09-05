# PR packet — `cli`

- Primary: `libreevolve/cli.py`; proposed branch `refactor/cli`; external PR not opened.
- Allowlist: `libreevolve/cli.py`, `libreevolve/core/run_inspection.py`, `tests/test_cli_characterization.py`.
- Scope: read-only history/manifest inspection extraction; Click parsing, formatting, export, rollback, and compatibility wrappers remain in the façade.
- Dependency PRs: `core-loop`, `core-config`, `problem-loader`. Uniform measurements: 2,842/2,622 → 1,571/1,437 primary physical/nonblank LOC; support `run_inspection.py` 1,469/1,342; decision proxy 499 → 200.
- Evidence: combined CLI `271 passed, 6 skipped`; README boundary `4 passed`; verifier `01a06fcd-6417-7233-9dbf-b28509dd70a2` CONDITIONAL for shared-dirty attribution; CLI help exits 0.
- Preserved contract: run/show output, history/manifest schema, export/error behavior, and source compatibility anchors. No unrelated paths staged.
- Risks/rollback: remove inspection delegation/support file only; clean attribution requires an isolated PR diff.
