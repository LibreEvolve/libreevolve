# Roadmap

This roadmap reflects the current codebase after ongoing AlphaEvolve-alignment
passes against `papers/2506.13131__AlphaEvolve.pdf`, local docs, the paper
index, and the checked-in tests. It is a practical development plan, not a
promise.

## Current State

LibreEvolve has:

- Python seed programs and seed workspaces with load-time-validated optional
  `# EVOLVE-BLOCK-START/END` regions
- marker spelling provenance reports under
  `runtime.history.marker_spelling_provenance_report`, recording AlphaEvolve
  Section 2.1/Figure 3 marker-text source locations, local parser probes, and
  the current canonical-only compatibility decision for the Figure 3 space
  variant
- existing-codebase integration reports under
  `runtime.history.existing_codebase_integration_report`, inventorying
  candidate workspace marker spans, skeleton hashes, unmarked-file hashes,
  seed-source references, and explicit remaining gaps for original codebase
  identity, marker-only setup diffs, and setup-change counts
- SEARCH/REPLACE diff mutation, including canonical AlphaEvolve fences, and
  configurable full-block/full-code replacement with unknown named block
  targets rejected before partial replacement
- workspace file topology mutations for create/edit/delete/move/rename and
  primary-file changes
- candidate path hardening for unsafe, ambiguous, overlong, Unicode-control,
  reserved, and dot-prefixed generated paths
- structured evaluator results with metrics, stage outcomes, diagnostics, and
  elapsed time
- configurable local evaluator stages with distinct validator entrypoints or
  opt-in candidate-owned `evaluate(eval_inputs)` entrypoints, thresholds,
  samples, validator-managed seed values, retries, timeouts, and per-attempt
  history
- embedded evaluator entrypoint reports under
  `runtime.history.embedded_evaluator_entrypoint_report`, summarizing executed
  candidate-owned `evaluate(eval_inputs)` stages, eval-input provenance,
  dependency scope, metric names, and remaining Figure 3 parity gaps
- AlphaEvolve Figure 1/Figure 2 process-exhibit reports under
  `runtime.history.alphaevolve_process_exhibit_report`, preserving stable
  figure IDs, node/edge-to-component mappings, Figure 2 pseudocode-step
  mappings, artifact cross-links, and explicit gaps for rendered diagram
  hashes, exact diagram text, and full process parity
- runtime cascade summaries that aggregate configured-stage promotion,
  attrition, threshold failures, work counters, and explicit claim-readiness
  limitations under `runtime.history.evaluation_cascade_report`
- evaluator-workload declarations for configured stages, including
  `simple_check`, `inner_search`, `ml_training`, and `custom` classifications,
  validated dataset/budget/checkpoint/score-field metadata, validator-visible
  `stage["workload"]`, and runtime aggregation under
  `runtime.history.evaluator_workload_report`
- strict scalar evaluator-output validation against `metrics.yaml`, including
  finite, strictly increasing non-boolean metric bounds and a reserved boolean
  validity gate outside optimization metrics
- paper-facing evaluator metric contracts under
  `runtime.history.paper_evaluator_metric_contract`, separating evaluator
  scalar metrics from local validity/output/feedback fields and recording raw,
  maximized, and normalized score evidence
- single-run paper metric table exports under
  `runtime.history.paper_metric_table_export`, with stable metric/program rows,
  raw/maximized/normalized value columns, display precision policy, excluded
  metric notes, and deterministic table hashes
- evaluator/oracle registry reports under
  `runtime.history.evaluator_oracle_registry`, registering the default
  validator or configured cascade stages plus LLM feedback graders with metric
  ownership, merge policy, failure policy, prompt-feedback linkage, and an
  explicit limitation for independent multi-oracle arbitration
- proposal lifecycle reports under
  `runtime.history.proposal_lifecycle_report`, merging generated-candidate
  history with failure records to show backend/call summaries, mutation hashes,
  evaluator validity, archive admission/rejection, rejection reasons,
  execution-filtered counts, bounded failure-memory linkage, and explicit
  limitations for independent false-acceptance/false-rejection audits
- opt-in evaluator artifact copy-out from temporary candidate workspaces with
  hashes, limits, and text redaction metadata
- validator subprocess environment allowlisting, persisted stdout/stderr
  redaction, and best-effort timeout process-tree cleanup
- MAP-Elites plus configurable ring-topology island migration, defaulting to
  five islands
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
- manifest-visible `libreevolve.alphaevolve_task_specification_bundle.v1`
  records that cross-link startup inputs such as seeds, evaluators, prompts,
  backends, context, candidate policy, and metrics into a partial task-spec
  bundle with validation and explicit remaining gaps
- runtime task-spec artifact-resolution reports under
  `runtime.history.task_spec_artifact_resolution_report`, validating
  task-spec manifest paths and linking each field to candidate-history,
  prompt-history, LLM-call, controller-budget, evaluator-artifact, and
  best-export evidence while leaving evolvable-span and score-link parity open
- manifest-visible `libreevolve.candidate_language_policy.v1` records that
  declare the current Python-primary text-workspace boundary and explicitly
  mark arbitrary-language/build-system runners as unsupported
- runtime candidate-abstraction choice reports under
  `runtime.history.candidate_abstraction_choice_report`, recording the current
  code-file-set selection, policy/runner linkage, runtime workspace shape,
  unsupported constructor/search/paired alternatives, and remaining
  AlphaEvolve abstraction-rationale and bias-evidence gaps
- local run-budget stop accounting for generations, evaluations,
  evaluator-seconds, wall-clock runtime, logical LLM calls, provider attempts,
  provider-reported tokens, configured estimated cost, and retained LLM
  latency
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
- Extend candidate-abstraction reports with benchmark metadata that records why
  a direct-solution, constructor-function, or search-algorithm formulation was
  chosen, what symmetry/structure bias was expected, and how alternatives
  performed under comparable budgets.
- Add language-aware evolve-block marker grammars if non-Python workspace files
  should preserve skeleton regions; the current boundary rejects marker-like
  declarations in non-`.py` files instead of treating them as unmarked full-file
  candidates.
- Add richer workspace fixtures beyond the current `workspace_math` nested
  package, JSON data, and binary static seed asset smoke case.
- Add a codebase-scale benchmark/report before claiming AlphaEvolve Table 1
  parity for entire-code-file, hundreds-of-lines, or multi-component algorithm
  evolution; current multi-file workspace support is only a local mechanics
  surface.
- Add mutation-operator construction reporting before claiming AlphaEvolve's
  Related Work distinction from systems with fixed handwritten mutation or
  crossover operator sets. Current diff/full/topology support is an edit
  grammar, not evidence that LLMs construct or adapt higher-level operator
  families.
- Extend binary/static candidate handling beyond the current bounded encoded
  static members, verified copy-only static assets, and raw direct-workspace
  byte normalization into richer binary mutation/replay policy.
- Keep topology-operation collision policy and structured materialization-
  failure diagnostics complete as new workspace, language, and build-runner
  edge cases are introduced.
- Extend workspace-candidate resume beyond the current archive-content restore
  bundle to ordered migration-event replay, controller queues, and pending-work
  resume.

### 2. Strengthen multi-objective search

- Extend the current single-run paper metric table export into cross-run
  metric-contract diff reports.
- Extend the current documented hybrid, which averages normalized declared
  metrics for archive ranking, into a first-class multi-objective policy:
  Pareto/frontier primary archive replacement, durable cross-run
  metric-specific optimization, or another tested policy beyond the current
  scalar primary grid plus bounded Pareto and metric-cell retained overlays.
- Extend the current configurable parent/inspiration sampling and run-local
  resurfacing queries beyond score, individual metric excellence, novelty,
  recency, lineage, feedback, and random/mixed policies to persisted
  feedback, lineage-diversity, and novelty indexes.
- Add source/workspace deduplication and evaluation-cache policy before
  treating deterministic candidate ids or workspace hashes as AlphaEvolve-grade
  memory over previously explored programs; identical proposals are not yet
  proved to skip, reuse, or intentionally re-evaluate with budget telemetry.
- Replace the remaining insertion-time adaptive TF-IDF diversity coordinates
  with evaluator-provided behavior descriptors, a fixed/learned descriptor
  model, or explicit tested rebin/snapshot semantics.
- Extend the current selected-row `show` archive objective-vector summaries
  and manifest-level metric archive summaries into CLI/report drill-downs for
  metric-specific archives.

### 3. Expand evaluation cascades

- Extend artifact collection beyond candidate-workspace copy-out where needed:
  outside-workspace artifacts, aggregate emitted-artifact hashes, and clearer
  artifact schemas for benchmarks.
- Extend budget accounting beyond current generation/evaluation/
  evaluator-second/wall-clock/logical-LLM-call, provider-attempt,
  provider-token, configured-cost, and retained LLM-latency stop reasons to
  accelerator and async queue budgets.
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
- Add statistical hypothesis-test promotion policies for cascades, separating
  current staged threshold gates from AlphaEvolve-style small-scale filters,
  main-test promotion decisions, confidence or p-value evidence, and
  sequential stopping diagnostics.
- Extend the evaluator/oracle registry into configurable independent
  multi-oracle authority, sufficiency, and conflict-resolution policies beyond
  the current local cascade plus optional synchronous feedback graders.
- Extend evaluator-workload provenance into actual workload-specific execution
  contracts for inner-search and ML-training tasks: dataset/split hash
  enforcement, training/search loop runners, checkpoint completeness checks,
  score-field-to-artifact linkage, and stochastic re-evaluation policy.
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
  remaining private package-source resolution policy, plus restore/check
  validation that separates bounded audit hints from replayable evaluator
  environment proof.

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
  preamble, bounded `runtime.history.hypothesis_index` summaries, and
  `runtime.history.hypothesis_branch_report` abandonment evidence into scored
  and semantically searchable proposal memory only if needed; remaining work is
  proposal scoring, semantic proposal-index retrieval, controller-driven
  backtracking decisions, cross-run proposal tables, hypothesis-refinement
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
- Keep the paper-index validator boundary explicit: it currently proves
  manifest/readability/count checks, Appendix B and ablation registry shape,
  implementation-status table structure, role/status taxonomy compatibility,
  TODO coverage row coverage, active ledger links, and completed-ledger
  checklist evidence. It does not yet prove every long status phrase,
  benchmark qualifier, or paper claim against a specific evidence record.
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
- Extend configured reward-accounted role selection, role-scoped backend
  eligibility, logical call caps, and role budget maps into separate per-role
  live scheduler state, calibrated reward signals, quota ownership, and budget
  policy for mutation generation, critique, feedback grading, and meta-prompt
  mutation calls.
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
- Add proposal-count/sample-efficiency reports that distinguish current LLM
  call/provider/token/configured-cost caps from AlphaEvolve Table 1 evidence
  that useful results can be reached with thousands rather than millions of
  LLM-generated samples.
- Extend current synchronous configurable critique reviewer pools, role routing,
  and first/last-valid aggregation toward async reviewer overlap, calibrated
  reviewer scoring, stronger provider isolation, and runtime artifacts for
  reviewer-specific timeout/failure behavior.

### 8. Plugin extensibility

- Extend the bounded `libreevolve.plugins` entry-point registry toward richer
  package policy and direct custom-plugin schema/provenance beyond the current
  entry-point distribution metadata and direct-instance signature-only policy
  that explicitly excludes constructor values.
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
  validation evidence while preserving `alphaevolve_comparable: false`. The
  standard paper-manifest gate now validates the shipped example-scope records
  directly so smoke fixtures cannot drift into paper-comparable claims.
- Connect real benchmark fixtures to `libreevolve.benchmark_hardening.v1`
  reports emitted by actual randomized/exhaustive validators and anti-gaming
  fixtures, including protected score/correctness/artifact signals,
  shortcut-threat evidence, operation/rank instrumentation, and saved
  construction artifacts. For Appendix B-style constructive-math claims, add
  Colab-equivalent construction-data exports and runnable verifier-code
  artifacts rather than only family/status registry entries.
- Add constructive-math aggregate outcome ledgers before making Section 3.2-
  style breadth claims: per-problem/per-parameter rows, mathematical branch
  labels, prior-best references, matched/improved/fell-behind status, and
  validated percentages for dozens-problem coverage.
- Add Appendix B result-version provenance before quoting paper-level
  constructive-math constants: source manuscript version, reported value,
  superseded/current status, update note, attribution, and verifier/Colab
  artifact linkage for revised results such as the uncertainty-inequality
  bound.
- Keep paper artifact-role attribution separate from artifact availability:
  `libreevolve.alphaevolve_paper_artifact_roles.v1` now validates the
  AlphaEvolve PDF contribution records for figure creators and companion
  Colab assemblers, but rendered figure artifacts and local notebook/export
  availability remain future work.
- Keep AlphaEvolve source-PDF versioning explicit:
  `libreevolve.alphaevolve_source_pdf_version.v1` now validates the cached
  `2506.13131` PDF manifest row against the audited first-page header
  `arXiv:2506.13131v1 [cs.AI] 16 Jun 2025`, including arXiv id, version,
  category, posted date, floating and versioned URLs, expected header page,
  local byte count, SHA-256 digest, and the policy that claim audits must name
  the source version. The paper-manifest gate validates this built-in record,
  but CSV/JSON row schema fields and per-claim source-version propagation
  remain open.
- Keep paper-cache row identity proven before version/rights evidence:
  `libreevolve.tools.paper_manifest` now validates that arXiv PDF/abs URLs
  contain a source id matching the manifest `id`, and that every local PDF
  filename begins with the manifest id before any `__` title suffix. Non-arXiv
  slug rows use the same filename source-prefix rule. This prevents base
  id/URL/file drift while keeping arXiv source-version fields and source-rights
  metadata as separate follow-on work.
- Keep cached source-PDF rights separate from project licensing:
  `libreevolve.alphaevolve_source_pdf_rights.v1` now validates the AlphaEvolve
  cached PDF page 1 rights statement `© 2025 Google DeepMind. All rights
  reserved`, rights holder/year, source page/location, manifest row hash/bytes,
  and boundaries separating third-party paper-source rights from LibreEvolve's
  MIT license and the companion repository's Apache/CC licensing. The paper-
  manifest gate validates the record against the current cached PDF text.
  Emitted paper-derived artifacts still need explicit excerpt/table/figure
  reproduction-policy rows linked to that rights evidence.
- Keep AlphaEvolve bibliography evidence grounded in source markers:
  `libreevolve.alphaevolve_references_section.v1` now validates that the
  cached PDF References section spans pages 23-32, includes contiguous
  reference ids `[1]` through `[120]`, preserves page-by-page marker ranges,
  and contains selected source anchor phrases. The paper-manifest gate checks
  those markers against the current cached PDF text. Normalized
  author/title/venue/year fields, local-cache linkage, and per-claim citation
  use categories remain open.
- Keep companion Colab source evidence separate from local generated exports:
  `libreevolve.alphaevolve_companion_colab_source.v1` now validates the pinned
  `google-deepmind/alphaevolve_results` commit, `mathematical_results.ipynb`
  raw/Colab URLs, SHA-256 digest, byte count, nbformat, cell count,
  readability status, matrix/constructive-math claim mappings,
  improved-results-only selection policy, matched-result exclusions,
  AlphaEvolve runtime-code absence, and the companion repository's
  Apache-2.0/CC-BY-4.0 license and disclaimer boundary. Local cache validation,
  generated LibreEvolve Colab-equivalent exports, and deeper per-cell claim
  spans remain open.
- Keep follow-on AlphaEvolve mathematical-discovery sources separate from the
  original `2506.13131` specification: `libreevolve.alphaevolve_follow_on_math_source.v1`
  now validates arXiv `2511.02864v3`, the 2025-12-22 revision date, the
  `Mathematical exploration and discovery at scale` title/author surface, and
  the pinned `google-deepmind/alphaevolve_repository_of_problems` snapshot at
  commit `bfd224d0e7763f89eb4a8efe93ac126091f85ed9`. It records the README
  digest, live-repository policy, declared 67-problem count, many-but-not-all
  notebook coverage, prompt/verifier/initial/final artifact kinds, runtime-code
  absence, source-use licenses, and citation boundary. Cached PDF rows,
  emitted source manifests, per-problem inventory, numbered-page reconciliation,
  notebook artifact hashes, and Appendix B claim mappings remain open.
- Keep follow-on problem-repository coverage snapshot-scoped:
  `libreevolve.alphaevolve_follow_on_problem_coverage.v1` now validates the
  pinned repository status artifacts (`status.json`, `status_grid.png`, and
  `result_distribution.png`), parses the four explicit `status.json` buckets
  into 43 listed problem ids, preserves the 24 ids not listed in `status.json`
  as `not_listed_in_status_json`, records browser-page and many-but-not-all
  Colab access modes, and captures the declared-67 versus observed-68 numbered
  HTML page boundary. Per-page hashes, notebook path/hash or absence reasons,
  prompt/verifier/initial/final/visualization flags, and page-68
  classification remain open.
- Keep Appendix A matrix target-suite curation scoped to reported-suite
  provenance: `libreevolve.alphaevolve_appendix_a_matrix_curation.v1` now
  validates the rough size-selection wording, sorted representative policy,
  axis-permutation equivalent omissions, included-target rationales, and
  unspecified `p` cutoff. Explicit non-equivalent excluded-target
  justifications remain open.
- Keep matrix target-scaling claims scoped to paper-source frontier evidence:
  `libreevolve.alphaevolve_appendix_a_matrix_resource_frontier.v1` now
  validates the Appendix A page 34 boundary for sizes beyond `<5,5,5>`, 1000
  random seeds, single-GPU evaluators, frequent OOM, and further-optimization
  need. Local scaling runs with attempted target sizes, measured GPU memory,
  OOM artifacts, reduced-seed tradeoffs, and exclusion rationale remain open.
- Keep matrix near-integrality wording scoped to evidence validation rather
  than executed search parity: `libreevolve.matrix_near_integrality_evidence.v1`
  now validates declared prompt instructions, integer/half-integer nearest
  rounding policy, raw-versus-rounded coefficient diagnostics, rounding-error
  consistency, and exactness-certificate links. Local benchmark runners still
  need to emit those records during matrix search.
- Keep matrix scalar-field wording scoped to evidence validation rather than
  emitted complex result parity: `libreevolve.matrix_scalar_field_evidence.v1`
  now validates declared real, complex, finite-field, and any-field
  applicability, field characteristic, exact coefficient representation,
  complex component domains, finite-field characteristic/order, paper complex
  target caveats, and certificate scope. Local benchmark runners still need to
  emit exact complex decomposition/certificate artifacts for those claims.
- Keep matrix tensor-rank wording scoped to evidence validation rather than
  emitted tensor-rank parity: `libreevolve.matrix_tensor_rank_evidence.v1` now
  validates algorithm kind, tensor-identity certificate scope, recursive
  applicability, target-tensor and exactness-certificate links, and source-note
  caveats for non-tensor multiplication algorithms. Local benchmark runners
  still need to emit those target-tensor/certificate and footnote-caveat
  artifacts.
- Keep matrix sweep-space wording scoped to evidence validation rather than
  executed Figure 9 workflow parity: `libreevolve.matrix_sweep_space_evidence.v1`
  now validates declared `sweep` function identity, user-provided `hyper`
  library provenance, hyperparameter ranges, sampled configuration rows with
  losses/ranks, winning configuration identity, and final decomposition plus
  exactness-certificate links. Local benchmark runners still need to emit
  those records during matrix search.
- Connect real compiler/hardware/kernel/scheduling fixtures to
  `libreevolve.systems_result_report.v1`, with separate optimization,
  held-out/generalization, and reference-correctness gates plus artifacts that
  distinguish loop feedback from generalization, deployment, or independent
  certification evidence.
- Add claim-calibrated metric records for systems reports before treating
  finite metrics as reproduced AlphaEvolve Section 3.3 result magnitudes:
  metric units, denominators, baselines, aggregation windows, deployment or
  runtime/synthesis context, and explicit mapping to scheduling resource
  recovery, kernel/training-time speedups, RTL PPA deltas, and compiler
  kernel/pre/postprocessing speedups.
- Add hardware-adoption evidence for TPU RTL-style reports before claiming
  Section 3.3.3 parity: RTL-stage workflow placement, standard-Verilog
  trust/adoption rationale, upcoming-chip integration, and time-to-market
  impact in addition to PPA and verification artifacts.
- Add self-improvement evidence boundaries before claiming AlphaEvolve-style
  infrastructure or base-model uplift: component identity, before/after
  measurements, deployment/adoption status, rollback/safety review, provenance
  tying the candidate to LibreEvolve's own execution path, and any
  distillation dataset/training/evaluation artifacts.
- For scheduling fixtures, add mission-critical deployment evidence beyond
  generic systems gates: interpretable heuristic structure, debuggability and
  operator review, predictable behavior checks, rollout-risk evidence, and
  comparison against less interpretable learned-policy baselines.
- Document reachable metric ranges, target/SOTA values, and normalization
  behavior for benchmark fixtures so intended improvements remain ordered.
- For each local domain paper, either add a benchmark, link it to an existing
  benchmark, or keep it marked background-only in `papers/README.md`.
- Add repeatable benchmark scripts for backend, seed, prompt, and archive
  ablations.
- For the Figure 8 `No evolution` ablation, keep the registry's validated
  prompt-history `paper_scope_boundary` marked unproven until prompt/history
  proof shows that every proposal uses the same initial program and excludes
  evolutionary database parent, inspiration, previous-candidate, and
  archive-feedback context.
- For the Figure 8 `No context in the prompt` ablation, keep the registry's
  validated explicit-context `paper_scope_boundary` marked over-broad and not
  equivalent until prompt-history or prompt-diagnostic proof shows that
  explicit problem/context sources were absent, while separately recording
  whether normal current-program,
  prior-program/inspiration, and rendered-result prompt ingredients remained
  present as part of the evolutionary prompt.
- For the Figure 8 `Small base LLM only` ablation, keep the registry's
  validated backend-telemetry `paper_scope_boundary` marked unproven until
  backend metadata and call-ledger proof shows that every mutation-generation
  call used one configured small/base-capable model with no large-model routing
  or fallback.
- For the Figure 8 `No meta prompt evolution` ablation, keep the registry's
  validated prompt-lineage `paper_scope_boundary` marked unproven until
  prompt-history, call-ledger, and prompt-program lineage proof shows that
  meta-prompt calls and prompt-template mutations were absent only in the
  ablated run and enabled in the full-system comparator.
- For the Figure 8 `No full-file evolution` ablation, keep the registry's
  validated `paper_scope_boundary` marked not equivalent until a
  tensor-decomposition harness proves only the loss function was mutable.
- Generate benchmark scripts that emit the validated Figure 8 target-family
  ablation reports and rendered curve exhibits; the report schema now requires
  comparable compute-budget fractions, target-metric identity, direction,
  normalization, and per-target mean/std aggregation, while the Figure 8
  exhibit schema validates panel ids, exact paper legend labels, axis/style
  metadata, rendered artifact hashes, and report/raw-trace links. No real
  runner produces those reports or rendered exhibit artifacts yet.
- Keep Appendix A Figure 9 matrix-diff exhibit claims scoped to declared
  exhibit validation: `libreevolve.alphaevolve_figure9_matrix_diff_exhibit.v1`
  now validates Figure 9a/9b/9c panel ids, pages 35-37, Figure 4 caption
  linkage, ordered line spans, source-diff/rendered/OCR hashes, semantic
  optimizer/init/noise/clipping/loss/discretization/sweep labels, and links to
  result, sweep-space, certificate, and companion notebook evidence. Rendered
  appendix panel artifacts are still not emitted or checked in.
- Keep Figure 4 matrix-discovery exhibit claims scoped to declared exhibit
  validation: `libreevolve.alphaevolve_figure4_matrix_discovery_exhibit.v1`
  now validates the main-text exhibit id, page 11, caption linkage,
  15-mutation count, `mm_4x4x4` rank-48 mapping, left diff outline plus the
  three highlighted right-side excerpt regions, source-diff/rendered-region
  hashes, semantic optimizer/init/loss/sweep coverage, and links to Figure 9,
  result, sweep-space, certificate, and companion notebook evidence. Rendered
  Figure 4 artifacts and accepted-mutation lineage records remain open.
- Keep matrix headline historicity claims scoped to declared evidence:
  `libreevolve.matrix_headline_historicity_evidence.v1` now validates the
  `mm_4x4x4` complex rank-48 headline against dimensions, rank, 48 scalar
  multiplications, characteristic-zero scope, 56-year first-below-49 flags,
  recursive Strassen rank-49 comparison, finite-field-only Fawzi rank-47 caveat,
  source refs, and links to result, scalar-field, tensor-rank, Figure 4,
  Figure 9, and companion Colab evidence. The runner still does not emit the
  headline record or linked decomposition/certificate/source artifacts.
- Keep matrix outcome claims scoped to named target subsets:
  `libreevolve.alphaevolve_matrix_subset_scope.v1` now validates
  `appendix_a_full`, `main_text_mnp_le_5`, and `table_2_selected` membership,
  outcome counts, out-of-scope rows, and Table 2/Table 3 source linkage. The
  scoped `m,n,p <= 5` subset has `20` rows with `0` fell behind, while the full
  Appendix A table has `54` rows with `2` fell behind. Runtime reports and
  rendered table artifacts still do not emit those subset-scope records.
- Keep Appendix A matrix row-note claims scoped to declared evidence:
  `libreevolve.alphaevolve_appendix_a_matrix_row_notes.v1` now validates the
  `mm_4x5x6` concurrent-work note that reference `[49]` also found a rank-90
  algorithm for `<4, 5, 6>`, including source page/table, rank relationship,
  and a non-exclusive-priority docs caveat. Runtime reports and rendered table
  artifacts still do not emit that row-note caveat.
- Keep Table 2/Table 3 matrix-rank claims scoped to declared exhibit evidence:
  `libreevolve.alphaevolve_matrix_rank_table_exhibit.v1` now validates stable
  table ids, selected/full-table membership, row ordering, rank values, outcome
  counts/color semantics, complex-row annotations, concurrent-note linkage,
  rendered/source/OCR artifact hashes, and registry/subset/row-note/Colab
  links. Runtime reports still do not render or emit those table artifacts.

### 10. Operational maturity

- Extend current config validation to plugin-specific schemas and
  provider/model API compatibility where feasible.
- Extend strict finite JSONL coverage and diagnostics beyond current
  candidate, prompt, manifest, and GRPO-export writers as new run artifacts are
  added.
- Improve `show` beyond the current validity/archive-aware selected-row view
  with runtime status, lineage/prompt/evaluation/feedback/failure summaries,
  bounded objective-vector metrics, and workspace-file display toward whole-run
  source integrity reports, richer archive/prompt/failure drill-downs, and
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
