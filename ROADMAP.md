# Roadmap

This roadmap reflects the current codebase as of 2026-05-25 after an
AlphaEvolve-alignment pass against `papers/2506.13131__AlphaEvolve.pdf`, local
docs, and the checked-in tests. It is a practical development plan, not a
promise.

## Current State

LibreEvolve has:

- Python seed programs and seed workspaces with optional
  `# EVOLVE-BLOCK-START/END` regions
- SEARCH/REPLACE diff mutation, including canonical AlphaEvolve fences, and
  configurable full-block/full-code replacement
- workspace file topology mutations for create/edit/delete/move/rename and
  primary-file changes
- structured evaluator results with metrics, stage outcomes, diagnostics, and
  elapsed time
- configurable local evaluator stages with distinct validator entrypoints,
  thresholds, samples, seeds, retries, and timeouts
- strict scalar metric validation against `metrics.yaml`
- MAP-Elites plus 5-island migration
- metric direction/bounds normalization for primary fitness
- a prompt sampler that renders context files and compact stage feedback
- a local prompt-program database with prompt selection, scoring, lineage, and
  optional interval-based LLM template mutation
- optional synchronous LLM critique/revision before mutation application
- optional LLM feedback graders with provenance, discard rules, and weighted
  score composition
- UCB-style backend routing plus experimental throughput/depth metadata
- structured `manifest.json`, rich `history.jsonl` with candidate file sets,
  per-candidate archive admission events, `best.py`, and `best_workspace/`
  artifacts
- example problems including `hello_world`, `sorting`, `circle_packing`,
  `matrix_multiplication`, and `workspace_math`

The project is still a Python-only, synchronous, local-workspace prototype. It
is not yet an AlphaEvolve reproduction.

## Near Term

### 1. Finish candidate workspace fidelity

- Add language/runner declarations or keep the Python-only divergence explicit.
- Add problem-defined candidate abstraction hooks or keep code-file-set
  evolution documented as a deliberate divergence.
- Prevalidate seed evolve-block markers during problem load, not only during
  mutation application.
- Add richer workspace fixtures with nested packages, package-style validator
  entrypoints, relative evaluator data, and non-Python/static artifacts.
- Define binary/static artifact handling for candidate workspaces.
- Add migration/resume support for workspace candidates.

### 2. Strengthen multi-objective search

- Define a first-class multi-objective policy: Pareto archive, weighted
  composition, metric-specific elites, or a documented hybrid.
- Sample parents/inspirations by score, individual metric excellence, diversity,
  novelty, feedback, lineage, and recency, while excluding the selected parent
  and deduplicating migrated copies from inspiration sets.
- Make MAP-Elites descriptors workspace-aware instead of using only the
  primary-file compatibility view for complexity/diversity.
- Stabilize descriptor normalization with fixed bounds, evaluator-provided
  behavior descriptors, or explicit rebin/snapshot semantics.
- Expose metric-vector archive diagnostics in run artifacts and `show`.

### 3. Expand evaluation cascades

- Add artifact collection and richer per-stage budget accounting.
- Add run-wide wall-clock, LLM-call, token, cost, evaluator-second, sample,
  retry, and stop-reason accounting.
- Add calibration/ablation reporting for LLM feedback graders.
- Normalize and bound LLM feedback metrics before using them in score
  composition.
- Add configurable retry/penalty policies for LLM feedback provider or parse
  failures beyond the current ignore-and-record behavior.
- Preserve every evaluator retry attempt in run history, not only the
  successful or final attempt.
- Add validator environment allowlisting, secret redaction, and network policy
  for subprocess evaluation.
- Extend problem-local evaluator import semantics from sibling helper modules
  to package-style validators and relative evaluator data files.
- Preserve evaluator artifacts beyond stdout/stderr where useful.

### 4. Prompt and context work

- Add stricter validation that configured and mutated prompt templates preserve
  required placeholders and contain no malformed format fields.
- Add AlphaEvolve-style stochastic formatting controls with weighted
  placeholder alternatives.
- Replace first-N-character context truncation with deterministic
  summarization/ranking for local PDFs and extracted text.
- Add context-source manifests with recursive selection, include/exclude rules,
  source hashes, extraction diagnostics, and page/span citations.
- Add global prompt budget/context-window accounting with deterministic
  section-level packing and prompt-size diagnostics.
- Add prompt/history redaction and data-retention controls for mutation,
  critique, feedback, plugin, and explicit-context prompt sections.
- Render richer bounded evaluator outputs in prompts, including stdout/stderr,
  artifacts, sample-level diagnostics, validator feedback, and LLM grader
  summaries.
- Add a structured proposal format that can preserve an idea/rationale section
  separately from the patch blocks while keeping raw-diff compatibility.
- Improve meta-prompt scoring beyond direct child score and add ablation
  reporting for prompt-program lineages, including documented prompt reward
  normalization and selection policy.

### 5. Documentation truthfulness

- Keep README, docs, paper index, and `docs/todo/*` aligned with implemented
  behavior.
- Continue labeling CausalEvolve, DeepEvolve, ImprovEvolve, ThetaEvolve,
  GigaEvo, CodeEvolve, and MadEvolve features as inspired unless paper behavior
  is actually implemented.

## Mid Term

### 6. Async and resumable runtime

- Add a controller with bounded queues for LLM proposals and evaluator workers.
- Persist enough archive, bandit, prompt, and pending-evaluation state to resume
  long runs.
- Persist MAP-Elites cell/island state, descriptor values, elite snapshots, and
  migration events, not only candidate history records.
- Record Git/code state, problem hashes, plugin specs, and artifact hashes in
  the run manifest.
- Define seeded replay semantics for run ids, candidate ids, prompt-program ids,
  RNG state, and provider nondeterminism boundaries.
- Add deterministic accounting for concurrent evaluations, retries, consumed
  budgets, and budget-exhaustion stop reasons.

### 7. Backend scheduling and critique

- Add a backend registry/plugin interface for custom LLM providers, not only
  the hard-coded OpenAI/Anthropic/Ollama constructors.
- Normalize/document UCB rewards against bounded assumptions or rename the
  current policy as a heuristic.
- Separate backend accounting for mutation generation, critique, feedback
  grading, and meta-prompt mutation calls.
- Persist normalized LLM call telemetry, including provider usage, latency,
  retries, request ids, finish reasons, and API mode.
- Add deterministic provider-failure handling for mutation, critique,
  feedback, and meta-prompt calls, including retries, fallback routing,
  failed-attempt accounting, and structured error logs.
- Add explicit breadth/depth/cost/latency scheduling tests.
- Extend critique/revision beyond a synchronous self-review call toward
  configurable reviewer pools.

### 8. Plugin extensibility

- Move plugin registration out of the hard-coded CLI registry.
- Allow plugin configuration through `config.yaml`.
- Record plugin constructor parameters, paper-inspiration scope, and emitted
  artifact paths in run manifests.
- Extend plugin provenance beyond the current score-composition chain to cover
  prompt-context attribution, configuration, versions, and emitted artifacts.

## Longer Term

### 9. Representative benchmarks

- Add stronger AlphaEvolve-style fixtures beyond toy examples:
  matrix-multiplication variants, kissing/circle packing extensions,
  constructive math, and one safe scheduling/kernel microbenchmark.
- Separate smoke examples from benchmark fixtures, with anti-gaming validators,
  expected artifact schemas, SOTA/target baselines, and repeated-seed runs.
- For each local domain paper, either add a benchmark, link it to an existing
  benchmark, or keep it marked background-only in `papers/README.md`.
- Add repeatable benchmark scripts for backend, seed, prompt, and archive
  ablations.
- Report benchmark progress at comparable compute-budget fractions, not only
  final generation counts.

### 10. Operational maturity

- Extend current config validation to plugin-specific schemas and
  provider/model API compatibility where feasible.
- Extend strict finite JSONL coverage and diagnostics beyond current
  candidate, prompt, manifest, and GRPO-export writers as new run artifacts are
  added.
- Improve `show` for run summaries, lineage, metrics, and failure statistics.
- Add packaging/release hygiene beyond editable installs.
- Broaden CI/interpreter coverage.

## Non-Goals For Now

- Requiring a service database for normal local use.
- Claiming arbitrary-language/codebase support before runners and validators
  exist.
- Advertising paper-inspired plugins as faithful implementations.

## Good First Follow-Ups

1. Add queryable database sampling by metric, novelty, lineage, and feedback.
2. Add one non-toy benchmark run fixture with expected artifacts.
3. Add workspace export/resume coverage beyond primary `best.py`.
4. Add LLM feedback calibration reports and grader ablation fixtures.
