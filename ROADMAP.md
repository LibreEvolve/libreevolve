# Roadmap

This roadmap reflects the current codebase as of 2026-05-24 after an
AlphaEvolve-alignment pass against `papers/2506.13131__AlphaEvolve.pdf`, local
docs, and the checked-in tests. It is a practical development plan, not a
promise.

## Current State

LibreEvolve has:

- Python seed programs and seed workspaces with optional
  `# EVOLVE-BLOCK-START/END` regions
- SEARCH/REPLACE diff mutation and configurable full-block/full-code replacement
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
- example problems including `hello_world`, `sorting`, `circle_packing`, and
  `matrix_multiplication`

The project is still a Python-only, synchronous, local-workspace prototype. It
is not yet an AlphaEvolve reproduction.

## Near Term

### 1. Finish candidate workspace fidelity

- Add language/runner declarations or keep the Python-only divergence explicit.
- Add problem-defined candidate abstraction hooks or keep code-file-set
  evolution documented as a deliberate divergence.
- Add richer workspace fixtures with nested packages and non-Python artifacts.
- Add compatibility with AlphaEvolve's canonical `<<<<<<< SEARCH` /
  `>>>>>>> REPLACE` diff block spelling while preserving the compact local
  format.
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
- Add calibration/ablation reporting for LLM feedback graders.
- Normalize and bound LLM feedback metrics before using them in score
  composition.
- Preserve evaluator artifacts beyond stdout/stderr where useful.

### 4. Prompt and context work

- Add stricter validation that mutated prompt templates preserve required
  placeholders.
- Add AlphaEvolve-style stochastic formatting controls with weighted
  placeholder alternatives.
- Replace first-N-character context truncation with deterministic
  summarization/ranking for local PDFs and extracted text.
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
- Record Git/code state, problem hashes, plugin specs, and artifact hashes in
  the run manifest.
- Add deterministic accounting for concurrent evaluations and retries.

### 7. Backend scheduling and critique

- Add a backend registry/plugin interface for custom LLM providers, not only
  the hard-coded OpenAI/Anthropic/Ollama constructors.
- Normalize/document UCB rewards against bounded assumptions or rename the
  current policy as a heuristic.
- Separate backend accounting for mutation generation, critique, feedback
  grading, and meta-prompt mutation calls.
- Add explicit breadth/depth/cost/latency scheduling tests.
- Extend critique/revision beyond a synchronous self-review call toward
  configurable reviewer pools.

### 8. Plugin extensibility

- Move plugin registration out of the hard-coded CLI registry.
- Allow plugin configuration through `config.yaml`.
- Clarify score-composition semantics when multiple plugins modify fitness.

## Longer Term

### 9. Representative benchmarks

- Add stronger AlphaEvolve-style fixtures beyond toy examples:
  matrix-multiplication variants, kissing/circle packing extensions,
  constructive math, and one safe scheduling/kernel microbenchmark.
- For each local domain paper, either add a benchmark, link it to an existing
  benchmark, or keep it marked background-only in `papers/README.md`.
- Add repeatable benchmark scripts for backend, seed, prompt, and archive
  ablations.

### 10. Operational maturity

- Validate config files, backend specs, stage configs, and feedback grader
  schemas before starting a run.
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
