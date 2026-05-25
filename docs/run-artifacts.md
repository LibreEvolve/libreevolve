# Run Artifacts

LibreEvolve writes machine-readable run outputs under `runs/` by default.
Run JSON and JSONL writers use strict finite JSON. Candidate history, prompt
history, manifests, and the ThetaEvolve-inspired export reject `NaN`/`Infinity`
or non-JSON-compatible values rather than emitting permissive Python JSON
tokens. Failed append attempts write diagnostic quarantine records next to the
target stream.

## Directory layout

For a run named `hello_world`:

```text
runs/
└── hello_world/
    ├── manifest.json
    ├── history.jsonl
    ├── history_invalid.jsonl          # Only when a candidate record is rejected
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
- optional LLM feedback grader records are stored under
  `evaluation.metadata.llm_feedback`

`code` is the primary file content for backward compatibility. `files` contains
the full candidate file set for workspace candidates.

`evaluation` includes normalized fitness, validity, per-stage outcomes, stdout,
stderr, error, elapsed time, and metadata such as the primary file and file
list. If feedback graders are enabled, their scores appear in `metrics`, and
the composed score appears as `feedback_adjusted_fitness` while the raw primary
validator metric remains intact. Configured evaluator retries are not fully
auditable yet: fail-then-pass retries preserve the successful attempt, and
all-fail retries preserve the final failed attempt, but earlier failed attempts
are not retained as separate history records.

Plugin `on_evaluated()` hooks can also modify the final top-level `fitness`.
That score-composition path is not currently stored as a structured trace, so
plugin-adjusted records may have top-level `fitness` values that differ from
`evaluation.fitness` without per-plugin before/after metadata. Archive
admission uses the final top-level fitness threshold, so a plugin can currently
make an evaluator-invalid candidate archive-eligible unless validity override
semantics are hardened.

Archive state is not serialized yet. `history.jsonl` contains evaluated
candidates, but not MAP-Elites cell coordinates, island assignment, diversity
descriptor values, elite-list snapshots, or migration events.
Per-candidate archive admission outcomes are also not recorded: history records
do not say whether a logged program was rejected by threshold, inserted into a
cell, ignored because it did not replace the occupant, or displaced a previous
occupant.

## `prompt_history.jsonl`

This file records prompt-program events:

- `add`: a seed or mutated prompt template entered the prompt database
- `score`: a prompt template was used for a candidate and received reward

Program records in `history.jsonl` include `metadata.prompt_program_id` so a
candidate can be traced back to the prompt program that produced it.

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

`show` is currently a compact compatibility view. Richer metric-vector,
lineage, archive, prompt, feedback, and full-workspace diagnostics are tracked
as follow-up work.

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
