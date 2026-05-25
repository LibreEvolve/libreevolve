# Run Artifacts

LibreEvolve writes machine-readable run outputs under `runs/` by default.
Strict JSON serialization is not fully hardened yet: if a plugin, feedback
grader, or unchecked evaluator path produces non-finite numeric values, the
current Python JSON writer may emit permissive `NaN`/`Infinity` tokens rather
than rejecting the record. Treat strict finite JSONL as open hardening work.

## Directory layout

For a run named `hello_world`:

```text
runs/
└── hello_world/
    ├── manifest.json
    ├── history.jsonl
    ├── prompt_history.jsonl
    └── best.py
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
validator metric remains intact.

Plugin `on_evaluated()` hooks can also modify the final top-level `fitness`.
That score-composition path is not currently stored as a structured trace, so
plugin-adjusted records may have top-level `fitness` values that differ from
`evaluation.fitness` without per-plugin before/after metadata.

## `prompt_history.jsonl`

This file records prompt-program events:

- `add`: a seed or mutated prompt template entered the prompt database
- `score`: a prompt template was used for a candidate and received reward

Program records in `history.jsonl` include `metadata.prompt_program_id` so a
candidate can be traced back to the prompt program that produced it.

## `best.py`

After a run completes, the CLI writes the best archived program's code to
`best.py`.

This is a convenience artifact only:

- it is not used for resume
- it is not necessarily the last candidate evaluated
- it reflects the best fitness seen in the archive
- for workspace candidates, it contains only the primary-file view; the full
  file set is currently recoverable from `history.jsonl`, not from a dedicated
  `best_workspace/` artifact

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
```

This file is global to the configured `log_dir`; it is not nested under the
per-run directory by default.
