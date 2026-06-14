# Roadmap

This roadmap reflects the current codebase after ongoing AlphaEvolve-alignment
passes against `papers/2506.13131__AlphaEvolve.pdf`, local docs, the paper
index, and the checked-in tests. It is a practical development plan, not a
promise.

Treat the current-state bullets as a maintained planning summary, not as a
machine-verified proof ledger for every implementation phrase. The code, tests,
runtime artifacts, paper sidecars, and active TODO ledgers remain the
authoritative evidence; semantic claim-by-claim roadmap verification is still
tracked as open documentation work.

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
  seed-source references, and optional
  `problem.codebase_integration_metadata` source-setup records for upstream
  identity, pre-marker hashes, marker-added setup diffs, evaluator-call
  continuity, static-asset source identity, and codebase-scale fixture
  declarations. The checked-in `workspace_math` fixture now supplies a
  smoke-scoped `codebase_integration.yaml` plus
  `source_setup/fixture_lib_v1/` pre-marker Python sources and static-asset
  identity hashes, with
  `papers/existing_codebase_integration_boundary.json` now carrying the
  paper-manifest-validated smoke-source-setup boundary; a real external or
  release-like codebase-scale fixture and independently checkable evidence
  bundle remain required before claiming paper-faithful minimal-change
  existing-codebase integration
- SEARCH/REPLACE diff mutation, including canonical AlphaEvolve fences, and
  configurable full-block/full-code replacement with unknown named block
  targets rejected before partial replacement
- adaptive mutation-mode absence boundary evidence under
  `papers/adaptive_mutation_mode_boundary.json`, preserving the distinction
  between configured run-wide `diff`/`full` prompt/parser support and
  unimplemented per-candidate diff-versus-full selection by code size,
  workspace shape, task shape, failure history, fallback behavior, or
  selection telemetry
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
  dependency scope, runtime-enforced materialized-candidate workspace
  dependency policy for local reads/imports, metric names, per-metric candidate
  path/block-span link candidates, embedded-only problem loading via
  all-`embedded_evaluate` `config.yaml` stages, static local invocation traces
  from `evaluate()` to EVOLVE-block-backed functions when AST evidence is
  present, external-validator stage metric visibility without causal linkage,
  and remaining Figure 3 parity gaps, including default candidate-owned
  evaluator loading, Figure 3 codebase fixture identity, typed eval-input
  contracts beyond JSON-safe config provenance, external `validate.py` still
  being the default outside all-embedded configs, with
  `papers/embedded_evaluator_boundary.json` now carrying the paper-manifest-
  validated absence boundary for build isolation, non-static score causality,
  external-validator causal score linkage, default contract gaps, and
  prompt/response exhibit artifacts
- Figure 3 supervised-learning exhibit boundary evidence under
  `papers/figure3_supervised_exhibit_boundary.json`, preserving the distinction
  between generic embedded-evaluator, prompt-history, candidate-history,
  SEARCH/REPLACE, preamble, prompt-packing, and prompt-example-copy support and
  an unreproduced paper-facing Figure 3 exhibit with exact source,
  assembled-prompt, LLM-output, displayed-score, rendered-hash, and
  run-artifact-link evidence
- AlphaEvolve Figure 1/Figure 2 process-exhibit reports under
  `runtime.history.alphaevolve_process_exhibit_report`, preserving stable
  figure IDs, node/edge-to-component mappings, Figure 2 pseudocode-step
  mappings, artifact cross-links, generated Mermaid/accessibility text
  artifacts, step-stream artifact validation records, strict JSONL row
  summaries, generated candidate semantic traces with durable LLM and
  archive-admission stream rows, hashed source-PDF page text extracts for
  Figure 1/Figure 2, validated current synchronous topology boundary evidence
  linked to `runtime.history.distributed_pipeline_topology_report`,
  validated current inline evaluator-pool boundary evidence,
  component-to-TODO links, and explicit gaps for exact source-diagram
  reproduction, exact source caption/text identity, source diagram text
  identity, diagram node-label source alignment, source figure image/crop
  hashes, visual node coordinates, source edge geometry/routing, Figure 2
  pseudocode line-number maps, Figure 2 line-level pseudocode alignment,
  visual diff/fidelity checks, and full process parity, with
  `papers/process_exhibit_boundary.json` now carrying the manifest-validated
  boundary for exact source-diagram layout reproduction, AlphaEvolve async
  topology implementation, and independent evaluator-pool implementation
- AlphaEvolve Table 1 capability-comparison exhibit reports under
  `runtime.history.alphaevolve_table1_capability_exhibit_report`, preserving a
  stable table id, eight ordered row ids, source page/caption location,
  source-cell text, row-to-report/TODO evidence mappings, generated
  Markdown/accessibility artifacts with hashes, and explicit false readiness
  for individual Table 1 capability-row parity, with
  `papers/table1_capability_exhibit_boundary.json` preserving that
  table-provenance-only boundary
- codebase-scale benchmark boundary reports under
  `runtime.history.codebase_scale_benchmark_report`, measuring retained
  program file/line scale, generated-candidate counts, parent-relative changed
  files/lines, multi-file and hundreds-line threshold evidence, and explicit
  false readiness for realistic codebase fixtures, arbitrary-language/build
  runners, cross-file dependency-edit evidence, coupled multi-component edit
  evidence, dependency-graph validation, non-Python fixtures, evaluator
  workload budgets, retained artifact hashes, reproducibility bundles,
  long-horizon quality progress, valid/admitted/retained-rate curves, and
  Table 1 code-scale parity, with
  `papers/codebase_scale_benchmark_boundary.json` preserving the paper-facing
  absence boundary
- distributed-pipeline topology boundary reports under
  `runtime.history.distributed_pipeline_topology_report`, naming the current
  single-process controller, in-process database, configured LLM sampler
  backends, local evaluator nodes, zero queues, blocking dependency edges, and
  runtime-budget linkage, with
  `papers/distributed_pipeline_topology_boundary.json` preserving the
  paper-facing absence boundary while keeping AlphaEvolve async pipeline parity
  explicitly false, including missing async task/coroutine identities,
  dependency wait-event telemetry, worker lifecycle/liveness records,
  scheduler-state snapshots, deterministic async completion/admission order,
  queue backpressure, and pending-work checkpoints
- runtime cascade summaries that aggregate configured-stage promotion,
  attrition, threshold failures, work counters, bounded candidate-stage
  history cross-links, denominator-policy boundaries, and explicit
  claim-readiness limitations under `runtime.history.evaluation_cascade_report`,
  including `stage_evidence_summary` counts for configured roles, local stage
  source refs/hashes when available, runtime samples, main-test exposure, and
  early pruning, with `papers/evaluation_cascade_boundary.json` now carrying
  the paper-manifest-validated absence boundary for stage difficulty/test-set
  identities, benchmark seed/sample policy, candidate transition matrices,
  promotion-decision rule attribution, next-stage exposure linkage,
  transition-denominator reconciliation, and cost-savings evidence
- cascade hypothesis-test boundary reports under
  `runtime.history.cascade_hypothesis_test_policy_report`, naming configured
  or fallback-inferred small-scale-filter/main-test roles, deterministic threshold/artifact
  promotion, and opt-in `one_sided_lower_confidence_bound` repeated-sample
  gates with confidence-bound, p-value, sequential early-stop, and
  configured false-promotion/false-rejection budget evidence, plus
  `binomial_success_rate` repeated-seed success-rate gates with Wilson
  lower-bound evidence, with `papers/cascade_hypothesis_test_boundary.json`
  preserving the runtime-policy-only boundary
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
  validator-versus-feedback discard cases, `oracle_source_evidence` source
  refs/hashes when available, and an explicit limitation for independent
  multi-oracle arbitration, with
  `papers/evaluator_oracle_boundary.json` now carrying the paper-manifest-
  validated absence boundary for reference/statistical oracles, benchmark
  sufficiency proof, candidate-level oracle lineage, per-generation feedback
  traces, primary evaluator contract proof, independent disagreement outcomes,
  and cross-run oracle tables
- proposal lifecycle reports under
  `runtime.history.proposal_lifecycle_report`, merging generated-candidate
  history with failure records to show backend/call summaries, mutation hashes,
  evaluator validity, archive admission/rejection, rejection reasons,
  execution-filtered counts, bounded failure-memory linkage, and explicit
  limitations for independent false-acceptance/false-rejection audits, with
  `papers/proposal_lifecycle_audit_boundary.json` now carrying the
  paper-manifest-validated absence boundary for independent rejudge,
  reference/statistical-oracle audit, sampled audit denominators, candidate-
  family filter rates, beyond-initial-pool novelty audits, cross-run proposal
  tables, semantic failed-proposal retrieval, and audited error rates
- incorrect-suggestion audit reports under
  `runtime.history.incorrect_suggestion_audit_report`, derived from proposal
  lifecycle records and recording local accepted/rejected/execution-filtered
  counts, invalid-evaluation and archive-rejection counts, local filter rates,
  bounded proposal audit rows, explicit zero-coverage independent rejudge
  summaries, and explicit false readiness for independent rejudge,
  reference/statistical-oracle sufficiency, sampled audit-denominator policy,
  candidate-family filter rates, beyond-initial-pool novelty audit, cross-run
  proposal tables, semantic failed-proposal retrieval, and audited false-
  acceptance/false-rejection rates, with
  `papers/incorrect_suggestion_audit_boundary.json` preserving the
  paper-facing independent-audit absence boundary and
  `papers/failure_memory_boundary.json` preserving the run-local failure
  diagnostics versus durable cross-run/semantic failed-proposal memory,
  replayable failed-mutation payload, failure-aware sampling, and cross-run
  failure-index migration boundary
- single-run sample-efficiency reports under
  `runtime.history.sample_efficiency_report`, derived from proposal lifecycle
  evidence and counting generated proposals, evaluated/valid/admitted
  candidates, retained elites, sampling-eligible candidates, logical LLM
  samples, and a bounded best-score cumulative curve while
  `papers/sample_efficiency_boundary.json` keeps run seed/evaluator identity,
  fixed compute budgets, target-definition provenance, target-attainment
  curves, target-hit indexes, replicate statistics, matched-budget run groups,
  thousands-scale, repeated-sampling, and model-size comparison evidence open
- repeated-sampling baseline boundary reports under
  `runtime.history.repeated_sampling_baseline_report`, linking observed sample
  counts to an explicit `No evolution` comparator absence boundary, with
  `papers/repeated_sampling_baseline_boundary.json` preserving the missing
  fixed prompt/model/request-parameter/seed/evaluator controls, fixed LLM-call
  budgets, candidate-validation parity, sample-index alignment, target
  metric/threshold linkage, disabled feedback/selection proof, budget parity,
  target-progress curves, comparator artifact hashes, and linked evolutionary
  comparator runs
- opt-in evaluator artifact copy-out from temporary candidate workspaces with
  hashes, limits, and text redaction metadata
- validator subprocess environment allowlisting, persisted stdout/stderr
  redaction, and best-effort timeout process-tree cleanup
- MAP-Elites plus configurable ring-topology island migration, defaulting to
  five islands, with validated `runtime.history.archive_state.topology_policy`
  evidence that keeps adaptive island counts, non-ring topologies, and
  AlphaEvolve-identical policy readiness false
- metric direction/bounds normalization for declared evaluator metrics and
  feedback-sourced objective metrics, averaged into archive selection score
- a prompt sampler that renders context files, compact stage feedback,
  proposal metadata, and prompt-size/section-budget diagnostics
- recursive problem-local context ingestion for `.txt`, `.md`, `.py`, and
  `.pdf` files with context-manifest include/exclude rules, source hashes,
  extraction spans, and bounded prompt rendering
- a local prompt-program database with prompt selection, lineage, UCB-style
  prompt-arm selection over normalized `absolute` or `improvement` child-score
  rewards, and optional interval-based LLM template mutation; configured and
  evolved templates are validated for known placeholders, compatible format
  specs, and parent-placeholder retention during mutation; configured prompt
  templates can also use weighted `[[prompt:name]]` stochastic formatting
  markers backed by `prompt_format_options`
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
  standalone schema completeness, user-authored source identity, prompt/config
  content identity, cross-field consistency validation, replay preflight,
  arbitrary-validator/build-system task-spec parity, and user-authored
  full-parity task packages open, with
  `papers/task_specification_boundary.json` preserving the paper-facing
  runtime-artifact-resolution-only boundary
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
  present, and the current primary-prompt provider-placement report boundary.
  Configured backend `llm_prompt_roles` can now send structured provider
  instructions and retain hash-only `prompt_role_policy` telemetry, but that
  telemetry is not yet joined into this primary-prompt evidence report
- runtime stochastic-formatting distribution provenance under
  `runtime.history.stochastic_prompt_format_distribution_report`, linking
  generated prompt ids to `[[prompt:name]]` option sets, normalized
  probabilities, selected alternative hashes/indexes, weight-source or
  prompt-context override source, inline/effective-config boundary, and the
  run-local framework RNG replay boundary while keeping separate config-file
  source attribution and human-authorship certification out of parity claims
  (`papers/runtime_rng_replay_boundary.json` keeps the framework RNG restore
  claim separate from full resumed sampling replay)
- runtime initial-program idea provenance reports under
  `runtime.history.initial_program_idea_provenance_report`, linking optional
  seed idea-origin metadata and seed variant ids from `problem.seed_sources` to
  generation-0 history rows; `papers/initial_program_seed_variant_matrix.json`
  now records design-level simple/random/researcher/stochastic/evolutionary
  seed-variant comparison axes while leaving executed equal-budget seed-variant
  result tables, exact rendered prompt digests, prompt-history spans, seed
  workspace hash linkage, replicate protocols, prompt-context linkage, and
  human contribution signoff open, with
  `papers/initial_program_idea_provenance_boundary.json` preserving the
  paper-facing metadata-contract-only boundary
- configurable initial-program validity policy with
  `runtime.history.initial_program_validity_report`, preserving permissive
  invalid generation-0 baselines by default while `alphaevolve_strict` stops
  before mutation with `invalid_initial_programs` when any selected seed is not
  evaluator-valid or lacks declared metrics, with the `embedded_evaluate_math`
  smoke fixture now exercising a claim-ready strict CLI startup path and
  `papers/initial_program_validity_boundary.json` preserving the paper-facing
  strict-policy-available boundary while multi-seed, provider-startup, matrix,
  constructive-math, and optimization-pressure-seed exclusion evidence remains
  open
- optional problem-formulation metadata under `formulation.yaml` or direct
  `Problem.formulation_metadata`, normalized into
  `problem.formulation_metadata` and summarized by
  `runtime.history.problem_formulation_provenance_report` for expert
  contributor roles, problem origin, formulation notes, objective/evaluator
  rationale, parameter-scope decisions, background refs, and review/signoff
  readiness, with `papers/problem_formulation_provenance_boundary.json`
  preserving the paper-facing metadata-contract-only boundary while
  expert/owner identity, evaluator/result artifact linkage, signoff versions,
  background-reference artifacts, anti-gaming review, and paper certification
  rows remain open
- benchmark-fixture readiness reports under
  `runtime.history.benchmark_fixture_readiness_report`, joining startup
  problem metadata to the example-scope registry and preserving explicit false
  readiness for smoke fixtures, missing repeated-seed protocols, missing
  SOTA/target baselines, missing fixture-emitted result artifacts, and missing
  anti-gaming negative-fixture evidence, with
  `papers/benchmark_fixture_readiness_boundary.json` preserving the
  paper-facing smoke-fixture readiness boundary
- optional external feedback metadata under `collaborator_feedback.yaml` or
  direct `Problem.collaborator_feedback_metadata`, normalized into
  `problem.collaborator_feedback_metadata` and summarized by
  `runtime.history.collaborator_feedback_provenance_report` for early-user or
  collaborator cohorts, feedback event ids, affected workflow areas,
  change-artifact links, validation outcomes, privacy/redaction policy, and
  robustness/versatility claim readiness, with
  `papers/collaborator_feedback_provenance_boundary.json` preserving the
  paper-facing metadata-contract-only boundary while cohort coverage, feedback
  source artifacts, code/docs diff links, validation reruns, privacy/redaction
  artifacts, review/signoff versions, follow-up, and claim-to-feedback traces
  remain open
- optional acknowledgement metadata under `acknowledgements.yaml` or direct
  `Problem.acknowledgement_metadata`, normalized into
  `problem.acknowledgement_metadata` and summarized by
  `runtime.history.acknowledgement_role_provenance_report` for white-paper
  review, early exploration, support/advice, practical-application management
  advice, application review, application-specific advice, source locators,
  privacy/redaction policy, and review/signoff readiness; the
  `matrix_multiplication` example carries a reviewed AlphaEvolve pages 21-22
  fixture and a manifest regression for the claim-ready acknowledgement-role
  boundary, with `papers/acknowledgement_role_provenance_boundary.json`
  preserving that paper-facing scope
- optional publication-author metadata under `paper_authors.yaml` or direct
  `Problem.paper_author_metadata`, normalized into
  `problem.paper_author_metadata` and summarized by
  `runtime.history.paper_author_metadata_report` for equal contributors,
  manuscript writers, paper-input contributors, corresponding authors,
  title-page marker linkage, contact/privacy policy, and review/signoff
  readiness; the `matrix_multiplication` example carries a reviewed
  AlphaEvolve pages 22-23 fixture plus title-page marker linkage and a
  manifest regression for the claim-ready publication-author metadata
  boundary, with `papers/paper_author_metadata_boundary.json` preserving that
  paper-facing scope
- optional title-page affiliation metadata under `title_page.yaml` or direct
  `Problem.title_page_metadata`, normalized into `problem.title_page_metadata`
  and summarized by `runtime.history.title_page_affiliation_report` for
  source-paper affiliation text, footnote marker definitions, author-marker
  mappings, source-rights linkage, privacy/redaction policy, and
  review/signoff readiness; the `matrix_multiplication` example carries a
  reviewed AlphaEvolve page 1 fixture linked to `papers/source_rights.json`
  and a manifest regression for the claim-ready title-page boundary, with
  `papers/title_page_affiliation_boundary.json` preserving that paper-facing
  source-publication scope
- optional system-contribution metadata under `system_contributions.yaml` or
  direct `Problem.system_contribution_metadata`, normalized into
  `problem.system_contribution_metadata` and summarized by
  `runtime.history.system_contribution_provenance_report` for system design,
  project scoping, first-benchmark iteration, final-system, infrastructure,
  code-review, coordination, and supervision role provenance; the
  `matrix_multiplication` example carries a reviewed AlphaEvolve pages 22-23
  fixture and a manifest regression for the claim-ready system-development
  contribution boundary, with
  `papers/system_contribution_provenance_boundary.json` preserving that
  paper-facing scope
- manifest-visible `libreevolve.candidate_language_policy.v1` records that
  declare the current Python-primary text-workspace boundary and explicitly
  mark arbitrary-language/build-system runners as unsupported, while
  preserving metadata-only `candidate_language_runners` and
  `candidate_build_systems` declarations when configured
- local workspace materialization diagnostics with typed
  `CandidateMaterializationError` reasons, bounded paths, casefold collision
  checks, recursive link preflight, and static source-copy hash checks, with
  `papers/workspace_materialization_boundary.json` preserving the absence
  boundary for portable static source identity, bulk directory operations,
  dependency graphs, language/build-runner artifacts, remote/container mounts,
  invalid-workspace fixture rows, and future-surface reason/path stability
- runtime candidate-language runner contract reports under
  `runtime.history.candidate_language_runner_contract_report`, recording the
  current Python subprocess validator runner, non-Python text files as
  workspace-only/no-runner members, unsupported arbitrary-language and
  build-system runner contracts, metadata-only language/build declarations
  plus `runner_declaration_evidence` counts, bounded
  `runner_declaration_workspace_evidence` path-match records against retained
  candidate workspaces, current-Python-runner environment linkage under
  `runner_environment_provenance`, unsupported task-abstraction hooks, and
  exact remaining gaps before
  AlphaEvolve-grade executable language/build parity, with
  `papers/candidate_language_runner_boundary.json` now carrying the
  paper-manifest-validated absence boundary for executable configured
  non-Python runners, language-aware marker grammars, build-system contracts,
  arbitrary-runner environment artifacts, and generated build artifacts
- runtime candidate-abstraction choice reports under
  `runtime.history.candidate_abstraction_choice_report`, recording the current
  code-file-set selection, policy/runner linkage, runtime workspace shape,
  unsupported constructor/search/paired alternatives, with
  `papers/candidate_abstraction_boundary.json` now carrying the
  paper-manifest-validated absence boundary for abstraction rationale,
  per-abstraction APIs, selection policy, abstraction-specific prompts,
  validators, archive descriptor mappings, migration policy, symmetry/bias
  evidence, problem-defined abstraction hooks, paired representations, and
  equal-budget abstraction comparisons, while
  `papers/candidate_abstraction_bias_matrix.json` records a design-level
  abstraction-family bias matrix without executed benchmark results
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
  non-Python language runners when non-Python candidates become supported; the
  current declaration fields are manifest metadata only.
- Add problem-defined candidate abstraction hooks if LibreEvolve should move
  beyond the documented code-file-set divergence from AlphaEvolve's flexible
  solution-abstraction API.
- Extend candidate-abstraction reports beyond the current design matrix with
  benchmark metadata that records why a direct-solution,
  constructor-function, or search-algorithm formulation was chosen for an
  actual problem, which abstraction-specific prompts, validators, archive
  descriptors, and migration policies were used, and how alternatives
  performed under comparable budgets.
- Add language-aware evolve-block marker grammars if non-Python workspace files
  should preserve skeleton regions; the current boundary rejects marker-like
  declarations in non-`.py` files instead of treating them as unmarked full-file
  candidates.
- Add richer workspace fixtures beyond the current `workspace_math` nested
  package, JSON data, and binary static seed asset smoke case.
- Add realistic codebase-scale fixtures, arbitrary-language/build runners,
  evaluator-workload, retained artifact hashes, reproducibility bundles,
  sample-efficiency, model-scale, prompt-context, and multi-metric benchmark
  evidence before claiming AlphaEvolve Table 1 capability parity; the current
  `runtime.history.alphaevolve_table1_capability_exhibit_report` preserves the
  comparison table as provenance, and
  `runtime.history.codebase_scale_benchmark_report` measures current run scale
  without proving each row is satisfied. The committed
  `papers/codebase_scale_benchmark_boundary.json` sidecar keeps that
  Table 1 code-scale absence boundary machine-validated.
- Extend `runtime.history.mutation_operator_boundary_report` beyond the
  current fixed diff/full/file/block/topology parser-surface evidence into
  proposal-level operator-family provenance, task/failure-aware operator
  construction, adaptive operator-family selection, scoring, and benchmark
  telemetry before claiming AlphaEvolve's Section 5 Related Work distinction from
  systems with fixed handwritten mutation or crossover operator sets. The
  committed `papers/mutation_operator_boundary.json` sidecar keeps the current
  fixed-edit-payload boundary machine-validated.
- Extend `runtime.history.prompt_example_copy_report` beyond current built-in
  exact, normalized-region, and example-format skeleton diagnostics into hard
  or configurable acceptance policy, broader semantic/renamed example-copy
  detection, and custom prompt-template example inventories before treating
  concrete prompt examples as fully guarded AlphaEvolve-style current-program
  edit demonstrations. The committed
  `papers/prompt_example_copy_boundary.json` sidecar keeps the current
  built-in-diagnostics-only scope machine-validated.
- Extend `runtime.history.mutation_consistency_report` beyond current
  multi-edit payload inventories, changed file/block/search edit units,
  best-effort Python AST introduced/reference symbols, unresolved-reference
  diagnostics, evaluator taxonomy, and admission links into language-aware
  scope resolution, config/resource dependency models, required-companion-edit
  inference, cross-file dataflow/import resolution, and benchmark-calibrated
  consistency gating. The committed
  `papers/mutation_consistency_boundary.json` sidecar keeps the current
  diagnostic-scan-only scope machine-validated.
- Extend `runtime.history.initial_pool_divergence_report` beyond current
  seed-vs-generated workspace hash, bounded primary-file text distance,
  changed-file summary, and numeric metric L1 evidence into task-specific
  functional artifacts, evaluator-output distance metrics, behavior/output-
  distance metrics, thresholds for substantially different claims,
  benchmark-level discovery-distance telemetry, cross-run discovery-distance
  tables, and syntax/function joint claim gates. The committed
  `papers/initial_pool_divergence_boundary.json` sidecar keeps the current
  syntactic-and-metric-telemetry-only scope machine-validated.
- Extend binary/static candidate handling beyond the current bounded encoded
  static members, verified copy-only static assets, and raw direct-workspace
  byte normalization into richer binary mutation/replay policy.
- Keep topology-operation collision policy and structured materialization-
  failure diagnostics complete as new workspace, language, and build-runner
  edge cases are introduced.
- Extend workspace-candidate resume beyond the current archive-content restore
  bundle to ordered migration-event replay, controller queues, and pending-work
  resume. The committed `papers/archive_event_replay_boundary.json` sidecar
  keeps current snapshot restore plus audit-only archive-event reconciliation
  separate from ordered event-stream restore-engine readiness.

### 2. Strengthen multi-objective search

- Extend the current cross-run paper metric report into persisted benchmark
  bundles and generated CSV/JSON artifacts.
- Extend the current documented hybrid, which averages normalized declared
  metrics for archive ranking, into a first-class multi-objective policy:
  Pareto/frontier primary archive replacement, durable cross-run
  metric-specific optimization, or another tested policy beyond the current
  scalar primary grid plus bounded Pareto and metric-cell retained overlays.
  Current `objective_archive_policy` snapshots carry
  `libreevolve.map_elites_objective_archive_readiness.v1` with those primary
  replacement and durable metric-database surfaces false.
- Extend the current configurable parent/inspiration sampling and run-local
  resurfacing queries beyond score, individual metric excellence, novelty,
  recency, lineage, feedback, and random/mixed policies to persisted
  feedback, lineage-diversity, and novelty indexes. Current generated-candidate
  metadata and `runtime.history.metric_diverse_inspiration_report` now prove
  when a rendered prompt contained inspirations from at least two declared
  metric niches while carrying a `benchmark_policy` boundary with
  `alphaevolve_section_2_4_claim_ready: false`, and
  `libreevolve.metric_diverse_benchmark_comparison_readiness.v1` false
  readiness for benchmark prompt-policy enforcement, cross-run fixtures,
  scalar-only baselines, single-metric baselines, and equal-budget comparison
  reports. `papers/metric_diverse_prompt_boundary.json` preserves this
  prompt-visible-evidence-only boundary for paper-manifest validation.
  `runtime.history.sampling_balance_report` now aggregates
  current-run parent/inspiration strategy decisions, with
  `papers/sampling_balance_boundary.json` preserving the local-counts-only
  boundary. Calibrated exploration/exploitation balance, fallback source-pool
  provenance, selected-program repetition tables, island/cell/metric/lineage/
  descriptor coverage, score-improvement versus diversity effects,
  equal-budget strategy comparisons, and AlphaEvolve-grade database-balance
  policy remain open.
- Extend the current run-local exact-workspace evaluator cache into
  AlphaEvolve-grade duplicate-work memory before treating deterministic
  candidate ids or workspace hashes as durable memory over previously explored
  programs. `runtime.history.duplicate_work_policy_report` now records
  canonical workspace plus evaluator-contract cache-key scope, cache stores,
  cache hits, and no-op cache-hit controller budget events. Durable cross-run
  workspace indexes, durable evaluation-cache storage, resume-spanning cache
  replay, cache invalidation/migration policy, stochastic re-evaluation
  policy, semantic near-duplicate detection, source/output-aware cache
  indexes, and an AlphaEvolve-grade fixed-budget memory claim gate remain
  open. The committed
  `papers/duplicate_work_policy_boundary.json` sidecar keeps the current
  run-local exact-cache scope machine-validated.
- Replace the remaining insertion-time adaptive TF-IDF diversity coordinates
  with evaluator-provided behavior descriptors, a fixed/learned descriptor
  model, or explicit tested rebin/snapshot semantics. Current
  `descriptor_model` snapshots carry
  `libreevolve.map_elites_descriptor_readiness.v1` with those readiness
  surfaces false and overclaim validation. The committed
  `papers/map_elites_descriptor_boundary.json` sidecar keeps this
  insertion-time descriptor snapshot scope machine-validated, while
  `papers/map_elites_illumination_boundary.json` records the source-specific
  MAP-Elites illumination boundary, keeping explicit
  `b(x)`/`f(x)` contracts, `P`/`X` map exports, illumination metrics,
  visualization/lineage artifacts, and paper-domain reproductions out of
  current archive claims.
- Extend the current selected-row `show` archive objective-vector summaries
  and manifest-level metric archive summaries into CLI/report drill-downs for
  metric-specific archives.
- Keep multi-objective archive policy scoped to retained overlays until
  Pareto/frontier replacement becomes the primary archive policy or durable
  cross-run metric-specific optimization lands. The committed
  `papers/objective_archive_boundary.json` sidecar keeps the current
  bounded-overlay and diagnostic-frontier scope machine-validated.

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
  from full-runtime restore bundles; `papers/expensive_evaluation_budget_boundary.json`
  keeps this scoped to local cooperative budgets while accelerator budgets,
  async queue budgets, compute-hour accounting, and pending-work/provider-
  output restore composition remain open.
- Extend paper-facing `libreevolve.llm_budget_report.v1` cooperative
  enforcement snapshots to pending-work queues, provider-output replay, and hard
  cancellation semantics; provider-attempt, token, configured-cost, and retained
  latency limits already feed live resumed-run stop checks. The current
  `papers/llm_budget_policy_boundary.json` sidecar preserves the cooperative
  LLM budget snapshot boundary while keeping async role work queues,
  queued/running pending-work budget state, provider-output replay for budget
  resume, hard provider-cancellation budget state, accelerator/worker lease
  accounting, and experiment-owned quota policy open.
- Emit calibration/ablation runs for LLM feedback graders; the
  `libreevolve.llm_feedback_calibration.v1` report and artifact-inventory
  contracts now validate declared multi-task calibration evidence, but no
  runtime fixture generates those reports yet. The current
  `papers/feedback_calibration_boundary.json` sidecar preserves the
  report-contract boundary while keeping runtime calibration runners, executed
  task-suite results, grader ablations, and independent feedback-quality
  validation open.
- Extend `runtime.history.qualitative_feedback_policy_report` and
  `runtime.history.qualitative_feedback_prompt_history_audit_report` beyond
  criterion/rubric/intent metadata and prompt-history row joins into executed
  calibration/task-suite evidence for hard-to-code properties such as
  simplicity. The current declared-policy boundary is tracked by
  `papers/qualitative_feedback_boundary.json`.
- Add broader statistical hypothesis-test promotion policies for cascades,
  extending the current `one_sided_lower_confidence_bound` plus
  normal-approximation error-budget support and `binomial_success_rate`
  Wilson-bound gates into benchmark-calibrated thresholds and repeated-seed
  matrix/tensor fixtures. The current boundary is tracked by
  `papers/cascade_hypothesis_test_boundary.json`.
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
  evaluator-environment fixtures, automatable-domain boundaries, setup/cost and
  expected discovery-value evidence, manual-to-code transition policy, and
  environment-scaling evidence. The committed
  `papers/automated_evaluator_scope_boundary.json` sidecar preserves the
  current machine-gradeable local evaluator scope while keeping robust
  environment readiness open.
- Extend `runtime.history.programmatic_representation_boundary_report` beyond
  the current executable-code versus natural-language-proposal separation into
  measured hallucination-risk controls, long-horizon step-count evidence, and
  a real AI-Co-Scientist-style natural-language hypothesis stage that can
  bridge into programmatic candidate evaluation. The committed
  `papers/programmatic_representation_boundary.json` sidecar preserves the
  current structural boundary without turning it into those measurement or
  bridge claims.
- Add OS/container-grade validator network isolation and stronger
  sandbox/resource controls beyond the current Python-socket denial option,
  minimal environment, wall-clock budgets, and process-tree cleanup. The
  committed `papers/validator_execution_boundary.json` sidecar preserves the
  current local-subprocess policy evidence without claiming OS/container
  sandboxing or resource quotas.
- Extend evaluator provenance beyond the enforced problem-local dependency
  policy to cover external package/native data access when that becomes part of
  the sandbox/environment contract.
- Preserve complete transitive environment/package provenance for evaluator
  runtime dependencies beyond the current bounded package/version and
  redacted/hash-backed `pip freeze` snapshots.
- Preserve the CI-smoke-only release packaging boundary with
  `papers/release_artifact_reproducibility_boundary.json`; wheel/sdist build
  checks, complete `libreevolve/` package-tree wheel and sdist inventory
  checks, and install-from-wheel CLI smoke checks exist, with CI-generated
  distribution hash/source-file provenance and uploaded release-smoke artifacts;
  the local release-smoke checklist is documented, while maintainer-approved
  release readiness, signed release provenance, and index artifact verification
  remain open.
- Extend current bounded environment provenance into stronger reproducibility
  evidence: complete install-source interpretation semantics, external build
  execution/options/environment records beyond `pyproject.toml`
  `[build-system]` and installed `WHEEL` metadata, non-project build metadata
  policy, live provider service/API-version capture beyond explicit false
  capability-readiness fields, provider cost and remote-default capture,
  accelerator budget/accounting semantics, and remaining private package-source
  resolution policy, plus restore/check validation that separates bounded audit
  hints from replayable evaluator environment proof.

### 4. Prompt and context work

- Extend prompt-template validation beyond the current schema, dry-run format
  checks, configured mutation-channel checks, explicit duplicate-arm/no-dedup
  audit, and parent-placeholder retention into role-specific compatibility
  policies for mutation, critique, feedback, and meta-prompt call surfaces.
- Replace first-N-character context truncation with deterministic
  summarization/ranking for local PDFs and extracted text.
- Extend current prompt caps, mutation-path provider-token section packing,
  role-scoped final-prompt token counting, and backend context-window metadata
  plus role-level section-packing overclaim guards into selected-backend
  provider-token section packing across all prompt roles and context surfaces.
  Runtime coverage keeps non-OpenAI/custom exact counters, registry/custom
  role packing, and retrieval/context/plugin/failure-memory packing readiness
  false until those surfaces exist. The current
  `papers/prompt_section_packing_boundary.json` sidecar preserves this
  mutation-section-packing boundary while keeping all-role provider-token
  section packing and full validator-metadata prompt policy open.
- Preserve stochastic prompt-format parity as effective-config distribution
  evidence only until separate source-file attribution exists. Runtime history
  links `[[prompt:name]]` selections to configured `prompt_format_options`,
  normalized probabilities, selected alternative hashes, prompt/call ids,
  weight-source boundaries, prompt-context overrides, and run-local RNG replay.
  The current `papers/stochastic_prompt_format_boundary.json` sidecar keeps
  separate distribution config paths/hashes/byte counts, config precedence,
  human-authored alternative provenance, author/reviewer metadata, revision
  history, and a paper-facing separate-file validator open.
- Extend current prompt/history retention controls into replay-retention
  policy and richer context-policy ownership. Mutation prompts, explicit
  context spans, critique prompts/mutations, feedback raw/parsed fields,
  provider output/error text, plugin context, meta-prompt evidence, framework
  quarantine snapshots, and DeepResearch retrieval bodies already have
  bounded configurable retention surfaces, and meta-prompt mutation metadata
  records validated compact capability-summary hashes for the prompt-context
  policy surface shown to the model. Runtime coverage keeps retrieval/
  summarization, semantic source-selection, non-`PromptSampler` role-policy,
  and DeepEvolve debug/refinement policy-readiness flags false with overclaim
  validation through `runtime.prompt_context_policy_coverage`.
- Integrate current evaluator-output prompt summaries, aggregate syntax
  diagnostics, and bounded run-local artifact content retrieval with
  selected-backend provider-token section packing. Artifact content can already
  be reopened from copied UTF-8 evaluator artifacts under bounded, redacted,
  run-local policy.
- Extend DeepEvolve-inspired retrieval from bounded provenance into
  audit-grade source integrity: unbounded provider-payload/source-content
  artifacts, learned or externally scored ranking/selection evidence beyond
  provider order, a replayable transport/failure decision tree, and explicit
  default-provider plus custom-provider provenance tests. Current bounded
  audits reject source-ranking metadata that overclaims semantic, learned, or
  external scoring evidence without implementing those rankers, and run-level
  coverage keeps those ranking/scoring readiness flags false. The committed
  `papers/deepevolve_boundary.json` sidecar keeps the broader DeepEvolve
  plan/search/write/code/evaluation/evolutionary-selection loop, cross-file
  coding, debugging, benchmark rows, qualitative judge rows, and ablation
  evidence separate from this bounded retrieval surface.
- Extend the current optional `IDEA`/`RATIONALE`/`HYPOTHESIS` proposal metadata
  preamble, bounded `runtime.history.hypothesis_index` summaries, and
  `runtime.history.hypothesis_branch_report` abandonment evidence, plus
  `runtime.history.proposal_diversity_report` exact duplicate counts and
  `runtime.history.proposal_score_report` outcome/exact-novelty score records,
  `runtime.history.controller_backtracking_report` observed branch-state
  transition/redirect evidence, and
  `runtime.history.natural_language_preamble_report` bounded leading
  explanatory-preamble capture, with
  `papers/proposal_score_boundary.json` preserving the bounded current-run
  proposal-score versus semantic idea-memory scope,
  `papers/proposal_diversity_boundary.json` preserving the exact-text
  duplicate-counts versus semantic proposal-novelty scope, and
  `papers/natural_language_preamble_boundary.json` preserving the
  bounded-leading-capture-only scope,
  into semantically searchable proposal memory only if needed; remaining work
  is semantic proposal-index retrieval, calibrated proposal-quality models,
  near-duplicate/idea-family novelty, code/semantic/task-output distance
  diagnostics, parent/inspiration relation linkage, prompt/backend model
  attribution, accepted/rejected outcome linkage, model-quality attribution,
  explicit controller-driven backtracking policies, cross-run proposal tables,
  hypothesis-refinement loops, with
  `papers/controller_backtracking_boundary.json` now carrying the
  paper-manifest-validated absence boundary for unpromising-decision
  rules/thresholds, controller branch-state machines, suppression/retry
  policy, prompt-sampling suppression effects, fallback-target decision
  events, causal replay, and cross-run hypothesis branch tables,
  configurable preamble policy, full-replacement
  preamble disambiguation, rationale-quality scoring, and stricter policy for
  which proposal fields may influence retrieval, prompting, and archive
  resurfacing.
- Improve meta-prompt scoring beyond the current absolute/improvement child
  score reward modes and UCB-style prompt-arm selection; add calibrated reward
  signals plus ablation reporting for prompt-program lineages.
- Promote the current local `PromptDatabase` beyond prompt-arm history and
  scoring before claiming AlphaEvolve-style prompt-database parity: define
  prompt-side archive/retention policy, prompt descriptors/objectives,
  archive-event streams, replay/migration semantics, async/controller-resumable
  prompt work, and benchmark evidence that it behaves as more than a local
  UCB-style prompt selector.

### 5. Documentation truthfulness

- Keep README, docs, paper index, and `docs/todo/*` aligned with implemented
  behavior. The committed
  `papers/documentation_truthfulness_boundary.json` sidecar preserves the
  current cross-document guard boundary, and
  `papers/documentation_claim_inventory.json` now gives top-level README,
  ROADMAP, and papers-index claim ids with evidence anchors while keeping
  complete claim coverage, semantic documentation-claim verification, and full
  AlphaEvolve-facing claim proof open.
- Keep the code-audit completeness boundary explicit:
  `papers/implementation_evidence_map_boundary.json` records core
  AlphaEvolve requirement anchors with module, test, sidecar, and TODO links,
  and `papers/status_claim_inventory.json` records checked row-level paper
  status inventory plus status-cell phrase hashes, source offsets, local
  artifact mention source offsets, and candidate evidence-link lists plus
  referenced local artifact and TODO evidence-path source offsets/existence checks plus
  row/phrase-specific TODO content artifact mention records and structural
  absence-signal source-offset classification, while
  `papers/benchmark_coverage_inventory.json` records structural implemented
  benchmark coverage bullets plus referenced local artifact mention source
  offsets/existence checks and limitation-signal term/source-offset
  classification.
  This is not an exhaustive source-span coverage matrix,
  per-phrase evidence-link sufficiency proof, status-cell semantic verifier,
  implemented-benchmark bullet semantic verifier,
  absence-sentence freshness matrix, coverage detector, generated code-audit
  report, or CI exhaustiveness gate.
- Keep paper-manifest validation diagnostics shareable by using
  repository-relative labels and secret-redacted exception text in text and JSON
  output.
- Keep the paper-index validator boundary explicit: it currently proves
  manifest/readability/count checks, Appendix B and ablation registry shape,
  implementation-status table structure, role/status taxonomy compatibility,
  status-cell local-artifact links to active or completed TODO evidence, TODO
  coverage row coverage, active ledger links, and completed-ledger checklist
  evidence. It also catches one narrow benchmark-coverage contradiction where
  an `Implemented` bullet is phrased as not implemented. It does not yet prove
  arbitrary natural-language semantics for every long status phrase, benchmark
  qualifier, implemented-benchmark limitation, or paper claim.
- Keep Section 5 Related Work positioning scoped to flat source inventory until a
  validated taxonomy lands. The committed
  `papers/related_work_taxonomy_boundary.json` sidecar records that source
  rows and individual TODOs do not yet prove source-category mapping,
  method-family labels, comparison axes, or AlphaEvolve positioning claims.
- Persisted validator-boundary consistency now has a CLI artifact gate:
  `validate_run_artifact_validator_boundary_consistency()` loads manifest-backed
  run directories, validates `policies.validator_execution`, scans
  `history.jsonl` and `failure_history.jsonl`, requires
  `evaluation.metadata.validator_boundary` on each persisted attempt, and
  `libreevolve show` fails missing, legacy, or mismatched boundary evidence.
  This remains audit consistency for the declared local-subprocess boundary,
  not OS/container sandbox, quota enforcement, or promotion-time archival
  blocking. The committed `papers/validator_artifact_promotion_boundary.json`
  sidecar preserves that CLI-inspection versus promotion-gate boundary.
- Continue labeling CausalEvolve, DeepEvolve, ImprovEvolve, ThetaEvolve,
  TTT Discover, Bruhat Intervals, GigaEvo, CodeEvolve, MadEvolve, Magellan,
  ArchAgent, Multiagent Learning, Bilateral Trade, Fault2Flow, Global NLP
  Optimization, Autoconvolution, Sums and Differences, Sums and Differences II,
  Ramsey Numbers, and Berczy
  local-correction combinatorics
  features as inspired, candidate benchmark, or
  application context unless paper behavior is actually implemented. The committed
  `papers/gigaevo_framework_boundary.json`
  sidecar records the GigaEvo source-specific boundary for Redis lifecycle
  storage, asyncio DAG execution, concurrent units, insight/lineage stages,
  LangGraph mutation, Hydra mapping, dual GitHub source disambiguation, and
  benchmark reproduction. The committed `papers/codeevolve_boundary.json`
  sidecar records the CodeEvolve source-specific boundary for prompt/solution
  dual fitness, semantic inspiration crossover, meta-prompting exploration,
  depth-targeted refinement, exploration scheduling, sandbox runtime/memory
  limits, MAP-Elites/CVT parity, benchmark rows, ablations, quality-cost
  comparisons, and linked experiment-artifact status. The committed
  `papers/thetaevolve_boundary.json` sidecar records the ThetaEvolve
  source-specific boundary for dynamic-environment architecture, single-LLM
  runtime, large-database scaling, batch sampling, early checks, lazy
  penalties, reward shaping, online GRPO/RL training, checkpoint lifecycle,
  throughput reports, and benchmark comparisons. The committed
  `papers/ttt_discover_boundary.json` sidecar records the TTT Discover
  source-specific boundary for test-time policy weight updates,
  single-problem RL environments, continuous-reward problem contracts, PUCT
  state reuse, adaptive entropic training objectives, Tinker training-run
  evidence, gpt-oss-120b LoRA backend records, matched Best-of-N/OpenEvolve
  comparator rows, math/kernel/AtCoder/biology result rows, expert or
  organizer reviews, public-code artifact hashes, cost records, and
  independent reproduction outputs. The committed
  `papers/bruhat_intervals_boundary.json` sidecar records the Bruhat Intervals
  source-specific boundary for permutation-pair candidate schemas,
  simple-reflection decoding, d-invariant evaluation, Bruhat order/Ehresmann
  matrix verification, x_m/y_m witness generation, dyadic interval checks,
  dyadically well-distributed permutation checks, fundamental/complementary
  block validators, poset-hypercube isomorphism checks, Kazhdan-Lusztig
  R-polynomial linkage rows, cluster-algebra and Bruhat-graph consequences,
  AlphaEvolve prompt/model/budget provenance, public artifact hashes, and
  independent checker outputs. The committed
  `papers/improvevolve_boundary.json` sidecar records the ImprovEvolve
  source-specific boundary for `generate_config`/`improve`/`perturb`
  interface enforcement, Stage A/B execution, basin hopping, perturbation
  schedules, monotonic acceptance, GigaEvo outer-loop parity, model/provider
  provenance, human-edited variants, HEX/ACI2 benchmark rows, ablations, and
  compute budgets. The committed `papers/madevolve_boundary.json` sidecar
  records the MadEvolve source-specific boundary for framework/application
  split, free-parameter tracking, nested parameter optimization, JAX/vmad
  compatibility, optimized-value source injection, BAO/21cm/tSZ task adapters,
  generated innovation reports, run/model-contribution statistics,
  reward-hacking controls, and hosted report artifacts. The committed
  `papers/causalevolve_boundary.json` sidecar records the CausalEvolve
  source-specific boundary for POMDP/SCM task-world records, causal scratchpad
  memory, LLM outcome-factor generation, executable factor code,
  CausalPlanner factor-direction interventions, procedure-factor extraction,
  treatment-effect tables, surprise-pattern detection, abductive hypotheses,
  scratchpad replay, and benchmark/ablation rows. The committed
  `papers/deepevolve_boundary.json` sidecar records the DeepEvolve
  source-specific boundary for problem/algorithm/instruction inputs,
  textualization, plan/search/write proposal records, retrieved-source
  provenance, proposal pseudo-code, cross-file coding, reflection
  checkpoints, debugging attempts, score-zero fallback, evolutionary database
  semantics, island/MAP-Elites inspiration sampling, nine-task benchmark rows,
  Table 2/Table 3/Table 4 records, Figure 3 judge rows, Appendix C query rows,
  and 30-minute/single-GPU budget evidence. The committed
  `papers/magellan_boundary.json` sidecar records the Magellan source-specific
  boundary for executable C++ decision logic, compiler-pass integration,
  EVOLVE-BLOCK compiler spans, compiler rebuild and macro-benchmark evaluation,
  Vizier-style autotuning, LLVM function-inlining rows, register-allocation
  rows, XLA graph-extraction/auto-sharding rows, expert/neural baselines,
  temporal/domain generalization, generated-policy maintainability evidence,
  and dedicated Magellan runtime-repository status. The committed
  `papers/archagent_boundary.json` sidecar records the ArchAgent
  source-specific boundary for generated C++ cache policies, ChampSim
  `policy.h` integration, CRC hardware configurations, SPEC06/Google Workload
  Trace fixtures, IPC-over-LRU metrics, Policy31/Policy31-Tuned/Policy61/
  Policy62 artifacts, hardware-realizability and state-budget checks,
  post-silicon specialization, simulator-escape controls, distributed
  simulation reliability, and dedicated ArchAgent runtime-repository status.
  The committed `papers/multiagent_learning_boundary.json` sidecar records
  the Multiagent Learning source-specific boundary for CFR/PSRO candidate
  schemas, OpenSpiel imperfect-information game fixtures, exploitability
  metrics, exact-oracle PSRO records, VAD-CFR/SHOR-PSRO rows, WOP-CFR/
  PM-PSRO distillation rows, IQM ablation audits, random normal-form
  validation, generated solver artifacts, and dedicated runtime-repository
  status. The committed `papers/ramsey_numbers_boundary.json` sidecar records
  the Ramsey Numbers source-specific boundary for graph candidate schemas,
  `run()` primary/prospect graph contracts, clique/independent-set verifiers,
  new/matched/exact lower-bound rows, Google Research construction/code links,
  graph and algorithm artifact hashes, initialization-family records,
  graph-size-to-lower-bound semantics, and independent checker outputs.
  The committed `papers/combinatorics_berczy_boundary.json` sidecar records
  the Berczy local-correction combinatorics source-specific boundary for
  bipartite and planar graph-reconstruction harnesses, Alon-Tarsi
  Latin-square trade/involution harnesses, Rota-basis local-exchange
  harnesses, certificate schemas, symmetry-scramble and hard-negative replay
  records, evolved-code and Gemini-summary artifacts, reported metric and
  conjecture rows, repository snapshots, and independent verifier outputs.
  The committed `papers/bilateral_trade_boundary.json` sidecar records the
  Bilateral Trade source-specific boundary for value-distribution candidate
  schemas, fixed Discrete Equal Revenue buyer fixtures, evolved seller CDF
  runtime, PMF/CDF/survival validation, first-best and Random-Offerer GFT
  evaluators, integer-rounding precision policy, witness artifacts, code
  hashes, prior-baseline rows, alternate-search attempts, BIC/BB/IR
  assumptions, unrounded-mixture caveat handling, and independent checker
  outputs. The committed `papers/fault2flow_boundary.json` sidecar records the
  Fault2Flow source-specific boundary for regulatory PDF ingestion,
  MinerU-to-Markdown extraction, PlantUML mind-map generation, PASTA
  fault-tree schemas, human-in-the-loop expert review states, AlphaEvolve
  reasoning optimization, multi-island archive provenance, n8n workflow
  synthesis and activation, workflow verification/refinement loops, DL/T
  722-2014 transformer fault-diagnosis dataset rows, GPT-5 judge outputs,
  Table 1 reproduction rows, token ledgers, human-annotation ethics records,
  placeholder publication-metadata caveats, and local workflow snapshots.
  The committed `papers/global_nlp_optimization_boundary.json` sidecar records
  the Global NLP Optimization source-specific boundary for direct NLP
  formulation schemas, Mosel model artifacts, min-max distance-ratio fixtures,
  square and perimeter-4 rectangle circle-packing fixtures, rotated unit
  hexagon-packing fixtures, Farkas non-overlap certificates, FICO Xpress and
  SCIP runner evidence, solver identity/version/license records,
  incumbent/bound/certificate artifacts, numerical tolerance and rounding
  policy, AlphaEvolve validation-code outputs, Table 1-3 reproduction rows,
  solver-attribution caveats, dual-bound-detail caveats, and independent
  checker outputs.
  The committed `papers/autoconvolution_boundary.json` sidecar records the
  post-AlphaEvolve Autoconvolution source-specific boundary for 575-interval
  witness schemas, coefficient payload hashes, formula (3) discrete
  autoconvolution checking, `L_j` sequence recomputation, `L2`/`Linf`/`L1`
  norm checks, exact fraction and decimal result validation, AlphaEvolve and
  Matolcsi-Vinuesa baseline records, simulated-annealing and gradient-search
  provenance, row-major coefficient parsing, public GitHub artifact snapshots,
  Mathematica `Verify.nb` evidence, support-normalization records, NCSU HPC
  resource provenance, and independent checker outputs.
  The committed `papers/sums_differences_boundary.json` sidecar records the
  post-AlphaEvolve Sums and Differences source-specific boundary for explicit
  U-set construction schemas, `W(m,L,B)` inclusion-exclusion records,
  base-(2B+1) injective encoding checks, sumset/difference-set cardinality
  verifiers, max-element/q-value records, theta recomputation, GMP exact
  arithmetic provenance, small and large parameter rows, exact-value artifact
  snapshots, AlphaEvolve 54265-integer baseline evidence, huge-set compression
  policy, lineage comparison rows, tolerance policy, and independent checker
  outputs.
  The committed `papers/sums_differences_sequence_boundary.json` sidecar
  records the post-AlphaEvolve Sums and Differences II source-specific
  boundary for sequence-of-U construction schemas, large-deviation `I(c,B)`
  records, asymptotic `W(m,floor(rm),B)` checks, Lemma 1/Lemma 2 verification,
  `q`/`s`/`d` bound derivation records, theta0 variational-formula
  recomputation, MATLAB 2024b code provenance, `B=3..10` tolerance-sweep
  rows, finite-prefix artifact policy, AlphaEvolve and Gerbicz baseline rows,
  convergence/tail-bound checks, lineage comparison rows, and independent
  checker outputs.
  The committed `papers/ucb1_boundary.json` sidecar records the UCB1
  finite-time-analysis boundary for bounded reward-support assumptions,
  conditional-mean/stationarity assumptions, regret definitions, Theorem 1 and
  suboptimal-pull constants, canonical confidence-index formulas,
  initialization semantics, backend-as-arm identity, reward normalization,
  selected-index traces, unsupported UCB-family variants, and the
  non-proof status of metadata-weighted `throughput_depth` routing.

## Mid Term

### 6. Async and resumable runtime

- Add a controller with bounded queues for LLM proposals and evaluator workers;
  the current loop reports its synchronous topology under
  `runtime.history.distributed_pipeline_topology_report`, with
  `papers/distributed_pipeline_topology_boundary.json` preserving the
  paper-facing single-process synchronous-topology absence boundary, including
  the missing Python `asyncio` runtime identity, async task/coroutine
  identities, dependency wait telemetry, worker lifecycle/liveness records,
  scheduler-state snapshots, and deterministic async completion/admission order
  required by AlphaEvolve Section 2.6. It
  supports sequential `proposals_per_generation` batches plus opt-in local
  `eval_stages[].sample_workers` fan-out for configured-stage samples, but not
  concurrent proposal/evaluation queues. Completed manifests also expose
  `runtime.history.parallel_evaluation_readiness_report`, which records local
  sample-worker fan-out and wall-clock compression, and
  `papers/parallel_evaluation_readiness_boundary.json` preserves the
  paper-facing absence boundary while keeping order-of-100-compute-hours
  candidate budgets, generation-cadence preservation under slow feedback,
  concurrent LLM sampler queues, candidate-level async evaluator queues,
  queue capacity/backpressure policy, distributed evaluator nodes,
  deterministic async result merge/admission order, concurrency-safe shared
  state mutation, mutation-depth impact, pending-work resume, and equal-budget
  parallelism evidence open.
- Compose the current restored LLM scheduler, prompt-history, RNG, archive, and
  budget snapshots with controller and pending-evaluation checkpoint state so
  long runs can resume from more than a terminal drained boundary. The committed
  `papers/controller_pending_work_resume_boundary.json` sidecar preserves the
  current terminal controller-state evidence while keeping queue checkpoint,
  running-work resume, provider handoff replay, and end-to-end resumed-trace
  proof open.
- Extend the current restorable MAP-Elites cell/island snapshots, elite
  snapshots, and island cursor/counter state with descriptor-value replay
  semantics, ordered migration-event replay, controller queues, and pending-work
  restore. Current manifests can restore cursor-only state or full archive
  cell/elite placements from a previous manifest/history bundle, and
  `--restore-runtime-from-manifest` composes those compatible synchronous
  restore surfaces into a checked full-runtime bundle, but it is not a full
  replay or resumed experiment trace. The committed
  `papers/archive_event_replay_boundary.json` sidecar preserves that
  snapshot-restore versus ordered-event-replay boundary, and
  `papers/controller_pending_work_resume_boundary.json` separately preserves
  the terminal controller-state versus pending-work resume boundary.
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
and lineage-boundary checks while keeping resumed-trace proof readiness false;
provider/plugin output replay, controller pending-work state, and end-to-end
resumed-trace proof are still open; the terminal controller-state boundary is
tracked by `papers/controller_pending_work_resume_boundary.json`, and the
deterministic lineage-id versus provider/direct-UUID replay boundary is tracked
by `papers/lineage_replay_boundary.json`.
- Extend budget accounting beyond the current local synchronous generation,
  evaluator-call, evaluator-second, wall-clock, LLM call/provider/token/
  configured-cost/latency, synchronous controller-budget event replay, and
  stop-reason counters, plus pre-applied full-runtime restore bundles, to cover
  concurrent evaluations, async queues, pending-work restore, provider-output
  replay, and executed equal-budget ablation reports. The current
  `papers/llm_budget_policy_boundary.json` sidecar keeps role-level LLM budget
  reporting scoped to cooperative snapshots rather than async pending-work
  accounting. The named AlphaEvolve
  Figure 8 ablation variants are now captured as a validated report contract,
  but the runs/curves are not implemented.

### 7. Backend scheduling and critique

- Normalize/document UCB rewards against bounded assumptions or rename the
  current policy as a heuristic.
- Extend opt-in `llm_role_scheduler_scope="role_scoped"` live per-role
  selection state, configured reward-accounted role selection, role-scoped
  backend eligibility, logical call caps, and role budget maps into calibrated
  reward signals, quota ownership, and budget policy for mutation generation,
  critique, feedback grading, and meta-prompt mutation calls. The current
  sidecar `papers/llm_role_scheduler_boundary.json` preserves the local
  role-scoped UCB/runtime evidence boundary while keeping calibrated role
  reward policy, role-specific backend-pool policy, role-specific exploration
  parameters, reward normalization reports, outcome-attribution datasets, async
  role work queues, cross-role interference analysis, experiment-owned quota
  policy, fast/strong model-mix reports, resume replay experiment reports, and
  role-specific budget behavior reports open.
- Extend current run-scoped call telemetry beyond provider usage, configured
  cost estimates, request ids, finish reasons, adapter-internal retry
  summaries, configured-pricing aggregate consistency checks, raw-payload
  replay overclaim checks, remote-default overclaim checks, explicit false
  pricing-readiness fields, and token/cost/latency budget stops to include raw
  provider diagnostics, live provider pricing/default-rate capture beyond
  configured token-cost estimates, and richer budget-event evidence. The
  current `papers/provider_pricing_boundary.json` sidecar preserves the
  configured-cost-estimate boundary while keeping live provider pricing,
  default-rate capture, account/model-specific pricing, and raw provider
  payload replay open. The current
  `papers/provider_diagnostics_replay_boundary.json` sidecar preserves the
  bounded scalar diagnostics boundary while keeping raw provider-payload
  sidecars, provider-output replay, complete provider-call replay, and
  account/model default capture open.
  `papers/llm_stochastic_reproducibility_boundary.json` separately preserves
  the request-parameter telemetry boundary while keeping backend/API-mode seed
  semantics, provider model-revision stability, repeated identical-call
  fixtures, and deterministic provider-output replay open.
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
  scheduler-observation, explicit false runtime-readiness fields, in-run
  quarantine-evidence, and mutation timeout failure-history paths. The current
  `papers/provider_cancellation_boundary.json` sidecar preserves the
  policy/audit-only boundary while keeping live SDK cancellation,
  timeout-driven stop enforcement, cross-run provider quarantine resume,
  richer role-specific timeout artifacts, and provider-output raw-payload
  replay open.
- Extend current focused `throughput_depth` metadata tests into
  AlphaEvolve-style breadth/depth/cost/latency scheduler validation, including
  experiment-level selection traces and equal-budget report evidence. The
  current `papers/fast_strong_model_mix_boundary.json` sidecar preserves the
  metadata-trace-only boundary while keeping fixed compute budget identity,
  matched problem/seed/evaluator controls, provider-model identity for
  fast/strong lanes, lane quota schedules, per-lane token/cost/latency
  accounting, lane switching traces, breadth-volume and breakthrough-quality
  attribution, reserved fast-breadth and strong-depth lane policies, candidate
  throughput/quality outcomes, and equal-budget scheduler comparisons open.
- Extend the current single-run sample-efficiency report into benchmark-level
  proposal-count curves, target-hit evidence, repeated-sampling comparisons,
  and model-size/equal-budget analyses before treating it as AlphaEvolve
  Table 1 evidence that useful results can be reached with thousands rather
  than millions of LLM-generated samples. Required evidence includes fixed
  run seed/evaluator identity, target-definition provenance, score-direction
  and normalization policy, target-attainment curves by logical sample and
  generated candidate, target-hit indexes, replicate seed sets, variance or
  confidence intervals, matched-budget run groups, and cost/latency budget
  curves.
- Turn the current repeated-sampling boundary report into an executable
  equal-budget comparator runner with fixed prompt/model/backend-request/
  seed/candidate-budget/evaluator controls, fixed LLM-call budgets, same
  candidate-validation pipeline, disabled archive/MAP-Elites/parent/
  inspiration/failure/critique/feedback/meta-prompt influence, sample-index
  alignment, target metric/threshold linkage, comparator artifact hashes, and
  linked evolutionary runs before making test-time-compute uplift claims over
  repeated base-model sampling.
- Turn the current Gemini provider-parity boundary report into a first-class
  Google/Gemini adapter or equivalent provider-plugin/substitution contract.
  Completed manifests and `papers/gemini_provider_parity_boundary.json` now
  record built-in provider types, configured Gemini-like custom backends,
  Flash/Pro-shaped model names, and `claim_ready: false`; this is evidence for
  the missing AlphaEvolve Flash/Pro provider surface, not provider parity.
  Remaining provider-parity gates include credential preflight, Gemini
  client-context configuration, request-parameter mapping, provider-native
  usage/default/error diagnostics, model-registry snapshots, account/model
  availability checks, first-class Flash and Pro lane identity, scheduler lane
  integration, paper-level substitution contracts, and
  substitution-equivalence justification.
- Extend current synchronous configurable critique reviewer pools, role routing,
  and first/last-valid aggregation toward async reviewer overlap, calibrated
  reviewer scoring, stronger provider isolation, and runtime artifacts for
  reviewer-specific timeout/failure behavior. The current
  `papers/critique_reviewer_pool_boundary.json` sidecar preserves the
  synchronous first/last-valid telemetry boundary while keeping async reviewer
  overlap, independent reviewer task definitions, reviewer/generator role
  separation proof, critique-to-revision attribution, reviewer
  score-to-selection policy, reviewer budget quota policy, reviewer failure-isolation
  reports, equal-budget no-reviewer comparisons, calibrated reviewer scoring,
  reviewer reliability ablations, per-reviewer provider isolation, and
  external reviewer timeout artifacts open.

### 8. Plugin extensibility

- Extend the bounded `libreevolve.plugins` entry-point registry toward richer
  package policy and direct custom-plugin schema/provenance beyond the current
  entry-point distribution metadata and direct-instance signature-only policy
  that explicitly excludes constructor values with false direct-instance
  readiness fields.
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
- Add a bounded sorting-network rediscovery fixture before heavier benchmark
  families: `sorting_network_8` and `sorting_network_9` now exhaustively
  verify `2^8` and `2^9` Boolean inputs and target 19 and 25 comparators from
  valid 28- and 36-comparator seeds. Their hardening bundle helper now emits
  negative-fixture descriptors, detector logs, inventories, summaries, and
  scope validation for both candidates. Add repeated-run, source-citation, and
  paper-certification evidence before treating them as comparable results. The
  `papers/sorting_network_rediscovery_boundary.json` sidecar preserves that
  executable-candidate-only boundary.
  This remains the current lowest-risk realistic benchmark path because it has
  cheap objective verification, known targets, and no external solver or
  accelerator dependency.
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
  from `papers/example_benchmark_scope.json` so smoke fixtures cannot drift
  into paper-comparable claims. Runtime manifests now also emit
  `runtime.history.benchmark_fixture_readiness_report`, which makes the same
  smoke-versus-benchmark boundary visible for each run while keeping real
  benchmark and paper-claim readiness false.
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
  verifier evidence remain open. The committed `papers/math_outcome_boundary.json`,
  `papers/math_starting_construction_boundary.json`,
  `papers/math_heuristic_handoff_boundary.json`, and
  `papers/math_heuristic_stage_sequence_boundary.json` sidecars now emit these
  absence boundaries for paper-manifest validation.
- Keep Appendix B per-result metric/value claims scoped to the registry's
  result-row absence boundary: `alphaevolve_appendix_b.json` now validates the
  missing cross-family layer for B.1-B.13 text-level result rows, including
  the `19` expected result ids, metric definitions, parameter tuples,
  prior-value attribution, source locations, construction payload hashes,
  verifier artifacts, result-version status, and recomputed values. The actual
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
  coordinate payloads, point-count/dimension certificates, pairwise distance
  matrix artifacts, min/max pair-witness certificates, or squared-ratio
  recomputation certificates. A `witness_certificate_boundary` now records the
  required future witness fields including those artifacts plus Figure 12
  panel artifact path/hash fields, preserves the 16-point/2D and 14-point/3D
  missing-witness rows, and keeps both B.8 witnesses and panel artifacts
  explicitly `not_recorded_locally`.
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
  `4.0` to `3.942`, and required future placement, pose/orientation,
  regular-hexagon geometry, containment, non-overlap,
  recomputed-side-length, side-length recomputation certificate, and Figure
  11 panel artifact fields. The actual placement payloads, pose/orientation
  schemas, geometry certificates, side-length recomputation certificates, and
  panel artifacts remain open.
- Keep Appendix B.9-B.10 Heilbronn claims scoped to result-boundary evidence
  until point/domain certificates land: the registry now validates the
  unit-area triangle row for `n = 11` with minimum area `> 0.0365`, the
  convex-region rows for `n = 13` and `n = 14` with minimum areas `0.0309`
  and `0.0278`, their prior `[29]` values, Figure 13 panel links, and
  required future point-coordinate, domain, unit-area, triple-count
  enumeration, convexity, all-triples area, minimum-witness-triangle,
  reported-value comparison, recomputed-minimum-area, and Figure 13 panel
  artifact path/hash fields, with panel artifacts explicitly
  `not_recorded_locally`. The actual coordinate/domain payloads, triple
  enumeration, area certificates, reported-value comparison certificates, and
  panel artifacts remain open.
- Keep Appendix B.11 kissing-number claims scoped to lemma-boundary evidence
  until the 593-vector certificate lands: the registry now validates the
  dimension-11 target, prior lower bound `592`, reported lower bound `593`,
  nonzero integral-coordinate witness requirements, max-norm versus
  minimum-pairwise-distance condition, Lemma 1 transformation to sphere
  centers, and required future vector, count/dimension, norm-matrix,
  distance-matrix, separate max-norm, minimum-pairwise-distance, strict
  inequality, lemma-applicability, transformed-center, unit-sphere
  normalization, kissing-angle, and recomputed-lower-bound fields. The actual
  vector payload, count/dimension certificates, norm/distance matrices,
  strict inequality proof, transformed unit-sphere proof, kissing-angle proof,
  and exact proof certificates remain open.
- Keep Appendix B.12-B.13 sum-of-radii packing claims scoped to
  result-boundary evidence until placement certificates land: the registry now
  validates `n = 26` and `n = 32` unit-square rows, the `n = 21` perimeter-4
  rectangle row, prior and reported sums of radii, Figure 14 panel links, the
  B.13 caption display `sum_of_radii >= 2.365` versus text value `2.3658`,
  and required future placement, exact-count, payload-schema validation,
  positive-radius, containment, non-overlap, perimeter, sum-formula,
  recomputed-sum, container-artifact, and Figure 14 panel artifact path/hash
  fields. It also preserves the Figure 5 display `2.6340 -> 2.6358` as a
  separate precision boundary from the Appendix B.12/Figure 14 `2.634` to
  `2.635` strings. The checked-in 26-circle fixture remains explicitly
  smoke-only, and the actual AlphaEvolve container artifacts, placement
  payloads, panel artifacts, exact certificates, payload-schema validation
  certificates, positive-radius certificates, sum-of-radii formula
  certificates, source locators, value-extraction certificates,
  value-reconciliation certificate, canonicalization policy, recomputed sum,
  and companion Colab link remain open.
- Keep Appendix B figure-exhibit claims scoped separately from family/result
  boundaries: the top-level `figure_exhibit_boundary` now validates the
  missing Figures 10-14 exhibit layer, including required future
  figure/subfigure ids, caption values, previous/current metric values,
  rendered visual artifacts, render parameters, source Colab locators, and
  verifier links, while the actual exhibit rows and artifacts remain
  `not_recorded_locally`.
- Keep paper artifact-role attribution separate from artifact availability:
  `libreevolve.alphaevolve_paper_artifact_roles.v1` now validates the
  AlphaEvolve PDF contribution records for figure creators and companion
  Colab assemblers, and `papers/paper_artifact_roles.json` now emits those
  records as a committed paper-facing sidecar. The companion
  `libreevolve.alphaevolve_paper_artifact_linkage.v1` record is also emitted
  in `papers/paper_artifact_linkage.json`; it validates the current
  `not_yet_linked` availability boundary and the digest, source-locator, and
  source-to-artifact-map fields required before rendered figure artifacts or
  notebook/export artifacts can be claimed. The paper-manifest gate requires
  both sidecars at the real repo root.
- Keep AlphaEvolve source-PDF versioning explicit:
  `libreevolve.alphaevolve_source_pdf_version.v1` now validates the cached
  `2506.13131` PDF manifest row against the audited first-page header
  `arXiv:2506.13131v1 [cs.AI] 16 Jun 2025`, including arXiv id, version,
  category, posted date, DOI, subject classes, submitted timestamp, author
  count, TeX source URL, arXiv license URL, floating and versioned URLs,
  expected header page, local byte count, SHA-256 digest, and the policy that
  claim audits must name the source version. The paper-manifest gate validates
  this built-in record and the committed `papers/source_versions.json`
  companion manifest, which emits the `2506.13131v1` source-version row and
  links it to docs/TODO claim surfaces while keeping the legacy CSV/JSON
  download manifests as PDF cache ledgers. Full publication-grade source
  metadata parity is still not claimed, but
  `papers/arxiv_abstract_snapshot.json` now records the current abstract-page
  byte count, SHA-256 digest, retained HTML artifact path, normalized title,
  author list, subject classes, DOI URL, submitted timestamp, TeX-source URL,
  license URL, and submission-history entry.
  `papers/alphaevolve_datacite_doi_boundary.json` now pins a bounded DataCite
  API response summary, response byte count, SHA-256 digest, DOI, landing URL,
  title, creator count, publisher, publication year, resource type, schema
  version, registered timestamp, and version.
  `papers/alphaevolve_tex_source_boundary.json` now pins the arXiv e-print
  endpoint, retrieval date, HTTP status, gzip content type,
  content-disposition filename, byte count, SHA-256 digest, and
  `2506.13131v1` source-version linkage.
  `papers/alphaevolve_current_version_boundary.json` now pins the floating
  abstract URL status/content/digest, confirms current version `2506.13131v1`,
  and records that the retained floating PDF artifact bytes/hash match the
  cached PDF.
  `papers/alphaevolve_cached_pdf_header_consistency_boundary.json` now pins
  cached-PDF first-page header extraction hashes and arXiv/title/rights
  markers for the retained AlphaEvolve PDF.
  `papers/alphaevolve_raw_http_headers_boundary.json` now preserves pinned raw
  HTTP response header lines for the versioned abstract, floating abstract,
  floating PDF, DataCite API, e-print archive, and license page.
  `papers/alphaevolve_doi_landing_resolution_boundary.json` now pins the DOI
  resolver `302` headers, redirect location, and final arXiv landing-page
  headers. `papers/alphaevolve_datacite_full_response_boundary.json` now
  retains the complete 15,905-byte DataCite API response body and validates its
  parsed DOI metadata fields.
  `papers/alphaevolve_tex_archive_retention_boundary.json` now retains the
  2,635,462-byte TeX/e-print archive artifact and validates its 58-entry member
  inventory. `papers/alphaevolve_license_page_html_retention_boundary.json`
  now retains the Creative Commons license-page HTML artifact and validates its
  bytes, hash, and key content markers.
  `papers/alphaevolve_metadata_extraction_script_boundary.json` now pins the
  reusable offline extraction script path, byte count, SHA-256 digest,
  import entrypoint, CLI command, and retained source artifact coverage for
  abstract HTML, cached PDF, DataCite full response, license HTML, and TeX
  archive inputs. `papers/alphaevolve_source_refresh_gate_boundary.json` now
  pins the deterministic/live refresh-gate script and the scheduled/manual
  GitHub Actions `source_refresh_gate` job that compares live
  arXiv/DataCite/e-print/license responses against committed source
  boundaries. `papers/alphaevolve_source_refresh_run_2026-06-14.json` now
  archives one successful manual live-network refresh run with six matched
  source responses and a canonical run-report hash. The scheduled/manual
  workflow now writes `alphaevolve_source_refresh_report.json` and uploads it
  as the `alphaevolve-source-refresh-report` artifact.
  `papers/alphaevolve_source_refresh_promotion_boundary.json` now records the
  decision not to relabel older per-source snapshot sidecars as standalone
  refresh-ready evidence, mapping each central-gate source id to the paper
  sidecars it covers. Scheduled CI refresh-run history remains open.
  `papers/alphaevolve_license_page_boundary.json` now pins the Creative
  Commons BY-NC-ND 4.0 license URL, retrieval date, HTTP status, content type,
  byte count, SHA-256 digest, title, license family, and version while keeping
  automated license-page refresh open.
- Keep paper-cache row identity proven before version/rights evidence:
  `libreevolve.tools.paper_manifest` now validates that arXiv PDF/abs URLs
  contain a source id matching the manifest `id`, and that every local PDF
  filename begins with the manifest id before any `__` title suffix. Non-arXiv
  slug rows use the same filename source-prefix rule. The committed
  `papers/row_identity.json` companion manifest emits those derived source
  identities for all 53 cache rows and links the AlphaEvolve row to
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
  the Appendix B `result_row_boundary` inventory of `19` expected result ids,
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
  with docs/TODO claim-surface links, the cached
  `papers/2511.02864__Mathematical_exploration_and_discovery_at_scale.pdf`
  row (`12141713` bytes,
  SHA-256 `77b43844077c98c26dfc76ad391cadbbd53d48a1d290ddae575ff4d1bcdef9d2`),
  and linked problem-coverage evidence for the declared-67 versus observed-68
  numbered-page boundary. It also maps the `19` original Appendix B result ids
  across the `13` Appendix B families to follow-on repository problem pages and
  notebook-link statuses without claiming normalized result rows, construction
  payloads, verifier artifacts, recomputed values, or full notebook cell
  inventories. Deeper per-claim artifact/recomputation ledgers remain open.
- Keep follow-on problem-repository rights separate from the original PDF,
  `alphaevolve_results`, and LibreEvolve licensing:
  `papers/follow_on_repository_rights.json` now records the pinned repository's
  citation/BibTeX requirement, Google LLC copyright, Apache-2.0 software /
  CC-BY-4.0 materials split, artifact-type license mapping, AS-IS and
  non-official-product disclaimers, Gómez-Serrano/Tao role attribution, Problem
  65's official IMO origin, docs/TODO claim-surface links, and reuse policy for
  copied source material versus generated local artifacts. It now attaches
  validated follow-on artifact-rights templates for local generated outputs,
  adapted verification code, and copied problem statements while preserving a
  zero-current-local-generated-artifact boundary for copied/adapted follow-on
  repository material.
- Keep follow-on problem-repository runtime availability scoped:
  `papers/follow_on_runtime_absence.json` now records the pinned repository
  README/tree evidence for 28 notebooks, including paths, Git blob ids, byte
  counts, raw SHA-256 hashes, artifact-kind flags, scoped observed artifact
  presence flags from notebook cell titles, explicit
  `alphaevolve_runtime_available: false`, verifier-versus-runtime
  classification, docs/TODO claim-surface links, and the source phrase that
  the repository does not contain the code to run AlphaEvolve. It treats
  notebooks as prompts/verifiers/inputs/outputs around completed experiments,
  not runnable AlphaEvolve implementation artifacts; full notebook cell
  inventories remain outside the claim.
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
  docs/TODO claim-surface links. The same sidecar now includes a
  `proof_element_artifact_boundary` that keeps Ramanujan witness inventories,
  MAX-k-CUT and metric-TSP gadget inventories, evolved verifier code,
  independent brute-force outputs, theorem-lifting metadata, baseline/SOTA
  rows, and source-repository status explicitly missing. Graph/gadget
  artifacts, AlphaEvolve search code, verifier code, original brute-force
  verifier provenance, and local graph-certification benchmarks remain open
  before roadmap claims can treat this source as implemented benchmark parity.
- Keep official DeepMind announcement claims separated from white-paper spec
  parity: `papers/official_deepmind_blog.json` now records the May 14, 2025
  blog URL/date/title/team, retrieval hash, white-paper and Colab outbound
  links, Early Access form link, claim ids, blog-versus-paper variants such as
  `32.5%` FlashAttention and weeks-to-days kernel work, and blog
  acknowledgement/illustration roles. Reconciliation to paper sections, Colab
  artifacts, rendered artifacts, and reproduced LibreEvolve evidence remains
  open before announcement wording can be treated as audited implementation
  parity.
- Keep official 2026 AlphaEvolve impact claims separated from local
  implementation and original-spec parity:
  `papers/alphaevolve_2026_impact_boundary.json` now records the May 7, 2026
  Google DeepMind impact article URL/date/title/team, retrieval hash, outbound
  source links, claim ids and values across genomics, power-grid optimization,
  Earth AI, quantum circuits, math/gallery examples, infrastructure,
  compiler/storage, commercial deployments, and UI/API attribution. Local
  DeepConsensus, AC OPF, Earth AI, Willow, TPU-design, cache-policy, Spanner,
  compiler-storage, customer-case, public-gallery, UI, API, and independent
  verification evidence remains open before roadmap or release wording can
  treat those impact claims as LibreEvolve-supported workflows. Operational
  lifecycle proof is also open for the article's pilot-to-core status,
  regular next-generation-TPU tool use, Google Cloud/commercial availability,
  UI/API artifact inventory, rollout ownership, and release-note claim gates.
  Product-surface proof is separately open for the Google Cloud AlphaEvolve
  private-preview launch, AlphaEvolve Service API Early Access access model,
  Gemini Enterprise Pre-GA restricted-access docs, account-team documentation
  boundary, console/API/billing artifacts, customer availability, and managed-
  agent workflow semantics.
- Keep FHE-on-TPU AlphaEvolve application claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.14718`, `Adapting AlphaEvolve to Optimize Fully Homomorphic
  Encryption on TPUs`, cached locally as
  `papers/2605.14718__FHE_on_TPU.pdf`. This is background application context
  only; FHE scheme/primitive taxonomy, Google Cloud TPUv5e execution
  provenance, TFHE/Jaxite and CKKS/CROSS fixtures, correctness-test evidence,
  baseline implementation identity, generated-kernel artifacts, and latency
  reports for the 2.5x, 1.31x, and 1.18x speedup claims remain open before
  roadmap wording can promote FHE accelerator optimization as supported.
- Keep AlphaEvolve HCI/user-study claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.05921`, `Intentmaking and Sensemaking: Human Interaction with
  AI-Guided Mathematical Discovery`, cached locally as
  `papers/2605.05921__Intentmaking_and_Sensemaking.pdf`. This is background
  HCI context only; formative-study dataset evidence, participant/session
  trace schemas, intentmaking/sensemaking event taxonomies, UI/dashboard
  artifact inventories, goal-revision and human-intervention records,
  privacy/redaction protocol evidence, and local collaborative-workflow
  support remain open before roadmap wording can promote AlphaEvolve-style HCI
  workflows as supported.
- Keep AlphaEvolve radar power-allocation claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.01794`, `Discover Fast Power Allocation Solution for Multi-Target
  Tracking via AlphaEvolve Evolution`, cached locally as
  `papers/2605.01794__Radar_Power_Allocation.pdf`. This is background
  radar/resource-allocation context only; radar scenario/target taxonomy,
  physically inspired feature schemas, deterministic feasibility transforms,
  tracking simulator fixtures, baseline iterative solver identity, average
  relative performance-loss rows, generalization evidence, speedup reports,
  and independent reproduction outputs remain open before roadmap wording can
  promote radar resource-allocation support.
- Keep EvoX adaptive meta-evolution claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2602.23413`, `EvoX: Meta-Evolution for Automated Discovery`, cached
  locally as `papers/2602.23413__EvoX.pdf`. This is background
  meta-evolution context only; adaptive strategy-genome schemas, outer
  meta-evolution controller state, strategy-credit assignment, dynamic
  search-policy update artifacts, task-suite taxonomy, baseline comparison
  rows against AlphaEvolve/OpenEvolve/GEPA/ShinkaEvolve, token-efficiency
  reports, strategy ablation records, and independent reproduction outputs
  remain open before roadmap wording can promote EvoX-style adaptive search
  support.
- Keep DeltaEvolve semantic-delta context claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2602.02919`, `DeltaEvolve: Accelerating Scientific Discovery through
  Momentum-Driven Evolution`, cached locally as
  `papers/2602.02919__DeltaEvolve.pdf`. This is background context-memory
  framework evidence only; first-class semantic-delta schemas,
  node-transition effect attribution, semantic-delta memory banks,
  multi-level database/index metadata, progressive disclosure traces,
  token-savings reports, full-code-history baseline comparisons,
  scientific-task benchmark taxonomies, and independent reproduction outputs
  remain open before roadmap wording can promote DeltaEvolve-style context
  support.
- Keep MLEvolve long-horizon ML-engineering claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2606.06473`, `MLEvolve: A Self-Evolving Framework for Automated Machine
  Learning Algorithm Discovery`, cached locally as
  `papers/2606.06473__MLEvolve.pdf`. This is background long-horizon MLE
  context only; MLE-Bench harnesses, Progressive MCGS graph state,
  cross-branch reference-edge provenance, entropy-inspired schedules,
  Retrospective Memory knowledge-base/global-memory artifacts, adaptive
  coding-mode traces, 12-hour medal-rate/valid-submission reports,
  mathematical-algorithm baseline comparisons, linked-code audits, and
  independent reproduction outputs remain open before roadmap wording can
  promote MLEvolve-style ML-engineering support.
- Keep LEVI cost-aware search-architecture claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.09764`, `LEVI: Stronger Search Architectures Can Substitute for
  Larger LLMs in Evolutionary Search`, cached locally as
  `papers/2605.09764__LEVI.pdf`. This is background cost-aware
  search-architecture context only; diversity-preserving solution-database
  reports, large/small model mutation-router policy, role-assignment traces,
  rank-preserving proxy benchmark construction, rollout/provider-cost
  accounting, systems-research benchmark fixtures, prompt-optimization budget
  comparisons, linked-code audits, and independent reproduction outputs remain
  open before roadmap wording can promote LEVI-style cost-aware search support.
- Keep PACEvolve long-horizon consistency claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2601.10657`, `PACEvolve: Enabling Long-Horizon Progress-Aware Consistent
  Evolution`, cached locally as `papers/2601.10657__PACEvolve.pdf`. This is
  background long-horizon consistency context only; context-pollution
  detectors, hierarchical context-management/pruning artifacts, mode-collapse
  diagnostics, momentum-based backtracking controllers, unified
  crossover/backtracking samplers, trajectory-collaboration diagnostics,
  LLM-SR/KernelBench/Modded NanoGPT benchmark reports, linked-code audits, and
  independent reproduction outputs remain open before roadmap wording can
  promote PACEvolve-style consistency support.
- Keep FlashEvolve asynchronous-stage orchestration claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.08520`, `FlashEvolve: Accelerating Agent Self-Evolution with
  Asynchronous Stage Orchestration`, cached locally as
  `papers/2605.08520__FlashEvolve.pdf`. This is background async-stage
  orchestration context only; asynchronous worker queues, stage dependency
  schedulers, artifact-version lineage DAGs, stale-artifact detectors,
  staleness repair policies, speculative stage-completion records, adaptive
  workflow controllers, EvolBench/ChatDev/MetaGPT benchmark reports, 3.5x/4.9x
  throughput reproductions, linked-code audits, and independent reproduction
  outputs remain open before roadmap wording can promote FlashEvolve-style
  async orchestration support.
- Keep evolutionary-agent trace-diagnostic claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.20086`, `What Do Evolutionary Coding Agents Evolve?`, cached locally
  as `papers/2605.20086__Evolutionary_Coding_Agents.pdf`. This is background
  trace-diagnostic evaluation context only; EvoTrace-compatible trace schemas,
  nine-class edit-taxonomy annotation, LLM-as-judge/human reannotation
  validation, parent-child search graph exports, prompt/context substitution
  replay, model substitution replay, component-removal intervention harnesses,
  constant-retuning baselines, deleted-line reintroduction/cycling detectors,
  held-out generalization reports, and independent reproduction outputs remain
  open before roadmap wording can promote EvoTrace/EvoReplay-style evidence.
- Keep Zarankiewicz reinforced-search claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.01120`, `New Bounds for Zarankiewicz Numbers via Reinforced LLM
  Evolutionary Search`, cached locally as
  `papers/2605.01120__Zarankiewicz_Reinforced_Search.pdf`. This is an
  unimplemented constructive-math benchmark candidate; Zarankiewicz parameter
  manifests, bipartite graph construction schemas, `K_{s,t}`-free verifiers,
  exact-value/lower-bound tables, generated-algorithm artifact hashes,
  OpenEvolve setup provenance, reward-function specifications, upper-bound
  comparison ledgers, per-parameter cost accounting, and independent
  reproduction outputs remain open before roadmap wording can promote
  Zarankiewicz discovery support.
- Keep CORAL autonomous multi-agent evolution claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2604.01658`, `CORAL: Towards Autonomous Multi-Agent Evolution for
  Open-Ended Discovery`, cached locally as `papers/2604.01658__CORAL.pdf`.
  This is background autonomous multi-agent evolution context only;
  long-running autonomous agent sessions, shared persistent memory
  repositories, asynchronous multi-agent execution runtimes, heartbeat-based
  intervention controllers, isolated per-agent workspaces, evaluator
  separation layers, resource/session/health managers, knowledge-reuse
  analyses, 10-task SOTA reports, 3-10x improvement-rate reproductions,
  Anthropic kernel-engineering 1363-to-1103 cycle reproductions, linked-code
  audits, and independent reproduction outputs remain open before roadmap
  wording can promote CORAL-style autonomous multi-agent support.
- Keep AEvo harnessed meta-editing claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.13821`, `Harnessing Agentic Evolution`, cached locally as
  `papers/2605.13821__AEvo.pdf`. This is background harnessed meta-editing
  context only; process-level evolution state, meta-agent procedure or
  agent-context editors, standardized editable evolution workspaces,
  protected evaluator boundaries, searchable candidate histories for
  meta-editing, meta-editing phase/evolution-segment runners, run-plan
  contracts, procedure-versus-agent evolution instantiations, five-baseline
  agentic/reasoning benchmark reports, 26% relative-improvement
  reproductions, three-task open-ended optimization reports, linked-code
  audits, and independent reproduction outputs remain open before roadmap
  wording can promote AEvo-style harnessed meta-editing support.
- Keep G-Zero verifier-free co-evolution claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.09959`, `G-Zero: Self-Play for Open-Ended Generation from Zero Data`,
  cached locally as `papers/2605.09959__G_Zero.pdf`. This is background
  verifier-free co-evolution context only; Hint-delta intrinsic-reward
  computation, Proposer/Generator model roles, self-generated query/hint
  datasets, GRPO proposer training, DPO generator training, co-evolution
  training loops, pseudo-label noise filters, exploration-coverage reports,
  best-iterate suboptimality fixtures, unverifiable-domain benchmarks,
  external-judge reward-hacking comparisons, linked-code audits, and
  independent reproduction outputs remain open before roadmap wording can
  promote G-Zero-style verifier-free self-evolution support.
- Keep GenEvolve multimodal trajectory-distillation claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.21605`, `GenEvolve: Self-Evolving Image Generation Agents via
  Tool-Orchestrated Visual Experience Distillation`, cached locally as
  `papers/2605.21605__GenEvolve.pdf`. This is background multimodal
  trajectory-distillation context only; image-generation tool pipelines,
  visual-reference ingestion, prompt-rewriting/layout-planning/image-
  generation/refinement trajectory schemas, tool-call artifact lineage,
  Agentic Visual Experience Distillation/Visual Experience Distillation
  targets, dense token-level supervision records, multimodal policy-update
  loops, GenEvolve-Data metadata, GenEvolve-Bench reports, baseline
  comparisons, linked-code audits, and independent reproduction outputs remain
  open before roadmap wording can promote GenEvolve-style multimodal support.
- Keep EvoRubric self-evolving reward-rubric claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.29847`, `EvoRubric: Self-Evolving Rubric-Driven RL for Open-Ended
  Generation`, cached locally as `papers/2605.29847__EvoRubric.pdf`. This is
  background self-evolving reward-rubric context only; single-policy
  Reasoner/Rubric-Generator co-evolution loops, generated-rubric provenance,
  meta-verifier records, zero-variance pruning records, Leave-One-Out
  peer-consensus traces, criteria memory-pool artifacts, dense multi-objective
  reward-vector definitions, expert-prior rubric expansion, medical/writing/
  science benchmark reports, reward-hacking audits, linked-code audits, and
  independent reproduction outputs remain open before roadmap wording can
  promote EvoRubric-style reward-rubric support.
- Keep LLM-ALSO adaptive learning-signal claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.29293`, `LLM-ALSO: LLM-Driven Adaptive Learning-Signal Optimization
  for Multi-Agent Reinforcement Learning`, cached locally as
  `papers/2605.29293__LLM_ALSO.pdf`. This is background learning-signal
  optimization context only; sparse-reward cooperative MARL harnesses, Critic
  LLM diagnosis roles, Generator LLM reward-shaping roles, compact behavior
  evidence records, stage-specific coordination-failure diagnoses,
  reward-shaping configuration artifacts, branch-validation trajectories,
  validated-update promotion gates, main-training trajectory provenance,
  learning-efficiency reports, linked-code audits, and independent
  reproduction outputs remain open before roadmap wording can promote
  LLM-ALSO-style adaptive learning-signal support.
- Keep MemEvolve memory-architecture evolution claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2512.18746`, `MemEvolve: Meta-Evolution of Agent Memory Systems`, cached
  locally as `papers/2512.18746__MemEvolve.pdf`. This is background memory-
  architecture evolution context only; explicit encode/store/retrieve/manage
  memory-component design spaces, memory-architecture genotypes,
  memory-system mutation/evaluation loops, experiential-knowledge co-evolution
  traces, EvolveLab benchmark mappings, static-memory baseline comparisons,
  cross-task or cross-LLM transfer reports, performance-delta records,
  linked-code audits, and independent reproduction outputs remain open before
  roadmap wording can promote MemEvolve-style memory support.
- Keep ANCHOR healthy-evolution oversight claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2606.06114`, `Towards Healthy Evolution: Exploring the Role and Mechanisms
  of Human-Agent Interaction in Self-Evolving Systems`, cached locally as
  `papers/2606.06114__ANCHOR_Healthy_Evolution.pdf`. This is background
  healthy-evolution oversight context only; ANCHOR human-like oversight
  agents, phase-specific norm-correction interfaces, safety-drift metric
  lineages, output-verification intervention records, reflection/review
  artifact streams, supervision-frequency/cadence traces, preservation-of-
  objective-performance reports, coding/math/safety benchmark reports,
  linked-code audits, and independent reproduction outputs remain open before
  roadmap wording can promote ANCHOR-style human-like oversight support.
- Keep SIA harness-plus-weight self-improvement claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.27276`, `SIA: Self Improving AI with Harness & Weight Updates`,
  cached locally as `papers/2605.27276__SIA.pdf`. This is background harness-
  plus-weight self-improvement context only; Feedback-Agent decision logs,
  editable task-agent harness inventories, harness patch/version records,
  online RL/fine-tuning loops, adapter/checkpoint lifecycles, training-data
  lineage, rollback/resume policies, harness-only versus weight-only versus
  combined ablation reports, LawBench/kernel/scRNA benchmark records,
  compute/cost telemetry, linked-code audits, and independent reproduction
  outputs remain open before roadmap wording can promote SIA-style harness-
  plus-weight self-improvement support.
- Keep HarnessFix trace-grounded harness repair claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2606.06324`, `From Failed Trajectories to Reliable LLM Agents:
  Diagnosing and Repairing Harness Flaws`, cached locally as
  `papers/2606.06324__HarnessFix.pdf`. This is background trace-grounded
  harness repair context only; HTIR trace-normalization schemas, raw-trace
  normalization records, harness-code linkage, step-level provenance,
  execution/tool/context/lifecycle/observability/verification/governance
  harness-layer attribution taxonomies, recurring flaw records, scoped
  repair-operator definitions, generated harness patch artifacts, flaw-
  specific validation specs, unacceptable-regression threshold records,
  held-out SWE-Bench Verified/Terminal-Bench 2.0 Verified/GAIA/AppWorld
  benchmark reports, linked-code audits, and independent reproduction
  outputs remain open before roadmap wording can promote HarnessFix-style
  trace-grounded harness repair support.
- Keep RHO retrospective harness-optimization claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2606.05922`, `Retrospective Harness Optimization: Improving LLM Agents via
  Self-Preference over Trajectory Rollouts`, cached locally as
  `papers/2606.05922__RHO.pdf`. This is background retrospective harness
  optimization context only; past-trajectory corpus schemas, hard/diverse
  coreset criteria, DPP coreset records, retrospective rollout batches,
  parallel re-solve provenance, self-validation and self-consistency
  diagnostics, candidate harness-update artifacts, pairwise self-preference
  rankings, label-free selection policies, deployment/rollback metadata,
  behavior-pattern shift reports, long-horizon accuracy records, SWE-Bench Pro
  benchmark records, linked-code audits, and independent reproduction outputs
  remain open before roadmap wording can promote RHO-style retrospective
  harness optimization support.
- Keep harness-updating versus harness-benefit claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.30621`, `Harness Updating Is Not Harness Benefit: Disentangling
  Evolution Capabilities in Self-Evolving LLM Agents`, cached locally as
  `papers/2605.30621__Harness_Updating_Is_Not_Harness_Benefit.pdf`. This is
  background harness-capability disentanglement context only; harness-updating
  metric schemas, harness-benefit metric schemas, evolver-versus-task-solver
  model-pair matrices, capability-tier grouping records, cross-benchmark
  harness self-evolution reports, activation-failure audits, adherence-failure
  audits, capability-budget recommendation reports, public-code snapshot
  audits, and independent reproduction outputs remain open before roadmap
  wording can promote separate harness-updating or harness-benefit support.
- Keep AHE observability-driven harness-evolution claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2604.25850`, `Agentic Harness Engineering: Observability-Driven Automatic
  Evolution of Coding-Agent Harnesses`, cached locally as
  `papers/2604.25850__AHE.pdf`. This is background agentic harness
  observability context only; file-level editable harness component graphs,
  component-observability schemas, layered drill-down trajectory evidence
  corpora, raw-trace-to-digest provenance, decision-observability prediction
  contracts, next-round falsification records, per-edit rollback manifests,
  ten-iteration Terminal-Bench 2 reports, SWE-bench-verified transfer reports,
  cross-family transfer reports, tools/middleware/memory ablations,
  public-code snapshot audits, and independent reproduction outputs remain
  open before roadmap wording can promote AHE-style observability-driven
  harness evolution support.
- Keep AI Harness Engineering runtime-substrate claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.13357`, `AI Harness Engineering: A Runtime Substrate for
  Foundation-Model Software Agents`, cached locally as
  `papers/2605.13357__AI_Harness_Engineering.pdf`. This is background AI
  harness runtime-substrate context only; complete eleven-responsibility
  harness contracts, H0-H3 harness-ladder fixtures, trace-based episode-
  package schemas, controlled validation-task reproductions,
  model-harness-environment capability equation records, failure-attribution
  taxonomy reports, deterministic requirement-check packages, structured
  verification reports, public-code snapshot audits, and independent
  reproduction outputs remain open before roadmap wording can promote AI
  Harness Engineering runtime-substrate support.
- Keep inference-time trajectory-alignment harness claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2605.21516`, `Harnesses for Inference-Time Alignment over Execution
  Trajectories`, cached locally as
  `papers/2605.21516__Inference_Time_Trajectory_Alignment.pdf`. This is
  background inference-time trajectory-alignment context only; decomposition
  versus guided-execution parameterizations, workflow-granularity sweeps,
  retry-budget studies, guidance-induced action-reweighting reports,
  stage-level gap metrics, over-decomposition/over-pruning/hallucinated-
  execution failure reports, partial-harnessing stopping rules, controlled
  synthetic experiments, terminal-agent benchmark reproductions, linked-code
  audits, and independent reproduction outputs remain open before roadmap
  wording can promote inference-time trajectory-alignment harness support.
- Keep Adaptive Auto-Harness open-ended task-stream claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2606.01770`, `Adaptive Auto-Harness: Sustained Self-Improvement for
  Agentic System Deployment on Open-Ended Task Streams`, cached locally as
  `papers/2606.01770__Adaptive_Auto_Harness.pdf`. This is background
  adaptive auto-harness deployment context only; chronological open-ended
  task-stream schemas, history-growth records, task-heterogeneity reports,
  distribution-shift detectors, evolution-loss/adaptation-loss decompositions,
  stateful multi-agent evolvers, harness trees, solve-time routing policies,
  human-steering hooks, overfitting/accuracy-peak-decline reports,
  prediction-market/security-competition/event-forecasting benchmark
  reproductions, five-baseline comparisons, linked-code audits, and
  independent reproduction outputs remain open before roadmap wording can
  promote sustained Adaptive Auto-Harness deployment support.
- Keep Meta-Harness outer-loop harness-code optimization claims source-scoped:
  `papers/download_manifest.*` and `papers/README.md` now include arXiv
  `2603.28052`, `Meta-Harness: End-to-End Optimization of Model
  Harnesses`, cached locally as `papers/2603.28052__Meta_Harness.pdf`.
  This is background outer-loop harness-code optimization context only;
  harness-code candidate schemas, filesystem-visible harness workspaces,
  agentic proposer traces, execution-trace feedback bundles,
  score/provenance replay packages, outer-loop harness search controllers,
  online text-classification reproductions, 200-problem IMO-level
  retrieval-augmented math reproductions, TerminalBench-2 reproductions,
  held-out-model transfer reports, linked-code audits, and independent
  reproduction outputs remain open before roadmap wording can promote
  Meta-Harness-style end-to-end harness optimization.
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
  HTML page boundary. It now classifies page 68 as an extra numbered
  duplicate-title `Logic puzzles` page outside the declared 67-page navigation
  range, records all-page resource-link diagnostics (`36` GitHub notebook blob
  URLs, `6` direct Google Colab URLs, `25` under-construction Colab
  placeholders, `1` generic Colab landing URL, and `1` paper-link placeholder),
  pins raw-page byte counts and SHA-256 hashes for all 68 numbered HTML pages,
  emits per-page source rows with titles, paper sections, page URLs, hashes,
  link-status diagnostics, status-bucket labels, notebook-link mappings, and
  notebook absence reasons, and links to the runtime-absence notebook
  inventory with 28 pinned notebook paths and scoped prompt/verifier/initial/
  final/visualization artifact flags. Full notebook cell inventories remain
  outside the claim.
- Keep Appendix A matrix target-suite curation scoped to reported-suite
  provenance: `libreevolve.alphaevolve_appendix_a_matrix_curation.v1` now
  validates the rough size-selection wording, sorted representative policy,
  axis-permutation equivalent omissions, included-target rationales, and
  unspecified `p` cutoff. `papers/appendix_a_matrix_curation.json` now emits
  this reported-suite curation record as a committed sidecar.
  `libreevolve.alphaevolve_appendix_a_matrix_excluded_target_curation_boundary.v1`
  now validates the current `not_recorded_locally` boundary and required
  future fields for excluded target ids, dimensions, exclusion class/reason,
  source basis, rough-rule and `p`-cutoff relations, symmetry-equivalence
  status, local attempt/resource-frontier refs, artifact paths, and hashes,
  and `papers/appendix_a_matrix_excluded_target_curation.json` emits that
  boundary as a committed sidecar.
  `appendix_a_matrix_excluded_target_curation_boundary_from_records()` builds
  recorded boundaries from supplied excluded-target justifications over a
  declared scope. Explicit broad non-equivalent excluded-target justifications
  remain open.
- Keep Appendix A best-known-rank citation claims scoped:
  `libreevolve.alphaevolve_appendix_a_matrix_baseline_citation_boundary.v1`
  now validates the committed
  `papers/appendix_a_matrix_baseline_citations.json` sidecar for per-target
  Table 3 best-known-rank references, including source table/page, source
  artifact path/hash, applicability caveats, field/characteristic scope, and
  report-visible baseline-source refs.
  `appendix_a_matrix_baseline_citation_boundary_from_citations()` builds
  recorded boundaries from supplied citation rows and validates registry rank,
  dimension, target-id, and report-source-ref linkage. Local matrix reports
  still need to attach those baseline-source records automatically.
- Keep matrix target-scaling claims scoped to paper-source frontier evidence:
  `libreevolve.alphaevolve_appendix_a_matrix_resource_frontier.v1` now
  validates the Appendix A page 34 boundary for sizes beyond `<5,5,5>`, 1000
  random seeds, single-GPU evaluators, frequent OOM, and further-optimization
  need, and `papers/appendix_a_matrix_resource_frontier.json` emits that
  paper-only boundary as a committed sidecar.
  `libreevolve.alphaevolve_appendix_a_matrix_local_resource_frontier.v1`
  now validates the local absence/readiness boundary and required fields for
  future attempted target sizes, measured GPU memory, OOM artifacts,
  reduced-seed tradeoffs, and exclusion rationale.
  `papers/appendix_a_matrix_local_resource_frontier.json` emits that local
  absence boundary as a committed sidecar. Actual local scaling runs remain
  open.
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
  and artifact hashes.
  `papers/matrix_baseline_component_runtime_boundary.json` now emits that
  absence/readiness boundary as a committed sidecar.
  `matrix_baseline_component_runtime_boundary_from_components()`
  builds emitted records from component inventories and validates top-level
  ref, mutable-scope, and fixed-hash linkage. Local benchmark runners still
  need to emit those baseline component records.
- Keep matrix repeated-seed wording scoped to result reports versus executed
  cascade traces: `libreevolve.matrix_cascade_run_runtime_boundary.v1` now
  validates the current `not_emitted_by_local_runner` boundary and emitted
  per-seed records for run/target/seed ids, cascade ids and versions, stage
  traces with threshold/rank/exactness/stop diagnostics, accepted final rank,
  candidate and matrix-result refs, artifact paths, and artifact hashes.
  `papers/matrix_cascade_run_runtime_boundary.json` now emits that
  absence/readiness boundary as a committed sidecar.
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
  `papers/matrix_near_integrality_runtime_boundary.json` now emits that
  absence/readiness boundary as a committed sidecar.
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
  `papers/matrix_scalar_field_runtime_boundary.json` now emits that
  absence/readiness boundary as a committed sidecar.
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
  hashes. `papers/matrix_tensor_rank_runtime_boundary.json` now emits that
  absence/readiness boundary as a committed sidecar.
  `matrix_tensor_rank_runtime_boundary_from_evidence()` builds an
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
  `papers/matrix_suite_publication_artifacts.json` now emits that
  absence/readiness boundary as a committed sidecar.
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
  `papers/matrix_sweep_space_runtime_boundary.json` now emits that
  absence/readiness boundary as a committed sidecar.
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
  and kernel reports must pass held-out gates, ready compiler and hardware
  reports must pass reference-correctness gates, and generic ready systems
  reports must pass both held-out and reference-correctness gates rather than
  using generic `not_applicable` rationales. Ready scheduling reports
  also require `scheduling_formulation` records for vector-bin-packing setup,
  CPU/memory dimensions, workload/capacity snapshots, stranded-resource
  objective, feature mapping, simulator hashes, and artifact refs, plus
  `scheduling_safety` records for feasible candidate-set source, ranking-only
  scope, simulator/admission/placement boundaries, resource invariants, and
  safety artifact refs. Ready scheduling reports also require
  `scheduling_deployment_readiness` records for interpretable heuristic
  structure, operator/debug review, predictability checks, deployment
  ergonomics, rollout-risk controls, and less-interpretable learned-policy
  comparison. Ready compiler reports also require `compiler_ir_provenance`
  with IR origin/editability boundaries, compiler-generated baseline
  provenance, reference implementation and randomized input-generator hashes,
  numerical tolerance policy, final expert-confirmation scope, and per-edit
  randomized reference-check records. They also require
  `compiler_stack_provenance` for FlashAttention/Pallas/JAX/XLA context:
  workload/model configuration, kernel identity, JAX pre/postprocessing
  boundaries, XLA lowering stage, hardware target, lowered-IR hash,
  optimization decision category, and artifact refs. Ready compiler reports
  also require `compiler_adoption_provenance` to classify existing-compiler
  bounded-use-case adoption versus AlphaEvolve-in-the-compiler-workflow
  integration, with target compiler/pass, optimization artifact hash,
  integration owner, reviewer scope, rollout/revert state, workflow handoff,
  and artifact refs.
  `papers/compiler_ir_reference_check_boundary.json` now preserves the
  compiler-IR metadata-versus-artifact boundary, so per-edit reference-check
  metadata cannot stand in for candidate edit sequences, randomized input
  coverage, reference-check outputs, tolerance/failure logs, or expert
  all-input signoff files.
  `papers/compiler_stack_context_boundary.json` separately preserves the
  FlashAttention/Pallas/JAX/XLA stack boundary, so compiler-stack metadata
  cannot stand in for workload/model records, Pallas source, JAX wrappers,
  XLA stage outputs, hardware-target records, lowered IR, or decision evidence.
  `papers/compiler_adoption_path_boundary.json` preserves the adoption-path
  boundary, so compiler-adoption metadata cannot stand in for compiler
  patch/pass artifacts, use-case integration records, reviewer signoff files,
  rollout/revert logs, workflow-handoff artifacts, or AlphaEvolve-in-compiler
  workflow integration evidence.
  Ready hardware reports now require
  `hardware_rtl_eda_provenance` with HDL/RTL source boundaries, synthesis/PPA
  provenance, timing/power/area constraints, equivalence/formal verification,
  designer validation, downstream synthesis confirmation, RTL-flow placement,
  standard-language adoption rationale, integration target, deployment impact,
  hashes, confirmation flags, and artifact refs. They also require
  `hardware_rewrite_provenance` for the concrete TPU arithmetic-circuit
  rewrite: before/after Verilog hashes, diff hash, component and matrix-unit
  context, semantic rewrite category, changed spans, removed-bit inventory,
  PPA linkage, verification linkage, and artifact refs. They also require
  `hardware_contribution_provenance` for the broader Gemini-to-TPU attribution
  claim: model-family relationship, AlphaEvolve run/backend identity, TPU
  generation, circuit identity, novelty basis, first-direct-contribution
  scope, integration milestone, hardware review scope, synthesis rediscovery
  distinction, confirmation flags, and artifact refs.
  `papers/systems_result_readiness_boundary.json` now preserves the manifest-
  checked boundary that those schemas and validators are report contracts
  without real emitted scheduling, kernel, compiler, or hardware fixture runs,
  deployment measurements, expert confirmations, or domain-specific result
  artifacts. That boundary now also marks Figure 6 scheduling-heuristic
  heatmap artifacts and Figure 7 Pallas-tiling diagram artifacts as required
  but missing engineering-exhibit evidence.
  `papers/figure6_scheduling_exhibit_boundary.json` now preserves the more
  specific Figure 6 scheduling-exhibit contract: stable exhibit ID, exact
  heuristic source/hash, residual feature/unit definitions, heatmap data and
  rendering parameters, rendered artifact hashes, baseline heuristic identity,
  simulator/held-out/deployment links, resource-recovery denominator/window,
  and readiness linkages. Real scheduling resource recovery,
  kernel/training-time speedup, RTL PPA, compiler speedup fixtures, emitted
  compiler-stack artifacts, real compiler adoption/integration artifacts, real
  hardware RTL/EDA artifacts, real hardware rewrite artifacts, and real
  Gemini-to-TPU attribution artifacts still need to populate those records.
  `papers/figure7_pallas_tiling_exhibit_boundary.json` similarly preserves
  the Figure 7 Pallas tiling-exhibit contract: stable exhibit ID, matrix
  product and dimension definitions, tile-parameter schema, Pallas kernel
  identity, accelerator/memory/fusion/compiler context, diagram data and
  rendering artifacts, baseline tiling heuristic identity, shape-corpus and
  runtime links, train/eval linkage, claim calibration, and systems-readiness
  linkage. `papers/kernel_tiling_shape_corpus_boundary.json` preserves the
  related runtime-evidence boundary for Pallas/Gemini kernel results: collected
  input-shape corpora, deterministic train/eval splits and hashes, real
  accelerator runtime artifacts, expert baseline tiling heuristics,
  tiling-only output constraints, unchanged-kernel-math proof, and
  shape-corpus-to-runtime joins remain missing.
- For Pallas/Gemini kernel fixtures, populate workflow-baseline evidence before
  claiming AlphaEvolve-style automation of tiling-heuristic work: distinguish
  search-based autotuning, manual heuristics, and expert-hybrid baselines;
  record retuning burden for input-shape changes, manual authoring/review
  effort, hardware-expertise assumptions, and model-developer ergonomics.
  `papers/pallas_workflow_baseline_boundary.json` now preserves this as a
  separate paper-facing boundary, so Pallas runtime or shape-corpus evidence
  cannot stand in for workflow-baseline evidence.
- For Gemini self-training claims, add a Pallas deployment-loop evidence row
  before describing kernel deployment as AlphaEvolve-style optimization of
  Gemini's own training pipeline: model/training workload identity,
  AlphaEvolve backend or Gemini-family relation, optimized Pallas kernel id,
  production rollout state, before/after training-time and kernel-runtime
  evidence, team-velocity evidence, and rollback/safety status.
  `papers/gemini_self_training_loop_boundary.json` now preserves this as a
  separate paper-facing boundary, so ordinary Pallas deployment evidence cannot
  stand in for Gemini self-optimization evidence.
- Populate real hardware-adoption and rewrite evidence for TPU RTL-style
  reports before claiming Section 3.3.3 parity: emitted RTL, before/after
  Verilog diffs, removed-bit inventories, synthesis/PPA, verification,
  designer-signoff, downstream-synthesis, upcoming-chip integration, Gemini/
  AlphaEvolve attribution review, firstness/novelty evidence, and
  time-to-market artifacts in addition to report metadata.
  `papers/hardware_rtl_eda_evidence_boundary.json` now preserves the
  metadata-versus-real-artifact boundary for RTL/EDA evidence, so validated
  hardware report fields cannot stand in for emitted Verilog, PPA,
  verification, signoff, synthesis, integration, or deployment-impact
  artifacts. `papers/hardware_rewrite_artifact_boundary.json` separately
  preserves the concrete rewrite-artifact boundary, so before/after Verilog
  hashes and removed-bit metadata cannot stand in for source files, diff/AST
  artifacts, removed-signal inventories, or per-bit PPA/verification links.
  `papers/hardware_contribution_attribution_boundary.json` now preserves the
  Gemini-to-TPU attribution boundary, so `hardware_contribution_provenance`
  metadata cannot stand in for model/run/backend records, reviewed TPU/circuit
  identifiers, firstness review, integration milestones, hardware signoff, or
  synthesis-rediscovery audit artifacts.
- Add self-improvement evidence boundaries before claiming AlphaEvolve-style
  infrastructure or base-model uplift: component identity, before/after
  measurements, deployment/adoption status, rollback/safety review, provenance
  tying the candidate to LibreEvolve's own execution path, and any
  distillation dataset/training/evaluation artifacts. The committed
  `papers/self_improvement_distillation_boundary.json` sidecar keeps those
  Discussion claims scoped as context only, while
  `papers/self_improvement_cadence_boundary.json` separately guards
  months-scale feedback-loop cadence and environment-ROI claims.
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
  produces those reports or rendered exhibit artifacts yet. The committed
  `papers/figure8_ablation_artifacts.json` sidecar now emits that
  absence/readiness boundary for paper-manifest validation.
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
  `papers/figure9_matrix_diff_artifacts.json` now emits that
  absence/readiness boundary as a committed sidecar.
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
  `papers/figure4_matrix_discovery_artifacts.json` now emits that
  absence/readiness boundary as a committed sidecar.
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
  `papers/matrix_headline_historicity_artifacts.json` now emits the
  paper-facing rank-48 headline historicity sidecar with nested evidence,
  source refs, prior comparisons, evidence links, artifact path, and digest.
  `libreevolve.matrix_headline_historicity_runtime_boundary.v1` now validates
  that emitted sidecar and emitted records for run/target/candidate ids,
  dimensions, headline rank/field values, source refs, prior comparisons,
  evidence links, matrix-result refs, artifact paths, and artifact hashes.
  `matrix_headline_historicity_runtime_boundary_from_evidence()` builds an
  emitted runtime row from validated headline evidence and validation links it
  back to nested target, dimensions, headline claim, source refs, prior
  comparisons, evidence links, and matrix-result provenance. Local runners
  still do not automatically attach that sidecar to matrix run outputs.
- Keep matrix outcome claims scoped to named target subsets:
  `libreevolve.alphaevolve_matrix_subset_scope.v1` now validates
  `appendix_a_full`, `main_text_mnp_le_5`, and `table_2_selected` membership,
  outcome counts, out-of-scope rows, and Table 2/Table 3 source linkage. The
  scoped `m,n,p <= 5` subset has `20` rows with `0` fell behind, while the full
  Appendix A table has `54` rows with `2` fell behind. The committed
  `papers/appendix_a_matrix_subset_scope_artifacts.json` sidecar now emits the
  three subset-scope artifacts with nested subset evidence, artifact path, and
  SHA-256 digests.
  `libreevolve.alphaevolve_matrix_subset_scope_artifact_boundary.v1` now
  validates the emitted sidecar and required artifact fields for subset
  identity, inclusion predicates, source linkage, counts, fell-behind/
  out-of-scope ids, nested subset-scope evidence, artifact paths, and hashes.
  `appendix_a_matrix_subset_scope_artifact_boundary_from_records()` builds
  emitted artifacts from validated subset-scope evidence and validation checks
  nested evidence linkage. Runtime reports and rendered table artifacts still
  need automatic subset-scope attachment.
- Keep Appendix A matrix row-note claims scoped to declared evidence:
  `libreevolve.alphaevolve_appendix_a_matrix_row_notes.v1` now validates the
  `mm_4x5x6` concurrent-work note that reference `[49]` also found a rank-90
  algorithm for `<4, 5, 6>`, including source page/table, rank relationship,
  and a non-exclusive-priority docs caveat. The committed
  `papers/appendix_a_matrix_row_note_artifacts.json` sidecar now emits that
  caveat artifact with nested row-note evidence, artifact path, and SHA-256
  digest.
  `libreevolve.alphaevolve_appendix_a_matrix_row_note_artifact_boundary.v1`
  now validates the emitted sidecar and required artifact fields for note
  identity, target/rank/reference values, source text, caveat flags, nested
  row-note evidence, artifact paths, and hashes.
  `appendix_a_matrix_row_note_artifact_boundary_from_records()` builds emitted
  artifacts from validated row-note evidence and validation checks nested
  evidence linkage. Runtime reports and rendered table artifacts still need to
  attach that row-note caveat automatically.
- Keep Table 2/Table 3 matrix-rank claims scoped to declared exhibit evidence:
  `libreevolve.alphaevolve_matrix_rank_table_exhibit.v1` now validates stable
  table ids, selected/full-table membership, row ordering, rank values, outcome
  counts/color semantics, complex-row annotations, concurrent-note linkage,
  rendered/source/OCR artifact hashes, and registry/subset/row-note/Colab
  links. Runtime reports still do not render or emit those table artifacts.
  `papers/matrix_rank_table_artifacts.json` now emits the Table 2/Table 3
  paper-table artifact sidecar. The companion
  `libreevolve.alphaevolve_matrix_rank_table_artifact_boundary.v1` validates
  that emitted sidecar and required artifact fields for table identity, source
  locations, rendered/OCR/source files, artifact paths/hashes, and nested
  table-exhibit evidence. `matrix_rank_table_artifact_boundary_from_exhibit()`
  builds emitted Table 2/Table 3 artifact records from validated exhibit
  metadata and validation checks nested table linkage. Runtime reports still
  do not automatically attach those table artifacts.

### 10. Operational maturity

- Extend current config validation beyond the
  `papers/config_validation_boundary.json` local effective-config boundary to
  plugin-specific schemas and provider/model API compatibility where feasible.
- Extend strict finite JSONL coverage and diagnostics beyond current
  candidate, prompt, manifest, and GRPO-export writers as new run artifacts are
  added.
- Improve run inspection beyond the current validity/archive-aware selected-row
  `show` view, streamed history source/workspace validation, bounded runtime
  summaries, and manifest-level whole-run source/workspace integrity report
  with `papers/whole_run_source_workspace_integrity_boundary.json`
  preserving the paper-facing absence boundary
  toward richer archive/prompt/failure drill-downs, durable query views over run
  artifacts, full source-payload replay, and cross-run source/workspace
  indexes.
- Extend current `pyproject.toml` metadata, dev extras, console-script
  packaging, and CI wheel/sdist/install smoke beyond smoke validation with
  signed release provenance, maintainer-approved release evidence, and index
  verification.
- Extend the current path-scoped GitHub Actions workflow beyond secret scan,
  Python 3.11/3.12 cross-platform non-integration tests, optional integration
  tests, and the committed-manifest paper/docs verifier suite and
  release-artifact smoke CI jobs with local-PDF paper-manifest checks where
  appropriate, fully semantic docs-claim verification, signed release
  provenance, cross-platform paper/docs, release, and integration coverage, and
  notification-safe trigger and branch policy. The current paper-facing CI
  boundary is tracked by
  `papers/ci_workflow_coverage_boundary.json`.

## Non-Goals For Now

- Requiring a service database for normal local use.
- Claiming arbitrary-language/codebase support before runners and validators
  exist.
- Advertising paper-inspired plugins as faithful implementations.

## Good First Follow-Ups

1. Persist database query indexes beyond run-local metric/novelty/lineage/
   feedback/artifact/exact program-output resurfacing. The current artifact
   scope is bounded metadata and excerpts, tracked by
   `papers/artifact_index_boundary.json`, not durable full-content or semantic
   artifact search.
2. Add one non-toy benchmark run fixture with expected artifacts.
3. Add workspace resume coverage beyond current `best_workspace/` export.
4. Emit real LLM feedback calibration reports and grader ablation fixtures.
