# LibreEvolve trial-ready local alpha — 2026-09-07

Classification: **trial-ready alpha for the documented Linux/WSL Luna/high
workflow**, not a release-ready product. The installed final package completed
a real-model experiment and independently verified its exported improvement.
External 3–5 developer usability results remain explicitly pending. CI is
excluded by the user's instruction; no green candidate CI is claimed.

## Candidate and artifacts

Packaged source commit: `8fdbf5132ed24b2960bde4c9f7acf14b28aadf59`.
Branch: `codex/early-alpha-20260905`, isolated checkout
`/mnt/c/users/timot/Documents/projects/domains/libreevolve-alpha`.
The shared dirty `libreevolve.com` checkout and unrelated `uv.lock` were
preserved. Follow-up evidence/documentation commits do not change package code.
No new push, public publication, deployment or participant contact was performed
during this completion pass; historical merge records are not current-head
remote synchronization claims.

Artifacts are local under `dist/8fdbf513/`:

| Artifact | SHA-256 |
| --- | --- |
| `libreevolve-0.1.0-py3-none-any.whl` | `b26f82c66b3397643cd0fc36e6318c6202797b561ac077e78c975031db18d999` |
| `libreevolve-0.1.0.tar.gz` | `2ee23e26c113471fc39768a7fa5c743ec944aa2b473173bae1346a93b46719e1` |
| `release_artifact_provenance.json` | `169fb8cc81cbd20b37ed46bcd16975b5f97461d0dbc687a49b025bedbc2f7369` |

An exact Git source archive was built with Python 3.12.13 `python -m build
--wheel --sdist`. Both archives byte-match all 455 tracked package files;
provenance records the exact commit and clean tracked source at build time.
Only `alpha_report.py` differs within the package from the `c223d127` cohort
build; generation, budget, evaluator and validator code are byte-identical.
All 455 installed Linux package files were also matched to the final wheel.

Preserved evidence bundle: `runs/alpha-validation-20260907/` (gitignored,
local-only). It includes package bytes/provenance/coverage, raw runs, transcripts,
installed-environment evidence, JUnit, independent report/export records and
browser screenshots. Raw transcripts are diagnostic material; review/redact
before sharing them. A bundle `SHA256SUMS` covers the retained files.

## Supported first run

Reference environment: Linux/WSL, Python 3.12.13, Codex CLI 0.153.4, an
authorized ChatGPT/Codex account with `gpt-5.6-luna` access, explicit `high`
reasoning. Native Windows Python 3.12.10 has final-wheel offline evidence only.
Provider/model access is account-specific. The installed Codex lane rejects
API-key authentication; no API billing fallback is part of this workflow.

From a fresh directory containing the wheel and matching provenance JSON,
follow [the full quickstart](../../docs/alpha-quickstart.md). Install the tested
CLI if needed with `npm install -g @openai/codex@0.153.4`, then complete
`codex login` using your own account. Verify the wheel hash before installation:

```bash
sha256sum libreevolve-0.1.0-py3-none-any.whl
python3.12 -m venv .venv
.venv/bin/python -m pip install ./libreevolve-0.1.0-py3-none-any.whl
.venv/bin/python -m pip check
.venv/bin/libreevolve alpha init packing-task --provider codex --model gpt-5.6-luna --reasoning-effort high
.venv/bin/libreevolve alpha doctor packing-task
.venv/bin/libreevolve run packing-task --run-name packing-first --progress
.venv/bin/libreevolve show runs/packing-first
.venv/bin/libreevolve alpha report runs/packing-first --output packing-first.html
.venv/bin/libreevolve alpha export runs/packing-first verified-first
```

Open `packing-first.html`. `verified-first/solution.py` is independently
verified on training and held-out cases; `verification.json` binds the results
to its SHA-256. New output names are required for every attempt.

Default Codex limits: three CLI invocations, four evaluations, 900 seconds per
run, 180 seconds per CLI invocation, no ensemble retries or fallback. These are
local work bounds, not hard provider-token or billing guarantees. Codex alpha
rejects token/dollar caps because the CLI cannot enforce them. Reported tokens
are observational; subscription charges/quota remain unknown. Authorize your
own account use before running. Press Ctrl+C to cancel; inspect the saved run
status independently of whether its selected candidate passes correctness.

## Implemented workflow and reliability

- Deterministic bin-packing task with an intentionally improvable next-fit seed,
  measurable bin-count quality, correctness checks, 55 training cases and 30
  held-out cases. Evaluator/holdout inputs stay outside editable seed workspace.
- `alpha init` and actionable local `alpha doctor`, using existing bounded
  `run --progress`, saved run artifacts and `show` inspection.
- Local HTML report with independent baseline/best checks, source diff, elapsed
  time, model/backend identity, observed token usage, unknown/partial cost,
  stopping condition and explicit failed-attempt/unchanged-seed explanations.
- Verified export with code hashes and explicit history/workspace selection if
  source bytes disagree; no silent overwrite or unverified candidate promotion.
- CLI inspection-helper and prompt-compatibility regressions, interruption and
  persistence fault tests. Cancellation uses a per-call cooperative signal and
  bounded same-process-group cleanup on Linux; a SIGTERM-ignoring descendant is
  included in tests. An actual earlier orphan-process fault was reproduced,
  recorded, explicitly cleaned up, fixed and independently regression-tested.
- Source, archive/history and budget restoration remain distinct from resuming
  pending work. Forced interruption may leave missing runtime finalization;
  no identical-model replay or pending-provider/evaluator resume is promised.
- Paper retrieval stays outside onboarding. Candidate evaluation is a timed
  local subprocess with host access, not a hostile-code security sandbox.

## Final-candidate verification

| Evidence class | Observed result |
| --- | --- |
| Six alpha suites plus Codex/ensemble | 508 passed, 1 Windows-only skip; exact candidate native clone, Python 3.12.13 |
| Docs, backend mocks, agents docs, release provenance and README boundaries | 147 passed, 10 inherited CI-routing failures |
| Supplemental docs/backend boundaries | 15 passed |
| Distinct selected-test aggregate | 670 passed, 10 inherited excluded-CI failures, 1 skip; 681 cases |
| Final Linux clean wheel | dependency check, both entrypoints, init, OAuth doctor, real run, show, HTML report and independently verified export passed |
| Final native Windows clean wheel | 13/13 commands passed; Python 3.12.10 AMD64, zero-generation run/export; no LLM constructed or provider calls |
| Archive/package integrity | wheel + sdist + installed Linux tree each match 455 package files |
| Browser inspection | successful and all-calls-failed reports rendered/read at 1440×1200 in isolated headless Chrome profiles |

All 10 failed assertions concern workflow path/trigger markers removed by the
existing billing pause. The identical 10 test IDs also fail on parent
`cf805a67`; the workflow, tests and helpers are unchanged by the final report
commit. They are recorded excluded-CI checks under the user's instruction, not
silently counted as passes. CI was neither enabled nor dispatched. Restore and
validate CI separately before release approval. The older 6,640-test full-suite
pass belongs to an earlier candidate; no final-head full-suite pass is claimed.
Exact commands, environments, diagnostics and JUnit are in the bundle's `tests/`.

Linux final live root: `/tmp/libreevolve-alpha-8fdbf513-live.9kC5BV`.
Windows final root:
`C:\Users\timot\AppData\Local\Temp\libreevolve-alpha-8fdbf513-winverify-1spTKka6`.
Clean independent verification root:
`/tmp/libreevolve-alpha-independent-repro.QYYZHw`; the initial pass at
`/tmp/libreevolve-alpha-independent.Vxoxha` is also retained. The clean
reproduction explicitly records partial-run inspection/export refusals as
expected behavior rather than assuming every command must succeed.
Their durable copies are in the evidence bundle; temporary roots are not the
only retained copies.

## Real-model results, including failures

All optimization proposals came from actual Codex OAuth Luna calls, not
scripted improvement controls. Framework seeds 17/29/43 are separate run-local
random seeds, not provider reproducibility guarantees. The three completed
comparison runs shared the frozen high-reasoning configuration, evaluator,
baseline and budgets. Seed 29 is an infrastructure-interruption replacement;
its original partial run is retained, not discarded on quality grounds.

| Completed run | Training quality | Holdout quality | Runtime seconds | Known tokens | Provider outcomes |
| --- | ---: | ---: | ---: | ---: | --- |
| Seed baseline | 0.801647 | 0.812165 | — | — | no model |
| Cohort seed 17 | 0.978224 | 0.980562 | 398.154 | 64,327 | 3 responses; one generated candidate invalid |
| Cohort seed 29 replacement | 0.978224 | 0.980562 | 439.397 | 41,762+ | 2 responses, 1 timeout |
| Cohort seed 43 | 0.978224 | 0.980562 | 362.623 | 37,322+ | 2 responses, 1 timeout |
| Separate high diagnostic, seed 17 | 0.978224 | 0.980562 | 133.097 | 19,701 | 1 response |
| Exact final-wheel smoke, seed 97 | 0.978224 | 0.980562 | 81.169 | 17,758 | 1 response |
| Text-only max trial, seed 17 | 0.801647 | 0.812165 | 540.729 | unknown | 3 timeouts; unchanged seed |

`+` means usage is incomplete, not an estimate of the omitted amount. The
three cohort best scores are identical on these finite corpora; there is no
claim of novel algorithms, global optimality, broad benchmark evidence or a
guaranteed improvement rate. Provider latency, timeout incidence and candidate
validity varied. Completed cohort runtime ranged from 6.04 to 7.32 minutes.

An independent non-authoring verifier reevaluated baseline and exact exported
bytes in fresh installed-package subprocesses, compared report/export results
and hashes, and verified that source runs were unchanged. Every completed
cohort export and final smoke passed 55/55 training and 30/30 holdout cases.
Training bins fell from 1,457 to 1,194; held-out bins from 1,118 to 926 (192
fewer, approximately 17.2%). Holdout results were inspected only after all
cohort/diagnostic/final-smoke model calls ended; no later tuning calls followed.

[OAUTH_ATTEMPTS.json](OAUTH_ATTEMPTS.json) retains all 11 optimization run
records and three diagnostic probes: **25 confirmed OAuth CLI invocations,
up to 27 under the configured bounds**, because two interrupted launches cannot
be confirmed. Known usage is **261,796 tokens**, an incomplete lower bound:
224,577 optimization tokens and 37,219 probe tokens. There are 11 successful
optimization responses, 10 timeout records and one separately observed
interrupted invocation without a call result. Cached/reasoning tokens are
subsets, not additions to totals. CLI-internal provider retries are not counted
independently. Subscription use was authorized; extra API allocation was $0,
and subscription charges remain unknown, not zero.

The record includes all max-reasoning failures (including the 600-second
diagnostic and cancelled next call), high diagnostics, the interrupted original
seed 29, the interrupted seed-71 smoke and seed 17's invalid mutation. A separate
earlier Windows placeholder-model diagnostic inherited an existing API-key
environment and returned authentication 401; it is disclosed separately from
the OAuth cohort. Recorded zero usage/cost in that failed diagnostic is not a
verified billing measurement. No API-key fallback was used for the OAuth runs.

Saved-state checks distinguish cancellation from forced termination. The older
cancelled max diagnostic has an `aborted` runtime (617.886 seconds), an
inspectable partial call ledger and a verified unchanged-seed export. This
validates saved-result inspection, not the final build's live child cleanup.
The forcibly interrupted original seed 29 and seed-71 smoke lack runtime
finalization: both produce explanatory `no_result` HTML, while `show` and
explicit history export refuse with `missing_runtime`. Their raw histories
remain preserved, but no automatic recovery or verified export is claimed.
Neither partial is counted as a completed cohort run.

## Pending acceptance and release limits

- [The 3–5 developer trial packet](USER_TRIAL.md) is prepared, including exact
  candidate/hash, tasks, local-work allocation, time-to-export measurements,
  assistance/failure logs and comprehension checks. Zero participants have
  been contacted or observed. Approximately 30-minute unassisted completion
  remains unmeasured; maintainer timing is not external usability evidence.
- CI remains excluded and paused, with the 10 routing assertions described
  above. No public/private index publication, signed provenance or release
  event is claimed. Those are separate release-authority decisions.
- Native Windows live Codex execution/cancellation, remote request cancellation,
  escaped-process containment, macOS runtime parity and pending-work resume
  are not validated by this Linux reference workflow.
- No spending/correctness/performance guarantee extends beyond the documented
  local limits and deterministic corpora. Max reasoning did not complete the
  optimization prompt in tested deadlines; use explicit `high` for this lane.

Under the revised scope (CI excluded, external trial allowed to remain pending),
the local engineering acceptance gates are satisfied. The next acceptance
activity is an authorized, observed developer trial, not another unbounded
maintainer experiment or an automatic publication.
