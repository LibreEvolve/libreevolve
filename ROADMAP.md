# Roadmap

This roadmap reflects the current codebase as of 2026-03-26. It is a practical
development plan, not a promise. The goal is to move LibreEvolve from a solid
research prototype toward a more reliable and extensible experimentation
platform.

## Current State

LibreEvolve already has:

- a working core evolution loop
- SEARCH/REPLACE diff mutation
- a cascade evaluator
- MAP-Elites plus 5-island migration
- UCB1 routing across multiple LLM backends
- a small built-in plugin system
- example problems and a solid unit test baseline

The next phase is mostly about tightening contracts, improving experiment
control, and making results easier to reproduce and extend.

## Near Term

### 1. Correctness and architecture alignment

- Wire `Problem.primary_bounds` into MAP-Elites performance normalization so
  non-`[0, 1]` problems are archived correctly.
- Audit README and example language for places where intended design still
  differs from actual code behavior.
- Add tests around problem-bound handling, archive binning, and score
  normalization.

### 2. Better experiment configuration

- Expose more `Config` fields through the CLI, especially migration and archive
  settings.
- Validate backend-specific config more explicitly, especially
  `reasoning_effort`.
- Improve config error messages for malformed backend specs and invalid
  problem-local `config.yaml`.

### 3. Run ergonomics

- Add richer `show` output for run summaries, lineage, and failure statistics.
- Add optional run metadata files for reproducibility, such as effective config
  and backend roster.
- Make output layout more consistent for plugin-generated artifacts.

### 4. Documentation and contributor usability

- Keep docs aligned with implementation as the code evolves.
- Add a contributor guide for adding new backends and plugins with minimal
  boilerplate.
- Add a short architecture diagram and example-driven docs for custom problems.

## Mid Term

### 5. Better extensibility

- Move plugin registration out of the hard-coded CLI registry and toward a more
  maintainable discovery mechanism.
- Allow plugin configuration through `config.yaml` instead of requiring code
  edits for constructor arguments.
- Clarify plugin ordering and score-composition semantics when multiple plugins
  modify fitness.

### 6. Stronger evaluation and safety controls

- Add more evaluator diagnostics so users can distinguish syntax failures, time
  limits, diff failures, and domain-invalid outputs from run artifacts.
- Consider tighter subprocess isolation options for validators.
- Add support for evaluator-side metadata beyond the primary metric and
  `is_valid`.

### 7. Experiment management

- Add resumable runs or explicit restart semantics.
- Add repeatable benchmark scripts for the example problems.
- Add comparison tooling for runs across different backends, seeds, or plugin
  combinations.

### 8. Population and search improvements

- Revisit parent selection and inspiration sampling policies with more explicit
  scheduling controls.
- Explore better diversity measures and archive diagnostics for code search.
- Add tests and benchmark coverage for migration behavior under longer runs.

## Longer Term

### 9. Research workflows

- Expand built-in example problems beyond toy tasks to more representative
  algorithmic benchmarks.
- Add first-class support for research-style ablations, including backend-only,
  plugin-only, and archive-parameter sweeps.
- Strengthen training-data export and downstream RL fine-tuning workflows around
  the `ttt_rl` plugin.

### 10. Operational maturity

- Add structured logging and machine-readable run summaries.
- Add packaging and release hygiene beyond editable-install workflows.
- Improve CI coverage to include a broader interpreter matrix and stronger
  integration coverage.

## Non-Goals For Now

- Turning LibreEvolve into a heavy framework with mandatory services or a
  database backend.
- Replacing the simple filesystem problem format with a more complex project
  model.
- Expanding features faster than the docs and tests can keep up.

## Good First Follow-Ups

If development resumes immediately, these are the highest-value concrete next
steps:

1. Fix archive performance normalization to use `Problem.primary_bounds`.
2. Add tests that fail without that fix.
3. Improve `show` so a user can inspect run quality without opening JSONL by
   hand.
4. Add configurable plugin loading and plugin options through config.
