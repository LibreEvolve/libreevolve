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
    ├── context.yaml
    ├── notes.md
    ├── formula.txt
    ├── helper.py
    ├── paper.pdf
    └── nested/
        └── extra.md
```

Optional source-setup metadata for existing-codebase integration can be placed
at the problem root:

```text
my_problem/
└── codebase_integration.yaml
```

The problem root itself must be a real directory, not a symlink or Windows
junction. `task_description.txt`, `metrics.yaml`, and `validate.py` must be
regular problem-local files. Optional `context/context.yaml` or
`context/context.yml` manifests must also be regular files. Directories,
symlinks, and Windows junctions at these setup-file paths are rejected before
file contents are read.
Unreadable context manifests fail problem loading with a path-aware diagnostic
whose error text is redacted before display. Read failures for
`task_description.txt` and `metrics.yaml`, plus inspection/stat failures for
`validate.py`, also fail problem loading with path-aware redacted diagnostics.

Supported context extensions are `.txt`, `.md`, `.py`, and `.pdf`. Valid
text-like files are decoded as UTF-8 and preserved exactly, including
leading/trailing whitespace and blank lines. Invalidly encoded selected text,
PDFs with no extractable text, and PDF extraction failures are skipped from
prompt context and retained as `context_policy.skipped` diagnostics. Successfully
loaded context items are rendered into prompts with a citation-style source
header containing a hash prefix, character span, and extraction status. Long
context files are truncated deterministically to the first 6000 characters
unless overridden in `context/context.yaml`.

Context ingestion is recursive and deterministic. Relative paths under
`context/` are used as source names, so duplicate basenames in different
subdirectories remain distinct. Dot-prefixed supported files and directories
under `context/` are skipped by default unless an include pattern explicitly
names a dot-prefixed component.
`context.yaml` can restrict selection and set a per-source character budget:

```yaml
include:
  - "**/*.md"
  - "*.py"
exclude:
  - "drafts/**"
max_chars_per_source: 4000
max_bytes_per_source: 1000000
max_total_bytes: 10000000
max_pdf_pages: 100
max_pdf_chars: 500000
max_context_entries: 1000
max_context_depth: 8
max_skipped_diagnostics: 500
max_context_provenance_chars: 200000
excerpt_policy: head  # or head_tail or term_ranked
source_selection_policy: path_order  # or term_ranked
max_selected_context_sources: null
on_explicit_context_failure: error  # or warn
```

Use either `context.yaml` or `context.yml`, not both. Context manifests accept
only `include`, `exclude`, `max_chars_per_source`, `max_bytes_per_source`,
`max_total_bytes`, `max_pdf_pages`, `max_pdf_chars`, `max_context_entries`,
`max_context_depth`, `max_skipped_diagnostics`,
`max_context_provenance_chars`, `excerpt_policy`,
`source_selection_policy`, `max_selected_context_sources`, and
`on_explicit_context_failure`; unsupported keys fail problem loading so typoed
selection rules are not silently ignored.
All numeric context limits must be positive integers. Duplicate mapping keys also fail
problem loading instead of silently replacing earlier values. Include and
exclude values must be non-empty problem-relative glob patterns using `/`
separators; traversal components, absolute paths, drive-style roots,
backslashes, ASCII control characters, and Unicode format controls such as
right-to-left override and zero-width joiner fail problem loading. Secret-like
include/exclude pattern text is also rejected before the selection policy is
stored. Ordinary non-ASCII path text is allowed.
Context globs are path-segment aware: `*` does not match `/`, `*.md` matches
only root files under `context/`, `nested/*.md` matches exactly one path segment
under `nested/`, and `**` matches zero or more path segments so `**/*.md`
matches root and nested Markdown files.
The `context/` tree must contain real problem-local files/directories:
symlinks and Windows junctions, including linked context manifests, are
rejected during problem loading rather than followed.
Dot-prefixed context sources are skipped by default with a
`hidden_not_included` diagnostic. To select one deliberately, use an include
pattern with a dot-prefixed component, such as `.notes.md` or `.papers/*.md`;
broad patterns such as `*.md` do not opt hidden context into prompts.

The loader records source hashes, byte counts, original/rendered character
counts, truncation spans, extraction status, and PDF page ranges where
available. Selected context source paths whose relative labels look like
secrets are rejected before prompt rendering or manifest persistence. Skipped
context diagnostic paths use the same secret-like label rejection before they
can be retained in `context_policy.skipped`. Selected hidden sources carry
`hidden: true` in source metadata. For
extracted PDFs, `excerpt_pages` and `excerpt_page_spans` identify the page span
of the excerpt actually rendered into the prompt, and prompt headers include
exact per-page spans such as `pages=1:0-20,3:60-80` when available rather than
collapsing non-contiguous pages into a single range.
`max_chars_per_source` is only a rendered prompt-excerpt limit. Ingestion work
is bounded separately: over-`max_bytes_per_source` files and files that would
exceed `max_total_bytes` are skipped before reading, while PDFs that exceed
`max_pdf_pages` or `max_pdf_chars` are skipped during extraction.
The default `excerpt_policy: head` preserves prefix excerpts. `head_tail`
retains deterministic first/last character spans under the same per-source cap,
records exact `excerpt_spans` plus omitted characters, and renders
non-contiguous prompt citations. `term_ranked` splits each source into
fixed-size windows using `max_chars_per_source`, scores each window by
deterministic overlap with task-description terms, keeps the highest-scoring
window, and records ranking policy, query-term hash/count, selected chunk, and
omitted chunk count. It is a deterministic local relevance heuristic, not an
embedding model or learned semantic ranker.
`source_selection_policy: term_ranked` can then rank successfully extracted
context sources by deterministic task-term overlap against the rendered
excerpt. Pair it with `max_selected_context_sources` to retain only the
highest-scoring sources for prompt context while recording candidate count,
selected/omitted sources, scores, source hashes, query-term hash/count, and
the selection policy in `context_policy.source_selection`. The default
`path_order` policy preserves existing path-order retention, and the prompt
renderer still sorts loaded source labels unless a prompt context policy
explicitly supplies source paths.
Files matched by an explicit `include` pattern must extract successfully by
default; invalid UTF-8 text, corrupt PDFs, no-text PDFs, read errors, and PDF
resource-limit failures abort problem loading before prompts or manifests can
overstate context availability. Set `on_explicit_context_failure: warn` only
when a degraded context load is intentional; the manifest then records
`explicit_context_failure_count` and matched include-pattern diagnostics.
Unreadable selected context sources are skipped with `reason: read_error`.
Unreadable unsupported, excluded, hidden, or not-included context sources keep
their original skip reason and record `read_status: read_error`, null
`sha256`, null `bytes`, and redacted error text.
Unreadable context directories are skipped with
`reason: directory_listing_error` and redacted error text while readable
sibling context remains available. Context source stat failures are skipped
with `reason: stat_error`, null hash/byte fields, and redacted error text.
`max_context_entries` stops deterministic traversal after the retained entry
budget, `max_context_depth` skips files beyond the allowed relative path depth,
`max_skipped_diagnostics` caps retained skipped-source records while preserving
the total skipped count, and `max_context_provenance_chars` can trim retained
skipped diagnostics further to bound manifest provenance size.
These source records are persisted in
`manifest.json` for run
provenance. The manifest also records `problem.context_policy`: whether
`context/` existed, supported extensions, the active context manifest hash when
present, effective include/exclude patterns, the per-source character budget,
byte/PDF extraction limits, context entry/depth/skipped-diagnostic/provenance
limits, the `hidden_source_policy`, selected/skipped counts,
`usable_selected_count`, `failed_extraction_count`,
`on_explicit_context_failure`, explicit-context failure diagnostics, retained
skipped-record counts, truncation/omission metadata, `include_patterns` with pre-filter
`matches` and post-filter `selected_matches`, `unmatched_includes`, and hashed
diagnostics for files skipped as
`unsupported_extension`, `not_included`, `hidden_not_included`,
`max_source_bytes`, `max_total_bytes`, `extraction_resource_limit`,
`extraction_failed`, `no_extractable_text`, `excluded`,
`max_context_entries`, or `max_context_depth`.
Unmatched include
patterns are diagnostics, not load failures. This makes local context selection
reconstructable from the run manifest, but it is still extractive, first-span
context handling rather than semantic ranking or summarization.
For each include pattern, `matches` counts supported candidate files before
hidden, exclude, stat, and resource filters; `selected_matches` counts files
that survived those filters and were selected for prompt context.

## `codebase_integration.yaml`

Use either `codebase_integration.yaml` or `codebase_integration.yml`, not both.
The file is optional. Direct callers can supply the same mapping through
`Problem.codebase_integration_metadata`.

This metadata records source-setup provenance for AlphaEvolve-style
existing-codebase integration. It supports:

```yaml
original_codebase_id: fixture-lib-1
upstream_release_artifact:
  id: fixture-lib-v1
  version: "1.0.0"
  source: local_fixture
pre_marker_source_sha256:
  - path: src/main.py
    sha256: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
marker_added_setup_diff:
  summary: Added evolve-block markers without changing executable code.
  files_changed: 1
  markers_added: 2
  non_marker_lines_changed: 0
setup_change_counts:
  files_changed: 1
  markers_added: 2
  non_marker_lines_changed: 0
evaluator_call_path_before_marker_insertion:
  - validate.py
  - src/main.py:solve
evaluator_call_path_after_marker_insertion:
  - validate.py
  - src/main.py:solve
copied_static_asset_source_identity:
  - path: data/config.json
    source_root: fixture-lib-v1
    sha256: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
codebase_scale_fixture:
  status: smoke
  file_count: 3
  component_count: 1
  upstream_identity_present: true
review:
  status: self_reviewed
  notes: Fixture metadata only.
```

Startup manifest validation normalizes this into
`problem.codebase_integration_metadata` with schema
`libreevolve.existing_codebase_setup_metadata.v1`. Text fields are bounded and
must not contain secret-like values. Paths must be safe relative candidate
paths, SHA-256 fields must be lowercase 64-character hashes, and count fields
must be non-negative integers. Completed run manifests surface the normalized
record in `runtime.history.existing_codebase_integration_report` as
`source_setup_metadata`, where it can make source-setup readiness visible
without setting `paper_faithful_existing_codebase_integration` or `claim_ready`
to true.

## `task_description.txt`

This file is inserted into the mutation prompt. Keep it concrete and
task-specific: target API, optimization goal, hard constraints, and invalid
conditions. Empty or whitespace-only task descriptions fail problem loading
before config construction or artifact preparation. Valid UTF-8 task text is
preserved exactly after decoding; the non-empty check does not strip the stored
prompt text. Invalid UTF-8 fails as a path-aware problem-load diagnostic.

## `metrics.yaml`

The loader expects a top-level `metrics` list. Unsupported root fields and
non-string YAML keys are rejected so typoed objective settings cannot be
silently ignored.
Invalid UTF-8 and syntactically invalid YAML fail as path-aware problem-load
diagnostics before evolution starts. Duplicate mapping keys are rejected rather
than resolved with YAML last-key-wins behavior. YAML anchors and aliases are
not supported in setup files, so each metric, context policy, and config record
must be written independently. Duplicate-key and anchor/alias diagnostics
redact common secret-like key text before CLI display.
Direct `Problem(...)` objects are lightweight Python values for tests and
integrations, but `evolve()` rechecks runtime-critical setup before database
writes: task text must be a non-empty string of at most 20000 characters, must
not contain secret-like text, ASCII controls other than tab/newline/carriage
return, or Unicode surrogates, and at least one seed program or workspace must
be present. Valid direct task text is preserved exactly rather than stripped or
redacted, so direct callers remain responsible for not putting secrets in task
objectives.
Direct `context_files`, when supplied without the loader, must be a mapping of
safe problem-relative labels to text values. Labels must use `/` separators and
cannot be absolute, drive-rooted, traversing, empty-segment, control-character,
Unicode format/surrogate/separator-space, compatibility-confusable, or
secret-like strings. Values are bounded to 6000 characters and are rendered as
JSON strings in prompts for delimiter safety; direct callers remain responsible
for omitting secrets from context bodies. The same validation runs before
prompt rendering and before `evolve()` creates or overwrites run artifacts.

```yaml
metrics:
  - name: score
    direction: maximize
    primary: true
    bounds: [0.0, 1.0]
    weight: 2.0
  - name: runtime
    direction: minimize
    primary: false
    bounds: [0.0, 10.0]
    weight: 1.0
```

Behavior:

- `metrics` must be a non-empty list
- the first metric with `primary: true` is primary
- if no metric is marked primary, the first metric is primary
- `bounds` defaults to `[0.0, 1.0]`
- metric names must be unique safe metric identifiers matching
  `[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*){0,7}`
- `is_valid` is reserved for evaluator validity and cannot be declared as a
  scalar metric
- metric names are ASCII identifiers with optional dotted namespaces; whitespace,
  hyphens, control characters, Unicode format controls, and non-ASCII names are
  rejected
- `direction` must be `maximize` or `minimize`
- `primary`, when present, must be a boolean; absent is treated as false
- `weight`, when present, must be a finite non-negative number; absent is
  treated as `1.0`
- at most one metric can be marked `primary: true`
- bounds for all declared metrics must be finite numeric, strictly increasing
  `[lo, hi]` pairs
- unsupported metric fields are rejected
- `direction: minimize` is inverted during normalization when a metric is
  explicitly normalized

Fitness is the normalized primary metric. Raw metrics are preserved in
`Program.metrics` and `history.jsonl`. Declared bounds are normalization
hints, not hard evaluator-output validity constraints. If a returned scalar
metric falls outside its declared bounds, LibreEvolve keeps the raw value and
adds `metric_bound_diagnostics` metadata with the raw value, declared bounds,
metric direction, clamped normalized value, and clamp flag.
Runtime `Program.metrics` keys use the same manifest-safe metric-name grammar
as declared metrics, including optional dotted namespaces. `is_valid` remains a
reserved boolean validity field; every other metric value must be a finite
JSON-native number.

The same metric-schema validation runs when constructing `Problem` objects
directly through Python. Direct callers cannot bypass metric-name grammar,
duplicate-name, primary-membership, direction, primary-flag, or bounds checks;
direct `primary_bounds` must be finite numeric `[lo, hi]` pairs that exactly
match the declared primary metric bounds. `Problem.__post_init__` also marks
the effective primary metric in `Problem.metrics`. Metrics default to
`source: evaluator`, which means validator output must include them. Non-primary
metrics may declare `source: feedback`, `source: plugin`, or
`source: final_fitness`; validator output must not include those names.
Feedback graders may fill feedback-sourced metrics only with
`objective_metric: true`, plugins may fill plugin-sourced metrics through
validated metric side effects, and final-fitness metrics are synthesized from
the candidate's final composed fitness after plugin score hooks run.
Objective helper methods
(`metric`, `metric_bounds`, `metric_direction`, and `normalize_metric`) reject
undeclared names; prompt/history rendering can still display undeclared
feedback or plugin metrics without assigning declared objective semantics. The
effective `Problem.metrics` schema is frozen after validation, including nested
bounds, weights, and source labels, and `objective_schema()` returns JSON-friendly copies
for manifests and callers.

## `validate.py`

`validate.py` must expose either the legacy one-argument signature:

```python
def evaluate(code: str) -> dict:
    ...
```

the workspace-aware signature:

```python
def evaluate(code: str, workspace_path: str) -> dict:
    ...
```

or the staged workspace-aware signature:

```python
def evaluate(code: str, workspace_path: str, stage: dict) -> dict:
    ...
```

LibreEvolve writes the candidate file set to a temporary workspace, imports
`validate.py` in a subprocess, calls the compatible `evaluate(...)` signature,
and expects the returned value to be JSON-serializable. `code` is always the
contents of the candidate's primary file. `workspace_path` points at the root of
the materialized candidate file set. `stage` is the active evaluation-stage
context for staged cascades and includes the stage name/index, sample index,
seed, attempt, and raw configured stage fields. Stage context is serialized
through JSON to the validator subprocess. Problem `config.yaml` stages accept
only the documented `eval_stages` keys; arbitrary custom stage metadata is not
part of the normal problem-config schema.

CLI runs and direct `evolve()` calls preflight the default validator and
configured stage validators before run-directory overwrite cleanup or
manifest/history creation. Preflight checks that validator files resolve inside
the problem directory, import cleanly, expose callable `evaluate`, and use the
documented one-, two-, or three-argument call shapes above. Async and
generator-style `evaluate` functions are rejected during startup preflight, as
are variadic, keyword-only, and extra-parameter signatures. Preflight does not
execute `evaluate`; returned metrics are still validated during candidate
evaluation. Preflight import/signature checks run in a bounded subprocess with
a temporary working directory and the configured validator environment allowlist
instead of importing validator modules in the parent CLI/runtime process.
Direct `CascadeEvaluator.evaluate()` calls run the same contract preflight once
after diff/syntax checks and before any validator subprocess. This keeps direct
library evaluation aligned with CLI and `evolve()` contract enforcement while
preserving local diff/syntax failure behavior.

The subprocess runs with `workspace_path` as the working directory and adds it
to `sys.path`, so validators can import candidate modules and read relative
candidate files by default.

Validator stdin defaults to DEVNULL. Set top-level `evaluator_stdin_text`,
`evaluator_stdin_file`, or per-stage `stdin_text` / `stdin_file` to pass
bounded UTF-8 fixture input to `sys.stdin`; raw fixture text is not persisted,
and metadata records only policy, size, hashes, redaction status, and
problem-local file provenance when applicable, plus explicit
`interactive_input` and `generated_input` support labels. Generated and
interactive stdin streams are unsupported by the current fixture-only policy.
Startup manifests record this boundary under `policies.validator_stdin` and
replace raw configured stdin text/file fields with hash/count-only metadata.

This is currently a code-file-set model. Problem authors can make validators
interpret the code as a constructor, solver, or search procedure, but the
framework does not yet expose first-class non-code candidate serializers or
paired solution/search abstractions.

The returned dict should include:

- the primary metric name from `metrics.yaml`
- `is_valid`
- every secondary metric declared in `metrics.yaml`

The evaluator treats `is_valid` as a required boolean validity gate, not as an
optimization metric. Evaluator result keys must be strings before transport;
non-string keys are rejected before JSON serialization can coerce them. The
evaluator also rejects missing declared metrics, undeclared metrics other than
the reserved `outputs` / `program_output` evidence keys, non-boolean
`is_valid`, non-numeric metric values, and non-finite numeric values. Rejected
evaluator contracts record a bounded diagnostic in
`evaluation.metadata.malformed_metrics` with a machine-readable `reason`, the
exception type, and a redacted message. Reserved `outputs` or `program_output`
return keys may carry strict-JSON evaluator evidence beside scalar metrics;
LibreEvolve redacts common secret patterns, hashes and size-accounts the
payload, stores retained values under `evaluation.metadata.program_outputs`
when the redacted JSON is at or below the 4,000-character cap, and keeps only
bounded preview/hash/omission metadata for larger payloads. Other undeclared
non-scalar return keys remain malformed metrics. Keep large reports, traces,
plots, or datasets as structured files under the candidate workspace and
retain them with `evaluator_artifact_include`.
This declared-metric contract applies to validator-returned JSON. Internal
framework failures such as diff, syntax, timeout, subprocess, and malformed
output diagnostics may synthesize only the primary metric plus `is_valid`
instead of every declared secondary metric; inspect the evaluation error,
stages, and metadata for those rows.

The validator return value is transported through a runner-owned result file,
not stdout. Validators may print diagnostics before or during `evaluate()`;
those prints are preserved as diagnostic stdout but cannot replace the returned
metrics.
Persisted stdout/stderr is decoded with replacement diagnostics, redacted by
the shared secret-pattern grammar, and capped by
`evaluator_output_max_chars` (`20000` by default) before being stored in
history. `evaluation.metadata.diagnostic_output` records byte counts,
replacement counts, truncation flags, and retained character counts. Prefer
configured evaluator artifacts for large reports, traces, plots, or datasets.

For workspace candidates, the validator subprocess runs with the materialized
candidate root as `cwd`, adds that root to `sys.path`, and passes the same root
as `workspace_path`. The validator directory is also added to `sys.path`, so
problem-local helper modules beside `validate.py` can be imported normally.
When a candidate file and a problem-local evaluator helper share the same
module name, the validator directory takes precedence; candidate-local imports
still work when they do not collide with validator helpers.
Validators run with a minimal environment by default. Add variable names to
`validator_env_allowlist` when a benchmark needs specific parent environment
values such as data paths. Allowlist names are stripped, uppercased,
deduplicated, and limited to manifest-safe environment labels before they are
used or persisted. Provider keys loaded through `.env` are not passed unless
explicitly allowlisted, and persisted stdout/stderr applies the shared
versioned secret-pattern grammar, including common provider-token shapes, before
the evaluator-output cap. Network access is not sandboxed yet.

Validator-created files can be collected before the temporary workspace is
deleted when `evaluator_artifact_include` is configured. Include/exclude
patterns are matched against files under the candidate workspace, then matching
files are copied under `runs/<run>/evaluator_artifacts/` with SHA-256 hashes,
byte counts, redaction status, and stage/sample/attempt metadata. Artifact
include/exclude patterns must be non-empty display-safe glob strings with no
Unicode format controls. UTF-8 text artifacts receive the same basic
secret-pattern redaction by default; binary or non-UTF-8 artifacts are copied
raw. Files that do not match the configured patterns remain temporary and are
deleted. Stage configs can override the top-level artifact policy with
`artifact_include`, `artifact_exclude`, `artifact_max_files`,
`artifact_max_bytes`, and `artifact_redact_secrets`.
On timeout, LibreEvolve attempts best-effort validator process-tree termination
and records cleanup metadata in the evaluation result. This timeout cleanup is
not a deterministic descendant-process guarantee, container, network sandbox,
memory limit, or general resource policy.

## Candidate Runner Declarations

`config.yaml` can declare future candidate-language and build-system runner
surfaces without enabling execution:

```yaml
candidate_language_runners:
  - language: rust
    candidate_role: supporting_text_workspace_member
    file_patterns: ["src/*.rs"]
    marker_grammar: custom_declared_unsupported
    runner_command: ["cargo", "test"]

candidate_build_systems:
  - name: cargo
    build_files: ["Cargo.toml"]
    build_command: ["cargo", "build"]
    artifact_patterns: ["target/debug/*"]
```

These records are manifest metadata only. LibreEvolve validates them as
manifest-safe declarations, stores them under `config` and
`policies.candidate_language.runner_declarations`, and includes them in
`runtime.history.candidate_language_runner_contract_report`. They do not run
commands, do not enable non-Python mutation or build execution, and keep
`language_runner_ready: false`.

## Evaluation semantics

The evaluator returns an `EvaluationResult` with normalized fitness, raw
metrics, validity, stage outcomes, stdout, stderr, error, elapsed time, and
metadata.
Persisted candidate fitness values are finite non-boolean numbers. Direct
`Program` construction rejects boolean, nonnumeric, and explicitly non-finite
fitness values; unevaluated program objects may still use the legacy `-inf`
sentinel until evaluation or database admission.

Default failure scores:

- malformed/no-op mutation: negative diff penalty
- syntax error, subprocess crash, timeout, or malformed JSON: `-0.2`
- validator returns `is_valid: false`: `-0.1`
- otherwise: normalized primary metric

For workspace candidates, the syntax prefilter checks Python files before
running `validate.py` and reports all Python syntax errors with file, line,
offset, and message metadata. Non-Python files are skipped by this Python-only
prefilter.

`Config.eval_stages` can run configured validator stages with per-stage
`validate_path`, per-attempt `timeout_sec`, per-sample `max_sample_seconds`,
stage-level `max_stage_seconds`, `min_score`, `metric_thresholds`, `samples`,
`seeds`, `retries`, `metric_aggregation`, `require_program_output`, and
`min_artifacts`.
`min_score` is a threshold on normalized primary fitness.
`metric_thresholds` can require declared metrics to satisfy finite `min` and/or
`max` bounds. `metric_aggregation` can choose `mean`, `min`, `max`, `last`,
`all`, `any`, or `{policy: quantile, q: <0..1>}` for multi-sample metric
aggregation. `require_program_output` can require a retained strict-JSON
program-output payload, and `min_artifacts` can require a minimum copied
evaluator-artifact count. `program_output_checks` can require exact scalar
values at dotted retained-output paths, and `required_artifacts` can require
copied artifact path/glob matches.
Copied UTF-8 evaluator artifacts retain a bounded `content_excerpt` in
artifact metadata after configured redaction; binary or non-UTF-8 artifacts
record `content_excerpt_status: binary_or_non_utf8` and no excerpt text. Prompt
feedback renders the stored excerpt by default. With
`prompt_artifact_content_mode: bounded_file`, runtime prompts can reopen copied
UTF-8 artifacts under the run directory with byte/character caps, redaction,
and path/link/binary diagnostics.
Stage numeric fields are prevalidated: `samples` must be positive, `retries`
non-negative, `timeout_sec` positive, `max_sample_seconds` and
`max_stage_seconds` positive when set, `min_score` numeric,
`metric_thresholds` finite by metric, `metric_aggregation` named by
manifest-safe metric, `require_program_output` boolean, `min_artifacts`
non-negative, `program_output_checks` path/value checked, `required_artifacts`
path-safe, and explicit `seeds` must be JSON-safe scalar values and match
`samples`. Every configured stage must have an explicit manifest-safe `name`
matching
`[A-Za-z0-9][A-Za-z0-9_.-]{0,127}`. Configured names must be unique, must not
look like secrets, and must not use the built-in `diff`, `syntax`, or
`validate` labels. Stage
`validate_path` entries must resolve to problem-local Python files or package
directories containing `__init__.py`; absolute paths are allowed only when they
remain inside the problem directory after symlink resolution. Package
validators are imported as packages, so relative imports from sibling modules
work during preflight and evaluation. Direct evaluator entrypoint files,
including package `__init__.py` entrypoints, are recorded in the run manifest
with problem-relative path labels, path hashes, redaction flags, SHA-256 source
hashes streamed in fixed-size chunks, byte counts, read-error status when
source hashing fails, and stage usage metadata. Each entrypoint also records a
bounded sibling helper/data companion snapshot. During preflight and
evaluation, problem-local imports and file reads are allowed only for the
configured entrypoint, captured companion files, and captured declared data
files; undeclared or over-budget problem-local helper/data access fails instead
of running without manifest provenance.
`evaluator_data_include` / `evaluator_data_exclude` and per-stage
`data_include` / `data_exclude` declare data files relative to the evaluator
directory; matching files are hashed under `declared_data_sources` and exposed
as relative labels in `stage["evaluator_data"]`.
Workspace-aware validators that accept `evaluate(code, workspace_path, stage)`
receive stage context containing stage name, index, sample index, seed, attempt,
declared evaluator data, and the raw stage config.

## `initial_programs`

All `*.py` files in `initial_programs/` are loaded, sorted by filename, and used
as single-file seed candidates. Directories under `initial_programs/` are loaded
as multi-file workspace seeds. For a seed directory, `main.py` is preferred as
the primary file, then `seed.py`, then the first `.py` file by path. A seed
directory with visible files but no `.py` file is skipped with
`reason: no_python_seed_primary`; this keeps the current seed compatibility
view Python-primary until first-class non-Python candidate abstractions exist.
Loaded seed records carry safe source provenance. Run manifests include
`problem.seed_sources`, and seed history/failure rows include
`seed_source_path` such as `initial_programs/seed.py` or
`initial_programs/baseline`, `seed_source_kind` (`file` or `directory`), and
`seed_index`. These are problem-relative artifact identifiers, not host
absolute paths. Direct `Problem.initial_workspace_sources` records must be
mappings using only `seed_index`, `seed_source_kind`, `seed_source_path`,
`primary_file`, `file_count`, `files`, and `allowed_reserved_paths`; path
labels use the candidate-path safety policy, `seed_index` must match the seed
position, and `file_count` must match `files` before manifests or seed history
rows are written.
When direct `Problem.initial_workspaces` is empty, direct
`Problem.initial_programs` must be a list of UTF-8-encodable seed strings. Each
direct inline seed is bounded to 1000000 characters and prevalidated for
malformed evolve-block markers before `evolve()` prepares or overwrites a run
directory. This direct limit does not yet define the broader candidate
workspace storage budget; loaded seed workspaces and later candidates still use
the candidate workspace policy described elsewhere.
When direct `Problem.initial_workspaces` is supplied, it must be a list of
`CandidateWorkspace` objects or workspace record mappings accepted by
`CandidateWorkspace.from_dict`. Direct workspace entries are normalized before
run setup, so malformed file maps, missing primary files, unsafe paths,
UTF-8-unsafe text, binary primary files, and malformed evolve-block markers
fail before run-directory preparation or manifest writes. Byte-valued workspace
entries are accepted as immutable binary static members with byte count,
SHA-256, and bounded `content_b64` provenance.
The `initial_programs/` root, seed files, and seed-workspace entries must be
real files/directories inside the problem package: symlinks and Windows
junctions are rejected during problem loading instead of being followed. Loaded
seed files are UTF-8 text; invalid encoding and file read failures fail as
path-aware problem-load diagnostics whose host error text is redacted. Within
visible seed workspace directories, non-UTF-8 files are skipped with
`reason: non_utf8_seed_workspace_file`, byte count, SHA-256, and
`hash_scope: file_bytes` instead of being coerced into candidate text. A
workspace whose visible files are all skipped still does not count as a seed
and records `all_seed_workspace_files_skipped`. Seed source labels that look
like secrets are rejected before they can become
workspace paths or `problem.seed_sources` provenance. If
`initial_programs/` exists but cannot be listed, problem loading fails with a
path-aware diagnostic whose error text is redacted before display.
Top-level `initial_programs/` entries whose names start with `.` or equal
`__pycache__` are skipped before seed loading, including hidden `.py` files and
hidden/cache seed directories. Other non-`.py` top-level files are skipped as
unsupported top-level seed files; place supporting files inside a workspace seed
directory when they should be part of a candidate workspace. Within visible seed
workspace directories, any path component starting with `.` and any
`__pycache__` component is also skipped. Empty directories and directories
whose contents are all skipped produce skipped-seed diagnostics. Visible
workspace directories with no Python primary file are also skipped with
`no_python_seed_primary`. If no other seed is present, the no-seeds diagnostic
includes skipped seed paths and reasons.
When a problem intentionally needs selected dot-prefixed or `__pycache__` seed
paths, add `initial_programs/seed_policy.yaml`:

```yaml
include:
  - baseline/.config.py
  - baseline/__pycache__/cached.py
exclude:
  - baseline/.env
```

Patterns are relative to `initial_programs/`, are matched by path component,
and `exclude` wins over `include`. Broad includes such as `baseline/**` do not
opt into reserved paths; the include pattern itself must name a dot-prefixed or
`__pycache__` component. Included reserved paths are carried in the loaded
`CandidateWorkspace.allowed_reserved_paths`, in
`problem.seed_sources[].allowed_reserved_paths`, and in history-row
`workspace_path_policy.allowed_reserved_paths`. The default policy remains
secret-safe: hidden/cache paths are skipped unless explicitly included, and
source labels that look like secrets are still rejected or redacted before
persistence.
When candidate workspaces are materialized for evaluation or export, the target
directory is treated as an owned snapshot root. After path and collision
preflight succeeds, the current candidate files are written to a temporary
sibling workspace and swapped into place only after every file write succeeds.
Existing visible roots are preserved if a file write fails. Link or junction
target roots, ancestors, and existing nested entries are rejected instead of
followed or deleted.
Candidate workspaces enforce text and static-member budgets before seeds,
mutations, direct programs, history rows, prompts, evaluator materialization,
or best exports can use them. Defaults are
`max_candidate_workspace_files: 256`, `max_candidate_file_chars: 1000000`,
`max_candidate_total_chars: 2000000`,
`max_candidate_static_file_bytes: 2000000`, and
`max_candidate_total_static_bytes: 10000000`; the configured values are
persisted in run manifests. `max_candidate_workspace_files` counts text files
plus static sidecars. Oversized workspaces are rejected rather than persisted
as summary-only rows or spilled into a separate blob store.
Static sidecars are protected by mutation policy in the `<<<FILE ...>>>FILE`
mutation grammar: text edits, deletes, creations, or move targets that name a
static member path are rejected. `<<<FILE STATIC path ... >>>FILE` and
`<<<FILE BINARY path ... >>>FILE` sections create generated static/binary
members, or replace existing static members marked `llm_editable`, when their
body is bounded base64 content. Immutable and metadata-only static members
remain rejected. Static records with `source_copy_path` are materialized by
copying that source file only after link checks plus byte-count and SHA-256
verification. Raw byte values in direct workspace file maps are normalized into
immutable binary static members with bounded encoded bytes for persistence.

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
The start marker grammar is exact: `# EVOLVE-BLOCK-START` with no name, or the
same token followed by whitespace and one valid block name. Prefix typos such
as `# EVOLVE-BLOCK-STARTED` are rejected. For Python candidates, marker
detection reads Python comment tokens, so marker-like text inside strings and
docstrings remains ordinary candidate text rather than creating protected
skeleton or mutable block regions. If Python tokenization fails while raw
evolve-block marker lines are present, marker validation fails closed with a
tokenization diagnostic instead of treating the file as unmarked. Mutation
rejects malformed or unmatched marker pairs before applying a change, including
missing end markers, orphan end markers, nested blocks, duplicate names, and
invalid block names.
Evolve-block skeleton preservation is currently a Python-file feature:
candidate files ending in `.py` may declare blocks with Python
`# EVOLVE-BLOCK-*` comment markers. Non-Python files can still participate in
workspace candidates as whole-file text artifacts, but marker-like declarations
using `//`, `/*`, `<!--`, or `#` prefixes in non-`.py` files fail workspace
validation with `unsupported_evolve_block_marker_syntax`. This fail-closed
boundary prevents a JavaScript, HTML, or text file with intended block markers
from being silently treated as an unmarked full-file replacement target.
Block names are prompt-visible persisted labels. They must use the ASCII
manifest-safe block-name grammar, must not contain Unicode format controls, and
must not look like secrets; unsafe names fail as malformed evolve-block markers
before mutation or seed loading proceeds.
Successful workspace mutations revalidate evolve-block markers across the full
resulting file set, including newly created files and untouched siblings, before
returning a mutated candidate.
Problem loading also prevalidates seed marker layouts for top-level `.py` seeds
and files inside seed workspaces, so malformed seed markers fail before
evaluation starts.

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
Each SEARCH payload must match exactly one target in the current scope. If the
same SEARCH text appears more than once in a whole file, within one evolve
block, or across multiple evolve blocks, the mutation is rejected with
`ambiguous_search_match` before any partial edit is applied.
SEARCH/REPLACE matching is line-ending tolerant: patch text and candidate text
are compared through an LF-normalized view, and accepted replacements are
written back using the matched candidate span's dominant line ending while
leaving surrounding text unchanged. Mixed-line-ending files are not globally
normalized by diff application.
When SEARCH/REPLACE blocks are present, all non-whitespace text outside those
blocks must be proposal metadata or the mutation is rejected as
`malformed_diff:unconsumed_text`.
Proposal metadata is recognized only as a leading contiguous response preamble.
It can use one-line `IDEA:`, `RATIONALE:`, or `HYPOTHESIS:` fields, or bounded
multiline blocks such as `[IDEA]...[/IDEA]`. Wrapped colon-style continuation
lines before a later proposal marker are rejected before mutation application as
`malformed_proposal_metadata:multiline_continuation`; unterminated multiline
blocks are rejected as `malformed_proposal_metadata:unterminated_section`.
Mutation parsing strips a single markdown code fence only when it wraps the
whole response, such as a `diff`-tagged fence around a complete SEARCH/REPLACE payload.
Triple-backtick text inside replacement code, file sections, and block sections
is preserved as candidate content.
File and block section delimiters are recognized only when `<<<FILE`,
`>>>FILE`, `<<<BLOCK`, or `>>>BLOCK` start a line. Marker-looking substrings
inside ordinary code lines are preserved as candidate content; delimiter lines
themselves remain reserved envelope syntax.

`mutation_mode: full` accepts a complete replacement. For one marked block, a
raw replacement becomes that block's body. For one or more marked blocks, named
block payloads are also accepted:

```text
<<<BLOCK solve
def solve():
    return 2
>>>BLOCK
```

The built-in prompt template is mode-aware: `diff` asks for SEARCH/REPLACE
blocks, while `full` asks for full-file, full-block, or file-section
replacement payloads. It also asks the model to keep same-response edits
consistent, so a new helper, config value, file, import, or block reference is
paired with the matching definition or topology change. Custom
`prompt_variants` templates can still override or omit that wording.

Mutation payloads are a text boundary. Direct calls to
`apply_candidate_mutation()` or `apply_workspace_mutation()` with `None`,
numbers, lists, or other non-string payloads return
`non_text_mutation_payload` without changing the candidate. Runtime failure
history stores a bounded representation, payload type, text/non-text flag, and
hash for those failed proposals.

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
Ambiguous spellings with empty path components, `.` components, leading `./`,
redundant separators, or trailing separators are rejected instead of being
silently canonicalized. Traversal, drive-letter, colon-component, POSIX
absolute, and UNC-style leading-backslash paths are rejected instead of being
reinterpreted as relative workspace paths. ASCII control characters,
Windows-reserved device names,
wildcard/quote/pipe characters, and trailing spaces or dots are rejected before
workspace construction or mutation application. Generated candidate paths
cannot contain dot-prefixed or `__pycache__` components, so `.env`,
`.git/config`, `pkg/.hidden.py`, and `__pycache__/cached.py` are rejected
before they can be evaluated or exported. Candidate path components are limited
to 255 characters, and normalized
relative paths are limited to 1024 characters before materialization. Unicode
names are NFC-normalized; ordinary non-ASCII letters are allowed, but Unicode
format controls such as right-to-left override and zero-width joiner are
rejected. Path labels must also be stable under Unicode compatibility
normalization, so compatibility forms such as fullwidth Latin letters,
Kelvin-sign aliases, non-ASCII separator spaces, and surrogate code points are
rejected. Candidate path labels that look like secrets are rejected before
workspace construction, seed loading, mutation application, prompt rendering,
history logging, or export.
Candidate workspace construction rejects file sets whose raw names normalize to
the same relative path. Materialization also rejects case-folded host-path
collisions before writing files. During evaluation, materialization failures
such as case-folded host-path collisions are returned as invalid
`materialization_error` results and can be logged in failure history instead of
aborting the run. Duplicate edit sections for the same `<<<FILE path ...>>>`
target are rejected before application. Workspace topology commands are
prevalidated before partial application: duplicate topology sources, duplicate
move targets, edits that collide with delete/move sources or move targets,
chained move/delete sources, duplicate `PRIMARY` commands, and non-empty
command bodies are rejected before the original workspace is replaced.
Candidate workspaces require a typed text file set: every path and file content
must be a string, and `primary_file` must be a string that names a present file
after canonicalization. File contents must be UTF-8 encodable before workspace
construction, mutation acceptance, evaluation, or export. Empty `Program`
records materialize an empty default primary file before they are logged or
archived.
For `Program` objects that include `files`, the workspace file set is
canonical; the legacy `Program.code` compatibility view is normalized from the
primary workspace file.
File/block envelopes are not represented as a complete mutation AST yet, but
unmatched, orphaned, nested, duplicate-name, empty-name, invalid-name, and
unknown-block-target sections fail before any partial edit is applied.
Same-line section envelopes such as `<<<FILE main.py>>>FILE` and
`<<<BLOCK core>>>BLOCK` are malformed; section headers must end with a newline
before the body or closing marker.
When block sections are present, all non-whitespace text outside those sections
must be proposal metadata (`IDEA`, `RATIONALE`, or `HYPOTHESIS`) or the mutation
is rejected as `malformed_block_sections:unconsumed_text`.

In `full` mode, the content inside `<<<FILE ... >>>FILE` becomes the file's new
content, unless the target file contains evolve blocks, in which case the
existing full-block rules apply: the section body is a raw one-block body or
named `<<<BLOCK ...>>>BLOCK` payload, not a complete replacement file. New
files can be created in `full` mode, including empty files when the section
body is empty. Final newlines and blank lines in full-mode file, file-section,
and block-section bodies are preserved.
When a response contains file sections, all non-whitespace text outside those
sections must be proposal metadata (`IDEA`, `RATIONALE`, or `HYPOTHESIS`) or
the mutation is rejected as `malformed_file_sections:unconsumed_text`.
Workspace topology can be changed with command file sections:

```text
<<<FILE DELETE package/old_helper.py
>>>FILE

<<<FILE MOVE old_module.py -> package/new_module.py
>>>FILE

<<<FILE PRIMARY package/new_module.py
>>>FILE
```

If an ordinary file path begins with a topology keyword, prefix the header with
`PATH` to force file-edit parsing:

```text
<<<FILE PATH DELETE helper.py
replacement for the file literally named DELETE helper.py
>>>FILE
```

`RENAME` is accepted as an alias for `MOVE`. Source and target paths use the
same safety normalization as ordinary file-section edits. Missing sources,
target collisions, unsafe paths, no-op moves, and last-file deletion are
rejected before the original workspace is replaced. Command sections must have
empty bodies; body text in `DELETE`, `MOVE`/`RENAME`, or `PRIMARY` sections is
rejected as `unexpected_command_body` before partial topology mutation. A
single mutation may contain at most one `PRIMARY` command. `PRIMARY` is
validated after same-mutation edits, deletes, and moves, so it can target a
file created or moved by the same mutation independent of section order. If a
mutation deletes the current primary file, it must include an explicit
replacement `PRIMARY` target.

Multi-block full replacement rejects duplicate `<<<BLOCK name ... >>>BLOCK`
sections before applying any replacement, so every named block target must be
unambiguous.

## Design guidance

- Make seeds intentionally improvable.
- Keep validators deterministic when possible.
- Return every metric you want future prompts or analysis to see.
- Run manifests persist the effective objective schema under
  `problem.objective_schema`, including normalized metrics, directions, bounds,
  weights, source labels, effective primary flags, `primary_metric`,
  `primary_bounds`, and `metric_count`.
- Use evolve blocks when the skeleton/API must stay fixed.
- Problem-load failures for malformed metrics, missing validators, empty tasks,
  and missing seeds are reported as CLI setup errors before artifact
  preparation or evolution starts.
- Included smoke-example validators enforce concrete return contracts for their
  checked behavior: `hello_world` accepts exact `str` greetings, `sorting`
  accepts exact `list` outputs, and `workspace_math` accepts exact `int`
  helper-dependent results.
- Classify example seeds by search pressure before using them as evidence:
  `hello_world`, `circle_packing`, and `matrix_multiplication` have measurable
  seed-to-best headroom, while `sorting` is an already-solved neutral
  plateau/diversity smoke fixture.
- The `matrix_multiplication` smoke validator counts scalar multiplications
  inside `matmul2` only and rejects known import/library delegation,
  module-level dead-code counters, and fixed-three-case lookup shortcuts. It
  remains a 2x2 smoke fixture rather than an AlphaEvolve tensor-rank benchmark.
- Direct and loaded prompt context entries render in deterministic path order.
  Context-source metadata is matched by path, duplicate metadata records for a
  path are selected canonically rather than by insertion order, and generated
  program prompt diagnostics retain the context order plus rendered prompt hash.
- Treat the current problem model as Python-only. Multi-file workspaces are
  local text file sets, not arbitrary build-system or containerized projects.
- Treat seed workspaces as UTF-8 text workspaces for now. Non-UTF-8 files in
  loaded seed workspaces are skipped with byte/hash provenance, but binary
  artifacts and artifact manifests are not first-class candidate members yet.
- Keep seed workspaces, context files, and plugin context compact. Prompt
  assembly does not yet enforce a global context-window budget across parent
  code, inspirations, context, failures, and feedback.
- Treat candidate abstraction as code-file evolution for now; richer
  problem-defined candidate representations are tracked as AlphaEvolve-alignment
  work.
