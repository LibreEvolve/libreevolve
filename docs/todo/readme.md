# README Todo: Incorrect or Unsupported Claims

This list tracks README statements that are inaccurate, misleading, or too
strong after comparing the current code, `papers/`, and AlphaEvolve sources.

## AlphaEvolve Comparison Table

## Research References and Bundled Papers

## Feature Claims

- [ ] Keep README evaluator-contract wording scoped to local validity gating
      until paper-facing scalar metric reports exist.
  - Spec evidence: AlphaEvolve Section 2.1 describes evaluator outputs as
    scalar metrics maximized by convention, and Figure 3 shows a Python
    evaluator returning `dict[str, float]`.
  - Current evidence: README correctly documents LibreEvolve's stricter local
    contract: `evaluate()` returns every declared scalar metric plus reserved
    boolean `is_valid`, while `outputs`/`program_output` carry non-scalar
    evidence separately. README also documents metric direction/bounds
    normalization for local archive scoring. It does not yet describe a
    benchmark/report contract that strips local control fields from
    paper-facing metric tables or shows minimize-to-maximize transforms.
  - Required result: when paper-facing evaluator metric reports land, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes the implemented LibreEvolve validity gate from
    AlphaEvolve-comparable scored scalar metrics.

- [ ] Keep README multi-evaluator wording scoped until evaluator-oracle
      composition evidence exists.
  - Spec evidence: AlphaEvolve describes feedback from one or more evaluators,
    with Section 2.4 separating a user-provided evaluation function from
    optional cascades and LLM-generated feedback.
  - Current evidence: README can describe a local cascade validator with
    stages/samples/thresholds and optional LLM feedback graders. It does not
    yet document independent evaluator/oracle sources, their authority,
    metric ownership, conflict/merge policy, or how evaluator disagreements
    affect validity, score reporting, archive admission, and prompt feedback.
  - Required result: when evaluator-oracle composition metadata lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes local staged validation and feedback graders from
    AlphaEvolve-style feedback from one or more independent evaluators.

- [ ] Keep README grounding claims scoped until incorrect-suggestion filtering
      evidence exists.
  - Spec evidence: AlphaEvolve states that code execution and automatic
    evaluation ground LLM-directed evolution and let the system avoid
    incorrect suggestions from the base LLM while using feedback to discover
    candidates substantially different from the initial pool.
  - Current evidence: README can describe local evaluator execution, strict
    result validation, the reserved `is_valid` gate, rejected-candidate
    diagnostics, malformed-output failures, and bounded failure feedback. It
    does not yet describe a paper-facing proposal-lifecycle report proving
    that incorrect LLM suggestions were caught by execution/evaluation,
    excluded from accepted discovery claims, and reused as feedback in
    subsequent search.
  - Required result: when proposal-lifecycle filtering reports land, update
    README, ROADMAP, papers index, and code/paper TODOs together with backend
    and proposal ids, mutation hashes, evaluator outcomes, validity/admission/
    retention status, rejection reasons, evaluator-oracle sufficiency,
    feedback/failure-memory linkage, and false-acceptance/false-rejection
    review fields so README distinguishes local validity mechanics from
    AlphaEvolve-style grounding against incorrect base-LLM suggestions.

- [ ] Keep README backtracking wording scoped until abandoned-hypothesis
      branch evidence exists.
  - Spec evidence: AlphaEvolve's Introduction describes discovery as including
    ideation, exploration, backtracking on unpromising hypotheses,
    experimentation, and validation; Section 2.4 says cascades can prune less
    promising solutions quickly.
  - Current evidence: README can describe rejected candidates, quarantine
    streams, bounded failure feedback, proposal metadata, and run-local
    hypothesis summaries. It should not imply that LibreEvolve records
    branch-level hypothesis abandonment, backtracking targets, or redirected
    sampling after an idea family becomes unpromising.
  - Required result: when hypothesis-branch reports land, update README,
    ROADMAP, papers index, and code/paper TODOs with branch ids,
    proposal/idea-family labels, explored candidate ids, evaluator/cascade
    evidence, abandonment or backtrack reasons, fallback target, prompt and
    failure-memory linkage, suppression/retry policy, resumed-search outcome,
    and claim-readiness checks.

- [ ] Keep README multiple-score prompt-context wording scoped until
      metric-diverse inspiration evidence exists.
  - Spec evidence: AlphaEvolve Section 2.4 says multiple metrics can improve a
    target metric by placing programs that excel under different evaluation
    criteria into prompts, each as a different definition of "good".
  - Current evidence: README documents declared metrics, direction/bounds
    normalization, selection scores, objective-vector diagnostics, metric
    overlays, metric-targeted parent/inspiration sampling, and prompt context
    filters/ranking. It should not imply those surfaces prove that a rendered
    prompt intentionally included a metric-diverse slate of inspirations or
    labelled each prompt-visible program by the metric niche it represents.
  - Required result: when metric-diverse inspiration selection lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes current metric bookkeeping and one-at-a-time metric-targeted
    sampling from AlphaEvolve-style prompt conditioning on programs that are
    high-performing under different metrics in the same prompt.

- [ ] Keep README evaluator-entrypoint wording scoped to external validators
      until embedded `evaluate(eval_inputs)` evidence exists.
  - Spec evidence: AlphaEvolve Section 2.1 and Figure 3 show the codebase
    skeleton exposing `evaluate(eval_inputs) -> dict[str, float]`, which invokes
    the evolved blocks and returns scores for the generated program.
  - Current evidence: README can describe local validators, configured stages,
    direct evaluator entrypoint provenance, and candidate imports in
    problem-local validators. It should not imply that external `validate.py`
    execution is the same as a candidate-owned `evaluate` function wired into
    the evolved skeleton.
  - Required result: when embedded evaluator-entrypoint support or report
    evidence lands, update README, ROADMAP, papers index, and code/paper TODOs
    with `evaluate` callable provenance, eval-input datasets, skeleton/block
    coupling, isolation policy, and score-field mapping.

- [ ] Keep README Figure 1/Figure 2 architecture wording scoped until
      process-diagram provenance exists.
  - Spec evidence: AlphaEvolve Figure 1 shows the high-level "Human defines
    What? / AlphaEvolve figures out How?" overview with LLM ensemble, prompt
    sampler, evaluator pool, and program database. Figure 2 expands the
    controller loop from database sampling through prompt construction, LLM
    generation, diff application, evaluator execution, and database admission.
  - Current evidence: README has its own Mermaid workflow and architecture
    sections describing seed programs, LLM mutation, cascade evaluation,
    MAP-Elites, island migration, and backend reward. Those diagrams are useful
    local documentation, but README does not document Figure 1/Figure 2 exhibit
    IDs, node/edge-to-component mappings, implemented/divergent node status,
    source PDF/caption locations, rendered diagram artifact hashes, or links
    from each displayed step to prompt-history, LLM-call, evaluator,
    candidate-history, database, and controller-state artifacts.
  - Required result: when Figure 1/Figure 2 process-diagram provenance lands,
    update README, ROADMAP, papers index, and matching TODOs so README
    distinguishes local workflow explanation from reproduced AlphaEvolve
    architecture/process exhibit evidence.

- [ ] Keep README evaluator-workload wording scoped until inner-search and
      ML-training provenance exists.
  - Spec evidence: AlphaEvolve Section 2.1 says an evaluator may perform a
    simple property check, run an evolved search algorithm, or train and
    evaluate a machine-learning model before returning scalar metrics.
  - Current evidence: README documents local validators, configured stages,
    samples, retries, seeds, budgets, artifact copy-out, dependency provenance,
    and environment audit records. It should not imply those invocation records
    prove AlphaEvolve-style support for search/training evaluators unless
    reports also identify workload type, dataset/split identity, training or
    inner-search budget, checkpoint/artifact policy, randomized initialization
    semantics, and score-field linkage.
  - Required result: when evaluator-workload provenance lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README distinguishes
    quick local validator execution from evaluator workloads that train models
    or run substantial search loops.

- [ ] Keep README candidate-language wording scoped to the Python-primary
  boundary record versus real language/build runners.
  - Spec evidence: AlphaEvolve tasks can define program artifacts and
    evaluator interfaces over codebases and task-specific solution
    representations, so README wording should distinguish the current local
    Python-primary file-set boundary from full arbitrary-language or
    problem-defined candidate abstractions.
  - Current evidence: README documents that LibreEvolve evolves bounded UTF-8
    code file sets rather than arbitrary problem-defined solution objects,
    marks that as a deliberate current divergence from AlphaEvolve's flexible
    solution-abstraction API, records `policies.candidate_language` with schema
    `libreevolve.candidate_language_policy.v1`, and says that arbitrary
    language/build-system runner surfaces are unsupported. README also states
    that seed workspaces still require a Python primary compatibility file and
    that non-Python evolve-block marker syntaxes are rejected with
    `unsupported_evolve_block_marker_syntax` instead of being treated as
    language-aware skeleton regions.
  - Required result: when configured language runners, build-system runner
    contracts, language-aware evolve-block grammars, or problem-defined
    candidate-abstraction hooks land, update README, ROADMAP, papers index,
    and code/paper TODO entries together so README neither underclaims the
    current manifest-visible boundary policy nor overclaims AlphaEvolve-grade
    arbitrary-language/codebase support.

- [ ] Keep README evolve-block integration wording scoped until
      minimal-marker evidence exists.
  - Spec evidence: AlphaEvolve Section 2.1 says evolve-block markers enable
    integrating with existing codebases using only minimal changes by adding
    special comments around evolvable blocks.
  - Current evidence: README can document Python evolve-block marker syntax,
    marker validation, fail-closed unsupported non-Python markers, workspace
    materialization, and full-workspace export. It does not yet document
    paper-facing evidence that an existing codebase was integrated with a
    marker-only or minimal setup diff while preserving non-evolved skeleton
    code and evaluator invocation.
  - Required result: when minimal-marker integration records land, update
    README, ROADMAP, papers index, and code/paper TODO entries together so
    README distinguishes local marker parsing and workspace mechanics from
    AlphaEvolve-style existing-codebase integration evidence.

- [ ] Keep README candidate-abstraction wording scoped to current divergence
      until abstraction-choice evidence exists.
  - Spec evidence: AlphaEvolve Section 2.1 and Discussion say users can choose
    different candidate abstractions for the same problem, and those choices
    carry biases: constructor functions can favor highly symmetric solutions,
    while customized search algorithms may work better for non-symmetric
    solutions.
  - Current evidence: README says LibreEvolve currently uses a deliberate
    code-file-set abstraction with a primary text file and lacks first-class
    non-code serializers or paired solution/search APIs. It does not describe
    benchmark metadata that records why one abstraction was selected, whether
    the problem is symmetric/non-symmetric, or how alternative abstractions
    performed under comparable budgets.
  - Required result: when abstraction-choice metadata, benchmark rationale,
    problem-structure labels, paired solution/search APIs, or equal-budget
    abstraction-comparison reports land, update README, ROADMAP, papers index,
    and code/paper TODOs so README distinguishes a documented divergence from
    AlphaEvolve-style abstraction-selection evidence.

- [ ] Keep README seed-provenance wording scoped to source identity until
      initial-program idea provenance exists.
  - Spec evidence: AlphaEvolve Section 2.1 makes the initial solution and
    optional background knowledge part of the task specification, and Section
    3.1 reports matrix targets where researchers seeded the initial program
    with their own ideas, such as stochastic evaluation or evolutionary
    approaches.
  - Current evidence: README documents seed source safety and provenance,
    including `seed_source_path`, `seed_source_kind`, `seed_index`,
    `problem.seed_sources`, skipped-seed diagnostics, inline seed labels, and
    generation-0 baselines. It does not document benchmark metadata that
    classifies initial programs by idea origin, records injected human or
    prior-art ideas, or compares simple/random and idea-seeded starts under a
    benchmark report.
  - Required result: when benchmark seed idea-origin metadata and seed-variant
    result evidence land, update README, ROADMAP, papers index, and code/paper
    TODO entries together so README does not imply source-path provenance is
    sufficient for AlphaEvolve-style human-seeded collaboration claims.

- [ ] Keep README seed-validity wording scoped to permissive examples versus
      AlphaEvolve-strict complete starts.
  - Spec evidence: AlphaEvolve Section 2.1 describes the initial implementation
    as complete but rudimentary, with the task skeleton and evaluator able to
    invoke it before evolution.
  - Current evidence: README documents valid/suboptimal seeds and deliberately
    invalid optimization-pressure seeds, including `hello_world`, and states
    that runs can record invalid seed baselines. That is useful prototype
    behavior, but it is not the same as a strict AlphaEvolve initial-program
    contract where every selected seed is complete, runnable, and validator
    valid before mutation begins.
  - Required result: when strict seed-validity policy/reporting lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes permissive invalid seed baselines from benchmark claims that
    require complete AlphaEvolve-style initial implementations.

- [ ] Keep README problem-formulation wording scoped until expert provenance
      exists.
  - Spec evidence: AlphaEvolve Section 3.2 reports that many mathematical
    problems were suggested by external mathematicians who advised on how to
    formulate them as AlphaEvolve inputs, while Section 2.1 treats task
    definition and optional background knowledge as human-provided setup.
  - Current evidence: README documents problem/source provenance, context file
    selection, local paper context, and seed source identity. It does not yet
    document benchmark metadata for expert contributor roles, problem-origin
    records, formulation advice, evaluator/objective rationale, or parameter
    scope decisions.
  - Required result: when expert formulation provenance and validation lands,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so README distinguishes context-source artifact tracking from
    AlphaEvolve-style human expert problem-formulation evidence.

- [ ] Keep README robustness and versatility wording scoped until early-user
      feedback provenance exists.
  - Spec evidence: AlphaEvolve's Acknowledgements say early users and
    collaborators supplied diverse use cases and insightful feedback that
    shaped the system into a more robust and versatile tool.
  - Current evidence: README can describe implemented surfaces, local examples,
    paper/status rows, expert formulation gaps, and domain-owner review gaps.
    It does not document feedback-provenance records for early-user or
    collaborator use cases, affected workflow areas, resulting changes,
    validation outcomes, or privacy/redaction policy.
  - Required result: when use-case feedback provenance lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes local feature breadth and smoke examples from
    AlphaEvolve-style robustness or versatility claims backed by diverse
    collaborator feedback.

- [ ] Keep README acknowledgement wording scoped until review/support/advice
      role evidence exists.
  - Spec evidence: AlphaEvolve's Acknowledgements separately credit white-paper
    review, early explorations and discussions, support/advice, practical
    application management advice, and application-specific reviewing.
  - Current evidence: README can describe local project status, examples,
    expert formulation gaps, systems owner/reviewer gaps, early-user feedback
    gaps, and contribution-role gaps. It does not document paper-process
    acknowledgement records for review/support/advice roles, nor distinguish
    those roles from implementation authorship, domain validation, deployment
    signoff, or feedback-backed robustness claims.
  - Required result: when acknowledgement-role metadata lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README separates
    white-paper review, support/advice, practical-application management
    advice, and application-review acknowledgements from technical
    AlphaEvolve-spec evidence.

- [ ] Keep README paper-author wording scoped until publication-author
      metadata exists.
  - Spec evidence: AlphaEvolve's Author information and Contributions sections
    separately record equal contributors, manuscript writers, paper-input
    contributors, and corresponding authors.
  - Current evidence: README can describe local project status, source papers,
    paper-artifact roles, acknowledgement-role gaps, and contribution-role
    gaps. It does not document publication-author metadata or distinguish that
    metadata from technical implementation authorship, artifact creation,
    domain validation, or acknowledgement review/support roles.
  - Required result: when paper-author metadata lands, update README, ROADMAP,
    papers index, and code/paper TODOs together so README separates equal
    contributor, manuscript-writing, paper-input, and corresponding-author
    records from AlphaEvolve technical capability or validation evidence.

- [ ] Keep README source-affiliation wording scoped until title-page
      affiliation metadata exists.
  - Spec evidence: page 1 of the AlphaEvolve PDF gives the title-page
    affiliation line `Google DeepMind1` and footnotes `1See Acknowledgments and
    Author information section.` and `*Equal contributions.`
  - Current evidence: README states LibreEvolve is independent and not
    affiliated with or endorsed by Google DeepMind, and active TODOs cover
    publication-author roles plus source-PDF version/rights metadata. README
    does not document paper-source affiliation/organization metadata, title-page
    footnote text, author-marker mapping, or how those paper-source facts
    differ from local project affiliation and endorsement boundaries.
  - Required result: when title-page affiliation metadata lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README separates
    source-paper affiliation and equal-contribution footnotes from
    LibreEvolve's independent project status, publication-author metadata, and
    AlphaEvolve technical capability evidence.

- [ ] Keep README system-development provenance scoped until contribution-role
      evidence exists.
  - Spec evidence: AlphaEvolve's Contributions section separately attributes
    system design/implementation phases, project vision and problem scoping,
    the first benchmark used for iterating on AlphaEvolve, infrastructure
    maintenance, code reviews, team coordination, and research-program
    supervision.
  - Current evidence: README can describe the current codebase, tests, runtime
    manifests, and contributor openness, but it does not document a
    contribution-role schema that links implementation phases, infrastructure
    ownership, benchmark-iteration ownership, code-review responsibility, or
    coordination/supervision roles to source sections and project artifacts.
  - Required result: when contribution-role metadata lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes local repository history from AlphaEvolve-style
    system-development provenance and does not overclaim comparable
    implementation, infrastructure, review, or coordination evidence.

- [ ] Keep README workspace-topology diagnostics scoped to current
  materialization and command preflight coverage.
  - Spec evidence: AlphaEvolve-style codebase evolution should leave stable,
    inspectable evaluator feedback for generated invalid artifacts, especially
    as task-defined program artifacts and workspace surfaces grow beyond the
    current local file-set prototype.
  - Current evidence: README documents that collision checks are still
    incomplete while also describing rejected normalized path collisions,
    case-folded host-path materialization preflights, structured
    `materialization_error` evaluation results, bounded redacted diagnostics,
    structured materialization `reason` and `paths`, exact snapshot
    materialization, link/junction rejection, static source-copy verification,
    and workspace topology command prevalidation for duplicate sources/targets,
    edit/delete/move conflicts, chained operations, host/case-folded target
    collisions, duplicate `PRIMARY` commands, and non-empty command bodies.
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
    multiple functions and components.
  - Current evidence: README can accurately describe Python-primary seed
    workspaces, multi-file candidates, topology mutations, materialization
    diagnostics, and `best_workspace/` export. It should not imply those
    mechanics prove AlphaEvolve-scale large-codebase behavior.
  - Required result: when a codebase-scale benchmark/report lands, update
    README, ROADMAP, papers index, and code/paper TODO entries with the
    generated-line/component counts, cross-file dependency edit evidence,
    evaluator budget, and quality-progress results that justify any
    AlphaEvolve Table 1 code-scale comparison.

- [ ] Keep README Table 1 wording scoped until capability-table exhibit
      provenance exists.
  - Spec evidence: AlphaEvolve Table 1 is a row-by-row FunSearch versus
    AlphaEvolve comparison covering code scale, language scope, evaluator
    duration/parallelism/accelerators, sample counts, model scale, prompt
    context/feedback, and single versus multiple metrics.
  - Current evidence: README has a high-level gap table and detailed sections
    for several Table 1-related capabilities, but it does not document a
    Table 1 exhibit record with stable row ids, exact comparison text, source
    PDF/caption location, row-to-gap mappings, rendered artifact hashes, or
    row-level implementation status.
  - Required result: when Table 1 exhibit provenance lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README can
    distinguish the reproduced capability-comparison table from the separate
    work needed to satisfy each Table 1 capability row.

- [ ] Keep README Figure 1 and Figure 2 process-diagram wording scoped until
      process-overview exhibit provenance exists.
  - Spec evidence: AlphaEvolve Figure 1 defines the high-level process among
    human task inputs, the LLM ensemble, prompt sampler, evaluator pool,
    program database, rich context, proposals, and quality feedback. Figure 2
    defines the expanded discovery-process diagram and controller pseudocode
    for sampling parents/inspirations, building prompts, generating and
    applying diffs, executing evaluators, and adding results to the database.
  - Current evidence: README describes LibreEvolve's loop, ensemble,
    evaluator, database, and diff mechanics, and related TODOs track many of
    those behaviors separately. It does not document Figure 1/2 exhibit IDs,
    diagram-node/edge labels, source page/caption locations, Figure 2
    pseudocode-line mappings, rendered artifact hashes, or step-to-code/TODO
    evidence links.
  - Required result: when Figure 1/2 process exhibit provenance lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README can
    explain which process-diagram steps LibreEvolve implements, which are
    partial or missing, and why process-diagram reproduction is separate from
    satisfying each underlying workflow capability.

- [ ] Keep README task-specification wording scoped until a unified
      AlphaEvolve input bundle exists.
  - Spec evidence: AlphaEvolve Section 2.1 and Figure 2 define a task
    specification as the user-provided initial program/components, evaluation
    code, prompt template and configuration, choice of existing or custom
    LLMs, and optional background knowledge.
  - Current evidence: README can accurately describe local problem folders,
    seed source provenance, evaluator source hashes, prompt variants, backend
    configuration, redacted/hash-backed effective config, and context-source
    diagnostics. It should not imply that those scattered records already form
    a single AlphaEvolve task-specification artifact with field-level
    readiness, omission diagnostics, and links to run evidence.
  - Required result: when a task-spec bundle lands, update README, ROADMAP,
    papers index, and code/paper TODOs with initial-program/workspace ids,
    evolvable spans, evaluator-code ids, prompt-template/config ids, backend/
    LLM choice ids, optional background-knowledge ids, source hashes/redaction
    status, and missing/unsupported field diagnostics.

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

- [ ] Keep README primary-prompt wording scoped until instruction/target
      provenance exists.
  - Spec evidence: AlphaEvolve Section 2.2 says the primary prompt comprises
    sampled previously discovered solutions plus system instructions on how to
    propose changes to a particular solution.
  - Current evidence: README can describe prompt templates, selected
    parent/inspiration metadata, parent-code rendering policy, prompt ids,
    prompt-size diagnostics, and mutation-instruction variants. It does not
    yet document a paper-facing prompt-core record that ties an instruction
    block/version/hash and provider message-role placement to the specific
    target solution and sampled supporting solutions for a mutation call.
  - Required result: when primary-prompt ingredient provenance lands, update
    README, ROADMAP, papers index, and code/paper TODO entries together so
    README distinguishes generic prompt rendering and template validation from
    AlphaEvolve-style target-specific prompt instruction evidence, including
    whether instructions were delivered as role-separated system/developer/user
    messages or as a serialized single prompt.

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
    registry also does not yet prove the `No evolution` setup where every
    prompt is built from the same initial program without database-selected
    parents, inspirations, previous-candidate feedback, or archive admission
    feedback. It also does not yet prove a paper-faithful
    `No context in the prompt` setup: the current registry disables
    parent/inspiration and feedback-like sections even though the paper
    describes removing explicit problem-specific context. README wording should
    require executed prompt-history proof that explicit context sources were
    absent, while separately reporting which current-program,
    parent/inspiration, rendered-result, failure, plugin, or retrieval sections
    were treated as core evolutionary prompt ingredients versus explicit
    context. It also does not yet prove the
    `Small base LLM only` setup where every mutation-generation call uses only
    one configured small/base-capable model and has no large-model eligibility,
    fallback, critique, or router leakage. It also does not yet prove the
    `No meta prompt evolution` setup where meta-prompt calls, prompt-template
    mutations, and prompt-program lineage updates are absent in the ablated run
    but enabled in the full-system comparator. It also does not yet prove the
    paper-specific `No full-file evolution` setup where only the tensor
    decomposition loss function is evolved; generic single-file/diff/no-topology
    labels should not be described as equivalent to that ablation.
    The report contract is also target-family generic: it validates declared
    targets but not Figure 8's matrix tensor-decomposition and kissing-number
    sphere-packing families, and it does not require per-target
    target-metric identity/direction/normalization or mean/standard-deviation
    curve summaries over three independent seeds.
  - Required result: when benchmark scripts emit executed equal-budget
    ablation reports, when component assertions are bound to supported runtime
    config controls, or when accelerator/async-worker budgets land, update
    README, ROADMAP, papers index, and code/paper TODO entries together so the
    README neither underclaims current token/configured-cost budget stops nor
    overclaims AlphaEvolve-style executed ablations. For `No full-file
    evolution`, require README wording to distinguish a real loss-function-only
    tensor-decomposition harness from broader localized-edit settings. Require
    README wording to distinguish `No evolution` registry labels from executed
    evidence that the same initial program was repeatedly prompted without
    evolutionary database feedback. Require
    README wording to distinguish `No context in the prompt` registry labels
    from executed prompt-history evidence of absent explicit context sources
    and from separate evidence about which normal evolutionary prompt sections
    remained present. Require README wording to distinguish generic
    `Small base LLM only` labels from executed backend telemetry proving a
    single small/base model actually handled every relevant generation call.
    Require README wording to distinguish generic
    `No meta prompt evolution` labels from executed prompt-history and
    call-ledger evidence that meta-prompt and prompt-mutation surfaces were
    disabled only for that ablation, with a frozen human-authored prompt
    identity/source/revision/context policy recorded for the human-prompter
    comparator. Require README wording to distinguish
    generic
    ablation-result schemas from
    Figure 8-equivalent matrix/kissing target-family reports with validated
    target-metric identity/direction/normalization and mean/standard-deviation
    curves.

- [ ] Keep README Figure 8 visual wording scoped until ablation-curve exhibit
      provenance exists.
  - Spec evidence: AlphaEvolve Figure 8 is a two-panel ablation plot with
    matrix tensor-decomposition curves on the left, kissing-number curves on
    the right, compute-budget fraction on the x-axis, aggregated target metric
    on the y-axis, named method curves, and shaded standard-deviation bands
    from three independent seeded runs.
  - Current evidence: README describes the ablation report contract, hashed
    curve artifacts, and open gaps for executable harnesses, component
    assertions, target-family coverage, and mean/std aggregation. It does not
    document Figure 8 exhibit IDs, panel definitions, series-to-variant legend
    mappings, exact paper legend labels, axis/scale metadata,
    color/style/shading parameters, source PDF/caption location, rendered plot
    artifact hashes, or links from plotted visuals to exact report rows and raw
    seed traces. The checked-in ablation registry currently uses
    `paper_label: "Full"` for the baseline even though Figure 8 labels that
    curve `Full method`, so README should not treat registry labels as exact
    paper-legend provenance yet.
  - Required result: when Figure 8 exhibit provenance lands, update README,
    ROADMAP, papers index, and matching TODOs so README distinguishes generic
    ablation-report artifacts from reproduced paper-quality Figure 8 visual
    evidence, including exact legend-label provenance such as `Full method`.

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
    plus generic cascade support elsewhere. It does not document an executed
    matrix benchmark runner that emits target/seed-level cascade traces, stage
    thresholds, per-stage rank/exactness diagnostics, pruning or early-stop
    reasons, and aggregation evidence linking executed cascades to the
    reported hit fraction.
  - Required result: when matrix cascade-run evidence lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes post-hoc per-seed report validation from AlphaEvolve
    Section 3.1-style repeated-seed cascade execution evidence.

- [ ] Keep README Table 2/Table 3 matrix-rank table wording scoped until table
      exhibit provenance exists.
  - Spec evidence: AlphaEvolve Table 2 is the selected main-text matrix-rank
    comparison table, and Appendix A Table 3 is the full 54-target version with
    caption-level aggregate counts, outcome coloring, complex-valued row
    caveats, companion Colab links, and the concurrent-work note for
    `<4, 5, 6>`.
  - Current evidence: README describes the Appendix A matrix registry and
    matrix report validation, while related TODOs cover baseline citations,
    row notes, target-suite curation, Figure 4 exhibit provenance,
    scalar-field evidence, and tensor-rank caveats. README does not document
    Table 2/Table 3 exhibit ids, selected-row versus full-table relation, row
    ordering, caption aggregate validation, color/outcome encoding,
    source/caption locations, rendered table artifacts/hashes, or links from
    table rows to registry/report/Colab evidence.
  - Required result: when Table 2/Table 3 matrix-rank table exhibit provenance
    lands, update README, ROADMAP, papers index, and code/paper TODOs together
    so README distinguishes reproduced paper-table exhibits from general
    Appendix A registry and matrix report-contract coverage.

- [ ] Keep README matrix outcome wording scoped until target-subset evidence
      exists.
  - Spec evidence: AlphaEvolve Table 2 says all parameters `m, n, p <= 5`
    matched or surpassed best-known ranks, while Appendix A Table 3 is a
    broader 54-target table that includes targets outside that subset.
  - Current evidence: README can cite the Appendix A registry and its aggregate
    outcome counts, but the registry includes larger-target `fell_behind` rows
    such as `mm_4x4x9` and `mm_6x6x6`. README should not imply that the full
    54-target Appendix A table is all matched/surpassed, or that the
    larger-target `fell_behind` rows contradict the narrower `m,n,p <= 5`
    main-text claim.
  - Required result: when matrix subset-scope reports land, update README,
    ROADMAP, papers index, and code/paper TODOs with named target subsets,
    inclusion predicates, row counts, outcome counts, out-of-scope row ids,
    source-caption/table linkage, and wording checks that separate Table 2's
    scoped main-text claim from Appendix A full-table aggregates.

- [ ] Keep README Appendix A row-note wording scoped until concurrent-work
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix A Table 3 includes row-level notes,
    including concurrent work [49] also finding a rank-90 algorithm for
    `<4, 5, 6>`.
  - Current evidence: README describes the Appendix A registry as target,
    rank, outcome, and exact-algorithm metadata, with separate gaps for
    baseline citations, curation, resource frontier, near-integrality, scalar
    fields, and Colab artifacts. It does not document row-level notes,
    concurrent-work attribution, independently matched result flags, or caveats
    for rows such as `mm_4x5x6`.
  - Required result: when Appendix A row-note provenance lands, update README,
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
    `dimensions` against the 54-row Appendix A Table 3 registry. It does not
    document target-suite curation metadata: the selection rule, sorted
    representative policy, omitted symmetry-equivalent targets, cutoff
    rationale, or included/excluded target justifications.
  - Required result: when Appendix A registry/report metadata captures
    target-suite curation and symmetry-equivalence provenance, update README,
    ROADMAP, papers index, and matching TODOs so README does not imply the
    54-row registry alone proves full paper-faithful suite construction.

- [ ] Keep README matrix-scaling wording scoped until resource-frontier
      reports exist.
  - Spec evidence: AlphaEvolve Appendix A notes that runs on matrix sizes
    beyond the reported suite often ran out of memory with 1000 random seeds
    on a single GPU accelerator, and that larger-size extension needs further
    optimization.
  - Current evidence: README documents matrix report contracts, Appendix A
    registry checks, one checked Strassen baseline bundle, generic runtime
    budget surfaces, and unsupported resource quotas. It does not document
    matrix-specific scaling attempts, accelerator-memory profiles,
    OOM/resource-exhaustion diagnostics, or target-exclusion rationale for
    sizes beyond the reported suite.
  - Required result: when matrix resource-frontier reports land, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes generic budget/resource metadata from AlphaEvolve Appendix
    A-style evidence about larger matrix target scaling limits.

- [ ] Keep README matrix wording scoped to result contracts until
      near-integrality prompt/evaluator evidence exists.
  - Spec evidence: AlphaEvolve Section 3.1 says the matrix prompt requested
    near-integral solutions and the reported decompositions were rounded to
    the nearest integer or half-integer before exactness verification.
  - Current evidence: README describes the matrix-result report contract,
    Appendix A registry, and checked Strassen baseline bundle, including
    coefficient-domain and exactness restrictions for AlphaEvolve-comparable
    reports. It does not yet document a matrix benchmark prompt/evaluator path
    that injects the near-integrality instruction, records raw-versus-rounded
    coefficient diagnostics, or links those diagnostics to per-seed exactness
    certificates produced during search.
  - Required result: when that benchmark prompt/evaluator evidence lands,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so README distinguishes report-schema validation from AlphaEvolve Section
    3.1 search-workflow parity.

- [ ] Keep README matrix wording scoped to final artifacts until sweep-space
      provenance exists.
  - Spec evidence: AlphaEvolve Figures 9a-9c show the 4x4 matrix program
    evolving a `sweep()` function that declares user-provided `hyper` ranges
    for optimizer, noise, clipping, discretization, and related search
    parameters.
  - Current evidence: README documents matrix result reports, Appendix A
    registry checks, the checked Strassen baseline bundle, and open
    near-integrality/scalar-field gaps. It does not yet document a matrix
    benchmark path that preserves candidate-produced sweep spaces, sampled
    configuration ids, per-sweep outcomes, or linkage from the selected sweep
    configuration to the final exact decomposition certificate.
  - Required result: when sweep-space provenance lands, update README,
    ROADMAP, papers index, and matching TODOs so README does not imply final
    matrix artifacts alone prove AlphaEvolve Figure 4/Figure 9 search-program
    parity.

- [ ] Keep README Appendix A Figure 9 wording scoped until magnified-diff
      exhibit provenance exists.
  - Spec evidence: AlphaEvolve Appendix A Figures 9a-9c are the three-panel
    magnified source/diff version of Figure 4's matrix program, showing the
    rank-48 4x4 search-program changes across ordered code excerpts. The
    displayed changes include optimizer, initialization, noise, clipping,
    hallucination/discretization/loss-penalty, and named sweep-field
    components.
  - Current evidence: README can document matrix result reports, Appendix A
    registry coverage, Figure 4 exhibit gaps, and Figure 9 sweep-space gaps.
    It does not document Figure 9a/9b/9c panel IDs, PDF page/caption locations,
    exact code line spans, source/diff excerpt artifact hashes, rendered/OCR
    text validation, panel continuity, semantic component labels for the shown
    code changes, or links from the appendix panels to matrix target rows,
    sweep metadata, exactness certificates, and companion source evidence.
  - Required result: when Appendix A Figure 9 magnified-diff exhibit
    provenance lands, update README, ROADMAP, papers index, and matching TODOs
    so README distinguishes reproduced appendix source/diff panels from
    Figure 4 main-text exhibit evidence, semantic change-component evidence,
    and generic sweep-space provenance.

- [ ] Keep README Figure 4 matrix-exhibit wording scoped until exhibit
      provenance exists.
  - Spec evidence: AlphaEvolve Figure 4 is the main-text matrix discovery
    exhibit, showing a concrete evolved 4x4 tensor-decomposition search-program
    diff and tying it to Section 3.1/Table 2 matrix rank-improvement results.
    The caption further says the example required 15 mutations, with
    non-trivial optimizer, weight-initialization, loss-function, and
    hyperparameter-sweep changes.
  - Current evidence: README documents matrix result reports, Appendix A
    registry checks, checked Strassen baseline evidence, and open
    near-integrality, scalar-field, baseline, and sweep-space gaps. It does
    not document Figure 4 exhibit ids, exact source diff excerpt
    artifacts/hashes, selected matrix target/result-row mappings, caption
    values, rendered visual/text artifact paths/hashes, rendering parameters,
    the 15-mutation accepted sequence, component-level mutation categories, or
    links from the displayed exhibit to matrix reports, certificates,
    notebooks, and paper-source evidence.
  - Required result: when Figure 4 exhibit provenance lands, update README,
    ROADMAP, papers index, and matching TODOs so README distinguishes
    reproduced main-text matrix exhibit evidence from general matrix benchmark
    readiness, Figure 4 mutation-lineage evidence, and Appendix A Figure 9
    sweep-space parity.

- [ ] Keep README matrix wording scoped to final reports until
      baseline-component provenance exists.
  - Spec evidence: AlphaEvolve Section 3.1 says matrix-decomposition search
    starts from a standard gradient-based algorithm with an initializer,
    reconstruction loss function, and Adam optimizer before evolving more
    sophisticated tensor-decomposition algorithms.
  - Current evidence: README documents matrix result reports, Appendix A
    registry coverage, checked Strassen artifacts, and open follow-ups for
    near-integrality, sweep provenance, scalar fields, and scaling limits. It
    does not yet document a matrix benchmark run record that inventories the
    generation-0 initializer/loss/optimizer components, records their source
    hashes/configuration, declares mutable versus fixed scopes, or links
    accepted mutations back to changed baseline components.
  - Required result: when matrix benchmark runs persist baseline component
    inventory and mutation-lineage records, update README, ROADMAP, papers
    index, and code/paper TODO entries together so README distinguishes final
    matrix result-report validation from AlphaEvolve Section 3.1
    baseline-to-evolved-program workflow evidence.

- [ ] Keep README matrix wording scoped to coefficient-domain validation until
      scalar-field evidence exists.
  - Spec evidence: AlphaEvolve Table 2 notes that some improved matrix
    algorithms use complex-valued multiplications and can be used for exact
    multiplication of complex or real-valued matrices, while Section 3.1
    contrasts characteristic-0 and finite-field-only results.
  - Current evidence: README describes matrix-result fields for coefficient
    domain and exactness, plus Appendix A target identity and checked Strassen
    baseline artifacts. It does not yet document scalar-field metadata,
    exact complex coefficient representation, characteristic/applicability
    claims, or certificate scope for real-versus-complex multiplication.
  - Required result: when matrix reports and certificates record scalar field,
    complex coefficient data, characteristic, and applicability evidence,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so README does not imply coefficient-domain validation is sufficient for
    AlphaEvolve-style complex-valued matrix result claims.

- [ ] Keep README matrix rank wording scoped until tensor-rank and recursive
      applicability caveats exist.
  - Spec evidence: AlphaEvolve Section 3.1 frames matrix improvements as
    low-rank tensor decompositions, and footnote 3 says some algorithms using
    fewer than 49 multiplications do not correspond to matrix-multiplication
    tensor decompositions and cannot be applied recursively to larger matrix
    multiplication.
  - Current evidence: README describes Appendix A target/rank/outcome
    validation, coefficient-domain/exactness fields, scalar-field gaps, and
    checked Strassen artifacts. It does not document algorithm-kind metadata,
    tensor-decomposition certificate scope, recursive applicability, or
    footnote-level caveats that separate tensor-rank evidence from
    non-recursive multiplication algorithms.
  - Required result: when matrix reports or companion metadata capture
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

- [ ] Keep README systems-metric wording scoped to finite report metrics versus
      calibrated Section 3.3 result claims.
  - Spec evidence: AlphaEvolve Section 3.3 reports concrete systems outcomes
    with units and comparison context, including scheduling resource recovery,
    Pallas/Gemini speedups and training-time reduction, hardware power/area
    objectives, and FlashAttention kernel plus pre/postprocessing speedups.
  - Current evidence: README documents that
    `libreevolve.systems_result_report.v1` requires finite metrics in
    optimization, held-out, and reference-correctness gates. It does not yet
    say those finite metrics must carry published-claim ids, units,
    denominators, baselines, aggregation rules, before/after windows, or
    deployment/runtime/synthesis context needed to compare them with
    AlphaEvolve Section 3.3 values.
  - Required result: once systems reports validate claim-calibrated metric
    records for scheduling, kernel, hardware, and compiler domains, update
    README, ROADMAP, papers index, and matching TODOs so README does not imply
    generic finite gate metrics reproduce AlphaEvolve result magnitudes.

- [ ] Keep README systems-result wording scoped until application-owner and
      domain-review provenance exists.
  - Spec evidence: AlphaEvolve Section 3.3 frames the Borg scheduling,
    Gemini/Pallas kernel, TPU RTL, and XLA/FlashAttention IR results as
    production-facing practical applications, and the Acknowledgements and
    Contributions sections identify the co-leads, advisors, reviewers,
    validation owners, TPU designers, and XLA reviewers involved in those
    domains.
  - Current evidence: README can describe systems report metrics, held-out
    gates, reference-correctness gates, deployment/reviewer evidence gaps, and
    artifact inventories. It does not yet state that AlphaEvolve-style
    practical systems claims also need domain-owner and reviewer provenance:
    responsible application role, review/signoff scope, validation/source data
    owner, production approval state, and links from calibrated metrics to the
    responsible domain team.
  - Required result: when systems reports or certification records add
    application-owner and domain-review provenance, update README, ROADMAP,
    papers index, and matching TODOs so README distinguishes local benchmark
    reports from domain-owner validated production or deployment claims.

- [ ] Keep README scheduling wording scoped to generic systems reports until
      ranking-only safety provenance exists.
  - Spec evidence: AlphaEvolve Section 3.3.1 says the Borg scheduling
    heuristic scores only machines already determined by Borg to be available
    and capable of running the pending job, so correctness is effectively by
    construction.
  - Current evidence: README documents systems result reports and artifact
    inventories, and notes that deployment evidence and domain-specific
    readiness gates remain open. It does not yet document scheduling-specific
    evidence that a heuristic only reorders feasible machines, preserves
    resource/capacity constraints, and cannot directly admit, reject, or place
    jobs outside the scheduler's feasibility boundary.
  - Required result: once scheduling report metadata captures feasibility
    filter provenance, ranking-only scope, resource invariants, and
    simulator/admission-boundary evidence, update README, ROADMAP, papers
    index, and matching TODOs so README does not imply generic systems report
    readiness proves Borg-style scheduling safety.

- [ ] Keep README scheduling wording scoped until vector-bin-packing
      formulation evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.1 formulates Borg scheduling as an
    online vector bin-packing problem with machines as CPU/memory-capacity
    bins, pending jobs as CPU/memory-demand items, stranded resources as the
    optimization motivation, and simulator feedback from historical workload
    and capacity snapshots.
  - Current evidence: README documents generic systems result reports and
    notes scheduling ranking-only safety, deployment, and Figure 6 evidence
    gaps. It does not yet document scheduling-specific problem-formulation
    evidence: bin/item schema, CPU/memory units and denominators,
    workload/capacity snapshot provenance, stranded-resource objective linkage,
    simulator input hashes, or mapping from the source data to `required` and
    `free` heuristic features.
  - Required result: once Borg-style scheduling formulation metadata lands,
    update README, ROADMAP, papers index, and matching TODOs so README
    distinguishes generic systems reports from AlphaEvolve-style scheduling
    problem setup before discussing safety, deployment, or fleet-recovery
    result claims.

- [ ] Keep README scheduling wording scoped to generic systems reports until
      interpretability/deployment-readiness evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.1 says the Borg scheduling
    heuristic was chosen over deep reinforcement learning because the code
    solution offered interpretability, debuggability, predictability, and ease
    of deployment, which were essential for a mission-critical system.
  - Current evidence: README documents generic systems result reports,
    deployment evidence gaps, and scheduling ranking-only safety gaps. It does
    not yet document scheduling-specific evidence for human-readable heuristic
    structure, operator/debug review, predictable behavior under edge cases,
    deployment-risk controls, or comparison against less interpretable learned
    policies.
  - Required result: once scheduling report metadata captures
    interpretability/debuggability review, predictability checks, deployment
    ergonomics, rollout-risk evidence, and baseline comparison against
    black-box approaches, update README, ROADMAP, papers index, and matching
    TODOs so README does not imply generic systems report readiness proves
    AlphaEvolve-style mission-critical deployment suitability.

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
    as a natural next step.
  - Current evidence: README documents provider budgets, systems-result
    schemas, benchmark contracts, and paper-result certification boundaries.
    It does not describe any LibreEvolve runtime, provider, compiler,
    evaluator, or benchmark component as an evolved optimization target for
    the tool itself, and it has no distillation dataset, training, or
    model-evaluation evidence derived from evolved candidates.
  - Required result: when self-improvement reports, deployment/adoption
    measurements, rollback/safety evidence, or distillation artifacts land,
    update README, ROADMAP, papers index, and matching TODOs so README neither
    underclaims concrete infrastructure improvements nor overclaims
    AlphaEvolve-style self-improving or model-uplift capability.

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
    the registry has that Colab-equivalent verifier-data surface yet.
  - Required result: when real target-family benchmark runners emit
    benchmark-grade hardening reports, negative fixtures, detector logs, and
    artifact inventories, and when Appendix B families gain executable
    construction/certificate validators, target baselines, construction-data
    exports, and verifier-code artifacts, update README, ROADMAP, papers index,
    and code/paper TODO entries together so README neither underclaims the
    checked smoke hardening evidence nor overclaims AlphaEvolve-comparable
    benchmark hardening.

- [ ] Keep README paper-source wording scoped until companion Colab artifacts
      are tracked.
  - Spec evidence: AlphaEvolve footnote 2 and Table 2 point readers to the
    accompanying `google-deepmind/alphaevolve_results` Colab notebook for
    discovered algorithms, mathematical results, and shown matrix
    decompositions.
  - Current evidence: README describes the local paper cache as PDF-only:
    `papers/README.md` plus CSV/JSON download manifests with canonical PDF
    byte counts and SHA-256 digests. It also describes future local
    Colab-equivalent construction exports and matrix notebooks, but it does
    not document the actual AlphaEvolve companion Colab as a tracked source
    artifact with URL/ref, digest, cache/readability checks, or claim mapping.
  - Required result: when companion-artifact manifest support lands, update
    README, ROADMAP, papers index, and code/paper TODO entries together so
    README distinguishes PDF-source validation, external AlphaEvolve Colab
    source evidence, and LibreEvolve-generated result notebooks/exports.

- [ ] Keep README paper-cache wording scoped until AlphaEvolve PDF version
      provenance is tracked.
  - Spec evidence: the local AlphaEvolve PDF header says
    `arXiv:2506.13131v1 [cs.AI] 16 Jun 2025`.
  - Current evidence: README describes the local paper cache as
    `papers/README.md` plus CSV/JSON download manifests with canonical PDF byte
    counts and SHA-256 digests. It does not explain that the current
    AlphaEvolve manifest row uses a floating arXiv PDF URL, nor that claim
    audits depend on the specific v1 source header/date rather than any future
    PDF served by the unversioned URL. Existing README TODOs scope companion
    Colab and Appendix B result revisions, but not source-PDF version identity.
  - Required result: after manifest support lands for arXiv source version,
    category/date, URL kind, expected header text/page, and version-pinned
    claim links, update README wording so paper-cache integrity claims
    distinguish content hash validation from source-version pinning.

- [ ] Keep README paper-cache wording scoped until source-PDF rights metadata
      is tracked.
  - Spec evidence: the local AlphaEvolve PDF header states
    `© 2025 Google DeepMind. All rights reserved`.
  - Current evidence: README states LibreEvolve's own MIT license and notes that
    the project is independent from Google DeepMind, while paper-cache wording
    describes local PDF byte/hash validation. It does not document source-PDF
    rights metadata for cached AlphaEvolve evidence, arXiv/license terms,
    excerpt or figure/table reproduction boundaries, or the distinction between
    repository licensing and third-party paper-source use rights.
  - Required result: after paper-source rights metadata lands in manifests and
    validators, update README wording so paper-cache and paper-derived-artifact
    claims include rights holder/year, rights statement or license id/text,
    source page/header location, allowed excerpt/reproduction policy, and a
    clear separation from LibreEvolve's own MIT license.

- [ ] Keep README follow-on AlphaEvolve math-source wording scoped until the
      expanded paper/repository are tracked.
  - Spec evidence: AlphaEvolve Section 3.2 says an upcoming paper would provide
    more examples and method details for the mathematical problems. Current
    primary-source evidence identifies arXiv `2511.02864`, `Mathematical
    exploration and discovery at scale`, and the
    `google-deepmind/alphaevolve_repository_of_problems` repository, whose
    README says it contains 67 problem descriptions and many Colab notebooks
    with prompts, verification code, initial programs, final evolved programs,
    and visualization or analysis code.
  - Current evidence: README can describe the local PDF cache for
    `2506.13131`, the original companion-Colab gap, Appendix B family/status
    coverage, and local Colab-equivalent export TODOs. It does not document
    the later arXiv paper, repository ref, problem/notebook inventory, or how
    those expanded sources affect claims about constructive-math completeness.
  - Required result: when follow-on source tracking lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README separates
    original AlphaEvolve paper parity, original companion-Colab evidence, and
    the later 67-problem mathematical-discovery source set.

- [ ] Keep README paper-index traceability wording scoped until TODO coverage
      cross-references are validated.
  - Spec evidence: `papers/README.md` presents a TODO coverage
    cross-reference table tying implementation-status rows to backlog
    evidence. README should not imply that the paper cache has complete
    semantic traceability to AlphaEvolve-alignment TODOs unless that map is
    validated, not merely maintained by hand.
  - Current evidence: README can describe paper-manifest validation,
    implementation-status table reconciliation, Appendix B registry checks,
    and ablation registry checks. A checked-in test lightly checks the
    `papers/README.md` cross-reference section, but the public validation
    command does not validate referenced TODO paths, grouped labels,
    active/completed classifications, or active open-gap presence.
  - Required result: when TODO coverage cross-reference validation lands,
    update README, ROADMAP, papers index, and code/paper TODOs together so
    README distinguishes manifest/status-table validation from verified
    backlog traceability for every local paper row.

- [ ] Keep README figure/notebook provenance wording scoped until paper
      artifact-role metadata exists.
  - Spec evidence: AlphaEvolve's Contributions section attributes paper figure
    creation to specific authors and separately identifies the people who
    assembled the accompanying Google Colab.
  - Current evidence: README can describe PDF manifest validation, future
    companion Colab tracking, exhibit provenance gaps, and rendered artifact
    hashes. It does not document creator/assembler role metadata for figures,
    tables, or companion notebooks, nor source locations tying those roles back
    to the AlphaEvolve Contributions section.
  - Required result: when paper-artifact role provenance lands, update README,
    ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes artifact availability, rendered/source hashes, and
    paper-attributed figure/notebook creator or assembler provenance.

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
  - Current evidence: README can point to broad Appendix B per-result
    metric/value and step-function payload gaps, but it does not separately
    warn that the three autocorrelation results need distinct interval-count,
    sign-policy, direction, prior-bound, and recomputation evidence.
  - Required result: when Appendix B.1-B.3 autocorrelation metadata lands,
    update README, ROADMAP, papers index, and code/paper TODOs together so
    README names the three constants, interval counts, bound directions,
    prior/current values, step-function payload hashes, and source links
    without merging them into one generic autocorrelation claim.

- [ ] Keep README Appendix B.1-B.3 labels scoped until paper-heading
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.1-B.3 are titled `First
    autocorrelation inequality`, `Second autocorrelation inequality`, and
    `Third autocorrelation inequality`, and the constants are `C1`, `C2`, and
    `C3`. The paper does not use `k=3`, `k=4`, or `k=5` labels for these three
    autocorrelation entries.
  - Current evidence: README can describe the Appendix B family/status registry
    and broad B.1-B.3 step-function gaps, but the checked registry and tests
    still use internal ids/names like `autocorrelation_bounds_k3` and
    `Autocorrelation inequality, k=3` without separate paper-facing label
    fields.
  - Required result: when Appendix B.1-B.3 label provenance lands, update
    README, ROADMAP, papers index, and code/paper TODOs so README exposes exact
    B.1-B.3 headings and C1-C3 constants, while any internal k-numbered ids are
    either renamed or clearly marked as non-paper implementation ids.

- [ ] Keep README Appendix B.8 ratio wording scoped until squared-ratio
      convention provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.8 reports constructions for the
    max/min pairwise-distance ratio, but the numerical values `12.889266112`
    for 16 points in 2D and `4.165849767` for 14 points in 3D are reported
    under a squared-ratio convention, with the geometric ratio obtained by a
    square-root transform.
  - Current evidence: README can point to broad Appendix B per-result
    metric/value provenance gaps, but it does not separately warn that B.8
    needs raw-value versus transformed-ratio labels before quoting those
    numbers.
  - Required result: when Appendix B.8 convention metadata lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    labels raw squared values, derived square-root ratios, point counts,
    dimensions, coordinate artifacts, and comparison units without conflating
    squared and unsquared objectives.

- [ ] Keep README Appendix B.8 witness wording scoped until distance
      certificates exist.
  - Spec evidence: AlphaEvolve Appendix B.8 and Figure 12 report 16 points in
    two dimensions achieving squared max/min-distance ratio `12.889266112`
    versus the prior squared bound `12.890`, and 14 points in three dimensions
    achieving squared ratio `4.165849767` versus the prior squared bound
    `4.168`.
  - Current evidence: README can point to broad Appendix B metric/value gaps
    and the B.8 squared-ratio convention gap, but it does not separately warn
    that B.8 needs coordinate payloads, exact point-count/dimension checks,
    all-pairs min/max distance recomputation, prior-bound comparisons, and
    Figure 12 panel links before claiming the point-set witnesses are
    reproduced.
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

- [ ] Keep README Appendix B.5 source-formulation wording scoped until
      equivalence evidence exists.
  - Spec evidence: AlphaEvolve Appendix B.5 defines the source problem using
    non-negative `f,g: [-1,1] -> [0,1]`, `f + g = 1`, `integral f = 1`,
    zero extension outside `[-1,1]`, and
    `sup_{x in [-2,2]} integral_{-1}^1 f(t) g(x+t) dt`, then uses `[40]` to
    reduce the constant to an infimum over normalized step functions `h` on
    `[0,2]`.
  - Current evidence: README can warn about B.5 step-function payload gaps, but
    it does not separately warn that the original problem statement and
    equivalence-to-step-functions reference must be preserved before claiming
    source-faithful Erdos minimum-overlap coverage.
  - Required result: when B.5 formulation/equivalence metadata lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    names the `f,g` constraints, zero-extension policy, shift-supremum domain,
    `[40]` equivalence, and mapping to the Figure 10 `h` payload.

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

- [ ] Keep README qualitative-feedback wording scoped until criterion
      provenance exists.
  - Spec evidence: AlphaEvolve Section 2.4 says LLM-generated feedback can
    grade hard-to-code properties such as simplicity and either add them as
    scores or discard candidates when a criterion is not fulfilled.
  - Current evidence: README accurately documents optional LLM feedback
    graders, bounded prompts, score parsing, normalized bounds/direction,
    weighted deltas, discard/min-score behavior, failure policies, and
    feedback-sourced objective metrics. It should not imply those mechanics
    prove AlphaEvolve-style qualitative feedback unless grader configuration
    also records the judged property, evaluator-gap rationale, rubric/prompt
    artifact, score-versus-discard intent, metric linkage, and calibration or
    report evidence.
  - Required result: when qualitative-feedback criterion provenance lands,
    update README, ROADMAP, papers index, and code/paper TODOs together so
    README distinguishes current generic feedback graders from governed
    hard-to-code criteria such as simplicity.

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

- [ ] Keep README proposal-memory claims scoped to bounded hypothesis indexes.
  - Spec evidence: AlphaEvolve-style evolutionary memory should be able to
    reuse prior proposal ideas, rationales, and hypotheses through scored and
    semantically searchable idea memory.
  - Current evidence: README now documents `runtime.history.hypothesis_index`
    as bounded redacted proposal `idea`/`rationale`/`hypothesis` summaries for
    valid programs that can feed current-run `resurfacing_index`, while noting
    that proposal scoring, semantic proposal retrieval, and persisted cross-run
    hypothesis tables remain open.
  - Required result: once proposal scoring, semantic/cross-run proposal
    indexes, or stricter proposal-field influence policy lands, update the
    README and matching code/paper TODO entries together so the README neither
    underclaims current proposal metadata capture nor overclaims
    AlphaEvolve-grade idea memory.

- [ ] Keep README scientific-discovery wording scoped to automated evaluators
      versus manual-experiment and LLM-only idea-review workflows.
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
    and proposal metadata, but it does not yet state a clear AlphaEvolve scope
    boundary for machine-gradeable tasks versus manual-experiment scientific
    workflows or pre-code LLM-only idea review, nor does it describe
    evaluator-environment readiness evidence such as robust evaluator design,
    automatable-domain boundaries, setup effort, and expected discovery value.
  - Required result: once scope metadata/reporting exists, update README,
    ROADMAP, papers index, and matching TODOs so public wording neither
    underclaims the current executable-evaluator workflow nor overclaims
    environment-scaling, manual-experiment, or AI-Co-Scientist-style
    idea-feedback support.

- [ ] Keep README AI-Co-Scientist comparison scoped until representation
      boundary evidence exists.
  - Spec evidence: AlphaEvolve Related Work says AI Co-Scientist represents
    hypotheses and evaluation criteria in natural language, whereas
    AlphaEvolve evolves code and uses programmatic evaluation functions. The
    paper says this choice helps sidestep LLM hallucinations and sustain many
    evolution time steps, while a future system could combine natural-language
    and programmatic idioms.
  - Current evidence: README can describe executable validators, optional LLM
    feedback graders, proposal `idea`/`rationale`/`hypothesis` metadata, and
    scientific-discovery scope caveats. It does not yet distinguish
    natural-language hypothesis artifacts from executable code candidates, nor
    does it provide report evidence for programmatic evaluation criteria,
    hallucination-risk controls, long-horizon step counts, or a bridge from
    language-only idea stages into executable candidate evaluation.
  - Required result: when representation-boundary reports land, update README,
    ROADMAP, papers index, and code/paper TODOs together so README separates
    AI-Co-Scientist-style natural-language hypothesis workflows from
    AlphaEvolve-style code/programmatic-evaluation workflows and does not
    overclaim hallucination resistance or long-horizon evolution from generic
    proposal metadata alone.

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
    diagnostics. It does not yet document a statistical cascade policy with
    confidence intervals, p-values, sequential stopping, false-promotion/
    false-rejection budgets, or explicit small-scale/main-test stage roles.
  - Required result: when statistical cascade promotion reports and validation
    land, update README, ROADMAP, papers index, and code/paper TODOs so README
    distinguishes current deterministic staged threshold gates from
    AlphaEvolve-style hypothesis-testing cascades.

- [ ] Keep README mutation-response wording scoped to structured proposal
      metadata versus natural-language preambles.
  - Spec evidence: AlphaEvolve Figure 3(c) shows explanatory natural-language
    text before a SEARCH/REPLACE diff example.
  - Current evidence: README accurately says text outside mutation payload
    sections must be proposal metadata; code accepts bounded structured fields
    and rejects ordinary prose around valid diff/block/workspace-file sections.
  - Required result: if LibreEvolve later accepts explanatory preambles, update
    README, ROADMAP, papers index, and code/paper TODOs with the exact parser
    boundary, redaction/provenance behavior, and distinction between safe
    proposal metadata and arbitrary unparsed prose.

- [ ] Keep README prompt-example wording scoped until copy-detection
      diagnostics exist.
  - Spec evidence: AlphaEvolve Figure 3(b,c) uses concrete current-program
    context and concrete SEARCH/REPLACE examples to communicate the edit
    contract.
  - Current evidence: README notes that concrete diff examples reduce observed
    placeholder-copying mistakes, but also says placeholder/example copying is
    not rejected by a dedicated validator. Current diagnostics prove parser
    shape, not that accepted mutations avoided copying prompt-only examples.
  - Required result: when prompt-example inventories and copy-detection
    diagnostics land, update README, ROADMAP, papers index, and code/paper
    TODOs so README can distinguish useful concrete examples from
    AlphaEvolve-style evidence that proposals edit the sampled current program
    rather than pasted prompt scaffolding.

- [ ] Keep README multi-edit consistency wording scoped until checked
      consistency evidence exists.
  - Spec evidence: AlphaEvolve Figure 3(b) includes a SEARCH/REPLACE prompt
    rule requiring proposed edits to be consistent with each other, for
    example adding a config variable when another replacement references it.
  - Current evidence: README can say LibreEvolve prompts ask for coherent
    edits and that parser, syntax, evaluator, and admission checks reject many
    broken candidates. It should not imply that the system has a
    paper-facing cross-edit consistency analyzer or report for introduced
    symbols/config/imports/resources, missing companion edits, coupled changed
    blocks, or unresolved references across a multi-block mutation.
  - Required result: when multi-edit consistency diagnostics land, update
    README, ROADMAP, papers index, and code/paper TODOs with proposal ids,
    changed block/file ids, introduced/reference labels, companion-edit links,
    unresolved-reference diagnostics, evaluator-failure taxonomy linkage, and
    accepted/rejected status so README distinguishes prompt guidance from
    AlphaEvolve-style evidence of coherent multi-edit proposals.

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

- [ ] Keep README mutation-operator wording scoped to fixed local edit
      surfaces until operator-construction evidence exists.
  - Spec evidence: AlphaEvolve Section 2.3 uses structured edit payloads, but
    Related Work distinguishes AlphaEvolve from evolutionary systems that need
    a handwritten set of mutation or crossover operators.
  - Current evidence: README correctly describes SEARCH/REPLACE diffs,
    configured full-block/full-code replacement, workspace file sections, and
    topology mutations. It does not yet describe a policy or report proving
    that LLMs construct higher-level mutation-operator families, that those
    families are selected adaptively from task/candidate/failure evidence, or
    that operator-family telemetry exists beyond the fixed parser/edit modes.
  - Required result: when mutation-operator construction policy lands, update
    README, ROADMAP, papers index, and code/paper TODOs with the boundary
    between edit payload grammar and mutation strategy, proposal-level
    operator-family provenance, adaptive selection/construction evidence, and
    benchmark telemetry before README implies AlphaEvolve-style replacement of
    handwritten mutation operators.

- [ ] Keep README creative-generation wording scoped until proposal-diversity
      evidence exists.
  - Spec evidence: AlphaEvolve Section 2.3 says SOTA LLMs digest previous
    solutions and propose new, diverse ways to improve them, while Section 4
    ablations connect stronger underlying LLMs to better performance.
  - Current evidence: README can describe parent/inspiration prompt context,
    proposal metadata, candidate history, sampling strategy metadata, bounded
    hypothesis summaries, and backend/model telemetry. It should not imply
    that LibreEvolve currently measures generated-proposal diversity,
    duplicate/near-duplicate rates, semantic idea novelty, or model-quality
    effects on proposal diversity.
  - Required result: when proposal-diversity reporting lands, update README,
    ROADMAP, papers index, and code/paper TODOs with per-call or per-batch
    idea/operator-family labels, parent/inspiration relations, prompt/backend
    model ids, duplicate/near-duplicate diagnostics, code and semantic or
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

- [ ] Keep README database-memory wording scoped until source/workspace dedup
      and evaluation-cache policy exists.
  - Spec evidence: AlphaEvolve's database stores generated solutions with
    attached evaluations and is meant to resurface previously explored ideas
    under fixed compute budgets.
  - Current evidence: README can describe deterministic candidate ids,
    candidate history, workspace hashes, unique program-id validation, and
    current-run resurfacing views. It should not imply that identical
    source/workspace proposals are rejected before evaluation, served from an
    evaluation cache, or intentionally re-evaluated under a documented
    stochastic-sampling policy.
  - Required result: when source/workspace deduplication or evaluation-cache
    policy lands, update README, ROADMAP, papers index, and code/paper TODOs
    with canonical hash scope, evaluator/config cache-key semantics,
    hit/miss/re-evaluation telemetry, replay behavior, and budget accounting.

- [ ] Keep README database-sampling wording scoped until sampling-balance
      reports exist.
  - Spec evidence: AlphaEvolve's database balances exploration and
    exploitation while resurfacing previously explored ideas.
  - Current evidence: README can describe configurable `explore_ratio`,
    `mixed` parent selection, explicit parent/inspiration strategies, selected
    parent/inspiration metadata, MAP-Elites cells, island pools, metric/frontier
    sampling, lineage sampling, novelty sampling, recency sampling, and bounded
    current-run resurfacing. It should not imply that these knobs have been
    calibrated or measured as an AlphaEvolve-style exploration/exploitation
    balance.
  - Required result: when sampling-balance reports land, update README,
    ROADMAP, papers index, and code/paper TODO entries with aggregate
    parent/inspiration decision counts, fallback and source-pool provenance,
    selected-program repetition, island/cell/metric/lineage/descriptor
    coverage, score-improvement versus diversity effects, and equal-budget
    comparisons across exploit, explore, mixed, metric, frontier, and lineage
    variants.

- [ ] Keep README discovery-distance wording scoped until initial-pool
      divergence evidence exists.
  - Spec evidence: AlphaEvolve's introduction says evolution can discover
    candidates substantially different from the initial candidate pool in both
    syntax and function.
  - Current evidence: README can describe lineage, workspace hashes, changed
    files, novelty/descriptor sampling, proposal metadata, and retained
    metrics. It should not imply that retained programs have been measured
    against every initial-pool candidate for syntactic or functional distance.
  - Required result: when initial-pool divergence reports land, update README,
    ROADMAP, papers index, and code/paper TODO entries together with
    seed-pool baselines, syntax-distance metrics, changed-component summaries,
    metric/behavior distance, and task-specific functional-difference evidence.

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

## Architecture Description
