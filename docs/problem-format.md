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
    ├── optional_more_seeds.py
    └── optional_workspace_seed/
        ├── main.py
        └── helper.py
```

Optional context files can be placed in:

```text
my_problem/
└── context/
    ├── notes.md
    ├── formula.txt
    ├── helper.py
    └── paper.pdf
```

Supported context extensions are `.txt`, `.md`, `.py`, and `.pdf`. Text-like
files are read directly. PDFs are extracted with `pypdf`; files with no
extractable text are marked as such, and extraction failures are rendered as
diagnostic context rather than aborting problem load. Each context item is
rendered into prompts with a source header. Long context files are truncated
deterministically to the first 6000 characters.

Context ingestion is currently flat and content-only: only immediate files in
`context/` are read, and source hashes, PDF page spans, extraction metadata,
include/exclude manifests, and recursive directory selection are not first-class
yet.

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
- metric names must be non-empty and unique
- `direction` must be `maximize` or `minimize`
- at most one metric can be marked `primary: true`
- bounds for all declared metrics must be finite numeric `[lo, hi]` pairs
  (zero-width and inverted ranges are currently accepted and should be avoided
  until stricter validation is implemented)
- unsupported metric fields are rejected
- `direction: minimize` is inverted during normalization when a metric is
  explicitly normalized

Fitness is the normalized primary metric. Raw metrics are preserved in
`Program.metrics` and `history.jsonl`.

## `validate.py`

`validate.py` must expose either the legacy one-argument signature:

```python
def evaluate(code: str) -> dict:
    ...
```

or the workspace-aware signature:

```python
def evaluate(code: str, workspace_path: str) -> dict:
    ...
```

LibreEvolve writes the candidate file set to a temporary workspace, imports
`validate.py` in a subprocess, calls the compatible `evaluate(...)` signature,
and expects the returned value to be JSON-serializable. `code` is always the
contents of the candidate's primary file. `workspace_path` points at the root of
the materialized candidate file set.

The subprocess runs with `workspace_path` as the working directory and adds it
to `sys.path`, so validators can import candidate modules and read relative
candidate files by default.

This is currently a code-file-set model. Problem authors can make validators
interpret the code as a constructor, solver, or search procedure, but the
framework does not yet expose first-class non-code candidate serializers or
paired solution/search abstractions.

The returned dict should include:

- the primary metric name from `metrics.yaml`
- `is_valid`
- every secondary metric declared in `metrics.yaml`

The evaluator rejects missing declared metrics, undeclared metrics,
non-boolean `is_valid`, non-numeric metric values, and non-finite numeric
values. Keep diagnostic strings in stdout/stderr rather than in the metrics
dictionary.

The evaluator parses the last non-empty stdout line as JSON, so validators may
print diagnostics before returning.

For workspace candidates, the validator subprocess runs with the materialized
candidate root as `cwd`, adds that root to `sys.path`, and passes the same root
as `workspace_path`. The validator directory is also added to `sys.path`, so
problem-local helper modules beside `validate.py` can be imported normally.

Validator-created files are not collected yet. The candidate workspace is a
temporary directory that is deleted after each subprocess evaluation, so any
plots, JSON outputs, traces, compiled files, or other generated artifacts must
be summarized through metrics/stdout/stderr until evaluator artifact collection
is implemented.
Timeouts do not yet guarantee process-tree cleanup: validators should avoid
spawning long-lived child processes until process-group/job-object cleanup is
implemented.

## Evaluation semantics

The evaluator returns an `EvaluationResult` with normalized fitness, raw
metrics, validity, stage outcomes, stdout, stderr, error, elapsed time, and
metadata.

Default failure scores:

- malformed/no-op mutation: negative diff penalty
- syntax error, subprocess crash, timeout, or malformed JSON: `-0.2`
- validator returns `is_valid: false`: `-0.1`
- otherwise: normalized primary metric

For workspace candidates, the syntax prefilter checks Python files before
running `validate.py`, but it currently returns only the first Python syntax
error. Non-Python files are skipped by this Python-only prefilter.

`Config.eval_stages` can run configured validator stages with per-stage
`validate_path`, timeout, `min_score`, `samples`, `seeds`, and `retries`.
`min_score` is currently a threshold on normalized primary fitness, not a
metric-specific pass/fail rule, and sample aggregation uses fixed defaults.
Stage numeric fields are prevalidated: `samples` must be positive, `retries`
non-negative, `timeout_sec` positive, `min_score` numeric, and explicit
`seeds` must match `samples`. Stage `validate_path` entries still need stronger
preflight/provenance checks.
Workspace-aware validators that accept `evaluate(code, workspace_path, stage)`
receive stage context containing stage name, index, sample index, seed, attempt,
and the raw stage config.

## `initial_programs`

All `*.py` files in `initial_programs/` are loaded, sorted by filename, and used
as single-file seed candidates. Directories under `initial_programs/` are loaded
as multi-file workspace seeds. For a seed directory, `main.py` is preferred as
the primary file, then `seed.py`, then the first `.py` file by path.

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
Mutation rejects malformed or unmatched marker pairs before applying a change,
including missing end markers, orphan end markers, nested blocks, duplicate
names, and invalid block names. Problem loading does not prevalidate markers
yet, so malformed seeds are diagnosed when the mutation path first touches
them.

### Multi-file seeds

```text
initial_programs/
└── baseline/
    ├── main.py
    └── package/
        └── helper.py
```

Multi-file candidates are rendered into prompts with one section per file, are
logged in `history.jsonl`, and are materialized for validators that accept
`workspace_path`.

## Mutation modes

`mutation_mode: diff` is the default SEARCH/REPLACE mode:

```text
<<<SEARCH
old code
===
new code
>>>REPLACE
```

AlphaEvolve-style SEARCH/REPLACE fences are also accepted: start with
`<<<<<<< SEARCH`, separate old and new text with `=======`, and end with
`>>>>>>> REPLACE`.

`mutation_mode: full` accepts a complete replacement. For one marked block, the
replacement becomes that block's body. For multiple blocks, use named block
payloads:

```text
<<<BLOCK solve
def solve():
    return 2
>>>BLOCK
```

The built-in prompt template is mode-aware: `diff` asks for SEARCH/REPLACE
blocks, while `full` asks for full-file, full-block, or file-section
replacement payloads. Custom `prompt_variants` templates can still override
that wording.

For multi-file candidates, wrap a file edit in a file section:

```text
<<<FILE package/helper.py
<<<SEARCH
old code
===
new code
>>>REPLACE
>>>FILE
```

File-section paths use the same relative-path normalization as candidate
workspaces. Nested paths, hyphens, spaces, Unicode filename characters, and
Windows-style backslashes are accepted when the normalized path is safe.
Path collision checks are incomplete: avoid file sets whose names normalize to
the same relative path or differ only by case on case-insensitive filesystems.
File/block envelopes are not represented as a complete mutation AST yet, but
unmatched, orphaned, nested, empty-name, and invalid-name sections fail before
any partial edit is applied.

In `full` mode, the content inside `<<<FILE ... >>>FILE` becomes the file's new
content, unless the target file contains evolve blocks, in which case the
existing full-block rules apply. New files can be created in `full` mode.
Workspace topology can be changed with command file sections:

```text
<<<FILE DELETE package/old_helper.py
>>>FILE

<<<FILE MOVE old_module.py -> package/new_module.py
>>>FILE

<<<FILE PRIMARY package/new_module.py
>>>FILE
```

`RENAME` is accepted as an alias for `MOVE`. Source and target paths use the
same safety normalization as ordinary file-section edits. Missing sources,
target collisions, unsafe paths, no-op moves, and last-file deletion are
rejected before the original workspace is replaced.

Multi-block full replacement does not yet reject duplicate
`<<<BLOCK name ... >>>BLOCK` sections. If the same block name appears twice, the
later parsed body currently wins, so avoid duplicate block-section targets until
duplicate detection is implemented.

## Design guidance

- Make seeds intentionally improvable.
- Keep validators deterministic when possible.
- Return every metric you want future prompts or analysis to see.
- Use evolve blocks when the skeleton/API must stay fixed.
- Treat the current problem model as Python-only. Multi-file workspaces are
  local text file sets, not arbitrary build-system or containerized projects.
- Treat seed workspaces as UTF-8 text workspaces for now; binary artifacts and
  artifact manifests are not first-class candidate members yet.
- Keep seed workspaces, context files, and plugin context compact. Prompt
  assembly does not yet enforce a global context-window budget across parent
  code, inspirations, context, failures, and feedback.
- Treat candidate abstraction as code-file evolution for now; richer
  problem-defined candidate representations are tracked as AlphaEvolve-alignment
  work.
