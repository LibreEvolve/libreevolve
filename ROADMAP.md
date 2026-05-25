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
- structured evaluator results with metrics, stage outcomes, diagnostics, and
  elapsed time
- configurable local evaluator stages with distinct validator entrypoints,
  thresholds, samples, seeds, retries, and timeouts
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
  and `best.py` artifacts
- example problems including `hello_world`, `sorting`, `circle_packing`,
  `matrix_multiplication`, and `workspace_math`

The project is still a Python-only, synchronous, local-workspace prototype. It
is not yet an AlphaEvolve reproduction.

## Near Term

### 1. Finish candidate workspace fidelity

- Add language/runner declarations or keep the Python-only divergence explicit.
- Add problem-defined candidate abstraction hooks or keep code-file-set
  evolution documented as a deliberate divergence.
- Validate evolve-block marker pairing at load/apply time so malformed skeletons
  cannot silently fall back to whole-file evolution.
- Unify file-section path parsing with candidate path normalization so ordinary
  codebase filenames are routable in mutations.
- Define validator execution semantics for materialized workspaces, including
  candidate-root `cwd`, import path, package entrypoints, and relative files.
- Add richer workspace fixtures with nested packages and non-Python artifacts.
- Preserve full workspace artifacts in `best`/export flows, not only the primary
  file convenience output.
- Add migration/resume support for workspace candidates.

### 2. Strengthen multi-objective search

- Define a first-class multi-objective policy: Pareto archive, weighted
  composition, metric-specific elites, or a documented hybrid.
- Sample parents/inspirations by score, individual metric excellence, diversity,
  novelty, feedback, lineage, and recency.
- Expose metric-vector archive diagnostics in run artifacts and `show`.

### 3. Expand evaluation cascades

- Enforce the scalar metric contract from `metrics.yaml` for evaluator outputs.
- Add artifact collection and richer per-stage budget accounting.
- Add run-wide wall-clock, LLM-call, token, cost, evaluator-second, sample,
  retry, and stop-reason accounting.
- Add calibration/ablation reporting for LLM feedback graders.
- Normalize and bound LLM feedback metrics before using them in score
  composition.
- Isolate LLM feedback provider, parse, and config failures as structured
  evaluation metadata or stage outcomes.
- Add validator environment allowlisting, secret redaction, and network policy
  for subprocess evaluation.
- Preserve evaluator artifacts beyond stdout/stderr where useful.

### 4. Prompt and context work

- Add stricter validation that mutated prompt templates preserve required
  placeholders.
- Add AlphaEvolve-style stochastic formatting controls with weighted
  placeholder alternatives.
- Replace first-N-character context truncation with deterministic
  summarization/ranking for local PDFs and extracted text.
- Add context-source manifests with recursive selection, include/exclude rules,
  source hashes, extraction diagnostics, and page/span citations.
- Add global prompt budget/context-window accounting with deterministic
  section-level packing and prompt-size diagnostics.
- Render richer bounded evaluator outputs in prompts, including stdout/stderr,
  artifacts, sample-level diagnostics, validator feedback, and LLM grader
  summaries.
- Add a structured proposal format that can preserve an idea/rationale section
  separately from the patch blocks while keeping raw-diff compatibility.
- Persist and resurface failed/rejected proposal text and error causes, not only
  changed invalid child snippets.
- Improve meta-prompt scoring beyond direct child score and add ablation
  reporting for prompt-program lineages.

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
- Clarify and persist score-composition semantics when multiple plugins modify
  fitness.

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

- Validate config files, backend specs, stage configs, and feedback grader
  schemas before starting a run.
- Harden `history.jsonl` and `prompt_history.jsonl` as strict finite JSONL,
  rejecting or quarantining non-finite records before persistence.
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
