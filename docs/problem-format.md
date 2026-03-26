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

All four parts are required. Missing `validate.py` or missing seed files are
hard errors during load.

## `task_description.txt`

This file is inserted directly into the mutation prompt. Keep it concrete and
task-specific. The model sees it as part of the `[SYSTEM]` prompt block.

Good task descriptions usually specify:

- the target function or API surface
- optimization goals
- hard constraints
- what counts as invalid output

## `metrics.yaml`

The loader expects a top-level `metrics` list.

Example:

```yaml
metrics:
  - name: score
    direction: maximize
    primary: true
    bounds: [0.0, 1.0]
  - name: is_valid
    direction: maximize
    primary: false
```

Current loader behavior:

- `metrics` must be a non-empty list
- the primary metric is the first metric with `primary: true`
- if no metric is marked primary, the first metric becomes primary
- `bounds` defaults to `[0.0, 1.0]` when omitted
- malformed bounds that are not length 2 raise an error

Important note:

- The loader stores `primary_bounds` on the `Problem` dataclass.
- The current population code does not yet use those bounds when normalizing
  MAP-Elites performance cells.

## `validate.py`

`validate.py` must expose:

```python
def evaluate(code: str) -> dict:
    ...
```

LibreEvolve writes the candidate program to a temporary file, imports
`validate.py` in an isolated subprocess, calls `evaluate(code)`, and expects the
returned value to be JSON-serializable.

The returned dict must include:

- the primary metric name from `metrics.yaml`
- `is_valid`

Example:

```python
def evaluate(code: str) -> dict:
    ns = {}
    try:
        exec(compile(code, "<candidate>", "exec"), ns)
    except Exception:
        return {"score": 0.0, "is_valid": False}

    fn = ns.get("solve")
    if not callable(fn):
        return {"score": 0.0, "is_valid": False}

    try:
        result = fn()
    except Exception:
        return {"score": 0.0, "is_valid": False}

    return {"score": 1.0 if result == 42 else 0.0, "is_valid": result == 42}
```

### Validation semantics

The evaluator interprets validator output as follows:

- if the subprocess crashes, times out, or emits invalid JSON, the candidate
  gets `-0.2`
- if `is_valid` is false, the candidate gets `-0.1`
- otherwise the candidate gets the primary metric value

That means `is_valid` is both a domain-validity flag and the gate for archive
admission. A candidate with a strong metric value but `is_valid: false` is still
treated as invalid.

## `initial_programs/*.py`

All `*.py` files in `initial_programs/` are loaded, sorted by filename, and used
as seed candidates.

Current behavior:

- every seed is evaluated before generation 0
- every seed is logged
- only seeds with score `>= 0.0` enter the archive

Multiple seeds are useful when you want the run to start from several plausible
local basins instead of one canonical baseline.

## Design guidance

### Use intentionally improvable seeds

A perfect seed can still produce archive diversity, but it reduces the chance of
meaningful fitness gains. Suboptimal seeds produce better evolutionary pressure.

### Keep validators deterministic when possible

Stochastic validators make backend reward and archive comparisons noisier. If
randomness is necessary, seed it inside `validate.py`.

### Fail safely

Treat malformed outputs, missing functions, and runtime exceptions as invalid.
The framework already expects validators to be defensive.

### Keep metrics simple

Only the primary metric is used for final scoring. Additional metrics may be
useful for your own analysis, but they are not consumed by the current archive
or CLI.
