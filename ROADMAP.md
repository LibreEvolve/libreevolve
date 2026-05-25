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
- a prompt sampler that renders context files and evaluator feedback
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

- Add artifact collection and richer per-stage budget accounting.
- Add calibration/ablation reporting for LLM feedback graders.
- Preserve evaluator artifacts beyond stdout/stderr where useful.

### 4. Prompt and context work

- Add stricter validation that mutated prompt templates preserve required
  placeholders.
- Add deterministic literature/context ingestion for local PDFs or extracted
  text.
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
- Add deterministic accounting for concurrent evaluations and retries.

### 7. Backend scheduling and critique

- Normalize/document UCB rewards against bounded assumptions or rename the
  current policy as a heuristic.
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
