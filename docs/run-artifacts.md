# Saved engineering-preview results

Each new run uses `runs/<run-name>/`. Existing run artifacts are protected;
choose a fresh name instead of overwriting a run. The [quickstart](alpha-quickstart.md)
is the canonical command source, and [reading results](results.md) explains how
to interpret the records.

## Artifact inventory

| Artifact | Purpose |
| --- | --- |
| `manifest.json` | Configuration, provenance, terminal status and bounded-work accounting. |
| `history.jsonl` | Evaluated candidate workspaces, metrics and admission evidence. |
| `failure_history.jsonl` | Failed or rejected proposals and bounded recent-failure memory. |
| `archive_events.jsonl` | Archive admission and migration events. |
| `controller_budget_events.jsonl` | Ordered evaluation, call, generation and stop counters. |
| `llm_calls.jsonl` | Bounded call and reward records, reported usage and local errors. |
| `prompt_history.jsonl` | Prompt selection and score records. |
| `evaluator_results.jsonl` | Saved evaluator results linked to candidates. |
| `best.py`, `best_workspace/` | Best retained candidate text and workspace. |
| `evaluator_artifacts/` | Optional bounded evaluator output evidence. |
| `*_invalid.jsonl` | Quarantined malformed records; diagnostics, never accepted state. |

The manifest carries schema information and path/hash records. Missing
artifacts, invalid JSON, unsafe paths, inconsistent required policy records or
unfinished exports are not proof of success. Inspection rejects required-state
errors. A forced termination or persistence failure can leave only partial
state.

## Inspection and reporting

`libreevolve show RUN` inspects the saved run. Modern runs report manifest
status and archive-retained selection. Legacy history-only data may be shown as
such; it is not a completed or verified preview run.

`libreevolve alpha report RUN --output result.html` builds a fresh local report.
The command reevaluates the baseline and the on-disk
`RUN/best_workspace/seed.py` candidate in timed local subprocesses, then writes
escaped HTML without a provider request. It has no history/workspace source
selector; missing or corrupt workspace state is reported rather than replaced
with history. Candidate execution has host access and is not a security
sandbox. Rendering HTML is not the same as approving arbitrary candidate
source.

The output path must be a new `.html` file and an existing file or symlink is
rejected. Review run status, validity, training quality, held-out quality,
retention, source identity and usage separately.

## Verified export

`libreevolve alpha export RUN DESTINATION` independently evaluates the selected
single-file candidate in a fresh local subprocess. The new directory contains
`solution.py` and `verification.json`, including the exact candidate SHA-256,
fresh training and held-out results, source-selection evidence and the source
run status. Existing destinations are not overwritten.

If `best_workspace/` differs from saved history, export requires an explicit
`--source workspace` or `--source history`; these selectors belong to export,
not report. A manually edited candidate does not inherit historical identity.
Validation failure must not be bypassed by editing saved metadata.

## Cancellation, usage and privacy

Ctrl+C attempts to preserve an aborted manifest and best-so-far artifacts before
re-raising cancellation. Secondary persistence errors must not mask the original
interruption. Local process cleanup does not prove remote provider cancellation.

Subscription charges and quota may be unknown; missing usage is not zero cost.
Local subprocesses are not a security sandbox. Treat source, logs and HTML as
local research data: redaction reduces accidental exposure but is not a
guarantee that arbitrary candidate source is safe to publish.
