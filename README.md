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
  report contract, scope-boundary records, and optional exhibit/artifact
  metadata, not executed equal-budget matrix/kissing benchmark runs, proven
  component-isolated ablation setups, rendered paper-quality curves, or
  accelerator/async-worker budget evidence.
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
