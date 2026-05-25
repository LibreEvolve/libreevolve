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
- mutation mode
- evaluator stage config
- prompt variants, meta-prompt settings, critique settings, and LLM feedback
  grader specs
- backend specs
- ensemble strategy
- plugins
- problem context-source provenance, including selected relative paths, source
  hashes, extraction status, excerpt spans, and PDF page ranges when available
- seed and log directory

This is a reproducibility aid. It is not yet a full resume checkpoint.

Reusing an existing run directory is not currently a defined resume operation:
`history.jsonl` and `prompt_history.jsonl` append, while `manifest.json` is
rewritten for the latest invocation. Until run ids or collision policies are
implemented, prefer a fresh `--run-name` for independent runs.

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
- optional critique metadata is stored under `metadata.critique`
- the mutation backend index is stored under `metadata.backend_idx`
- archive admission metadata is stored under `metadata.archive_admission`
- optional LLM feedback grader records are stored under
  `evaluation.metadata.llm_feedback`

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

`evaluation` includes normalized fitness, validity, per-stage outcomes, stdout,
stderr, error, elapsed time, and metadata such as the primary file and file
list. If feedback graders are enabled, their scores appear in `metrics`, and
the composed score appears as `feedback_adjusted_fitness` while the raw primary
validator metric remains intact. Configured evaluator retry attempts are stored
under `evaluation.metadata.attempts`; each attempt record includes attempt
index, pass/fail status, fitness, metrics, stdout, stderr, error, elapsed time,
stage context, and per-stage diagnostics. The selected attempt still determines
the sample/stage result.

Validator-generated files are not collected yet. Evaluators run in a temporary
candidate workspace, and files created there are deleted with that temporary
directory unless the validator encodes their contents into metrics or stdout/
stderr.

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

LLM call telemetry is not first-class yet. Candidate records store the mutation
backend index, and feedback/critique paths store limited backend indexes or raw
responses, but provider usage, latency, retry counts, request ids, finish
reasons, and API mode are not persisted as a normalized call log.

## `best.py` and `best_workspace/`

After a run completes, the CLI writes the best archived program's primary-file
content to `best.py` and materializes the complete best candidate file set
under `best_workspace/`.

`best.py` is a compatibility convenience artifact:

- it is not used for resume
- it is not necessarily the last candidate evaluated
- it reflects the best fitness seen in the archive

For workspace candidates, `best_workspace/` is the direct reusable output. It
is overwritten on each invocation using the same run directory, matching the
current undefined run-collision semantics described above.

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
from `history.jsonl` and prints its metrics when present. For legacy histories
without archive metadata, including the checked-in fixtures above, it falls
back to the highest top-level `fitness` row. Use `best.py`/`best_workspace/`
from the original run as the exact archived output. Richer stage, lineage,
archive, prompt, feedback, and full-workspace diagnostics are tracked as
follow-up work.

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
