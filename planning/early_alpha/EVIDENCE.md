# Early alpha implementation evidence

This record separates source-checkout, installed-package, provider, CI, and
external-usability evidence. The packaged candidate is
`8621ea69b4d8bc6c2b5aafec75b8a90056a6a338`; the code is merged at
`a906b53e138c5598edc40c12154f2d5f9635d6df`.

## Follow-up source reliability fix

Local source commit `2b7b7e30` fixes a POSIX verification cleanup race: a
worker that exits after spawning a child is now observed without reaping its
process-group leader, the inherited session is killed, and group disappearance
is boundedly awaited. The focused descendant-cleanup test passes all 3
parameters, and the combined alpha report/reliability subset passes 62 tests
with 1 Windows-only skip. These are source-checkout results on Linux Python
3.12.3 with temporary test dependencies. A fresh Linux Python 3.12 package
build from exact follow-up HEAD
`ba7a4a71e473110e3f1a7eea989812dca45cee64` is preserved under
`dist/ba7a4a71/` with these SHA-256 values:

- follow-up wheel: `f02467d24bda40b9d0dcaa976ba14b0a69e0e8f85b4306f1460b24f421b4a677`
- follow-up sdist: `eb5bbaaf85b423d3e2df494ec7a4fe7f607a9c663c0b816a73741b27854a73ce`
- follow-up provenance: `8be0f3cee6f1d1ccbb4986da72f9cf198cb0b2df1e52c976bb9d8babbe081028`

The follow-up wheel and sdist each contain all 455 tracked package files, and
a clean target-directory install passed the documented provider-free
`--help`, `alpha init`, offline doctor, zero-generation run, show, HTML report,
and verified export smoke. This is Linux package evidence; the Windows package
smoke below is now also recorded for the follow-up. The follow-up has not been
pushed.

The same follow-up wheel (`f02467d24bda40b9d0dcaa976ba14b0a69e0e8f85b4306f1460b24f421b4a677`)
was installed with Windows Python 3.12.10 into the clean venv
`C:\Users\timot\AppData\Local\Temp\libreevolve-alpha-winverify.byuiqP`.
`pip check`, `libreevolve --help`, and `python -m libreevolve --help` passed.
From a separate fresh smoke directory
`C:\Users\timot\AppData\Local\Temp\libreevolve-alpha-win-smoke.1xxHEH`,
`alpha init`, offline `alpha doctor`, a zero-generation run, `show`, HTML
`report`, and verified `export` all exited 0. The exported solution hash was
`a37e6880acd271cbb5ad50b781d95b8e71d9fbbde15701505738d62f51d06507`; training
and held-out correctness were both true with scores `0.8016472203157172` and
`0.8121645796064401`. This remains retained-seed evidence with zero provider
attempts, not model-guided improvement evidence.

## Cross-platform cleanup follow-up

Local source commit `b215993954368b1d357d3e19b9b94ed0e6140b5b` extends the
verification cleanup fix. Darwin workers use a non-reaping `kqueue` exit
observer because the supported macOS Python path does not expose
`waitid(..., WNOWAIT)`; POSIX platforms that cannot provide a safe observer now
fail closed instead of falling back to reaping `poll()`. POSIX `killpg()` and
an assigned Windows job-close failure are retained as `cleanup_failed` evidence
after best-effort root cleanup. The five alpha regression files passed 123 tests
with 1 Windows-only skip in 1607.69 seconds on Linux Python 3.12.3; the focused
report/workflow subset passed 32 tests with 1 Windows-only skip.

The exact follow-up source commit was packaged with Windows Python 3.12 under
`dist/b2159939/`:

- wheel: `ae7d8283f895f079927fa058ad3c95a8e45be2a05a69ee3d617d3704aff645c4`
- source distribution: `f1ca2f489cafc54f8c7491cf16994fe329f5f9a6ed5064f5b95fdccb54292d2a`
- provenance: `82f93ed276913c9b2ba4d7355e22443539d6a886c480f4593590b242b1b45df1`

The provenance records git commit `b215993954368b1d357d3e19b9b94ed0e6140b5b`
and a clean tracked tree. Wheel and sdist each contain all 455 tracked package
files. A fresh Windows Python 3.12.10 venv
`C:\Users\timot\AppData\Local\Temp\libreevolve-alpha-b215-winverify` passed
`pip check`, both CLI help entrypoints, and the installed provider-free
workflow from fresh smoke directory
`C:\Users\timot\AppData\Local\Temp\libreevolve-alpha-b215-win-smoke`:
`alpha init`, offline `alpha doctor`, a zero-generation run, `show`, HTML
`report`, and verified `export` all exited 0. The export hash was
`a37e6880acd271cbb5ad50b781d95b8e71d9fbbde15701505738d62f51d06507`; training
and held-out correctness were true with scores `0.8016472203157172` and
`0.8121645796064401`; provider attempts were 0. This remains retained-seed
evidence, not model-guided improvement evidence.

## Current exact-head package smoke

The current exact source/CI-anchor commit is
`2a472c2d231fe4157f2c6afcb3e309978ccde4f8`; it contains the portable cleanup
fix plus restore-intent CI path anchors. Windows Python 3.12 built one wheel
and one source distribution under `dist/2a472c2d/`:

- wheel: `d19ef828de690f233b51719a5f4e7e48a06a186711b03f40ea2a734fedcf91ea`
- source distribution: `c1e94cf512943ddad51b6fa1baabf8377ffe0f95901b422055961d26d241cad9`
- provenance: `a8fb46be74e083dccfb84b24072861d9a5a1dfb96588a12d7045f356d1d598ca`

The provenance records that exact commit and a clean tracked tree; both
artifacts contain all 455 tracked package files. A separate clean Windows
Python 3.12.10 venv
`C:\Users\timot\AppData\Local\Temp\libreevolve-alpha-2a472-winverify`
passed `pip check`, `libreevolve --help`, `python -m libreevolve --help`, and
the fresh provider-free workflow in
`C:\Users\timot\AppData\Local\Temp\libreevolve-alpha-2a472-win-smoke`:
`alpha init`, offline `alpha doctor`, zero-generation `run`, `show`, HTML
`report`, and verified `export` all exited 0. The export hash was
`a37e6880acd271cbb5ad50b781d95b8e71d9fbbde15701505738d62f51d06507`; training
and held-out correctness were true with scores `0.8016472203157172` and
`0.8121645796064401`; provider attempts were 0. This is retained-seed package
evidence, not model-guided improvement evidence.

## Implemented workflow

- The supported example is deterministic bin packing with an intentionally
  improvable next-fit Python seed, fixed training and held-out cases, strict
  correctness checks, and evaluator data outside the editable workspace.
- `alpha init` creates a bounded task; `alpha doctor` performs provider/config
  preflight; `run --progress`, `show`, `alpha report`, and `alpha export` cover
  the first-run workflow.
- Reports include baseline/best quality, correctness, code changes, run state,
  stopping reason, provider/model identity, token usage, and estimated cost.
  Estimated cost is explicitly not a hard billing guarantee.
- Cancellation, interruption, persistence failures, prompt compatibility,
  artifact inspection, and source-selection ambiguity have dedicated tests and
  documentation. Restore documentation explicitly excludes pending-work resume.
- The prepared developer trial materials contain no participant results; no
  participants have been contacted.

## Source-checkout verification

- Exact-candidate non-integration suite: 6,640 passed, 27 skipped, 3
  deselected, exit 0. This is not installed-package or provider evidence.
- Recorded alpha suite: 124 passed, exit 0.
- Recorded broad loop/reliability suite: 496 passed, 2 skipped, exit 0.
- Secret baseline review and configured all-files scan passed without weakening
  detector settings. No provider calls were made by these checks.

After the POSIX cleanup follow-up, a fresh Linux Python 3.12.3 source-copy run
passed the alpha workflow and reliability/report subset: 122 passed, 1
Windows-only skip, plus the end-to-end workflow test (123 collected). The
documentation, release-provenance, release-checklist, and CI-boundary subset
at the tracked follow-up checkout passed 26/26. The source-copy run was made
outside the Windows-mounted checkout so subprocess cleanup timing was measured
on a native Linux filesystem; it does not change the declared Windows support
claim.

## Exact-head package and installed verification

Built with Windows Python 3.12 from the clean tracked exact candidate:

- wheel: `libreevolve-0.1.0-py3-none-any.whl`
  - SHA-256: `8271db759a94a5a637539a65d2d9138966a6958c520feaf4f0801e9a3ba7871f`
- source distribution: `libreevolve-0.1.0.tar.gz`
  - SHA-256: `b5626d897273527e2378236a4fc432d4a8448ebc14fc6559884fee2d905a830d`
- `release_artifact_provenance.json`
  - SHA-256: `bc35ef56f6c50ff234e01d4d7783bbe91188dc7fb27d05924b284fe43a876548`

The wheel and source distribution each contain all 455 files under the
`libreevolve/` package tree. In the isolated venv, both
`libreevolve --help` and `python -m libreevolve --help` passed.

A fresh Windows Python 3.12 venv without system packages installed the exact
wheel and its declared dependencies; `pip check` passed. The documented
provider-free workflow then passed end to end: CLI help, `alpha init`, offline
`alpha doctor`, zero-generation run, `show`, HTML report, and verified export.
The exported code passed independent training and held-out correctness checks:

- exported code SHA-256: `a37e6880acd271cbb5ad50b781d95b8e71d9fbbde15701505738d62f51d06507`
- training score/correctness: `0.8016472203157172` / `true`
- held-out score/correctness: `0.8121645796064401` / `true`
- provider attempts: `0`

This is retained-seed evidence only; it does not demonstrate model-guided
improvement.

## Remote CI and external acceptance gates

PR #1 is merged, but post-merge runs `34019445028` (Tests) and `34019445056`
(Installed Alpha) failed before job execution because GitHub reported recent
account payment failure or an insufficient spending limit. Passing CI remains
unproved; this is an account gate, not a code-failure diagnosis. Automatic
push, pull-request, and scheduled triggers are temporarily disabled while that
account issue is unresolved; both workflows remain available by manual
dispatch and must be re-enabled before claiming a release gate.

The following acceptance evidence is still missing:

1. Three independent real-provider experiments under an explicitly authorized
   aggregate cap, with all attempts, failures, usage, cost estimates, and
   independent exported-candidate reevaluations retained.
2. A passing exact-head CI run after the GitHub billing gate is resolved.
3. Observed usability results from 3–5 developers who did not build the
   product. The trial packet and record template are prepared, but no contact
   or feedback is authorized or recorded.

## Current classification

The evidence supports an engineering preview. It does not support a
trial-ready or release-ready alpha, and no broad improvement claim is made.

## Current branch and boundary regression follow-up

The implementation and package-validation tip is
`eb4d5eaec8fe0a460c7e121d2b9bcbf1a78a0b06`, and the clean local worktree has a
later documentation-only reconciliation commit. The private
`LibreEvolve/codex/early-alpha-20260905` remote branch remains at the
implementation tip; the local documentation commit is intentionally not
pushed. The branch is not merged into the private `master`
(`dbf8b210d7743694ef90a0f7fc0942782dc40cbc`).
The exact Windows package smoke remains intentionally tied to source/CI-anchor
commit `2a472c2d231fe4157f2c6afcb3e309978ccde4f8`, whose artifacts and
provenance are recorded above; later commits in this branch are documentation
only.

A full exact-current native Linux non-integration diagnostic collected 6,670
tests (6,667 selected) but reached its 5,400-second timeout at 84% before
pytest could emit a final summary. Its five failures were boundary checks: the
diagnostic environment selected pypdf 6.17 despite the declared `<6.11` bound,
and the paused workflow lacked a textual marker for the retained weekly
source-refresh cron. With the declared pypdf range and commit `eb4d5eae`, the
14 direct boundary tests passed in 8.24 seconds and the three affected
paper-manifest acceptance tests passed in 365.46 seconds. This does not replace
the earlier completed exact-candidate full-suite result above, and no claim of
a completed full current-head suite is made.

## Current-head alpha workflow rerun

From the clean local documentation tip `6fba9e27bde5738f808109d7ab9fc808b89c481c`,
the five alpha bin-packing/onboarding/reliability/report/workflow files were
rerun in an isolated Linux Python 3.12.13 environment with the declared
development dependencies (including `pypdf==6.10.2`). The command

```text
/tmp/libreevolve-alpha-check/bin/pytest tests/test_alpha_bin_packing.py tests/test_alpha_onboarding.py tests/test_alpha_reliability.py tests/test_alpha_report.py tests/test_alpha_workflow.py --tb=short -q
```

completed with 123 passed and 1 Windows-only skip in 814.46 seconds. This is
source-checkout, provider-free regression evidence; it does not replace the
missing real-provider cohort, independent usability trial, or CI evidence.

## Current-tip Windows package smoke

Windows Python 3.12.10 built a fresh wheel and source distribution from
`c2a0f8cade18402b75046d487ee0bf81dd449471` (the current local tip when the
build started) under `dist/c2a0f8ca/`. Linux Python regenerated provenance so
Git could record the commit; the tracked source tree was clean. The artifact
hashes are:

- wheel: `a3e4ac5c62f897bd8fe9f7a900877b1aa4bc6493f4c7612e471813b1c9e4d17a`
- source distribution: `6798eeb3e7cd75fa3dfee5c275411265786265fd0620d5add30f465a4d535955`
- provenance JSON: `b1ba3f7631a5da6e9598d808d5350c4854ee0589bcfeb110f57d37d79d9325d9`

Both distributions contain all 455 tracked `libreevolve/` files. A clean
Windows Python 3.12.10 virtual environment with system packages disabled
installed the wheel; `pip check`, both help entrypoints, `alpha init`, offline
`alpha doctor`, a zero-generation run, `show`, HTML `report`, and verified
`export` all passed from a fresh smoke directory. The installed package used
`pypdf==6.10.2`. The exported seed retained independent correctness on 55
training and 30 held-out cases (scores `0.8016472203157172` and
`0.8121645796064401`), with code SHA-256
`a37e6880acd271cbb5ad50b781d95b8e71d9fbbde15701505738d62f51d06507` and
verification JSON SHA-256
`0fcb136c10cb2da3feb699fc11e2075e8e7f02fef07ee4c1ade793168ca90516`.
Provider attempts were zero; this remains retained-seed evidence, not
model-guided improvement evidence.

## Separate credential-bearing diagnostic

An exploratory one-generation command was run separately from the documented
zero-generation smoke to check failure persistence. The Windows host inherited
an existing `OPENAI_API_KEY` (the value was never inspected), so this command
made one OpenAI Responses attempt against the placeholder model
`offline-model`. The provider returned authentication failure 401; the run
retained its redacted `llm_calls.jsonl` and `failure_history.jsonl` records,
used zero input/output tokens and zero estimated cost, and performed no retry.
The run is not part of the real-model cohort and is not improvement evidence;
the documented seed-only smoke still recorded zero provider attempts.
