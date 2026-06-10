# README Todo: Incorrect or Unsupported Claims

This list tracks README statements that are inaccurate, misleading, or too
strong after comparing the current code, `papers/`, and AlphaEvolve sources.

## AlphaEvolve Comparison Table

## Research References and Bundled Papers

## Feature Claims

- [ ] Keep README multi-evaluator wording scoped until independent
      evaluator-oracle evidence exists.
  - Spec evidence: AlphaEvolve describes feedback from one or more evaluators,
    with Section 2.4 separating a user-provided evaluation function from
    optional cascades and LLM-generated feedback.
  - Current evidence: README now documents
    `runtime.history.evaluator_oracle_registry` with oracle ids/types,
    authority, input/output schema, metric ownership, failure policy, merge
    policy, prompt-feedback linkage, runtime counts, an `arbitration_policy`
    authority matrix, benchmark-sufficiency labels, conflict roles, failure
    effects, bounded local `disagreement_outcomes` for validator-versus-
    feedback cases, and `claim_ready: false` for independent multi-oracle
    arbitration.
  - Required result: when independent reference/statistical oracles,
    per-benchmark sufficiency evidence, and independent disagreement outcome
    records land, update README, ROADMAP, papers index, and code/paper TODOs
    together so README distinguishes local staged validation and feedback
    graders from AlphaEvolve-style feedback from one or more independent
    evaluators.

- [ ] Keep README grounding claims scoped until independent incorrect-
      suggestion audit evidence exists.
  - Spec evidence: AlphaEvolve states that code execution and automatic
    evaluation ground LLM-directed evolution and let the system avoid
    incorrect suggestions from the base LLM while using feedback to discover
    candidates substantially different from the initial pool.
  - Current evidence: README now describes
    `runtime.history.proposal_lifecycle_report`, a validated
    `libreevolve.proposal_lifecycle_report.v1` summary with proposal ids,
    backend/call summaries, mutation hashes, evaluator validity, archive
    admission or rejection, rejection reasons, execution-filtered counts,
    failure-memory linkage, and explicit false-acceptance/false-rejection
    review fields. It also keeps the claim scoped to local execution-
    grounding evidence rather than an independent benchmark rejudge.
  - Required result: when independent rejudge/reference-checker or statistical
    oracle evidence lands, update README, ROADMAP, papers index, and code/paper
    TODOs together with benchmark-specific evaluator-oracle sufficiency,
    cross-run proposal lifecycle tables, semantic failed-proposal retrieval,
    and audited false-acceptance/false-rejection rates.

- [ ] Keep README cascade claims scoped to partial promotion/attrition reports.
  - Spec evidence: AlphaEvolve Section 2.4 says evaluation cascades can use
    ensembles of test cases with increasing difficulty, promote candidates to
    the next stage only after sufficiently promising earlier-stage results,
    prune less promising solutions quickly, and run small-scale tests before
    main tests. The matrix-multiplication experiment also uses multiple random
    seeds with the Section 2.4 cascade.
  - Current evidence: README can now cite
    `runtime.history.evaluation_cascade_report`, a validated
    `libreevolve.evaluation_cascade_report.v1` runtime summary with stage
    candidate counts, pass/fail/threshold-fail counts, failure reasons,
    sample/retry/subprocess/timeout totals, elapsed seconds, promotion rates,
    main-test exposure, early-prune counts, and explicit `claim_ready: false`
    limitations. The README can also mention bounded candidate-stage
    `history.jsonl` cross-links and runtime denominator-policy boundaries.
    README should still not imply AlphaEvolve cascade-efficiency parity because
    stage difficulty/scale labels, evaluator/test-set hashes, benchmark
    seed/sample policy, and cost-savings counterfactuals remain incomplete.
  - Required result: update README, ROADMAP, papers index, and code/paper TODOs
    with the partial cascade report and the remaining difficulty, benchmark
    denominator, test-set, and cost gaps.

- [ ] Keep README backtracking wording scoped until explicit controller
      backtracking policies exist.
  - Spec evidence: AlphaEvolve's Introduction describes discovery as including
    ideation, exploration, backtracking on unpromising hypotheses,
    experimentation, and validation; Section 2.4 says cascades can prune less
    promising solutions quickly.
  - Current evidence: README now documents
    `runtime.history.hypothesis_branch_report`, which groups generated
    candidates by captured proposal idea/hypothesis/rationale hashes, includes
    rejected candidates, and marks rejected/no-accepted branches as
    `abandoned_evidence` with fallback-parent inference, failure-memory
    linkage, and claim-readiness limits. README also documents
    `runtime.history.controller_backtracking_report`, which records current-run
    branch state transitions and observed redirects to a later fallback parent
    or alternative branch without claiming causal controller proof.
  - Required result: when explicit controller-owned backtracking policy lands,
    update README, ROADMAP, papers index, and code/paper TODOs with configured
    suppression/retry behavior, selected fallback ancestor or alternative
    branch events, causal resumed-search outcome, and replayable validation.

- [ ] Keep README multiple-score prompt-context wording scoped until
      benchmark-required metric-diverse prompt policies exist.
  - Spec evidence: AlphaEvolve Section 2.4 says multiple metrics can improve a
    target metric by placing programs that excel under different evaluation
    criteria into prompts, each as a different definition of "good".
  - Current evidence: README documents declared metrics, direction/bounds
    normalization, selection scores, objective-vector diagnostics, metric
    overlays, metric-targeted parent/inspiration sampling, prompt context
    filters/ranking, generated-candidate
    `metadata.inspiration_selection.metric_diversity`, and
    `runtime.history.metric_diverse_inspiration_report`, whose
    `libreevolve.metric_diverse_prompt_benchmark_boundary.v1`
    `benchmark_policy` keeps AlphaEvolve Section 2.4 readiness false. It
    should still not imply those current-run evidence surfaces enforce
    benchmark-wide metric-diverse prompt conditioning or compare against scalar
    and one-at-a-time metric-targeted sampling.
  - Required result: when benchmark-required metric-diverse prompt policies and
    fixtures land, update README, ROADMAP, papers index, and code/paper TODOs
    together so README distinguishes current-run prompt-visible evidence from
    AlphaEvolve-style benchmark claims.

- [ ] Extend README evaluator-entrypoint wording from opt-in embedded evidence
      to full Figure 3 parity.
  - Spec evidence: AlphaEvolve Section 2.1 and Figure 3 show the codebase
    skeleton exposing `evaluate(eval_inputs) -> dict[str, float]`, which invokes
    the evolved blocks and returns scores for the generated program. Local PDF
    page 4 describes this as a Python `evaluate` function with a fixed
    input/output signature, and Figure 3 on page 6 says evaluators invoke the
    Figure 3(a) `evaluate` function to obtain the proposed program's scores.
  - Current evidence: README now describes both external validators and the
    opt-in configured stage mode `mode: embedded_evaluate`. In that mode
    LibreEvolve imports the materialized candidate primary file, requires a
    candidate-owned `evaluate(eval_inputs)` callable, invokes it with JSON-safe
    configured inputs, maps the returned dictionary through the local metrics
    contract, records candidate callable plus eval-input provenance, and points
    completed manifests at `runtime.history.embedded_evaluator_entrypoint_report`.
    README should still not imply full Figure 3 parity because the problem
    loader still requires `validate.py` by default and skeleton/block invocation
    coupling is not yet evidenced.
  - Required result: when skeleton/block invocation evidence, stronger callable
    isolation/build policy, and non-static/external-validator score-field
    linkage land, update README, ROADMAP, papers index, and code/paper TODOs
    together so README can make the stronger Figure 3 evaluator claim without
    overclaiming the current opt-in report.

- [ ] Extend README Figure 1/Figure 2 architecture wording from process
      mappings to full diagram parity.
  - Spec evidence: AlphaEvolve Figure 1 shows the high-level "Human defines
    What? / AlphaEvolve figures out How?" overview with LLM ensemble, prompt
    sampler, evaluator pool, and program database on local PDF page 3. Figure
    2 on page 4 expands the
    controller loop from database sampling through prompt construction, LLM
    generation, diff application, evaluator execution, and database admission.
  - Current evidence: README has its own Mermaid workflow and architecture
    sections describing seed programs, LLM mutation, cascade evaluation,
    MAP-Elites, island migration, and backend reward. Current implementation
    has evidence for a serial local loop through parent sampling, inspiration
    sampling, prompt building, LLM generation, workspace mutation, evaluator
    execution, admission, history logging, and terminal controller-state
    summaries, with artifacts such as `prompt_history.jsonl`,
    `llm_calls.jsonl`, evaluator metadata, `history.jsonl`,
    `archive_events.jsonl`, `controller_budget_events.jsonl`, and
    `manifest.json`. README now documents
    `runtime.history.alphaevolve_process_exhibit_report`, which records Figure
    1/Figure 2 exhibit IDs, node/edge-to-component mappings, implemented/
    divergent node status, Figure 2 pseudocode-step mappings, source
    PDF/caption locations, and links from displayed steps to prompt-history,
    LLM-call, evaluator, candidate-history, database, and controller-state
    artifacts.
  - Required result: when rendered diagram artifacts/hashes, exact diagram
    text or accessibility export, async controller topology, independent
    evaluator-pool parallelism, and artifact-level step validation land, update
    README, ROADMAP, papers index, and matching TODOs so README distinguishes
    local workflow explanation from full reproduced AlphaEvolve
    architecture/process exhibit evidence.

- [ ] Keep README evaluator-workload wording scoped until inner-search and
      ML-training execution contracts exist.
  - Spec evidence: AlphaEvolve Section 2.1 says an evaluator may perform a
    simple property check, run an evolved search algorithm, or train and
    evaluate a machine-learning model before returning scalar metrics.
  - Current evidence: README now documents `eval_stages[].workload` metadata,
    validator-visible `stage["workload"]`, validated dataset/budget/
    checkpoint/artifact/score-field declarations, and
    `runtime.history.evaluator_workload_report`. It also says the report is
    not a workload-specific runner and remains `claim_ready: false`. README can
    now cite dataset-digest completeness, score-field-to-returned-metric
    linkage, observed artifact evidence, protocol-readiness counts, and the
    managed-runner overclaim guard.
  - Required result: when executable workload-specific training/search
    contracts land, update README, ROADMAP, papers index, and code/paper TODOs
    together so README distinguishes declarative workload provenance from
    AlphaEvolve-style evaluators that actually train models or run substantial
    search loops with artifact and score linkage.

- [ ] Extend README evolve-block integration wording beyond runtime
      minimal-marker evidence.
  - Spec evidence: AlphaEvolve Section 2.1 says evolve-block markers enable
    integrating with existing codebases using only minimal changes by adding
    special comments around evolvable blocks. The local AlphaEvolve PDF page 4
    explicitly ties the marker API to existing-codebase integration, and Figure
    3 on page 6 shows marked code blocks plus `evaluate(eval_inputs) ->
    dict[str, float]` as the evaluator-facing entrypoint.
  - Current evidence: README documents Python evolve-block marker syntax,
    marker validation, fail-closed unsupported non-Python markers, workspace
    materialization, full-workspace export, and the `workspace_math` fixture's
    nested Python package plus JSON/static resource contract. It now also
    documents `runtime.history.existing_codebase_integration_report`, which
    records runtime candidate workspace marker spans, stable span ids, skeleton
    hashes, unmarked-file hashes, seed-source references, marker grammar, and
    explicit upstream-integration gaps. Static copy-only assets are verified by
    local `source_copy_path` hash/byte-count checks, but README wording should
    not treat that as portable codebase/release-artifact integration until
    source roots or artifact identities can replay across machines.
  - Required result: when upstream codebase identity, pre-marker hashes,
    marker-only setup diffs, evaluator-call paths before/after marker
    insertion, setup-change counts, and portable static-source identities land,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so README distinguishes runtime marker/workspace inventory from
    AlphaEvolve-style existing-codebase integration evidence.

- [ ] Keep README candidate-abstraction wording scoped beyond the current
      abstraction-choice report.
  - Spec evidence: AlphaEvolve Section 2.1 and Discussion say users can choose
    different candidate abstractions for the same problem, and those choices
    carry biases: constructor functions can favor highly symmetric solutions,
    while customized search algorithms may work better for non-symmetric
    solutions. In the local PDF, page 5 describes flexibility in abstraction
    choice, and page 21 reiterates that direct search, constructor functions,
    and evolved search algorithms suit different problems because of different
    biases.
  - Current evidence: README says LibreEvolve currently uses a deliberate
    code-file-set abstraction with a primary text file and lacks first-class
    non-code serializers or paired solution/search APIs. The underlying
    manifest policy records this as `python_primary_text_workspace_v1` with
    `problem_defined_solution_abstractions: unsupported` and
    `language_runner_ready: False`. README now also documents
    `runtime.history.candidate_abstraction_choice_report`, which records the
    selected code-file-set abstraction, policy linkage, unsupported
    constructor/search/paired alternatives, and missing bias/equal-budget
    evidence.
  - Required result: when benchmark rationale, problem-structure labels, typed
    candidate-abstraction hooks, paired solution/search APIs, or equal-budget
    abstraction-comparison reports land, update README, ROADMAP, papers index,
    and code/paper TODOs so README distinguishes the current partial report
    from AlphaEvolve-style abstraction-selection evidence.

- [ ] Keep README seed-provenance wording scoped beyond current idea metadata.
  - Spec evidence: AlphaEvolve Section 2.1 makes the initial solution and
    optional background knowledge part of the task specification, and Section
    3.1 reports matrix targets where researchers seeded the initial program
    with their own ideas, such as stochastic evaluation or evolutionary
    approaches. In the local PDF, page 10 says most Table 2 matrix results used
    a simple initial program, while some parameters improved from
    researcher-idea-seeded starts.
  - Current evidence: README documents seed source safety and provenance,
    including `seed_source_path`, `seed_source_kind`, `seed_index`,
    `problem.seed_sources`, skipped-seed diagnostics, inline seed labels, and
    generation-0 baselines. README now also documents optional seed idea
    metadata fields and
    `runtime.history.initial_program_idea_provenance_report`, which links seed
    variant ids, idea origins, contribution roles, prior-technique labels, and
    background refs to generation-0 history rows and declared metric names.
  - Required result: when seed-variant result tables, prompt/context linkage,
    equal-budget simple/random/researcher-idea comparisons, and contribution
    review/signoff land, update README, ROADMAP, papers index, and code/paper
    TODO entries together so README does not imply metadata alone is
    sufficient for AlphaEvolve-style human-seeded collaboration claims.

- [ ] Keep README seed-validity wording scoped after strict policy/reporting.
  - Spec evidence: AlphaEvolve Section 2.1 describes the initial implementation
    as complete but rudimentary, with the task skeleton and evaluator able to
    invoke it before evolution. Local PDF page 5 says user-provided code inside
    evolution blocks serves as the initial solution.
  - Current evidence: README documents valid/suboptimal seeds and deliberately
    invalid optimization-pressure seeds, including `hello_world`, and states
    that runs can record invalid seed baselines. Code evidence shows the seed
    loop evaluates seeds, logs rejected seeds through `log_seed_failure()`, and
    can finish a seed-only run with all seeds invalid as `no_valid_programs`.
    README now also documents `initial_program_validity_policy:
    alphaevolve_strict`, `runtime.stop_reason: invalid_initial_programs`, and
    `runtime.history.initial_program_validity_report` for runs that require
    every selected seed to be evaluator-valid and metric-complete before
    mutation.
  - Required result: when benchmark fixtures opt into strict mode and publish
    fixture-level complete-start evidence, update README, ROADMAP, papers
    index, and code/paper TODOs together so README distinguishes the available
    strict policy/report from benchmark claims that require complete
    AlphaEvolve-style initial implementations.

- [ ] Keep README problem-formulation wording scoped until benchmark fixtures
      carry expert-reviewed metadata.
  - Spec evidence: AlphaEvolve Section 3.2 reports that many mathematical
    problems were suggested by external mathematicians who advised on how to
    formulate them as AlphaEvolve inputs, while Section 2.1 treats task
    definition and optional background knowledge as human-provided setup.
    Figure 1 further frames the setup boundary as humans defining the "what"
    by setting evaluation criteria, providing the initial solution, and adding
    optional background knowledge.
  - Current evidence: README documents problem/source provenance, context file
    selection, local paper context, seed source identity, optional
    `formulation.yaml` / `Problem.formulation_metadata`, normalized
    `problem.formulation_metadata`, and
    `runtime.history.problem_formulation_provenance_report`. It distinguishes
    context-source artifact tracking from expert formulation evidence and says
    claim readiness requires expert roles, rationale, parameter-scope,
    background refs, and review/signoff. Existing benchmark fixtures do not yet
    carry real expert-reviewed formulation records.
  - Required result: when matrix and constructive-math benchmark fixtures are
    populated with reviewed formulation metadata and paper-facing evidence,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so README can describe the benchmark claim without implying the schema
    alone proves AlphaEvolve-style human expert problem formulation.

- [ ] Keep README robustness and versatility wording scoped until populated
      collaborator-feedback evidence exists.
  - Spec evidence: AlphaEvolve's Acknowledgements say early users and
    collaborators supplied diverse use cases and insightful feedback that
    shaped the system into a more robust and versatile tool. This external
    use-case feedback is distinct from candidate-evaluation feedback,
    prompt-visible evaluator feedback, and configured LLM feedback graders.
  - Current evidence: README can describe implemented surfaces, local examples,
    paper/status rows, expert formulation gaps, domain-owner review gaps,
    optional `collaborator_feedback.yaml` /
    `Problem.collaborator_feedback_metadata`, normalized
    `problem.collaborator_feedback_metadata`, and
    `runtime.history.collaborator_feedback_provenance_report`. It now
    distinguishes external early-user/collaborator feedback from in-run
    `evaluation.metadata.llm_feedback`, `llm_feedback:<name>` stages, feedback
    retention, feedback indexes, and feedback-sourced metrics. Existing
    fixtures do not yet carry real multi-cohort feedback records with
    change-link and validation evidence.
  - Required result: when representative fixtures are populated with reviewed
    collaborator-feedback metadata and paper-facing evidence, update README,
    ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes local feature breadth and smoke examples from
    AlphaEvolve-style robustness or versatility claims backed by diverse
    collaborator feedback.

- [ ] Keep README workspace-topology diagnostics scoped to current
  materialization and command preflight coverage.
  - Spec evidence: AlphaEvolve-style codebase evolution should leave stable,
    inspectable evaluator feedback for generated invalid artifacts, especially
    as task-defined program artifacts and workspace surfaces grow beyond the
    current local file-set prototype. The AlphaEvolve PDF describes
    multi-component codebase evolution, larger-codebase diff-block sequences,
    and entire-codebase evolution, so README wording needs to separate current
    local file-workspace support from broader codebase parity.
  - Current evidence: README documents that collision checks are still
    incomplete while also describing rejected normalized path collisions,
    case-folded host-path materialization preflights, structured
    `materialization_error` evaluation results, bounded redacted diagnostics,
    structured materialization `reason` and `paths`, exact snapshot
    materialization, link/junction rejection, static source-copy verification,
    and workspace topology command prevalidation for duplicate sources/targets,
    edit/delete/move conflicts, chained operations, host/case-folded target
    collisions, duplicate `PRIMARY` commands, and non-empty command bodies. It
    also documents prompt controls for selecting and capping
    materialization-error fields. These are current local-workspace
    diagnostics, not proof of arbitrary-language, build-runner,
    dependency-graph, or remote/container workspace parity.
  - Required result: when future topology surfaces such as bulk directory
    operations, language/build-runner generated artifacts, external
    materialization paths, or richer artifact runners land, update README,
    ROADMAP, papers index, and code/paper TODO entries together so README
    neither underclaims current structured invalid-workspace feedback nor
    overclaims robust AlphaEvolve-grade codebase-scale diagnostics.

- [ ] Keep README code-scale claims scoped to current workspace support versus
      Table 1 parity.
  - Spec evidence: AlphaEvolve Table 1 claims evolution of entire code files,
    hundreds of lines of code, any language, and complex algorithms spanning
    multiple functions and components. The local PDF places those code-scale
    comparison rows on page 2 and later discusses entire-codebase evolution on
    pages 18-19.
  - Current evidence: README can accurately describe Python-primary seed
    workspaces, multi-file candidates, topology mutations, materialization
    diagnostics, and `best_workspace/` export. It should not imply those
    mechanics prove AlphaEvolve-scale large-codebase behavior. Current
    machine-readable example scope records mark `workspace_math` as a smoke
    `workspace_packaging_fixture` and not AlphaEvolve-comparable.
  - Required result: when a codebase-scale benchmark/report lands, update
    README, ROADMAP, papers index, and code/paper TODO entries with the
    generated-line/component counts, cross-file dependency edit evidence,
    evaluator budget, quality-progress results, and language/build-runner
    scope that justify any AlphaEvolve Table 1 code-scale comparison.

- [ ] Keep README Table 1 wording scoped until capability-table exhibit
      provenance exists.
  - Spec evidence: AlphaEvolve Table 1 is a row-by-row FunSearch versus
    AlphaEvolve comparison covering code scale, language scope, evaluator
    duration/parallelism/accelerators, sample counts, model scale, prompt
    context/feedback, and single versus multiple metrics. Local PDF page 2
    contains the eight comparison rows and caption.
  - Current evidence: README has a high-level gap table and detailed sections
    for several Table 1-related capabilities, but it does not document a
    Table 1 exhibit record with stable row ids, exact comparison text for both
    FunSearch and AlphaEvolve cells, source PDF/caption location, row-to-gap
    mappings, rendered artifact hashes, or row-level implementation status.
    README's current comparison table should therefore remain an explanatory
    status summary, not a validated reproduction of Table 1.
  - Required result: when Table 1 exhibit provenance lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README can
    distinguish the reproduced capability-comparison table from the separate
    work needed to satisfy each Table 1 capability row.

- [ ] Extend README Figure 1 and Figure 2 process-diagram wording beyond the
      current process-overview exhibit map.
  - Spec evidence: AlphaEvolve Figure 1 defines the high-level process among
    human task inputs, the LLM ensemble, prompt sampler, evaluator pool,
    program database, rich context, proposals, and quality feedback. Figure 2
    defines the expanded discovery-process diagram and controller pseudocode
    for sampling parents/inspirations, building prompts, generating and
    applying diffs, executing evaluators, and adding results to the database.
    Local PDF page 3 carries Figure 1; page 4 carries Figure 2 and the
    expanded-process caption.
  - Current evidence: README describes LibreEvolve's loop, ensemble,
    evaluator, database, and diff mechanics, and related TODOs track many of
    those behaviors separately. It now documents
    `runtime.history.alphaevolve_process_exhibit_report`, which records Figure
    1/2 exhibit IDs, diagram-node/edge labels, source page/caption locations,
    Figure 2 pseudocode-step mappings, artifact cross-links, and
    `claim_ready: false` process-parity gaps. README workflow text should
    still remain local documentation, not a validated reproduction of the
    paper process diagrams.
  - Required result: when exact diagram/pseudocode text, rendered artifact
    hashes, component-to-code/TODO evidence links, and artifact-level step
    validation land, update README, ROADMAP, papers index, and code/paper TODOs
    together so README can explain which process-diagram steps LibreEvolve
    implements, which are partial or missing, and why process-diagram
    reproduction is separate from satisfying each underlying workflow
    capability.

- [ ] Extend README task-specification wording beyond field-level artifact
      resolution.
  - Spec evidence: AlphaEvolve Section 2.1 and Figure 2 define a task
    specification as the user-provided initial program/components, evaluation
    code, prompt template and configuration, choice of existing or custom
    LLMs, and optional background knowledge. Local PDF page 4 labels those
    Figure 2 inputs and says the user provides the initial program, evaluation
    code, and optional configurations before AlphaEvolve starts the loop.
  - Current evidence: README can now cite `manifest.json.task_specification`,
    a validated `libreevolve.alphaevolve_task_specification_bundle.v1` record
    that cross-links initial programs, evaluator code or embedded evaluator
    stages, prompt template/config metadata, backend choices, optional
    background context, candidate representation, and objective metrics to
    their manifest paths. It records field statuses, ids/hashes/counts, a
    deterministic `task_spec_id`, and unsupported/incomplete gaps. README also
    cites `runtime.history.task_spec_artifact_resolution_report`, which
    validates task-spec manifest paths and cross-links each field to runtime
    artifact paths for candidate history, prompt history, LLM calls,
    controller-budget events, evaluator artifacts, best exports, initial
    evolvable component spans when markers are present, embedded score-field
    candidate-path links with static AST causal attribution when supported
    candidate-owned evaluation ran, and the hashed
    standalone `task_specification.json` run artifact. It also documents
    bounded candidate, prompt, and evaluator JSONL row joins plus the checked
    `docs/examples/task_specification.embedded_evaluate_math.json` example.
    README should still not imply full AlphaEvolve task-spec parity because
    external validators, arbitrary language/build runner specs, and full
    user-authored task-spec evidence remain incomplete.
  - Required result: when those non-embedded task-spec parity gaps land, update
    README, ROADMAP, papers index, and code/paper TODOs together.

- [ ] Keep README install and CLI wording scoped to editable/local use versus
  release-artifact verification.
  - Spec evidence: AlphaEvolve-style experimental artifacts should be
    reproducible from the code and dependency environment that users actually
    install before running long experiments; local editable setup is not the
    same as a checked release distribution.
  - Current evidence: README currently instructs developers to run
    `py -3.12 -m pip install -e ".[dev]"`, invokes the CLI through
    `py -3.12 -m libreevolve ...`, documents the `libreevolve run` and
    `libreevolve show` command shapes, and documents runtime environment
    provenance over `pyproject.toml`, installed package metadata, bounded
    `WHEEL` metadata, `direct_url.json`, `INSTALLER`, hash-only `RECORD`,
    `pip freeze`, and `pip config`. Code evidence shows `pyproject.toml`
    declares setuptools metadata, runtime dependencies, dev extras, package
    discovery, and a `libreevolve` console script, while the code TODO still
    notes there is no committed wheel/sdist build check, install-from-wheel CLI
    smoke test, package-data inclusion validation, release checklist, or
    release-artifact provenance.
  - Required result: when wheel/sdist build validation, isolated
    install-from-wheel smoke tests, package-data checks, release checklists, or
    release-artifact provenance land, update README, ROADMAP, papers index, and
    code TODO entries together so README neither underclaims current
    editable/local CLI use nor overclaims verified release-distribution
    reproducibility.

- [ ] Keep README `show` and run-inspection wording scoped to selected-row
  display plus streamed-row validation.
  - Spec evidence: AlphaEvolve-scale runs need auditable generated-program
    databases and whole-run source/workspace integrity reports, not only a
    compact best-candidate view.
  - Current evidence: README documents `show` as a compact history view that
    selects the best archive-retained valid record, prints selected-row
    metrics, archive diagnostics, bounded run-inspection summaries, and
    selected-row workspace files, and validates streamed current and legacy
    history rows before printing. It also states that malformed unselected,
    invalid, or non-admitted rows fail inspection before any best-looking row
    is printed, with source/workspace paths, `files`, and `primary_file`
    checked under the runtime candidate path grammar. The paper TODO still
    requires whole-run source/workspace integrity summaries and durable
    query/report surfaces over every candidate's source payloads, workspace
    paths, source hashes, primary-file coherence, and display/truncation
    policy.
  - Required result: when whole-run source/workspace integrity reports, durable
    run-artifact query views, richer archive/prompt/failure drill-downs, or
    every-candidate source-hash summaries land, update README, ROADMAP, papers
    index, and code/paper TODO entries together so README neither underclaims
    current streamed-row validation nor overclaims AlphaEvolve-grade run
    inspection.

- [ ] Keep README provider-token prompt-packing wording scoped to implemented
  mutation and final-prompt boundaries.
  - Spec evidence: AlphaEvolve-scale prompt construction needs prompt sections
    and context surfaces to fit model-specific context windows without
    silently dropping important evaluator, parent, inspiration, or retrieval
    evidence.
  - Current evidence: README now distinguishes implemented backend
    context-window heuristic capacity, automatic mutation-path local OpenAI
    tokenizer discovery, and role-scoped final-prompt exact token counting
    from the still-open provider-token section-priority packing outside
    mutation prompts and exact counters across non-OpenAI provider families.
    Code evidence includes `core.loop.discover_prompt_token_counter(...)`
    before `PromptSampler` construction, `LLMEnsemble._prompt_token_counter_for_role(...)`
    before final prompt validation, and tests covering mutation diagnostics and
    critique-role final-prompt counter telemetry.
  - Required result: when selected-backend provider-token section packing
    covers critique, feedback, meta-prompt, registry-created, custom, and
    retrieval/context/plugin/failure-memory sections across provider families,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so README neither underclaims automatic OpenAI counter discovery nor
    overclaims full AlphaEvolve-grade context-window fitting.

- [ ] Keep README explicit-context wording scoped until context-source roles
      exist.
  - Spec evidence: AlphaEvolve Section 2.2 says explicit context can include
    fixed human-written instructions, equations, code snippets, and relevant
    literature such as PDF files.
  - Current evidence: README can describe local context manifests, source
    hashes, extraction spans, PDF rendering, deterministic ordering/filtering,
    truncation, and prompt diagnostics. It does not yet document typed
    source-role metadata proving that a selected context source is intended as
    an instruction, equation, code snippet, literature/PDF source, or other
    AlphaEvolve-style explicit problem context.
  - Required result: when context-source role metadata lands, update README,
    ROADMAP, papers index, and code/paper TODO entries together so README
    separates generic local file ingestion and retrieval/plugin context from
    paper-facing explicit problem-context evidence.

- [ ] Keep README ablation-report wording aligned with current LLM budget
  stops.
  - Spec evidence: AlphaEvolve Figure 8 compares executed equal-budget
    ablation curves; report-schema validation alone is not executed
    budget-controlled experimentation, but README text should not deny budget
    stops that now exist.
  - Current evidence: README now says
    `libreevolve.alphaevolve_ablation_report.v1` validates report shape only
    and does not run ablation experiments or add accelerator/async-worker
    budget stops beyond the current live provider-token and configured-cost LLM
    budget surfaces. Code evidence includes `RunBudget.max_llm_tokens`,
    `RunBudget.max_llm_cost_microusd`, role-scoped token/cost limits, and
    controller-budget event replay into restored budget snapshots. The
    checked-in Figure 8 registry is still `definition_only` and should keep
    the full-system baseline distinct from the five component-disabled
    ablations; several
    `required_config_assertions` are intended component labels rather than
    current executable config switches, including `candidate_source`,
    `archive_admission_enabled`, `prompt_context_sections`,
    `candidate_workspace_mode`, `file_create_delete_enabled`,
    `ensemble_strategy: single_backend`, and `backend_capability_tier`. The
    registry now records a validated `No evolution` `paper_scope_boundary`
    marking current zero-generation/seed-only labels as
    `prompt_history_unproven`, but it still does not prove that every prompt is
    built from the same initial program without database-selected parents,
    inspirations, previous-candidate feedback, or archive admission feedback.
    It also does not yet prove a paper-faithful
    `No context in the prompt` setup: the registry now records a validated
    `paper_scope_boundary` marking the current parent/inspiration/failure/
    plugin section-disable scope as `over_broad_not_equivalent` to
    AlphaEvolve's explicit problem-specific context removal. README wording
    should still require executed prompt-history proof that explicit context
    sources were absent, while separately reporting which current-program,
    parent/inspiration, rendered-result, failure, plugin, or retrieval sections
    were treated as core evolutionary prompt ingredients versus explicit
    context. It also does not yet prove the
    `Small base LLM only` setup: the registry now records a validated
    `paper_scope_boundary` marking the current single-backend/small-base
    labels as `telemetry_unproven`, but there is still no proof that every
    mutation-generation call uses only one configured small/base-capable model
    and has no large-model eligibility, fallback, critique, or router leakage.
    It also does not yet prove the
    `No meta prompt evolution` setup: the registry now records a validated
    `paper_scope_boundary` marking current meta-prompt-disabled labels as
    `lineage_unproven`, but there is still no proof that meta-prompt calls,
    prompt-template mutations, and prompt-program lineage updates are absent in
    the ablated run but enabled in the full-system comparator. The
    `No full-file evolution` registry row also records a validated
    non-equivalence boundary for the paper-specific tensor-decomposition
    loss-function-only setup; generic single-file/diff/no-topology labels still
    should not be described as executable evidence for that ablation.
    The report contract now validates Figure 8 target-family coverage for
    matrix tensor-decomposition and kissing-number sphere-packing targets,
    target-metric identity/direction/normalization, and per-target
    mean/standard-deviation curve summaries over three independent seeds.
  - Required result: when benchmark scripts emit executed equal-budget
    ablation reports, when component assertions are bound to supported runtime
    config controls, or when accelerator/async-worker budgets land, update
    README, ROADMAP, papers index, and code/paper TODO entries together so the
    README neither underclaims current token/configured-cost budget stops nor
    overclaims AlphaEvolve-style executed ablations. For `No full-file
    evolution`, keep README wording tied to the validated non-equivalence
    boundary until a real loss-function-only tensor-decomposition harness
    exists. Keep README wording tied to the `No evolution`
    prompt-history-unproven boundary until executed evidence proves that the
    same initial program was repeatedly prompted without evolutionary database
    feedback. Keep README wording tied to the
    `No context in the prompt` validated over-broad non-equivalence boundary
    until executed prompt-history evidence proves absent explicit context
    sources and separately identifies which normal evolutionary prompt sections
    remained present. Keep README wording tied to the `Small base LLM only`
    telemetry-unproven boundary until executed backend telemetry proves a
    single small/base model actually handled every relevant generation call.
    Keep README wording tied to the `No meta prompt evolution`
    lineage-unproven boundary until executed prompt-history, call-ledger, and
    prompt-program lineage evidence proves meta-prompt and prompt-mutation
    surfaces were disabled only for that ablation, with a frozen human-authored
    prompt identity/source/revision/context policy recorded for the
    human-prompter comparator. Require README wording to distinguish validated
    ablation-result schemas from executed Figure 8-equivalent matrix/kissing
    target-family runs and rendered curve exhibits.

- [ ] Keep README Figure 8 visual wording scoped until rendered ablation-curve
      exhibits exist.
  - Spec evidence: AlphaEvolve Figure 8 is a two-panel ablation plot with
    matrix tensor-decomposition curves on the left, kissing-number curves on
    the right, compute-budget fraction on the x-axis, aggregated target metric
    on the y-axis, named method curves, and shaded standard-deviation bands
    from three independent seeded runs.
  - Current evidence: README describes the ablation report contract, hashed
    curve artifacts, target-family/mean/std validation, and the Figure 8
    visual-exhibit contract. The exhibit contract validates Figure 8 exhibit
    IDs, panel definitions, series-to-variant legend mappings, exact paper
    legend labels such as `Full method`, axis/scale metadata,
    color/style/shading parameters, rendered plot artifact hashes, and links
    from plotted visuals to report/curve/raw-trace artifacts. The
    `figure8_exhibit_from_ablation_report()` builder now derives that two-panel
    exhibit from a validated equal-budget report plus declared rendered/source
    artifacts, while still leaving actual plot emission and real run proof open.
  - Required result: when generated Figure 8 exhibit records and rendered
    artifacts land, update README, ROADMAP, papers index, and matching TODOs so
    README distinguishes validated exhibit metadata from reproduced
    paper-quality Figure 8 visual evidence tied to real ablation runs.

- [ ] Keep README matrix-publication wording scoped to one checked Strassen
  baseline versus full Appendix A discovery.
  - Spec evidence: AlphaEvolve Appendix A reports a matrix-multiplication
    target suite with discovered algorithms, exact constructions, and
    accompanying export/notebook artifacts; a single checked baseline bundle is
    not evidence that LibreEvolve discovered or exported the full suite.
  - Current evidence: README now says
    `write_strassen_2x2_publication_bundle()` emits a concrete checked
    Strassen bundle for registered `mm_2x2x2` with canonical algorithm,
    certificate, notebook, report, and artifact-inventory files, while also
    stating that this is a reproducible baseline artifact and not evidence that
    LibreEvolve discovered or exported the full Appendix A target suite. The
    54-target Appendix A registry is rank/outcome metadata, not stored target
    tensors, discovered decompositions, coefficient lists, per-target
    certificates, notebook exports, or construction provenance.
    README now also documents `libreevolve.matrix_suite_publication_artifact_boundary.v1`
    as the current `not_generated_locally` boundary and required future fields
    for one generated artifact record per registered Appendix A target.
    `matrix_suite_publication_artifact_boundary_from_artifacts()` can build the
    generated boundary and validation checks nested matrix-result report
    linkage, while README still marks full-suite generation missing.
    Matching paper TODO and paper-index entries now make the same distinction.
  - Required result: when real tensor-decomposition benchmark runs emit
    target tensors, discovered algorithms, coefficient data, certificates,
    notebooks, or publication bundles across Appendix A targets, update
    README, ROADMAP, papers index, and code/paper TODO entries together so
    README neither underclaims the checked Strassen baseline nor overclaims
    AlphaEvolve-comparable discovery coverage.

- [ ] Keep README Appendix A best-known-rank wording scoped until baseline
      citation provenance exists.
  - Spec evidence: AlphaEvolve Table 2 reports matrix targets using a
    `best known [reference]` baseline-rank column, and Appendix A Table 3
    extends the best-known-rank comparison table.
  - Current evidence: README describes the Appendix A registry as target,
    dimension, rank, and outcome metadata for validating matrix result reports.
    It does not document a per-target prior-work citation/source record for
    each best-known rank, reference id, paper/source location, applicability
    caveat, source digest, or report-visible baseline-source field.
    `libreevolve.alphaevolve_appendix_a_matrix_baseline_citation_boundary.v1`
    now documents and validates that README-scoped absence boundary plus
    recorded per-target citation fields. README also documents the builder for
    supplied citation rows and registry/source-ref linkage, but not a real
    emitted citation corpus.
  - Required result: when Appendix A best-known-rank citation provenance lands,
    update README, ROADMAP, papers index, and code/paper TODOs together so
    README distinguishes stored best-known rank values from traceable cited
    baseline evidence.

- [ ] Keep README matrix per-seed wording scoped until cascade-run provenance
      exists.
  - Spec evidence: AlphaEvolve Section 3.1 says matrix experiments run over
    multiple random seeds using the evaluation cascade, then report the best
    rank and the fraction of seeds that reached it.
  - Current evidence: README documents the matrix report contract's declared
    per-seed rows, best-rank consistency checks, and hit-fraction validation,
    plus generic cascade support elsewhere. It now also documents
    `libreevolve.matrix_cascade_run_runtime_boundary.v1`, which validates the
    current `not_emitted_by_local_runner` boundary and emitted repeated-seed
    matrix cascade traces. README also documents
    `matrix_cascade_run_runtime_boundary_from_matrix_result()` for building
    emitted records from seed rows plus per-seed stage traces, including
    aggregate best-rank/hit-fraction recomputation. It does not document an
    executed matrix benchmark runner that automatically emits target/seed-level
    cascade traces or pruning/early-stop reasons.
  - Required result: when matrix cascade-run evidence lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes post-hoc per-seed report validation from AlphaEvolve
    Section 3.1-style repeated-seed cascade execution evidence.

- [ ] Keep README Table 2/Table 3 matrix-rank table wording scoped until
      emitted table exhibit artifacts exist.
  - Spec evidence: AlphaEvolve Table 2 is the selected main-text matrix-rank
    comparison table, and Appendix A Table 3 is the full 54-target version with
    caption-level aggregate counts, outcome coloring, complex-valued row
    caveats, companion Colab links, and the concurrent-work note for
    `<4, 5, 6>`.
  - Current evidence: README now documents
    `libreevolve.alphaevolve_matrix_rank_table_exhibit.v1`, which validates
    Table 2/Table 3 exhibit ids, selected-row versus full-table relation, row
    ordering, caption aggregate validation, color/outcome encoding,
    source/caption locations, rendered table artifacts/hashes, and links from
    table rows to registry/report/Colab evidence. No emitted report/table
    artifact carries those rendered/source/OCR files yet.
    `libreevolve.alphaevolve_matrix_rank_table_artifact_boundary.v1` now
    documents and validates that README-scoped absence boundary plus required
    future emitted-artifact fields.
    `matrix_rank_table_artifact_boundary_from_exhibit()` builds emitted table
    artifacts from validated Table 2/Table 3 exhibit metadata and validation
    checks nested table linkage, while README still keeps local report/export
    emission marked missing.
  - Required result: when Table 2/Table 3 matrix-rank table exhibit artifacts
    land, update README, ROADMAP, papers index, and code/paper TODOs together
    so README distinguishes reproduced paper-table exhibits from general
    Appendix A registry and matrix report-contract coverage.

- [ ] Keep README matrix outcome wording scoped until emitted target-subset
      artifacts exist.
  - Spec evidence: AlphaEvolve Table 2 says all parameters `m, n, p <= 5`
    matched or surpassed best-known ranks, while Appendix A Table 3 is a
    broader 54-target table that includes targets outside that subset.
  - Current evidence: README now documents
    `libreevolve.alphaevolve_matrix_subset_scope.v1`, which validates named
    target subsets for `appendix_a_full`, `main_text_mnp_le_5`, and
    `table_2_selected`, including inclusion predicates, row counts, outcome
    counts, out-of-scope row ids, and source-caption/table linkage. README can
    distinguish the full 54-target Appendix A table from the narrower
    all-matched-or-surpassed `m,n,p <= 5` main-text claim, but no emitted
    report/table artifact carries that subset-scope evidence yet.
    `libreevolve.alphaevolve_matrix_subset_scope_artifact_boundary.v1` now
    documents and validates that README-scoped absence boundary plus
    emitted-artifact fields. README also documents the builder from subset
    evidence and nested-linkage validation, but no report/table exporter emits
    the records automatically.
  - Required result: when matrix subset-scope artifacts land, update README,
    ROADMAP, papers index, and code/paper TODOs with named target subsets,
    inclusion predicates, row counts, outcome counts, out-of-scope row ids,
    source-caption/table linkage, and wording checks that separate Table 2's
    scoped main-text claim from Appendix A full-table aggregates.

- [ ] Keep README matrix headline wording scoped until emitted 4x4 rank-48
      historicity artifacts exist.
  - Spec evidence: AlphaEvolve's abstract and Section 3.1 headline the 4x4
    complex matrix result as a rank-48 procedure using 48 scalar
    multiplications and the first characteristic-zero rank-below-49
    improvement after 56 years, while Section 3.1 separately notes recursive
    Strassen rank 49 over any field and Fawzi et al. rank 47 over the field
    with two elements.
  - Current evidence: README now documents
    `libreevolve.matrix_headline_historicity_evidence.v1`, which validates a
    declared source-backed headline record for target id, dimensions,
    field/characteristic, rank, 56-year first-below-49 flags, Strassen/Fawzi
    prior comparisons, source refs, and links to result, scalar-field,
    tensor-rank, Figure 4, Figure 9, and companion Colab evidence. README now
    also documents `libreevolve.matrix_headline_historicity_runtime_boundary.v1`
    as the current `not_emitted_by_local_runner` boundary plus emitted-record
    validation for run/target/candidate ids, dimensions, headline
    rank/field values, source refs, prior comparisons, evidence links,
    matrix-result refs, artifact paths, and artifact hashes. It also documents
    the builder that turns validated headline evidence into a linked runtime
    row. That contract distinguishes the complex/characteristic-zero headline
    from the finite-field caveat, but it does not prove the claim until
    concrete emitted artifacts and source-span/decomposition/certificate links
    exist.
  - Required result: when matrix-headline historicity artifacts land, update
    README, ROADMAP, papers index, and code/paper TODOs with target id,
    dimensions, field/characteristic, rank, prior-algorithm comparison,
    bibliography references, source page/spans, certificate/Colab links, and
    wording checks so README does not overclaim a first-improvement result
    from rank-row metadata alone.

- [ ] Keep README Appendix A row-note wording scoped until emitted
      concurrent-work caveat artifacts exist.
  - Spec evidence: AlphaEvolve Appendix A Table 3 includes row-level notes,
    including concurrent work [49] also finding a rank-90 algorithm for
    `<4, 5, 6>`.
  - Current evidence: README now documents
    `libreevolve.alphaevolve_appendix_a_matrix_row_notes.v1`, which validates
    row-level notes, concurrent-work attribution, independently matched result
    flags, and caveats for rows such as `mm_4x5x6`. It records that reference
    `[49]` also found a rank-90 algorithm for `<4, 5, 6>`, independently
    matching AlphaEvolve's rank. No emitted report/table artifact carries that
    row-note caveat yet.
    `libreevolve.alphaevolve_appendix_a_matrix_row_note_artifact_boundary.v1`
    now documents and validates that README-scoped absence boundary plus
    emitted-artifact fields. README also documents the builder from row-note
    evidence and nested-linkage validation, but no report/table exporter emits
    the caveat automatically.
  - Required result: when Appendix A row-note artifacts land, update README,
    ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes stored rank/outcome values from paper-faithful result-note
    evidence and does not overstate exclusive SOTA priority where the paper
    records concurrent matching work.

- [ ] Keep README Appendix A target-suite wording scoped to registry coverage
      versus curation provenance.
  - Spec evidence: AlphaEvolve Appendix A says the 54 reported matrix sizes
    were chosen roughly from dimensions with 2 <= m,n <= 5 and a cutoff for p,
    and that axis-permutation symmetries make equivalent algorithms, so the
    paper focuses on sorted sizes.
  - Current evidence: README says the matrix report checks `target_id` and
    `dimensions` against the 54-row Appendix A Table 3 registry and now
    documents `libreevolve.alphaevolve_appendix_a_matrix_curation.v1` for
    rough selection wording, sorted representative policy, omitted
    symmetry-equivalent target ids, included-target rationales, and the
    unspecified `p` cutoff. README now also documents
    `libreevolve.alphaevolve_appendix_a_matrix_excluded_target_curation_boundary.v1`
    as the current `not_recorded_locally` boundary and required future
    excluded-target justification fields.
    `appendix_a_matrix_excluded_target_curation_boundary_from_records()` can
    build a recorded boundary for supplied excluded-target justifications over
    a declared scope. README still does not document emitted justifications for
    every possible excluded non-equivalent target outside the reported suite.
  - Required result: when excluded-target justification metadata lands, update
    README, ROADMAP, papers index, and matching TODOs so README does not imply
    the curation record proves full exhaustive target-suite construction.

- [ ] Keep README matrix-scaling wording scoped until resource-frontier
      reports exist.
  - Spec evidence: AlphaEvolve Appendix A notes that runs on matrix sizes
    beyond the reported suite often ran out of memory with 1000 random seeds
    on a single GPU accelerator, and that larger-size extension needs further
    optimization.
  - Current evidence: README documents matrix report contracts, Appendix A
    registry checks, one checked Strassen baseline bundle, generic runtime
    budget surfaces, unsupported resource quotas, and
    `libreevolve.alphaevolve_appendix_a_matrix_resource_frontier.v1`. The
    resource-frontier contract documents the paper-only boundary for sizes
    beyond `<5,5,5>`, 1000 random seeds, single-GPU evaluators, frequent OOM,
    and further-optimization need.
    `libreevolve.alphaevolve_appendix_a_matrix_local_resource_frontier.v1` now
    documents the local absence/readiness boundary and required fields for
    measured accelerator-memory profiles, OOM/resource-exhaustion artifacts,
    reduced-seed tradeoffs, and target-exclusion rationale for sizes beyond
    the reported suite.
    `appendix_a_matrix_local_resource_frontier_from_attempts()` can build an
    `attempts_recorded` boundary from supplied local attempt diagnostics, but
    README still marks real larger-target attempts and artifacts missing.
  - Required result: when local matrix resource-frontier reports land, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes paper-source OOM boundary evidence from local larger-target
    scaling evidence.

- [ ] Keep README matrix wording scoped to result contracts until
      near-integrality prompt/evaluator evidence exists.
  - Spec evidence: AlphaEvolve Section 3.1 says the matrix prompt requested
    near-integral solutions and the reported decompositions were rounded to
    the nearest integer or half-integer before exactness verification.
  - Current evidence: README describes the matrix-result report contract,
    Appendix A registry, and checked Strassen baseline bundle, including
    coefficient-domain and exactness restrictions for AlphaEvolve-comparable
    reports. It now documents `libreevolve.matrix_near_integrality_evidence.v1`
    as a validation contract for declared prompt instructions,
    integer/half-integer rounding policy, raw-versus-rounded coefficient
    diagnostics, and exactness-certificate links. It now also documents
    `libreevolve.matrix_near_integrality_runtime_boundary.v1` as the current
    `not_emitted_by_local_runner` boundary plus emitted-record validation for
    run/target/candidate ids, seeds, prompt hashes/instructions, raw and
    rounded coefficients, rounding error, exactness-certificate links,
    matrix-result refs, artifact paths, and artifact hashes. It also documents
    the builder that turns validated near-integrality evidence into linked
    runtime rows. It does not document a local matrix benchmark
    prompt/evaluator path that emits those records during search.
  - Required result: when local benchmark prompt/evaluator emission lands,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so README distinguishes evidence-schema validation from AlphaEvolve Section
    3.1 search-workflow parity.

- [ ] Keep README matrix wording scoped until sweep-space records are emitted.
  - Spec evidence: AlphaEvolve Figures 9a-9c show the 4x4 matrix program
    evolving a `sweep()` function that declares user-provided `hyper` ranges
    for optimizer, noise, clipping, discretization, and related search
    parameters.
  - Current evidence: README documents matrix result reports, Appendix A
    registry checks, the checked Strassen baseline bundle, and open
    near-integrality/scalar-field gaps. It now documents
    `libreevolve.matrix_sweep_space_evidence.v1` as a declared-evidence
    validator for candidate-produced sweep spaces, sampled configuration ids,
    per-sweep outcomes, selected winner identity, and final
    decomposition/exactness-certificate links. It now also documents
    `libreevolve.matrix_sweep_space_runtime_boundary.v1` as the current
    `not_emitted_by_local_runner` boundary plus emitted-record validation for
    run/target/candidate ids, seeds, search-program refs, sweep function
    identity, hyper-library and hyperparameter declarations, sampled
    configurations, winning configuration, certificate/decomposition refs,
    matrix-result refs, artifact paths, and artifact hashes. It also documents
    the builder that turns validated sweep-space evidence into a linked runtime
    row and states that local matrix benchmark runners still do not emit those
    records.
  - Required result: when matrix runners emit sweep-space provenance, update
    README, ROADMAP, papers index, and matching TODOs so README can distinguish
    actual AlphaEvolve Figure 4/Figure 9 search-program evidence from schema
    validation alone.

- [ ] Keep README Appendix A Figure 9 wording scoped until magnified-diff
      panel artifacts exist.
  - Spec evidence: AlphaEvolve Appendix A Figures 9a-9c are the three-panel
    magnified source/diff version of Figure 4's matrix program, showing the
    rank-48 4x4 search-program changes across ordered code excerpts. The
    displayed changes include optimizer, initialization, noise, clipping,
    hallucination/discretization/loss-penalty, and named sweep-field
    components.
  - Current evidence: README can document matrix result reports, Appendix A
    registry coverage, Figure 4 exhibit gaps, Figure 9 sweep-space gaps, and
    `libreevolve.alphaevolve_figure9_matrix_diff_exhibit.v1`. README now
    documents that the Figure 9 schema validates Figure 9a/9b/9c panel IDs,
    PDF pages 35-37, Figure 4 caption linkage, exact code line spans,
    source/diff excerpt artifact hashes, rendered/OCR text hashes, panel
    continuity, semantic component labels for the shown code changes, and links
    from the appendix panels to matrix target rows, sweep metadata, exactness
    certificates, and companion source evidence. It now also documents
    `libreevolve.alphaevolve_figure9_matrix_diff_artifact_boundary.v1` as the
    current `not_emitted_by_local_report_export` boundary and emitted
    panel-artifact fields. It also documents the builder from Figure 9 exhibit
    metadata and nested-panel linkage validation, while still stating that the
    rendered/OCR/source-diff panel artifacts are not emitted or checked in.
  - Required result: when Appendix A Figure 9 magnified-diff panel artifacts
    land, update README, ROADMAP, papers index, and matching TODOs so README
    distinguishes reproduced appendix source/diff panels from Figure 4
    main-text exhibit evidence, semantic change-component evidence, and generic
    sweep-space provenance.

- [ ] Keep README Figure 4 matrix-exhibit wording scoped until rendered
      artifacts and mutation lineage exist.
  - Spec evidence: AlphaEvolve Figure 4 is the main-text matrix discovery
    exhibit, showing a concrete evolved 4x4 tensor-decomposition search-program
    diff and tying it to Section 3.1/Table 2 matrix rank-improvement results.
    The caption further says the example required 15 mutations, with
    non-trivial optimizer, weight-initialization, loss-function, and
    hyperparameter-sweep changes.
  - Current evidence: README documents matrix result reports, Appendix A
    registry checks, checked Strassen baseline evidence, and open
    near-integrality, scalar-field, baseline, and sweep-space gaps. It now
    documents `libreevolve.alphaevolve_figure4_matrix_discovery_exhibit.v1`,
    which validates Figure 4 exhibit ids, source PDF page 11, caption values,
    exact source diff excerpt artifacts/hashes, selected matrix target/result
    mappings, rendered visual/text artifact paths/hashes, rendering parameters,
    the 15-mutation caption count, component-level mutation categories, and
    links from the displayed exhibit to Figure 9, matrix reports,
    certificates, notebooks, and paper-source evidence. It now also documents
    `libreevolve.alphaevolve_figure4_matrix_discovery_artifact_boundary.v1`
    as the current `not_emitted_by_local_report_export` boundary and emitted
    Figure 4 artifact/lineage fields. It also documents the builder from
    Figure 4 exhibit metadata plus supplied accepted-mutation lineage and
    nested-linkage validation, while still stating that rendered/source
    artifacts and accepted-mutation lineage are not emitted.
  - Required result: when Figure 4 rendered/source artifacts and accepted
    mutation-lineage records land, update README, ROADMAP, papers index, and
    matching TODOs so README distinguishes reproduced main-text matrix exhibit
    evidence from general matrix benchmark readiness, Figure 4 mutation-lineage
    evidence, and Appendix A Figure 9 sweep-space parity.

- [ ] Keep README matrix wording scoped to final reports until
      baseline-component provenance exists.
  - Spec evidence: AlphaEvolve Section 3.1 says matrix-decomposition search
    starts from a standard gradient-based algorithm with an initializer,
    reconstruction loss function, and Adam optimizer before evolving more
    sophisticated tensor-decomposition algorithms.
  - Current evidence: README documents matrix result reports, Appendix A
    registry coverage, checked Strassen artifacts, and open follow-ups for
    near-integrality, sweep provenance, scalar fields, and scaling limits. It
    now documents `libreevolve.matrix_baseline_component_runtime_boundary.v1`,
    which validates the current `not_emitted_by_local_runner` boundary and
    required future fields for Section 3.1 starting-algorithm records. It also
    documents the builder that can create emitted records from a component
    inventory and validate ref/scope/hash linkage, but it does not yet document
    automatic matrix benchmark runner emission for those records.
  - Required result: when matrix benchmark runs persist baseline component
    inventory and mutation-lineage records, update README, ROADMAP, papers
    index, and code/paper TODO entries together so README distinguishes final
    matrix result-report validation from AlphaEvolve Section 3.1
    baseline-to-evolved-program workflow evidence.

- [ ] Keep README matrix wording scoped until scalar-field artifacts exist.
  - Spec evidence: AlphaEvolve Table 2 notes that some improved matrix
    algorithms use complex-valued multiplications and can be used for exact
    multiplication of complex or real-valued matrices, while Section 3.1
    contrasts characteristic-0 and finite-field-only results.
  - Current evidence: README describes matrix-result fields for coefficient
    domain and exactness, plus Appendix A target identity and checked Strassen
    baseline artifacts. It now documents
    `libreevolve.matrix_scalar_field_evidence.v1`, which validates scalar-field
    metadata, exact complex coefficient representation,
    characteristic/applicability claims, paper complex target caveats, and
    certificate scope for real-versus-complex multiplication. It also
    documents `libreevolve.matrix_scalar_field_runtime_boundary.v1` as the
    current `not_emitted_by_local_runner` boundary plus emitted-record
    validation for run/target/candidate ids, seeds, scalar field,
    characteristic, applicability, coefficient representation, algorithm refs,
    certificate refs, matrix-result refs, artifact paths, and artifact hashes.
    It also documents the builder that turns validated scalar-field evidence
    into a linked runtime row and states that local runners do not emit exact
    complex decomposition/certificate artifacts.
  - Required result: when matrix reports and certificates emit scalar field,
    complex coefficient data, characteristic, and applicability artifacts,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so README can distinguish schema validation from AlphaEvolve-style
    complex-valued matrix result evidence.

- [ ] Keep README matrix rank wording scoped until tensor-rank artifacts exist.
  - Spec evidence: AlphaEvolve Section 3.1 frames matrix improvements as
    low-rank tensor decompositions, and footnote 3 says some algorithms using
    fewer than 49 multiplications do not correspond to matrix-multiplication
    tensor decompositions and cannot be applied recursively to larger matrix
    multiplication.
  - Current evidence: README describes Appendix A target/rank/outcome
    validation, coefficient-domain/exactness fields, scalar-field gaps, and
    checked Strassen artifacts. It now documents
    `libreevolve.matrix_tensor_rank_evidence.v1`, which validates
    algorithm-kind metadata, tensor-decomposition certificate scope, recursive
    applicability, target-tensor/certificate links, and footnote-level caveats
    that separate tensor-rank evidence from non-recursive multiplication
    algorithms. It also documents
    `libreevolve.matrix_tensor_rank_runtime_boundary.v1` as the current
    `not_emitted_by_local_runner` boundary plus emitted-record validation for
    run/target/candidate ids, seeds, algorithm kind, rank, recursive
    applicability, certificate scope, tensor-identity status, target-tensor
    refs, exactness-certificate refs, matrix-result refs, artifact paths, and
    artifact hashes. It also documents the builder that turns validated
    tensor-rank evidence into a linked runtime row and states that
    target-tensor/certificate artifacts are not emitted.
  - Required result: when matrix reports or companion artifacts capture
    tensor-rank applicability and recursive-use caveats, update README,
    ROADMAP, papers index, and code/paper TODO entries together so README
    qualifies rank comparisons and does not imply every fewer-multiplication
    algorithm is a recursive tensor-decomposition baseline.

- [ ] Keep README certification and systems-result wording scoped to report
  contracts versus executed independent evidence.
  - Spec evidence: AlphaEvolve Section 3.3 reports confirmation beyond local
    optimizer feedback, including post-deployment fleet measurements, held-out
    kernel-shape evaluation, randomized reference-code checks, and human expert
    confirmation for final FlashAttention changes.
  - Current evidence: README now says
    `libreevolve.paper_result_certification.v1` distinguishes local validator
    records from paper-claim-ready independent certifications, and that the
    accompanying artifact inventory proves named evidence files are present,
    not that independent verifiers, deployment measurements, or human review
    have been performed. README also says
    `libreevolve.systems_result_report.v1` is a readiness/report schema only,
    while `libreevolve.systems_result_artifact_inventory.v1` proves artifact
    availability, not unseen workloads, reference-code checks, deployment
    evidence, or independent certification. Matching paper/code TODOs still
    require real verifier scripts, reviewer/deployment provenance, systems
    fixtures, held-out case sets, randomized/reference-correctness checks, and
    domain-specific rules for when a held-out or reference-correctness gate may
    be marked `not_applicable`.
  - Required result: when benchmark runs emit real certification reports,
    deployment/reviewer evidence, held-out systems reports, or reference-code
    checks, and when systems reports enforce domain-specific readiness gates,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so README neither underclaims the current report and inventory contracts
    nor overclaims AlphaEvolve-style confirmed result evidence.

- [ ] Keep README systems-metric wording scoped until calibrated Section 3.3
      result claims are populated.
  - Spec evidence: AlphaEvolve Section 3.3 reports concrete systems outcomes
    with units and comparison context, including scheduling resource recovery,
    Pallas/Gemini speedups and training-time reduction, hardware power/area
    objectives, and FlashAttention kernel plus pre/postprocessing speedups.
  - Current evidence: README now documents that
    `libreevolve.systems_result_report.v1` requires `claim_calibration`
    records for `alphaevolve_ready` reports, including published-style claim
    ids, units, denominators, baselines, aggregation rules, before/after
    windows, runtime/deployment/synthesis context, artifact refs, and source
    refs. Existing fixtures do not yet carry real calibrated Section 3.3
    result-claim records.
  - Required result: once systems fixtures and certification examples populate
    calibrated metric records for scheduling, kernel, hardware, and compiler
    domains, update README, ROADMAP, papers index, and matching TODOs so README
    can describe those records without implying the schema alone reproduces
    AlphaEvolve result magnitudes.

- [ ] Keep README systems-result wording scoped until application-owner and
      domain-review provenance is populated.
  - Spec evidence: AlphaEvolve Section 3.3 frames the Borg scheduling,
    Gemini/Pallas kernel, TPU RTL, and XLA/FlashAttention IR results as
    production-facing practical applications, and the Acknowledgements and
    Contributions sections identify the co-leads, advisors, reviewers,
    validation owners, TPU designers, and XLA reviewers involved in those
    domains.
  - Current evidence: README now documents `application_provenance` records
    required for `alphaevolve_ready` systems reports: responsible application
    role, review/signoff scope, validation/source data owner, production
    approval state, claim links, artifact refs, and a local-benchmark versus
    production-claim boundary. Existing fixtures do not yet carry real
    reviewed owner/reviewer records.
  - Required result: when practical systems fixtures and certification examples
    are populated with reviewed application-owner and domain-review provenance,
    update README, ROADMAP, papers index, and matching TODOs so README can
    describe those records without implying the schema alone proves
    domain-owner validated production or deployment claims.

- [ ] Keep README scheduling wording scoped until ranking-only safety
      provenance is populated.
  - Spec evidence: AlphaEvolve Section 3.3.1 says the Borg scheduling
    heuristic scores only machines already determined by Borg to be available
    and capable of running the pending job, so correctness is effectively by
    construction.
  - Current evidence: README now documents `scheduling_safety` records required
    for `alphaevolve_ready` scheduling reports, including feasible
    candidate-set source, ranking-only scope, resource invariants,
    simulator/admission/placement boundaries, authority flags, and artifact
    refs. Existing scheduling fixtures do not yet carry real populated safety
    records.
  - Required result: once scheduling fixtures and certification examples
    populate feasibility-filter provenance, ranking-only scope, resource
    invariants, and simulator/admission-boundary evidence, update README,
    ROADMAP, papers index, and matching TODOs so README can describe those
    records without implying the schema alone proves Borg-style scheduling
    safety.

- [ ] Keep README scheduling wording scoped until vector-bin-packing
      formulation evidence is populated.
  - Spec evidence: AlphaEvolve Section 3.3.1 formulates Borg scheduling as an
    online vector bin-packing problem with machines as CPU/memory-capacity
    bins, pending jobs as CPU/memory-demand items, stranded resources as the
    optimization motivation, and simulator feedback from historical workload
    and capacity snapshots.
  - Current evidence: README now documents `scheduling_formulation` records
    required for `alphaevolve_ready` scheduling reports: bin/item schema,
    CPU/memory units and denominators, workload/capacity snapshot provenance,
    stranded-resource objective linkage, simulator input hashes, artifact refs,
    and mapping from source data to `required` and `free` heuristic features.
    Existing scheduling fixtures do not yet carry real populated formulation
    records.
  - Required result: once scheduling fixtures and certification examples
    populate Borg-style formulation evidence, update README, ROADMAP, papers
    index, and matching TODOs so README can describe those records without
    implying the schema alone proves AlphaEvolve-style scheduling problem
    setup.

- [ ] Keep README scheduling wording scoped until
      interpretability/deployment-readiness evidence is populated.
  - Spec evidence: AlphaEvolve Section 3.3.1 says the Borg scheduling
    heuristic was chosen over deep reinforcement learning because the code
    solution offered interpretability, debuggability, predictability, and ease
    of deployment, which were essential for a mission-critical system.
  - Current evidence: README now documents `scheduling_deployment_readiness`
    records required for `alphaevolve_ready` scheduling reports, including
    human-readable heuristic structure, operator/debug review, predictability
    checks, deployment-risk controls, deployment ergonomics, artifact refs, and
    comparison against less interpretable learned policies. Existing scheduling
    fixtures do not yet carry real populated deployment-readiness records.
  - Required result: once scheduling fixtures and certification examples
    populate interpretability/debuggability review, predictability checks,
    deployment ergonomics, rollout-risk evidence, and baseline comparison
    against black-box approaches, update README, ROADMAP, papers index, and
    matching TODOs so README can describe those records without implying the
    schema alone proves AlphaEvolve-style mission-critical deployment
    suitability.

- [ ] Keep README Figure 6 scheduling wording scoped until heuristic-exhibit
      provenance exists.
  - Spec evidence: AlphaEvolve Figure 6 shows the exact Borg scheduling
    heuristic source and a CPU/memory residual heatmap, while Section 3.3.1
    ties the heuristic to simulator feedback, unseen workloads, deployment,
    and about 0.7% fleet-wide resource recovery.
  - Current evidence: README documents generic systems reports, scheduling
    ranking-only safety gaps, interpretability/deployment gaps, and
    Section 3.3 metric-calibration gaps. It does not document Figure 6 exhibit
    mapping, exact heuristic code hashes, residual-feature definitions,
    heatmap data/rendering parameters, visual artifact paths/hashes, baseline
    production heuristic identity, or simulator/deployment report links.
  - Required result: when Figure 6 exhibit provenance lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes generic scheduling readiness and result claims from
    reproduced paper figure/exhibit evidence.

- [ ] Keep README Figure 7 Pallas wording scoped until tiling-problem exhibit
      provenance exists.
  - Spec evidence: AlphaEvolve Figure 7 visualizes the Pallas matrix-product
    tiling heuristic problem with dimensions `M`, `N`, and `P`; Section 3.3.2
    explains that tile-size selection depends on accelerator shapes, memory
    capacity, fused operations, and compiler details.
  - Current evidence: README documents generic systems reports and Pallas
    shape-split/runtime gaps. It does not document Figure 7 exhibit mapping,
    matrix-shape variable definitions, tile-parameter schema,
    accelerator/memory/fusion/compiler-context annotations, diagram data,
    rendered visual artifact paths/hashes, rendering parameters, or links from
    the visualization to shape-corpus/runtime reports.
  - Required result: when Figure 7 exhibit provenance lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes generic kernel readiness and Pallas runtime evidence from
    reproduced paper figure/tiling-problem visual evidence.

- [ ] Keep README kernel wording scoped to generic systems reports until
      Pallas shape-split/runtime evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.2 optimizes Gemini Pallas
    matrix-multiplication tiling heuristics on real TPU accelerators, using
    realistic user-collected input shapes split into training and evaluation
    halves, with correctness preserved by changing tiling strategy rather than
    the underlying operation.
  - Current evidence: README documents generic systems result reports and
    held-out/reference gates, but it does not yet document kernel-specific
    shape-corpus provenance, train/eval split hashes, accelerator runtime
    artifacts, expert-baseline heuristic identity, tiling-only output
    constraints, correctness-by-construction scope, or engineering-effort
    calibration for months-to-days optimization turnaround and deployment/
    ergonomics impact.
  - Required result: once kernel report metadata captures shape-corpus,
    train/eval split, TPU runtime, expert-baseline comparison, tiling
    constraints, unchanged-operation evidence, engineering-effort baseline,
    automated-experiment duration, and production/workflow adoption state,
    update README, ROADMAP, papers index, and matching TODOs so README does not
    imply generic systems report readiness proves AlphaEvolve-style Pallas
    kernel optimization.

- [ ] Keep README Pallas workflow wording scoped until autotuning/manual
      heuristic baseline evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.2 contrasts AlphaEvolve-discovered
    tiling heuristics with search-based autotuning, which interrupts research
    workflows and requires retuning for input-shape changes, and manually
    crafted heuristics, which are a major expert-engineering bottleneck. It
    frames AlphaEvolve as a path toward automating manual tuning and improving
    Gemini kernel ergonomics.
  - Current evidence: README can describe generic systems reports, shape splits,
    TPU runtime gaps, expert-baseline comparison gaps, and months-to-days
    optimization-turnaround calibration. It should not imply current kernel
    evidence proves reduced autotuning interruption, reduced manual heuristic
    effort, retuning avoidance, or model-developer ergonomics impact.
  - Required result: once kernel report metadata captures baseline workflow
    class, autotuning search/retuning policy, manual-effort assumptions,
    input-shape-change sensitivity, hardware-expertise requirements, and
    ergonomics comparison, update README, ROADMAP, papers index, and matching
    TODOs so README distinguishes speedup evidence from AlphaEvolve-style
    workflow automation for Pallas tiling.

- [ ] Keep README Gemini self-training wording scoped until Pallas deployment
      loop evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.2 says the deployed Pallas tiling
    heuristic directly enhanced Gemini training efficiency and marked a novel
    instance where Gemini, through AlphaEvolve, optimized its own training
    process.
  - Current evidence: README can point to Pallas shape-split/runtime gaps,
    workflow-baseline gaps, speedup calibration gaps, and broad
    self-improvement boundaries. It does not separately require evidence that
    a deployed kernel optimization affected the training pipeline of the same
    Gemini-family system that powered AlphaEvolve, or that production metrics
    justify the self-training interpretation.
  - Required result: when Gemini self-training loop evidence lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes ordinary Pallas kernel deployment and workflow automation
    from AlphaEvolve-style self-optimization of Gemini's training process.

- [ ] Keep README hardware wording scoped to generic systems reports until
      RTL/EDA verification evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.3 optimizes Verilog RTL for a TPU
    arithmetic circuit, tracks power/area objectives, requires robust
    functional verification, and reports TPU-designer plus downstream
    synthesis-tool confirmation. It also frames the result as an early
    RTL-stage contribution integrated into an upcoming TPU, with direct
    Verilog communication fostering trust, simplifying adoption, and
    potentially reducing time to market.
  - Current evidence: README documents systems result reports and artifact
    inventories as generic readiness/report contracts. It does not yet
    document hardware-specific evidence for HDL source boundaries,
    synthesis/PPA metrics, equivalence or formal verification, timing/power/
    area constraints, designer signoff, downstream synthesis confirmation,
    RTL-stage placement, standard-language adoption/trust evidence,
    upcoming-chip integration, or time-to-market impact.
  - Required result: when RTL/EDA report metadata and validators land, update
    README, ROADMAP, papers index, and matching TODOs so README does not imply
    generic systems report readiness proves AlphaEvolve-style TPU-circuit
    optimization, adoption, or deployment evidence.

- [ ] Keep README hardware-rewrite wording scoped until TPU bit-removal
      artifact evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.3 says the TPU hardware result was
    a simple Verilog rewrite of a key arithmetic circuit in the matrix
    multiplication unit that removed unnecessary bits while reducing area and
    power.
  - Current evidence: README documents generic systems reports and the broader
    RTL/EDA verification gap, but it does not require README wording to wait
    for concrete rewrite provenance: before/after Verilog artifact hashes,
    changed spans, removed-bit or signal inventory, component/matrix-unit
    identifiers, rewrite-category labels, or links from the eliminated bits to
    PPA and verification records.
  - Required result: once TPU arithmetic-circuit rewrite metadata lands, update
    README, ROADMAP, papers index, and matching TODOs so README distinguishes
    a reproduced bit-removal rewrite artifact from generic hardware
    correctness, PPA, designer-signoff, or downstream synthesis evidence.

- [ ] Keep README Gemini-to-TPU contribution wording scoped until hardware
      attribution evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.3 says the RTL improvement was
    integrated into an upcoming TPU and marked "Gemini's first direct
    contribution to TPU arithmetic circuits", achieved via AlphaEvolve.
  - Current evidence: README can point to hardware verification gaps,
    upcoming-TPU integration gaps, downstream synthesis-tool confirmation
    gaps, and concrete bit-removal artifact gaps. It does not require evidence
    for the attribution chain that makes the claim about Gemini directly
    contributing to TPU arithmetic circuits rather than merely reporting a
    Verilog optimization.
  - Required result: when Gemini-to-TPU contribution metadata lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes RTL optimization, integration, and synthesis rediscovery
    evidence from the broader self-contribution claim involving Gemini,
    AlphaEvolve, a specific TPU generation, and reviewed arithmetic-circuit
    integration.

- [ ] Keep README compiler-IR wording scoped to final reference gates until
      per-edit randomized checks exist.
  - Spec evidence: AlphaEvolve Section 3.3.4 checked each FlashAttention
    compiler-IR modification against reference code on randomized inputs and
    then separately had the final code confirmed by human experts for all
    possible inputs; the same section says the optimized XLA IR was intended
    for debugging rather than direct developer editing and was
    compiler-generated/already highly optimized.
  - Current evidence: README documents generic systems result reports and
    reference-correctness gates, but it does not yet describe per-edit
    randomized reference-check traces, reference implementation hashes,
    randomized input generator provenance, IR-origin/editability boundaries,
    compiler-generated baseline provenance, numerical tolerance policy, or
    kernel-versus-pre/postprocessing attribution.
  - Required result: once compiler/kernel report metadata captures per-edit
    reference checks, randomized input coverage, tolerance/failure policy,
    IR provenance/editability constraints, abstraction-level attribution, and
    final expert signoff scope, update README, ROADMAP, papers index, and
    matching TODOs so README does not imply final reference-gate artifacts
    prove AlphaEvolve-style compiler-IR traces.

- [ ] Keep README compiler-stack wording scoped until FlashAttention context
      provenance exists.
  - Spec evidence: AlphaEvolve Section 3.3.4 situates the compiler task in a
    specific stack: FlashAttention implements Transformer attention as a
    Pallas accelerator kernel, higher-level JAX code wraps input preparation
    and output postprocessing, XLA lowers the implementation through IR stages
    for particular hardware, and the optimized configuration is a high-impact
    inference workload on GPUs.
  - Current evidence: README documents generic systems reports and notes
    compiler-IR reference-check and speedup gaps, but it does not document the
    stack-context evidence needed to make a compiler claim AlphaEvolve-like:
    workload/model configuration, FlashAttention/Pallas kernel identity, JAX
    wrapper boundaries, XLA lowering-stage identities, hardware target,
    lowered-IR artifact hashes, or memory-orchestration versus scheduling
    decision categories.
  - Required result: once FlashAttention compiler-stack metadata lands, update
    README, ROADMAP, papers index, and matching TODOs so README distinguishes
    generic compiler readiness from the specific Pallas/JAX/XLA/FlashAttention
    context behind AlphaEvolve's compiler-generated IR result.

- [ ] Keep README compiler-adoption wording scoped until compiler integration
      path evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.4 separates two compiler adoption
    possibilities after the FlashAttention result: incorporating discovered
    optimizations into existing compilers for specific use cases, or, longer
    term, incorporating AlphaEvolve into the compiler workflow itself.
  - Current evidence: README documents generic systems reports plus compiler-IR
    reference-check, stack-context, and speedup gaps. It does not describe the
    evidence needed before claiming a discovered optimization was incorporated
    into an existing compiler, nor the stronger evidence needed before claiming
    AlphaEvolve-style compiler-workflow integration: target compiler/pass,
    bounded use case, optimization artifact, integration reviewer, rollout or
    revert state, and workflow handoff.
  - Required result: once compiler report metadata captures adoption path,
    target compiler/pass identity, use-case constraints, integration and
    rollout status, update README, ROADMAP, papers index, and matching TODOs so
    README separates concrete compiler adoption from longer-term AlphaEvolve
    workflow integration.

- [ ] Keep README self-improvement wording scoped until infrastructure and
      distillation evidence exists.
  - Spec evidence: AlphaEvolve's Discussion says practical discoveries can
    improve the efficiency of its own infrastructure and future base LLMs, and
    frames distillation of AlphaEvolve-augmented performance into base models
    as a natural next step. Local PDF page 21 contains those Discussion
    statements.
  - Current evidence: README documents provider budgets, systems-result
    schemas, benchmark contracts, and paper-result certification boundaries.
    It does not describe any LibreEvolve runtime, provider, compiler,
    evaluator, or benchmark component as an evolved optimization target for
    the tool itself, and it has no distillation dataset, training, or
    model-evaluation evidence derived from evolved candidates. The
    ThetaEvolve-inspired export plugin can write clipped reward examples, but
    that export is not model training, model evaluation, or proof of
    AlphaEvolve-augmented base-model uplift.
  - Required result: when self-improvement reports, deployment/adoption
    measurements, rollback/safety evidence, or distillation artifacts land,
    update README, ROADMAP, papers index, and matching TODOs so README neither
    underclaims concrete infrastructure improvements nor overclaims
    AlphaEvolve-style self-improving or model-uplift capability.

- [ ] Keep README feedback-loop cadence wording scoped until environment ROI
      evidence exists.
  - Spec evidence: AlphaEvolve's Discussion says current self-improvement gains
    are moderate, feedback loops for improving the next AlphaEvolve version
    are on the order of months, and those improvements should make setting up
    more robust-evaluator environments more valuable.
  - Current evidence: README can describe provider budgets, systems reports,
    benchmark contracts, self-improvement boundaries, and distillation gaps. It
    does not document measured improvement-loop duration, next-version
    dependency, moderate-gain calibration, or environment setup cost/value
    evidence for creating more robust evaluator environments.
  - Required result: when feedback-loop cadence and environment ROI metadata
    lands, update README, ROADMAP, papers index, and code/paper TODOs together
    so README distinguishes ordinary self-improvement evidence from
    AlphaEvolve-style months-scale infrastructure/model feedback loops and the
    economic case for adding new robust-evaluator problem environments.

- [ ] Keep README benchmark-hardening wording scoped to smoke evidence versus
  benchmark-grade anti-gaming fixtures.
  - Spec evidence: AlphaEvolve-comparable benchmark claims require robust target
    suites whose reported improvements cannot be explained by hardcoded cases,
    shortcut access to reference answers, artifact spoofing, or local smoke
    validator quirks.
  - Current evidence: README now says
    `libreevolve.benchmark_hardening.v1` validates protected signals, shortcut
    threats, detector strategy, negative fixtures, and hashed hardening
    artifacts; it also says the artifact inventory proves named anti-gaming
    evidence files exist, not that a real benchmark runner generated them.
    Matching roadmap/paper/code TODOs distinguish the checked matrix smoke
    hardening bundle, which preserves `alphaevolve_comparable: false`, from
    still-missing benchmark-grade tensor/geometric/compiler/systems fixtures
    with real randomized or exhaustive anti-gaming evidence. Matching paper and
    code TODOs also mark the Appendix B registry as a family/status ledger:
    paper-result families still have null target-baseline values, and
    construction/certificate artifact-schema strings are not executable
    validators, reported constructions, SOTA thresholds, or verifier scripts.
    AlphaEvolve Appendix B says the reported construction data and verification
    code are available in an accompanying Google Colab; README should not imply
    the registry has that Colab-equivalent verifier-data surface yet. The
    shipped-example scope registry is validated in focused tests, smoke
    hardening evidence, and README's routine paper-cache validation command.
  - Required result: when real target-family benchmark runners emit
    benchmark-grade hardening reports, negative fixtures, detector logs, and
    artifact inventories, and when Appendix B families gain executable
    construction/certificate validators, target baselines, construction-data
    exports, and verifier-code artifacts, update README, ROADMAP, papers
    index, and code/paper TODO entries together so README neither underclaims the
    checked smoke hardening evidence nor overclaims AlphaEvolve-comparable
    benchmark hardening.

- [ ] State follow-on problem-repository coverage as snapshot-scoped.
  - Spec evidence: the `google-deepmind/alphaevolve_repository_of_problems`
    README says the repository is live and expected to expand/improve over
    time, with problem pages for all 67 mathematical problems and Colab
    notebooks for many, but not all, problems. It says notebooks can include
    prompts, verification code, initial programs, final evolved programs, and
    visualization/analysis code where appropriate. It gives a hosted
    `problems/{n}.html` URL pattern on `google-deepmind.github.io`, says no
    installation is required, says notebooks open in Google Colab and webpages
    open in any browser, and points the distribution graphic to root-level
    `status_grid.png`. Current `status.json` has buckets `world_record`,
    `former_record`, `worse_than_record`, and `matched_optimal`, listing 43
    problem ids total.
  - Current evidence: README now documents
    `libreevolve.alphaevolve_follow_on_problem_coverage.v1`, which validates
    the pinned repository URL/commit/date, live-update policy, declared
    67-problem id range, browser-page and many-but-not-all Colab access modes,
    root-level status artifact paths/hashes for `status.json`,
    `status_grid.png`, and `result_distribution.png`, parsed status buckets,
    43 listed ids, 24 `not_listed_in_status_json` ids, and the declared-67
    versus observed-68 numbered HTML page boundary. README still cannot point
    to per-problem page hashes, notebook paths/hashes or absence reasons,
    prompt/verifier/initial/final/visualization flags, page-68 classification,
    or emitted source-manifest rows.
  - Required result: after per-problem source-coverage metadata lands, update
    README so AlphaEvolve follow-on claims name hosted page URL/hash per
    problem, partial notebook/artifact coverage, notebook absence reasons,
    emitted status/source rows, and explicit wording that avoids implying
    notebook or artifact coverage is complete when only problem-page and
    status-bucket evidence is currently scoped.

- [ ] Keep README follow-on problem-count wording scoped until page inventory
      is reconciled.
  - Spec evidence: the `google-deepmind/alphaevolve_repository_of_problems`
    README says there are 67 mathematical problem descriptions, while the
    current live `problems/` directory exposes 68 numbered HTML files.
    `problems/67.html` and `problems/68.html` are both titled `Logic puzzles`;
    one page has an under-construction Colab placeholder and the other has a
    generic Colab URL plus a placeholder paper link.
  - Current evidence: README TODOs require follow-on repository coverage,
    hosted URLs, notebook/artifact access modes, status buckets, and pinned
    snapshots. They do not require README wording that explains the live
    repository's numbered-page inventory versus the README/paper problem-count
    claim, nor do they require duplicate-title or placeholder-link diagnostics.
  - Required result: after numbered-page inventory validation exists, update
    README so follow-on source claims distinguish paper/README problem count
    from live repository HTML-page count, list any duplicate or placeholder
    pages as snapshot diagnostics, and avoid treating every numbered page as a
    complete problem/notebook/paper-linked source artifact until reconciled.

- [ ] Keep README figure/notebook provenance wording scoped until paper
      artifact-role records are bound to artifacts.
  - Spec evidence: AlphaEvolve's Contributions section attributes paper figure
    creation to specific authors and separately identifies the people who
    assembled the accompanying Google Colab.
  - Current evidence: README can describe PDF manifest validation, future
    companion Colab tracking, exhibit provenance gaps, rendered artifact
    hashes, and `libreevolve.alphaevolve_paper_artifact_roles.v1`. The role
    contract validates figure-creator and companion-Colab assembler records
    with stable artifact ids, exact initials, source section/page metadata, and
    source phrases. README now also documents
    `libreevolve.alphaevolve_paper_artifact_linkage.v1`, which validates the
    current `not_yet_linked` availability boundary and required digest/link/
    source-map fields, but it does not document concrete rendered figure files,
    companion notebook URLs/digests, or source-to-artifact maps.
  - Required result: when role records are linked to concrete rendered or
    companion-notebook artifacts, update README, ROADMAP, papers index, and
    code/paper TODOs together so README distinguishes artifact availability,
    rendered/source hashes, and paper-attributed figure/notebook creator or
    assembler provenance.

- [ ] Keep README constructive-math wording scoped to static context/artifacts
      versus AlphaEvolve-style incumbent handoff.
  - Spec evidence: AlphaEvolve Section 3.2 evolved heuristic search programs
    that use a fixed budget and a strong previously discovered construction as
    input, then return an improved construction for verification.
  - Current evidence: README can accurately describe workspace seeds, static
    context, evaluator artifacts, Appendix B coverage/status records, and
    smoke examples. It should not imply current constructive-math support
    includes a benchmark runner that passes incumbent constructions to
    candidate heuristics, records the fixed search budget, or verifies
    candidate-produced construction improvements as a Section 3.2-style loop.
  - Required result: when real heuristic-search handoff support lands, update
    README, ROADMAP, papers index, and code/paper TODO entries together so
    README distinguishes static problem context and post-run artifacts from
    first-class incumbent-construction benchmark handoff evidence.

- [ ] Keep README constructive-math wording scoped until heuristic-stage
      sequence evidence exists.
  - Spec evidence: AlphaEvolve Section 3.2 says constructive-math heuristics
    were run with fixed time budgets such as `1000 seconds` and that final
    constructions often resulted from a sequence of specialized heuristics:
    early broad-gain stages from random/simple starts and later fine-tuning
    stages near optimal configurations.
  - Current evidence: README can describe runtime budgets, static context,
    simple/random starting-point gaps, incumbent handoff gaps, and aggregate
    outcome gaps. It should not imply the current reports prove a
    stage-by-stage adaptive heuristic chain with exact per-stage budget,
    incumbent lineage, produced construction, improvement delta, and stage role.
  - Required result: when heuristic-stage sequence reports land, update README,
    ROADMAP, papers index, and code/paper TODO entries together so README
    distinguishes one-shot heuristic handoff support from AlphaEvolve-style
    multi-stage constructive-math search evidence.

- [ ] Keep README constructive-math coverage wording scoped to Appendix B
      family status until aggregate outcome reports exist.
  - Spec evidence: AlphaEvolve Section 3.2 reports over 50 mathematical
    problems across more than five branches, with roughly 75% matching best
    known constructions and roughly 20% improving SOTA.
  - Current evidence: README describes the Appendix B registry as thirteen
    constructive-math families with one smoke fixture and planned entries for
    the rest. That is a family/status and expected-artifact ledger, not a
    per-problem/per-parameter outcome report with branch taxonomy, previous
    best references, construction links, and matched/improved aggregate
    percentages.
  - Required result: when constructive-math outcome reports land, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes Appendix B family coverage from AlphaEvolve-style aggregate
    mathematical breadth and SOTA-rate claims.

- [ ] Keep README constructive-math starting-point wording scoped until
      simple/random construction provenance exists.
  - Spec evidence: AlphaEvolve Section 3.2 says the initial starting point for
    the constructive-math cases was a simple or random construction.
  - Current evidence: README can describe seed/source provenance, invalid
    optimization-pressure seeds, Appendix B family/status coverage, aggregate
    outcome gaps, and human-seeded matrix-result caveats. It does not yet
    document constructive-math report fields that classify each initial
    construction as simple, random, human-seeded, or prior-art-seeded, preserve
    the construction artifact/hash and generator seed, record the baseline
    value, or prove that aggregate Section 3.2 claims are not based on hidden
    incumbent construction seeding.
  - Required result: when constructive-math starting-construction provenance
    lands, update README, ROADMAP, papers index, and code/paper TODOs together
    so README distinguishes Appendix B family coverage and aggregate outcomes
    from the paper's simple/random-start claim.

- [ ] Keep README Figure 5 constructive-math wording scoped until exhibit
      provenance exists.
  - Spec evidence: AlphaEvolve Figure 5 shows selected SOTA-breaking
    mathematical constructions with branch labels, problem labels,
    before/after metric values, and rendered visuals.
  - Current evidence: README describes Appendix B registry/status coverage,
    smoke fixture boundaries, construction/verifier export gaps, aggregate
    outcome/report gaps, and result-version provenance gaps. It does not
    document Figure 5 exhibit mapping, visual artifact paths/hashes,
    before/after values, previous-best sources, rendering parameters, source
    Colab cells/artifacts, or verifier links.
  - Required result: when Figure 5 exhibit provenance lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes family/aggregate constructive-math coverage from reproduced
    paper figures and exhibit-level visual evidence.

- [ ] Keep README Figure 5 sum-of-radii value wording scoped until
      source-specific precision provenance exists.
  - Spec evidence: AlphaEvolve Figure 5 displays a sum-of-radii improvement
    `2.6340 -> 2.6358`, while Appendix B.12 and Figure 14 state the `n = 26`
    unit-square circle-packing result as `2.634` to `2.635`.
  - Current evidence: README can point to broad Figure 5 exhibit and
    B.12-B.13 packing TODOs, but it does not warn that the same visible result
    currently has source-specific display precision. Existing wording follows
    the Appendix B.12 `2.635` value and does not preserve the Figure 5
    `2.6358` display.
  - Required result: when source-specific precision provenance lands, update
    README, ROADMAP, papers index, and code/paper TODOs so README records the
    Figure 5, Appendix B.12, and Figure 14 value strings separately, explains
    the rounding/canonicalization policy, and avoids treating `2.6358` and
    `2.635` as interchangeable evidence.

- [ ] Keep README Appendix B figure wording scoped until Figures 10-14
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B includes construction figures beyond
    Figure 5: Erdos minimum overlap, regular-hexagon packings,
    maximum/minimum-distance point sets, Heilbronn variants, and
    circle/rectangle packing sum-of-radii examples.
  - Current evidence: README describes Appendix B family/status coverage,
    construction/verifier export gaps, aggregate outcome/report gaps,
    result-version provenance gaps, and Figure 5 exhibit gaps. It does not
    document Appendix B Figure 10-14 mappings, subfigure labels,
    figure-caption values, visual artifact paths/hashes, rendering parameters,
    construction payloads, previous-best sources, source Colab cells/artifacts,
    or verifier links.
  - Required result: when Appendix B figure-level provenance lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes family/aggregate constructive-math coverage, main-text
    Figure 5 exhibits, and Appendix B reproduced figure evidence.

- [ ] Keep README Appendix B numeric-result wording scoped until per-result
      metric/value provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.1-B.13 reports individual
    mathematical result values with heterogeneous metric definitions,
    parameter settings, inequality directions, prior bounds, reported values,
    source citations, section/figure/caption locations, and heterogeneous
    construction representations such as step functions, coefficients, finite
    sets, coordinates, kissing configurations, and packing placements.
  - Current evidence: README describes Appendix B family/status coverage,
    construction/verifier export gaps, aggregate outcome/report gaps,
    result-version gaps, Figure 5 exhibit gaps, and Appendix B figure gaps. It
    does not document per-result rows tying every Appendix B text-level numeric
    claim to exact metric formulas, parameter tuples, upper/lower or
    maximize/minimize semantics, previous-best values and sources,
    AlphaEvolve reported values, source locations, construction-representation
    schemas, or artifact hashes.
  - Required result: when Appendix B per-result metric/value provenance lands,
    update README, ROADMAP, papers index, and code/paper TODOs together so
    README distinguishes family coverage, aggregate outcomes, figure
    reproduction, revised-result history, construction-payload evidence, and
    text-level Appendix B numeric claim evidence.

- [ ] Keep README Appendix B.1-B.3 autocorrelation wording scoped until
      step-function provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.1-B.3 reports three
    autocorrelation/autoconvolution improvements: `600` equally-spaced
    intervals on `[-1/4, 1/4]` for `C1 <= 1.5053`, `50` intervals on the same
    domain for `0.8962 <= C2`, and `400` intervals on the same domain for
    `C3 <= 1.4557`.
  - Current evidence: README now says the Appendix B registry validates
    B.1-B.3 step-function summary metadata: interval counts, common domain,
    sign policy, bound direction, previous bound/source, and reported bound.
    It still warns that the actual step-function payloads and recomputation
    certificates remain absent.
  - Required result: when Appendix B.1-B.3 autocorrelation metadata lands,
    update README, ROADMAP, papers index, and code/paper TODOs together so
    README names the three constants, step-function payload hashes, verifier
    artifacts, and recomputed values without merging them into one generic
    autocorrelation claim.

- [x] Keep README Appendix B.1-B.3 labels scoped until paper-heading
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.1-B.3 are titled `First
    autocorrelation inequality`, `Second autocorrelation inequality`, and
    `Third autocorrelation inequality`, and the constants are `C1`, `C2`, and
    `C3`. The paper does not use `k=3`, `k=4`, or `k=5` labels for these three
    autocorrelation entries.
  - Status: README now states that the Appendix B registry preserves the exact
    B.1-B.3 paper-facing labels and C1-C3 constants separately from internal
    `autocorrelation_bounds_k*` ids. The registry validator and tests reject
    missing label metadata, drifted constants, and public `k=` names.
  - Verification: `py -3.12 -m pytest tests/test_appendix_b_registry.py -q`
    passes.

- [x] Keep README Appendix B.8 ratio wording scoped until squared-ratio
      convention provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.8 reports constructions for the
    max/min pairwise-distance ratio, but the numerical values `12.889266112`
    for 16 points in 2D and `4.165849767` for 14 points in 3D are reported
    under a squared-ratio convention, with the geometric ratio obtained by a
    square-root transform.
  - Status: README now states that Appendix B.8 registry evidence preserves the
    raw squared values, square-root-derived ratios, point counts, dimensions,
    prior squared bounds, and comparison policy, while leaving coordinate
    payloads and all-pairs distance certificates open.
  - Verification: `py -3.12 -m pytest tests/test_appendix_b_registry.py -q`
    passes.

- [ ] Keep README Appendix B.8 witness wording scoped until distance
      certificates exist.
  - Spec evidence: AlphaEvolve Appendix B.8 and Figure 12 report 16 points in
    two dimensions achieving squared max/min-distance ratio `12.889266112`
    versus the prior squared bound `12.890`, and 14 points in three dimensions
    achieving squared ratio `4.165849767` versus the prior squared bound
    `4.168`.
  - Current evidence: README now points to B.8 squared-ratio convention
    metadata with point counts, dimensions, prior squared bounds, and Figure 12
    panel linkage. It also points to a `witness_certificate_boundary` that
    records required future coordinate/certificate fields and keeps both
    witnesses `not_recorded_locally`. It still warns that coordinate payloads
    and all-pairs min/max distance recomputation remain open.
  - Required result: when Appendix B.8 distance-certificate metadata lands,
    update README, ROADMAP, papers index, and code/paper TODOs together so
    README distinguishes raw convention metadata from validated point-set
    witness evidence with coordinate artifacts, recomputed distances,
    prior/current squared ratios, and Figure 12 panel linkage.

- [ ] Keep README Appendix B.5 minimum-overlap wording scoped until
      step-function provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.5 improves the Erdos
    minimum-overlap upper bound from `C5 <= 0.380927` to `C5 <= 0.380924`
    using a Figure 10 step function on `[0, 2]` with values in `[0, 1]`,
    integral normalization `integral_0^2 h(x) dx = 1`, and a shift-overlap
    objective.
  - Current evidence: README can point to broad Appendix B per-result and
    Figure 10 visual gaps, but it does not separately warn that B.5 needs
    domain/value-range, normalization, objective recomputation, prior-bound,
    improved-bound, and construction-payload evidence before quoting the
    minimum-overlap result.
  - Required result: when Appendix B.5 minimum-overlap metadata lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    names the domain, normalization, step-function payload, objective
    certificate, prior/current bounds, Figure 10 link, and source location
    without merging B.5 into generic step-function Appendix B coverage.

- [x] Keep README Appendix B.5 source-formulation wording scoped until
      equivalence evidence exists.
  - Spec evidence: AlphaEvolve Appendix B.5 defines the source problem using
    non-negative `f,g: [-1,1] -> [0,1]`, `f + g = 1`, `integral f = 1`,
    zero extension outside `[-1,1]`, and
    `sup_{x in [-2,2]} integral_{-1}^1 f(t) g(x+t) dt`, then uses `[40]` to
    reduce the constant to an infimum over normalized step functions `h` on
    `[0,2]`.
  - Status: README now states that the Appendix B registry preserves the B.5
    source paired-function formulation, zero-extension convention,
    shift-supremum objective, known bounds, `[40]` equivalence, and mapping to
    the normalized `[0,2]` step-function formulation, while the Figure 10
    construction payload remains open.
  - Verification: `py -3.12 -m pytest tests/test_appendix_b_registry.py -q`
    passes.

- [ ] Keep README Appendix B.6 finite-set wording scoped until witness
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.6 improves the sums-and-differences
    lower bound with two finite integer-set witnesses: `U1` has size `2003`
    and gives `1.1479 <= C6`, while `U2` has size `54265` and gives
    `1.1584 <= C6`. The derivation uses the Gyarmati et al. inequality with
    `U` containing zero, `|U - U| <= 2 max(U) + 1`, and recomputed
    `|U-U|`/`|U+U|` counts.
  - Current evidence: README can point to broad Appendix B per-result
    metric/value and finite-set payload gaps, but it does not separately warn
    that B.6 needs two witness-specific records before quoting the lower-bound
    improvements.
  - Required result: when Appendix B.6 witness metadata lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README names both
    witness sets, cardinalities, feasibility checks, derived lower-bound
    values, payload hashes, and source links without collapsing the result to
    one aggregate finite-set claim.

- [ ] Keep README Appendix B.6 theorem wording scoped until admissibility
      evidence exists.
  - Spec evidence: AlphaEvolve Appendix B.6 defines `C6` via arbitrarily large
    finite sets `A` and `B`, explicit sumset/difference-set notation,
    `X << Y` and `X >> Y` constants independent of sufficiently large sets,
    `[39, Corollary 3]` for the `4/3` upper bound, `[39, Theorem 1]` for the
    lower-bound method, and a Gyarmati finite-set admissibility condition for
    non-negative integer `U` containing zero.
  - Current evidence: README can point to B.6 witness gaps, but it does not
    separately warn that theorem definitions and admissibility conditions must
    be present before presenting the witness rows as source-faithful evidence
    for `C6`.
  - Required result: when B.6 theorem-condition metadata lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README distinguishes
    theorem scope, notation, source theorem anchors, admissible-`U` checks,
    and witness arithmetic instead of treating all B.6 evidence as payload
    provenance alone.

- [ ] Keep README Appendix B.7 regular-hexagon wording scoped until packing
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.7 reports two unit-regular-hexagon
    packing improvements: `n = 11` improves the outer regular-hexagon side
    length from `3.943` to `3.931`, and `n = 12` improves it from `4.0` to
    `3.942`.
  - Current evidence: README can point to broad Appendix B per-result
    metric/value and Figure 11 visual gaps, but it does not separately warn
    that B.7 needs per-`n` geometry conventions, placement payload,
    containment/non-overlap certificates, prior/current side lengths, and
    Figure 11 panel linkage before quoting those bounds.
  - Required result: when Appendix B.7 regular-hexagon metadata lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    names both `n` values, unit/outer hexagon conventions, side-length
    improvements, certificates, Figure 11 panel links, and artifact hashes
    without merging them into one generic hexagon-packing claim.

- [ ] Keep README Appendix B.9-B.10 Heilbronn wording scoped until
      minimum-area provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.9-B.10 reports three Heilbronn
    improvements: `n = 11` points in a unit-area triangle improve the minimum
    triangle area from `0.036` to greater than `0.0365`; `n = 13` points in a
    unit-area convex region improve `0.0306` to `0.0309`; and `n = 14` points
    in a unit-area convex region improve `0.0277` to `0.0278`.
  - Current evidence: README can point to broad Appendix B per-result
    metric/value and Figure 13 visual gaps, but it does not separately warn
    that the Heilbronn results need per-parameter domain, unit-area,
    coordinate/region payload, all-triples certificate, and prior/current
    value evidence before quoting those bounds.
  - Required result: when Appendix B.9-B.10 Heilbronn metadata lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    names the three `n` values, domains, minimum-area certificates, prior and
    reported values, Figure 13 panel links, and artifact hashes without merging
    them into one generic Heilbronn claim.

- [ ] Keep README kissing-number wording scoped until Lemma 1 certificate
      evidence exists.
  - Spec evidence: AlphaEvolve Appendix B.11 derives the dimension-11 kissing
    number lower bound of 593 from 593 nonzero integral-coordinate points plus
    an exact norm/distance condition and Lemma 1's transformation into a valid
    kissing configuration.
  - Current evidence: README can describe Appendix B family/status coverage,
    construction/verifier export gaps, aggregate outcome gaps, and visual
    construction figure gaps. It does not yet document a kissing-specific
    certificate with point count, dimension, coordinate domain, exact
    norm/pairwise-distance inequalities, Lemma 1 applicability, transformed
    sphere centers, tangency/non-overlap checks, and lower-bound claim linkage.
  - Required result: when Appendix B.11 certificate provenance lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes visual Appendix B construction evidence from proof-grade
    kissing-number lower-bound verification.

- [ ] Keep README Appendix B.12-B.13 circle/rectangle wording scoped until
      sum-of-radii provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.12-B.13 reports three sum-of-radii
    improvements: `n = 26` circles in a unit square improve `2.634` to
    `2.635`, `n = 32` circles in a unit square improve `2.936` to `2.937`, and
    `n = 21` circles in a perimeter-4 rectangle improve `2.364` to `2.3658`.
  - Current evidence: README documents the checked-in `circle_packing` example
    as a fixed-26 unit-square smoke fixture, and it can point to broad
    Appendix B per-result and Figure 14 visual gaps. It does not separately
    warn that the full paper claim needs all three rows, container geometry,
    exact circle counts, containment/non-overlap certificates, sum-of-radii
    recomputation, prior/current values, and Figure 14 panel linkage.
  - Required result: when Appendix B.12-B.13 packing metadata lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    names all three `n`/container rows, certificates, sum-of-radii values,
    Figure 14 panel links, and artifact hashes while keeping the 26-circle
    smoke fixture out of full AlphaEvolve evidence claims.

- [ ] Keep README Appendix B result wording scoped until revised-result
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.4 records a result revision for the
    uncertainty inequality: the text first reports `C4 <= 0.3521`, then notes
    a post-first-version refinement after Henry Cohn's observation that
    improved the reported constant to `0.3216`.
  - Current evidence: README describes the Appendix B registry as family/status
    coverage plus missing construction-data and verifier-code exports. It does
    not mention result revisions, superseded constants, source manuscript
    version, update attribution, or verifier artifacts for revised mathematical
    values.
  - Required result: when Appendix B result-version rows and validators land,
    update README, ROADMAP, papers index, and code/paper TODOs together so
    README does not imply the family registry is enough to reproduce current
    AlphaEvolve Appendix B constants or accidentally mix stale and revised
    bounds.

- [ ] Keep README Appendix B.4 prior-bound wording scoped until rounding
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.4 frames the uncertainty-inequality
    result against prior work as `0.2025 <= C4 <= 0.3523`, while noting that
    reference `[33]` states the upper bound as `0.353` and that rounding the
    referenced solution to the fourth digit gives `0.3523`. AlphaEvolve's
    first-version `C4 <= 0.3521` result is compared against that rounded
    baseline.
  - Current evidence: README can describe Appendix B family/status coverage,
    construction/verifier export gaps, revised-result gaps, Hermite-certificate
    gaps, and B.4 similarity-interpretation gaps. It does not separately warn
    that prior-bound claims need source-linked evidence for the stated
    `[33]` value, the fourth-digit rounding caveat, the lower-bound context,
    and the exact comparison baseline.
  - Required result: when B.4 prior-bound rounding metadata and validators
    land, update README, ROADMAP, papers index, and code/paper TODOs together
    so README distinguishes the prior `0.353` statement, the rounded `0.3523`
    comparison baseline, AlphaEvolve's `0.3521` first-version bound, the later
    `0.3216` revision, and the separate Hermite certificate evidence.

- [ ] Keep README Appendix B.4 numeric wording scoped until Hermite-polynomial
      certificate evidence exists.
  - Spec evidence: AlphaEvolve Appendix B.4 derives the `C4 <= 0.3521`
    uncertainty-inequality bound from a Hermite-polynomial test function,
    approximate coefficients `[0.32925, -0.01159, -8.9216e-5]`, the largest
    positive root of `P(x)/x^2`, and the formula `r_max^2 / (2*pi)`.
  - Current evidence: README can describe Appendix B family/status coverage,
    construction/verifier export gaps, revised-result gaps, and B.4
    similarity-interpretation gaps. It does not document B.4 coefficient
    payloads, Hermite-basis identities, root computation, sign/condition
    checks, bound recomputation, or artifact hashes for the actual `C4`
    certificate.
  - Required result: when B.4 Hermite certificate metadata and validators land,
    update README, ROADMAP, papers index, and code/paper TODOs together so
    README distinguishes the quoted uncertainty-inequality value from verified
    polynomial/root evidence, result-version history, and qualitative
    near-optimality interpretation.

- [ ] Keep README Appendix B.4 interpretation wording scoped until
      prior-construction similarity evidence exists.
  - Spec evidence: AlphaEvolve Appendix B.4 says the uncertainty-inequality
    construction found by AlphaEvolve is qualitatively very similar to the one
    in reference `[33]`, and presents that similarity as empirical support for
    the prior hypothesis that the construction is nearly optimal.
  - Current evidence: README can point to Appendix B numeric-value,
    coefficient, construction/verifier, and revised-result gaps. It does not
    separately warn that B.4's interpretation claim needs source-linked
    comparison evidence before README characterizes the result as supporting a
    near-optimality hypothesis.
  - Required result: when Appendix B.4 comparison metadata lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes the reported `C4` numeric bound from qualitative similarity
    to prior work and from any claim that the construction is nearly optimal.

- [ ] Keep README feedback-calibration wording scoped to report contracts
  versus executed calibration experiments.
  - Spec evidence: AlphaEvolve-style feedback and reviewer channels need
    calibrated evidence from real reviewer/task suites and ablations, not only
    validators for declared calibration records.
  - Current evidence: README now says
    `libreevolve.llm_feedback_calibration.v1` validates declared graders,
    at least two calibrated tasks for readiness, per-grader/task scored
    records, normalized expected/observed scores, exact absolute-error
    consistency, and declared calibration artifacts. It also says the
    artifact-inventory contract verifies calibration report, raw-record,
    grader-config, and plot artifacts under a safe root, and that the current
    code does not run feedback-grader calibration experiments. Matching
    roadmap/paper/code TODOs still require real feedback-calibration fixtures
    and grader ablation reports.
  - Required result: when runtime fixtures or benchmark scripts emit real
    feedback-calibration reports, reviewer/task suites, or grader ablation
    evidence, update README, ROADMAP, papers index, and code/paper TODO entries
    together so README neither underclaims the report and inventory contracts
    nor overclaims executed AlphaEvolve-style calibration evidence.

- [ ] Keep README qualitative-feedback wording scoped until calibration and
      prompt-history audits exist.
  - Spec evidence: AlphaEvolve Section 2.4 says LLM-generated feedback can
    grade hard-to-code properties such as simplicity and either add them as
    scores or discard candidates when a criterion is not fulfilled.
  - Current evidence: README documents optional LLM feedback graders plus
    qualitative policy fields, retained `qualitative_policy` records, and
    `runtime.history.qualitative_feedback_policy_report`. It should not imply
    AlphaEvolve-style qualitative feedback quality until calibration/task-suite
    linkage and prompt-history audits exist.
  - Required result: when calibration/task-suite and prompt-history audit
    evidence lands, update README, ROADMAP, papers index, and code/paper TODOs
    together so README distinguishes declared hard-to-code criteria from
    validated qualitative feedback such as simplicity.

- [ ] Keep README provider-cancellation wording scoped to timeout policy and
  observation evidence versus live hard cancellation.
  - Spec evidence: AlphaEvolve-scale runs need bounded provider latency,
    attributable stop behavior, and cancellation semantics that prevent stalled
    model calls from blocking long budgeted experiments.
  - Current evidence: README now says
    `libreevolve.provider_cancellation_policy.v1` validates provider
    request-timeout, ensemble-deadline, runtime-deadline, and hard-cancel
    policy rules by role, including artifact requirements and hard-cancel
    readiness gated on cancellation-record evidence. It also says runtime
    manifests currently scope provider timeout/deadline rules to active LLM
    role surfaces and attach scheduler-derived timeout/quarantine observations,
    but that this is policy and observation evidence only. The README further
    says provider SDK hard cancellation and timeout-driven stop enforcement
    remain runtime work, and that artifact inventory proves named cancellation
    evidence files exist rather than proving in-flight SDK calls can be
    hard-cancelled.
  - Required result: when live provider SDK cancellation, timeout-driven
    stop-run behavior, richer timeout/cancellation artifacts, or cross-run
    quarantine/resume proof lands, update README, ROADMAP, papers index, and
    code/paper TODO entries together so README neither underclaims current
    timeout-policy evidence nor overclaims AlphaEvolve-style hard cancellation.

- [ ] Keep README validator sandbox/resource-limit wording scoped to local
  subprocess audit evidence versus OS/container enforcement.
  - Spec evidence: AlphaEvolve-scale systems and codebase experiments need
    trustworthy execution isolation, filesystem capability boundaries, network
    egress control, and resource quotas when evaluating generated code.
  - Current evidence: README now says validator execution records expose
    `libreevolve.validator_execution_policy.v1`,
    `evaluation.metadata.validator_boundary`, `filesystem_capabilities`, and
    `resource_limit_policy` with local-subprocess execution,
    `security_sandbox: "unsupported"`, `container: "unsupported"`, Python
    socket-denial metadata when configured, wall-clock-only timeout policy,
    unsupported CPU/memory/GPU/disk/process-count quotas, and a
    minimal-environment/redacted-diagnostic secret boundary. The README also
    says the filesystem and resource records are audit evidence for the current
    local runner, not an OS/container security sandbox. Matching code/paper
    TODOs still require configurable sandbox/container enforcement,
    OS/container-grade network egress isolation, OS-enforced filesystem
    capability policy, CPU/memory/GPU/disk/process quotas, and distributed
    evaluator worker state.
  - Required result: when real sandbox/container, filesystem capability,
    network isolation, or resource-quota enforcement lands, update README,
    ROADMAP, papers index, and code/paper TODO entries together so README
    neither underclaims the current manifest-visible boundary audit nor
    overclaims AlphaEvolve-grade execution isolation.

- [ ] Keep README validator-boundary consistency wording scoped to CLI
  artifact validation until promotion/finalization enforcement exists.
  - Spec evidence: README-facing AlphaEvolve alignment should distinguish
    manifest-visible audit fields from automated verification over the run
    artifacts used to justify discoveries.
  - Current evidence: README says startup manifests record
    `policies.validator_execution`, the
    `validate_validator_boundary_consistency.v1` contract, and
    `validate_run_artifact_validator_boundary_consistency()` for scanning
    manifest-backed `history.jsonl` and `failure_history.jsonl` rows. README
    also states that `libreevolve show` invokes this artifact check and fails
    missing, legacy, or drifting boundary evidence with stream/line diagnostics.
  - Required result: when run-finalization, CI, or release-artifact promotion
    enforcement lands, update README, ROADMAP, papers index, and code/paper TODO
    entries together so README distinguishes the current CLI inspection gate
    from automatic artifact-promotion enforcement and from stronger OS/container
    sandboxing.

- [ ] Keep README and agent-facing OpenAI API-mode wording aligned with adapter
  routing.
  - Spec evidence: AlphaEvolve-style runs should make provider request
    surfaces explicit enough for reproducibility; local docs should not imply a
    different API route than the configured adapter will use.
  - Current evidence: README correctly states that OpenAI defaults to Chat
    Completions and uses Responses API when `api_mode: responses` or
    `reasoning_effort` is configured. `OpenAIBackend` resolves explicit
    `api_mode: responses` without reasoning into Responses mode, while
    `api_mode: auto` without reasoning preserves Chat Completions. `AGENTS.md`
    has been updated to match that boundary.
  - Required result: when OpenAI API-mode routing, supported request
    parameters, or static compatibility checks change, update README,
    `AGENTS.md`, code TODOs, and paper TODOs together so docs neither
    underclaim explicit Responses support nor overclaim live provider
    capability discovery.

- [ ] Keep README provider capability lookup wording scoped to static local
  validation versus live model-registry evidence.
  - Spec evidence: AlphaEvolve-scale model orchestration should preserve enough
    provider/account capability evidence to explain which backend model ids and
    API modes were available for a run, especially as provider registries,
    service API versions, and account entitlements change.
  - Current evidence: README says LibreEvolve forwards configured model strings
    to provider SDKs, validates only manifest-safe identifier syntax/secret
    shape, records `policies.provider_capability_lookup`, and performs no live
    model-registry, service/API-version, or account-availability lookup before
    the run. Code and paper TODO entries already scope the remaining provider
    auth gap to live authenticated request/model-registry validation rather
    than credential-presence and local client-construction preflight.
  - Required result: when live provider model-registry discovery,
    service/API-version capture, account-availability validation, or provider
    capability evidence lands, update README, ROADMAP, papers index, and
    code/paper TODO entries together so README neither underclaims the current
    static manifest policy nor overclaims AlphaEvolve-grade provider
    reproducibility evidence.

- [ ] Keep README paper-inspired plugin claims scoped to approximation status.
  - Spec evidence: citing CausalEvolve, DeepEvolve, ImprovEvolve,
    ThetaEvolve, GigaEvo, CodeEvolve, or MadEvolve should not imply faithful
    reproduction unless paper-specific behavior is implemented.
  - Current evidence: README says built-in plugins are paper-inspired
    approximations, not full reproductions; it labels CausalEvolve as
    token-pattern outcome-factor guidance, DeepEvolve as pluggable
    arXiv/web-search context, ImprovEvolve as modular decomposition prompting,
    and ThetaEvolve as clipped-reward JSONL export, not training. The README
    paper table also marks GigaEvo and CodeEvolve as inspiration only and
    MadEvolve as background context.
  - Required result: when paper-specific plugin/framework behavior lands,
    update README, ROADMAP, papers index, code TODO, and paper TODO entries
    together so the README neither underclaims current approximation metadata
    nor overclaims faithful paper implementations.

- [ ] Keep README custom-plugin provenance claims scoped to entry-point specs
  versus direct instances.
  - Spec evidence: AlphaEvolve-grade plugin extensibility should make custom
    hook code and configuration reproducible without hiding arbitrary
    constructor state.
  - Current evidence: README now documents entry-point plugin specs with
    manifest-safe or declared-schema constructor options, paper-inspiration
    labels, distribution name/version and hash metadata, while direct custom
    plugin instances record constructor signature shape only and explicitly
    exclude constructor values and instance attributes.
  - Required result: once direct custom plugin registries, safe constructor
    value/schema attribution, or richer package provenance land, update README
    and matching code/paper TODO entries so the README neither underclaims
    entry-point provenance nor overclaims direct-instance replayability.

- [ ] Keep README proposal-memory claims scoped to bounded heuristic proposal
      scoring.
  - Spec evidence: AlphaEvolve-style evolutionary memory should be able to
    reuse prior proposal ideas, rationales, and hypotheses through scored and
    semantically searchable idea memory.
  - Current evidence: README now documents `runtime.history.hypothesis_index`
    as bounded redacted proposal `idea`/`rationale`/`hypothesis` summaries for
    valid programs that can feed current-run `resurfacing_index`, plus
    `runtime.history.proposal_score_report` as bounded current-run outcome/
    exact-novelty score records. README should not imply semantic proposal
    retrieval, calibrated proposal-quality models, cross-run hypothesis tables,
    or score-driven prompt/archive selection.
  - Required result: once semantic/cross-run proposal indexes, calibrated
    proposal-quality models, or stricter score/field influence policy lands,
    update the README and matching code/paper TODO entries together so the
    README neither underclaims current proposal scoring nor overclaims
    AlphaEvolve-grade idea memory.

- [ ] Keep README scientific-discovery wording scoped to automated evaluators
      until robust evaluator-environment fixtures exist.
  - Spec evidence: AlphaEvolve states that automated evaluation is a core
    advantage and limitation: tasks requiring manual experimentation are out
    of scope, and LLM-provided evaluation of ideas is possible but not the
    optimized setting. The paper's future bridge is high-level idea feedback
    before transitioning to an implementation stage with machine feedback
    through code execution. The Discussion also says future high-value
    discoveries depend on setting up more problem environments with robust
    evaluation functions.
  - Current evidence: README describes automated algorithm discovery, local
    subprocess evaluators, staged validator cascades, optional LLM feedback,
    proposal metadata, and `runtime.history.automated_evaluator_scope_report`,
    which states the AlphaEvolve scope boundary for machine-gradeable tasks
    versus manual-experiment scientific workflows or pre-code LLM-only idea
    review. It still does not describe evaluator-environment readiness evidence
    such as robust evaluator design, automatable-domain boundaries, setup
    effort, and expected discovery value.
  - Required result: once robust environment fixtures and transition policies
    exist, update README, ROADMAP, papers index, and matching TODOs so public
    wording neither underclaims the current executable-evaluator workflow nor
    overclaims environment-scaling, manual-experiment, or
    AI-Co-Scientist-style idea-feedback support.

- [ ] Keep README AI-Co-Scientist comparison scoped until measurement and
      bridge evidence exists beyond the current representation-boundary report.
  - Spec evidence: AlphaEvolve Related Work says AI Co-Scientist represents
    hypotheses and evaluation criteria in natural language, whereas
    AlphaEvolve evolves code and uses programmatic evaluation functions. The
    paper says this choice helps sidestep LLM hallucinations and sustain many
    evolution time steps, while a future system could combine natural-language
    and programmatic idioms.
  - Current evidence: README now describes
    `runtime.history.programmatic_representation_boundary_report`, which
    separates executable generated candidates from natural-language proposal
    metadata and records declared evaluator metrics plus deterministic
    evaluator validity as programmatic criteria. README also states that the
    report does not measure hallucination resistance, prove long-horizon
    evolution, or implement a bridge from language-only idea stages into
    executable candidate evaluation.
  - Required result: when hallucination-risk measurements, long-horizon
    evidence, or natural-language-to-programmatic bridge contracts land, update
    README, ROADMAP, papers index, and code/paper TODOs together so README does
    not overclaim those properties from generic proposal metadata alone.

- [ ] Keep README Related Work positioning scoped until taxonomy evidence
      exists.
  - Spec evidence: AlphaEvolve Related Work presents the system as
    execution-feedback code superoptimization and programmatic scientific
    discovery, compares it with pre-LLM superoptimization, AlphaTensor,
    GPU-kernel and LLM-agent optimizers, AI-for-science systems, and proof
    search, emphasizes programmatic hypothesis representations, programmatic
    evaluation metrics, and witness/counterexample discovery, and treats
    continuous LLM fine-tuning through reinforcement learning plus
    LLM-directed concept learning/summaries of high-performing programs as
    adjacent complementary ideas rather than established AlphaEvolve
    components.
  - Current evidence: README can list bundled papers, mention inspirations,
    and document specific implemented or missing features. It does not yet
    expose a related-work taxonomy that maps sources to method families,
    candidate representation, evaluator/evidence mode, discovery stage,
    proof-versus-witness status, comparison claim, complementary-mechanism
    status, and local implementation status.
  - Required result: when Related Work taxonomy records land, update README,
    ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes source availability and broad inspiration from
    AlphaEvolve-style positioning claims about superoptimization,
    programmatic discovery, proof/witness scope, adjacent fine-tuning or
    concept-learning mechanisms, and local capability.

- [ ] Keep README cascade wording scoped to staged threshold gates until
      statistical hypothesis-test promotion is implemented.
  - Spec evidence: AlphaEvolve Section 2.4 presents evaluation cascades as
    hypothesis testing: candidates are tried on small-scale tests before main
    test cases, and only sufficiently promising candidates advance. Section
    3.1 uses multiple randomized initializations for matrix tensor targets.
  - Current evidence: README describes cascade evaluation, staged validators,
    samples, retries, thresholds, stage/sample budgets, and prompt-visible
    diagnostics. README now also documents
    `runtime.history.cascade_hypothesis_test_policy_report`, which records
    configured or fallback-inferred small-scale/main-test roles, observed promotion counts,
    configured sample/seed counts, and the supported opt-in
    `one_sided_lower_confidence_bound` gate with retained observations,
    confidence-bound evidence, p-values, and `hypothesis_test_not_met`
    rejection. README also documents optional sequential stopping after
    `min_samples` plus optional normal-approximation `error_budget` evidence
    for configured false-promotion and false-rejection rates. README now also
    documents `binomial_success_rate` gates for Wilson-bound repeated-seed
    pass/fail evidence.
  - Required result: when richer statistical cascade promotion execution lands,
    update README, ROADMAP, papers index, and code/paper TODOs so README
    distinguishes the current lower-confidence-bound gate from complete
    AlphaEvolve-style hypothesis-testing cascades.

- [ ] Keep README mutation-response wording scoped beyond bounded
      natural-language preamble capture.
  - Spec evidence: AlphaEvolve Figure 3(c) shows explanatory natural-language
    text before a SEARCH/REPLACE diff example.
  - Current evidence: README documents that leading explanatory preambles are
    accepted before structured mutation markers and captured in bounded,
    redacted metadata through `runtime.history.natural_language_preamble_report`.
    It also says prose between or after mutation sections remains rejected.
  - Remaining gap: README still needs to stay scoped as future work adds
    configurable preamble policies, raw full-replacement disambiguation,
    rationale-quality scoring, or cross-run proposal-memory joins.
  - Required result: when any of those broader preamble features land, update
    README, ROADMAP, papers index, and code/paper TODOs together with the exact
    parser boundary and provenance behavior.

- [ ] Keep README prompt-example wording scoped beyond built-in normalized and
      skeleton copy signals.
  - Spec evidence: AlphaEvolve Figure 3(b,c) uses concrete current-program
    context and concrete SEARCH/REPLACE examples to communicate the edit
    contract.
  - Current evidence: README notes that concrete diff examples reduce observed
    placeholder-copying mistakes. README now cites
    `runtime.history.prompt_example_copy_report`, which inventories built-in
    mutation-format example sentinels and records exact, normalized
    file-section-region, and example-format skeleton signals with candidate
    status/admission metadata.
  - Remaining gap: the report is diagnostic-only and still lacks configurable
    rejection, custom prompt-template example inventories, and broader
    semantic/renamed copy detection.
  - Required result: when stronger copy-detection policy lands, update README,
    ROADMAP, papers index, and code/paper TODOs with configurable rejection,
    semantic/renamed copy detection, and custom prompt-template inventories so
    README can distinguish useful concrete examples from full
    AlphaEvolve-style current-program edit fidelity.

- [ ] Keep README multi-edit consistency wording scoped beyond current
      diagnostic scan.
  - Spec evidence: AlphaEvolve Figure 3(b) includes a SEARCH/REPLACE prompt
    rule requiring proposed edits to be consistent with each other, for
    example adding a config variable when another replacement references it.
  - Current evidence: README documents
    `runtime.history.mutation_consistency_report` as a current-run diagnostic
    for multi-edit payloads, changed edit units, co-change links, best-effort
    Python symbol/reference scans, unresolved references, evaluator status,
    and archive admission. It also says the report is not a semantic proof or
    archive gate.
  - Remaining gap: README must stay scoped until language-aware scope/import
    resolution, config/resource companion-edit models, required-link
    inference, benchmark-calibrated consistency taxonomy, and optional gating
    exist.
  - Required result: when broader consistency analysis lands, update README,
    ROADMAP, papers index, and code/paper TODOs with the exact analyzer scope
    and acceptance policy.

- [ ] Keep README Figure 3 supervised-learning example wording scoped until
      exhibit provenance exists.
  - Spec evidence: AlphaEvolve Figure 3 presents a supervised-learning pipeline
    example with linked subfigures for a user-provided JAX/Jaxline file and
    `evaluate` function, an assembled prompt with prior/current program scores,
    and an LLM output containing explanatory prose plus SEARCH/REPLACE edits.
  - Current evidence: README documents evolve-block parsing, prompt context,
    SEARCH/REPLACE mutation, strict prose handling, and prompt-example-copy
    gaps. It does not document Figure 3 exhibit IDs, subfigure labels, exact
    source/prompt/output excerpt artifact hashes, displayed score values,
    omitted-line/ellipsis policy, source PDF/caption location, rendered
    artifact paths/hashes, or links from the displayed example to prompt
    history, evaluator, candidate, and run artifacts.
  - Required result: when Figure 3 exhibit provenance lands, update README,
    ROADMAP, papers index, and matching TODOs so README distinguishes
    reproduced supervised-learning paper-example evidence from generic
    prompt/mutation/evaluator feature support.

- [ ] Keep README mutation-mode wording scoped to configured `diff`/`full`
      support versus adaptive prompting.
  - Spec evidence: AlphaEvolve Section 2.3 requests diff blocks for larger
    codebases and direct full-code output when code is very short or a rewrite
    is more suitable.
  - Current evidence: README correctly says LLM mutations use SEARCH/REPLACE
    diffs by default and full-block/full-code replacements when
    `mutation_mode: full` is configured. It should not imply that LibreEvolve
    currently chooses that output contract per candidate size, workspace shape,
    or prior failure mode.
  - Required result: when adaptive mutation-mode selection lands, update
    README, ROADMAP, papers index, and code/paper TODOs with the selection
    policy, per-candidate telemetry, and examples that prove diff prompts and
    full-rewrite prompts are selected under documented AlphaEvolve-style
    conditions.

- [ ] Keep README mutation-operator wording scoped until operator-family
      construction evidence exists beyond the current boundary report.
  - Spec evidence: AlphaEvolve Section 2.3 uses structured edit payloads, but
    Related Work distinguishes AlphaEvolve from evolutionary systems that need
    a handwritten set of mutation or crossover operators.
  - Current evidence: README now describes
    `runtime.history.mutation_operator_boundary_report`, which records fixed
    local parser/edit surfaces, configured run-wide mutation mode, observed
    payload surfaces, and the current `claim_ready: false` boundary for
    LLM-constructed operator families and adaptive strategy selection.
  - Required result: when mutation-operator construction policy lands, update
    README, ROADMAP, papers index, and code/paper TODOs with proposal-level
    operator-family provenance, adaptive selection/construction evidence,
    operator-family scoring, and benchmark telemetry before README implies
    AlphaEvolve-style replacement of handwritten mutation operators.

- [ ] Keep README creative-generation wording scoped until semantic proposal-
      diversity evidence exists beyond exact duplicate counts.
  - Spec evidence: AlphaEvolve Section 2.3 says SOTA LLMs digest previous
    solutions and propose new, diverse ways to improve them, while Section 4
    ablations connect stronger underlying LLMs to better performance.
  - Current evidence: README now describes
    `runtime.history.proposal_diversity_report`, including exact proposal and
    idea hash uniqueness/duplicate counts by generation and proposal batch. It
    also states that near-duplicate detection, idea-family classification,
    semantic novelty, model-quality attribution, and benchmark linkage remain
    future work.
  - Required result: when semantic proposal-diversity reporting lands, update
    README, ROADMAP, papers index, and code/paper TODOs with per-call or
    per-batch idea/operator-family labels, parent/inspiration relations,
    prompt/backend model ids, near-duplicate diagnostics, code and semantic or
    task-output distance measures where available, accepted/rejected outcomes,
    novelty contribution, and equal-budget/model ablation linkage.

- [ ] Keep README database-output claims scoped to prompt-visible output
      capture versus queryable output indexes.
  - Spec evidence: AlphaEvolve's evolutionary database stores generated
    solutions with evaluation results and program outputs attached, then
    resurfaces useful prior ideas in later generations.
  - Current evidence: README can describe strict evaluator `outputs` /
    `program_output` capture, redaction, truncation, stage output checks, and
    bounded prompt-visible program-output summaries. It should not imply those
    outputs are yet indexed as a durable database dimension or used for
    output-similarity/query-based resurfacing.
  - Required result: when `program_output_index` records, output-aware
    resurfacing APIs, durable output query tables, or semantic output
    retrieval land, update README, ROADMAP, papers index, and code/paper TODO
    entries together so README distinguishes prompt-visible program outputs
    from AlphaEvolve-style queryable output-attached database evidence.

- [ ] Keep README database-memory wording scoped until duplicate-work cache is
      durable and cross-run.
  - Spec evidence: AlphaEvolve's database stores generated solutions with
    attached evaluations and is meant to resurface previously explored ideas
    under fixed compute budgets.
  - Current evidence: README can describe deterministic candidate ids,
    candidate history, workspace hashes, unique program-id validation,
    current-run resurfacing views, and
    `runtime.history.duplicate_work_policy_report`, which reports duplicate
    workspaces plus run-local evaluator cache stores/hits for diff-error-free
    exact workspace matches. README can say cache hits reuse evaluator results
    under canonical workspace plus evaluator-contract keys and avoid evaluator-
    call budget, but it should not imply durable cross-run database memory,
    semantic near-duplicate handling, or resume-spanning cache replay.
  - Required result: when durable source/workspace deduplication or cross-run
    evaluation-cache reuse lands, update README, ROADMAP, papers index, and
    code/paper TODOs with cache storage scope, invalidation/migration policy,
    stochastic re-evaluation semantics, replay behavior, and source/output-
    aware duplicate indexes.

- [ ] Keep README database-sampling wording scoped until calibrated sampling-
      balance comparisons exist.
  - Spec evidence: AlphaEvolve's database balances exploration and
    exploitation while resurfacing previously explored ideas.
  - Current evidence: README can describe configurable `explore_ratio`,
    `mixed` parent selection, explicit parent/inspiration strategies, selected
    parent/inspiration metadata, MAP-Elites cells, island pools, metric/frontier
    sampling, lineage sampling, novelty sampling, recency sampling, bounded
    current-run resurfacing, and `runtime.history.sampling_balance_report` with
    aggregate parent/inspiration decision counts. It should not imply that
    these knobs have been calibrated or measured as an AlphaEvolve-style
    exploration/exploitation balance.
  - Required result: when calibrated sampling-balance comparisons land, update
    README, ROADMAP, papers index, and code/paper TODO entries with fallback
    and source-pool provenance, selected-program repetition,
    island/cell/metric/lineage/descriptor coverage, score-improvement versus
    diversity effects, and equal-budget comparisons across exploit, explore,
    mixed, metric, frontier, and lineage variants.

- [ ] Keep README discovery-distance wording scoped until functional
      initial-pool divergence evidence exists.
  - Spec evidence: AlphaEvolve's introduction says evolution can discover
    candidates substantially different from the initial candidate pool in both
    syntax and function.
  - Current evidence: README now describes
    `runtime.history.initial_pool_divergence_report`, which compares generated
    candidates against generation-0 seed programs with canonical workspace
    hashes, bounded primary-file text distance, changed-component summaries,
    and numeric metric L1 distance over shared metric names. It should not
    imply task-specific functional-distance proof or "substantially different"
    discovery-distance readiness.
  - Required result: when task-specific functional-distance evidence lands,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    with behavior/output-distance metrics, evaluator-output artifacts,
    substantially-different thresholds, and benchmark-level telemetry.

- [ ] Keep README/AGENTS failure-memory claims scoped to run-local diagnostics.
  - Spec evidence: AlphaEvolve-style repeated-mutation avoidance should be able
    to reuse failed-proposal evidence across runs through durable, searchable,
    and semantically meaningful memory rather than only bounded display
    snippets.
  - Current evidence: README documents `failure_history.jsonl`,
    `load_failure_history_records()`, persisted failure fingerprints,
    repetition counts, and diagnostic-only mutation payload replay policy.
    Prompt context policy supports `recent_failure_limit`, selection modes,
    required/excluded error labels, changed files, stage names, text terms,
    repetition/score thresholds, and per-field caps. Runtime manifests include
    a bounded failure index grouped by fingerprint/repetition/recency.
    `AGENTS.md` now scopes this as persisted run-local failure diagnostics and
    bounded prompt-visible failure memory, not durable cross-run semantic
    failed-proposal memory.
  - Required result: when cross-run failure tables, semantic failed-proposal
    retrieval, learned repetition avoidance, replayable failed-mutation
    payloads, or durable failure-aware sampling policies land, update README,
    AGENTS.md, ROADMAP, papers index, and code/paper TODO entries together so
    docs neither underclaim current run-local failure memory nor overclaim
    AlphaEvolve-grade failed-proposal memory.

- [ ] Keep README meta-prompt context-policy wording scoped to validated
  current fields.
  - Spec evidence: AlphaEvolve-style meta-prompt evolution should improve
    prompt instructions and context policy, not only mutate whole prompt text
    or a fixed subset of locally known rendering controls.
  - Current evidence: README now documents prompt-program selection, scoring,
    lineage, prompt-history replay, rejected mutation diagnostics, bounded
    meta-prompt evidence, accepted JSON meta-prompt responses with optional
    `context_policy`, and validated `libreevolve.prompt_context_policy.v1`
    controls for optional channels, section priorities, mutation-instruction
    variants, parent-code selection/filtering/ranking/caps/truncation,
    proposal metadata enablement, feedback subsection selection/order/caps,
    inspiration sampling controls, and related diagnostics. It also documents
    `validate_meta_prompt_context_policy_capabilities()` checking the
    meta-prompt-visible capability map against the current structured policy
    fields.
  - Required result: when prompt-program policy can control retrieval or
    summarization behavior, learned/semantic context selection, arbitrary
    instruction channels, broader per-role retention, or other prompt surfaces
    beyond the currently validated field set, update README, ROADMAP, papers
    index, and code/paper TODO entries together so README neither underclaims
    current structured policy mutation nor overclaims full AlphaEvolve-grade
    prompt evolution.

- [ ] Keep README prompt-template compatibility and duplicate-arm wording
  scoped to current mutation-template validation.
  - Spec evidence: AlphaEvolve-style prompt evolution should distinguish
    prompt-template compatibility for each model-call role from generic
    mutation-template rendering checks, and should make duplicate prompt-arm
    semantics explicit.
  - Current evidence: README documents prompt-program selection, scoring,
    lineage, history replay, invalid-mutation diagnostics, configured
    `prompt_variant_semantic_policy`, stochastic `prompt_format_options`, and
    duplicate configured/evolved prompt templates retained as separate prompt
    arms with deterministic ids and `template_sha256` audit identity. Code
    validates known placeholders, dry-run formatting, AlphaEvolve-style
    configured mutation channels, and parent-placeholder retention for evolved
    children, but does not implement role-specific compatibility policy or
    prompt-program text deduplication.
  - Required result: when role-specific prompt-template compatibility,
    prompt-program deduplication, or an explicit validated no-dedup policy
    lands, update README, ROADMAP, papers index, and code/paper TODO entries
    together so README neither underclaims current template validation nor
    overclaims AlphaEvolve-grade prompt-policy management.

- [ ] Keep README meta-prompt scoring wording scoped to absolute/improvement
  reward modes and UCB-style prompt-arm selection.
  - Spec evidence: AlphaEvolve-style prompt evolution needs calibrated reward
    signals and ablation evidence for prompt-program lineages, not only direct
    child fitness or immediate score improvement.
  - Current evidence: README documents prompt-program selection, scoring,
    lineage, reward bounds/modes, normalized prompt reward metadata,
    reward-policy-compatible history replay, bounded prompt-performance
    evidence in meta-prompt requests, and UCB-style prompt-arm selection. Code
    currently supports `absolute` and `improvement` prompt reward modes rather
    than calibrated prompt-specific reward models or lineage ablation reports.
  - Required result: when calibrated meta-prompt rewards,
    prompt-lineage ablation reporting, or stronger prompt-policy attribution
    lands, update README, ROADMAP, papers index, and code/paper TODO entries
    together so README neither underclaims current prompt reward accounting nor
    overclaims AlphaEvolve-grade prompt evolution scoring.

- [ ] Keep README prompt-program database wording scoped to local prompt-arm
  history versus a solution-database analogue.
  - Spec evidence: AlphaEvolve Section 2.2 says meta-prompt instructions and
    context are co-evolved in a separate database analogous to solution
    programs.
  - Current evidence: README documents prompt-program selection, scoring,
    logging, duplicate-arm retention, prompt-history replay, and optional
    meta-prompt mutation. Current code implements that as a deterministic
    local prompt-arm store, not a prompt-side MAP-Elites/island database with
    descriptor/objective retention, archive events, migration/rebin semantics,
    or async/controller resume state.
  - Required result: when prompt-side archive semantics or benchmark evidence
    for a solution-database-equivalent prompt database land, update README,
    ROADMAP, papers index, and code/paper TODOs so README distinguishes the
    current prompt-history selector from AlphaEvolve's separate co-evolved
    prompt database.

- [ ] Keep README MAP-Elites descriptor claims scoped to insertion-time
  TF-IDF coordinates.
  - Spec evidence: AlphaEvolve-grade quality-diversity search should use
    task-meaningful behavior descriptors or stable learned descriptor models,
    with explicit archive compatibility when descriptors change.
  - Current evidence: README now documents that workspace complexity/diversity
    use stable text-workspace serialization, that `map_elites_descriptor_axes`
    can select configured metric/metadata axes, and that archive snapshots
    persist a `descriptor_model` with current diversity reference ids plus
    no-rebin insertion-time coordinate policy. It also says existing cells are
    not re-binned and diversity coordinates are local heuristic coordinates
    rather than stable learned descriptors.
  - Required result: once evaluator-provided behavior descriptors, learned
    descriptor models, or tested archive rebin semantics land, update the
    README and matching code/paper TODO entries together so the README neither
    underclaims descriptor-policy snapshots nor overclaims AlphaEvolve-grade
    behavior descriptors.

- [ ] Keep README island-count claims scoped to configurable defaults.
  - Spec evidence: AlphaEvolve describes an island-inspired evolutionary
    database, while LibreEvolve's local implementation exposes island count as
    configuration rather than a fixed paper-derived constant.
  - Current evidence: README now describes configurable ring-topology island
    migration with a five-island default, matching `Config.n_islands` and the
    tests that instantiate one-, two-, and three-island models.
  - Required result: when future topology or migration-policy work lands,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so the README does not imply a hardcoded five-island runtime or overclaim
    AlphaEvolve-specific island-policy fidelity.

- [ ] Keep README per-role LLM scheduler claims scoped to current role routing
  and budget maps.
  - Spec evidence: AlphaEvolve-style LLM orchestration needs role-specific
    scheduling and reward semantics for proposal generation, critique,
    feedback, and prompt improvement, not only role labels on shared telemetry.
    Its Section 2.4 model mix also uses a fast model for high-volume
    candidate generation and a stronger model for occasional higher-quality
    suggestions.
  - Current evidence: README now says `role_scheduler_state` is an
    audit/restoration record, while role routing can narrow eligible backends
    and role budget maps can stop matching roles before later calls. It also
    states that the global ensemble state remains authoritative and that
    independent per-role scheduler configuration, reward calibration, and
    quota/budget ownership remain open. README should likewise avoid implying
    that backend metadata or `throughput_depth` unit coverage proves a
    Flash/Pro-style fast-breadth plus strong-depth scheduling policy.
  - Required result: once independent per-role live scheduler state, calibrated
    reward semantics, quota/budget ownership, and experiment-backed fast/
    strong model-mix scheduling land, update the README and matching
    code/paper TODO entries together so the README neither underclaims current
    role-scoped backend eligibility nor overclaims AlphaEvolve-style role or
    model-mix scheduling.

- [ ] Keep README provider claims explicit about missing Google/Gemini
      first-class support.
  - Spec evidence: AlphaEvolve's published model mix uses Gemini 2.0 Flash and
    Gemini 2.0 Pro for fast/strong scheduling.
  - Current evidence: README can accurately describe OpenAI, Anthropic,
    Ollama, and custom backend support, but the built-in registry does not
    include a Google/Gemini backend. A custom backend is not the same as
    first-class provider telemetry, credential preflight, capability evidence,
    or Flash/Pro lane labeling.
  - Required result: if Gemini support or an equivalent provider-plugin
    contract lands, update README, ROADMAP, papers index, and code/paper TODOs
    so provider claims distinguish generic extensibility from reproducing or
    deliberately substituting AlphaEvolve's Gemini Flash/Pro ensemble.

- [ ] Keep README parallelized-evaluation wording scoped until compute-hour
      throughput reports exist.
  - Spec evidence: AlphaEvolve Section 2.4 says individual candidate
    evaluations can consume roughly 100 compute-hours and should be
    parallelized so slow evaluator wall-clock time does not prevent several
    consecutive mutations.
  - Current evidence: README can describe the synchronous loop,
    `proposals_per_generation` sequential sibling batches, staged samples and
    retries, stage/sample wall-clock budgets, evaluator-second accounting, and
    future parallel LLM/evaluator workers. It should not imply that current
    sequential batches prove evaluation-cluster fan-out, compute-hour
    accounting, or preserved mutation-chain depth under expensive evaluation.
  - Required result: when parallelized-evaluation reports land, update README,
    ROADMAP, papers index, and code/paper TODOs with per-candidate compute-hour
    budget, wall-clock duration, evaluator-worker fan-out, randomized
    initialization shard counts/seeds, queued/running/completed worker state,
    local-or-cluster execution identity, mutation-depth impact, pending-work
    resume behavior, and equal-budget report links.

- [ ] Keep README distributed-pipeline wording scoped until topology evidence
      exists.
  - Spec evidence: AlphaEvolve Section 2.6 describes an asynchronous pipeline
    composed of a controller, LLM samplers, and evaluation nodes, where
    concurrent computations block on unfinished dependencies and the system is
    optimized for throughput under a computation budget.
  - Current evidence: README can document `runtime.history.controller_state`,
    controller-budget event replay, terminal drained state, and future async
    controller/worker work. Current manifests deliberately report
    `controller_model: single_process_serial_loop`, zero queued/running
    proposals or evaluations, zero in-flight LLM calls, and limitations saying
    the snapshot is not an async queue checkpoint. README now also documents
    `runtime.history.distributed_pipeline_topology_report`, which names the
    current local controller, database, configured LLM sampler backends, local
    evaluator nodes, zero queues, blocking edges, runtime-budget linkage, and
    validation overclaim guards while keeping `claim_ready: false`.
  - Required result: when async topology artifacts land, update README,
    ROADMAP, papers index, and code/paper TODOs with real queue capacities,
    dependency edges, worker role ownership/fan-out, throughput dispatch
    telemetry, pending-work checkpoints, and validation status so README
    separates local synchronous topology evidence from reproduced Section 2.6
    pipeline evidence.

- [ ] Keep README sample-efficiency claims scoped to budget telemetry until
      proposal-count evidence exists.
  - Spec evidence: AlphaEvolve Table 1 contrasts FunSearch's millions of LLM
    samples with AlphaEvolve's thousands of samples, and Section 4 ties
    performance to stronger model/full-system components under fixed compute
    budgets.
  - Current evidence: README documents logical LLM call caps, provider-attempt,
    token, configured-cost, and latency stops, sequential
    `proposals_per_generation` batches, equal-budget ablation report schemas,
    and the `Small base LLM only` registry variant. It does not document
    benchmark evidence that useful target progress is achieved in
    thousands-scale generated/evaluated proposal counts.
  - Required result: once benchmark reports track generated proposals,
    evaluated candidates, admitted/retained candidates, target hits, and
    score/target progress versus LLM sample budgets, update README, ROADMAP,
    papers index, and code/paper TODOs so README does not imply that budget
    caps or small-base labels prove AlphaEvolve-style sample efficiency.

- [ ] Keep README test-time-compute wording scoped until repeated-sampling
      baselines exist.
  - Spec evidence: AlphaEvolve's Discussion says the evolutionary procedure
    enhances base-LLM capability compared with repeated sampling, sustained by
    machine feedback.
  - Current evidence: README can describe budget telemetry, generated
    candidates, archive admission, and the equal-budget ablation report
    contract with a `No evolution` variant. It does not document controlled
    repeated base-model sampling baselines with matched prompt/model/seed/
    evaluator settings, disabled evolutionary feedback, disabled
    parent/inspiration resurfacing, disabled meta-prompt updates, and
    target-progress comparisons against matching evolutionary runs.
  - Required result: when repeated-sampling baseline reports land, update
    README, ROADMAP, papers index, and code/paper TODOs so README separates
    generic LLM-call budget caps and `No evolution` labels from evidence that
    LibreEvolve's evolutionary loop improves over equal-budget repeated
    base-model sampling.

- [ ] Keep README critique-reviewer wording scoped to synchronous first/last
  valid mutation selection.
  - Spec evidence: AlphaEvolve-style critique/reviewer channels need calibrated
    signal, explicit budget policy, and robust provider isolation beyond a
    sequential mutation-replacement filter.
  - Current evidence: README now says `critique_reviewers` runs a synchronous
    bounded reviewer pool with manifest-safe reviewer names, optional prompts,
    role labels such as `critique:correctness`, existing backend routing and
    role budget telemetry, `first_valid` or `last_valid` aggregation, and
    retained `metadata.critique.reviewer_pool.reviewers[]` records with parser
    status and selected-reviewer provenance. Matching code/roadmap TODOs still
    say reviewer calls are sequential, replacement-only, and selected by
    first/last valid mutation rather than calibrated reviewer score or
    benchmarked reviewer reliability.
  - Required result: when async reviewer overlap, calibrated reviewer scoring,
    reviewer-pool ablations, stronger per-reviewer provider isolation, or
    richer reviewer-specific timeout/failure artifacts land, update README,
    ROADMAP, papers index, and code/paper TODO entries together so README
    neither underclaims the current synchronous reviewer-pool metadata nor
    overclaims AlphaEvolve-grade critique orchestration.

- [ ] Keep README LLM budget/replay claims scoped to current synchronous
  restore boundaries.
  - Spec evidence: AlphaEvolve-scale reproduction needs compute-budgeted model
    scheduling, replayable run accounting, and enough provider evidence to
    distinguish resumed controller state from replayed provider outputs. It
    also needs a clear boundary between sequential sibling proposal batches and
    any future consecutive-mutation-depth policy used to keep search deep when
    evaluator feedback is slow.
  - Current evidence: README now documents live synchronous
    provider-attempt/token/configured-cost/latency stops, restorable runtime
    budget snapshots, `controller_budget_events.jsonl` replay, and
    full-runtime restore validation. It also documents strict call-ledger
    provider-failure summaries and restorable scheduler failure-policy state,
    and it correctly states that `proposals_per_generation` is sequential
    batch sampling/accounting rather than parallel LLM/evaluator execution.
    while still marking live provider pricing/default-rate capture beyond
    configured estimates, provider-output/raw-payload replay, cross-run
    provider-failure policy proof, async/pending-work budget composition, and
    mutation-chain-depth policy for slow evaluator feedback as open.
  - Required result: once provider-output replay, async/pending-work budget
    composition, live pricing/default-rate capture beyond configured
    estimates, cross-run provider-failure quarantine/resume proof, or
    consecutive-mutation-depth control lands, update the README and matching
    code/paper TODO entries together so the README neither underclaims current
    synchronous budget replay and provider failure-policy evidence nor
    overclaims full AlphaEvolve-style replay.

- [ ] Keep README lineage replay wording scoped to loop-owned deterministic
  ids and provider-output non-replay boundaries.
  - Spec evidence: AlphaEvolve-scale ablations and repeated-seed comparisons
    need reproducible lineage records that distinguish deterministic framework
    ids from stochastic provider/plugin/validator behavior.
  - Current evidence: README now documents run-local RNG restore,
    `load_full_resume_bundle(manifest.json)`,
    `--restore-runtime-from-manifest`, `runtime.lineage_replay_policy`,
    deterministic loop-owned candidate, prompt, and LLM call id policy,
    explicit exclusion of direct `Program()` and `PromptProgram()` UUID4
    defaults from the replay contract, and the fact that replay-stable LLM call
    ids do not prove identical provider outputs. `AGENTS.md` now also states
    that `config.seed` initializes the run-local framework RNG rather than
    reseeding Python's process-global `random` module. Code TODO evidence still
    says direct UUID boundaries, plugin/provider RNG boundaries,
    provider-output replay, and end-to-end resumed-trace lineage proof remain
    open.
  - Required result: when provider/plugin output replay, direct UUID replay
    contracts, plugin/provider RNG capture, ordered migration replay, or
    resumed-trace lineage proof lands, update README, AGENTS.md, ROADMAP,
    papers index, and code/paper TODO entries together so README and
    agent-facing instructions neither underclaim current loop-owned
    deterministic id policy nor overclaim full AlphaEvolve-grade lineage
    replay.

- [ ] Keep README DeepResearch retrieval evidence scoped to bounded redacted
  sidecars and non-semantic provenance.
  - Spec evidence: retrieval-driven AlphaEvolve-style runs should identify the
    external knowledge injected into prompts while distinguishing replayable
    retained artifacts from unbounded raw provider/source availability, TLS
    transport replay, and semantic source correctness.
  - Current evidence: README now documents
    `libreevolve.retrieval_payload_artifact.v1` sidecars,
    `libreevolve.retrieval_payload_artifact_inventory.v1`,
    `libreevolve.retrieval_source_ranking_provenance.v1`,
    `libreevolve.retrieval_source_content_trust_policy.v1`,
    `libreevolve.retrieval_transport_policy.v1`,
    `libreevolve.retrieval_source_grounding_policy.v1`,
    `libreevolve.retrieval_evidence_boundary_policy.v1`,
    `libreevolve.retrieval_context_audit_policy.v1`,
    `libreevolve.retrieval_semantic_boundary_audit.v1`, and
    `libreevolve.retrieval_evidence_coverage.v1`. It states that retained
    under-budget payloads can be checked through secret-redacted sidecar
    artifacts and inventory hashes; active prompt context links to bounded
    transport, source-content, lexical-grounding, and evidence-boundary states;
    semantic-boundary audits and run-level coverage validation reject raw
    payload, semantic-verification, learned-ranking, TLS-replay, full-replay,
    and authoritative-context overclaims. Unbounded raw payload availability,
    semantic source correctness, learned/external ranking, and replayable
    transport/TLS decision evidence remain open.
  - Required result: when retrieval payload retention, learned/external source
    ranking, semantic verification, or transport/TLS replay evidence changes,
    update README, code TODOs, and paper TODOs together so the README neither
    underclaims bounded redacted sidecar replay nor overclaims DeepEvolve-grade
    auditability.

- [ ] Keep README environment-provenance claims scoped to bounded audit
  evidence.
  - Spec evidence: AlphaEvolve-scale experimental results should be
    reproducible against the evaluator environment, including external build
    steps, package sources, accelerator runtime, and compute-budget evidence.
  - Current evidence: README now documents selected project/build metadata,
    known lockfile hashes, installed-distribution metadata, bounded/redacted
    `pip freeze` and `pip config` evidence, NumPy config hashes, provider SDK
    versions, and bounded accelerator environment/driver probe hints. It also
    states that the policy is audit-only and excludes complete install-source
    interpretation, broader non-project build provenance, private package
    source identity/authentication resolution, remote package artifact
    verification, live provider service/default capture, and accelerator
    budget/accounting evidence.
  - Required result: once replayable external-build records, package-source
    resolution policy, remote artifact verification, accelerator budget
    accounting, or environment restore/check validators land, update README,
    roadmap, papers index, and code/paper TODO entries together so the README
    neither underclaims current bounded environment evidence nor overclaims a
    reproducible AlphaEvolve-grade runtime environment.

- [ ] Keep README archive restore claims scoped to current archive-content
  restore.
  - Spec evidence: AlphaEvolve-style long-running evolutionary search needs
    reproducible population state and clear boundaries for migration-order
    replay versus snapshot restore.
  - Current evidence: README now says full archive cell/island contents can be
    restored from manifest snapshots plus checked accepted-history rows, while
    ordered migration-event replay remains audit-only rather than a MAP-Elites
    restore engine. Both the early runtime-provenance section and the archive
    section now distinguish cursor-only restore from
    `--restore-archive-from-manifest` full archive bundle restore.
  - Required result: when ordered migration-event replay or async
    controller/pending-work resume lands, update README archive sections,
    roadmap, papers index, and code/paper TODO entries together so they do not
    underclaim archive-content restore or overclaim migration replay.

- [ ] Keep README 2026 AlphaEvolve impact wording source-scoped until claim
      provenance exists.
  - Spec evidence: the May 7, 2026 Google DeepMind impact article says
    AlphaEvolve is scaling across health, sustainability, research,
    infrastructure, and commercial applications, with claims including
    DeepConsensus, AC Optimal Power Flow, Earth AI, Willow quantum circuits,
    public gallery examples, TPU design, cache replacement, Spanner, compiler
    storage, and customer deployments.
  - Current evidence: README currently documents the original AlphaEvolve
    paper/announcement boundary, local LibreEvolve implementation status,
    benchmark-report contracts, source repositories, and known open gaps. It
    has no source row or claim table for the 2026 impact article and no local
    benchmark fixtures for the named new domains or customer cases.
  - Required result: when the 2026 impact source is added, update README with
    explicitly scoped wording that identifies the article URL/date/title,
    separates official impact claims from implemented LibreEvolve features,
    points each claim to linked paper/repository/customer evidence when
    available, and avoids implying local support for DeepConsensus, power-grid,
    quantum, Earth AI, Spanner, compiler-storage, TPU-design, commercial, UI,
    API, or public-gallery workflows.

- [ ] Keep README FHE-on-TPU AlphaEvolve claims absent or source-scoped until
      paper and benchmark evidence exists.
  - Spec evidence: arXiv `2605.14718` reports adapting AlphaEvolve to optimize
    Fully Homomorphic Encryption kernels on TPUs, using hardware execution and
    correctness tests for TFHE/Jaxite and CKKS/CROSS on Google Cloud TPUv5e,
    with latency improvements over human-engineered baselines.
  - Current evidence: README documents LibreEvolve's current implementation
    boundaries, matrix/systems benchmark contracts, original AlphaEvolve
    paper claims, and selected later paper rows. It does not list
    `2605.14718`, FHE schemes, TPUv5e cryptographic-kernel execution,
    hardware-feedback traces, correctness-test evidence, or FHE latency
    benchmarks.
  - Required result: if README mentions FHE, cryptography, TPUv5e hardware
    execution, Jaxite, CROSS, or the `2605.14718` speedups, keep the wording
    source-scoped until the paper is in the manifest and a local benchmark or
    explicit background-only row exists. Avoid implying LibreEvolve supports
    FHE-on-TPU optimization without runnable kernels, hardware-execution
    provenance, correctness tests, and latency report artifacts.

- [ ] Keep README AlphaEvolve HCI/user-study claims absent or source-scoped
      until intentmaking evidence exists.
  - Spec evidence: arXiv `2605.05921` reports 11 expert mathematicians using
    AlphaEvolve and frames effective AI-guided mathematical discovery around
    repeated intentmaking and sensemaking cycles, not a one-shot question/
    answer workflow.
  - Current evidence: README documents the CLI, run artifacts, prompt/context
    policies, `show` inspection, source provenance, and current implementation
    boundaries. It does not list `2605.05921`, preserve user-study evidence,
    expose an interactive experiment-planning UI, record human goal-revision
    cycles, or provide a sensemaking dashboard for AlphaEvolve sessions.
  - Required result: if README mentions intentmaking, sensemaking,
    mathematician user studies, collaborative scientific-discovery
    instruments, AlphaEvolve UI workflows, or `2605.05921`, keep the wording
    source-scoped until the paper is in the manifest and local artifacts can
    show interaction/session traces, goal-revision metadata, result-analysis
    dashboard state, and privacy/redaction boundaries. Avoid implying
    LibreEvolve supports the AlphaEvolve HCI workflow without those artifacts.

- [ ] Keep README radar power-allocation AlphaEvolve claims absent or
      source-scoped until paper and benchmark evidence exists.
  - Spec evidence: arXiv `2605.01794` reports using AlphaEvolve Evolution to
    discover a fast closed-form power-allocation solution for multi-target
    tracking, with physically inspired features, a deterministic
    constraint-satisfying transform, 1.51% average relative performance loss,
    cross-scenario/target-count generalization, and over three orders of
    magnitude speedup versus iterative solvers.
  - Current evidence: README documents current LibreEvolve feature boundaries,
    matrix/systems benchmark contracts, and selected AlphaEvolve-related paper
    rows. It does not list `2605.01794`, radar resource allocation,
    multi-target tracking fixtures, feasibility-transform artifacts, tracking
    metrics, generalization splits, or iterative-solver baselines.
  - Required result: if README mentions radar, multi-target tracking,
    real-time resource allocation, closed-form power allocation, or the
    `2605.01794` performance/speedup claims, keep the wording source-scoped
    until the paper is in the manifest and local benchmark/report artifacts
    exist. Avoid implying LibreEvolve supports this application without
    runnable radar fixtures, constraint checks, baselines, and metric reports.

- [ ] Keep README EvoX adaptive meta-evolution claims absent or source-scoped
      until paper and benchmark evidence exists.
  - Spec evidence: arXiv `2602.23413`, `EvoX: Meta-Evolution for Automated
    Discovery`, says AlphaEvolve-style systems reuse evaluated solutions to
    guide new candidates, but fixed search strategies with predefined
    explore/exploit knobs can fail to adapt. It proposes jointly evolving
    candidate solutions and search strategies, dynamically shifting strategy
    choices, and reports outperforming AlphaEvolve, OpenEvolve, GEPA, and
    ShinkaEvolve on the majority of nearly 200 real-world optimization tasks.
  - Current evidence: README documents LibreEvolve's current implementation
    boundaries, parent-selection behavior, islands/archive artifacts, and
    benchmark-report contracts. It does not list `2602.23413`, preserve EvoX
    paper evidence, expose adaptive strategy genomes, record strategy-credit
    assignment, or provide benchmark reports comparing fixed mixed 30/70
    parent selection against EvoX-style adaptive search.
  - Required result: if README mentions EvoX, adaptive evolution, strategy
    self-optimization, dynamic explore/exploit shifting, or comparative wins
    over AlphaEvolve/OpenEvolve/GEPA/ShinkaEvolve, keep the wording
    source-scoped until the paper is in the manifest and local artifacts can
    show strategy-state traces, task-suite definitions, baseline identities,
    ablation reports, token-efficiency data, and benchmark outcomes. Avoid
    implying LibreEvolve supports EvoX-style meta-evolution without those
    implementation and report artifacts.

- [ ] Keep README DeltaEvolve semantic-delta claims absent or source-scoped
      until paper and benchmark evidence exists.
  - Spec evidence: arXiv `2602.02919`, `DeltaEvolve: Accelerating Scientific
    Discovery through Momentum-Driven Evolution`, says AlphaEvolve-style
    systems can rely on full-code histories that are context-inefficient and
    provide weak guidance. It proposes structured semantic deltas over
    successive program-node modifications, a multi-level database, and
    progressive disclosure to reduce input tokens and improve scientific-task
    search.
  - Current evidence: README documents prompt history, parent selection,
    SEARCH/REPLACE diffs, run artifacts, current failure-memory limits, and
    implementation boundaries. It does not list `2602.02919`, preserve
    semantic-delta records, expose delta-effect attribution, maintain a
    multi-level semantic memory, or provide token-efficiency benchmarks
    comparing full-code context with DeltaEvolve-style momentum guidance.
  - Required result: if README mentions DeltaEvolve, semantic deltas,
    momentum-driven evolution, progressive disclosure, multi-level delta
    memory, or token-reduction wins over full-code histories, keep the wording
    source-scoped until the paper is in the manifest and local artifacts can
    show semantic-delta schemas, node-transition provenance, prompt assembly
    traces, token accounting, benchmark tasks, baseline identities, and
    outcomes. Avoid implying LibreEvolve supports DeltaEvolve-style context
    control without those implementation and report artifacts.

- [ ] Keep README MLEvolve long-horizon ML-engineering claims absent or
      source-scoped until paper and benchmark evidence exists.
  - Spec evidence: arXiv `2606.06473`, `MLEvolve: A Self-Evolving Framework
    for Automated Machine Learning Algorithm Discovery`, describes
    self-evolving multi-agent MLE with Progressive MCGS, graph-based
    cross-branch reference edges, entropy-inspired explore/exploit scheduling,
    Retrospective Memory, adaptive coding modes, MLE-Bench state-of-the-art
    metrics under a 12-hour budget, and stronger mathematical algorithm
    optimization than AlphaEvolve.
  - Current evidence: README documents LibreEvolve's current CLI, evaluator,
    MAP-Elites/islands behavior, parent-selection policy, prompt/run
    artifacts, and benchmark-report boundaries. It does not list
    `2606.06473`, expose an MLE-Bench integration, store Progressive MCGS
    graphs or reference edges, maintain Retrospective Memory, separate
    strategic planning from coding modes, or report medal-rate/valid
    submission metrics.
  - Required result: if README mentions MLEvolve, MLE-Bench, Progressive MCGS,
    cross-branch information flow, retrospective memory, adaptive coding
    modes, 12-hour MLE budgets, valid submission or medal rates, or
    outperformance of AlphaEvolve on mathematical algorithm optimization,
    keep the wording source-scoped until the paper is in the manifest and
    local artifacts can show task harnesses, graph-search state, memory
    records, mode traces, baseline identities, budget accounting, and report
    outcomes. Avoid implying LibreEvolve supports MLEvolve-style long-horizon
    MLE without those implementation and benchmark artifacts.

- [ ] Keep README LEVI cost-aware search-architecture claims absent or
      source-scoped until paper and benchmark evidence exists.
  - Spec evidence: arXiv `2605.09764`, `LEVI: Stronger Search Architectures
    Can Substitute for Larger LLMs in Evolutionary Search`, says
    AlphaEvolve-style evolutionary methods are effective but expensive because
    search allocation often fails to preserve diversity, spends frontier-model
    budget on local edits, and evaluates redundant examples. LEVI proposes a
    diversity-preserving solution database, large/small LLM mutation routing,
    and rank-preserving proxy benchmarks, reporting lower-budget systems and
    prompt-optimization results.
  - Current evidence: README documents LibreEvolve's current MAP-Elites
    archive, islands, LLM ensemble heuristic, evaluator artifacts, and
    benchmark-report boundaries. It does not list `2605.09764`, expose
    LEVI-style model routing, preserve diversity/cost evidence, calibrate
    proxy benchmarks, record rank-preservation checks, or report systems/
    prompt optimization budget comparisons.
  - Required result: if README mentions LEVI, cheaper-than-frontier
    evolutionary search, large/small model routing, diversity-preserving
    archives, proxy benchmarks, 3.3x-6.7x lower budgets, 35x lower-cost
    matches, or reduced GEPA rollout budgets, keep the wording source-scoped
    until the paper is in the manifest and local artifacts can show database
    diversity metrics, routing traces, proxy calibration, rank-correlation
    evidence, budget/cost accounting, benchmark baselines, and report
    outcomes. Avoid implying LibreEvolve supports LEVI-style cost-aware search
    architecture without those implementation and benchmark artifacts.

- [ ] Keep README PACEvolve long-horizon consistency claims absent or
      source-scoped until paper and benchmark evidence exists.
  - Spec evidence: arXiv `2601.10657`, `PACEvolve: Enabling Long-Horizon
    Progress-Aware Consistent Evolution`, says LLM-in-the-loop evolutionary
    systems suffer from context pollution, mode collapse, and weak
    collaboration. It proposes hierarchical context management with pruning,
    momentum-based backtracking, and self-adaptive sampling that unifies
    backtracking and crossover, with reported LLM-SR, KernelBench, and Modded
    NanoGPT results.
  - Current evidence: README documents LibreEvolve's current prompt/context
    history, failed-proposal limits, parent selection, MAP-Elites archive,
    islands, and benchmark-report boundaries. It does not list `2601.10657`,
    diagnose context pollution, prune hierarchical context, implement
    momentum backtracking, coordinate crossover with backtracking, or report
    LLM-SR/KernelBench/Modded-NanoGPT results.
  - Required result: if README mentions PACEvolve, progress-aware consistent
    evolution, context-pollution control, hierarchical context pruning,
    momentum-based backtracking, mode-collapse recovery, coordinated
    crossover/backtracking, weak-collaboration mitigation, LLM-SR,
    KernelBench, or Modded NanoGPT records, keep the wording source-scoped
    until the paper is in the manifest and local artifacts can show context
    metrics, pruning traces, backtracking state, sampling-policy records,
    trajectory collaboration diagnostics, benchmark baselines, and report
    outcomes. Avoid implying LibreEvolve supports PACEvolve-style consistency
    controls without those implementation and benchmark artifacts.

- [ ] Keep README FlashEvolve async-stage claims absent or source-scoped until
      paper and benchmark evidence exists.
  - Spec evidence: arXiv `2605.08520`, `FlashEvolve: Accelerating Agent
    Self-Evolution with Asynchronous Stage Orchestration`, says synchronized
    stage execution and LLM-heavy stage imbalance bottleneck LLM-based
    evolution. It proposes asynchronous workers and queues, artifact-version
    tracking, staleness-aware update/discard/patch policies, language-space
    stale-artifact repair, speculative stage completion, adaptive workflow
    control, and reports 3.5x local-vLLM and 4.9x API throughput gains over
    synchronous GEPA.
  - Current evidence: README documents LibreEvolve's current CLI, evaluator,
    run artifacts, archive/island behavior, reviewer pool, and implementation
    boundaries. It does not list `2605.08520`, expose async worker queues,
    overlap proposal/evaluation/admission stages, track artifact versions for
    stale queue items, implement reflective stale-patching, or report
    throughput/token-efficiency gains.
  - Required result: if README mentions FlashEvolve, asynchronous stage
    orchestration, async workers/queues, stale artifact repair, speculative
    stage completion, adaptive workflow control, GEPA throughput gains,
    local-vLLM/API speedups, ACE, or Meta-Harness applicability, keep the
    wording source-scoped until the paper is in the manifest and local
    artifacts can show queue traces, artifact-version lineage, staleness
    policies, patch outputs, throughput/token metrics, baseline identities,
    and report outcomes. Avoid implying LibreEvolve supports FlashEvolve-style
    async orchestration without those implementation and benchmark artifacts.

- [ ] Keep README mechanistic evolutionary-agent claims absent or source-scoped
      until trace-diagnostic evidence exists.
  - Spec evidence: arXiv `2605.20086`, `What Do Evolutionary Coding Agents
    Evolve?`, argues that final benchmark scores hide how evolutionary coding
    agents improve programs and whether improvements are structural
    innovations, constant tuning, overfitting, or cycling artifacts. It
    introduces EvoTrace annotations and EvoReplay interventions for
    AlphaEvolve-style agents including AlphaEvolve, OpenEvolve, and FunSearch.
  - Current evidence: README documents run artifacts, history streams, prompt
    history, archives, evaluator reports, and current implementation
    boundaries. It does not list `2605.20086`, annotate edit mechanisms,
    extract dependency structures, classify fitness trajectories, detect
    cycling or overfitting, separate constant tuning from new logic, or expose
    replay interventions over historical search traces.
  - Required result: if README mentions mechanistic discovery, structural
    innovation, interpretable evolutionary progress, overfitting resistance,
    prompt/population sensitivity, EvoTrace, EvoReplay, or claims that
    LibreEvolve's best programs represent genuine algorithmic discovery, keep
    the wording source-scoped until the paper is in the manifest and local
    artifacts can show edit annotations, dependency graphs, fitness-trajectory
    classes, cycling/overfitting labels, replay interventions, counterfactual
    outcomes, baseline-agent identities, and task reports. Avoid implying
    LibreEvolve has trace-level mechanistic evidence without those artifacts.

- [ ] Keep README Zarankiewicz discovery claims absent or source-scoped until
      paper and benchmark evidence exists.
  - Spec evidence: arXiv `2605.01120`, `New Bounds for Zarankiewicz Numbers
    via Reinforced LLM Evolutionary Search`, reports exact values for three
    Zarankiewicz numbers, lower bounds for 41 more, four matched closed cases,
    generated construction algorithms, and computational costs under `$30` per
    parameter combination using OpenEvolve.
  - Current evidence: README documents LibreEvolve's current examples, source
    provenance, run artifacts, benchmark contracts, and implementation
    boundaries. It does not list `2605.01120`, provide a Zarankiewicz problem
    fixture, verify `K_{s,t}`-free bipartite graphs, preserve generated
    construction algorithms, reproduce exact/lower-bound tables, or report
    parameter-specific costs.
  - Required result: if README mentions Zarankiewicz numbers, extremal
    bipartite graph discovery, OpenEvolve combinatorics results, exact
    `Z(m,n,s,t)` values, 41 lower bounds, or under-`$30` construction costs,
    keep the wording source-scoped until the paper is in the manifest and
    local artifacts can show graph fixtures, verifier outputs, construction
    algorithms, exact/lower-bound records, proof/check status, cost accounting,
    baseline references, and reproducibility reports. Avoid implying
    LibreEvolve supports this application without those artifacts.

- [ ] Keep README CORAL autonomous multi-agent claims absent or source-scoped
      until paper and runtime evidence exists.
  - Spec evidence: arXiv `2604.01658`, `CORAL: Towards Autonomous Multi-Agent
    Evolution for Open-Ended Discovery`, describes long-running agents that
    explore, reflect, and collaborate through shared persistent memory,
    asynchronous multi-agent execution, and heartbeat interventions, with
    safeguards for isolated workspaces, evaluator separation, resource
    management, and agent session/health management. It reports 3-10x higher
    improvement rates with fewer evaluations and kernel-engineering cycle
    improvements.
  - Current evidence: README documents LibreEvolve's current CLI, MAP-Elites
    archive, islands, migration, evaluator subprocesses, run artifacts, and
    benchmark boundaries. It does not list `2604.01658`, expose long-running
    agent sessions, implement shared persistent multi-agent memory, run
    asynchronous collaborative agents, provide heartbeat interventions,
    isolate per-agent workspaces, manage quotas, or report agent health.
  - Required result: if README mentions CORAL, autonomous multi-agent
    evolution, shared persistent memory, asynchronous agent collaboration,
    heartbeat interventions, isolated workspaces, evaluator separation,
    resource management, session health, 3-10x improvement rates, or
    Anthropic kernel-engineering cycle records, keep the wording source-scoped
    until the paper is in the manifest and local artifacts can show session
    state, shared-memory records, communication traces, heartbeat logs,
    workspace/resource policies, health telemetry, benchmark baselines, and
    report outcomes. Avoid implying LibreEvolve supports CORAL-style
    autonomous multi-agent evolution without those artifacts.

- [ ] Keep README AEvo meta-editing claims absent or source-scoped until paper
      and runtime evidence exists.
  - Spec evidence: arXiv `2605.13821`, `Harnessing Agentic Evolution`,
    formulates agentic evolution as an interactive environment where
    accumulated candidates, feedback, traces, and failures are process-level
    state. AEvo uses a meta-agent to edit the procedure or agent context that
    controls future evolution, rather than directly proposing the next
    candidate, and reports stronger results than several evolution baselines.
  - Current evidence: README documents LibreEvolve's current static config,
    CLI, prompt/run artifacts, failure streams, parent selection, archive
    behavior, and benchmark boundaries. It does not list `2605.13821`, expose
    process-level state, run a meta-agent, patch the controller or agent
    context mid-run, version control-edit artifacts, diagnose drift, or report
    AEvo-style benchmark outcomes.
  - Required result: if README mentions AEvo, harnessed meta-editing,
    process-level evolution state, meta-agent controller edits, procedure or
    context patching, adaptive revision of the evolution mechanism, or
    open-ended optimization gains from controller self-modification, keep the
    wording source-scoped until the paper is in the manifest and local
    artifacts can show process-state records, meta-agent actions, patch
    provenance, rollback/versioning, drift diagnostics, budget accounting,
    baselines, and report outcomes. Avoid implying LibreEvolve supports
    AEvo-style meta-editing without those artifacts.

- [ ] Keep README G-Zero verifier-free self-evolution claims absent or
      source-scoped until paper and runtime evidence exists.
  - Spec evidence: arXiv `2605.09959`, `G-Zero: Self-Play for Open-Ended
    Generation from Zero Data`, says open-ended self-evolution can avoid proxy
    LLM judges by using verifier-free co-evolution. It introduces
    `Hint-delta`, Generator/Proposer roles, self-generated hints, GRPO
    training for the Proposer, DPO training for the Generator, exploration
    coverage requirements, and pseudo-label noise assumptions.
  - Current evidence: README documents LibreEvolve's evaluator-first design,
    validator contracts, run artifacts, archive behavior, and benchmark
    boundaries. It does not list `2605.09959`, support verifier-free
    open-ended tasks, compute Hint-delta rewards, train Generator/Proposer
    models, store self-generated hints, or audit reward hacking and
    pseudo-label noise for unverifiable domains.
  - Required result: if README mentions G-Zero, verifier-free self-play,
    open-ended generation without judges, intrinsic rewards, Hint-delta,
    Generator/Proposer co-evolution, GRPO/DPO self-training, exploration
    coverage, or reward-hacking resistance, keep the wording source-scoped
    until the paper is in the manifest and local artifacts can show role
    schemas, response/hint pairs, intrinsic-reward records, training traces,
    coverage/noise diagnostics, task baselines, and report outcomes. Avoid
    implying LibreEvolve supports G-Zero-style verifier-free co-evolution
    without those artifacts.

- [ ] Keep README GenEvolve multimodal trajectory-distillation claims absent
      or source-scoped until paper and runtime evidence exists.
  - Spec evidence: arXiv `2605.21605`, `GenEvolve: Self-Evolving Image
    Generation Agents via Tool-Orchestrated Visual Experience Distillation`,
    models image-generation attempts as tool-orchestrated trajectories with
    evidence gathering, reference selection, generation-skill invocation, and
    prompt-reference programs. It compares multiple trajectories, converts
    best-worst differences into structured visual experience for a privileged
    teacher branch, and distills dense token-level supervision into a student.
  - Current evidence: README documents LibreEvolve's current text-program
    workflow, SEARCH/REPLACE diffs, evaluator artifacts, prompt history,
    examples, and benchmark boundaries. It does not list `2605.21605`, support
    image-generation tools, preserve visual references, store prompt-reference
    programs, compare visual trajectories, run privileged teacher/student
    distillation, or report GenEvolve-Bench results.
  - Required result: if README mentions GenEvolve, multimodal or image
    generation, tool-orchestrated visual trajectories, prompt-reference
    programs, visual experience distillation, privileged teacher branches,
    dense token-level supervision, GenEvolve-Data, or GenEvolve-Bench, keep
    the wording source-scoped until the paper is in the manifest and local
    artifacts can show visual trajectory logs, reference/evidence records,
    image provenance, distillation traces, token-supervision metadata,
    benchmark baselines, and report outcomes. Avoid implying LibreEvolve
    supports GenEvolve-style multimodal evolution without those artifacts.

- [ ] Keep README EvoRubric self-evolving reward-rubric claims absent or
      source-scoped until paper and runtime evidence exists.
  - Spec evidence: arXiv `2605.29847`, `EvoRubric: Self-Evolving
    Rubric-Driven RL for Open-Ended Generation`, proposes alternating
    Reasoner and Rubric Generator roles under one policy, validating generated
    criteria with a meta-verifier, zero-variance pruning, and Leave-One-Out
    peer consensus, archiving criteria into memory, and producing dense
    multi-objective rewards for open-ended generation.
  - Current evidence: README documents LibreEvolve's current evaluator-first
    workflow, scalar/structured scores, MAP-Elites retention, run artifacts,
    and benchmark boundaries. It does not list `2605.29847`, generate dynamic
    rubrics, validate criteria with peer consensus, archive reward criteria,
    produce dense rubric reward vectors, or audit reward hacking in medical,
    writing, or science generation domains.
  - Required result: if README mentions EvoRubric, self-evolving rubrics,
    dynamic open-ended rewards, Reasoner/Rubric-Generator co-evolution,
    meta-verification, zero-variance pruning, Leave-One-Out peer consensus,
    criteria memory pools, dense multi-objective rewards, or expert-prior
    rubric expansion, keep the wording source-scoped until the paper is in
    the manifest and local artifacts can show generated-rubric provenance,
    verification records, consensus traces, reward vectors, reward-hacking
    diagnostics, benchmark baselines, and report outcomes. Avoid implying
    LibreEvolve supports EvoRubric-style reward evolution without those
    artifacts.

- [ ] Keep README LLM-ALSO adaptive learning-signal claims absent or
      source-scoped until paper and runtime evidence exists.
  - Spec evidence: arXiv `2605.29293`, `LLM-ALSO: LLM-Driven Adaptive
    Learning-Signal Optimization for Multi-Agent Reinforcement Learning`,
    proposes iterative diagnosis, proposal, and validation for sparse-reward
    cooperative MARL: a Critic LLM diagnoses stage-specific failures, a
    Generator LLM proposes reward-shaping configurations, and branch
    validation gates updates before they affect the main training trajectory.
  - Current evidence: README documents LibreEvolve's evaluator-first workflow,
    plugins, scoring artifacts, run manifests, and benchmark boundaries. It
    does not list `2605.29293`, provide sparse-reward MARL environments,
    implement Critic/Generator learning-signal roles, generate reward-shaping
    configs, run branch validation, or report MARL learning-efficiency gains.
  - Required result: if README mentions LLM-ALSO, adaptive learning-signal
    optimization, sparse-reward MARL, stage-aware reward shaping, Critic/
    Generator reward roles, branch validation, or promoted reward updates,
    keep the wording source-scoped until the paper is in the manifest and
    local artifacts can show diagnosis records, reward-shaping configs,
    validation traces, promotion decisions, main-training trajectories,
    MARL baselines, and report outcomes. Avoid implying LibreEvolve supports
    LLM-ALSO-style adaptive reward shaping without those artifacts.

- [ ] Keep README MemEvolve memory-architecture claims absent or source-scoped
      until paper and runtime evidence exists.
  - Spec evidence: arXiv `2512.18746`, `MemEvolve: Meta-Evolution of Agent
    Memory Systems`, says agent memory systems usually store trajectories,
    distill experience, and synthesize reusable tools through manually
    engineered static architectures. MemEvolve jointly evolves experiential
    knowledge and the memory architecture itself, using an EvolveLab modular
    design space over encode, store, retrieve, and manage.
  - Current evidence: README documents LibreEvolve's current run artifacts,
    prompt history, failure streams, archive events, and implementation
    boundaries. It does not list `2512.18746`, expose evolvable memory
    architecture components, mutate encode/store/retrieve/manage policies,
    compare static memory baselines, or report cross-task/cross-LLM transfer.
  - Required result: if README mentions MemEvolve, self-evolving memory,
    meta-evolving memory architecture, EvolveLab, encode/store/retrieve/manage
    memory design, trajectory distillation, reusable-tool memory, or adaptive
    memory transfer, keep the wording source-scoped until the paper is in the
    manifest and local artifacts can show memory component schemas, mutation
    records, content/architecture co-evolution traces, benchmark baselines,
    transfer metrics, and report outcomes. Avoid implying LibreEvolve supports
    MemEvolve-style memory architecture evolution without those artifacts.

- [ ] Keep README ANCHOR healthy-evolution oversight claims absent or
      source-scoped until paper and runtime evidence exists.
  - Spec evidence: arXiv `2606.06114`, `Towards Healthy Evolution: Exploring
    the Role and Mechanisms of Human-Agent Interaction in Self-Evolving
    Systems`, introduces Agent Norm Correction through Human-like Oversight
    and Review (ANCHOR). Its abstract frames autonomous self-evolution as a
    safety-drift and capability-degradation risk, then reports that limited
    simulated human supervision can mitigate safety degradation while
    preserving core objective performance, with output verification as the
    strongest intervention point and diminishing returns from increased
    supervision frequency.
  - Current evidence: README documents LibreEvolve's current evaluator-first
    workflow, validity gates, failure/quarantine artifacts, prompt history,
    MAP-Elites retention, and benchmark boundaries. It does not list
    `2606.06114`, simulate human-like oversight, implement ANCHOR norm
    correction, provide phase-specific supervision hooks, measure safety drift
    during self-evolution, record output-verification interventions, or report
    supervision-cadence tradeoffs.
  - Required result: if README mentions ANCHOR, healthy evolution, human-like
    oversight, norm correction, safety drift, capability degradation during
    self-evolution, output-verification supervision, supervision frequency, or
    human-aligned self-evolving agents, keep the wording source-scoped until
    the paper is in the manifest and local artifacts can show oversight-role
    schemas, phase-specific feedback records, safety metrics, intervention
    logs, objective-preservation reports, cadence experiments, benchmark
    baselines, and report outcomes. Avoid implying LibreEvolve supports
    ANCHOR-style healthy-evolution oversight without those artifacts.

- [ ] Keep README SIA harness-plus-weight self-improvement claims absent or
      source-scoped until paper and runtime evidence exists.
  - Spec evidence: arXiv `2605.27276`, `SIA: Self Improving AI with Harness
    & Weight Updates`, proposes a self-improving loop where a Feedback-Agent
    updates both the harness/scaffold and the weights of a task-specific
    agent. Its abstract contrasts harness-only meta-agent updates with
    test-time training under a fixed harness, then reports that combining
    both levers outperforms scaffold iteration alone across Chinese legal
    charge classification, low-level GPU kernel optimization, and single-cell
    RNA denoising.
  - Current evidence: README documents LibreEvolve's current evaluator-first
    workflow, fixed LLM backends, prompt/run artifacts, candidate mutation,
    plugin outputs, and ThetaEvolve-style GRPO export boundary. It does not
    list `2605.27276`, implement a Feedback-Agent, edit task-agent harnesses
    as first-class artifacts, train or fine-tune model weights online, retain
    adapter/checkpoint artifacts, or report harness-only versus
    harness-plus-weight benchmark comparisons.
  - Required result: if README mentions SIA, Self Improving AI, harness and
    weight updates, Feedback-Agent loops, task-specific agent scaffolds,
    online RL/fine-tuning, adapter or checkpoint improvement, LawBench,
    kernel-optimization SIA results, scRNA denoising gains, or autonomous
    model-plus-harness self-improvement, keep the wording source-scoped until
    the paper is in the manifest and local artifacts can show role schemas,
    harness patch provenance, weight-update records, training-data lineage,
    checkpoint/adaptor lifecycle, verifier/reward evidence, ablation
    baselines, compute/cost accounting, and report outcomes. Avoid implying
    LibreEvolve supports SIA-style harness-plus-weight self-improvement
    without those artifacts.

- [ ] Keep README HarnessFix trace-grounded harness repair claims absent or
      source-scoped until paper and runtime evidence exists.
  - Spec evidence: arXiv `2606.06324`, `From Failed Trajectories to Reliable
    LLM Agents: Diagnosing and Repairing Harness Flaws`, introduces
    HarnessFix, which compiles raw execution traces and harness code into a
    Harness-aware Trace Intermediate Representation (HTIR), attributes
    failures to trajectory steps and harness layers, consolidates recurring
    flaw records, maps them to scoped repair operators, and validates harness
    patches under flaw-specific repair specs to avoid unacceptable
    regressions. The abstract reports 15.2% to 50.0% held-out improvements
    across SWE-Bench Verified, Terminal-Bench 2.0 Verified, GAIA, and
    AppWorld.
  - Current evidence: README documents LibreEvolve's current run artifacts,
    prompt history, evaluator failures, quarantine streams, validators, and
    benchmark boundaries. It does not list `2606.06324`, expose HTIR-like
    trace normalization, link failures to harness code and layers, consolidate
    recurring harness flaws, generate scoped harness repairs, or report
    regression-bounded held-out validation for harness patches.
  - Required result: if README mentions HarnessFix, trace-grounded harness
    repair, HTIR, harness-layer failure attribution, scoped repair operators,
    recurring harness flaws, regression-bounded patch validation, SWE-Bench
    Verified harness improvements, Terminal-Bench 2.0 Verified, GAIA,
    AppWorld, or autonomous agent reliability repair, keep the wording
    source-scoped until the paper is in the manifest and local artifacts can
    show trace IR records, harness-code links, attribution reports, flaw
    records, repair patches, validation specs, regression thresholds, held-out
    benchmark baselines, and report outcomes. Avoid implying LibreEvolve
    supports HarnessFix-style trace-grounded harness repair without those
    artifacts.

- [ ] Keep README RHO retrospective harness-optimization claims absent or
      source-scoped until paper and runtime evidence exists.
  - Spec evidence: arXiv `2606.05922`, `Retrospective Harness Optimization:
    Improving LLM Agents via Self-Preference over Trajectory Rollouts`,
    introduces RHO, a self-supervised method that improves an agent harness
    from past trajectories without ground-truth validation labels. Its
    abstract says RHO selects a diverse coreset of challenging tasks, re-solves
    them in parallel, analyzes the rollouts with self-validation and
    self-consistency, generates candidate harness updates, and selects the
    best update through pairwise self-preference. It reports a single-round
    SWE-Bench Pro pass-rate improvement from 59% to 78% without external
    grading.
  - Current evidence: README documents LibreEvolve's evaluator-first workflow,
    run artifacts, prompt history, failure streams, validators, candidate
    mutation, and benchmark boundaries. It does not list `2606.05922`, provide
    a label-free retrospective harness optimizer, select hard/diverse
    trajectory coresets, re-run past tasks in parallel for harness comparison,
    record self-validation or self-consistency analyses, or rank candidate
    harness updates by self-preference.
  - Required result: if README mentions RHO, Retrospective Harness
    Optimization, self-preference over trajectory rollouts, label-free
    harness optimization, hard/diverse trajectory coresets, parallel
    re-rollouts, self-validation, self-consistency, SWE-Bench Pro 59-to-78
    improvement, or long-horizon harness behavior shifts, keep the wording
    source-scoped until the paper is in the manifest and local artifacts can
    show trajectory corpus records, coreset criteria, rollout batches,
    self-analysis artifacts, candidate harness patches, pairwise preference
    rankings, deployment/rollback metadata, benchmark baselines, and report
    outcomes. Avoid implying LibreEvolve supports RHO-style retrospective
    harness optimization without those artifacts.

- [ ] Keep README harness self-evolution benefit claims scoped until
      harness-updating and harness-benefit evidence both exist.
  - Spec evidence: arXiv `2605.30621`, `Harness Updating Is Not Harness
    Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM
    Agents`, distinguishes harness-updating from harness-benefit. Its
    abstract reports that models across capability tiers can produce harness
    updates with similar gains, but the ability to benefit from updated
    harnesses is non-monotonic and can fail when agents do not activate
    relevant harness artifacts or do not follow them faithfully.
  - Current evidence: README documents LibreEvolve's current prompt context,
    backend ensemble, candidate mutation, failure streams, and benchmark
    boundaries. It does not list `2605.30621`, measure harness-update quality
    separately from task-agent benefit, record whether prompt/context artifacts
    were activated or used, track long-horizon adherence to updated harness
    instructions, compare evolver and task-agent model tiers, or report
    capability-budget tradeoffs.
  - Required result: if README mentions harness self-evolution, harness
    updating, harness benefit, persistent harness updates, artifact activation,
    skill or memory load rates, adherence to harness instructions, mid-tier
    benefit peaks, weak-agent activation failures, or capability-budget
    guidance for evolver versus task agent, keep the wording source-scoped
    until the paper is in the manifest and local artifacts can show separate
    update and benefit metrics, activation telemetry, adherence traces,
    model-tier comparisons, benchmark baselines, and report outcomes. Avoid
    implying LibreEvolve benefits from harness self-evolution merely because
    it can generate or record update-like artifacts.

- [ ] Keep README AHE observability-driven harness evolution claims absent or
      source-scoped until paper and runtime evidence exists.
  - Spec evidence: arXiv `2604.25850`, `Agentic Harness Engineering:
    Observability-Driven Automatic Evolution of Coding-Agent Harnesses`,
    introduces AHE, a closed loop for coding-agent harness evolution with
    component observability, experience observability, and decision
    observability. Its abstract says every editable harness component has a
    file-level representation, trajectory evidence is distilled into a
    layered corpus, and every edit carries a self-declared prediction later
    verified against task-level outcomes. It reports Terminal-Bench 2 pass@1
    improvement from 69.7% to 77.0% after ten iterations and transfer of a
    frozen harness to SWE-bench Verified.
  - Current evidence: README documents LibreEvolve's current CLI, prompt
    history, evaluator artifacts, candidate diffs, MAP-Elites archive,
    plugins, and benchmark boundaries. It does not list `2604.25850`, expose
    file-level editable harness components, create a layered trajectory
    evidence corpus, pair harness edits with falsifiable predictions, verify
    those predictions against later outcomes, attribute gains to specific
    harness component classes, or report frozen-harness transfer.
  - Required result: if README mentions AHE, Agentic Harness Engineering,
    observability-driven harness evolution, component observability,
    experience observability, decision observability, file-level harness
    components, drill-down trajectory evidence, falsifiable edit contracts,
    Terminal-Bench 2 69.7-to-77.0 pass@1, Codex-CLI comparison, or frozen-
    harness transfer to SWE-bench Verified, keep the wording source-scoped
    until the paper is in the manifest and local artifacts can show component
    manifests, revertible edit records, evidence corpus records,
    edit-prediction verification, component-attribution reports, benchmark
    baselines, token/cost accounting, and report outcomes. Avoid implying
    LibreEvolve supports AHE-style observability-driven harness evolution
    without those artifacts.

- [ ] Keep README AI Harness Engineering runtime-substrate claims absent or
      source-scoped until paper and runtime evidence exists.
  - Spec evidence: arXiv `2605.13357`, `AI Harness Engineering: A Runtime
    Substrate for Foundation-Model Software Agents`, frames reliable
    autonomous software engineering as a model-harness-environment property.
    Its abstract identifies eleven harness responsibilities, proposes an
    H0-H3 ladder of runtime support, and defines a trace-based evaluation
    protocol where each run becomes an auditable episode package.
  - Current evidence: README documents LibreEvolve's current CLI, config,
    prompt history, evaluator artifacts, LLM-call logs, failure/quarantine
    streams, plugins, and benchmark boundaries. It does not list
    `2605.13357`, expose a complete eleven-responsibility harness contract,
    classify runs by H0-H3 support level, build episode packages, audit
    entropy or maintenance burden, log human interventions, or require
    structured requirement-level verification reports before task completion
    claims.
  - Required result: if README mentions AI Harness Engineering, runtime
    substrate, model-harness-environment capability, H0-H3 harness levels,
    auditable episode packages, entropy auditing, intervention recording,
    permission-boundary traces, requirement-level verification, task-state
    files, context/tool/project-memory traces, or maintainable autonomous
    software-engineering behavior, keep the wording source-scoped until the
    paper is in the manifest and local artifacts can show responsibility
    records, runtime-resource exposure, trace bundles, verification reports,
    entropy audits, intervention logs, benchmark baselines, and report
    outcomes. Avoid implying LibreEvolve implements an AI Harness Engineering
    runtime substrate without those artifacts.

- [ ] Keep README inference-time harness-alignment claims scoped until
      decomposition and guidance tradeoffs are evidenced.
  - Spec evidence: arXiv `2605.21516`, `Harnesses for Inference-Time
    Alignment over Execution Trajectories`, says harnesses improve agents
    through task decomposition and guided execution, but more elaborate
    harnesses are not uniformly better. Its abstract identifies workflow
    granularity, retry budgets, and guidance-induced action reweighting as
    key levers, with over-decomposition, over-pruning, and hallucinated
    execution as failure modes. It also shows partial harnesses can outperform
    fully structured workflows.
  - Current evidence: README documents LibreEvolve's prompt construction,
    context sources, evaluator stages, retries, plugins, and benchmark
    boundaries. It does not list `2605.21516`, report decomposition
    granularity, guidance strength, local guidance rules, pass-rate/final-bias
    tradeoffs, retry-budget sensitivity, over-decomposition or over-pruning
    failures, hallucinated execution, or partial-harness comparisons.
  - Required result: if README mentions inference-time harness alignment,
    task decomposition, guided execution, workflow granularity, retry-budget
    optimization, guidance strength, partial harnessing, over-decomposition,
    over-pruning, hallucinated execution, or claims that more structured
    workflows improve long-horizon performance, keep the wording
    source-scoped until the paper is in the manifest and local artifacts can
    show parameter records, trajectory evidence, pass-rate/final-bias metrics,
    retry and guidance sweeps, partial-harness baselines, and report outcomes.
    Avoid implying LibreEvolve has proven that increased harness structure is
    beneficial without those artifacts.

- [ ] Keep README Adaptive Auto-Harness deployment claims absent or
      source-scoped until open-ended task-stream evidence exists.
  - Spec evidence: arXiv `2606.01770`, `Adaptive Auto-Harness: Sustained
    Self-Improvement for Agentic System Deployment on Open-Ended Task
    Streams`, says fixed offline harness benchmarks do not capture open-ended
    deployments where histories grow, tasks differ, and distributions shift.
    Its abstract warns that a single densely updated harness can become
    brittle, then proposes evolution-loss/adaptation-loss accounting, a
    stateful multi-agent evolver, a harness tree with solve-time routing, and
    human-steering hooks.
  - Current evidence: README documents LibreEvolve's current problem-centric
    CLI, run artifacts, prompt history, MAP-Elites archive, islands, examples,
    and benchmark boundaries. It does not list `2606.01770`, support
    open-ended task streams, manage growing cross-run histories for
    deployment, maintain a harness tree, route tasks to harness variants,
    distinguish evolution loss from adaptation loss, record human steering, or
    report sustained performance under distribution shift.
  - Required result: if README mentions Adaptive Auto-Harness, sustained self-
    improvement, open-ended task streams, deployment adaptation, history-
    growth management, task-wise harness routing, harness trees, solve-time
    routing, human steering, evolution loss, adaptation loss, prediction-
    market/security/event-forecasting streams, or degradation from dense
    repeated harness updates, keep the wording source-scoped until the paper
    is in the manifest and local artifacts can show stream schemas,
    distribution-shift records, harness-tree artifacts, routing traces,
    steering logs, sustained-performance curves, benchmark baselines, and
    report outcomes. Avoid implying LibreEvolve supports Adaptive
    Auto-Harness-style deployment without those artifacts.

- [ ] Keep README Meta-Harness optimization claims absent or source-scoped
      until harness-code search evidence exists.
  - Spec evidence: arXiv `2603.28052`, `Meta-Harness: End-to-End
    Optimization of Model Harnesses`, introduces an outer-loop system that
    searches over harness code using an agentic proposer with filesystem
    access to prior source code, scores, and execution traces. Its abstract
    reports gains in online text classification with fewer context tokens,
    retrieval-augmented IMO-level math reasoning across held-out models, and
    TerminalBench-2 agentic coding.
  - Current evidence: README documents LibreEvolve's current candidate
    workspace mutation, prompt construction, evaluator artifacts, run
    histories, and benchmark boundaries. It does not list `2603.28052`, treat
    harness code as the evolved artifact, expose a source/score/trace corpus
    of prior harness candidates, provide an agentic harness proposer, report
    context-token efficiency, evaluate held-out model transfer, or benchmark
    discovered harnesses against hand-engineered baselines.
  - Required result: if README mentions Meta-Harness, end-to-end harness
    optimization, harness-code search, agentic proposer, filesystem-visible
    prior candidates, source/score/trace search history, context-token
    efficiency, held-out model transfer, online text classification, RAG math,
    or TerminalBench-2 discovered harnesses, keep the wording source-scoped
    until the paper is in the manifest and local artifacts can show harness
    candidate schemas, proposer records, corpus layout, mutation/evaluation
    traces, transfer reports, benchmark baselines, and report outcomes. Avoid
    implying LibreEvolve supports Meta-Harness-style harness-code optimization
    without those artifacts.

- [ ] Keep README AlphaEvolve MARL algorithm-discovery claims absent or
      source-scoped until CFR/PSRO benchmark evidence exists.
  - Spec evidence: arXiv `2602.16928`, `Discovering Multiagent Learning
    Algorithms with Large Language Models`, applies AlphaEvolve to CFR and
    PSRO game-theoretic algorithm design. Its abstract reports VAD-CFR and
    SHOR-PSRO, an 18-game evaluation suite covering Poker, Goofspiel, Liar's
    Dice, Blotto, and Battleship variants, and ablation/distillation into
    WOP-CFR and PM-PSRO minimal solvers that improve generalization with lower
    structural complexity. The method uses OpenSpiel, exact exploitability,
    deterministic metrics, and train-test ablation to separate overfit
    mechanisms from minimal algorithmic cores.
  - Current evidence: README documents LibreEvolve's Python problem format,
    local subprocess validators, staged evaluator cascades, examples,
    benchmark boundaries, and paper cache. It does not mention `2602.16928`,
    provide CFR or PSRO candidate interfaces, include an imperfect-information
    game evaluator, define game-suite train/generalization splits, compare
    against human-designed MARL baselines, report evolved mechanism coupling,
    or show ablation/distillation evidence for minimal generalizing solvers.
    It also lacks README boundaries for exact exploitability scale limits,
    exact best-response PSRO, IQM log-improvement audits, random normal-form
    validation, single-trajectory caveats, and tabular-baseline-only
    comparison scope.
  - Required result: if README mentions AlphaEvolve MARL discovery,
    game-theoretic learning, CFR, PSRO, VAD-CFR, SHOR-PSRO, WOP-CFR,
    PM-PSRO, Poker/Goofspiel/Liar's Dice/Blotto/Battleship benchmarks,
    evolved multiagent-learning algorithms, mechanism distillation, or
    generalized MARL solver discovery, keep the wording source-scoped until
    local artifacts can show the paper in the manifest, candidate schemas,
    OpenSpiel or equivalent evaluator protocols, game-suite split records,
    exact-exploitability and exact-oracle records, baseline identities,
    result tables, IQM ablation/distillation traces, structural-complexity
    metrics, random normal-form validation, limitation records, and
    generalization reports. Avoid implying LibreEvolve supports
    AlphaEvolve-style MARL algorithm discovery without those artifacts.

- [ ] Keep README AlphaEvolve Ramsey-number claims absent or source-scoped
      until graph-witness benchmark evidence exists.
  - Spec evidence: arXiv `2603.09172`, `Reinforced Generation of
    Combinatorial Structures: Ramsey Numbers`, reports AlphaEvolve-improved
    lower bounds for nine classical Ramsey numbers, recovery of all exact
    known Ramsey lower bounds, many matched best-known lower bounds, and one
    meta-algorithm yielding search algorithms for those results. The paper
    defines a lower-bound witness as an `n`-vertex graph with no `r`-clique
    and no `s`-independent set, proving `R(r,s) >= n+1`; its Algorithm 1
    scores evolved programs that return both a valid primary graph `G1` and a
    larger prospect graph `G2` with violation-count guidance; and its PDF links
    Google Research artifacts for the nine improved graph constructions and
    generated search code.
  - Current evidence: README documents general constructive-math gaps, paper
    cache status, benchmark-report contracts, and example smoke fixtures. It
    does not mention `2603.09172`, define Ramsey graph witnesses, provide a
    verifier for `R(s,t)` lower-bound certificates, list the nine Ramsey
    prior/current values, show exact-bound recovery results, compare matched
    best-known bounds, or store generated search algorithms and witness graph
    artifacts. It also does not explain graph-size versus lower-bound
    off-by-one semantics, Algorithm 1 primary/prospect graph scoring, Table 1's
    28-cell coverage/status classes, Table 2 initialization families, public
    artifact links, or provenance caveats for graph-only and
    personal-communication baselines.
  - Required result: if README mentions Ramsey numbers, reinforced
    combinatorial-structure generation, AlphaEvolve-discovered Ramsey lower
    bounds, exact-bound recovery, matched best-known Ramsey bounds, one
    meta-algorithm for Ramsey search, graph witnesses, or `R(s,t)`
    certificates, keep the wording source-scoped until local artifacts can
    show the paper in the manifest, candidate and witness schemas, verifier
    outputs, parameter/result rows, prior/current value provenance, witness
    graph hashes, search-algorithm provenance, independent checker evidence,
    and benchmark reports. Avoid implying LibreEvolve supports
    AlphaEvolve-style Ramsey-number discovery without those artifacts. README
    wording should distinguish `n`-vertex witness graphs from implied
    `R(r,s) >= n+1` lower bounds, state whether Google Research construction
    and code artifacts were imported or only cited, and keep Table 1/Table 2
    and appendix-algorithm references source-scoped until LibreEvolve has
    executable certifiers and reproducible Ramsey benchmark reports.

- [ ] Keep README AlphaEvolve local-correction combinatorics claims absent or
      source-scoped until certificate benchmark evidence exists.
  - Spec evidence: arXiv `2603.06692`, `Evolving Local Corrections for Global
    Constructions in Combinatorics`, uses AlphaEvolve as an experimental
    engine for finite correcting-step certificates in graph reconstruction,
    Latin-square Alon-Tarsi parity, and Rota's Basis Conjecture. Its abstract
    says the paper produces explicit algorithms and structural patterns for
    later mathematical analysis, and does not claim proofs. The body frames
    success as fixed mathematical harnesses evaluating short Python evolvable
    blocks with hard constraints, shaped progress scores, symmetry-scramble
    robustness, and experimental run summaries; it reports concrete
    graph-reconstruction, Latin-square, and Rota benchmark tables rather than
    a general theorem.
  - Current evidence: README documents constructive-math coverage gaps,
    benchmark report contracts, paper-cache status, and smoke fixtures. It
    does not mention `2603.06692`, define local-correction certificate
    candidates, provide graph reconstruction from vertex-deleted subgraphs,
    Latin-square local trade/involution checks, Rota basis-exchange policy
    fixtures, scoring protocol records, conjecture/proof-status fields, or
    finite correcting-step trace artifacts. README also lacks the paper's
    source-specific boundaries: exact deck-agreement checks for bipartite and
    planar reconstructions, Latin-square validity/involution/sign-flip/
    locality/residual-bias/isotopy metrics for orders `8,10,12,14,26`, Rota
    rank/pool/rollout/fitness tables over `F2`, appendix evolved-code
    provenance, and AI-generated summary/AI-use caveats.
  - Required result: if README mentions Berczi local-correction
    combinatorics, graph reconstruction, vertex-deleted subgraphs,
    Alon-Tarsi parity, Latin-square local trades, sign-reversing involutions,
    Rota's Basis Conjecture, local basis-exchange policies, finite
    correcting-step certificates, AlphaEvolve-generated conjectures, or
    explicit algorithms from `2603.06692`, keep the wording source-scoped
    until local artifacts can show the paper in the manifest, certificate
    schemas, case-study fixtures, scoring protocols, finite-step traces,
    generated algorithms, checker outputs, conjecture/proof-status records,
    and benchmark reports. Avoid implying LibreEvolve proves or implements
    AlphaEvolve-style local-correction combinatorics without those artifacts.
    README wording should distinguish the reported `1420/1420` and `896/896`
    reconstruction results, Alon-Tarsi Tables 1-3, and Rota Tables 4-6 from
    local LibreEvolve capabilities unless executable harnesses, trace
    artifacts, appendix-code hashes, verifier outputs, robustness reports, and
    explicit conjecture/proof-status ledgers exist locally.

- [ ] Keep README AlphaEvolve bilateral-trade claims absent or source-scoped
      until mechanism-design benchmark evidence exists.
  - Spec evidence: arXiv `2603.08679`, `A New Lower Bound for the Random
    Offerer Mechanism in Bilateral Trade using AI-Guided Evolutionary Search`,
    uses AlphaEvolve to search value distributions for Random-Offerer
    worst-case performance. Its abstract reports a witness with
    `GFT_FB / GFT_RO >= 2.0749` under the bilateral-trade framing of first-best
    gains from trade versus BIC and BB mechanisms. The paper body fixes the
    benchmark to independent seller/buyer distributions, a Discrete Equal
    Revenue buyer, an evolved seller CDF over `H=20000`, exact FB/SO/BO/RO GFT
    computation after `1e-15` rounding, and a rounded
    mixture-of-modulated-power-laws seller witness with component values
    `1.2322`, `0.3312`, `0.8565`, `0.5939`, and ratio `2.0749`.
  - Current evidence: README documents benchmark-report contracts, paper-cache
    status, constructive-math and systems gaps, and example fixtures. It does
    not mention `2603.08679`, define bilateral-trade value distributions,
    compute first-best or Random-Offerer GFT, preserve BIC/BB assumptions,
    compare the prior `2` conjecture or `~2.02` counterexample, or provide
    witness distribution artifacts and checker outputs. It also lacks
    source-scoped wording for the fixed-buyer/evolved-seller search setup,
    optimal take-it-or-leave-it price evaluation, rounded-integer probability
    policy, appendix evaluator/code-listing provenance, and the caveat that
    the unrounded mixture's exact ratio is left open by the paper.
  - Required result: if README mentions bilateral trade, Random-Offerer,
    Myerson-Satterthwaite, BIC/BB mechanism design, first-best gains from
    trade, `GFT_FB / GFT_RO`, AlphaEvolve-discovered value distributions, or
    the `2.0749` lower bound, keep the wording source-scoped until local
    artifacts can show the paper in the manifest, distribution schemas,
    evaluator and ratio definitions, precision/tolerance records, baseline
    attribution, witness artifacts, independent checker outputs, and benchmark
    reports. Avoid implying LibreEvolve supports AlphaEvolve-style bilateral-
    trade lower-bound discovery without those artifacts. README wording should
    distinguish paper-reported rounded-distribution evidence from local
    LibreEvolve capability unless the repo has the `H=20000` evaluator,
    equal-revenue buyer fixture, evolved seller generator artifact, exact
    FB/SO/BO/RO recomputation, reserve-price witness logs, appendix evaluator
    hash, and rounded-versus-unrounded caveat recorded.

- [ ] Keep README AlphaEvolve Magellan compiler-optimization claims absent or
      source-scoped until compiler benchmark evidence exists.
  - Spec evidence: arXiv `2601.21096`, `Magellan: Autonomous Discovery of
    Novel Compiler Optimization Heuristics with AlphaEvolve`, uses
    AlphaEvolve-style search to synthesize executable C++ decision logic for
    compiler passes. Its abstract reports a closed loop of generation,
    user-provided macro-benchmark evaluation, autotuning, and refinement, with
    LLVM function-inlining, register-allocation, and preliminary XLA
    optimization results. The paper's concrete loop edits EVOLVE-BLOCK regions
    in compiler source, emits C++ decision policies with compiler-flag
    hyperparameters, rebuilds the toolchain, scores macro-benchmarks with
    binary-size or runtime signals, and feeds best scores, tuning logs, and
    profiling traces back into AlphaEvolve.
  - Current evidence: README documents general AlphaEvolve systems gaps,
    paper-cache status, benchmark-report contracts, and existing smoke
    fixtures. It does not mention `2601.21096`, define compiler-heuristic
    candidates, run compiler pass candidates, evaluate LLVM inlining, measure
    register-allocation priority rules, test XLA portability, preserve macro-
    benchmark provenance, compare expert compiler baselines, or report binary-
    size and end-to-end-performance results. It also lacks README boundaries
    for feature-based versus full-API inlining modes, autotuner-assisted
    hyperparameter search, temporal/domain generalization, generated-policy
    maintainability, and XLA graph-extraction or auto-sharding benchmark
    caveats.
  - Required result: if README mentions Magellan, compiler-optimization
    heuristics, executable C++ compiler decision logic, compiler pass
    evolution, LLVM inlining, register-allocation priority rules, XLA
    portability, macro-benchmark compiler evaluation, AlphaEvolve-discovered
    compiler policies, or compiler autotuning loops, keep the wording source-
    scoped until local artifacts can show the paper in the manifest, candidate
    schemas, EVOLVE-BLOCK compiler-source spans, compiler-pass runners,
    benchmark provenance, metric definitions, feature/full heuristic mode
    labels, autotuning traces, generalization reports, maintainability reports,
    XLA task/protocol rows, baseline identities, environment hashes,
    independent checker outputs, and benchmark reports. Avoid implying
    LibreEvolve supports AlphaEvolve-style Magellan compiler optimization
    without those artifacts.

- [ ] Keep README AlphaEvolve ArchAgent computer-architecture claims absent
      or source-scoped until simulator benchmark evidence exists.
  - Spec evidence: arXiv `2602.22425`, `ArchAgent: Agentic AI-driven Computer
    Architecture Discovery`, uses an AlphaEvolve-based agentic flow to design
    and implement cache replacement policies. Its abstract reports IPC speedup
    improvements on public multi-core Google Workload Traces and single-core
    SPEC06 workloads, faster development than prior human-developed SoTA
    policies, post-silicon hyperspecialization gains, and simulator-escape
    behavior. The method evaluates C++ cache replacement policies in
    ChampSim, reports IPC speedup normalized to LRU, separates short
    evolution runs from longer validation runs, and requires hardware-
    realizability checks.
  - Current evidence: README documents general AlphaEvolve systems gaps,
    benchmark-report contracts, paper-cache status, and smoke fixtures. It
    does not mention `2602.22425`, define cache replacement policy candidates,
    integrate a microarchitectural simulator, preserve Google Workload Trace
    or SPEC06 provenance, compare prior SoTA policies, measure IPC speedup,
    record post-silicon specialization parameters, distinguish short feedback
    simulations from validation simulations, document policy-state budgets or
    hardware-realizability checks, preserve ablation evidence, or flag
    simulator escapes.
  - Required result: if README mentions ArchAgent, computer architecture
    discovery, cache replacement policies, ChampSim or microarchitectural
    simulators, Google Workload Traces, SPEC06 cache benchmarks, IPC speedup,
    post-silicon hyperspecialization, AlphaEvolve-discovered hardware
    policies, or simulator escapes, keep the wording source-scoped until
    local artifacts can show the paper in the manifest, candidate schemas,
    simulator runners, workload provenance, benchmark splits, metric
    definitions, baseline identities, generated policy artifacts, CRC
    configuration records, policy-state budget checks, short/long simulation
    protocols, ablation reports, simulator-escape controls, independent
    checker outputs, and benchmark reports. Avoid implying LibreEvolve
    supports AlphaEvolve-style ArchAgent computer-architecture discovery
    without those artifacts.

- [ ] Keep README AlphaEvolve Fault2Flow workflow-automation claims absent or
      source-scoped until fault-to-workflow benchmark evidence exists.
  - Spec evidence: arXiv `2511.12916`, `Fault2Flow: An AlphaEvolve-Optimized
    Human-in-the-Loop Multi-Agent System for Fault-to-Workflow Automation`,
    uses an AlphaEvolve module to optimize reasoning logic in a workflow that
    extracts regulatory logic into PASTA fault trees, incorporates expert
    verification, and emits n8n-executable workflows. Its abstract reports
    transformer fault-diagnosis validation with `100%` topological consistency
    and high semantic fidelity. The body adds that the system parses
    regulatory PDFs with MinerU, stores text in MySQL and embeddings in
    Milvus, generates PlantUML mind maps, converts them into PASTA DSL, uses
    an OpenEvolve-linked AlphaEvolve optimizer, emits n8n IF/ELSE workflows,
    and evaluates 16 transformer DGA cases with LRM, SF, TC, E2ERC,
    success/fail, and token metrics.
  - Current evidence: README documents general plugins, paper-cache status,
    benchmark-report contracts, and smoke fixtures. It does not mention
    `2511.12916`, parse regulatory fault-diagnosis text into PASTA fault
    trees, model expert verification states, optimize reasoning logic for
    fault workflows, emit n8n workflows, preserve transformer fault-diagnosis
    dataset provenance, or report topological-consistency and semantic-
    fidelity metrics. README also lacks source-scoped boundaries for
    PlantUML/PASTA/n8n artifacts, MinerU/MySQL/Milvus provenance, synthesized
    workflow verification tests, GPT-5 evaluator caveats, Table 1 model rows,
    and placeholder ACM/conference/DOI metadata caveats.
  - Required result: if README mentions Fault2Flow, fault-to-workflow
    automation, PASTA fault trees, power-grid fault diagnosis, regulatory
    logic extraction, human-in-the-loop expert verification, n8n workflow
    synthesis, AlphaEvolve-optimized reasoning logic, topological consistency,
    or semantic fidelity, keep the wording source-scoped until local artifacts
    can show the paper in the manifest, candidate schemas, expert-review
    records, workflow artifacts, dataset provenance, metric definitions,
    independent checker outputs, and benchmark reports. Avoid implying
    LibreEvolve supports AlphaEvolve-style Fault2Flow automation without those
    artifacts. README wording should distinguish paper-reported Fault2Flow
    results from local capability unless the repo has executable PASTA/n8n
    workflows, PlantUML and fault-tree artifacts, human-review state logs,
    AlphaEvolve/OpenEvolve optimization traces, synthesized test-case outputs,
    LRM/SF/TC/E2ERC recomputation, Table 1 model/baseline rows, token ledgers,
    human-annotation/data-ethics caveats, and publication-metadata caveats
    recorded.

- [ ] Keep README TTT-Discover test-time-training claims absent or source-
      scoped until mutable-policy benchmark evidence exists.
  - Spec evidence: arXiv `2601.16175`, `Learning to Discover at Test Time`,
    contrasts AlphaEvolve-style frozen-LLM prompting with reinforcement
    learning at test time, where the LLM keeps training on one specific
    discovery problem. Its abstract reports continuous-reward results across
    math, GPU kernel engineering, algorithm design, and biology, with open
    model `OpenAI gpt-oss-120b`, public code, Tinker runs, expert or
    organizer review, and low per-problem costs. The body uses mutable
    test-time weights, adaptive entropic RL, PUCT reuse, LoRA rank `32`, `50`
    steps of `512` rollouts, Tinker `32768`-token context windows, and
    benchmark-specific verifiers for math constructions, Triton kernels, C++
    AtCoder submissions, and single-cell denoising.
  - Current evidence: README documents provider adapters, feedback graders,
    benchmark-report contracts, paper-cache status, and smoke fixtures. It
    does not mention `2601.16175`, implement test-time RL, mutate model
    weights or policy state, record Tinker/API training runs, preserve open-
    model checkpoint provenance, define continuous-reward task rows for the
    cited domains, record expert/organizer review, or compare frozen-search
    AlphaEvolve/OpenEvolve baselines against a trained-at-test-time policy.
    README also lacks source-scoped boundaries for public TTT-Discover URLs,
    LoRA/checkpoint lineage, adaptive-beta/PUCT traces, GPUMode/AtCoder/
    OpenProblems harness provenance, Table 2-10 result rows, OpenEvolve
    truncation caveats, official submission links, and the sampling-budget
    inconsistency in the paper text.
  - Required result: if README mentions TTT-Discover, test-time training,
    reinforcement learning at test time, mutable LLM policy state, Tinker
    discovery runs, `gpt-oss-120b` reproduction, continuous-reward discovery
    benchmarks, Erdos minimum overlap, autocorrelation, GPUMode, AtCoder,
    single-cell denoising, or open-model alternatives to AlphaEvolve, keep the
    wording source-scoped until local artifacts can show the paper in the
    manifest, policy/training-state schemas, training-run provenance,
    checkpoint records, benchmark definitions, baseline identities, expert
    review artifacts, budget/cost records, independent checker outputs, and
    benchmark reports. Avoid implying LibreEvolve supports TTT-Discover-style
    test-time training without those artifacts. README wording should also
    distinguish provider inference, critique, and feedback grading from
    weight-updating test-time RL unless local artifacts include mutable
    checkpoints, rollout batches, adaptive-beta and PUCT records, table-level
    result reproduction, official score/runtime submissions, and source
    caveats for paper-text inconsistencies.

- [ ] Keep README AlphaEvolve Bruhat-interval claims absent or source-scoped
      until permutation and interval-verifier evidence exists.
  - Spec evidence: arXiv `2601.01235`, `Bruhat intervals that are large
    hypercubes`, says AlphaEvolve-suggested permutations revealed a pattern
    for large Bruhat intervals that are poset hypercubes in `S_n`, later
    proved for general `n`. For powers of `2`, the paper exhibits
    `O(n log n)`-dimensional hypercubes, characterizes vertices as dyadically
    well-distributed permutations, and links the result to Kazhdan-Lusztig
    `R`-polynomial coefficients and lower-bound consequences in cluster
    algebras and Bruhat-graph embeddings. The body identifies the construction
    as bit-reversal endpoints `x_m`/`y_m` whose interval equals the
    dyadically well-distributed permutations `D_m`, with verification through
    Ehresmann matrices, complementary-block flips, and a poset isomorphism to
    a rank `m * 2^(m-1)` hypercube.
  - Current evidence: README documents constructive-math gaps, benchmark-
    report contracts, paper-cache status, and smoke fixtures. It does not
    mention `2601.01235`, define permutation generators for `S_n`, verify
    Bruhat intervals, check poset-hypercube structure, compute dyadic well-
    distribution predicates, record power-of-two benchmark rows, connect
    outputs to Kazhdan-Lusztig coefficients or cluster-algebra consequences,
    or preserve finite-search versus general-proof status. README also lacks
    source-scoped boundaries for Section 4 AlphaEvolve/FunSearch experiment
    provenance, public `Bruhat-hypercubes` artifact links, model/cost/run
    metadata, bit-reversal lineage and low-discrepancy-literature caveats,
    `R`-polynomial/d-invariant checker formulas, and PDF/arXiv metadata
    caveats.
  - Required result: if README mentions Bruhat intervals, poset hypercubes in
    `S_n`, dyadically well-distributed permutations, AlphaEvolve-suggested
    permutation patterns, Kazhdan-Lusztig `R`-polynomials, open Richardson
    cluster-algebra frozen variables, Bruhat graph embeddings, or
    `2601.01235`, keep the wording source-scoped until local artifacts can
    show the paper in the manifest, permutation schemas, interval witness
    artifacts, hypercube verifier outputs, dyadic checker records, benchmark
    rows, proof-status fields, independent checker outputs, and benchmark
    reports. Avoid implying LibreEvolve supports AlphaEvolve-style Bruhat-
    interval hypercube discovery without those artifacts. README wording should
    also distinguish generic constructive-math search from this paper's
    specific `d`-invariant objective, FunSearch/AlphaEvolve generalizer-mode
    process, bit-reversal theorem proof, public artifact verification, and
    theorem-backed consequences.

- [ ] Keep README global-NLP solver comparison claims absent or source-scoped
      until solver benchmark evidence exists.
  - Spec evidence: arXiv `2601.05943`, `Global Optimization for
    Combinatorial Geometry Problems`, asks whether off-the-shelf global
    optimization solvers can match AlphaEvolve benchmark results when hard
    geometry/combinatorial problems are directly formulated as NLPs. Its
    abstract reports straightforward NLP formulations evaluated with
    commercial FICO Xpress and open-source SCIP, reproducing and sometimes
    improving best known and LLM-driven results without solver modifications.
    The body focuses on min-max distance ratio, square/rectangle circle
    packing, and regular-hexagon packing, using Mosel formulations, QCP
    squared-distance constraints, circle center/radius variables, and Farkas-
    multiplier hexagon non-overlap constraints.
  - Current evidence: README documents constructive-math gaps, benchmark-
    report contracts, paper-cache status, and smoke fixtures. It does not
    mention `2601.05943`, define direct NLP formulations for AlphaEvolve
    benchmark problems, run Xpress or SCIP, record solver licenses/versions,
    preserve solver incumbents/bounds/certificates, compare solver outputs
    against AlphaEvolve and literature baselines, or document numerical
    tolerance and reproducibility for direct solver baselines. README also
    lacks source-scoped boundaries for Mosel model artifacts, selected
    distance/circle/hexagon benchmark rows, AlphaEvolve repository validation
    outputs, Table 1-3 comparisons, solver-attribution caveats, dual-bound
    omissions, and commercial-license handling for Xpress.
  - Required result: if README mentions global NLP solvers, FICO Xpress, SCIP,
    direct nonlinear-programming formulations of AlphaEvolve benchmarks,
    solver reproduction of AlphaEvolve discoveries, solver improvements over
    LLM-driven results, or `2601.05943`, keep the wording source-scoped until
    local artifacts can show the paper in the manifest, NLP formulation
    schemas, solver-run records, version/license metadata, incumbent/bound/
    certificate artifacts, tolerance policy, baseline comparisons,
    independent checker outputs, and benchmark reports. Avoid implying
    LibreEvolve supports global-NLP solver comparison for AlphaEvolve
    benchmarks without those artifacts. README wording should also distinguish
    LibreEvolve's LLM evolutionary code search from direct mathematical
    programming baselines unless local reports include exported NLP models,
    solver logs, solution validation, baseline citations, table-level outcome
    rows, and reproducibility/licensing status for both solvers.

- [ ] Keep README post-AlphaEvolve autoconvolution improvement claims absent
      or source-scoped until 575-interval witness evidence exists.
  - Spec evidence: arXiv `2506.16750`, `An improved example for an
    autoconvolution inequality`, reports a nonnegative step function with
    `575` equally spaced intervals and autoconvolution ratio `>= 0.901564`.
    Its abstract says this improves on DeepMind's AlphaEvolve `50`-interval
    witness with value `>= 0.8962`, and that the improved witness was found by
    simulated annealing and gradient methods rather than LLMs. The body gives
    an exact rational certificate, a finite coefficient-list formula using
    `L_j` convolution samples, public Python/Mathematica code, and Appendix A
    integer coefficients obtained by scaling by `2^24` and rounding.
  - Current evidence: README documents Appendix B/autoconvolution gaps,
    constructive-math benchmark-report contracts, paper-cache status, and
    smoke fixtures. It does not mention `2506.16750`, store a 575-interval
    step-function witness, recompute the autoconvolution objective, compare
    the AlphaEvolve 50-interval baseline against the later result, preserve
    non-LLM search provenance, or define a rounding/tolerance rule for
    `0.901564`. README also lacks source-scoped boundaries for the public
    `autoconvolutionHolder` repository, `coeffBL.txt` and `Verify.nb`
    artifacts, row-major coefficient parsing, translation/dilation support
    normalization, Matolcsi-Vinuesa and AlphaEvolve coefficient comparisons,
    integer-arithmetic checker provenance, and NCSU HPC/resource caveats.
  - Required result: if README mentions the improved autoconvolution example,
    the 575-interval witness, the `0.901564` value, the AlphaEvolve
    `0.8962` autoconvolution baseline, simulated annealing, gradient-based
    improvement over AlphaEvolve, or `2506.16750`, keep the wording source-
    scoped until local artifacts can show the paper in the manifest, witness
    payloads, convolution/norm recomputation, objective/tolerance policy,
    baseline comparison rows, non-LLM search provenance, independent checker
    outputs, and benchmark reports. Avoid implying LibreEvolve supports this
    post-AlphaEvolve autoconvolution improvement without those artifacts.
    README wording should also distinguish AlphaEvolve's LLM-generated
    50-interval witness from this later non-LLM 575-interval certificate until
    local artifacts include exact coefficients, exact-rational/decimal checker
    outputs, GitHub artifact hashes, and reproducible Python/Mathematica
    verification.

- [ ] Keep README post-AlphaEvolve sums-and-differences improvement claims
      absent or source-scoped until huge-set construction evidence exists.
  - Spec evidence: arXiv `2505.16105`, `Sums and differences of sets
    (improvement over AlphaEvolve)`, by Robert Gerbicz says AlphaEvolve
    improved the lower bound from `theta = 1.14465` to `theta = 1.1584` using
    a set of `54265` integers. The paper improves the bound to
    `theta = 1.173050` with an explicit `U` set containing more than
    `10^43546` elements and uses GMP for fast integer and floating-point
    arithmetic. Its construction defines `W(m, L, B)`, encodes bounded
    coordinates in base `2B + 1`, reports a `theta = 1.162997` small-search
    case at `m = 80`, `L = 64`, `B = 5`, and confirms
    `theta = 1.173050` for `m = 81411`, `L = 65536`, `B = 5`; the paper cites
    GMP code and exact computed values at `https://bit.ly/43mWCVC`.
  - Current evidence: README documents Appendix B sums-and-differences gaps,
    constructive-math benchmark-report contracts, paper-cache status, and
    smoke fixtures. It does not mention `2505.16105`, store an explicit or
    compressed `U`-set construction, verify sumset/difference-set
    cardinalities, recompute `theta = 1.173050`, compare against the
    AlphaEvolve `54265`-integer `1.1584` baseline, preserve GMP arithmetic
    provenance, retrieve the cited exact-value artifact, preserve the
    `W(m, L, B)` and base-`2B + 1` construction details, or distinguish the
    later explicit construction from AlphaEvolve's LLM-generated witness.
  - Required result: if README mentions this sums-and-differences improvement,
    the `1.173050` bound, the huge `U` set, `10^43546`, the AlphaEvolve
    `54265`-integer construction, the `1.1584` or `1.14465` baselines, GMP
    arithmetic, `W(m, L, B)`, base-`2B + 1` encoding, the `(81411, 65536, 5)`
    parameter triple, the cited exact-value payload, or `2505.16105`, keep the
    wording source-scoped until local artifacts can show the paper in the
    manifest, construction payloads, sumset/difference-set verification,
    max-element/q-value checks, `theta` recomputation, tolerance policy,
    baseline comparison rows, arithmetic provenance, independent checker
    outputs, and benchmark reports. Avoid implying LibreEvolve supports this
    post-AlphaEvolve sums-and-differences improvement without those artifacts.

- [ ] Keep README further post-AlphaEvolve sums-and-differences claims absent
      or source-scoped until sequence evidence exists.
  - Spec evidence: arXiv `2506.01896`, `Sums and differences of sets: a
    further improvement over AlphaEvolve`, improves on both AlphaEvolve's
    `theta = 1.1584` and the later `2505.16105` explicit-construction result
    `theta = 1.173050`. Its abstract constructs a sequence of `U` sets whose
    limit establishes `theta = 1.173077`. The paper, by Fan Zheng, uses
    large-deviation estimates for `W(m, floor(rm), B)`, a base-`2B + 1`
    integer-image construction, asymptotic bounds on `q(U)`, `s(U)`, and
    `d(U)`, and a MATLAB 2024b optimization over `B`, `r`, and `a`; the
    reported best row is `B = 5` with `theta - 1 = 0.173077279785136` at
    both `1e-8` and `1e-10` tolerances.
  - Current evidence: README documents Appendix B sums-and-differences gaps
    plus the need for source-scoped coverage of `2505.16105`. It does not
    mention `2506.01896`, define a sequence-of-sets construction, preserve
    finite-prefix artifacts, verify limiting lower-bound derivations, preserve
    large-deviation lemma evidence, extract or reimplement the MATLAB
    optimizer, compare against both the AlphaEvolve and `2505.16105`
    baselines, or distinguish asymptotic sequence evidence from finite
    huge-set evidence.
  - Required result: if README mentions the further sums-and-differences
    improvement, the `1.173077` bound, a sequence of `U` sets, limiting
    lower-bound constructions, the AlphaEvolve `1.1584` baseline, the
    `2505.16105` `1.173050` baseline, large-deviation estimates, MATLAB
    optimization, the `B = 5` tolerance-sweep result, or `2506.01896`, keep
    the wording source-scoped until local artifacts can show the paper in the
    manifest, sequence schemas, finite-prefix artifacts, limiting-bound
    derivation records, large-deviation checker outputs, MATLAB extraction or
    independent reimplementation, convergence/tail-bound checker outputs,
    baseline comparison rows, independent checker outputs, and benchmark
    reports. Avoid implying LibreEvolve supports this further
    post-AlphaEvolve sums-and-differences improvement without those artifacts.

- [ ] Keep README UCB-style scheduler wording scoped until UCB1 source
      assumptions and regret evidence exist.
  - Spec evidence: the local `auer-cesa-bianchi-fischer-2002` paper,
    `Finite-time Analysis of the Multiarmed Bandit Problem`, by Peter Auer,
    Nicolo Cesa-Bianchi, and Paul Fischer analyzes UCB1 for arms with reward
    distributions supported in `[0, 1]`, defines regret as expected loss from
    not always playing the best arm, and proves finite-time logarithmic regret
    bounds using empirical reward means, play counts, and a confidence-radius
    index. Theorem 1 bounds regret with the `8 ln(n) / Delta_i` constant and
    the proof uses Chernoff-Hoeffding bounds; the paper notes Theorems 1-3 do
    not need cross-machine independence and only require the per-arm
    conditional-mean condition. UCB2, `epsilon_n`-GREEDY, UCB1-NORMAL, and
    UCB1-TUNED are separate variants, and UCB1-TUNED has no proven regret
    bound in the paper.
  - Current evidence: README describes LibreEvolve's backend selector as
    `UCB-style` and the paper table lists UCB1 as inspiration for heuristic
    backend routing. ROADMAP/code caveats already warn against canonical UCB1
    overclaims, but README does not require a source-specific boundary for the
    local UCB1 PDF id/hash, reward-support assumptions,
    conditional-mean/stationarity assumptions, reward-normalization policy,
    backend-as-arm stability, selected-arm/index telemetry, coefficient
    mapping from canonical UCB1 to LibreEvolve's configurable exploration
    term, metadata-aware `throughput_depth` caveats, or regret-report proof
    status.
  - Required result: when README discusses UCB1, UCB-style routing, backend
    bandits, or scheduler reward, keep wording source-scoped until manifests
    and reports record the `auer-cesa-bianchi-fischer-2002` UCB1 source row,
    bounded-reward normalization,
    conditional-mean/stationarity disclaimer, stable backend-as-arm identity,
    selected-backend/index telemetry, exploration-coefficient mapping, regret
    metrics where applicable, variant unsupported status for UCB2,
    `epsilon_n`-GREEDY, UCB1-NORMAL, and UCB1-TUNED where relevant, and a
    clear statement that heuristic backend routing is not a finite-time-
    regret UCB1 reproduction without those assumptions.

- [ ] Keep README GigaEvo wording scoped until framework-parity evidence
      exists.
  - Spec evidence: local arXiv `2511.17592`, `GigaEvo: An Open Source
    Optimization Framework Powered by LLMs and Evolution Algorithms`, by
    Valentin Khrulkov et al. describes Redis-backed program storage with UUID,
    source code, lifecycle states (`FRESH`, `RUNNING`, `COMPLETE`), metrics,
    genealogical lineage, DAG stage outputs, and optimistic concurrency;
    an `asyncio` DAG execution engine with data-flow and execution-order
    dependencies, caching, and automatic stage skipping; MAP-Elites evolution;
    LangGraph mutation operators; insight generation; bidirectional lineage
    tracking; Hydra configuration; diff and rewrite mutation modes; and
    AlphaEvolve benchmark reproduction experiments. The paper reports
    Heilbronn `n = 11` at `0.0364` vs AlphaEvolve `0.0365`, circle-packing
    reproduction attempts, kissing-number recovery without improvements in
    most dimensions, bin-packing Weibull excess bin usage `0.55%`, and Jigsaw
    prompt/agent evolution with `0.803` test AUC for the evolved agent.
  - Current evidence: README and `papers/README.md` mark GigaEvo as framework
    inspiration only and say Redis lifecycle database, `asyncio` DAG engine,
    insight stage, and concurrent units are not implemented. Existing README
    TODOs group GigaEvo with other paper-inspired approximations, but README
    does not require a source-specific boundary for `2511.17592`, code
    repository status, architecture-component mapping, lifecycle/DAG/lineage
    semantics, Hydra problem-layout mapping, or benchmark-reproduction claim
    handling.
  - Required result: if README mentions GigaEvo, Redis lifecycle storage,
    DAG-based evaluation, concurrent units, insight stages, bidirectional
    lineage tracking, LangGraph mutation, or GigaEvo benchmark reproduction,
    keep the wording source-scoped until local manifests and reports include
    the `2511.17592` source row, PDF/code hashes, lifecycle-state schema,
    DAG-stage/dependency records, concurrency/caching telemetry, insight and
    lineage artifacts, Hydra/component-layout mapping, benchmark reproduction
    rows for the named paper tasks, and a clear distinction between
    LibreEvolve's current local runner and GigaEvo framework parity.

- [ ] Keep README CodeEvolve wording scoped until operator and benchmark
      evidence exists.
  - Spec evidence: local arXiv `2510.14150`, `CODE EVOLVE: an open-source
    evolutionary framework for algorithmic discovery and optimization`, by
    Henrique Assumpcao et al. describes islands-based evolution with weighted
    LLM ensembles, inspiration-based semantic crossover, meta-prompting
    exploration, depth-based targeted refinement with `k` nearest ancestors,
    exploration scheduling, sandboxed evaluation, MAP-Elites/CVT-MAP-Elites
    archives, and AlphaEvolve/EoH benchmark plus quality-cost comparisons. It
    defines separate solution and prompt fitness (`fsol`/`fprompt`), reports
    that CODE EVOLVE matches or surpasses AlphaEvolve on `5` of `9`
    AlphaEvolve benchmark instances, shows `CirclePackingSquare(n = 26)`
    `2.63598` vs AlphaEvolve `2.63586` and `n = 32` `2.93956` vs
    AlphaEvolve `2.93794`, and reports Qwen3-Coder-30B cost advantages over
    GEMINI-2.5 such as roughly `$6` vs just under `$35` for the `n = 26`
    circle-packing run.
  - Current evidence: README and `papers/README.md` mark CodeEvolve as
    agentic code-evolution inspiration only and say crossover, targeted
    refinement, modular orchestration, and context-aware recombination are not
    implemented. Existing README TODOs group CodeEvolve with other
    paper-inspired approximations, but README does not require a
    source-specific boundary for `2510.14150`, prompt/solution fitness,
    semantic crossover, meta-prompting exploration, depth-refinement ancestor
    context, Plateau Scheduler behavior, sandbox parity, MAP-Elites/CVT
    archive parity, benchmark rows, ablations, hyperparameter guidance, or
    cost-comparison claims.
  - Required result: if README mentions CodeEvolve, inspiration crossover,
    meta-prompting, targeted refinement, modular orchestration,
    context-aware recombination, open-weight cost comparisons, or CodeEvolve
    benchmark results, keep wording source-scoped until manifests and reports
    include the `2510.14150` source row, PDF/code hashes, operator artifacts,
    scheduler traces, prompt/solution fitness metadata, sandbox/runtime-memory
    evidence, MAP-Elites/CVT compatibility reports, AlphaEvolve/EoH benchmark
    rows, ablation/cost reports, hyperparameter defaults, and a clear
    distinction between LibreEvolve's current prompt-program features and
    CodeEvolve framework parity.

- [ ] Keep README ThetaEvolve wording scoped until test-time learning evidence
      exists.
  - Spec evidence: local arXiv `2511.23473`, `ThetaEvolve: Test-time Learning
    on Open Problems`, by Yiping Wang et al. describes an
    AlphaEvolve-inspired dynamic environment with a single LLM, large program
    database, batch sampling, early checks, lazy penalties, reward shaping,
    optional GRPO/RL training at test time, RL-trained checkpoints, and
    open-problem benchmark claims. It reports DeepSeek-R1-0528-Qwen3-8B
    improving `CirclePacking` and `FirstAutoCorrIneq` bounds mentioned in
    AlphaEvolve, including Table 1 rows `2.63598308` vs AlphaEvolve
    `2.63586276` for circle packing and `1.503133` vs AlphaEvolve `1.503164`
    for FACI, plus a `3` second circle-packing program vs ShinkaEvolve's
    roughly `75` second program.
  - Current evidence: README says the ThetaEvolve-inspired `ttt_rl` plugin
    writes clipped-reward training data and is not a real GRPO/RL trainer.
    `papers/README.md` likewise says there is no online RL/GRPO training loop,
    checkpoint management, resume semantics, or lazy-penalty dynamics.
    Existing README TODOs group ThetaEvolve with paper-inspired approximations,
    but README does not require a `2511.23473` source-specific boundary for
    batch-sampled dynamic environments, large database scaling, lazy penalties,
    reward-shaping parameters, GRPO telemetry, checkpoint provenance,
    evaluator caveats, transfer reports, throughput reports, or benchmark
    comparison claims.
  - Required result: if README mentions ThetaEvolve, test-time learning,
    GRPO/RL training, lazy penalties, reward shaping, batch sampling, large
    program databases, trained checkpoints, or ThetaEvolve benchmark results,
    keep wording source-scoped until manifests and reports include the
    `2511.23473` source row, PDF/code hashes, dynamic-environment metadata,
    batch-sampling records, lazy-penalty and reward-shaping schemas, training
    and checkpoint artifacts, evaluator-compatibility caveats,
    AlphaEvolve/ShinkaEvolve/OpenEvolve comparison rows, database-size and
    batch-throughput ablations, checkpoint-transfer rows, and a clear
    distinction between clipped-reward JSONL export and actual test-time RL.

- [ ] Keep README ImprovEvolve wording scoped until modular-operator execution
      evidence exists.
  - Spec evidence: local arXiv `2602.10233`, `ImprovEvolve: Ask AlphaEvolve
    to Improve the Input Solution and Then Improvise`, by Kravatskiy,
    Khrulkov, and Oseledets evolves a class with `generate_config`, `improve`,
    and `perturb` methods, then executes those methods through a two-stage
    basin-hopping validation loop with scheduled perturbation intensity,
    monotonic acceptance, GigaEvo outer evolution, and benchmark claims for
    hexagon packing and the second autocorrelation inequality. It reports
    Table 1 values including `HEX 11` `3.9245` vs AlphaEvolve `3.9301`,
    `HEX 12` `3.9416` vs AlphaEvolve `3.9419`, and human-edited ACI2
    `0.96258` vs AlphaEvolve `0.96102`; Table 3 additionally tracks HEX
    `13..30` generalization and human-edited variants.
  - Current evidence: README describes the ImprovEvolve-inspired modular
    plugin as static prompt guidance: it does not select, execute, or log a
    `generate_config`/`improve`/`perturb` operation, and its metadata marks
    execution/enforcement false. Existing README TODOs group ImprovEvolve with
    paper-inspired approximations, but README does not require a `2602.10233`
    source-specific boundary for interface enforcement, basin-hopping records,
    perturbation schedules, human-edited variants, GigaEvo-backbone relation,
    HEX/ACI2 benchmark results, ablations, model/provider provenance, or
    compute-budget claims.
  - Required result: if README mentions ImprovEvolve, modular search,
    `generate_config`, `improve`, `perturb`, basin-hopping validation,
    scheduled perturbations, `ImprovEvolve+E`, hexagon-packing improvements,
    ACI2 improvements, or GigaEvo-backed modular execution, keep wording
    source-scoped until manifests and reports include the `2602.10233` source
    row, PDF/code hashes, interface schemas, executed validation-loop
    artifacts, perturbation and seed records, human-edit provenance,
    benchmark/baseline rows, ablation and budget reports, model/provider
    provenance, and a clear distinction between static prompt guidance and
    ImprovEvolve execution.

- [ ] Keep README MadEvolve wording scoped until parameter-optimization and
      innovation-report evidence exists.
  - Spec evidence: local arXiv `2602.15951`, `MadEvolve: Evolutionary
    Optimization of Cosmological Algorithms with Large Language Models`,
    presents AlphaEvolve-like scientific algorithm evolution with explicit
    free-parameter tracking, greedy one-shot and autodiff/Adam inner
    optimization, JAX/`vmad` differentiability constraints, hybrid
    MAP-Elites/island/elite population management, UCB-style model routing,
    generated scientific reports, and BAO, 21cm, and tSZ cosmology results.
    It reports Table 1 improvements from `0.752` to `0.924` for standard BAO
    reconstruction, `0.933` to `0.959` for iterative BAO reconstruction,
    `0.743` to `0.971` for 21cm tidal reconstruction, and tSZ loss reduction
    from `0.613` to `0.230`, plus Table 2/3 run and model-contribution
    statistics across `2,126` generated programs.
  - Current evidence: README labels MadEvolve as background context with no
    MadEvolve implementation; `papers/README.md` says there is no
    free-parameter optimization or innovation report. Existing README TODOs
    keep paper-inspired framework rows scoped generally, but README does not
    require a `2602.15951` source-specific boundary for parameter schemas,
    inner optimizer records, optimized-value source injection,
    differentiability/operator validation, generated report sections, per-task
    benchmark rows, run statistics, model-contribution statistics, compute
    budgets, overfitting/reward-hacking caveats, hosted report artifacts, or
    public code/source status.
  - Required result: if README mentions MadEvolve, domain evolution,
    free-parameter optimization, nested optimization, autodiff/JAX/vmad
    support, generated innovation reports, BAO/21cm/tSZ MadEvolve results,
    UCB model-contribution statistics, or MadEvolve public code availability,
    keep wording source-scoped until manifests and reports include the
    `2602.15951` source row, PDF/code hashes, parameter and optimizer schemas,
    executed inner-loop artifacts, differentiability checks, report-generator
    artifacts, benchmark/baseline/result rows, success/improvement/model
    contribution tables, compute environment, task prompts/evaluators,
    reward-hacking and over-parameterization caveats, madevolve.org report
    links, and a clear distinction between LibreEvolve's current generic
    evolution surfaces and MadEvolve execution semantics.

- [ ] Keep README CausalEvolve wording scoped until causal-scratchpad evidence
      exists.
  - Spec evidence: local arXiv `2603.14575v2`, `CausalEvolve: Towards
    Open-Ended Discovery with Causal Scratchpad`, adds causal memory to
    AlphaEvolve-like search: LLM-generated outcome-level factors and executable
    factor code, CausalPlanner MAB interventions over factor directions,
    procedure-level factor discovery from accumulated trials, approximate
    treatment-effect estimates, surprise-pattern detection, abductive reasoning
    for new factors/hypotheses, and four-task comparisons against
    ShinkaEvolve, CausalPlanner(Meta), and COAT. Table 1 reports final-step
    CausalEvolve mean/best values of `0.568`/`0.576` on Hadamard,
    `0.793`/`0.809` on second autocorrelation, `2.476`/`2.564` on circle
    packing, and `38.89`/`40.00` on AIME with Grok-4.1-fast-reasoning.
  - Current evidence: README says the causal plugin is a lightweight
    token-pattern heuristic, not CausalEvolve's causal scratchpad, and
    `papers/README.md` says detected factors are fixed local token-pattern
    categories rather than LLM-discovered causal variables. Existing README
    TODOs keep paper-inspired plugin rows scoped generally, but README does not
    require a `2603.14575` source-specific boundary for POMDP/SCM framing,
    executable outcome factors, directional interventions, procedure factors,
    treatment effects, surprise patterns, abductive hypotheses, benchmark rows,
    ablations, seed/step schedules, or model provenance.
  - Required result: if README mentions CausalEvolve, causal scratchpads,
    outcome-level factors, procedure-level factors, causal planning,
    treatment-effect guidance, surprise-pattern reasoning, abductive causal
    hypotheses, or CausalEvolve benchmark improvements, keep wording
    source-scoped until manifests and reports include the `2603.14575` source
    row, PDF/code hashes, factor-generation prompts, executable factor metrics,
    intervention/action records, scratchpad memory artifacts, procedure-factor
    and treatment-effect tables, abduction outputs, benchmark/baseline/result
    rows, model/seed/step provenance, paper license and code/source status,
    and a clear distinction between fixed token-pattern factor guidance and
    CausalEvolve causal-scratchpad execution.

- [ ] Keep README DeepEvolve wording scoped until cross-file research/debug
      loop evidence exists.
  - Spec evidence: local arXiv `2510.06056v1`, `Scientific Algorithm Discovery
    by Augmenting AlphaEvolve with Deep Research`, augments algorithm evolution
    with deep research through planning, searching, writing proposals with
    pseudo-code, cross-file coding, evaluation, evolutionary selection,
    reflection checkpoints, debugging attempts, and nine benchmark tasks with
    performance/runtime and execution-success tables. Table 2 reports score
    gains such as Molecular Translation `0.1885` to `0.2562`, Circle Packing
    `0.3891` to `2.9806`, and Polymer Prediction `0.6770` to `0.7714`, while
    Table 3 reports debugging success-rate gains such as Open Vaccine `0.130`
    to `0.990` and Circle Packing `0.540` to `1.000`.
  - Current evidence: README says the DeepEvolve-inspired retrieval plugin
    injects best-effort arXiv/web-search summaries and explicitly states that
    it is not a full hypothesis-refinement loop, semantic literature selector,
    source-content verification system, or systematic DeepEvolve-style
    debug/refinement loop. Existing README TODOs scope retrieval provenance,
    but README does not require a `2510.06056` source-specific boundary for
    plan/search/write artifacts, proposal pseudo-code, cross-file edit
    localization, debugging attempts, reflection agents, algorithm-description
    records, nine-task benchmark rows, runtime budgets, execution-success
    ablations, or qualitative idea-scoring claims.
  - Required result: if README mentions DeepEvolve, deep research, proposal
    writing, cross-file code editing, automatic debugging, reflection,
    hypothesis refinement, external research-guided evolution, or DeepEvolve
    benchmark improvements, keep wording source-scoped until manifests and
    reports include the `2510.06056` source row, PDF/code hashes,
    plan/search/write proposal artifacts, retrieved-source evidence,
    cross-file coding and debugging records, algorithm-description fields,
    benchmark/baseline/result rows, execution-success and ablation tables,
    runtime/GPU budgets, idea-quality judge records, paper license and code
    repository status, and a clear distinction between bounded retrieval
    context and DeepEvolve execution semantics.

- [ ] Keep README MAP-Elites wording scoped until illumination evidence exists.
  - Spec evidence: local arXiv `1504.04909`, `Illuminating search spaces by
    mapping elites`, by Jean-Baptiste Mouret and Jeff Clune is a preliminary
    draft dated April 21, 2015 with cached SHA-256
    `df7344343b14893a1d79a5459c1f56db50562e246d132cd0269f5201d1455872`.
    It defines MAP-Elites as an illumination algorithm that returns a feature-
    performance map of elites across user-chosen behavior dimensions, with
    explicit feature descriptors, discretized cells, random initialization,
    variation from selected elites, per-cell replacement, and reports for
    global performance, global reliability, precision, and coverage. Its
    experiments include modular neural-network retina maps, simulated soft-
    robot morphology maps, and a real soft-arm map.
  - Current evidence: README describes LibreEvolve's MAP-Elites archive as a
    local 3D quality-diversity grid plus retained elite list, with default
    axes based on archive selection score, complexity, and TF-IDF diversity,
    and configurable descriptor axes over metrics/metadata. Existing README
    TODOs scope descriptor claims to insertion-time coordinates, but README
    does not require a `1504.04909` source-specific boundary for paper
    pseudocode, user-chosen feature descriptor contracts, illumination metrics,
    feature-performance map exports, visualization artifacts, unfilled-cell
    diagnostics, lineage/stepping-stone analysis, benchmark/domain
    reproduction, or descriptor rebin compatibility evidence.
  - Required result: if README mentions MAP-Elites, illumination, behavior
    descriptors, feature-performance maps, archive coverage, reliability,
    precision, elite maps, or paper-faithful quality-diversity behavior, keep
    wording source-scoped until manifests and reports include the `1504.04909`
    source row, PDF hash, `b(x)`/`f(x)` schemas, dimension/discretization
    records, initialization/variation/replacement records, full map exports,
    coverage/reliability/precision/global-performance reports, visualization
    artifacts for Figures 3-7 style maps, lineage/parent-distance evidence,
    retina/simulated-soft-robot/physical-soft-arm benchmark schedules,
    descriptor compatibility tests, and a clear distinction between
    LibreEvolve's current 3D archive and MAP-Elites illumination semantics.

- [ ] Keep README hardness-of-approximation wording scoped until proof-element
      artifacts exist.
  - Spec evidence: local arXiv `2509.18057v7`, `Reinforced Generation of
    Combinatorial Structures: Hardness of Approximation`, by Ansh Nagda,
    Prabhakar Raghavan, and Abhradeep Thakurta was submitted as v7 on March 9,
    2026 with cached SHA-256
    `32eb8c787527bf8674ec22fd08ee6e1108179e88d97300e110286270c041e842`
    and CC BY 4.0 metadata. It uses AlphaEvolve to produce finite proof
    elements for complexity theory, including Ramanujan graph witnesses,
    MAX-k-CUT gadgets, and metric-TSP equation gadgets. It reports
    AlphaEvolve-evolved verifier speedups around `10,000x`, uses judge-LLM plus
    synthetic correctness checks plus human inspection for fast verifiers, and
    separates proxy search scores, independent brute-force verification, human
    inspection, and mathematical lifting/proof arguments.
  - Current evidence: README TODOs already say theoretical-CS AlphaEvolve
    wording should remain scoped until proof-element source tracking exists,
    and `papers/README.md` marks `2509.18057` as background only with no graph/
    certification benchmark. README does not require a detailed source-specific
    boundary for graph/gadget inventories, verifier runtime/correctness
    artifacts, final brute-force verifier outputs, theorem/proof cross-links,
    lifting-framework metadata, human-inspection attribution, or SOTA/baseline
    comparison rows.
  - Required result: if README mentions AlphaEvolve complexity-theory results,
    hardness of approximation, MAX-k-CUT, metric TSP, random regular graph
    certification, Ramanujan graph witnesses, proof elements, verifier speedups,
    or theorem-lifting applications, keep wording source-scoped until manifests
    and reports include the `2509.18057` source row, PDF/artifact hashes,
    graph/gadget schemas, verifier-speed and correctness records, judge-LLM and
    human-inspection records, brute-force verification outputs, theorem/proof
    cross-links, baseline/SOTA rows for `0.987`, `0.9649`, and `111/110`,
    source/repository status, human/proof-handoff attribution, and a clear
    distinction between generic LibreEvolve evaluator validation and
    AlphaEvolve-discovered complexity-theory proof elements.

## Architecture Description
