# Run Artifacts

LibreEvolve writes two kinds of outputs during and after a run:

- append-only run history
- a standalone copy of the final best program

By default these live under `runs/`.

## Directory layout

For a run named `hello_world`, the default output looks like:

```text
runs/
└── hello_world/
    ├── history.jsonl
    └── best.py
```

The run subdirectory name comes from:

- `--run-name`, if provided
- otherwise the loaded problem directory name

## `history.jsonl`

This file is written by
[`libreevolve/core/database.py`](../libreevolve/core/database.py). Each line is
one JSON record for one candidate program.

Current fields:

- `id`
- `code`
- `fitness`
- `generation`
- `parent_id`
- `lineage`
- `metadata`

Important behavior:

- every evaluated candidate is logged, even invalid ones
- the log is append-only
- the archive and the log are not the same thing

That distinction matters:

- `history.jsonl` is a complete run trace
- the population archive only contains programs whose final score is `>= 0.0`

### `metadata`

The evolution loop currently stores:

- `prompt`: the prompt sent to the chosen backend
- `diff`: the raw SEARCH/REPLACE response

This makes `history.jsonl` useful for:

- prompt debugging
- mutation replay
- backend behavior analysis
- training data extraction

## `best.py`

After the run completes, the CLI writes the best archived program's code to
`best.py`.

This is a convenience artifact only:

- it is not used for resume
- it is not necessarily the last candidate evaluated
- it reflects the best fitness seen in the archive

## Example histories committed to the repo

The repository also includes curated examples under
[`examples/runs/`](../examples/runs/README.md). These are intentionally checked
in so users can inspect representative runs without generating fresh output.

Use:

```bash
py -3.12 -m libreevolve show examples/runs/hello_world_ensemble
py -3.12 -m libreevolve show examples/runs/sorting_ttt_rl
```

## Related plugin artifact

The `ttt_rl` plugin writes training examples to:

```text
runs/grpo_data.jsonl
```

This file is global to the configured `log_dir`; it is not nested under the
per-run directory by default.
