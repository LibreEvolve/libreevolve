# `cli.py` refactor

Primary path: `libreevolve/cli.py`.
Support paths: `libreevolve/core/run_inspection.py`,
`tests/test_cli_characterization.py`.

Design: extract read-only history/manifest inspection, archive selection,
diagnostics, validation, and bounded source rendering into a Click-free
inspection module. Keep Click commands/options, terminal formatting, exit
translation, artifact export, rollback, and a compatibility legacy source
anchor in `cli.py`; runtime status rendering remains owned by the support
module.

Measurements compare the current checkout with `HEAD`; `cli.py` and loader
were already dirty at the Wave 0 snapshot, so these are not a clean PR diff
measurement. The verifier therefore retains a conditional attribution label.

| metric | before (`HEAD`) | after primary | after with support |
|---|---:|---:|---:|
| physical LOC | 2,842 | 1,571 | 3,040 |
| logical non-comment LOC | 2,622 | 1,437 | 2,779 |
| functions | 103 | 61 | 117 |
| classes | 2 | 1 | 4 |
| decision proxy | 489 | 205 | 486 |
| largest function | `run`, 152 | `run`, 152 | `run`, 152 |

The combined increase reflects a mechanical seam extraction with explicit
result typing and compatibility wrappers; it is not evidence of a net
complexity reduction. Current static ownership checks show no Click or write
ownership in the support module and preserved `_iter_history_records` and
`_validator_boundary_artifact_summary` anchors.

Evidence: `271 passed, 6 skipped` for characterization plus existing CLI
tests, README boundary `4 passed`, and compile/ownership checks. Sequential
writer `01a06afc-5d03-7b21-8b36-60e0c5bdc9a9` added only the compatibility
source anchor. Fresh verifier `01a06fcd-6417-7233-9dbf-b28509dd70a2` returned PASS for
that correction, with dirty-checkout attribution still conditional. No PR was
opened.
