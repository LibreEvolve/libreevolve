# Saved engineering-preview results

Each new run uses `runs/<run-name>/`. Existing run artifacts are protected.
Use a fresh name instead of overwriting a run.

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

The manifest carries schema information and path/hash records. Missing artifacts,
invalid JSON, unsafe paths, inconsistent required policy records or unfinished
exports are not proof of success. Inspection rejects required-state errors.
A forced termination or persistence failure can leave only partial state.

`libreevolve show RUN` inspects the saved run. Legacy history-only data may be
shown as such; it is not a completed or verified preview run.
`libreevolve alpha report RUN --output result.html` produces a local HTML report,
separating correctness, training quality, held-out quality, recorded usage and
completion status. It does not make provider calls.

`libreevolve alpha export RUN DESTINATION` independently evaluates the chosen
candidate in a fresh local subprocess. The new directory contains
`solution.py` and `verification.json`, including the exact candidate SHA-256,
fresh training and held-out results, and source-selection evidence. Existing
destinations are not overwritten.

If `best_workspace/` differs from saved history, export requires an explicit
`--source workspace` or `--source history`. A manually edited candidate does
not inherit the historical candidate identity. Validation failure must not be
bypassed by editing saved metadata.

Ctrl+C attempts to preserve an aborted manifest and best-so-far artifacts before
re-raising cancellation. Secondary persistence errors must not mask the original
interruption. Local process cleanup does not prove remote provider cancellation.

Subscription charges and quota may be unknown; missing usage is not zero cost.
Local subprocesses are not a security sandbox. Treat source, logs and HTML as
local research data: redaction reduces accidental exposure but is not a
guarantee that arbitrary candidate source is safe to publish.
