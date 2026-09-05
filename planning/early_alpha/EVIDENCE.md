# Alpha implementation evidence

All results here are development-worktree evidence until a candidate commit and
installed-wheel verification are recorded. No real-provider experiment has run.

## Initial integration

- Baseline commit: 462443213b7391a6622d539a0564f14444e0cfce.
- Windows Python 3.12 `tests/test_alpha_onboarding.py` plus
  `tests/test_alpha_bin_packing.py`, with `--noconftest --tb=short -q`:
  53 passed, exit 0 (session 79688).
- CLI characterization plus onboarding: 17 passed, 2 skipped, exit 0
  (session 17312; before subsequent report integration).
- `alpha init runs/alpha-smoke-task-v2 --model account-model --token-price 10
  --budget-usd 1`: exit 0. Placeholder is offline-only.
- `alpha doctor runs/alpha-smoke-task --offline`: exit 0; contract preflight
  does not itself evaluate seed correctness.
- Initial actual engine run `runs/alpha-seed-smoke`: no valid programs,
  `malformed_metrics`. This exposed undeclared diagnostics in the example.
  Failure artifacts are preserved locally. Fixture schema and actual evaluator
  regression were repaired; this run is not counted as successful.
- `run runs/alpha-smoke-task-v2 --max-generations 0 --run-name
  alpha-seed-smoke-v2 --progress`: exit 0 (session 36431). Evaluated one valid
  seed, fitness 0.8016472203157172, exported best.py and best_workspace/seed.py.
  No provider calls, so this establishes engine integration only.

## Additional development checks

- CLI, CLI characterization, onboarding, bin-packing, agent docs and roadmap
  corpus checks: 343 passed, 6 skipped, exit 0 (session 4706).
- Actual `show runs/alpha-seed-smoke-v2`: exit 0 (session 37464), valid archive
  selection, artifact validation and primary workspace output.
- `tests/test_alpha_workflow.py`: 1 passed, exit 0 (session 7145): actual engine
  seed evaluation, HTML report, independent training/held-out export, byte-level
  exported SHA-256 verification, existing-destination protection, zero calls.
- Windows installed-alpha CI workflow prepared; no remote execution claimed.
- Final agent verification: example 45 passes (actual evaluator included),
  reliability 31 passes plus 47 existing regressions, reporting 32 passes
  including minimal environment and child-process cleanup. All writers stopped.
- Coordinator reliability run: 31 passed, exit 0 (session 98932).
- Coordinator report + workflow: 33 passed, exit 0 (session 98171).
- Actual CLI report and export: exits 0 (sessions 38612 and 16774).
  Exported SHA-256 a37e6880acd271cbb5ad50b781d95b8e71d9fbbde15701505738d62f51d06507
  matches verification.json; both training and held-out correctness pass.
  This is the unchanged baseline, not an optimization claim.
- Broader core-loop + reliability suite is running under session 55841;
  no terminal result recorded yet.
- Clean Windows virtual environment prepared outside checkout at
  C:/Users/timot/AppData/Local/Temp/libreevolve-alpha-wheel.NUDGXn/venv.

## Pending

Full relevant regressions; package artifact hashes; clean installed-wheel
workflow; CI result for candidate commit; three real-model runs under an
authorized aggregate cap; independent developer trials.
