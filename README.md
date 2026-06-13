# LibreEvolve

LibreEvolve is a Python research prototype for LLM-guided evolutionary program
discovery. It takes a problem directory, asks configured LLM backends to propose
code mutations, evaluates the resulting candidates, and keeps the best programs
in a small quality-diversity archive.

It is inspired by AlphaEvolve, Karpathy's `autoresearch`, MAP-Elites, and recent
work on LLM-guided program search. It is an independent project and is not
affiliated with or endorsed by Google DeepMind or the authors of the cited
papers.

## Status

This is an alpha-stage research codebase, not a production optimizer and not a
full AlphaEvolve reproduction.

Implemented today:

- Python-primary candidate workspaces and seed programs.
- SEARCH/REPLACE diff mutations using the AlphaEvolve fence format.
- Full-code replacement mode when configured.
- OpenAI, Anthropic, and Ollama backend adapters.
- A heuristic UCB-style backend selector.
- Synchronous MAP-Elites and island archives, with five islands by default.
- Local subprocess evaluation with staged validator support.
- Optional critique, feedback, and plugin hooks.
- Run artifacts under `runs/`, including manifests, histories, prompts,
  failures, best candidates, and plugin/evaluator artifacts.

Important limits:

- Evaluators run in local subprocesses, not hardened security sandboxes.
- The controller, archive, migration, and evaluator flow are local and
  synchronous, not a distributed asynchronous AlphaEvolve-style service.
- Figure 1/Figure 2 process-exhibit reports map AlphaEvolve diagram nodes,
  edges, and pseudocode steps to local artifacts, not exact source-diagram
  reproduction, async controller/sampler/evaluator topology, independent
  evaluator-pool implementation, or full process parity; that boundary is
  tracked by `papers/process_exhibit_boundary.json`.
- Existing-codebase integration reports inventory runtime Python EVOLVE-block
  marker spans and optional source-setup metadata, not AlphaEvolve-style
  minimal-change integration with identified upstream releases, pre-marker
  hashes, marker-only setup diffs, evaluator-call continuity, portable
  source-root identity, or setup-change counts; that boundary is tracked by
  `papers/existing_codebase_integration_boundary.json`.
- Workspace topology and materialization diagnostics cover local file-workspace
  path/case-folding/source-copy preflights, topology-command validation, and
  prompt-visible `materialization_error` summaries, not arbitrary-language or
  build-runner artifacts, dependency-graph validation, bulk directory or
  external-path operations, remote/container workspaces, or codebase-scale
  workspace parity.
- Codebase-scale reports are current-run workspace telemetry for retained
  file/line counts, generated candidates, multi-file and hundreds-line
  observations, and parent-relative edits, not realistic multi-component
  benchmark fixtures, coupled cross-file dependency edits, arbitrary-language
  or build-runner execution, long-horizon quality progress, retained-rate
  benchmark summaries, or AlphaEvolve Table 1 code-scale parity; those
  boundaries are tracked by `papers/codebase_scale_benchmark_boundary.json`
  and `papers/candidate_language_runner_boundary.json`.
- Table 1 capability-exhibit reports preserve FunSearch-versus-AlphaEvolve
  row text, source location, rendered artifacts, row-to-gap mappings, and
  implementation status, not validated parity for the individual code-scale,
  language, evaluator, sample-count, model-scale, prompt-context, or
  multi-metric capability rows.
- Task-specification bundles, `task_specification.json`, and artifact-
  resolution reports link initial programs, evaluators, prompts, backends,
  context, candidate representation, metrics, history streams, best exports,
  marked spans, and supported embedded score causality, not external-validator
  score causality, arbitrary-language/build-runner task specs, user-authored
  standalone task-spec parity, or full AlphaEvolve task-spec parity; that
  boundary is tracked by `papers/task_specification_boundary.json`.
- Archive restore uses manifest archive-state snapshots plus accepted-history
  rows for current cursor/cell/elite contents; `archive_events.jsonl` replay is
  audit-only and not an ordered MAP-Elites restore engine. That boundary is
  tracked by `papers/archive_event_replay_boundary.json`.
- Scientific-discovery scope is machine-gradeable local evaluator workflow
  scope; robust evaluator-environment fixtures, manual-to-code transition
  policies, and LLM-only idea-stage contracts are tracked by
  `papers/automated_evaluator_scope_boundary.json`.
- Evaluation-cascade reports are runtime attrition and promotion telemetry when
  stages run, not AlphaEvolve-style cascade-efficiency evidence with stage
  difficulty rationale, evaluator/test-set identities and hashes, benchmark
  seed/sample policy, counterfactual full-evaluation costs, or observed
  wall-clock cost savings; that boundary is tracked by
  `papers/evaluation_cascade_boundary.json`.
- Cascade hypothesis-test gates are runtime policy evidence, not
  benchmark-calibrated AlphaEvolve Section 2.4 cascade proof with repeated-seed
  fixtures and empirical false-promotion/false-rejection validation; that
  boundary is tracked by `papers/cascade_hypothesis_test_boundary.json`.
- Evaluator/oracle reports register local validators, configured cascade
  stages, and optional LLM feedback graders with arbitration metadata, not
  independent reference/statistical-oracle evidence, benchmark sufficiency
  proof, independent disagreement outcomes, or cross-run oracle tables; that
  boundary is tracked by `papers/evaluator_oracle_boundary.json`.
- Evaluator workload metadata and `runtime.history.evaluator_workload_report`
  record declared `simple_check`, `inner_search`, `ml_training`, and `custom`
  stage provenance, not managed workload-specific training/search runners,
  checkpoint completeness, score-field-to-artifact causality, or stochastic
  re-evaluation policy.
- Embedded evaluator support is opt-in `embedded_evaluate` stage evidence, not
  full AlphaEvolve Figure 3 evaluator parity with default candidate-owned
  `evaluate(eval_inputs)` problem loading, stronger build/runtime isolation, or
  non-static/external-validator score linkage; that boundary is tracked by
  `papers/embedded_evaluator_boundary.json`.
- Validator execution policy records are local-subprocess audit evidence:
  `policies.validator_execution`, `evaluation.metadata.validator_boundary`,
  `filesystem_capabilities`, and `resource_limit_policy` declare the current
  temporary subprocess boundary, candidate-root/declared-file filesystem
  scope, optional Python-socket denial metadata, wall-clock timeout cleanup,
  unsupported security sandbox/container status, and unsupported CPU, memory,
  GPU, disk, and process-count quotas. They are not OS/container sandboxing,
  OS-enforced filesystem capabilities, kernel/container network isolation, or
  AlphaEvolve-scale resource-limit enforcement.
- Execution-grounding and incorrect-suggestion reports are local run telemetry
  over accepted, rejected, execution-filtered, invalid-evaluation, parse-error,
  archive-rejected, and accepted-invalid candidates, not independent rejudge
  coverage, audited false-acceptance/false-rejection rates, semantic failed-
  proposal retrieval, or publication-strength filtering proof; that boundary
  is tracked by `papers/incorrect_suggestion_audit_boundary.json`.
- Hypothesis-branch and controller-backtracking reports show abandoned-looking
  branches and observed redirects, not controller-owned backtracking policy
  with configured suppression/retry behavior, explicit fallback-target events,
  causal resumed-search replay, or cross-run branch tables; that boundary is
  tracked by `papers/controller_backtracking_boundary.json`.
- Qualitative LLM-feedback records are declared criterion/rubric/intent
  provenance and prompt-history audit evidence, not executed calibration,
  task-suite, ablation, or independent feedback-quality validation; that
  boundary is tracked by `papers/qualitative_feedback_boundary.json`.
- Feedback calibration artifacts are schema/report contracts, not runtime
  calibration runners, executed task-suite results, grader ablations, or
  independent feedback-quality validation; that boundary is tracked by
  `papers/feedback_calibration_boundary.json`.
- Role-scoped LLM scheduling is opt-in local UCB/runtime evidence with
  reward-accounted roles, role budget maps, scheduler-state snapshots, and
  per-call policy telemetry, not calibrated AlphaEvolve role reward policy,
  experiment-owned quota policy, fast/strong model-mix reports, or
  role-specific budget behavior reports; that boundary is tracked by
  `papers/llm_role_scheduler_boundary.json`.
- `throughput_depth` backend selection records cost/latency/depth metadata and
  fast-breadth/strong-depth lane labels, not experiment-level fast/strong
  model-mix validation, reserved lane policy, candidate throughput/quality
  outcomes, or equal-budget scheduler comparisons; that boundary is tracked by
  `papers/fast_strong_model_mix_boundary.json`.
- Natural-language proposal metadata is context around executable code
  candidates, not AI-Co-Scientist-style hypothesis representation or
  hallucination-resistance evidence; that boundary is tracked by
  `papers/programmatic_representation_boundary.json`.
- Natural-language preambles are bounded leading metadata before structured
  mutation markers, not complete freeform rationale handling; that boundary is
  tracked by `papers/natural_language_preamble_boundary.json`.
- Prompt example-copy reports are built-in exact/normalized/skeleton
  diagnostics, not hard rejection, semantic-copy detection, or custom-template
  inventory evidence; that boundary is tracked by
  `papers/prompt_example_copy_boundary.json`.
- Multi-edit consistency reports are current-run diagnostics, not proof that
  accepted edits are semantically coherent or that required companion edits are
  inferred; that boundary is tracked by
  `papers/mutation_consistency_boundary.json`.
- Mutation-operator evidence is fixed edit payload grammar and proposal
  metadata, not proposal-level operator-family provenance, adaptive
  operator-family selection, operator scoring, or benchmark telemetry; that
  boundary is tracked by `papers/mutation_operator_boundary.json`.
- Mutation mode is a configured run-wide `diff` or `full` prompt/parser
  contract, not adaptive per-candidate diff-versus-full selection based on
  code size, workspace shape, task shape, or failure history; that boundary is
  tracked by `papers/adaptive_mutation_mode_boundary.json`.
- Initial-pool divergence reports are syntactic and shared-metric telemetry,
  not task-specific functional-distance proof or "substantially different"
  benchmark evidence; that boundary is tracked by
  `papers/initial_pool_divergence_boundary.json`.
- Initial-program idea provenance is optional seed metadata plus a generation-0
  linkage report, not equal-budget seed-variant result tables, simple/random/
  researcher-seed comparisons, prompt-context-to-seed linkage, human
  contribution review/signoff, paper certification rows, or AlphaEvolve
  human-seeded benchmark parity; that boundary is tracked by
  `papers/initial_program_idea_provenance_boundary.json`.
- Initial-program validity can be enforced with
  `initial_program_validity_policy: alphaevolve_strict`, but the default
  permissive baseline still records invalid seeds as diagnostics and does not
  prove benchmark-suite strict runs, paper certification rows, or AlphaEvolve
  complete initial-program parity; that boundary is tracked by
  `papers/initial_program_validity_boundary.json`.
- Problem-formulation metadata and benchmark-fixture readiness reports are
  provenance/readiness telemetry, not populated expert-reviewed matrix or
  constructive-math formulation records, non-smoke AlphaEvolve-comparable
  fixture scope, repeated-seed protocols, SOTA/target baselines, fixture-
  emitted result artifacts, anti-gaming negative fixtures, or paper-claim-ready
  benchmark evidence; those boundaries are tracked by
  `papers/problem_formulation_provenance_boundary.json` and
  `papers/benchmark_fixture_readiness_boundary.json`.
- Constructive-math Section 3.2 heuristic-handoff records preserve the
  AlphaEvolve claim that search-heuristic programs run under fixed budgets from
  strong previous-best construction inputs toward improved constructions, not
  local heuristic-program artifacts, incumbent or produced construction
  payloads, fixed-budget execution records, before/after metric rows,
  evaluator scores, or verifier evidence; that boundary is tracked by
  `papers/math_heuristic_handoff_boundary.json`.
- Constructive-math Section 3.2 stage-sequence records preserve the
  AlphaEvolve claim that final constructions often came from multiple
  specialized heuristics, including early broad-gain stages from random/simple
  starts and later fine-tuning near optimal configurations, not local
  per-stage heuristic artifacts, ordered construction transitions, stage-role
  rows, improvement deltas, budget rows, or verifier evidence; that boundary is
  tracked by `papers/math_heuristic_stage_sequence_boundary.json`.
- Constructive-math Section 3.2 aggregate-outcome records preserve the
  AlphaEvolve source claim of over 50 mathematical problems across more than
  five branches, about 75% best-known rediscovery, about 20% SOTA improvement,
  and definition-based verification, not local per-problem rows, branch
  taxonomy rows, prior-best references, construction/verifier artifacts,
  aggregate counts, or percentage recomputation; that boundary is tracked by
  `papers/math_outcome_boundary.json`.
- Constructive-math Section 3.2 starting-construction records preserve the
  AlphaEvolve source claim that the initial starting point was a simple or
  random construction, not local per-instance starting construction payloads,
  generator or random-seed records, baseline metric rows, prior-best visibility
  policy, or prior-best seeding policy evidence; that boundary is tracked by
  `papers/math_starting_construction_boundary.json`.
- Figure 5 constructive-math exhibit provenance remains absent: README
  describes Appendix B family/status coverage, smoke-fixture boundaries, and
  constructive-math absence boundaries, not main-text Figure 5 exhibit ids,
  selected result-row links, branch/problem label mappings, before/after metric
  values, previous-best sources, rendered visual artifact paths or hashes,
  rendering parameters, source Colab cells/artifacts, or verifier links.
- Figure 5 versus Appendix B.12 sum-of-radii precision remains unreconciled:
  the registry preserves Figure 5's `2.6340 -> 2.6358` display separately from
  the Appendix B.12/Figure 14 `2.634 -> 2.635` strings, not source-specific
  locators, Figure 5 panel artifacts, value-extraction certificates,
  normalized values, rounding or canonicalization policy, value-reconciliation
  certificate, recomputed sum, or companion Colab link.
- Appendix B Figures 10-14 figure-exhibit provenance remains absent: the
  registry names Erdos minimum overlap, regular-hexagon packing,
  maximum/minimum-distance point sets, Heilbronn variants, and
  circle/rectangle sum-of-radii packing figure scopes, not normalized
  figure-exhibit rows, subfigure ids, caption-value extraction,
  previous/current metric rows, construction payload artifacts, rendered panel
  artifacts, rendering parameters, source Colab cells/artifacts, or verifier
  links.
- Appendix B numeric-result provenance remains absent: the registry enumerates
  B.1-B.13 family/status metadata and the 19 expected future result ids,
  including the B.4 revision row, not normalized per-result metric/value rows,
  parameter tuples, inequality or optimization direction records, previous-best
  values/sources, AlphaEvolve reported-value rows, source locations,
  construction-representation schemas, construction/verifier artifact hashes,
  result-version status, recomputed values, or recomputation status.
- Appendix B.1-B.3 autocorrelation step-function provenance remains absent:
  the registry preserves the paper-facing C1-C3 labels, interval counts,
  shared `[-1/4, 1/4]` domain, sign policy, bound direction, previous
  bound/source, and reported bounds (`C1 <= 1.5053`, `0.8962 <= C2`, and
  `C3 <= 1.4557`), not local step-function payload hashes,
  domain/spacing/sign-policy certificates, verifier artifacts, recomputed
  bound rows, or recomputation certificates.
- Appendix B.8 max/min-distance point-set witness provenance remains absent:
  the registry preserves the squared-ratio convention, Figure 12 left/right
  linkage, 16-point/2D and 14-point/3D metadata, prior squared bounds
  (`12.890`, `4.168`), and reported squared ratios (`12.889266112`,
  `4.165849767`), not coordinate payload hashes, point-count/dimension
  certificates, all-pairs distance matrix artifacts, min/max pair-witness
  certificates, recomputed squared-ratio rows, or Figure 12 panel artifacts.
- Appendix B.5 Erdos minimum-overlap step-function provenance remains absent:
  the registry preserves the source formulation, `[40]` equivalence,
  normalized `[0, 2]` step-function reduction, Figure 10 result id, prior
  `0.379005 <= C5 <= 0.380927` bounds, and reported `C5 <= 0.380924` upper
  bound, not a step-function payload hash, original-formulation mapping
  certificate, `[40]` equivalence-reference artifact, shift-domain
  certificate, value-range or integral-normalization certificates,
  shift-objective recomputation, recomputed upper bound, or Figure 10 panel
  artifact.
- Appendix B.6 finite-set witness provenance remains absent: the registry
  preserves the `C6` theorem/admissibility statement, `U1`/`U2` witness labels,
  set sizes `2003` and `54265`, reported lower bounds `1.1479 <= C6` and
  `1.1584 <= C6`, and required future finite-set fields, not sorted integer
  payload hashes, contains-zero or non-negative certificates,
  `|U - U| <= 2 max(U) + 1` admissibility certificates, `|U-U|`/`|U+U|`
  cardinality certificates, max-element certificates, formula-substitution
  certificates, or recomputed lower-bound rows.
- Appendix B.7 regular-hexagon packing provenance remains absent: the registry
  preserves the unit-regular-hexagon objective, Figure 11 left/right linkage,
  prior `[29]` values, `n = 11` and `n = 12` witness summaries, and reported
  outer-side improvements (`3.943 -> 3.931` and `4.0 -> 3.942`), not
  placement payload hashes, pose/orientation schemas, inner/outer
  regular-hexagon geometry certificates, containment or non-overlap
  certificates, side-length recomputation certificates, recomputed side
  lengths, or Figure 11 panel artifacts.
- Appendix B.9-B.10 Heilbronn minimum-area provenance remains absent: the
  registry preserves Figure 13 left/middle/right linkage, B.9 triangle and
  B.10 convex-region domains, the `n = 11`, `n = 13`, and `n = 14` witness
  summaries, prior values (`0.036`, `0.0306`, `0.0277`), and reported values
  (`minimum_area > 0.0365`, `0.0309`, `0.0278`), not point-coordinate or
  domain artifact hashes, domain-membership proofs, unit-area or convexity
  certificates, triple-count enumeration, all-triples minimum-area
  certificates, minimum-witness-triangle certificates, reported-value
  comparison certificates, recomputed minimum areas, or Figure 13 panel
  artifacts.
- Appendix B.11 kissing-number proof provenance remains absent: the registry
  preserves dimension `11`, prior lower bound `592`, reported lower bound
  `593`, the 593 nonzero integral-coordinate witness count, the max-norm
  versus minimum-pairwise-distance condition, Lemma 1, and the
  `{2 x / ||x||}` sphere-center transform, not a 593-vector payload hash,
  count/dimension or exact-coordinate certificates, norm and pairwise-distance
  matrix artifacts, exact max-norm or minimum-pairwise-distance certificates,
  witness vectors/pairs, strict norm-distance inequality proof, Lemma 1
  applicability certificate, transformed-center and unit-sphere certificates,
  kissing-angle certificate, or recomputed lower-bound row.
- Appendix B.12-B.13 circle/rectangle sum-of-radii provenance remains absent:
  the registry preserves Figure 14 left/middle/right linkage, `n = 26` and
  `n = 32` unit-square rows, the `n = 21` perimeter-4 rectangle row, prior
  sums (`2.634`, `2.936`, `2.364`), reported sums (`2.635`, `2.937`,
  `2.3658`), the B.13 caption display, and the checked-in 26-circle fixture as
  smoke-only, not AlphaEvolve container hashes, circle placement payloads,
  exact-count checks, payload-schema validation certificates, positive-radius
  certificates, containment or pairwise non-overlap certificates, rectangle
  dimensions, rectangle-perimeter proof, sum-of-radii formula certificates,
  recomputed sums, or Figure 14 panel artifacts.
- Appendix B.4 revised-result provenance remains absent: the registry
  preserves the first-version `C4 <= 0.3521` uncertainty-inequality result,
  Henry Cohn's pointer to the `[18]` refinement, the external `0.3284`
  constant, and AlphaEvolve's revised `0.3216` note, not local revision
  artifacts, Colab or verifier linkage, comparison-to-`0.3284` certificates,
  recomputed revised constants, artifact hashes, or proof that the current
  Appendix B value has been locally reproduced.
- Appendix B.4 prior-bound rounding provenance remains absent: the registry
  preserves the `[33]` lower bound `0.2025`, source-stated upper bound `0.353`,
  rounded comparison baseline `0.3523`, and policy that AlphaEvolve's
  first-version `C4 <= 0.3521` is compared against the rounded baseline, not a
  `[33]` page or section locator, source-solution artifact, prior-solution
  rounding artifact, rounding-audit certificate, or locally reproduced
  certificate for the `0.353` to `0.3523` distinction.
- Appendix B.4 Hermite-polynomial certificate provenance remains absent: the
  registry preserves the first-version `C4 <= 0.3521` uncertainty-inequality
  result from the Hermite basis, approximate coefficients
  `[0.32925, -0.01159, -8.9216e-5]`, `P(x)/x^2` largest-root computation, and
  `r_max^2 / (2*pi)` formula, not local coefficient payloads,
  Hermite/Fourier/root certificates, origin-condition certificates,
  eventual-nonnegative certificates, or recomputed-bound evidence.
- Appendix B.4 prior-construction similarity provenance remains absent: the
  registry preserves the paper's qualitative statement that AlphaEvolve's
  linear combination is very similar to reference `[33]` and that this supports
  a near-optimality hypothesis, not local prior/AlphaEvolve coefficient
  payloads, basis-alignment certificates, coefficient-similarity metrics,
  hypothesis-source artifacts, or proof that the near-optimality hypothesis is
  locally verified.
- Matrix-publication evidence is one checked `mm_2x2x2` Strassen baseline
  bundle plus Appendix A registry/status metadata, not full-suite local target
  tensors, discovered decompositions, coefficient data, exactness certificates,
  notebooks, per-seed reports, or publication bundles for every registered
  Appendix A target; that boundary is tracked by
  `papers/matrix_suite_publication_artifacts.json`.
- Matrix per-seed reports validate declared seed rows, best rank, and hit
  fraction, and matrix cascade-run boundary records can link seed rows to
  stage traces, but local matrix runners do not yet emit AlphaEvolve Section
  3.1-style repeated-seed cascade traces, pruning decisions, or early-stop
  provenance; that boundary is tracked by
  `papers/matrix_cascade_run_runtime_boundary.json`.
- Appendix A matrix target-suite curation records the reported 54 sorted
  targets, rough paper selection wording, symmetry policy, and included-target
  rationales, not an exhaustive locally justified corpus for every excluded
  non-equivalent matrix size outside the reported suite; that boundary is
  tracked by `papers/appendix_a_matrix_excluded_target_curation.json`.
- Appendix A matrix resource-frontier records preserve the paper-source
  statement about sizes beyond `<5,5,5>`, 1000 random seeds, single-GPU
  evaluators, frequent OOM, and further-optimization need, not local
  larger-target runs, measured accelerator-memory profiles, OOM artifacts,
  reduced-seed tradeoffs, or reproduced scaling evidence; those boundaries are
  tracked by `papers/appendix_a_matrix_resource_frontier.json` and
  `papers/appendix_a_matrix_local_resource_frontier.json`.
- Matrix near-integrality records validate declared prompt instructions,
  integer/half-integer rounding policy, raw-versus-rounded coefficient
  diagnostics, and exactness-certificate links, not a local matrix runner that
  emits AlphaEvolve Section 3.1 near-integral prompt/evaluator evidence during
  search; that boundary is tracked by
  `papers/matrix_near_integrality_runtime_boundary.json`.
- Matrix sweep-space records validate declared Figure 9-style `sweep()`
  provenance, user-provided `hyper` ranges, sampled configurations, selected
  winners, final decompositions, and exactness-certificate links, not a local
  matrix runner that emits AlphaEvolve Figure 4/Figure 9 search-program sweep
  evidence during search; that boundary is tracked by
  `papers/matrix_sweep_space_runtime_boundary.json`.
- Appendix A Figure 9 matrix-diff records validate panel ids, pages, line
  spans, semantic components, source/diff hashes, rendered/OCR artifact
  metadata, and links to matrix result, sweep-space, certificate, and companion
  notebook evidence, not local report/export output that emits rendered panel
  images, OCR text, or source-diff artifacts for Figures 9a-9c; that boundary
  is tracked by `papers/figure9_matrix_diff_artifacts.json`.
- Figure 4 matrix-discovery records validate main-text exhibit metadata, page
  and caption linkage, the 15-mutation caption count, `mm_4x4x4` rank-48
  target mapping, highlighted component categories, source/diff artifact
  metadata, and links to Figure 9, matrix-result, certificate, and notebook
  evidence, not local report/export output that emits rendered Figure 4
  artifacts or accepted 15-mutation lineage; that boundary is tracked by
  `papers/figure4_matrix_discovery_artifacts.json`.
- Matrix baseline-component records validate Section 3.1 starting-algorithm
  provenance fields for baseline program ids, initializer, reconstruction
  loss, Adam optimizer metadata, mutable scopes, fixed hashes, generation-0
  metrics, mutation lineage, and matrix-result links, not local matrix-runner
  output that emits the initializer/loss/optimizer provenance during search;
  that boundary is tracked by
  `papers/matrix_baseline_component_runtime_boundary.json`.
- Matrix scalar-field records validate complex/finite-field metadata,
  characteristic and applicability claims, exact coefficient representation,
  algorithm and certificate refs, and matrix-result links, not local matrix
  runners that emit exact complex decomposition/certificate artifacts for
  AlphaEvolve Section 3.1 scalar-field claims; that boundary is tracked by
  `papers/matrix_scalar_field_runtime_boundary.json`.
- Matrix tensor-rank records validate tensor-decomposition versus non-tensor
  algorithm claims, rank, recursive applicability, certificate scope,
  tensor-identity status, target-tensor refs, exactness-certificate refs, and
  matrix-result links, not local matrix runners that emit AlphaEvolve Section
  3.1 target-tensor/certificate artifacts during search; that boundary is
  tracked by `papers/matrix_tensor_rank_runtime_boundary.json`.
- Collaborator-feedback provenance is optional metadata and runtime reporting
  for cohorts, events, affected workflow areas, change links, validation
  outcomes, privacy/redaction policy, and review state, not populated
  representative-fixture feedback records, multi-cohort reviewed evidence,
  paper certification rows, reviewed validation outcomes, or AlphaEvolve
  robustness/versatility parity; that boundary is tracked by
  `papers/collaborator_feedback_provenance_boundary.json`.
- Duplicate-work reports are run-local exact-workspace cache diagnostics, not
  durable cross-run memory, semantic duplicate detection, or resume-spanning
  cache replay; that boundary is tracked by
  `papers/duplicate_work_policy_boundary.json`.
- Failure memory is run-local diagnostic evidence, not durable cross-run
  semantic failed-proposal memory, learned repetition avoidance, or
  failure-aware sampling policy; that boundary is tracked by
  `papers/failure_memory_boundary.json`.
- Related Work positioning is not inferred from the bundled paper list; the
  missing taxonomy and claim gates are tracked by
  `papers/related_work_taxonomy_boundary.json`.
- Candidate execution is Python-primary code-file-set execution. The
  abstraction-choice report does not claim AlphaEvolve-style problem-defined
  serializers/materializers/runners, paired solution/search representations,
  abstraction-rationale metadata, symmetry/bias evidence, or equal-budget
  direct-solution/constructor/search comparisons; that boundary is tracked by
  `papers/candidate_abstraction_boundary.json`.
- Configuration validation is local effective-config validation; live
  provider/model API compatibility is tracked by
  `papers/config_validation_boundary.json`.
- Runtime budgets are local cooperative generation/evaluation/evaluator-second/
  wall-clock/LLM/provider counters, not per-candidate compute-hour accounting,
  accelerator/worker leases, async queue budgets, or equal-budget execution
  reports; that boundary is tracked by
  `papers/expensive_evaluation_budget_boundary.json`.
- AlphaEvolve Figure 8 ablation support is a validated registry, equal-budget
  report contract, scope-boundary records, and optional
  `libreevolve.alphaevolve_figure8_exhibit.v1` exhibit metadata; the committed
  `papers/figure8_ablation_artifacts.json` sidecar records the current
  rendered-artifact absence boundary. This is not executed equal-budget
  matrix/kissing benchmark runs, proven component-isolated ablation setups,
  rendered paper-quality curves, or accelerator/async-worker budget evidence.
- Provider cost evidence is configured token-cost estimates from retained
  provider usage, not live provider pricing, provider default-rate capture,
  account/model-specific pricing, or raw provider-payload replay; that boundary
  is tracked by `papers/provider_pricing_boundary.json`.
- Provider diagnostics are bounded retained scalar/id/finish/retry/failure
  telemetry, not raw provider-payload sidecars, provider-output replay,
  complete provider-call replay, or account/model default capture; that
  boundary is tracked by `papers/provider_diagnostics_replay_boundary.json`.
- Provider cancellation records are policy/audit evidence for request
  timeouts, ensemble wait deadlines, artifact gates, and quarantine
  observations, not live provider SDK hard cancellation, timeout-driven stop
  enforcement, cross-run provider quarantine resume, richer role-specific
  timeout artifacts, or provider-output raw-payload replay; that boundary is
  tracked by `papers/provider_cancellation_boundary.json`.
- Critique reviewer pools are bounded synchronous first/last-valid mutation
  filters with reviewer telemetry, not async reviewer overlap, calibrated
  reviewer scoring, reviewer reliability ablations, per-reviewer provider
  isolation, or external reviewer timeout artifacts; that boundary is tracked
  by `papers/critique_reviewer_pool_boundary.json`.
- Prompt section packing is mutation-path and final-prompt-boundary evidence,
  not all-role provider-token section packing, exact non-OpenAI provider
  counters, registry/custom role section packing, retrieval/context/plugin/
  failure-memory packing, or full validator-metadata prompt policy; that
  boundary is tracked by `papers/prompt_section_packing_boundary.json`.
- Explicit-context source-role reports classify configured problem-local
  `context.yaml` sources as human instructions, equations, code snippets,
  literature PDFs, or background references with topic, source-location,
  prompt-inclusion, hash, and redaction metadata, not semantic proof that those
  roles are correct, expert-reviewed problem-formulation evidence, live or
  external context-source classification, or full AlphaEvolve context-selection
  and context-evolution parity.
- Paper-result certification and systems-result validation are report,
  artifact-inventory, and evidence-bundle contracts with independence,
  artifact-hash, claim-calibration, application-provenance, domain-readiness,
  and gate checks, not proof that independent certifiers, real
  application-owner or domain-review signoff, reviewer/deployment evidence,
  real Section 3.3 scheduling/kernel/hardware/compiler result magnitudes, or
  real compiler, hardware, kernel, and scheduling fixtures have emitted
  held-out, deployment, expert-confirmation, reference-code, or
  domain-specific result artifacts; that boundary is tracked by
  `papers/systems_result_readiness_boundary.json`.
- Scheduling safety records validate feasible candidate-set provenance,
  ranking-only scope, simulator/admission/placement boundaries, resource
  invariants, and artifact refs, not proof of Borg-style scheduling safety,
  real feasibility-filter runs, or production placement correctness; that
  boundary is tracked by `papers/systems_result_readiness_boundary.json`.
- Scheduling formulation records validate online vector-bin-packing schema,
  CPU/memory bin and item fields, workload/capacity snapshot provenance,
  stranded-resource objective links, simulator-input hashes, feature mapping,
  and artifact refs, not proof of populated Borg-style workload fixtures,
  simulator runs, or AlphaEvolve scheduling problem setup; that boundary is
  tracked by `papers/systems_result_readiness_boundary.json`.
- Scheduling deployment-readiness records validate interpretable heuristic
  structure, operator/debug review, predictability checks, deployment-risk
  controls, ergonomics, learned-policy comparison, review flags, and artifact
  refs, not proof of real mission-critical rollout, operator acceptance,
  deployment measurements, or AlphaEvolve-comparable Borg scheduling readiness;
  that boundary is tracked by `papers/systems_result_readiness_boundary.json`.
- Scheduling documentation does not yet reproduce AlphaEvolve Figure 6 exhibit
  provenance: exact Borg heuristic source/hash, CPU/memory residual-feature
  definitions, heatmap data and rendering parameters, rendered artifact hashes,
  baseline production heuristic identity, or simulator/held-out/deployment
  report links remain active code and paper TODOs.
- Kernel documentation does not yet reproduce AlphaEvolve Figure 7 Pallas
  tiling-problem exhibit provenance: matrix-shape variable definitions,
  tile-parameter schema, accelerator/memory/fusion/compiler-context
  annotations, diagram source data, rendered visual artifact hashes, rendering
  parameters, and links to shape-corpus/runtime reports remain active code and
  paper TODOs.
- Kernel systems-result reports currently cover generic domain gates and
  claim-calibration metadata, not Pallas/Gemini input-shape corpus provenance,
  deterministic train/eval split hashes, real TPU runtime artifacts,
  expert-baseline tiling heuristic identity, tiling-only candidate boundaries,
  unchanged-operation correctness-by-construction evidence, engineering-effort
  calibration, or production/workflow adoption.
- Pallas workflow documentation does not yet prove AlphaEvolve-style
  automation of search-based autotuning or manual tiling-heuristic work:
  baseline workflow class, autotuning search/retuning policy, manual
  authoring/review effort, input-shape-change sensitivity, hardware-expertise
  assumptions, and model-developer ergonomics comparisons remain active code
  and paper TODOs.
- Gemini self-training wording remains bounded: README does not yet claim that
  a deployed Pallas kernel optimization affected the training workload of the
  same Gemini-family system that powered AlphaEvolve, nor that before/after
  production training metrics, engineering-velocity evidence, rollout state,
  or safety/rollback records justify an AlphaEvolve-style self-optimization
  interpretation.
- Hardware RTL/EDA records validate HDL source boundaries, synthesis/PPA
  provenance, timing/power/area constraints, equivalence or formal-verification
  evidence, designer validation, downstream synthesis confirmation, RTL-flow
  placement, adoption rationale, integration targets, deployment impact, hashes,
  flags, and artifact refs, not real Verilog/RTL source, synthesis/PPA runs,
  verification logs, designer signoff, downstream-synthesis artifacts,
  upcoming-chip integration, or deployment/time-to-market evidence.
- Hardware rewrite records validate before/after Verilog hashes, rewrite diff
  hashes, changed spans, removed-bit or signal metadata, component and
  matrix-unit context, rewrite category/rationale, and PPA/verification refs,
  not real before/after Verilog files, exact diff or AST artifacts,
  removed-bit inventories, component review files, or per-bit functional and
  PPA evidence for the TPU arithmetic-circuit rewrite.
- Hardware contribution records validate Gemini/AlphaEvolve model-family
  relationship, run/backend identity, TPU generation and arithmetic-circuit
  identity, novelty basis, first-direct-contribution scope, integration
  milestone, hardware review scope, synthesis-rediscovery caveat, confirmation
  flags, and artifact refs, not real model/run/backend records, reviewed
  TPU/circuit identifiers, firstness evidence, integration records, hardware
  signoff files, or synthesis-rediscovery audit artifacts.
- Compiler IR records validate IR-origin/editability boundaries,
  compiler-generated baseline provenance, reference and input-generator hashes,
  numerical tolerance policy, final expert-confirmation scope, per-edit
  reference-check metadata, abstraction-level attribution, and artifact refs,
  not real XLA/FlashAttention edit artifacts, randomized input coverage,
  reference-check outputs, tolerance/failure logs, or expert all-input signoff.
- Compiler stack records validate workload/model configuration,
  FlashAttention/Pallas kernel identity, JAX pre/postprocessing boundaries,
  XLA lowering stage, hardware target, lowered-IR hash, optimization decision
  category, and artifact refs, not real Transformer/inference configuration
  records, Pallas source snapshots, JAX wrapper artifacts, XLA stage outputs,
  hardware-target records, lowered-IR files, or decision-evidence artifacts.
- Compiler adoption records validate adoption-path classification, target
  compiler/version/pass identity, bounded use-case scope, optimization artifact
  identity/hash, integration owner, reviewer scope, adoption state,
  rollout/revert state, workflow-handoff boundary, and artifact refs, not real
  compiler patch/pass artifacts, use-case integration records, reviewer signoff
  files, deployment or rollback logs, or AlphaEvolve-in-compiler-loop evidence.
- Self-improvement and distillation claims remain absent: README does not yet
  identify LibreEvolve runtime/provider/evaluator/compiler/benchmark components
  as evolved optimization targets, link evolved candidates to measured
  improvements in LibreEvolve's own execution path, record deployment/adoption
  or rollback/safety evidence, or provide distillation datasets, training runs,
  or model-evaluation artifacts derived from evolved programs.
- Feedback-loop cadence and environment-ROI claims remain absent: README does
  not yet record loop IDs, next-version targets, elapsed-month cadence,
  moderate-gain calibration, setup or maintenance costs for robust evaluator
  environments, expected versus realized discovery value, gating assumptions,
  or readiness evidence for expanding AlphaEvolve-style evaluator environments.
- Benchmark hardening records and shipped-example scope validate smoke-scope
  anti-gaming metadata, negative-fixture files, detector logs, artifact hashes,
  and `alphaevolve_comparable: false` boundaries for shipped examples, not
  benchmark-grade tensor/geometric/constructive-math runners, randomized or
  exhaustive anti-gaming evidence, executable construction/certificate
  validators, target/SOTA baselines, Colab-equivalent Appendix B construction
  data, or verifier-code artifacts.
- Follow-on problem-repository coverage records validate a pinned snapshot's
  problem-page, status-bucket, link, hash, notebook-link, absence-reason,
  notebook-hash, scoped artifact-flag, Appendix B crosswalk, and
  artifact-rights-template evidence, not live repository completeness, full
  notebook cell inventories, normalized result rows, construction payloads,
  verifier artifacts, recomputed values, or copied/adapted generated
  artifacts.
- Follow-on problem-count wording remains snapshot-scoped: the source
  README/paper declares 67 mathematical problems, while pinned diagnostics
  observe 68 numbered HTML pages and classify page 68 as an extra
  duplicate-title `Logic puzzles` page outside the declared navigation range
  with a generic Colab landing URL and placeholder paper link. That evidence is
  not a claim that every numbered page is a complete notebook-backed or
  paper-linked source artifact.
- Paper artifact-role records validate AlphaEvolve PDF page 23 figure-creator
  and companion-Google-Colab assembler attribution with stable artifact ids,
  exact contributor initials, source section/page metadata, and source
  phrases, not linked rendered figure files, caption/source maps, figure-region
  artifacts, companion notebook URLs or digests, retrieved notebook exports,
  cell maps, or source-to-artifact maps; the current linkage sidecar marks
  both artifacts as `not_yet_linked`.
- Documentation alignment checks are path, manifest, TODO-coverage, and
  sidecar-registry guards, not semantic proof that every README, ROADMAP,
  papers-index, and TODO statement is current; that boundary is tracked by
  `papers/documentation_truthfulness_boundary.json`.
- Database sampling reports are local strategy/count telemetry, not calibrated
  AlphaEvolve-style exploration/exploitation evidence; that boundary is tracked
  by `papers/sampling_balance_boundary.json`.
- Multi-objective archive data is retained overlay and diagnostic frontier
  evidence, not primary Pareto/frontier archive replacement or durable
  cross-run metric optimization; that boundary is tracked by
  `papers/objective_archive_boundary.json`.
- Metric-diverse prompt evidence is current-run prompt-visible telemetry, not
  benchmark-required metric-diverse prompt policy, cross-run fixtures, or
  scalar/single-metric equal-budget comparisons; that boundary is tracked by
  `papers/metric_diverse_prompt_boundary.json`.
- Proposal scores and hypothesis indexes are bounded current-run records, not
  semantic idea-memory retrieval, calibrated proposal-quality models,
  cross-run proposal tables, or score-driven prompt/archive policy; that
  boundary is tracked by `papers/proposal_score_boundary.json`.
- Proposal-diversity reports are exact proposal/idea hashes and duplicate
  counts, not semantic novelty, near-duplicate detection, operator-family
  labels, code or task-output distance, novelty scoring, prompt/backend
  attribution, or equal-budget/model-ablation evidence; that boundary is
  tracked by `papers/proposal_diversity_boundary.json`.
- Program-output resurfacing is exact current-run source-key/hash lookup over
  bounded output summaries, not durable output tables, schema-aware retrieval,
  semantic output similarity search, or replayable output-driven sampling;
  that boundary is tracked by `papers/program_output_boundary.json`.
- Figure 3 supervised-learning example support is generic embedded-evaluator,
  prompt-history, candidate-history, SEARCH/REPLACE, and preamble handling,
  not reproduced paper subfigure evidence with exact source/prompt/output
  excerpts, displayed score values, rendered hashes, or run-artifact links;
  that boundary is tracked by
  `papers/figure3_supervised_exhibit_boundary.json`.
- Artifact indexes are bounded current-run path/hash/redaction/skipped/stage
  metadata and content excerpts, not durable artifact query tables,
  full-content artifact search, semantic artifact similarity search, cross-run
  artifact indexes, content-ranking policy, or replayable artifact-driven
  sampling; that boundary is tracked by `papers/artifact_index_boundary.json`.
- `libreevolve show` and whole-run source/workspace integrity reports provide
  streamed-row validation, selected-row display, retained-program workspace
  hashes, source-payload shape checks, static-file reference counts, and
  selected runtime artifact hashes, not a durable whole-run query surface, full
  source-payload replay, cross-run workspace deduplication, static-file content
  replay, or selected/unselected source-diff views; that boundary is tracked by
  `papers/whole_run_source_workspace_integrity_boundary.json`.
- MAP-Elites descriptor snapshots are insertion-time local descriptor metadata,
  not stable learned/evaluator-provided behavior descriptors or archive rebin
  semantics; that boundary is tracked by
  `papers/map_elites_descriptor_boundary.json`.
- The included examples are smoke fixtures and small demos unless a fixture
  explicitly documents stronger benchmark evidence.
- Gemini/provider parity, benchmark-scale claims, paper-result reproduction,
  release packaging, and broader CI/platform guarantees are tracked as
  boundaries in `papers/README.md` and `ROADMAP.md`, not promised here.

## Installation

Use Python 3.11 or newer. On this Windows machine, use `py -3.12`.

```bash
py -3.12 -m pip install -e ".[dev]"
```

Create a `.env` file at the project root for any provider keys you plan to use:

```dotenv
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_HOST=http://localhost:11434
```

`.env` is loaded for `libreevolve run` with `override=True`. Do not commit API
keys.

## Quick Start

Run one of the bundled examples with a backend available in your environment:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends "openai:<openai-model-id>"
```

For Anthropic:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/sorting --max-generations 10 --backends "anthropic:<anthropic-model-id>"
```

For a local Ollama model:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends "ollama:<installed-ollama-model>"
```

Inspect a run:

```bash
py -3.12 -m libreevolve show runs/hello_world
```

Use a fresh `--run-name` for repeat runs, or pass `--overwrite` when you
intentionally want to replace the existing run directory.

## Run Artifacts

Runs write to `runs/<run-name>/`, which is gitignored. The main outputs are
`manifest.json`, `best.py`, `best_workspace/`, evaluator/plugin artifact
folders, and the current JSONL streams:

- `archive_events.jsonl`
- `controller_budget_events.jsonl`
- `evaluator_results.jsonl`
- `failure_history.jsonl`
- `history.jsonl`
- `llm_calls.jsonl`
- `prompt_current_binding_table.jsonl`
- `prompt_history.jsonl`
- `prompt_prior_score_table.jsonl`

See [docs/run-artifacts.md](docs/run-artifacts.md) for schemas, invalid-record
quarantine streams, restore behavior, and inspection details. Whole-run
source/workspace integrity is bounded by
`papers/whole_run_source_workspace_integrity_boundary.json`.

## How It Works

1. Load a problem directory with seed code, objective text, optional config, and
   a validator.
2. Evaluate the seed candidate.
3. Select parent programs from the archive.
4. Render a mutation prompt and call an LLM backend.
5. Parse the response as SEARCH/REPLACE diffs or full replacement code.
6. Evaluate the candidate in a subprocess and apply any configured stages.
7. Admit valid finite-scoring candidates into the program database and
   MAP-Elites archive.
8. Persist run artifacts for inspection and later analysis.

## Problem Layout

Problem directories live under `libreevolve/problems/examples/`. A minimal
problem usually includes:

- `seed.py`: initial program to evolve.
- `evaluator.py`: validator entrypoint.
- `prompt.txt` or problem metadata: task instructions for the LLM.
- optional `config.yaml`: backend, archive, prompt, and evaluator settings.

See [docs/problem-format.md](docs/problem-format.md) for the full contract.

## CLI

```bash
py -3.12 -m libreevolve --help
py -3.12 -m libreevolve run --help
py -3.12 -m libreevolve show --help
```

Common run options:

- `--max-generations`
- `--max-evaluations`
- `--max-runtime-seconds`
- `--backends`
- `--plugins`
- `--mutation-mode diff|full`
- `--parent-selection-strategy`
- `--overwrite`

## Documentation

- [docs/README.md](docs/README.md): documentation index.
- [docs/architecture.md](docs/architecture.md): runtime architecture.
- [docs/configuration.md](docs/configuration.md): config fields and CLI
  overrides.
- [docs/backends.md](docs/backends.md): OpenAI, Anthropic, and Ollama behavior.
- [docs/plugins.md](docs/plugins.md): plugin hooks and built-in plugins.
- [docs/run-artifacts.md](docs/run-artifacts.md): files written under `runs/`.
- [ROADMAP.md](ROADMAP.md): implementation status and remaining work.
- [papers/README.md](papers/README.md): source papers, status rows, and
  claim-boundary records.

## Research Sources

LibreEvolve is informed by a local cache of 53 papers on LLM-guided evolution,
program synthesis, quality-diversity optimization, and related benchmarks. The
PDF cache lives locally under `papers/`, but the PDFs themselves are gitignored.
The committed repository tracks `papers/README.md`, download manifests, and
JSON source-boundary artifacts.

Manifest `title` fields are inventory/display slugs derived from cache names,
not authoritative bibliographic titles. Use `papers/README.md` for paper-facing
titles, implementation status, and benchmark coverage decisions.

`papers/README.md` is the complete implementation-status index for all 53
manifest rows. It separates implemented behavior, inspiration-only sources,
candidate benchmark ideas, and source-boundary records so the root README does
not have to carry the full research ledger.

Rehydrate the ignored local PDF cache on a fresh checkout:

```bash
py -3.12 -m libreevolve.tools.paper_manifest --rehydrate
```

Validate the paper index:

```bash
py -3.12 -m libreevolve.tools.paper_manifest
py -3.12 -m libreevolve.tools.paper_manifest --require-local-pdfs
```

## Testing

Run the non-integration tests:

```bash
py -3.12 -m pytest tests/ -m "not integration" --tb=short
```

Run integration tests only when the required provider credentials are present:

```bash
py -3.12 -m pytest tests/integration/ -m integration --tb=short
```

## Repository Layout

```text
libreevolve/
  core/          orchestration, prompting, evaluation, diffing, database, config
  llm/           OpenAI, Anthropic, Ollama, and ensemble routing
  population/    program records, MAP-Elites, island migration
  plugins/       optional lifecycle hooks and paper-inspired plugins
  problems/      examples and problem loading
  tools/         paper/source manifest validation
docs/            architecture, configuration, backend, plugin, and artifact docs
papers/          tracked manifests plus ignored local PDF cache
runs/            gitignored run outputs
tests/           unit and integration tests
```

## Contributing

Keep root README changes practical and short. Detailed behavior belongs in
`docs/`, source-boundary evidence belongs in `papers/README.md` and JSON
sidecars, and long-term implementation status belongs in `ROADMAP.md` or
`docs/todo/`.

Before opening a change, run focused tests for touched code and the paper
manifest check when source-boundary files change.

GitHub Actions currently provide path-scoped Ubuntu validation for secret
scanning, Python 3.11/3.12 non-integration tests, and optional credential-gated
integration tests. Broader paper/docs CI, wheel/sdist smoke checks,
cross-platform matrices, and branch/notification policy are tracked by
`papers/ci_workflow_coverage_boundary.json`.

The secret scan uses `.secrets.baseline`. If you intentionally add synthetic
provider-looking tokens in tests or TODO evidence, use a narrow fixture marker
such as `# pragma: allowlist secret` where appropriate, or regenerate and stage
the resulting `.secrets.baseline` change. A detect-secrets report about an
unstaged baseline is a validation issue to review and stage, not a
`provider/API failure`.

## License

MIT. See [LICENSE](LICENSE).
