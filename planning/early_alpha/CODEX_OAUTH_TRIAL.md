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

Pending adapter usage telemetry and OAuth onboarding verification. This record
supersedes the earlier interpretation that the user's Luna/OAuth permission
covered internal reasoning only. Existing experimental backend limitations
are implementation work; they do not revoke the user's authorization.
