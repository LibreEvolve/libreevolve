# Problem Format

A LibreEvolve problem is a directory with code, scoring metadata, and one or
more seed programs. Problems are loaded by
[`libreevolve/problems/loader.py`](../libreevolve/problems/loader.py).

## Required layout

```text
my_problem/
├── task_description.txt
├── metrics.yaml
├── validate.py
└── initial_programs/
    ├── seed.py
    └── optional_more_seeds.py
```

Optional context files can be placed in:

```text
my_problem/
└── context/
    ├── notes.md
    ├── formula.txt
    └── helper.py
```

Supported context extensions are `.txt`, `.md`, and `.py`. These files are
rendered into prompts as explicit context.

## `task_description.txt`

This file is inserted into the mutation prompt. Keep it concrete and
task-specific: target API, optimization goal, hard constraints, and invalid
conditions.

## `metrics.yaml`

The loader expects a top-level `metrics` list.

```yaml
metrics:
  - name: score
    direction: maximize
    primary: true
    bounds: [0.0, 1.0]
  - name: runtime
    direction: minimize
    primary: false
    bounds: [0.0, 10.0]
  - name: is_valid
    direction: maximize
    primary: false
```

Behavior:

- `metrics` must be a non-empty list
- the first metric with `primary: true` is primary
- if no metric is marked primary, the first metric is primary
- `bounds` defaults to `[0.0, 1.0]`
- malformed bounds raise an error
- `direction: minimize` is inverted during normalization

Fitness is the normalized primary metric. Raw metrics are preserved in
`Program.metrics` and `history.jsonl`.

## `validate.py`

`validate.py` must expose:

```python
def evaluate(code: str) -> dict:
    ...
```

LibreEvolve writes the candidate to a temporary file, imports `validate.py` in a
subprocess, calls `evaluate(code)`, and expects the returned value to be
JSON-serializable.

The returned dict should include:

- the primary metric name from `metrics.yaml`
- `is_valid`
- any secondary metrics useful for prompts, logs, or later analysis

The evaluator parses the last non-empty stdout line as JSON, so validators may
print diagnostics before returning.

## Evaluation semantics

The evaluator returns an `EvaluationResult` with normalized fitness, raw
metrics, validity, stage outcomes, stdout, stderr, error, elapsed time, and
metadata.

Default failure scores:

- malformed/no-op mutation: negative diff penalty
- syntax error, subprocess crash, timeout, or malformed JSON: `-0.2`
- validator returns `is_valid: false`: `-0.1`
- otherwise: normalized primary metric

`Config.eval_stages` can run configured validator stages with per-stage timeout
and `min_score` thresholds.

## `initial_programs/*.py`

All `*.py` files in `initial_programs/` are loaded, sorted by filename, and used
as seed candidates.

Seeds can be unmarked whole Python programs, preserving backward compatibility,
or they can mark one or more evolvable regions:

```python
def helper(x):
    return x

# EVOLVE-BLOCK-START solve
def solve():
    return 1
# EVOLVE-BLOCK-END
```

With markers, the surrounding skeleton is preserved and mutations are applied to
the marked region(s). Without markers, the whole program remains evolvable.

## Mutation modes

`mutation_mode: diff` is the default SEARCH/REPLACE mode:

```text
<<<SEARCH
old code
===
new code
>>>REPLACE
```

`mutation_mode: full` accepts a complete replacement. For one marked block, the
replacement becomes that block's body. For multiple blocks, use named block
payloads:

```text
<<<BLOCK solve
def solve():
    return 2
>>>BLOCK
```

## Design guidance

- Make seeds intentionally improvable.
- Keep validators deterministic when possible.
- Return every metric you want future prompts or analysis to see.
- Use evolve blocks when the skeleton/API must stay fixed.
- Treat the current problem model as Python-only and single-workspace; multi-file
  candidates are planned but not implemented.
