# Roadmap

This roadmap reflects the current codebase as of 2026-05-26 after an
AlphaEvolve-alignment pass against `papers/2506.13131__AlphaEvolve.pdf`, local
docs, the paper index, and the checked-in tests. It is a practical development
plan, not a promise.

## Current State

LibreEvolve has:

- Python seed programs and seed workspaces with load-time-validated optional
  `# EVOLVE-BLOCK-START/END` regions
- SEARCH/REPLACE diff mutation, including canonical AlphaEvolve fences, and
  configurable full-block/full-code replacement with unknown named block
  targets rejected before partial replacement
- workspace file topology mutations for create/edit/delete/move/rename and
  primary-file changes
- candidate path hardening for unsafe, ambiguous, overlong, Unicode-control,
  reserved, and dot-prefixed generated paths
- structured evaluator results with metrics, stage outcomes, diagnostics, and
  elapsed time
- configurable local evaluator stages with distinct validator entrypoints,
  thresholds, samples, validator-managed seed values, retries, timeouts, and
  per-attempt history
- strict scalar evaluator-output validation against `metrics.yaml`, including
  finite, strictly increasing non-boolean metric bounds
- opt-in evaluator artifact copy-out from temporary candidate workspaces with
  hashes, limits, and text redaction metadata
- validator subprocess environment allowlisting, persisted stdout/stderr
  redaction, and best-effort timeout process-tree cleanup
- MAP-Elites plus 5-island migration
- metric direction/bounds normalization for declared evaluator metrics and
  feedback-sourced objective metrics, averaged into archive selection score
- a prompt sampler that renders context files, compact stage feedback,
  proposal metadata, and prompt-size/section-budget diagnostics
- recursive problem-local context ingestion for `.txt`, `.md`, `.py`, and
  `.pdf` files with context-manifest include/exclude rules, source hashes,
  extraction spans, and bounded prompt rendering
- a local prompt-program database with prompt selection, scoring, lineage, and
  optional interval-based LLM template mutation; configured and evolved
  templates are validated for known placeholders, compatible format specs, and
  parent-placeholder retention during mutation; configured prompt templates can
  also use weighted `[[prompt:name]]` stochastic formatting markers backed by
  `prompt_format_options`
- optional synchronous LLM critique/revision before mutation application
- optional LLM feedback graders with provenance, discard rules, and weighted
  score composition using normalized bounded reviewer scores
- UCB-style backend routing plus experimental throughput/depth metadata,
  ensemble-level call telemetry with redacted/bounded provider errors, and
  configurable retry/fallback attempts plus a local accepted-response
  character cap
- structured `manifest.json`, rich `history.jsonl` with candidate file sets,
  per-candidate archive admission events, and CLI-written `best.py` /
  `best_workspace/` artifacts; startup manifests retain configured absolute
  `log_dir` roots as a placeholder plus SHA-256 metadata rather than raw local
  paths
- explicit v1 run-artifact schema metadata on `manifest.json` and current
  JSONL streams, with legacy history rows still readable for `show` and restore
  helpers
- manifest-visible `libreevolve.candidate_language_policy.v1` records that
  declare the current Python-primary text-workspace boundary and explicitly
  mark arbitrary-language/build-system runners as unsupported
- local run-budget stop accounting for generations, evaluations,
  evaluator-seconds, and wall-clock runtime
- framework-owned run-local RNG isolation plus persisted `runtime.rng`
  snapshots that direct callers and CLI runs can restore before startup
- example problems including `hello_world`, `sorting`, `circle_packing`,
  `matrix_multiplication`, and `workspace_math`

The project is still a Python-only, synchronous, local-workspace prototype. It
is not yet an AlphaEvolve reproduction.

## Near Term

### 1. Finish candidate workspace fidelity

- Extend the current Python-primary candidate-language policy into actual
  language/runner declarations when non-Python candidates become supported.
- Add problem-defined candidate abstraction hooks if LibreEvolve should move
  beyond the documented code-file-set divergence from AlphaEvolve's flexible
  solution-abstraction API.
- Add language-aware evolve-block marker grammars if non-Python workspace files
  should preserve skeleton regions; the current boundary rejects marker-like
  declarations in non-`.py` files instead of treating them as unmarked full-file
  candidates.
- Add richer workspace fixtures beyond the current `workspace_math` nested
  package, JSON data, and binary static seed asset smoke case.
- Extend binary/static candidate handling beyond bounded encoded members to
  external copy-only static assets and raw non-encoded binary members.
- Keep topology-operation collision policy and structured materialization-
  failure diagnostics complete as new workspace, language, and build-runner
  edge cases are introduced.
- Add migration/resume support for workspace candidates.

### 2. Strengthen multi-objective search

- Extend the current documented hybrid, which averages normalized declared
  metrics for archive ranking, into a first-class multi-objective policy:
  Pareto archive, configurable weighted composition, metric-specific elites,
  or another tested policy.
- Extend the current configurable parent/inspiration sampling and run-local
  resurfacing queries beyond score, individual metric excellence, novelty,
  recency, lineage, feedback, and random/mixed policies to persisted
  feedback, lineage-diversity, and novelty indexes.
- Replace the remaining adaptive diversity descriptor with evaluator-provided
  behavior descriptors, a fixed descriptor model, or explicit rebin/snapshot
  semantics.
- Extend the current `show` archive objective-vector summaries into future
  metric-specific archive views.

### 3. Expand evaluation cascades

- Extend artifact collection beyond candidate-workspace copy-out where needed:
  outside-workspace artifacts, aggregate emitted-artifact hashes, and clearer
  artifact schemas for benchmarks.
- Extend budget accounting beyond current generation/evaluation/
  evaluator-second/wall-clock/logical-LLM-call stop reasons to token, cost,
  provider-attempt, LLM wall-clock, accelerator, and async queue budgets.
  Provider-attempt, provider-token, configured-cost, and retained LLM latency
  usage now stop live runs before the next LLM call and can be pre-applied
  from full-runtime restore bundles; accelerator budgets, async queue budgets,
  and pending-work/provider-output restore composition remain open.
- Extend paper-facing `libreevolve.llm_budget_report.v1` cooperative
  enforcement snapshots to pending-work queues, provider-output replay, and hard
  cancellation semantics; provider-attempt, token, configured-cost, and retained
  latency limits already feed live resumed-run stop checks.
- Emit calibration/ablation runs for LLM feedback graders; the
  `libreevolve.llm_feedback_calibration.v1` report and artifact-inventory
  contracts now validate declared multi-task calibration evidence, but no
  runtime fixture generates those reports yet.
- Add OS/container-grade validator network isolation and stronger
  sandbox/resource controls beyond the current Python-socket denial option,
  minimal environment, wall-clock budgets, and process-tree cleanup.
- Extend evaluator provenance beyond the enforced problem-local dependency
  policy to cover external package/native data access when that becomes part of
  the sandbox/environment contract.
- Preserve complete transitive environment/package provenance for evaluator
  runtime dependencies beyond the current bounded package/version and
  redacted/hash-backed `pip freeze` snapshots.
- Extend current bounded environment provenance into stronger reproducibility
  evidence: complete install-source interpretation semantics, external build
  execution/options/environment records beyond `pyproject.toml`
  `[build-system]` and installed `WHEEL` metadata, non-project build metadata
  policy, live provider service/API-version capture, provider cost and
  remote-default capture, accelerator budget/accounting semantics, and
  remaining private package-source resolution policy.

### 4. Prompt and context work

- Extend prompt-template validation beyond the current schema, dry-run format
  checks, and parent-placeholder retention into role-specific compatibility
  policies and prompt-program deduplication.
- Replace first-N-character context truncation with deterministic
  summarization/ranking for local PDFs and extracted text.
- Extend current prompt caps, mutation-path provider-token section packing,
  role-scoped final-prompt token counting, and backend context-window metadata
  into selected-backend provider-token section packing across all prompt roles
  and context surfaces.
- Extend current prompt/history retention controls into replay-retention
  policy and richer context-policy ownership. Mutation prompts, explicit
  context spans, critique prompts/mutations, feedback raw/parsed fields,
  provider output/error text, plugin context, meta-prompt evidence, framework
  quarantine snapshots, and DeepResearch retrieval bodies already have
  bounded configurable retention surfaces.
- Integrate current evaluator-output prompt summaries, aggregate syntax
  diagnostics, and bounded run-local artifact content retrieval with
  selected-backend provider-token section packing. Artifact content can already
  be reopened from copied UTF-8 evaluator artifacts under bounded, redacted,
  run-local policy.
- Extend DeepEvolve-inspired retrieval from bounded provenance into
  audit-grade source integrity: unbounded provider-payload/source-content
  artifacts, learned or externally scored ranking/selection evidence beyond
  provider order, a replayable transport/failure decision tree, and explicit
  default-provider plus custom-provider provenance tests.
- Extend the current optional `IDEA`/`RATIONALE`/`HYPOTHESIS` proposal metadata
  preamble into a richer versioned proposal object only if needed; remaining
  work is proposal scoring, semantic proposal-index retrieval beyond the
  bounded manifest `runtime.history.hypothesis_index`, hypothesis-refinement
  loops, and stricter policy for which proposal fields may influence
  retrieval, prompting, and archive resurfacing.
- Improve meta-prompt scoring beyond the current absolute/improvement child
  score reward modes and UCB-style prompt-arm selection; add calibrated reward
  signals plus ablation reporting for prompt-program lineages.

### 5. Documentation truthfulness

- Keep README, docs, paper index, and `docs/todo/*` aligned with implemented
  behavior.
- Keep paper-manifest validation diagnostics shareable by using
  repository-relative labels and secret-redacted exception text in text and JSON
  output.
- Continue labeling CausalEvolve, DeepEvolve, ImprovEvolve, ThetaEvolve,
  GigaEvo, CodeEvolve, and MadEvolve features as inspired unless paper behavior
  is actually implemented.

## Mid Term

### 6. Async and resumable runtime

- Add a controller with bounded queues for LLM proposals and evaluator workers;
  the current loop supports sequential `proposals_per_generation` batches but
  not concurrent proposal/evaluation queues.
- Compose the current restored LLM scheduler, prompt-history, RNG, archive, and
  budget snapshots with controller and pending-evaluation checkpoint state so
  long runs can resume from more than a terminal drained boundary.
- Extend the current restorable MAP-Elites cell/island snapshots, elite
  snapshots, and island cursor/counter state with descriptor-value replay
  semantics, ordered migration-event replay, controller queues, and pending-work
  restore. Current manifests can restore cursor-only state or full archive
  cell/elite placements from a previous manifest/history bundle, and
  `--restore-runtime-from-manifest` composes those compatible synchronous
  restore surfaces into a checked full-runtime bundle, but it is not a full
  replay or resumed experiment trace.
- Complete run manifest hardening for direct custom plugin package-registry and
  constructor-value/schema attribution beyond the current direct-instance
  signature-only policy, plus aggregate hashes for artifacts emitted after
  startup. Git/code state, redacted/hash-backed source/problem/Git root labels,
  problem hashes, direct evaluator hashes, plugin module hashes, built-in plugin
  constructor specs, and entry-point distribution/schema/paper-scope metadata
  are already recorded.
- Complete seeded replay semantics for run ids, candidate ids, prompt-program
  ids, restored archive/controller state, plugin/provider RNG boundaries, and
  provider nondeterminism. The framework RNG snapshot can already be restored
  for direct `evolve()` calls and CLI runs, and the current full-runtime bundle
  composes it with compatible LLM scheduler, archive, budget, controller-budget,
  and lineage-boundary checks; provider/plugin output replay, controller
  pending-work state, and end-to-end resumed-trace proof are still open.
- Extend budget accounting beyond the current local synchronous generation,
  evaluator-call, evaluator-second, wall-clock, LLM call/provider/token/
  configured-cost/latency, synchronous controller-budget event replay, and
  stop-reason counters, plus pre-applied full-runtime restore bundles, to cover
  concurrent evaluations, async queues, pending-work restore, provider-output
  replay, and executed equal-budget ablation reports. The named AlphaEvolve
  Figure 8 ablation variants are now captured as a validated report contract,
  but the runs/curves are not implemented.

### 7. Backend scheduling and critique

- Normalize/document UCB rewards against bounded assumptions or rename the
  current policy as a heuristic.
- Extend configured reward-accounted role selection into separate per-role
  scheduler state, reward signals, quotas, and budget policy for mutation
  generation, critique, feedback grading, and meta-prompt mutation calls.
- Extend current run-scoped call telemetry beyond provider usage, configured
  cost estimates, request ids, finish reasons, adapter-internal retry
  summaries, and token/cost/latency budget stops to include raw provider
  diagnostics, live provider pricing/default-rate capture beyond configured
  token-cost estimates, and richer budget-event evidence.
- Extend the current configurable role/backend consecutive-failure quarantine
  and zero-reward scheduler penalty beyond ensemble-local retry/fallback
  handling, restorable scheduler failure-policy state, and strict ledger
  summaries to cross-run resume, provider isolation, live cancellation/stop
  behavior, raw provider-output replay, and persisted runtime artifacts for
  mutation, critique, feedback, and meta-prompt calls.
- Connect `libreevolve.provider_cancellation_policy.v1` to live provider SDK
  cancellation, budget-affecting timeout/cancellation stop behavior across LLM
  roles, cross-run quarantine/resume behavior, and persisted role-specific
  timeout artifacts beyond the currently covered timeout-policy,
  scheduler-observation, in-run quarantine-evidence, and mutation timeout
  failure-history paths.
- Extend current focused `throughput_depth` metadata tests into
  AlphaEvolve-style breadth/depth/cost/latency scheduler validation, including
  experiment-level selection traces and equal-budget report evidence.
- Extend current synchronous configurable critique reviewer pools, role routing,
  and first/last-valid aggregation toward async reviewer overlap, calibrated
  reviewer scoring, stronger provider isolation, and runtime artifacts for
  reviewer-specific timeout/failure behavior.

### 8. Plugin extensibility

- Extend the bounded `libreevolve.plugins` entry-point registry toward richer
  package policy and direct custom-plugin schema/provenance beyond the current
  entry-point distribution metadata and direct-instance signature-only policy.
- Broaden plugin configuration schemas beyond built-in scalar/path options and
  entry-point declared constructor schemas to cover direct custom constructor
  policy.
- Extend paper-inspiration scope and package-version attribution beyond current
  configured entry-point plugin labels/distribution records to direct custom
  plugins and versioned custom registries.
- Extend plugin provenance beyond current prompt-context/configuration/artifact
  records and manifest-safe emitted artifact summaries to cover stronger
  artifact lifecycle hashes, versioned custom registry entries, and richer
  strategy choices.

## Longer Term

### 9. Representative benchmarks

- Add stronger AlphaEvolve-style fixtures beyond toy examples:
  matrix-multiplication variants, kissing/circle packing extensions,
  constructive math, and one safe compiler/hardware/systems/kernel/scheduling
  microbenchmark.
- Separate smoke examples from benchmark fixtures, with anti-gaming validators,
  fixture-emitted artifacts, SOTA/target baselines, and repeated-seed runs.
  Current example seed-score classes are documented: `hello_world`,
  `circle_packing`, and `matrix_multiplication` are optimization-pressure
  smoke fixtures, while `sorting` is a neutral plateau/diversity fixture.
  The matrix smoke validator now rejects known import/library delegation,
  module-level dead-code counters, and fixed-three-case lookup shortcuts, but
  stronger benchmark fixtures that emit the existing report contracts remain
  planned work. The matrix smoke fixture also has a scope-checked hardening
  bundle helper that emits report, inventory, summary, and smoke-scope
  validation evidence while preserving `alphaevolve_comparable: false`.
- Connect real benchmark fixtures to `libreevolve.benchmark_hardening.v1`
  reports emitted by actual randomized/exhaustive validators and anti-gaming
  fixtures, including protected score/correctness/artifact signals,
  shortcut-threat evidence, operation/rank instrumentation, and saved
  construction artifacts.
- Connect real compiler/hardware/kernel/scheduling fixtures to
  `libreevolve.systems_result_report.v1`, with separate optimization,
  held-out/generalization, and reference-correctness gates plus artifacts that
  distinguish loop feedback from generalization, deployment, or independent
  certification evidence.
- Document reachable metric ranges, target/SOTA values, and normalization
  behavior for benchmark fixtures so intended improvements remain ordered.
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
- Improve `show` beyond the current validity/archive-aware selected-row view
  with runtime status, lineage/prompt/evaluation/feedback/failure summaries,
  bounded objective-vector metrics, and workspace-file display toward whole-run
  source integrity checks, richer archive/prompt/failure drill-downs, and
  durable query views over run artifacts.
- Extend current `pyproject.toml` metadata, dev extras, and console-script
  packaging beyond editable/local use with wheel/sdist build checks,
  package-data validation, install-from-wheel smoke tests, and release-artifact
  provenance.
- Extend the current path-scoped GitHub Actions workflow beyond secret scan,
  Python 3.11/3.12 non-integration tests, optional integration tests, and
  documented paper-manifest commands with broader docs/paper-specific
  validation, more interpreter/platform coverage, and notification-safe trigger
  and branch policy.

## Non-Goals For Now

- Requiring a service database for normal local use.
- Claiming arbitrary-language/codebase support before runners and validators
  exist.
- Advertising paper-inspired plugins as faithful implementations.

## Good First Follow-Ups

1. Persist database query indexes beyond run-local metric/novelty/lineage/
   feedback resurfacing.
2. Add one non-toy benchmark run fixture with expected artifacts.
3. Add workspace resume coverage beyond current `best_workspace/` export.
4. Emit real LLM feedback calibration reports and grader ablation fixtures.
