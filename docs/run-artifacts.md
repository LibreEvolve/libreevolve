# Run Artifacts

LibreEvolve writes machine-readable run outputs under `runs/` by default.
Run JSON and JSONL writers use strict finite JSON. Candidate history, prompt
history, manifests, and the ThetaEvolve-inspired export reject `NaN`/`Infinity`
or non-JSON-compatible values rather than emitting permissive Python JSON
tokens. Failed candidate, prompt, and GRPO append attempts write diagnostic
quarantine records. Failure-history append failures use the separate
`failure_history_invalid.jsonl` quarantine.

## Directory layout

For a run named `hello_world`:

```text
runs/
└── hello_world/
    ├── manifest.json
    ├── history.jsonl
    ├── failure_history.jsonl
    ├── history_invalid.jsonl          # Only when a candidate record is rejected
    ├── failure_history_invalid.jsonl  # Only when a failure record is rejected
    ├── prompt_history.jsonl
    ├── prompt_history_invalid.jsonl   # Only when a prompt record is rejected
    ├── best.py
    ├── evaluator_artifacts/
    │   └── ...                        # Optional collected validator outputs
    └── best_workspace/
        └── ...                        # Complete best candidate file set
```

The run subdirectory name comes from `--run-name`, if provided, otherwise from
the loaded problem directory name.

## `manifest.json`

`manifest.json` captures the effective run settings used by
[`ProgramDatabase`](../libreevolve/core/database.py), including:

- problem name
- generation and population settings
- run budget limits: `max_generations`, optional `max_evaluations`,
  `max_evaluator_seconds`, and `max_runtime_seconds`
- mutation mode
- evaluator stage config
- parent and inspiration sampling strategies
- prompt variants, meta-prompt settings, critique settings, and LLM feedback
  grader specs
- backend specs
- ensemble strategy
- plugins
- problem context-source provenance, including selected relative paths, source
  hashes, extraction status, excerpt spans, and PDF page ranges when available
- evaluator entrypoint provenance, including resolved problem-local validator
  paths, relative paths, SHA-256 hashes, byte counts, and stage usage metadata
- run provenance, including Git `HEAD` and dirty status when available,
  source-tree hashes for `libreevolve/`, problem-tree hashes, and plugin module
  file hashes
- seed and log directory
- run id and run-directory collision policy
- validator environment allowlist configuration

This is a reproducibility aid. It is not yet a full resume checkpoint.
Source and problem tree hashes exclude `.git`, `runs/`, `__pycache__`, and
local test/cache directories. Problem tree hashes cover problem-local files,
including validators, seeds, context, and config. Plugin provenance currently
hashes the Python module file for each plugin instance; constructor arguments,
validated plugin config schemas, emitted plugin artifacts, and provider-side
retrieval context are still separate gaps.
Evaluator provenance currently covers the Python files directly configured as
`validate.py` or `eval_stages[].validate_path`; transitive helper imports,
relative evaluator data files, and package-style entrypoints are not hashed as
evaluator sources yet. Opt-in collected evaluator artifacts carry their own
hashes in per-evaluation metadata rather than the run-start manifest.

Reusing an existing run directory is intentionally not treated as resume.
Before a run starts, LibreEvolve checks the target run directory for known run
artifacts: `history.jsonl`, `history_invalid.jsonl`, `failure_history.jsonl`,
`failure_history_invalid.jsonl`, `prompt_history.jsonl`,
`prompt_history_invalid.jsonl`, `manifest.json`, `best.py`, and
`best_workspace/`, and `evaluator_artifacts/`.

The default collision policy is `fail`: if any of those artifacts already
exist, startup fails before appending new history or rewriting the manifest.
Use a fresh `--run-name` for independent runs, or pass `--overwrite` / set
`run_collision_policy: overwrite` to delete only those known artifacts before
the new run begins. Arbitrary files in the run directory are left alone.
`manifest.json` records `run_id` and `run_collision_policy`. `run_id` is
provenance metadata, not a resume handle.

After a run exits normally, `manifest.json` also receives a `runtime` section
with structured stop reason and consumed local budgets: seed/candidate/total
evaluation counts, cumulative evaluator elapsed seconds, wall-clock runtime
seconds, and generation counts. Current stop reasons include
`max_generations`, `max_evaluations`, `max_evaluator_seconds`,
`max_runtime_seconds`, `no_parent`, `no_valid_programs`, and `completed`.
Token, provider cost, LLM-call retry, stage-sample, and accelerator budgets are
not first-class counters yet.

## `history.jsonl`

Each line is one candidate record. Current fields:

- `id`
- `code`
- `files`
- `primary_file`
- `fitness`
- `generation`
- `parent_id`
- `lineage`
- `metadata`
- `metrics`
- `evaluation`

Important behavior:

- every evaluated candidate is logged, including invalid candidates
- the log is append-only
- the archive and the log are distinct
- candidate ids and prompt-program ids are UUID4 values, not deterministic
  seed-derived ids
- raw metrics and evaluator diagnostics are preserved for later inspection
- declared numeric metrics normalized through `metrics.yaml` are stored under
  `metadata.normalized_metrics`; the first-pass multi-objective archive
  policy stores its equal-weight scalar as `metadata.selection_score` and its
  policy description as `metadata.selection_policy`
- optional critique metadata is stored under `metadata.critique`
- the mutation backend index is stored under `metadata.backend_idx`
- normalized LLM call telemetry is stored under `metadata.llm_calls` for
  successful mutation, critique, and feedback calls associated with the
  candidate
- archive admission metadata is stored under `metadata.archive_admission`
- optional LLM feedback grader records are stored under
  `evaluation.metadata.llm_feedback`
- `metadata.budget` stores the run-budget snapshot immediately after that
  candidate's evaluation

When critique is enabled, `metadata.critique` stores the original mutation, the
revised mutation, the critique prompt, the critique backend index, parser
diagnostics for the revised and original mutations, and whether the revision or
the original mutation was selected for evaluation.

Prompt metadata is stored for auditability, but mutation prompts and critique
prompts are currently persisted as rendered text without a general redaction or
data-retention policy. LLM feedback workspace prompts use basic secret
redaction before provider calls; that redaction path is not yet shared by
mutation prompts, critique prompts, explicit context files, plugin context, or
prompt history.

`code` is the primary file content for backward compatibility. `files` contains
the full candidate file set for workspace candidates.

`metadata.archive_admission.selection_score` records the score used for
MAP-Elites cell competition and elite/exploit ordering when present. Threshold
rejection still uses final top-level `fitness`, so plugin penalties and
feedback composition can invalidate candidates even when their declared metric
normalization remains high.

`evaluation` includes normalized fitness, validity, per-stage outcomes, stdout,
stderr, error, elapsed time, and metadata such as the primary file and file
list. Subprocess metadata records the validator environment policy, provided
environment keys, and allowlist names, but never environment values. Timeout
results also include `evaluation.metadata.timeout_cleanup` with the attempted
process-tree cleanup method and outcome. Persisted validator stdout/stderr
applies basic secret-pattern redaction. If feedback graders are enabled, their
scores appear in `metrics`, and the composed score appears as
`feedback_adjusted_fitness` while the raw primary validator metric remains
intact. Configured evaluator retry attempts are stored under
`evaluation.metadata.attempts`; each attempt record includes attempt index,
pass/fail status, fitness, metrics, stdout, stderr, error, elapsed time, stage
context, and per-stage diagnostics. The selected attempt still determines the
sample/stage result.

Validator-generated files are collected only when
`evaluator_artifact_include` is configured. Matching candidate-workspace files
are copied to `evaluator_artifacts/<collection_id>/...` before the temporary
workspace is deleted. Each copied artifact record in
`evaluation.metadata.artifacts.files` includes the original relative path,
stored artifact path, stored byte count, source byte count, SHA-256 hash of the
stored content, redaction flag/status, stage name, sample index, and attempt.
The collection metadata also records the effective include/exclude patterns,
redaction policy, max-file and max-byte limits, skipped files, total copied
bytes, and collection id. UTF-8 text artifacts receive basic secret-pattern
redaction by default; binary or non-UTF-8 artifacts are copied raw.
`eval_stages[]` can override the top-level artifact policy for that stage.
Non-matching files and files written outside the candidate workspace are not
retained.

Plugin `on_evaluated()` hooks can also modify the final top-level `fitness`.
That score-composition path is stored under `metadata.score_composition` with
evaluator fitness, optional feedback-adjusted fitness, per-plugin before/after
scores, metric additions/changes, invalid score rejections, final fitness, and
whether the final score diverged from `evaluation.fitness`. Archive admission
uses the final top-level fitness threshold but remains gated by
`evaluation.is_valid`, so plugin score changes do not accidentally archive
evaluator-invalid candidates.

Archive state is not serialized yet. `history.jsonl` contains evaluated
candidates and per-candidate archive admission events, but not complete
MAP-Elites cell snapshots, elite-list snapshots, migration events, or
normalization state. `metadata.archive_admission` records threshold rejection,
island id, cell coordinates, descriptor values, previous occupant id, cell
replacement status, elite-list entry, and displaced elite ids for each program.

## `prompt_history.jsonl`

This file records prompt-program events:

- `add`: a seed or mutated prompt template entered the prompt database
- `score`: a prompt template was used for a candidate and received reward
- `penalty`: an invalid meta-prompt mutation was rejected and penalized its
  parent prompt program

Score events store prompt-program reward telemetry in
`program.metadata.last_prompt_reward`: reward mode, raw reward, normalized
reward, and normalization bounds. In `absolute` mode the raw reward is the final
composed candidate score; in `improvement` mode it is child score minus parent
score.

Rejected meta-prompt mutations are written to `prompt_history_invalid.jsonl`
with the parent prompt id, generation, rejected template, error, and metadata.

Program records in `history.jsonl` include `metadata.prompt_program_id` so a
candidate can be traced back to the prompt program that produced it.

## `failure_history.jsonl`

This append-only stream records failed or rejected mutations. Each record
includes:

- `program_id`, `parent_id`, and `generation`
- final failed score and validity
- evaluator `error` and mutation `diff_error`
- changed file paths and file-delta kinds
- bounded mutation text
- compact evaluator stdout/stderr/stage summaries
- `repetition_count` for repeated failures with the same parent, error, and
  mutation text

The evolution loop renders a bounded recent tail of these records into later
prompts. The file is queryable as JSONL, but there is not yet a scored
long-term retrieval policy over all historical failures.

Prompt feedback for the selected parent also renders bounded, redacted
summaries from the candidate's persisted evaluation record: recent stage
status, stdout/stderr, retry/sample attempts, evaluator artifact paths and hash
prefixes, and LLM grader feedback. Prompt rendering does not currently retrieve
full artifact contents from `evaluator_artifacts/`, and these sections are not
yet governed by a global prompt-size budget.

LLM call telemetry is normalized at the ensemble boundary. Records include
role, backend index/name, backend metadata, strategy, API mode, prompt/output
sizes and hashes, latency, success/error status, retry/fallback attempt indexes,
retry/fallback decisions, and scheduler counts before/after the call. Provider
token usage, adapter-internal retry counts, request/response ids, finish
reasons, and raw provider diagnostics are not available yet and are recorded as
empty fields. There is no separate run-scoped call log yet; successful
mutation/critique/feedback call records are embedded in candidate history, and
meta-prompt call records are embedded in
`prompt_history.jsonl`.

## `best.py` and `best_workspace/`

After a run completes, the CLI writes the best archived program's primary-file
content to `best.py` and materializes the complete best candidate file set
under `best_workspace/`.

`best.py` is a compatibility convenience artifact:

- it is not used for resume
- it is not necessarily the last candidate evaluated
- it reflects the best fitness seen in the archive

For workspace candidates, `best_workspace/` is the direct reusable output. It
is regenerated on each successful invocation. If an earlier `best_workspace/`
already exists, startup fails by default with the run-directory collision
policy described above, or removes the previous workspace first when
`overwrite` is explicitly selected.

## Example histories committed to the repo

The repository includes curated examples under
[`examples/runs/`](../examples/runs/README.md). Use:

```bash
py -3.12 -m libreevolve show examples/runs/hello_world_ensemble
py -3.12 -m libreevolve show examples/runs/sorting_ttt_rl
```

Those checked-in examples are legacy history fixtures. They do not contain the
complete current artifact layout shown above, including `manifest.json`,
`prompt_history.jsonl`, `failure_history.jsonl`, or `best_workspace/`.

`show` is a compact compatibility view. For current histories that include
`metadata.archive_admission`, it selects the best archive-admitted valid record
from `history.jsonl` by archive selection score with fitness as the tie-break,
then prints metrics and archive cell/descriptor diagnostics when present. For
legacy histories without archive metadata, including the checked-in fixtures
above, it falls back to the highest top-level `fitness` row. Use
`best.py`/`best_workspace/` from the original run as the exact archived output.
Richer stage, lineage, prompt, feedback, and full-workspace diagnostics are
tracked as follow-up work.

## Related plugin artifact

The `ttt_rl` plugin writes training examples to:

```text
runs/grpo_data.jsonl
runs/grpo_data_invalid.jsonl   # Only when an export record is rejected
```

This file is global to the configured `log_dir`; it is not nested under the
per-run directory by default. It exports clipped rewards
(`reward = max(0.0, score)`) and is not currently linked or hashed from
`manifest.json`.
