# Architecture

LibreEvolve is a Python research framework for LLM-guided program mutation. It
is AlphaEvolve-inspired, but intentionally smaller: the current runtime is
local, Python-only, and filesystem-backed, with opt-in candidate-level asyncio
evaluation inside a proposal batch.

## Top-level flow

The CLI entrypoint is [`libreevolve/cli.py`](../libreevolve/cli.py). Importing
that module does not load `.env`, and `show` remains history-only. The `run`
command loads `.env` during run setup with `override=True`, before backend
preflight, and records non-secret dotenv source metadata in the run manifest.
The `run` command:

- loads a problem directory with `load_problem()`
- merges problem-local `config.yaml` into the default `Config`
- validates configured built-in plugin specs before overwrite cleanup
- calls `evolve(problem, config)`, where core resolves configured built-in
  plugins unless explicit plugin instances are provided by a direct caller
- writes the best archived primary-file view to `runs/<problem_name>/best.py`
- writes the complete best candidate file set to
  `runs/<problem_name>/best_workspace/`

## Problem loading

`load_problem()` in [`libreevolve/problems/loader.py`](../libreevolve/problems/loader.py)
constructs a `Problem` from:

- `task_description.txt`
- `metrics.yaml`
- `validate.py`
- `initial_programs/*.py` or seed directories under `initial_programs/`
- optional `context/*.{txt,md,py,pdf}`

The loader keeps all declared metrics, picks a primary evaluator-sourced
metric, exposes metric direction/bounds/source helpers, and loads deterministic
prompt context. Valid
text/code context is decoded as UTF-8 and preserved exactly; invalidly encoded
selected text context that cannot be decoded is kept out of prompts and
retained as skipped-source provenance. PDFs are extracted with `pypdf`, with
failed or no-text extraction retained as diagnostics rather than prompt
context. Source-byte, total-byte, PDF-page, and PDF-character limits bound
ingestion separately from rendered prompt excerpts. Context loading walks
`context/` recursively, honors optional segment-aware `context.yaml`
include/exclude patterns and per-source character budgets, skips dot-prefixed
supported context files unless an include pattern
explicitly names a dot-prefixed component, renders prompt citation headers, and
records hashes, spans,
extraction status, PDF document page ranges, and rendered-excerpt PDF page spans
in the run manifest. Prompt citation headers include exact rendered-excerpt
PDF page spans such as `pages=1:0-20,3:60-80` when available, exact
non-contiguous excerpt page lists when spans are absent, and only fall back to
document-level page ranges when no excerpt page metadata exists.
The run manifest also records
the effective context policy: active manifest file hash, include/exclude rules,
character budget, byte/PDF extraction budgets, per-include pre-filter matches
and post-filter selected matches, unmatched include patterns,
hidden-source policy, selected/skipped counts, and hashed diagnostics for
unsupported, not-included, hidden-not-included, or excluded context files.
Unmatched includes remain setup diagnostics rather than hard load failures.
Include/exclude patterns must be safe
problem-relative globs; traversal, absolute or drive-style roots, backslashes,
control characters, and secret-like text fail problem loading. Single-star
patterns match within one path segment, while `**` matches zero or more path
segments for recursive selection. Selected context
source labels that look like secrets are also rejected before prompt rendering
or manifest persistence. Symlinks and Windows junctions under `context/`,
including linked context manifests, are rejected before context selection or
reading. Fitness is the normalized
primary metric: `maximize` maps low-to-high bounds to `0..1`; `minimize` inverts
that scale.

CLI startup and direct `evolve()` calls preflight default and staged evaluator
entrypoints before run artifact mutation. The preflight imports validator
modules, checks callable `evaluate`, verifies the fixed one-, two-, or
three-argument public call shapes, and rejects invalid staged paths before
overwrite cleanup or manifest creation. Async, generator, variadic,
keyword-only, and extra-parameter validators are rejected during preflight.

## Candidate representation

Candidates use `CandidateWorkspace`: a text file set with a `primary_file`.
`Program.code` remains as a compatibility view of the primary file, so existing
single-file seeds, validators, prompts, and `best.py` workflows still work.
When a program has a workspace file set, the file set is canonical and
`Program.code` is derived from `files[primary_file]`.
Workspace construction validates that file paths and contents are strings and
that `primary_file` names a present file; malformed serialized workspace
records are rejected instead of being coerced into source text.
This is still a code-file abstraction. AlphaEvolve-style problem-defined
candidate abstractions, such as raw solution objects, constructor functions, or
paired solution/search representations, are not first-class hooks yet.
Seed files may mark evolvable regions:

```python
# EVOLVE-BLOCK-START main
def solve():
    return 1
# EVOLVE-BLOCK-END
```

Mutation application lives in [`libreevolve/core/candidate.py`](../libreevolve/core/candidate.py).
When markers are present, surrounding skeleton code is preserved and mutations
are constrained to marked regions. Multiple blocks are supported. Existing
unmarked `initial_programs/*.py` remain valid. Mutation application validates
marker pairing, nesting, names, duplicate block names, and orphan end markers
before applying a change, so malformed skeletons fail closed instead of falling
back to whole-file mutation. Problem loading prevalidates evolve-block markers
in top-level seed files and seed workspace files, so malformed seed task
boundaries fail before evaluation starts. Initial seed files and workspace
entries must be real problem-local files/directories: symlinks and Windows
junctions under
`initial_programs/` are rejected instead of followed. Loaded seed files are
UTF-8 text; invalid encoding is reported as a path-aware problem-load
diagnostic.
Loaded seed artifacts keep problem-relative provenance in manifests and seed
history/failure rows through `seed_source_path`, `seed_source_kind`, and
`seed_index`, so duplicate baseline workspaces can be audited without host
absolute paths.
Hidden and cache seed paths are skipped by default, but
`initial_programs/seed_policy.yaml` can explicitly include selected
dot-prefixed or `__pycache__` paths and exclude others. Excludes take
precedence, and broad include patterns do not opt into reserved paths unless
the pattern itself names the reserved component. Included reserved seed paths
are persisted as `allowed_reserved_paths` in seed provenance and as
`workspace_path_policy` on history rows.

Two mutation modes are supported:

- `diff`: default SEARCH/REPLACE blocks, accepting both compact local fences
  and AlphaEvolve-style `<<<<<<< SEARCH` / `>>>>>>> REPLACE` fences
- `full`: complete replacement of the whole unmarked program, the single marked
  block, or named multi-block replacements with `<<<BLOCK name ... >>>BLOCK`

The default prompt template is mutation-mode aware. In `diff` mode it asks for
compact or AlphaEvolve-style SEARCH/REPLACE fences. In `full` mode it asks for
full replacement content, including full-file `<<<FILE ... >>>FILE` sections
for workspace candidates and named `<<<BLOCK ... >>>BLOCK` sections for
multi-block replacements. Custom prompt templates remain supported and may
ignore or render the `{mutation_mode}` and `{mutation_instructions}` fields.
Direct prompt rendering treats `template=None` as the only sampler/default
fallback signal; explicit blank template strings are rejected by prompt-template
validation.
SEARCH/REPLACE application requires each SEARCH payload to identify exactly one
target in the current replacement scope. Duplicate matches in a whole file,
inside one evolve block, or across multiple evolve blocks are rejected with
`ambiguous_search_match` before any partial edit is committed.

For multi-file candidates, LLM responses can wrap edits in file sections:

```text
<<<FILE package/module.py
<<<SEARCH
old code
===
new code
>>>REPLACE
>>>FILE
```

`full` mode can replace existing files or create new files with the same
`<<<FILE path ... >>>FILE` envelope, including intentionally empty new files
when the section body is empty or only blank lines. Candidate paths are
normalized and cannot escape the candidate workspace. File-section headers are
parsed through the
same relative-path normalization used by `CandidateWorkspace`, so nested paths,
hyphens, spaces, Unicode filename characters, and Windows-style backslashes are
accepted when the resulting normalized path is safe. Ambiguous spellings with
empty path components, `.` components, leading `./`, redundant separators, or
trailing separators are rejected rather than silently canonicalized. Traversal,
drive-letter, colon-component, POSIX absolute, and UNC-style leading-backslash
paths are rejected before mutation application or materialization. ASCII control
characters, Windows-reserved device names, wildcard/quote/pipe characters, and
trailing spaces or dots are also rejected. Dot-prefixed and `__pycache__`
components are rejected for generated candidate paths, so `.env`,
`.git/config`, nested hidden files, and interpreter cache files cannot enter
candidate workspaces through direct construction or mutation envelopes unless
the workspace was created from a seed policy that explicitly allowlisted the
exact reserved path. That allowlist is preserved across mutation so selected
seed dotfiles can be edited, but it does not grant blanket permission to create
new reserved paths. Path components longer than 255 characters and normalized relative
paths longer than 1024 characters are rejected before materialization. This
does not yet provide a canonical collision model: workspace
construction rejects raw paths that
normalize to the same relative name, and materialization preflights
case-folded host-path collisions before writing files. Materialization is an
exact snapshot operation for a normal target directory: after preflight
succeeds, existing non-link entries under the target root are removed before
the candidate file set is written, so stale files cannot remain from an older
candidate. Link or junction target roots, ancestors, and existing nested
entries are rejected rather than followed or deleted. Mutation-envelope
handling rejects duplicate edit sections for the same `<<<FILE path ...>>>`
target. Workspace topology commands are prevalidated before partial
application: duplicate topology sources, duplicate move targets, edits that
collide with delete/move sources or move targets, chained move/delete sources,
duplicate `PRIMARY` commands, and non-empty command bodies are rejected before
the original workspace is replaced.
Envelope parsing now rejects unmatched, orphaned, nested, duplicate-name,
empty-name, invalid-name, and unknown-block-target `<<<FILE` / `<<<BLOCK`
sections before applying partial edits. It is still a local envelope parser
rather than a full mutation AST.
Command file sections can delete files, move/rename files, and change the
workspace primary file. Command sections must have empty bodies, and a single
mutation may contain at most one `PRIMARY` reassignment. `PRIMARY` is resolved
after same-mutation file edits, deletes, and moves, and deleting the current
primary file requires an explicit replacement primary:

```text
<<<FILE DELETE obsolete.py
>>>FILE
<<<FILE MOVE old.py -> pkg/new.py
>>>FILE
<<<FILE PRIMARY pkg/new.py
>>>FILE
```

## Evolution loop

The core loop lives in [`libreevolve/core/loop.py`](../libreevolve/core/loop.py).
For each generation it records one generation-start event, then runs
`proposals_per_generation` proposal passes. They are sequential by default. With
`async_llm_sampling`, parent/inspiration/prompt state for all siblings is fixed
before a bounded set of worker-owned LLM ensembles runs concurrently; mutation
results rejoin the following ordered path in proposal order. For each proposal
the loop:

1. samples a parent from the island model
2. runs plugin start hooks
3. samples diverse inspirations
4. builds plugin context and prompt context through `PromptSampler`
5. calls the LLM ensemble
6. optionally runs one critique reviewer or a configured synchronous reviewer
   pool on the proposed mutation
7. previews critique revisions, aggregates valid reviewer revisions by policy,
   and falls back to the original mutation if selected revisions are malformed
   but the original applies cleanly
8. applies the configured mutation mode
9. evaluates the child synchronously, or dispatches it to the bounded local
   candidate-evaluation queue when async evaluation is enabled
10. optionally applies LLM feedback graders with provenance and score
   composition
11. constructs a `Program` with metrics and structured evaluation data
12. runs plugin score hooks
13. logs the candidate and archives valid programs
14. rewards the selected backend with non-negative fitness improvement
15. records prompt reward for the selected prompt program

After the final proposal, the loop migrates elites at the configured interval,
runs generation-end hooks, and records one completed generation. With
`async_llm_sampling: true`, named local sampler tasks own distinct ensembles;
provider calls may finish out of order, while call persistence, mutation
application, evaluation dispatch, and shared-state updates follow proposal
order. Rewards are queued back through the owning worker so scheduler state is
never mutated concurrently with that worker's next generation call. With
`async_candidate_evaluation: true`, uncached sibling evaluations can also finish
out of order; feedback, plugin scoring, prompt rewards, history, and archive
admission still commit in proposal order. Exact duplicate evaluations already
in flight are coalesced without consuming a second evaluation budget unit.

This is a local, batch-scoped asynchronous pipeline, not full asynchronous or
distributed AlphaEvolve parity. Critique and feedback remain serial, proposals
do not cross generation boundaries, and queued/running state is not checkpointed
or resumed. The queue controllers and report validators live in
[`libreevolve/core/async_sampler.py`](../libreevolve/core/async_sampler.py) and
[`libreevolve/core/async_evaluator.py`](../libreevolve/core/async_evaluator.py);
`loop.py` owns prompt-batch preparation, ordered merge, cache coalescing, budget
accounting, deterministic commit, and runtime-history integration.

`on_generation_start()` is therefore a pre-prompt hook, not a pre-parent hook:
it can update state before inspiration sampling and prompt construction, but it
cannot change the already selected parent for the first proposal in that
generation.

`VALID_THRESHOLD` is currently `0.0`.

## Prompt sampling

[`libreevolve/core/prompt.py`](../libreevolve/core/prompt.py) provides
`PromptSampler`. It renders:

- task description
- explicit problem context files
- parent code, normalized fitness, metrics, and bounded recent evaluation
  feedback
- multi-file parent/inspiration contents when present
- inspiration programs with metrics
- plugin-provided context
- recent failed/rejected mutation records

Prompt assembly now applies a deterministic section-priority packer when
`prompt_max_chars` or `prompt_max_estimated_tokens` is configured. Oversized
optional string placeholders such as explicit context, extra context,
inspirations, evaluator feedback, and recent failure memory are omitted by
priority before the final rendered-prompt cap is applied; required
AlphaEvolve channels remain intact, so large required sections can still force
character-level truncation. The local caps are enforced once during mutation
prompt rendering and again at the `LLMEnsemble.generate()` boundary before
backend selection. The ensemble boundary uses a common locally available
provider-token counter for the selected role's eligible backends when one can
be discovered, including critique, feedback, meta-prompt, registry-created, and
custom roles; otherwise it records why exact counting was unavailable and uses
the heuristic token estimate. The run records prompt-size diagnostics for
rendered mutation prompts. Those diagnostics include `section_budget`, a
deterministic per-placeholder accounting record with section priorities,
hashes, character counts, estimated tokens, required/optional totals, template
overhead, required-section fit status, configured cap sources, and packing
decisions. Prompt section packing is still only fully automatic in the mutation
sampler; non-mutation roles get final-prompt validation and telemetry, not
per-section provider-token packing. Final manifests expose that boundary under
`runtime.prompt_section_packing` with schema
`libreevolve.prompt_section_packing_coverage.v1`; its embedded validation
keeps `automatic_provider_token_section_packing_complete` false and lists
mutation, critique, feedback, and meta-prompt role coverage separately.

Generated candidate metadata persists mutation prompts according to
`mutation_prompt_retention_mode`: `redacted` by default, with `full`,
`hash_only`, and `off` also supported. Each generated row records
`metadata.prompt_retention`, and manifests summarize the current prompt
retention boundary under `policies.prompt_data_retention`. Critique prompt and
mutation text retained under `metadata.critique` is bounded, redacted, and
hash-backed, while LLM feedback output previews carry bounded redaction and
retention metadata. Explicit context, plugin, provider, retrieval,
meta-prompt, and framework-owned quarantine snapshot surfaces now have
configurable or hash-only prompt-data retention policies. The shared
`libreevolve.redaction.v2` grammar is regex-based and bounded; it is not a
semantic scanner for arbitrary private data.

The feedback section renders bounded, redacted summaries of recent stage
status, execution stdout/stderr, retry/sample diagnostics, and LLM grader
feedback, plus bounded evaluator artifact path/hash summaries, bounded
stored-content excerpts for copied UTF-8 artifacts, skipped-artifact
diagnostics with field-level caps, aggregate syntax diagnostics with field-level
caps, metric-bound clamp diagnostics with field-level caps,
malformed metric diagnostics with field-level caps, sample aggregation
counts/policies with field-level caps, validator metadata summaries with
item-count and per-key caps, validator
execution boundary with field-level caps and nested resource-limit field caps,
stage/sample budget diagnostics with field-level caps,
stdin policy with
field-level caps,
diagnostic-output decode/cap/redaction metadata with field-level caps,
timeout-cleanup context with field-level caps, stage summaries with field-level
caps, configured stage threshold checks with field-level caps,
metric-threshold checks with field-level caps, and artifact/output gate checks
with field-level caps.
Failure-memory rendering also has field-level caps, including selected
LLM-grader records, so failed trial prompts can expose bounded mutation,
error, execution, and reviewer evidence without reopening full run artifacts.
Delimiter-like diagnostic text is JSON-escaped after redaction/truncation. This
is intentionally bounded evidence rather than an unbounded log dump. By
default prompts use stored artifact excerpts; `prompt_artifact_content_mode:
bounded_file` can reopen copied UTF-8 artifacts under the run directory with
byte/character caps, redaction, and path/link/binary diagnostics. Binary or
non-UTF-8 artifacts are marked as having no prompt excerpt or renderable
artifact content.
Persisted evaluator metadata uses problem-relative validator paths plus
`validate_path_hash`, `validate_path_scope`, and `validate_path_redacted`.
Nested stage config and retry-attempt metadata use the same path display
policy, so configured absolute validator paths do not leak through history
rows. Unicode format controls in visible evaluator path labels are escaped,
while ordinary non-ASCII path text remains visible.

Failed/rejected mutations are logged to `failure_history.jsonl` with parent ids,
mutation text, diff errors, changed file paths, evaluator summaries, and
repetition counts. A bounded in-memory tail of those records is rendered into
later prompts as negative examples. This is still a local recent-memory
mechanism rather than a learned retrieval system over all historical failures.
Evaluator-level synthetic diff errors are normalized before persistence:
known parser/runtime mutation reasons stay canonical, unknown strings become
`unknown_diff_error` with bounded/redacted detail metadata, and non-string direct
inputs become `malformed_diff_error`. Framework-generated evaluator failures
fill every declared metric with the finite failure penalty, set
`is_valid=False`, and persist `synthetic_failure_metrics_v1` metadata so
multi-metric histories keep a stable vector shape without hiding the failure
source.

When `capture_proposal_metadata` is enabled, mutation prompts ask the LLM to
place short `IDEA`, `RATIONALE`, and `HYPOTHESIS` sections before the patch.
The mutation parser extracts those bounded fields into candidate metadata while
leaving SEARCH/REPLACE, file-section, block-section, and full-code patch
application compatible with diff-only responses. Later prompts render bounded,
redacted proposal summaries for selected parent and inspiration programs, with
prompt-policy field caps available for proposal summary rendering.
Only the leading contiguous proposal preamble is treated as proposal metadata;
marker-like `IDEA:`, `RATIONALE:`, or `HYPOTHESIS:` lines after the first
payload line are preserved as candidate content. Proposal fields are single-line
fields; wrapped continuation text is not captured as metadata.
If critique is enabled, `metadata.proposal` is extracted from the selected
post-critique mutation, while `metadata.critique` retains original/revised
proposal summaries plus the selected `proposal_source`.

`Config.prompt_variants` provides alternate templates. The loop stores those
templates as `PromptProgram` records in `PromptDatabase`, selects prompt
programs, records prompt reward/usage, and logs prompt lineage to
`prompt_history.jsonl`. Initial untried prompt programs are selected in
configured template order, and restored prompt histories use replayed prompt
event order. Duplicate configured variants and duplicate evolved templates are
modeled as independent prompt arms with separate ids, usage counts, rewards,
and lineage; accepted prompt-history records include `template_sha256` so those
arms can be grouped by template content. A non-empty `prompt_history.jsonl` is
replayed by `PromptDatabase` before configured templates are seeded, restoring
prior prompt arms, scores, penalties, metadata, lineage, and selection state
with reward-policy compatibility checks. Whole-run resume still depends on
separate archive/controller restore. When `meta_prompt_evolution` is
enabled, the loop can periodically ask the active LLM backend to produce a
revised full prompt template with an instruction to preserve placeholders.
Prompt programs also persist a validated structured context policy with schema
`libreevolve.prompt_context_policy.v1`; the loop passes that policy to
`PromptSampler`, which can disable optional rendered channels and override
section priorities used during deterministic prompt packing. It can select the
mutation-instruction variant and keep or remove the built-in mutation-format
example block without accepting arbitrary instruction text. It can also
override proposal metadata instruction/parsing behavior for a selected prompt
arm while preserving the run-level default when unset. It can also select and
deterministically order bounded parent-feedback subsections before prompt
rendering, and can suppress or cap individual feedback sections before the
aggregate feedback cap. Execution-output fields can also be independently
capped or suppressed for `stdout`, `stderr`, and `error` before top-level
execution output or stage-summary IO is rendered, and sample/retry diagnostic
text fields can be independently capped or suppressed before rendering.
Program-output text fields can also be independently capped or suppressed
before rendering, and validator-artifact text fields can be capped or
suppressed before rendering while artifact content keeps its separate bounded
file policy. Validator diagnostics can select and cap safe evaluator-path
provenance fields, including the redacted validate path, scope, hash, and
redaction status, and can select/cap safe evaluator dependency-policy fields
derived from problem-local validator dependency provenance. They can also
select/cap safe derived evaluator stage-context fields such as stage/sample
indexes, configured validate path, stdin policy, and evaluator-data counts.
They can also select/cap safe evaluated workspace provenance fields such as
primary file, file count, and bounded file list.
Execution diagnostics can also select/cap value-free validator environment
policy, key, allowlist, and redaction-status fields.
The same policy can override upstream inspiration
strategy and sample count, and can filter upstream inspirations to programs
carrying a manifest-safe required metric before plugin context and prompt
rendering. It can filter out upstream inspirations carrying any listed
manifest-safe metric names before plugin context and prompt rendering. It can
filter upstream inspirations by finite fitness min/max bounds before plugin
context and prompt rendering. It can also require numeric inspiration metrics
to satisfy safe min/max thresholds before plugin context and prompt rendering, rank the
upstream pool by a numeric metric before final inspiration selection, and keep
loaded local context sources in path/policy order or rank selected sources by
deterministic task-term overlap against rendered source text using either the
task description or explicit safe ranking terms, filter loaded
sources by required/excluded safe content terms, then cap how many ordered
local context sources render for the prompt arm. It can also
select retained failure-memory records by recent order, oldest order, lowest
score, or highest repetition count before per-field caps are applied, and filter retained failure-memory by
required or excluded exact safe `error`/`diff_error` labels or finite score
bounds before selection and limiting. It can also filter retained
failure-memory by required or excluded safe exact changed-file paths before
selection and limiting, by required or excluded safe exact evaluation stage
names before repetition and score filtering, by required or excluded safe
text terms in the failure evidence, and by repetition-count bounds before
score filtering and selection.
The same policy
can suppress all plugin prompt context or allowlist selected plugin identity
labels before plugin context hooks run, reorder selected plugin context by safe
identity labels before aggregate prompt packing, filter bounded plugin context
text by required/excluded safe terms before prompt visibility, exclude selected
plugin identity labels before prompt-context hooks run, rank prompt-visible
plugin context sections by explicit safe terms, cap how many ordered plugin
context sections become prompt-visible, and global plus
per-label caps can bound rendered plugin context before aggregate prompt
packing. Accepted prompt history records
include `context_policy` and `context_policy_sha256`, replay checks policy
hashes, and score/penalty rows cannot silently alter the policy.
Runtime manifests also record `runtime.prompt_context_policy_coverage` with
schema `libreevolve.prompt_context_policy_coverage.v1`. That record hashes and
counts the current meta-prompt-visible policy fields, validates them against
the `libreevolve.meta_prompt_context_policy_capabilities.v1` map and
`libreevolve.prompt_context_policy.v1` schema, and keeps
`alphaevolve_context_policy_complete` false while listing unsupported
retrieval/summarization, learned semantic ranking, and deeper context-control
surfaces.
Meta-prompt responses may remain plain revised template text or return a
strict JSON object with `template` and optional `context_policy`. That request
includes a
bounded redacted prompt-performance evidence block containing reward policy,
selected prompt statistics, latest candidate outcome, prompt-arm summaries,
and recent failure summaries. Dynamic evidence keys and values are redacted and
bounded before rendering; changed keys receive short SHA-256 suffixes. The
selected current template is rendered as a separate secret-redacted, capped
prompt section with a placeholder list, and prompt-history metadata stores
evidence plus current-template hash, length, redaction, truncation, and
display-safety provenance. Prompt-history metadata keys and string values reject
Unicode format controls while ordinary Unicode metadata remains supported.
Configured and mutated prompt templates are validated against
the `PromptSampler` placeholder schema and dry-run rendered with
representative values before use. Configured seed templates use
`prompt_variant_semantic_policy: alphaevolve` by default, requiring task,
parent code/workspace, mutation instructions, at least one evaluator-feedback
channel, and at least one context/inspiration channel. Minimal externally
managed templates require `prompt_variant_semantic_policy: compatibility`.
Evolved prompt children must retain every placeholder used by their parent
prompt program; children that drop parent context channels are rejected,
quarantined, and penalize the parent prompt arm. Startup manifests still store configured prompt templates
and critique instructions as raw effective config under
`manifest.json.config.prompt_variants` and
`manifest.json.config.critique_prompt`; this is reproducibility provenance, not
a secret-safe publication format.
Prompt rewards are normalized to `0..1` using
`prompt_reward_bounds`; `prompt_reward_mode` chooses absolute final composed
score or child-minus-parent improvement as the raw reward, and
`prompt_explore_coeff` controls the prompt selector's exploration term. The
prompt database validates those reward-policy fields at direct construction
too, and prompt programs validate id, parent id, generation, use count, finite
reward sum, and JSON-safe metadata before archive insertion. Prompt scoring and
mutation also validate referenced prompt ids before lookup; missing or invalid
references are written as bounded `prompt_reference_error` rows in
`prompt_history_invalid.jsonl`.
The policy is still scalar; richer multi-metric prompt-fitness models and
experiment ablation reporting remain future work. The context policy is also
limited: it controls optional channel inclusion, packing priorities, bounded
feedback/context field allowlists, inspiration sampling/count/render caps, and
deterministic local context-source ordering, and whether plugin prompt-context
generation runs for a prompt arm, but not
retrieval/summarization algorithms, context-source manifests, plugin-internal
state, learned semantic context ranking, or learned evaluator-field extraction.

## Evaluation

[`libreevolve/core/evaluator.py`](../libreevolve/core/evaluator.py) returns an
`EvaluationResult` instead of a bare float. It includes:

- normalized primary `fitness`
- raw validator `metrics`
- `is_valid`
- per-stage outcomes
- stdout, stderr, error, elapsed time, and metadata

Declared metric bounds are normalization hints. Out-of-range scalar outputs are
kept as raw metrics and surfaced in `metadata.metric_bound_diagnostics` with
the declared range and clamped normalized value used for selection.

For compatibility, `EvaluationResult` can still be compared/subtracted like a
numeric fitness in existing tests and callers.

The default cascade is:

- mutation/diff penalty
- Python syntax check across all candidate `.py` files
- subprocess execution of `validate.py` with the candidate workspace

The syntax prefilter reports all Python syntax errors across the candidate
workspace with file, line, offset, and message metadata. Non-Python files are
skipped by this Python-only prefilter.

`Config.eval_stages` can configure local validator stages with separate
`validate_path` entrypoints, timeouts, `min_score` thresholds, sample counts,
seed-value lists, and retries. Stage seed values are passed to validators in
the JSON `stage` context; the framework does not seed validator process RNG
state automatically. Validators may keep the old `evaluate(code)` signature or
opt into `evaluate(code, workspace_path)` or
`evaluate(code, workspace_path, stage)`. Multi-sample stages aggregate numeric
metrics and stop the cascade when validity or threshold checks fail. This is a
local cascade model, not AlphaEvolve's full parallel evaluator-worker
architecture.
Stage `timeout_sec` values are per subprocess attempt, not whole-stage
budgets. Samples and retries multiply the number of attempts, and distinct
per-sample/per-stage budget accounting is still tracked as future evaluator
hardening.
Sample aggregation is likewise fixed policy: numeric metrics are averaged,
boolean metrics use `all`, and nonnumeric values fall back to the last sample.
There are no configurable worst-case, quantile, all-samples-pass, or per-metric
stage pass policies yet. When a sample is invalid, aggregate raw metrics can
still reflect the mean of the sample outputs while top-level fitness is a
penalty and top-level validity is false.

Stage numeric fields are validated at startup: `samples` must be positive,
`timeout_sec` must be positive, `retries` must be non-negative, `min_score`
must be numeric, and explicit `seeds` must match `samples`. Stage
`validate_path` entries are resolved to problem-local Python files or package
directories containing `__init__.py` before execution; missing files,
directories without `__init__.py`, non-Python files, outside-root paths, and
symlinks that resolve outside the problem directory are rejected. Remaining
cascade gaps are higher-level: arbitrary runtime-loaded helper/data provenance
outside declared evaluator data globs, metric-specific threshold policies,
richer artifact schemas, and distributed evaluator workers are not implemented.

The subprocess runs with the materialized candidate root as `cwd`, passes that
root as `workspace_path`, and adds both the candidate root and validator
directory to `sys.path`. Validators can import candidate-local modules, read
relative candidate files, and import sibling problem-local helper modules by
default. Package validator directories are imported through their `__init__.py`
entrypoints, with the problem root added so package-relative imports work. The
problem directory is not used as `cwd`, and evaluator helper/data provenance is
bounded to files under each evaluator directory. The run manifest records the
direct evaluator entrypoint files with problem-relative redacted path labels,
path hashes, streamed SHA-256 source hashes, byte counts, read-error status
when source hashing fails, and stage usage metadata. Each entrypoint also
records a `companion_sources` snapshot for sibling `.py` and common data/text
files under the evaluator directory, with streamed file hashes, byte/count
caps, skipped-file diagnostics, and a deterministic aggregate hash.
Configured `evaluator_data_include` / `evaluator_data_exclude` and per-stage
`data_include` / `data_exclude` globs declare evaluator data relative to the
evaluator directory. Matching files are hashed under `declared_data_sources`,
and three-argument validators receive the declared relative paths in
`stage["evaluator_data"]`. This declares provenance and stage context; it does
not change the validator subprocess `cwd`, which remains the candidate
workspace.

After local evaluation, `Config.llm_feedback` can run optional LLM graders for
properties that are awkward to encode in `validate.py`, such as clarity or
style. Graders run only for locally valid candidates by default unless a grader
sets `include_invalid: true`. Graders return JSON-like feedback with a numeric
score and optional discard flag. Scores are added as metrics; redacted,
bounded response previews, retention hashes, and backend indexes are recorded
under `evaluation.metadata.llm_feedback`; and weighted feedback adjusts
`Program.fitness` while preserving the raw validator metric. Feedback graders
can declare raw score `bounds` and `direction`;
`weighted_delta` uses the resulting normalized score while the raw reviewer
score remains the feedback metric. Feedback `weight` and normalized
`min_score` are finite `[0, 1]` values;
feedback metric names must be manifest-safe, cannot collide with evaluator
metrics or another feedback metric, and cannot use reserved fields such as
`feedback_adjusted_fitness`. Feedback grader prompts render bounded
full-workspace file sections with path headers, primary-file marking, basic
redaction, and compact evaluator diagnostics.
Feedback grader call and parse failures are recorded in
`evaluation.metadata.llm_feedback` as `llm_feedback_failed` records. Graders can
set bounded `failure_retries` and choose `ignore`, `penalize`, or `discard`
failure policy; policy decisions and retry attempts are reflected in feedback
records and `llm_feedback:<name>` stage metadata. Feedback `raw_response`
previews and successful parsed `feedback` text are redacted and bounded before
history persistence, with SHA-256 hashes, original/stored character counts, and
redaction/truncation flags recorded beside them. Configured
`llm_feedback[].prompt` strings are also copied into `manifest.json.config`
verbatim today, so runs with private reviewer instructions should treat the
manifest as sensitive until prompt-config redaction/hash metadata is
implemented.

After that, plugin `on_evaluated()` hooks may modify the effective fitness used
for logging and prompt reward. Prompt reward uses that final composed child
score, optionally as an improvement over the parent score. Backend reward uses
the final composed score only for evaluator-valid, archive-admitted candidates
and records zero reward otherwise. The loop records
`metadata.score_composition` with evaluator fitness, optional feedback-adjusted
fitness, per-plugin before/after scores, metric additions/changes, invalid
plugin-score rejections, and final composed fitness. Archive admission uses the
composed top-level fitness threshold but remains gated by
`evaluation.is_valid`, so a plugin cannot accidentally archive an
evaluator-invalid candidate by raising its score.

Plugins that inspect mutation text should share the core mutation parser.
`CausalPlugin` routes diff-mode factor detection through `parse_diff_blocks()`,
so compact local SEARCH/REPLACE fences and canonical AlphaEvolve fences are both
visible to its token-pattern factor analysis. Full-mode replacement payloads
are scanned directly for the same token-pattern factors. This is still a
heuristic, paper-limited approximation rather than CausalEvolve's causal
scratchpad.

The ThetaEvolve-inspired `ttt_rl` plugin emits a JSONL dataset rather than
training a model. When loaded by the CLI, it writes under the active run's
`plugin_artifacts/ttt_rl/` directory, exports `raw_score` plus clipped
`reward = max(0.0, raw_score)`, and reports path/hash/count metadata in
`manifest.json`.

The DeepEvolve-inspired retrieval plugin keeps only the latest synthesis string
in memory. Candidate metadata records the rendered plugin-context text, hash,
parent id, and inspiration ids plus bounded retrieval events with provider,
query, generation, best id/fitness, timestamp, status, result length, synthesis
hash, arXiv source IDs/URLs, source timestamps/authors, summary hashes, and
redacted/bounded error text plus structured error types when applicable. It
also writes cache snapshots when configured and reports those snapshot files as
plugin artifact metadata with counts, byte sizes, per-file hashes, retention
limits, skipped/read-error counts, and an aggregate hash. Retrieval events with
a query include `libreevolve.retrieval_transport_policy.v1` records that
classify HTTPS request state, redirects, HTTP status class, payload hash
presence, oversized payloads, missing custom-provider transport, and
TLS/certificate-looking failures. A semantic-boundary audit helper verifies
retrieval events, plugin metadata, or cache snapshots do not overclaim semantic
verification, full replay readiness, raw provider/source payload retention, TLS
certificate-chain retention, or authoritative prompt context. Completed
manifests include bounded `runtime.retrieval` summaries plus
`libreevolve.retrieval_evidence_coverage.v1`, a run-level count of which
retrieval evidence surfaces were present and a validation record that rejects
raw-payload, semantic-verification, learned-ranking, TLS-replay, and full-replay
overclaims. It still does not persist full provider/source payloads, semantic
source-content trust verification, richer ranking scores, or a systematic
debug/refinement loop.

The ImprovEvolve-inspired `modular` plugin is similar prompt-only context. It
always injects the same guidance block. Candidate metadata can attribute that
rendered block to the plugin and records a static strategy label:
`strategy_policy: static_prompt_only`,
`operation_selected: static_modular_guidance`, the described
`generate_config`/`improve`/`perturb` operations, and false
`operation_executed` / `interface_enforced` flags. No real
generate/improve/perturb operation is executed for the candidate.

## Population model

Population state is split across:

- `Program`: primary code, candidate files, fitness, lineage, metadata,
  metrics, and evaluation summary
- `MAPElites`: one quality-diversity archive
- `IslandModel`: multiple archives plus ring migration

`MAPElites` maps programs into a 3D grid using archive selection score, code
length, and TF-IDF char-4gram diversity. The performance-like axis is the
current `metadata.selection_score`, which is already normalized to `0..1` from
declared metric bounds when present and falls back to top-level fitness only
for legacy/direct records without a finite selection score. For workspace
candidates, complexity and TF-IDF diversity still use `Program.code`, the
primary-file compatibility view, rather than a canonical full-workspace
representation.

Final manifests persist a compact `runtime.history.archive_state` snapshot with
the island round-robin cursor, archive/migration/metric-sampling sequence
counters, archive sequence by program id, and per-island occupancy/elite
counts. The same snapshot now includes `archive_contents`, which serializes each
island's MAP-Elites occupied cells, elite-program ids, descriptor policy, and
archive configuration, plus `migration_replay`, which validates that migration
events are not applied as a restore engine and that archive-content restore
covers current migrated placements. `load_runtime_archive_state_snapshot()`
validates the manifest snapshot before resume use.
Final manifests also include `runtime.history.archive_event_replay_audit`, an
audit-only reconciliation that validates `archive_events.jsonl`, replays the
last admitted migration placement per target island/cell, and compares those
placements with `archive_contents`. Normal archive admissions are still not
reconstructed from migration rows, so `archive_contents` remains the restore
source.
`IslandModel.restore_cursor_state()` can apply the cursor/counter subset directly, while
`IslandModel.restore_archive_state()` restores cells and elites when supplied
with checked `Program` snapshots. `load_archive_restore_bundle()` builds those
snapshots from `manifest.json` plus `history.jsonl`, and `ProgramDatabase` can
accept the resulting `archive_state_snapshot` and `archive_programs_by_id`
during construction. `evolve()` exposes cursor restore through
`runtime_archive_state_snapshot` and full archive restore when
`runtime_archive_programs_by_id` is supplied; CLI runs can use
`--restore-archive-cursor-from-manifest` for cursor-only restore or
`--restore-archive-from-manifest` for full cell/elite restore from a prior
manifest plus sibling `history.jsonl`. Startup manifests record
`policies.archive_identity.resume_status:
manifest_archive_state_restore_supported`, the restored archive surfaces, and
`migration_event_replay: audit_only_not_restore_engine`. `archive_events.jsonl` persists
versioned migration placement events, and `load_archive_event_records()`
validates that stream as migration audit data. Full migration event-order
restore and async controller/pending-work restore remain open.
Final runtime history also includes `runtime.history.controller_state`, a
terminal drained-state snapshot for the synchronous single-process controller.
It records zero queued/running proposals, evaluations, in-flight LLM calls, and
pending archive admissions at finalization plus a compact
`controller_budget_events.jsonl` stream summary. The embedded
`libreevolve.controller_state_validation.v1` record verifies that the snapshot
is terminal and drained, rejects pending work and async/full-replay overclaims,
and preserves that boundary in the manifest. This is a terminal resume
boundary, not an async worker queue checkpoint or mid-generation restore point.
`history.jsonl` logs candidates, but it is not a serialized archive checkpoint
or MAP-Elites event stream.
Candidate records do include `metadata.archive_admission` events that state
whether a candidate was rejected by threshold, assigned to an island and cell,
replaced a cell occupant, entered only the capped elite list, or was ignored by
cell competition.
Island round-robin assignment advances only after an admission changes retained
search state; non-admitted candidates such as `not_improving_cell` attempts
record the attempted island but leave the next assignment on that island.

Descriptor normalization is configurable but still bounded to three axes per
MAP-Elites archive. The default axes are performance, serialized-workspace
complexity, and TF-IDF diversity, and `map_elites_descriptor_axes` can select
normalized evaluator metrics, numeric evaluator metadata, or numeric candidate
metadata instead. Complexity is normalized against the configured
`map_elites_complexity_max_chars` bound, while the built-in TF-IDF diversity
axis is computed against the current capped elite list. Archive-content
snapshots persist descriptor axes, a `descriptor_model` revision, diversity
reference ids, and the explicit no-rebin policy:
`no_rebin_existing_cells_cell_coordinates_are_insertion_time_snapshots`.
Existing cells are not re-binned when the reference set changes, so current
built-in diversity coordinates are documented insertion-time local heuristics
rather than stable learned descriptors.

Parent selection has configurable strategies. The default `mixed` mode preserves
the seeded exploit/explore ratio, where exploit uses the archive selection key
and explore samples a random occupied cell. Explicit parent strategies can also
select by individual normalized-metric leaders, novelty, or recency. Metric
leaders are ordered primary-metric first, then remaining configured metrics,
then unconfigured normalized metrics alphabetically. Metric parent selection
cycles through that target-metric order and records the selected strategy,
parent id, and target metric on generated candidate metadata. Recency ranks by
the archive update sequence first, then generation and score.

Inspiration sampling is also configurable. `mixed` is a deterministic priority
cascade over normalized-metric leaders, novelty-ranked candidates,
selection-score leaders, and random fill for any remaining slots; `selection`,
`metric`, `novelty`, `recency`, and `random` are available as explicit policies.
Inspiration sampling excludes the selected parent and deduplicates migrated
copies by program id. Generated candidate metadata records
`metadata.inspiration_selection` with the strategy, requested and selected
counts, selected ids, and metric target/program pairs for metric leader
policies. This is still an in-memory archive policy rather than a queryable
evolutionary database, and it does not yet use feedback text, lineage diversity,
or persisted novelty indexes.

Direct database archive admission maintains a run-local archive id registry and
rejects duplicate ids before mutating MAP-Elites/island state. Migration uses
canonical candidate-id references across islands rather than cloned ids, skips
duplicate target placements, records in-memory placement metadata, and appends
versioned placement records to `archive_events.jsonl`. Full replayable archive
snapshots and restore loaders remain future work.

LibreEvolve stores metric vectors and now annotates each program with
`metadata.normalized_metrics` for declared numeric objective metrics plus an
equal-weight `metadata.selection_score`. Evaluator-sourced metrics are required
from validators; feedback-sourced non-primary metrics can be filled only by
`llm_feedback` graders configured with `objective_metric: true`; plugin-sourced
non-primary metrics can be filled by plugin hooks as validated metric side
effects; final-fitness-sourced non-primary metrics are synthesized from the
candidate's final composed fitness after plugin score hooks run. MAP-Elites
performance placement, cell replacement, elite ranking, and exploit/best
sampling use that selection score with final composed fitness as a tie-break.
Final runtime manifests also include `runtime.history.objective_frontier`, a
bounded diagnostic Pareto frontier over complete declared normalized metric
vectors, and `runtime.history.objective_metric_leaders`, a diagnostic
best-program view for each declared normalized metric. They also include
`runtime.history.objective_metric_archives`, a bounded top-program archive view
for each declared normalized metric,
`runtime.history.objective_primary_archive_readiness`, a scalar-primary versus
retained-overlay readiness audit, and `runtime.history.lineage_index`, a
bounded best-valid-programs view grouped by root lineage. It also includes
`runtime.history.score_index`, a bounded top-valid-programs view ranked by
selection score and final fitness,
`runtime.history.descriptor_index`, a bounded top-program view for finite
archive-admission descriptor values such as diversity, complexity, and
performance, and `runtime.history.feedback_index`, a bounded feedback-record
view grouped by LLM feedback grader. Parent and inspiration sampling can use a `frontier` strategy to
surface non-dominated retained programs with complete declared normalized
metric vectors, and a `lineage` strategy to cycle or render the best retained
representative for each root lineage. Admission thresholds, archive
replacement, backend rewards, and sampling replay still use scalar/live
policies. The MAP-Elites objective archive policy is independently checkable
with `validate_map_elites_objective_archive_policy()`, which keeps the current
bounded retention contract separate from primary Pareto/frontier replacement.
The manifest resurfacing view is independently checkable with
`validate_resurfacing_index_summary()`, which validates deterministic
rank-fusion records without claiming a durable database table. Richer
Pareto/frontier archive replacement plus a full persisted database index remain
open.

## Backend selection

[`libreevolve/llm/ensemble.py`](../libreevolve/llm/ensemble.py) wraps one or
more backends. The default `ensemble_strategy` is `ucb1`, implemented as a
heuristic adaptation of UCB1 over admission-gated valid fitness improvements.

An experimental `throughput_depth` strategy layers optional backend metadata
(`cost`, `latency`, `depth`, `role`) over UCB scores so configs can distinguish
cheap breadth models from deeper models. This is a scheduling concept, not a
verified reproduction of AlphaEvolve's Gemini Flash/Pro policy.
The current scoring formula uses only numeric `cost`, `latency`, and `depth`;
it first selects each non-excluded backend once, then lets metadata influence
selection. Call telemetry also records a bounded
`throughput_depth_lane_evidence` metadata trace with eligible lanes,
normalized inputs, and recognized fast-breadth/strong-depth labels when
`model_lane` or `role` metadata declares them. Backend metadata `role` is an
optional live routing lane: if one or more backends declare a role matching the
current LLM call role, selection is restricted to those backends; if no backend
declares that role, the global backend bandit remains active. The ensemble
constructor validates strategy names, exploration coefficients,
retry/fallback controls, and one JSON-safe
backend-metadata mapping per backend before calls can be generated.

Mutation calls are the default reward-accounted ensemble pulls and receive
archive-improvement rewards after evaluation. `llm_reward_accounted_roles` can
opt additional manifest-safe roles into reward accounting; roles outside that
configured policy are telemetry-only records that preserve call provenance but
do not advance backend counts or become rewardable call ids. Scheduler
snapshots and durable ledger replay now include role-accounting summaries for
successes, failures, reward-accounted calls, telemetry-only calls,
retry/fallback attempts, and adapter-internal provider attempts, plus
provider-reported token totals, provider-failure category counts, and the
effective `reward_accounting_policy`. Scheduler snapshots now also include
`role_scheduler_state`, which keeps per-role backend counts, wins, total pulls,
and rewarded/unrewarded call ids for audit and validated restore. The configured
`llm_role_scheduler_scope` is preserved in startup manifests, scheduler
snapshots, and runtime accounting so shared versus role-owned selection is
auditable after the run. Per-call
`scheduler_policy` records whether selection used the global bandit, an
explicit `llm_role_backend_indices` backend lane, or backend `role` metadata.
Configured `llm_role_call_limits` enforce logical `generate()` call quotas by
validated role or manifest-safe prefix scope such as `feedback:*`, and persist
restorable exact-role `role_call_limits` consumption in
scheduler/runtime accounting. Non-mutation reward-signal semantics, live
token/cost/provider-attempt budget stop policy,
quarantine/penalty policy, live provider pricing/default capture, and
provider-output replay remain future work. Provider cost is audit-accounted
when backend metadata supplies `cost_usd_per_million_tokens` and provider
usage supplies `total_tokens`; the resulting micro-dollar estimate is persisted
in role accounting and rendered as `cost_usd` in runtime LLM budget reports.
Per-call cost-estimate records identify configured backend metadata as the
pricing source, provider usage metadata as the token-count source, and explicitly
avoid claiming live provider pricing. A companion `cost_estimate_status` record
keeps not-estimated cases explicit instead of silently treating missing local
rates or missing token totals as free calls.
Backend metadata can also supply `prompt_max_estimated_tokens`; the ensemble
combines that eligible backend/model prompt-token cap with the global cap
before provider calls and records the effective/global/backend caps in call
telemetry. When the selected role's eligible backends share a local tokenizer
counter, call telemetry also records exact provider-token counts and the
role-scoped capability record; otherwise it records the unavailable reason and
uses the heuristic character-derived estimate. This is still final-prompt
fitting, not complete provider-tokenizer-backed section packing for every
rendered prompt component. `runtime.prompt_section_packing` validates the
current role coverage and identifies non-mutation prompt builders as
final-boundary-only.
Final runtime manifests
record `runtime.llm_scheduler` as a JSON-finite scheduler snapshot validated
against the `LLMEnsemble` restore contract, or as explicit `not_initialized` /
`unavailable` / `invalid` diagnostics when no mutation LLM was constructed or
the exposed state cannot be trusted. Direct `evolve()` callers can restore a
validated scheduler snapshot with `runtime_llm_scheduler_state_snapshot`, and
CLI runs can use `--restore-llm-scheduler-from-manifest`.

For OpenAI, `api_mode` controls routing. `auto` preserves legacy routing:
Chat Completions unless `reasoning_effort` is set, otherwise Responses. Explicit
`responses` can force Responses without reasoning, and explicit
`chat_completions` is rejected with `reasoning_effort`. Startup manifests
record `policies.provider_capability_lookup` to make the boundary explicit:
LibreEvolve uses local static validation and does not query live provider model
registries, service/API versions, or account availability before a run.

The backend adapters still return generated text, but `LLMEnsemble` validates
prompt payloads and call-role labels before scheduler selection, then wraps
calls with normalized telemetry containing role, backend, backend metadata,
strategy, API mode, prompt/output sizes and hashes, latency, success/error
status, and backend counts before/after the call. Successful mutation/critique
calls are attached to candidate metadata, feedback calls are attached to
feedback records, and meta-prompt calls are attached to prompt-history
metadata. Empty, non-text, oversized, refusal, or tool-call-only backend outputs
are recorded as categorized failed call attempts with retry/fallback eligibility
before success counters advance.
Call `id` values are deterministic ordered-call-stream identities for in-run
reward linkage. They include per-run sequence, backend/role/attempt
coordinates, and prompt hashes, so matching deterministic call streams produce
matching ids while repeated calls inside one stream remain distinct.
Built-in adapters copy safe provider usage counts, request/response ids, and
finish reasons into call telemetry when SDK responses expose them.
Built-in adapters also record safe `adapter_retry` telemetry for their
configured internal provider retry cap, provider attempts, failed attempt
count, and exception type labels. Raw provider diagnostics, configured
provider-cost accounting, and token-budget stop policy are available as bounded
telemetry and live run-budget inputs; live provider pricing remains out of
scope. Provider
exception text is redacted and truncated before it is stored in telemetry, while
`provider_failure_category` classifies failures as provider-response, timeout,
rate-limit, transport, provider client/server status, or unknown. Failed SDK
exceptions with safe integer HTTP-style status codes also retain
`provider_status_code`. The ensemble supports configured same-backend retries
capped at `10` and optional fallback to another backend; each attempt is
recorded with retry/fallback indexes and whether it will retry or fallback. If
failed, the call also records `provider_failure_policy` with the local
retry/fallback decision and, when `llm_role_failure_quarantine_after` is
configured for that exact role, role/backend quarantine state after exhausted
failures. Runtime cancellation-policy manifests expose matching timeout
quarantine actions and `quarantine_record` evidence for configured roles.
Strict ledger replay returns
`provider_failure_policy_summary` so the failed-call policy evidence can be
audited by role, failure category, retry/fallback decision, and
quarantine/penalty decision. If
all provider attempts fail, mutation calls can still abort before
candidate/evaluation logging. Feedback graders apply their configured failure
policy, critique calls fall back to the original mutation with bounded failure
metadata, and meta-prompt calls record rejected prompt mutations instead of
aborting already-logged candidate work. Scheduler
snapshots and ledger replay summarize provider-failure categories and policy
decisions by role as audit evidence, not as cross-role penalty or stop-policy
decisions.
Scheduler metadata, counts, and rewards are stored privately; public
metadata/counter/state accessors return defensive copies, and direct state
restoration goes through validated `restore_scheduler_state()` input.
The runtime manifest persists a final scheduler snapshot for inspection and
future resume design, but the current core loop does not load it back into a
new process.
Validated LLM call roles are passed through to backend implementations as a
`role` keyword on original, retry, and fallback attempts. `llm_prompt_roles`
can configure bounded system/developer instructions per call role; OpenAI
receives structured system/developer messages or input items, Anthropic
receives a composed provider `system` field, and Ollama receives a system
message. Omitted roles retain the default single user message/input item.
Built-in backend specs expose validated request parameters for `temperature`,
`top_p`, provider-supported stop sequences, and provider-supported request
seeds; effective normalized values and hash-only prompt-role policy metadata
are stored in call telemetry. Built-in adapters also persist
`backend_defaults` with LibreEvolve's effective local output-token cap,
provider internal retry cap, configured request timeout or `null`, API mode,
and OpenAI reasoning/API-mode policy when relevant; remote provider SDK
defaults and pricing are not inferred.
Endpoint/client context is explicit when configured: OpenAI backends accept
`base_url`, `organization`, and `project`; Anthropic backends accept
`base_url`; Ollama backends accept `host` and use a configured
`ollama.Client`. Safe accepted values are manifest config and call-log
`client_context` provenance. Omitted fields still inherit SDK/environment
defaults.

## Logging and artifacts

[`libreevolve/core/database.py`](../libreevolve/core/database.py) writes:

- `manifest.json`: effective run configuration, runtime metadata, and
  provenance hashes
- `history.jsonl`: append-only candidate records
- `prompt_history.jsonl`: append-only prompt-program selection/scoring records
- `best.py`: primary-file compatibility view of the final best archived program
- `best_workspace/`: complete file set for the final best archived program

Core best-artifact export stages `best.py` and `best_workspace/` under
temporary paths and only replaces the visible pair after workspace
materialization succeeds. If a replacement fails, the exporter rolls back to
the previous visible pair when one existed. The direct export helper rejects
symlink or Windows-junction visible, temporary, and backup best-artifact paths
before replacement or cleanup. Rollback and cleanup failures are retained as
secondary redacted diagnostics while the original export failure stays primary,
and unrestored backup paths are preserved rather than removed. Normal
`evolve()` finalization records `runtime.best_artifact_export` before writing
the completed manifest, including export success or failure, redacted failure
diagnostics, and refreshed best-artifact path/hash records. The CLI reads that
record and reports the saved paths or a redacted export failure.

Each history record includes primary code, candidate files, primary file,
fitness, lineage, metadata, metrics, and the structured evaluation summary.
Program records include `metadata.prompt_program_id`, which links candidates to
prompt-program events in `prompt_history.jsonl`.
Rejected archive-admission metadata is finite and JSON-safe, but it is not a
normalization layer for a restored or hook-mutated program's top-level
non-finite `fitness` or metric values. Accepted history remains strict; those
malformed rejected candidates are quarantine/invalid-stream diagnostics until a
dedicated rejected-candidate persistence policy exists.

Run-directory reuse is guarded before these writers append or replace files.
The default policy fails startup if the target directory already contains known
run artifacts; explicit overwrite removes only known run artifacts before the
new run. The manifest records the generated `run_id` and effective collision
policy, but this is provenance metadata rather than resumable state.
It also records Git state resolved from the hashed `libreevolve/` source tree
when available, `libreevolve/` source-tree hashes, problem-tree hashes, direct
evaluator entrypoint hashes, and plugin module file hashes, Python/platform
metadata, `pyproject.toml` statuses and hashes when present, package/build
metadata including selected PEP 621 fields and bounded extra `[project]`
metadata records, installed versions for declared runtime dependencies, and
explicit context selection policy/skipped-source diagnostics.
Environment provenance is scoped to direct declared runtime dependencies,
local package/platform metadata, bounded installed-distribution name/version
snapshots with parsed `WHEEL` metadata, bounded/redacted `pip_freeze`
records with a raw stdout hash, bounded/redacted `pip_config` records with a
raw stdout hash, NumPy numerical-runtime config hash/preview metadata, built-in
LLM provider SDK version records with adapter API modes, bounded accelerator
runtime environment hints and `nvidia-smi`/`rocm-smi` probe records, and
hash-only records for known project-root lockfiles
(`requirements.txt`, `requirements.lock`, `uv.lock`, `poetry.lock`,
`pdm.lock`, and `Pipfile.lock`). It is not a complete install-source/options
interpretation policy, broader build-provenance record, private package-index
policy, live provider service/API-version or provider cost or remote provider-side default
record, or accelerator budget/accounting record. The manifest-visible
`environment_reproducibility_policy` hashes the bounded evidence surfaces and
lists those unsupported surfaces explicitly so environment changes covered by
the policy affect provenance without claiming full replay readiness.
Plugin module paths are persisted as project-relative paths for files under
the repository and basename-only external markers for files outside it; the
raw resolved path is represented by `path_hash`, not by a durable absolute
path string. File-backed plugin module provenance has its own `max_file_bytes`
cap and records `skipped_max_file_bytes` or `read_error` status instead of
failing manifest construction for over-limit or unreadable module files.
Dirty Git status entries are redacted for common secret patterns before
persistence, Unicode format controls are escaped before persistence, and hashes
of the original porcelain lines are stored separately.
Source/problem tree file paths and skipped paths also redact common
secret-like substrings and store `path_hash` / `path_redacted` when redaction
changes the visible path. Unicode format controls in tree and plugin path
labels are escaped as `[U+....]`, hash-backed, and flagged with
`path_unsafe_chars_redacted`.
Their `tree_hash` values are included-file digests with
`tree_hash_scope: included_files`; skipped path/reason diagnostics are hashed
separately as `skipped_hash`, and `provenance_hash` combines the included-file
digest, skipped-diagnostic digest, and exclusion-directory policy without
reading excluded file contents.
Source/problem tree provenance also records `max_file_bytes`; regular files
larger than that cap become skipped `max_file_bytes` diagnostics before their
contents are read, read failures become skipped `read_error` diagnostics,
directory enumeration failures become skipped `directory_listing_error`
diagnostics with redacted error text, and binary files under the cap are hashed
directly as bytes.
Malformed or non-UTF-8 `pyproject.toml` files become degraded package
provenance records with `package.pyproject.status` set to `invalid_toml` or
`invalid_encoding`, preserving the file hash and byte count without treating
package metadata as valid.
Syntactically valid files with invalid dependency or build-system requirement
schemas become `package.pyproject.status: invalid_pyproject_schema` with
bounded path-aware diagnostics instead of normal dependency rows.
Missing `pyproject.toml` files are also typed as degraded package provenance
with `package.pyproject.status: missing` and `path: pyproject.toml`; package
metadata and dependency records are omitted while `installed_version_name`
records the fallback package name used for installed-version lookup.
Package metadata, build requirements, installed-package labels, and dependency
spec strings redact common secret patterns, escape Unicode format controls, and
retain hash-backed raw identity fields when the visible value changes.
Source/problem provenance skips symlinks and Windows junctions with
`link_not_followed` diagnostics rather than hashing linked target bytes.
Problem provenance resolves relative generated roots from the problem root, so
direct helper calls are not sensitive to the process cwd. The evolution loop
passes the effective run directory as an absolute generated root before
building the manifest.
Problem provenance includes ordinary problem-owned `runs/` directories; only
the active generated run root is skipped as `excluded_output_root` when it
resolves inside the problem tree. Plugin constructor parameters/spec schemas
and aggregate hashes for artifacts emitted after startup remain open.

The local controller uses `RunBudget` for generation/evaluation/evaluator-
second/wall-clock limits, detailed evaluator counters, logical LLM calls,
provider attempts, provider-reported tokens, configured cost, and retained LLM
latency. Budget consumption is written into candidate records and the completed
manifest. Detailed evaluator limits are cooperative: they stop new work after
the consuming evaluation rather than interrupting a running validator. Async
candidate jobs reserve the total-evaluation cap before dispatch; actual worker
results are accounted and logged serially during deterministic merge, while
cache reuse does not consume another evaluation. Validated budget snapshots can
be restored through direct or CLI entrypoints. This remains local accounting,
not queue-wait or worker/accelerator lease budgeting, hard cancellation, or
queued/running pending-work restore.

## Known gaps

- Candidate workspaces are local text file sets, not arbitrary-language build
  systems or external repositories.
- Materialized workspace execution uses the candidate root as subprocess `cwd`
  and import path, but it is still a local Python subprocess rather than a
  container or arbitrary build-system runner. Startup manifests record
  `policies.validator_execution` for this local-subprocess boundary.
- Evaluator timeouts attempt best-effort process-tree cleanup and record cleanup
  metadata, but this remains local subprocess management rather than a
  deterministic descendant-process guarantee, container, network sandbox, or
  general resource-limit system.
- Validator subprocesses use a minimal environment plus
  `validator_env_allowlist`; provider keys loaded through `.env` are hidden by
  default and persisted evaluator stdout/stderr is secret-redacted for common
  assignment and provider-token shapes. This is not a network sandbox.
- Candidate abstractions are code file sets with a primary file, not
  problem-defined non-code solution objects or paired solution/search artifacts.
- Proposal generation can overlap on opt-in, worker-owned local asyncio sampler
  tasks, and candidate evaluations can overlap on a separate opt-in local queue.
  Critique/feedback remain serial, and there are no distributed evaluators,
  cross-generation dependency scheduling, or resumable queued/running tasks.
- Runtime budget accounting covers local generation count, total evaluator
  calls, cumulative evaluator seconds, evaluator subprocess attempts,
  configured-stage samples, retry attempts, evaluator timeouts, sample/stage
  budget exhaustion counts, wall-clock seconds, and structured stop reasons.
  Logical LLM calls, provider attempts, provider-reported tokens, configured
  cost, retained LLM latency, and detailed evaluator counters have cooperative
  stop policies. Per-candidate compute-hours, worker/accelerator leases, queue-
  wait budgets, and hard interruption of already running work are not
  implemented.
- Archive cell/island state is persisted in manifests with full cell/elite
  restore support from accepted history; migration-event replay, pending async
  evaluations, and broader resumed experiment traces remain open. Terminal
  synchronous or local sampler/evaluator-async controller state is manifest-visible
  under `runtime.history.controller_state` with an embedded validation record
  for the drained boundary.
- LLM critique and feedback are synchronous optional passes; there are no
  parallel reviewer/evaluator workers yet.
- Proposal ideas/rationales can be parsed, stored, and rendered for selected
  parent/inspiration candidates when configured, but they are not yet scored,
  searched, or used as an indexed retrieval signal over historical candidates.
- Prompt evolution is implemented at the template boundary with configured and
  mutated template placeholder validation plus bounded absolute/improvement
  reward normalization; richer ablation reporting remains open.
- Run ids and collision policy are persisted, but archive/controller reload and
  parent-run resume relationships are not implemented.
- Prompt feedback rendering includes bounded execution output, artifact
  metadata/excerpts, sample/retry diagnostics, validator execution metadata,
  grader summaries, and opt-in bounded-file content rendering for copied UTF-8
  evaluator artifacts, but does not yet participate in a global prompt-size
  budget.
- `libreevolve show` validates ids, metrics, current-history evaluation shape,
  and archive diagnostics while streaming. For the selected current-format row
  it reports bounded lineage, prompt id/parent-selection, evaluator
  stage/accounting, LLM feedback, and run-level failure-stat summaries without
  raw prompts or mutation payloads. It also validates generation, legacy
  source, workspace files, and primary-file payloads while streaming every
  history row, so malformed unselected rows fail inspection before display.
- `libreevolve show` validates MAP-Elites cell coordinate arity, integer shape,
  non-negativity, and, when `manifest.json.config.map_elites_bins` is present,
  per-axis upper bounds. Histories without manifest/bin metadata remain
  legacy-bounded only by arity/type/non-negativity.
- LLM feedback graders receive bounded full-workspace file sections, basic
  secret redaction, and compact evaluator diagnostics.
- Mutation, critique, feedback, plugin-context, provider-output/error,
  retrieval-body, explicit-context, and meta-prompt evidence surfaces expose
  configurable retention modes or hash-only prompt telemetry. Quarantine
  snapshots still need configurable retention modes.
- Evaluator output is parsed as JSON, validated against declared scalar
  metrics, and normalized around the primary metric. Evaluator-returned
  non-scalar program outputs are not first-class attachments yet; use
  stdout/stderr or opt-in copied evaluator artifacts for that evidence.
- Persisted evaluator stdout/stderr is decoded, secret-redacted, and capped by
  `evaluator_output_max_chars` before result, stage, retry, sample, and history
  storage. Prompt feedback still renders bounded summaries and copied UTF-8
  artifact excerpts only; full/live artifact-content retrieval and global
  prompt section packing remain open.
- Config validation now rejects unknown problem config keys, invalid
  mutation/ensemble enums, malformed backend specs, bad evaluator-stage
  numeric fields, invalid top-level population/runtime ranges, and malformed
  LLM feedback grader specs. Malformed YAML and scalar/list top-level
  `config.yaml` files now fail with path-aware startup diagnostics.
  Built-in loaded plugin constructor parameters are recorded under
  `runtime.plugin_state.loaded_specs`, and built-in plugin specs validate
  supported constructor options before plugin construction. Arbitrary
  custom-plugin constructor introspection is not implemented yet.
  `Config.plugins` entries must be manifest-safe labels or spec mappings and
  are revalidated by the database before manifest persistence. Core `evolve()`
  resolves configured built-in specs when explicit plugin objects are omitted.
  Runtime manifests record `runtime.plugin_state` to distinguish configured
  labels from loaded runtime plugin identities.
- OpenAI API mode is now an explicit `api_mode` policy with legacy `auto`
  routing and manifest records, but it is still not a live provider capability
  lookup.
- `manifest.json` records configuration plus Git/source/problem/plugin-module
  provenance and runtime aggregate hashes for known emitted artifact files and
  directories, and built-in loaded-plugin constructor spec records, but not a
  general plugin config schema/registry or resume/controller state.
- `Config.seed` controls local Python-random choices. Configured prompt
  variants are selected in config order, restored prompt histories replay event
  order, database-created prompt ids are deterministic, and loop-created seed
  or generated candidate ids are deterministic. Completed and aborted runtime
  manifests persist the final run-local RNG state under `runtime.rng`, and
  direct callers can pass a validated snapshot back into `evolve()` through
  `runtime_rng_state_snapshot`; CLI runs expose that path with
  `--restore-rng-from-manifest`. `runtime.rng.replay_boundary` records which
  framework-owned stochastic surfaces are covered and explicitly excludes LLM
  provider outputs, plugin internal randomness, and validator subprocess
  randomness from the framework RNG restore contract. The paper-facing version
  of that boundary is preserved in `papers/runtime_rng_replay_boundary.json`.
  `runtime.lineage_replay_policy` separately declares deterministic loop-owned
  candidate, prompt, and LLM call id surfaces, excludes direct `Program()` and
  `PromptProgram()` UUID4 defaults, and states that provider outputs are not
  replayed by call ids or RNG restore. The paper-facing version of that
  boundary is preserved in `papers/lineage_replay_boundary.json`.
- `prompt_history.jsonl` can be replayed into a prompt archive, and the current
  full-runtime restore bundle can validate RNG, LLM scheduler, archive
  cell/elite, runtime-budget, synchronous controller-budget event, explicit RNG
  replay-boundary, and lineage replay-policy/provider-boundary surfaces, but
  whole-run resume still lacks controller pending-work, provider-output,
  plugin-state, ordered migration-event, and end-to-end lineage replay proof.
- Plugin names are paper-inspired approximations unless documented otherwise.
