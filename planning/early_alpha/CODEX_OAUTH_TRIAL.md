# Codex OAuth bin-packing trial

The user authorized Luna at max reasoning through Codex OAuth on 2026-09-07
("you can use the luna max model as much as you want", clarified as Codex
OAuth). This authorizes subscription usage for this work. CI is excluded by
the user's earlier instruction. External usability may remain pending as
allowed by the original objective.

Use `gpt-5.6-luna` with `reasoning_effort: max`, authenticated through the
existing Codex ChatGPT login. Do not switch to API-key billing. The additional
API spending allocation is $0; subscription quota consumption is authorized,
but subscription charges and remaining quota are not observable from the CLI.
No fabricated token price or zero-cost measurement should appear in reports.

The initial cohort comprises three fresh bin-packing runs with seeds 17, 29,
and 43, each limited to three logical generation calls, four evaluations and
900 seconds, with no ensemble retries or fallback. Each CLI process has a
180-second deadline. CLI internal network retries are not independently
observable; the call limit counts CLI invocations. Token usage is recorded
after each call; it is not a hard output-token guarantee.

Use the same bundled corpus and baseline, model and configuration across all
three runs. Keep held-out results out of mutation prompts. Retain every
attempt, including errors and non-improvements. Generate reports and verify
exports after the entire cohort, with baseline and candidates reevaluated by
the same bundled training and holdout validator in fresh subprocesses.

## Access probe

A Codex CLI 0.153.4 request for `OK`, using `gpt-5.6-luna` with max reasoning,
completed successfully through the local OAuth session. The CLI reported
13,248 input tokens, 8,960 cached input tokens, five output tokens and zero
reasoning output tokens. This is an access probe, excluded from optimization
results but retained in total experiment accounting. Dollar cost is unknown.

## Cohort status

The initial cohort at package commit `51a44454` stopped after seed 17: all three
calls reached the 180-second ensemble timeout. CLI traces show shell inspection
of the empty working directory and no final candidate. The baseline remained
at 0.8016472203157172. Token usage was absent on those timed-out calls; dollar
charges remain unknown. Seeds 29 and 43 were not initiated with that driver.
Artifacts are retained under `/tmp/libreevolve-oauth-trial.0XweBf/runs/luna-seed-17`
and its sibling `transcripts` directory.

The next candidate disables shell tools for alpha generation, requests a JSON
program field, and explicitly instructs text generation from the supplied prompt.
A fresh three-run cohort will retain the same numerical limits and seeds. This record
supersedes the earlier interpretation that the user's Luna/OAuth permission
covered internal reasoning only. Existing experimental backend limitations
are implementation work; they do not revoke the user's authorization.

### Deadline diagnostic (2026-09-07)

The installed `04b00a60` text-only driver also reached its first 180-second
deadline with only `thread.started` and `turn.started` events, no tool calls,
and no final response. This does not establish a model-access failure. The
outer ensemble and inner CLI deadlines were equal, which also races cleanup
and usage collection. The original short-deadline run is retained in full.

A separate fresh cohort uses the same model, reasoning, baseline and seeds,
but permits 600 seconds per CLI invocation, 630 seconds at the ensemble layer,
and a 2,000-second run threshold. Calls/evaluations remain three/four; retries
and fallback remain disabled. Configuration is frozen in `packing-long` under
`/tmp/libreevolve-oauth-cohort.XjPBLZ`. These are measured-run settings, not
yet a claim that onboarding reliably completes in 30 minutes. The additional
API allocation remains $0 and subscription usage/unknown charges are unchanged.
No held-out results were inspected to select these deadline changes.

A separate minimal structured-output access probe at 20:47 UTC returned
`{"program":"pass"}` through the same Luna/max OAuth route with shell tools
disabled and a required JSON string field. It reported 11,897 input tokens,
zero cached input tokens, 15 output tokens and zero reasoning output tokens;
thread `01a07da0-7d09-7b50-813a-18678bad8390`. It is not an optimization
experiment and is included separately in attempt accounting. This verifies
basic model access and JSON output, not completion of the longer task prompt.

An installed-adapter minimal probe (`Return the text pass`) then succeeded
with the same OAuth selection, stdin transport, schema and no-tools settings.
Its single 90-second-bounded invocation reported 11,965 input, 89 output,
12,054 total tokens, zero cached input and 72 reasoning output tokens (the
latter are a subset of output, not additional tokens). Its transcript is in
`/tmp/libreevolve-oauth-cohort.XjPBLZ/adapter-probe`. This is another diagnostic
attempt, not an optimization result; subscription charges remain unknown.

### Longer request failure and cancellation

The first `packing-long` request reached its 600-second backend timeout with
no final response or usage. Its second invocation had started when the operator
sent SIGINT; the CLI saved an aborted run and exited 130. The ensemble worker
thread left that second Codex process alive. Its exact process group was
explicitly terminated and disappearance verified. Count both invocations,
including the interrupted one whose usage is unavailable. Seeds 29/43 were
not started with this failed driver. This live cancellation fault blocks
supporting that threaded alpha Codex configuration until fixed and tested.

A fresh `packing-compact` diagnostic uses one generation/call, two evaluations,
a 240-second runtime threshold and 180-second CLI deadline. The outer ensemble
timeout was disabled as an attempted cancellation mitigation. The subsequent
fault test showed the run-wide deadline still recreates an ensemble worker;
the actual fix requires an explicit per-call cancellation signal and bounded
local process-group cleanup. A supported custom prompt template keeps task, current code and
training metrics, asks for one compact heuristic improvement without exact
search, and omits generic multi-file and validator-provenance instructions.
No algorithm, candidate implementation, or held-out results are supplied.
This changes the prompt/driver, so it is not pooled with the earlier cohorts.

The compact diagnostic also timed out after 180 seconds with only thread/turn
start events, no candidate and no reported usage. It retained the baseline.
Thus neither a compact prompt nor a 600-second full-prompt deadline has yet
established successful optimization with `max` reasoning. After the cancellation
fix is independently tested, a separate bounded `high`-reasoning diagnostic on
the same authorized Luna/OAuth route will test a lower-compute configuration.
This is not represented as a max-reasoning success, and all max failures remain
in the record. No other provider or API-key billing fallback is permitted.

### Installed cancellation candidate / high diagnostic

Candidate `c223d12755937e4589c20ec42f8ea6488999fb59` was built from an exact
source archive; both wheel and sdist byte-match all 455 package files. A clean
Linux/WSL Python 3.12.13 environment at `/tmp/libreevolve-alpha-high.SJliwk/venv`
installed that wheel and passed dependency and local OAuth preflight checks.
Initialization selected `--reasoning-effort high` explicitly. The first run
uses the unchanged full mutation prompt, seed 17, one generation/logical call/
CLI invocation, two evaluations, a 180-second CLI deadline and a 240-second
runtime threshold. No retries or fallback. Run name: `luna-high-diagnostic-17`.
This is a configuration diagnostic, separate from any subsequent three-seed
cohort. It consumes the same authorized subscription; charges remain unknown.

The high diagnostic completed one real mutation: training quality improved
from `0.8016472203157172` to `0.9782244556113903` (the run artifacts are authority
for full precision), with training correctness passed. Held-out results were
not inspected before freezing the next cohort.

The high-reasoning cohort uses three fresh runs, seeds 17/29/43, with the same
installed `c223d127` wheel and initialized task. Each retains the generated
default limits: three generations/CLI calls, four evaluations, 180 seconds per
CLI invocation, 900 seconds per run, no retries/fallback. Run names are
`luna-high-seed-17`, `luna-high-seed-29`, `luna-high-seed-43`. They execute
concurrently in independent processes/output directories; this reduces cohort
wall time but is not a claim of distributed execution. Aggregate allocation is
nine CLI invocations for this cohort. No prompt or budget tuning based on
cohort results; reports and exports follow completion of all three runs.
Failed, unimproved and interrupted attempts remain in the complete inventory.
