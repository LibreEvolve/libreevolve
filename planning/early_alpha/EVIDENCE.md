# Alpha implementation evidence

Development-worktree and installed-wheel evidence are separated below.
No real-provider experiment has run.

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
- Broader core-loop + reliability suite completed under session 55841:
  496 passed, 2 skipped in 704.55 seconds.
- Clean Windows virtual environment prepared outside checkout at
  C:/Users/timot/AppData/Local/Temp/libreevolve-alpha-wheel.NUDGXn/venv.

## Packaged candidate 97a5a822

Commit: 97a5a822acfa9084355fdc6f2faf707e9bc63e1b. Built wheel and source
distribution, verified all 455 package files in both and wheel bytes against
source; provenance records the commit and clean tracked tree.

- Wheel SHA-256: 2004e589a651ec61acef873288939f8e6d7266dea59eb995568d218374ca6829.
- Sdist SHA-256: f8d05093d65bd70a4eaf137347b32abff8702dbf1dd6c2f1a03813db8f2ebbe1.
- Artifacts: dist/97a5a822, including release_artifact_provenance.json.
- External Windows venv above: installed wheel, verified site-packages import,
  pip check, both help entrypoints, offline init/doctor/run/report/export.
  Actual run session 66857 exited 0; runs/installed-head and verified-head
  retained under the external temp root. Both correctness splits passed with
  zero provider attempts. This is seed-only evidence, not model discovery.
- Private branch CI runs 33989147661 and 33989147632 failed before job steps.
  Check 101368106016 reports account payments/spending-limit failure. These
  are not passing checks and do not identify a code regression.

## Follow-up working-tree validation

Uncommitted doctor/export fixes were independently re-reviewed without residual
blocking defects. Doctor reports disabled checks honestly; export requires a
choice when workspace and history differ and hashes the actual exported bytes.
Oversized finite budgets now fail with an actionable error.

- Session 2935: 41 passed in 8.88 seconds (onboarding/workflow, AGENTS docs,
  roadmap scan, README map and docs reader paths).
- Session 41945: workflow regression passed in 5.26 seconds, additionally
  checking explicit history selection and CRLF-only equivalent workspace bytes.
- Full non-integration session 95463 remains running. Source edits occurred
  during it, so its eventual result cannot prove an exact final candidate.
- Fresh complete alpha tests, session 49879: 124 passed in 70.61 seconds.
- All 3,005 new secret-scan findings were independently classified: 3,000
  explicit SHA-256 fields, two resolvable commit references, three synthetic
  redaction-test strings. Exact reviewed baseline additions were applied and
  stale line metadata refreshed. Configured all-files hook session 87454
  exited 0: passed, no findings, no baseline modification, all candidate files
  tracked. Detector/filter settings were not weakened.
- Installed-alpha CI now records provenance bound to GITHUB_SHA, checks the
  installed dependency graph, and preserves run/report/export evidence alongside
  distributions. YAML structure parses locally; this is not executed CI proof.
- Session 8671: 17 AGENTS-document and release-provenance tests pass.

## Pending

Final-candidate full regressions, secret review, new package artifacts and clean
installed-wheel verification covering follow-up changes, passing candidate CI,
three real-model runs under an authorized aggregate cap, independent developer
trials. The result remains an engineering preview.
