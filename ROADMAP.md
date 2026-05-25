# Roadmap

This roadmap reflects the current codebase as of 2026-05-24 after an
AlphaEvolve-alignment pass against `papers/2506.13131__AlphaEvolve.pdf`, local
docs, and the checked-in tests. It is a practical development plan, not a
promise.

## Current State

LibreEvolve has:

- Python seed programs with optional `# EVOLVE-BLOCK-START/END` regions
- SEARCH/REPLACE diff mutation and configurable full-block/full-code replacement
- structured evaluator results with metrics, stage outcomes, diagnostics, and
  elapsed time
- configurable local evaluator stages with thresholds/timeouts
- MAP-Elites plus 5-island migration
- metric direction/bounds normalization for primary fitness
- a prompt sampler that renders context files and evaluator feedback
- UCB-style backend routing plus experimental throughput/depth metadata
- structured `manifest.json`, rich `history.jsonl`, and `best.py` artifacts
- example problems including `hello_world`, `sorting`, `circle_packing`, and
  `matrix_multiplication`

The project is still a Python-only, synchronous, single-workspace prototype. It
is not yet an AlphaEvolve reproduction.

## Near Term

### 1. Finish candidate workspace fidelity

- Represent candidates as file sets, not only one Python string.
- Apply diffs and full replacements across marked files/components.
- Pass a candidate workspace to validators without breaking existing
  `evaluate(code: str)` problems.
- Add language/runner declarations or keep the Python-only divergence explicit.

### 2. Strengthen multi-objective search

- Define a first-class multi-objective policy: Pareto archive, weighted
  composition, metric-specific elites, or a documented hybrid.
- Sample parents/inspirations by score, individual metric excellence, diversity,
  novelty, feedback, lineage, and recency.
- Expose metric-vector archive diagnostics in run artifacts and `show`.

### 3. Expand evaluation cascades

- Let stages choose different validator entrypoints, seeds, sample sizes, and
  budgets.
- Add optional LLM-generated feedback graders with provenance and score
  composition rules.
- Preserve evaluator artifacts beyond stdout/stderr where useful.

### 4. Prompt and meta-prompt work

- Add problem-local prompt templates and validated template variables.
- Add deterministic literature/context ingestion for local PDFs or extracted
  text.
- Implement a prompt-program database only after prompt variants and feedback
  metrics are stable enough to score.

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
- Support optional critique/revision passes before expensive evaluation.

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

1. Add candidate file-set representation while preserving existing string APIs.
2. Add queryable database sampling by metric, novelty, lineage, and feedback.
3. Add stage-specific evaluator entrypoints and sample budgets.
4. Add one non-toy benchmark run fixture with expected artifacts.
