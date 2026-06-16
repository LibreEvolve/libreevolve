# Current Implementation Status

This page preserves the detailed implementation and absence-boundary ledger
previously carried by the root README. Keep the root README practical and short;
use this document when a reader needs the fuller status inventory behind the
top-level summary.

For long-term priorities, see [ROADMAP](../ROADMAP.md). For paper/source status
and validated sidecar boundaries, see [papers/README.md](../papers/README.md).

## Status

This is an alpha-stage research codebase, not a production optimizer and not a
full AlphaEvolve reproduction.

Implemented today:

- Python-primary candidate workspaces and seed programs.
- SEARCH/REPLACE diff mutations using the AlphaEvolve fence format.
- Full-code replacement mode when configured.
- OpenAI, Anthropic, Ollama, and configured custom import-path backend
  support.
- A heuristic UCB-style backend selector.
- Synchronous MAP-Elites and island archives, with five islands by default.
- Local subprocess evaluation with staged validator support.
- Optional critique, feedback, and plugin hooks.
- Run artifacts under `runs/`, including manifests, histories, prompts,
  failures, prompt current-binding/prior-score tables, best candidates,
  best workspaces, and plugin/evaluator artifacts. The generated-artifact
  lifecycle remains incomplete for prompt-table exports and
  `paper_artifacts/...` evidence: active TODOs still track unified
  collision/overwrite cleanup, artifact-hash, schema, restore, and
  `show` inspection proof for those paper-facing outputs.

Important limits:

- Evaluators run in local subprocesses, not hardened security sandboxes.
- The controller, archive, migration, and evaluator flow are local and
  synchronous, not a distributed asynchronous AlphaEvolve-style service.
  Runtime histories record
  `runtime.history.distributed_pipeline_topology_report`, naming the current
  single-process controller, in-process database, configured LLM sampler
  backends, local evaluator nodes, zero queues, blocking dependency edges, and
  runtime-budget linkage. It keeps AlphaEvolve Section 2.6 Python `asyncio`
  pipeline parity false; `papers/distributed_pipeline_topology_boundary.json`
  preserves the same single-process synchronous-topology absence boundary,
  including the missing asyncio runtime identity, async task/coroutine
  identities, dependency wait-event telemetry, worker lifecycle/liveness
  records, scheduler-state snapshots, deterministic async completion/admission
  order, queue backpressure, and pending-work checkpoints.
- Built-in provider adapters are OpenAI, Anthropic, and Ollama. Custom
  import-path backends can wrap other services, but Google/Gemini is not a
  first-class provider yet, so AlphaEvolve's Gemini 2.0 Flash/Gemini 2.0 Pro
  model mix remains an explicit absence boundary. Runtime histories record
  `runtime.history.gemini_provider_parity_report`, and
  `papers/gemini_provider_parity_boundary.json` preserves the same boundary
  for paper-manifest validation. Missing parity gates include Gemini
  credential preflight, client-context configuration, request-parameter
  mapping, provider-native usage/default/error diagnostics, capability and
  model-registry snapshots, account/model availability checks, first-class
  Flash/Pro lane identity, scheduler lane integration, substitution contracts,
  and substitution-equivalence justification.
- AlphaEvolve source-version evidence now records arXiv abstract-page-adjacent
  metadata for `2506.13131v1` in `papers/source_versions.json`, including DOI,
  subject classes, submitted timestamp, author count, TeX source URL, and
  source license URL. It remains boundary evidence only:
  `papers/arxiv_abstract_snapshot.json` now pins an abstract-page byte/hash,
  retained HTML artifact, and normalized metadata snapshot; DataCite DOI,
  TeX/e-print, license-page, and current-version/floating-PDF digest sidecars
  now preserve bounded response metadata and hashes, while the raw HTTP headers
  sidecar preserves pinned source response header lines and the DataCite
  full-response sidecar retains the complete raw API response body. The TeX
  archive-retention sidecar now retains the full e-print archive and member
  inventory, and the license-page HTML retention sidecar now retains the
  Creative Commons license-page HTML artifact with byte/hash and
  content-marker validation. The current-version sidecar validates that the
  retained floating PDF artifact bytes/hash match the cached PDF, and the
  cached-PDF header consistency sidecar validates first-page header extraction
  hashes and markers. The metadata extraction-script sidecar now pins the
  reusable offline extraction script and retained source-artifact coverage.
  The source refresh-gate sidecar now pins the deterministic/live refresh
  script and scheduled/manual GitHub Actions job for arXiv/DataCite/e-print/
  license drift checks, and the refresh-run sidecar archives one successful
  manual live-network run with six matched source responses. The workflow now
  uploads `alphaevolve_source_refresh_report.json` as
  `alphaevolve-source-refresh-report`. The source refresh-promotion sidecar
  maps each central-gate source id to covered paper sidecars while keeping
  those older sidecars as bounded snapshots. Scheduled CI refresh-run history
  is still not claimed.
- Figure 1/Figure 2 process-exhibit reports map AlphaEvolve diagram nodes,
  edges, and pseudocode steps to local artifacts, not exact source-diagram
  reproduction, exact source caption/text identity, source diagram text
  identity, diagram node-label source alignment, source figure image/crop
  hashes, visual node coordinates, source edge geometry/routing, Figure 2
  pseudocode line-number maps, Figure 2 line-level pseudocode alignment,
  visual diff/fidelity checks, async controller/sampler/evaluator topology,
  independent evaluator-pool implementation, or full process parity; that
  boundary is tracked by `papers/process_exhibit_boundary.json`.
- Existing-codebase integration reports inventory runtime Python EVOLVE-block
  marker spans and optional source-setup metadata. The `workspace_math`
  example now includes a smoke-scoped `codebase_integration.yaml` and
  `source_setup/fixture_lib_v1/` pre-marker source bundle so a real run can
  surface complete smoke source-setup metadata. This is still not
  AlphaEvolve-style minimal-change integration with a real external upstream,
  codebase-scale fixture, independent setup-diff artifact, or verified
  before/after evaluator-call proof; that boundary is tracked by
  `papers/existing_codebase_integration_boundary.json`.
- Workspace topology and materialization diagnostics cover local file-workspace
  path/case-folding/source-copy preflights, topology-command validation, and
  prompt-visible `materialization_error` summaries. Metadata-only language and
  build runner declarations can be recorded, but arbitrary-language or
  build-runner artifacts, dependency-graph validation, bulk directory or
  external-path operations, portable static source-copy identity,
  remote/container workspaces, paper-facing invalid-workspace fixture rows, or
  codebase-scale workspace parity are still not implemented; that boundary is
  tracked by `papers/workspace_materialization_boundary.json`.
- Codebase-scale reports are current-run workspace telemetry for retained
  file/line counts, generated candidates, multi-file and hundreds-line
  observations, and parent-relative edits, not realistic multi-component
  benchmark fixtures, coupled cross-file dependency edits, dependency-graph
  validation, non-Python fixtures, arbitrary-language or build-runner
  execution, evaluator workload budgets, retained artifact hashes,
  reproducibility bundles, long-horizon quality progress, retained-rate
  benchmark curves, or AlphaEvolve Table 1 code-scale parity; those
  boundaries are tracked by `papers/codebase_scale_benchmark_boundary.json`
  and `papers/candidate_language_runner_boundary.json`.
- Table 1 capability-exhibit reports preserve FunSearch-versus-AlphaEvolve
  row text, source location, rendered artifacts, row-to-gap mappings, and
  implementation status, not validated parity for the individual code-scale,
  language, evaluator, sample-count, model-scale, prompt-context, or
  multi-metric capability rows. The
  `papers/table1_capability_exhibit_boundary.json` sidecar keeps that
  table-provenance-only boundary manifest-validated.
- The shipped `sorting` example is a solved smoke/plateau fixture, not the
  sorting-network rediscovery benchmark. `sorting_network_8` and
  `sorting_network_9` now provide non-comparable benchmark candidates with
  exhaustive zero-one verification, comparator-count/depth metrics, valid
  28- and 36-comparator seeds, checked 19- and 25-comparator targets, and a
  helper-generated hardening bundle for generic negative fixtures, detector
  logs, inventories, summaries, and scope validation. LibreEvolve still lacks
  repeated-run evidence, source-citation sidecars, run-tied hardening
  certification, best-candidate artifact hashes, and paper certification. The
  `papers/sorting_network_rediscovery_boundary.json` sidecar keeps that
  candidate-only boundary manifest-validated.
- Sample-efficiency reports under `runtime.history.sample_efficiency_report`
  are single-run counts for generated proposals, evaluated/valid/admitted
  candidates, retained elites, sampling-eligible candidates, logical LLM
  samples, and a bounded best-score curve. They are not run seed/evaluator
  identity evidence, fixed compute-budget evidence, target-definition
  provenance, score-direction/normalization policy, target-attainment curves,
  target-hit indexes, replicate statistics, matched-budget run groups,
  cost/latency budget curves, thousands-scale benchmark curves, model-size
  comparisons, repeated-sampling comparators, or FunSearch-versus-AlphaEvolve
  budget reproduction; that boundary is tracked by
  `papers/sample_efficiency_boundary.json`.
- Repeated-sampling baseline reports under
  `runtime.history.repeated_sampling_baseline_report` are explicit
  not-configured absence records for the AlphaEvolve `No evolution` /
  repeated base-model sampling comparator. They list observed local sample
  counts and required comparator controls, but they are not executable
  fixed prompt/model/request-parameter/seed/evaluator repeated-sampling runs,
  fixed LLM-call budget evidence, candidate-validation parity,
  sample-index alignment, target metric/threshold linkage, budget-parity
  checks, disabled-evolutionary-feedback proof, disabled critique/feedback
  proof, target-progress curves, comparator artifact hashes, or linked
  evolutionary comparator evidence; that boundary is tracked by
  `papers/repeated_sampling_baseline_boundary.json`.
- Task-specification bundles, `task_specification.json`, and artifact-
  resolution reports link initial programs, evaluators, prompts, backends,
  context, candidate representation, metrics, history streams, best exports,
  marked spans, and supported embedded score causality, not external-validator
  score causality, standalone schema completeness for the full user-provided
  Figure 2 contract, user-authored source identity, prompt/config content
  identity, cross-field consistency validation, task-spec replay preflight,
  arbitrary-language/build-runner task specs, user-authored standalone
  task-spec parity, or full AlphaEvolve task-spec parity; that boundary is
  tracked by `papers/task_specification_boundary.json`.
- Archive restore uses manifest archive-state snapshots plus accepted-history
  rows for current cursor/cell/elite contents; `archive_events.jsonl` replay is
  audit-only and not an ordered MAP-Elites restore engine. That boundary is
  tracked by `papers/archive_event_replay_boundary.json`.
- Scientific-discovery scope is machine-gradeable local evaluator workflow
  scope; robust evaluator-environment fixtures, automatable-domain boundaries,
  setup/cost and expected discovery-value evidence, manual-to-code transition
  policies, and LLM-only idea-stage contracts are tracked by
  `papers/automated_evaluator_scope_boundary.json`.
- Evaluation-cascade reports are runtime attrition and promotion telemetry when
  stages run. They now include `stage_evidence_summary` counts for configured
  stage roles, local stage source refs/hashes when available, runtime samples,
  main-test exposure, and early pruning, plus explicit absent-evidence statuses.
  They are not AlphaEvolve-style cascade-efficiency evidence with stage
  difficulty rationale, evaluator/test-set identities and hashes, benchmark
  seed/sample policy, candidate transition matrices, promotion-decision rule
  attribution, next-stage exposure linkage, transition-denominator
  reconciliation, counterfactual full-evaluation costs, or observed wall-clock
  cost savings; that boundary is tracked by
  `papers/evaluation_cascade_boundary.json`.
- Cascade hypothesis-test gates are runtime policy evidence, not
  benchmark-calibrated AlphaEvolve Section 2.4 cascade proof with repeated-seed
  fixtures, small-filter-to-main-test linkage, benchmark-calibrated
  thresholds, or empirical false-promotion/false-rejection validation; that
  boundary is tracked by `papers/cascade_hypothesis_test_boundary.json`.
- Evaluator/oracle reports register local validators, configured cascade
  stages, and optional LLM feedback graders with arbitration metadata, not
  candidate-level oracle lineage, per-generation feedback traces, primary
  evaluator contract proof, independent reference/statistical-oracle evidence,
  benchmark sufficiency proof, independent disagreement outcomes, or cross-run
  oracle tables; that boundary is tracked by
  `papers/evaluator_oracle_boundary.json`.
- Evaluator workload metadata and `runtime.history.evaluator_workload_report`
  record declared `simple_check`, `inner_search`, `ml_training`, and `custom`
  stage provenance, not managed workload-specific training/search runners,
  checkpoint completeness, score-field-to-artifact causality, or stochastic
  re-evaluation policy.
- Embedded evaluator support is opt-in `embedded_evaluate` stage evidence, not
  full AlphaEvolve Figure 3 evaluator parity with default candidate-owned
  `evaluate(eval_inputs)` problem loading, Figure 3 codebase fixture identity,
  typed eval-input contracts beyond JSON-safe config provenance, stronger
  build/runtime isolation, generated/interactive task-input replay policy
  shared across embedded and external-validator stages, or
  non-static/external-validator causal score linkage; that boundary is tracked by
  `papers/embedded_evaluator_boundary.json`.
- Validator execution policy records are local-subprocess audit evidence:
  `policies.validator_execution`, `evaluation.metadata.validator_boundary`,
  `filesystem_capabilities`, and `resource_limit_policy` declare the current
  temporary subprocess boundary, candidate-root/declared-file filesystem
  scope, optional Python-socket denial metadata, wall-clock timeout cleanup,
  unsupported security sandbox/container status, and unsupported CPU, memory,
  GPU, disk, and process-count quotas. They are not OS/container sandboxing,
  OS-enforced filesystem capabilities, kernel/container network isolation, or
  AlphaEvolve-scale resource-limit enforcement; that boundary is tracked by
  `papers/validator_execution_boundary.json`.
- Validator-boundary consistency checks are CLI/run-inspection evidence:
  `validate_run_artifact_validator_boundary_consistency()` scans manifest-
  backed `history.jsonl` and `failure_history.jsonl` rows, and
  `libreevolve show` reports missing, legacy, or drifting boundary evidence
  with stream/line diagnostics. This is not run-finalization, CI, or release-
  artifact promotion enforcement, and it remains separate from stronger
  OS/container sandboxing and resource-quota enforcement; the promotion-gate
  boundary is tracked by `papers/validator_artifact_promotion_boundary.json`.
- Execution-grounding and incorrect-suggestion reports are local run telemetry
  over accepted, rejected, execution-filtered, invalid-evaluation, parse-error,
  archive-rejected, and accepted-invalid candidates, not independent rejudge
  coverage, sampled audit-denominator policy, candidate-family filter rates,
  beyond-initial-pool novelty audit, audited false-acceptance/false-rejection
  rates, semantic failed-proposal retrieval, or publication-strength filtering
  proof; that boundary is tracked by
  `papers/incorrect_suggestion_audit_boundary.json`.
- Hypothesis-branch and controller-backtracking reports show abandoned-looking
  branches and observed redirects, not controller-owned backtracking policy
  with unpromising-decision rules/thresholds, controller branch-state
  machines, configured suppression/retry behavior, prompt-sampling suppression
  effects, explicit fallback-target events, causal resumed-search replay, or
  cross-run branch tables; that boundary is tracked by
  `papers/controller_backtracking_boundary.json`.
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
  role-specific backend-pool policy, role-specific exploration parameters,
  reward normalization reports, outcome-attribution datasets, async role work
  queues, cross-role interference analysis, experiment-owned quota policy,
  fast/strong model-mix reports, or role-specific budget behavior reports; that
  boundary is tracked by
  `papers/llm_role_scheduler_boundary.json`.
- `throughput_depth` backend selection records cost/latency/depth metadata and
  fast-breadth/strong-depth lane labels, not experiment-level fast/strong
  model-mix validation, fixed compute budget identity, matched
  problem/seed/evaluator controls, provider-model identity for fast/strong
  lanes, lane quota schedules, per-lane token/cost/latency accounting, lane
  switching traces, breadth-volume or breakthrough-quality attribution,
  reserved lane policy, candidate throughput/quality outcomes, or equal-budget
  scheduler comparisons; that boundary is tracked by
  `papers/fast_strong_model_mix_boundary.json`.
- Natural-language proposal metadata is context around executable code
  candidates, not AI-Co-Scientist-style hypothesis representation or
  hallucination-resistance, long-horizon evolution, natural-language-to-code
  bridge, proposal-truth model, or combined AI-Co-Scientist workflow evidence;
  that boundary is tracked by `papers/programmatic_representation_boundary.json`.
- Natural-language preambles are bounded leading metadata before structured
  mutation markers, not configurable preamble policy controls, raw
  full-replacement disambiguation, rationale-quality scoring, cross-run
  preamble tables, proposal-memory joins, or arbitrary unparsed rationale
  handling; that boundary is tracked by
  `papers/natural_language_preamble_boundary.json`.
- Prompt example-copy reports are built-in exact/normalized/skeleton
  diagnostics, not hard/configurable rejection, semantic or renamed-copy
  detection, custom prompt-template inventories, per-template source mapping,
  cross-run copy-rate tables, copy-signal-to-acceptance policy, or
  prompt-example revision guidance; that boundary is tracked by
  `papers/prompt_example_copy_boundary.json`.
- Multi-edit consistency reports are current-run diagnostics, not
  language-aware scope/import resolution, config/resource dependency models,
  required companion-edit inference, cross-file dataflow, benchmark-calibrated
  consistency failures, hard/configurable acceptance gates, or semantic proof
  that accepted edits are coherent; that boundary is tracked by
  `papers/mutation_consistency_boundary.json`.
- Mutation-operator evidence is fixed edit payload grammar and proposal
  metadata, not operator-family declaration schemas, proposal-level operator
  provenance, LLM-constructed operator families, task/failure-aware
  construction, adaptive operator-family selection, operator scoring, or
  benchmark telemetry; that boundary is tracked by
  `papers/mutation_operator_boundary.json`.
- Mutation mode is a configured run-wide `diff` or `full` prompt/parser
  contract, not adaptive per-candidate diff-versus-full selection based on
  code size, workspace shape, task shape, failure history, parser/critique
  fallback policy, selection-reason telemetry, mixed-mode run history, or
  AlphaEvolve-style selection tests; that boundary is tracked by
  `papers/adaptive_mutation_mode_boundary.json`.
- Initial-pool divergence reports are syntactic and shared-metric telemetry,
  not task-specific functional-distance artifacts, evaluator-output distance,
  behavior/output distance, substantially-different threshold policy,
  benchmark-level discovery-distance telemetry, cross-run discovery-distance
  tables, syntax/function joint claim gates, or "substantially different"
  benchmark evidence; that boundary is tracked by
  `papers/initial_pool_divergence_boundary.json`.
- Initial-program idea provenance is optional seed metadata plus a generation-0
  linkage report and design-level seed-variant comparison matrix, not executed
  equal-budget seed-variant result tables, simple/random/researcher-seed
  comparisons, exact rendered prompt digests, prompt-history seed-context
  spans, seed-workspace-hash-to-prompt linkage, per-variant run-artifact
  manifests, replicate protocols, matrix-parameter seed-idea attribution,
  human contribution review/signoff, paper certification rows, or AlphaEvolve
  human-seeded benchmark parity; that boundary is tracked by
  `papers/initial_program_idea_provenance_boundary.json` and
  `papers/initial_program_seed_variant_matrix.json`.
- Initial-program validity can be enforced with
  `initial_program_validity_policy: alphaevolve_strict`, but the default
  permissive baseline still records invalid seeds as diagnostics. The
  `embedded_evaluate_math` smoke fixture now opts into strict mode and has a
  CLI-path manifest regression for a claim-ready single-seed strict report, but
  that does not prove multi-seed strict fixture reports, provider-startup
  strict preflight reports, matrix or constructive-math strict seed fixtures,
  enforced exclusion of optimization-pressure seeds from parity suites, paper
  certification rows, or AlphaEvolve complete initial-program parity; that
  boundary is tracked by
  `papers/initial_program_validity_boundary.json`.
- Problem-formulation metadata and benchmark-fixture readiness reports are
  provenance/readiness telemetry, not populated expert-reviewed matrix or
  constructive-math formulation records, external expert or problem-owner
  identity records, evaluator/result artifact linkage, parameter-scope signoff,
  background-reference artifacts, review timestamps or versions, anti-gaming
  review evidence, non-smoke AlphaEvolve-comparable fixture scope,
  repeated-seed protocols, SOTA/target baselines, fixture-emitted result
  artifacts, anti-gaming negative fixtures, or paper-claim-ready benchmark
  evidence; those boundaries are tracked by
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
  minimum cohort-coverage policy, feedback source artifacts, code/docs diff
  links, validation rerun artifacts, privacy/redaction artifacts,
  review/signoff identity and version records, longitudinal follow-up,
  claim-to-feedback traceability, paper certification rows, reviewed validation
  outcomes, or AlphaEvolve robustness/versatility parity; that boundary is
  tracked by
  `papers/collaborator_feedback_provenance_boundary.json`.
- Duplicate-work reports are run-local exact-workspace cache diagnostics, not
  cross-run workspace indexes, durable evaluation-cache storage, resume-
  spanning replay, cache invalidation/migration policy, stochastic
  re-evaluation policy, semantic duplicate detection, source/output-aware
  cache indexes, or an AlphaEvolve-grade fixed-budget memory claim gate; that
  boundary is tracked by `papers/duplicate_work_policy_boundary.json`.
- Failure memory is run-local diagnostic evidence, not durable cross-run
  failure tables, semantic failed-proposal retrieval, learned repetition
  avoidance, replayable failed-mutation payloads, failure-aware sampling
  policy, or cross-run failure-index migrations; that boundary is tracked by
  `papers/failure_memory_boundary.json`.
- Section 5 Related Work positioning is not inferred from the bundled paper list; the
  missing method-family, representation, feedback/evidence, task-stage,
  proof/witness, complementary-mechanism, and AlphaEvolve positioning taxonomy
  gates are tracked by `papers/related_work_taxonomy_boundary.json`.
- Candidate execution is Python-primary code-file-set execution. The
  abstraction-choice report does not claim AlphaEvolve-style problem-defined
  serializers/materializers/runners, paired solution/search representations,
  abstraction-specific prompts, validators, archive descriptor mappings,
  migration policies, executed bias evidence, or equal-budget
  direct-solution/constructor/search/paired-representation comparisons. The
  design-level abstraction-family matrix records expected rationale and bias
  fields but not benchmark results; these boundaries are tracked by
  `papers/candidate_abstraction_boundary.json` and
  `papers/candidate_abstraction_bias_matrix.json`.
- Candidate language runner reports record metadata-only non-Python language
  and build declarations when configured, including declaration counts and
  unsupported execution status, and link the current Python runner to bounded
  manifest environment provenance. They do not implement arbitrary-language
  runners, build-system execution, arbitrary-runner environment artifacts,
  generated build artifacts, or language-aware marker grammars; that boundary
  is tracked by `papers/candidate_language_runner_boundary.json`.
- Configuration validation is local effective-config validation; live
  provider/model API compatibility is tracked by
  `papers/config_validation_boundary.json`.
- Runtime environment provenance is audit evidence, not a complete replayable
  environment: `libreevolve.environment_reproducibility_policy.v1` covers
  project metadata, known lockfile hashes, installed-distribution metadata,
  bounded/redacted `pip freeze` and `pip config` evidence, NumPy config hashes,
  built-in provider SDK versions, and bounded accelerator runtime/driver hints.
  It does not prove complete install-source interpretation, broader
  non-project build provenance, private package-source identity/authentication,
  remote package artifact hashes, live provider service/default capture,
  accelerator budget accounting, or environment restore/check readiness.
- Runtime budgets are local cooperative generation/evaluation/evaluator-second/
  wall-clock/LLM/provider counters, not per-candidate compute-hour accounting,
  accelerator/worker leases, async queue budgets, or equal-budget execution
  reports; that boundary is tracked by
  `papers/expensive_evaluation_budget_boundary.json`.
- Live run stops cover generations, evaluations, evaluator seconds,
  wall-clock runtime, logical LLM calls, provider attempts,
  provider-reported tokens, configured estimated cost, and retained LLM
  latency. `controller_budget_events.jsonl` and full-runtime restore can
  replay those synchronous counters into resumed runs, but this is not
  provider-output/raw-payload replay, pending-work or async-worker resume,
  cross-run provider-failure policy proof, or a mutation-chain-depth policy
  for slow evaluator feedback; the role-level LLM budget boundary is tracked
  by `papers/llm_budget_policy_boundary.json`, and the terminal
  controller-state versus pending-work resume boundary is tracked by
  `papers/controller_pending_work_resume_boundary.json`.
- Lineage replay evidence is limited to loop-owned deterministic surfaces:
  run-local RNG snapshots, prompt-history replay, deterministic seed/generated
  candidate ids, database-created prompt ids, ordered LLM call ids, and the
  validated `runtime.lineage_replay_policy` included in full-runtime restore
  bundles. Direct `Program()` / `PromptProgram()` UUID4 defaults, provider/model
  outputs, controller pending work, plugin internal randomness, validator
  subprocess randomness, migration-event replay, and end-to-end resumed-trace
  proof remain outside the replay contract. This lineage boundary is tracked by
  `papers/lineage_replay_boundary.json`; the current terminal controller
  evidence is separately bounded by
  `papers/controller_pending_work_resume_boundary.json`.
- Parallel-evaluation readiness is limited to configured local
  `eval_stages[].sample_workers` fan-out, observed sample wall-clock
  compression, and topology linkage. It is not AlphaEvolve-style
  per-candidate compute-hour budgeting, concurrent LLM sampler queues,
  candidate-level async evaluator queues, queue capacity/backpressure policy,
  distributed evaluator nodes, deterministic async result merge/admission
  order, concurrency-safe shared-state mutation, mutation-depth impact
  evidence, or pending-work resume; that boundary is tracked by
  `runtime.history.parallel_evaluation_readiness_report` and
  `papers/parallel_evaluation_readiness_boundary.json`.
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
- Provider request parameters are normalized and logged for supported backends,
  including temperature, top-p, stop sequences, and supported seed fields, but
  this is best-effort sampling-control telemetry rather than a cross-provider
  deterministic generation contract or proof that identical prompts reproduce
  identical provider outputs; that request-telemetry boundary is tracked by
  `papers/llm_stochastic_reproducibility_boundary.json`.
- OpenAI API-mode routing is local adapter policy, not live provider
  capability discovery: omitted or `api_mode: auto` without
  `reasoning_effort` uses Chat Completions, `api_mode: responses` forces the
  Responses API, and configured `reasoning_effort` routes through Responses
  while rejecting `api_mode: chat_completions`.
- Provider capability lookup is static/offline policy evidence:
  `policies.provider_capability_lookup` validates manifest-safe model ids,
  configured API-mode policy, and local compatibility records while keeping
  live model-registry lookup, service/API-version lookup, and
  account-availability validation explicitly false. It is not provider/account
  availability proof or AlphaEvolve-grade provider reproducibility evidence.
- Provider cancellation records are policy/audit evidence for request
  timeouts, ensemble wait deadlines, artifact gates, and quarantine
  observations, not live provider SDK hard cancellation, timeout-driven stop
  enforcement, cross-run provider quarantine resume, richer role-specific
  timeout artifacts, or provider-output raw-payload replay; that boundary is
  tracked by `papers/provider_cancellation_boundary.json`.
- Critique reviewer pools are bounded synchronous first/last-valid mutation
  filters with reviewer telemetry, not async reviewer overlap, calibrated
  reviewer scoring, independent reviewer task definitions, reviewer/generator
  role separation proof, critique-to-revision attribution, reviewer
  score-to-selection policy, reviewer budget quota policy, reviewer
  failure-isolation reports, equal-budget no-reviewer comparisons, reviewer
  reliability ablations, per-reviewer provider isolation, or external reviewer
  timeout artifacts; that boundary is tracked by
  `papers/critique_reviewer_pool_boundary.json`.
- Prompt section packing is mutation-path and final-prompt-boundary evidence,
  not all-role provider-token section packing, exact non-OpenAI provider
  counters, registry/custom role section packing, retrieval/context/plugin/
  failure-memory packing, or full validator-metadata prompt policy; that
  boundary is tracked by `papers/prompt_section_packing_boundary.json`.
- Prompt-template validation covers known placeholders, dry-run formatting,
  configured AlphaEvolve-style mutation-channel requirements, and parent
  placeholder retention for evolved prompt children. Duplicate configured or
  evolved prompt text is intentionally retained as independent prompt arms with
  deterministic ids and shared `template_sha256`, not deduplicated into one
  prompt policy; role-specific compatibility for critique, feedback, and
  meta-prompt call surfaces remains open.
- Stochastic prompt-format reports record weighted `prompt_format_options`
  probabilities, selected alternative hashes/indexes, prompt/call linkage, and
  run-local RNG replay boundaries, not distinct separate config-file source
  identity, certified human-authored alternatives, author/reviewer provenance,
  or revision history for AlphaEvolve Section 2.2 stochastic-formatting parity;
  that boundary is tracked by
  `papers/stochastic_prompt_format_boundary.json`. The broader framework RNG
  restore boundary is tracked by `papers/runtime_rng_replay_boundary.json`.
- Configured `llm_prompt_roles` can send bounded system/developer instruction
  text through built-in backend provider payloads and records hash-only
  `prompt_role_policy` call telemetry. The primary-prompt instruction report
  still does not join that telemetry back to generated prompt records, so
  AlphaEvolve primary-prompt role-placement parity remains an evidence gap
  rather than a globally absent backend feature.
- Meta-prompt scoring currently means local `PromptDatabase` accounting over
  configured `absolute` or `improvement` child-score rewards, normalized to
  configured finite bounds and selected with a UCB-style prompt-arm heuristic.
  Prompt history records reward policy metadata and meta-prompt mutation
  requests include bounded prompt-performance evidence; calibrated
  prompt-specific reward models, prompt-lineage ablation reports, and stronger
  prompt-policy attribution remain open.
- `PromptDatabase` is a deterministic local prompt-arm history/scoring store
  with append-only prompt-history replay, lineage ids, duplicate-arm audit
  identity, and optional interval-based template/context-policy mutation. It is
  not yet a prompt-side analogue of the solution database with MAP-Elites or
  island retention, descriptor/objective indexes, archive-event streams,
  migration/rebin semantics, or async/controller-resumable prompt work.
- Meta-prompt context-policy mutation is validated only for the current
  `libreevolve.prompt_context_policy.v1` fields exposed in
  `runtime.prompt_context_policy_coverage` and meta-prompt capability-summary
  hashes, not retrieval/summarization policy, learned or semantic source
  selection, non-`PromptSampler` role policy, DeepEvolve-style debug/
  refinement context control, or full AlphaEvolve-grade prompt evolution.
- DeepResearch retrieval evidence is bounded, redacted, and non-authoritative:
  retained payload sidecars and inventories, source-ranking provenance,
  source-content trust/lexical-grounding policies, transport policy,
  context-audit policy, semantic-boundary audits, and run-level retrieval
  evidence coverage can verify selected retained evidence without claiming raw
  provider/source payload retention, TLS certificate-chain replay, semantic
  source correctness, learned/external ranking, full retrieval replay, or
  DeepEvolve-style cross-file research/debug-loop parity.
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
- The May 7, 2026 Google DeepMind AlphaEvolve impact article is official
  source context, not local LibreEvolve benchmark support. Its DeepConsensus,
  AC Optimal Power Flow, Earth AI, Willow quantum-circuit, public-gallery,
  TPU-design, cache-replacement, Spanner, compiler-storage, UI/API, and
  customer-deployment claims remain source-scoped until local fixtures,
  source snapshots, benchmark reports, independent verification, and
  operational lifecycle/adoption evidence for the article's pilot-to-core,
  regular-tool, Google Cloud/commercial, UI/API, rollout, and owner claims
  exist. The related Google Cloud launch post, AlphaEvolve Service API Early
  Access wording, Gemini Enterprise Pre-GA restricted-access documentation, and
  Google Keyword one-year update are product/source surfaces only; Cloud
  service API docs, private-preview eligibility, Pre-GA terms, account-team
  access boundaries, console/API/billing artifacts, customer availability, and
  managed-agent semantics are not implemented or locally verified;
  that boundary is tracked by `papers/alphaevolve_2026_impact_boundary.json`.
- ArXiv `2605.14718` is FHE-on-TPU AlphaEvolve application context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no TFHE/Jaxite or CKKS/CROSS primitive harness, Google Cloud
  TPUv5e execution provenance, FHE correctness-test suite, generated
  cryptographic-kernel artifacts, baseline implementation identity, latency
  benchmark rows, or local reproduction of the reported 2.5x, 1.31x, and 1.18x
  speedups.
- ArXiv `2605.05921` is AlphaEvolve HCI/user-study context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no
  formative-study dataset, participant/session trace schema,
  intentmaking/sensemaking event taxonomy, AlphaEvolve UI/dashboard artifact
  inventory, goal-revision or human-intervention records, privacy/redaction
  protocol for study data, coded qualitative-analysis evidence, or
  collaborative scientific-discovery instrument workflow support.
- ArXiv `2605.01794` is radar/resource-allocation AlphaEvolve application
  context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no radar scenario/target-count taxonomy, physically inspired
  feature schema, deterministic constraint-satisfying power-allocation
  transform, multi-target tracking simulator, baseline iterative solver
  identity, average relative performance-loss benchmark rows, cross-scenario
  generalization evidence, three-orders speedup reproduction, or independent
  checker output.
- ArXiv `2602.23413` is adaptive meta-evolution context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no
  adaptive strategy-genome schema, outer meta-evolution loop, strategy-credit
  assignment, dynamic search-policy update artifacts, EvoX task-suite
  taxonomy, baseline comparison table against AlphaEvolve/OpenEvolve/GEPA/
  ShinkaEvolve, token-efficiency report, strategy ablation records, or
  independent reproduction output.
- ArXiv `2602.02919` is context-memory framework evidence only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no
  first-class semantic-delta schema, node-transition effect attribution,
  semantic-delta memory bank, multi-level database/index metadata, progressive
  disclosure traces, token-savings report, full-code-history baseline
  comparison, scientific-task benchmark taxonomy, or independent reproduction
  output.
- ArXiv `2606.06473` is long-horizon MLE framework context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no
  MLE-Bench task harness, Progressive MCGS state schema, graph-based
  reference-edge provenance, entropy-inspired progressive schedule,
  Retrospective Memory knowledge base or global memory artifacts, adaptive
  coding-mode traces, 12-hour medal-rate/valid-submission report,
  mathematical-algorithm baseline comparison, linked-code audit, or
  independent reproduction output.
- ArXiv `2605.09764` is cost-aware search-architecture context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no LEVI-style diversity-preserving solution-database report,
  large/small model mutation-router policy, role-assignment trace,
  rank-preserving proxy benchmark, rollout/provider-cost accounting report,
  systems-research benchmark fixture, prompt-optimization budget comparison,
  linked-code audit, or independent reproduction output.
- ArXiv `2601.10657` is long-horizon consistency framework context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no context-pollution detector, hierarchical
  context-management/pruning artifacts, mode-collapse diagnostics,
  momentum-based backtracking controller, unified crossover/backtracking
  sampler, trajectory-collaboration diagnostics, LLM-SR/KernelBench/Modded
  NanoGPT benchmark report, linked-code audit, or independent reproduction
  output.
- ArXiv `2605.08520` is asynchronous-stage orchestration context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no asynchronous worker queue, stage dependency scheduler,
  artifact-version lineage DAG, stale-artifact detector, staleness repair
  policy, speculative stage-completion records, adaptive workflow controller,
  EvolBench/ChatDev/MetaGPT benchmark report, 3.5x/4.9x throughput
  reproduction, linked-code audit, or independent reproduction output.
- ArXiv `2605.20086` is trace-diagnostic evaluation context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no
  EvoTrace-compatible trace schema, nine-class edit taxonomy annotation
  pipeline, LLM-as-judge edit reannotation validation, parent-child search
  graph export, prompt/context substitution replay, model substitution replay,
  component-removal intervention harness, constant-retuning baseline,
  deterministic deleted-line reintroduction/cycling detector, held-out
  generalization report, or independent reproduction output.
- ArXiv `2605.01120` is an unimplemented constructive-math benchmark
  candidate; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no Zarankiewicz parameter manifest, bipartite graph
  construction schema, `K_{s,t}`-free verifier, exact-value/lower-bound table,
  generated-algorithm artifact hashes, OpenEvolve setup provenance,
  reward-function specification, upper-bound comparison ledger, per-parameter
  cost accounting, or independent reproduction output for the three exact
  values, 41 lower bounds, four matched closed cases, or sub-$30 cost claim.
- ArXiv `2604.01658` is autonomous multi-agent evolution context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no long-running autonomous agent sessions, shared persistent
  memory repository, asynchronous multi-agent execution runtime,
  heartbeat-based intervention controller, isolated per-agent workspaces,
  evaluator separation layer, resource/session/health manager,
  knowledge-reuse analysis, 10-task SOTA report, 3-10x improvement-rate
  reproduction, Anthropic kernel-engineering 1363-to-1103 cycle reproduction,
  linked-code audit, or independent reproduction output.
- ArXiv `2605.13821` is harnessed meta-editing context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no
  process-level evolution state exposing accumulated candidates, feedback,
  traces, failures, or costs, meta-agent procedure or agent-context editor,
  standardized editable evolution workspace, protected evaluator boundary,
  searchable candidate history for meta-editing, meta-editing phase/evolution
  segment runner, run-plan contract, procedure-versus-agent evolution
  instantiation, five-baseline agentic/reasoning benchmark report, 26%
  relative-improvement reproduction, three-task open-ended optimization report,
  linked-code audit, or independent reproduction output.
- ArXiv `2605.09959` is verifier-free co-evolution context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no
  Hint-delta intrinsic-reward computation from unassisted versus
  hint-conditioned Generator responses, Proposer model, Generator model,
  self-generated query/hint dataset, GRPO proposer trainer, DPO generator
  trainer, co-evolution training loop, pseudo-label noise filter,
  exploration-coverage report, best-iterate suboptimality fixture,
  unverifiable-domain benchmark, external-judge reward-hacking comparison,
  linked-code audit, or independent reproduction output.
- ArXiv `2605.21605` is multimodal trajectory-distillation context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no image-generation tool pipeline, visual-reference
  ingestion, prompt-rewriting/layout-planning/image-generation/refinement
  trajectory schema, tool-call artifact lineage, Agentic Visual Experience
  Distillation or Visual Experience Distillation target, dense token-level
  supervision record, multimodal policy-update loop, GenEvolve-Data metadata,
  GenEvolve-Bench task/report, baseline comparison, linked-code audit, or
  independent reproduction output.
- ArXiv `2605.29847` is self-evolving reward-rubric context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no
  single-policy Reasoner/Rubric-Generator co-evolution loop, generated-rubric
  provenance, meta-verifier records, zero-variance pruning records,
  Leave-One-Out peer-consensus traces, criteria memory pool, dense
  multi-objective reward vectors, expert-prior rubric expansion,
  medical/writing/science benchmark report, reward-hacking audit, linked-code
  audit, or independent reproduction output.
- ArXiv `2605.29293` is learning-signal optimization context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no
  sparse-reward cooperative MARL harness, Critic LLM diagnosis role,
  Generator LLM reward-shaping role, compact behavior evidence record,
  stage-specific coordination-failure diagnosis, reward-shaping configuration
  artifact, branch-validation trajectory, validated-update promotion gate,
  main-training trajectory provenance, learning-efficiency report, linked-code
  audit, or independent reproduction output.
- ArXiv `2512.18746` is memory-architecture evolution context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no
  explicit encode/store/retrieve/manage memory-component design space,
  memory-architecture genotype, memory-system mutation/evaluation loop,
  experiential-knowledge co-evolution trace, EvolveLab benchmark mapping,
  static-memory baseline comparison, cross-task or cross-LLM transfer report,
  performance-delta record, linked-code audit, or independent reproduction
  output.
- ArXiv `2606.06114` is healthy-evolution oversight context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no
  ANCHOR human-like oversight agent, phase-specific norm-correction interface,
  safety-drift metric lineage, output-verification intervention records,
  reflection/review artifact stream, supervision-frequency/cadence trace,
  preservation-of-objective-performance report, coding/math/safety benchmark
  report, linked-code audit, or independent reproduction output.
- ArXiv `2605.27276` is harness-plus-weight self-improvement context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no Feedback-Agent that chooses between harness and weight
  updates, editable task-agent harness inventory, harness patch provenance,
  online RL/fine-tuning loop, adapter/checkpoint lifecycle,
  trajectory-to-training-data promotion policy, rollback/resume policy,
  harness-only versus weight-only versus combined ablation report,
  LawBench/kernel/scRNA benchmark report, linked-code audit, or independent
  reproduction output.
- ArXiv `2606.06324` is trace-grounded harness repair context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no HTIR
  trace-normalization schema, raw-trace normalization record, harness-code
  linkage, step-level provenance, execution/tool/context/lifecycle/
  observability/verification/governance harness-layer attribution taxonomy,
  recurring flaw consolidation, scoped repair operator schema, generated
  harness patch artifact, flaw-specific validation specification,
  unacceptable-regression threshold record, held-out SWE-Bench Verified/
  Terminal-Bench 2.0 Verified/GAIA/AppWorld benchmark report, linked-code
  audit, or independent reproduction output.
- ArXiv `2606.05922` is retrospective harness optimization context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no unlabeled past-trajectory harness optimizer, hard/diverse
  coreset selector, DPP coreset record, parallel retrospective re-solve
  workflow, group rollout artifact, self-validation diagnostic,
  self-consistency diagnostic, candidate harness-update set, pairwise
  self-preference selector, label-free promotion policy, deployment/rollback
  metadata, behavior-pattern shift report, long-horizon accuracy report,
  SWE-Bench Pro 59%-to-78% reproduction, linked-code audit, or independent
  reproduction output.
- ArXiv `2605.30621` is harness-capability disentanglement context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no harness-updating metric schema, harness-benefit metric
  schema, evolver-versus-task-solver model-pair matrix, capability-tier
  grouping record, cross-benchmark harness self-evolution report, activation-
  failure audit, adherence-failure audit, capability-budget recommendation
  report, public-code snapshot audit, or independent reproduction output.
- ArXiv `2604.25850` is agentic harness observability context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no
  file-level editable harness component graph, component-observability schema,
  layered drill-down trajectory evidence corpus, raw-trace-to-digest
  provenance, decision-observability prediction contract, next-round
  falsification record, per-edit rollback manifest, ten-iteration
  Terminal-Bench 2 report, SWE-bench-verified transfer report, cross-family
  transfer report, tools/middleware/memory ablation, public-code snapshot
  audit, or independent reproduction output.
- ArXiv `2605.13357` is AI harness runtime-substrate context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no
  complete eleven-responsibility harness contract, H0-H3 harness-ladder
  fixture, trace-based episode-package schema, controlled validation-task
  reproduction, model-harness-environment capability equation record,
  failure-attribution taxonomy report, deterministic requirement-check
  package, structured verification report, public-code snapshot audit, or
  independent reproduction output.
- ArXiv `2605.21516` is inference-time trajectory-alignment context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no harness parameterization for decomposition versus guided
  execution, workflow-granularity sweep, retry-budget study, guidance-induced
  action-reweighting report, stage-level gap metric, over-decomposition
  failure report, over-pruning failure report, hallucinated-execution failure
  report, partial-harnessing stopping rule, controlled synthetic experiment,
  terminal-agent benchmark reproduction, linked-code audit, or independent
  reproduction output.
- ArXiv `2606.01770` is adaptive auto-harness deployment context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no chronological open-ended task-stream schema,
  history-growth record, task-heterogeneity report, distribution-shift
  detector, evolution-loss/adaptation-loss decomposition, stateful multi-agent
  evolver, harness tree, solve-time routing policy, human-steering hook,
  overfitting/accuracy-peak-decline report, prediction-market/security-
  competition/event-forecasting benchmark reproduction, five-baseline
  comparison, linked-code audit, or independent reproduction output.
- ArXiv `2603.28052` is outer-loop harness-code optimization context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no first-class harness-code candidate schema,
  filesystem-visible harness workspace, agentic proposer that edits harness code,
  candidate harness edit provenance, execution-trace feedback bundle,
  score/provenance replay package, outer-loop harness search controller,
  online text-classification reproduction, 200-problem IMO-level
  retrieval-augmented math reproduction, TerminalBench-2 reproduction,
  held-out-model transfer report, linked-code audit, or independent
  reproduction output.
- ArXiv `2602.16928` is AlphaEvolve MARL algorithm-discovery context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no CFR candidate schema, PSRO candidate schema, OpenSpiel
  imperfect-information game fixture, game-suite split record, exact
  exploitability metric record, exact best-response oracle record, VAD-CFR
  result row, SHOR-PSRO result row, WOP-CFR distillation row, PM-PSRO
  distillation row, IQM ablation audit, random normal-form validation row,
  baseline solver ledger, generated solver artifact hash, or reproducible
  CFR/PSRO runtime evidence; `papers/multiagent_learning_boundary.json`
  records that absence boundary.
- ArXiv `2603.09172` is AlphaEvolve constructive Ramsey-number context only;
  the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no Ramsey graph candidate schema, `run()` primary/prospect
  graph contract, graph witness artifact schema, clique/independent-set
  verifier, Ramsey parameter row, new lower-bound row, matched-best-known row,
  exact-known-bound recovery row, graph vertex-count record, implied
  lower-bound record, Google Research construction/code snapshot hash,
  initialization-family record, search budget or seed record, algorithm-summary
  audit record, or independent checker output; `papers/ramsey_numbers_boundary.json`
  records that absence boundary.
- ArXiv `2603.06692` is AlphaEvolve-assisted local-correction combinatorics
  context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no bipartite graph-reconstruction harness, planar
  graph-reconstruction harness, Alon-Tarsi Latin-square involution harness,
  Rota-basis linear-matroid exchange harness, candidate certificate schema,
  local-correction policy API, symmetry-scramble record, hard-negative replay
  buffer, evolved code-block artifact hash, Gemini experiment-summary artifact,
  reported metric table, conjecture/proof-status ledger, repository snapshot,
  or independent verifier output; `papers/combinatorics_berczy_boundary.json`
  records that absence boundary.
- ArXiv `2603.08679` is AlphaEvolve mechanism-design result context only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no bilateral-trade distribution candidate schema, fixed
  Discrete Equal Revenue buyer fixture, evolved seller CDF generator runtime,
  PMF/CDF/survival validator, first-best GFT evaluator, seller-offering GFT
  evaluator, buyer-offering GFT evaluator, Random-Offerer ratio evaluator,
  `1e-15` integer-rounding precision policy, witness distribution artifact,
  evolved or evaluation code hash, prior-baseline row, alternate-search
  attempt row, BIC/BB/IR assumption record, unrounded-mixture caveat handling,
  or independent checker output; `papers/bilateral_trade_boundary.json`
  records that absence boundary.
- ArXiv `2601.21096` is AlphaEvolve compiler-optimization application context
  only; the root README now defers source-specific paper lists to
  `papers/README.md`, which remains the complete implementation-status index.
  LibreEvolve has no executable C++ decision-logic candidate schema, LLVM/XLA
  compiler-pass integration, EVOLVE-BLOCK compiler-source span record, compiler
  rebuild record, macro-benchmark harness, binary-size metric record,
  end-to-end performance metric record, Vizier-style autotuning record, LLVM
  function-inlining result row, register-allocation priority-rule row, XLA
  graph-extraction row, XLA auto-sharding row, expert/neural baseline row,
  temporal/domain generalization row, generated-policy maintainability row, or
  dedicated Magellan runtime repository; `papers/magellan_boundary.json`
  records that absence boundary.
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
  report links remain active code and paper TODOs; that exhibit-specific
  boundary is tracked by `papers/figure6_scheduling_exhibit_boundary.json`.
- Kernel documentation does not yet reproduce AlphaEvolve Figure 7 Pallas
  tiling-problem exhibit provenance: matrix-shape variable definitions,
  tile-parameter schema, accelerator/memory/fusion/compiler-context
  annotations, diagram source data, rendered visual artifact hashes, rendering
  parameters, and links to shape-corpus/runtime reports remain active code and
  paper TODOs; that exhibit-specific boundary is tracked by
  `papers/figure7_pallas_tiling_exhibit_boundary.json`.
- Kernel systems-result reports currently cover generic domain gates and
  claim-calibration metadata, not Pallas/Gemini input-shape corpus provenance,
  deterministic train/eval split hashes, real TPU runtime artifacts,
  expert-baseline tiling heuristic identity, tiling-only candidate boundaries,
  unchanged-operation correctness-by-construction evidence, engineering-effort
  calibration, or production/workflow adoption; the shape-corpus/runtime
  boundary is tracked by `papers/kernel_tiling_shape_corpus_boundary.json`.
- Pallas workflow documentation does not yet prove AlphaEvolve-style
  automation of search-based autotuning or manual tiling-heuristic work:
  baseline workflow class, autotuning search/retuning policy, manual
  authoring/review effort, input-shape-change sensitivity, hardware-expertise
  assumptions, and model-developer ergonomics comparisons remain active code
  and paper TODOs; that workflow-baseline boundary is tracked by
  `papers/pallas_workflow_baseline_boundary.json`.
- Gemini self-training wording remains bounded: README does not yet claim that
  a deployed Pallas kernel optimization affected the training workload of the
  same Gemini-family system that powered AlphaEvolve, nor that before/after
  production training metrics, engineering-velocity evidence, rollout state,
  or safety/rollback records justify an AlphaEvolve-style self-optimization
  interpretation; that self-training-loop boundary is tracked by
  `papers/gemini_self_training_loop_boundary.json`.
- Hardware RTL/EDA records validate HDL source boundaries, synthesis/PPA
  provenance, timing/power/area constraints, equivalence or formal-verification
  evidence, designer validation, downstream synthesis confirmation, RTL-flow
  placement, adoption rationale, integration targets, deployment impact, hashes,
  flags, and artifact refs, not real Verilog/RTL source, synthesis/PPA runs,
  verification logs, designer signoff, downstream-synthesis artifacts,
  upcoming-chip integration, or deployment/time-to-market evidence; that
  metadata-versus-artifact boundary is tracked by
  `papers/hardware_rtl_eda_evidence_boundary.json`.
- Hardware rewrite records validate before/after Verilog hashes, rewrite diff
  hashes, changed spans, removed-bit or signal metadata, component and
  matrix-unit context, rewrite category/rationale, and PPA/verification refs,
  not real before/after Verilog files, exact diff or AST artifacts,
  removed-bit inventories, component review files, or per-bit functional and
  PPA evidence for the TPU arithmetic-circuit rewrite; that concrete rewrite
  boundary is tracked by `papers/hardware_rewrite_artifact_boundary.json`.
- Hardware contribution records validate Gemini/AlphaEvolve model-family
  relationship, run/backend identity, TPU generation and arithmetic-circuit
  identity, novelty basis, first-direct-contribution scope, integration
  milestone, hardware review scope, synthesis-rediscovery caveat, confirmation
  flags, and artifact refs, not real model/run/backend records, reviewed
  TPU/circuit identifiers, firstness evidence, integration records, hardware
  signoff files, or synthesis-rediscovery audit artifacts; that attribution
  boundary is tracked by
  `papers/hardware_contribution_attribution_boundary.json`.
- Compiler IR records validate IR-origin/editability boundaries,
  compiler-generated baseline provenance, reference and input-generator hashes,
  numerical tolerance policy, final expert-confirmation scope, per-edit
  reference-check metadata, abstraction-level attribution, and artifact refs,
  not real XLA/FlashAttention edit artifacts, randomized input coverage,
  reference-check outputs, tolerance/failure logs, or expert all-input signoff;
  that compiler-IR reference-check boundary is tracked by
  `papers/compiler_ir_reference_check_boundary.json`.
- Compiler stack records validate workload/model configuration,
  FlashAttention/Pallas kernel identity, JAX pre/postprocessing boundaries,
  XLA lowering stage, hardware target, lowered-IR hash, optimization decision
  category, and artifact refs, not real Transformer/inference configuration
  records, Pallas source snapshots, JAX wrapper artifacts, XLA stage outputs,
  hardware-target records, lowered-IR files, or decision-evidence artifacts;
  that stack-context boundary is tracked by
  `papers/compiler_stack_context_boundary.json`.
- Compiler adoption records validate adoption-path classification, target
  compiler/version/pass identity, bounded use-case scope, optimization artifact
  identity/hash, integration owner, reviewer scope, adoption state,
  rollout/revert state, workflow-handoff boundary, and artifact refs, not real
  compiler patch/pass artifacts, use-case integration records, reviewer signoff
  files, deployment or rollback logs, or AlphaEvolve-in-compiler-loop evidence;
  that adoption-path boundary is tracked by
  `papers/compiler_adoption_path_boundary.json`.
- Self-improvement and distillation claims remain absent: README does not yet
  identify LibreEvolve runtime/provider/evaluator/compiler/benchmark components
  as evolved optimization targets, link evolved candidates to measured
  improvements in LibreEvolve's own execution path, record deployment/adoption
  or rollback/safety evidence, or provide distillation datasets, training runs,
  or model-evaluation artifacts derived from evolved programs. The
  `papers/self_improvement_distillation_boundary.json` sidecar keeps that
  Discussion-context-only boundary manifest-validated.
- Feedback-loop cadence and environment-ROI claims remain absent: README does
  not yet record loop IDs, next-version targets, elapsed-month cadence,
  moderate-gain calibration, setup or maintenance costs for robust evaluator
  environments, expected versus realized discovery value, gating assumptions,
  or readiness evidence for expanding AlphaEvolve-style evaluator environments.
  The `papers/self_improvement_cadence_boundary.json` sidecar keeps that
  months-scale/environment-economics boundary manifest-validated.
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
- Documentation alignment checks are path, manifest, TODO-coverage,
  sidecar-registry, top-level README/ROADMAP/papers-index claim-inventory
  guards, structural `docs/status.md` ledger inventory, and a ROADMAP
  readiness taxonomy boundary. The checked
  documentation-claim inventory records file-offset source anchors, local
  evidence-ref existence records, Markdown fragment-anchor resolution records,
  audited surface heading records with uncovered heading-to-claim gap records
  linked to active TODO owners, and status-ledger implemented/limit bullet
  spans, hashes, status-signal terms, and local backtick-path existence
  records. It also records a structural run-artifacts guide inventory comparing
  the documented top-level artifact tree with the current overwrite-cleanup
  artifact set. These are not semantic proof that every README, ROADMAP,
  papers-index, TODO, `docs/run-artifacts.md`, or `docs/status.md` statement is
  current. `papers/roadmap_readiness_boundary.json` separately records
  stable readiness categories, weights, raw TODO-ledger completion, and
  weighted TODO-ledger completion while keeping semantic AlphaEvolve
  implementation readiness false. `papers/todo_ledger_ownership_boundary.json`
  records TODO owner files, active/completed counts, active-ledger checked
  marker drift, and exact normalized-title duplicate groups while keeping
  canonical underlying-gap ids and canonical completion percentages absent;
  those boundaries are tracked by
  `papers/todo_ledger_ownership_boundary.json`,
  `papers/roadmap_readiness_boundary.json`,
  `papers/roadmap_source_span_disposition_boundary.json`,
  `papers/roadmap_non_goal_contradiction_boundary.json`,
  `papers/roadmap_good_first_followups_boundary.json`,
  `papers/roadmap_phase_sequence_boundary.json`,
  `papers/roadmap_operational_maturity_boundary.json`,
  `papers/roadmap_representative_benchmark_portfolio_boundary.json`,
  `papers/roadmap_plugin_extensibility_boundary.json`,
  `papers/roadmap_backend_scheduling_critique_boundary.json`,
  `papers/roadmap_async_resumable_runtime_boundary.json`,
  `papers/roadmap_prompt_context_system_boundary.json`,
  `papers/documentation_truthfulness_boundary.json` and
  `papers/documentation_claim_inventory.json`.
- ROADMAP source-span disposition evidence currently maps the six core
  AlphaEvolve anchors from `papers/implementation_evidence_map_boundary.json`
  to ROADMAP section ids, phase buckets, sidecars, and TODO links, and records
  53 paper-index rows with only the AlphaEvolve source row dispositioned by
  this core matrix. This is not an exhaustive retained-PDF section/figure/
  table/appendix/application-result coverage matrix.
- ROADMAP non-goal contradiction evidence now assigns stable ids to the three
  current ROADMAP non-goals, maps nine constrained documentation surfaces,
  validates required safe-scope phrases, and records zero exact forbidden
  support-claim phrase matches for that bounded surface set. This is not a
  runtime metadata scan, plugin docstring scan, exhaustive Markdown corpus
  scan, CI non-goal promotion gate, or intentional-promotion workflow.
- ROADMAP Good First Follow-Ups evidence now records the four current priority
  items with stable ids, active TODO refs, priority rationale,
  dependency-readiness labels, validation gates, and AlphaEvolve impact labels.
  This is not dependency-state refresh automation, stale-priority detection,
  calibrated priority scoring, CI freshness gating, or owner review signoff.
- ROADMAP phase-sequencing evidence now records the Near Term, Mid Term, and
  Longer Term sequence for ten major ROADMAP sections, active blocker TODO
  refs, validation-gate labels, and promotion criteria. This is not a full
  dependency graph, stale-phase detector, promotion/demotion workflow, CI
  phase freshness gate, or owner review signoff.
- ROADMAP representative-benchmark portfolio evidence now records five
  portfolio families spanning sorting-network rediscovery, matrix tensor
  targets, constructive-math geometry, systems/kernel/scheduling work, and
  smoke-fixture guardrails, with domains, validator-strength labels, current
  sidecar refs, active TODO refs, baseline/SOTA target labels, artifact-output
  requirements, and readiness-status labels. This is not a domain-coverage
  matrix, benchmark admission checklist, repeated-seed run matrix, anti-gaming
  certification, SOTA/baseline citation sufficiency proof, portfolio-balance
  score, CI freshness gate, or owner review signoff.
- ROADMAP plugin-extensibility evidence now records six plugin surfaces:
  built-in catalog, entry-point plugins, direct instances, future custom
  registries, hook isolation, and plugin artifact lifecycle, with
  configuration shape, package/source identity, constructor provenance,
  artifact hashing, trust-boundary, paper-scope attribution, validation-gate,
  code-ref, sidecar-ref, active-TODO, and readiness labels. This is not a
  plugin trust-boundary matrix, plugin admission checklist, direct constructor
  value/schema registry, versioned custom plugin registry, artifact lifecycle
  hash policy, runtime isolation policy, paper-scope attribution policy,
  stale-readiness detector, or owner review signoff.
- ROADMAP backend-scheduling and critique evidence now records nine tracks:
  heuristic UCB rewards, role-scoped routing, provider diagnostics/pricing,
  cancellation/quarantine, fast/strong model mix, sample efficiency,
  repeated-sampling baselines, Gemini provider parity, and critique reviewer
  pools, with selection-policy, reward-assumption, budget/quota,
  pricing/default-rate, diagnostics/replay, cancellation, resume,
  equal-budget, reviewer-isolation, Gemini-substitution, sidecar-ref,
  active-TODO, validation-gate, and readiness labels. This is not a
  backend-role capability matrix, critique-control checklist, calibrated
  reward policy, role quota ownership, live provider pricing/default evidence,
  raw provider replay, live hard cancellation, equal-budget scheduler
  comparator, first-class Gemini lane evidence, async reviewer isolation,
  stale-readiness detector, or owner review signoff.
- ROADMAP async/resumable-runtime evidence now records nine criteria for
  topology, parallel evaluation, controller pending work, archive-event replay,
  RNG/lineage replay, provider/plugin nondeterminism, budget resume,
  environment replay, and resumed-trace proof, with current scope,
  missing-readiness, sidecar-ref, active-TODO, validation-gate, and readiness
  labels. This is not an async-state inventory, replay-resume acceptance
  checklist, controller queue checkpoint, LLM sampler task state, evaluator
  pending-work state, deterministic async merge/admission order, ordered
  migration restore engine, provider-output replay, plugin RNG replay, async
  budget accounting, external environment replay, end-to-end resumed trace
  proof, stale-readiness detector, or owner review signoff.
- ROADMAP prompt/context-system evidence now records nine criteria for
  role-template compatibility, context-source selection, token section packing,
  stochastic prompt-format provenance, retention/replay policy, retrieval
  integrity, proposal-memory semantics, meta-prompt reward evidence, and
  prompt-database lifecycle, with current scope, missing-readiness,
  sidecar-ref, active-TODO, validation-gate, and readiness labels. This is not
  a prompt-role capability matrix, deterministic context summarization,
  all-role provider-token section packing, separate prompt-format source
  provenance, full prompt replay-retention policy, audit-grade retrieval
  source integrity, semantic proposal memory, calibrated meta-prompt rewards,
  prompt-database archive lifecycle, prompt/context benchmark evidence,
  stale-readiness detector, or owner review signoff.
- ROADMAP operational-maturity evidence now records six section-level criteria
  with risk classes, current sidecar refs, active TODO refs, and
  acceptance-gate labels. This is not a global acceptance threshold, unified
  run-artifact lifecycle inventory, semantic docs verification, signed release
  provenance, cross-platform CI policy, or owner review signoff.
- Implementation evidence mapping now has core AlphaEvolve requirement anchors
  for markers, evaluator cascades, LLM prompting/sampling, evolutionary
  database behavior, async/distributed topology, and published benchmark
  evidence. The checked `papers/status_claim_inventory.json` sidecar now
  records row-level paper status inventory plus status-cell phrase hashes,
  source offsets, local artifact mention source offsets, candidate
  evidence-link lists, and referenced local artifact and TODO evidence-path
  source offsets/existence checks plus row-specific TODO content
  matched source tokens, block hashes/source offsets, artifact-mention source
  offsets, phrase-local TODO block records, and structural absence-signal
  source-offset classification.
  The checked
  `papers/benchmark_coverage_inventory.json` sidecar now records structural
  implemented-benchmark coverage bullet evidence plus file character offsets,
  mention-level source-token/local-artifact/limitation file offsets, and
  referenced local artifact existence checks. This is not an exhaustive
  source-span coverage matrix, per-phrase evidence-link sufficiency proof,
  status-cell semantic verifier, implemented-benchmark bullet semantic
  verifier, absence-sentence freshness
  matrix, or generated code-audit report; that boundary is tracked by
  `papers/implementation_evidence_map_boundary.json`.
- Paper-index implementation-status validation now records 60 unique referenced
  local artifact paths across status rows and zero missing referenced local
  artifacts, plus 6 unique referenced TODO evidence paths, 289 TODO evidence
  path mention records, and zero missing referenced TODO evidence paths. It
  also records 175 matched TODO content source tokens, 950 row-specific TODO
  block hashes/source offsets, 291 TODO content artifact mention source-offset
  records, zero status-row local artifact paths, and zero status-phrase local
  artifact paths missing from linked row-specific TODO evidence, 286
  phrase-level TODO block records, and
  structurally classifies 87 status-cell
  absence-signal phrases with 99 source-offset records. This is path/content
  linkage and signal evidence, not proof that each artifact or TODO link is
  semantically sufficient or that absence wording is fresh.
- AlphaEvolve arXiv abstract-page metadata now has a pinned HTML byte count,
  SHA-256 digest, normalized author list, subject classes, DOI URL, submitted
  timestamp, TeX-source URL, license URL, and submission-history entry.
  DataCite DOI, TeX/e-print, license-page, and current-version/floating-PDF
  digest sidecars now preserve bounded response metadata and hashes, and the
  raw HTTP headers, DOI landing-resolution, and DataCite full-response sidecars
  preserve pinned source response evidence, and the TeX archive-retention
  sidecar retains the full e-print archive plus member inventory. The
  arXiv abstract snapshot and license-page HTML retention sidecars retain their
  full HTML artifacts and validate byte/hash markers; the current-version
  sidecar validates the retained floating PDF artifact bytes/hash. The
  cached-PDF header consistency sidecar validates first-page header extraction
  hashes and markers. The metadata extraction-script sidecar pins the offline
  extraction script path/hash, entrypoint, CLI, and retained source-artifact
  coverage. This is not an automated CI refresh gate.
- Paper-index benchmark coverage validation currently catches structural
  coverage issues and one narrow `Implemented`-but-`not implemented`
  contradiction, and the committed benchmark coverage inventory records source
  spans, file character offsets, hashes, source-token match file offsets, local
  artifact mention file offsets, artifact-existence records, limitation-signal terms/source
  offsets/counts, and contradiction flags for each implemented bullet. It
  currently records 3 referenced manifest source IDs across 15 source-token
  match records,
  116 unique referenced local artifact paths and zero missing referenced local
  artifacts. It is not semantic proof that every implemented benchmark bullet
  is fresh, sufficient, or benchmark-comparable; that remains part of the
  paper-index semantic evidence-mapping TODO.
- Database sampling reports are local strategy/count telemetry, not calibrated
  AlphaEvolve-style exploration/exploitation balance, fallback source-pool
  provenance, selected-program repetition tables, island/cell/metric/lineage/
  descriptor coverage, score-improvement versus diversity effects,
  equal-budget strategy comparisons, or an AlphaEvolve-grade database-balance
  policy; that boundary is tracked by `papers/sampling_balance_boundary.json`.
- Multi-objective archive data is retained overlay and diagnostic frontier
  evidence, not primary Pareto/frontier archive replacement or durable
  cross-run metric optimization; that boundary is tracked by
  `papers/objective_archive_boundary.json`.
- Metric-diverse prompt evidence is current-run prompt-visible telemetry, not
  benchmark-required metric-diverse prompt policy, cross-run fixtures, or
  scalar/single-metric equal-budget comparisons; that boundary is tracked by
  `papers/metric_diverse_prompt_boundary.json`.
- Built-in paper-inspired plugins are approximations, not faithful
  reproductions: `causal` is token-pattern outcome-factor guidance,
  `deep_research` is bounded arXiv/web-search context, `modular` is static
  ImprovEvolve-inspired prompt guidance, and `ttt_rl` exports clipped-reward
  JSONL examples without training. GigaEvo, CodeEvolve, and MadEvolve are
  currently paper/index inspiration or background context, not implemented
  framework parity.
- Custom plugin provenance is strongest for configured entry-point specs:
  entry-point plugins can record distribution metadata plus manifest-safe or
  declared-schema constructor options, while direct custom plugin instances
  record module/file/version identity and constructor signature shape only.
  Direct-instance constructor values, arbitrary instance attributes, versioned
  custom registries, and richer package provenance remain out of scope.
- Proposal scores and hypothesis indexes are bounded current-run records, not
  semantic idea-memory retrieval, calibrated proposal-quality models,
  cross-run proposal tables, or score-driven prompt/archive policy; that
  boundary is tracked by `papers/proposal_score_boundary.json`.
- Proposal-diversity reports are exact proposal/idea hashes and duplicate
  counts, not semantic novelty, near-duplicate detection, operator-family
  labels, code/semantic/task-output distance, parent/inspiration relation
  evidence, novelty scoring, prompt/backend attribution, accepted/rejected
  status linkage, or equal-budget/model-ablation evidence; that boundary is
  tracked by `papers/proposal_diversity_boundary.json`.
- Program-output resurfacing is exact current-run source-key/hash lookup over
  bounded output summaries, not durable output tables, schema-aware retrieval,
  semantic output similarity search, or replayable output-driven sampling;
  that boundary is tracked by `papers/program_output_boundary.json`.
- Figure 3 supervised-learning example support is generic embedded-evaluator,
  prompt-history, candidate-history, SEARCH/REPLACE, and preamble handling,
  not reproduced paper subfigure evidence with source/evaluate/prompt/output
  excerpt artifacts, subfigure/source locators, displayed score-value links,
  rendered hashes, or prompt/candidate/evaluator/run-artifact links; that
  boundary is tracked by
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
