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
bounded before prompt rendering. Context loading is flat and content-only today:
recursive context directories, include/exclude manifests, page-span citations,
and source hashes are not recorded yet. Fitness is the normalized primary metric:
`maximize` maps low-to-high bounds to `0..1`; `minimize` inverts that scale.

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
a canonical collision model: paths that normalize to the same relative name, or
that collide on a case-insensitive host filesystem, can overwrite each other.
Envelope parsing now rejects unmatched, orphaned, nested, empty-name, and
invalid-name `<<<FILE` / `<<<BLOCK` sections before applying partial edits. It
does not yet reject duplicate `<<<BLOCK name ... >>>BLOCK` sections in
multi-block full replacement; later duplicate sections currently win. It is
still a local envelope parser rather than a full mutation AST.
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
7. applies the configured mutation mode
8. evaluates the child
9. optionally applies LLM feedback graders with provenance and score
   composition
10. constructs a `Program` with metrics and structured evaluation data
11. runs plugin score hooks
12. logs the candidate and archives valid programs
13. rewards the selected backend with non-negative fitness improvement
14. migrates elites at the configured interval

`VALID_THRESHOLD` is currently `0.0`.

## Prompt sampling

[`libreevolve/core/prompt.py`](../libreevolve/core/prompt.py) provides
`PromptSampler`. It renders:

- task description
- explicit problem context files
- parent code, normalized fitness, metrics, and recent stage feedback
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

The feedback section is intentionally compact today: it renders recent stage
names, pass/fail states, scores, and errors. Although full stdout, stderr,
artifacts, and LLM grader records are persisted in run history, prompt rendering
does not yet include those richer outputs.

Failed/rejected mutations are logged to `failure_history.jsonl` with parent ids,
mutation text, diff errors, changed file paths, evaluator summaries, and
repetition counts. A bounded in-memory tail of those records is rendered into
later prompts as negative examples. This is still a local recent-memory
mechanism rather than a learned retrieval system over all historical failures.

`Config.prompt_variants` provides alternate templates. The loop stores those
templates as `PromptProgram` records in `PromptDatabase`, selects prompt
programs, records prompt reward/usage, and logs prompt lineage to
`prompt_history.jsonl`. Initial untried prompt programs are selected by
sorting UUID4 ids, so configured prompt-variant order is not currently
seed-stable. When `meta_prompt_evolution` is enabled, the loop can
periodically ask the active LLM backend to produce a revised full prompt
template with an instruction to preserve placeholders. Placeholder validation is
not enforced for either configured variants or mutated templates yet.
Prompt-program rewards are currently the final composed child score recorded
after evaluator, feedback, and plugin adjustments, and prompt selection uses a
fixed UCB-like formula rather than a documented AlphaEvolve-grade
prompt-fitness policy.

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

The syntax prefilter currently reports the first Python syntax error only.
Additional invalid `.py` files in the same workspace are not surfaced until
aggregate syntax diagnostics are implemented.

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
must be numeric, and explicit `seeds` must match `samples`. Remaining cascade
gaps are higher-level: `validate_path` provenance/preflight, metric-specific
threshold policies, stage-specific artifact schemas, and distributed evaluator
workers are not implemented.

The subprocess runs with the materialized candidate root as `cwd`, passes that
root as `workspace_path`, and adds both the candidate root and validator
directory to `sys.path`. Validators can import candidate-local modules, read
relative candidate files, and import sibling problem-local helper modules by
default. The problem directory is not used as `cwd`, and evaluator helper/data
provenance is not hashed into manifests yet.

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
for logging, prompt reward, and backend reward. The loop records
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

The DeepEvolve-inspired retrieval plugin also affects prompt context without
run-scoped provenance. It keeps only the latest synthesis string in memory and
does not persist provider/query/result metadata, citations, timestamps,
failure diagnostics, or hashes for the context injected into prompts.

The ImprovEvolve-inspired `modular` plugin is similar prompt-only context. It
always injects the same guidance block and does not record a structured
plugin-context event or selected generate/improve/perturb operation for the
candidate.

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

Parent selection and inspiration sampling are also intentionally thin today.
Exploit picks the global best, explore samples a random occupied cell, and
inspirations are random occupied cells across islands. Inspiration sampling
excludes the selected parent and deduplicates migrated copies by program id, but
sampling is not yet metric-aware and does not use novelty, feedback, lineage, or
recency signals.

LibreEvolve stores metric vectors, but its multi-objective policy is still a
first pass: archive comparison and backend rewards use normalized primary
fitness. Richer Pareto/frontier sampling remains open.

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

The backend interface returns only generated text. Provider usage, latency,
retry count, request/response ids, finish reasons, API mode, and raw response
metadata are not normalized or persisted, which limits cost accounting,
debugging, and scheduler analysis. Provider exceptions are not isolated by
role today: mutation, critique, feedback, and meta-prompt calls can abort the
run, and failed attempts are not retried, routed to fallback backends, or
counted in scheduler state.

## Logging and artifacts

[`libreevolve/core/database.py`](../libreevolve/core/database.py) writes:

- `manifest.json`: effective run configuration and runtime metadata
- `history.jsonl`: append-only candidate records
- `prompt_history.jsonl`: append-only prompt-program selection/scoring records
- `best.py`: primary-file compatibility view of the final best archived program
- `best_workspace/`: complete file set for the final best archived program

Each history record includes primary code, candidate files, primary file,
fitness, lineage, metadata, metrics, and the structured evaluation summary.
Program records include `metadata.prompt_program_id`, which links candidates to
prompt-program events in `prompt_history.jsonl`.

## Known gaps

- Candidate workspaces are local text file sets, not arbitrary-language build
  systems or external repositories.
- Materialized workspace execution uses the candidate root as subprocess `cwd`
  and import path, but it is still a local Python subprocess rather than a
  container or arbitrary build-system runner.
- Evaluator timeouts apply to the direct validator runner, but there is no
  process-group/job-object cleanup for subprocess descendants spawned by
  validator code yet.
- Validator subprocesses inherit the parent process environment, including
  `.env`-loaded provider credentials, because no validator environment
  allowlist or secret redaction policy exists yet.
- Candidate abstractions are code file sets with a primary file, not
  problem-defined non-code solution objects or paired solution/search artifacts.
- The loop is synchronous; async LLM/evaluator workers are not implemented.
- Runtime budget accounting is limited to `max_generations` and evaluator
  timeouts; there is no run-wide wall-clock, token, cost, evaluator-second, or
  structured stop-reason model.
- Archive cell/island state and migration events are not persisted separately
  from candidate history records.
- LLM critique and feedback are synchronous optional passes; there are no
  parallel reviewer/evaluator workers yet.
- Mutation responses are raw patch text; proposal ideas/rationales are not
  parsed, scored, or resurfaced as separate artifacts.
- Prompt evolution is implemented at the template boundary; richer prompt
  fitness plus configured/mutated template placeholder validation remain open.
- Prompt feedback rendering is a compact stage summary; richer stdout/stderr,
  artifact, sample-level diagnostic, and grader-feedback rendering remains open.
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
- `manifest.json` records configuration but not code version, problem hashes,
  plugin specs, artifact hashes, or resume/controller state.
- `Config.seed` controls local Python-random choices, but prompt variant order
  is mediated by UUID4 prompt-program ids, and candidate/prompt-program ids are
  UUID4 values, so persisted lineage is not stable across repeated
  deterministic local runs yet.
- Plugin names are paper-inspired approximations unless documented otherwise.
