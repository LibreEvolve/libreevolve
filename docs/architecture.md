# Architecture

LibreEvolve is a Python research framework for LLM-guided program mutation. It
is AlphaEvolve-inspired, but intentionally smaller: the current runtime is
synchronous, Python-only, and filesystem-backed.

## Top-level flow

The CLI entrypoint is [`libreevolve/cli.py`](../libreevolve/cli.py). The `run`
command:

- loads `.env` with `override=True`
- loads a problem directory with `load_problem()`
- merges problem-local `config.yaml` into the default `Config`
- instantiates built-in plugins named on the CLI
- calls `evolve(problem, config, plugins)`
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

The loader keeps all declared metrics, picks a primary metric, exposes metric
direction/bounds helpers, and loads deterministic prompt context. Text/code
context is read directly; PDFs are extracted with `pypdf`; long context is
bounded before prompt rendering. Context loading walks `context/` recursively,
honors optional `context.yaml` include/exclude patterns and per-source character
budgets, renders prompt citation headers, and records hashes, spans, extraction
status, and PDF page ranges in the run manifest. Fitness is the normalized
primary metric: `maximize` maps low-to-high bounds to `0..1`; `minimize` inverts
that scale.

## Candidate representation

Candidates use `CandidateWorkspace`: a text file set with a `primary_file`.
`Program.code` remains as a compatibility view of the primary file, so existing
single-file seeds, validators, prompts, and `best.py` workflows still work.
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
back to whole-file mutation. Problem loading still accepts malformed seed files
until mutation/evaluation time; earlier load-time diagnostics remain a useful
future improvement.

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
`<<<FILE path ... >>>FILE` envelope. Candidate paths are normalized and cannot
escape the candidate workspace. File-section headers are parsed through the
same relative-path normalization used by `CandidateWorkspace`, so nested paths,
hyphens, spaces, Unicode filename characters, and Windows-style backslashes are
accepted when the resulting normalized path is safe. This does not yet provide
a canonical collision model: workspace construction rejects raw paths that
normalize to the same relative name, and materialization preflights
case-folded host-path collisions before writing files. Mutation-envelope
handling rejects duplicate edit sections for the same `<<<FILE path ...>>>`
target. Unicode-normalization collisions and more complex topology-operation
collision policy remain incomplete.
Envelope parsing now rejects unmatched, orphaned, nested, duplicate-name,
empty-name, and invalid-name `<<<FILE` / `<<<BLOCK` sections before applying
partial edits. It is still a local envelope parser rather than a full mutation
AST.
Command file sections can delete files, move/rename files, and change the
workspace primary file:

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
For each generation it:

1. runs plugin start hooks
2. samples a parent from the island model
3. samples diverse inspirations
4. builds prompt context through `PromptSampler`
5. calls the LLM ensemble
6. optionally runs a critique/revision LLM pass on the proposed mutation
7. previews the critique revision and falls back to the original mutation if
   the revision is malformed but the original applies cleanly
8. applies the configured mutation mode
9. evaluates the child
10. optionally applies LLM feedback graders with provenance and score
   composition
11. constructs a `Program` with metrics and structured evaluation data
12. runs plugin score hooks
13. logs the candidate and archives valid programs
14. rewards the selected backend with non-negative fitness improvement
15. migrates elites at the configured interval

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

Prompt assembly does not yet apply a global token or character budget across
sections. Large parent workspaces, many inspirations, plugin context, or
already-truncated context files can still produce oversized prompts, and the
run does not record prompt size or context-window fit diagnostics.

Mutation and critique prompts are rendered and stored as raw text today.
General prompt redaction, per-role prompt logging modes, and data-retention
controls are not implemented; only the LLM feedback workspace-rendering path
applies basic secret redaction.

The feedback section renders a bounded, redacted summary of recent stage
status, execution stdout/stderr, retry/sample diagnostics, evaluator artifact
paths and hashes, and LLM grader feedback. It is intentionally a summary rather
than full log or artifact-content retrieval.

Failed/rejected mutations are logged to `failure_history.jsonl` with parent ids,
mutation text, diff errors, changed file paths, evaluator summaries, and
repetition counts. A bounded in-memory tail of those records is rendered into
later prompts as negative examples. This is still a local recent-memory
mechanism rather than a learned retrieval system over all historical failures.

When `capture_proposal_metadata` is enabled, mutation prompts ask the LLM to
place short `IDEA`, `RATIONALE`, and `HYPOTHESIS` sections before the patch.
The mutation parser extracts those bounded fields into candidate metadata while
leaving SEARCH/REPLACE, file-section, block-section, and full-code patch
application compatible with diff-only responses. Later prompts render bounded,
redacted proposal summaries for selected parent and inspiration programs.

`Config.prompt_variants` provides alternate templates. The loop stores those
templates as `PromptProgram` records in `PromptDatabase`, selects prompt
programs, records prompt reward/usage, and logs prompt lineage to
`prompt_history.jsonl`. Initial untried prompt programs are selected by
sorting UUID4 ids, so configured prompt-variant order is not currently
seed-stable. When `meta_prompt_evolution` is enabled, the loop can
periodically ask the active LLM backend to produce a revised full prompt
template with an instruction to preserve placeholders. Configured and mutated
prompt templates are validated against the `PromptSampler` placeholder schema
before use. Prompt rewards are normalized to `0..1` using
`prompt_reward_bounds`; `prompt_reward_mode` chooses absolute final composed
score or child-minus-parent improvement as the raw reward, and
`prompt_explore_coeff` controls the prompt selector's exploration term.
The policy is still scalar; richer multi-metric prompt-fitness models and
experiment ablation reporting remain future work.

## Evaluation

[`libreevolve/core/evaluator.py`](../libreevolve/core/evaluator.py) returns an
`EvaluationResult` instead of a bare float. It includes:

- normalized primary `fitness`
- raw validator `metrics`
- `is_valid`
- per-stage outcomes
- stdout, stderr, error, elapsed time, and metadata

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
seed lists, and retries. Validators may keep the old `evaluate(code)` signature
or opt into `evaluate(code, workspace_path)` or
`evaluate(code, workspace_path, stage)`. Multi-sample stages aggregate numeric
metrics and stop the cascade when validity or threshold checks fail. This is a
local cascade model, not AlphaEvolve's full parallel evaluator-worker
architecture.

Stage numeric fields are validated at startup: `samples` must be positive,
`timeout_sec` must be positive, `retries` must be non-negative, `min_score`
must be numeric, and explicit `seeds` must match `samples`. Stage
`validate_path` entries are resolved to problem-local Python files before
execution; missing files, directories, non-Python files, outside-root paths,
and symlinks that resolve outside the problem directory are rejected. Remaining
cascade gaps are higher-level: transitive helper/data provenance,
metric-specific threshold policies, richer artifact schemas, and distributed
evaluator workers are not implemented.

The subprocess runs with the materialized candidate root as `cwd`, passes that
root as `workspace_path`, and adds both the candidate root and validator
directory to `sys.path`. Validators can import candidate-local modules, read
relative candidate files, and import sibling problem-local helper modules by
default. The problem directory is not used as `cwd`, and evaluator helper/data
provenance is not hashed into manifests yet. The run manifest does record the
direct evaluator entrypoint files with resolved paths, problem-relative paths,
SHA-256 hashes, byte counts, and stage usage metadata.

After local evaluation, `Config.llm_feedback` can run optional LLM graders for
properties that are awkward to encode in `validate.py`, such as clarity or
style. Graders run only for locally valid candidates by default unless a grader
sets `include_invalid: true`. Graders return JSON-like feedback with a numeric
score and optional discard flag. Scores are added as metrics, raw responses and
backend indexes are recorded under `evaluation.metadata.llm_feedback`, and
weighted feedback adjusts `Program.fitness` while preserving the raw validator
metric. Feedback score calibration against `metrics.yaml` direction/bounds is
not implemented yet. Feedback grader prompts render bounded full-workspace file
sections with path headers, primary-file marking, basic redaction, and compact
evaluator diagnostics.
Feedback grader call and parse failures are recorded in
`evaluation.metadata.llm_feedback` as `llm_feedback_failed` records and are
ignored for score/validity composition. There is not yet a configurable retry,
penalty, or discard policy for failed feedback graders.

After that, plugin `on_evaluated()` hooks may modify the effective fitness used
for logging, prompt reward, and backend reward. Prompt reward uses that final
composed child score, optionally as an improvement over the parent score. The
loop records
`metadata.score_composition` with evaluator fitness, optional feedback-adjusted
fitness, per-plugin before/after scores, metric additions/changes, invalid
plugin-score rejections, and final composed fitness. Archive admission uses the
composed top-level fitness threshold but remains gated by
`evaluation.is_valid`, so a plugin cannot accidentally archive an
evaluator-invalid candidate by raising its score.

Plugins that inspect mutation text should share the core mutation parser.
`CausalPlugin` now routes factor detection through `parse_diff_blocks()`, so
compact local SEARCH/REPLACE fences and canonical AlphaEvolve fences are both
visible to its token-pattern factor analysis. This is still a heuristic,
paper-limited approximation rather than CausalEvolve's causal scratchpad.

The ThetaEvolve-inspired `ttt_rl` plugin emits a side dataset rather than a
run-scoped artifact. It clips rewards with `max(0.0, score)` and appends to
`runs/grpo_data.jsonl` by default; that file is not hashed or referenced from
the run manifest yet.

The DeepEvolve-inspired retrieval plugin keeps only the latest synthesis string
in memory. Candidate metadata records the rendered plugin-context text, hash,
parent id, and inspiration ids plus bounded retrieval events with provider,
query, generation, best id/fitness, timestamp, status, result length, synthesis
hash, arXiv source IDs/URLs, source timestamps/authors, summary hashes, and
error text plus structured error types when applicable. It still does not
persist full result payloads, ranking provenance, or a systematic
debug/refinement loop. Completed manifests include bounded `runtime.retrieval`
summaries.

The ImprovEvolve-inspired `modular` plugin is similar prompt-only context. It
always injects the same guidance block. Candidate metadata can attribute that
rendered block to the plugin, but no selected generate/improve/perturb
operation is executed or logged for the candidate.

## Population model

Population state is split across:

- `Program`: primary code, candidate files, fitness, lineage, metadata,
  metrics, and evaluation summary
- `MAPElites`: one quality-diversity archive
- `IslandModel`: multiple archives plus ring migration

`MAPElites` maps programs into a 3D grid using normalized performance, code
length, and TF-IDF char-4gram diversity. Performance bounds now use the
problem's normalized `0..1` fitness scale. For workspace candidates,
complexity and TF-IDF diversity still use `Program.code`, the primary-file
compatibility view, rather than a canonical full-workspace representation.

Full archive snapshots, elite snapshots, migration events, and normalization
state are still in-memory runtime state today. `history.jsonl` logs candidates,
but it is not a serialized archive checkpoint or MAP-Elites event stream.
Candidate records do include `metadata.archive_admission` events that state
whether a candidate was rejected by threshold, assigned to an island and cell,
replaced a cell occupant, entered only the capped elite list, or was ignored by
cell competition.

Descriptor normalization is also stateful. Complexity is normalized against
the largest primary-file length seen so far, and TF-IDF diversity is computed
against the current capped elite list. Existing cells are not re-binned when
those reference sets change, so current MAP-Elites coordinates are local
heuristics rather than stable behavior-descriptor coordinates.

Parent selection has configurable strategies. The default `mixed` mode preserves
the seeded exploit/explore ratio, where exploit uses the archive selection key
and explore samples a random occupied cell. Explicit parent strategies can also
select by individual normalized-metric leaders, novelty, or recency.

Inspiration sampling is also configurable. `mixed` combines normalized-metric
leaders, novelty, selection score, and random fill; `selection`, `metric`,
`novelty`, `recency`, and `random` are available as explicit policies.
Inspiration sampling excludes the selected parent and deduplicates migrated
copies by program id. This is still an in-memory archive policy rather than a
queryable evolutionary database, and it does not yet use feedback text, lineage
diversity, or persisted novelty indexes.

LibreEvolve stores metric vectors and now annotates each program with
`metadata.normalized_metrics` for declared numeric metrics plus an equal-weight
`metadata.selection_score`. MAP-Elites performance placement, cell replacement,
elite ranking, and exploit/best sampling use that selection score with final
composed fitness as a tie-break. Admission thresholds and backend rewards still
use final scalar fitness, and richer Pareto/frontier sampling, configurable
weights, and metric-specific elite archives remain open.

## Backend selection

[`libreevolve/llm/ensemble.py`](../libreevolve/llm/ensemble.py) wraps one or
more backends. The default `ensemble_strategy` is `ucb1`, implemented as a
heuristic adaptation of UCB1 over observed fitness improvements.

An experimental `throughput_depth` strategy layers optional backend metadata
(`cost`, `latency`, `depth`, `role`) over UCB scores so configs can distinguish
cheap breadth models from deeper models. This is a scheduling concept, not a
verified reproduction of AlphaEvolve's Gemini Flash/Pro policy.
The current scoring formula uses only numeric `cost`, `latency`, and `depth`;
`role` is preserved as descriptive metadata and does not drive routing yet.

All current LLM calls share the same ensemble state. Mutation calls are rewarded
after evaluation; critique, feedback, and meta-prompt calls are counted as
backend pulls but do not have role-specific reward semantics yet.

For OpenAI, the adapter uses Chat Completions unless `reasoning_effort` is set,
in which case it uses the Responses API. There is no automatic
reasoning-model detection or API-mode validation yet.

The backend adapters still return generated text, but `LLMEnsemble` wraps calls
with normalized telemetry containing role, backend, backend metadata, strategy,
API mode, prompt/output sizes and hashes, latency, success/error status, and
backend counts before/after the call. Successful mutation/critique calls are
attached to candidate metadata, feedback calls are attached to feedback records,
and meta-prompt calls are attached to prompt-history metadata. Provider usage
tokens, adapter-internal retry counts, request/response ids, finish reasons,
and raw provider diagnostics are not available yet. The ensemble supports
configured same-backend retries and optional fallback to another backend; each
attempt is recorded with retry/fallback indexes and whether it will retry or
fallback. If all provider attempts fail, the final exception still propagates to
the active role, so mutation, critique, feedback, and meta-prompt calls can
still abort the run rather than becoming role-specific quarantined records.

## Logging and artifacts

[`libreevolve/core/database.py`](../libreevolve/core/database.py) writes:

- `manifest.json`: effective run configuration, runtime metadata, and
  provenance hashes
- `history.jsonl`: append-only candidate records
- `prompt_history.jsonl`: append-only prompt-program selection/scoring records
- `best.py`: primary-file compatibility view of the final best archived program
- `best_workspace/`: complete file set for the final best archived program

Each history record includes primary code, candidate files, primary file,
fitness, lineage, metadata, metrics, and the structured evaluation summary.
Program records include `metadata.prompt_program_id`, which links candidates to
prompt-program events in `prompt_history.jsonl`.

Run-directory reuse is guarded before these writers append or replace files.
The default policy fails startup if the target directory already contains known
run artifacts; explicit overwrite removes only known run artifacts before the
new run. The manifest records the generated `run_id` and effective collision
policy, but this is provenance metadata rather than resumable state.
It also records Git state when available, `libreevolve/` source-tree hashes,
problem-tree hashes, direct evaluator entrypoint hashes, and plugin module file
hashes. Plugin constructor parameters/spec schemas and aggregate hashes for
artifacts emitted after startup remain open.

The synchronous loop uses a local `RunBudget` tracker for `max_generations`,
optional total evaluation count, optional cumulative evaluator seconds, and
optional wall-clock seconds. Budget consumption is written into each candidate
record under `metadata.budget`, and the completed run writes a `runtime`
summary with stop reason back into `manifest.json`. These are local accounting
counters, not async queue checkpoints or provider token/cost accounting.

## Known gaps

- Candidate workspaces are local text file sets, not arbitrary-language build
  systems or external repositories.
- Materialized workspace execution uses the candidate root as subprocess `cwd`
  and import path, but it is still a local Python subprocess rather than a
  container or arbitrary build-system runner.
- Evaluator timeouts attempt process-tree cleanup and record cleanup metadata,
  but this remains local subprocess management rather than a container,
  network sandbox, or general resource-limit system.
- Validator subprocesses use a minimal environment plus
  `validator_env_allowlist`; provider keys loaded through `.env` are hidden by
  default and persisted evaluator stdout/stderr is secret-redacted. This is not
  a network sandbox.
- Candidate abstractions are code file sets with a primary file, not
  problem-defined non-code solution objects or paired solution/search artifacts.
- The loop is synchronous; async LLM/evaluator workers are not implemented.
- Runtime budget accounting covers local generation count, total evaluator
  calls, cumulative evaluator seconds, wall-clock seconds, and structured stop
  reasons. Token, provider-cost, LLM retry, stage-sample, accelerator, and
  async queue budgets are not implemented.
- Archive cell/island state and migration events are not persisted separately
  from candidate history records.
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
  metadata, sample/retry diagnostics, and grader summaries, but does not yet
  retrieve artifact contents or participate in a global prompt-size budget.
- LLM feedback graders receive bounded full-workspace file sections, basic
  secret redaction, and compact evaluator diagnostics.
- Mutation/critique prompts and persisted prompt history do not yet share that
  redaction path or expose data-retention controls.
- Evaluator output is parsed as JSON, validated against declared scalar
  metrics, and normalized around the primary metric.
- Config validation now rejects unknown problem config keys, invalid
  mutation/ensemble enums, malformed backend specs, bad evaluator-stage
  numeric fields, invalid top-level population/runtime ranges, and malformed
  LLM feedback grader specs when `config.yaml` parses to a mapping. Malformed
  YAML and scalar/list top-level config files can still fail before normalized
  startup diagnostics. Plugin-specific schemas remain only partially validated.
- OpenAI API mode is selected by the presence of `reasoning_effort`, not by
  validated model capabilities.
- `manifest.json` records configuration plus Git/source/problem/plugin-module
  provenance, but not validated plugin specs, constructor parameters,
  aggregate emitted-artifact hashes, or resume/controller state.
- `Config.seed` controls local Python-random choices, but prompt variant order
  is mediated by UUID4 prompt-program ids, and candidate/prompt-program ids are
  UUID4 values, so persisted lineage is not stable across repeated
  deterministic local runs yet.
- Plugin names are paper-inspired approximations unless documented otherwise.
