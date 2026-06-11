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
  Section 2.1/Figure 3 marker-text source locations, local parser probes,
  hashed local PDF page-text / Figure 3 marker-line artifacts when the paper
  cache is present, final local classification of the Figure 3 space variant
  as PDF text-extraction uncertainty, and the current canonical-only
  compatibility decision for that variant
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
  dependency scope, metric names, per-metric candidate path/block-span link
  candidates, embedded-only problem loading via all-`embedded_evaluate`
  `config.yaml` stages, and remaining Figure 3 parity gaps
- AlphaEvolve Figure 1/Figure 2 process-exhibit reports under
  `runtime.history.alphaevolve_process_exhibit_report`, preserving stable
  figure IDs, node/edge-to-component mappings, Figure 2 pseudocode-step
  mappings, artifact cross-links, and explicit gaps for rendered diagram
  hashes, exact diagram text, and full process parity
- distributed-pipeline topology boundary reports under
  `runtime.history.distributed_pipeline_topology_report`, naming the current
  single-process controller, in-process database, configured LLM sampler
  backends, local evaluator nodes, zero queues, blocking dependency edges, and
  runtime-budget linkage while keeping AlphaEvolve async pipeline parity
  explicitly false
- runtime cascade summaries that aggregate configured-stage promotion,
  attrition, threshold failures, work counters, bounded candidate-stage
  history cross-links, denominator-policy boundaries, and explicit
  claim-readiness limitations under `runtime.history.evaluation_cascade_report`
- cascade hypothesis-test boundary reports under
  `runtime.history.cascade_hypothesis_test_policy_report`, naming configured
  or fallback-inferred small-scale-filter/main-test roles, deterministic threshold/artifact
  promotion, and opt-in `one_sided_lower_confidence_bound` repeated-sample
  gates with confidence-bound, p-value, sequential early-stop, and
  configured false-promotion/false-rejection budget evidence, plus
  `binomial_success_rate` repeated-seed success-rate gates with Wilson
  lower-bound evidence
- evaluator-workload declarations for configured stages, including
  `simple_check`, `inner_search`, `ml_training`, and `custom` classifications,
  validated dataset/budget/checkpoint/score-field metadata, validator-visible
  `stage["workload"]`, runtime dataset/score-field/artifact readiness
  evidence, explicit managed-runner overclaim guards, and aggregation under
  `runtime.history.evaluator_workload_report`
- strict scalar evaluator-output validation against `metrics.yaml`, including
  finite, strictly increasing non-boolean metric bounds and a reserved boolean
  validity gate outside optimization metrics
- paper-facing evaluator metric contracts under
  `runtime.history.paper_evaluator_metric_contract`, separating evaluator
  scalar metrics from local validity/output/feedback fields and recording raw,
  maximized, and normalized score evidence
- explicit-context source-role reports under
  `runtime.history.explicit_context_source_role_report`, backed by validated
  `context.yaml` `source_roles` metadata for human instructions, equations,
  code snippets, literature PDFs, and background references, including task
  topic linkage, source location, startup prompt inclusion/omission decision,
  and hash/redaction policy
- single-run paper metric table exports under
  `runtime.history.paper_metric_table_export`, with stable metric/program rows,
  raw/maximized/normalized value columns, display precision policy, excluded
  metric notes, and deterministic table hashes
- cross-run paper metric comparison reports via
  `paper_metric_cross_run_report()`, validating multiple manifests'
  evaluator-metric contracts and metric table exports, aggregating metric
  names/table hashes, and flagging metric-contract, table-column, or
  display-policy drift
- evaluator/oracle registry reports under
  `runtime.history.evaluator_oracle_registry`, registering the default
  validator or configured cascade stages plus LLM feedback graders with metric
  ownership, merge policy, failure policy, prompt-feedback linkage, an
  `arbitration_policy` authority matrix, benchmark-sufficiency labels,
  conflict roles, failure effects, bounded local `disagreement_outcomes` for
  validator-versus-feedback discard cases, and an explicit limitation for
  independent multi-oracle arbitration
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
- optional LLM feedback graders with qualitative criterion provenance, discard
  rules, and weighted score composition using normalized bounded reviewer
  scores
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
  bundle with validation and explicit remaining gaps, with the same bundle
  emitted as `task_specification.json`
- runtime task-spec artifact-resolution reports under
  `runtime.history.task_spec_artifact_resolution_report`, validating
  task-spec manifest paths and linking each field to candidate-history,
  prompt-history, LLM-call, controller-budget, evaluator-artifact, and
  best-export evidence, plus initial evolvable-span ids and embedded
  score-field candidate-path links with static AST causal attribution when
  candidate-owned `evaluate` metric returns depend on EVOLVE blocks, plus
  bounded candidate and prompt/evaluator JSONL row joins, plus a validated
  standalone task-spec example under `docs/examples/`, while leaving
  arbitrary-validator/build-system task-spec parity open
- runtime prompt prior-score provenance under
  `runtime.history.prompt_prior_score_provenance_report`, linking generated
  mutation prompts to target-parent and selected-inspiration score records,
  source workspace hashes, finite metric values, displayed aggregate score
  formula, history/failure-history rows, evaluator-result rows, and top-level
  prompt-feedback execution-output display attribution, stage-summary IO
  display attribution, score-display field visibility for aggregate and metric
  fields including prompt-context selection/cap omission and truncation
  reasons, explicit `average_score` display/formula aliasing normalized
  `program.fitness`, feedback-section selection/order/section-cap/global-cap
  policy attribution, plus `prompt_prior_score_table.jsonl` cross-run rows
- runtime primary-prompt instruction provenance under
  `runtime.history.primary_prompt_instruction_report`, recording generated
  prompt target solution hashes, sampled supporting inspiration roles,
  mutation-instruction policy/hash, required task/parent-code/instruction
  channel presence, mutation-mode constraints, telemetry call joins when
  present, and the current serialized-single-prompt provider placement
  boundary instead of role-separated provider message parity
- runtime stochastic-formatting distribution provenance under
  `runtime.history.stochastic_prompt_format_distribution_report`, linking
  generated prompt ids to `[[prompt:name]]` option sets, normalized
  probabilities, selected alternative hashes/indexes, weight-source or
  prompt-context override source, inline/effective-config boundary, and the
  run-local framework RNG replay boundary while keeping separate config-file
  source attribution and human-authorship certification out of parity claims
- runtime initial-program idea provenance reports under
  `runtime.history.initial_program_idea_provenance_report`, linking optional
  seed idea-origin metadata and seed variant ids from `problem.seed_sources` to
  generation-0 history rows while leaving equal-budget seed-variant result
  tables and human contribution signoff open
- configurable initial-program validity policy with
  `runtime.history.initial_program_validity_report`, preserving permissive
  invalid generation-0 baselines by default while `alphaevolve_strict` stops
  before mutation with `invalid_initial_programs` when any selected seed is not
  evaluator-valid or lacks declared metrics
- optional problem-formulation metadata under `formulation.yaml` or direct
  `Problem.formulation_metadata`, normalized into
  `problem.formulation_metadata` and summarized by
  `runtime.history.problem_formulation_provenance_report` for expert
  contributor roles, problem origin, formulation notes, objective/evaluator
  rationale, parameter-scope decisions, background refs, and review/signoff
  readiness
- optional external feedback metadata under `collaborator_feedback.yaml` or
  direct `Problem.collaborator_feedback_metadata`, normalized into
  `problem.collaborator_feedback_metadata` and summarized by
  `runtime.history.collaborator_feedback_provenance_report` for early-user or
  collaborator cohorts, feedback event ids, affected workflow areas,
  change-artifact links, validation outcomes, privacy/redaction policy, and
  robustness/versatility claim readiness
- optional acknowledgement metadata under `acknowledgements.yaml` or direct
  `Problem.acknowledgement_metadata`, normalized into
  `problem.acknowledgement_metadata` and summarized by
  `runtime.history.acknowledgement_role_provenance_report` for white-paper
  review, early exploration, support/advice, practical-application management
  advice, application review, application-specific advice, source locators,
  privacy/redaction policy, and review/signoff readiness; the
  `matrix_multiplication` example carries a reviewed AlphaEvolve pages 21-22
  fixture and a manifest regression for the claim-ready acknowledgement-role
  boundary
- optional publication-author metadata under `paper_authors.yaml` or direct
  `Problem.paper_author_metadata`, normalized into
  `problem.paper_author_metadata` and summarized by
  `runtime.history.paper_author_metadata_report` for equal contributors,
  manuscript writers, paper-input contributors, corresponding authors,
  title-page marker linkage, contact/privacy policy, and review/signoff
  readiness; the `matrix_multiplication` example carries a reviewed
  AlphaEvolve pages 1/22/23 fixture and a manifest regression for the
  claim-ready publication-author metadata boundary
- optional title-page affiliation metadata under `title_page.yaml` or direct
  `Problem.title_page_metadata`, normalized into `problem.title_page_metadata`
  and summarized by `runtime.history.title_page_affiliation_report` for
  source-paper affiliation text, footnote marker definitions, author-marker
  mappings, source-rights linkage, privacy/redaction policy, and
  review/signoff readiness; the `matrix_multiplication` example carries a
  reviewed AlphaEvolve page 1 fixture linked to `papers/source_rights.json`
  and a manifest regression for the claim-ready title-page boundary
- optional system-contribution metadata under `system_contributions.yaml` or
  direct `Problem.system_contribution_metadata`, normalized into
  `problem.system_contribution_metadata` and summarized by
  `runtime.history.system_contribution_provenance_report` for system design,
  project scoping, first-benchmark iteration, final-system, infrastructure,
  code-review, coordination, and supervision role provenance; the
  `matrix_multiplication` example carries a reviewed AlphaEvolve pages 22-23
  fixture and a manifest regression for the claim-ready system-development
  contribution boundary
- manifest-visible `libreevolve.candidate_language_policy.v1` records that
  declare the current Python-primary text-workspace boundary and explicitly
  mark arbitrary-language/build-system runners as unsupported
- runtime candidate-language runner contract reports under
  `runtime.history.candidate_language_runner_contract_report`, recording the
  current Python subprocess validator runner, non-Python text files as
  workspace-only/no-runner members, unsupported arbitrary-language and
  build-system runner contracts, unsupported task-abstraction hooks, and exact
  remaining gaps before AlphaEvolve-grade language/build parity
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

- Extend the checked candidate-language runner contracts into actual
  non-Python language runners when non-Python candidates become supported.
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
- Extend `runtime.history.mutation_operator_boundary_report` beyond the
  current fixed diff/full/file/block/topology parser-surface evidence into
  proposal-level operator-family provenance, task/failure-aware operator
  construction, adaptive operator-family selection, scoring, and benchmark
  telemetry before claiming AlphaEvolve's Related Work distinction from
  systems with fixed handwritten mutation or crossover operator sets.
- Extend `runtime.history.prompt_example_copy_report` beyond current built-in
  exact, normalized-region, and example-format skeleton diagnostics into hard
  or configurable acceptance policy, broader semantic/renamed example-copy
  detection, and custom prompt-template example inventories before treating
  concrete prompt examples as fully guarded AlphaEvolve-style current-program
  edit demonstrations.
- Extend `runtime.history.mutation_consistency_report` beyond current
  multi-edit payload inventories, changed file/block/search edit units,
  best-effort Python AST introduced/reference symbols, unresolved-reference
  diagnostics, evaluator taxonomy, and admission links into language-aware
  scope resolution, config/resource dependency models, required-companion-edit
  inference, cross-file dataflow/import resolution, and benchmark-calibrated
  consistency gating.
- Extend `runtime.history.initial_pool_divergence_report` beyond current
  seed-vs-generated workspace hash, bounded primary-file text distance,
  changed-file summary, and numeric metric L1 evidence into task-specific
  functional artifacts, behavior/output-distance metrics, thresholds for
  substantially different claims, and benchmark-level discovery-distance
  telemetry.
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

- Extend the current cross-run paper metric report into persisted benchmark
  bundles and generated CSV/JSON artifacts.
- Extend the current documented hybrid, which averages normalized declared
  metrics for archive ranking, into a first-class multi-objective policy:
  Pareto/frontier primary archive replacement, durable cross-run
  metric-specific optimization, or another tested policy beyond the current
  scalar primary grid plus bounded Pareto and metric-cell retained overlays.
- Extend the current configurable parent/inspiration sampling and run-local
  resurfacing queries beyond score, individual metric excellence, novelty,
  recency, lineage, feedback, and random/mixed policies to persisted
  feedback, lineage-diversity, and novelty indexes. Current generated-candidate
  metadata and `runtime.history.metric_diverse_inspiration_report` now prove
  when a rendered prompt contained inspirations from at least two declared
  metric niches while carrying a `benchmark_policy` boundary with
  `alphaevolve_section_2_4_claim_ready: false`, and
  `runtime.history.sampling_balance_report` now aggregates current-run
  parent/inspiration strategy decisions. Benchmark-required policies, cross-run
  fixtures, scalar/single-metric comparators, and equal-budget strategy-effect
  analysis remain open.
- Extend the current run-local exact-workspace evaluator cache into
  AlphaEvolve-grade duplicate-work memory before treating deterministic
  candidate ids or workspace hashes as durable memory over previously explored
  programs. `runtime.history.duplicate_work_policy_report` now records
  canonical workspace plus evaluator-contract cache-key scope, cache stores,
  cache hits, and no-op cache-hit controller budget events. Durable cross-run
  cache storage, resume-spanning cache replay, stochastic re-evaluation
  policy, and semantic near-duplicate detection remain open.
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
- Extend `runtime.history.qualitative_feedback_policy_report` beyond
  criterion/rubric/intent metadata into calibration/task-suite evidence and
  prompt-history row audits for hard-to-code properties such as simplicity.
- Add broader statistical hypothesis-test promotion policies for cascades,
  extending the current `one_sided_lower_confidence_bound` plus
  normal-approximation error-budget support and `binomial_success_rate`
  Wilson-bound gates into benchmark-calibrated thresholds and repeated-seed
  matrix/tensor fixtures.
- Extend the evaluator/oracle registry beyond the current arbitration-policy
  matrix and local post-evaluator disagreement outcomes into independent
  reference/statistical oracles, benchmark sufficiency evidence, and
  independent cross-oracle disagreement outcome records beyond the current
  local cascade plus optional synchronous feedback graders.
- Extend evaluator-workload provenance into actual workload-specific execution
  contracts for inner-search and ML-training tasks: managed training/search
  loop runners, checkpoint completeness checks beyond observed artifacts,
  score-field-to-artifact causality, and stochastic re-evaluation policy.
- Extend `runtime.history.automated_evaluator_scope_report` beyond the current
  machine-feedback/manual-experiment/LLM-feedback boundary into robust
  evaluator-environment fixtures, manual-to-code transition policy, and
  environment-scaling evidence.
- Extend `runtime.history.programmatic_representation_boundary_report` beyond
  the current executable-code versus natural-language-proposal separation into
  measured hallucination-risk controls, long-horizon step-count evidence, and
  a real AI-Co-Scientist-style natural-language hypothesis stage that can
  bridge into programmatic candidate evaluation.
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
  `runtime.history.hypothesis_branch_report` abandonment evidence, plus
  `runtime.history.proposal_diversity_report` exact duplicate counts and
  `runtime.history.proposal_score_report` outcome/exact-novelty score records,
  `runtime.history.controller_backtracking_report` observed branch-state
  transition/redirect evidence, and
  `runtime.history.natural_language_preamble_report` bounded leading
  explanatory-preamble capture,
  into semantically searchable proposal memory only if needed; remaining work
  is semantic proposal-index retrieval, calibrated proposal-quality models,
  near-duplicate/idea-family novelty, model-quality attribution,
  explicit controller-driven backtracking policies, cross-run proposal tables,
  hypothesis-refinement loops, configurable preamble policy, full-replacement
  preamble disambiguation, rationale-quality scoring, and stricter policy for
  which proposal fields may influence retrieval, prompting, and archive
  resurfacing.
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
  status-cell local-artifact links to active or completed TODO evidence, TODO
  coverage row coverage, active ledger links, and completed-ledger checklist
  evidence. It does not yet prove arbitrary natural-language semantics for
  every long status phrase, benchmark qualifier, or paper claim.
- Persisted validator-boundary consistency now has a CLI artifact gate:
  `validate_run_artifact_validator_boundary_consistency()` loads manifest-backed
  run directories, validates `policies.validator_execution`, scans
  `history.jsonl` and `failure_history.jsonl`, requires
  `evaluation.metadata.validator_boundary` on each persisted attempt, and
  `libreevolve show` fails missing, legacy, or mismatched boundary evidence.
  This remains audit consistency for the declared local-subprocess boundary,
  not OS/container sandbox or quota enforcement.
- Continue labeling CausalEvolve, DeepEvolve, ImprovEvolve, ThetaEvolve,
  GigaEvo, CodeEvolve, and MadEvolve features as inspired unless paper behavior
  is actually implemented.

## Mid Term

### 6. Async and resumable runtime

- Add a controller with bounded queues for LLM proposals and evaluator workers;
  the current loop reports its synchronous topology under
  `runtime.history.distributed_pipeline_topology_report` and supports
  sequential `proposals_per_generation` batches, but not concurrent
  proposal/evaluation queues.
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
- Keep constructive-math aggregate outcome claims scoped to the Section 3.2
  absence boundary until per-instance rows land:
  `libreevolve.problems.benchmarks.math_outcomes` now validates the paper's
  over-50-problem, more-than-five-branch, roughly 75% best-known rediscovery,
  roughly 20% SOTA-improvement, and verification-claim source facts plus the
  required future per-instance and aggregate fields. Per-problem/per-parameter
  rows, mathematical branch labels, prior-best references,
  matched/improved/fell-behind status, construction/verifier artifacts, and
  recomputed aggregate percentages remain open.
- Keep constructive-math starting-point claims scoped to the Section 3.2
  simple-or-random absence boundary: the same metadata module now validates
  the paper statement that the initial starting point was "a simple or a
  random construction" and requires future per-instance fields for starting
  class, construction artifact, generator/random seed, baseline metric,
  prior-best visibility, and prior-best seeding policy. Those artifacts and
  policies remain open before any Section 3.2 breadth claim can be treated as
  simple/random-start evidence.
- Keep constructive-math heuristic-handoff claims scoped to the Section 3.2
  handoff absence boundary: `math_outcomes` now validates that AlphaEvolve
  evolved search-heuristic programs, not direct constructions, gave them fixed
  budgets such as `1000` seconds, showed the previous best heuristic's
  construction, and selected for producing better constructions. Per-instance
  heuristic program artifacts, incumbent/produced construction artifacts,
  before/after metric values, evaluator scores, and verifier evidence remain
  open.
- Keep constructive-math stage-sequence claims scoped to the Section 3.2
  staged-heuristic absence boundary: `math_outcomes` now validates the paper's
  claim that final constructions often came from sequences of specialized
  heuristics, with early broad-gain stages from random/simple states and later
  fine-tuning stages near optimal configurations. Per-stage ordering records,
  stage roles, input/output construction artifacts, improvement deltas, and
  verifier evidence remain open.
- Keep Appendix B per-result metric/value claims scoped to the registry's
  result-row absence boundary: `alphaevolve_appendix_b.json` now validates the
  missing cross-family layer for B.1-B.13 text-level result rows, including
  stable result ids, metric definitions, parameter tuples, prior-value
  attribution, source locations, construction payload hashes, verifier
  artifacts, result-version status, and recomputed values. The actual
  normalized rows and artifacts remain open.
- Add Appendix B result-version provenance before quoting paper-level
  constructive-math constants: source manuscript version, reported value,
  superseded/current status, update note, attribution, and verifier/Colab
  artifact linkage for revised results such as the uncertainty-inequality
  bound.
- Keep Appendix B.4 uncertainty-inequality claims scoped to validated absence
  boundaries until coefficient/revision artifacts land: the registry now
  validates the source formulation, `[33]` prior-bound rounding (`0.353`
  stated versus `0.3523` rounded), the first-version Hermite-polynomial
  result boundary (`C4 <= 0.3521`, coefficients
  `[0.32925, -0.01159, -8.9216e-5]`, `P(x)/x^2`, and `r_max^2 / (2*pi)`), the
  qualitative similarity/hypothesis claim against `[33]`, and the
  post-first-version revision note (`[18]` at `0.3284`, AlphaEvolve at
  `0.3216`). Actual `[33]` source locators, prior-solution rounding artifacts,
  rounding-audit certificates, coefficient payloads, Hermite/Fourier/root
  certificates, origin-condition certificates, eventual-nonnegative certificates,
  coefficient-comparison artifacts (prior and AlphaEvolve payloads,
  basis-alignment certificate, similarity metric, and hypothesis-source
  artifact), Colab/verifier linkage, comparison-to-`0.3284` certificates, and
  recomputation certificates remain open.
- Keep Appendix B.1-B.3 public labels tied to paper terminology: the registry
  now validates exact paper-facing labels for `B.1`/`C1`, `B.2`/`C2`, and
  `B.3`/`C3`, while treating `autocorrelation_bounds_k*` as internal ids only.
- Keep Appendix B.1-B.3 step-function evidence scoped to summary metadata
  until construction payloads land: the registry now validates the paper's
  interval counts, common domain, sign policy, bound direction, previous
  bound/source, and reported bound for C1-C3. A validated
  `step_function_payload_boundary` also records the required future payload,
  domain/spacing/sign-policy certificate, verifier-artifact, and
  recomputed-bound fields, but the actual step-function payloads and
  recomputation certificates remain open.
- Keep Appendix B.8 distance-ratio claims scoped to metric convention evidence
  until point-set certificates land: the registry now validates the squared
  raw values, square-root-derived ratios, point counts, dimensions, prior
  squared bounds, Figure 12 panel labels, and comparison policy, but not the
  coordinate payloads or all-pairs distance certificates. A
  `witness_certificate_boundary` now records the required future witness
  fields including Figure 12 panel artifact path/hash fields, preserves the
  16-point/2D and 14-point/3D missing-witness rows, and keeps both B.8
  witnesses and panel artifacts explicitly `not_recorded_locally`.
- Keep Appendix B.5 source-problem and construction evidence separated: the
  registry now validates the original paired-function Erdős formulation,
  zero-extension convention, shift-supremum objective, known bounds, `[40]`
  equivalence, and mapping to the normalized `[0,2]` step-function row; the
  `step_function_result_boundary` now validates the paper's Figure 10
  result id, `C5 <= 0.380924` upper bound, prior bounds, normalized-domain
  constraint, shift-objective expression, and required future payload and
  certificate fields. It now keeps the original-formulation mapping
  certificate, `[40]` equivalence-reference artifact, shift-domain certificate,
  payload, value-range certificate, integral-normalization certificate,
  shift-objective certificate, recomputed upper bound, and Figure 10 panel
  artifact explicitly `not_recorded_locally`.
- Keep Appendix B.6 theorem conditions and finite-set witnesses separated:
  the registry now validates the source `C6` sums-and-differences statement,
  sumset/difference-set definitions, `<<`/`>>` notation, known
  `1.14465 <= C6 <= 4/3` bounds, Gyarmati admissibility condition, and
  lower-bound formula. A `finite_set_witness_boundary` now validates the
  paper's `U1` and `U2` witness summaries, set sizes `2003` and `54265`,
  reported lower bounds `1.1479 <= C6` and `1.1584 <= C6`, and required
  future finite-set payload, contains-zero, non-negative, admissibility,
  sumset-cardinality, difference-set-cardinality, max-element,
  lower-bound-formula substitution, and recomputation fields, while the actual
  set payloads, set-algebra certificates, formula-substitution certificates,
  and recomputation certificates remain open.
- Keep Appendix B.7 regular-hexagon packing claims scoped to result-boundary
  evidence until geometry certificates land: the registry now validates the
  unit-regular-hexagon objective, Figure 11 linkage, prior `[29]` values,
  `n = 11` improvement from `3.943` to `3.931`, `n = 12` improvement from
  `4.0` to `3.942`, and required future placement, containment,
  non-overlap, recomputed-side-length, and Figure 11 panel artifact fields.
  The actual placement payloads, geometry certificates, and panel artifacts
  remain open.
- Keep Appendix B.9-B.10 Heilbronn claims scoped to result-boundary evidence
  until point/domain certificates land: the registry now validates the
  unit-area triangle row for `n = 11` with minimum area `> 0.0365`, the
  convex-region rows for `n = 13` and `n = 14` with minimum areas `0.0309`
  and `0.0278`, their prior `[29]` values, Figure 13 panel links, and
  required future point-coordinate, domain, unit-area, convexity, all-triples
  area, recomputed-minimum-area, and Figure 13 panel artifact path/hash
  fields, with panel artifacts explicitly `not_recorded_locally`. The actual
  coordinate/domain payloads, area certificates, and panel artifacts remain
  open.
- Keep Appendix B.11 kissing-number claims scoped to lemma-boundary evidence
  until the 593-vector certificate lands: the registry now validates the
  dimension-11 target, prior lower bound `592`, reported lower bound `593`,
  nonzero integral-coordinate witness requirements, max-norm versus
  minimum-pairwise-distance condition, Lemma 1 transformation to sphere
  centers, and required future vector, separate max-norm,
  minimum-pairwise-distance, lemma-applicability, transformed-center, and
  recomputed-lower-bound fields. The actual vector payload, max-norm proof,
  minimum-pairwise-distance proof, and exact proof certificates remain open.
- Keep Appendix B.12-B.13 sum-of-radii packing claims scoped to
  result-boundary evidence until placement certificates land: the registry now
  validates `n = 26` and `n = 32` unit-square rows, the `n = 21` perimeter-4
  rectangle row, prior and reported sums of radii, Figure 14 panel links, the
  B.13 caption display `sum_of_radii >= 2.365` versus text value `2.3658`,
  and required future placement, containment, non-overlap, perimeter,
  recomputed-sum, container-artifact, and Figure 14 panel artifact path/hash
  fields. It also preserves the Figure 5 display `2.6340 -> 2.6358` as a
  separate precision boundary from the Appendix B.12/Figure 14 `2.634` to
  `2.635` strings. The checked-in 26-circle fixture remains explicitly
  smoke-only, and the actual AlphaEvolve container artifacts, placement
  payloads, panel artifacts, exact certificates, source locators,
  canonicalization policy, recomputed sum, and companion Colab link remain
  open.
- Keep paper artifact-role attribution separate from artifact availability:
  `libreevolve.alphaevolve_paper_artifact_roles.v1` now validates the
  AlphaEvolve PDF contribution records for figure creators and companion
  Colab assemblers. `libreevolve.alphaevolve_paper_artifact_linkage.v1` now
  validates the current `not_yet_linked` availability boundary and the digest,
  source-locator, and source-to-artifact-map fields required before rendered
  figure artifacts or notebook/export artifacts can be claimed.
- Keep AlphaEvolve source-PDF versioning explicit:
  `libreevolve.alphaevolve_source_pdf_version.v1` now validates the cached
  `2506.13131` PDF manifest row against the audited first-page header
  `arXiv:2506.13131v1 [cs.AI] 16 Jun 2025`, including arXiv id, version,
  category, posted date, floating and versioned URLs, expected header page,
  local byte count, SHA-256 digest, and the policy that claim audits must name
  the source version. The paper-manifest gate validates this built-in record
  and the committed `papers/source_versions.json` companion manifest, which
  emits the `2506.13131v1` source-version row and links it to docs/TODO claim
  surfaces while keeping the legacy CSV/JSON download manifests as PDF cache
  ledgers.
- Keep paper-cache row identity proven before version/rights evidence:
  `libreevolve.tools.paper_manifest` now validates that arXiv PDF/abs URLs
  contain a source id matching the manifest `id`, and that every local PDF
  filename begins with the manifest id before any `__` title suffix. Non-arXiv
  slug rows use the same filename source-prefix rule. The committed
  `papers/row_identity.json` companion manifest emits those derived source
  identities for all 24 cache rows and links the AlphaEvolve row to
  `papers/source_versions.json`. This prevents base id/URL/file drift while
  keeping source-rights metadata as separate follow-on work.
- Keep cached source-PDF rights separate from project licensing:
  `libreevolve.alphaevolve_source_pdf_rights.v1` now validates the AlphaEvolve
  cached PDF page 1 rights statement `© 2025 Google DeepMind. All rights
  reserved`, rights holder/year, source page/location, manifest row hash/bytes,
  and boundaries separating third-party paper-source rights from LibreEvolve's
  MIT license and the companion repository's Apache/CC licensing. The paper-
  manifest gate validates `papers/source_rights.json` against the current
  cached PDF text; that companion manifest links to `papers/row_identity.json`
  and records reproduction-policy requirements for excerpts, tables, figures,
  quotes, and appendix claims.
- Keep AlphaEvolve bibliography evidence grounded in source markers:
  `libreevolve.alphaevolve_references_section.v1` now validates that the
  cached PDF References section spans pages 23-32, includes contiguous
  reference ids `[1]` through `[120]`, preserves page-by-page marker ranges,
  and contains selected source anchor phrases. The paper-manifest gate checks
  those markers against the current cached PDF text. The committed
  `papers/references.json` companion manifest adds normalized rows for all
  120 references, including the reference 120 continuation on page 33, raw
  citation text, author/title/venue/year fields, DOI/URL/arXiv fields where
  detected, local-cache linkage, and citation-use categories. Per-claim
  citation links remain scoped separately from the normalized bibliography
  table.
- Keep companion Colab source evidence separate from local generated exports:
  `libreevolve.alphaevolve_companion_colab_source.v1` now validates the pinned
  `google-deepmind/alphaevolve_results` commit, `mathematical_results.ipynb`
  raw/Colab URLs, SHA-256 digest, byte count, nbformat, cell count,
  readability status, matrix/constructive-math claim mappings,
  improved-results-only selection policy, matched-result exclusions,
  AlphaEvolve runtime-code absence, and the companion repository's
  Apache-2.0/CC-BY-4.0 license and disclaimer boundary.
  `papers/companion_sources.json` now emits this committed external source row,
  docs/TODO claim-surface links, and local-cache policy, and the paper-manifest
  gate validates it. Companion selection-scope rows now distinguish included
  improved-over-SOTA results from matched-but-not-outperformed companion
  absences while preserving verifier-code availability and AlphaEvolve runtime-
  code absence; matrix result/headline reports validate that scope for the
  `mm_4x4x4` companion claim. Companion artifact-rights rows now attach to
  generated matrix artifact reports and inventories, separating local generated
  artifacts from copied/adapted companion notebook code, verifier code, or
  construction data with Apache-2.0 / CC-BY-4.0 / local-project reuse policy,
  AS-IS disclaimer, non-official-product, and non-endorsement boundaries. Local
  generated LibreEvolve Colab-equivalent exports and deeper per-cell claim
  spans remain open.
- Keep follow-on AlphaEvolve mathematical-discovery sources separate from the
  original `2506.13131` specification: `libreevolve.alphaevolve_follow_on_math_source.v1`
  now validates arXiv `2511.02864v3`, the 2025-12-22 revision date, the
  `Mathematical exploration and discovery at scale` title/author surface, and
  the pinned `google-deepmind/alphaevolve_repository_of_problems` snapshot at
  commit `bfd224d0e7763f89eb4a8efe93ac126091f85ed9`. It records the README
  digest, live-repository policy, declared 67-problem count, many-but-not-all
  notebook coverage, prompt/verifier/initial/final artifact kinds, runtime-code
  absence, source-use licenses, and citation boundary.
  `papers/follow_on_sources.json` now emits the committed follow-on source row
  with docs/TODO claim-surface links and an explicit no-cache policy. Cached
  PDF rows, per-problem inventory, numbered-page reconciliation, notebook
  artifact hashes, and Appendix B claim mappings remain open.
- Keep follow-on problem-repository rights separate from the original PDF,
  `alphaevolve_results`, and LibreEvolve licensing:
  `papers/follow_on_repository_rights.json` now records the pinned repository's
  citation/BibTeX requirement, Google LLC copyright, Apache-2.0 software /
  CC-BY-4.0 materials split, artifact-type license mapping, AS-IS and
  non-official-product disclaimers, Gómez-Serrano/Tao role attribution, Problem
  65's official IMO origin, docs/TODO claim-surface links, and reuse policy for
  copied source material versus generated local artifacts.
- Keep follow-on problem-repository runtime availability scoped:
  `papers/follow_on_runtime_absence.json` now records the pinned repository
  README/tree evidence for 28 notebooks, including paths, Git blob ids, byte
  counts, artifact-kind flags, explicit `alphaevolve_runtime_available: false`,
  verifier-versus-runtime classification, docs/TODO claim-surface links, and
  the source phrase that the repository does not contain the code to run
  AlphaEvolve. It treats notebooks as prompts/verifiers/inputs/outputs around
  completed experiments, not runnable AlphaEvolve implementation artifacts;
  per-problem notebook mapping, SHA-256 notebook inventory, and cell-level
  artifact verification remain open.
- Keep Tao follow-on blog claims secondary to pinned artifacts:
  `papers/follow_on_tao_blog.json` now records the canonical WordPress URL,
  post id/date/modified metadata, retrieval hashes, linked arXiv/repository/
  tool URLs, claim categories, source-line spans, docs/TODO claim-surface
  links, and the policy that blog commentary does not become unqualified
  AlphaEvolve specification or implementation-parity evidence without backing
  paper, repository, notebook, verifier, or proof artifacts.
- Keep theoretical-CS proof-element applications separate from original spec
  parity: `papers/theoretical_cs_sources.json` now records the September 30,
  2025 Google Research article, arXiv `2509.18057v7`, cached PDF metadata,
  MAX-k-CUT gadget, random-graph/Ramanujan, and metric-TSP application rows,
  lifting-framework and final-brute-force-verification boundaries, and
  docs/TODO claim-surface links. Graph/gadget artifacts, AlphaEvolve search
  code, verifier code, original brute-force verifier provenance, and local
  graph-certification benchmarks remain open before roadmap claims can treat
  this source as implemented benchmark parity.
- Keep official DeepMind announcement claims separated from white-paper spec
  parity: `papers/official_deepmind_blog.json` now records the May 14, 2025
  blog URL/date/title/team, retrieval hash, white-paper and Colab outbound
  links, Early Access form link, claim ids, blog-versus-paper variants such as
  `32.5%` FlashAttention and weeks-to-days kernel work, and blog
  acknowledgement/illustration roles. Reconciliation to paper sections, Colab
  artifacts, rendered artifacts, and reproduced LibreEvolve evidence remains
  open before announcement wording can be treated as audited implementation
  parity.
- Keep paper-index backlog traceability explicit: `validate_paper_manifest()`
  now validates the `papers/README.md` TODO coverage table for exact manifest
  row coverage, duplicate/extra rows, safe active/completed `docs/todo/`
  paths, active open TODO blocks for each paper id, source-specific completed
  checklist evidence, and rejection of grouped labels until a grouped-label
  taxonomy exists. This is backlog-link validation, not full semantic proof of
  every implementation-status sentence.
- Keep active TODO prose internally consistent: `validate_paper_manifest()`
  now rejects manifest-id-scoped stale absence wording such as
  `no source-specific README TODO` when the target active ledger already has
  an open TODO block for that paper id. The check is intentionally phrase-
  family scoped, so broader paraphrases remain a review/future-pattern task.
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
  unspecified `p` cutoff.
  `libreevolve.alphaevolve_appendix_a_matrix_excluded_target_curation_boundary.v1`
  now validates the current `not_recorded_locally` boundary and required
  future fields for excluded target ids, dimensions, exclusion class/reason,
  source basis, rough-rule and `p`-cutoff relations, symmetry-equivalence
  status, local attempt/resource-frontier refs, artifact paths, and hashes.
  `appendix_a_matrix_excluded_target_curation_boundary_from_records()` builds
  recorded boundaries from supplied excluded-target justifications over a
  declared scope. Explicit broad non-equivalent excluded-target justifications
  remain open.
- Keep Appendix A best-known-rank citation claims scoped:
  `libreevolve.alphaevolve_appendix_a_matrix_baseline_citation_boundary.v1`
  now validates the current `not_recorded_locally` boundary and required
  future per-target fields for cited reference id, source table/page, source
  artifact path/hash, applicability caveats, field/characteristic scope, and
  report-visible baseline-source refs.
  `appendix_a_matrix_baseline_citation_boundary_from_citations()` builds
  recorded boundaries from supplied citation rows and validates registry rank,
  dimension, target-id, and report-source-ref linkage. Real per-target cited
  source metadata still needs to be collected and emitted.
- Keep matrix target-scaling claims scoped to paper-source frontier evidence:
  `libreevolve.alphaevolve_appendix_a_matrix_resource_frontier.v1` now
  validates the Appendix A page 34 boundary for sizes beyond `<5,5,5>`, 1000
  random seeds, single-GPU evaluators, frequent OOM, and further-optimization
  need. `libreevolve.alphaevolve_appendix_a_matrix_local_resource_frontier.v1`
  now validates the local absence/readiness boundary and required fields for
  future attempted target sizes, measured GPU memory, OOM artifacts,
  reduced-seed tradeoffs, and exclusion rationale. Actual local scaling runs
  remain open.
  `appendix_a_matrix_local_resource_frontier_from_attempts()` builds an
  `attempts_recorded` boundary from supplied local attempt diagnostics without
  claiming the full paper frontier has been reproduced.
- Keep matrix starting-algorithm wording scoped to boundary validation rather
  than emitted Section 3.1 provenance:
  `libreevolve.matrix_baseline_component_runtime_boundary.v1` now validates
  the current `not_emitted_by_local_runner` boundary and required future
  emitted-record fields for run/target ids, baseline program ids,
  initializer/reconstruction-loss/optimizer component records, Adam optimizer
  name/version/config, mutable component scopes, fixed component hashes,
  generation-0 metrics, mutation lineage, matrix-result refs, artifact paths,
  and artifact hashes. `matrix_baseline_component_runtime_boundary_from_components()`
  builds emitted records from component inventories and validates top-level
  ref, mutable-scope, and fixed-hash linkage. Local benchmark runners still
  need to emit those baseline component records.
- Keep matrix repeated-seed wording scoped to result reports versus executed
  cascade traces: `libreevolve.matrix_cascade_run_runtime_boundary.v1` now
  validates the current `not_emitted_by_local_runner` boundary and emitted
  per-seed records for run/target/seed ids, cascade ids and versions, stage
  traces with threshold/rank/exactness/stop diagnostics, accepted final rank,
  candidate and matrix-result refs, artifact paths, and artifact hashes.
  `matrix_cascade_run_runtime_boundary_from_matrix_result()` builds emitted
  records from matrix result seed rows plus per-seed stage traces and validates
  final-stage/result-row linkage plus best-rank, hit-count, and hit-fraction
  aggregation from emitted seed records. Local benchmark runners still need to
  emit those AlphaEvolve Section 3.1-style matrix cascade traces automatically.
- Keep matrix near-integrality wording scoped to evidence validation rather
  than executed search parity: `libreevolve.matrix_near_integrality_evidence.v1`
  now validates declared prompt instructions, integer/half-integer nearest
  rounding policy, raw-versus-rounded coefficient diagnostics, rounding-error
  consistency, and exactness-certificate links.
  `libreevolve.matrix_near_integrality_runtime_boundary.v1` now validates the
  current `not_emitted_by_local_runner` boundary and emitted records for
  run/target/candidate ids, seeds, prompt hashes/instructions, raw and rounded
  coefficients, rounding error, exactness-certificate links, matrix-result
  refs, artifact paths, and artifact hashes.
  `matrix_near_integrality_runtime_boundary_from_evidence()` builds emitted
  runtime rows from validated near-integrality evidence and validation links
  each row back to the nested target, prompt, candidate, rounding, and
  certificate evidence. Local benchmark runners still need to emit those
  records during matrix search.
- Keep matrix scalar-field wording scoped to evidence validation rather than
  emitted complex result parity: `libreevolve.matrix_scalar_field_evidence.v1`
  now validates declared real, complex, finite-field, and any-field
  applicability, field characteristic, exact coefficient representation,
  complex component domains, finite-field characteristic/order, paper complex
  target caveats, and certificate scope.
  `libreevolve.matrix_scalar_field_runtime_boundary.v1` now validates the
  current `not_emitted_by_local_runner` boundary and emitted records for
  run/target/candidate ids, seeds, scalar field, characteristic,
  applicability, coefficient representation, algorithm refs, certificate refs,
  matrix-result refs, artifact paths, and artifact hashes.
  `matrix_scalar_field_runtime_boundary_from_evidence()` builds an emitted
  runtime row from validated scalar-field evidence and validation links it back
  to the nested target, field claim, applicability, coefficient
  representation, algorithm, and certificate evidence. Local benchmark runners
  still need to emit exact complex decomposition/certificate artifacts for
  those claims.
- Keep matrix tensor-rank wording scoped to evidence validation rather than
  emitted tensor-rank parity: `libreevolve.matrix_tensor_rank_evidence.v1` now
  validates algorithm kind, tensor-identity certificate scope, recursive
  applicability, target-tensor and exactness-certificate links, and source-note
  caveats for non-tensor multiplication algorithms.
  `libreevolve.matrix_tensor_rank_runtime_boundary.v1` now validates the
  current `not_emitted_by_local_runner` boundary and emitted records for
  run/target/candidate ids, seeds, algorithm kind, rank, recursive
  applicability, certificate scope, tensor-identity status, target-tensor refs,
  exactness-certificate refs, matrix-result refs, artifact paths, and artifact
  hashes. `matrix_tensor_rank_runtime_boundary_from_evidence()` builds an
  emitted runtime row from validated tensor-rank evidence and validation links
  it back to the nested target, rank claim, recursive-applicability,
  tensor-identity, target-tensor, and certificate evidence. Local benchmark
  runners still need to emit those target-tensor/certificate and
  footnote-caveat artifacts.
- Keep Strassen baseline claims scoped to one pinned baseline artifact:
  `validate_strassen_2x2_publication_bundle()` now validates the checked-in
  `mm_2x2x2` Strassen bundle under
  `libreevolve/problems/benchmarks/artifacts/strassen_2x2_publication_bundle/`,
  including report/inventory file hashes and regeneration parity against fresh
  `write_strassen_2x2_publication_bundle()` output. This remains baseline
  evidence only; Appendix A suite-wide discovered decompositions, certificates,
  and notebook exports remain open.
  `libreevolve.matrix_suite_publication_artifact_boundary.v1` now validates the
  current `not_generated_locally` boundary and required future fields for one
  generated artifact record per registered Appendix A target: target tensors,
  algorithms, coefficient data, exactness certificates, notebooks, per-seed
  reports, embedded matrix-result reports, artifact inventories,
  publication-bundle refs, artifact paths, and hashes.
  `matrix_suite_publication_artifact_boundary_from_artifacts()` builds a
  generated boundary from one record per registered target, and validation
  checks nested matrix-result report linkage. Local generation of the full
  Appendix A suite artifacts remains open.
- Keep matrix sweep-space wording scoped to evidence validation rather than
  executed Figure 9 workflow parity: `libreevolve.matrix_sweep_space_evidence.v1`
  now validates declared `sweep` function identity, user-provided `hyper`
  library provenance, hyperparameter ranges, sampled configuration rows with
  losses/ranks, winning configuration identity, and final decomposition plus
  exactness-certificate links.
  `libreevolve.matrix_sweep_space_runtime_boundary.v1` now validates the
  current `not_emitted_by_local_runner` boundary and emitted records for
  run/target/candidate ids, seeds, search-program refs, sweep function
  identity, hyper-library and hyperparameter declarations, sampled
  configurations, winning configuration, certificate/decomposition refs,
  matrix-result refs, artifact paths, and artifact hashes.
  `matrix_sweep_space_runtime_boundary_from_evidence()` builds an emitted
  runtime row from validated sweep-space evidence and validation links it back
  to the nested target, search program, `sweep` function, hyper-library,
  hyperparameters, sampled configurations, winner, and selected certificate/
  decomposition evidence. Local benchmark runners still need to emit those
  records during matrix search.
- Connect real compiler/hardware/kernel/scheduling fixtures to
  `libreevolve.systems_result_report.v1`, with separate optimization,
  held-out/generalization, and reference-correctness gates plus artifacts that
  distinguish loop feedback from generalization, deployment, or independent
  certification evidence. Ready reports require `claim_calibration` records
  that map finite metrics to Section 3.3-style claim ids with units,
  denominators, baselines, aggregation windows, deployment/runtime/synthesis
  context, and explicit metric/artifact/source refs, plus
  `application_provenance` records that link ready practical claims to
  application owners/advisors, domain reviewers, validation or data owners,
  production approvers, approval state, artifact references, and
  local-benchmark-versus-production boundary text. Ready scheduling reports
  also require `scheduling_formulation` records for vector-bin-packing setup,
  CPU/memory dimensions, workload/capacity snapshots, stranded-resource
  objective, feature mapping, simulator hashes, and artifact refs, plus
  `scheduling_safety` records for feasible candidate-set source, ranking-only
  scope, simulator/admission/placement boundaries, resource invariants, and
  safety artifact refs. Ready scheduling reports also require
  `scheduling_deployment_readiness` records for interpretable heuristic
  structure, operator/debug review, predictability checks, deployment
  ergonomics, rollout-risk controls, and less-interpretable learned-policy
  comparison. Real scheduling resource recovery, kernel/training-time speedup,
  RTL PPA, and compiler speedup fixtures still need to populate those records.
- Add hardware-adoption evidence for TPU RTL-style reports before claiming
  Section 3.3.3 parity: RTL-stage workflow placement, standard-Verilog
  trust/adoption rationale, upcoming-chip integration, and time-to-market
  impact in addition to PPA and verification artifacts.
- Add self-improvement evidence boundaries before claiming AlphaEvolve-style
  infrastructure or base-model uplift: component identity, before/after
  measurements, deployment/adoption status, rollback/safety review, provenance
  tying the candidate to LibreEvolve's own execution path, and any
  distillation dataset/training/evaluation artifacts.
- For scheduling fixtures, populate mission-critical deployment-readiness
  evidence beyond generic systems gates: interpretable heuristic structure,
  debuggability and operator review, predictable behavior checks, rollout-risk
  evidence, deployment ergonomics, and comparison against less interpretable
  learned-policy baselines.
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
  metadata, rendered artifact hashes, and report/raw-trace links.
  `figure8_exhibit_from_ablation_report()` can derive the two-panel exhibit
  from a validated equal-budget report plus declared artifacts. No real runner
  produces those reports or rendered exhibit artifacts yet.
- Keep Appendix A Figure 9 matrix-diff exhibit claims scoped to declared
  exhibit validation: `libreevolve.alphaevolve_figure9_matrix_diff_exhibit.v1`
  now validates Figure 9a/9b/9c panel ids, pages 35-37, Figure 4 caption
  linkage, ordered line spans, source-diff/rendered/OCR hashes, semantic
  optimizer/init/noise/clipping/loss/discretization/sweep labels, and links to
  result, sweep-space, certificate, and companion notebook evidence. Rendered
  appendix panel artifacts are still not emitted or checked in.
  `libreevolve.alphaevolve_figure9_matrix_diff_artifact_boundary.v1` now
  validates the current `not_emitted_by_local_report_export` boundary and
  required future fields for panel ids/order/pages, code line spans,
  source-diff excerpts, rendered panel images, OCR text, aggregate panel-set
  artifacts, artifact paths/hashes, and nested Figure 9 exhibit metadata.
  `figure9_matrix_diff_artifact_boundary_from_exhibit()` builds emitted panel
  artifacts from validated Figure 9 exhibit metadata and validation checks
  nested panel linkage. Rendered appendix panel artifacts are still not
  emitted or checked in automatically.
- Keep Figure 4 matrix-discovery exhibit claims scoped to declared exhibit
  validation: `libreevolve.alphaevolve_figure4_matrix_discovery_exhibit.v1`
  now validates the main-text exhibit id, page 11, caption linkage,
  15-mutation count, `mm_4x4x4` rank-48 mapping, left diff outline plus the
  three highlighted right-side excerpt regions, source-diff/rendered-region
  hashes, semantic optimizer/init/loss/sweep coverage, and links to Figure 9,
  result, sweep-space, certificate, and companion notebook evidence. Rendered
  Figure 4 artifacts and accepted-mutation lineage records remain open.
  `libreevolve.alphaevolve_figure4_matrix_discovery_artifact_boundary.v1` now
  validates the current `not_emitted_by_local_report_export` boundary and
  required future fields for rendered Figure 4 image, left diff outline,
  highlighted excerpts, paper text excerpt, region renders, source-diff
  artifacts, accepted 15-mutation lineage, artifact paths/hashes, and nested
  Figure 4 exhibit metadata.
  `figure4_matrix_discovery_artifact_boundary_from_exhibit()` builds emitted
  artifacts from validated Figure 4 exhibit metadata plus supplied accepted
  mutation lineage and validation checks nested exhibit linkage. Rendered
  Figure 4 artifacts and accepted-mutation lineage records remain open.
- Keep matrix headline historicity claims scoped to declared evidence:
  `libreevolve.matrix_headline_historicity_evidence.v1` now validates the
  `mm_4x4x4` complex rank-48 headline against dimensions, rank, 48 scalar
  multiplications, characteristic-zero scope, 56-year first-below-49 flags,
  recursive Strassen rank-49 comparison, finite-field-only Fawzi rank-47 caveat,
  source refs, and links to result, scalar-field, tensor-rank, Figure 4,
  Figure 9, and companion Colab evidence. The runner still does not emit the
  headline record or linked decomposition/certificate/source artifacts.
  `libreevolve.matrix_headline_historicity_runtime_boundary.v1` now validates
  the current `not_emitted_by_local_runner` boundary and emitted records for
  run/target/candidate ids, dimensions, headline rank/field values, source
  refs, prior comparisons, evidence links, matrix-result refs, artifact paths,
  and artifact hashes.
  `matrix_headline_historicity_runtime_boundary_from_evidence()` builds an
  emitted runtime row from validated headline evidence and validation links it
  back to nested target, dimensions, headline claim, source refs, prior
  comparisons, evidence links, and matrix-result provenance.
- Keep matrix outcome claims scoped to named target subsets:
  `libreevolve.alphaevolve_matrix_subset_scope.v1` now validates
  `appendix_a_full`, `main_text_mnp_le_5`, and `table_2_selected` membership,
  outcome counts, out-of-scope rows, and Table 2/Table 3 source linkage. The
  scoped `m,n,p <= 5` subset has `20` rows with `0` fell behind, while the full
  Appendix A table has `54` rows with `2` fell behind. Runtime reports and
  rendered table artifacts still do not emit those subset-scope records.
  `libreevolve.alphaevolve_matrix_subset_scope_artifact_boundary.v1` now
  records the current `not_emitted_by_local_report_export` boundary and
  required future emitted-artifact fields for subset identity, inclusion
  predicates, source linkage, counts, fell-behind/out-of-scope ids, nested
  subset-scope evidence, artifact paths, and hashes.
  `appendix_a_matrix_subset_scope_artifact_boundary_from_records()` builds
  emitted artifacts from validated subset-scope evidence and validation checks
  nested evidence linkage. Runtime reports and rendered table artifacts still
  need to emit those subset-scope records automatically.
- Keep Appendix A matrix row-note claims scoped to declared evidence:
  `libreevolve.alphaevolve_appendix_a_matrix_row_notes.v1` now validates the
  `mm_4x5x6` concurrent-work note that reference `[49]` also found a rank-90
  algorithm for `<4, 5, 6>`, including source page/table, rank relationship,
  and a non-exclusive-priority docs caveat. Runtime reports and rendered table
  artifacts still do not emit that row-note caveat.
  `libreevolve.alphaevolve_appendix_a_matrix_row_note_artifact_boundary.v1`
  now records the current `not_emitted_by_local_report_export` boundary and
  required future emitted-artifact fields for note identity, target/rank/
  reference values, source text, caveat flags, nested row-note evidence,
  artifact paths, and hashes.
  `appendix_a_matrix_row_note_artifact_boundary_from_records()` builds emitted
  artifacts from validated row-note evidence and validation checks nested
  evidence linkage. Runtime reports and rendered table artifacts still need to
  emit that row-note caveat automatically.
- Keep Table 2/Table 3 matrix-rank claims scoped to declared exhibit evidence:
  `libreevolve.alphaevolve_matrix_rank_table_exhibit.v1` now validates stable
  table ids, selected/full-table membership, row ordering, rank values, outcome
  counts/color semantics, complex-row annotations, concurrent-note linkage,
  rendered/source/OCR artifact hashes, and registry/subset/row-note/Colab
  links. Runtime reports still do not render or emit those table artifacts.
  `libreevolve.alphaevolve_matrix_rank_table_artifact_boundary.v1` now records
  the current `not_emitted_by_local_report_export` boundary and required
  future emitted-artifact fields for table identity, source locations,
  rendered/OCR/source files, artifact paths/hashes, and nested table-exhibit
  evidence. `matrix_rank_table_artifact_boundary_from_exhibit()` builds emitted
  Table 2/Table 3 artifact records from validated exhibit metadata and
  validation checks nested table linkage. Runtime reports still do not render
  or emit those table artifacts.

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
